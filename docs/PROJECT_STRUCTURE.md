# 📊 Vista General del Proyecto - Microservicios

## 🎯 Proyecto Completamente Reorganizado

El proyecto **Fraud Detection Engine** ahora está organizado en una **arquitectura de microservicios** clara y escalable.

---

## 📁 Estructura Completa

```
fraud-detection-engine/
│
├── 🔷 services/                          # MICROSERVICIOS
│   │
│   ├── 📡 api-gateway/                   # Servicio 1: API Gateway
│   │   ├── src/
│   │   │   ├── routes/                   # Endpoints REST
│   │   │   │   ├── transactions.py
│   │   │   │   ├── audit.py
│   │   │   │   ├── review.py
│   │   │   │   └── config.py
│   │   │   ├── middleware/               # Autenticación, rate limiting
│   │   │   │   ├── auth.py
│   │   │   │   └── rate_limit.py
│   │   │   ├── dependencies.py
│   │   │   └── main.py                   # FastAPI App
│   │   ├── tests/
│   │   ├── Dockerfile                    # Puerto 8000
│   │   ├── pyproject.toml
│   │   └── README.md                     # ✅ Documentación completa
│   │
│   ├── 🧠 fraud-evaluation-service/      # Servicio 2: Evaluación de Fraude
│   │   ├── src/
│   │   │   ├── domain/                   # ✅ CLEAN ARCHITECTURE
│   │   │   │   ├── models/
│   │   │   │   │   ├── transaction.py
│   │   │   │   │   ├── evaluation.py
│   │   │   │   │   └── value_objects.py
│   │   │   │   └── strategies/           # ✅ STRATEGY PATTERN
│   │   │   │       ├── base.py
│   │   │   │       ├── amount_threshold.py
│   │   │   │       ├── location_check.py
│   │   │   │       ├── velocity_check.py    # Futuro
│   │   │   │       └── impossible_travel.py # Futuro
│   │   │   ├── application/              # Use Cases
│   │   │   │   ├── interfaces.py         # Puertos (DI)
│   │   │   │   └── use_cases/
│   │   │   │       ├── evaluate_transaction.py
│   │   │   │       └── review_transaction.py
│   │   │   ├── infrastructure/           # Adaptadores
│   │   │   │   ├── api/
│   │   │   │   │   ├── main.py
│   │   │   │   │   └── routes.py
│   │   │   │   └── adapters/
│   │   │   │       └── redis_adapter.py
│   │   │   └── config.py
│   │   ├── tests/
│   │   │   ├── unit/                     # ✅ TDD
│   │   │   │   ├── domain/
│   │   │   │   └── application/
│   │   │   └── integration/
│   │   ├── Dockerfile                    # Puerto 8001
│   │   ├── pyproject.toml
│   │   └── README.md                     # ✅ Documentación completa
│   │
│   ├── ⚙️ worker-service/                # Servicio 3: Worker RabbitMQ
│   │   ├── src/
│   │   │   ├── consumer/
│   │   │   │   └── rabbitmq_consumer.py
│   │   │   ├── processors/
│   │   │   │   ├── transaction_processor.py
│   │   │   │   └── review_processor.py
│   │   │   ├── adapters/
│   │   │   │   ├── mongodb_adapter.py
│   │   │   │   ├── redis_adapter.py
│   │   │   │   └── fraud_service_client.py
│   │   │   ├── config.py
│   │   │   └── worker.py                 # Main
│   │   ├── tests/
│   │   ├── Dockerfile                    # No expone puerto
│   │   ├── pyproject.toml
│   │   └── README.md                     # ✅ Documentación completa
│   │
│   └── 📦 shared/                        # Código Compartido
│       ├── domain/                       # Models comunes
│       │   ├── models.py
│       │   └── strategies/
│       ├── config.py                     # Config compartida
│       ├── adapters.py                   # Adapters comunes
│       └── interfaces.py                 # Interfaces comunes
│
├── 🗄️ infrastructure/                    # INFRAESTRUCTURA EXTERNA
│   ├── databases/
│   │   ├── mongodb/
│   │   │   └── init-scripts/
│   │   └── README.md
│   ├── messaging/
│   │   ├── rabbitmq/
│   │   │   └── config/
│   │   └── README.md
│   └── cache/
│       ├── redis/
│       │   └── config/
│       └── README.md
│
├── 🎨 frontend/                          # FRONTEND
│   ├── streamlit/
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── evaluation.py
│   │   │   ├── audit.py
│   │   │   ├── review.py
│   │   │   └── config.py
│   │   └── components/
│   ├── Dockerfile                        # Puerto 8501
│   └── README.md
│
├── 🧪 tests/                             # TESTS DE INTEGRACIÓN
│   ├── integration/                      # Tests E2E entre servicios
│   ├── e2e/                              # Tests de usuario final
│   ├── performance/                      # Load testing
│   └── README.md
│
├── 🛠️ scripts/                           # SCRIPTS DEVOPS
│   ├── deploy/
│   │   ├── kubernetes/
│   │   └── terraform/
│   ├── validate_architecture.py          # ✅ Validación Clean Architecture
│   ├── run_tests.sh
│   └── setup.sh
│
├── 📊 .github/                           # CI/CD
│   └── workflows/
│       ├── ci.yml                        # ✅ Pipeline con SonarQube
│       ├── deploy.yml
│       └── sonarqube.yml
│
├── 📄 DOCUMENTACIÓN
│   ├── README.md                         # Overview del proyecto
│   ├── ARQUITECTURE.md                   # Arquitectura original
│   ├── MICROSERVICES_ARCHITECTURE.md    # ✅ Arquitectura de microservicios
│   ├── QUICKSTART.md                     # Guía rápida
│   ├── IMPLEMENTATION_SUMMARY.md         # Resumen de implementación
│   └── PROJECT_STRUCTURE.md              # ✅ Este archivo
│
├── 🐳 DOCKER & COMPOSE
│   ├── docker-compose.yml               # Original (monolito)
│   ├── docker-compose.microservices.yml # ✅ Microservicios
│   ├── docker-compose.dev.yml           # Desarrollo
│   └── docker-compose.prod.yml          # Producción
│
└── ⚙️ CONFIGURACIÓN
    ├── sonar-project.properties         # ✅ SonarQube
    ├── pyproject.toml                   # Poetry root
    ├── .env.example                     # Variables de entorno
    ├── .gitignore
    └── .pre-commit-config.yaml
```

---

## 🔷 Microservicios Implementados

| Servicio | Puerto | Tecnología | Responsabilidad | Escalable |
|----------|--------|------------|-----------------|-----------|
| **API Gateway** | 8000 | FastAPI | Routing, Auth, Rate Limiting | ✅ Sí |
| **Fraud Evaluation** | 8001 | Python + Clean Arch | Lógica de negocio, Strategies | ✅ Sí |
| **Worker Service** | - | Python + Pika | Procesamiento asíncrono | ✅ Sí |
| **Frontend** | 8501 | Streamlit | UI Demo | ❌ No |

---

## 🗄️ Infraestructura

| Componente | Puerto | Propósito | HA |
|------------|--------|-----------|-----|
| **MongoDB** | 27017 | Persistencia | ✅ Replica Set |
| **Redis** | 6379 | Caché | ✅ Sentinel |
| **RabbitMQ** | 5672, 15672 | Mensajería | ✅ Cluster |

---

## 🔄 Comunicación entre Servicios

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ HTTP
       ▼
┌──────────────────┐
│   API Gateway    │◄─────┐
│   (Puerto 8000)  │      │
└────────┬─────────┘      │
         │                │
         │ Publish        │ Query
         ▼                │
   ┌──────────┐           │
   │ RabbitMQ │           │
   └─────┬────┘           │
         │ Consume        │
         ▼                │
┌──────────────────┐      │
│  Worker Service  │      │
└────────┬─────────┘      │
         │ HTTP Call      │
         ▼                │
┌──────────────────────┐  │
│ Fraud Evaluation Svc │  │
│    (Puerto 8001)     │  │
└──────────┬───────────┘  │
           │              │
           ▼              │
    ┌──────────┐    ┌─────────┐
    │ MongoDB  │    │  Redis  │
    └──────────┘    └─────────┘
```

---

## 🚀 Comandos Rápidos

### Levantar Arquitectura de Microservicios
```bash
docker-compose -f docker-compose.microservices.yml up --build
```

### Escalar Servicios Independientemente
```bash
# Escalar workers
docker-compose up --scale worker-service=3

# Escalar fraud evaluation
docker-compose up --scale fraud-evaluation-service=2

# Escalar API gateway
docker-compose up --scale api-gateway=2
```

### Ver Estado de Todos los Servicios
```bash
docker-compose ps
```

### Logs por Servicio
```bash
docker logs fraud-api-gateway -f
docker logs fraud-evaluation-service -f
docker logs fraud-worker-service -f
```

---

## 📊 Ventajas de esta Organización

### ✅ Separación Clara
- Cada microservicio en su propia carpeta
- Código compartido en `/services/shared`
- Infraestructura separada en `/infrastructure`

### ✅ Escalabilidad
- Cada servicio puede escalarse independientemente
- Deploy independiente sin afectar otros servicios
- Load balancing automático con Docker Compose

### ✅ Mantenibilidad
- READMEs específicos por servicio
- Tests separados por servicio
- Dockerfiles individuales optimizados

### ✅ Clean Architecture
- Domain Layer sin dependencias externas
- Application Layer con casos de uso
- Infrastructure Layer con adaptadores

### ✅ SOLID
- Single Responsibility: 1 servicio = 1 responsabilidad
- Open/Closed: Nuevas estrategias sin modificar código
- Dependency Inversion: Interfaces bien definidas

---

## 🎯 Próximos Pasos

1. **Implementar código en cada microservicio**
   - Mover código existente a la nueva estructura
   - Crear Dockerfiles específicos
   - Configurar dependencias por servicio

2. **Configurar Service Mesh (Opcional)**
   - Istio o Linkerd para comunicación segura
   - Observabilidad distribuida
   - Circuit breakers y retries

3. **Deploy en Kubernetes**
   - Crear manifests por servicio
   - ConfigMaps y Secrets
   - Horizontal Pod Autoscaler

---

**Arquitectura:** Microservicios + Clean Architecture  
**Patrón:** Event-Driven + Strategy Pattern  
**DevOps:** Docker Compose + Kubernetes Ready  
**Escalabilidad:** Horizontal por servicio
