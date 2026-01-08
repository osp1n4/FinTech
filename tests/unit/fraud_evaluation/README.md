# Tests Unitarios - fraud-evaluation-service

## 📁 Estructura

```
tests/unit/fraud_evaluation/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── test_models.py           # Tests para entidades y VOs
├── test_strategies.py       # Tests para estrategias de fraude
├── test_use_cases.py        # Tests para casos de uso
└── test_adapters.py         # Tests para adaptadores
```

## 🎯 Cobertura de Tests

### 1. Domain Layer (`test_models.py`)

**Location (Value Object)**
- ✅ Crear ubicación válida
- ✅ Inmutabilidad (no se puede modificar)
- ✅ Igualdad entre ubicaciones
- ✅ Validación de latitud (-90 a 90)
- ✅ Validación de longitud (-180 a 180)

**Transaction (Entity)**
- ✅ Crear transacción válida
- ✅ Rechazar monto negativo
- ✅ Rechazar monto cero

**FraudEvaluation (Entity)**
- ✅ Crear evaluación de fraude
- ✅ Timestamp automático
- ✅ Múltiples razones de riesgo
- ✅ Valores correctos de RiskLevel enum

### 2. Strategies (`test_strategies.py`)

**AmountThresholdStrategy**
- ✅ Transacción bajo umbral pasa (LOW_RISK)
- ✅ Transacción sobre umbral falla (HIGH_RISK)
- ✅ Transacción igual al umbral pasa
- ✅ Nombre correcto de estrategia

**LocationStrategy**
- ✅ Ubicación dentro del radio pasa
- ✅ Ubicación fuera del radio falla (MEDIUM_RISK)
- ✅ Sin ubicación previa pasa (primera transacción)
- ✅ Cálculo correcto de distancia Haversine

**DeviceValidationStrategy**
- ✅ Dispositivo conocido pasa
- ✅ Dispositivo desconocido falla
- ✅ Sin device_id genera alerta
- ✅ Primer dispositivo puede pasar

**Strategy Chaining**
- ✅ Múltiples estrategias todas pasan
- ✅ Una estrategia falla
- ✅ Acumulación de razones de múltiples estrategias

### 3. Application Layer (`test_use_cases.py`)

**EvaluateTransactionUseCase**
- ✅ Evaluar transacción bajo riesgo → APPROVED
- ✅ Evaluar transacción alto riesgo → REJECTED
- ✅ Evaluar transacción riesgo medio → PENDING_REVIEW
- ✅ Guardar ubicación en cache
- ✅ Agregar resultados de múltiples estrategias
- ✅ Guardar evaluación en repository
- ✅ Publicar evaluación en message broker

**ReviewTransactionUseCase**
- ✅ Aprobar transacción en revisión
- ✅ Rechazar transacción en revisión
- ✅ Fallar si transacción no existe
- ✅ Rechazar decisión inválida
- ✅ Rechazar re-revisar transacción ya revisada

### 4. Infrastructure Layer (`test_adapters.py`)

**MongoDBAdapter**
- ✅ Inicialización correcta
- ✅ Guardar evaluación (save_evaluation)
- ✅ Obtener evaluación por ID (encontrada)
- ✅ Obtener evaluación por ID (no encontrada)

**RedisAdapter**
- ✅ Inicialización correcta
- ✅ Obtener ubicación de usuario (encontrada)
- ✅ Obtener ubicación de usuario (no encontrada)
- ✅ Guardar ubicación de usuario
- ✅ Obtener dispositivos de usuario
- ✅ Agregar dispositivo a usuario

**RabbitMQAdapter**
- ✅ Inicialización correcta
- ✅ Publicar evaluación
- ✅ Publicar a cola correcta según status

## 🚀 Ejecutar Tests

### Todos los tests
```bash
pytest tests/unit/fraud_evaluation/
```

### Tests específicos
```bash
# Solo domain models
pytest tests/unit/fraud_evaluation/test_models.py

# Solo strategies
pytest tests/unit/fraud_evaluation/test_strategies.py

# Solo use cases
pytest tests/unit/fraud_evaluation/test_use_cases.py

# Solo adapters
pytest tests/unit/fraud_evaluation/test_adapters.py
```

### Con cobertura
```bash
pytest tests/unit/fraud_evaluation/ --cov=services.fraud_evaluation_service --cov-report=html
```

### Verbose (ver cada test)
```bash
pytest tests/unit/fraud_evaluation/ -v
```

### Solo tests que fallan
```bash
pytest tests/unit/fraud_evaluation/ --lf
```

## 📊 Estadísticas

### Número de Tests
- **Domain Models**: 14 tests
- **Strategies**: 21 tests
- **Use Cases**: 11 tests
- **Adapters**: 12 tests
- **Total**: **58 tests**

### Cobertura Esperada
- Domain Layer: ~95%
- Application Layer: ~90%
- Infrastructure Layer: ~80% (mocks)

## 🔧 Fixtures Compartidas (`conftest.py`)

```python
@pytest.fixture
def sample_transaction_data():
    """Datos de transacción de ejemplo"""
    ...

@pytest.fixture
def sample_high_amount_transaction():
    """Transacción de monto alto"""
    ...

@pytest.fixture
def sample_unusual_location_transaction():
    """Transacción de ubicación inusual"""
    ...
```

## 🧪 Patrones de Testing

### 1. Arrange-Act-Assert (AAA)
```python
def test_create_location_valid(self):
    # Arrange
    latitude = 40.7128
    longitude = -74.0060
    
    # Act
    location = Location(latitude=latitude, longitude=longitude)
    
    # Assert
    assert location.latitude == latitude
```

### 2. Mocking con unittest.mock
```python
@pytest.fixture
def mock_repository(self):
    repository = Mock()
    repository.save_evaluation = AsyncMock()
    return repository
```

### 3. Pytest Fixtures
```python
@pytest.mark.asyncio
async def test_evaluate_transaction(mock_repository, mock_cache):
    use_case = EvaluateTransactionUseCase(
        repository=mock_repository,
        cache=mock_cache,
        ...
    )
```

## 🎓 Mejores Prácticas Aplicadas

### 1. Test Isolation
- ✅ Cada test es independiente
- ✅ No comparten estado
- ✅ Usan fixtures para setup

### 2. Mocking
- ✅ Mocks de dependencies externas (MongoDB, Redis, RabbitMQ)
- ✅ AsyncMock para operaciones async
- ✅ No se conecta a servicios reales

### 3. Nombres Descriptivos
- ✅ `test_create_location_valid()`
- ✅ `test_transaction_above_threshold_fails()`
- ✅ `test_evaluate_high_risk_transaction()`

### 4. Test Coverage
- ✅ Happy path (casos exitosos)
- ✅ Error path (casos de error)
- ✅ Edge cases (casos límite)

### 5. Fast Tests
- ✅ Tests unitarios rápidos (<1ms cada uno)
- ✅ No I/O real (todo mockeado)
- ✅ Suite completa en <5 segundos

## 🐛 Debugging Tests

### Ver output de prints
```bash
pytest tests/unit/fraud_evaluation/ -s
```

### Parar en primer fallo
```bash
pytest tests/unit/fraud_evaluation/ -x
```

### Correr test específico
```bash
pytest tests/unit/fraud_evaluation/test_models.py::TestLocation::test_create_location_valid
```

### Modo debug con pdb
```bash
pytest tests/unit/fraud_evaluation/ --pdb
```

## 📦 Dependencias Requeridas

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.11.0"
```

## ✅ Continuous Integration

### GitHub Actions (ejemplo)
```yaml
- name: Run tests
  run: |
    pytest tests/unit/fraud_evaluation/ --cov --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## 🎯 Próximos Pasos

1. **Integration Tests**: Agregar tests con MongoDB/Redis reales
2. **E2E Tests**: Tests completos de API endpoints
3. **Performance Tests**: Medir tiempos de respuesta
4. **Load Tests**: Probar con múltiples transacciones concurrentes

## 📚 Referencias

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
- [Clean Architecture Testing](https://herbertograca.com/2017/09/28/testing-strategies/)
