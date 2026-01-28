/**
 * Tipos para el Chatbot de Soporte FAQ
 * Fase 2 - Paso 1: Data Layer
 */

/** Categorías de FAQs disponibles */
export type FAQCategory = 
  | 'cuenta-acceso'
  | 'transacciones'
  | 'seguridad-fraude'
  | 'problemas-tecnicos'
  | 'soporte';

/** Estructura de una pregunta frecuente */
export interface FAQItem {
  id: string;
  category: FAQCategory;
  question: string;
  answer: string;
  keywords: string[];
}

/** Resultado de búsqueda de FAQ */
export interface FAQMatchResult {
  found: boolean;
  faq: FAQItem | null;
  score: number;
}

/** Mensaje del chat */
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

/** Estado del chatbot */
export interface ChatbotState {
  isOpen: boolean;
  messages: ChatMessage[];
  isTyping: boolean;
}
