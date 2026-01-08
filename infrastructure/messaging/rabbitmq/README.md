# RabbitMQ Configuration

Este directorio contiene configuraciones para RabbitMQ.

## Estructura de Mensajería

### Exchanges

#### fraud_exchange (topic)
- **Tipo**: Topic exchange
- **Durable**: Sí
- **Propósito**: Routing de mensajes de fraude

### Queues

#### 1. transactions
- **Propósito**: Cola para procesamiento de transacciones
- **TTL**: 1 hora (3,600,000 ms)
- **Max Length**: 10,000 mensajes
- **Routing Key**: `transaction.evaluate`
- **Consumidor**: worker-service

#### 2. manual_review
- **Propósito**: Cola para revisión manual de analistas
- **TTL**: 24 horas (86,400,000 ms)
- **Max Length**: 5,000 mensajes
- **Routing Key**: `transaction.review`
- **Consumidor**: worker-service / admin-dashboard

#### 3. notifications
- **Propósito**: Cola para notificaciones a usuarios
- **TTL**: 30 minutos (1,800,000 ms)
- **Max Length**: 1,000 mensajes
- **Routing Key**: `notification.*`
- **Consumidor**: notification-service (futuro)

#### 4. dead_letter
- **Propósito**: Cola para mensajes fallidos (DLQ)
- **Routing Key**: `dead_letter`
- **Uso**: Debugging y recuperación de errores

## Patrones de Routing

```
fraud_exchange (topic)
├── transaction.evaluate → transactions queue
├── transaction.review → manual_review queue
├── notification.email → notifications queue
├── notification.sms → notifications queue
└── notification.push → notifications queue
```

## Dead Letter Exchange (DLX)

Mensajes que fallan después de reintentos van a `dead_letter` queue:

```
Original Queue (con x-dead-letter-exchange)
    ↓ (failure después de reintentos)
dlx_exchange
    ↓
dead_letter queue
```

## High Availability (HA)

Policy `ha-all` aplicada a todas las queues:
- **ha-mode**: all (réplicas en todos los nodos)
- **ha-sync-mode**: automatic (sincronización automática)

## Uso en Docker

```yaml
rabbitmq:
  volumes:
    - ./infrastructure/messaging/rabbitmq/definitions.json:/etc/rabbitmq/definitions.json
  environment:
    - RABBITMQ_DEFAULT_USER=fraud
    - RABBITMQ_DEFAULT_PASS=fraud2026
```

## Management UI

- **URL**: http://localhost:15672
- **Usuario**: fraud
- **Password**: fraud2026

## Ejemplos de Publicación

### Python (Pika)
```python
import pika
import json

connection = pika.BlockingConnection(
    pika.URLParameters('amqp://fraud:fraud2026@localhost:5672')
)
channel = connection.channel()

# Publicar transacción para evaluación
message = {
    "id": "txn_12345",
    "amount": 1500.00,
    "user_id": "user_001"
}

channel.basic_publish(
    exchange='fraud_exchange',
    routing_key='transaction.evaluate',
    body=json.dumps(message),
    properties=pika.BasicProperties(
        delivery_mode=2,  # Persistente
    )
)
```

## Monitoreo

### Ver estado de queues
```bash
docker exec rabbitmq rabbitmqctl list_queues name messages consumers
```

### Ver exchanges
```bash
docker exec rabbitmq rabbitmqctl list_exchanges
```

### Ver bindings
```bash
docker exec rabbitmq rabbitmqctl list_bindings
```
