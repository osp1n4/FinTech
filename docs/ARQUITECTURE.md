Arquitectura del Motor de Reglas de Fraude (Fraud Detection Engine)

## 1. Visión General del Sistema
El Motor de Reglas de Fraude es un microservicio de backend asíncrono con un enfoque en la **Arquitectura Limpia (Clean Architecture)**. El objetivo es lograr alta **testeabilidad** y **extensibilidad (FT-003)**. El motor central está desacoplado de la infraestructura web, utilizando FastAPI como Adaptador HTTP. 

## 2. Estructura de Capas

| Capa | Componentes Clave | Rol en el Fraude | Restricción Clave (FT-007) |
| :--- | :--- | :--- | :--- |
| **Domain (Núcleo)** | `Transaction`, `FraudEvaluation`, `FraudStrategy` | Lógica de las reglas (Monto, Ubicación. | **No debe importar Infrastructure.** |
| **Application** | `EvaluateTransactionUseCase`, `ReviewTransactionUseCase` | Orquesta la evaluación, persistencia y la notificación de *Human in the Loop*. | Usa Inyección de Dependencias. |
| **Infrastructure** | FastAPI, MongoDBAdapter, RedisAdapter, RabbitMQ | Adapta el Domain a la tecnología. Implementa APIs de entrada y gestión. | Adaptadores externos. |

## 3. Flujo de Procesamiento Asíncrono
1.  **Input (FastAPI):** Recibe `POST /transaction`. Responde `202 Accepted` (HU-001).
2.  **Mensajería (RabbitMQ):** Publica el evento de la transacción.
3.  **Worker:** Consume el mensaje y ejecuta el `EvaluateTransactionUseCase`.
4.  **Decisión:** El resultado se persiste en MongoDB (HU-002).
5.  **Gobernanza:** FastAPI expone APIs de Auditoría (`GET /audit/all`) y de Decisión (`PUT /transaction/review/{id}`) para la interfaz del Analista.

## 4. Persistencia y Herramientas
* **FastAPI:** Motor del servicio y Adaptador HTTP.
* **MongoDB:** Log de auditoría inmutable de todas las evaluaciones.
* **Redis:** Caché de alta velocidad para perfiles de comportamiento de usuario.

---

