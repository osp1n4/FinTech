# Playwright E2E Tests - Fraud Detection Engine

Pruebas End-to-End automatizadas con **Playwright** que cubren **las 14 historias de usuario** documentadas en [TEST_CASES.md](../docs/TEST_CASES.md).

---

## 📊 Cobertura de Tests E2E

| Archivo | HU Cubiertas | Test Cases | Descripción |
|---------|--------------|------------|-------------|
| `hu-001-reception.spec.ts` | HU-001 | 3 | Recepción de transacciones por API |
| `hu-002-audit.spec.ts` | HU-002 | 2 | Auditoría inmutable de evaluaciones |
| `hu-003-007-fraud-strategies.spec.ts` | HU-003 a HU-007 | 10 | Estrategias de detección de fraude |
| `hu-008-009-config.spec.ts` | HU-008, HU-009 | 4 | Configuración dinámica |
| `hu-012-manual-review.spec.ts` | HU-012 | 4 | Revisión manual por analista |
| `hu-013-user-dashboard.spec.ts` | HU-013 | 4 | Dashboard usuario |
| `hu-014-admin-metrics.spec.ts` | HU-014 | 5 | Dashboard admin y métricas |
| `admin-dashboard.spec.ts` | HU-011 | 5 | Gestión de reglas personalizadas |
| `user-app.spec.ts` | HU-013 | 6 | App de usuario (legacy) |
| `api-integration.spec.ts` | HU-001 | 5 | Integración API (legacy) |
| **TOTAL** | **14 HU** | **48** | **Cobertura completa** |

---

## 📁 Estructura del Proyecto

```
tests-e2e/
├── playwright.config.ts          # Configuración de Playwright
├── package.json                  # Dependencias npm
├── tsconfig.json                 # Configuración TypeScript
├── pages/                        # Page Object Model
│   ├── BasePage.ts              # Clase base con funcionalidad común
│   ├── RulesPage.ts             # Página de gestión de reglas (Admin)
│   ├── TransactionsPage.ts      # Página de transacciones (Admin)
│   └── UserDashboardPage.ts     # Dashboard de usuario
├── tasks/                        # Screenplay Pattern
│   ├── NavigateTo.ts            # Tareas de navegación
│   ├── CreateRule.ts            # Tareas de creación de reglas
│   ├── ReviewTransaction.ts     # Tareas de revisión manual
│   └── ValidateTransaction.ts   # Tareas de validación de transacciones
├── tests/                        # Test specs (NUEVOS tests basados en TEST_CASES.md)
│   ├── hu-001-reception.spec.ts        # HU-001: Recepción API ✅ NUEVO
│   ├── hu-002-audit.spec.ts            # HU-002: Auditoría ✅ NUEVO
│   ├── hu-003-007-fraud-strategies.spec.ts # HU-003 a HU-007: Estrategias ✅ NUEVO
│   ├── hu-008-009-config.spec.ts       # HU-008, HU-009: Config ✅ NUEVO
│   ├── hu-012-manual-review.spec.ts    # HU-012: Revisión manual ✅ NUEVO
│   ├── hu-013-user-dashboard.spec.ts   # HU-013: Dashboard usuario ✅ NUEVO
│   ├── hu-014-admin-metrics.spec.ts    # HU-014: Métricas admin ✅ NUEVO
│   ├── admin-dashboard.spec.ts  # Tests de dashboard admin (reglas) - HU-011
│   ├── transactions.spec.ts     # Tests de transacciones (admin)
│   ├── user-app.spec.ts         # Tests de app usuario - HU-013
│   └── api-integration.spec.ts  # Tests de integración API - HU-001
├── fixtures/                     # Datos de prueba
│   ├── transactions.json        # Transacciones de ejemplo
│   └── rules.json               # Reglas de ejemplo
├── screenshots/                  # Capturas automáticas
├── videos/                       # Videos de ejecución
└── test-results/                 # Reportes HTML
```

## 🚀 Instalación

### 1. Instalar dependencias

```powershell
cd tests-e2e
npm install
```

### 2. Instalar navegadores de Playwright

```powershell
npx playwright install
```

### 3. Verificar instalación

```powershell
npx playwright --version
```

## ▶️ Ejecución de Tests

### Ejecutar todos los tests

```powershell
npm test
```

### Ejecutar en modo UI interactivo (RECOMENDADO)

```powershell
npm run test:ui
```

Esta es la forma más visual y útil para desarrollo. Abre una interfaz gráfica donde puedes:
- Ver tests ejecutándose en tiempo real
- Pausar y reanudar ejecución
- Inspeccionar elementos
- Ver timeline de acciones

### Ejecutar tests con navegador visible

```powershell
npm run test:headed
```

### Ejecutar tests en modo debug

```powershell
npm run test:debug
```

### Ejecutar tests por archivo

```powershell
# Solo tests de admin dashboard
npm run test:admin

# Solo tests de usuario
npm run test:user

# Solo tests de API
npm run test:api
```

### Ejecutar en navegador específico

```powershell
# Chromium
npm run test:chromium

# Firefox
npm run test:firefox

# WebKit (Safari)
npm run test:webkit
```

### Ejecutar test específico

```powershell
# Por nombre de test
npx playwright test --grep "TEST-001"

# Por archivo específico
npx playwright test tests/admin-dashboard.spec.ts
```

## 📊 Ver Reportes

### HTML Reporter (Interfaz Dinámica)

```powershell
npm run test:report
```

Esto abre un navegador con:
- ✅ Lista de todos los tests ejecutados
- 📊 Estadísticas (pass/fail/skip)
- 🖼️ Screenshots incrustados
- 🎥 Videos de ejecución
- ⏱️ Tiempos de ejecución
- 🔍 Filtros por estado

### Trace Viewer (Timeline Interactivo)

```powershell
npx playwright show-trace test-results/traces/trace.zip
```

Permite:
- Ver timeline completo de la ejecución
- Inspeccionar cada acción paso a paso
- Ver DOM snapshots en cada momento
- Revisar network requests
- Ver console logs

## 📸 Screenshots y Videos

### Screenshots

Los screenshots se toman automáticamente:
- ✅ En cada paso importante (configurado en los tests)
- ❌ Automáticamente cuando un test falla
- 📁 Guardados en `screenshots/`

Para capturar screenshot manual:

```typescript
await page.screenshot({ path: 'screenshots/my-screenshot.png' });
```

### Videos

Los videos se graban automáticamente:
- 🎥 Solo cuando el test falla (configuración actual)
- 📁 Guardados en `test-results/videos/`

Para cambiar configuración (grabar siempre):

```typescript
// En playwright.config.ts
use: {
  video: 'on' // o 'retain-on-failure'
}
```

## 🧪 Casos de Prueba Implementados

### Admin Dashboard - Reglas (10 tests)

- ✅ **TEST-001**: Crear regla de umbral de monto
- ✅ **TEST-002**: Crear regla de validación GPS
- ✅ **TEST-003**: Crear regla personalizada con JSON
- ✅ **TEST-004**: Verificar listado de reglas
- ✅ **TEST-005**: Buscar regla por nombre
- ✅ **TEST-006**: Crear regla de ventana de tiempo
- ✅ **TEST-007**: Crear regla de validación de dispositivo
- ✅ **TEST-008**: Abrir modal de nueva regla
- ✅ **TEST-009**: Cancelar creación de regla
- ✅ **TEST-010**: Validación de JSON en parámetros

### Admin Dashboard - Transacciones (10 tests)

- ✅ **TEST-011**: Ver listado de transacciones
- ✅ **TEST-012**: Filtrar por estado PENDING
- ✅ **TEST-013**: Filtrar por estado APPROVED
- ✅ **TEST-014**: Filtrar por estado REJECTED
- ✅ **TEST-015**: Ver detalles de transacción
- ✅ **TEST-016**: Buscar transacción por ID
- ✅ **TEST-017**: Actualizar listado
- ✅ **TEST-018**: Verificar paginación
- ✅ **TEST-019**: Aprobar transacción pendiente
- ✅ **TEST-020**: Contar transacciones por estado

### User App (10 tests)

- ✅ **TEST-021**: Ver página principal
- ✅ **TEST-022**: Ver historial completo
- ✅ **TEST-023**: Verificar información de transacciones
- ✅ **TEST-024**: Contar transacciones aprobadas
- ✅ **TEST-025**: Contar transacciones rechazadas
- ✅ **TEST-026**: Contar transacciones pendientes
- ✅ **TEST-027**: Filtrar por rango de fechas
- ✅ **TEST-028**: Limpiar filtros
- ✅ **TEST-029**: Verificar lista vacía
- ✅ **TEST-030**: Resumen por estado

### API Integration (12 tests)

- ✅ **TEST-031**: Transacción de bajo riesgo
- ✅ **TEST-032**: Transacción de alto monto
- ✅ **TEST-033**: Ubicación sospechosa
- ✅ **TEST-034**: Dispositivo desconocido
- ✅ **TEST-035**: Alto riesgo múltiple
- ✅ **TEST-036**: Verificar estado
- ✅ **TEST-037**: Múltiples transacciones
- ✅ **TEST-038**: Helper lowRisk
- ✅ **TEST-039**: Helper highRiskAmount
- ✅ **TEST-040**: Helper suspiciousLocation
- ✅ **TEST-041**: Helper unknownDevice
- ✅ **TEST-042**: Verificar formato de respuesta

**Total: 42 tests E2E** ✅

## 🎯 Patrones Implementados

### Page Object Model (POM)

Cada página tiene su propia clase que encapsula:
- Locators (selectores de elementos)
- Métodos de interacción
- Lógica específica de la página

```typescript
const rulesPage = new RulesPage(page);
await rulesPage.navigate();
await rulesPage.createRule({ ... });
```

### Screenplay Pattern

Tareas de alto nivel que representan acciones del usuario:

```typescript
await CreateRule.withAmountThreshold(page, 'My Rule', 1500);
await ReviewTransaction.approve(page, 'tx-123', 'Justification');
await ValidateTransaction.lowRisk(request, 'user-001');
```

### BasePage

Funcionalidad común heredada por todos los Page Objects:
- Navegación
- Esperas inteligentes
- Screenshots
- Manejo de toasts/notificaciones
- Utilidades de interacción

## 🔧 Configuración

### playwright.config.ts

Configuración principal:
- **Timeout**: 30s por test, 5s para assertions
- **Retries**: 2 en CI, 0 en local
- **Workers**: Paralelo en local, secuencial en CI
- **Screenshots**: Solo en fallos (configurable)
- **Videos**: Solo en fallos (configurable)
- **Trace**: En primer reintento

### Navegadores configurados

- ✅ Chromium (Chrome/Edge)
- ✅ Firefox
- ✅ WebKit (Safari)

## 📝 Buenas Prácticas Implementadas

1. **Auto-wait**: Playwright espera automáticamente a que elementos estén disponibles
2. **Screenshots contextuales**: Capturas en momentos clave
3. **Tests independientes**: Cada test puede ejecutarse solo
4. **Fixtures reutilizables**: Datos de prueba centralizados
5. **Patrón AAA**: Arrange-Act-Assert en todos los tests
6. **Descripción clara**: Nombres descriptivos para tests y métodos
7. **Console logs**: Información útil en la salida de tests

## 🚨 Prerequisitos

Antes de ejecutar los tests, asegúrate de que:

1. **Backend** esté corriendo en `http://localhost:8000`
2. **Admin Dashboard** esté corriendo en `http://localhost:3001`
3. **User App** esté corriendo en `http://localhost:5173`

### Iniciar servicios

```powershell
# Backend (en terminal 1)
cd services/api-gateway
poetry run uvicorn src.main:app --reload

# Admin Dashboard (en terminal 2)
cd frontend/admin-dashboard
npm run dev

# User App (en terminal 3)
cd frontend/user-app
npm run dev
```

## 🐛 Debugging

### Modo UI Interactivo

```powershell
npx playwright test --ui
```

### Modo Debug con DevTools

```powershell
npx playwright test --debug
```

### Ver screenshots de un test

```powershell
# Los screenshots están en:
test-results/[test-name]/screenshots/
```

### Ver video de un test fallido

```powershell
# Los videos están en:
test-results/[test-name]/video.webm
```

## 🔄 Integración CI/CD

Para agregar a GitHub Actions, crear `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd tests-e2e
          npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Start services
        run: |
          # Iniciar backend, frontends, etc.
      
      - name: Run E2E tests
        run: npm test
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: test-results/
```

## 📚 Documentación Adicional

- [Playwright Documentation](https://playwright.dev)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Screenplay Pattern](https://serenity-js.org/handbook/design/screenplay-pattern/)

## 💡 Tips

- Usa `test.only()` para ejecutar un solo test durante desarrollo
- Usa `test.skip()` para saltar tests temporalmente
- Revisa el HTML Reporter después de cada ejecución
- Usa el Trace Viewer para debuggear tests complejos
- Ejecuta en modo headed (`--headed`) para ver qué está pasando

## 🎉 ¡Listo!

Ahora tienes una suite completa de tests E2E con:
- ✅ 42 tests automatizados
- ✅ Screenshots automáticos
- ✅ Videos de ejecución
- ✅ HTML Reporter interactivo
- ✅ Trace Viewer con timeline
- ✅ Patrón Page Object Model
- ✅ Patrón Screenplay
- ✅ Multi-browser support
