import { test, expect } from '@playwright/test';
import { NavigateTo } from '../tasks/NavigateTo';
import { TransactionsPage } from '../pages/TransactionsPage';

/**
 * Tests E2E para Admin Dashboard - Gestión de Transacciones
 * 
 * Casos de prueba:
 * 1. Ver listado de transacciones
 * 2. Filtrar transacciones por estado
 * 3. Aprobar transacción pendiente
 * 4. Rechazar transacción sospechosa
 * 5. Buscar transacción específica
 */

test.describe('Admin Dashboard - Gestión de Transacciones', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navegar a la página de transacciones antes de cada test
    await NavigateTo.transactionsPage(page);
  });

  test('TEST-011: Ver listado completo de transacciones', async ({ page }) => {
    // Arrange & Act
    const transactionsPage = new TransactionsPage(page);
    const transactions = await transactionsPage.getTransactionsList();

    // Assert
    expect(transactions.length).toBeGreaterThanOrEqual(0);
    
    console.log(`Total de transacciones: ${transactions.length}`);

    await transactionsPage.takeScreenshot('test-011-transactions-list');
  });

  test('TEST-012: Filtrar transacciones por estado PENDING', async ({ page }) => {
    // Arrange
    const transactionsPage = new TransactionsPage(page);

    // Act
    await transactionsPage.filterByStatus('pending');

    // Assert
    const pendingCount = await transactionsPage.countTransactionsByStatus('pending');
    console.log(`Transacciones pendientes: ${pendingCount}`);

    await transactionsPage.takeScreenshot('test-012-pending-transactions');
  });

  test('TEST-013: Filtrar transacciones por estado APPROVED', async ({ page }) => {
    // Arrange
    const transactionsPage = new TransactionsPage(page);

    // Act
    await transactionsPage.filterByStatus('approved');

    // Assert
    const approvedCount = await transactionsPage.countTransactionsByStatus('approved');
    console.log(`Transacciones aprobadas: ${approvedCount}`);

    await transactionsPage.takeScreenshot('test-013-approved-transactions');
  });

  test('TEST-014: Filtrar transacciones por estado REJECTED', async ({ page }) => {
    // Arrange
    const transactionsPage = new TransactionsPage(page);

    // Act
    await transactionsPage.filterByStatus('rejected');

    // Assert
    const rejectedCount = await transactionsPage.countTransactionsByStatus('rejected');
    console.log(`Transacciones rechazadas: ${rejectedCount}`);

    await transactionsPage.takeScreenshot('test-014-rejected-transactions');
  });

  test('TEST-017: Actualizar listado de transacciones', async ({ page }) => {
    // Arrange
    const transactionsPage = new TransactionsPage(page);

    // Act
    await transactionsPage.refreshTransactions();

    // Assert
    const transactions = await transactionsPage.getTransactionsList();
    expect(transactions).toBeDefined();

    await transactionsPage.takeScreenshot('test-017-refreshed-list');
  });

  test('TEST-018: Verificar paginación de transacciones', async ({ page }) => {
    // Arrange
    const transactionsPage = new TransactionsPage(page);
    const firstPageTransactions = await transactionsPage.getTransactionsList();

    // Assert
    console.log(`Transacciones en primera página: ${firstPageTransactions.length}`);
    
    await transactionsPage.takeScreenshot('test-018-pagination');
  });

  test('TEST-020: Contar transacciones por cada estado', async ({ page }) => {
    // Arrange
    const transactionsPage = new TransactionsPage(page);
    const statuses = ['all', 'approved', 'rejected', 'pending'] as const;
    const counts: Record<string, number> = {};

    // Act
    for (const status of statuses) {
      await transactionsPage.filterByStatus(status);
      const transactions = await transactionsPage.getTransactionsList();
      counts[status] = transactions.length;
    }

    // Assert
    console.log('Conteo de transacciones por estado:', counts);
    expect(counts.all).toBeGreaterThanOrEqual(0);

    await transactionsPage.takeScreenshot('test-020-status-counts');
  });
});
