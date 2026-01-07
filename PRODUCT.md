✨ Motor de Reglas de Fraude: Visión del Producto y Alcance

## 1. Alcance y Límites del Proyecto
El alcance se limita al **Backend (Lógica, APIs y Colas)**. La interfaz de usuario final (Paneles de Administración y Revisión) están fuera de alcance. La **interfaz de demostración (Streamlit)** se utiliza únicamente como herramienta de validación para el desarrollo basado en el comportamiento (BDD).

## 2. Requisitos Funcionales Clave (RF)

| HU ID | Funcionalidad | Valor de Negocio |
| :--- | :--- | :--- |
| **HU-003** | **Regla de Umbral de Monto** | Marca como sospechosa cualquier transacción que exceda el umbral de $1,500 USD. |
| **HU-005** | **Regla de Ubicación Inusual** | Previene fraudes por *takeover* geográfico (fuera del radio de 100 km). |
| **HU-010** | **Servicio Human in the Loop** | Envía transacciones de riesgo intermedio a una cola de mensajes (RabbitMQ) y habilita la API de decisión final para el Analista. |
| **HU-008/009** | **Gobernanza de Umbrales** | Permite al Analista de Riesgo modificar los umbrales de las reglas vía API, sin desplegar código nuevo. |

## 3. Requisitos de Calidad y Metodología (RNF)

* **TDD/BDD Real (FT-004):** Adopción estricta del ciclo TDD/BDD, priorizando la creación de tests antes de la implementación. 
* **Cobertura (FT-004):** Cobertura de tests mínima del **70%** en las capas Domain y Application.
* **Regla del Crítico (FT-008):** Todo código asistido por IA requiere un comentario de revisión obligatoria para validar la ingeniería.