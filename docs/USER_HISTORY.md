# 📖 Historias de Usuario Detalladas - Fraud Detection Engine

**HUMAN REVIEW (Maria Paula):**
Este documento fue creado siguiendo TDD/BDD. Primero se definieron las historias de usuario
con sus criterios de aceptación en Gherkin, luego se implementaron los tests automatizados,
y finalmente el código que hace pasar esos tests. No escribimos código sin tests primero.

---

## Principios INVEST Aplicados

✅ **I**ndependent - Cada HU puede desarrollarse independientemente  
✅ **N**egotiable - Los detalles técnicos son flexibles  
✅ **V**aluable - Cada HU aporta valor al negocio  
✅ **E**stimable - Todas tienen estimación en puntos  
✅ **S**mall - Se pueden completar en un sprint  
✅ **T**estable - Tienen criterios de aceptación claros en Gherkin

---

## MÓDULO 1: 📨 RECEPCIÓN Y PROCESAMIENTO (HU-001 a HU-002)

### 🧪 HU-001 – Recepción de Transacciones por API REST

**Como** sistema externo bancario  
**Quiero** enviar transacciones al motor de fraude vía API REST  
**Para** que sean evaluadas de forma asíncrona y obtener una respuesta inmediata

**Descripción:**  
El sistema debe exponer un endpoint REST que reciba transacciones con información del usuario, monto, ubicación y dispositivo. La respuesta debe ser inmediata (202 Accepted) y el procesamiento ocurre de forma asíncrona.

**Estimación:** 3 puntos  
**Prioridad:** Alta  
**Dependencias:** Ninguna

#### Criterios de Aceptación

```gherkin
Feature: Recepción de transacciones por API REST

  Scenario: Recepción exitosa de transacción válida
    Given que el API está disponible en "http://localhost:8000"
    When envío POST a "/api/v1/transactions/evaluate" con datos válidos
      | campo      | valor                      |
      | user_id    | user_123                   |
      | amount     | 500.0                      |
      | location   | Bogotá, Colombia           |
      | device_id  | device_abc                 |
      | timestamp  | 2026-01-12T10:30:00Z       |
    Then el sistema responde con código 202
    And el response contiene "transaction_id"
    And el response contiene "status": "processing"

  Scenario: Rechazo de transacción sin user_id
    Given que el API está disponible
    When envío POST sin el campo "user_id"
    Then el sistema responde con código 422
    And el response contiene error "user_id is required"

  Scenario: Rechazo de transacción con monto negativo
    Given que el API está disponible
    When envío POST con "amount": -100.0
    Then el sistema responde con código 422
    And el response contiene error "amount must be positive"
```

#### 🧪 TC-HU-001-01 (Positivo)
**Descripción:** Validar recepción exitosa de transacción válida.

**Datos de Entrada:**
- user_id: `user_123`
- amount: `500.0`
- location: `Bogotá, Colombia`
- device_id: `device_abc`
- Endpoint: `POST /api/v1/transactions/evaluate`

**Pasos:**
```gherkin
Scenario: TC-HU-001-01 - Recepción exitosa
  Given que tengo credenciales válidas
  And el servicio está activo
  When envío la transacción con datos completos
  Then el sistema acepta la transacción con 202
  And genera un transaction_id único
  And registra la transacción para procesamiento asíncrono
```

**Resultado Esperado:** HTTP 202, transaction_id generado, status "processing"

**Archivo de Test:** `tests/unit/test_routes.py::TestTransactionEvaluationEndpoint::test_evaluate_transaction_success`

---

#### 🧪 TC-HU-001-02 (Negativo)
**Descripción:** Validar rechazo de transacción sin user_id.

**Datos de Entrada:**
- amount: `500.0`
- location: `Bogotá, Colombia`
- user_id: *(omitido)*
- Endpoint: `POST /api/v1/transactions/evaluate`

**Pasos:**
```gherkin
Scenario: TC-HU-001-02 - Rechazo por falta de user_id
  Given que el API está disponible
  When envío transacción sin user_id
  Then el sistema responde 422 Unprocessable Entity
  And el mensaje de error indica "user_id is required"
  And no se procesa la transacción
```

**Resultado Esperado:** HTTP 422, mensaje de error claro

**Archivo de Test:** `tests/unit/test_routes.py::TestTransactionEvaluationEndpoint::test_evaluate_transaction_missing_required_fields`

---

### 🧪 HU-002 – Auditoría Inmutable de Evaluaciones

**Como** auditor financiero  
**Quiero** que todas las evaluaciones de fraude queden registradas en un log inmutable  
**Para** cumplir con requisitos de compliance y auditoría

**Descripción:**  
Cada evaluación de fraude debe registrarse en MongoDB con toda la información de la transacción, estrategias aplicadas, resultado y timestamp. Los registros no deben ser modificables.

#### Criterios de Aceptación

```gherkin
Feature: Auditoría inmutable de evaluaciones

  Scenario: Registro de evaluación exitosa
    Given que una transacción fue procesada con resultado "LOW_RISK"
    When consulto el log de auditoría
    Then encuentro un registro con transaction_id
    And el registro contiene risk_level "LOW_RISK"
    And el registro contiene timestamp de evaluación
    And el registro contiene estrategias aplicadas
    And el registro es de solo lectura (no modificable)

  Scenario: Consulta de auditoría por usuario
    Given que existen transacciones del usuario "user_123"
    When consulto GET "/api/v1/audit/transactions?user_id=user_123"
    Then el sistema responde con código 200
    And retorna lista de transacciones del usuario
    And las transacciones están ordenadas por fecha descendente
```

#### 🧪 TC-HU-002-01 (Positivo)
**Descripción:** Verificar que se registra la auditoría correctamente.

**Datos de Entrada:**
- transaction_id: `txn_001`
- risk_level: `LOW_RISK`
- user_id: `user_123`

**Pasos:**
```gherkin
Scenario: TC-HU-002-01 - Registro de auditoría exitoso
  Given que se procesó una transacción LOW_RISK
  When se guarda en la base de datos
  Then existe un registro en la colección "evaluations"
  And el registro contiene todos los campos requeridos
  And el timestamp es válido en formato ISO 8601
  And el registro no puede ser modificado (append-only)
```

**Resultado Esperado:** Registro en MongoDB, campos completos, inmutable

**Archivo de Test:** `tests/unit/test_routes.py::TestAuditEndpoint::test_get_all_transactions_with_data`

---

## MÓDULO 2: 🎯 DETECCIÓN DE FRAUDE (HU-003 a HU-007)

### 🧪 HU-003 – Regla de Umbral de Monto

**Como** sistema de detección de fraude  
**Quiero** marcar como sospechosas las transacciones que excedan un umbral configurable  
**Para** detectar transacciones inusualmente altas

**Descripción:**  
Implementar una estrategia que evalúe si el monto de la transacción excede un umbral predefinido (inicialmente $1,500 USD). Las transacciones que excedan este monto deben marcarse como HIGH_RISK.

#### Criterios de Aceptación

```gherkin
Feature: Detección por umbral de monto

  Scenario: Transacción dentro del umbral
    Given que el umbral está configurado en $1,500
    When se evalúa una transacción de $500
    Then el resultado es LOW_RISK
    And el motivo es "Amount within threshold"

  Scenario: Transacción que excede el umbral
    Given que el umbral está configurado en $1,500
    When se evalúa una transacción de $2,000
    Then el resultado es HIGH_RISK
    And el motivo es "Amount exceeds threshold"
    And se incluye el detalle del exceso ($500)

  Scenario: Transacción exactamente en el umbral
    Given que el umbral está configurado en $1,500
    When se evalúa una transacción de $1,500
    Then el resultado es LOW_RISK
    And se considera dentro del límite aceptable
```

#### 🧪 TC-HU-003-01 (Positivo - Debajo del umbral)
**Descripción:** Transacción de $500 con umbral de $1,500.

**Datos de Entrada:**
- amount: `500.0`
- threshold: `1500.0`

**Pasos:**
```gherkin
Scenario: TC-HU-003-01 - Monto dentro del umbral
  Given que el umbral es $1,500
  And creo una transacción de $500
  When ejecuto AmountThresholdStrategy.evaluate()
  Then el risk_level es LOW_RISK
  And el risk_increment es 0
  And no hay razones de rechazo
```

**Resultado Esperado:** LOW_RISK, sin incremento de riesgo

**Archivo de Test:** `tests/unit/test_fraud_strategies.py::TestAmountThresholdStrategy::test_threshold_allows_low_risk_when_below`

---

#### 🧪 TC-HU-003-02 (Negativo - Excede umbral)
**Descripción:** Transacción de $2,000 con umbral de $1,500.

**Datos de Entrada:**
- amount: `2000.0`
- threshold: `1500.0`

**Pasos:**
```gherkin
Scenario: TC-HU-003-02 - Monto excede umbral
  Given que el umbral es $1,500
  And creo una transacción de $2,000
  When ejecuto AmountThresholdStrategy.evaluate()
  Then el risk_level es HIGH_RISK
  And el risk_increment es mayor a 0
  And la razón incluye "exceeds threshold"
  And el detalle muestra exceso de $500
```

**Resultado Esperado:** HIGH_RISK, incremento de riesgo, razón clara

**Archivo de Test:** `tests/unit/test_fraud_strategies.py::TestAmountThresholdStrategy::test_threshold_detects_high_risk_when_exceeded`

---

### 🧪 HU-004 – Validación de Dispositivo Conocido

**Como** sistema de detección de fraude  
**Quiero** validar que el dispositivo utilizado esté registrado para el usuario  
**Para** detectar posibles accesos no autorizados

**Descripción:**  
Verificar que el deviceId de la transacción esté en la lista de dispositivos conocidos del usuario almacenados en Redis. Dispositivos desconocidos incrementan el nivel de riesgo.

#### Criterios de Aceptación

```gherkin
Feature: Validación de dispositivo conocido

  Scenario: Dispositivo conocido y registrado
    Given que el usuario tiene dispositivos registrados en Redis
    And el device_id "device_abc" está en la lista
    When se evalúa una transacción con device_id "device_abc"
    Then el resultado es LOW_RISK
    And el motivo es "Known device"

  Scenario: Dispositivo desconocido
    Given que el usuario tiene dispositivos registrados
    But el device_id "device_xyz" NO está en la lista
    When se evalúa una transacción con device_id "device_xyz"
    Then el resultado es HIGH_RISK
    And el motivo es "Unknown device"
    And se registra el nuevo dispositivo para futuros accesos

  Scenario: Primera transacción (sin historial)
    Given que el usuario NO tiene dispositivos registrados
    When se evalúa su primera transacción
    Then el resultado es MEDIUM_RISK
    And el motivo es "First device for user"
    And se registra el dispositivo como conocido
```

#### 🧪 TC-HU-004-01 (Positivo - Dispositivo conocido)
**Descripción:** Validar dispositivo registrado previamente.

**Datos de Entrada:**
- user_id: `user_123`
- device_id: `device_abc`
- Redis: contiene `user_123:devices = ["device_abc"]`

**Pasos:**
```gherkin
Scenario: TC-HU-004-01 - Dispositivo conocido
  Given que Redis tiene el device_id registrado
  When ejecuto DeviceValidationStrategy.evaluate()
  Then el resultado es LOW_RISK
  And no se incrementa el riesgo
```

**Resultado Esperado:** LOW_RISK

**Archivo de Test:** `tests/unit/test_device_validation_strategy.py::TestDeviceValidationStrategy::test_known_device_returns_low_risk`

---

### 🧪 HU-005 – Detección de Ubicación Inusual

**Como** sistema de detección de fraude  
**Quiero** detectar transacciones desde ubicaciones lejanas a la ubicación habitual del usuario  
**Para** prevenir fraudes por takeover geográfico

**Descripción:**  
Calcular la distancia entre la ubicación actual de la transacción y la última ubicación conocida del usuario. Si la distancia excede 100 km, marcar como HIGH_RISK.


#### Criterios de Aceptación

```gherkin
Feature: Detección de ubicación inusual

  Scenario: Transacción desde ubicación cercana
    Given que la última ubicación del usuario fue Bogotá (4.7110, -74.0721)
    When se evalúa una transacción desde Chía (4.8610, -74.0590) - 15 km
    Then el resultado es LOW_RISK
    And el motivo es "Location within expected radius"

  Scenario: Transacción desde ubicación lejana
    Given que la última ubicación del usuario fue Bogotá (4.7110, -74.0721)
    When se evalúa una transacción desde Cali (3.4516, -76.5320) - 320 km
    Then el resultado es HIGH_RISK
    And el motivo es "Unusual location"
    And el detalle incluye la distancia calculada

  Scenario: Primera transacción del usuario
    Given que el usuario NO tiene historial de ubicaciones
    When se evalúa su primera transacción
    Then el resultado es LOW_RISK
    And se registra la ubicación como baseline
```

#### 🧪 TC-HU-005-01 (Positivo - Ubicación cercana)
**Descripción:** Transacción a 15 km de la última ubicación.

**Datos de Entrada:**
- Ubicación anterior: `Bogotá (4.7110, -74.0721)`
- Ubicación actual: `Chía (4.8610, -74.0590)`
- Radio permitido: `100 km`

**Pasos:**
```gherkin
Scenario: TC-HU-005-01 - Ubicación dentro del radio
  Given que la distancia es menor a 100 km
  When ejecuto LocationStrategy.evaluate()
  Then calcula distancia usando fórmula de Haversine
  And el resultado es LOW_RISK
```

**Resultado Esperado:** LOW_RISK, distancia ~15 km

**Archivo de Test:** `tests/unit/test_location_strategy.py::TestLocationStrategy::test_transaction_within_radius_low_risk`

---

### 🧪 HU-006 – Detección de Transacciones en Cadena

**Como** sistema de detección de fraude  
**Quiero** detectar múltiples transacciones del mismo usuario en corto tiempo  
**Para** prevenir ataques de consumo masivo

**Descripción:**  
Si un usuario realiza más de 3 transacciones en menos de 5 minutos, el sistema debe marcar las transacciones subsecuentes como sospechosas.

#### Criterios de Aceptación

```gherkin
Feature: Detección de transacciones en cadena

  Scenario: Transacciones espaciadas normalmente
    Given que un usuario hizo 2 transacciones en 10 minutos
    When evalúo una tercera transacción
    Then el resultado es LOW_RISK

  Scenario: Cuarta transacción en menos de 5 minutos
    Given que un usuario hizo 3 transacciones en 4 minutos
    When evalúo la cuarta transacción
    Then el resultado es HIGH_RISK
    And el motivo es "Rapid transaction sequence detected"
```

#### 🧪 TC-HU-006-01 (Positivo - Transacciones normales)
**Descripción:** 3 transacciones espaciadas en 10 minutos.

**Datos de Entrada:**
- Transacción 1: `T+0s`
- Transacción 2: `T+5min`
- Transacción 3: `T+10min`

**Pasos:**
```gherkin
Scenario: TC-HU-006-01 - Transacciones normales
  Given que las transacciones están espaciadas > 5 min
  When ejecuto RapidTransactionStrategy.evaluate()
  Then el contador de transacciones se resetea
  And el resultado es LOW_RISK
```

**Resultado Esperado:** LOW_RISK

**Archivo de Test:** `tests/unit/test_rapid_transaction_strategy.py::TestRapidTransactionStrategy::test_three_transactions_within_limit_low_risk`

---

### 🧪 HU-007 – Detección de Horario Inusual

**Como** sistema de detección de fraude  
**Quiero** detectar transacciones en horarios atípicos para el usuario  
**Para** identificar posible uso no autorizado

**Descripción:**  
Analizar el patrón de horarios de transacciones del usuario. Si una transacción ocurre en un horario significativamente diferente al patrón habitual, incrementar el nivel de riesgo.

#### Criterios de Aceptación

```gherkin
Feature: Detección de horario inusual

  Scenario: Transacción en horario habitual
    Given que el usuario opera entre 9am-6pm
    When evalúo una transacción a las 2pm
    Then el resultado es LOW_RISK

  Scenario: Transacción en horario inusual
    Given que el usuario opera entre 9am-6pm
    When evalúo una transacción a las 3am
    Then el resultado es MEDIUM_RISK
    And el motivo es "Unusual transaction time"
```

#### 🧪 TC-HU-007-01 (Positivo - Horario normal)
**Descripción:** Transacción dentro del horario habitual.

**Datos de Entrada:**
- Historial: `9am-6pm (días laborales)`
- Transacción actual: `2:00 PM`

**Pasos:**
```gherkin
Scenario: TC-HU-007-01 - Horario habitual
  Given que la hora está dentro del patrón
  When ejecuto UnusualTimeStrategy.evaluate()
  Then el resultado es LOW_RISK
```

**Resultado Esperado:** LOW_RISK

**Archivo de Test:** `tests/unit/test_unusual_time_strategy.py::TestUnusualTimeStrategy::test_within_normal_hours_low_risk`

---

## MÓDULO 3: ⚙️ CONFIGURACIÓN Y GOBERNANZA (HU-008 a HU-009)

### 🧪 HU-008 – Modificación de Umbrales sin Redespliegue

**Como** administrador del sistema  
**Quiero** modificar los umbrales de las reglas de fraude vía API  
**Para** ajustar el sistema sin necesidad de redesplegar código

**Descripción:**  
Exponer un endpoint que permita actualizar los parámetros de configuración de las estrategias de fraude que se aplican inmediatamente a nuevas transacciones.


#### Criterios de Aceptación

```gherkin
Feature: Modificación dinámica de umbrales

  Scenario: Actualización exitosa del umbral
    Given que tengo permisos de administrador
    When envío POST "/api/v1/config/thresholds" con nuevo valor
      | campo            | valor |
      | amount_threshold | 2000  |
    Then el sistema responde con código 200
    And la configuración se actualiza inmediatamente
```

#### 🧪 TC-HU-008-01 (Positivo)
**Descripción:** Actualizar umbral de monto exitosamente.

**Datos de Entrada:**
- Endpoint: `POST /api/v1/config/thresholds`
- Body: `{"amount_threshold": 2000}`

**Pasos:**
```gherkin
Scenario: TC-HU-008-01 - Actualización de umbral
  Given que soy administrador
  When envío nuevo umbral
  Then se actualiza en Redis/configuración
  And las nuevas transacciones usan el nuevo umbral
```

**Resultado Esperado:** HTTP 200, configuración actualizada

**Archivo de Test:** `tests/unit/test_routes.py::TestConfigurationEndpoint::test_update_threshold_config`

---

---

## MÓDULO 4: 🔄 HUMAN IN THE LOOP (HU-010 a HU-012)

### 🧪 HU-010 – Envío de Transacciones a Cola de Revisión

**Como** sistema de evaluación  
**Quiero** enviar transacciones de RIESGO MEDIO/ALTO a una cola de mensajes  
**Para** que sean revisadas manualmente por un analista

**Descripción:**  
Las transacciones que resulten en MEDIUM_RISK o HIGH_RISK deben publicarse en RabbitMQ para revisión manual. Las transacciones de LOW_RISK se aprueban automáticamente.

#### Criterios de Aceptación

```gherkin
Feature: Encolamiento para revisión manual

  Scenario: Transacción de bajo riesgo se aprueba automáticamente
    Given una transacción evaluada con resultado "LOW_RISK"
    When el worker procesa la transacción
    Then la transacción se marca como "APPROVED"
    And NO se envía a la cola "fraud_review_queue"
    And se registra en auditoría con status "AUTO_APPROVED"

  Scenario: Transacción de riesgo medio se envía a revisión
    Given una transacción evaluada con resultado "MEDIUM_RISK"
    When el worker procesa la transacción
    Then la transacción se publica en cola "fraud_review_queue"
    And el status se marca como "PENDING_REVIEW"
    And se registra en auditoría

  Scenario: Transacción de alto riesgo con prioridad
    Given una transacción evaluada con resultado "HIGH_RISK"
    When el worker procesa la transacción
    Then se publica en cola con prioridad ALTA
    And se genera notificación al analista de guardia
```

#### 🧪 TC-HU-010-01 (Positivo - LOW_RISK aprobado)
**Descripción:** Transacción de bajo riesgo se aprueba automáticamente.

**Datos de Entrada:**
- transaction_id: `tx_001`
- risk_level: `LOW_RISK`
- user_id: `user_001`

**Pasos:**
```gherkin
Scenario: TC-HU-010-01 - Aprobación automática
  Given que el worker recibe transacción LOW_RISK
  When procesa el mensaje de RabbitMQ
  Then actualiza status a "APPROVED" en MongoDB
  And NO publica en cola de revisión manual
  And registra en audit log como "AUTO_APPROVED"
```

**Resultado Esperado:** Status "APPROVED", sin cola manual

**Archivo de Test:** `tests/unit/test_worker.py::TestWorkerService::test_worker_auto_approves_low_risk`

---

#### 🧪 TC-HU-010-02 (Negativo - MEDIUM_RISK a cola)
**Descripción:** Transacción de riesgo medio se envía a revisión manual.

**Datos de Entrada:**
- transaction_id: `tx_002`
- risk_level: `MEDIUM_RISK`
- reasons: `["Unknown device"]`

**Pasos:**
```gherkin
Scenario: TC-HU-010-02 - Envío a cola de revisión
  Given que el worker recibe transacción MEDIUM_RISK
  When procesa el mensaje
  Then actualiza status a "PENDING_REVIEW"
  And publica mensaje en cola "fraud_review_queue"
  And el mensaje contiene transaction_id, risk_level, reasons
```

**Resultado Esperado:** Status "PENDING_REVIEW", mensaje en cola

**Archivo de Test:** `tests/unit/test_worker.py::TestWorkerService::test_worker_sends_medium_risk_to_review_queue`

---

### 🧪 HU-011 – Gestión de Reglas Personalizadas

**Como** administrador  
**Quiero** crear y gestionar reglas de fraude personalizadas  
**Para** adaptar el sistema a patrones específicos de mi negocio

**Descripción:**  
Permitir al administrador crear reglas con condiciones personalizadas (ejemplo: "Si usuario de Colombia compra en USD >$1000, marcar HIGH_RISK").


#### Criterios de Aceptación

```gherkin
Feature: Gestión de reglas personalizadas

  Scenario: Creación de regla personalizada
    Given soy administrador autenticado
    When envío POST "/api/v1/admin/rules" con:
      | campo      | valor                           |
      | name       | "Colombia USD rule"             |
      | condition  | "country=CO AND currency=USD"   |
      | threshold  | 1000                            |
      | risk_level | "HIGH_RISK"                     |
    Then la regla se crea exitosamente
    And se aplica en próximas evaluaciones

  Scenario: Modificación de regla existente
    Given existe una regla con ID "rule_001"
    When envío PUT "/api/v1/admin/rules/rule_001"
    Then la regla se actualiza
    And se aplica inmediatamente

  Scenario: Desactivación de regla
    When envío DELETE "/api/v1/admin/rules/rule_001"
    Then la regla se marca como inactiva
    And deja de aplicarse en evaluaciones
```

#### 🧪 TC-HU-011-01 (Positivo)
**Descripción:** Crear regla personalizada exitosamente.

**Datos de Entrada:**
- name: `Colombia USD rule`
- condition: `country=CO AND currency=USD`
- threshold: `1000`

**Pasos:**
```gherkin
Scenario: TC-HU-011-01 - Creación de regla
  Given que soy admin con permisos
  When envío datos de nueva regla
  Then se crea en base de datos
  And se valida en próximas transacciones
```

**Resultado Esperado:** HTTP 201, regla creada

**Archivo de Test:** `tests/unit/test_routes.py::TestAdminRoutes::test_create_custom_rule`

---

### 🧪 HU-012 – Revisión Manual por Analista

**Como** analista de fraude  
**Quiero** revisar transacciones sospechosas desde el dashboard  
**Para** decidir si aprobarlas o rechazarlas

**Descripción:**  
Dashboard administrativo muestra transacciones pendientes y permite aprobarlas/rechazarlas con justificación obligatoria.

#### Criterios de Aceptación

```gherkin
Feature: Revisión manual por analista

  Scenario: Listado de transacciones pendientes
    Given existen 5 transacciones "PENDING_REVIEW"
    When el analista consulta GET "/api/v1/admin/transactions/pending"
    Then recibe lista de 5 transacciones
    And cada una muestra: ID, usuario, monto, riesgo, motivos

  Scenario: Aprobación con justificación
    Given transacción "tx_001" en PENDING_REVIEW
    When envía PUT "/api/v1/admin/transactions/tx_001/review" con:
      | campo    | valor                             |
      | decision | APPROVED                          |
      | notes    | Usuario verificado por llamada    |
      | analyst  | analyst_maria                     |
    Then transacción se marca "APPROVED"
    And se registra decisión en audit log

  Scenario: Rechazo sin justificación (error)
    When envía decision sin campo "notes"
    Then recibe status 422
    And error indica "notes field is required"
```

#### 🧪 TC-HU-012-01 (Positivo - Aprobación)
**Descripción:** Analista aprueba transacción con justificación.

**Datos de Entrada:**
- transaction_id: `tx_001`
- decision: `APPROVED`
- notes: `Usuario verificado por llamada telefónica`
- analyst: `analyst_maria`

**Pasos:**
```gherkin
Scenario: TC-HU-012-01 - Aprobación por analista
  Given que existe transacción PENDING_REVIEW
  When analista envía decisión APPROVED con notes
  Then status se actualiza a APPROVED
  And se crea registro en audit_decisions
  And usuario recibe notificación
```

**Resultado Esperado:** HTTP 200, transacción aprobada

**Archivo de Test:** `tests/unit/test_routes.py::TestReviewEndpoint::test_analyst_approves_transaction`

---

## MÓDULO 5: 📊 DASHBOARDS Y VISUALIZACIÓN (HU-013 a HU-014)

### 🧪 HU-013 – Dashboard de Usuario (Historial)

**Como** usuario final  
**Quiero** ver el historial de mis transacciones y su estado  
**Para** conocer cuáles fueron aprobadas o rechazadas

**Descripción:**  
Frontend de usuario muestra lista de transacciones propias con estado, monto, fecha y nivel de riesgo detectado.

#### Criterios de Aceptación

```gherkin
Feature: Historial de transacciones del usuario

  Scenario: Usuario consulta su historial
    Given el usuario "user_001" está autenticado
    And tiene 10 transacciones en el sistema
    When accede a GET "/api/v1/user/transactions"
    Then recibe 200 OK
    And el response contiene 10 transacciones
    And cada una muestra: ID, monto, fecha, status, risk_level

  Scenario: Filtro por rango de fechas
    Given el usuario tiene transacciones de ene-mar
    When consulta con ?from=2026-02-01&to=2026-02-28
    Then recibe solo transacciones de febrero

  Scenario: Usuario no puede ver datos de otros
    Given usuario "user_001" autenticado
    When intenta ?userId=user_002
    Then recibe 403 Forbidden
```

#### 🧪 TC-HU-013-01 (Positivo)
**Descripción:** Usuario consulta su historial exitosamente.

**Datos de Entrada:**
- user_id: `user_001` (autenticado)
- Endpoint: `GET /api/v1/user/transactions`

**Pasos:**
```gherkin
Scenario: TC-HU-013-01 - Consulta de historial
  Given que usuario está autenticado
  When consulta su endpoint de transacciones
  Then recibe lista de sus transacciones
  And no ve transacciones de otros usuarios
```

**Resultado Esperado:** HTTP 200, lista de transacciones propias

**Archivo de Test:** `tests/unit/test_routes.py::TestUserEndpoint::test_get_user_transactions`

---

### 🧪 HU-014 – Dashboard Admin (Métricas)

**Como** administrador  
**Quiero** ver métricas y estadísticas de detección de fraude  
**Para** monitorear la efectividad del sistema

**Descripción:**  
Dashboard administrativo muestra métricas: total evaluado, % por nivel de riesgo, falsos positivos, tiempo promedio de revisión.


#### Criterios de Aceptación

```gherkin
Feature: Dashboard de métricas de fraude

  Scenario: Visualización de métricas generales
    Given existen transacciones evaluadas
    When admin consulta GET "/api/v1/admin/metrics"
    Then recibe 200 OK
    And el response contiene:
      | métrica                  | tipo   |
      | total_transactions       | number |
      | low_risk_percentage      | number |
      | medium_risk_percentage   | number |
      | high_risk_percentage     | number |
      | avg_review_time_minutes  | number |
      | false_positive_rate      | number |

  Scenario: Top usuarios sospechosos
    When consulta GET "/api/v1/admin/metrics/top-suspicious-users"
    Then recibe lista de 10 usuarios
    And cada uno muestra: userId, suspicious_count, last_incident
```

#### 🧪 TC-HU-014-01 (Positivo)
**Descripción:** Admin consulta métricas generales.

**Datos de Entrada:**
- Endpoint: `GET /api/v1/admin/metrics`
- Rol: `admin`

**Pasos:**
```gherkin
Scenario: TC-HU-014-01 - Métricas generales
  Given que existen transacciones procesadas
  When admin consulta endpoint de métricas
  Then recibe estadísticas calculadas
  And los porcentajes suman 100%
```

**Resultado Esperado:** HTTP 200, métricas completas

**Archivo de Test:** `tests/unit/test_routes.py::TestMetricsEndpoint::test_get_general_metrics`

---

**Documento creado:** Enero 07, 2026    
**Versión:** 1.0   
