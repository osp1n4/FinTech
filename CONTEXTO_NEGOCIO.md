# 📋 Contexto de Negocio - Fraud Detection Engine

## 1. Descripción del Proyecto

**Nombre del Proyecto:** Fraud Detection Engine (Motor de Detección de Fraude)

**Objetivo del Proyecto:**  
Proporcionar una plataforma integral de detección de fraude en transacciones financieras en tiempo real, permitiendo la evaluación automática de transacciones mediante reglas configurables, notificación de casos sospechosos para revisión manual, y gestión centralizada de reglas y umbrales sin necesidad de redesplegar el sistema. El proyecto busca reducir las pérdidas por fraude, mejorar la experiencia del cliente legítimo y optimizar el tiempo de los analistas mediante automatización inteligente.

---

## 2. Flujos Críticos del Negocio

### Principales Flujos de Trabajo:

1. **Flujo de Evaluación de Transacciones:**
   - El usuario inicia una transacción desde la aplicación móvil o web
   - El sistema recibe la transacción (userId, amount, location, deviceId) vía API
   - Se aplican reglas de fraude configuradas (umbral de monto, ubicación inusual)
   - Se genera un nivel de riesgo: BAJO, MEDIO, ALTO
   - Las transacciones de RIESGO BAJO se aprueban automáticamente
   - Las transacciones de RIESGO MEDIO/ALTO se envían a cola para revisión manual
   - Las transacciones de RIESGO ALTO se rec
2. **Flujo de Revisión Manual (Human in the Loop):**
   - Las transacciones sospechosas se envían a cola de mensajes (RabbitMQ)
   - El analista de fraude revisa la transacción desde el dashboard administrativo
   - El analista aprueba o rechaza la transacción con justificación
   - El sistema actualiza el estado y notifica al usuario

3. **Flujo de Gestión de Reglas:**
   - El administrador del sistema accede al dashboard de configuración
   - Puede modificar umbrales de reglas existentes (monto máximo, distancia permitida)
   - Puede crear nuevas reglas personalizadas con parámetros JSON
   - Puede activar/desactivar reglas sin redespliegue
   - Los cambios se aplican inmediatamente a nuevas transacciones

4. **Flujo de Auditoría:**
   - Todas las evaluaciones se registran en MongoDB (inmutable)
   - El administrador puede consultar histórico de transacciones
   - Puede filtrar por usuario, nivel de riesgo, fecha, estado
   - Puede exportar reportes para análisis

### Módulos o Funcionalidades Críticas:

- **API Gateway:** Recepción de transacciones y endpoints de administración
- **Motor de Evaluación:** Aplicación de estrategias de detección (Strategy Pattern)
- **Worker Asíncrono:** Procesamiento de transacciones desde cola de mensajes
- **Dashboard de Usuario:** Visualización de transacciones propias y estado
- **Dashboard Administrativo:** Gestión de reglas, revisión manual y auditoría
- **Módulo de Auditoría:** Registro inmutable de todas las evaluaciones
- **Módulo de Configuración:** Gestión dinámica de umbrales y reglas

---

## 3. Reglas de Negocio y Restricciones

### Reglas de Negocio Relevantes:

1. **Regla de Umbral de Monto (HU-003):**  
   Cualquier transacción que exceda **$1,500 USD** se marca automáticamente como RIESGO ALTO.

2. **Regla de Ubicación Inusual (HU-005):**  
   Si la ubicación de la transacción está a más de **100 km** de la última ubicación conocida del usuario, se marca como RIESGO ALTO (prevención de takeover geográfico).

3. **Regla de Dispositivo Desconocido:**  
   Si el `deviceId` no coincide con los dispositivos registrados del usuario, se incrementa el nivel de riesgo.

4. **Gobernanza de Umbrales (HU-008/HU-009):**  
   - Solo los administradores pueden modificar los umbrales de las reglas
   - Los cambios de configuración deben aplicarse sin necesidad de redespliegue
   - Los usuarios regulares no pueden modificar reglas ni ver configuraciones

5. **Human in the Loop (HU-010):**  
   - Las transacciones con RIESGO MEDIO o ALTO deben enviarse a una cola para revisión manual
   - Solo analistas autorizados pueden aprobar/rechazar transacciones
   - Toda decisión manual debe incluir una justificación

6. **Auditoría Obligatoria (HU-002):**  
   - Todas las evaluaciones deben registrarse en MongoDB de forma inmutable
   - El registro debe incluir: transacción, estrategias aplicadas, resultado, timestamp
   - Los registros deben conservarse por tiempo indefinido para compliance

7. **Procesamiento Asíncrono:**  
   - El API debe responder **202 Accepted** inmediatamente (HU-001)
   - El procesamiento real ocurre de forma asíncrona en el Worker
   - Los usuarios pueden consultar el estado posteriormente

### Regulaciones o Normativas:

- **PCI DSS:** Cumplimiento de estándares de seguridad de datos de tarjetas de pago
- **GDPR/Ley de Protección de Datos:** Protección de información personal de usuarios (ubicación, datos financieros)
- **SOX (Sarbanes-Oxley):** Auditoría inmutable y trazabilidad de decisiones financieras
- **Ley de Lavado de Activos:** Detección de patrones sospechosos y reporte de actividades inusuales
- **ISO 27001:** Gestión de seguridad de la información

---

## 4. Perfiles de Usuario y Roles

### Perfiles o Roles de Usuario en el Sistema:

1. **Usuario Final (Cliente):**  
   - Realiza transacciones desde la aplicación web o móvil
   - Consulta el estado de sus transacciones
   - Ve el historial de sus transacciones evaluadas
   - No tiene acceso a reglas ni configuraciones del sistema

2. **Administrador (Analista de Fraude / Administrador de Riesgo):**  
   - Revisa transacciones marcadas como sospechosas con capacidad de aprobar/rechazar
   - Gestiona todas las reglas de fraude (crear, editar, eliminar, activar/desactivar)
   - Modifica umbrales sin necesidad de redespliegue (monto máximo, distancia permitida)
   - Define políticas de detección de fraude y configura parámetros de riesgo
   - Consulta reportes completos de auditoría
   - Analiza métricas y tendencias de fraude
   - Gestiona configuraciones del sistema
   - Acceso completo a todas las funcionalidades administrativas

### Permisos y Limitaciones de Cada Perfil:

| Perfil | Ver Transacciones | Revisar Manualmente | Modificar Reglas | Ver Auditoría | Configurar Sistema |
|--------|-------------------|---------------------|------------------|---------------|-------------------|
| **Usuario Final** | ✅ Propias | ❌ | ❌ | ❌ | ❌ |
| **Administrador** | ✅ Todas | ✅ | ✅ | ✅ Completa | ✅ |

**Restricciones importantes:**
- Los usuarios finales NO pueden ver transacciones de otros usuarios
- Solo los administradores tienen acceso al dashboard administrativo
- Los administradores deben justificar los cambios de configuración críticos
- Toda acción administrativa queda registrada en el log de auditoría

---

## 5. Condiciones del Entorno Técnico

### Plataformas Soportadas:

- **Backend API:** Plataforma web accesible vía HTTP/REST
- **Frontend de Usuario:** Aplicación web responsive (React + TypeScript) - Compatible con navegadores modernos
- **Dashboard Administrativo:** Aplicación web responsive (React + TypeScript) - Compatible con navegadores modernos
- **Arquitectura:** Microservicios containerizados con Docker

### Tecnologías o Integraciones Clave:

**Backend:**
- **FastAPI:** Framework web para API Gateway (Python 3.11+)
- **RabbitMQ:** Sistema de mensajería para procesamiento asíncrono
- **MongoDB:** Base de datos NoSQL para auditoría inmutable
- **Redis:** Caché de alta velocidad para perfiles de usuario
- **Poetry:** Gestor de dependencias Python

**Frontend:**
- **React 18:** Biblioteca para interfaces de usuario
- **TypeScript:** Lenguaje tipado para mayor robustez
- **Vite:** Herramienta de build y desarrollo
- **TailwindCSS:** Framework CSS para estilos

**DevOps y Calidad:**
- **Docker & Docker Compose:** Containerización de servicios
- **GitHub Actions:** CI/CD automatizado (Build, Test, SonarQube)
- **Pytest:** Framework de testing con cobertura ≥70%
- **SonarQube:** Análisis estático de código y calidad
- **Gitflow:** Estrategia de branching (main, develop, feature/*)

**Arquitectura:**
- **Clean Architecture:** Separación en capas (Domain, Application, Infrastructure)
- **Principios SOLID:** 0 violaciones SOLID documentadas
- **Strategy Pattern:** Extensibilidad de reglas de fraude sin modificar código
- **Dependency Injection:** Desacoplamiento de componentes

**Integraciones:**
- Potencial integración con sistemas de pago (Stripe, PayPal)
- Potencial integración con servicios de geolocalización (Google Maps API)
- Potencial integración con servicios de identidad (Auth0, Azure AD)

---

## 6. Casos Especiales o Excepciones

### Escenarios Alternos o Excepciones que Deben Considerarse:

1. **Transacciones de Prueba:**  
   Las transacciones de usuarios de prueba o ambientes de desarrollo deben procesarse con reglas menos restrictivas para facilitar testing.

2. **Ubicación No Disponible:**  
   Si el usuario no proporciona ubicación GPS (permisos denegados o dispositivo sin GPS), la regla de ubicación debe omitirse y usar reglas alternativas.

3. **Primera Transacción del Usuario:**  
   La primera transacción de un usuario no tiene historial previo, por lo que las reglas de "ubicación inusual" o "dispositivo desconocido" deben aplicarse con menor severidad.

4. **Límites por País/Región:**  
   El umbral de monto debe ser ajustable por región geográfica (ej: $1,500 USD en USA, pero equivalente en otras monedas).

5. **Transacciones en Cadena:**  
   Si un usuario realiza múltiples transacciones en corto tiempo desde la misma ubicación, el sistema debe considerar el monto acumulado, no solo el individual.

6. **Analista Fuera de Horario:**  
   Las transacciones que requieren revisión manual fuera del horario laboral deben quedar en cola pero notificar por email/SMS al analista de guardia.

7. **Caída de Servicios Externos:**  
   Si MongoDB o Redis están temporalmente inaccesibles, el sistema debe poder operar en modo degradado (solo evaluación en memoria) y registrar cuando vuelvan a estar disponibles.

8. **Regla Inválida:**  
   Si un administrador crea una regla con parámetros JSON inválidos, el sistema debe validar y rechazar la configuración antes de aplicarla, sin afectar transacciones en curso.

9. **Timeout de Revisión Manual:**  
   Si una transacción no es revisada por un analista en 24 horas, debe escalarse automáticamente a un supervisor o aprobarse/rechazarse según políticas de riesgo.

10. **Usuario VIP o Whitelisted:**  
    Clientes premium o usuarios en lista blanca pueden tener umbrales más altos o bypass de ciertas reglas (configurable).

---

## 7. Métricas de Éxito del Negocio

Para medir el éxito del proyecto, se deben monitorear las siguientes métricas:

- **Tasa de Detección de Fraude:** % de transacciones fraudulentas detectadas correctamente
- **Falsos Positivos:** % de transacciones legítimas marcadas como fraudulentas (objetivo: <5%)
- **Tiempo de Respuesta:** Latencia promedio de la API (<200ms para 95% de requests)
- **Tiempo de Revisión Manual:** Tiempo promedio que toma un analista revisar una transacción (<5 minutos)
- **Cobertura de Tests:** Mantener ≥70% de cobertura en capas críticas (Domain, Application)
- **Disponibilidad del Sistema:** Uptime ≥99.5%
- **Ahorro Económico:** Reducción de pérdidas por fraude vs. sistema anterior

---

## 8. Glosario de Términos del Dominio

- **Transaction:** Operación financiera iniciada por un usuario (userId, amount, location, deviceId)
- **Risk Level:** Nivel de riesgo asignado a una transacción (LOW, MEDIUM, HIGH)
- **Fraud Strategy:** Regla de evaluación de fraude (AmountThreshold, UnusualLocation, DeviceValidation)
- **Human in the Loop:** Proceso de revisión manual por analista humano
- **Threshold:** Umbral configurable de una regla (ej: monto máximo, distancia permitida)
- **Audit Log:** Registro inmutable de todas las evaluaciones realizadas
- **Strategy Pattern:** Patrón de diseño que permite cambiar reglas sin modificar código base
- **Clean Architecture:** Arquitectura en capas (Domain, Application, Infrastructure) con dependencias invertidas
- **TDD/BDD:** Test-Driven Development / Behavior-Driven Development - Metodología de crear tests antes que código

---

**Documento creado:** Enero 2026  
**Última actualización:** Enero 8, 2026  
**Versión:** 1.0
