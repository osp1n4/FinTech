import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * TransactionsPage - Page Object para la página de transacciones (Admin)
 * URL: http://localhost:3001/transactions
 * 
 * Funcionalidades:
 * - Listar transacciones
 * - Filtrar por estado
 * - Ver detalles de transacción
 * - Aprobar/Rechazar transacción pendiente
 * - Buscar transacción
 */
export class TransactionsPage extends BasePage {
  // Locators principales
  readonly transactionsTable: Locator;
  readonly searchInput: Locator;
  readonly statusFilter: Locator;
  readonly refreshButton: Locator;

  // Filtros de estado
  readonly allFilter: Locator;
  readonly approvedFilter: Locator;
  readonly rejectedFilter: Locator;
  readonly pendingFilter: Locator;

  // Modal de detalles
  readonly detailsModal: Locator;
  readonly transactionId: Locator;
  readonly transactionAmount: Locator;
  readonly transactionStatus: Locator;
  readonly justificationTextarea: Locator;
  readonly approveButton: Locator;
  readonly rejectButton: Locator;
  readonly closeModalButton: Locator;

  constructor(page: Page) {
    super(page);
    
    // Elementos principales
    this.transactionsTable = page.locator('table, [data-testid="transactions-table"]');
    this.searchInput = page.getByPlaceholder(/buscar|search/i);
    this.statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]');
    this.refreshButton = page.getByRole('button', { name: /actualizar|refresh/i });

    // Filtros rápidos
    this.allFilter = page.getByRole('button', { name: /todas|all/i });
    this.approvedFilter = page.getByRole('button', { name: /aprobadas|approved/i });
    this.rejectedFilter = page.getByRole('button', { name: /rechazadas|rejected/i });
    this.pendingFilter = page.getByRole('button', { name: /pendientes|pending/i });

    // Modal de detalles
    this.detailsModal = page.locator('[role="dialog"], .modal');
    this.transactionId = page.locator('[data-field="transaction-id"]');
    this.transactionAmount = page.locator('[data-field="amount"]');
    this.transactionStatus = page.locator('[data-field="status"]');
    this.justificationTextarea = page.locator('textarea[name="justification"], textarea[placeholder*="justif"]');
    this.approveButton = page.getByRole('button', { name: /aprobar|approve/i });
    this.rejectButton = page.getByRole('button', { name: /rechazar|reject/i });
    this.closeModalButton = page.getByRole('button', { name: /cerrar|close/i });
  }

  /**
   * Navegar a la página de transacciones
   */
  async navigate(): Promise<void> {
    await this.goto('http://localhost:3001/transactions');
    await this.waitForLoadingComplete();
  }

  /**
   * Filtrar transacciones por estado
   */
  /**
   * Filtrar transacciones por estado usando el select
   */
  async filterByStatus(status: 'all' | 'approved' | 'rejected' | 'pending'): Promise<void> {
    const valueMap = {
      all: '',
      approved: 'APPROVED',
      rejected: 'REJECTED',
      pending: 'SUSPICIOUS'
    };
    
    // Usar el select dropdown en lugar de botones
    const selectElement = this.page.locator('select').first();
    await selectElement.selectOption(valueMap[status]);
    await this.waitForLoadingComplete();
    await this.takeScreenshot(`transactions-filtered-${status}`);
  }

  /**
   * Buscar transacción por texto
   */
  async searchTransaction(searchText: string): Promise<void> {
    await this.fillField(this.searchInput, searchText);
    await this.page.waitForTimeout(500); // Debounce
  }

  /**
   * Obtener lista de transacciones visibles (limitado a primeras 50 para performance)
   */
  async getTransactionsList(limit: number = 50): Promise<Array<{
    id: string;
    amount: string;
    status: string;
    date: string;
  }>> {
    const rows = await this.transactionsTable.locator('tbody tr').all();
    const transactions: Array<{id: string; amount: string; status: string; date: string}> = [];
    
    // Limitar la cantidad de filas procesadas para evitar timeout
    const maxRows = Math.min(rows.length, limit);
    
    for (let i = 0; i < maxRows; i++) {
      const row = rows[i];
      const cells = await row.locator('td').all();
      if (cells.length >= 4) {
        transactions.push({
          id: await cells[0]?.textContent() || '',
          amount: await cells[1]?.textContent() || '',
          status: await cells[2]?.textContent() || '',
          date: await cells[3]?.textContent() || ''
        });
      }
    }
    
    return transactions;
  }

  /**
   * Click en una transacción específica
   */
  async clickTransaction(transactionId: string): Promise<void> {
    const row = this.transactionsTable.locator('tbody tr').filter({ hasText: transactionId });
    await this.clickElement(row);
    await this.waitForElement(this.detailsModal);
    await this.takeScreenshot('transaction-details-opened');
  }

  /**
   * Aprobar transacción pendiente
   */
  async approveTransaction(transactionId: string, justification: string): Promise<void> {
    await this.clickTransaction(transactionId);
    await this.fillField(this.justificationTextarea, justification);
    await this.takeScreenshot('transaction-approval-filled');
    await this.clickElement(this.approveButton);
    await this.waitForToastMessage();
    await this.takeScreenshot('transaction-approved');
  }

  /**
   * Rechazar transacción pendiente
   */
  async rejectTransaction(transactionId: string, justification: string): Promise<void> {
    await this.clickTransaction(transactionId);
    await this.fillField(this.justificationTextarea, justification);
    await this.takeScreenshot('transaction-rejection-filled');
    await this.clickElement(this.rejectButton);
    await this.waitForToastMessage();
    await this.takeScreenshot('transaction-rejected');
  }

  /**
   * Cerrar modal de detalles
   */
  async closeDetailsModal(): Promise<void> {
    await this.clickElement(this.closeModalButton);
    await this.page.waitForTimeout(300); // Animación de cierre
  }

  /**
   * Contar transacciones por estado
   */
  async countTransactionsByStatus(status: string): Promise<number> {
    const transactions = await this.getTransactionsList();
    return transactions.filter(tx => tx.status.toLowerCase().includes(status.toLowerCase())).length;
  }

  /**
   * Verificar que transacción existe
   */
  async transactionExists(transactionId: string): Promise<boolean> {
    const transactions = await this.getTransactionsList();
    return transactions.some(tx => tx.id.includes(transactionId));
  }

  /**
   * Obtener estado de transacción
   */
  async getTransactionStatus(transactionId: string): Promise<string> {
    await this.clickTransaction(transactionId);
    const status = await this.getElementText(this.transactionStatus);
    await this.closeDetailsModal();
    return status;
  }

  /**
   * Actualizar lista de transacciones (recargando la página)
   */
  async refreshTransactions(): Promise<void> {
    await this.page.reload();
    await this.waitForLoadingComplete();
  }
}
