"""
RabbitMQ Worker - Consumidor de mensajes para procesamiento asíncrono
Ejecuta los casos de uso al recibir mensajes de la cola

Cumple Single Responsibility: Solo consume mensajes y ejecuta casos de uso

Nota del desarrollador (María Gutiérrez):
La IA sugirió procesar los mensajes en el mismo hilo. Agregué manejo
de errores y dead letter queue para mayor resiliencia.
"""
import pika
import json
import asyncio
from decimal import Decimal
from src.adapters import (
    MongoDBAdapter,
    RedisAdapter,
    RabbitMQAdapter,
)
from src.config import settings
from src.domain.strategies.amount_threshold import AmountThresholdStrategy
from src.domain.strategies.location_check import LocationStrategy
from src.domain.strategies.device_validation import DeviceValidationStrategy
from src.domain.strategies.rapid_transaction import RapidTransactionStrategy
from src.domain.strategies.unusual_time import UnusualTimeStrategy
from src.application.use_cases import EvaluateTransactionUseCase


def create_use_case() -> EvaluateTransactionUseCase:
    """
    Crea el caso de uso con todas sus dependencias
    
    Nota del desarrollador:
    La IA sugirió crear esto en cada callback. Lo extraje a una función
    para cumplir con DRY y facilitar testing.
    """
    repository = MongoDBAdapter(settings.mongodb_url, settings.mongodb_database)
    publisher = RabbitMQAdapter(settings.rabbitmq_url)
    cache = RedisAdapter(settings.redis_url, settings.redis_ttl)

    strategies = [
        AmountThresholdStrategy(threshold=Decimal(str(settings.amount_threshold))),
        LocationStrategy(radius_km=settings.location_radius_km),
        DeviceValidationStrategy(redis_client=cache.redis_sync),
        RapidTransactionStrategy(redis_client=cache.redis_sync),
        UnusualTimeStrategy(audit_repository=repository),
    ]

    return EvaluateTransactionUseCase(repository, publisher, cache, strategies)


def callback(ch, method, properties, body):
    """
    Callback para procesar mensajes de la cola
    
    Args:
        ch: Canal de RabbitMQ
        method: Método de entrega
        properties: Propiedades del mensaje
        body: Cuerpo del mensaje (JSON)
    
    Nota del desarrollador:
    La IA olvidó agregar manejo de errores. Agregué try/except para
    evitar que un mensaje corrupto detenga el worker (resilience pattern).
    """
    try:
        transaction_data = json.loads(body)
        print(f"Processing transaction: {transaction_data['id']}")

        # Ejecutar caso de uso
        use_case = create_use_case()
        result = asyncio.run(use_case.execute(transaction_data))

        print(
            f"Transaction {transaction_data['id']} evaluated as {result['risk_level']}"
        )

        # Acknowledge el mensaje
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in message: {e}")
        # Rechazar mensaje y no reencolar (está corrupto)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except ValueError as e:
        print(f"Error: Invalid transaction data: {e}")
        # Rechazar mensaje y no reencolar (datos inválidos)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        print(f"Error processing transaction: {e}")
        # Rechazar mensaje y reencolar (error temporal, puede recuperarse)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_worker():
    """
    Inicia el worker que consume mensajes de RabbitMQ
    
    Nota del desarrollador:
    La IA sugirió basic_consume sin prefetch_count. Agregué prefetch_count=1
    para evitar que un worker acumule todos los mensajes y distribuir
    la carga equitativamente (fair dispatch pattern).
    
    También agregué retry logic con backoff exponencial porque el worker puede
    iniciar antes de que RabbitMQ esté completamente listo (race condition).
    """
    import time
    
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Connecting to RabbitMQ: {settings.rabbitmq_url} (attempt {attempt + 1}/{max_retries})")
            connection = pika.BlockingConnection(
                pika.URLParameters(settings.rabbitmq_url)
            )
            channel = connection.channel()

            # Declarar cola (idempotente)
            channel.queue_declare(queue=settings.rabbitmq_transactions_queue, durable=True)

            # Prefetch count = 1: procesar un mensaje a la vez
            channel.basic_qos(prefetch_count=1)

            # Consumir mensajes
            channel.basic_consume(
                queue=settings.rabbitmq_transactions_queue, on_message_callback=callback
            )

            print(f"✅ Worker started successfully. Waiting for messages from {settings.rabbitmq_transactions_queue}")
            print("To exit press CTRL+C")

            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print("\nStopping worker...")
                channel.stop_consuming()
                connection.close()
                print("Worker stopped")
            
            break  # Salir del loop de retry si se conectó exitosamente
            
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"❌ Connection failed: {e}")
                print(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Backoff exponencial
            else:
                print(f"❌ Failed to connect after {max_retries} attempts")
                raise


if __name__ == "__main__":
    start_worker()
