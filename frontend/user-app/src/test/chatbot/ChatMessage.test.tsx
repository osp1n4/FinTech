/**
 * Tests para ChatMessage Component
 * Fase 2 - Paso 2: UI Components
 * 
 * Metodología TDD - FASE RED
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ChatMessage from '../../components/chatbot/ChatMessage';
import type { ChatMessage as ChatMessageType } from '../../types/chatbot.types';

const mockUserMessage: ChatMessageType = {
  id: 'msg-1',
  text: 'Hola, necesito ayuda',
  sender: 'user',
  timestamp: new Date('2026-01-21T10:00:00')
};

const mockBotMessage: ChatMessageType = {
  id: 'msg-2',
  text: 'Hola 👋, ¿en qué puedo ayudarte?',
  sender: 'bot',
  timestamp: new Date('2026-01-21T10:00:01')
};

describe('ChatMessage Component', () => {
  it('should render user message', () => {
    render(<ChatMessage message={mockUserMessage} />);
    expect(screen.getByText('Hola, necesito ayuda')).toBeInTheDocument();
  });

  it('should render bot message', () => {
    render(<ChatMessage message={mockBotMessage} />);
    expect(screen.getByText(/en qué puedo ayudarte/i)).toBeInTheDocument();
  });

  it('should apply different styles for user vs bot', () => {
    const { rerender } = render(<ChatMessage message={mockUserMessage} />);
    const userBubble = screen.getByTestId('chat-message');
    expect(userBubble.className).toMatch(/justify-end/);
    
    rerender(<ChatMessage message={mockBotMessage} />);
    const botBubble = screen.getByTestId('chat-message');
    expect(botBubble.className).toMatch(/justify-start/);
  });

  it('should display timestamp', () => {
    render(<ChatMessage message={mockUserMessage} />);
    expect(screen.getByText(/10:00/)).toBeInTheDocument();
  });

  it('should show bot indicator for bot messages', () => {
    render(<ChatMessage message={mockBotMessage} />);
    expect(screen.getByText(/bot/i)).toBeInTheDocument();
  });
});
