/**
 * Tests para useChatbot Hook
 * Fase 2 - Paso 3: Business Logic
 * 
 * Metodología TDD - FASE RED
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChatbot } from '../../hooks/useChatbot';
import { WELCOME_MESSAGE } from '../../data/faqData';

describe('useChatbot Hook', () => {
  describe('Inicialización', () => {
    it('should initialize with chat closed', () => {
      const { result } = renderHook(() => useChatbot());
      expect(result.current.isOpen).toBe(false);
    });

    it('should initialize with welcome message', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
      });

      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].text).toBe(WELCOME_MESSAGE);
      expect(result.current.messages[0].sender).toBe('bot');
    });

    it('should not be typing initially', () => {
      const { result } = renderHook(() => useChatbot());
      expect(result.current.isTyping).toBe(false);
    });
  });

  describe('Abrir y Cerrar Chat', () => {
    it('should open chat when openChat is called', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
      });

      expect(result.current.isOpen).toBe(true);
    });

    it('should close chat when closeChat is called', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.closeChat();
      });

      expect(result.current.isOpen).toBe(false);
    });

    it('should preserve messages when chat is closed and reopened', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
      });

      const messageCount = result.current.messages.length;

      act(() => {
        result.current.closeChat();
        result.current.openChat();
      });

      expect(result.current.messages).toHaveLength(messageCount);
    });
  });

  describe('Enviar Mensajes', () => {
    it('should add user message when sendMessage is called', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.sendMessage('Hola');
      });

      const lastMessage = result.current.messages[result.current.messages.length - 1];
      expect(lastMessage.text).toBe('Hola');
      expect(lastMessage.sender).toBe('user');
    });

    it('should generate bot response after user message', async () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
      });

      const initialCount = result.current.messages.length;

      act(() => {
        result.current.sendMessage('¿Cómo creo una cuenta?');
      });

      // Esperar a que termine el typing indicator
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 600));
      });

      expect(result.current.messages.length).toBeGreaterThan(initialCount + 1);
    });

    it('should show typing indicator before bot response', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.sendMessage('Hola');
      });

      expect(result.current.isTyping).toBe(true);
    });

    it('should hide typing indicator after bot response', async () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.sendMessage('Hola');
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 600));
      });

      expect(result.current.isTyping).toBe(false);
    });
  });

  describe('Respuestas del Bot', () => {
    it('should respond with FAQ answer when keywords match', async () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.sendMessage('¿Cómo creo una cuenta?');
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 600));
      });

      const botResponse = result.current.messages[result.current.messages.length - 1];
      expect(botResponse.sender).toBe('bot');
      expect(botResponse.text).toContain('crear una cuenta');
    });

    it('should respond with fallback when no keywords match', async () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.sendMessage('xyz123abc');
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 600));
      });

      const botResponse = result.current.messages[result.current.messages.length - 1];
      expect(botResponse.sender).toBe('bot');
      expect(botResponse.text).toContain('No encontré');
    });

    it('should respond immediately when FAQ is selected', () => {
      const { result } = renderHook(() => useChatbot());
      
      const mockFAQ = {
        id: 'faq-1',
        category: 'cuenta-acceso',
        question: '¿Cómo creo una cuenta?',
        answer: 'Para crear una cuenta, haz clic en "Registrarse"...',
        keywords: ['crear', 'cuenta', 'registro']
      };

      act(() => {
        result.current.openChat();
        result.current.selectFAQ(mockFAQ);
      });

      const lastTwoMessages = result.current.messages.slice(-2);
      expect(lastTwoMessages[0].text).toBe(mockFAQ.question);
      expect(lastTwoMessages[0].sender).toBe('user');
      expect(lastTwoMessages[1].text).toBe(mockFAQ.answer);
      expect(lastTwoMessages[1].sender).toBe('bot');
    });
  });

  describe('Generación de IDs', () => {
    it('should generate unique message IDs', () => {
      const { result } = renderHook(() => useChatbot());
      
      act(() => {
        result.current.openChat();
        result.current.sendMessage('Mensaje 1');
      });

      act(() => {
        result.current.sendMessage('Mensaje 2');
      });

      const ids = result.current.messages.map(m => m.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });
  });
});
