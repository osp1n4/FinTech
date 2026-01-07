# Fraud Evaluation Service

## 🎯 Responsabilidad

Servicio core de evaluación de fraude. Contiene toda la lógica de negocio (Domain Layer) y aplica las estrategias de detección.

## 🏗️ Arquitectura Clean Architecture

```
fraud-evaluation-service/
├── src/
│   ├── domain/                   # ✅ Domain Layer (0 dependencias)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py
│   │   │   ├── evaluation.py
│   │   │   └── value_objects.py
│   │   └── strategies/           # Strategy Pattern
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── amount_threshold.py
│   │       ├── location_check.py
│   │       ├── velocity_check.py
│   │       └── impossible_travel.py
│   ├── application/              # ✅ Application Layer (casos de uso)
│   │   ├── __init__.py
│   │   ├── interfaces.py         # Puertos
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── evaluate_transaction.py
│   │       └── review_transaction.py
│   ├── infrastructure/           # ✅ Infrastructure Layer (adaptadores)
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   └── routes.py
│   │   └── adapters/
│   │       ├── __init__.py
│   │       └── redis_adapter.py
│   └── config.py
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   └── application/
│   └── integration/
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 🎯 Estrategias de Fraude Implementadas

### 1. Amount Threshold Strategy
Detecta transacciones que exceden un umbral de monto.
- **Umbral default:** $1,500
- **Riesgo:** HIGH_RISK
- **Configurable:** Sí (sin redespliegue)

### 2. Location Check Strategy
Detecta ubicaciones inusuales (>100 km del último registro).
- **Radio:** 100 km
- **Algoritmo:** Haversine formula
- **Riesgo:** MEDIUM_RISK

### 3. Velocity Check Strategy (Futuro)
Detecta frecuencia anormal de transacciones.

### 4. Impossible Travel Strategy (Futuro)
Detecta viajes físicamente imposibles entre transacciones.

## 📡 API Endpoints

### Evaluación
- `POST /evaluate` - Evaluar transacción
- `POST /evaluate/batch` - Evaluar lote de transacciones

### Estrategias
- `GET /strategies` - Listar estrategias disponibles
- `GET /strategies/:id` - Detalles de estrategia
- `PUT /strategies/:id/config` - Configurar estrategia

### Health
- `GET /health` - Health check

## 🔄 Flujo de Evaluación

```
1. Recibir Transaction
2. Cargar estrategias activas
3. Ejecutar cada estrategia
4. Combinar resultados
5. Determinar nivel de riesgo
6. Retornar FraudEvaluation
```

## 🚀 Ejecución

```bash
# Desarrollo
cd services/fraud-evaluation-service
poetry install
poetry run uvicorn src.infrastructure.api.main:app --reload --port 8001

# Docker
docker build -t fraud-evaluation-service .
docker run -p 8001:8001 fraud-evaluation-service

# Docker Compose
docker-compose up fraud-evaluation-service
```

## 🧪 Tests (TDD/BDD)

```bash
# Tests unitarios (Domain + Application)
poetry run pytest tests/unit/ -v

# Con cobertura (>=70% requerido)
poetry run pytest tests/unit/ --cov=src --cov-fail-under=70

# Tests de integración
poetry run pytest tests/integration/ -v
```

## 🎨 Principios SOLID

✅ **Single Responsibility:** Cada estrategia tiene una responsabilidad  
✅ **Open/Closed:** Extensible con nuevas estrategias sin modificar código  
✅ **Liskov Substitution:** Todas las estrategias son intercambiables  
✅ **Interface Segregation:** Interfaces específicas (CacheService, etc.)  
✅ **Dependency Inversion:** Use cases dependen de abstracciones

## 📊 Escalabilidad

Este servicio puede escalarse horizontalmente:

```bash
docker-compose up --scale fraud-evaluation-service=3
```

Cada instancia es stateless y puede procesar requests independientemente.

---

**Puerto:** 8001  
**Tecnología:** Python + FastAPI  
**Patrón:** Strategy + Clean Architecture  
**SOLID:** 0 violaciones
