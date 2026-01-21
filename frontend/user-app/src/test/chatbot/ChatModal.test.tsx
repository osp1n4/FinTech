/**
 * Tests para ChatModal Component
 * Fase 2 - Paso 2: UI Components
 * 
 * Metodología TDD - FASE RED
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatModal from '../../components/chatbot/ChatModal';
import type { ChatMessage } from '../../types/chatbot.types';

const mockMessages: ChatMessage[] = [
  {
    id: 'msg-1',
    text: 'Hola 👋, soy el asistente de Soporte FinTech.',
    sender: 'bot',
    timestamp: new Date('2026-01-21T10:00:00')
  },
  {
    id: 'msg-2',
    text: '¿Cómo creo una cuenta?',
    sender: 'user',
    timestamp: new Date('2026-01-21T10:00:05')
  }
];

describe('ChatModal Component', () => {
  it('should render when isOpen is true', () => {
    render(
      <ChatModal 
        isOpen={true} 
        onClose={() => {}} 
        messages={mockMessages}
        onSendMessage={() => {}}
      />
    );
    expect(screen.getByText(/asistente de soporte/i)).toBeInTheDocument();
  });

  it('should not render when isOpen is false', () => {
    render(
      <ChatModal 
        isOpen={false} 
        onClose={() => {}} 
        messages={mockMessages}
        onSendMessage={() => {}}
      />
    );
    expect(screen.queryByText(/asistente de soporte/i)).not.toBeInTheDocument();
  });

  it('should render header with title', () => {
    render(
      <ChatModal 
        isOpen={true} 
        onClose={() => {}} 
        messages={[]}
        onSendMessage={() => {}}
      />
    );
    expect(screen.getByText(/soporte fintech/i)).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(
      <ChatModal 
        isOpen={true} 
        onClose={handleClose} 
        messages={[]}
        onSendMessage={() => {}}
      />
    );
    
    const closeButton = screen.getByRole('button', { name: /cerrar/i });
    fireEvent.click(closeButton);
    
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('should render all messages', () => {
    render(
      <ChatModal 
        isOpen={true} 
        onClose={() => {}} 
        messages={mockMessages}
        onSendMessage={() => {}}
      />
    );
    
    expect(screen.getByText(/asistente de soporte/i)).toBeInTheDocument();
    expect(screen.getByText('¿Cómo creo una cuenta?')).toBeInTheDocument();
  });

  it('should have input for sending messages', () => {
    render(
      <ChatModal 
        isOpen={true} 
        onClose={() => {}} 
        messages={[]}
        onSendMessage={() => {}}
      />
    );
    
    expect(screen.getByPlaceholderText(/escribe tu pregunta/i)).toBeInTheDocument();
  });

  it('should show bot indicator', () => {
    render(
      <ChatModal 
        isOpen={true} 
        onClose={() => {}} 
        messages={[]}
        onSendMessage={() => {}}
      />
    );
    
    expect(screen.getByText(/bot automático/i)).toBeInTheDocument();
  });

  it('should show typing indicator when isTyping is true', () => {
    render(
      <ChatModal 
        isOpen={true} 
        onClose={() => {}} 
        messages={[]}
        onSendMessage={() => {}}
        isTyping={true}
      />
    );
    
    expect(screen.getByText(/escribiendo/i)).toBeInTheDocument();
  });
});
