# 🏗️ Arquitectura de Servicios - Fraud Detection Engine

Este documento describe la arquitectura **tal como está implementada en el código y en `docker-compose.yml`**, sin elementos “propuestos” que aún no existen.

---

## 📁 Módulos Principales

- **`services/fraud-evaluation-service`**
  - Implementa la lógica de negocio de fraude:
    - Modelos de dominio (`Transaction`, `FraudEvaluation`, `Location`, etc.).
    - Estrategias (`amount_threshold`, `location_check`, `rapid_transaction`, `unusual_time`, `device_validation`, etc.).
    - Casos de uso para evaluar y revisar transacciones.

- **`services/api-gateway`**
  - Servicio FastAPI que expone la API REST pública en `http://localhost:8000`.
  - Se encarga de:
    - Recibir requests HTTP.
    - Orquestar casos de uso de evaluación y revisión.
    - Exponer endpoints de configuración y auditoría.

- **`services/worker-service`**
  - Worker que procesa mensajes en segundo plano vía RabbitMQ.
  - Aplica estrategias de fraude y persiste los resultados.

- **Frontends**
  - `frontend/user-app`: app de usuario (historial de transacciones).
  - `frontend/admin-dashboard`: dashboard admin (métricas y reglas).

---

## 🔄 Flujo de Alto Nivel

```text
Cliente (User App / Admin Dashboard / API client)
        │
        │ HTTP
        ▼
┌──────────────────────┐
│      API Gateway     │  (FastAPI, puerto 8000)
└─────────┬────────────┘
          │
          │ 1) Publica mensajes de evaluación
          ▼
   ┌───────────────┐
   │   RabbitMQ    │
   └──────┬────────┘
          │
          │ 2) Worker consume mensajes
          ▼
┌─────────────────────────────┐
│     Worker Service          │
│   (fraud-evaluation core)   │
└─────────┬───────────────────┘
          │
          │ 3) Usa estrategias de fraude
          ▼
┌─────────────────────────────┐
│ Fraud Evaluation Service    │
│ (domain + application)      │
└─────────┬─────────┬────────┘
          │         │
          │         │
          ▼         ▼
     ┌────────┐  ┌────────┐
     │MongoDB │  │ Redis  │
     └────────┘  └────────┘
```

- **MongoDB**: almacena evaluaciones, auditoría y configuración persistente.
- **Redis**: guarda caché de ubicaciones, dispositivos conocidos, umbrales, etc.

---

## 🐳 Servicios en `docker-compose.yml`

El archivo `docker-compose.yml` define los servicios reales que se levantan:

1. **`mongodb`**
   - Imagen: `mongo:7.0`
   - Puerto: `27017`
   - Uso: base de datos principal para evaluaciones y usuarios.

2. **`redis`**
   - Imagen: `redis:7.2-alpine`
   - Puerto: `6379`
   - Uso: caché para ubicaciones, dispositivos, configuración.

3. **`rabbitmq`**
   - Imagen: `rabbitmq:3.12-management-alpine`
   - Puertos:
     - `5672`: AMQP
     - `15672`: UI de administración

4. **`api`**
   - Construido desde `services/api-gateway/Dockerfile`.
   - Expone `http://localhost:8000`.

5. **`worker`**
   - Construido desde `services/worker-service/Dockerfile`.
   - No expone puerto público; se comunica con RabbitMQ/MongoDB/Redis.

6. **`frontend-user`**
   - Construido desde `frontend/user-app/Dockerfile`.
   - Servido por Nginx en `http://localhost:3000`.

7. **`frontend-admin`**
   - Construido desde `frontend/admin-dashboard/Dockerfile`.
   - Servido por Nginx en `http://localhost:3001`.

No se usan actualmente archivos `docker-compose.dev.yml` ni `docker-compose.prod.yml`; cualquier mención en documentos antiguos es legacy.

---

## 🔐 Seguridad y Configuración

- Las URLs de servicios se leen desde variables de entorno, configuradas en `docker-compose.yml` y en `src/config.py`.
- Credenciales de ejemplo (`admin/fraud2026`, etc.) están pensadas **solo para desarrollo local**.
- Para producción se recomienda:
  - Variables de entorno seguras / secretos (por ejemplo, Key Vault).
  - TLS terminado en un reverse proxy o gateway de API externo.

---

## 📈 Observabilidad y Salud

- **Health check**:
  - `GET /health` en el API Gateway.
- **Logs**:
  - Cada contenedor escribe a `stdout`/`stderr` y se consulta con `docker-compose logs`.
- **RabbitMQ**:
  - UI de administración en `http://localhost:15672` (`fraud` / `fraud2026` para desarrollo).

---

## ✅ Resumen

- La arquitectura implementada es **orientada a servicios**, con:
  - Un API Gateway FastAPI.
  - Un “núcleo” de evaluación de fraude desacoplado (dominio + casos de uso).
  - Un worker asíncrono para procesar colas.
  - Frontends independientes (user/admin) hablando con la API.
- Toda la infraestructura necesaria para desarrollo local se levanta con **un solo comando**:

```bash
docker-compose up -d
```

Para más detalles de carpetas y archivos, ver también `docs/PROJECT_STRUCTURE.md`.
