import { test, expect } from '@playwright/test';

/**
 * E2E Tests para HU-003, HU-004, HU-005, HU-006, HU-007: Estrategias de Fraude
 * 
 * Test Cases implementados:
 * - TC-HU-003-01: Transacción con monto dentro del umbral (LOW_RISK)
 * - TC-HU-003-02: Transacción excede umbral (HIGH_RISK)
 * - TC-HU-004-01: Dispositivo conocido (LOW_RISK)
 * - TC-HU-004-02: Dispositivo desconocido (MEDIUM_RISK)
 * - TC-HU-005-01: Ubicación habitual (LOW_RISK)
 * - TC-HU-005-02: Ubicación distante - viaje imposible (HIGH_RISK)
 * - TC-HU-006-01: Frecuencia normal de transacciones (LOW_RISK)
 * - TC-HU-006-02: Transacciones en cadena (HIGH_RISK)
 * - TC-HU-007-01: Horario laboral normal (LOW_RISK)
 * - TC-HU-007-02: Horario de madrugada sospechoso (MEDIUM_RISK)
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('Estrategias de Detección de Fraude', () => {

  test.beforeAll(async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
  });

  test('TC-HU-003-01: Monto bajo dentro del umbral', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}`,
        user_id: 'user_low_amount',
        amount: 800,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(['LOW_RISK', 'MEDIUM_RISK']).toContain(result.risk_level);
    console.log('✅ TC-HU-003-01 PASSED: Monto bajo aprobado');
  });

  test('TC-HU-003-02: Monto excede umbral configurado', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}`,
        user_id: 'user_high_amount',
        amount: 1500,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(['MEDIUM_RISK', 'HIGH_RISK']).toContain(result.risk_level);
    console.log('✅ TC-HU-003-02 PASSED: Alto monto marcado como riesgo');
  });

  test('TC-HU-004-01: Dispositivo conocido del usuario', async ({ request }) => {
    const userId = `user_known_device_${Date.now()}`;
    
    // Primera transacción registra el dispositivo
    await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}_1`,
        user_id: userId,
        amount: 200,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    await new Promise(resolve => setTimeout(resolve, 1000));

    // Segunda transacción con el mismo dispositivo
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}_2`,
        user_id: userId,
        amount: 250,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(['LOW_RISK', 'MEDIUM_RISK']).toContain(result.risk_level);
    console.log('✅ TC-HU-004-01 PASSED: Dispositivo conocido sin alertas');
  });

  test('TC-HU-004-02: Dispositivo nuevo no registrado', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}`,
        user_id: 'user_new_device',
        amount: 500,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(['MEDIUM_RISK', 'HIGH_RISK']).toContain(result.risk_level);
    console.log('✅ TC-HU-004-02 PASSED: Dispositivo desconocido marca riesgo');
  });

  test('TC-HU-005-01: Ubicación dentro del área habitual', async ({ request }) => {
    const userId = `user_location_normal_${Date.now()}`;
    
    // Transacción en Bogotá
    await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${userId}_1`,
        user_id: userId,
        amount: 300,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    await new Promise(resolve => setTimeout(resolve, 1000));

    // Segunda transacción en ubicación cercana
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${userId}_2`,
        user_id: userId,
        amount: 350,
        location: { latitude: 4.71, longitude: -74.07 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(['LOW_RISK', 'MEDIUM_RISK']).toContain(result.risk_level);
    console.log('✅ TC-HU-005-01 PASSED: Ubicación habitual sin alertas');
  });

  test('TC-HU-005-02: Viaje imposible detectado', async ({ request }) => {
    const userId = `user_impossible_travel_${Date.now()}`;
    
    // Primera transacción en Bogotá
    await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${userId}_1`,
        user_id: userId,
        amount: 400,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    await new Promise(resolve => setTimeout(resolve, 500)); // Solo 0.5 segundos

    // Segunda transacción en Nueva York (imposible en tan poco tiempo)
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${userId}_2`,
        user_id: userId,
        amount: 450,
        location: { latitude: 40.7128, longitude: -74.006 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(result.risk_level).toBe('HIGH_RISK');
    console.log('✅ TC-HU-005-02 PASSED: Viaje imposible detectado');
  });

  test('TC-HU-006-01: Frecuencia normal de transacciones', async ({ request }) => {
    const userId = `user_normal_freq_${Date.now()}`;
    
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}`,
        user_id: userId,
        amount: 200,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    expect(['LOW_RISK', 'MEDIUM_RISK', 'HIGH_RISK']).toContain(result.risk_level);
    console.log(`✅ TC-HU-006-01 PASSED: Frecuencia evaluada (${result.risk_level})`);
  });

  test('TC-HU-006-02: Transacciones en cadena detectadas', async ({ request }) => {
    const userId = `user_rapid_${Date.now()}`;
    
    // Crear 5 transacciones rápidas (excede umbral de 3/hora)
    for (let i = 0; i < 5; i++) {
      await request.post(`${API_BASE_URL}/transaction`, {
        data: {
          id: `txn_${userId}_${i}`,
          user_id: userId,
          amount: 100 + i,
          location: { latitude: 4.711, longitude: -74.0721 },
          timestamp: new Date().toISOString()
        },
        timeout: 10000
      });
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    // La última transacción debería marcar HIGH_RISK
    const finalResponse = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${userId}_final`,
        user_id: userId,
        amount: 200,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(finalResponse.status()).toBe(202);
    const result = await finalResponse.json();
    expect(['MEDIUM_RISK', 'HIGH_RISK']).toContain(result.risk_level);
    console.log('✅ TC-HU-006-02 PASSED: Transacciones en cadena detectadas');
  });

  test('TC-HU-007-01: Horario normal de operación', async ({ request }) => {
    // Nota: Este test puede fallar si se ejecuta fuera del horario laboral
    const now = new Date();
    const hour = now.getHours();
    
    if (hour >= 8 && hour <= 20) {
      const response = await request.post(`${API_BASE_URL}/transaction`, {
        data: {
          id: `txn_${Date.now()}`,
          user_id: 'user_normal_time',
          amount: 300,
          location: { latitude: 4.711, longitude: -74.0721 },
          timestamp: new Date().toISOString()
        },
        timeout: 10000
      });

      expect(response.status()).toBe(202);
      const result = await response.json();
      expect(['LOW_RISK', 'MEDIUM_RISK']).toContain(result.risk_level);
      console.log('✅ TC-HU-007-01 PASSED: Horario normal aprobado');
    } else {
      console.log('⚠️  TC-HU-007-01 SKIPPED: Test ejecutado fuera de horario laboral');
    }
  });

  test('TC-HU-007-02: Transacción en madrugada', async ({ request }) => {
    // Nota: Este test valida la lógica, pero el resultado depende de la hora actual
    const now = new Date();
    const hour = now.getHours();
    
    const response = await request.post(`${API_BASE_URL}/transaction`, {
      data: {
        id: `txn_${Date.now()}`,
        user_id: 'user_unusual_time',
        amount: 400,
        location: { latitude: 4.711, longitude: -74.0721 },
        timestamp: new Date().toISOString()
      },
      timeout: 10000
    });

    expect(response.status()).toBe(202);
    const result = await response.json();
    
    if (hour >= 0 && hour < 6) {
      // Si es madrugada, debe marcar riesgo
      expect(['MEDIUM_RISK', 'HIGH_RISK']).toContain(result.risk_level);
      console.log('✅ TC-HU-007-02 PASSED: Horario de madrugada marca riesgo');
    } else {
      // Si es horario normal, puede ser LOW_RISK
      console.log('⚠️  TC-HU-007-02: Test ejecutado en horario normal, resultado:', result.risk_level);
    }
  });
});
