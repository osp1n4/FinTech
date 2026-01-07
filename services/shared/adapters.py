"""
Infrastructure - Adaptadores para persistencia, caché y mensajería
Implementación concreta de los puertos definidos en Application Layer

Cumplimiento SOLID:
- Dependency Inversion: Implementa interfaces definidas en Application
- Interface Segregation: Cada adaptador implementa solo la interface necesaria
- Single Responsibility: Cada adaptador tiene una responsabilidad única

Nota del desarrollador (María Gutiérrez):
La IA sugirió un solo adaptador genérico "DataAdapter". Lo refactoricé en
tres adaptadores específicos para cumplir con Interface Segregation y
Single Responsibility.
"""
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
import redis.asyncio as redis_async
import pika
import json
from shared.application.interfaces import (
    TransactionRepository,
    MessagePublisher,
    CacheService,
)
from shared.domain.models import FraudEvaluation, RiskLevel
from shared.config import settings


class MongoDBAdapter(TransactionRepository):
    """
    Adaptador de MongoDB que implementa TransactionRepository
    
    Cumple Dependency Inversion: Application depende de la interface,
    no de esta implementación concreta
    
    Nota del desarrollador:
    La IA sugirió usar Motor (driver asíncrono). Lo cambié a pymongo
    simple para mantener el MVP minimalista. Se puede refactorizar
    a Motor después si es necesario (YAGNI principle).
    """

    def __init__(self, connection_string: str, database_name: str) -> None:
        """
        Inicializa el adaptador de MongoDB
        
        Args:
            connection_string: URL de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.evaluations = self.db.evaluations

        # Crear índices para mejorar performance
        self.evaluations.create_index("transaction_id", unique=True)
        self.evaluations.create_index([("timestamp", -1)])
        self.evaluations.create_index("user_id")

    async def save_evaluation(self, evaluation: FraudEvaluation) -> None:
        """
        Guarda una evaluación en MongoDB
        
        Nota del desarrollador:
        La IA sugirió guardar la entidad directamente. Agregué conversión
        explícita a dict para controlar la serialización y evitar problemas
        con tipos de Python no soportados por MongoDB.
        """
        document = {
            "transaction_id": evaluation.transaction_id,
            "user_id": evaluation.user_id,
            "risk_level": evaluation.risk_level.name,
            "reasons": evaluation.reasons,
            "timestamp": evaluation.timestamp,
            "status": evaluation.status,
            "reviewed_by": evaluation.reviewed_by,
            "reviewed_at": evaluation.reviewed_at,
        }
        self.evaluations.insert_one(document)

    async def get_all_evaluations(self) -> List[FraudEvaluation]:
        """
        Obtiene todas las evaluaciones ordenadas por timestamp descendente
        
        Nota del desarrollador:
        La IA sugirió retornar los documentos directamente. Agregué conversión
        a entidades FraudEvaluation para mantener el Domain Model en toda
        la aplicación y evitar "Primitive Obsession".
        """
        documents = self.evaluations.find().sort("timestamp", -1)
        return [self._document_to_evaluation(doc) for doc in documents]

    async def get_evaluation_by_id(
        self, transaction_id: str
    ) -> Optional[FraudEvaluation]:
        """
        Obtiene una evaluación específica por ID
        """
        document = self.evaluations.find_one({"transaction_id": transaction_id})
        if document is None:
            return None
        return self._document_to_evaluation(document)

    def get_evaluations_by_user(self, user_id: str) -> List[FraudEvaluation]:
        """
        Obtiene todas las evaluaciones de un usuario específico
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de evaluaciones ordenadas por timestamp descendente
        """
        documents = self.evaluations.find({"user_id": user_id}).sort("timestamp", -1)
        return [self._document_to_evaluation(doc) for doc in documents]

    async def update_evaluation(self, evaluation: FraudEvaluation) -> None:
        """
        Actualiza una evaluación existente
        
        Raises:
            ValueError: Si la evaluación no existe
        """
        result = self.evaluations.update_one(
            {"transaction_id": evaluation.transaction_id},
            {
                "$set": {
                    "status": evaluation.status,
                    "reviewed_by": evaluation.reviewed_by,
                    "reviewed_at": evaluation.reviewed_at,
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError(f"Transaction {evaluation.transaction_id} not found")

    def _document_to_evaluation(self, document: dict) -> FraudEvaluation:
        """
        Convierte un documento de MongoDB a entidad FraudEvaluation
        
        Nota del desarrollador:
        La IA olvidó manejar el enum RiskLevel. Agregué conversión explícita
        para evitar errores de tipos.
        """
        return FraudEvaluation(
            transaction_id=document["transaction_id"],
            user_id=document.get("user_id", "unknown"),
            risk_level=RiskLevel[document["risk_level"]],  # Usar RiskLevel[name] en lugar de RiskLevel(value)
            reasons=document["reasons"],
            timestamp=document["timestamp"],
            status=document.get("status", "PENDING_REVIEW"),
            reviewed_by=document.get("reviewed_by"),
            reviewed_at=document.get("reviewed_at"),
        )


class RedisAdapter(CacheService):
    """
    Adaptador de Redis que implementa CacheService
    
    Usa redis.asyncio para operaciones asíncronas reales
    """

    def __init__(self, connection_string: str, ttl: int) -> None:
        """
        Inicializa el adaptador de Redis
        
        Args:
            connection_string: URL de conexión a Redis
            ttl: Tiempo de vida por defecto en segundos
        """
        self.redis = redis_async.from_url(connection_string, decode_responses=True)
        self.ttl = ttl

    async def get_user_location(self, user_id: str) -> Optional[dict]:
        """
        Obtiene la ubicación histórica del usuario
        
        Nota del desarrollador:
        La IA sugirió almacenar como string separado por comas.
        Lo cambié a JSON para ser más robusto y extensible.
        """
        data = await self.redis.get(f"user:{user_id}:location")
        if data is None:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    async def set_user_location(
        self, user_id: str, latitude: float, longitude: float, ttl: int = None
    ) -> None:
        """
        Almacena la ubicación del usuario en caché
        """
        if ttl is None:
            ttl = self.ttl

        location_data = json.dumps({"latitude": latitude, "longitude": longitude})
        await self.redis.setex(f"user:{user_id}:location", ttl, location_data)

    async def get_threshold_config(self) -> Optional[dict]:
        """
        Obtiene la configuración de umbrales desde caché (HU-008/009)
        """
        data = await self.redis.get("config:thresholds")
        if data is None:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    async def set_threshold_config(
        self, amount_threshold: float, location_radius_km: float
    ) -> None:
        """
        Almacena la configuración de umbrales en caché
        
        Nota del desarrollador:
        La IA sugirió no usar TTL para configuración. Agregué TTL
        de 1 año para evitar que Redis lo elimine por falta de uso,
        pero permitir limpieza eventual si el sistema se reconfigura.
        """
        config_data = json.dumps(
            {
                "amount_threshold": amount_threshold,
                "location_radius_km": location_radius_km,
            }
        )
        # TTL de 1 año (31536000 segundos)
        await self.redis.setex("config:thresholds", 31536000, config_data)


class RabbitMQAdapter(MessagePublisher):
    """
    Adaptador de RabbitMQ que implementa MessagePublisher
    
    Nota del desarrollador:
    La IA sugirió usar pika asíncrono (aio-pika). Para el MVP usé
    pika bloqueante para simplicidad. Se puede migrar a aio-pika
    después si el rendimiento lo requiere (premature optimization is evil).
    """

    def __init__(self, connection_string: str) -> None:
        """
        Inicializa el adaptador de RabbitMQ
        
        Args:
            connection_string: URL de conexión a RabbitMQ
        """
        self.connection_string = connection_string
        self._connection = None
        self._channel = None
        self._ensure_connection()

    def _ensure_connection(self) -> None:
        """
        Asegura que la conexión está activa
        
        Nota del desarrollador:
        La IA no contempló reconexión. Agregué lógica para verificar
        y restablecer conexión si está cerrada (resilience pattern).
        """
        if self._connection is None or self._connection.is_closed:
            self._connection = pika.BlockingConnection(
                pika.URLParameters(self.connection_string)
            )
            self._channel = self._connection.channel()

            # Declarar colas (idempotente)
            self._channel.queue_declare(
                queue=settings.rabbitmq_transactions_queue, durable=True
            )
            self._channel.queue_declare(
                queue=settings.rabbitmq_manual_review_queue, durable=True
            )

    async def publish_transaction_for_processing(
        self, transaction_data: dict
    ) -> None:
        """
        Publica una transacción en la cola de procesamiento
        
        Nota del desarrollador:
        La IA sugirió no persistir los mensajes (delivery_mode=1).
        Lo cambié a delivery_mode=2 para que los mensajes sobrevivan
        reinicios de RabbitMQ (durability).
        """
        self._ensure_connection()

        self._channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_transactions_queue,
            body=json.dumps(transaction_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
                content_type="application/json",
            ),
        )

    async def publish_for_manual_review(self, evaluation_data: dict) -> None:
        """
        Publica una evaluación en la cola de revisión manual (HU-010)
        """
        self._ensure_connection()

        self._channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_manual_review_queue,
            body=json.dumps(evaluation_data),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

    def close(self) -> None:
        """
        Cierra la conexión a RabbitMQ
        
        Nota del desarrollador:
        La IA olvidó agregar un método de limpieza. Lo agregué para
        liberar recursos correctamente (resource management pattern).
        """
        if self._connection and not self._connection.is_closed:
            self._connection.close()
