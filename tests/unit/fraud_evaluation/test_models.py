"""
Unit Tests - Domain Models
Pruebas para entidades y value objects del dominio
"""
import pytest
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import (
    Transaction,
    FraudEvaluation,
    Location,
    RiskLevel,
)


class TestLocation:
    """Tests para Location Value Object"""

    def test_create_location_valid(self):
        """Debe crear una ubicación válida"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060

    def test_location_is_immutable(self):
        """Location debe ser inmutable (Value Object)"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(AttributeError):
            location.latitude = 50.0

    def test_location_equality(self):
        """Dos locations con mismas coordenadas deben ser iguales"""
        loc1 = Location(latitude=40.7128, longitude=-74.0060)
        loc2 = Location(latitude=40.7128, longitude=-74.0060)
        assert loc1 == loc2

    def test_location_inequality(self):
        """Dos locations con diferentes coordenadas no deben ser iguales"""
        loc1 = Location(latitude=40.7128, longitude=-74.0060)
        loc2 = Location(latitude=41.8781, longitude=-87.6298)
        assert loc1 != loc2

    def test_location_invalid_latitude(self):
        """Debe rechazar latitud fuera de rango"""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            Location(latitude=100.0, longitude=-74.0060)

    def test_location_invalid_longitude(self):
        """Debe rechazar longitud fuera de rango"""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            Location(latitude=40.7128, longitude=-200.0)


class TestTransaction:
    """Tests para Transaction Entity"""

    def test_create_transaction_valid(self):
        """Debe crear una transacción válida"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.50"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )
        assert transaction.id == "txn_001"
        assert transaction.amount == Decimal("100.50")
        assert transaction.user_id == "user_001"
        assert transaction.location == location

    def test_transaction_negative_amount(self):
        """Debe rechazar monto negativo"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction(
                id="txn_001",
                amount=Decimal("-10.00"),
                user_id="user_001",
                location=location,
                timestamp=datetime(2026, 1, 8, 12, 0, 0),
            )

    def test_transaction_zero_amount(self):
        """Debe rechazar monto cero"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction(
                id="txn_001",
                amount=Decimal("0.00"),
                user_id="user_001",
                location=location,
                timestamp=datetime(2026, 1, 8, 12, 0, 0),
            )


class TestFraudEvaluation:
    """Tests para FraudEvaluation Entity"""

    def test_create_fraud_evaluation(self):
        """Debe crear una evaluación de fraude"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            amount=Decimal("1500.00"),
            location=location,
            risk_level=RiskLevel.HIGH_RISK,
            reasons=["Amount exceeds threshold"],
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
            status="REJECTED",
        )
        assert evaluation.transaction_id == "txn_001"
        assert evaluation.risk_level == RiskLevel.HIGH_RISK
        assert evaluation.status == "REJECTED"
        assert len(evaluation.reasons) == 1

    def test_fraud_evaluation_has_timestamp(self):
        """Debe tener timestamp automático"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        now = datetime(2026, 1, 8, 12, 0, 0)
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            amount=Decimal("100.00"),
            location=location,
            risk_level=RiskLevel.LOW_RISK,
            reasons=[],
            timestamp=now,
            status="APPROVED",
        )
        assert evaluation.timestamp is not None
        assert isinstance(evaluation.timestamp, datetime)
        assert evaluation.timestamp == now

    def test_risk_level_enum_values(self):
        """Debe tener los valores correctos de RiskLevel"""
        assert RiskLevel.LOW_RISK.value == 1
        assert RiskLevel.MEDIUM_RISK.value == 2
        assert RiskLevel.HIGH_RISK.value == 3

    def test_fraud_evaluation_multiple_reasons(self):
        """Debe soportar múltiples razones"""
        location = Location(latitude=40.7128, longitude=-74.0060)
        reasons = ["High amount", "Unusual location", "Unknown device"]
        evaluation = FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            amount=Decimal("2000.00"),
            location=location,
            risk_level=RiskLevel.HIGH_RISK,
            reasons=reasons,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
            status="PENDING_REVIEW",
        )
        assert len(evaluation.reasons) == 3
        assert "High amount" in evaluation.reasons
