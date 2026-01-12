"""
Tests finales para alcanzar 100% de cobertura.
Cubre líneas 109, 150, 153, 157, 184, 202-203.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import RiskLevel, Location, Transaction, FraudEvaluation
from src.application.use_cases import EvaluateTransactionUseCase


class TestTransactionValidation:
    """Cubrir líneas 150, 153 en Transaction.__post_init__()."""
    
    def test_transaction_empty_id(self):
        """Línea 150: ValueError cuando transaction_id está vacío."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        try:
            Transaction(id="", user_id="user_001", amount=Decimal("500"), location=location, timestamp=datetime.now())
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Transaction ID cannot be empty" in str(e)
    
    def test_transaction_empty_user_id(self):
        """Línea 153: ValueError cuando user_id está vacío."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        try:
            Transaction(id="txn_001", user_id="   ", amount=Decimal("500"), location=location, timestamp=datetime.now())
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "User ID cannot be empty" in str(e)


class TestFraudEvaluationMethods:
    """Cubrir líneas 184, 202-203 en FraudEvaluation."""
    
    def test_apply_manual_decision_empty_analyst(self):
        """Línea 184: ValueError cuando analyst_id está vacío."""
        evaluation = FraudEvaluation(
            transaction_id="txn_001", user_id="user_001", risk_level=RiskLevel.MEDIUM_RISK,
            reasons=[], timestamp=datetime.now(), status="PENDING_REVIEW"
        )
        try:
            evaluation.apply_manual_decision("APPROVED", "")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Analyst ID cannot be empty" in str(e)
    
    def test_authenticate_by_user(self):
        """Líneas 202-203: authenticate_by_user asigna user_authenticated y user_auth_timestamp."""
        evaluation = FraudEvaluation(
            transaction_id="txn_002", user_id="user_002", risk_level=RiskLevel.HIGH_RISK,
            reasons=[], timestamp=datetime.now(), status="REJECTED"
        )
        evaluation.authenticate_by_user(confirmed=False)
        assert evaluation.user_authenticated == False
        assert evaluation.user_auth_timestamp is not None


class TestUseCaseTwoRulesViolated:
    """Cubrir línea 109 en use_cases.py."""
    
    @pytest.mark.asyncio
    async def test_high_risk_with_two_violations(self):
        """Línea 109: HIGH_RISK cuando rules_violated >= 2."""
        repository, publisher, cache = Mock(), Mock(), Mock()
        repository.save_evaluation = AsyncMock()
        publisher.publish_for_manual_review = AsyncMock()
        cache.get_user_location = AsyncMock(return_value=None)
        cache.set_user_location = AsyncMock()
        
        strategy1 = Mock()
        strategy1.evaluate = Mock(return_value={"risk_level": RiskLevel.HIGH_RISK, "reasons": ["reason1"]})
        strategy2 = Mock()
        strategy2.evaluate = Mock(return_value={"risk_level": RiskLevel.MEDIUM_RISK, "reasons": ["reason2"]})
        
        use_case = EvaluateTransactionUseCase(repository, publisher, cache, [strategy1, strategy2])
        
        data = {
            "id": "txn_001", "amount": 5000.0, "user_id": "user_001",
            "location": {"latitude": 4.7110, "longitude": -74.0721}
        }
        
        result = await use_case.execute(data)
        assert result["risk_level"] == "HIGH_RISK"


class TestUnusualTimeException:
    """Cubrir línea 157 en unusual_time.py."""
    
    def test_exception_handling(self):
        """Línea 157: captura excepción y retorna lista vacía."""
        from src.domain.strategies.unusual_time import UnusualTimeStrategy
        
        mock_repo = Mock()
        mock_repo.get_user_transaction_history = Mock(side_effect=Exception("DB error"))
        
        strategy = UnusualTimeStrategy(audit_repository=mock_repo)
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_001", user_id="user_001", amount=Decimal("500"),
            location=location, timestamp=datetime.now()
        )
        
        # Llamar a evaluate que internamente llama a _get_transaction_history
        # que lanza excepción y ejecuta la línea 157 (return [])
        result = strategy.evaluate(transaction, None)
        assert result["risk_level"] == RiskLevel.LOW_RISK
