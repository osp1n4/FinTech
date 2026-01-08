# 🧪 Test Cases - Fraud Detection Engine (Gherkin)

## Estructura de Archivos de Testing

```
tests/
├── unit/
│   ├── test_domain_models.py           # TC-001 a TC-015
│   ├── test_fraud_strategies.py        # TC-003, TC-004, TC-005, TC-006, TC-007
│   ├── test_use_cases.py               # TC-020 a TC-030
│   └── test_location_edge_cases.py     # TC-005-05 a TC-005-45
└── integration/
    ├── test_api_endpoints.py           # TC-001, TC-008, TC-009
    ├── test_audit_service.py           # TC-002
    ├── test_rabbitmq_worker.py         # TC-010
    ├── test_custom_rules.py            # TC-011
    ├── test_manual_review.py           # TC-012
    ├── test_user_dashboard.py          # TC-013
    └── test_metrics_dashboard.py       # TC-014
```

---

# HU-001: Recepción de Transacciones por API

## TC-001-01: Recepción exitosa de transacción válida

**Archivo:** `tests/integration/test_api_endpoints.py`

```gherkin
Feature: Recepción de transacciones por API REST

  @integration @critical
  Scenario: Recepción exitosa de transacción válida
    Given el API está disponible en "http://localhost:8000"
    And tengo los siguientes datos de transacción:
      | campo     | valor                |
      | userId    | user_001             |
      | amount    | 500.00               |
      | location  | 4.7110,-74.0721      |
      | deviceId  | device_mobile_001    |
    When envío una petición POST a "/api/v1/transaction/validate"
    Then la respuesta tiene status code 202
    And el cuerpo de la respuesta contiene:
      """json
      {
        "message": "Transaction received for processing",
        "transaction_id": "<uuid>",
        "status": "PROCESSING"
      }
      """
    And el header "Content-Type" es "application/json"
```

**Implementación Python:**

```python
def test_receive_valid_transaction(api_client):
    """TC-001-01: Recepción exitosa de transacción válida"""
    # Given
    transaction_data = {
        "userId": "user_001",
        "amount": 500.00,
        "location": "4.7110,-74.0721",
        "deviceId": "device_mobile_001"
    }
    
    # When
    response = api_client.post(
        "/api/v1/transaction/validate",
        json=transaction_data
    )
    
    # Then
    assert response.status_code == 202
    assert "transaction_id" in response.json()
    assert response.json()["message"] == "Transaction received for processing"
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
```

---

## TC-001-02: Rechazo de transacción sin userId

```gherkin
  @integration @validation
  Scenario: Rechazo de transacción sin userId
    Given el API está disponible
    And tengo una transacción sin el campo "userId":
      | campo     | valor                |
      | amount    | 500.00               |
      | location  | 4.7110,-74.0721      |
      | deviceId  | device_mobile_001    |
    When envío una petición POST a "/api/v1/transaction/validate"
    Then la respuesta tiene status code 422
    And el cuerpo de la respuesta contiene:
      """json
      {
        "detail": [
          {
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

## Resumen de Test Cases

| HU      | Test Cases | Unit | Integration | Total |
|---------|------------|------|-------------|-------|
| HU-001  | 5          | 0    | 5           | 5     |
| HU-002  | 5          | 0    | 5           | 5     |
| HU-003  | 5          | 5    | 0           | 5     |
| HU-004  | 5          | 5    | 0           | 5     |
| HU-005  | 5+         | 45+  | 0           | 45+   |
| HU-006  | 5          | 4    | 1           | 5     |
| HU-007  | 5          | 5    | 0           | 5     |
| HU-008  | 5          | 0    | 5           | 5     |
| HU-009  | 3          | 0    | 3           | 3     |
| HU-010  | 5          | 0    | 5           | 5     |
| HU-011  | 5          | 0    | 5           | 5     |
| HU-012  | 5          | 0    | 5           | 5     |
| HU-013  | 4          | 0    | 4           | 4     |
| HU-014  | 4          | 0    | 4           | 4     |
| **TOTAL** | **66+** | **59+** | **42** | **106+** |

---

**Documento creado:** Enero 2026  
**Última actualización:** Enero 8, 2026  
**Versión:** 1.0  
**Total de Test Cases Documentados:** 106+
