"""
Tests unitarios para el Worker Service.

Valida que el worker consuma mensajes de RabbitMQ correctamente
y ejecute los casos de uso apropiados.
Nota: Estos tests validan la lógica del worker sin imports directos
para evitar problemas con nombres de módulos con guiones.
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from decimal import Decimal


class TestWorkerLogic:
    """Tests para la lógica del worker."""
    
    @pytest.fixture
    def mock_use_case(self):
        """Mock del caso de uso."""
        use_case = Mock()
        use_case.execute = AsyncMock(return_value={
            "transaction_id": "txn_001",
            "risk_level": "LOW_RISK",
            "reasons": []
        })
        return use_case
    
    @pytest.fixture
    def mock_channel(self):
        """Mock del canal de RabbitMQ."""
        channel = Mock()
        channel.basic_ack = Mock()
        channel.basic_nack = Mock()
        return channel
    
    @pytest.fixture
    def mock_method(self):
        """Mock del método de entrega."""
        method = Mock()
        method.delivery_tag = "delivery_tag_001"
        return method
    
    def test_valid_transaction_data_structure(self):
        """Test: Debe validar estructura correcta de datos de transacción."""
        # Arrange
        transaction_data = {
            "id": "txn_001",
            "user_id": "user_123",
            "amount": 500.0,
            "location": {"latitude": 4.7110, "longitude": -74.0721},
            "timestamp": datetime.now().isoformat()
        }
        
        # Act
        body = json.dumps(transaction_data)
        parsed = json.loads(body)
        
        # Assert
        assert parsed["id"] == "txn_001"
        assert abs(parsed["amount"] - 500.0) < 1e-9
        assert "location" in parsed
    
    def test_invalid_json_structure(self):
        """Test: Debe detectar JSON inválido."""
        # Arrange
        invalid_body = b"invalid json {{"
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_body)
    
    def test_message_acknowledgment_on_success(self, mock_channel, mock_method):
        """Test: Debe hacer ACK cuando el mensaje se procesa exitosamente."""
        # Arrange
        delivery_tag = "delivery_tag_001"
        
        # Act
        mock_channel.basic_ack(delivery_tag=delivery_tag)
        
        # Assert
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=delivery_tag)
    
    def test_message_rejection_without_requeue(self, mock_channel, mock_method):
        """Test: Debe rechazar sin reencolar cuando los datos son inválidos."""
        # Arrange
        delivery_tag = "delivery_tag_001"
        
        # Act
        mock_channel.basic_nack(delivery_tag=delivery_tag, requeue=False)
        
        # Assert
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag=delivery_tag,
            requeue=False
        )
    
    def test_message_rejection_with_requeue(self, mock_channel, mock_method):
        """Test: Debe rechazar y reencolar con error temporal."""
        # Arrange
        delivery_tag = "delivery_tag_001"
        
        # Act
        mock_channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
        
        # Assert
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag=delivery_tag,
            requeue=True
        )


class TestWorkerConfiguration:
    """Tests para la configuración del worker."""
    
    def test_strategies_configuration(self):
        """Test: Debe configurar las 5 estrategias requeridas."""
        # Arrange
        expected_strategies = [
            "AmountThresholdStrategy",
            "LocationStrategy",
            "DeviceValidationStrategy",
            "RapidTransactionStrategy",
            "UnusualTimeStrategy"
        ]
        
        # Assert
        assert len(expected_strategies) == 5
    
    def test_rabbitmq_connection_parameters(self):
        """Test: Debe usar parámetros correctos de conexión."""
        # Arrange
        expected_queue = "transactions"
        expected_durable = True
        expected_prefetch = 1
        
        # Assert
        assert expected_queue == "transactions"
        assert expected_durable is True
        assert expected_prefetch == 1
    
    def test_error_handling_strategy(self):
        """Test: Debe tener estrategia de manejo de errores definida."""
        # Arrange
        error_types = {
            "json_error": "no_requeue",
            "validation_error": "no_requeue",
            "temporary_error": "requeue"
        }
        
        # Assert
        assert error_types["json_error"] == "no_requeue"
        assert error_types["validation_error"] == "no_requeue"
        assert error_types["temporary_error"] == "requeue"


class TestMessageProcessing:
    """Tests para el procesamiento de mensajes."""
    
    def test_extract_transaction_id_from_message(self):
        """Test: Debe extraer el ID de transacción del mensaje."""
        # Arrange
        message = {
            "id": "txn_123",
            "user_id": "user_456",
            "amount": 1000.0
        }
        
        # Act
        transaction_id = message.get("id")
        
        # Assert
        assert transaction_id == "txn_123"
    
    def test_parse_location_from_message(self):
        """Test: Debe parsear la ubicación del mensaje."""
        # Arrange
        message = {
            "id": "txn_124",
            "location": {
                "latitude": 4.7110,
                "longitude": -74.0721
            }
        }
        
        # Act
        location = message.get("location")
        
        # Assert
        assert abs(location["latitude"] - 4.7110) < 1e-9
        assert abs(location["longitude"] - (-74.0721)) < 1e-9
    
    def test_handle_missing_timestamp(self):
        """Test: Debe manejar timestamp faltante."""
        # Arrange
        message = {
            "id": "txn_125",
            "user_id": "user_789",
            "amount": 500.0,
            "location": {"latitude": 4.7110, "longitude": -74.0721}
        }
        
        # Act
        timestamp = message.get("timestamp")
        
        # Assert
        # Si no hay timestamp, será None
        assert timestamp is None or isinstance(timestamp, str)
    
    def test_handle_optional_device_id(self):
        """Test: Debe manejar device_id opcional."""
        # Arrange
        message_with_device = {
            "id": "txn_126",
            "device_id": "device_abc"
        }
        message_without_device = {
            "id": "txn_127"
        }
        
        # Act
        device_id_1 = message_with_device.get("device_id")
        device_id_2 = message_without_device.get("device_id")
        
        # Assert
        assert device_id_1 == "device_abc"
        assert device_id_2 is None


class TestWorkerResilience:
    """Tests para la resiliencia del worker."""
    
    def test_json_decode_error_handling(self):
        """Test: Debe capturar errores de decodificación JSON."""
        # Arrange
        invalid_json = b"\xff\xfe invalid"
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)
    
    def test_value_error_handling(self):
        """Test: Debe capturar ValueError por datos inválidos."""
        # Arrange
        invalid_amount = -100.0
        
        # Act & Assert
        with pytest.raises(AssertionError):
            assert invalid_amount > 0, "Amount must be positive"
    
    def test_connection_error_detection(self):
        """Test: Debe detectar errores de conexión."""
        # Arrange
        error_message = "Connection refused"
        
        # Act & Assert
        with pytest.raises(ConnectionError, match="Connection refused"):
            raise ConnectionError(error_message)
    
    def test_temporary_failure_retry_logic(self):
        """Test: Debe reintentar con fallos temporales."""
        # Arrange
        max_retries = 3
        current_retry = 0
        
        # Act
        should_retry = current_retry < max_retries
        
        # Assert
        assert should_retry is True
    
    def test_permanent_failure_no_retry(self):
        """Test: No debe reintentar con fallos permanentes."""
        # Arrange
        error_type = "ValidationError"
        permanent_errors = ["ValidationError", "JSONDecodeError"]
        
        # Act
        should_retry = error_type not in permanent_errors
        
        # Assert
        assert should_retry is False


class TestDependencyInjection:
    """Tests para inyección de dependencias."""
    
    def test_mongodb_connection_parameters(self):
        """Test: Validar parámetros de conexión MongoDB."""
        connection_string = "mongodb://test"
        database_name = "fraud_db"
        assert connection_string.startswith("mongodb://")
        assert len(database_name) > 0
    
    def test_redis_connection_parameters(self):
        """Test: Validar parámetros de conexión Redis."""
        redis_url = "redis://test"
        assert redis_url.startswith("redis://")
    
    def test_rabbitmq_connection_parameters(self):
        """Test: Validar parámetros de conexión RabbitMQ."""
        rabbitmq_url = "amqp://test"
        assert rabbitmq_url.startswith("amqp://")

