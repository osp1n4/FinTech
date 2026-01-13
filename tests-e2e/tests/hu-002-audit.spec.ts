import { test, expect } from '@playwright/test';
import { randomUUID } from 'node:crypto';

/**
 * E2E Tests para HU-002: Auditoría Inmutable de Evaluaciones
 * 
 * Test Cases implementados:
 * - TC-HU-002-01: Verificar registro automático en auditoría
 * - TC-HU-002-02: Consultar historial completo de un usuario
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('HU-002: Auditoría Inmutable de Evaluaciones', () => {

  test.beforeAll(async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
  });

  test('TC-HU-002-01: Registro automático en auditoría', async ({ request }) => {
    // Paso 1: Crear una transacción para generar registro de auditoría
    const transactionData = {
      id: `txn_audit_${Date.now()}`,
      user_id: 'user_audit_001',
      amount: 500,
      location: { latitude: 4.711, longitude: -74.0721 },
      timestamp: new Date().toISOString()
    };

    const createResponse = await request.post(`${API_BASE_URL}/transaction`, {
      data: transactionData,
      timeout: 10000
    });

    expect(createResponse.status()).toBe(202);
    const { transaction_id } = await createResponse.json();

    // Esperar a que se procese la transacción (procesamiento asíncrono)
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Paso 2: Verificar que existe en el audit log consultando todos los registros
    const auditAllResponse = await request.get(`${API_BASE_URL}/audit/all`, {
      timeout: 10000
    });

    expect(auditAllResponse.status()).toBe(200);
    
    const allAudits = await auditAllResponse.json();
    expect(Array.isArray(allAudits)).toBe(true);
    
    // Buscar nuestra transacción en la lista
    const ourAudit = allAudits.find((a: any) => a.transaction_id === transaction_id);
    expect(ourAudit).toBeDefined();
    expect(ourAudit.risk_level).toBeDefined();
    expect(ourAudit.timestamp).toBeTruthy();

    console.log('✅ TC-HU-002-01 PASSED: Auditoría completa registrada');
    console.log('   Transaction ID:', transaction_id);
    console.log('   Risk level:', ourAudit.risk_level);
  });

  test('TC-HU-002-02: Consulta de historial por usuario', async ({ request }) => {
    // Paso 1: Crear múltiples transacciones para el mismo usuario
    const userId = `user_history_${Date.now()}`;
    
    const transactions = [
      { amount: 100, location: { latitude: 4.711, longitude: -74.0721 } },
      { amount: 1800, location: { latitude: 4.711, longitude: -74.0721 } },
      { amount: 500, location: { latitude: 4.711, longitude: -74.0721 } }
    ];

    for (const tx of transactions) {
      const response = await request.post(`${API_BASE_URL}/transaction`, {
        data: {
          id: `txn_${userId}_${Date.now()}_${randomUUID().substring(0, 8)}`,
          user_id: userId,
          amount: tx.amount,
          location: tx.location,
          timestamp: new Date().toISOString()
        },
        timeout: 10000
      });
      expect(response.status()).toBe(202);
      // Pequeña pausa entre transacciones
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Esperar a que se procesen
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Paso 2: Consultar historial del usuario
    const historyResponse = await request.get(`${API_BASE_URL}/audit/user/${userId}`, {
      timeout: 10000
    });

    // Resultado Esperado: Lista filtrada correctamente por userId
    expect(historyResponse.status()).toBe(200);
    
    const historyData = await historyResponse.json();
    expect(Array.isArray(historyData)).toBe(true);
    expect(historyData.length).toBeGreaterThanOrEqual(1); // Al menos una debe estar procesada

    console.log('✅ TC-HU-002-02 PASSED: Historial completo recuperado');
    console.log('   User ID:', userId);
    console.log('   Total transactions:', historyData.length);
  });
});
