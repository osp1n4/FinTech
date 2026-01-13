# 🔄 Flujo de Trabajo TDD/BDD - Fraud Detection Engine

**HUMAN REVIEW (Maria Paula):**
Este diagrama muestra cómo seguimos TDD y BDD en cada historia de usuario.
No es solo teoría, es exactamente cómo trabajamos en este proyecto.

---

## 📊 Flujo Completo: De Historia de Usuario a Código en Producción

```
┌─────────────────────────────────────────────────────────────────────┐
│                    1. INICIO: HISTORIA DE USUARIO                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  HU-003: Regla de Umbral de Monto                 │
        │                                                    │
        │  Como: Sistema de detección de fraude             │
        │  Quiero: Marcar transacciones > $1,500 sospechosas│
        │  Para: Detectar transacciones inusualmente altas  │
        └───────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              2. BDD: ESCRIBIR CRITERIOS DE ACEPTACIÓN                │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  Feature: Detección por umbral de monto           │
        │                                                    │
        │  Scenario: Transacción dentro del umbral          │
        │    Given que el umbral es $1,500                  │
        │    When evalúo transacción de $500                │
        │    Then el resultado es LOW_RISK                  │
        │                                                    │
        │  Scenario: Transacción excede umbral              │
        │    Given que el umbral es $1,500                  │
        │    When evalúo transacción de $2,000              │
        │    Then el resultado es HIGH_RISK                 │
        └───────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     3. TDD FASE RED: TEST QUE FALLA                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  # tests/unit/test_fraud_strategies.py            │
        │                                                    │
        │  def test_threshold_allows_low_risk_when_below(): │
        │      strategy = AmountThresholdStrategy(1500.0)   │
        │      transaction = Transaction(amount=500.0)      │
        │                                                    │
        │      result = strategy.evaluate(transaction)      │
        │                                                    │
        │      assert result.risk_level == LOW_RISK         │
        │                                                    │
        │  ❌ ERROR: AmountThresholdStrategy not defined    │
        └───────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │   Ejecutar: pytest            │
                    │   Resultado: ❌ FAILED         │
                    └───────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  4. TDD FASE GREEN: CÓDIGO MÍNIMO                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  # services/.../amount_threshold.py               │
        │                                                    │
        │  class AmountThresholdStrategy:                   │
        │      def __init__(self, threshold: float):        │
        │          self.threshold = threshold               │
        │                                                    │
        │      def evaluate(self, transaction):             │
        │          if transaction.amount > self.threshold:  │
        │              return EvaluationResult(             │
        │                  risk_level=RiskLevel.HIGH_RISK   │
        │              )                                     │
        │          return EvaluationResult(                 │
        │              risk_level=RiskLevel.LOW_RISK        │
        │          )                                         │
        └───────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │   Ejecutar: pytest            │
                    │   Resultado: ✅ PASSED         │
                    └───────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                5. TDD FASE REFACTOR: MEJORAR CÓDIGO                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  # Mejoramos sin romper tests                     │
        │                                                    │
        │  def evaluate(self, transaction):                 │
        │      if transaction.amount > self.threshold:      │
        │          excess = transaction.amount - threshold  │
        │          return EvaluationResult(                 │
        │              risk_level=RiskLevel.HIGH_RISK,      │
        │              reasons=[                            │
        │                  f"Amount exceeds by ${excess}"   │
        │              ],                                    │
        │              risk_increment=10                    │
        │          )                                         │
        │      return EvaluationResult(                     │
        │          risk_level=RiskLevel.LOW_RISK,           │
        │          risk_increment=0                         │
        │      )                                             │
        └───────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │   Ejecutar: pytest            │
                    │   Resultado: ✅ PASSED         │
                    │   Cobertura: 100%             │
                    └───────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   6. AGREGAR MÁS TESTS (EDGE CASES)                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  def test_threshold_accepts_exact_value():        │
        │      # ❌ RED                                      │
        │      transaction = Transaction(amount=1500.0)     │
        │      assert result.risk_level == LOW_RISK         │
        │                                                    │
        │  # Ajustar código para pasar                      │
        │  if transaction.amount > self.threshold:  # OK    │
        │                                                    │
        │  ✅ GREEN - Test pasa                             │
        └───────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       7. INTEGRACIÓN CONTINUA                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────┐
        │  git commit -m "Add AmountThreshold with tests"   │
        │  git push origin main                             │
        │                                                    │
        │  GitHub Actions / Azure DevOps:                   │
        │  ├─ Run pytest                                    │
        │  ├─ Check coverage (>80%)                         │
        │  ├─ Run SonarQube                                 │
        │  └─ Deploy if all pass ✅                         │
        └───────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        8. PRODUCCIÓN ✅                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Ciclo TDD en Detalle

```
     ┌──────────────────────────────────────────────────┐
     │                                                  │
     │         🔴 RED → 🟢 GREEN → 🔵 REFACTOR          │
     │                                                  │
     └──────────────────────────────────────────────────┘
              │                │              │
              │                │              │
              ▼                ▼              ▼
     ┌────────────────┐  ┌──────────────┐  ┌────────────────┐
     │  1️⃣ WRITE TEST  │  │ 2️⃣ MAKE PASS │  │ 3️⃣ IMPROVE     │
     │   (FALLA)      │  │ (CÓDIGO MIN) │  │ (REFACTOR)     │
     └────────────────┘  └──────────────┘  └────────────────┘
              │                │              │
              └────────────────┼──────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  4️⃣ REPEAT (LOOP)    │
                    │  Siguiente test      │
                    └──────────────────────┘
```

### Ejemplo Real: Location Strategy

#### Iteración 1

```python
# 🔴 RED - Test falla
def test_transaction_within_radius_low_risk():
    # LocationStrategy no existe
    strategy = LocationStrategy(radius_km=100)
    assert strategy.evaluate(transaction).risk_level == LOW_RISK

# Resultado: ❌ NameError: LocationStrategy not defined
```

```python
# 🟢 GREEN - Código mínimo
class LocationStrategy:
    def __init__(self, radius_km):
        self.radius_km = radius_km
    
    def evaluate(self, transaction):
        return EvaluationResult(risk_level=LOW_RISK)

# Resultado: ✅ PASSED (pero incompleto)
```

```python
# 🔵 REFACTOR - Mejorar
# (Test sigue pasando, pero no agregamos funcionalidad aún)
class LocationStrategy(FraudDetectionStrategy):
    """Strategy para detectar ubicaciones inusuales."""
    
    def __init__(self, radius_km: float = 100.0):
        self.radius_km = radius_km
    
    def evaluate(self, transaction: Transaction) -> EvaluationResult:
        return EvaluationResult(risk_level=RiskLevel.LOW_RISK)

# Resultado: ✅ PASSED
```

#### Iteración 2

```python
# 🔴 RED - Test falla (agregamos comportamiento)
def test_transaction_outside_radius_high_risk():
    strategy = LocationStrategy(radius_km=100)
    # Distancia = 320 km (Bogotá → Cali)
    result = strategy.evaluate(transaction)
    assert result.risk_level == HIGH_RISK

# Resultado: ❌ Expected HIGH_RISK, got LOW_RISK
```

```python
# 🟢 GREEN - Implementar lógica de distancia
def evaluate(self, transaction: Transaction) -> EvaluationResult:
    last_location = self.get_last_location(transaction.user_id)
    
    if not last_location:
        return EvaluationResult(risk_level=RiskLevel.LOW_RISK)
    
    distance = self.calculate_haversine_distance(
        last_location, transaction.location
    )
    
    if distance > self.radius_km:
        return EvaluationResult(
            risk_level=RiskLevel.HIGH_RISK,
            reasons=[f"Distance {distance} km exceeds {self.radius_km} km"]
        )
    
    return EvaluationResult(risk_level=RiskLevel.LOW_RISK)

# Resultado: ✅ PASSED
```

```python
# 🔵 REFACTOR - Extraer método Haversine
def calculate_haversine_distance(self, loc1, loc2) -> float:
    """
    HUMAN REVIEW (Maria Paula):
    Refactorizamos para mejorar legibilidad.
    Los tests siguen pasando, pero el código es más limpio.
    """
    from math import radians, cos, sin, asin, sqrt
    
    lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
    lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return 6371 * c  # Radio de la Tierra en km

# Resultado: ✅ PASSED (ambos tests)
```

---

## 📊 Estadísticas del Proyecto

### Evolución TDD

```
Sprint 1:
├─ Tests escritos: 45
├─ Código implementado: Sí (después de tests)
├─ Tests pasando: 45/45 ✅
└─ Cobertura: 91%

Sprint 2:
├─ Tests escritos: 62 (+17)
├─ Código implementado: Sí (después de tests)
├─ Tests pasando: 107/107 ✅
└─ Cobertura: 89%

Sprint 3:
├─ Tests escritos: 55 (+55)
├─ Código implementado: Sí (después de tests)
├─ Tests pasando: 162/162 ✅
└─ Cobertura: 89%

TOTAL:
├─ Tests: 162
├─ Cobertura: 89%
├─ Bugs en producción: 0
└─ Confianza en código: Alta ✅
```

### Matriz de Tests por Tipo

```
┌─────────────────────────┬────────┬──────────┬──────────┐
│ Tipo de Test            │ Cuenta │ % Total  │ Estado   │
├─────────────────────────┼────────┼──────────┼──────────┤
│ Unit Tests              │  162   │  100%    │ ✅ PASS  │
│ Integration Tests       │   0    │    0%    │ ⏭️ TODO   │
│ End-to-End Tests        │   0    │    0%    │ ⏭️ TODO   │
├─────────────────────────┼────────┼──────────┼──────────┤
│ TOTAL                   │  162   │  100%    │ ✅ PASS  │
└─────────────────────────┴────────┴──────────┴──────────┘
```

### Tiempo de Ejecución

```
┌────────────────────────────────────────────────┐
│  Execution Time: pytest tests/unit/           │
├────────────────────────────────────────────────┤
│  test_adapters.py ................ 2.34s ✅   │
│  test_domain_models.py ........... 1.12s ✅   │
│  test_fraud_strategies.py ........ 0.89s ✅   │
│  test_location_edge_cases.py ..... 3.21s ✅   │
│  test_location_strategy.py ....... 2.45s ✅   │
│  test_rapid_transaction.py ....... 1.78s ✅   │
│  test_routes.py .................. 2.67s ✅   │
│  test_unusual_time_strategy.py ... 1.34s ✅   │
│  test_use_cases.py ............... 1.56s ✅   │
│  test_worker.py .................. 3.89s ✅   │
├────────────────────────────────────────────────┤
│  TOTAL: 162 passed in 21.25s                  │
└────────────────────────────────────────────────┘
```

---

## 🎓 Lecciones Aprendidas

### ✅ Lo que funcionó bien

1. **Escribir tests primero nos salvó de bugs**
   - Detectamos edge cases antes de implementar
   - Ejemplo: Coordenadas en polo norte, cruce de meridiano 180°

2. **Gherkin mejoró comunicación con stakeholders**
   - Criterios de aceptación claros
   - No hubo ambigüedades en requisitos

3. **Refactoring sin miedo**
   - Mejoramos estructura 3 veces
   - Los tests garantizaron que nada se rompiera

4. **Documentación siempre actualizada**
   - Los tests SON la documentación
   - No hay docs obsoletos

### ⚠️ Desafíos enfrentados

1. **Curva de aprendizaje inicial**
   - Solución: Pair programming en primeras HU

2. **Tests tardaban en ejecutarse**
   - Solución: Mocking de dependencias externas

3. **Escribir tests requiere tiempo**
   - Pero: Ahorramos 10x ese tiempo en debugging

---

## 📚 Recursos de Referencia

### Libros que inspiraron nuestro enfoque

- **"Test Driven Development: By Example"** - Kent Beck
- **"Clean Architecture"** - Robert C. Martin
- **"BDD in Action"** - John Ferguson Smart
- **"Growing Object-Oriented Software, Guided by Tests"** - Freeman & Pryce

### Artículos útiles

- [The Three Laws of TDD](http://butunclebob.com/ArticleS.UncleBob.TheThreeRulesOfTdd)
- [Given-When-Then](https://martinfowler.com/bliki/GivenWhenThen.html)
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**Documento creado:** Enero 12, 2026  
**Última actualización:** Enero 12, 2026  
**Versión:** 1.0  
**Responsable:** Maria Paula Gutierrez

---

> **"Code without tests is broken by design."**  
> — Jacob Kaplan-Moss (Django creator)

> **"If you're not doing TDD, you're doing legacy code."**  
> — Michael Feathers
