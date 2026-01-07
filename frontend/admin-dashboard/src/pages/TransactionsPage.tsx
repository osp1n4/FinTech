import { useEffect, useState } from 'react';
import { getTransactionsLog, reviewTransaction } from '@/services/api';
import type { Transaction } from '@/types';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [filter, setFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTransactions();
  }, [filter]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const data = await getTransactionsLog(filter || undefined, 100);
      setTransactions(data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (transactionId: string, decision: 'APPROVED' | 'REJECTED') => {
    console.log('🔵 handleReview llamado:', { transactionId, decision });
    try {
      console.log('🔵 Llamando a reviewTransaction...');
      const result = await reviewTransaction(transactionId, decision);
      console.log('✅ reviewTransaction exitoso:', result);
      
      // Recargar transacciones para reflejar el cambio
      console.log('🔵 Recargando transacciones...');
      await loadTransactions();
      console.log('✅ Transacciones recargadas');
      
      alert(`Transacción ${decision === 'APPROVED' ? 'aprobada' : 'rechazada'} exitosamente`);
    } catch (error: any) {
      console.error('❌ Error reviewing transaction:', error);
      console.error('❌ Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      alert(`Error al revisar la transacción: ${error.response?.data?.detail || error.message}`);
    }
  };

  const suspiciousCount = transactions.filter((t) => t.status === 'SUSPICIOUS').length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Log de Transacciones</h1>
        <div className="bg-admin-surface px-4 py-2 rounded-lg">
          <span className="text-yellow-400">⚠</span>
          <span className="ml-2">En Revisión: {suspiciousCount}</span>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-admin-surface rounded-xl p-4">
        <div className="flex space-x-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
          >
            <option value="">Todas</option>
            <option value="APPROVED">Aprobadas</option>
            <option value="SUSPICIOUS">Sospechosas</option>
            <option value="REJECTED">Rechazadas</option>
          </select>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-admin-surface rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Cargando...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-admin-bg">
                <tr>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">ID</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Monto</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Usuario</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Usuario</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Ubicación</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Fecha/Hora</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Estado</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Autenticación</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Violaciones</th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id} className="border-t border-gray-700 hover:bg-gray-700">
                    <td className="py-4 px-6 text-sm">#{tx.id.slice(0, 8)}</td>
                    <td className="py-4 px-6 font-semibold">${tx.amount.toLocaleString()}</td>
                    <td className="py-4 px-6 text-sm text-gray-400">{tx.userId}</td>
                    <td className="py-4 px-6 text-sm text-gray-400">{tx.location || 'N/A'}</td>
                    <td className="py-4 px-6 text-sm text-gray-400">
                      {new Date(tx.date).toLocaleString('es-ES', {
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="py-4 px-6">
                      <span
                        className={`
                          px-3 py-1 rounded-full text-xs font-semibold
                          ${tx.status === 'APPROVED' ? 'bg-green-900 text-green-300' : ''}
                          ${tx.status === 'SUSPICIOUS' ? 'bg-yellow-900 text-yellow-300' : ''}
                          ${tx.status === 'REJECTED' ? 'bg-red-900 text-red-300' : ''}
                        `}
                      >
                        {tx.status === 'APPROVED' && '✓'}
                        {tx.status === 'SUSPICIOUS' && '⚠'}
                        {tx.status === 'REJECTED' && '⛔'}
                        {' '}
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      {tx.userAuthenticated === true && (
                        <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded-full text-xs font-semibold">
                          ✓ Usuario confirmó
                        </span>
                      )}
                      {tx.userAuthenticated === false && (
                        <span className="px-2 py-1 bg-red-900 text-red-300 rounded-full text-xs font-semibold">
                          ✗ Usuario negó
                        </span>
                      )}
                      {tx.userAuthenticated === null && tx.status === 'SUSPICIOUS' && (
                        <span className="px-2 py-1 bg-gray-700 text-gray-400 rounded-full text-xs">
                          ⏳ Pendiente
                        </span>
                      )}
                      {tx.status !== 'SUSPICIOUS' && tx.userAuthenticated === null && (
                        <span className="text-gray-500 text-xs">-</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-sm">
                      {tx.violations.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {tx.violations.slice(0, 2).map((v, i) => (
                            <span key={i} className="px-2 py-1 bg-gray-700 rounded text-xs">
                              {v}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="py-4 px-6">
                      {tx.status === 'SUSPICIOUS' ? (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleReview(tx.id, 'APPROVED')}
                            className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs font-semibold transition-colors"
                            title="Aprobar transacción"
                          >
                            ✓ Aprobar
                          </button>
                          <button
                            onClick={() => handleReview(tx.id, 'REJECTED')}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-semibold transition-colors"
                            title="Rechazar transacción"
                          >
                            ✗ Rechazar
                          </button>
                        </div>
                      ) : (
                        <span className="text-gray-500 text-xs">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
