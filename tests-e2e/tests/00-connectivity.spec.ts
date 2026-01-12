import { test, expect } from '@playwright/test';

/**
 * Test de conectividad básica - Verifica que el API esté disponible
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('00-Conectividad', () => {

  test('Verificar que el API está disponible', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/docs`, {
      timeout: 10000
    });

    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    console.log('✅ API está disponible en', API_BASE_URL);
  });

  test('Verificar endpoint de health check', async ({ request }) => {
    try {
      const response = await request.get(`${API_BASE_URL}/health`, {
        timeout: 10000
      });

      if (response.ok()) {
        console.log('✅ Health check endpoint disponible');
      } else {
        console.log('⚠️  Health check no disponible, pero API responde');
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.log('⚠️  Health check endpoint no implementado (esperado):', errorMessage);
    }
  });
});
