"""
Tests unitarios para DeviceValidationStrategy.

Verifica que la estrategia detecte correctamente dispositivos nuevos
y reconozca dispositivos previamente registrados.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path al servicio (sin /src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Transaction, Location, RiskLevel
from src.domain.strategies.device_validation import DeviceValidationStrategy


class TestDeviceValidationStrategy:
    """Tests para la estrategia de validación de dispositivos."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock del cliente Redis."""
        redis_client = Mock()
        redis_client.sismember = Mock(return_value=False)
        redis_client.sadd = Mock(return_value=1)
        redis_client.expire = Mock(return_value=True)
        return redis_client
    
    @pytest.fixture
    def strategy(self, mock_redis_client):
        """Instancia de la estrategia con Redis mockeado."""
        return DeviceValidationStrategy(redis_client=mock_redis_client)
    
    @pytest.fixture
    def sample_transaction(self):
        """Transacción de ejemplo con device_id."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        return Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now(),
            device_id="device_abc123"
        )
    
    def test_new_device_detected_as_high_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: Un dispositivo nuevo debe ser detectado como HIGH_RISK."""
        # Arrange
        mock_redis_client.sismember.return_value = False  # Dispositivo no conocido
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "Dispositivo nuevo o no reconocido" in result["reasons"]
        assert "device_abc123" in result["details"]
        
        # Verificar que se registró el dispositivo
        mock_redis_client.sadd.assert_called_once_with("user_devices:user_123", "device_abc123")
        mock_redis_client.expire.assert_called_once_with("user_devices:user_123", 90 * 24 * 60 * 60)
    
    def test_known_device_returns_low_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: Un dispositivo conocido debe retornar LOW_RISK sin violaciones."""
        # Arrange
        mock_redis_client.sismember.return_value = True  # Dispositivo conocido
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []  # Sin violaciones
        assert "registrado previamente" in result["details"]
        
        # No debe registrar el dispositivo nuevamente
        mock_redis_client.sadd.assert_not_called()
    
    def test_transaction_without_device_id_medium_risk(self, strategy, mock_redis_client):
        """Test: Transacción sin device_id debe ser MEDIUM_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_002",
            user_id="user_456",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now(),
            device_id=None  # Sin device_id
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
        assert "No se proporcionó device_id" in result["reasons"]
    
    def test_transaction_with_empty_device_id_medium_risk(self, strategy, mock_redis_client):
        """Test: Transacción con device_id vacío debe ser MEDIUM_RISK."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_003",
            user_id="user_789",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now(),
            device_id=""  # Device_id vacío
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.MEDIUM_RISK
        assert "No se proporcionó device_id" in result["reasons"]
    
    def test_redis_error_returns_low_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: Error en Redis debe retornar LOW_RISK para no bloquear transacciones."""
        # Arrange
        mock_redis_client.sismember.side_effect = Exception("Redis connection failed")
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert "Error en validación de dispositivo" in result["reasons"]
    
    def test_multiple_devices_per_user(self, strategy, mock_redis_client):
        """Test: Un usuario puede tener múltiples dispositivos registrados."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        device1_transaction = Transaction(
            id="txn_004",
            user_id="user_multi",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now(),
            device_id="device_001"
        )
        device2_transaction = Transaction(
            id="txn_005",
            user_id="user_multi",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now(),
            device_id="device_002"
        )
        
        mock_redis_client.sismember.return_value = False
        
        # Act
        result1 = strategy.evaluate(device1_transaction)
        result2 = strategy.evaluate(device2_transaction)
        
        # Assert
        assert result1["risk_level"] == RiskLevel.HIGH_RISK  # Primer dispositivo
        assert result2["risk_level"] == RiskLevel.HIGH_RISK  # Segundo dispositivo
        assert mock_redis_client.sadd.call_count == 2
    
    def test_redis_key_format(self, strategy, mock_redis_client, sample_transaction):
        """Test: Verificar el formato correcto de la clave Redis."""
        # Act
        strategy.evaluate(sample_transaction)
        
        # Assert
        expected_key = "user_devices:user_123"
        mock_redis_client.sismember.assert_called_once_with(expected_key, "device_abc123")
    
    def test_device_expiration_time(self, strategy, mock_redis_client, sample_transaction):
        """Test: Los dispositivos deben expirar después de 90 días."""
        # Arrange
        mock_redis_client.sismember.return_value = False
        
        # Act
        strategy.evaluate(sample_transaction)
        
        # Assert
        expected_expiration = 90 * 24 * 60 * 60  # 90 días en segundos
        mock_redis_client.expire.assert_called_once_with("user_devices:user_123", expected_expiration)
