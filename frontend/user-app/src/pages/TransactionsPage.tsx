import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { getUserTransactions, authenticateTransaction } from '../services/api';
import { useUser } from '../context/UserContext';
import { useTheme } from '../context/ThemeContext';
import { translateViolation } from '../utils/translations';
import { useToast } from '../components/ToastContainer';

interface Transaction {
  id: string;
  transactionId?: string;
  amount: number;
  location: string;
  timestamp: string;
  status: string;
  riskScore: string;
  violations: string[];
  needsAuthentication: boolean;
  userAuthenticated: boolean | null;
  reviewedBy: string | null;
  reviewedAt: string | null;
}

export function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authenticating, setAuthenticating] = useState<string | null>(null);

  // Obtener userId del contexto
  const { userId } = useUser();
  const { darkMode } = useTheme();

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await getUserTransactions(userId);
      setTransactions(data);
      setError(null);
    } catch (err) {
      setError('Error al cargar transacciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [userId]); // Recargar cuando cambie el userId

  const { add } = useToast();

  const handleAuthenticate = async (transactionId: string, confirmed: boolean) => {
    try {
      setAuthenticating(transactionId);
      await authenticateTransaction(transactionId, confirmed);
      await loadTransactions(); // Recargar lista
      add(confirmed 
        ? 'Confirmaste que fuiste tú. Un analista revisará pronto.' 
        : 'Gracias por alertarnos. Bloquearemos esta transacción.',
        confirmed ? 'success' : 'warning',
        confirmed ? 'Autenticación confirmada' : 'Transacción reportada'
      );
    } catch (err) {
      add('Error al autenticar transacción', 'error', 'Error');
      console.error(err);
    } finally {
      setAuthenticating(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 rounded-full text-sm font-medium">✓ Aprobada</span>;
      case 'REJECTED':
        return <span className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 rounded-full text-sm font-medium">✗ Rechazada</span>;
      case 'PENDING_REVIEW':
        return <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 rounded-full text-sm font-medium">⏳ Revisión</span>;
      default:
        return <span className="px-3 py-1 bg-gray-100 dark:bg-slate-700 text-gray-800 dark:text-slate-300 rounded-full text-sm">{status}</span>;
    }
  };

  const getAuthBadge = (authenticated: boolean | null) => {
    if (authenticated === true) {
      return <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded text-xs">Confirmaste</span>;
    }
    if (authenticated === false) {
      return <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 rounded text-xs">No fuiste tú</span>;
    }
    return null;
  };

  if (loading) {
    return (
      <div className={darkMode ? 'dark' : ''}>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800 py-12 px-4">
          <div className="max-w-5xl mx-auto text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-12 h-12 mx-auto border-4 border-user-primary dark:border-indigo-500 border-t-transparent rounded-full"
            />
            <p className="mt-4 text-gray-600 dark:text-slate-400">Cargando transacciones...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800 py-12 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mis Transacciones</h1>
            <p className="text-gray-600 dark:text-slate-400 mt-2">
              Historial completo de tus transacciones y su estado de validación
            </p>
          </motion.div>

          {error && (
            <Card className="mb-6 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <p className="text-red-700 dark:text-red-400">{error}</p>
            </Card>
          )}

          {transactions.length === 0 ? (
            <Card className="dark:bg-slate-800 dark:border-slate-700">
              <div className="text-center py-12">
                <span className="text-6xl">📭</span>
                <p className="mt-4 text-gray-600 dark:text-slate-400">No tienes transacciones aún</p>
              </div>
            </Card>
        ) : (
          <div className="space-y-4">
            {transactions.map((tx, index) => (
              <motion.div
                key={tx.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className={`dark:bg-slate-800 dark:border-slate-700 ${tx.needsAuthentication ? 'border-2 border-yellow-400 dark:border-yellow-600 shadow-lg' : ''}`}>
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-slate-400">ID: {tx.id.slice(0, 12)}...</p>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                          ${tx.amount.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-right space-y-2">
                        {getStatusBadge(tx.status)}
                        {getAuthBadge(tx.userAuthenticated)}
                      </div>
                    </div>

                    {/* Details */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500 dark:text-slate-400">Ubicación</p>
                        <p className="font-medium text-gray-900 dark:text-white">{tx.location || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-slate-400">Fecha</p>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {new Date(tx.timestamp).toLocaleString('es-ES')}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-slate-400">Nivel de Riesgo</p>
                        <p className="font-medium text-gray-900 dark:text-white">{tx.riskScore}</p>
                      </div>
                      {tx.violations.length > 0 && (
                        <div>
                          <p className="text-gray-500 dark:text-slate-400">Alertas</p>
                          <p className="font-medium text-orange-600 dark:text-orange-400">{tx.violations.length} regla(s)</p>
                        </div>
                      )}
                    </div>

                    {/* Violations */}
                    {tx.violations.length > 0 && (
                      <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
                        <p className="text-xs font-medium text-orange-800 dark:text-orange-400 mb-2">MOTIVOS:</p>
                        <ul className="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                          {tx.violations.map((v) => (
                            <li key={`${tx.transactionId || tx.id}-${v}`}>• {translateViolation(v)}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Authentication needed */}
                    {tx.needsAuthentication && (
                      <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-400 dark:border-yellow-600 rounded-lg p-4">
                        <p className="font-bold text-yellow-900 dark:text-yellow-400 mb-3 flex items-center">
                          <span className="text-2xl mr-2">⚠️</span>
                          {' '}
                          ¿Realizaste esta transacción?
                        </p>
                        <p className="text-sm text-yellow-800 dark:text-yellow-300 mb-4">
                          Detectamos actividad inusual. Por seguridad, confirma si fuiste tú.
                        </p>
                        <div className="flex gap-3">
                          <button
                            onClick={() => handleAuthenticate(tx.id, true)}
                            disabled={authenticating === tx.id}
                            className="flex-1 py-3 bg-green-600 dark:bg-green-700 text-white rounded-lg hover:bg-green-700 dark:hover:bg-green-600 disabled:opacity-50 font-medium transition-colors"
                          >
                            {authenticating === tx.id ? '...' : '✓ Fui yo'}
                          </button>
                          <button
                            onClick={() => handleAuthenticate(tx.id, false)}
                            disabled={authenticating === tx.id}
                            className="flex-1 py-3 bg-red-600 dark:bg-red-700 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-600 disabled:opacity-50 font-medium transition-colors"
                          >
                            {authenticating === tx.id ? '...' : '✗ No fui yo'}
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Review info */}
                    {tx.reviewedBy && (
                      <div className="text-xs text-gray-500 dark:text-slate-400 pt-2 border-t dark:border-slate-700">
                        Revisada por {tx.reviewedBy} el {new Date(tx.reviewedAt!).toLocaleString('es-ES')}
                      </div>
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
    </div>
  );
}
