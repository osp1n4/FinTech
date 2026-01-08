import { Page } from '@playwright/test';
import { RulesPage } from '../pages/RulesPage';

/**
 * CreateRule - Task para crear reglas de fraude
 * Patrón Screenplay: Encapsula la lógica de creación de reglas
 */
export class CreateRule {
  /**
   * Crear regla de umbral de monto
   */
  static async withAmountThreshold(
    page: Page, 
    ruleName: string, 
    threshold: number
  ): Promise<void> {
    const rulesPage = new RulesPage(page);
    
    await rulesPage.createRule({
      name: ruleName,
      type: 'amount_threshold',
      parameters: JSON.stringify({ threshold }),
      priority: 10,
      enabled: true
    });
  }

  /**
   * Crear regla de ubicación
   */
  static async withLocationRadius(
    page: Page,
    ruleName: string,
    maxDistanceKm: number
  ): Promise<void> {
    const rulesPage = new RulesPage(page);
    
    await rulesPage.createRule({
      name: ruleName,
      type: 'location_check', // Coincide con el frontend real
      parameters: JSON.stringify({ radius_km: maxDistanceKm }),
      priority: 20,
      enabled: true
    });
  }

  /**
   * Crear regla personalizada
   */
  static async withCustomParameters(
    page: Page,
    ruleName: string,
    type: string,
    parameters: Record<string, any>,
    priority: number = 10
  ): Promise<void> {
    const rulesPage = new RulesPage(page);
    
    await rulesPage.createRule({
      name: ruleName,
      type,
      parameters: JSON.stringify(parameters),
      priority,
      enabled: true
    });
  }

  /**
   * Crear regla basada en tiempo
   */
  static async withTimeWindow(
    page: Page,
    ruleName: string,
    windowMinutes: number,
    maxTransactions: number
  ): Promise<void> {
    const rulesPage = new RulesPage(page);
    
    await rulesPage.createRule({
      name: ruleName,
      type: 'time_based',
      parameters: JSON.stringify({ 
        window_minutes: windowMinutes,
        max_transactions: maxTransactions 
      }),
      priority: 15,
      enabled: true
    });
  }

  /**
   * Crear regla de dispositivo
   */
  static async withDeviceValidation(
    page: Page,
    ruleName: string,
    requireKnownDevice: boolean
  ): Promise<void> {
    const rulesPage = new RulesPage(page);
    
    await rulesPage.createRule({
      name: ruleName,
      type: 'frequency', // Usando un tipo que existe en el select
      parameters: JSON.stringify({ require_known_device: requireKnownDevice }),
      priority: 25,
      enabled: true
    });
  }
}
