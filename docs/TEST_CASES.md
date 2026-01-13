# 🧪 Test Cases - Fraud Detection Engine

**Proyecto:** Fraud Detection Engine  
**Fecha:** Enero 08, 2026  
**Total HU:** 14  
**Total Test Cases:** 63  
**Tests Implementados:** 162  
**Cobertura:** 95%

---

## Estructura de Archivos de Testing

```
tests/
├── unit/
│   ├── test_domain_models.py           # HU-001, HU-002
│   ├── test_fraud_strategies.py        # HU-003, HU-004
│   ├── test_location_strategy.py       # HU-005
│   ├── test_location_edge_cases.py     # HU-005 (casos extremos)
│   ├── test_rapid_transaction.py       # HU-006
│   ├── test_unusual_time_strategy.py   # HU-007
│   ├── test_routes.py                  # HU-008, HU-009, HU-011, HU-012, HU-013, HU-014
│   ├── test_worker.py                  # HU-010
│   └── test_use_cases.py               # HU-001
└── integration/
    └── test_api_endpoints.py           # Tests de integración
```

---

## MÓDULO 1: 📡 RECEPCIÓN Y AUDITORÍA (HU-001 a HU-002)

### 🧪 HU-001 – Recepción de Transacciones por API

#### 🧪 TC-HU-001-01 (Positivo)
**Descripción:** Validar recepción exitosa de transacción válida.

**Datos de Entrada:**
- userId: `user_001`
- amount: `500.00`
- location: `4.7110,-74.0721`
- deviceId: `device_mobile_001`
- Endpoint: `POST /api/v1/transactions/evaluate`

**Pasos:**
```gherkin
Scenario: Recepción exitosa de transacción válida
  Given el API de fraud detection está disponible
  When envío POST a /api/v1/transactions/evaluate con datos válidos
  Then el sistema responde con código 202 Accepted
  And retorna transaction_id y risk_level
  And la transacción se registra en MongoDB para auditoría
```

**Resultado Esperado:** Transacción recibida correctamente, evaluada por estrategias de fraude, y guardada en auditoría con risk_level asignado.

**Archivo de Test:** `tests/unit/test_use_cases.py::test_evaluate_transaction_success`

---

#### 🧪 TC-HU-001-02 (Negativo)
**Descripción:** Rechazar transacción sin campo userId requerido.

**Datos de Entrada:**
- userId: `null` (campo omitido)
- amount: `500.00`
- location: `4.7110,-74.0721`
- deviceId: `device_mobile_001`
- Endpoint: `POST /api/v1/transactions/evaluate`

**Pasos:**
```gherkin
Scenario: Rechazo de transacción sin userId
  Given el API está disponible
  When envío POST sin el campo userId
  Then el sistema responde con código 422 Unprocessable Entity
  And retorna mensaje de error "userId is required"
```

**Resultado Esperado:** Error de validación HTTP 422 indicando campo faltante.

**Archivo de Test:** `tests/unit/test_routes.py::test_evaluate_transaction_missing_user_id`

---

#### 🧪 TC-HU-001-03 (Negativo)
**Descripción:** Rechazar transacción con monto negativo.

**Datos de Entrada:**
- userId: `user_001`
- amount: `-100.00`
- location: `4.7110,-74.0721`
- deviceId: `device_mobile_001`

**Pasos:**
```gherkin
Scenario: Rechazo de monto negativo
  Given el API está disponible
  When envío POST con amount negativo (-100.00)
  Then el sistema responde con código 422
  And retorna mensaje "amount must be positive"
```

**Resultado Esperado:** Validación rechaza montos negativos antes de procesar.

**Archivo de Test:** `tests/unit/test_domain_models.py::test_transaction_negative_amount`

---

### 🧪 HU-002 – Auditoría Inmutable de Evaluaciones

#### 🧪 TC-HU-002-01 (Positivo)
**Descripción:** Verificar que toda evaluación se registra automáticamente en MongoDB.

**Datos de Entrada:**
- transaction_id: `tx_12345`
- user_id: `user_001`
- amount: `500.00`
- risk_level: `LOW_RISK`
- strategies_applied: `["AmountThreshold", "DeviceValidation"]`

**Pasos:**
```gherkin
Scenario: Registro automático en auditoría
  Given una transacción fue evaluada exitosamente
  When consulto GET /api/v1/audit/transactions/{transaction_id}
  Then el sistema responde con código 200
  And retorna todos los campos de la evaluación
  And incluye timestamp de creación
  And contiene lista de estrategias aplicadas
```

**Resultado Esperado:** Registro completo e inmutable en MongoDB con todos los detalles de la evaluación.

**Archivo de Test:** `tests/unit/test_adapters.py::test_mongodb_audit_repository_save`

---

#### 🧪 TC-HU-002-02 (Positivo)
**Descripción:** Consultar historial completo de transacciones de un usuario.

**Datos de Entrada:**
- user_id: `user_001`
- Transacciones existentes: 3 (tx_001, tx_002, tx_004)
- Endpoint: `GET /api/v1/audit/user/user_001`

**Pasos:**
```gherkin
Scenario: Consulta de historial por usuario
  Given existen múltiples transacciones de diferentes usuarios
  When consulto GET /api/v1/audit/user/user_001
  Then el sistema responde con código 200
  And retorna array con 3 transacciones del usuario
  And no incluye transacciones de otros usuarios
  And están ordenadas por fecha descendente
```

**Resultado Esperado:** Lista filtrada correctamente por userId, solo transacciones propias.

**Archivo de Test:** `tests/unit/test_adapters.py::test_mongodb_audit_repository_find_by_user`

---

## MÓDULO 2: 🚨 ESTRATEGIAS DE DETECCIÓN DE FRAUDE (HU-003 a HU-007)

### 🧪 HU-003 – Regla de Umbral de Monto

#### 🧪 TC-HU-003-01 (Positivo)
**Descripción:** Transacción con monto dentro del umbral configurado (LOW_RISK).

**Datos de Entrada:**
- amount: `800.00`
- Umbral configurado: `1000.00`

**Pasos:**
```gherkin
Scenario: Monto bajo dentro del umbral
  Given el umbral de riesgo está configurado en 1000.00
  When evalúo una transacción de 800.00
  Then la estrategia AmountThreshold retorna LOW_RISK
  And el factor de riesgo es 0.0
```

**Resultado Esperado:** Transacción aprobada como bajo riesgo.

**Archivo de Test:** `tests/unit/test_fraud_strategies.py::test_amount_threshold_low_risk`

---

#### 🧪 TC-HU-003-02 (Negativo)
**Descripción:** Transacción con monto que excede el umbral (HIGH_RISK).

**Datos de Entrada:**
- amount: `1500.00`
- Umbral configurado: `1000.00`

**Pasos:**
```gherkin
Scenario: Monto excede umbral configurado
  Given el umbral de riesgo está configurado en 1000.00
  When evalúo una transacción de 1500.00
  Then la estrategia AmountThreshold retorna HIGH_RISK
  And el factor de riesgo es 0.5 (50% sobre el umbral)
```

**Resultado Esperado:** Transacción marcada como alto riesgo por exceder límite.

**Archivo de Test:** `tests/unit/test_fraud_strategies.py::test_amount_threshold_high_risk`

---

### 🧪 HU-004 – Validación de Dispositivo Conocido

#### 🧪 TC-HU-004-01 (Positivo)
**Descripción:** Dispositivo registrado previamente para el usuario (LOW_RISK).

**Datos de Entrada:**
- user_id: `user_001`
- device_id: `device_mobile_001`
- Dispositivos conocidos: `["device_mobile_001", "device_laptop_001"]`

**Pasos:**
```gherkin
Scenario: Dispositivo conocido del usuario
  Given el usuario user_001 tiene dispositivos registrados
  When evalúo transacción desde device_mobile_001
  Then la estrategia DeviceValidation retorna LOW_RISK
  And el factor de riesgo es 0.0
```

**Resultado Esperado:** Sin riesgo adicional por dispositivo confiable.

**Archivo de Test:** `tests/unit/test_device_validation.py::test_device_validation_known_device`

---

#### 🧪 TC-HU-004-02 (Negativo)
**Descripción:** Dispositivo nuevo no registrado (MEDIUM_RISK).

**Datos de Entrada:**
- user_id: `user_001`
- device_id: `device_unknown_999`
- Dispositivos conocidos: `["device_mobile_001"]`

**Pasos:**
```gherkin
Scenario: Dispositivo desconocido
  Given el usuario user_001 solo tiene device_mobile_001 registrado
  When evalúo transacción desde device_unknown_999
  Then la estrategia DeviceValidation retorna MEDIUM_RISK
  And el factor de riesgo es 0.3
```

**Resultado Esperado:** Alerta de riesgo medio por dispositivo no reconocido.

**Archivo de Test:** `tests/unit/test_device_validation.py::test_device_validation_unknown_device`

---

### 🧪 HU-005 – Detección de Ubicación Inusual

#### 🧪 TC-HU-005-01 (Positivo)
**Descripción:** Transacción desde ubicación habitual del usuario (LOW_RISK).

**Datos de Entrada:**
- user_id: `user_001`
- location: `4.7110,-74.0721` (Bogotá)
- Última ubicación: `4.7100,-74.0700` (mismo radio)

**Pasos:**
```gherkin
Scenario: Ubicación dentro del área habitual
  Given el usuario realiza transacciones en Bogotá regularmente
  When evalúo transacción desde coordenadas cercanas
  Then la estrategia LocationStrategy retorna LOW_RISK
  And la distancia calculada es menor a 50km
```

**Resultado Esperado:** Sin alerta de fraude geográfico.

**Archivo de Test:** `tests/unit/test_location_strategy.py::test_location_nearby`

---

#### 🧪 TC-HU-005-02 (Negativo)
**Descripción:** Transacción desde ubicación distante (HIGH_RISK).

**Datos de Entrada:**
- user_id: `user_001`
- location: `40.7128,-74.0060` (Nueva York)
- Última ubicación: `4.7110,-74.0721` (Bogotá)
- Tiempo transcurrido: `1 hora`

**Pasos:**
```gherkin
Scenario: Viaje imposible detectado
  Given última transacción fue en Bogotá hace 1 hora
  When evalúo transacción desde Nueva York
  Then la estrategia LocationStrategy retorna HIGH_RISK
  And detecta "impossible travel" (distancia >5000km en <2 horas)
```

**Resultado Esperado:** Alerta crítica de fraude por teletransportación imposible.

**Archivo de Test:** `tests/unit/test_location_strategy.py::test_location_impossible_travel`

---

#### 🧪 TC-HU-005-03 (Edge Case)
**Descripción:** Coordenadas en el límite de latitud/longitud válidas.

**Datos de Entrada:**
- location: `90.0,-180.0` (Polo Norte, extremo oeste)

**Pasos:**
```gherkin
Scenario: Coordenadas en límites válidos
  Given coordenadas en valores extremos válidos
  When valido la ubicación
  Then el sistema acepta las coordenadas
  And calcula distancia correctamente
```

**Resultado Esperado:** Sistema maneja casos extremos sin errores.

**Archivo de Test:** `tests/unit/test_location_edge_cases.py::test_edge_coordinates`

---

### 🧪 HU-006 – Detección de Transacciones en Cadena

#### 🧪 TC-HU-006-01 (Positivo)
**Descripción:** Usuario realiza transacciones espaciadas normalmente (LOW_RISK).

**Datos de Entrada:**
- user_id: `user_001`
- Transacciones en última hora: `1`
- Umbral configurado: `3 transacciones/hora`

**Pasos:**
```gherkin
Scenario: Frecuencia normal de transacciones
  Given el usuario tiene 1 transacción en la última hora
  When evalúo nueva transacción
  Then la estrategia RapidTransactionStrategy retorna LOW_RISK
  And el contador es menor al umbral
```

**Resultado Esperado:** Comportamiento normal sin alertas.

**Archivo de Test:** `tests/unit/test_rapid_transaction.py::test_rapid_transaction_low_risk`

---

#### 🧪 TC-HU-006-02 (Negativo)
**Descripción:** Usuario supera umbral de transacciones por hora (HIGH_RISK).

**Datos de Entrada:**
- user_id: `user_001`
- Transacciones en última hora: `4`
- Umbral configurado: `3 transacciones/hora`

**Pasos:**
```gherkin
Scenario: Transacciones en cadena detectadas
  Given el usuario ya realizó 4 transacciones en 1 hora
  When evalúo la quinta transacción
  Then la estrategia RapidTransactionStrategy retorna HIGH_RISK
  And el factor de riesgo es proporcional al exceso
```

**Resultado Esperado:** Alerta de fraude por actividad anormal frecuente.

**Archivo de Test:** `tests/unit/test_rapid_transaction.py::test_rapid_transaction_high_risk`

---

### 🧪 HU-007 – Detección de Horario Inusual

#### 🧪 TC-HU-007-01 (Positivo)
**Descripción:** Transacción en horario laboral habitual (LOW_RISK).

**Datos de Entrada:**
- timestamp: `2026-01-12T14:30:00` (lunes 2:30 PM)

**Pasos:**
```gherkin
Scenario: Horario normal de operación
  Given la transacción ocurre un lunes a las 2:30 PM
  When evalúo el horario con UnusualTimeStrategy
  Then retorna LOW_RISK
  And el horario está dentro del rango 8AM-8PM
```

**Resultado Esperado:** Sin alertas por horario normal.

**Archivo de Test:** `tests/unit/test_unusual_time_strategy.py::test_unusual_time_low_risk`

---

#### 🧪 TC-HU-007-02 (Negativo)
**Descripción:** Transacción en horario sospechoso madrugada (MEDIUM_RISK).

**Datos de Entrada:**
- timestamp: `2026-01-12T03:15:00` (lunes 3:15 AM)

**Pasos:**
```gherkin
Scenario: Transacción en madrugada
  Given la transacción ocurre a las 3:15 AM
  When evalúo el horario
  Then retorna MEDIUM_RISK
  And detecta horario fuera de rango habitual
```

**Resultado Esperado:** Alerta moderada por horario inusual.

**Archivo de Test:** `tests/unit/test_unusual_time_strategy.py::test_unusual_time_high_risk`

---

## MÓDULO 3: ⚙️ CONFIGURACIÓN DINÁMICA (HU-008 a HU-009)

### 🧪 HU-008 – Modificación de Umbrales sin Redespliegue

#### 🧪 TC-HU-008-01 (Positivo)
**Descripción:** Actualizar umbral de monto mediante API.

**Datos de Entrada:**
- Endpoint: `PUT /api/v1/admin/config`
- Body: `{"amount_threshold": 2000.00}`
- Rol: `admin`

**Pasos:**
```gherkin
Scenario: Actualización exitosa de umbral
  Given soy un usuario con rol admin
  When envío PUT /api/v1/admin/config con nuevo valor
  Then el sistema responde con código 200
  And la nueva configuración se aplica inmediatamente
  And las siguientes transacciones usan el nuevo umbral
```

**Resultado Esperado:** Configuración actualizada sin reiniciar servicios.

**Archivo de Test:** `tests/unit/test_routes.py::test_update_config_success`

---

#### 🧪 TC-HU-008-02 (Negativo)
**Descripción:** Rechazar actualización con valor inválido.

**Datos de Entrada:**
- Body: `{"amount_threshold": -500.00}` (negativo)

**Pasos:**
```gherkin
Scenario: Validación de configuración inválida
  Given intento actualizar con valor negativo
  When envío PUT con amount_threshold = -500
  Then el sistema responde con código 422
  And retorna mensaje "threshold must be positive"
```

**Resultado Esperado:** Validación impide configuraciones incorrectas.

**Archivo de Test:** `tests/unit/test_routes.py::test_update_config_invalid`

---

### 🧪 HU-009 – Consulta de Configuración Actual

#### 🧪 TC-HU-009-01 (Positivo)
**Descripción:** Consultar configuración vigente del sistema.

**Datos de Entrada:**
- Endpoint: `GET /api/v1/admin/config`

**Pasos:**
```gherkin
Scenario: Obtener configuración actual
  Given el sistema tiene configuración activa
  When envío GET /api/v1/admin/config
  Then el sistema responde con código 200
  And retorna todos los umbrales configurados
  And incluye valores de amount_threshold, max_transactions_per_hour, etc
```

**Resultado Esperado:** JSON con toda la configuración vigente.

**Archivo de Test:** `tests/unit/test_routes.py::test_get_config_success`

---

## MÓDULO 4: 👤 HUMAN IN THE LOOP (HU-010 a HU-012)

### 🧪 HU-010 – Envío a Cola de Revisión Manual

#### 🧪 TC-HU-010-01 (Positivo)
**Descripción:** Transacción LOW_RISK se aprueba automáticamente sin cola.

**Datos de Entrada:**
- transaction_id: `tx_low_001`
- risk_level: `LOW_RISK`

**Pasos:**
```gherkin
Scenario: Aprobación automática de bajo riesgo
  Given una transacción fue evaluada como LOW_RISK
  When el worker procesa el resultado
  Then la transacción se aprueba automáticamente
  And NO se envía a RabbitMQ para revisión manual
```

**Resultado Esperado:** Flujo automático sin intervención humana.

**Archivo de Test:** `tests/unit/test_worker.py::test_worker_auto_approve_low_risk`

---

#### 🧪 TC-HU-010-02 (Negativo)
**Descripción:** Transacción MEDIUM/HIGH_RISK va a cola de revisión.

**Datos de Entrada:**
- transaction_id: `tx_high_002`
- risk_level: `HIGH_RISK`
- Cola: `manual_review_queue`

**Pasos:**
```gherkin
Scenario: Envío a cola de revisión manual
  Given una transacción fue evaluada como HIGH_RISK
  When el worker procesa el resultado
  Then publica mensaje en RabbitMQ queue "manual_review_queue"
  And incluye prioridad ALTA
  And el estado cambia a "PENDING_REVIEW"
```

**Resultado Esperado:** Transacción encolada para analista de fraude.

**Archivo de Test:** `tests/unit/test_worker.py::test_worker_send_to_manual_review`

---

### 🧪 HU-011 – Gestión de Reglas Personalizadas

#### 🧪 TC-HU-011-01 (Positivo)
**Descripción:** Admin crea regla personalizada para usuario específico.

**Datos de Entrada:**
- Endpoint: `POST /api/v1/admin/rules`
- Body: `{"user_id": "user_vip_001", "max_amount": 50000, "rule_type": "vip_limit"}`

**Pasos:**
```gherkin
Scenario: Creación de regla personalizada
  Given soy admin del sistema
  When envío POST con regla para usuario VIP
  Then el sistema responde con código 201
  And la regla se aplica en siguientes evaluaciones
  And se almacena en colección "custom_rules"
```

**Resultado Esperado:** Regla activa para casos especiales (VIP, listas blancas).

**Archivo de Test:** `tests/unit/test_routes.py::test_create_custom_rule`

---

### 🧪 HU-012 – Revisión Manual por Analista

#### 🧪 TC-HU-012-01 (Positivo)
**Descripción:** Analista aprueba transacción con justificación.

**Datos de Entrada:**
- transaction_id: `tx_pending_001`
- Endpoint: `PUT /api/v1/admin/transactions/tx_pending_001/review`
- Body: `{"decision": "APPROVED", "analyst_notes": "Cliente verificado por teléfono"}`

**Pasos:**
```gherkin
Scenario: Aprobación manual exitosa
  Given una transacción está en estado PENDING_REVIEW
  When el analista envía decisión APPROVED con notas
  Then el sistema responde con código 200
  And el estado cambia a "APPROVED"
  And se registra analyst_id y timestamp en auditoría
```

**Resultado Esperado:** Transacción aprobada manualmente con trazabilidad completa.

**Archivo de Test:** `tests/unit/test_routes.py::test_manual_review_approve`

---

#### 🧪 TC-HU-012-02 (Negativo)
**Descripción:** Rechazar aprobación sin notas justificativas.

**Datos de Entrada:**
- Body: `{"decision": "APPROVED", "analyst_notes": ""}` (vacío)

**Pasos:**
```gherkin
Scenario: Validación de notas obligatorias
  Given intento aprobar sin justificación
  When envío decisión con analyst_notes vacío
  Then el sistema responde con código 422
  And retorna "analyst_notes is required for manual decisions"
```

**Resultado Esperado:** Sistema obliga a documentar decisiones manuales.

**Archivo de Test:** `tests/unit/test_routes.py::test_manual_review_missing_notes`

---

## MÓDULO 5: 📊 DASHBOARDS Y VISUALIZACIÓN (HU-013 a HU-014)

### 🧪 HU-013 – Dashboard Usuario (Historial de Transacciones)

#### 🧪 TC-HU-013-01 (Positivo)
**Descripción:** Usuario consulta su propio historial de transacciones.

**Datos de Entrada:**
- user_id: `user_001` (autenticado)
- Endpoint: `GET /api/v1/user/transactions`

**Pasos:**
```gherkin
Scenario: Consulta de historial propio
  Given estoy autenticado como user_001
  When consulto GET /api/v1/user/transactions
  Then el sistema responde con código 200
  And retorna solo mis transacciones
  And incluye risk_level, amount, timestamp para cada transacción
```

**Resultado Esperado:** Usuario ve únicamente su historial, no de otros.

**Archivo de Test:** `tests/unit/test_routes.py::test_get_user_transactions`

---

#### 🧪 TC-HU-013-02 (Negativo)
**Descripción:** Usuario no puede ver transacciones de otros.

**Datos de Entrada:**
- user_id autenticado: `user_001`
- user_id solicitado: `user_002`
- Endpoint: `GET /api/v1/user/transactions?user_id=user_002`

**Pasos:**
```gherkin
Scenario: Restricción de acceso a datos ajenos
  Given estoy autenticado como user_001
  When intento consultar transacciones de user_002
  Then el sistema responde con código 403 Forbidden
  And retorna mensaje "Access denied: cannot view other users' data"
```

**Resultado Esperado:** Segregación correcta de datos por usuario.

**Archivo de Test:** `tests/unit/test_routes.py::test_user_cannot_access_others_transactions`

---

### 🧪 HU-014 – Dashboard Admin (Métricas de Fraude)

#### 🧪 TC-HU-014-01 (Positivo)
**Descripción:** Admin consulta métricas generales del sistema.

**Datos de Entrada:**
- Endpoint: `GET /api/v1/admin/metrics`
- Rol: `admin`

**Pasos:**
```gherkin
Scenario: Obtener métricas generales
  Given soy admin del sistema
  When consulto GET /api/v1/admin/metrics
  Then el sistema responde con código 200
  And retorna total_transactions, fraud_rate, approval_rate
  And incluye distribución por risk_level (LOW, MEDIUM, HIGH)
```

**Resultado Esperado:** Dashboard con KPIs para monitoreo de fraude.

**Archivo de Test:** `tests/unit/test_routes.py::test_get_admin_metrics`

---

## 📊 Resumen Completo de Test Cases

| HU | Módulo | Descripción | Test Cases | Tests Implementados |
|----|--------|-------------|------------|---------------------|
| HU-001 | Recepción | Recepción de transacciones | 3 | 17 |
| HU-002 | Auditoría | Auditoría inmutable | 2 | 16 |
| HU-003 | Fraude | Umbral de monto | 2 | 9 |
| HU-004 | Fraude | Dispositivo conocido | 2 | 8 |
| HU-005 | Fraude | Ubicación inusual | 3 | 39 |
| HU-006 | Fraude | Transacciones en cadena | 2 | 13 |
| HU-007 | Fraude | Horario inusual | 2 | 11 |
| HU-008 | Config | Modificar umbrales | 2 | 5 |
| HU-009 | Config | Consultar configuración | 1 | 3 |
| HU-010 | HITL | Cola de revisión manual | 2 | 20 |
| HU-011 | HITL | Reglas personalizadas | 1 | 4 |
| HU-012 | HITL | Revisión manual | 2 | 8 |
| HU-013 | Dashboard | Historial usuario | 2 | 6 |
| HU-014 | Dashboard | Métricas admin | 1 | 3 |
| **TOTAL** | **5 Módulos** | **14 HU** | **27** | **162** |

---

## 🎯 Cobertura por Tipo de Test

| Tipo | Cantidad | Porcentaje |
|------|----------|------------|
| Unit Tests | 152 | 94% |
| Integration Tests | 10 | 6% |
| **Total** | **162** | **100%** |

---

## ✅ Estado de Implementación

**Fecha:** Enero 12, 2026  
**Tests Pasando:** 162/162 (100%)  
**Tests Fallando:** 0  
**Tests Omitidos:** 0  
**Cobertura de Código:** 89%  
**Estado:** ✅ COMPLETO - Todos los test cases implementados y pasando

---

**Documento actualizado:** Enero 12, 2026  
**Versión:** 3.0 - Formato estandarizado con ejemplo US-001
            "loc": ["body", "userId"],
            "msg": "field required",
            "type": "value_error.missing"
          }
        ]
      }
      """
```

**Implementación Python:**

```python
def test_reject_transaction_without_user_id(api_client):
    """TC-001-02: Rechazo de transacción sin userId"""
    # Given
    invalid_transaction = {
        "amount": 500.00,
        "location": "4.7110,-74.0721",
        "deviceId": "device_mobile_001"
    }
    
    # When
    response = api_client.post(
        "/api/v1/transaction/validate",
        json=invalid_transaction
    )
    
    # Then
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"] == ["body", "userId"] for err in errors)
```

---

## TC-001-03: Rechazo de transacción con monto negativo

```gherkin
  @integration @validation
  Scenario: Rechazo de transacción con monto negativo
    Given el API está disponible
    And tengo una transacción con monto negativo:
      | campo     | valor                |
      | userId    | user_001             |
      | amount    | -100.00              |
      | location  | 4.7110,-74.0721      |
      | deviceId  | device_mobile_001    |
    When envío una petición POST a "/api/v1/transaction/validate"
    Then la respuesta tiene status code 422
    And el error contiene "amount must be positive"
```

**Implementación Python:**

```python
def test_reject_transaction_with_negative_amount(api_client):
    """TC-001-03: Rechazo de transacción con monto negativo"""
    # Given
    invalid_transaction = {
        "userId": "user_001",
        "amount": -100.00,
        "location": "4.7110,-74.0721",
        "deviceId": "device_mobile_001"
    }
    
    # When
    response = api_client.post(
        "/api/v1/transaction/validate",
        json=invalid_transaction
    )
    
    # Then
    assert response.status_code == 422
    assert "amount must be positive" in str(response.json())
```

---

## TC-001-04: Rechazo de ubicación en formato inválido

```gherkin
  @integration @validation
  Scenario Outline: Validación de formatos de ubicación
    Given el API está disponible
    And tengo una transacción con location "<location>"
    When envío la petición POST
    Then la respuesta tiene status code <status_code>
    And el mensaje es "<message>"

    Examples:
      | location          | status_code | message                      |
      | INVALID_GPS       | 422         | invalid location format      |
      | 200,300           | 422         | latitude out of range        |
      | 45,-200           | 422         | longitude out of range       |
      | abc,def           | 422         | invalid coordinates          |
      | 4.7110            | 422         | missing longitude            |
      | 4.7110,-74.0721   | 202         | Transaction received         |
```

**Implementación Python:**

```python
@pytest.mark.parametrize("location,expected_status,expected_msg", [
    ("INVALID_GPS", 422, "invalid location format"),
    ("200,300", 422, "latitude out of range"),
    ("45,-200", 422, "longitude out of range"),
    ("abc,def", 422, "invalid coordinates"),
    ("4.7110", 422, "missing longitude"),
    ("4.7110,-74.0721", 202, "Transaction received"),
])
def test_location_validation(api_client, location, expected_status, expected_msg):
    """TC-001-04: Validación de formatos de ubicación"""
    # Given
    transaction = {
        "userId": "user_001",
        "amount": 500.00,
        "location": location,
        "deviceId": "device_mobile_001"
    }
    
    # When
    response = api_client.post("/api/v1/transaction/validate", json=transaction)
    
    # Then
    assert response.status_code == expected_status
    assert expected_msg in str(response.json())
```

---

# HU-002: Auditoría de Evaluaciones

## TC-002-01: Registro de evaluación exitosa

**Archivo:** `tests/integration/test_audit_service.py`

```gherkin
Feature: Auditoría inmutable de evaluaciones de fraude

  @integration @audit @critical
  Scenario: Registro automático de evaluación en MongoDB
    Given una transacción fue procesada:
      | campo              | valor                           |
      | transaction_id     | tx_12345                        |
      | user_id            | user_001                        |
      | amount             | 500.00                          |
      | location           | 4.7110,-74.0721                 |
      | device_id          | device_mobile_001               |
      | risk_level         | LOW_RISK                        |
      | strategies_applied | AmountThreshold,DeviceValidation|
    When consulto el log de auditoría con GET "/api/v1/audit/transaction/tx_12345"
    Then la respuesta tiene status code 200
    And el registro contiene todos los campos esperados
    And el campo "created_at" es un timestamp válido
    And el campo "strategies_applied" es un array con 2 elementos
```

**Implementación Python:**

```python
def test_audit_log_creation(api_client, mock_mongodb):
    """TC-002-01: Registro de evaluación exitosa"""
    # Given - Se procesó una transacción
    transaction_id = "tx_12345"
    
    # When - Consultamos el audit log
    response = api_client.get(f"/api/v1/audit/transaction/{transaction_id}")
    
    # Then
    assert response.status_code == 200
    audit_data = response.json()
    
    assert audit_data["transaction_id"] == transaction_id
    assert audit_data["user_id"] == "user_001"
    assert audit_data["amount"] == 500.00
    assert audit_data["risk_level"] == "LOW_RISK"
    assert len(audit_data["strategies_applied"]) == 2
    assert "created_at" in audit_data
    
    # Verificar formato de timestamp
    from datetime import datetime
    datetime.fromisoformat(audit_data["created_at"])  # Debe parsear sin error
```

---

## TC-002-02: Consulta de auditoría por usuario

```gherkin
  @integration @audit
  Scenario: Obtener todas las transacciones de un usuario
    Given existen las siguientes transacciones en el sistema:
      | transaction_id | user_id  | amount  | risk_level  | created_at          |
      | tx_001         | user_001 | 100.00  | LOW_RISK    | 2026-01-01T10:00:00 |
      | tx_002         | user_001 | 1800.00 | HIGH_RISK   | 2026-01-01T11:00:00 |
      | tx_003         | user_002 | 300.00  | LOW_RISK    | 2026-01-01T12:00:00 |
      | tx_004         | user_001 | 500.00  | MEDIUM_RISK | 2026-01-01T13:00:00 |
    When consulto GET "/api/v1/audit/user/user_001"
    Then la respuesta tiene status code 200
    And el response contiene 3 transacciones
    And todas las transacciones tienen user_id "user_001"
    And están ordenadas por created_at en orden descendente
    And la primera transacción es tx_004
```

**Implementación Python:**

```python
def test_get_audit_by_user(api_client, seed_audit_data):
    """TC-002-02: Consulta de auditoría por usuario"""
    # Given - Ya existen transacciones (seed_audit_data fixture)
    
    # When
    response = api_client.get("/api/v1/audit/user/user_001")
    
    # Then
    assert response.status_code == 200
    transactions = response.json()
    
    assert len(transactions) == 3
    assert all(tx["user_id"] == "user_001" for tx in transactions)
    
    # Verificar orden descendente por created_at
    timestamps = [tx["created_at"] for tx in transactions]
    assert timestamps == sorted(timestamps, reverse=True)
    
    # Primera debe ser la más reciente
    assert transactions[0]["transaction_id"] == "tx_004"
```

---

## TC-002-03: Consulta por nivel de riesgo

```gherkin
  @integration @audit
  Scenario: Filtrar transacciones por nivel de riesgo
    Given existen transacciones con diferentes niveles de riesgo
    When consulto GET "/api/v1/audit/risk-level/HIGH_RISK"
    Then la respuesta tiene status code 200
    And todas las transacciones tienen risk_level "HIGH_RISK"
    And el conteo coincide con el total esperado
```

**Implementación Python:**

```python
def test_get_audit_by_risk_level(api_client, seed_audit_data):
    """TC-002-03: Consulta por nivel de riesgo"""
    # When
    response = api_client.get("/api/v1/audit/risk-level/HIGH_RISK")
    
    # Then
    assert response.status_code == 200
    transactions = response.json()
    
    assert all(tx["risk_level"] == "HIGH_RISK" for tx in transactions)
    assert len(transactions) > 0  # Al menos una HIGH_RISK en seed data
```

---

## TC-002-04: Inmutabilidad del log

```gherkin
  @integration @audit @security
  Scenario: Intento de modificar registro de auditoría
    Given existe un registro de auditoría con ID "audit_001"
    When envío una petición PUT a "/api/v1/audit/audit_001" con nuevos datos
    Then la respuesta tiene status code 405 (Method Not Allowed)
    And el mensaje indica "Audit logs are immutable"
    And al consultar el registro original, permanece sin cambios
```

**Implementación Python:**

```python
def test_audit_log_immutability(api_client):
    """TC-002-04: Inmutabilidad del log de auditoría"""
    # Given
    audit_id = "audit_001"
    original_response = api_client.get(f"/api/v1/audit/{audit_id}")
    original_data = original_response.json()
    
    # When - Intentar actualizar
    modified_data = {**original_data, "risk_level": "LOW_RISK"}
    update_response = api_client.put(
        f"/api/v1/audit/{audit_id}",
        json=modified_data
    )
    
    # Then
    assert update_response.status_code == 405
    assert "immutable" in update_response.json()["detail"].lower()
    
    # Verificar que el original no cambió
    check_response = api_client.get(f"/api/v1/audit/{audit_id}")
    assert check_response.json() == original_data
```

---

# HU-003: Regla de Umbral de Monto

## TC-003-01: Transacción dentro del umbral

**Archivo:** `tests/unit/test_fraud_strategies.py`

```gherkin
Feature: Estrategia de detección por umbral de monto

  @unit @strategy @critical
  Scenario: Transacción con monto por debajo del umbral configurado
    Given la estrategia AmountThresholdStrategy está configurada con umbral 1500.00
    And tengo una transacción con amount 800.00
    When ejecuto strategy.evaluate(transaction)
    Then el resultado es StrategyResult con status "PASS"
    And el campo risk_increment es 0
    And el campo reason es None
```

**Implementación Python:**

```python
def test_amount_below_threshold():
    """TC-003-01: Transacción dentro del umbral"""
    # Given
    strategy = AmountThresholdStrategy(threshold=1500.00)
    transaction = Transaction(
        transaction_id="tx_001",
        user_id="user_001",
        amount=800.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "PASS"
    assert result.risk_increment == 0
    assert result.reason is None
```

---

## TC-003-02: Transacción que excede el umbral

```gherkin
  @unit @strategy @critical
  Scenario: Transacción con monto que excede el umbral
    Given la estrategia AmountThresholdStrategy con umbral 1500.00
    And una transacción con amount 2000.00
    When ejecuto strategy.evaluate(transaction)
    Then el resultado es StrategyResult con status "FAIL"
    And el campo risk_increment es mayor a 0
    And el campo reason contiene "Amount exceeds threshold"
    And el campo details contiene amount=2000.00 y threshold=1500.00
```

**Implementación Python:**

```python
def test_amount_exceeds_threshold():
    """TC-003-02: Transacción que excede el umbral"""
    # Given
    strategy = AmountThresholdStrategy(threshold=1500.00)
    transaction = Transaction(
        transaction_id="tx_002",
        user_id="user_001",
        amount=2000.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "FAIL"
    assert result.risk_increment > 0
    assert "Amount exceeds threshold" in result.reason
    assert result.details["amount"] == 2000.00
    assert result.details["threshold"] == 1500.00
```

---

## TC-003-03: Transacción exactamente en el umbral

```gherkin
  @unit @strategy @edge-case
  Scenario: Transacción con monto exactamente igual al umbral
    Given la estrategia con umbral 1500.00
    And una transacción con amount exactamente 1500.00
    When ejecuto strategy.evaluate(transaction)
    Then el resultado es "PASS" (el umbral no se excede si es igual)
    And risk_increment es 0
```

**Implementación Python:**

```python
def test_amount_exactly_at_threshold():
    """TC-003-03: Transacción exactamente en el umbral"""
    # Given
    strategy = AmountThresholdStrategy(threshold=1500.00)
    transaction = Transaction(
        transaction_id="tx_003",
        user_id="user_001",
        amount=1500.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then - Igual al umbral NO lo excede
    assert result.status == "PASS"
    assert result.risk_increment == 0
```

---

# HU-005: Regla de Ubicación Inusual

## TC-005-01: Ubicación cercana

**Archivo:** `tests/unit/test_location_strategies.py`

```gherkin
Feature: Estrategia de detección por ubicación inusual

  @unit @strategy @location @critical
  Scenario: Transacción desde ubicación cercana a la última conocida
    Given el usuario "user_001" tiene última ubicación en:
      | latitude  | longitude   |
      | 4.7110    | -74.0721    |
    And una transacción desde ubicación:
      | latitude  | longitude   |
      | 4.6097    | -74.0817    |
    And la distancia calculada es aproximadamente 30 km
    And el umbral de distancia es 100 km
    When ejecuto UnusualLocationStrategy.evaluate(transaction)
    Then el resultado es "PASS"
    And risk_increment es 0
```

**Implementación Python:**

```python
def test_location_within_radius(mock_redis):
    """TC-005-01: Transacción desde ubicación cercana"""
    # Given
    strategy = UnusualLocationStrategy(
        redis_client=mock_redis,
        max_distance_km=100
    )
    
    # Usuario con última ubicación conocida
    mock_redis.hget.return_value = "4.7110,-74.0721"
    
    transaction = Transaction(
        transaction_id="tx_001",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=4.6097, longitude=-74.0817),  # ~30 km
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "PASS"
    assert result.risk_increment == 0
    assert result.details["distance_km"] < 100
```

---

## TC-005-02: Ubicación lejana

```gherkin
  @unit @strategy @location @critical
  Scenario: Transacción desde ubicación muy lejana
    Given el usuario tiene última ubicación en Bogotá (4.7110,-74.0721)
    And una transacción desde Medellín (6.2442,-75.5812)
    And la distancia es aproximadamente 200 km
    When ejecuto la estrategia
    Then el resultado es "FAIL"
    And risk_increment es mayor a 0
    And reason contiene "Unusual location distance: 200 km"
```

**Implementación Python:**

```python
def test_location_far_from_last_known(mock_redis):
    """TC-005-02: Transacción desde ubicación lejana"""
    # Given
    strategy = UnusualLocationStrategy(
        redis_client=mock_redis,
        max_distance_km=100
    )
    
    mock_redis.hget.return_value = "4.7110,-74.0721"  # Bogotá
    
    transaction = Transaction(
        transaction_id="tx_002",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=6.2442, longitude=-75.5812),  # Medellín ~200km
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "FAIL"
    assert result.risk_increment > 0
    assert "distance" in result.reason.lower()
    assert result.details["distance_km"] > 100
```

---

## TC-005-03: Primera transacción sin historial

```gherkin
  @unit @strategy @location
  Scenario: Usuario nuevo sin ubicación previa registrada
    Given el usuario "user_new_001" no tiene ubicaciones en Redis
    And una transacción desde cualquier ubicación válida
    When ejecuto la estrategia
    Then el resultado es "PASS"
    And la ubicación se registra en Redis como ubicación base
    And risk_increment es 0
```

**Implementación Python:**

```python
def test_first_transaction_no_location_history(mock_redis):
    """TC-005-03: Primera transacción sin historial"""
    # Given - Usuario sin historial
    strategy = UnusualLocationStrategy(redis_client=mock_redis, max_distance_km=100)
    mock_redis.hget.return_value = None  # Sin ubicación previa
    
    transaction = Transaction(
        transaction_id="tx_003",
        user_id="user_new_001",
        amount=500.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "PASS"
    assert result.risk_increment == 0
    
    # Verificar que se guardó la ubicación
    mock_redis.hset.assert_called_once_with(
        "user_locations",
        "user_new_001",
        "4.7110,-74.0721"
    )
```

---

## TC-005-04: Ubicación exactamente a 100 km (límite)

```gherkin
  @unit @strategy @location @edge-case
  Scenario: Transacción exactamente a la distancia umbral
    Given umbral de distancia configurado en 100 km
    And una transacción a exactamente 100.0 km de la última ubicación
    When ejecuto la estrategia
    Then el resultado es "PASS" (100 km no excede el umbral de 100)
```

**Implementación Python:**

```python
def test_location_exactly_at_threshold(mock_redis):
    """TC-005-04: Ubicación exactamente a 100 km"""
    # Given
    strategy = UnusualLocationStrategy(redis_client=mock_redis, max_distance_km=100)
    
    # Usar coordenadas que dan exactamente 100 km (calculadas previamente)
    mock_redis.hget.return_value = "4.7110,-74.0721"
    
    transaction = Transaction(
        transaction_id="tx_004",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=5.6110, longitude=-74.0721),  # Exactamente 100 km
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then - Exactamente en el umbral NO lo excede
    assert result.status == "PASS"
    assert abs(result.details["distance_km"] - 100.0) < 0.1  # Margen de precisión
```

---

# HU-008: Modificación de Umbrales

## TC-008-01: Actualización exitosa del umbral de monto

**Archivo:** `tests/integration/test_config_management.py`

```gherkin
Feature: Gestión dinámica de configuración

  @integration @config @critical
  Scenario: Actualizar umbral de monto sin redespliegue
    Given el sistema tiene umbral de monto en 1500.00
    When envío PUT "/api/v1/admin/config" con:
      """json
      {
        "amount_threshold": 2000.00
      }
      """
    Then la respuesta tiene status code 200
    And el response confirma "Configuration updated successfully"
    When consulto GET "/api/v1/admin/config"
    Then el campo "amount_threshold" es 2000.00
    When envío una transacción con amount 1800.00
    Then la transacción pasa la regla de monto (1800 < 2000)
```

**Implementación Python:**

```python
def test_update_amount_threshold(api_client):
    """TC-008-01: Actualización exitosa del umbral de monto"""
    # Given - Estado inicial
    initial_config = api_client.get("/api/v1/admin/config").json()
    assert initial_config["amount_threshold"] == 1500.00
    
    # When - Actualizar configuración
    update_response = api_client.put(
        "/api/v1/admin/config",
        json={"amount_threshold": 2000.00}
    )
    
    # Then
    assert update_response.status_code == 200
    assert "updated successfully" in update_response.json()["message"].lower()
    
    # Verificar que se aplicó
    new_config = api_client.get("/api/v1/admin/config").json()
    assert new_config["amount_threshold"] == 2000.00
    
    # Verificar que nueva transacción usa nuevo umbral
    tx_response = api_client.post(
        "/api/v1/transaction/validate",
        json={
            "userId": "user_001",
            "amount": 1800.00,  # Antes excedía (1800 > 1500), ahora no (1800 < 2000)
            "location": "4.7110,-74.0721",
            "deviceId": "device_001"
        }
    )
    assert tx_response.status_code == 202
```

---

## TC-008-03: Rechazo de valor inválido

```gherkin
  @integration @config @validation
  Scenario: Intento de actualizar con valor negativo
    When envío PUT "/api/v1/admin/config" con:
      """json
      {
        "amount_threshold": -500.00
      }
      """
    Then la respuesta tiene status code 422
    And el error contiene "amount_threshold must be positive"
    And la configuración anterior permanece sin cambios
```

**Implementación Python:**

```python
def test_reject_negative_threshold(api_client):
    """TC-008-03: Rechazo de valor de umbral inválido"""
    # Given
    original_config = api_client.get("/api/v1/admin/config").json()
    
    # When - Intentar establecer valor negativo
    response = api_client.put(
        "/api/v1/admin/config",
        json={"amount_threshold": -500.00}
    )
    
    # Then
    assert response.status_code == 422
    assert "must be positive" in response.json()["detail"]
    
    # Verificar que no cambió
    current_config = api_client.get("/api/v1/admin/config").json()
    assert current_config == original_config
```

---

# HU-010: Cola de Revisión Manual

## TC-010-01: LOW_RISK se aprueba automáticamente

**Archivo:** `tests/integration/test_rabbitmq_worker.py`

```gherkin
Feature: Encolamiento de transacciones para revisión manual

  @integration @rabbitmq @worker @critical
  Scenario: Transacción de bajo riesgo no requiere revisión
    Given una transacción fue evaluada con resultado "LOW_RISK"
    When el worker procesa el mensaje de la cola
    Then la transacción se marca como "APPROVED" en MongoDB
    And NO se publica mensaje en la cola "fraud_review_queue"
    And el audit log muestra status "AUTO_APPROVED"
```

**Implementación Python:**

```python
def test_low_risk_auto_approved(mock_mongodb, mock_rabbitmq):
    """TC-010-01: LOW_RISK se aprueba automáticamente"""
    # Given
    transaction_data = {
        "transaction_id": "tx_001",
        "user_id": "user_001",
        "amount": 100.00,
        "risk_level": "LOW_RISK"
    }
    
    # When - Worker procesa la transacción
    worker = FraudWorker(mongodb=mock_mongodb, rabbitmq=mock_rabbitmq)
    worker.process_transaction(transaction_data)
    
    # Then
    # Verificar que se guardó como APPROVED
    saved_doc = mock_mongodb.transactions.find_one({"transaction_id": "tx_001"})
    assert saved_doc["status"] == "APPROVED"
    
    # Verificar que NO se publicó en cola de revisión
    mock_rabbitmq.publish.assert_not_called()
    
    # Verificar audit log
    audit = mock_mongodb.audit_logs.find_one({"transaction_id": "tx_001"})
    assert audit["status"] == "AUTO_APPROVED"
```

---

## TC-010-02: MEDIUM_RISK se envía a cola

```gherkin
  @integration @rabbitmq @worker @critical
  Scenario: Transacción de riesgo medio requiere revisión manual
    Given una transacción evaluada con "MEDIUM_RISK"
    When el worker procesa el mensaje
    Then la transacción se marca como "PENDING_REVIEW"
    And se publica mensaje en la cola "fraud_review_queue"
    And el mensaje contiene: transaction_id, user_id, amount, risk_level, reasons
```

**Implementación Python:**

```python
def test_medium_risk_sent_to_review_queue(mock_mongodb, mock_rabbitmq):
    """TC-010-02: MEDIUM_RISK se envía a cola de revisión"""
    # Given
    transaction_data = {
        "transaction_id": "tx_002",
        "user_id": "user_001",
        "amount": 500.00,
        "risk_level": "MEDIUM_RISK",
        "reasons": ["Unknown device"]
    }
    
    # When
    worker = FraudWorker(mongodb=mock_mongodb, rabbitmq=mock_rabbitmq)
    worker.process_transaction(transaction_data)
    
    # Then
    # Verificar status PENDING_REVIEW
    saved_doc = mock_mongodb.transactions.find_one({"transaction_id": "tx_002"})
    assert saved_doc["status"] == "PENDING_REVIEW"
    
    # Verificar publicación en RabbitMQ
    mock_rabbitmq.publish.assert_called_once()
    published_data = mock_rabbitmq.publish.call_args[0][1]
    assert published_data["transaction_id"] == "tx_002"
    assert published_data["risk_level"] == "MEDIUM_RISK"
    assert "reasons" in published_data
```

---

# HU-012: Revisión Manual por Analista

## TC-012-02: Aprobación con justificación

**Archivo:** `tests/integration/test_manual_review.py`

```gherkin
Feature: Revisión manual de transacciones sospechosas

  @integration @review @critical
  Scenario: Analista aprueba transacción sospechosa
    Given existe una transacción "tx_001" con status "PENDING_REVIEW"
    When envío PUT "/api/v1/admin/transactions/tx_001/review" con:
      """json
      {
        "decision": "APPROVED",
        "notes": "Usuario verificado por llamada telefónica",
        "analyst": "analyst_maria"
      }
      """
    Then la respuesta tiene status code 200
    And la transacción se actualiza a status "APPROVED"
    And se crea registro en audit_decisions con:
      | campo         | valor                                    |
      | transaction_id| tx_001                                   |
      | analyst       | analyst_maria                            |
      | decision      | APPROVED                                 |
      | notes         | Usuario verificado por llamada telefónica|
      | timestamp     | <current_timestamp>                      |
```

**Implementación Python:**

```python
def test_analyst_approves_transaction(api_client, mock_mongodb):
    """TC-012-02: Aprobación de transacción por analista"""
    # Given - Transacción pendiente
    mock_mongodb.transactions.insert_one({
        "transaction_id": "tx_001",
        "user_id": "user_001",
        "status": "PENDING_REVIEW",
        "risk_level": "MEDIUM_RISK"
    })
    
    # When - Analista aprueba
    response = api_client.put(
        "/api/v1/admin/transactions/tx_001/review",
        json={
            "decision": "APPROVED",
            "notes": "Usuario verificado por llamada telefónica",
            "analyst": "analyst_maria"
        }
    )
    
    # Then
    assert response.status_code == 200
    
    # Verificar actualización en MongoDB
    updated_tx = mock_mongodb.transactions.find_one({"transaction_id": "tx_001"})
    assert updated_tx["status"] == "APPROVED"
    
    # Verificar registro de auditoría de decisión
    audit_decision = mock_mongodb.audit_decisions.find_one({"transaction_id": "tx_001"})
    assert audit_decision["analyst"] == "analyst_maria"
    assert audit_decision["decision"] == "APPROVED"
    assert "verificado" in audit_decision["notes"].lower()
    assert "timestamp" in audit_decision
```

---

## TC-012-04: Rechazo sin justificación

```gherkin
  @integration @review @validation
  Scenario: Intento de revisión sin campo notes
    Given una transacción pendiente de revisión
    When envío PUT con decision pero sin campo "notes"
    Then la respuesta tiene status code 422
    And el error contiene "notes field is required"
    And la transacción permanece en status "PENDING_REVIEW"
```

**Implementación Python:**

```python
def test_reject_review_without_notes(api_client, mock_mongodb):
    """TC-012-04: Intento de revisión sin justificación"""
    # Given
    mock_mongodb.transactions.insert_one({
        "transaction_id": "tx_002",
        "status": "PENDING_REVIEW"
    })
    
    # When - Intentar revisar sin notes
    response = api_client.put(
        "/api/v1/admin/transactions/tx_002/review",
        json={
            "decision": "APPROVED",
            "analyst": "analyst_maria"
            # Falta "notes"
        }
    )
    
    # Then
    assert response.status_code == 422
    assert "notes" in response.json()["detail"].lower()
    assert "required" in response.json()["detail"].lower()
    
    # Verificar que no cambió el status
    tx = mock_mongodb.transactions.find_one({"transaction_id": "tx_002"})
    assert tx["status"] == "PENDING_REVIEW"
```

---

# HU-006: Detección de Transacciones en Cadena

## TC-006-01: Transacciones espaciadas normalmente

**Archivo:** `tests/unit/test_rapid_transaction_strategy.py`

```gherkin
Feature: Detección de transacciones en cadena

  @unit @strategy @rapidtransaction
  Scenario: Tres transacciones espaciadas en 10 minutos
    Given el usuario "user_001" tiene historial en Redis
    And la ventana de tiempo es 5 minutos
    And el límite es 3 transacciones
    And las transacciones están espaciadas cada 5 minutos
    When ejecuto RapidTransactionStrategy.evaluate()
    Then el resultado es "PASS"
    And risk_increment es 0
```

**Implementación Python:**

```python
def test_three_transactions_within_limit_low_risk(mock_redis):
    """TC-006-01: Transacciones espaciadas normalmente"""
    # Given
    strategy = RapidTransactionStrategy(
        redis_client=mock_redis,
        time_window_minutes=5,
        max_transactions=3
    )
    
    # Simular 2 transacciones previas en 10 minutos
    mock_redis.lrange.return_value = [
        (datetime.now() - timedelta(minutes=10)).isoformat(),
        (datetime.now() - timedelta(minutes=5)).isoformat()
    ]
    
    transaction = Transaction(
        transaction_id="tx_003",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=datetime.now()
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "PASS"
    assert result.risk_increment == 0
```

---

## TC-006-02: Cuarta transacción en 4 minutos

```gherkin
  @unit @strategy @rapidtransaction @critical
  Scenario: Cuarta transacción excede el límite
    Given el usuario tiene 3 transacciones en los últimos 4 minutos
    And el límite es 3 transacciones en 5 minutos
    When evalúo la cuarta transacción
    Then el resultado es "FAIL"
    And risk_increment es mayor a 0
    And reason contiene "Rapid transaction sequence detected"
```

**Implementación Python:**

```python
def test_four_transactions_in_5_minutes_high_risk(mock_redis):
    """TC-006-02: Cuarta transacción en 4 minutos"""
    # Given
    strategy = RapidTransactionStrategy(
        redis_client=mock_redis,
        time_window_minutes=5,
        max_transactions=3
    )
    
    # Simular 3 transacciones en 4 minutos
    now = datetime.now()
    mock_redis.lrange.return_value = [
        (now - timedelta(minutes=4)).isoformat(),
        (now - timedelta(minutes=2)).isoformat(),
        (now - timedelta(minutes=1)).isoformat()
    ]
    
    transaction = Transaction(
        transaction_id="tx_004",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=now
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "FAIL"
    assert result.risk_increment > 0
    assert "rapid" in result.reason.lower()
```

---

# HU-007: Detección de Horario Inusual

## TC-007-01: Horario habitual (9am-6pm)

**Archivo:** `tests/unit/test_unusual_time_strategy.py`

```gherkin
Feature: Detección de horario inusual

  @unit @strategy @time
  Scenario: Transacción dentro del horario habitual del usuario
    Given el usuario tiene patrón de transacciones 9am-6pm
    And la transacción actual es a las 2:00 PM
    When ejecuto UnusualTimeStrategy.evaluate()
    Then el resultado es "PASS"
    And risk_increment es 0
```

**Implementación Python:**

```python
def test_within_normal_hours_low_risk(mock_redis):
    """TC-007-01: Transacción en horario habitual"""
    # Given
    strategy = UnusualTimeStrategy(
        redis_client=mock_redis,
        normal_hours=(9, 18)  # 9am-6pm
    )
    
    # Hora dentro del rango
    transaction_time = datetime.now().replace(hour=14, minute=0)  # 2:00 PM
    
    transaction = Transaction(
        transaction_id="tx_001",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=transaction_time
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "PASS"
    assert result.risk_increment == 0
```

---

## TC-007-02: Horario inusual (3am)

```gherkin
  @unit @strategy @time @critical
  Scenario: Transacción en horario inusual
    Given el usuario opera entre 9am-6pm
    And la transacción es a las 3:00 AM
    When ejecuto la estrategia
    Then el resultado es "FAIL"
    And risk_increment es mayor a 0
    And reason contiene "Unusual transaction time"
```

**Implementación Python:**

```python
def test_outside_normal_hours_medium_risk(mock_redis):
    """TC-007-02: Transacción en horario inusual"""
    # Given
    strategy = UnusualTimeStrategy(
        redis_client=mock_redis,
        normal_hours=(9, 18)
    )
    
    # Hora fuera del rango (3 AM)
    transaction_time = datetime.now().replace(hour=3, minute=0)
    
    transaction = Transaction(
        transaction_id="tx_002",
        user_id="user_001",
        amount=500.00,
        location=Location(latitude=4.7110, longitude=-74.0721),
        device_id="device_001",
        timestamp=transaction_time
    )
    
    # When
    result = strategy.evaluate(transaction)
    
    # Then
    assert result.status == "FAIL"
    assert result.risk_increment > 0
    assert "unusual" in result.reason.lower()
```

---

# HU-008: Modificación de Umbrales sin Redespliegue

## TC-008-01: Actualización exitosa del umbral de monto

**Archivo:** `tests/unit/test_routes.py`

```gherkin
Feature: Gestión dinámica de configuración

  @unit @config @critical
  Scenario: Actualizar umbral de monto sin redespliegue
    Given el sistema tiene umbral de monto en 1500.00
    When envío PUT "/api/v1/admin/config" con:
      """json
      {
        "amount_threshold": 2000.00
      }
      """
    Then la respuesta tiene status code 200
    And el response confirma "Configuration updated successfully"
    And al consultar GET "/api/v1/admin/config"
    Then el campo "amount_threshold" es 2000.00
```

**Implementación Python:**

```python
def test_update_amount_threshold_config(api_client, mock_redis):
    """TC-008-01: Actualización exitosa del umbral"""
    # Given - Configuración inicial
    mock_redis.hget.return_value = "1500.00"
    
    # When - Actualizar
    response = api_client.put(
        "/api/v1/admin/config",
        json={"amount_threshold": 2000.00}
    )
    
    # Then
    assert response.status_code == 200
    assert "updated" in response.json()["message"].lower()
    
    # Verificar que se guardó en Redis
    mock_redis.hset.assert_called_with("config", "amount_threshold", "2000.00")
```

---

## TC-008-02: Rechazo de valor inválido

```gherkin
  @unit @config @validation
  Scenario: Intento de actualizar con valor negativo
    When envío PUT con amount_threshold: -500.00
    Then la respuesta tiene status code 422
    And el error contiene "amount_threshold must be positive"
    And la configuración anterior permanece sin cambios
```

**Implementación Python:**

```python
def test_reject_negative_threshold(api_client, mock_redis):
    """TC-008-02: Rechazo de valor inválido"""
    # Given
    mock_redis.hget.return_value = "1500.00"
    
    # When
    response = api_client.put(
        "/api/v1/admin/config",
        json={"amount_threshold": -500.00}
    )
    
    # Then
    assert response.status_code == 422
    assert "must be positive" in response.json()["detail"]
    
    # Verificar que NO se actualizó
    mock_redis.hset.assert_not_called()
```

---

# HU-009: Consulta de Configuración Actual

## TC-009-01: Consulta exitosa de configuración

**Archivo:** `tests/unit/test_routes.py`

```gherkin
Feature: Consulta de configuración

  @unit @config
  Scenario: Obtener configuración actual
    Given el sistema tiene configuración guardada
    When envío GET "/api/v1/admin/config"
    Then la respuesta tiene status code 200
    And el response contiene:
      | campo             | valor   |
      | amount_threshold  | 1500.00 |
      | location_radius   | 100     |
      | time_window       | 5       |
```

**Implementación Python:**

```python
def test_get_current_config(api_client, mock_redis):
    """TC-009-01: Consulta de configuración"""
    # Given
    mock_redis.hgetall.return_value = {
        "amount_threshold": "1500.00",
        "location_radius": "100",
        "time_window": "5"
    }
    
    # When
    response = api_client.get("/api/v1/admin/config")
    
    # Then
    assert response.status_code == 200
    config = response.json()
    assert config["amount_threshold"] == 1500.00
    assert config["location_radius"] == 100
```

---

# HU-010: Envío de Transacciones a Cola de Revisión

## TC-010-01: LOW_RISK se aprueba automáticamente

**Archivo:** `tests/unit/test_worker.py`

```gherkin
Feature: Encolamiento para revisión manual

  @unit @worker @critical
  Scenario: Transacción de bajo riesgo se aprueba automáticamente
    Given una transacción evaluada con "LOW_RISK"
    When el worker procesa el mensaje
    Then la transacción se marca como "APPROVED"
    And NO se publica en cola "fraud_review_queue"
    And se registra en audit con "AUTO_APPROVED"
```

**Implementación Python:**

```python
def test_worker_auto_approves_low_risk(mock_mongodb, mock_rabbitmq):
    """TC-010-01: LOW_RISK aprobado automáticamente"""
    # Given
    transaction_data = {
        "transaction_id": "tx_001",
        "user_id": "user_001",
        "amount": 100.00,
        "risk_level": "LOW_RISK"
    }
    
    # When
    worker = FraudWorker(mongodb=mock_mongodb, rabbitmq=mock_rabbitmq)
    worker.process_transaction(transaction_data)
    
    # Then
    saved = mock_mongodb.transactions.find_one({"transaction_id": "tx_001"})
    assert saved["status"] == "APPROVED"
    
    # NO se publicó en RabbitMQ
    mock_rabbitmq.publish.assert_not_called()
```

---

## TC-010-02: MEDIUM_RISK se envía a cola

```gherkin
  @unit @worker @critical
  Scenario: Transacción de riesgo medio requiere revisión
    Given una transacción evaluada con "MEDIUM_RISK"
    When el worker procesa el mensaje
    Then la transacción se marca como "PENDING_REVIEW"
    And se publica mensaje en cola "fraud_review_queue"
    And el mensaje contiene: transaction_id, risk_level, reasons
```

**Implementación Python:**

```python
def test_worker_sends_medium_risk_to_review_queue(mock_mongodb, mock_rabbitmq):
    """TC-010-02: MEDIUM_RISK a cola de revisión"""
    # Given
    transaction_data = {
        "transaction_id": "tx_002",
        "risk_level": "MEDIUM_RISK",
        "reasons": ["Unknown device"]
    }
    
    # When
    worker = FraudWorker(mongodb=mock_mongodb, rabbitmq=mock_rabbitmq)
    worker.process_transaction(transaction_data)
    
    # Then
    saved = mock_mongodb.transactions.find_one({"transaction_id": "tx_002"})
    assert saved["status"] == "PENDING_REVIEW"
    
    # Se publicó en RabbitMQ
    mock_rabbitmq.publish.assert_called_once()
    published = mock_rabbitmq.publish.call_args[0][1]
    assert published["transaction_id"] == "tx_002"
```

---

# HU-011: Gestión de Reglas Personalizadas

## TC-011-01: Creación de regla personalizada

**Archivo:** `tests/unit/test_routes.py`

```gherkin
Feature: Gestión de reglas personalizadas

  @unit @admin @rules
  Scenario: Crear regla personalizada exitosamente
    Given soy administrador autenticado
    When envío POST "/api/v1/admin/rules" con:
      | campo      | valor                        |
      | name       | "Colombia USD rule"          |
      | condition  | "country=CO AND currency=USD"|
      | threshold  | 1000                         |
      | risk_level | "HIGH_RISK"                  |
    Then la respuesta es 201 Created
    And la regla se guarda en base de datos
```

**Implementación Python:**

```python
def test_create_custom_rule(api_client, mock_mongodb):
    """TC-011-01: Crear regla personalizada"""
    # Given / When
    response = api_client.post(
        "/api/v1/admin/rules",
        json={
            "name": "Colombia USD rule",
            "condition": "country=CO AND currency=USD",
            "threshold": 1000,
            "risk_level": "HIGH_RISK"
        }
    )
    
    # Then
    assert response.status_code == 201
    assert "rule_id" in response.json()
    
    # Verificar guardado en MongoDB
    mock_mongodb.rules.insert_one.assert_called_once()
```

---

# HU-012: Revisión Manual por Analista

## TC-012-01: Aprobación con justificación

**Archivo:** `tests/unit/test_routes.py`

```gherkin
Feature: Revisión manual de transacciones

  @unit @admin @review @critical
  Scenario: Analista aprueba transacción sospechosa
    Given transacción "tx_001" con status "PENDING_REVIEW"
    When envío PUT "/api/v1/admin/transactions/tx_001/review" con:
      | campo    | valor                             |
      | decision | APPROVED                          |
      | notes    | Usuario verificado por llamada    |
      | analyst  | analyst_maria                     |
    Then la respuesta es 200 OK
    And la transacción se actualiza a "APPROVED"
    And se crea registro en audit_decisions
```

**Implementación Python:**

```python
def test_analyst_approves_transaction(api_client, mock_mongodb):
    """TC-012-01: Aprobación por analista"""
    # Given
    mock_mongodb.transactions.find_one.return_value = {
        "transaction_id": "tx_001",
        "status": "PENDING_REVIEW"
    }
    
    # When
    response = api_client.put(
        "/api/v1/admin/transactions/tx_001/review",
        json={
            "decision": "APPROVED",
            "notes": "Usuario verificado por llamada",
            "analyst": "analyst_maria"
        }
    )
    
    # Then
    assert response.status_code == 200
    
    # Verificar actualización
    mock_mongodb.transactions.update_one.assert_called_once()
    update_call = mock_mongodb.transactions.update_one.call_args
    assert update_call[0][0]["transaction_id"] == "tx_001"
    assert update_call[0][1]["$set"]["status"] == "APPROVED"
```

---

## TC-012-02: Rechazo sin justificación (error)

```gherkin
  @unit @admin @review @validation
  Scenario: Intento de revisión sin campo notes
    When envío decision sin campo "notes"
    Then la respuesta es 422
    And el error contiene "notes field is required"
    And la transacción permanece en "PENDING_REVIEW"
```

**Implementación Python:**

```python
def test_reject_review_without_notes(api_client):
    """TC-012-02: Rechazo sin justificación"""
    # When
    response = api_client.put(
        "/api/v1/admin/transactions/tx_002/review",
        json={
            "decision": "APPROVED",
            "analyst": "analyst_maria"
            # Falta "notes"
        }
    )
    
    # Then
    assert response.status_code == 422
    assert "notes" in response.json()["detail"].lower()
```

---

# HU-013: Dashboard de Usuario - Historial

## TC-013-01: Consulta de historial propio

**Archivo:** `tests/unit/test_routes.py`

```gherkin
Feature: Historial de transacciones del usuario

  @unit @user @dashboard
  Scenario: Usuario consulta su historial
    Given el usuario "user_001" está autenticado
    And tiene 10 transacciones en el sistema
    When accede a GET "/api/v1/user/transactions"
    Then recibe 200 OK
    And el response contiene 10 transacciones
    And cada una muestra: ID, monto, fecha, status, risk_level
```

**Implementación Python:**

```python
def test_get_user_transactions(api_client, mock_mongodb):
    """TC-013-01: Usuario consulta su historial"""
    # Given
    mock_mongodb.transactions.find.return_value = [
        {
            "transaction_id": f"tx_{i}",
            "user_id": "user_001",
            "amount": 100.00 * i,
            "status": "APPROVED",
            "risk_level": "LOW_RISK"
        }
        for i in range(1, 11)
    ]
    
    # When
    response = api_client.get(
        "/api/v1/user/transactions",
        headers={"Authorization": "Bearer user_001_token"}
    )
    
    # Then
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 10
    assert all(tx["user_id"] == "user_001" for tx in transactions)
```

---

## TC-013-02: Usuario no puede ver datos de otros

```gherkin
  @unit @user @security
  Scenario: Usuario no puede ver transacciones de otros
    Given usuario "user_001" autenticado
    When intenta GET "/api/v1/user/transactions?userId=user_002"
    Then recibe 403 Forbidden
    And el mensaje indica "Access denied"
```

**Implementación Python:**

```python
def test_user_cannot_see_others_transactions(api_client):
    """TC-013-02: Aislamiento de datos por usuario"""
    # When
    response = api_client.get(
        "/api/v1/user/transactions?userId=user_002",
        headers={"Authorization": "Bearer user_001_token"}
    )
    
    # Then
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()
```

---

# HU-014: Dashboard Admin - Métricas

## TC-014-01: Consulta de métricas generales

**Archivo:** `tests/unit/test_routes.py`

```gherkin
Feature: Dashboard de métricas de fraude

  @unit @admin @metrics
  Scenario: Visualización de métricas generales
    Given existen transacciones evaluadas en el sistema
    When admin consulta GET "/api/v1/admin/metrics"
    Then recibe 200 OK
    And el response contiene:
      | métrica                  | tipo   |
      | total_transactions       | number |
      | low_risk_percentage      | number |
      | medium_risk_percentage   | number |
      | high_risk_percentage     | number |
      | avg_review_time_minutes  | number |
```

**Implementación Python:**

```python
def test_get_general_metrics(api_client, mock_mongodb):
    """TC-014-01: Métricas generales del sistema"""
    # Given
    mock_mongodb.transactions.count_documents.return_value = 1000
    mock_mongodb.transactions.aggregate.return_value = [
        {"_id": "LOW_RISK", "count": 700},
        {"_id": "MEDIUM_RISK", "count": 250},
        {"_id": "HIGH_RISK", "count": 50}
    ]
    
    # When
    response = api_client.get("/api/v1/admin/metrics")
    
    # Then
    assert response.status_code == 200
    metrics = response.json()
    
    assert metrics["total_transactions"] == 1000
    assert metrics["low_risk_percentage"] == 70.0
    assert metrics["medium_risk_percentage"] == 25.0
    assert metrics["high_risk_percentage"] == 5.0
```

---

## Resumen Completo de Test Cases

| HU | Descripción | Test Cases | Unit | Integration | Total Tests |
|----|-------------|------------|------|-------------|-------------|
| HU-001 | Recepción API | 5 | 0 | 5 | 17 |
| HU-002 | Auditoría | 5 | 0 | 5 | 16 |
| HU-003 | Umbral Monto | 5 | 5 | 0 | 9 |
| HU-004 | Dispositivo | 5 | 5 | 0 | 8 |
| HU-005 | Ubicación | 9 | 39 | 0 | 39 |
| HU-006 | Transacciones Cadena | 5 | 5 | 0 | 13 |
| HU-007 | Horario Inusual | 4 | 4 | 0 | 11 |
| HU-008 | Modificar Umbrales | 3 | 3 | 0 | 5 |
| HU-009 | Consultar Config | 2 | 2 | 0 | 3 |
| HU-010 | Cola Revisión | 5 | 5 | 0 | 20 |
| HU-011 | Reglas Personalizadas | 3 | 3 | 0 | 4 |
| HU-012 | Revisión Manual | 5 | 5 | 0 | 8 |
| HU-013 | Dashboard Usuario | 4 | 4 | 0 | 6 |
| HU-014 | Dashboard Admin | 3 | 3 | 0 | 3 |
| **TOTAL** | **14 HU** | **63** | **83** | **10** | **162** |

---

**Documento creado:** Enero 12, 2026  
**Última actualización:** Enero 12, 2026  
**Versión:** 2.0 - COMPLETO (14 HU cubiertas)  
**Total de Test Cases:** 63 documentados  
**Total de Tests:** 162 implementados
