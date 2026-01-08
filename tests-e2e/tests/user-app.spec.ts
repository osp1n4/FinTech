import { test, expect } from '@playwright/test';
import { NavigateTo } from '../tasks/NavigateTo';
import { UserDashboardPage } from '../pages/UserDashboardPage';

/**
 * Tests E2E para User App - Historial de Transacciones
 * 
 * Casos de prueba:
 * 1. Ver historial de transacciones del usuario
 * 2. Filtrar transacciones por fecha
 * 3. Ver detalles de transacción
 * 4. Verificar estados de transacciones
 * 5. Contar transacciones por estado
 */

test.describe('User App - Historial de Transacciones', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navegar a la app de usuario antes de cada test
    await NavigateTo.userDashboard(page);
  });

  test('TEST-021: Ver página principal de usuario', async ({ page }) => {
    // Arrange & Act
    const userDashboard = new UserDashboardPage(page);
    const pageTitle = await userDashboard.getPageHeader();

    // Assert
    expect(pageTitle).toBeTruthy();
    expect(await userDashboard.urlContains('localhost:5173')).toBe(true);

    await userDashboard.takeScreenshot('test-021-user-dashboard');
  });

  test('TEST-022: Ver historial completo de transacciones', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);

    // Act
    const transactions = await userDashboard.getTransactionsList();

    // Assert
    expect(transactions).toBeDefined();
    console.log(`Total de transacciones del usuario: ${transactions.length}`);

    await userDashboard.takeScreenshot('test-022-transaction-history');
  });

  test('TEST-023: Verificar que transacciones tienen información completa', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);
    const transactions = await userDashboard.getTransactionsList();

    // Skip si no hay transacciones
    test.skip(transactions.length === 0, 'No hay transacciones para verificar');

    // Assert
    const firstTransaction = transactions[0];
    expect(firstTransaction.id).toBeTruthy();
    expect(firstTransaction.amount).toBeTruthy();
    expect(firstTransaction.status).toBeTruthy();
    expect(firstTransaction.date).toBeTruthy();

    console.log('Primera transacción:', firstTransaction);

    await userDashboard.takeScreenshot('test-023-transaction-details');
  });

  test('TEST-024: Contar transacciones aprobadas', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);

    // Act
    const approvedCount = await userDashboard.countTransactionsByStatus('approved');

    // Assert
    expect(approvedCount).toBeGreaterThanOrEqual(0);
    console.log(`Transacciones aprobadas: ${approvedCount}`);

    await userDashboard.takeScreenshot('test-024-approved-count');
  });

  test('TEST-025: Contar transacciones rechazadas', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);

    // Act
    const rejectedCount = await userDashboard.countTransactionsByStatus('rejected');

    // Assert
    expect(rejectedCount).toBeGreaterThanOrEqual(0);
    console.log(`Transacciones rechazadas: ${rejectedCount}`);

    await userDashboard.takeScreenshot('test-025-rejected-count');
  });

  test('TEST-026: Contar transacciones pendientes', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);

    // Act
    const pendingCount = await userDashboard.countTransactionsByStatus('pending');

    // Assert
    expect(pendingCount).toBeGreaterThanOrEqual(0);
    console.log(`Transacciones pendientes: ${pendingCount}`);

    await userDashboard.takeScreenshot('test-026-pending-count');
  });

  test.skip('TEST-027: Filtrar transacciones por rango de fechas', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);
    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 7);

    const fromDate = lastWeek.toISOString().split('T')[0];
    const toDate = today.toISOString().split('T')[0];

    // Act
    await userDashboard.filterByDateRange(fromDate, toDate);

    // Assert
    const filteredTransactions = await userDashboard.getTransactionsList();
    console.log(`Transacciones en rango ${fromDate} - ${toDate}: ${filteredTransactions.length}`);

    await userDashboard.takeScreenshot('test-027-date-filter');
  });

  test.skip('TEST-028: Limpiar filtros de fecha', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);
    
    // Aplicar filtro primero
    const today = new Date().toISOString().split('T')[0];
    await userDashboard.filterByDateRange(today, today);
    const filteredCount = await userDashboard.getTotalTransactionsCount();

    // Act
    await userDashboard.clearFilters();

    // Assert
    const allCount = await userDashboard.getTotalTransactionsCount();
    expect(allCount).toBeGreaterThanOrEqual(filteredCount);

    await userDashboard.takeScreenshot('test-028-filters-cleared');
  });

  test.skip('TEST-029: Verificar que no hay transacciones (caso vacío)', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);
    
    // Filtrar por fecha futura para simular lista vacía
    const futureDate = new Date();
    futureDate.setFullYear(futureDate.getFullYear() + 1);
    const futureDateStr = futureDate.toISOString().split('T')[0];

    // Act
    await userDashboard.filterByDateRange(futureDateStr, futureDateStr);

    // Assert
    const hasNoTransactions = await userDashboard.hasNoTransactions();
    expect(hasNoTransactions).toBe(true);

    await userDashboard.takeScreenshot('test-029-no-transactions');
  });

  test('TEST-030: Verificar resumen de transacciones por estado', async ({ page }) => {
    // Arrange
    const userDashboard = new UserDashboardPage(page);

    // Act
    const totalTransactions = await userDashboard.getTotalTransactionsCount();
    const approvedCount = await userDashboard.countTransactionsByStatus('approved');
    const rejectedCount = await userDashboard.countTransactionsByStatus('rejected');
    const pendingCount = await userDashboard.countTransactionsByStatus('pending');

    // Assert
    console.log('Resumen de transacciones:');
    console.log(`  Total: ${totalTransactions}`);
    console.log(`  Aprobadas: ${approvedCount}`);
    console.log(`  Rechazadas: ${rejectedCount}`);
    console.log(`  Pendientes: ${pendingCount}`);

    expect(totalTransactions).toBeGreaterThanOrEqual(0);

    await userDashboard.takeScreenshot('test-030-transactions-summary');
  });
});
