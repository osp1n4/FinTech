import { defineConfig, devices } from '@playwright/test';

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
  timeout: 30 * 1000, // 30 segundos por test
  expect: {
    timeout: 5000, // 5 segundos para assertions
  },

  /* Configuración de ejecución */
  fullyParallel: true, // Ejecutar tests en paralelo
  forbidOnly: !!process.env.CI, // Fallar si hay test.only en CI
  retries: process.env.CI ? 2 : 0, // 2 reintentos en CI, 0 en local
  workers: process.env.CI ? 1 : undefined, // Workers en paralelo (local: auto)
  
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
    screenshot: 'only-on-failure', // Cambiar a 'on' para siempre capturar

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

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
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
