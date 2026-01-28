/**
 * Tests para ChatInput Component
 * Fase 2 - Paso 2: UI Components
 * 
 * Metodología TDD - FASE RED
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatInput from '../../components/chatbot/ChatInput';

describe('ChatInput Component', () => {
  it('should render input field', () => {
    render(<ChatInput onSend={() => {}} />);
    const input = screen.getByPlaceholderText(/escribe tu pregunta/i);
    expect(input).toBeInTheDocument();
  });

  it('should render send button', () => {
    render(<ChatInput onSend={() => {}} />);
    const button = screen.getByRole('button', { name: /enviar/i });
    expect(button).toBeInTheDocument();
  });

  it('should call onSend with input value when submitted', async () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);
    
    const input = screen.getByPlaceholderText(/escribe tu pregunta/i);
    await userEvent.type(input, 'Mi pregunta');
    
    const button = screen.getByRole('button', { name: /enviar/i });
    fireEvent.click(button);
    
    expect(handleSend).toHaveBeenCalledWith('Mi pregunta');
  });

  it('should clear input after sending', async () => {
    render(<ChatInput onSend={() => {}} />);
    
    const input = screen.getByPlaceholderText(/escribe tu pregunta/i) as HTMLInputElement;
    await userEvent.type(input, 'Mi pregunta');
    
    const button = screen.getByRole('button', { name: /enviar/i });
    fireEvent.click(button);
    
    expect(input.value).toBe('');
  });

  it('should not send empty message', () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);
    
    const button = screen.getByRole('button', { name: /enviar/i });
    fireEvent.click(button);
    
    expect(handleSend).not.toHaveBeenCalled();
  });

  it('should send on Enter key press', async () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);
    
    const input = screen.getByPlaceholderText(/escribe tu pregunta/i);
    await userEvent.type(input, 'Mi pregunta{enter}');
    
    expect(handleSend).toHaveBeenCalledWith('Mi pregunta');
  });

  it('should be disabled when disabled prop is true', () => {
    render(<ChatInput onSend={() => {}} disabled />);
    
    const input = screen.getByPlaceholderText(/escribe tu pregunta/i);
    const button = screen.getByRole('button', { name: /enviar/i });
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });
});
