# 🛡️ Fraud Detection Engine

Motor de detección de fraude implementado con **Clean Architecture**, principios **SOLID** y patrón de diseño **Strategy**.

## 🏗️ Arquitectura

### Capas

- **Domain**: Entidades, Value Objects y Estrategias de fraude (sin dependencias externas)
- **Application**: Casos de uso y puertos (interfaces)
- **Infrastructure**: Adaptadores (FastAPI, MongoDB, Redis, RabbitMQ)

### Principios SOLID

✅ **0 violaciones SOLID**

- **S** (Single Responsibility): Cada clase tiene una única razón para cambiar
- **O** (Open/Closed): Extensible mediante Strategy Pattern sin modificar código existente
- **L** (Liskov Substitution): Las estrategias son intercambiables
- **I** (Interface Segregation): Interfaces específicas para cada puerto
- **D** (Dependency Inversion): Los casos de uso dependen de abstracciones, no de implementaciones

## 🎯 Historias de Usuario Implementadas

- **HU-001**: API de recepción de transacciones (202 Accepted)
- **HU-002**: Auditoría de evaluaciones
- **HU-003**: Regla de umbral de monto (>$1,500)
- **HU-005**: Regla de ubicación inusual (>100 km)
- **HU-008**: Modificación de umbrales sin redespliegue
- **HU-009**: Consulta de configuración actual
- **HU-010**: Human in the Loop (revisión manual)

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- Docker Desktop (debe estar corriendo)
- Poetry (opcional, para desarrollo local)

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Verificar que Docker Desktop esté corriendo
docker --version

# 2. Levantar todos los servicios
docker-compose up -d

# 3. Verificar que los contenedores estén corriendo
docker-compose ps

# 4. Ver logs
docker-compose logs -f

# 5. Acceder a la API
# http://localhost:8000/docs (Swagger UI)

# 6. Acceder al frontend (en otra terminal)
# Instalar Poetry si no lo tienes
pip install poetry

# Instalar dependencias
poetry install

# Ejecutar Streamlit
poetry run streamlit run demo/streamlit_app.py
```

### Opción 2: Desarrollo Local

```bash
# 1. Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Instalar dependencias
poetry install

# 3. Copiar variables de entorno
copy .env.example .env

# 4. Levantar solo las bases de datos
docker-compose up -d mongodb redis rabbitmq

# 5. Ejecutar API
poetry run uvicorn src.infrastructure.api.main:app --reload

# 6. Ejecutar Worker (en otra terminal)
poetry run python -m src.infrastructure.worker

# 7. Ejecutar frontend (en otra terminal)
poetry run streamlit run demo/streamlit_app.py
```

## 🧪 Testing

El proyecto sigue **TDD/BDD** estricto:

```bash
# Tests unitarios
poetry run pytest tests/unit -v

# Tests de integración
poetry run pytest tests/integration -v

# Cobertura
poetry run pytest --cov=src --cov-report=html
```

## 📊 Reglas de Fraude

1. **Umbral de Monto**: Transacciones > $1,500 USD se marcan como HIGH_RISK
2. **Ubicación Inusual**: Transacciones > 100 km del radio habitual se marcan como sospechosas

## 🔧 Endpoints API

- `POST /transaction` - Enviar transacción para evaluación (202 Accepted)
- `GET /audit/all` - Consultar todas las evaluaciones
- `GET /audit/transaction/{id}` - Consultar evaluación específica
- `PUT /transaction/review/{id}` - Revisar transacción manualmente
- `GET /config/thresholds` - Consultar configuración actual
- `PUT /config/thresholds` - Actualizar umbrales

## 📝 Licencia

MIT License
