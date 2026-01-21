/**
 * FAQ Matcher - Lógica de búsqueda por keywords
 * Fase 2 - Paso 1: Data Layer
 * 
 * TODO: Implementar en fase GREEN
 */

import type { FAQItem, FAQMatchResult } from '../types/chatbot.types';

/**
 * Normaliza texto para comparación (minúsculas, sin acentos)
 */
export function normalizeText(text: string): string {
  // TODO: Implementar
  throw new Error('Not implemented');
}

/**
 * Calcula el score de coincidencia entre query y FAQ
 */
export function calculateMatchScore(query: string, faq: FAQItem): number {
  // TODO: Implementar
  throw new Error('Not implemented');
}

/**
 * Busca la mejor coincidencia de FAQ para una consulta
 */
export function findBestMatch(query: string, faqs: FAQItem[]): FAQMatchResult {
  // TODO: Implementar
  throw new Error('Not implemented');
}

/**
 * Obtiene FAQs por categoría
 */
export function getFAQsByCategory(category: string, faqs: FAQItem[]): FAQItem[] {
  // TODO: Implementar
  throw new Error('Not implemented');
}
