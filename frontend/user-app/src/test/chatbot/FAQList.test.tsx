/**
 * Tests para FAQList Component
 * Fase 2 - Paso 2: UI Components
 * 
 * Metodología TDD - FASE RED
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FAQList from '../../components/chatbot/FAQList';
import type { FAQItem } from '../../types/chatbot.types';

const mockFAQs: FAQItem[] = [
  {
    id: 'faq-1',
    category: 'cuenta-acceso',
    question: '¿Cómo creo una cuenta?',
    answer: 'Para crear una cuenta...',
    keywords: ['crear', 'cuenta']
  },
  {
    id: 'faq-2',
    category: 'transacciones',
    question: '¿Cómo realizo una transacción?',
    answer: 'Para realizar una transacción...',
    keywords: ['transaccion', 'realizar']
  }
];

describe('FAQList Component', () => {
  it('should render list of FAQ questions', () => {
    render(<FAQList faqs={mockFAQs} onSelect={() => {}} />);
    
    expect(screen.getByText('¿Cómo creo una cuenta?')).toBeInTheDocument();
    expect(screen.getByText('¿Cómo realizo una transacción?')).toBeInTheDocument();
  });

  it('should call onSelect when FAQ is clicked', () => {
    const handleSelect = vi.fn();
    render(<FAQList faqs={mockFAQs} onSelect={handleSelect} />);
    
    fireEvent.click(screen.getByText('¿Cómo creo una cuenta?'));
    
    expect(handleSelect).toHaveBeenCalledWith(mockFAQs[0]);
  });

  it('should render title', () => {
    render(<FAQList faqs={mockFAQs} onSelect={() => {}} />);
    expect(screen.getByText(/preguntas frecuentes/i)).toBeInTheDocument();
  });

  it('should render empty state when no FAQs', () => {
    render(<FAQList faqs={[]} onSelect={() => {}} />);
    expect(screen.getByText(/no hay preguntas/i)).toBeInTheDocument();
  });

  it('should be keyboard accessible', () => {
    const handleSelect = vi.fn();
    render(<FAQList faqs={mockFAQs} onSelect={handleSelect} />);
    
    const firstFAQ = screen.getByText('¿Cómo creo una cuenta?');
    fireEvent.keyDown(firstFAQ, { key: 'Enter' });
    
    expect(handleSelect).toHaveBeenCalledWith(mockFAQs[0]);
  });
});
