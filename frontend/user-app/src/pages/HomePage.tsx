import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { CreditCard, DollarSign, Activity } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useTheme } from '../context/ThemeContext';
import { getUserTransactions } from '../services/api';
import { useState, useEffect } from 'react';
import { ChatButton, ChatModal } from '../components/chatbot';
import { useChatbot } from '../hooks/useChatbot';

interface HomePageProps {
  readonly onNavigate: (page: 'new-transaction' | 'my-transactions') => void;
}

interface Transaction {
  id?: string;
  transactionId?: string;
  amount: number;
  description?: string;
  timestamp?: string;
  date?: string;
  createdAt?: string;
  status: string;
  transactionType?: string;
}

export function HomePage({ onNavigate }: HomePageProps) {
  const { userId } = useUser();
  const { darkMode } = useTheme();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [allTransactions, setAllTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Chatbot hook
  const chatbot = useChatbot();
  
  const cardNumber = "**** **** **** 4521";
  
  // Balance inicial para cada usuario (guardado en localStorage)
  const INITIAL_BALANCE = 50000;
  
  // Calcular balance actual basado en transacciones aprobadas
  const calculateBalance = (allTxs: Transaction[]) => {
    const initialBalance = INITIAL_BALANCE;
    
    // Sumar/restar solo transacciones APPROVED
    const approvedTransactions = allTxs.filter(tx => tx.status === 'APPROVED');
    const totalMovements = approvedTransactions.reduce((sum, tx) => {
      return sum + (tx.amount || 0);
    }, 0);
    
    return initialBalance + totalMovements;
  };

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        setLoading(true);
        const data = await getUserTransactions(userId);
        // Ordenar por timestamp descendente para asegurar recientes primero
        const sorted = Array.isArray(data)
          ? data.slice().sort((a: any, b: any) => new Date(b.timestamp || b.date || 0).getTime() - new Date(a.timestamp || a.date || 0).getTime())
          : [];

        // Guardar todas las transacciones para calcular balance
        setAllTransactions(sorted);

        // Mostrar solo las últimas 3 en actividad reciente (incluye todos los estados)
        setTransactions(sorted.slice(0, 3));
      } catch (error) {
        console.error('Error loading transactions:', error);
        // Si hay error, mostrar transacciones de ejemplo
        const exampleTxs = [
          { amount: -150, description: 'Transferencia a Juan Pérez', timestamp: 'Hoy, 10:30 AM', status: 'APPROVED', transactionType: 'transfer' },
          { amount: -85.5, description: 'Pago servicio público', timestamp: 'Ayer, 3:15 PM', status: 'APPROVED', transactionType: 'payment' },
          { amount: 2500, description: 'Depósito nómina', timestamp: '2 días', status: 'APPROVED', transactionType: 'deposit' }
        ];
        setAllTransactions(exampleTxs);
        setTransactions(exampleTxs);
      } finally {
        setLoading(false);
      }
    };

    loadTransactions();
  }, [userId]);

  const userBalance = calculateBalance(allTransactions);
  const recentTransactions = transactions.length;

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800 transition-colors">
        <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
          {/* Saludo personalizado */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">¡Hola de nuevo! 👋</h2>
            <p className="text-gray-600 dark:text-slate-400 mt-1">Aquí está un resumen de tu cuenta</p>
          </motion.div>

      {/* Tarjeta de saldo única */}
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-gradient-to-br from-user-primary to-indigo-700 text-white p-8 hover:shadow-2xl transition-shadow">
            <div className="flex justify-between items-start mb-8">
              <div>
                <p className="text-indigo-200 text-sm font-medium">Cuenta Corriente</p>
                <h3 className="text-5xl font-bold mt-2">
                  ${userBalance.toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                </h3>
              </div>
              <div className="bg-white/20 p-3 rounded-full">
                <DollarSign className="w-6 h-6" />
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-indigo-200 text-sm">{cardNumber}</span>
              <CreditCard className="w-8 h-8 text-indigo-200" />
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Acciones rápidas */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <button
          onClick={() => onNavigate('new-transaction')}
          className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm hover:shadow-md transition-all border border-gray-200 dark:border-slate-700 text-left group"
        >
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white group-hover:text-user-primary dark:group-hover:text-indigo-400 transition-colors">
                Transferir Dinero
              </h4>
              <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">Envía dinero de forma segura</p>
            </div>
            <div className="bg-user-primary/10 dark:bg-indigo-900/30 p-3 rounded-full group-hover:bg-user-primary dark:group-hover:bg-indigo-600 group-hover:text-white transition-colors">
              <DollarSign className="w-5 h-5 text-user-primary dark:text-indigo-400 group-hover:text-white" />
            </div>
          </div>
        </button>

        <button
          onClick={() => onNavigate('my-transactions')}
          className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm hover:shadow-md transition-all border border-gray-200 dark:border-slate-700 text-left group"
        >
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                Ver Movimientos
              </h4>
              <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">{recentTransactions} transacciones este mes</p>
            </div>
            <div className="bg-emerald-100 dark:bg-emerald-900/30 p-3 rounded-full group-hover:bg-emerald-500 dark:group-hover:bg-emerald-600 transition-colors">
              <Activity className="w-5 h-5 text-emerald-600 dark:text-emerald-400 group-hover:text-white" />
            </div>
          </div>
        </button>

        <button className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm hover:shadow-md transition-all border border-gray-200 dark:border-slate-700 text-left">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white">Protección Activa</h4>
              <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">Sistema antifraude monitoreando</p>
            </div>
            <div className="bg-green-500 p-3 rounded-full">
              <span className="text-white text-xs font-bold">✓</span>
            </div>
          </div>
        </button>
      </motion.div>

      {/* Resumen de actividad */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="p-6 dark:bg-slate-800 dark:border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">Actividad Reciente</h3>
            {loading && <span className="text-xs text-gray-500 dark:text-slate-400">Cargando...</span>}
          </div>
          <div className="space-y-3">
              {transactions.length === 0 && !loading ? (
              <p className="text-center text-gray-500 dark:text-slate-400 py-8">No hay transacciones recientes</p>
            ) : (
              transactions.map((tx, i) => {
                // Formatear la fecha recibida desde el servidor (se envía en UTC)
                const rawDate = tx.timestamp || tx.createdAt || tx.date || null;
                const displayDate = rawDate ? new Date(rawDate).toLocaleString('es-ES', {
                  day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                }) : 'Fecha desconocida';
                
                // Mejorar descripción mostrando el tipo si no hay descripción
                let displayDesc = tx.description || 'Transacción sin descripción';
                if (!tx.description && tx.transactionType) {
                  const typeLabels: Record<string, string> = {
                    'transfer': 'Transferencia',
                    'payment': 'Pago de servicio',
                    'recharge': 'Recarga de celular',
                    'deposit': 'Depósito'
                  };
                  displayDesc = typeLabels[tx.transactionType] || 'Transacción';
                }
                
                const amount = typeof tx.amount === 'number' ? tx.amount : 0;
                
                // Determinar etiqueta de estado
                const statusLabel = tx.status === 'APPROVED' ? 'Aprobada' : tx.status === 'REJECTED' ? 'Rechazada' : tx.status === 'SUSPICIOUS' ? 'Sospechosa' : tx.status;
                const statusClass = tx.status === 'APPROVED' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : tx.status === 'REJECTED' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';

                return (
                  <div key={tx.id || tx.transactionId || i} className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-slate-700 last:border-0">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        amount > 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-slate-700'
                      }`}>
                        <DollarSign className={`w-5 h-5 ${amount > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-slate-400'}`} />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{displayDesc}</p>
                        <p className="text-xs text-gray-500 dark:text-slate-400">{displayDate}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold ${amount > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-white'}`}>
                        {amount > 0 ? '+' : ''}${Math.abs(amount).toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                      </p>
                      <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${statusClass}`}>
                        {statusLabel}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
          <button
            onClick={() => onNavigate('my-transactions')}
            className="w-full mt-4 py-2 text-user-primary dark:text-indigo-400 hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg transition-colors font-medium"
          >
            Ver todas las transacciones →
          </button>
        </Card>
      </motion.div>
      </div>
    
      {/* Chatbot de Soporte */}
      <ChatButton onClick={chatbot.openChat} />
      <ChatModal
        isOpen={chatbot.isOpen}
        onClose={chatbot.closeChat}
        messages={chatbot.messages}
        isTyping={chatbot.isTyping}
        onSendMessage={chatbot.sendMessage}
        onSelectFAQ={chatbot.selectFAQ}
      />
      </div>
    </div>
  );
}
