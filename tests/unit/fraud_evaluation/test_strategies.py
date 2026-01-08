"""
Unit Tests - Fraud Detection Strategies
Pruebas para las estrategias de detección de fraude
"""
import pytest
from decimal import Decimal
from datetime import datetime
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Transaction, Location, RiskLevel
from src.domain.strategies.amount_threshold import AmountThresholdStrategy
from src.domain.strategies.location_check import LocationStrategy
from src.domain.strategies.device_validation import DeviceValidationStrategy


class TestAmountThresholdStrategy:
    """Tests para AmountThresholdStrategy"""

    def test_transaction_below_threshold_passes(self):
        """Transacción bajo el umbral debe pasar"""
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.00"))
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("1000.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        result = strategy.evaluate(transaction)

        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert len(result["reasons"]) == 0

    def test_transaction_above_threshold_fails(self):
        """Transacción sobre el umbral debe fallar"""
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.00"))
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("2000.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        result = strategy.evaluate(transaction)

        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert len(result["reasons"]) == 1
        assert "amount_threshold_exceeded" in result["reasons"]

    def test_transaction_at_threshold_passes(self):
        """Transacción igual al umbral debe pasar"""
        strategy = AmountThresholdStrategy(threshold=Decimal("1500.00"))
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("1500.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        result = strategy.evaluate(transaction)

        assert result["risk_level"] == RiskLevel.LOW_RISK


class TestLocationStrategy:
    """Tests para LocationStrategy"""

    def test_location_within_radius_passes(self):
        """Ubicación dentro del radio debe pasar"""
        strategy = LocationStrategy(radius_km=100.0)
        # Nueva York
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        # Simular ubicación previa cercana (Nueva York también)
        previous_location = Location(latitude=40.7580, longitude=-73.9855)
        result = strategy.evaluate(transaction, historical_location=previous_location)

        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert len(result["reasons"]) == 0

    def test_location_outside_radius_fails(self):
        """Ubicación fuera del radio debe fallar"""
        strategy = LocationStrategy(radius_km=100.0)
        # Los Angeles
        location = Location(latitude=34.0522, longitude=-118.2437)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        # Ubicación previa en Nueva York
        previous_location = Location(latitude=40.7128, longitude=-74.0060)
        result = strategy.evaluate(transaction, historical_location=previous_location)

        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert len(result["reasons"]) == 1
        assert "unusual_location" in result["reasons"]

    def test_no_previous_location_passes(self):
        """Sin ubicación previa debe pasar (primera transacción)"""
        strategy = LocationStrategy(radius_km=100.0)
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        result = strategy.evaluate(transaction, historical_location=None)

        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert len(result["reasons"]) > 0
        assert "no_historical_location" in result["reasons"]

    def test_haversine_distance_calculation(self):
        """Debe calcular distancia correctamente usando el método interno"""
        strategy = LocationStrategy(radius_km=100.0)
        
        # Nueva York a Los Angeles (~3,944 km)
        ny = Location(latitude=40.7128, longitude=-74.0060)
        la = Location(latitude=34.0522, longitude=-118.2437)

        distance = strategy._calculate_distance(ny, la)

        # Debe estar cerca de 3,944 km (con margen de error)
        assert 3900 <= distance <= 4000


class TestDeviceValidationStrategy:
    """Tests para DeviceValidationStrategy"""

    def test_known_device_passes(self):
        """Dispositivo conocido debe pasar"""
        known_devices = {"device_123", "device_456"}
        strategy = DeviceValidationStrategy(known_devices=known_devices)
        location = Location(latitude=40.7128, longitude=-74.0060)
        
        # Crear transacción con device_id
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )
        # Agregar device_id manualmente
        transaction.device_id = "device_123"

        result = strategy.evaluate(transaction)

        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert len(result["reasons"]) == 0

    def test_unknown_device_fails(self):
        """Dispositivo desconocido debe generar alerta"""
        known_devices = {"device_123", "device_456"}
        strategy = DeviceValidationStrategy(known_devices=known_devices)
        location = Location(latitude=40.7128, longitude=-74.0060)
        
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )
        transaction.device_id = "device_999"

        result = strategy.evaluate(transaction)

        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert len(result["reasons"]) == 1
        assert "unknown_device" in result["reasons"]

    def test_no_device_id_fails(self):
        """Sin device_id debe generar alerta"""
        strategy = DeviceValidationStrategy(known_devices=set())
        location = Location(latitude=40.7128, longitude=-74.0060)
        
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )
        # No agregar device_id

        result = strategy.evaluate(transaction)

        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
        assert len(result["reasons"]) == 1
        assert "no_device_id" in result["reasons"]

    def test_empty_known_devices_first_transaction(self):
        """Lista vacía de dispositivos conocidos con device_id debe dar riesgo alto"""
        strategy = DeviceValidationStrategy(known_devices=set())
        location = Location(latitude=40.7128, longitude=-74.0060)
        
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )
        transaction.device_id = "device_new"

        result = strategy.evaluate(transaction)

        # Dispositivo no conocido = alto riesgo
        assert result["risk_level"] == RiskLevel.HIGH_RISK


class TestStrategyChaining:
    """Tests para encadenamiento de estrategias"""

    def test_multiple_strategies_all_pass(self):
        """Todas las estrategias pasan"""
        amount_strategy = AmountThresholdStrategy(threshold=Decimal("1500.00"))
        location_strategy = LocationStrategy(radius_km=100.0)

        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("100.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        amount_result = amount_strategy.evaluate(transaction)
        location_result = location_strategy.evaluate(transaction, historical_location=None)

        assert amount_result["risk_level"] == RiskLevel.LOW_RISK
        assert location_result["risk_level"] == RiskLevel.LOW_RISK

    def test_multiple_strategies_one_fails(self):
        """Una estrategia falla"""
        amount_strategy = AmountThresholdStrategy(threshold=Decimal("1500.00"))
        location_strategy = LocationStrategy(radius_km=100.0)

        # Monto alto
        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("2000.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )

        amount_result = amount_strategy.evaluate(transaction)
        location_result = location_strategy.evaluate(transaction, historical_location=None)

        assert amount_result["risk_level"] == RiskLevel.HIGH_RISK
        assert location_result["risk_level"] == RiskLevel.LOW_RISK

    def test_aggregate_reasons_from_multiple_strategies(self):
        """Debe acumular razones de múltiples estrategias"""
        amount_strategy = AmountThresholdStrategy(threshold=Decimal("1000.00"))
        device_strategy = DeviceValidationStrategy(known_devices={"device_123"})

        location = Location(latitude=40.7128, longitude=-74.0060)
        transaction = Transaction(
            id="txn_001",
            amount=Decimal("2000.00"),
            user_id="user_001",
            location=location,
            timestamp=datetime(2026, 1, 8, 12, 0, 0),
        )
        transaction.device_id = "unknown_device"

        amount_result = amount_strategy.evaluate(transaction)
        device_result = device_strategy.evaluate(transaction)

        all_reasons = amount_result["reasons"] + device_result["reasons"]

        assert len(all_reasons) == 2
        assert "amount_threshold_exceeded" in all_reasons
        assert "unknown_device" in all_reasons
