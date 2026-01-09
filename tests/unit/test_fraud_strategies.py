"""
Tests unitarios para las estrategias de detección de fraude.

HUMAN REVIEW (Maria Paula Gutierrez):
Estos tests validan que cada estrategia detecte correctamente
los patrones de fraude según los requisitos de negocio.
"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'services' / 'fraud-evaluation-service'))

from datetime import datetime
from decimal import Decimal
from src.domain.models import (
    Transaction,
    Location,
    RiskLevel
)
from src.domain.strategies.amount_threshold import AmountThresholdStrategy


class TestAmountThresholdStrategy:
    """Tests para la estrategia de umbral de monto."""
    
    def test_threshold_strategy_creation(self):
        """Test: Debe crear una estrategia con umbral válido."""
        # Act
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.0"))
        
        # Assert
        assert strategy.threshold == Decimal("1500.0")
    
    def test_threshold_strategy_rejects_negative_threshold(self):
        """Test: Debe rechazar umbrales negativos o cero."""
        # Act & Assert
        with pytest.raises(ValueError):
            AmountThresholdStrategy(threshold=Decimal("-100.0"))
        
        with pytest.raises(ValueError):
            AmountThresholdStrategy(threshold=Decimal("0.0"))
    
    def test_threshold_detects_high_risk_when_exceeded(self):
        """Test: Debe marcar como HIGH_RISK si el monto excede el umbral."""
        # Arrange
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.0"))
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="test_001",
            user_id="user_001",
            amount=Decimal("2000.0"),  # Excede el umbral
            location=location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "amount_threshold_exceeded" in result["reasons"]
        assert "2000.0" in result["details"]
        assert "1500.0" in result["details"]
    
    def test_threshold_allows_low_risk_when_below(self):
        """Test: Debe marcar como LOW_RISK si el monto está por debajo."""
        # Arrange
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.0"))
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="test_001",
            user_id="user_001",
            amount=Decimal("500.0"),  # Por debajo del umbral
            location=location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert len(result["reasons"]) == 0
    
    def test_threshold_exact_amount_is_low_risk(self):
        """Test: Monto exactamente igual al umbral debe ser LOW_RISK."""
        # Arrange
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.0"))
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="test_001",
            user_id="user_001",
            amount=Decimal("1500.0"),  # Exactamente el umbral
            location=location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        # Debe ser LOW_RISK porque el requisito dice "exceda", no "igual o mayor"
        assert result["risk_level"] == RiskLevel.LOW_RISK
    
    def test_threshold_rejects_none_transaction(self):
        """Test: Debe rechazar transacciones None."""
        # Arrange
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.0"))
        
        # Act & Assert
        with pytest.raises(ValueError):
            strategy.evaluate(None)
    
    def test_threshold_uses_decimal_for_precision(self):
        """Test: Debe usar Decimal para evitar problemas de precisión."""
        # Arrange
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.50"))
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="test_001",
            user_id="user_001",
            amount=Decimal("1500.51"),  # Mínimamente superior
            location=location,
            timestamp=datetime.now()
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        # Si usara float, podría fallar por problemas de precisión


class TestLocationStrategy:
    """Tests para la estrategia de ubicación."""
    
    def test_location_strategy_placeholder(self):
        """Test: Placeholder para estrategia de ubicación (pendiente)."""
        # TODO: Implementar tests cuando se cree LocationStrategy
        pass


class TestTimeBasedStrategy:
    """Tests para la estrategia de horario nocturno."""
    
    def test_time_based_strategy_placeholder(self):
        """Test: Placeholder para estrategia de horario (pendiente)."""
        # TODO: Implementar tests cuando se cree TimeBasedStrategy
        pass
