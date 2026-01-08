"""
Unit Tests - Use Cases
Pruebas para los casos de uso de evaluación de fraude
"""
import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal
from datetime import datetime
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import FraudEvaluation, RiskLevel
from src.application.use_cases import (
    EvaluateTransactionUseCase,
    ReviewTransactionUseCase,
)


class TestEvaluateTransactionUseCase:
    """Tests para EvaluateTransactionUseCase"""

    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de evaluaciones"""
        repository = Mock()
        repository.save_evaluation = AsyncMock()
        repository.get_evaluation_by_id = AsyncMock()
        return repository

    @pytest.fixture
    def mock_cache(self):
        """Mock del servicio de cache"""
        cache = Mock()
        cache.get_user_location = AsyncMock(return_value=None)
        cache.set_user_location = AsyncMock()
        return cache

    @pytest.fixture
    def mock_publisher(self):
        """Mock del publicador de mensajes"""
        publisher = Mock()
        publisher.publish_evaluation = AsyncMock()
        publisher.publish_for_manual_review = AsyncMock()
        return publisher

    @pytest.fixture
    def mock_strategies(self):
        """Mock de las estrategias de fraude"""
        from src.domain.strategies.base import FraudStrategy

        class MockStrategy(FraudStrategy):
            def __init__(self, risk_level, reasons):
                self._risk_level = risk_level
                self._reasons = reasons

            def evaluate(self, transaction, historical_location=None):
                return {
                    "risk_level": self._risk_level,
                    "reasons": self._reasons,
                    "details": ""
                }

        return [
            MockStrategy(RiskLevel.LOW_RISK, []),
            MockStrategy(RiskLevel.LOW_RISK, []),
        ]

    @pytest.mark.asyncio
    async def test_evaluate_low_risk_transaction(
        self, mock_repository, mock_cache, mock_publisher, mock_strategies
    ):
        """Debe evaluar transacción de bajo riesgo"""
        use_case = EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=mock_strategies,
        )

        transaction_data = {
            "id": "txn_001",
            "amount": 100.0,
            "user_id": "user_001",
            "location": {"latitude": 40.7128, "longitude": -74.0060},
        }

        result = await use_case.execute(transaction_data)

        assert result["risk_level"] == "LOW_RISK"
        assert result["status"] == "APPROVED"
        assert len(result["reasons"]) == 0
        mock_repository.save_evaluation.assert_called_once()
        # LOW_RISK no publica a review manual
        mock_publisher.publish_for_manual_review.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluate_high_risk_transaction(
        self, mock_repository, mock_cache, mock_publisher
    ):
        """Debe evaluar transacción de alto riesgo"""
        from src.domain.strategies.base import FraudStrategy

        class HighRiskStrategy(FraudStrategy):
            def evaluate(self, transaction, historical_location=None):
                return {
                    "risk_level": RiskLevel.HIGH_RISK,
                    "reasons": ["Amount exceeds threshold"],
                    "details": "High amount detected"
                }

        use_case = EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=[HighRiskStrategy()],
        )

        transaction_data = {
            "id": "txn_001",
            "amount": 5000.0,
            "user_id": "user_001",
            "location": {"latitude": 40.7128, "longitude": -74.0060},
        }

        result = await use_case.execute(transaction_data)

        # Una estrategia con HIGH_RISK = 1 regla violada = MEDIUM_RISK final
        assert result["risk_level"] == "MEDIUM_RISK"
        assert result["status"] == "PENDING_REVIEW"
        assert "Amount exceeds threshold" in result["reasons"]

    @pytest.mark.asyncio
    async def test_evaluate_medium_risk_transaction(
        self, mock_repository, mock_cache, mock_publisher
    ):
        """Debe evaluar transacción de riesgo medio"""
        from src.domain.strategies.base import FraudStrategy

        class MediumRiskStrategy(FraudStrategy):
            def evaluate(self, transaction, historical_location=None):
                return {
                    "risk_level": RiskLevel.MEDIUM_RISK,
                    "reasons": ["Unusual location"],
                    "details": "Location change detected"
                }

        use_case = EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=[MediumRiskStrategy()],
        )

        transaction_data = {
            "id": "txn_001",
            "amount": 1000.0,
            "user_id": "user_001",
            "location": {"latitude": 40.7128, "longitude": -74.0060},
        }

        result = await use_case.execute(transaction_data)

        assert result["risk_level"] == "MEDIUM_RISK"
        assert result["status"] == "PENDING_REVIEW"
        assert "Unusual location" in result["reasons"]

    @pytest.mark.asyncio
    async def test_cache_user_location_after_evaluation(
        self, mock_repository, mock_cache, mock_publisher, mock_strategies
    ):
        """Debe guardar la ubicación del usuario en cache"""
        use_case = EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=mock_strategies,
        )

        transaction_data = {
            "id": "txn_001",
            "amount": 100.0,
            "user_id": "user_001",
            "location": {"latitude": 40.7128, "longitude": -74.0060},
        }

        await use_case.execute(transaction_data)

        mock_cache.set_user_location.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_strategies_aggregate_results(
        self, mock_repository, mock_cache, mock_publisher
    ):
        """Debe agregar resultados de múltiples estrategias"""
        from src.domain.strategies.base import FraudStrategy

        class Strategy1(FraudStrategy):
            def evaluate(self, transaction, historical_location=None):
                return {
                    "risk_level": RiskLevel.MEDIUM_RISK,
                    "reasons": ["Reason 1"],
                    "details": "Detail 1"
                }

        class Strategy2(FraudStrategy):
            def evaluate(self, transaction, historical_location=None):
                return {
                    "risk_level": RiskLevel.LOW_RISK,
                    "reasons": ["Reason 2"],
                    "details": "Detail 2"
                }

        use_case = EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=[Strategy1(), Strategy2()],
        )

        transaction_data = {
            "id": "txn_001",
            "amount": 500.0,
            "user_id": "user_001",
            "location": {"latitude": 40.7128, "longitude": -74.0060},
        }

        result = await use_case.execute(transaction_data)

        # 2 estrategias con reasons = 2 reglas violadas = HIGH_RISK
        assert result["risk_level"] == "HIGH_RISK"
        assert len(result["reasons"]) >= 1


class TestReviewTransactionUseCase:
    """Tests para ReviewTransactionUseCase"""

    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de evaluaciones"""
        repository = Mock()
        repository.get_evaluation_by_id = AsyncMock()
        repository.update_evaluation = AsyncMock()
        return repository

    @pytest.mark.asyncio
    async def test_review_transaction_approved(self, mock_repository):
        """Debe aprobar una transacción pendiente"""
        # Crear evaluación mock
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
            status="PENDING_REVIEW",
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation

        use_case = ReviewTransactionUseCase(repository=mock_repository)
        await use_case.execute("txn_001", "APPROVED", "analyst_001")

        # Verificar que apply_manual_decision fue llamado
        assert evaluation.status == "APPROVED"
        assert evaluation.reviewed_by == "analyst_001"
        mock_repository.update_evaluation.assert_called_once()

    @pytest.mark.asyncio
    async def test_review_transaction_rejected(self, mock_repository):
        """Debe rechazar una transacción pendiente"""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.HIGH_RISK,
            reasons=["High amount"],
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
            status="PENDING_REVIEW",
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation

        use_case = ReviewTransactionUseCase(repository=mock_repository)
        await use_case.execute("txn_001", "REJECTED", "analyst_001")

        assert evaluation.status == "REJECTED"
        assert evaluation.reviewed_by == "analyst_001"

    @pytest.mark.asyncio
    async def test_review_transaction_not_found(self, mock_repository):
        """Debe lanzar error si la transacción no existe"""
        mock_repository.get_evaluation_by_id.return_value = None

        use_case = ReviewTransactionUseCase(repository=mock_repository)
        
        with pytest.raises(ValueError, match="Transaction txn_001 not found"):
            await use_case.execute("txn_001", "APPROVED", "analyst_001")

    @pytest.mark.asyncio
    async def test_review_invalid_decision(self, mock_repository):
        """Debe rechazar decisión inválida"""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
            status="PENDING_REVIEW",
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation

        use_case = ReviewTransactionUseCase(repository=mock_repository)
        
        with pytest.raises(ValueError, match="Invalid decision"):
            await use_case.execute("txn_001", "INVALID", "analyst_001")

    @pytest.mark.asyncio
    async def test_review_already_reviewed_transaction(self, mock_repository):
        """El código permite re-revisar transacciones (no lanza error)"""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
            status="APPROVED",
            reviewed_by="analyst_002",
            reviewed_at=datetime(2026, 1, 8, 12, 30, 0),
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation

        use_case = ReviewTransactionUseCase(repository=mock_repository)
        
        # No debería lanzar error - permite re-revisar
        await use_case.execute("txn_001", "APPROVED", "analyst_001")
        
        # El status se actualiza
        assert evaluation.reviewed_by == "analyst_001"
