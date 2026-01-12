import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from './components/ui/Card';
import { TransactionForm } from './components/TransactionForm';
import { ResultDisplay } from './components/ResultDisplay';
import { TransactionsPage } from './pages/TransactionsPage';
import { HomePage } from './pages/HomePage';
import { UserSelector } from './components/UserSelector';
import { validateTransaction, getUserTransactions } from './services/api';
import { Bell } from 'lucide-react';
import { useUser } from './context/UserContext';
import type { TransactionRequest, TransactionResponse, TransactionStatus } from './types/transaction';

type Page = 'home' | 'new-transaction' | 'my-transactions';

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: 'success' | 'warning' | 'info';
  read: boolean;
}

function App() {
  const { userId } = useUser();
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [status, setStatus] = useState<TransactionStatus>('idle');
  const [result, setResult] = useState<TransactionResponse | null>(null);
  const [currentTransaction, setCurrentTransaction] = useState<TransactionRequest | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [homeRefreshKey, setHomeRefreshKey] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [lastCheckedTransactions, setLastCheckedTransactions] = useState<Set<string>>(new Set());

  // Polling para verificar actualizaciones de transacciones del admin
  useEffect(() => {
    if (!userId) return;

    const checkForUpdates = async () => {
      try {
        const transactions = await getUserTransactions(userId);
        
        // Verificar transacciones que fueron revisadas por el admin
        transactions.forEach((transaction: any) => {
          const txId = transaction.transactionId || transaction.id;
          
          // Si la transacción fue revisada y no la hemos notificado antes
          if (transaction.reviewedBy && !lastCheckedTransactions.has(txId)) {
            if (transaction.status === 'APPROVED') {
              addNotification(
                'Transacción aprobada por el banco',
                `Tu transacción de $${Math.abs(transaction.amount).toLocaleString()} fue aprobada por el analista.`,
                'success'
              );
            } else if (transaction.status === 'REJECTED') {
              addNotification(
                'Transacción rechazada',
                `Tu transacción de $${Math.abs(transaction.amount).toLocaleString()} fue rechazada por el banco.`,
                'warning'
              );
            }
            
            // Marcar como ya notificada
            setLastCheckedTransactions(prev => new Set([...prev, txId]));
            // Refrescar la página de inicio para actualizar el balance
            setHomeRefreshKey(prev => prev + 1);
          }
        });
      } catch (error) {
        console.error('Error checking for transaction updates:', error);
      }
    };

    // Verificar inmediatamente
    checkForUpdates();
    
    // Verificar cada 10 segundos
    const interval = setInterval(checkForUpdates, 10000);

    return () => clearInterval(interval);
  }, [userId, lastCheckedTransactions]);

  const addNotification = (title: string, message: string, type: 'success' | 'warning' | 'info') => {
    const newNotification: Notification = {
      id: Date.now().toString(),
      title,
      message,
      time: 'Justo ahora',
      type,
      read: false
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const handleSubmit = async (transaction: TransactionRequest) => {
    setStatus('loading');
    setError(null);
    setCurrentTransaction(transaction);

    try {
      const response = await validateTransaction(transaction);
      setResult(response);
      setStatus('success');
      
      // Agregar notificación según el resultado
      if (response.status === 'APPROVED') {
        addNotification(
          'Transacción aprobada',
          `Tu ${transaction.transactionType === 'transfer' ? 'transferencia' : transaction.transactionType === 'deposit' ? 'depósito' : 'pago'} de $${Math.abs(transaction.amount).toLocaleString()} fue procesada exitosamente.`,
          'success'
        );
      } else if (response.status === 'SUSPICIOUS' || response.status === 'REJECTED') {
        addNotification(
          'Transacción requiere autenticación',
          `Tu transacción de $${Math.abs(transaction.amount).toLocaleString()} fue marcada como sospechosa. Por favor, confirma tu identidad.`,
          'warning'
        );
      }
    } catch (err) {
      setError('Ocurrió un error al procesar tu transacción. Por favor, intenta de nuevo.');
      setStatus('error');
      console.error('Error:', err);
    }
  };

  const handleNewTransaction = () => {
    setStatus('idle');
    setResult(null);
    setCurrentTransaction(null);
    setError(null);
    // Volver a home y forzar recarga
    setCurrentPage('home');
    setHomeRefreshKey(prev => prev + 1);
  };

  // Componente reutilizable de navegación
  const NavBar = () => (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-user-primary to-indigo-700 bg-clip-text text-transparent">
          FinTech Bank
        </h1>
        <div className="flex gap-4 items-center">
          <UserSelector />
          {/* Campanita de notificaciones */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-600 hover:text-user-primary transition-colors" 
              title="Notificaciones"
            >
              <Bell className="w-6 h-6" />
              {/* Badge de notificaciones */}
              {notifications.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              )}
            </button>
            
            {/* Dropdown de notificaciones */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">Notificaciones</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                      <Bell className="w-12 h-12 mx-auto mb-2 opacity-30" />
                      <p className="text-sm">No tienes notificaciones</p>
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <div key={notification.id} className="p-4 hover:bg-gray-50 border-b border-gray-100 last:border-b-0">
                        <div className="flex items-start gap-3">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            notification.type === 'success' ? 'bg-green-500' :
                            notification.type === 'warning' ? 'bg-yellow-500' :
                            'bg-blue-500'
                          }`}></div>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                            <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
                            <p className="text-xs text-gray-400 mt-1">{notification.time}</p>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <div className="p-3 border-t border-gray-200 text-center">
                  <button 
                    onClick={() => setShowNotifications(false)}
                    className="text-sm text-user-primary hover:text-indigo-700 font-medium"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage('home')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentPage === 'home'
                  ? 'bg-user-primary text-white'
                  : 'text-gray-600 hover:text-user-primary hover:bg-gray-50'
              }`}
            >
              Inicio
            </button>
            <button
              onClick={() => setCurrentPage('new-transaction')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentPage === 'new-transaction'
                  ? 'bg-user-primary text-white'
                  : 'text-gray-600 hover:text-user-primary hover:bg-gray-50'
              }`}
            >
              Transferir
            </button>
            <button
              onClick={() => setCurrentPage('my-transactions')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                currentPage === 'my-transactions'
                  ? 'bg-user-primary text-white'
                  : 'text-gray-600 hover:text-user-primary hover:bg-gray-50'
              }`}
            >
              Movimientos
            </button>
          </div>
        </div>
      </div>
    </nav>
  );

  // Página de inicio (Dashboard bancario)
  if (currentPage === 'home') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <NavBar />
        <HomePage key={homeRefreshKey} onNavigate={setCurrentPage} />
      </div>
    );
  }

  // Si estamos en la página de transacciones, mostrarla
  if (currentPage === 'my-transactions') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <NavBar />
        <TransactionsPage />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <NavBar />
      
      <div className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Nueva Transferencia
            </h1>
            <p className="text-gray-600">
              Completa los datos para realizar una transacción segura
            </p>
          </motion.div>

          {/* Content */}
          <AnimatePresence mode="wait">
          {status === 'idle' || status === 'loading' ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <Card>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Realizar una Transferencia
                </h2>
                <TransactionForm onSubmit={handleSubmit} isLoading={status === 'loading'} />
              </Card>
            </motion.div>
          ) : status === 'success' && result && currentTransaction ? (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <ResultDisplay
                result={result}
                transaction={currentTransaction}
                onNewTransaction={handleNewTransaction}
              />
            </motion.div>
          ) : status === 'error' ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <Card>
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-red-100 flex items-center justify-center">
                    <span className="text-4xl text-red-600">⚠</span>
                  </div>
                  <h2 className="text-xl font-bold text-red-700">Error</h2>
                  <p className="text-gray-600">{error}</p>
                  <button
                    onClick={handleNewTransaction}
                    className="w-full py-3 bg-user-primary text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Intentar de Nuevo
                  </button>
                </div>
              </Card>
            </motion.div>
          ) : null}
        </AnimatePresence>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 text-center text-sm text-gray-500"
        >
          Powered by FinTech Bank v1.0
        </motion.div>
        </div>
      </div>
    </div>
  );
}

export default App;
