"""
Unit Tests - Infrastructure Adapters
Pruebas para los adaptadores de infraestructura
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import FraudEvaluation, Location, RiskLevel
from src.infrastructure.adapters.mongodb import MongoDBAdapter
from src.infrastructure.adapters.redis import RedisAdapter
from src.infrastructure.adapters.rabbitmq import RabbitMQAdapter


class TestMongoDBAdapter:
    """Tests para MongoDBAdapter"""

    @pytest.mark.asyncio
    async def test_mongodb_adapter_initialization(self):
        """Debe inicializar correctamente el adaptador"""
        with patch('src.infrastructure.adapters.mongodb.MongoClient') as mock_client:
            adapter = MongoDBAdapter(connection_string="mongodb://localhost:27017", database_name="test_db")
            
            assert adapter.client is not None

    @pytest.mark.asyncio
    async def test_save_evaluation(self):
        """Debe guardar una evaluación en MongoDB"""
        with patch('src.infrastructure.adapters.mongodb.MongoClient') as mock_client:
            # Configurar mock
            mock_collection = Mock()
            mock_db = Mock()
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_client.return_value.__getitem__ = Mock(return_value=mock_db)
            
            adapter = MongoDBAdapter(connection_string="mongodb://localhost:27017", database_name="test_db")
            adapter.collection = mock_collection
            
            # Crear evaluación
            location = Location(latitude=40.7128, longitude=-74.0060)
            evaluation = FraudEvaluation(
                transaction_id="txn_001",
                user_id="user_001",
                risk_level=RiskLevel.LOW_RISK,
                reasons=[],
                amount=Decimal("100.00"),
                location=location,
                timestamp=datetime(2026, 1, 8, 12, 0, 0),
            )
            
            # Guardar evaluación
            await adapter.save_evaluation(evaluation)
            
            # Verificar que se llamó a insert_one
            mock_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_evaluation_by_id_found(self):
        """Debe recuperar una evaluación por ID"""
        with patch('src.infrastructure.adapters.mongodb.MongoClient') as mock_client:
            # Configurar mock
            mock_collection = Mock()
            mock_collection.find_one.return_value = {
                "transaction_id": "txn_001",
                "user_id": "user_001",
                "risk_level": "HIGH_RISK",
                "reasons": ["Amount exceeds threshold"],
                "amount": "1500.00",
                "location": {"latitude": 40.7128, "longitude": -74.0060},
                "timestamp": datetime(2026, 1, 8, 12, 0, 0),
                "status": "REJECTED",
            }
            
            mock_db = Mock()
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_client.return_value.__getitem__ = Mock(return_value=mock_db)
            
            adapter = MongoDBAdapter(connection_string="mongodb://localhost:27017", database_name="test_db")
            adapter.collection = mock_collection
            
            # Recuperar evaluación
            evaluation = await adapter.get_evaluation_by_id("txn_001")
            
            assert evaluation is not None
            assert evaluation.transaction_id == "txn_001"
            assert evaluation.user_id == "user_001"

    @pytest.mark.asyncio
    async def test_get_evaluation_by_id_not_found(self):
        """Debe retornar None si no encuentra la evaluación"""
        with patch('src.infrastructure.adapters.mongodb.MongoClient') as mock_client:
            # Configurar mock
            mock_collection = Mock()
            mock_collection.find_one.return_value = None
            
            mock_db = Mock()
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_client.return_value.__getitem__ = Mock(return_value=mock_db)
            
            adapter = MongoDBAdapter(connection_string="mongodb://localhost:27017", database_name="test_db")
            adapter.collection = mock_collection
            
            # Recuperar evaluación inexistente
            evaluation = await adapter.get_evaluation_by_id("txn_999")
            
            assert evaluation is None


class TestRedisAdapter:
    """Tests para RedisAdapter"""

    def test_redis_adapter_initialization(self):
        """Debe inicializar correctamente el adaptador"""
        adapter = RedisAdapter(redis_url="redis://localhost:6379", ttl=3600)
        
        assert adapter.redis_url == "redis://localhost:6379"
        assert adapter.default_ttl == 3600

    @pytest.mark.asyncio
    async def test_get_user_location_not_found(self):
        """Debe retornar None si no hay ubicación en cache"""
        with patch('src.infrastructure.adapters.redis.redis_async') as mock_redis:
            mock_client = AsyncMock()
            mock_client.get.return_value = None
            mock_redis.from_url = AsyncMock(return_value=mock_client)
            
            adapter = RedisAdapter(redis_url="redis://localhost:6379")
            
            location = await adapter.get_user_location("user_001")
            
            assert location is None

    @pytest.mark.asyncio
    async def test_get_user_location_found(self):
        """Debe recuperar ubicación del cache"""
        import json
        with patch('src.infrastructure.adapters.redis.redis_async') as mock_redis:
            mock_client = AsyncMock()
            location_data = {"latitude": 40.7128, "longitude": -74.0060}
            mock_client.get.return_value = json.dumps(location_data)
            mock_redis.from_url = AsyncMock(return_value=mock_client)
            
            adapter = RedisAdapter(redis_url="redis://localhost:6379")
            adapter.client = mock_client
            
            location = await adapter.get_user_location("user_001")
            
            assert location is not None
            assert location["latitude"] == 40.7128
            assert location["longitude"] == -74.0060

    @pytest.mark.asyncio
    async def test_set_user_location(self):
        """Debe guardar ubicación en cache"""
        with patch('src.infrastructure.adapters.redis.redis_async') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url = AsyncMock(return_value=mock_client)
            
            adapter = RedisAdapter(redis_url="redis://localhost:6379")
            adapter.client = mock_client
            
            await adapter.set_user_location("user_001", 40.7128, -74.0060)
            
            # Verificar que se llamó a setex
            mock_client.setex.assert_called_once()


class TestRabbitMQAdapter:
    """Tests para RabbitMQAdapter"""

    def test_rabbitmq_adapter_initialization(self):
        """Debe inicializar correctamente el adaptador"""
        adapter = RabbitMQAdapter(
            rabbitmq_url="amqp://localhost:5672",
            transactions_queue="transactions",
            manual_review_queue="manual_review"
        )
        
        assert adapter.rabbitmq_url == "amqp://localhost:5672"
        assert adapter.transactions_queue == "transactions"
        assert adapter.manual_review_queue == "manual_review"

    @pytest.mark.asyncio
    async def test_publish_evaluation(self):
        """Debe publicar una evaluación"""
        with patch('src.infrastructure.adapters.rabbitmq.pika') as mock_pika:
            # Configurar mocks
            mock_connection = Mock()
            mock_channel = Mock()
            mock_connection.is_closed = False
            mock_pika.URLParameters.return_value = Mock()
            mock_pika.BlockingConnection.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            
            adapter = RabbitMQAdapter(
                rabbitmq_url="amqp://localhost:5672",
                transactions_queue="transactions",
                manual_review_queue="manual_review"
            )
            adapter.connection = mock_connection
            adapter.channel = mock_channel
            
            # Publicar evaluación
            evaluation_data = {
                "transaction_id": "txn_001",
                "user_id": "user_001",
                "risk_level": "HIGH_RISK",
                "status": "REJECTED",
            }
            
            await adapter.publish_transaction_for_processing(evaluation_data)
            
            # Verificar que se llamó a basic_publish
            mock_channel.basic_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_rabbitmq_publish_to_correct_queue(self):
        """Debe publicar a la cola correcta"""
        with patch('src.infrastructure.adapters.rabbitmq.pika') as mock_pika:
            # Configurar mocks
            mock_connection = Mock()
            mock_channel = Mock()
            mock_connection.is_closed = False
            mock_pika.URLParameters.return_value = Mock()
            mock_pika.BlockingConnection.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            
            adapter = RabbitMQAdapter(
                rabbitmq_url="amqp://localhost:5672",
                transactions_queue="transactions",
                manual_review_queue="manual_review"
            )
            adapter.connection = mock_connection
            adapter.channel = mock_channel
            
            # Publicar evaluación
            evaluation_data = {
                "transaction_id": "txn_001",
                "user_id": "user_001",
                "risk_level": "MEDIUM_RISK",
                "status": "PENDING_REVIEW",
            }
            
            await adapter.publish_for_manual_review(evaluation_data)
            
            # Verificar que se llamó con la cola correcta
            call_args = mock_channel.basic_publish.call_args
            assert call_args[1]["routing_key"] == "manual_review"
