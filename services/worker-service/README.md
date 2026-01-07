# Worker Service

## 🎯 Responsabilidad

Consumidor de mensajes RabbitMQ que procesa transacciones de manera asíncrona. Coordina la evaluación de fraude y persiste los resultados.

## 🏗️ Arquitectura

```
worker-service/
├── src/
│   ├── consumer/
│   │   ├── __init__.py
│   │   └── rabbitmq_consumer.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── transaction_processor.py
│   │   └── review_processor.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── mongodb_adapter.py
│   │   ├── redis_adapter.py
│   │   └── fraud_service_client.py
│   ├── config.py
│   └── worker.py               # Main entry point
├── tests/
│   ├── test_consumer.py
│   └── test_processors.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 🔄 Flujo de Procesamiento

```
1. Consumir mensaje de RabbitMQ (queue: fraud_evaluations)
2. Deserializar payload
3. Llamar a Fraud Evaluation Service
4. Guardar resultado en MongoDB
5. Actualizar caché en Redis
6. ACK mensaje
7. (Si error) → NACK + Dead Letter Queue
```

## 📡 Queues de RabbitMQ

### fraud_evaluations
- **Propósito:** Transacciones nuevas a evaluar
- **Prefetch:** 1 (fair dispatch)
- **Durable:** Sí
- **TTL:** 1 hora

### fraud_reviews
- **Propósito:** Decisiones manuales de analistas
- **Prefetch:** 1
- **Durable:** Sí

### fraud_dlq (Dead Letter Queue)
- **Propósito:** Mensajes que fallaron después de N reintentos
- **Análisis:** Manual o batch reprocessing

## 🔁 Retry Logic

Implementa backoff exponencial con max retries:

```python
max_retries = 10
retry_delay = 2 segundos
backoff = exponencial (2^n)
```

## 🚨 Manejo de Errores

1. **Errores transitorios** (network, timeout):
   - Retry automático con backoff
   - Max 10 intentos

2. **Errores permanentes** (validation, business logic):
   - Log error
   - Enviar a DLQ
   - Notificar equipo

3. **Errores de conexión**:
   - Reconectar automáticamente
   - Esperar healthcheck de RabbitMQ

## 🚀 Ejecución

```bash
# Desarrollo
cd services/worker-service
poetry install
poetry run python src/worker.py

# Docker
docker build -t fraud-worker-service .
docker run fraud-worker-service

# Docker Compose
docker-compose up worker-service
```

## 📊 Escalabilidad

Múltiples workers pueden ejecutarse en paralelo:

```bash
# 3 workers procesando en paralelo
docker-compose up --scale worker-service=3
```

Cada worker:
- Procesa 1 mensaje a la vez (prefetch_count=1)
- Distribuye carga automáticamente (round-robin)
- Es stateless (puede detenerse/reiniciarse sin pérdida)

## 🔐 Resiliencia

- **Idempotencia:** Mismo mensaje puede procesarse múltiples veces sin duplicados
- **Circuit Breaker:** Si Fraud Evaluation Service falla, espera antes de reintentar
- **Graceful Shutdown:** Al recibir SIGTERM, termina de procesar mensajes actuales

## 📊 Métricas

- Mensajes procesados/segundo
- Latency promedio de procesamiento
- Error rate
- Queue depth (RabbitMQ)
- Workers activos

## 🧪 Tests

```bash
poetry run pytest tests/ -v
poetry run pytest tests/ --cov=src
```

## 🐞 Debugging

```bash
# Ver logs en tiempo real
docker logs -f fraud-worker-service

# Ver mensajes en RabbitMQ Management
http://localhost:15672
# Usuario: fraud, Password: fraud2026
```

---

**Tecnología:** Python + Pika (RabbitMQ)  
**Pattern:** Consumer/Worker  
**Escalable:** Sí (horizontal)  
**Stateless:** Sí
