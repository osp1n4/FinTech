/**
 * ChatMessage Component
 * Burbuja de mensaje del chat
 * 
 * Fase 2 - Paso 2: UI Components - FASE GREEN
 */

import type { ChatMessage as ChatMessageType } from '../../types/chatbot.types';

type ChatMessageProps = Readonly<{
  message: ChatMessageType;
}>;

/**
 * Formatea la hora del mensaje
 */
function formatTime(date: Date): string {
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isBot = message.sender === 'bot';
  
  return (
    <div 
      data-testid="chat-message"
      className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-3`}
    >
      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
        isBot 
          ? 'bg-gray-100 text-gray-800' 
          : 'bg-blue-600 text-white'
      }`}>
        {isBot && (
          <span className="text-xs font-medium text-blue-600 block mb-1">
            🤖 Bot
          </span>
        )}
        <p className="text-sm">{message.text}</p>
        <span className={`text-xs block mt-1 ${isBot ? 'text-gray-500' : 'text-blue-100'}`}>
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
