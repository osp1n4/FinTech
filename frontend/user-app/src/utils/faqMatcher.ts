/**
 * FAQ Matcher - Lógica de búsqueda por keywords
 * Fase 2 - Paso 1: Data Layer
 * 
 * Implementación GREEN - Código mínimo para pasar tests
 */

import type { FAQItem, FAQMatchResult } from '../types/chatbot.types';

/** Umbral mínimo para considerar una coincidencia válida */
const MATCH_THRESHOLD = 0.2;

/**
 * Normaliza texto para comparación (minúsculas, sin acentos)
 * @param text - Texto a normalizar
 * @returns Texto normalizado
 */
export function normalizeText(text: string): string {
  if (!text) return '';
  
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Elimina acentos
    .replace(/[¿?¡!]/g, '') // Elimina signos de puntuación especiales
    .trim();
}

/**
 * Calcula el score de coincidencia entre query y FAQ
 * @param query - Consulta del usuario
 * @param faq - FAQ a comparar
 * @returns Score entre 0 y 1
 */
export function calculateMatchScore(query: string, faq: FAQItem): number {
  const normalizedQuery = normalizeText(query);
  
  if (!normalizedQuery) return 0;
  
  const queryWords = normalizedQuery.split(/\s+/);
  let matchCount = 0;
  
  for (const word of queryWords) {
    for (const keyword of faq.keywords) {
      const normalizedKeyword = normalizeText(keyword);
      if (word.includes(normalizedKeyword) || normalizedKeyword.includes(word)) {
        matchCount++;
        break;
      }
    }
  }
  
  // Score basado en proporción de palabras que coinciden con keywords
  const score = matchCount / Math.max(queryWords.length, faq.keywords.length);
  return Math.min(score, 1);
}

/**
 * Busca la mejor coincidencia de FAQ para una consulta
 * @param query - Consulta del usuario
 * @param faqs - Lista de FAQs disponibles
 * @returns Resultado con la mejor coincidencia
 */
export function findBestMatch(query: string, faqs: FAQItem[]): FAQMatchResult {
  if (!query || !faqs.length) {
    return { found: false, faq: null, score: 0 };
  }
  
  let bestMatch: FAQItem | null = null;
  let bestScore = 0;
  
  for (const faq of faqs) {
    const score = calculateMatchScore(query, faq);
    if (score > bestScore) {
      bestScore = score;
      bestMatch = faq;
    }
  }
  
  // Solo retornar coincidencia si supera el umbral
  if (bestScore >= MATCH_THRESHOLD && bestMatch) {
    return { found: true, faq: bestMatch, score: bestScore };
  }
  
  return { found: false, faq: null, score: bestScore };
}

/**
 * Obtiene FAQs por categoría
 * @param category - Categoría a filtrar
 * @param faqs - Lista de FAQs
 * @returns FAQs de la categoría especificada
 */
export function getFAQsByCategory(category: string, faqs: FAQItem[]): FAQItem[] {
  return faqs.filter(faq => faq.category === category);
}
