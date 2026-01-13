"""
Tests unitarios para RapidTransactionStrategy.

Verifica la detección de múltiples transacciones rápidas en un período corto.
HU-006: Detectar más de 3 transacciones en 5 minutos.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path al servicio (sin /src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Transaction, Location, RiskLevel
from src.domain.strategies.rapid_transaction import RapidTransactionStrategy


class TestRapidTransactionStrategy:
    """Tests para la estrategia de transacciones rápidas."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock del cliente Redis."""
        redis_client = Mock()
        redis_client.zadd = Mock(return_value=1)
        redis_client.expire = Mock(return_value=True)
        redis_client.zremrangebyscore = Mock(return_value=0)
        redis_client.zcount = Mock(return_value=1)
        return redis_client
    
    @pytest.fixture
    def strategy(self, mock_redis_client):
        """Instancia de la estrategia con Redis mockeado."""
        return RapidTransactionStrategy(
            redis_client=mock_redis_client,
            max_transactions=3,
            window_minutes=5
        )
    
    @pytest.fixture
    def sample_transaction(self):
        """Transacción de ejemplo."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        return Transaction(
            id="txn_001",
            user_id="user_123",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
    
    def test_first_transaction_low_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: La primera transacción debe ser LOW_RISK."""
        # Arrange
        mock_redis_client.zcount.return_value = 1  # Solo esta transacción
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
        assert "1 transactions in 5 minutes" in result["details"]
    
    def test_three_transactions_within_limit_low_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: 3 transacciones o menos deben ser LOW_RISK."""
        # Arrange
        mock_redis_client.zcount.return_value = 3  # Justo en el límite
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
        assert result["reasons"] == []
        assert "3 transactions in 5 minutes" in result["details"]
    
    def test_four_transactions_exceeds_limit_high_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: Más de 3 transacciones debe ser HIGH_RISK."""
        # Arrange
        mock_redis_client.zcount.return_value = 4  # Excede el límite
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "rapid_transactions_detected" in result["reasons"]
        assert "4 transactions in 5 minutes" in result["details"]
        assert "limit: 3" in result["details"]
    
    def test_multiple_rapid_transactions_high_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: Múltiples transacciones rápidas deben ser HIGH_RISK."""
        # Arrange
        mock_redis_client.zcount.return_value = 7  # Muchas transacciones
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "rapid_transactions_detected" in result["reasons"]
        assert "7 transactions in 5 minutes" in result["details"]
    
    def test_transaction_added_to_redis(self, strategy, mock_redis_client, sample_transaction):
        """Test: La transacción debe ser añadida a Redis."""
        # Arrange
        mock_redis_client.zcount.return_value = 1
        
        # Act
        strategy.evaluate(sample_transaction)
        
        # Assert
        expected_key = "rapid_tx:user_123"
        mock_redis_client.zadd.assert_called_once()
        call_args = mock_redis_client.zadd.call_args
        assert call_args[0][0] == expected_key
        assert sample_transaction.id in call_args[0][1]
    
    def test_redis_key_expiration_set(self, strategy, mock_redis_client, sample_transaction):
        """Test: La clave Redis debe tener expiración configurada."""
        # Arrange
        mock_redis_client.zcount.return_value = 1
        
        # Act
        strategy.evaluate(sample_transaction)
        
        # Assert
        expected_key = "rapid_tx:user_123"
        expected_expiration = 5 * 60  # 5 minutos en segundos
        mock_redis_client.expire.assert_called_once_with(expected_key, expected_expiration)
    
    def test_old_transactions_removed(self, strategy, mock_redis_client, sample_transaction):
        """Test: Las transacciones antiguas deben ser eliminadas."""
        # Arrange
        mock_redis_client.zcount.return_value = 2
        current_timestamp = sample_transaction.timestamp.timestamp()
        window_seconds = 5 * 60
        
        # Act
        strategy.evaluate(sample_transaction)
        
        # Assert
        expected_key = "rapid_tx:user_123"
        mock_redis_client.zremrangebyscore.assert_called_once()
        call_args = mock_redis_client.zremrangebyscore.call_args
        assert call_args[0][0] == expected_key
        assert call_args[0][1] == 0
        assert abs(call_args[0][2] - (current_timestamp - window_seconds)) < 1.0
    
    def test_custom_time_window(self, mock_redis_client):
        """Test: Debe permitir configurar ventana de tiempo personalizada."""
        # Arrange
        strategy = RapidTransactionStrategy(
            redis_client=mock_redis_client,
            max_transactions=5,
            window_minutes=10
        )
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_002",
            user_id="user_456",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
        mock_redis_client.zcount.return_value = 6
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "6 transactions in 10 minutes" in result["details"]
        assert "limit: 5" in result["details"]
    
    def test_custom_max_transactions(self, mock_redis_client):
        """Test: Debe permitir configurar número máximo de transacciones."""
        # Arrange
        strategy = RapidTransactionStrategy(
            redis_client=mock_redis_client,
            max_transactions=2,
            window_minutes=5
        )
        location = Location(latitude=4.7110, longitude=-74.0721)
        transaction = Transaction(
            id="txn_003",
            user_id="user_789",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
        mock_redis_client.zcount.return_value = 3
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.HIGH_RISK
        assert "limit: 2" in result["details"]
    
    def test_redis_error_returns_low_risk(self, strategy, mock_redis_client, sample_transaction):
        """Test: Error en Redis debe retornar LOW_RISK para no bloquear transacciones."""
        # Arrange
        mock_redis_client.zadd.side_effect = Exception("Redis connection failed")
        
        # Act
        result = strategy.evaluate(sample_transaction)
        
        # Assert
        assert result["risk_level"] == RiskLevel.LOW_RISK
    
    def test_strategy_name(self, strategy):
        """Test: Verificar que el nombre de la estrategia es correcto."""
        assert strategy.get_name() == "rapid_transaction"
    
    def test_different_users_tracked_separately(self, strategy, mock_redis_client):
        """Test: Diferentes usuarios deben ser rastreados por separado."""
        # Arrange
        location = Location(latitude=4.7110, longitude=-74.0721)
        user1_transaction = Transaction(
            id="txn_user1",
            user_id="user_001",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
        user2_transaction = Transaction(
            id="txn_user2",
            user_id="user_002",
            amount=Decimal("500.0"),
            location=location,
            timestamp=datetime.now()
        )
        mock_redis_client.zcount.return_value = 1
        
        # Act
        strategy.evaluate(user1_transaction)
        strategy.evaluate(user2_transaction)
        
        # Assert
        # Verificar que se usaron claves diferentes para cada usuario
        zadd_calls = mock_redis_client.zadd.call_args_list
        assert zadd_calls[0][0][0] == "rapid_tx:user_001"
        assert zadd_calls[1][0][0] == "rapid_tx:user_002"
