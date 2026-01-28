import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Moon, Sun } from 'lucide-react';
import { Card } from './components/ui/Card';
import { TransactionForm } from './components/TransactionForm';
import { ResultDisplay } from './components/ResultDisplay';
import { TransactionsPage } from './pages/TransactionsPage';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { validateTransaction, getUserTransactions } from './services/api';
import { useUser } from './context/UserContext';
import { useTheme } from './context/ThemeContext';
import type { TransactionRequest, TransactionResponse, TransactionStatus } from './types/transaction';

type Page = 'home' | 'new-transaction' | 'my-transactions';
type AuthView = 'login' | 'register' | 'verify-email';
type NotificationType = 'success' | 'warning' | 'info';

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: NotificationType;
  read: boolean;
  meta?: {
    amount?: number;
    txId?: string;
  };
}

// Helper functions para reducir complejidad
const getTransactionTypeLabel = (type: string | undefined): string => {
  if (type === 'transfer') return 'transferencia';
  if (type === 'deposit') return 'depósito';
  return 'pago';
};

function App() {
  const { userId, isAuthenticated, login, logout } = useUser();
  const { darkMode, toggleDarkMode } = useTheme();
  const [authView, setAuthView] = useState<AuthView>('login');
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [status, setStatus] = useState<TransactionStatus>('idle');
  const [result, setResult] = useState<TransactionResponse | null>(null);
  const [currentTransaction, setCurrentTransaction] = useState<TransactionRequest | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [homeRefreshKey, setHomeRefreshKey] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(() => {
    try {
      const raw = localStorage.getItem('notifications');
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  });
  const [lastCheckedTransactions, setLastCheckedTransactions] = useState<Set<string>>(() => {
    try {
      const raw = localStorage.getItem('lastCheckedTransactions');
      const arr = raw ? JSON.parse(raw) : [];
      return new Set(arr);
    } catch (e) {
      return new Set();
    }
  });

  const addNotification = (title: string, message: string, type: NotificationType, meta?: { amount?: number; txId?: string }) => {
    const newNotification: Notification = {
      id: Date.now().toString(),
      title,
      message,
      time: new Date().toLocaleString(),
      type,
      read: false,
      meta
    };
    setNotifications(prev => {
      const next = [newNotification, ...prev];
      try { localStorage.setItem('notifications', JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => {
      const next = prev.filter(n => n.id !== id);
      try { localStorage.setItem('notifications', JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  const markAllRead = () => {
    setNotifications(prev => {
      const next = prev.map(n => ({ ...n, read: true }));
      try { localStorage.setItem('notifications', JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  // Polling para verificar actualizaciones de transacciones del admin
  useEffect(() => {
    // Guard: Solo ejecutar si está autenticado y tenemos userId
    if (!userId || !isAuthenticated) return;

    const checkForUpdates = async () => {
      try {
        const transactions = await getUserTransactions(userId);
        
        // Verificar transacciones que fueron revisadas por el admin
        transactions.forEach((transaction: any) => {
          const txId = transaction.transactionId || transaction.id;

          // Si la transacción fue revisada y no la hemos notificado antes
          if (transaction.reviewedBy && !lastCheckedTransactions.has(txId)) {
            // Construir representación del monto para buscar notificaciones previas
            const amountStr = `$${Math.abs(transaction.amount).toLocaleString()}`;

            // Eliminar notificaciones previas que indiquen "requiere autenticación" para la misma cantidad
            setNotifications(prev => {
              const filtered = prev.filter(n => {
                const isPendingTitle = n.title && n.title.includes('Transacción requiere autenticación');
                if (!isPendingTitle) return true;
                // Si la notificación tiene meta.amount, usarla para comparar
                if (n.meta && typeof n.meta.amount === 'number') {
                  return n.meta.amount !== Math.abs(transaction.amount);
                }
                // Fallback a comparar texto (por compatibilidad con notificaciones antiguas)
                return !(n.message && n.message.includes(amountStr));
              });
              try { localStorage.setItem('notifications', JSON.stringify(filtered)); } catch (e) {}
              return filtered;
            });

            if (transaction.status === 'APPROVED') {
              // usar id ligado a la transacción para evitar duplicados
              setNotifications(prev => {
                const newNotif: Notification = {
                  id: `tx-${txId}`,
                  title: 'Transacción aprobada por el banco',
                  message: `Tu transacción de ${amountStr} fue aprobada por el analista.`,
                  time: new Date().toLocaleString(),
                  type: 'success',
                  read: false
                };
                const next = [newNotif, ...prev];
                try { localStorage.setItem('notifications', JSON.stringify(next)); } catch (e) {}
                return next;
              });
            } else if (transaction.status === 'REJECTED') {
              setNotifications(prev => {
                const newNotif: Notification = {
                  id: `tx-${txId}`,
                  title: 'Transacción rechazada',
                  message: `Tu transacción de ${amountStr} fue rechazada por el banco.`,
                  time: new Date().toLocaleString(),
                  type: 'warning',
                  read: false
                };
                const next = [newNotif, ...prev];
                try { localStorage.setItem('notifications', JSON.stringify(next)); } catch (e) {}
                return next;
              });
            }

            // Marcar como ya notificada
            setLastCheckedTransactions(prev => {
              const next = new Set([...prev, txId]);
              try { localStorage.setItem('lastCheckedTransactions', JSON.stringify(Array.from(next))); } catch (e) {}
              return next;
            });
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
  }, [userId, lastCheckedTransactions, isAuthenticated]);

  const handleSubmit = async (transaction: TransactionRequest) => {
    setStatus('loading');
    setError(null);
    setCurrentTransaction(transaction);

    try {
      const response = await validateTransaction(transaction);
      console.debug('validateTransaction response', response);
      setResult(response);
      setStatus('success');
      
      const amount = Math.abs(transaction.amount).toLocaleString();
      const transactionTypeLabel = getTransactionTypeLabel(transaction.transactionType);
      
      // Agregar notificación según el resultado
      if (response.status === 'APPROVED') {
        addNotification(
          'Transacción aprobada',
          `Tu ${transactionTypeLabel} de $${amount} fue procesada exitosamente.`,
          'success'
        );
      } else if (response.status === 'SUSPICIOUS') {
        addNotification(
          'Transacción requiere autenticación',
          `Tu transacción de $${Math.abs(transaction.amount).toLocaleString()} fue marcada como sospechosa. Por favor, confirma tu identidad.`,
          'warning',
          { amount: Math.abs(transaction.amount) }
        );
      } else if (response.status === 'REJECTED') {
        addNotification(
          'Transacción rechazada',
          `Tu transacción de $${Math.abs(transaction.amount).toLocaleString()} fue rechazada por el banco.`,
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

  // Lógica condicional de autenticación
  if (!isAuthenticated) {
    if (authView === 'login') {
      return (
        <LoginPage
          onLogin={async (userId, password) => {
            try {
              const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId, password }),
              });

              const data = await response.json();

              if (!response.ok) {
                throw new Error(data.detail || 'Error al iniciar sesión');
              }

              login(userId, data.access_token, data.email, data.full_name);
            } catch (err: any) {
              throw err;
            }
          }}
          onSwitchToRegister={() => setAuthView('register')}
        />
      );
    } else if (authView === 'register') {
      return (
        <RegisterPage
          onRegisterSuccess={(email: string) => {
            setPendingVerificationEmail(email);
            setAuthView('verify-email');
          }}
          onSwitchToLogin={() => setAuthView('login')}
        />
      );
    } else if (authView === 'verify-email' && pendingVerificationEmail) {
      return (
        <VerifyEmailPage
          email={pendingVerificationEmail}
          onVerifySuccess={() => {
            setPendingVerificationEmail(null);
            setAuthView('login');
          }}
          onBackToLogin={() => {
            setPendingVerificationEmail(null);
            setAuthView('login');
          }}
        />
      );
    }
    
    // Fallback si algo sale mal
    return (
      <LoginPage
        onLogin={async (userId, password) => {
          try {
            const response = await fetch('http://localhost:8000/api/v1/auth/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ user_id: userId, password }),
            });

            const data = await response.json();

            if (!response.ok) {
              throw new Error(data.detail || 'Error al iniciar sesión');
            }

            login(userId, data.access_token, data.email, data.full_name);
          } catch (err: any) {
            throw err;
          }
        }}
        onSwitchToRegister={() => setAuthView('register')}
      />
    );
  }

  // Componente reutilizable de navegación
  const NavBar = () => (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <img src="assets/logo-full.svg" alt="FinTech Bank" className="h-24" />
          <button className="ml-2 px-4 py-2 bg-gray-100 border border-gray-200 rounded-full text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-200 transition-colors">
            {userId}
          </button>
        </div>
        <div className="flex gap-4 items-center">
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
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-gray-200 dark:border-slate-700 z-50">
                <div className="p-4 border-b border-gray-200 dark:border-slate-700">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Notificaciones</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 dark:text-slate-400">
                      <Bell className="w-12 h-12 mx-auto mb-2 opacity-30" />
                      <p className="text-sm">No tienes notificaciones</p>
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <div key={notification.id} className={`p-4 border-b border-gray-100 dark:border-slate-700 last:border-b-0 ${notification.read ? 'bg-gray-50 dark:bg-slate-700/50' : 'dark:bg-slate-800'}`}>
                        <div className="flex items-start gap-3">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            notification.type === 'success' ? 'bg-green-500' :
                            notification.type === 'warning' ? 'bg-yellow-500' :
                            'bg-blue-500'
                          }`}></div>
                          <div className="flex-1">
                            <div className="flex justify-between items-start">
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">{notification.title}</p>
                                <p className="text-xs text-gray-600 dark:text-slate-400 mt-1">{notification.message}</p>
                                <p className="text-xs text-gray-400 dark:text-slate-500 mt-1">{notification.time}</p>
                              </div>
                              <div className="ml-4 flex-shrink-0">
                                <button onClick={() => removeNotification(notification.id)} className="text-xs text-gray-400 dark:text-slate-500 hover:text-red-500 dark:hover:text-red-400">Eliminar</button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <div className="p-3 border-t border-gray-200 dark:border-slate-700 text-center">
                  <div className="flex items-center justify-between">
                    <button onClick={markAllRead} className="text-sm text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 font-medium">Marcar todas leídas</button>
                    <button 
                      onClick={() => setShowNotifications(false)}
                      className="text-sm text-user-primary dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
                    >
                      Cerrar
                    </button>
                  </div>
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
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg text-gray-600 hover:text-user-primary hover:bg-gray-50 transition-colors"
              title={darkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => logout()}
              className="px-4 py-2 rounded-lg font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    </nav>
  );

  const renderPage = (): JSX.Element => {
    if (currentPage === 'home') {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
          <NavBar />
          <HomePage key={homeRefreshKey} onNavigate={setCurrentPage} />
        </div>
      );
    }

    if (currentPage === 'my-transactions') {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
          <NavBar />
          <TransactionsPage />
        </div>
      );
    }

    return renderTransactionPage();
  };

  const renderTransactionPage = (): JSX.Element => {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800">
        <NavBar />
        
        <div className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md mx-auto">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-8"
            >
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Nueva Transferencia
              </h1>
              <p className="text-gray-600 dark:text-slate-400">
                Completa los datos para realizar una transacción segura
              </p>
            </motion.div>

            {/* Content */}
            <AnimatePresence mode="wait">
              {renderTransactionContent()}
            </AnimatePresence>

            {/* Footer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-8 text-center text-sm text-gray-500 dark:text-slate-400"
            >
              Powered by FinTech Bank v1.0
            </motion.div>
          </div>
        </div>
      </div>
    );
  };

  const renderTransactionContent = (): JSX.Element | null => {
    if (status === 'idle' || status === 'loading') {
      return (
        <motion.div
          key="form"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
        >
          <Card className="dark:bg-slate-800 dark:border-slate-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Realizar una Transferencia
            </h2>
            <TransactionForm onSubmit={handleSubmit} isLoading={status === 'loading'} />
          </Card>
        </motion.div>
      );
    }
    
    if (status === 'success' && result && currentTransaction) {
      return (
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
      );
    }
    
    if (status === 'error') {
      return (
        <motion.div
          key="error"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
        >
          <Card className="dark:bg-slate-800 dark:border-slate-700">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <span className="text-4xl text-red-600 dark:text-red-400">⚠</span>
              </div>
              <h2 className="text-xl font-bold text-red-700 dark:text-red-400">Error</h2>
              <p className="text-gray-600 dark:text-slate-400">{error}</p>
              <button
                onClick={handleNewTransaction}
                className="w-full py-3 bg-user-primary text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Intentar de Nuevo
              </button>
            </div>
          </Card>
        </motion.div>
      );
    }
    
    return null;
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      {renderPage()}
    </div>
  );
}

export default App;

