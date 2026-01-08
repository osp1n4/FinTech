"""
RabbitMQ Adapter - Implementación concreta de MessagePublisher

Cumplimiento SOLID:
- Dependency Inversion: Implementa la interface MessagePublisher
- Single Responsibility: Solo maneja mensajería con RabbitMQ
"""
import pika
import json
from typing import Optional


class RabbitMQAdapter:
    """Adaptador de RabbitMQ que implementa MessagePublisher"""

    def __init__(
        self,
        rabbitmq_url: str,
        transactions_queue: str,
        manual_review_queue: str,
    ) -> None:
        """
        Inicializa el adaptador de RabbitMQ
        
        Args:
            rabbitmq_url: URL de conexión a RabbitMQ
            transactions_queue: Nombre de la cola de transacciones
            manual_review_queue: Nombre de la cola de revisión manual
        """
        self.rabbitmq_url = rabbitmq_url
        self.transactions_queue = transactions_queue
        self.manual_review_queue = manual_review_queue
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

    def connect(self) -> None:
        """Establece conexión con RabbitMQ"""
        parameters = pika.URLParameters(self.rabbitmq_url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declarar colas
        self.channel.queue_declare(queue=self.transactions_queue, durable=True)
        self.channel.queue_declare(queue=self.manual_review_queue, durable=True)

    def disconnect(self) -> None:
        """Cierra conexión con RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    async def publish_transaction_for_processing(
        self, transaction_data: dict
    ) -> None:
        """Publica una transacción en la cola para procesamiento"""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        message = json.dumps(transaction_data)
        self.channel.basic_publish(
            exchange="",
            routing_key=self.transactions_queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
            ),
        )

    async def publish_for_manual_review(self, evaluation_data: dict) -> None:
        """Publica una evaluación en la cola de revisión manual"""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        message = json.dumps(evaluation_data)
        self.channel.basic_publish(
            exchange="",
            routing_key=self.manual_review_queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
            ),
        )
