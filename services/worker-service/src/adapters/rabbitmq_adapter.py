"""
RabbitMQ Adapter - Implementación de MessagePublisher

Cumplimiento SOLID:
- Single Responsibility: Solo maneja publicación de mensajes
- Dependency Inversion: Implementa interface MessagePublisher
- Open/Closed: Extensible sin modificar código existente

Nota del desarrollador (María Gutiérrez):
Extraído de adapters.py para mejor organización.
La IA sugirió usar pika asíncrono (aio-pika). Para el MVP usé
pika bloqueante para simplicidad. Se puede migrar a aio-pika
después si el rendimiento lo requiere (premature optimization is evil).
"""
import json
import pika

from src.application.interfaces import MessagePublisher
from src.infrastructure.config import settings


class RabbitMQAdapter(MessagePublisher):
    """
    Adaptador de RabbitMQ que implementa MessagePublisher
    
    Usa pika bloqueante para simplicidad en el MVP
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
