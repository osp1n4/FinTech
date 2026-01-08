"""
Tests unitarios para el modelo Transaction y estrategias de fraude.

HUMAN REVIEW (Maria Paula Gutierrez):
Estos tests se escribieron siguiendo TDD (Test-Driven Development).
Primero se definen los casos de prueba que validan el comportamiento esperado,
luego se verifica que el código existente cumple con esas expectativas.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from services.shared.domain.models import (
    Transaction,
    Location,
    RiskLevel,
    FraudEvaluation
)


class TestLocation:
    """Tests para el Value Object Location."""
    
    def test_location_creation_valid(self):
        """Test: Debe crear una ubicación válida con coordenadas correctas."""
        # Arrange & Act
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Assert
        assert location.latitude == 4.7110
        assert location.longitude == -74.0721
    
    def test_location_immutable(self):
        """Test: Location debe ser inmutable (no permite modificar valores)."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act & Assert
        with pytest.raises(Exception):  # frozen=True lanza FrozenInstanceError
            location.latitude = 10.0
    
    def test_location_invalid_latitude(self):
        """Test: Debe rechazar latitudes fuera del rango [-90, 90]."""
        # Act & Assert
        with pytest.raises(ValueError):
            Location(latitude=100.0, longitude=-74.0721)
        
        with pytest.raises(ValueError):
            Location(latitude=-100.0, longitude=-74.0721)
    
    def test_location_invalid_longitude(self):
        """Test: Debe rechazar longitudes fuera del rango [-180, 180]."""
        # Act & Assert
        with pytest.raises(ValueError):
            Location(latitude=4.7110, longitude=200.0)
        
        with pytest.raises(ValueError):
            Location(latitude=4.7110, longitude=-200.0)


class TestTransaction:
    """Tests para el modelo Transaction."""
    
    def test_transaction_creation(self):
        """Test: Debe crear una transacción con todos los campos requeridos."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act
        transaction = Transaction(
            id="test_001",
            user_id="user_001",
            amount=Decimal("100.0"),
            location=location,
            timestamp=datetime.now()
        )
        
        # Assert
        assert transaction.id == "test_001"
        assert transaction.user_id == "user_001"
        assert transaction.amount == Decimal("100.0")
        assert transaction.location == location
    
    def test_transaction_invalid_empty_id(self):
        """Test: Debe rechazar transacción con ID vacío."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
            Transaction(
                id="",
                user_id="user_001",
                amount=Decimal("100.0"),
                location=location,
                timestamp=datetime.now()
            )
    
    def test_transaction_invalid_empty_user_id(self):
        """Test: Debe rechazar transacción con user_id vacío."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            Transaction(
                id="test_001",
                user_id="",
                amount=Decimal("100.0"),
                location=location,
                timestamp=datetime.now()
            )
    
    def test_transaction_amount_must_be_positive(self):
        """Test: El monto de la transacción debe ser mayor a cero."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction(
                id="test_001",
                user_id="user_001",
                amount=Decimal("-100.0"),
                location=location,
                timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction(
                id="test_001",
                user_id="user_001",
                amount=Decimal("0.0"),
                location=location,
                timestamp=datetime.now()
            )
    
    def test_transaction_requires_location(self):
        """Test: Una transacción debe tener una ubicación."""
        # Act & Assert
        with pytest.raises(ValueError, match="Location cannot be None"):
            Transaction(
                id="test_001",
                user_id="user_001",
                amount=Decimal("100.0"),
                location=None,
                timestamp=datetime.now()
            )


class TestFraudEvaluation:
    """Tests para el modelo FraudEvaluation."""
    
    def test_fraud_evaluation_low_risk_auto_approved(self):
        """Test: Las evaluaciones de riesgo bajo deben aprobarse automáticamente."""
        # Arrange & Act
        evaluation = FraudEvaluation(
            transaction_id="test_001",
            user_id="user_001",
            risk_level=RiskLevel.LOW_RISK,
            reasons=["No risk factors detected"],
            timestamp=datetime.now()
        )
        
        # Assert
        assert evaluation.status == "APPROVED"
        assert evaluation.risk_level == RiskLevel.LOW_RISK
    
    def test_fraud_evaluation_medium_risk_pending_review(self):
        """Test: Las evaluaciones de riesgo medio deben requerir revisión."""
        # Arrange & Act
        evaluation = FraudEvaluation(
            transaction_id="test_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime.now()
        )
        
        # Assert
        assert evaluation.status == "PENDING_REVIEW"
        assert evaluation.risk_level == RiskLevel.MEDIUM_RISK
    
    def test_fraud_evaluation_high_risk_rejected(self):
        """Test: Las evaluaciones de riesgo alto deben rechazarse automáticamente."""
        # Arrange & Act
        evaluation = FraudEvaluation(
            transaction_id="test_001",
            user_id="user_001",
            risk_level=RiskLevel.HIGH_RISK,
            reasons=["Multiple fraud indicators"],
            timestamp=datetime.now()
        )
        
        # Assert
        assert evaluation.status == "REJECTED"
        assert evaluation.risk_level == RiskLevel.HIGH_RISK
    
    def test_fraud_evaluation_manual_decision_approved(self):
        """Test: Debe permitir que un analista apruebe manualmente una transacción."""
        # Arrange
        evaluation = FraudEvaluation(
            transaction_id="test_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime.now()
        )
        
        # Act
        evaluation.apply_manual_decision("APPROVED", "analyst_001")
        
        # Assert
        assert evaluation.status == "APPROVED"
        assert evaluation.reviewed_by == "analyst_001"
        assert evaluation.reviewed_at is not None
    
    def test_fraud_evaluation_manual_decision_rejected(self):
        """Test: Debe permitir que un analista rechace manualmente una transacción."""
        # Arrange
        evaluation = FraudEvaluation(
            transaction_id="test_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime.now()
        )
        
        # Act
        evaluation.apply_manual_decision("REJECTED", "analyst_001")
        
        # Assert
        assert evaluation.status == "REJECTED"
        assert evaluation.reviewed_by == "analyst_001"
        assert evaluation.reviewed_at is not None
    
    def test_fraud_evaluation_invalid_decision(self):
        """Test: Debe rechazar decisiones inválidas."""
        # Arrange
        evaluation = FraudEvaluation(
            transaction_id="test_001",
            user_id="user_001",
            risk_level=RiskLevel.MEDIUM_RISK,
            reasons=["Unusual location"],
            timestamp=datetime.now()
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid decision"):
            evaluation.apply_manual_decision("INVALID", "analyst_001")


class TestRiskLevel:
    """Tests para el enum RiskLevel."""
    
    def test_risk_level_values(self):
        """Test: RiskLevel debe tener tres niveles con valores numéricos ordenados."""
        # Assert
        assert RiskLevel.LOW_RISK.value == 1
        assert RiskLevel.MEDIUM_RISK.value == 2
        assert RiskLevel.HIGH_RISK.value == 3
    
    def test_risk_level_comparison(self):
        """Test: Los niveles de riesgo deben ser comparables por gravedad."""
        # Assert
        assert RiskLevel.LOW_RISK.value < RiskLevel.MEDIUM_RISK.value
        assert RiskLevel.MEDIUM_RISK.value < RiskLevel.HIGH_RISK.value
        assert RiskLevel.LOW_RISK.value < RiskLevel.HIGH_RISK.value
