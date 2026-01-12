"""
Tests para cubrir líneas faltantes en use_cases.py e interfaces.

Cubre casos de error y excepciones en:
- EvaluateTransactionUseCase
- ReviewTransactionUseCase
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.application.use_cases import EvaluateTransactionUseCase, ReviewTransactionUseCase
from src.domain.models import FraudEvaluation, RiskLevel, Location, Transaction


class TestEvaluateTransactionUseCaseComplete:
    """Tests para cubrir líneas faltantes en EvaluateTransactionUseCase."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mocks de las dependencias."""
        repository = Mock()
        publisher = Mock()
        cache = Mock()
        strategies = []
        
        repository.save_evaluation = AsyncMock()
        publisher.publish_transaction_for_processing = AsyncMock()
        cache.get_user_location = AsyncMock(return_value=None)
        cache.set_user_location = AsyncMock()
        
        return repository, publisher, cache, strategies
    
    @pytest.mark.asyncio
    async def test_parse_transaction_missing_field(self, mock_dependencies):
        """Test: parse_transaction con campo faltante (línea 188)."""
        repository, publisher, cache, strategies = mock_dependencies
        use_case = EvaluateTransactionUseCase(repository, publisher, cache, strategies)
        
        # Data sin campo requerido 'id'
        invalid_data = {
            "amount": 500.0,
            "user_id": "user_001"
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            use_case._build_transaction_from_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_parse_transaction_invalid_format(self, mock_dependencies):
        """Test: parse_transaction con formato inválido (línea 189)."""
        repository, publisher, cache, strategies = mock_dependencies
        use_case = EvaluateTransactionUseCase(repository, publisher, cache, strategies)
        
        # Data con latitude no numérica (causa ValueError en Location)
        invalid_data = {
            "id": "txn_001",
            "amount": 500.0,
            "user_id": "user_001",
            "location": {
                "latitude": "not a number",
                "longitude": -74.0721
            }
        }
        
        with pytest.raises(ValueError, match="Invalid data format"):
            use_case._build_transaction_from_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_get_historical_location_corrupt_data(self, mock_dependencies):
        """Test: get_historical_location con datos corruptos (líneas 202-209)."""
        repository, publisher, cache, strategies = mock_dependencies
        use_case = EvaluateTransactionUseCase(repository, publisher, cache, strategies)
        
        # Datos sin latitude/longitude requeridos
        cache.get_user_location.return_value = {"bad_key": "bad_value"}
        
        result = await use_case._get_historical_location("user_001")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_execute_without_historical_location(self, mock_dependencies):
        """Test: execute sin ubicación histórica (línea 109)."""
        repository, publisher, cache, strategies = mock_dependencies
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy.evaluate.return_value = {
            "risk_level": RiskLevel.LOW_RISK,
            "reasons": []
        }
        strategies.append(mock_strategy)
        
        use_case = EvaluateTransactionUseCase(repository, publisher, cache, strategies)
        
        data = {
            "id": "txn_001",
            "amount": 500.0,
            "user_id": "user_001",
            "location": {
                "latitude": 4.7110,
                "longitude": -74.0721
            }
        }
        
        result = await use_case.execute(data)
        
        assert result["risk_level"] == "LOW_RISK"


class TestReviewTransactionUseCaseComplete:
    """Tests para cubrir líneas faltantes en ReviewTransactionUseCase."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio."""
        return Mock()
    
    def test_execute_transaction_not_found(self, mock_repository):
        """Test: execute con transacción inexistente (líneas 254-263)."""
        mock_repository.get_evaluation_by_id.return_value = None
        
        use_case = ReviewTransactionUseCase(mock_repository)
        
        with pytest.raises(ValueError, match="not found"):
            use_case.execute("txn_nonexistent", "APPROVED", "analyst_001")
    
    def test_execute_invalid_decision(self, mock_repository):
        """Test: execute con decisión inválida (línea 233)."""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["suspicious"],
            timestamp=datetime.now(),
            status="PENDING_REVIEW"
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation
        
        use_case = ReviewTransactionUseCase(mock_repository)
        
        # apply_manual_decision debería validar decisión inválida
        with pytest.raises(ValueError):
            use_case.execute("txn_001", "INVALID_DECISION", "analyst_001")
    
    def test_execute_success_approved(self, mock_repository):
        """Test: execute exitoso con APPROVED (líneas 254-263)."""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["suspicious"],
            timestamp=datetime.now(),
            status="PENDING_REVIEW"
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation
        mock_repository.update_evaluation.return_value = None
        
        use_case = ReviewTransactionUseCase(mock_repository)
        use_case.execute("txn_001", "APPROVED", "analyst_001")
        
        # Verificar que se llamó update_evaluation
        mock_repository.update_evaluation.assert_called_once()
        assert evaluation.status == "APPROVED"
        assert evaluation.reviewed_by == "analyst_001"
    
    def test_execute_success_rejected(self, mock_repository):
        """Test: execute exitoso con REJECTED."""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.HIGH_RISK,
            reasons=["high_amount"],
            timestamp=datetime.now(),
            status="PENDING_REVIEW"
        )
        mock_repository.get_evaluation_by_id.return_value = evaluation
        mock_repository.update_evaluation.return_value = None
        
        use_case = ReviewTransactionUseCase(mock_repository)
        use_case.execute("txn_001", "REJECTED", "analyst_001")
        
        mock_repository.update_evaluation.assert_called_once()
        assert evaluation.status == "REJECTED"


class TestInterfacesCoverage:
    """Tests para marcar líneas abstractas como cubiertas."""
    
    def test_transaction_repository_abstract_methods(self):
        """Test: Verificar que TransactionRepository tiene métodos abstractos."""
        from src.application.interfaces import TransactionRepository
        import inspect
        
        assert inspect.isabstract(TransactionRepository)
        abstract_methods = TransactionRepository.__abstractmethods__
        assert 'save_evaluation' in abstract_methods
        assert 'get_all_evaluations' in abstract_methods
        assert 'get_evaluation_by_id' in abstract_methods
        assert 'update_evaluation' in abstract_methods
    
    def test_message_publisher_abstract_methods(self):
        """Test: Verificar que MessagePublisher tiene métodos abstractos."""
        from src.application.interfaces import MessagePublisher
        import inspect
        
        assert inspect.isabstract(MessagePublisher)
    
    def test_cache_service_abstract_methods(self):
        """Test: Verificar que CacheService tiene métodos abstractos."""
        from src.application.interfaces import CacheService
        import inspect
        
        assert inspect.isabstract(CacheService)


class TestAdditionalEdgeCases:
    """Tests adicionales para cubrir casos edge."""
    
    @pytest.mark.asyncio
    async def test_evaluate_transaction_with_timestamp(self):
        """Test: _build_transaction_from_data con timestamp proporcionado (línea 174)."""
        from src.application.use_cases import EvaluateTransactionUseCase
        
        repository = Mock()
        publisher = Mock()
        cache = Mock()
        repository.save_evaluation = AsyncMock()
        publisher.publish_for_manual_review = AsyncMock()
        cache.get_user_location = AsyncMock(return_value=None)
        cache.set_user_location = AsyncMock()
        
        use_case = EvaluateTransactionUseCase(repository, publisher, cache, [])
        
        data = {
            "id": "txn_001",
            "amount": 500.0,
            "user_id": "user_001",
            "location": {
                "latitude": 4.7110,
                "longitude": -74.0721
            },
            "timestamp": "2026-01-12T10:00:00Z"
        }
        
        transaction = use_case._build_transaction_from_data(data)
        assert transaction.timestamp.year == 2026
