import { Page } from '@playwright/test';
import { RulesPage } from '../pages/RulesPage';
import { TransactionsPage } from '../pages/TransactionsPage';
import { UserDashboardPage } from '../pages/UserDashboardPage';

/**
 * NavigateTo - Task para navegación entre páginas
 * Patrón Screenplay: Implementa la tarea de navegación
 */
export class NavigateTo {
  /**
   * Navegar a la página de reglas (Admin)
   */
  static async rulesPage(page: Page): Promise<RulesPage> {
    const rulesPage = new RulesPage(page);
    await rulesPage.navigate();
    return rulesPage;
  }

  /**
   * Navegar a la página de transacciones (Admin)
   */
  static async transactionsPage(page: Page): Promise<TransactionsPage> {
    const transactionsPage = new TransactionsPage(page);
    await transactionsPage.navigate();
    return transactionsPage;
  }

  /**
   * Navegar a la página de usuario
   */
  static async userDashboard(page: Page): Promise<UserDashboardPage> {
    const userDashboard = new UserDashboardPage(page);
    await userDashboard.navigate();
    return userDashboard;
  }

  /**
   * Navegar a URL específica
   */
  static async url(page: Page, url: string): Promise<void> {
    await page.goto(url, { waitUntil: 'domcontentloaded' });
  }
}
