import { test, expect } from '@playwright/test';
import { ValidateTransaction } from '../tasks/ValidateTransaction';
import transactionsFixture from '../fixtures/transactions.json';

/**
 * Tests E2E de Integración con API
 * 
 * Casos de prueba:
 * 1. Validar transacción de bajo riesgo
 * 2. Validar transacción de alto riesgo (monto)
 * 3. Validar transacción con ubicación sospechosa
 * 4. Validar transacción con dispositivo desconocido
 * 5. Verificar estado de transacción
 */

test.describe('API Integration - Validación de Transacciones', () => {

  test('TEST-031: Validar transacción de bajo riesgo vía API', async ({ request }) => {
    // Arrange
    const lowRiskTransaction = transactionsFixture[0];

    // Act
    const result = await ValidateTransaction.viaAPI(request, {
      userId: lowRiskTransaction.userId,
      amount: lowRiskTransaction.amount,
      location: lowRiskTransaction.location,
      deviceId: lowRiskTransaction.deviceId
    });

    // Assert
    expect(result.transactionId).toBeTruthy();
    expect(result.status).toBeDefined();
    console.log('Transacción de bajo riesgo:', result);
  });

  test('TEST-032: Validar transacción de alto monto vía API', async ({ request }) => {
    // Arrange
    const highAmountTransaction = transactionsFixture[2];

    // Act
    const result = await ValidateTransaction.viaAPI(request, {
      userId: highAmountTransaction.userId,
      amount: highAmountTransaction.amount,
      location: highAmountTransaction.location,
      deviceId: highAmountTransaction.deviceId
    });

    // Assert
    expect(result.transactionId).toBeTruthy();
    expect(result.riskScore).toBeGreaterThan(0);
    console.log('Transacción de alto monto:', result);
  });

  test('TEST-033: Validar transacción con ubicación sospechosa vía API', async ({ request }) => {
    // Arrange
    const suspiciousLocationTx = transactionsFixture[3];

    // Act
    const result = await ValidateTransaction.viaAPI(request, {
      userId: suspiciousLocationTx.userId,
      amount: suspiciousLocationTx.amount,
      location: suspiciousLocationTx.location,
      deviceId: suspiciousLocationTx.deviceId
    });

    // Assert
    expect(result.transactionId).toBeTruthy();
    console.log('Transacción con ubicación sospechosa:', result);
  });

  test('TEST-034: Validar transacción con dispositivo desconocido vía API', async ({ request }) => {
    // Arrange
    const unknownDeviceTx = transactionsFixture[4];

    // Act
    const result = await ValidateTransaction.viaAPI(request, {
      userId: unknownDeviceTx.userId,
      amount: unknownDeviceTx.amount,
      location: unknownDeviceTx.location,
      deviceId: unknownDeviceTx.deviceId
    });

    // Assert
    expect(result.transactionId).toBeTruthy();
    console.log('Transacción con dispositivo desconocido:', result);
  });

  test('TEST-035: Validar transacción de alto riesgo múltiple vía API', async ({ request }) => {
    // Arrange - Transacción con múltiples factores de riesgo
    const highRiskTx = transactionsFixture[5];

    // Act
    const result = await ValidateTransaction.viaAPI(request, {
      userId: highRiskTx.userId,
      amount: highRiskTx.amount,
      location: highRiskTx.location,
      deviceId: highRiskTx.deviceId
    });

    // Assert
    expect(result.transactionId).toBeTruthy();
    expect(result.riskScore).toBeGreaterThan(0);
    console.log('Transacción de alto riesgo múltiple:', result);
  });

  test('TEST-037: Validar múltiples transacciones en secuencia', async ({ request }) => {
    // Arrange
    const testTransactions = [
      { userId: 'user_001', amount: 50, location: '4.7110,-74.0721', deviceId: 'device_001' },
      { userId: 'user_001', amount: 100, location: '4.7110,-74.0721', deviceId: 'device_001' },
      { userId: 'user_001', amount: 150, location: '4.7110,-74.0721', deviceId: 'device_001' }
    ];

    const results = [];

    // Act
    for (const tx of testTransactions) {
      const result = await ValidateTransaction.viaAPI(request, tx);
      results.push(result);
    }

    // Assert
    expect(results.length).toBe(3);
    results.forEach(result => {
      expect(result.transactionId).toBeTruthy();
    });

    console.log('Transacciones creadas:', results.map(r => r.transactionId));
  });

  test('TEST-038: Validar transacción usando helper lowRisk', async ({ request }) => {
    // Act
    const transactionId = await ValidateTransaction.lowRisk(request, 'user_helper_001');

    // Assert
    expect(transactionId).toBeTruthy();
    console.log('Transacción de bajo riesgo creada:', transactionId);
  });

  test('TEST-039: Validar transacción usando helper highRiskAmount', async ({ request }) => {
    // Act
    const transactionId = await ValidateTransaction.highRiskAmount(request, 'user_helper_002');

    // Assert
    expect(transactionId).toBeTruthy();
    console.log('Transacción de alto monto creada:', transactionId);
  });

  test('TEST-040: Validar transacción usando helper suspiciousLocation', async ({ request }) => {
    // Act
    const transactionId = await ValidateTransaction.suspiciousLocation(request, 'user_helper_003');

    // Assert
    expect(transactionId).toBeTruthy();
    console.log('Transacción con ubicación sospechosa creada:', transactionId);
  });

  test('TEST-041: Validar transacción usando helper unknownDevice', async ({ request }) => {
    // Act
    const transactionId = await ValidateTransaction.unknownDevice(request, 'user_helper_004');

    // Assert
    expect(transactionId).toBeTruthy();
    console.log('Transacción con dispositivo desconocido creada:', transactionId);
  });

  test('TEST-042: Verificar formato de respuesta de API', async ({ request }) => {
    // Act
    const result = await ValidateTransaction.lowRisk(request);

    // Assert - Verificar estructura de respuesta
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string'); // transactionId es string
    expect(result.length).toBeGreaterThan(0);

    console.log('Transaction ID format validated:', result);
  });
});
