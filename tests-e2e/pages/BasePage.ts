import { Page, Locator } from '@playwright/test';

/**
 * BasePage - Clase base para todos los Page Objects
 * 
 * Proporciona funcionalidad común:
 * - Navegación
 * - Esperas inteligentes
 * - Screenshots
 * - Manejo de errores
 * - Utilidades de interacción
 */
export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navegar a una URL específica
   */
  async goto(url: string): Promise<void> {
    await this.page.goto(url, { waitUntil: 'domcontentloaded' });
  }

  /**
   * Esperar a que un elemento sea visible
   */
  async waitForElement(locator: Locator, timeout: number = 10000): Promise<void> {
    await locator.waitFor({ state: 'visible', timeout });
  }

  /**
   * Click con espera automática
   */
  async clickElement(locator: Locator): Promise<void> {
    await locator.waitFor({ state: 'visible' });
    await locator.click();
  }

  /**
   * Llenar campo de texto con espera
   */
  async fillField(locator: Locator, text: string): Promise<void> {
    await locator.waitFor({ state: 'visible' });
    await locator.clear();
    await locator.fill(text);
  }

  /**
   * Seleccionar opción de dropdown
   */
  async selectOption(locator: Locator, value: string): Promise<void> {
    await locator.waitFor({ state: 'visible' });
    await locator.selectOption(value);
  }

  /**
   * Obtener texto de un elemento
   */
  async getElementText(locator: Locator): Promise<string> {
    await locator.waitFor({ state: 'visible' });
    return await locator.textContent() || '';
  }

  /**
   * Verificar que elemento existe
   */
  async elementExists(locator: Locator): Promise<boolean> {
    try {
      await locator.waitFor({ state: 'visible', timeout: 3000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Tomar screenshot con nombre personalizado
   */
  async takeScreenshot(name: string): Promise<void> {
    const timestamp = new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-');
    await this.page.screenshot({ 
      path: `screenshots/${name}-${timestamp}.png`,
      fullPage: false  // Cambiado a false para evitar error de 32767 píxeles
    });
  }

  /**
   * Esperar a que desaparezca el spinner de carga
   */
  async waitForLoadingComplete(): Promise<void> {
    try {
      await this.page.waitForSelector('[data-testid="loading-spinner"]', { 
        state: 'hidden', 
        timeout: 5000 
      });
    } catch {
      // Si no hay spinner, continuar
    }
  }

  /**
   * Obtener título de la página
   */
  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * Verificar que URL contiene un texto
   */
  async urlContains(text: string): Promise<boolean> {
    return this.page.url().includes(text);
  }

  /**
   * Esperar a que aparezca un toast/notification
   */
  async waitForToastMessage(timeout: number = 5000): Promise<string> {
    const toast = this.page.locator('[role="status"], .toast, [class*="toast"]').first();
    await toast.waitFor({ state: 'visible', timeout });
    return await toast.textContent() || '';
  }

  /**
   * Hacer scroll hacia un elemento
   */
  async scrollToElement(locator: Locator): Promise<void> {
    await locator.scrollIntoViewIfNeeded();
  }

  /**
   * Presionar tecla
   */
  async pressKey(key: string): Promise<void> {
    await this.page.keyboard.press(key);
  }

  /**
   * Obtener atributo de un elemento
   */
  async getElementAttribute(locator: Locator, attribute: string): Promise<string | null> {
    await locator.waitFor({ state: 'visible' });
    return await locator.getAttribute(attribute);
  }

  /**
   * Verificar que elemento está habilitado
   */
  async isElementEnabled(locator: Locator): Promise<boolean> {
    return await locator.isEnabled();
  }

  /**
   * Contar elementos que coinciden con locator
   */
  async countElements(locator: Locator): Promise<number> {
    return await locator.count();
  }
}
