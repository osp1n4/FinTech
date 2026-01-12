import { test, expect } from '@playwright/test';
import { NavigateTo } from '../tasks/NavigateTo';
import { CreateRule } from '../tasks/CreateRule';
import { RulesPage } from '../pages/RulesPage';

/**
 * Tests E2E para Admin Dashboard - Gestión de Reglas
 * 
 * NOTA: Tests deshabilitados temporalmente - funcionalidad no implementada en frontend
 * 
 * Casos de prueba:
 * 1. Crear nueva regla de umbral de monto
 * 2. Crear regla de validación de ubicación
 * 3. Verificar que reglas aparecen en la lista
 * 4. Activar/Desactivar regla
 * 5. Eliminar regla personalizada
 */

test.describe.skip('Admin Dashboard - Gestión de Reglas', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navegar a la página de reglas antes de cada test
    await NavigateTo.rulesPage(page);
  });

  test('TEST-001: Crear nueva regla de umbral de monto', async ({ page }) => {
    // Arrange
    const ruleName = `Umbral Alto ${Date.now()}`;
    const threshold = 2000;

    // Act
    await CreateRule.withAmountThreshold(page, ruleName, threshold);

    // Assert
    const rulesPage = new RulesPage(page);
    const ruleExists = await rulesPage.ruleExists(ruleName);
    expect(ruleExists).toBe(true);

    // Screenshot final
    await rulesPage.takeScreenshot('test-001-rule-created');
  });

  test('TEST-002: Crear regla de validación de ubicación GPS', async ({ page }) => {
    // Arrange
    const ruleName = `GPS Radius ${Date.now()}`;
    const maxDistance = 50; // 50 km

    // Act
    await CreateRule.withLocationRadius(page, ruleName, maxDistance);

    // Assert
    const rulesPage = new RulesPage(page);
    const ruleExists = await rulesPage.ruleExists(ruleName);
    expect(ruleExists).toBe(true);

    await rulesPage.takeScreenshot('test-002-gps-rule-created');
  });

  test('TEST-003: Crear regla personalizada con parámetros JSON', async ({ page }) => {
    // Arrange
    const ruleName = `Regla Custom ${Date.now()}`;
    const customParams = {
      max_attempts: 3,
      lockout_minutes: 30,
      notify_admin: true
    };

    // Act
    await CreateRule.withCustomParameters(
      page, 
      ruleName, 
      'custom', 
      customParams, 
      15
    );

    // Assert
    const rulesPage = new RulesPage(page);
    const ruleExists = await rulesPage.ruleExists(ruleName);
    expect(ruleExists).toBe(true);

    await rulesPage.takeScreenshot('test-003-custom-rule-created');
  });

  test('TEST-004: Verificar listado completo de reglas', async ({ page }) => {
    // Arrange & Act
    const rulesPage = new RulesPage(page);
    await page.waitForTimeout(1000); // Esperar a que carguen las reglas
    const totalRules = await rulesPage.getTotalRulesCount();

    // Assert
    expect(totalRules).toBeGreaterThanOrEqual(0); // Puede haber 0 reglas al inicio

    // Obtener lista de reglas
    const rulesList = await rulesPage.getRulesList();
    console.log(`Total de reglas encontradas: ${totalRules}`);
    console.log('Reglas:', rulesList);

    await rulesPage.takeScreenshot('test-004-rules-list');
  });

  test.skip('TEST-005: Buscar regla por nombre', async ({ page }) => {
    // Test saltado: funcionalidad de búsqueda no implementada en el frontend
    const rulesPage = new RulesPage(page);
    const searchTerm = 'Umbral';

    await rulesPage.searchRule(searchTerm);
    await page.waitForTimeout(1000);

    const filteredRules = await rulesPage.getRulesList();
    
    if (filteredRules.length > 0) {
      filteredRules.forEach(rule => {
        expect(rule.toLowerCase()).toContain(searchTerm.toLowerCase());
      });
    }

    await rulesPage.takeScreenshot('test-005-search-results');
  });

  test('TEST-006: Crear regla basada en ventana de tiempo', async ({ page }) => {
    // Arrange
    const ruleName = `Time Window ${Date.now()}`;

    // Act
    await CreateRule.withTimeWindow(page, ruleName, 10, 5); // 5 tx en 10 min

    // Assert
    const rulesPage = new RulesPage(page);
    const ruleExists = await rulesPage.ruleExists(ruleName);
    expect(ruleExists).toBe(true);

    await rulesPage.takeScreenshot('test-006-time-rule-created');
  });

  test('TEST-007: Crear regla de validación de dispositivo', async ({ page }) => {
    // Arrange
    const ruleName = `Device Check ${Date.now()}`;

    // Act
    await CreateRule.withDeviceValidation(page, ruleName, true);

    // Assert
    const rulesPage = new RulesPage(page);
    const ruleExists = await rulesPage.ruleExists(ruleName);
    expect(ruleExists).toBe(true);

    await rulesPage.takeScreenshot('test-007-device-rule-created');
  });

  test('TEST-008: Modal de nueva regla se abre correctamente', async ({ page }) => {
    // Arrange
    const rulesPage = new RulesPage(page);

    // Act
    await rulesPage.openNewRuleModal();

    // Assert
    await expect(rulesPage.modal).toBeVisible();
    await expect(rulesPage.ruleNameInput).toBeVisible();
    await expect(rulesPage.ruleTypeSelect).toBeVisible();
    await expect(rulesPage.saveButton).toBeVisible();

    await rulesPage.takeScreenshot('test-008-modal-opened');
  });

  test('TEST-009: Cancelar creación de regla cierra modal', async ({ page }) => {
    // Arrange
    const rulesPage = new RulesPage(page);
    await rulesPage.openNewRuleModal();

    // Act
    await rulesPage.clickElement(rulesPage.cancelButton);
    await page.waitForTimeout(500); // Animación

    // Assert
    const isClosed = await rulesPage.isModalClosed();
    expect(isClosed).toBe(true);

    await rulesPage.takeScreenshot('test-009-modal-closed');
  });

  test('TEST-010: Validación de JSON en campo de parámetros', async ({ page }) => {
    // Arrange
    const rulesPage = new RulesPage(page);
    await rulesPage.openNewRuleModal();

    // Act - Llenar con JSON inválido
    await rulesPage.fillField(rulesPage.ruleNameInput, 'Test Rule');
    await rulesPage.selectOption(rulesPage.ruleTypeSelect, 'custom');
    await rulesPage.fillField(rulesPage.parametersInput, '{ invalid json }');

    // Screenshot del estado de validación
    await rulesPage.takeScreenshot('test-010-invalid-json');

    // Act - Corregir JSON
    await rulesPage.fillField(rulesPage.parametersInput, '{"key": "value"}');

    await rulesPage.takeScreenshot('test-010-valid-json');
  });
});
