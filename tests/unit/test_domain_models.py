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
    TransactionStatus
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
    
    def test_transaction_creation(self, sample_transaction_data):
        """Test: Debe crear una transacción con todos los campos requeridos."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act
        transaction = Transaction(
            transaction_id=sample_transaction_data["transaction_id"],
            user_id=sample_transaction_data["user_id"],
            amount=Decimal(str(sample_transaction_data["amount"])),
            location=location,
            device_id=sample_transaction_data["device_id"],
            timestamp=datetime.now()
        )
        
        # Assert
        assert transaction.transaction_id == sample_transaction_data["transaction_id"]
        assert transaction.user_id == sample_transaction_data["user_id"]
        assert transaction.amount == Decimal("100.0")
        assert transaction.location == location
        assert transaction.device_id == sample_transaction_data["device_id"]
        assert transaction.status == TransactionStatus.PENDING
        assert transaction.risk_score == 0
    
    def test_transaction_initial_status_pending(self):
        """Test: Una transacción nueva debe tener estado PENDING."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act
        transaction = Transaction(
            transaction_id="test_001",
            user_id="user_001",
            amount=Decimal("100.0"),
            location=location,
            device_id="device_001",
            timestamp=datetime.now()
        )
        
        # Assert
        assert transaction.status == TransactionStatus.PENDING
    
    def test_transaction_initial_risk_score_zero(self):
        """Test: Una transacción nueva debe tener risk_score = 0."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act
        transaction = Transaction(
            transaction_id="test_001",
            user_id="user_001",
            amount=Decimal("100.0"),
            location=location,
            device_id="device_001",
            timestamp=datetime.now()
        )
        
        # Assert
        assert transaction.risk_score == 0
    
    def test_transaction_mark_as_approved(self):
        """Test: Debe poder marcar una transacción como aprobada."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            transaction_id="test_001",
            user_id="user_001",
            amount=Decimal("100.0"),
            location=location,
            device_id="device_001",
            timestamp=datetime.now()
        )
        
        # Act
        transaction.status = TransactionStatus.APPROVED
        
        # Assert
        assert transaction.status == TransactionStatus.APPROVED
    
    def test_transaction_mark_as_blocked(self):
        """Test: Debe poder marcar una transacción como bloqueada."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            transaction_id="test_001",
            user_id="user_001",
            amount=Decimal("100.0"),
            location=location,
            device_id="device_001",
            timestamp=datetime.now()
        )
        
        # Act
        transaction.status = TransactionStatus.BLOCKED
        
        # Assert
        assert transaction.status == TransactionStatus.BLOCKED
    
    def test_transaction_update_risk_score(self):
        """Test: Debe poder actualizar el risk_score de una transacción."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            transaction_id="test_001",
            user_id="user_001",
            amount=Decimal("100.0"),
            location=location,
            device_id="device_001",
            timestamp=datetime.now()
        )
        
        # Act
        transaction.risk_score = 75
        
        # Assert
        assert transaction.risk_score == 75
    
    def test_transaction_amount_must_be_positive(self):
        """Test: El monto de la transacción debe ser mayor a cero."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        
        # Act & Assert
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="test_001",
                user_id="user_001",
                amount=Decimal("-100.0"),  # Monto negativo
                location=location,
                device_id="device_001",
                timestamp=datetime.now()
            )
        
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="test_001",
                user_id="user_001",
                amount=Decimal("0.0"),  # Monto cero
                location=location,
                device_id="device_001",
                timestamp=datetime.now()
            )


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
