"""
RabbitMQ Worker - Consumidor de mensajes para procesamiento asíncrono
Ejecuta los casos de uso al recibir mensajes de la cola

Cumple Single Responsibility: Solo consume mensajes y ejecuta casos de uso

Nota del desarrollador (María Gutiérrez):
La IA sugirió procesar los mensajes en el mismo hilo. Agregué manejo
de errores y dead letter queue para mayor resiliencia.

Actualización: Ahora usa HTTP client para comunicarse con fraud-evaluation-service
en lugar de imports directos.
"""
import pika
import json
import requests
from src.config import settings


def call_fraud_evaluation_service(transaction_data: dict) -> dict:
    """
    Llama al servicio de evaluación de fraude vía HTTP
    
    Args:
        transaction_data: Datos de la transacción
    
    Returns:
        Dict con el resultado de la evaluación
    
    Raises:
        requests.RequestException: Si falla la comunicación
    """
    try:
        fraud_service_url = settings.fraud_evaluation_service_url
        response = requests.post(
            f"{fraud_service_url}/api/v1/evaluate",
            json=transaction_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Error calling fraud evaluation service: {str(e)}")


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
    
    Actualización: Ahora llama al fraud-evaluation-service vía HTTP.
    """
    try:
        transaction_data = json.loads(body)
        print(f"Processing transaction: {transaction_data['id']}")

        # Llamar al servicio de evaluación
        result = call_fraud_evaluation_service(transaction_data)

        print(
            f"Transaction {transaction_data['id']} evaluated as {result.get('risk_level')}"
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
