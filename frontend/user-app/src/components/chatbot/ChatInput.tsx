/**
 * ChatInput Component
 * Campo de entrada para enviar mensajes
 * 
 * Fase 2 - Paso 2: UI Components - FASE GREEN
 */

import { useState, type KeyboardEvent } from 'react';

type ChatInputProps = Readonly<{
  onSend: (message: string) => void;
  disabled?: boolean;
}>;

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue) {
      onSend(trimmedValue);
      setInputValue('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex gap-2 p-3 border-t border-gray-200 bg-white">
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Escribe tu pregunta..."
        disabled={disabled}
        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      />
      <button
        onClick={handleSend}
        disabled={disabled}
        aria-label="Enviar mensaje"
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        Enviar
      </button>
    </div>
  );
}
