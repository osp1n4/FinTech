# 📚 Índice Maestro de Documentación TDD/BDD

**Fraud Detection Engine - Documentación Completa**

---

## 🎯 Inicio Rápido

Si eres nuevo en el proyecto o quieres verificar rápidamente el cumplimiento TDD/BDD, comienza aquí:

### ⚡ Para Stakeholders / Management

1. 📊 **[RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md)** ⭐ **COMIENZA AQUÍ**
   - Respuesta rápida: ¿Cumple el proyecto con TDD/BDD?
   - Métricas clave y evidencia
   - 5 minutos de lectura

### 👨‍💻 Para Desarrolladores

1. 🔄 **[FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md)** ⭐ **COMIENZA AQUÍ**
   - Cómo seguimos TDD/BDD en el día a día
   - Ejemplos reales con código
   - Diagramas de flujo
   - 10 minutos de lectura

### 🧪 Para QA / Testers

1. 🧪 **[TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md)** ⭐ **COMIENZA AQUÍ**
   - Estrategia de testing completa
   - Matriz de trazabilidad
   - 162 tests documentados
   - 15 minutos de lectura

---

## 📖 Documentación por Rol

### 👔 Product Owner / Analista de Negocio

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md) | Historias con criterios Gherkin | 20 min |
| [TEST_CASES_GHERKIN.md](./TEST_CASES_GHERKIN.md) | Casos de prueba en lenguaje natural | 15 min |
| [RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md) | Evidencia de cumplimiento | 5 min |

**Total:** 40 minutos

### 👨‍💻 Desarrollador Backend

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md) | Proceso de desarrollo | 10 min |
| [CUMPLIMIENTO_TDD_BDD.md](./CUMPLIMIENTO_TDD_BDD.md) | Evidencia técnica detallada | 20 min |
| [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md) | Estrategia de tests | 15 min |
| [../tests/unit/](../tests/unit/) | Tests implementados | Variable |

**Total:** 45 minutos + práctica

### 🧪 QA Engineer / Tester

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md) | Plan maestro de testing | 15 min |
| [TEST_CASES_GHERKIN.md](./TEST_CASES_GHERKIN.md) | Casos de prueba detallados | 15 min |
| [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md) | Criterios de aceptación | 20 min |
| [htmlcov/index.html](../htmlcov/index.html) | Reporte de cobertura | 5 min |

**Total:** 55 minutos

### 🏗️ Arquitecto de Software

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [ARQUITECTURE.md](./ARQUITECTURE.md) | Arquitectura Clean | 15 min |
| [CUMPLIMIENTO_TDD_BDD.md](./CUMPLIMIENTO_TDD_BDD.md) | Cómo TDD afecta diseño | 20 min |
| [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md) | Ciclo de desarrollo | 10 min |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | Estructura de capas | 10 min |

**Total:** 55 minutos

### 📊 Auditor / Compliance

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md) | Evidencia de cumplimiento | 5 min |
| [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md) | Trazabilidad HU → Tests | 15 min |
| [coverage.xml](../coverage.xml) | Cobertura en formato XML | 2 min |
| [sonar-project.properties](../sonar-project.properties) | Configuración SonarQube | 2 min |

**Total:** 24 minutos

---

## 📚 Documentación Completa (Orden Sugerido)

### Nivel 1: Fundamentos (OBLIGATORIO)

1. **[RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md)** - 5 min
   - ✅ Respuesta rápida al cumplimiento
   - ✅ Métricas clave
   - ✅ Evidencia resumida

2. **[HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md)** - 20 min
   - ✅ 9 historias con formato INVEST
   - ✅ Criterios de aceptación en Gherkin
   - ✅ Casos de prueba positivos/negativos

3. **[TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md)** - 15 min
   - ✅ Estrategia de testing
   - ✅ Matriz de trazabilidad
   - ✅ 162 tests documentados

### Nivel 2: Profundización (RECOMENDADO)

4. **[FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md)** - 10 min
   - ✅ Diagramas de flujo
   - ✅ Proceso Red-Green-Refactor
   - ✅ Ejemplos reales

5. **[CUMPLIMIENTO_TDD_BDD.md](./CUMPLIMIENTO_TDD_BDD.md)** - 20 min
   - ✅ Evidencia técnica detallada
   - ✅ Comparaciones antes/después TDD
   - ✅ Checklist de verificación

6. **[TEST_CASES_GHERKIN.md](./TEST_CASES_GHERKIN.md)** - 15 min
   - ✅ Todos los casos en Gherkin
   - ✅ Datos de entrada/salida
   - ✅ Resultados esperados

### Nivel 3: Arquitectura y Contexto (OPCIONAL)

7. **[ARQUITECTURE.md](./ARQUITECTURE.md)** - 15 min
   - Arquitectura Clean
   - Capas: Domain, Application, Infrastructure

8. **[CONTEXTO_NEGOCIO.md](./CONTEXTO_NEGOCIO.md)** - 10 min
   - Contexto del problema
   - Justificación del proyecto

9. **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - 10 min
   - Estructura de carpetas
   - Organización del código

10. **[TECH_STACK.md](./TECH_STACK.md)** - 8 min
    - Python 3.11, FastAPI
    - MongoDB, Redis, RabbitMQ
    - pytest, Docker

---

## 🔍 Búsqueda por Tema

### TDD (Test-Driven Development)

- [CUMPLIMIENTO_TDD_BDD.md](./CUMPLIMIENTO_TDD_BDD.md) - Evidencia de TDD
- [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md) - Ciclo Red-Green-Refactor
- [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md) - Estrategia de tests

### BDD (Behavior-Driven Development)

- [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md) - Historias con Gherkin
- [TEST_CASES_GHERKIN.md](./TEST_CASES_GHERKIN.md) - Casos en Given-When-Then
- [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md) - Integración BDD con tests

### Tests y Cobertura

- [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md) - Plan maestro
- [../tests/unit/](../tests/unit/) - Tests implementados (162)
- [../htmlcov/index.html](../htmlcov/index.html) - Reporte HTML de cobertura
- [../coverage.xml](../coverage.xml) - Cobertura XML para CI/CD

### Historias de Usuario

- [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md) - Detalladas con Gherkin
- [HISTORIAS_USUARIO.md](./HISTORIAS_USUARIO.md) - Versión original
- [TEST_CASES_GHERKIN.md](./TEST_CASES_GHERKIN.md) - Casos de cada HU

### Arquitectura

- [ARQUITECTURE.md](./ARQUITECTURE.md) - Clean Architecture
- [MICROSERVICES_ARCHITECTURE.md](./MICROSERVICES_ARCHITECTURE.md) - Arquitectura de servicios
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Estructura del proyecto

---

## 📊 Estadísticas del Proyecto

### Tests

```
Total Tests:          162
├─ Unit Tests:        162 ✅
├─ Integration:         0 ⏭️
└─ E2E:                 0 ⏭️

Estado:               100% pasando
Cobertura:            89%
Tiempo ejecución:     21.25s
```

### Documentación

```
Total Documentos:     19
├─ TDD/BDD:            6 ✅ (NUEVO)
├─ Arquitectura:       5
├─ Negocio:            4
├─ Técnicos:           4

Total Páginas:        ~180
Total Palabras:       ~45,000
```

### Historias de Usuario

```
Total HU:             9
├─ Implementadas:     9 ✅
├─ Con Gherkin:       9 ✅
├─ Con Tests:         9 ✅

Scenarios Gherkin:    20
Tests:                162 (8-16 tests/HU)
```

---

## 🎯 Mapas de Lectura Rápida

### 📖 "Quiero entender TDD/BDD en 15 minutos"

1. [RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md) (5 min)
2. [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md) - Solo "Ciclo TDD en Detalle" (5 min)
3. Ver un test real: [tests/unit/test_fraud_strategies.py](../tests/unit/test_fraud_strategies.py) (5 min)

**Total:** 15 minutos ⏱️

### 📖 "Quiero verificar cumplimiento completo" (Auditor)

1. [RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md) (5 min)
2. [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md) - Matriz de trazabilidad (10 min)
3. Ejecutar: `pytest --cov` (2 min)
4. Abrir: [htmlcov/index.html](../htmlcov/index.html) (3 min)

**Total:** 20 minutos ⏱️

### 📖 "Quiero implementar una nueva funcionalidad" (Dev)

1. [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md) (10 min)
2. [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md) - Ver ejemplo HU-003 (5 min)
3. Ver test real correspondiente: [tests/unit/test_fraud_strategies.py](../tests/unit/test_fraud_strategies.py) (5 min)
4. Seguir ciclo Red-Green-Refactor

**Total:** 20 minutos + implementación ⏱️

### 📖 "Quiero escribir una nueva HU" (PO/Analista)

1. [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md) - Ver formato (10 min)
2. [TEST_CASES_GHERKIN.md](./TEST_CASES_GHERKIN.md) - Ver ejemplos Gherkin (10 min)
3. Usar plantilla de HU existente
4. Validar con equipo de desarrollo

**Total:** 20 minutos + escritura ⏱️

---

## 🔗 Enlaces Externos Útiles

### Teoría TDD/BDD

- [Test Driven Development by Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Given When Then by Martin Fowler](https://martinfowler.com/bliki/GivenWhenThen.html)
- [The Three Laws of TDD by Uncle Bob](http://butunclebob.com/ArticleS.UncleBob.TheThreeRulesOfTdd)

### Herramientas

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/reference/)

---

## 📞 Soporte

### ¿Tienes preguntas?

- **Sobre TDD/BDD:** Revisar [CUMPLIMIENTO_TDD_BDD.md](./CUMPLIMIENTO_TDD_BDD.md)
- **Sobre tests específicos:** Revisar [TEST_PLAN_COMPLETO.md](./TEST_PLAN_COMPLETO.md)
- **Sobre una HU:** Revisar [HISTORIAS_USUARIO_DETALLADAS.md](./HISTORIAS_USUARIO_DETALLADAS.md)

### ¿Quieres contribuir?

1. Lee [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md)
2. Sigue el ciclo Red-Green-Refactor
3. Asegura cobertura >80%
4. Documenta en Gherkin

---

## ✅ Checklist para Nuevos Desarrolladores

- [ ] Leer [RESUMEN_EJECUTIVO_TDD_BDD.md](./RESUMEN_EJECUTIVO_TDD_BDD.md)
- [ ] Leer [FLUJO_TDD_BDD.md](./FLUJO_TDD_BDD.md)
- [ ] Ejecutar tests: `pytest tests/unit/ -v`
- [ ] Ver cobertura: `pytest --cov --cov-report=html`
- [ ] Revisar un test: `tests/unit/test_fraud_strategies.py`
- [ ] Revisar código: `services/fraud-evaluation-service/src/`
- [ ] Entender arquitectura: [ARQUITECTURE.md](./ARQUITECTURE.md)
- [ ] Hacer pair programming con equipo
- [ ] Implementar primera HU siguiendo TDD

---

## 📅 Mantenimiento del Índice

**Última actualización:** Enero 12, 2026  
**Versión:** 1.0  
**Responsable:** Maria Paula Gutierrez

**Actualizar cuando:**
- Se agreguen nuevas HU
- Se creen nuevos documentos
- Se modifiquen tests significativamente
- Se cambien enlaces o estructura

---

## 🏆 Resumen

### ✅ 6 Documentos TDD/BDD Creados

1. ✅ RESUMEN_EJECUTIVO_TDD_BDD.md (48 KB)
2. ✅ HISTORIAS_USUARIO_DETALLADAS.md (64 KB)
3. ✅ TEST_PLAN_COMPLETO.md (58 KB)
4. ✅ CUMPLIMIENTO_TDD_BDD.md (48 KB)
5. ✅ FLUJO_TDD_BDD.md (52 KB)
6. ✅ INDICE_MAESTRO_TDD_BDD.md (este archivo)

### ✅ Evidencia Completa

- 162 tests implementados
- 9 historias con Gherkin
- 89% cobertura de código
- 100% tests pasando
- Documentación completa y actualizada

---

**¡Comienza tu lectura con el documento recomendado para tu rol! 🚀**
