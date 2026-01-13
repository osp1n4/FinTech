import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { getUserTransactions, authenticateTransaction } from '../services/api';
import { useUser } from '../context/UserContext';
import { translateViolation } from '../utils/translations';
import { useToast } from '../components/ToastContainer';

interface Transaction {
  id: string;
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
        return <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">✓ Aprobada</span>;
      case 'REJECTED':
        return <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">✗ Rechazada</span>;
      case 'PENDING_REVIEW':
        return <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">⏳ Revisión</span>;
      default:
        return <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">{status}</span>;
    }
  };

  const getAuthBadge = (authenticated: boolean | null) => {
    if (authenticated === true) {
      return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Confirmaste</span>;
    }
    if (authenticated === false) {
      return <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">No fuiste tú</span>;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 mx-auto border-4 border-user-primary border-t-transparent rounded-full"
          />
          <p className="mt-4 text-gray-600">Cargando transacciones...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">Mis Transacciones</h1>
          <p className="text-gray-600 mt-2">
            Historial completo de tus transacciones y su estado de validación
          </p>
        </motion.div>

        {error && (
          <Card className="mb-6 bg-red-50 border-red-200">
            <p className="text-red-700">{error}</p>
          </Card>
        )}

        {transactions.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <span className="text-6xl">📭</span>
              <p className="mt-4 text-gray-600">No tienes transacciones aún</p>
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
                <Card className={`${tx.needsAuthentication ? 'border-2 border-yellow-400 shadow-lg' : ''}`}>
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-gray-500">ID: {tx.id.slice(0, 12)}...</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
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
                        <p className="text-gray-500">Ubicación</p>
                        <p className="font-medium text-gray-900">{tx.location || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Fecha</p>
                        <p className="font-medium text-gray-900">
                          {new Date(tx.timestamp).toLocaleString('es-ES')}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Nivel de Riesgo</p>
                        <p className="font-medium text-gray-900">{tx.riskScore}</p>
                      </div>
                      {tx.violations.length > 0 && (
                        <div>
                          <p className="text-gray-500">Alertas</p>
                          <p className="font-medium text-orange-600">{tx.violations.length} regla(s)</p>
                        </div>
                      )}
                    </div>

                    {/* Violations */}
                    {tx.violations.length > 0 && (
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                        <p className="text-xs font-medium text-orange-800 mb-2">MOTIVOS:</p>
                        <ul className="text-sm text-orange-700 space-y-1">
                          {tx.violations.map((v) => (
                            <li key={`${tx.transactionId || tx.id}-${v}`}>• {translateViolation(v)}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Authentication needed */}
                    {tx.needsAuthentication && (
                      <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-4">
                        <p className="font-bold text-yellow-900 mb-3 flex items-center">
                          <span className="text-2xl mr-2">⚠️</span>
                          {' '}
                          ¿Realizaste esta transacción?
                        </p>
                        <p className="text-sm text-yellow-800 mb-4">
                          Detectamos actividad inusual. Por seguridad, confirma si fuiste tú.
                        </p>
                        <div className="flex gap-3">
                          <button
                            onClick={() => handleAuthenticate(tx.id, true)}
                            disabled={authenticating === tx.id}
                            className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium transition-colors"
                          >
                            {authenticating === tx.id ? '...' : '✓ Fui yo'}
                          </button>
                          <button
                            onClick={() => handleAuthenticate(tx.id, false)}
                            disabled={authenticating === tx.id}
                            className="flex-1 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium transition-colors"
                          >
                            {authenticating === tx.id ? '...' : '✗ No fui yo'}
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Review info */}
                    {tx.reviewedBy && (
                      <div className="text-xs text-gray-500 pt-2 border-t">
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
  );
}
