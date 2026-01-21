/**
 * Tests para FAQ Data
 * Fase 2 - Paso 1: Data Layer
 * 
 * Verifica la integridad de los datos de FAQs
 */

import { describe, it, expect } from 'vitest';
import { faqData, WELCOME_MESSAGE, FALLBACK_MESSAGE } from '../../data/faqData';
import type { FAQCategory } from '../../types/chatbot.types';

describe('FAQ Data - Structure', () => {
  it('should have at least 15 FAQs', () => {
    expect(faqData.length).toBeGreaterThanOrEqual(15);
  });

  it('should have unique IDs for all FAQs', () => {
    const ids = faqData.map(faq => faq.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it('should have all required properties for each FAQ', () => {
    for (const faq of faqData) {
      expect(faq).toHaveProperty('id');
      expect(faq).toHaveProperty('category');
      expect(faq).toHaveProperty('question');
      expect(faq).toHaveProperty('answer');
      expect(faq).toHaveProperty('keywords');
      expect(Array.isArray(faq.keywords)).toBe(true);
      expect(faq.keywords.length).toBeGreaterThan(0);
    }
  });
});

describe('FAQ Data - Categories', () => {
  const validCategories: FAQCategory[] = [
    'cuenta-acceso',
    'transacciones',
    'seguridad-fraude',
    'problemas-tecnicos',
    'soporte'
  ];

  it('should have FAQs for all categories', () => {
    for (const category of validCategories) {
      const categoryFaqs = faqData.filter(faq => faq.category === category);
      expect(categoryFaqs.length).toBeGreaterThan(0);
    }
  });

  it('should only use valid categories', () => {
    for (const faq of faqData) {
      expect(validCategories).toContain(faq.category);
    }
  });
});

describe('FAQ Data - Content', () => {
  it('should have non-empty questions', () => {
    for (const faq of faqData) {
      expect(faq.question.trim().length).toBeGreaterThan(0);
    }
  });

  it('should have non-empty answers', () => {
    for (const faq of faqData) {
      expect(faq.answer.trim().length).toBeGreaterThan(0);
    }
  });

  it('should have at least 3 keywords per FAQ', () => {
    for (const faq of faqData) {
      expect(faq.keywords.length).toBeGreaterThanOrEqual(3);
    }
  });
});

describe('FAQ Data - Messages', () => {
  it('should have a welcome message', () => {
    expect(WELCOME_MESSAGE).toBeDefined();
    expect(WELCOME_MESSAGE.length).toBeGreaterThan(0);
    expect(WELCOME_MESSAGE).toContain('FinTech');
  });

  it('should have a fallback message', () => {
    expect(FALLBACK_MESSAGE).toBeDefined();
    expect(FALLBACK_MESSAGE.length).toBeGreaterThan(0);
  });

  it('should mention support contact in fallback', () => {
    expect(FALLBACK_MESSAGE).toContain('soporte');
  });
});
