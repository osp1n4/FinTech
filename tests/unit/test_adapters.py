"""
Tests unitarios para los adaptadores de infraestructura.

Valida que los adaptadores de MongoDB, Redis y RabbitMQ
implementen correctamente las interfaces del Application Layer.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

# Agregar path al servicio (sin /src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import FraudEvaluation, RiskLevel, Transaction, Location


class TestMongoDBAdapter:
    """Tests para el adaptador de MongoDB."""
    
    @pytest.fixture
    def mock_mongo_client(self):
        """Mock del cliente de MongoDB."""
        with patch('src.adapters.MongoClient') as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_db.evaluations = mock_collection
            mock_client.return_value.__getitem__.return_value = mock_db
            yield mock_client, mock_db, mock_collection
    
    @pytest.fixture
    def sample_evaluation(self):
        """Evaluación de ejemplo."""
        location = Location(latitude=4.7110, longitude=-74.0721)
        return FraudEvaluation(
            transaction_id="txn_001",
            user_id="user_001",
            risk_level=RiskLevel.HIGH_RISK,
            reasons=["Amount exceeds threshold"],
            timestamp=datetime(2026, 1, 12, 10, 0, 0),
            status="PENDING",
            amount=Decimal("2000.0"),
            location=location
        )
    
    @pytest.mark.asyncio
    async def test_mongodb_adapter_initialization(self, mock_mongo_client):
        """Test: Inicialización del adaptador MongoDB."""
        from src.adapters import MongoDBAdapter
        
        _, _, mock_collection = mock_mongo_client
        
        _ = MongoDBAdapter("mongodb://localhost:27017", "test_db")
        
        # Verificar que se crearon índices
        assert mock_collection.create_index.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_save_evaluation(self, mock_mongo_client, sample_evaluation):
        """Test: Guardar evaluación en MongoDB."""
        from src.adapters import MongoDBAdapter
        
        _, _, mock_collection = mock_mongo_client
        adapter = MongoDBAdapter("mongodb://localhost:27017", "test_db")
        
        await adapter.save_evaluation(sample_evaluation)
        
        # Verificar que se llamó insert_one
        assert mock_collection.insert_one.called
        inserted_doc = mock_collection.insert_one.call_args[0][0]
        assert inserted_doc["transaction_id"] == "txn_001"
        assert inserted_doc["user_id"] == "user_001"
        assert inserted_doc["risk_level"] == "HIGH_RISK"
    
    @pytest.mark.asyncio
    async def test_get_all_evaluations(self, mock_mongo_client):
        """Test: Obtener todas las evaluaciones."""
        from src.adapters import MongoDBAdapter
        
        _, _, mock_collection = mock_mongo_client
        
        # Mock de datos devueltos
        mock_docs = [
            {
                "transaction_id": "txn_001",
                "user_id": "user_001",
                "risk_level": "HIGH_RISK",
                "reasons": ["test"],
                "timestamp": datetime(2026, 1, 12, 10, 0, 0),
                "status": "PENDING",
                "amount": 1000.0,
                "location": {"latitude": 4.7110, "longitude": -74.0721}
            }
        ]
        mock_collection.find.return_value.sort.return_value = mock_docs
        
        adapter = MongoDBAdapter("mongodb://localhost:27017", "test_db")
        evaluations = await adapter.get_all_evaluations()
        
        # Verificar que se llamó find y sort
        mock_collection.find.assert_called_once()
        assert len(evaluations) == 1
    
    @pytest.mark.asyncio
    async def test_get_evaluation_by_id(self, mock_mongo_client):
        """Test: Obtener evaluación por ID de transacción."""
        from src.adapters import MongoDBAdapter
        
        _, _, mock_collection = mock_mongo_client
        
        mock_doc = {
            "transaction_id": "txn_001",
            "user_id": "user_001",
            "risk_level": "HIGH_RISK",
            "reasons": ["test"],
            "timestamp": datetime(2026, 1, 12, 10, 0, 0),
            "status": "PENDING"
        }
        mock_collection.find_one.return_value = mock_doc
        
        adapter = MongoDBAdapter("mongodb://localhost:27017", "test_db")
        evaluation = adapter.get_evaluation_by_id("txn_001")
        
        mock_collection.find_one.assert_called_with({"transaction_id": "txn_001"})
        assert evaluation is not None
    
    def test_get_evaluations_by_user(self, mock_mongo_client):
        """Test: Obtener evaluaciones por usuario."""
        from src.adapters import MongoDBAdapter
        
        _, _, mock_collection = mock_mongo_client
        
        mock_docs = [
            {
                "transaction_id": "txn_001",
                "user_id": "user_001",
                "risk_level": "HIGH_RISK",
                "reasons": [],
                "timestamp": datetime(2026, 1, 12, 10, 0, 0),
                "status": "PENDING"
            }
        ]
        mock_collection.find.return_value.sort.return_value = mock_docs
        
        adapter = MongoDBAdapter("mongodb://localhost:27017", "test_db")
        _ = adapter.get_evaluations_by_user("user_001")
        
        mock_collection.find.assert_called_with({"user_id": "user_001"})


class TestRedisAdapter:
    """Tests para el adaptador de Redis."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock del cliente de Redis."""
        with patch('src.adapters.redis_async.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            yield mock_client
    
    @pytest.mark.asyncio
    async def test_redis_adapter_initialization(self, mock_redis_client):
        """Test: Inicialización del adaptador Redis."""
        from src.adapters import RedisAdapter
        
        adapter = RedisAdapter("redis://localhost:6379", ttl=3600)
        assert adapter.ttl == 3600
    
    @pytest.mark.asyncio
    async def test_get_user_location(self, mock_redis_client):
        """Test: Obtener ubicación de usuario."""
        from src.adapters import RedisAdapter
        
        mock_redis_client.get.return_value = '{"latitude": 4.7110, "longitude": -74.0721}'
        
        adapter = RedisAdapter("redis://localhost:6379", ttl=3600)
        location = await adapter.get_user_location("user_001")
        
        mock_redis_client.get.assert_called_with("user:user_001:location")
        assert abs(location["latitude"] - 4.7110) < 0.0001
    
    @pytest.mark.asyncio
    async def test_set_user_location(self, mock_redis_client):
        """Test: Guardar ubicación de usuario."""
        from src.adapters import RedisAdapter
        
        adapter = RedisAdapter("redis://localhost:6379", ttl=3600)
        await adapter.set_user_location("user_001", 4.7110, -74.0721)
        
        mock_redis_client.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_threshold_config(self, mock_redis_client):
        """Test: Obtener configuración de umbrales."""
        from src.adapters import RedisAdapter
        
        mock_redis_client.get.return_value = '{"amount_threshold": 1500.0, "location_radius_km": 100.0}'
        
        adapter = RedisAdapter("redis://localhost:6379", ttl=3600)
        config = await adapter.get_threshold_config()
        
        mock_redis_client.get.assert_called_with("config:thresholds")
        assert abs(config["amount_threshold"] - 1500.0) < 0.001


class TestRabbitMQAdapter:
    """Tests para el adaptador de RabbitMQ."""
    
    @pytest.fixture
    def mock_pika(self):
        """Mock de pika connection."""
        with patch('src.adapters.pika.BlockingConnection') as mock_conn:
            mock_channel = MagicMock()
            mock_conn.return_value.channel.return_value = mock_channel
            yield mock_conn, mock_channel
    
    def test_rabbitmq_adapter_initialization(self, mock_pika):
        """Test: Inicialización del adaptador RabbitMQ."""
        from src.adapters import RabbitMQAdapter
        
        _, mock_channel = mock_pika
        _ = RabbitMQAdapter("amqp://localhost:5672")
        
        # Verificar que se declararon colas
        assert mock_channel.queue_declare.called
    
    @pytest.mark.asyncio
    async def test_publish_transaction(self, mock_pika):
        """Test: Publicar transacción para procesamiento."""
        from src.adapters import RabbitMQAdapter
        
        _, mock_channel = mock_pika
        adapter = RabbitMQAdapter("amqp://localhost:5672")
        
        await adapter.publish_transaction_for_processing({"transaction_id": "txn_001"})
        
        # Verificar que se publicó el mensaje
        mock_channel.basic_publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_publish_manual_review(self, mock_pika):
        """Test: Publicar para revisión manual."""
        from src.adapters import RabbitMQAdapter
        
        _, mock_channel = mock_pika
        adapter = RabbitMQAdapter("amqp://localhost:5672")
        
        await adapter.publish_for_manual_review({"evaluation_id": "eval_001"})
        
        # Verificar que se publicó el mensaje
        assert mock_channel.basic_publish.call_count >= 1
    
    def test_close_connection(self, mock_pika):
        """Test: Cerrar conexión."""
        from src.adapters import RabbitMQAdapter
        
        mock_conn, _ = mock_pika
        mock_instance = mock_conn.return_value
        mock_instance.is_closed = False
        
        adapter = RabbitMQAdapter("amqp://localhost:5672")
        adapter.close()
        
        mock_instance.close.assert_called_once()
