# 🏗️ Arquitectura de Microservicios - Fraud Detection Engine

## 📁 Estructura del Proyecto

```
fraud-detection-engine/
├── services/                           # 🔷 Microservicios
│   ├── api-gateway/                    # API Gateway (FastAPI)
│   │   ├── src/
│   │   │   ├── routes/                 # Endpoints REST
│   │   │   ├── middleware/             # Middlewares
│   │   │   └── main.py                 # FastAPI App
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── fraud-evaluation-service/       # Servicio de Evaluación de Fraude
│   │   ├── src/
│   │   │   ├── domain/                 # Lógica de negocio
│   │   │   │   ├── models/             # Entidades
│   │   │   │   └── strategies/         # Strategy Pattern
│   │   │   ├── application/            # Casos de uso
│   │   │   └── interfaces/             # Puertos
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── worker-service/                 # Worker RabbitMQ
│   │   ├── src/
│   │   │   ├── consumer/               # Consumidor de mensajes
│   │   │   ├── processors/             # Procesadores
│   │   │   └── worker.py               # Worker principal
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── shared/                         # 📦 Código Compartido
│       ├── domain/                     # Domain Models compartidos
│       │   ├── models.py
│       │   └── strategies/
│       ├── config.py                   # Configuración compartida
│       ├── adapters.py                 # Adaptadores compartidos
│       └── interfaces.py               # Interfaces compartidas
│
├── infrastructure/                     # 🗄️ Infraestructura Externa
│   ├── databases/
│   │   ├── mongodb/
│   │   │   └── docker-compose.yml
│   │   └── init-scripts/
│   ├── messaging/
│   │   ├── rabbitmq/
│   │   │   └── docker-compose.yml
│   │   └── config/
│   └── cache/
│       ├── redis/
│       │   └── docker-compose.yml
│       └── config/
│
├── frontend/                           # 🎨 Frontend
│   ├── streamlit/
│   │   ├── app.py
│   │   ├── pages/
│   │   └── components/
│   └── Dockerfile
│
├── tests/                              # 🧪 Tests de Integración
│   ├── integration/
│   ├── e2e/
│   └── performance/
│
├── scripts/                            # 🛠️ Scripts de DevOps
│   ├── deploy/
│   ├── validate_architecture.py
│   └── setup.sh
│
├── .github/                            # 🔄 CI/CD
│   └── workflows/
│       ├── ci.yml
│       ├── deploy.yml
│       └── sonarqube.yml
│
├── docker-compose.yml                  # 🐳 Orquestación completa
├── docker-compose.dev.yml              # Desarrollo
├── docker-compose.prod.yml             # Producción
├── sonar-project.properties            # SonarQube
├── .env.example
├── README.md
└── ARCHITECTURE.md                     # Este archivo
```

## 🔷 Microservicios

### 1. API Gateway (`api-gateway`)
**Puerto:** 8000  
**Tecnología:** FastAPI  
**Responsabilidades:**
- Recibir requests HTTP
- Routing a servicios internos
- Autenticación y autorización
- Rate limiting
- API documentation (Swagger)

**Endpoints:**
- `POST /transaction` - Recibir transacción
- `GET /audit/all` - Consultar evaluaciones
- `PUT /transaction/:id/review` - Revisión manual
- `GET /config/thresholds` - Consultar configuración
- `PUT /config/thresholds` - Actualizar configuración

### 2. Fraud Evaluation Service (`fraud-evaluation-service`)
**Puerto:** 8001  
**Tecnología:** Python + Clean Architecture  
**Responsabilidades:**
- Evaluar transacciones con estrategias de fraude
- Aplicar Strategy Pattern (AmountThreshold, LocationCheck, etc.)
- Lógica de negocio pura (Domain Layer)
- Calcular nivel de riesgo

**Componentes:**
- **Domain Layer**: Entidades, Value Objects, Strategies
- **Application Layer**: Use Cases (EvaluateTransaction, ReviewTransaction)
- **Interfaces**: Puertos para persistencia y mensajería

### 3. Worker Service (`worker-service`)
**Tecnología:** Python + Pika (RabbitMQ)  
**Responsabilidades:**
- Consumir mensajes de RabbitMQ
- Procesar transacciones asíncronamente
- Actualizar estado en MongoDB
- Publicar resultados

**Características:**
- Retry logic con backoff exponencial
- Fair dispatch (prefetch_count=1)
- Manejo robusto de errores
- Dead letter queue

## 🗄️ Infraestructura Externa

### 1. MongoDB (`infrastructure/databases/mongodb`)
**Puerto:** 27017  
**Propósito:** Persistencia de evaluaciones

**Colecciones:**
- `evaluations`: Evaluaciones de fraude
- `configurations`: Umbrales configurables

### 2. RabbitMQ (`infrastructure/messaging/rabbitmq`)
**Puertos:** 5672 (AMQP), 15672 (Management)  
**Propósito:** Mensajería asíncrona

**Queues:**
- `fraud_evaluations`: Transacciones a evaluar
- `fraud_reviews`: Revisiones manuales

### 3. Redis (`infrastructure/cache/redis`)
**Puerto:** 6379  
**Propósito:** Caché de ubicaciones históricas y configuración

**Keys:**
- `user:<id>:location`: Última ubicación del usuario
- `config:thresholds`: Umbrales de fraude

## 📦 Shared (Código Compartido)

Código reutilizable entre microservicios:
- **Domain Models**: Transaction, FraudEvaluation, Location
- **Strategies**: FraudStrategy base class
- **Adapters**: MongoDB, Redis, RabbitMQ adapters
- **Config**: Pydantic Settings compartidas

## 🔄 Flujo de Comunicación

```
Cliente
  │
  ├──► API Gateway (8000)
  │      │
  │      ├──► Publish to RabbitMQ
  │      │      │
  │      │      └──► Worker Service
  │      │             │
  │      │             ├──► Fraud Evaluation Service (8001)
  │      │             │      │
  │      │             │      └──► Strategy Pattern
  │      │             │
  │      │             ├──► MongoDB (save)
  │      │             └──► Redis (cache)
  │      │
  │      └──► Query MongoDB (audit endpoints)
  │
  └──► Frontend (Streamlit)
```

## 🐳 Docker Compose

### Servicios Docker:
1. **mongodb** - Base de datos
2. **redis** - Caché
3. **rabbitmq** - Message broker
4. **api-gateway** - API REST
5. **fraud-evaluation** - Servicio de evaluación
6. **worker** - Procesador asíncrono
7. **frontend** - UI Streamlit

### Redes:
- `backend-network`: Microservicios internos
- `frontend-network`: Frontend ↔ API Gateway
- `data-network`: Bases de datos

## 🚀 Despliegue

### Desarrollo:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Producción:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Por Microservicio:
```bash
# Solo API Gateway
docker-compose up api-gateway

# Solo Worker
docker-compose up worker-service

# Solo Fraud Evaluation
docker-compose up fraud-evaluation-service
```

## 📊 Escalabilidad

Cada microservicio puede escalarse independientemente:

```bash
# Escalar workers
docker-compose up --scale worker-service=3

# Escalar API Gateway
docker-compose up --scale api-gateway=2

# Escalar Fraud Evaluation
docker-compose up --scale fraud-evaluation-service=2
```

## 🔐 Seguridad

- **API Gateway**: JWT tokens, rate limiting
- **Inter-service**: mTLS o API keys
- **Databases**: Autenticación, TLS
- **Secrets**: Docker secrets o Vault

## 📈 Observabilidad

- **Logging**: Structured logs (JSON)
- **Tracing**: OpenTelemetry
- **Metrics**: Prometheus + Grafana
- **Health Checks**: `/health` en cada servicio

## 🎯 Ventajas de esta Arquitectura

1. **Separación de Responsabilidades**: Cada servicio tiene un propósito único
2. **Escalabilidad Independiente**: Escalar solo lo que necesitas
3. **Deploy Independiente**: Desplegar sin afectar otros servicios
4. **Tecnología por Servicio**: Usar la mejor herramienta para cada tarea
5. **Mantenibilidad**: Código más pequeño y manejable
6. **Resiliencia**: Fallo de un servicio no afecta a los demás

---

**Arquitectura:** Microservicios + Clean Architecture  
**Patrón de Comunicación:** Event-Driven (RabbitMQ)  
**Patrón de Diseño:** Strategy, Repository, Dependency Injection  
**DevOps:** Docker + Docker Compose + GitHub Actions
