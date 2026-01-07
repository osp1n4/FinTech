# 🚀 Guía de Instalación y Ejecución

## Requisitos Previos

- **Python 3.11+**
- **Docker y Docker Compose**
- **Git**

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd fraud-detection-engine
```

### 2. Instalar Poetry (gestor de dependencias)

#### Windows (PowerShell)
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Linux/macOS
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Agregar Poetry al PATH según instrucciones que aparezcan.

### 3. Instalar dependencias del proyecto

```bash
poetry install
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` si es necesario (los valores por defecto funcionan para desarrollo local).

## Ejecución

### Opción 1: Con Docker Compose (Recomendado)

#### Levantar todos los servicios

```bash
docker-compose up -d
```

Esto iniciará:
- MongoDB (puerto 27017)
- Redis (puerto 6379)
- RabbitMQ (puerto 5672, UI en puerto 15672)
- API REST (puerto 8000)
- Worker

#### Verificar que los servicios están corriendo

```bash
docker-compose ps
```

#### Ver logs

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api
docker-compose logs -f worker
```

#### Detener servicios

```bash
docker-compose down
```

#### Eliminar volúmenes (datos)

```bash
docker-compose down -v
```

### Opción 2: Ejecución Local (Sin Docker)

#### 1. Levantar solo las bases de datos con Docker

```bash
docker-compose up -d mongodb redis rabbitmq
```

#### 2. Ejecutar la API localmente

```bash
poetry run uvicorn src.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Ejecutar el Worker localmente (en otra terminal)

```bash
poetry run python -m src.infrastructure.worker
```

#### 4. Ejecutar la demo de Streamlit (en otra terminal)

```bash
poetry run streamlit run demo/streamlit_app.py
```

## Testing

### Ejecutar todos los tests

```bash
poetry run pytest -v
```

### Ejecutar solo tests unitarios

```bash
poetry run pytest tests/unit/ -v
```

### Ejecutar tests con cobertura

```bash
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing
```

Ver reporte de cobertura:
```bash
# Abrir en navegador
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### Validar arquitectura (Clean Architecture)

```bash
python scripts/validate_architecture.py
```

## Linters y Formateo

### Formatear código con Black

```bash
poetry run black src/ tests/
```

### Verificar formato sin cambiar archivos

```bash
poetry run black --check src/ tests/
```

### Ejecutar Pylint

```bash
poetry run pylint src/
```

### Ejecutar MyPy (type checking)

```bash
poetry run mypy src/ --ignore-missing-imports
```

## Acceso a Servicios

### API REST
- **URL:** http://localhost:8000
- **Docs interactivos (Swagger):** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

### RabbitMQ Management UI
- **URL:** http://localhost:15672
- **Usuario:** `fraud`
- **Password:** `fraud2026`

### Demo Streamlit
- **URL:** http://localhost:8501 (si se ejecuta localmente)

## Endpoints de la API

### Evaluar Transacción (HU-001)
```bash
POST /transaction
Content-Type: application/json

{
  "id": "txn_001",
  "amount": 2000.00,
  "user_id": "user_123",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

### Consultar Auditoría (HU-002)
```bash
GET /audit/all
```

### Consultar Transacción Específica
```bash
GET /audit/transaction/{transaction_id}
```

### Revisar Transacción Manualmente (HU-010)
```bash
PUT /transaction/review/{transaction_id}
Content-Type: application/json
X-Analyst-ID: analyst_001

{
  "decision": "APPROVED"
}
```

### Consultar Configuración (HU-009)
```bash
GET /config/thresholds
```

### Actualizar Configuración (HU-008)
```bash
PUT /config/thresholds
Content-Type: application/json
X-Analyst-ID: analyst_001

{
  "amount_threshold": 2000.00,
  "location_radius_km": 150.0
}
```

## Ejemplos de Uso con curl

### Transacción de ALTO RIESGO (monto > $1,500)
```bash
curl -X POST http://localhost:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "id": "txn_high_risk",
    "amount": 3000.00,
    "user_id": "user_456",
    "location": {"latitude": 40.7128, "longitude": -74.0060}
  }'
```

### Transacción de BAJO RIESGO (monto < $1,500)
```bash
curl -X POST http://localhost:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "id": "txn_low_risk",
    "amount": 500.00,
    "user_id": "user_789",
    "location": {"latitude": 40.7128, "longitude": -74.0060}
  }'
```

### Consultar todas las evaluaciones
```bash
curl http://localhost:8000/audit/all
```

### Aprobar una transacción
```bash
curl -X PUT http://localhost:8000/transaction/review/txn_high_risk \
  -H "Content-Type: application/json" \
  -H "X-Analyst-ID: analyst_demo" \
  -d '{"decision": "APPROVED"}'
```

## Troubleshooting

### Error: "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Error: "Cannot connect to MongoDB/Redis/RabbitMQ"
Verificar que los contenedores están corriendo:
```bash
docker-compose ps
```

Reiniciar servicios:
```bash
docker-compose restart
```

### Error: "Module not found"
Reinstalar dependencias:
```bash
poetry install --no-cache
```

### Tests fallan
Verificar que las bases de datos de test estén disponibles:
```bash
docker-compose up -d mongodb redis rabbitmq
```

## Estructura del Proyecto

```
fraud-detection-engine/
├── src/
│   ├── domain/              # Capa Domain (sin dependencias)
│   │   ├── models.py        # Entidades y Value Objects
│   │   └── strategies/      # Patrón Strategy
│   ├── application/         # Capa Application
│   │   ├── interfaces.py    # Puertos (interfaces)
│   │   └── use_cases.py     # Casos de uso
│   └── infrastructure/      # Capa Infrastructure
│       ├── adapters.py      # MongoDB, Redis, RabbitMQ
│       ├── config.py        # Configuración
│       ├── worker.py        # Worker RabbitMQ
│       └── api/             # FastAPI
├── tests/
│   ├── unit/                # Tests unitarios (TDD)
│   └── integration/         # Tests de integración
├── demo/
│   └── streamlit_app.py     # UI de demostración
├── scripts/
│   └── validate_architecture.py  # Validación de arquitectura
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Recursos Adicionales

- **Documentación de FastAPI:** https://fastapi.tiangolo.com/
- **Documentación de RabbitMQ:** https://www.rabbitmq.com/
- **Clean Architecture:** https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **SOLID Principles:** https://en.wikipedia.org/wiki/SOLID

## Soporte

Para reportar bugs o solicitar features, crear un issue en GitHub.
