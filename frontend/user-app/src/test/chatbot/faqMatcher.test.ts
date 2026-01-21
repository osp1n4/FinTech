/**
 * Tests para FAQ Matcher
 * Fase 2 - Paso 1: Data Layer
 * 
 * Metodología TDD - FASE RED
 * Estos tests deben FALLAR inicialmente
 */

import { describe, it, expect } from 'vitest';
import { 
  normalizeText, 
  calculateMatchScore, 
  findBestMatch,
  getFAQsByCategory 
} from '../../utils/faqMatcher';
import type { FAQItem } from '../../types/chatbot.types';

// Mock FAQs para tests
const mockFAQs: FAQItem[] = [
  {
    id: 'faq-1',
    category: 'cuenta-acceso',
    question: '¿Cómo creo una cuenta?',
    answer: 'Para crear una cuenta, haz clic en "Registrarse"...',
    keywords: ['crear', 'cuenta', 'registrar', 'registro', 'nueva']
  },
  {
    id: 'faq-2',
    category: 'cuenta-acceso',
    question: '¿Cómo inicio sesión?',
    answer: 'Ingresa tu user_id y contraseña...',
    keywords: ['iniciar', 'sesion', 'login', 'entrar', 'acceder']
  },
  {
    id: 'faq-3',
    category: 'transacciones',
    question: '¿Cómo realizo una transacción?',
    answer: 'Desde el dashboard, selecciona "Nueva Transacción"...',
    keywords: ['transaccion', 'realizar', 'hacer', 'enviar', 'transferir']
  },
  {
    id: 'faq-4',
    category: 'seguridad-fraude',
    question: '¿Qué es el nivel de riesgo?',
    answer: 'Es una evaluación automática: LOW_RISK, MEDIUM_RISK, HIGH_RISK',
    keywords: ['riesgo', 'nivel', 'seguridad', 'evaluacion', 'fraude']
  },
  {
    id: 'faq-5',
    category: 'soporte',
    question: '¿Cómo contacto a soporte humano?',
    answer: 'Envía un email a soporte@fintech.com',
    keywords: ['soporte', 'contactar', 'humano', 'ayuda', 'email']
  }
];

describe('FAQ Matcher - normalizeText', () => {
  it('should convert text to lowercase', () => {
    expect(normalizeText('HOLA MUNDO')).toBe('hola mundo');
  });

  it('should remove accents from text', () => {
    expect(normalizeText('cómo estás')).toBe('como estas');
  });

  it('should handle mixed case and accents', () => {
    expect(normalizeText('¿Cómo CREO una Cuenta?')).toBe('como creo una cuenta');
  });

  it('should trim whitespace', () => {
    expect(normalizeText('  hola  ')).toBe('hola');
  });

  it('should handle empty string', () => {
    expect(normalizeText('')).toBe('');
  });
});

describe('FAQ Matcher - calculateMatchScore', () => {
  it('should return high score for exact keyword match', () => {
    const score = calculateMatchScore('crear cuenta', mockFAQs[0]);
    expect(score).toBeGreaterThan(0.5);
  });

  it('should return 0 for no match', () => {
    const score = calculateMatchScore('xyz abc', mockFAQs[0]);
    expect(score).toBe(0);
  });

  it('should return higher score for more keyword matches', () => {
    const scoreOne = calculateMatchScore('crear', mockFAQs[0]);
    const scoreTwo = calculateMatchScore('crear cuenta nueva', mockFAQs[0]);
    expect(scoreTwo).toBeGreaterThan(scoreOne);
  });

  it('should be case insensitive', () => {
    const scoreLower = calculateMatchScore('crear cuenta', mockFAQs[0]);
    const scoreUpper = calculateMatchScore('CREAR CUENTA', mockFAQs[0]);
    expect(scoreLower).toBe(scoreUpper);
  });

  it('should handle accents in query', () => {
    const score = calculateMatchScore('iniciar sesión', mockFAQs[1]);
    expect(score).toBeGreaterThan(0);
  });
});

describe('FAQ Matcher - findBestMatch', () => {
  it('should find matching FAQ for valid query', () => {
    const result = findBestMatch('como creo una cuenta', mockFAQs);
    expect(result.found).toBe(true);
    expect(result.faq?.id).toBe('faq-1');
  });

  it('should return found=false for no match', () => {
    const result = findBestMatch('pizza hamburguesa', mockFAQs);
    expect(result.found).toBe(false);
    expect(result.faq).toBeNull();
  });

  it('should find transaction FAQ', () => {
    const result = findBestMatch('como hago una transaccion', mockFAQs);
    expect(result.found).toBe(true);
    expect(result.faq?.category).toBe('transacciones');
  });

  it('should find security FAQ', () => {
    const result = findBestMatch('que es el nivel de riesgo', mockFAQs);
    expect(result.found).toBe(true);
    expect(result.faq?.category).toBe('seguridad-fraude');
  });

  it('should handle empty query', () => {
    const result = findBestMatch('', mockFAQs);
    expect(result.found).toBe(false);
  });

  it('should handle empty FAQ list', () => {
    const result = findBestMatch('crear cuenta', []);
    expect(result.found).toBe(false);
  });

  it('should return score in result', () => {
    const result = findBestMatch('crear cuenta', mockFAQs);
    expect(result.score).toBeGreaterThanOrEqual(0);
    expect(result.score).toBeLessThanOrEqual(1);
  });
});

describe('FAQ Matcher - getFAQsByCategory', () => {
  it('should return FAQs for cuenta-acceso category', () => {
    const faqs = getFAQsByCategory('cuenta-acceso', mockFAQs);
    expect(faqs).toHaveLength(2);
    expect(faqs.every(f => f.category === 'cuenta-acceso')).toBe(true);
  });

  it('should return FAQs for transacciones category', () => {
    const faqs = getFAQsByCategory('transacciones', mockFAQs);
    expect(faqs).toHaveLength(1);
    expect(faqs[0].category).toBe('transacciones');
  });

  it('should return empty array for non-existent category', () => {
    const faqs = getFAQsByCategory('inexistente', mockFAQs);
    expect(faqs).toHaveLength(0);
  });

  it('should handle empty FAQ list', () => {
    const faqs = getFAQsByCategory('cuenta-acceso', []);
    expect(faqs).toHaveLength(0);
  });
});
