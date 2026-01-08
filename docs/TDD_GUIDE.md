# Guía TDD/BDD para Fraud Detection Engine

**HUMAN REVIEW (Maria Paula Gutierrez):**  
Esta guía explica cómo seguir Test-Driven Development (TDD) en el proyecto para cumplir con el requisito de "TDD/BDD Real" donde los tests se crean ANTES que el código de producción.

---

## 📋 ¿Qué es TDD/BDD Real?

**TDD Real** significa que:
1. ✅ Los tests se escriben PRIMERO
2. ✅ El código de producción se escribe DESPUÉS
3. ✅ Esto se evidencia en el historial de Git

**NO es TDD Real:**
- ❌ Escribir código primero y luego agregar tests
- ❌ Tests que solo verifican implementación existente
- ❌ Tests escritos después del deployment

---

## 🔄 Ciclo TDD (Red-Green-Refactor)

### 1. **RED** - Escribe un test que falla
```python
# tests/unit/test_new_feature.py
def test_nueva_funcionalidad():
    """Test: La nueva funcionalidad debe hacer X."""
    # Arrange
    input_data = {...}
    
    # Act
    result = nueva_funcionalidad(input_data)
    
    # Assert
    assert result == expected_value
```

Ejecuta: `pytest tests/unit/test_new_feature.py`  
**Resultado esperado:** ❌ FALLA (porque la función aún no existe)

### 2. **GREEN** - Escribe código mínimo para pasar
```python
# services/shared/domain/nueva_funcionalidad.py
def nueva_funcionalidad(input_data):
    """Implementación mínima para pasar el test."""
    return expected_value  # Implementación simple
```

Ejecuta: `pytest tests/unit/test_new_feature.py`  
**Resultado esperado:** ✅ PASA

### 3. **REFACTOR** - Mejora el código sin romper tests
```python
# services/shared/domain/nueva_funcionalidad.py
def nueva_funcionalidad(input_data):
    """Implementación refactorizada y optimizada."""
    # Lógica más robusta y limpia
    result = procesar_con_validacion(input_data)
    return result
```

Ejecuta: `pytest tests/unit/test_new_feature.py`  
**Resultado esperado:** ✅ PASA (mismo comportamiento, mejor código)

---

## 📝 Flujo de Trabajo con Git

### Paso 1: Crear branch para la feature
```bash
git checkout -b feature/nueva-regla-fraude
```

### Paso 2: Escribir los tests PRIMERO
```bash
# Crear archivo de test
code tests/unit/test_nueva_regla.py

# Escribir tests que fallen
# Commit de tests
git add tests/unit/test_nueva_regla.py
git commit -m "test: Add tests for nueva regla de fraude (RED)"
```

### Paso 3: Implementar código para pasar tests
```bash
# Crear código de producción
code services/shared/domain/strategies/nueva_regla.py

# Commit de implementación
git add services/shared/domain/strategies/nueva_regla.py
git commit -m "feat: Implement nueva regla de fraude (GREEN)"
```

### Paso 4: Refactorizar si es necesario
```bash
# Mejorar código
code services/shared/domain/strategies/nueva_regla.py

# Commit de refactor
git add services/shared/domain/strategies/nueva_regla.py
git commit -m "refactor: Optimize nueva regla implementation"
```

### Paso 5: Push y merge
```bash
git push origin feature/nueva-regla-fraude
# Crear Pull Request en GitHub
```

---

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Nueva estrategia de fraude

#### Test primero (RED):
```python
# tests/unit/test_velocity_strategy.py
def test_velocity_strategy_detects_multiple_transactions():
    """Test: Debe detectar múltiples transacciones en poco tiempo."""
    # Arrange
    strategy = VelocityStrategy(max_transactions=3, window_minutes=10)
    transactions = [
        create_transaction(timestamp="10:00"),
        create_transaction(timestamp="10:02"),
        create_transaction(timestamp="10:05"),
        create_transaction(timestamp="10:07"),  # 4ta en 10 min
    ]
    
    # Act
    result = strategy.evaluate(transactions[-1], transactions[:-1])
    
    # Assert
    assert result["risk_level"] == RiskLevel.HIGH_RISK
    assert "velocity_exceeded" in result["reasons"]

# Commit: "test: Add velocity strategy tests (RED)"
```

#### Código después (GREEN):
```python
# services/shared/domain/strategies/velocity.py
class VelocityStrategy(FraudStrategy):
    def __init__(self, max_transactions: int, window_minutes: int):
        self.max_transactions = max_transactions
        self.window_minutes = window_minutes
    
    def evaluate(self, transaction, historical):
        # Implementación...
        pass

# Commit: "feat: Implement velocity strategy (GREEN)"
```

### Ejemplo 2: Nuevo endpoint API

#### Test primero (RED):
```python
# tests/integration/test_admin_endpoints.py
def test_bulk_approve_transactions(client):
    """Test: Debe aprobar múltiples transacciones a la vez."""
    # Arrange
    transaction_ids = ["txn_001", "txn_002", "txn_003"]
    
    # Act
    response = client.post(
        "/api/v1/admin/transactions/bulk-approve",
        json={"transaction_ids": transaction_ids}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["approved_count"] == 3

# Commit: "test: Add bulk approve endpoint test (RED)"
```

#### Código después (GREEN):
```python
# services/api-gateway/src/routes.py
@router.post("/admin/transactions/bulk-approve")
async def bulk_approve_transactions(request: BulkApproveRequest):
    """Aprueba múltiples transacciones."""
    # Implementación...
    return {"approved_count": len(request.transaction_ids)}

# Commit: "feat: Add bulk approve endpoint (GREEN)"
```

---

## 🚀 Comandos Útiles

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar solo tests unitarios
```bash
pytest tests/unit/ -m unit
```

### Ejecutar solo tests de integración
```bash
pytest tests/integration/ -m integration
```

### Ver coverage
```bash
pytest --cov=services --cov-report=html
# Abrir htmlcov/index.html en el navegador
```

### Ejecutar tests en modo watch (re-ejecuta al cambiar código)
```bash
pytest-watch
```

---

## ✅ Checklist para TDD

Antes de hacer commit de una nueva feature:

- [ ] Tests escritos PRIMERO y commitados
- [ ] Tests fallan inicialmente (RED)
- [ ] Código implementado para pasar tests (GREEN)
- [ ] Tests pasan exitosamente
- [ ] Código refactorizado si es necesario
- [ ] Coverage >= 70%
- [ ] Historial de Git muestra orden correcto (test → código)

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [TDD by Example - Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [Clean Architecture - Robert C. Martin](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)

---

## 🤝 Contribuir

Si agregas una nueva feature:
1. Crea tests primero en `tests/unit/` o `tests/integration/`
2. Commit con mensaje: `test: Add tests for [feature] (RED)`
3. Implementa código mínimo
4. Commit con mensaje: `feat: Implement [feature] (GREEN)`
5. Refactoriza si es necesario
6. Commit con mensaje: `refactor: Improve [feature]`

**Recuerda:** El historial de Git debe mostrar que los tests se crearon ANTES que el código.
