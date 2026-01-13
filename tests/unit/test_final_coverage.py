"""
Tests finales para alcanzar el máximo de cobertura posible.

Cubre líneas específicas restantes en models.py, base.py, use_cases.py, unusual_time.py.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import RiskLevel, Location, Transaction, FraudEvaluation
from src.application.use_cases import EvaluateTransactionUseCase


class TestRiskLevelStr:
    """Tests para cubrir RiskLevel.__str__ (línea 38)."""
    
    def test_risk_level_str_low(self):
        """Test: __str__ de RiskLevel.LOW_RISK."""
        assert str(RiskLevel.LOW_RISK) == "LOW_RISK"
    
    def test_risk_level_str_medium(self):
        """Test: __str__ de RiskLevel.MEDIUM_RISK."""
        assert str(RiskLevel.MEDIUM_RISK) == "MEDIUM_RISK"
    
    def test_risk_level_str_high(self):
        """Test: __str__ de RiskLevel.HIGH_RISK."""
        assert str(RiskLevel.HIGH_RISK) == "HIGH_RISK"


class TestTransactionOptionalFields:
    """Tests para cubrir campos opcionales de Transaction."""
    
    def test_transaction_without_optional_fields(self):
        """Test: Transaction sin device_id, transaction_type, description (líneas 150, 153)."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_001",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
        
        # Verificar que los campos opcionales son None
        assert transaction.device_id is None
        assert transaction.transaction_type is None
        assert transaction.description is None
        
        # Verificar que __str__ funciona sin device_id (línea 150)
        str_repr = str(transaction)
        assert "txn_001" in str_repr
        assert "user_001" in str_repr


class TestFraudEvaluationOptionalFields:
    """Tests para cubrir campos opcionales de FraudEvaluation."""
    
    def test_fraud_evaluation_str_without_amount(self):
        """Test: __str__ de FraudEvaluation sin amount (línea 184)."""
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.LOW_RISK,
            reasons=[],
            timestamp=datetime.now(),
            status="APPROVED"
        )
        
        str_repr = str(evaluation)
        assert "txn_001" in str_repr
        assert "user_001" in str_repr
        assert "LOW_RISK" in str_repr
    
    def test_fraud_evaluation_str_with_all_fields(self):
        """Test: __str__ de FraudEvaluation con todos los campos (líneas 202-203)."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        evaluation = FraudEvaluation(
            transaction_id="txn_002",
            user_id="user_002",
            risk_level=RiskLevel.HIGH_RISK,
            reasons=["high_amount", "unusual_location"],
            timestamp=datetime.now(),
            amount=Decimal("10000.0"),
            location=location,
            transaction_type="WITHDRAWAL",
            description="ATM withdrawal",
            status="REJECTED"
        )
        
        str_repr = str(evaluation)
        assert "txn_002" in str_repr
        assert "user_002" in str_repr
        assert "HIGH_RISK" in str_repr
        assert "10000" in str_repr


class TestUseCaseLocationHandling:
    """Tests para cubrir manejo de ubicación en use_cases.py."""
    
    @pytest.mark.asyncio
    async def test_execute_with_historical_location(self):
        """Test: execute con ubicación histórica del usuario (línea 109)."""
        # Setup mocks
        repository = Mock()
        publisher = Mock()
        cache = Mock()
        
        repository.save_evaluation = AsyncMock()
        publisher.publish_for_manual_review = AsyncMock()
        
        # Configurar cache para devolver ubicación histórica
        cache.get_user_location = AsyncMock(return_value={
            "latitude": 4.6097,
            "longitude": -74.0817
        })
        cache.set_user_location = AsyncMock()
        
        # Mock strategy que usa historical_location
        mock_strategy = Mock()
        mock_strategy.evaluate.side_effect = lambda transaction, historical_location: {
            "risk_level": RiskLevel.MEDIUM_RISK if historical_location else RiskLevel.LOW_RISK,
            "reasons": ["different_location"] if historical_location else []
        }
        
        strategies = [mock_strategy]
        
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
        
        _ = await use_case.execute(data)
        
        # Verificar que se llamó con historical_location
        assert mock_strategy.evaluate.called
        call_args = mock_strategy.evaluate.call_args[0]
        assert call_args[1] is not None  # historical_location no es None
        assert abs(call_args[1].latitude - 4.6097) < 0.0001


class TestUnusualTimeEdgeCases:
    """Tests para cubrir casos edge en unusual_time.py."""
    
    def test_unusual_time_with_no_pattern_data(self):
        """Test: evaluate con data=None en patrón (línea 157)."""
        from src.domain.strategies.unusual_time import UnusualTimeStrategy
        
        mock_audit_repo = Mock()
        # Configurar get_user_transaction_history para devolver lista vacía
        mock_audit_repo.get_user_transaction_history = Mock(return_value=[])
        
        strategy = UnusualTimeStrategy(audit_repository=mock_audit_repo)
        
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_001",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime(2024, 1, 15, 3, 0, 0)  # 3 AM - hora inusual
        )
        
        result = strategy.evaluate(transaction, None)
        
        # Sin patrones históricos, cualquier hora es aceptable
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert len(result["reasons"]) == 0


class TestBaseStrategyAbstract:
    """Tests para cubrir base.py."""
    
    def test_fraud_strategy_abstract_evaluate(self):
        """Test: Llamar evaluate en implementación concreta (línea 50)."""
        from src.domain.strategies.amount_threshold import AmountThresholdStrategy
        
        strategy = AmountThresholdStrategy(threshold=1000.0)
        
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001",
            user_id="user_001",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
        
        result = strategy.evaluate(transaction, None)
        
        assert "risk_level" in result
        assert result["risk_level"] == RiskLevel.LOW_RISK
