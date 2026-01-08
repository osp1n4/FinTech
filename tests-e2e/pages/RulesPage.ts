import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * RulesPage - Page Object para la página de gestión de reglas
 * URL: http://localhost:3001/rules
 * 
 * Funcionalidades:
 * - Listar reglas existentes
 * - Crear nueva regla
 * - Editar regla
 * - Activar/Desactivar regla
 * - Eliminar regla
 */
export class RulesPage extends BasePage {
  // Locators principales
  readonly newRuleButton: Locator;
  readonly rulesTable: Locator;
  readonly searchInput: Locator;
  readonly filterSelect: Locator;

  // Modal de creación/edición
  readonly modal: Locator;
  readonly ruleNameInput: Locator;
  readonly ruleTypeSelect: Locator;
  readonly parametersInput: Locator;
  readonly priorityInput: Locator;
  readonly enabledCheckbox: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  // Mensajes
  readonly successToast: Locator;
  readonly errorToast: Locator;

  constructor(page: Page) {
    super(page);
    
    // Botones de acción - basado en el código real del frontend
    this.newRuleButton = page.getByText('Nueva Regla');
    this.rulesTable = page.locator('.grid.grid-cols-1.lg\\:grid-cols-2.gap-6').first(); // El contenedor de las reglas
    this.searchInput = page.getByPlaceholder(/buscar|search/i);
    this.filterSelect = page.locator('select[name="filter"], [data-testid="filter-select"]');

    // Modal - cuando está visible
    this.modal = page.locator('div.fixed.inset-0').filter({ has: page.locator('h2:has-text("Crear Nueva Regla"), h2:has-text("Editar Regla")') }).first();
    
    // Campos del formulario - usando placeholder y labels específicos
    this.ruleNameInput = page.getByPlaceholder('Ej: Regla de horario nocturno');
    this.ruleTypeSelect = page.locator('select').first();
    this.parametersInput = page.locator('textarea').first();
    this.priorityInput = page.locator('label:has-text("Prioridad")').locator('..').locator('input[type="number"]');
    this.enabledCheckbox = page.locator('input[type="checkbox"]#enabled');
    this.saveButton = page.getByText('Crear Regla');
    this.cancelButton = page.getByText('Cancelar').first();

    // Toast messages
    this.successToast = page.locator('[role="status"]').filter({ hasText: /éxito|success/i });
    this.errorToast = page.locator('[role="status"]').filter({ hasText: /error/i });
  }

  /**
   * Navegar a la página de reglas
   */
  async navigate(): Promise<void> {
    await this.goto('http://localhost:3001/rules');
    await this.waitForLoadingComplete();
  }

  /**
   * Abrir modal de nueva regla
   */
  async openNewRuleModal(): Promise<void> {
    await this.clickElement(this.newRuleButton);
    await this.waitForElement(this.modal);
    await this.takeScreenshot('rules-modal-opened');
  }

  /**
   * Crear una nueva regla
   */
  async createRule(ruleData: {
    name: string;
    type: string;
    parameters: string;
    priority: number;
    enabled?: boolean;
  }): Promise<void> {
    await this.openNewRuleModal();

    // Llenar formulario
    await this.fillField(this.ruleNameInput, ruleData.name);
    await this.selectOption(this.ruleTypeSelect, ruleData.type);
    await this.fillField(this.parametersInput, ruleData.parameters);
    await this.fillField(this.priorityInput, ruleData.priority.toString());

    // Checkbox de enabled (si está definido)
    if (ruleData.enabled !== undefined) {
      const isChecked = await this.enabledCheckbox.isChecked();
      if (isChecked !== ruleData.enabled) {
        await this.clickElement(this.enabledCheckbox);
      }
    }

    await this.takeScreenshot('rules-form-filled');

    // Guardar
    await this.clickElement(this.saveButton);
    
    // Esperar confirmación
    await this.waitForToastMessage();
    await this.takeScreenshot('rules-created-success');
  }

  /**
   * Buscar regla por nombre
   */
  async searchRule(ruleName: string): Promise<void> {
    await this.fillField(this.searchInput, ruleName);
    await this.page.waitForTimeout(500); // Debounce de búsqueda
  }

  /**
   * Obtener lista de reglas visibles
   */
  async getRulesList(): Promise<string[]> {
    // Las reglas se muestran en cards, no en tabla
    const ruleCards = await this.page.locator('.bg-admin-surface.rounded-xl.p-6').all();
    const rules: string[] = [];
    
    for (const card of ruleCards) {
      const ruleName = await card.locator('h3').textContent();
      if (ruleName) rules.push(ruleName.trim());
    }
    
    return rules;
  }

  /**
   * Verificar que regla existe en la lista
   */
  async ruleExists(ruleName: string): Promise<boolean> {
    const rules = await this.getRulesList();
    return rules.some(rule => rule.includes(ruleName));
  }

  /**
   * Click en regla específica
   */
  async clickRule(ruleName: string): Promise<void> {
    const ruleRow = this.rulesTable.locator('tbody tr').filter({ hasText: ruleName });
    await this.clickElement(ruleRow);
  }

  /**
   * Activar/Desactivar regla
   */
  async toggleRuleStatus(ruleName: string): Promise<void> {
    const ruleRow = this.rulesTable.locator('tbody tr').filter({ hasText: ruleName });
    const toggleButton = ruleRow.locator('button[data-action="toggle"], input[type="checkbox"]');
    await this.clickElement(toggleButton);
    await this.waitForToastMessage();
  }

  /**
   * Eliminar regla
   */
  async deleteRule(ruleName: string): Promise<void> {
    const ruleRow = this.rulesTable.locator('tbody tr').filter({ hasText: ruleName });
    const deleteButton = ruleRow.getByRole('button', { name: /eliminar|delete/i });
    await this.clickElement(deleteButton);
    
    // Confirmar eliminación si hay modal de confirmación
    const confirmButton = this.page.getByRole('button', { name: /confirmar|confirm|sí|yes/i });
    if (await confirmButton.isVisible({ timeout: 2000 })) {
      await this.clickElement(confirmButton);
    }
    
    await this.waitForToastMessage();
  }

  /**
   * Obtener detalles de una regla
   */
  async getRuleDetails(ruleName: string): Promise<{
    name: string;
    type: string;
    status: string;
    priority: string;
  }> {
    const ruleRow = this.rulesTable.locator('tbody tr').filter({ hasText: ruleName });
    const cells = await ruleRow.locator('td').all();
    
    return {
      name: await cells[0]?.textContent() || '',
      type: await cells[1]?.textContent() || '',
      status: await cells[2]?.textContent() || '',
      priority: await cells[3]?.textContent() || ''
    };
  }

  /**
   * Verificar que modal está cerrado
   */
  async isModalClosed(): Promise<boolean> {
    return !(await this.modal.isVisible({ timeout: 1000 }));
  }

  /**
   * Contar total de reglas
   */
  async getTotalRulesCount(): Promise<number> {
    return await this.countElements(this.page.locator('.bg-admin-surface.rounded-xl.p-6'));
  }
}
