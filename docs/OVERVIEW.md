## 🧾 Resumen Conceptual del Proyecto

Este documento resume, en lenguaje sencillo, **qué es cada cosa en el proyecto** y cómo se relaciona con el resto.  
Está pensado como apoyo para presentaciones y onboarding rápido.

---

## 🎯 Objetivo del Fraud Detection Engine

- Detectar transacciones potencialmente fraudulentas usando un **conjunto de reglas de negocio** (estrategias de fraude).
- Mantener una **arquitectura limpia y testeable**:
  - Separar la lógica de negocio de la infraestructura.
  - Facilitar cambios en reglas sin romper todo el sistema.
- Ofrecer:
  - **API REST** para otros sistemas.
  - **UIs** para usuarios finales y analistas.
  - **Trazabilidad** completa de las decisiones (auditoría).

---

## 🏗️ Piezas Principales (visión rápida)

- **Backend (Python)**:
  - `services/fraud-evaluation-service`: núcleo de negocio de fraude (reglas, modelos, casos de uso).
  - `services/api-gateway`: API FastAPI pública.
  - `services/worker-service`: worker asíncrono que procesa colas de RabbitMQ.
- **Frontends (React/Vite)**:
  - `frontend/user-app`: aplicación de usuario para ver transacciones e historial.
  - `frontend/admin-dashboard`: dashboard de analista/admin para métricas y revisión manual.
- **Infraestructura**:
  - `docker-compose.yml`: define MongoDB, Redis, RabbitMQ, API, worker y frontends.
- **Tests**:
  - `tests/`: tests unitarios/integración backend (pytest).
  - `tests-e2e/`: tests end-to-end (Playwright).
- **Documentación**:
  - `docs/*.md`: arquitectura, estructura, historias de usuario, plan de pruebas, etc.

---

## 🧱 Backend – Servicios

### 1. `services/fraud-evaluation-service`

- **Qué es**: el **núcleo de negocio** del motor de fraude.
- **Qué contiene**:
  - `domain/`:
    - **Entidades**: `Transaction`, `FraudEvaluation`, `Location`, `RiskLevel`, etc.
    - **Estrategias de fraude**:
      - `amount_threshold.py`: regla por monto.
      - `location_check.py`: regla por distancia geográfica.
      - `device_validation.py`: dispositivo conocido vs nuevo.
      - `rapid_transaction.py`: muchas transacciones en poco tiempo.
      - `unusual_time.py`: horarios inusuales para el usuario.
  - `application/`:
    - Casos de uso:
      - `EvaluateTransactionUseCase`: evalúa una transacción aplicando todas las estrategias.
      - `ReviewTransactionUseCase`: permite al analista modificar la decisión.
    - Interfaces/puertos:
      - Repositorios, cache, mensajería.
  - `adapters.py`, `config.py`: adaptadores a MongoDB, Redis, RabbitMQ y configuración.
- **Por qué es importante**:
  - Aquí vive la lógica de negocio pura y las reglas que justifican el proyecto.

### 2. `services/api-gateway`

- **Qué es**: una **API REST** implementada con FastAPI.
- **Responsabilidad**:
  - Recibir peticiones HTTP de clientes y frontends.
  - Exponer endpoints como:
    - `POST /transaction` — enviar transacción para evaluación.
    - `GET /audit/all` — ver todas las evaluaciones.
    - `GET /audit/transaction/{id}` — ver el detalle de una evaluación.
    - `PUT /transaction/review/{id}` — revisión manual por analista.
    - `GET /config/thresholds` / `PUT /config/thresholds` — consultar/actualizar umbrales.
  - Hacer **dependency injection** de los adaptadores y casos de uso del núcleo.
- **Archivo clave**:
  - `src/main.py`: crea la app FastAPI y monta las rutas.

### 3. `services/worker-service`

- **Qué es**: un **worker asíncrono** que procesa mensajes de RabbitMQ.
- **Responsabilidad**:
  - Leer mensajes con transacciones pendientes de evaluación.
  - Construir entidades `Transaction`.
  - Invocar `EvaluateTransactionUseCase`.
  - Guardar resultados en MongoDB y actualizar datos de apoyo en Redis.
- **Por qué existe**:
  - Permite que la API responda rápido (`202 Accepted`) sin bloquearse por la evaluación.

---

## 🌐 Frontends

### 1. `frontend/user-app`

- **Público objetivo**: usuario final del sistema (cliente bancario, por ejemplo).
- **Tecnologías**:
  - React + Vite + TypeScript + TailwindCSS.
- **Funciones principales**:
  - Ver **historial de transacciones**.
  - Ver el **estado de riesgo** de cada transacción (aprobada, sospechosa, rechazada).
- **Cómo se conecta**:
  - Llama a la API del Gateway (por ejemplo, endpoints de consulta de auditoría o transacciones por usuario).

### 2. `frontend/admin-dashboard`

- **Público objetivo**: analistas de fraude y administradores.
- **Tecnologías**:
  - React + Vite + TypeScript + TailwindCSS.
  - Recharts (gráficas), TanStack Table (tablas).
- **Funciones principales**:
  - Ver **métricas de fraude** (HIGH/MEDIUM/LOW, volumen por día, etc.).
  - Navegar la **auditoría** de evaluaciones.
  - Hacer **revisión manual** de transacciones de riesgo.
  - Consultar y actualizar **configuración/umbrales** (según endpoints).

---

## 🗄️ Infraestructura – `docker-compose.yml`

- **Objetivo**: levantar todo el entorno local con un solo comando:

```bash
docker-compose up -d
```

- **Servicios definidos**:
  - `mongodb` – base de datos principal (27017).
  - `redis` – caché de alta velocidad (6379).
  - `rabbitmq` – broker de mensajería (5672, 15672).
  - `api` – API Gateway (FastAPI, puerto 8000).
  - `worker` – worker asíncrono.
  - `frontend-user` – User App servida por Nginx (puerto 3000).
  - `frontend-admin` – Admin Dashboard servido por Nginx (puerto 3001).
- **Idea clave**:
  - Simular el entorno completo de producción en tu máquina local con una sola herramienta (Docker Compose).

---

## 🔁 Flujo de una Transacción (de extremo a extremo)

1. **Cliente (User App / sistema externo)** envía la transacción:
   - `POST /transaction` al API Gateway.
2. **API Gateway (FastAPI)**:
   - Valida el request.
   - Publica un mensaje en RabbitMQ.
   - Devuelve `202 Accepted` rápidamente.
3. **RabbitMQ**:
   - Coloca la transacción en una cola de evaluación.
4. **Worker Service**:
   - Lee el mensaje.
   - Crea una `Transaction`.
   - Ejecuta `EvaluateTransactionUseCase` (núcleo de fraude).
5. **Fraud Evaluation Service**:
   - Aplica todas las estrategias de fraude.
   - Calcula un `FraudEvaluation` (nivel de riesgo + razones).
6. **Persistencia**:
   - Guarda el resultado en MongoDB (para auditoría).
   - Actualiza Redis (por ejemplo, historial de ubicación, dispositivos).
7. **Consulta y revisión**:
   - Admin Dashboard llama a endpoints como:
     - `GET /audit/all`, `GET /audit/transaction/{id}` para ver resultados.
     - `PUT /transaction/review/{id}` para revisión manual.

---

## 🧪 Testing y Calidad

- **Backend (pytest)**:
  - `tests/unit/`: 244 tests unitarios (estrategias, adaptadores, modelos, rutas, etc.).
  - Cobertura ~95% (ver `coverage.xml` y `htmlcov/`).
- **Frontends (Vitest)**:
  - `frontend/user-app`: tests de componentes y lógica de UI.
  - `frontend/admin-dashboard`: tests de componentes, tablas, gráficas, etc.
- **E2E (Playwright)**:
  - `tests-e2e/`: cubre historias de usuario completas (User App + Admin Dashboard + API).
- **Documentos clave**:
  - `docs/TEST_PLAN.md`: qué tipos de tests existen y cómo se ejecutan.
  - `docs/TEST_CASES.md`: casos de prueba específicos.

---

## 📚 Documentación Relacionada

- `docs/ARQUITECTURE.md`  
  Explica las **capas lógicas** (Domain/Application/Infrastructure) y el flujo asíncrono con RabbitMQ, MongoDB y Redis.

- `docs/PROJECT_STRUCTURE.md`  
  Explica **dónde está cada cosa** en el repositorio (carpetas y archivos).

- `docs/MICROSERVICES_ARCHITECTURE.md`  
  Describe cómo se relacionan los servicios (API, worker, núcleo de fraude) y qué servicios levanta Docker Compose.

- `docs/USER_HISTORY.md`  
  Lista detallada de **historias de usuario** y contexto de negocio.

- `docs/INSTALL.md`  
  Pasos para instalar, levantar y probar el proyecto en local.

---

## 💡 Cómo usar este archivo en tu presentación

- Como referencia rápida para:
  - Explicar **qué hace cada carpeta/servicio** sin entrar al código.
  - Conectar la parte técnica (código) con la parte funcional (historias de usuario).
- Puedes copiar secciones enteras como:
  - “Backend – Servicios” (para explicar arquitectura de backend).
  - “Frontends” (para enseñar las UIs).
  - “Flujo de una transacción” (para un diagrama de alto nivel).
  - “Testing y calidad” (para justificar la robustez del sistema).


