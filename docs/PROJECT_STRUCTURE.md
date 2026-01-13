# 📊 Vista General del Proyecto

Este archivo describe **la estructura real del repositorio** tal como está hoy, para evitar confusiones con estructuras “propuestas” o legacy.

---

## 📁 Estructura Principal

```text
fraud-detection-engine/
├── services/                      # Backend (servicios lógicos en un mismo repo)
│   ├── api-gateway/               # FastAPI expuesta en puerto 8000
│   │   ├── src/
│   │   │   ├── main.py            # App FastAPI y DI
│   │   │   └── ...                # Rutas, auth, etc.
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── fraud-evaluation-service/  # Dominio de fraude (estrategias, modelos, casos de uso)
│   │   ├── src/
│   │   │   ├── domain/            # Entidades, Value Objects y estrategias
│   │   │   ├── application/       # Casos de uso
│   │   │   ├── adapters.py        # MongoDB, Redis, RabbitMQ
│   │   │   ├── config.py
│   │   │   └── ...
│   │   └── README.md
│   │
│   └── worker-service/            # Worker asíncrono (RabbitMQ → evaluación)
│       ├── src/
│       │   └── worker.py
│       ├── Dockerfile
│       └── README.md
│
├── frontend/
│   ├── user-app/                  # App de usuario (historial de transacciones)
│   │   ├── src/
│   │   ├── package.json
│   │   └── ...
│   └── admin-dashboard/           # Dashboard admin (métricas y reglas)
│       ├── src/
│       ├── package.json
│       └── ...
│
├── tests/                         # Tests backend (pytest)
│   ├── unit/
│   └── integration/
│
├── tests-e2e/                     # Tests end-to-end (Playwright)
│   ├── tests/
│   ├── pages/
│   ├── tasks/
│   └── README.md
│
├── scripts/                       # Scripts de ayuda (PowerShell)
│   ├── run-tests.ps1
│   ├── start-all-services.ps1
│   └── ...
│
├── docs/                          # Documentación
│   ├── ARQUITECTURE.md
│   ├── PROJECT_STRUCTURE.md       # Este archivo
│   ├── MICROSERVICES_ARCHITECTURE.md
│   ├── TECH_STACK.md
│   └── ...
│
├── docker-compose.yml             # Orquestación de MongoDB, Redis, RabbitMQ, API, worker y frontends
├── pyproject.toml                 # Configuración backend (Poetry)
├── requirements-test.txt
├── sonar-project.properties
└── README.md
```

---

## 🔷 Servicios Backend

- **`services/fraud-evaluation-service`**
  - Implementa la **lógica de negocio de fraude**:
    - Modelos de dominio (`Transaction`, `FraudEvaluation`, `Location`, etc.).
    - Estrategias (`amount_threshold`, `location_check`, `rapid_transaction`, `unusual_time`, etc.).
    - Casos de uso (`EvaluateTransactionUseCase`, `ReviewTransactionUseCase`).

- **`services/api-gateway`**
  - Expone la API REST en `http://localhost:8000`.
  - Maneja rutas como:
    - `POST /transaction`
    - `GET /audit/all`
    - `PUT /transaction/review/{id}`
    - `GET /config/thresholds`

- **`services/worker-service`**
  - Procesa mensajes de RabbitMQ de forma asíncrona.
  - Aplica estrategias de fraude y persiste resultados.

Todos estos servicios se levantan juntos a través de `docker-compose.yml`.

---

## 🎨 Frontend

- **`frontend/user-app`**
  - Vite + React + TypeScript + Tailwind.
  - Muestra el historial de transacciones y resultados de evaluación.
  - En Docker se sirve en `http://localhost:3000`.
  - En modo dev (`npm run dev`) normalmente corre en `http://localhost:5173`.

- **`frontend/admin-dashboard`**
  - Vite + React + TypeScript + Tailwind + Recharts + TanStack Table.
  - Muestra métricas de fraude, transacciones y gestión de reglas.
  - En Docker se sirve en `http://localhost:3001`.
  - En modo dev (`npm run dev`) corre en `http://localhost:3001`.

Más detalles en `docs/TECH_STACK.md` y en los `README.md` de cada frontend.

---

## 🧪 Testing

- **Backend** (`tests/`):
  - `tests/unit/`: 200+ tests unitarios (estrategias, adaptadores, rutas, modelos).
  - `tests/integration/`: pruebas de integración sobre API y servicios.

- **Frontends**:
  - Cada app (`frontend/user-app`, `frontend/admin-dashboard`) usa **Vitest** + Testing Library.
  - Scripts estándar: `npm test`, `npm run test:coverage`.

- **E2E** (`tests-e2e/`):
  - Playwright cubriendo flujos de usuario y dashboard.
  - Ver `tests-e2e/README.md` para comandos y estructura.

Cobertura backend actual: ~95% (`coverage.xml` generado por pytest + coverage).

---

## 🐳 Docker / Infraestructura

- **`docker-compose.yml`** (único archivo de compose usado actualmente):
  - `mongodb` (27017)
  - `redis` (6379)
  - `rabbitmq` (5672, 15672)
  - `api` (8000)
  - `worker`
  - `frontend-user` (3000)
  - `frontend-admin` (3001)

No existen actualmente archivos como `docker-compose.microservices.yml`, `docker-compose.dev.yml` o `docker-compose.prod.yml`; cualquier referencia a ellos en documentos antiguos debe considerarse **legacy**.

---

## ℹ️ Notas

- Algunos documentos antiguos describen una estructura con carpetas como `shared/`, `infrastructure/` o un frontend en Streamlit. Esa estructura fue una propuesta inicial pero **no corresponde al código actual**.
- Este archivo (`PROJECT_STRUCTURE.md`) es la referencia de verdad (“source of truth”) sobre cómo está organizado el proyecto hoy.
