Arquitectura del Motor de Reglas de Fraude (Fraud Detection Engine)

## 1. Visión General del Sistema

El Motor de Reglas de Fraude está implementado siguiendo **Arquitectura Limpia (Clean Architecture)** y principios **SOLID**, desplegado como varios servicios coordinados por Docker Compose:

- Núcleo de fraude: `services/fraud-evaluation-service/src`
- API pública (FastAPI): `services/api-gateway/src`
- Worker asíncrono: `services/worker-service/src`

La lógica de negocio (dominio y casos de uso) está desacoplada de FastAPI y de la infraestructura (MongoDB, Redis, RabbitMQ), que se modelan como adaptadores externos.

> Para la estructura de carpetas completa ver `docs/PROJECT_STRUCTURE.md`.  
> Aquí nos centramos en capas lógicas y flujo de datos.

## 2. Estructura de Capas

| Capa | Dónde vive | Componentes Clave | Rol en el Fraude | Restricción Clave |
| :--- | :--------- | :---------------- | :---------------- | :---------------- |
| **Domain (Núcleo)** | `services/fraud-evaluation-service/src/domain` | `Transaction`, `FraudEvaluation`, `RiskLevel`, `FraudStrategy` y estrategias (`amount_threshold`, `location_check`, `rapid_transaction`, `unusual_time`, `device_validation`, etc.) | Lógica pura de reglas (monto, ubicación, tiempo, dispositivo, velocidad, etc.). | **No debe importar Infrastructure ni frameworks.** |
| **Application** | `services/fraud-evaluation-service/src/application` | `EvaluateTransactionUseCase`, `ReviewTransactionUseCase`, interfaces/puertos | Orquesta evaluación, persistencia y notificación *human in the loop*. | Usa inyección de dependencias sobre interfaces. |
| **Infrastructure** | `services/api-gateway/src`, `services/fraud-evaluation-service/src/adapters.py`, `services/worker-service/src` | FastAPI, `MongoDBAdapter`, `RedisAdapter`, `RabbitMQAdapter`, configuración, worker | Adapta el dominio a HTTP, bases de datos y colas. Implementa APIs de entrada y salidas técnicas. | Depende de librerías externas, pero no al revés. |

## 3. Flujo de Procesamiento Asíncrono

1. **Input (API Gateway - FastAPI)**  
   - Recibe `POST /transaction` desde frontends o clientes externos.  
   - Valida el payload y responde `202 Accepted` (HU-001).  
   - Publica un mensaje en RabbitMQ con los datos de la transacción.

2. **Mensajería (RabbitMQ)**  
   - Cola de entrada de transacciones a evaluar.  
   - Desacopla la API del tiempo de procesamiento del motor de fraude.

3. **Worker (`services/worker-service`)**  
   - Consume el mensaje.  
   - Construye entidades de dominio (`Transaction`).  
   - Invoca `EvaluateTransactionUseCase` del núcleo de fraude.

4. **Evaluación (Fraud Evaluation Core)**  
   - Aplica todas las estrategias configuradas (monto, ubicación, dispositivo, horario inusual, transacciones rápidas, etc.).  
   - Produce un `FraudEvaluation` con `risk_level`, razones (`reasons`) y detalles para auditoría.

5. **Persistencia (MongoDB + Redis)**  
   - MongoDB guarda la evaluación como registro de auditoría (HU-002).  
   - Redis almacena datos de apoyo (ubicaciones históricas, dispositivos conocidos, configuración activa).

6. **Gobernanza y Revisión Manual (FastAPI)**  
   - La API expone endpoints de lectura y revisión:
     - `GET /audit/all`, `GET /audit/transaction/{id}` para auditoría.  
     - `PUT /transaction/review/{id}` para revisión manual por analista (HU-010).  
   - Estos endpoints son consumidos principalmente por el **Admin Dashboard**.

## 4. Persistencia y Herramientas

- **FastAPI (`services/api-gateway`)**: motor HTTP y adaptador de entrada, con documentación en `http://localhost:8000/docs`.
- **MongoDB**: log de auditoría inmutable y almacenamiento de configuraciones.
- **Redis**: caché de alta velocidad para perfiles de comportamiento (ubicación, dispositivos, umbrales).
- **RabbitMQ**: mensajería asíncrona para desacoplar API y procesamiento pesado.

---

Para la organización detallada de carpetas y servicios, ver `docs/PROJECT_STRUCTURE.md` y `docs/MICROSERVICES_ARCHITECTURE.md`.
