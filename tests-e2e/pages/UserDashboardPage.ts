import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * UserDashboardPage - Page Object para la aplicación de usuario
 * URL: http://localhost:5173
 * 
 * Funcionalidades:
 * - Ver historial de transacciones
 * - Filtrar transacciones por fecha
 * - Ver detalles de transacción
 * - Verificar estado de transacciones
 */
export class UserDashboardPage extends BasePage {
  // Locators principales
  readonly transactionsContainer: Locator;
  readonly transactionCards: Locator;
  readonly dateFilterFrom: Locator;
  readonly dateFilterTo: Locator;
  readonly applyFilterButton: Locator;
  readonly clearFilterButton: Locator;

  // Encabezado
  readonly pageTitle: Locator;
  readonly userInfo: Locator;

  // Tarjetas de transacción
  readonly approvedBadge: Locator;
  readonly rejectedBadge: Locator;
  readonly pendingBadge: Locator;

  constructor(page: Page) {
    super(page);
    
    // Elementos principales
    this.transactionsContainer = page.locator('[data-testid="transactions-list"], .transactions-container');
    this.transactionCards = page.locator('[data-testid="transaction-card"], .transaction-card');
    this.dateFilterFrom = page.locator('input[type="date"][name="dateFrom"], input[placeholder*="Desde"]');
    this.dateFilterTo = page.locator('input[type="date"][name="dateTo"], input[placeholder*="Hasta"]');
    this.applyFilterButton = page.getByRole('button', { name: /aplicar|apply/i });
    this.clearFilterButton = page.getByRole('button', { name: /limpiar|clear/i });

    // Encabezado
    this.pageTitle = page.locator('h1, h2').first();
    this.userInfo = page.locator('[data-testid="user-info"], .user-info');

    // Badges de estado
    this.approvedBadge = page.locator('[data-status="approved"], .badge-approved');
    this.rejectedBadge = page.locator('[data-status="rejected"], .badge-rejected');
    this.pendingBadge = page.locator('[data-status="pending"], .badge-pending');
  }

  /**
   * Navegar a la página de usuario
   */
  async navigate(): Promise<void> {
    const userAppUrl = process.env.USER_APP_URL || 'http://localhost:3000';
    await this.goto(userAppUrl);
    await this.waitForLoadingComplete();
  }

  /**
   * Obtener lista de transacciones visibles
   */
  async getTransactionsList(): Promise<Array<{
    id: string;
    amount: string;
    status: string;
    date: string;
  }>> {
    const cards = await this.transactionCards.all();
    const transactions: Array<{id: string; amount: string; status: string; date: string}> = [];
    
    for (const card of cards) {
      transactions.push({
        id: await card.locator('[data-field="id"]').textContent() || '',
        amount: await card.locator('[data-field="amount"]').textContent() || '',
        status: await card.locator('[data-field="status"]').textContent() || '',
        date: await card.locator('[data-field="date"]').textContent() || ''
      });
    }
    
    return transactions;
  }

  /**
   * Filtrar transacciones por rango de fechas
   */
  async filterByDateRange(fromDate: string, toDate: string): Promise<void> {
    await this.fillField(this.dateFilterFrom, fromDate);
    await this.fillField(this.dateFilterTo, toDate);
    await this.clickElement(this.applyFilterButton);
    await this.waitForLoadingComplete();
    await this.takeScreenshot('user-transactions-filtered-by-date');
  }

  /**
   * Limpiar filtros
   */
  async clearFilters(): Promise<void> {
    await this.clickElement(this.clearFilterButton);
    await this.waitForLoadingComplete();
  }

  /**
   * Contar transacciones por estado
   */
  async countTransactionsByStatus(status: 'approved' | 'rejected' | 'pending'): Promise<number> {
    const badgeMap = {
      approved: this.approvedBadge,
      rejected: this.rejectedBadge,
      pending: this.pendingBadge
    };
    
    return await this.countElements(badgeMap[status]);
  }

  /**
   * Click en una transacción específica
   */
  async clickTransaction(transactionId: string): Promise<void> {
    const card = this.transactionCards.filter({ hasText: transactionId });
    await this.clickElement(card);
    await this.takeScreenshot('user-transaction-details');
  }

  /**
   * Verificar que transacción existe
   */
  async transactionExists(transactionId: string): Promise<boolean> {
    const transactions = await this.getTransactionsList();
    return transactions.some(tx => tx.id.includes(transactionId));
  }

  /**
   * Obtener total de transacciones mostradas
   */
  async getTotalTransactionsCount(): Promise<number> {
    return await this.countElements(this.transactionCards);
  }

  /**
   * Verificar que no hay transacciones
   */
  async hasNoTransactions(): Promise<boolean> {
    const count = await this.getTotalTransactionsCount();
    return count === 0;
  }

  /**
   * Obtener título de la página
   */
  async getPageHeader(): Promise<string> {
    return await this.getElementText(this.pageTitle);
  }
}
