import { Page } from '@playwright/test';
import { TransactionsPage } from '../pages/TransactionsPage';

/**
 * ReviewTransaction - Task para revisar transacciones sospechosas
 * Patrón Screenplay: Encapsula la lógica de revisión manual
 */
export class ReviewTransaction {
  /**
   * Aprobar transacción pendiente
   */
  static async approve(
    page: Page,
    transactionId: string,
    justification: string = 'Transacción válida verificada por administrador'
  ): Promise<void> {
    const transactionsPage = new TransactionsPage(page);
    await transactionsPage.navigate();
    await transactionsPage.filterByStatus('pending');
    await transactionsPage.approveTransaction(transactionId, justification);
  }

  /**
   * Rechazar transacción sospechosa
   */
  static async reject(
    page: Page,
    transactionId: string,
    justification: string = 'Transacción fraudulenta confirmada'
  ): Promise<void> {
    const transactionsPage = new TransactionsPage(page);
    await transactionsPage.navigate();
    await transactionsPage.filterByStatus('pending');
    await transactionsPage.rejectTransaction(transactionId, justification);
  }

  /**
   * Revisar todas las transacciones pendientes
   */
  static async reviewAllPending(page: Page): Promise<number> {
    const transactionsPage = new TransactionsPage(page);
    await transactionsPage.navigate();
    await transactionsPage.filterByStatus('pending');
    
    const pendingCount = await transactionsPage.countTransactionsByStatus('pending');
    return pendingCount;
  }

  /**
   * Buscar y aprobar transacción específica
   */
  static async findAndApprove(
    page: Page,
    searchText: string,
    justification: string
  ): Promise<void> {
    const transactionsPage = new TransactionsPage(page);
    await transactionsPage.navigate();
    await transactionsPage.searchTransaction(searchText);
    
    const transactions = await transactionsPage.getTransactionsList();
    if (transactions.length > 0) {
      await transactionsPage.approveTransaction(transactions[0].id, justification);
    }
  }

  /**
   * Verificar estado de transacción
   */
  static async checkStatus(
    page: Page,
    transactionId: string
  ): Promise<string> {
    const transactionsPage = new TransactionsPage(page);
    await transactionsPage.navigate();
    return await transactionsPage.getTransactionStatus(transactionId);
  }
}
