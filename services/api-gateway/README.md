# API Gateway Service

## 🎯 Responsabilidad

Punto de entrada principal para todas las requests HTTP externas. Maneja routing, autenticación, rate limiting y documentación de API.

## 🏗️ Arquitectura

```
api-gateway/
├── src/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── transactions.py      # Endpoints de transacciones
│   │   ├── audit.py             # Endpoints de auditoría
│   │   ├── review.py            # Endpoints de revisión manual
│   │   └── config.py            # Endpoints de configuración
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py              # Autenticación
│   │   ├── rate_limit.py        # Rate limiting
│   │   └── logging.py           # Logging
│   ├── dependencies.py          # Dependency injection
│   └── main.py                  # FastAPI App
├── tests/
│   ├── test_routes.py
│   └── test_middleware.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 📡 Endpoints

### Transacciones
- `POST /transaction` - Recibir transacción (202 Accepted)
- `GET /transaction/:id` - Consultar transacción específica

### Auditoría
- `GET /audit/all` - Listar todas las evaluaciones
- `GET /audit/pending` - Listar pendientes de revisión
- `GET /audit/high-risk` - Listar alto riesgo

### Revisión Manual
- `PUT /transaction/:id/review` - Aplicar decisión manual
- `POST /transaction/:id/comment` - Agregar comentario

### Configuración
- `GET /config/thresholds` - Consultar umbrales
- `PUT /config/thresholds` - Actualizar umbrales
- `GET /config/strategies` - Listar estrategias activas
- `PUT /config/strategies` - Activar/desactivar estrategias

### Health & Metrics
- `GET /health` - Health check
- `GET /metrics` - Métricas Prometheus

## 🔄 Flujo de Request

```
Cliente → API Gateway → RabbitMQ → Worker → Fraud Evaluation Service
                 ↓
             MongoDB/Redis (query directo)
```

## 🚀 Ejecución

```bash
# Desarrollo
cd services/api-gateway
poetry install
poetry run uvicorn src.main:app --reload --port 8000

# Docker
docker build -t fraud-api-gateway .
docker run -p 8000:8000 fraud-api-gateway

# Docker Compose
docker-compose up api-gateway
```

## 🔐 Autenticación

- JWT tokens para endpoints administrativos
- API keys para integraciones
- Rate limiting por IP/usuario

## 📊 Métricas

- Request count por endpoint
- Latency promedio
- Error rate
- Active connections

## 🧪 Tests

```bash
poetry run pytest tests/ -v
poetry run pytest tests/ --cov=src
```

---

**Puerto:** 8000  
**Tecnología:** FastAPI + Uvicorn  
**Dependencias:** RabbitMQ, MongoDB, Redis
