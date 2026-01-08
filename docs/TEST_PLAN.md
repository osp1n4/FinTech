# 🧪 Test Plan - Fraud Detection Engine

## 1. Introducción

### 1.1 Propósito
Este documento describe el plan de pruebas automatizadas para el Fraud Detection Engine, enfocándose exclusivamente en pruebas unitarias e integraciones ejecutables mediante frameworks de testing.

### 1.2 Alcance
- **Incluido:** Pruebas unitarias, pruebas de integración, pruebas de API, pruebas de componentes
- **Excluido:** Pruebas manuales, pruebas exploratorias, pruebas de usuario final

### 1.3 Objetivos de Calidad
- ✅ Cobertura de código ≥ 70% en capas Domain y Application
- ✅ 100% de historias de usuario con pruebas automatizadas
- ✅ 0 regresiones en funcionalidades críticas
- ✅ Tiempo de ejecución del suite completo < 5 minutos

---

## 2. Estrategia de Testing

### 2.1 Pirámide de Testing

```
        /\
       /  \          E2E (10%)
      /____\         - Flujos críticos end-to-end
     /      \        
    /________\       Integration (30%)
   /          \      - API endpoints con servicios reales
  /____________\     - Worker + RabbitMQ + MongoDB
                     
    Unit Tests (60%)
    - Domain models
    - Strategies
    - Use cases
```

### 2.2 Frameworks y Herramientas

| Componente | Framework | Propósito |
|------------|-----------|-----------|
| **Backend Unit** | pytest | Tests unitarios de lógica de negocio |
| **Backend Integration** | pytest + TestClient (FastAPI) | Tests de API con mocks |
| **Coverage** | pytest-cov | Medición de cobertura |
| **Mocking** | pytest-mock, unittest.mock | Simulación de dependencias |
| **Fixtures** | pytest fixtures | Datos de prueba reutilizables |
| **Async Tests** | pytest-asyncio | Tests de código asíncrono |

### 2.3 Ambientes de Testing

- **Unit Tests:** Sin dependencias externas (mocks)
- **Integration Tests:** Docker Compose con MongoDB, Redis, RabbitMQ
- **CI Pipeline:** GitHub Actions con servicios containerizados

---

## 3. Test Cases por Historia de Usuario

### 3.1 HU-001: Recepción de Transacciones

**Archivo:** `tests/integration/test_api_endpoints.py::TestTransactionEndpoint`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-001-01 | Recepción exitosa de transacción válida | Integration | Alta |
| TC-001-02 | Rechazo de transacción sin userId | Integration | Alta |
| TC-001-03 | Rechazo de transacción con monto negativo | Integration | Alta |
| TC-001-04 | Rechazo de transacción con ubicación inválida | Integration | Media |
| TC-001-05 | Validación de schema JSON completo | Integration | Media |

**Cobertura esperada:** 95%

---

### 3.2 HU-002: Auditoría de Evaluaciones

**Archivo:** `tests/integration/test_audit_service.py::TestAuditLog`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-002-01 | Registro de evaluación exitosa | Integration | Alta |
| TC-002-02 | Consulta de auditoría por usuario | Integration | Alta |
| TC-002-03 | Consulta de auditoría por nivel de riesgo | Integration | Media |
| TC-002-04 | Inmutabilidad del log (rechazo de PUT) | Integration | Alta |
| TC-002-05 | Ordenamiento por timestamp descendente | Integration | Baja |

**Cobertura esperada:** 90%

---

### 3.3 HU-003: Regla de Umbral de Monto

**Archivo:** `tests/unit/test_fraud_strategies.py::TestAmountThresholdStrategy`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-003-01 | Transacción dentro del umbral (PASS) | Unit | Alta |
| TC-003-02 | Transacción que excede el umbral (FAIL) | Unit | Alta |
| TC-003-03 | Transacción exactamente en el umbral | Unit | Alta |
| TC-003-04 | Umbral cero (casos edge) | Unit | Media |
| TC-003-05 | Monto negativo (validación) | Unit | Media |

**Cobertura esperada:** 100%

---

### 3.4 HU-004: Validación de Dispositivo

**Archivo:** `tests/unit/test_device_validation.py::TestDeviceValidationStrategy`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-004-01 | Dispositivo conocido y registrado | Unit | Alta |
| TC-004-02 | Dispositivo desconocido | Unit | Alta |
| TC-004-03 | Usuario sin dispositivos (primera tx) | Unit | Alta |
| TC-004-04 | Registro automático de nuevo dispositivo | Unit | Media |
| TC-004-05 | Case insensitive en deviceId | Unit | Baja |

**Cobertura esperada:** 95%

---

### 3.5 HU-005: Regla de Ubicación Inusual

**Archivo:** `tests/unit/test_location_strategies.py::TestUnusualLocationStrategy`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-005-01 | Transacción desde ubicación cercana (<100 km) | Unit | Alta |
| TC-005-02 | Transacción desde ubicación lejana (>100 km) | Unit | Alta |
| TC-005-03 | Primera transacción sin historial | Unit | Alta |
| TC-005-04 | Ubicación exactamente a 100 km | Unit | Media |
| TC-005-05 | Coordenadas en polos (casos extremos) | Unit | Baja |

**Cobertura esperada:** 100%

**Archivo adicional:** `tests/unit/test_location_edge_cases.py` (40+ edge cases)

---

### 3.6 HU-006: Transacciones en Cadena

**Archivo:** `tests/unit/test_rapid_transaction.py::TestRapidTransactionStrategy`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-006-01 | Transacciones espaciadas normalmente | Unit | Alta |
| TC-006-02 | Cuarta transacción en <5 minutos | Unit | Alta |
| TC-006-03 | Reinicio de contador después de 5 min | Unit | Alta |
| TC-006-04 | Exactamente 3 transacciones en 300 seg | Unit | Media |
| TC-006-05 | Múltiples usuarios concurrentes | Integration | Media |

**Cobertura esperada:** 90%

---

### 3.7 HU-007: Detección de Horario Inusual

**Archivo:** `tests/unit/test_time_based_strategies.py::TestUnusualTimeStrategy`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-007-01 | Transacción en horario habitual | Unit | Alta |
| TC-007-02 | Transacción en horario inusual | Unit | Alta |
| TC-007-03 | Usuario nuevo sin patrón | Unit | Alta |
| TC-007-04 | Ajuste por zonas horarias | Unit | Media |
| TC-007-05 | Patrón de fin de semana vs días laborales | Unit | Baja |

**Cobertura esperada:** 85%

---

### 3.8 HU-008: Modificación de Umbrales

**Archivo:** `tests/integration/test_config_management.py::TestConfigUpdate`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-008-01 | Actualización exitosa del umbral de monto | Integration | Alta |
| TC-008-02 | Actualización del umbral de distancia | Integration | Alta |
| TC-008-03 | Rechazo de valor inválido (negativo) | Integration | Alta |
| TC-008-04 | Múltiples parámetros simultáneos | Integration | Media |
| TC-008-05 | Aplicación inmediata en nuevas tx | Integration | Alta |

**Cobertura esperada:** 95%

---

### 3.9 HU-009: Consulta de Configuración

**Archivo:** `tests/integration/test_config_management.py::TestConfigRetrieval`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-009-01 | Consulta exitosa de configuración default | Integration | Alta |
| TC-009-02 | Consulta después de actualización | Integration | Alta |
| TC-009-03 | Validación de estructura JSON | Integration | Media |

**Cobertura esperada:** 90%

---

### 3.10 HU-010: Cola de Revisión Manual

**Archivo:** `tests/integration/test_rabbitmq_worker.py::TestManualReviewQueue`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-010-01 | LOW_RISK se aprueba automáticamente | Integration | Alta |
| TC-010-02 | MEDIUM_RISK se envía a cola | Integration | Alta |
| TC-010-03 | HIGH_RISK se envía con prioridad alta | Integration | Alta |
| TC-010-04 | Publicación correcta en RabbitMQ | Integration | Alta |
| TC-010-05 | Registro en auditoría con status correcto | Integration | Media |

**Cobertura esperada:** 90%

---

### 3.11 HU-011: Gestión de Reglas Personalizadas

**Archivo:** `tests/integration/test_custom_rules.py::TestCustomRuleManagement`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-011-01 | Creación exitosa de regla personalizada | Integration | Alta |
| TC-011-02 | Desactivación de regla existente | Integration | Alta |
| TC-011-03 | Rechazo de JSON inválido en parámetros | Integration | Alta |
| TC-011-04 | Eliminación de regla personalizada | Integration | Media |
| TC-011-05 | Listado de reglas con filtros | Integration | Media |

**Cobertura esperada:** 85%

---

### 3.12 HU-012: Revisión Manual por Analista

**Archivo:** `tests/integration/test_manual_review.py::TestAnalystReview`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-012-01 | Listado de transacciones pendientes | Integration | Alta |
| TC-012-02 | Aprobación con justificación | Integration | Alta |
| TC-012-03 | Rechazo con justificación | Integration | Alta |
| TC-012-04 | Rechazo de revisión sin notes | Integration | Alta |
| TC-012-05 | Auditoría de decisión del analista | Integration | Media |

**Cobertura esperada:** 90%

---

### 3.13 HU-013: Historial de Usuario

**Archivo:** `tests/integration/test_user_dashboard.py::TestUserTransactionHistory`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-013-01 | Consulta de historial propio | Integration | Alta |
| TC-013-02 | Filtro por rango de fechas | Integration | Media |
| TC-013-03 | Restricción de acceso a otras transacciones | Integration | Alta |
| TC-013-04 | Paginación de resultados | Integration | Media |

**Cobertura esperada:** 85%

---

### 3.14 HU-014: Métricas de Fraude

**Archivo:** `tests/integration/test_metrics_dashboard.py::TestFraudMetrics`

| Test Case ID | Descripción | Tipo | Prioridad |
|--------------|-------------|------|-----------|
| TC-014-01 | Métricas generales del sistema | Integration | Alta |
| TC-014-02 | Métricas filtradas por fecha | Integration | Media |
| TC-014-03 | Top usuarios sospechosos | Integration | Media |
| TC-014-04 | Cálculo de tasa de falsos positivos | Integration | Media |

**Cobertura esperada:** 80%

---

## 4. Test Suites y Ejecución

### 4.1 Suite de Tests Unitarios

```bash
# Ejecutar solo tests unitarios
pytest tests/unit/ -v

# Con cobertura
pytest tests/unit/ --cov=services/shared/domain --cov=services/shared/application --cov-report=html

# Tests rápidos (excluir lentos)
pytest tests/unit/ -m "not slow"
```

**Tiempo esperado:** < 30 segundos

---

### 4.2 Suite de Tests de Integración

```bash
# Levantar servicios
docker-compose up -d mongodb redis rabbitmq

# Ejecutar tests de integración
pytest tests/integration/ -v

# Con servicios en CI
pytest tests/integration/ --cov=services --cov-report=xml
```

**Tiempo esperado:** 2-3 minutos

---

### 4.3 Suite Completa

```bash
# Ejecutar todo el suite
pytest -v --cov=services --cov-report=html --cov-report=xml

# En CI (GitHub Actions)
pytest --cov=services --cov-report=xml --cov-fail-under=70
```

**Tiempo esperado:** < 5 minutos

---

## 5. Fixtures y Datos de Prueba

### 5.1 Fixtures Principales

**Archivo:** `tests/conftest.py`

```python
@pytest.fixture
def sample_transaction_data():
    """Transacción válida para pruebas"""

@pytest.fixture
def mock_mongodb():
    """Mock de MongoDB client"""

@pytest.fixture
def mock_redis():
    """Mock de Redis client"""

@pytest.fixture
def mock_rabbitmq():
    """Mock de RabbitMQ publisher"""

@pytest.fixture
def api_client():
    """TestClient de FastAPI"""
```

### 5.2 Datos de Prueba

| Dataset | Descripción | Ubicación |
|---------|-------------|-----------|
| Valid Transactions | 20 transacciones válidas variadas | `tests/fixtures/valid_transactions.json` |
| Edge Case Locations | 40+ coordenadas extremas | `tests/fixtures/edge_locations.json` |
| User Profiles | Perfiles con historial | `tests/fixtures/user_profiles.json` |

---

## 6. Criterios de Aceptación del Test Plan

### 6.1 Definición de Done

✅ Todos los tests pasan en ambiente local  
✅ Todos los tests pasan en CI  
✅ Cobertura ≥ 70% en Domain y Application  
✅ 0 warnings de pytest  
✅ Documentación de test cases actualizada  

### 6.2 Criterios de Éxito por Sprint

| Sprint | Objetivo | Meta de Cobertura |
|--------|----------|-------------------|
| Sprint 1 | HU-001, HU-002, HU-003 | ≥ 60% |
| Sprint 2 | HU-004, HU-005, HU-008, HU-009 | ≥ 65% |
| Sprint 3 | HU-006, HU-007, HU-010 | ≥ 70% |
| Sprint 4 | HU-011, HU-012, HU-013, HU-014 | ≥ 75% |

---

## 7. Mantenimiento del Test Plan

### 7.1 Frecuencia de Actualización

- **Diaria:** Ejecución en CI con cada push
- **Semanal:** Revisión de cobertura y métricas
- **Por Sprint:** Actualización del documento con nuevos test cases

### 7.2 Responsables

| Rol | Responsabilidad |
|-----|-----------------|
| **Developers** | Crear tests unitarios antes del código (TDD) |
| **QA Lead** | Mantener test plan actualizado |
| **Tech Lead** | Revisar cobertura y calidad de tests en PRs |

---

## 8. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Tests lentos (>5 min) | Media | Alto | Paralelizar ejecución, optimizar fixtures |
| Flaky tests (intermitentes) | Baja | Alto | Identificar y corregir inmediatamente |
| Baja cobertura en capas críticas | Media | Crítico | Bloquear PRs con cobertura < 70% |
| Tests desactualizados | Alta | Medio | Code review obligatorio de tests |

---

## Apéndices

### A. Comandos Útiles

```bash
# Tests de un módulo específico
pytest tests/unit/test_fraud_strategies.py -v

# Tests por marca (marker)
pytest -m "unit" -v
pytest -m "integration" -v
pytest -m "slow" -v

# Generar reporte de cobertura
pytest --cov=services --cov-report=html
# Ver en: htmlcov/index.html

# Tests con output detallado
pytest -vv -s

# Tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Tests hasta primer fallo
pytest -x

# Re-ejecutar solo tests que fallaron
pytest --lf
```

### B. Configuración pytest

**Archivo:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests (>1s)"
]
addopts = "-ra -q --strict-markers"
```

---

**Documento creado:** Enero 2026  
**Última actualización:** Enero 8, 2026  
**Versión:** 1.0  
**Total Test Cases:** 75+
