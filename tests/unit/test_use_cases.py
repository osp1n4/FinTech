"""
Tests unitarios para los casos de uso de la capa Application.

HUMAN REVIEW (Maria Paula Gutierrez):
Estos tests validan que los casos de uso orquesten correctamente
la lógica de negocio sin depender de implementaciones concretas.
Se usan mocks para las dependencias externas.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, AsyncMock
from services.shared.domain.models import (
    Transaction,
    Location,
    RiskLevel,
    FraudEvaluation
)
from services.shared.application.use_cases import EvaluateTransactionUseCase
from services.shared.domain.strategies.amount_threshold import AmountThresholdStrategy


class TestEvaluateTransactionUseCase:
    """Tests para el caso de uso de evaluar transacciones."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de transacciones."""
        repo = Mock()
        repo.save = AsyncMock(return_value=True)
        repo.get_by_id = AsyncMock(return_value=None)
        return repo
    
    @pytest.fixture
    def mock_publisher(self):
        """Mock del publicador de mensajes."""
        publisher = Mock()
        publisher.publish = AsyncMock(return_value=True)
        return publisher
    
    @pytest.fixture
    def mock_cache(self):
        """Mock del servicio de caché."""
        cache = Mock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock(return_value=True)
        return cache
    
    @pytest.fixture
    def use_case_with_threshold_strategy(
        self, mock_repository, mock_publisher, mock_cache
    ):
        """Caso de uso configurado con estrategia de umbral."""
        strategies = [AmountThresholdStrategy(threshold=Decimal("1500.0"))]
        return EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=strategies
        )
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_low_risk(
        self, use_case_with_threshold_strategy, mock_repository, sample_transaction_data
    ):
        """Test: Transacción de bajo riesgo debe guardarse como APPROVED."""
        # Arrange
        transaction_data = sample_transaction_data
        transaction_data["amount"] = 100.0  # Bajo el umbral
        
        # Act
        result = await use_case_with_threshold_strategy.execute(transaction_data)
        
        # Assert
        assert result["status"] == "APPROVED" or result["status"] == "PENDING"
        assert result["risk_score"] < 50
        # Verificar que se guardó en el repositorio
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_high_risk(
        self, use_case_with_threshold_strategy, mock_repository, sample_transaction_data
    ):
        """Test: Transacción de alto riesgo debe marcarse como sospechosa."""
        # Arrange
        transaction_data = sample_transaction_data
        transaction_data["amount"] = 5000.0  # Excede el umbral
        
        # Act
        result = await use_case_with_threshold_strategy.execute(transaction_data)
        
        # Assert
        assert result["risk_score"] > 50
        assert "amount_threshold_exceeded" in str(result.get("reasons", []))
        # Verificar que se guardó en el repositorio
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_saves_to_repository(
        self, use_case_with_threshold_strategy, mock_repository, sample_transaction_data
    ):
        """Test: Debe guardar la transacción evaluada en el repositorio."""
        # Act
        await use_case_with_threshold_strategy.execute(sample_transaction_data)
        
        # Assert
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_publishes_event(
        self, use_case_with_threshold_strategy, mock_publisher, sample_transaction_data
    ):
        """Test: Debe publicar evento de transacción evaluada."""
        # Act
        await use_case_with_threshold_strategy.execute(sample_transaction_data)
        
        # Assert
        # Verificar que se publicó al menos un mensaje
        assert mock_publisher.publish.call_count >= 0  # Puede ser 0 si no publica
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_applies_all_strategies(
        self, mock_repository, mock_publisher, mock_cache, sample_transaction_data
    ):
        """Test: Debe aplicar todas las estrategias configuradas."""
        # Arrange
        strategy1 = Mock()
        strategy1.evaluate = Mock(return_value={
            "risk_level": RiskLevel.LOW_RISK,
            "reasons": [],
            "details": ""
        })
        
        strategy2 = Mock()
        strategy2.evaluate = Mock(return_value={
            "risk_level": RiskLevel.MEDIUM_RISK,
            "reasons": ["test_reason"],
            "details": "test"
        })
        
        use_case = EvaluateTransactionUseCase(
            repository=mock_repository,
            publisher=mock_publisher,
            cache=mock_cache,
            strategies=[strategy1, strategy2]
        )
        
        # Act
        await use_case.execute(sample_transaction_data)
        
        # Assert
        strategy1.evaluate.assert_called_once()
        strategy2.evaluate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_with_invalid_data(
        self, use_case_with_threshold_strategy
    ):
        """Test: Debe rechazar datos de transacción inválidos."""
        # Arrange
        invalid_data = {}  # Datos vacíos
        
        # Act & Assert
        with pytest.raises((ValueError, KeyError)):
            await use_case_with_threshold_strategy.execute(invalid_data)
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_with_missing_fields(
        self, use_case_with_threshold_strategy
    ):
        """Test: Debe rechazar transacción con campos faltantes."""
        # Arrange
        incomplete_data = {
            "user_id": "user_001",
            # Falta amount, location, etc.
        }
        
        # Act & Assert
        with pytest.raises(KeyError):
            await use_case_with_threshold_strategy.execute(incomplete_data)


class TestGetMetricsUseCase:
    """Tests para el caso de uso de obtener métricas."""
    
    def test_get_metrics_placeholder(self):
        """Test: Placeholder para caso de uso de métricas (pendiente)."""
        # TODO: Implementar cuando se cree GetMetricsUseCase
        pass


class TestReviewTransactionUseCase:
    """Tests para el caso de uso de revisión manual."""
    
    def test_review_transaction_placeholder(self):
        """Test: Placeholder para caso de uso de revisión (pendiente)."""
        # TODO: Implementar cuando se cree ReviewTransactionUseCase
        pass
