/**
 * Tests para ChatButton Component
 * Fase 2 - Paso 2: UI Components
 * 
 * Metodología TDD - FASE RED
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatButton from '../../components/chatbot/ChatButton';

describe('ChatButton Component', () => {
  it('should render the chat button', () => {
    render(<ChatButton onClick={() => {}} />);
    const button = screen.getByRole('button', { name: /soporte/i });
    expect(button).toBeInTheDocument();
  });

  it('should display chat icon', () => {
    render(<ChatButton onClick={() => {}} />);
    expect(screen.getByText('💬')).toBeInTheDocument();
  });

  it('should call onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<ChatButton onClick={handleClick} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should have fixed position styling', () => {
    render(<ChatButton onClick={() => {}} />);
    const button = screen.getByRole('button');
    expect(button.className).toMatch(/fixed/);
  });

  it('should be accessible with aria-label', () => {
    render(<ChatButton onClick={() => {}} />);
    const button = screen.getByLabelText(/abrir chat de soporte/i);
    expect(button).toBeInTheDocument();
  });
});
