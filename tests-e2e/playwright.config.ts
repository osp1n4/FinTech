import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';

// Cargar variables de entorno desde .env
dotenv.config();

/**
 * Configuración de Playwright para Fraud Detection Engine
 * 
 * Características:
 * - Screenshots automáticos en fallos
 * - Videos de ejecución (on-first-retry)
 * - Trace con timeline completo
 * - HTML Reporter interactivo
 * - Tests en paralelo
 * - Multi-browser support
 */
export default defineConfig({
  testDir: './tests',
  
  /* Configuración de timeout */
  timeout: 120 * 1000, // 120 segundos por test (aumentado para tests lentos)
  expect: {
    timeout: 15000, // 15 segundos para assertions
  },

  /* Configuración de ejecución */
  fullyParallel: true, // Ejecutar tests en paralelo para mayor velocidad
  forbidOnly: !!process.env.CI, // Fallar si hay test.only en CI
  retries: process.env.CI ? 2 : 0, // Sin reintentos en local para acelerar
  workers: 3, // 3 workers en paralelo para mejor rendimiento
  
  /* Reportes */
  reporter: [
    ['html', { 
      outputFolder: 'test-results/html-report',
      open: 'never' // Cambiar a 'always' para abrir automáticamente
    }],
    ['json', { 
      outputFile: 'test-results/results.json' 
    }],
    ['junit', { 
      outputFile: 'test-results/junit.xml' 
    }],
    ['list'] // Reporter en consola
  ],

  /* Configuración global de tests */
  use: {
    /* URL base de la aplicación */
    baseURL: 'http://localhost:3001', // Admin dashboard por defecto

    /* Trace on first retry */
    trace: 'on-first-retry',

    /* Screenshots */
    screenshot: 'off', // Deshabilitado para evitar error de 32767 píxeles

    /* Videos */
    video: 'retain-on-failure', // Guardar video solo si falla

    /* Configuración del navegador */
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true,
    
    /* Configuración de timeouts */
    actionTimeout: 10000, // 10 segundos para acciones
    navigationTimeout: 30000, // 30 segundos para navegación
  },

  /* Proyectos de testing (multi-browser) */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--disable-dev-shm-usage'] // Para CI/Docker
        }
      },
    },

    
    /* Tests en dispositivos móviles (opcional) */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],

  /* Configuración de servidor local (opcional) */
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:3001',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120 * 1000,
  // },
});
