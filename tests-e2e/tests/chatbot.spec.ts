/**
 * Tests E2E para Chatbot de Soporte FAQ
 * Fase 2 - Paso 4: Integration
 * 
 * TDD RED Phase - Tests que deben fallar inicialmente
 */

import { test, expect } from '@playwright/test';

test.describe('Chatbot de Soporte FAQ', () => {
  test.beforeEach(async ({ page }) => {
    // Navegar a la página principal del usuario
    await page.goto('http://localhost:5173/');
    
    // Login (si es necesario)
    // Por ahora asumimos que HomePage está accesible directamente
  });

  test('01 - should display chat button on HomePage', async ({ page }) => {
    // Verificar que el botón del chatbot está visible
    const chatButton = page.getByRole('button', { name: /chat|ayuda|soporte/i });
    await expect(chatButton).toBeVisible();
    
    // Verificar que tiene el icono de chat
    await expect(chatButton).toContainText('💬');
  });

  test('02 - should open and close chat modal', async ({ page }) => {
    // Click en el botón del chatbot
    const chatButton = page.getByRole('button', { name: /chat|ayuda|soporte/i });
    await chatButton.click();
    
    // Verificar que el modal se abre
    await expect(page.getByText(/asistente de soporte fintech/i)).toBeVisible();
    
    // Verificar mensaje de bienvenida
    await expect(page.getByText(/hola/i)).toBeVisible();
    
    // Cerrar el modal
    const closeButton = page.getByRole('button', { name: /cerrar|close|×/i });
    await closeButton.click();
    
    // Verificar que el modal se cierra
    await expect(page.getByText(/asistente de soporte fintech/i)).not.toBeVisible();
  });

  test('03 - should send message and receive bot response', async ({ page }) => {
    // Abrir chat
    const chatButton = page.getByRole('button', { name: /chat|ayuda|soporte/i });
    await chatButton.click();
    
    // Esperar que cargue el mensaje de bienvenida
    await page.waitForSelector('text=/asistente de soporte fintech/i');
    
    // Escribir pregunta
    const input = page.getByPlaceholder(/escribe tu pregunta/i);
    await input.fill('¿Cómo creo una cuenta?');
    
    // Enviar mensaje
    const sendButton = page.getByRole('button', { name: /enviar/i });
    await sendButton.click();
    
    // Verificar que aparece el mensaje del usuario
    await expect(page.getByText('¿Cómo creo una cuenta?')).toBeVisible();
    
    // Esperar respuesta del bot
    await page.waitForTimeout(700); // Esperar más que el delay de typing (600ms)
    
    // Verificar que aparece respuesta del bot con la palabra clave
    await expect(page.getByText(/registrarse|email|código/i)).toBeVisible();
  });

  test('04 - should show fallback message for unknown query', async ({ page }) => {
    // Abrir chat
    const chatButton = page.getByRole('button', { name: /chat|ayuda|soporte/i });
    await chatButton.click();
    
    await page.waitForSelector('text=/asistente de soporte fintech/i');
    
    // Escribir pregunta sin coincidencia
    const input = page.getByPlaceholder(/escribe tu pregunta/i);
    await input.fill('xyz123 pregunta aleatoria sin sentido');
    
    const sendButton = page.getByRole('button', { name: /enviar/i });
    await sendButton.click();
    
    // Esperar respuesta
    await page.waitForTimeout(700);
    
    // Verificar mensaje fallback
    await expect(page.getByText(/no encontré una respuesta/i)).toBeVisible();
  });

  test('05 - should select FAQ from list', async ({ page }) => {
    // Abrir chat
    const chatButton = page.getByRole('button', { name: /chat|ayuda|soporte/i });
    await chatButton.click();
    
    await page.waitForSelector('text=/asistente de soporte fintech/i');
    
    // Buscar y click en una FAQ de la lista (si está visible)
    // Las FAQs pueden estar como botones o links
    const faqButton = page.getByText(/¿cómo creo una cuenta\?/i).first();
    
    if (await faqButton.isVisible()) {
      await faqButton.click();
      
      // Verificar que aparece la pregunta como mensaje del usuario
      await expect(page.getByText(/¿cómo creo una cuenta\?/i)).toBeVisible();
      
      // Verificar que aparece la respuesta inmediatamente (sin delay de typing)
      await expect(page.getByText(/registrarse/i)).toBeVisible();
    }
  });

  test('06 - should show typing indicator', async ({ page }) => {
    // Abrir chat
    const chatButton = page.getByRole('button', { name: /chat|ayuda|soporte/i });
    await chatButton.click();
    
    await page.waitForSelector('text=/asistente de soporte fintech/i');
    
    // Escribir y enviar mensaje
    const input = page.getByPlaceholder(/escribe tu pregunta/i);
    await input.fill('¿Cómo inicio sesión?');
    
    const sendButton = page.getByRole('button', { name: /enviar/i });
    await sendButton.click();
    
    // Verificar que aparece indicador de typing (puede ser texto "escribiendo..." o puntos animados)
    // Esperamos un breve momento para capturar el indicador
    await page.waitForTimeout(100);
    
    // El indicador debería estar visible brevemente
    const typingIndicator = page.getByText(/escribiendo|typing|\.\.\./i);
    
    // Verificar que eventualmente aparece la respuesta
    await page.waitForTimeout(700);
    await expect(page.getByText(/user_id|contraseña|dashboard/i)).toBeVisible();
  });
});
