/**
 * FAQList Component
 * Lista de preguntas frecuentes sugeridas
 * 
 * Fase 2 - Paso 2: UI Components - FASE GREEN
 */

import type { FAQItem } from '../../types/chatbot.types';
import type { KeyboardEvent } from 'react';

type FAQListProps = Readonly<{
  faqs: FAQItem[];
  onSelect: (faq: FAQItem) => void;
}>;

export default function FAQList({ faqs, onSelect }: FAQListProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLButtonElement>, faq: FAQItem) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(faq);
    }
  };

  if (faqs.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No hay preguntas disponibles.</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        📋 Preguntas Frecuentes
      </h3>
      <div className="space-y-2">
        {faqs.map((faq) => (
          <button
            key={faq.id}
            onClick={() => onSelect(faq)}
            onKeyDown={(e) => handleKeyDown(e, faq)}
            className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm text-blue-700 transition-colors border border-blue-200"
          >
            {faq.question}
          </button>
        ))}
      </div>
    </div>
  );
}
