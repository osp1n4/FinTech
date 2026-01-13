import { test, expect } from '@playwright/test';

/**
 * E2E Tests para HU-001: Recepción de Transacciones por API
 * 
 * Test Cases implementados:
 * - TC-HU-001-01: Recepción exitosa de transacción válida
 * - TC-HU-001-02: Rechazo de transacción sin userId
 * - TC-HU-001-03: Rechazo de transacción con monto negativo
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('HU-001: Recepción de Transacciones por API', () => {

  test.beforeAll(async () => {
    // Esperar a que el API esté disponible
    await new Promise(resolve => setTimeout(resolve, 500));
  });

  test('TC-HU-001-01: Recepción exitosa de transacción válida', async ({ request }) => {
    // Datos de Entrada
    const transactionData = {
      id: `txn_${Date.now()}`,
      user_id: 'user_001',
      amount: 500,
      location: { latitude: 4.711, longitude: -74.0721 },
      timestamp: new Date().toISOString(),
      transaction_type: 'transfer'
    };

    // Pasos: Envío POST a /transaction con datos válidos
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: transactionData,
      timeout: 10000
    });

    // Resultado Esperado: Transacción recibida correctamente (HTTP 202)
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(202);
    
    const responseBody = await response.json();
    expect(responseBody.status).toBe('accepted');
    expect(responseBody.transaction_id).toBe(transactionData.id);
    expect(responseBody.risk_level).toBeDefined();
    expect(['LOW_RISK', 'MEDIUM_RISK', 'HIGH_RISK']).toContain(responseBody.risk_level);

    console.log('✅ TC-HU-001-01 PASSED:', responseBody);
  });

  test('TC-HU-001-02: Rechazo de transacción sin userId', async ({ request }) => {
    // Datos de Entrada: user_id omitido
    const invalidTransaction = {
      id: `txn_${Date.now()}`,
      amount: 500,
      location: { latitude: 4.711, longitude: -74.0721 }
    };

    // Pasos: Envío POST sin el campo user_id
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: invalidTransaction,
      timeout: 10000
    });

    // Resultado Esperado: Error de validación HTTP 422
    expect([400, 422]).toContain(response.status());
    
    const responseBody = await response.json();
    expect(responseBody.detail).toBeDefined();
    const bodyStr = JSON.stringify(responseBody).toLowerCase();
    expect(bodyStr.includes('userid') || bodyStr.includes('user_id') || bodyStr.includes('required')).toBeTruthy();

    console.log('✅ TC-HU-001-02 PASSED: Validación correcta de userId requerido');
  });

  test('TC-HU-001-03: Rechazo de transacción con monto negativo', async ({ request }) => {
    // Datos de Entrada: amount negativo
    const invalidTransaction = {
      id: `txn_${Date.now()}`,
      user_id: 'user_001',
      amount: -100,
      location: { latitude: 4.711, longitude: -74.0721 }
    };

    // Pasos: Envío POST con amount negativo
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: invalidTransaction,
      timeout: 10000
    });

    // Resultado Esperado: Validación rechaza montos negativos
    expect([400, 422]).toContain(response.status());
    
    const responseBody = await response.json();
    const bodyStr = JSON.stringify(responseBody).toLowerCase();
    expect(bodyStr.includes('amount') || bodyStr.includes('positive') || bodyStr.includes('negative')).toBeTruthy();

    console.log('✅ TC-HU-001-03 PASSED: Validación correcta de monto positivo');
  });
});
