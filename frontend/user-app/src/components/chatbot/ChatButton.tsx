/**
 * ChatButton Component
 * Botón flotante para abrir el chatbot
 * 
 * Fase 2 - Paso 2: UI Components - FASE GREEN
 */

type ChatButtonProps = Readonly<{
  onClick: () => void;
}>;

export default function ChatButton({ onClick }: ChatButtonProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 flex items-center gap-2 z-50"
      aria-label="Abrir chat de soporte"
    >
      <span className="text-xl">💬</span>
      <span className="font-medium">Soporte</span>
    </button>
  );
}
