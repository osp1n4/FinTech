# 🛡️ Fintech Bank

Motor de detección de fraude implementado con **Clean Architecture**, **TDD/BDD**, principios **SOLID** y patrón de diseño **Strategy**.

## 🧪 Cumplimiento TDD/BDD

[![Tests](https://img.shields.io/badge/tests-252%20passed-brightgreen)](docs/TEST_PLAN.md)
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)](docs/CODE_COVERAGE_REPORT.md)
[![TDD](https://img.shields.io/badge/TDD-aplicado-blue)](docs/FLUJO_TDD_BDD.md)
[![BDD](https://img.shields.io/badge/BDD-historias%20Gherkin-blue)](docs/USER_HISTORY.md)

### ✅ Verificación Completa (estado actual)

- ✅ **252 tests unitarios backend** pasando (pytest, `tests/unit/`)
- ✅ **2 tests frontend** pasando (Vitest - user-app y admin-dashboard)
- ✅ **Cobertura backend 96%** según `coverage.xml` (umbral mínimo configurado: 70%)
- ✅ **14 historias de usuario** cubiertas con tests unitarios, integración y E2E
- ✅ **Tests escritos antes del código** (TDD)
- ✅ **Ciclo Red-Green-Refactor** documentado
- ✅ **Especificaciones ejecutables** (BDD)
- ✅ **11 módulos con 100% de cobertura** (adaptadores, estrategias, servicios críticos)

📖 **Ver documentación completa (actualizada):**
- `docs/USER_HISTORY.md`: Historias de usuario y flujos de negocio
- `docs/TEST_PLAN.md`: Plan de pruebas y tipos de tests
- `docs/TEST_CASES.md`: Casos de prueba
- `tests-e2e/README.md`: Tests E2E con Playwright

## 🏗️ Arquitectura

### Visión general

- **Backend**:
  - `services/fraud-evaluation-service`: dominio de fraude (estrategias, modelos, casos de uso)
  - `services/api-gateway`: API FastAPI expuesta en `http://localhost:8000`
  - `services/worker-service`: worker asíncrono con RabbitMQ
- **Frontends**:
  - `frontend/user-app`: app de usuario (historial de transacciones)
  - `frontend/admin-dashboard`: dashboard admin (métricas y reglas)
- **Infraestructura**:
  - MongoDB, Redis y RabbitMQ orquestados con `docker-compose.yml`

Para una descripción más detallada ver:
- `docs/PROJECT_STRUCTURE.md`
- `docs/MICROSERVICES_ARCHITECTURE.md`

### Principios SOLID

✅ **0 violaciones SOLID**

- **S** (Single Responsibility): Cada clase tiene una única razón para cambiar
- **O** (Open/Closed): Extensible mediante Strategy Pattern sin modificar código existente
- **L** (Liskov Substitution): Las estrategias son intercambiables
- **I** (Interface Segregation): Interfaces específicas para cada puerto
- **D** (Dependency Inversion): Los casos de uso dependen de abstracciones, no de implementaciones

## 🛠️ Tecnologías Utilizadas

### Backend

- **Lenguaje**: Python 3.11+
- **Framework Web**: FastAPI 0.109.1
- **Servidor ASGI**: Uvicorn 0.27.0 (con extras standard)
- **Validación de Datos**: Pydantic 2.5.0, Pydantic Settings 2.1.0
- **Base de Datos**: 
  - MongoDB (PyMongo 4.6.0)
  - Redis 5.0.1 (caché y sesiones)
- **Message Broker**: RabbitMQ (Pika 1.3.2)
- **Autenticación**: 
  - Python-JOSE 3.3.0 (JWT con cryptography)
  - Bcrypt 4.0.0 (hash de contraseñas)
- **Geolocalización**: Geopy 2.4.1
- **Email**: Aiosmtplib 3.0.1
- **HTTP Client**: HTTPX 0.27.2
- **Gestión de Dependencias**: Poetry
- **Herramientas de Desarrollo**:
  - Black 24.1.1 (formateo de código)
  - Pylint 3.0.3 (linting)
  - MyPy 1.8.0 (type checking)

### Frontend

#### User App (`frontend/user-app`)
- **Framework**: React 18.3.1
- **Lenguaje**: TypeScript 5.7.2
- **Build Tool**: Vite 6.0.7
- **Estilos**: Tailwind CSS 3.4.17
- **HTTP Client**: Axios 1.7.9
- **Animaciones**: Framer Motion 12.0.1
- **Iconos**: Lucide React 0.263.1

#### Admin Dashboard (`frontend/admin-dashboard`)
- **Framework**: React 18.3.1
- **Lenguaje**: TypeScript 5.7.2
- **Build Tool**: Vite 6.0.7
- **Estilos**: Tailwind CSS 3.4.1
- **HTTP Client**: Axios 1.7.9
- **Routing**: React Router DOM 7.0.2
- **Estado Global**: Zustand 5.0.2
- **Tablas**: TanStack React Table 8.20.6
- **Gráficos**: Recharts 2.15.0
- **Notificaciones**: React Hot Toast 2.4.1
- **Fechas**: date-fns 4.1.0

### Testing

#### Backend
- **Framework**: Pytest 7.4.4
- **Cobertura**: Pytest-cov 4.1.0
- **Async Testing**: Pytest-asyncio 0.23.3
- **Mocking**: Pytest-mock 3.12.0

#### Frontend
- **Framework**: Vitest 1.1.0
- **Testing Library**: 
  - @testing-library/react 14.1.2
  - @testing-library/jest-dom 6.1.5
  - @testing-library/user-event 14.5.1
- **DOM Environment**: jsdom 23.0.1
- **UI Testing**: @vitest/ui 1.1.0

#### End-to-End (E2E)
- **Framework**: Playwright 1.41.0
- **Lenguaje**: TypeScript 5.3.3
- **Navegadores**: Chromium, Firefox, WebKit
- **Características**:
  - Screenshots automáticos en fallos
  - Videos de ejecución (on-first-retry)
  - Trace con timeline completo
  - HTML Reporter interactivo
  - Tests en paralelo (3 workers)
  - Multi-browser support

### Infraestructura

- **Orquestación**: Docker Compose
- **Bases de Datos**:
  - MongoDB (almacenamiento principal)
  - Redis (caché y sesiones)
- **Message Queue**: RabbitMQ
- **Web Server**: Nginx (para frontends en producción)

## 🎯 Historias de Usuario Implementadas

- **HU-001**: API de recepción de transacciones (202 Accepted) - ✅ 5 tests
- **HU-002**: Auditoría de evaluaciones - ✅ 5 tests
- **HU-003**: Regla de umbral de monto (>$1,500) - ✅ 5 tests
- **HU-004**: Validación de dispositivo conocido - ✅ 5 tests
- **HU-005**: Detección de ubicación inusual (>100 km) - ✅ 9 tests
- **HU-006**: Detección de transacciones en cadena - ✅ 5 tests
- **HU-007**: Detección de horario inusual - ✅ 4 tests
- **HU-008**: Modificación de umbrales sin redespliegue - ✅ 3 tests
- **HU-009**: Consulta de configuración actual - ✅ 2 tests
- **HU-010**: Envío a cola de revisión manual - ✅ 5 tests
- **HU-011**: Gestión de reglas personalizadas - ✅ 3 tests
- **HU-012**: Revisión manual por analista - ✅ 5 tests
- **HU-013**: Dashboard usuario (historial transacciones) - ✅ 4 tests
- **HU-014**: Dashboard admin (métricas de fraude) - ✅ 3 tests

**Total:** 14 historias, 252 tests backend + 2 tests frontend, 96% cobertura ✅

📊 **Ver reporte detallado de cobertura:** [`docs/CODE_COVERAGE_REPORT.md`](docs/CODE_COVERAGE_REPORT.md)

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

# 5. Acceder a la API (Swagger UI)
# http://localhost:8000/docs

# 6. Acceder a los frontends (servidos por Nginx en Docker)
# Frontend Usuario: http://localhost:3000
# Frontend Admin: http://localhost:3001

# Iniciar frontend de usuario
cd frontend/user-app
npm install
npm run dev

# Iniciar frontend admin (en otra terminal)
cd frontend/admin-dashboard
npm install
npm run dev
```

### Opción 2: Desarrollo Local (sin Docker para backend)

```bash
# 1. Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Instalar dependencias backend
poetry install

# 3. Copiar variables de entorno (si aplica)
cp .env.example .env  # o copy en Windows

# 4. Levantar solo las bases de datos con Docker
docker-compose up -d mongodb redis rabbitmq

# 5. Ejecutar API (desde la raíz del repo)
poetry run uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000

# 6. Ejecutar Worker (en otra terminal)
poetry run python -m services.worker-service.src.worker

# 7. Ejecutar frontends en modo dev
cd frontend/user-app && npm install && npm run dev       # http://localhost:5173
cd frontend/admin-dashboard && npm install && npm run dev  # http://localhost:3001
```

## 🧪 Testing

**252 tests backend + 2 tests frontend** | **96% cobertura** | **TDD/BDD aplicado**

```bash
# Ejecutar todos los tests
pytest tests/unit/ -v

# Frontend
cd frontend/user-app && npm test
cd frontend/admin-dashboard && npm test
```

📊 **Cobertura:** 96% (659 líneas, 29 sin cubrir)  
📖 **Detalles:** [`docs/CODE_COVERAGE_REPORT.md`](docs/CODE_COVERAGE_REPORT.md) | [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md)  
🔄 **CI/CD:** Tests automáticos en GitHub Actions

## 📊 Reglas de Fraude

**5 estrategias** implementadas con patrón Strategy:

1. **Amount Threshold** - Monto > $1000 USD → `HIGH_RISK`
2. **Location Check** - Distancia > 100 km → `HIGH_RISK`
3. **Device Validation** - Dispositivo desconocido → `HIGH_RISK`
4. **Rapid Transaction** - >2 transacciones en 5 min → `HIGH_RISK`
5. **Unusual Time** - Horario fuera del patrón → `MEDIUM/HIGH_RISK`

**Lógica de combinación:**
- **0 violaciones** → `LOW_RISK` → `APPROVED`
- **1 violación** → `MEDIUM_RISK` → `PENDING_REVIEW`
- **2+ violaciones** → `HIGH_RISK` → `REJECTED`

## 🔧 API Endpoints

**Autenticación:** `/api/v1/auth/register`, `/login`, `/verify-email`, `/me`  
**Transacciones:** `/api/v1/transactions/evaluate`, `/validate`, `/user/{id}`  
**Auditoría:** `/api/v1/audit/all`, `/transaction/{id}`, `/user/{id}`  
**Revisión:** `/api/v1/transactions/review/{id}` (requiere `X-Analyst-Id`)  
**Configuración:** `/api/v1/config/thresholds` (GET/PUT)

📖 **Swagger UI:** http://localhost:8000/docs

## 📝 Licencia

MIT License

---

## 📚 Documentación

**Principal:** [Arquitectura](docs/ARQUITECTURE.md) | [Microservicios](docs/MICROSERVICES_ARCHITECTURE.md) | [Estructura](docs/PROJECT_STRUCTURE.md) | [Resumen](docs/OVERVIEW.md)  
**Testing:** [Plan de Pruebas](docs/TEST_PLAN.md) | [Cobertura](docs/CODE_COVERAGE_REPORT.md) | [Casos de Prueba](docs/TEST_CASES.md)  
**Negocio:** [Historias de Usuario](docs/USER_HISTORY.md) | [Contexto](docs/CONTEXTO_NEGOCIO.md) | [TDD/BDD](docs/FLUJO_TDD_BDD.md)  
**Guías:** [Instalación](docs/INSTALL.md) | [Docker](docs/DOCKER_COMPOSE_USAGE.md) | [Seguridad](docs/SECURITY_CONFIGURATION.md)
