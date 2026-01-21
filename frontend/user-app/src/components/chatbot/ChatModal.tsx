/**
 * ChatModal Component
 * Panel principal del chatbot
 * 
 * Fase 2 - Paso 2: UI Components - FASE GREEN
 */

import type { ChatMessage as ChatMessageType } from '../../types/chatbot.types';
import ChatMessageComponent from './ChatMessage';
import ChatInput from './ChatInput';

type ChatModalProps = Readonly<{
  isOpen: boolean;
  onClose: () => void;
  messages: ChatMessageType[];
  onSendMessage: (message: string) => void;
  isTyping?: boolean;
}>;

export default function ChatModal({ 
  isOpen, 
  onClose, 
  messages, 
  onSendMessage, 
  isTyping = false 
}: ChatModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-xl shadow-2xl flex flex-col z-50 border border-gray-200">
      {/* Header */}
      <div className="bg-blue-600 text-white px-4 py-3 rounded-t-xl flex justify-between items-center">
        <div>
          <h2 className="font-semibold">🤖 Soporte FinTech</h2>
          <p className="text-xs text-blue-100">Bot automático disponible 24/7</p>
        </div>
        <button
          onClick={onClose}
          aria-label="Cerrar chat"
          className="text-white hover:bg-blue-700 rounded-full p-1 transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map((msg) => (
          <ChatMessageComponent key={msg.id} message={msg} />
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start mb-3">
            <div className="bg-gray-200 rounded-lg px-4 py-2 text-gray-600 text-sm">
              <span className="animate-pulse">Escribiendo...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={onSendMessage} />
    </div>
  );
}
