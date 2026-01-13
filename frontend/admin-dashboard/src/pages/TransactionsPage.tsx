import { useEffect, useState } from 'react';
import { getTransactionsLog, reviewTransaction } from '@/services/api';
import { translateViolation } from '@/utils/translations';
import { useToast } from '@/components/ToastContainer';
import type { Transaction } from '@/types';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [allTransactions, setAllTransactions] = useState<Transaction[]>([]);
  const [filter, setFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [pageSize, setPageSize] = useState<string>('100');
  
  // Filtros locales
  const [searchId, setSearchId] = useState('');
  const [searchUser, setSearchUser] = useState('');
  const [searchLocation, setSearchLocation] = useState('');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  
  // Estados para mostrar/ocultar filtros
  const [showIdFilter, setShowIdFilter] = useState(false);
  const [showUserFilter, setShowUserFilter] = useState(false);
  const [showLocationFilter, setShowLocationFilter] = useState(false);
  const [showAmountFilter, setShowAmountFilter] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, [filter, pageSize]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      // Convert pageSize into numeric limit or undefined for 'Todos'
      const limit = pageSize === 'Todos' || pageSize === 'all' ? undefined : parseInt(pageSize, 10);
      const data = await getTransactionsLog(filter || undefined, limit as any);
      setAllTransactions(data);
      applyFilters(data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  // Aplicar filtros locales
  const applyFilters = (data: Transaction[]) => {
    let filtered = [...data];

    if (searchId) {
      filtered = filtered.filter(tx => 
        tx.id.toLowerCase().includes(searchId.toLowerCase())
      );
    }

    if (searchUser) {
      filtered = filtered.filter(tx => 
        tx.userId.toLowerCase().includes(searchUser.toLowerCase())
      );
    }

    if (searchLocation) {
      filtered = filtered.filter(tx => 
        tx.location?.toLowerCase().includes(searchLocation.toLowerCase())
      );
    }

    if (minAmount) {
      filtered = filtered.filter(tx => tx.amount >= Number.parseFloat(minAmount));
    }
    if (maxAmount) {
      filtered = filtered.filter(tx => tx.amount <= Number.parseFloat(maxAmount));
    }

    setTransactions(filtered);
  };

  useEffect(() => {
    applyFilters(allTransactions);
  }, [searchId, searchUser, searchLocation, minAmount, maxAmount, allTransactions]);

  const { add } = useToast();

  const handleReview = async (transactionId: string, decision: 'APPROVED' | 'REJECTED') => {
    try {
      await reviewTransaction(transactionId, decision);
      await loadTransactions();
      add(`Transacción ${decision === 'APPROVED' ? 'aprobada' : 'rechazada'} exitosamente`, 'success', decision === 'APPROVED' ? 'Aprobación completada' : 'Rechazo completado');
    } catch (error: any) {
      add(`Error al revisar la transacción: ${error.response?.data?.detail || error.message}`, 'error', 'Error al revisar');
    }
  };

  const suspiciousCount = transactions.filter((t) => t.status === 'SUSPICIOUS').length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transacciones</h1>
        <div className="bg-admin-surface px-4 py-2 rounded-lg">
          <span className="text-yellow-400">⚠</span>
          <span className="ml-2">En Revisión: {suspiciousCount}</span>
        </div>
      </div>

      {/* Filtro de estado */}
      <div className="bg-admin-surface rounded-xl p-4">
          <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-gray-400">Estado:</span>
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
          <div className="ml-4">
            <label className="text-sm text-gray-400 mr-2">Mostrar:</label>
            <select
              value={pageSize}
              onChange={(e) => setPageSize(e.target.value)}
              className="px-3 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
            >
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="500">500</option>
              <option value="1000">1000</option>
              <option value="Todos">Todos</option>
            </select>
          </div>
          <span className="text-sm text-gray-400 ml-auto">
            Mostrando {transactions.length} de {allTransactions.length} transacciones
          </span>
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
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">
                    <div className="flex items-center gap-2">
                      ID
                      {' '}
                      <button
                        onClick={() => setShowIdFilter(!showIdFilter)}
                        className="text-gray-500 hover:text-admin-primary transition-colors"
                        title="Filtrar por ID"
                      >
                        🔍
                      </button>
                    </div>
                    {showIdFilter && (
                      <input
                        type="text"
                        placeholder="Buscar ID..."
                        value={searchId}
                        onChange={(e) => setSearchId(e.target.value)}
                        className="mt-2 px-3 py-1 w-full bg-admin-bg rounded border border-gray-600 focus:border-admin-primary focus:outline-none text-sm text-white"
                        onClick={(e) => e.stopPropagation()}
                      />
                    )}
                  </th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">
                    <div className="flex items-center gap-2">
                      Monto
                      {' '}
                      <button
                        onClick={() => setShowAmountFilter(!showAmountFilter)}
                        className="text-gray-500 hover:text-admin-primary transition-colors"
                        title="Filtrar por monto"
                      >
                        🔍
                      </button>
                    </div>
                    {showAmountFilter && (
                      <div className="mt-2 flex gap-2">
                        <input
                          type="number"
                          placeholder="Min"
                          value={minAmount}
                          onChange={(e) => setMinAmount(e.target.value)}
                          className="px-2 py-1 w-20 bg-admin-bg rounded border border-gray-600 focus:border-admin-primary focus:outline-none text-sm text-white"
                        />
                        <input
                          type="number"
                          placeholder="Max"
                          value={maxAmount}
                          onChange={(e) => setMaxAmount(e.target.value)}
                          className="px-2 py-1 w-20 bg-admin-bg rounded border border-gray-600 focus:border-admin-primary focus:outline-none text-sm text-white"
                        />
                      </div>
                    )}
                  </th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">
                    <div className="flex items-center gap-2">
                      Usuario
                      {' '}
                      <button
                        onClick={() => setShowUserFilter(!showUserFilter)}
                        className="text-gray-500 hover:text-admin-primary transition-colors"
                        title="Filtrar por usuario"
                      >
                        🔍
                      </button>
                    </div>
                    {showUserFilter && (
                      <input
                        type="text"
                        placeholder="Buscar usuario..."
                        value={searchUser}
                        onChange={(e) => setSearchUser(e.target.value)}
                        className="mt-2 px-3 py-1 w-full bg-admin-bg rounded border border-gray-600 focus:border-admin-primary focus:outline-none text-sm text-white"
                      />
                    )}
                  </th>
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">
                    <div className="flex items-center gap-2">
                      Ubicación
                      {' '}
                      <button
                        onClick={() => setShowLocationFilter(!showLocationFilter)}
                        className="text-gray-500 hover:text-admin-primary transition-colors"
                        title="Filtrar por ubicación"
                      >
                        🔍
                      </button>
                    </div>
                    {showLocationFilter && (
                      <input
                        type="text"
                        placeholder="Buscar ubicación..."
                        value={searchLocation}
                        onChange={(e) => setSearchLocation(e.target.value)}
                        className="mt-2 px-3 py-1 w-full bg-admin-bg rounded border border-gray-600 focus:border-admin-primary focus:outline-none text-sm text-white"
                      />
                    )}
                  </th>
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
                          {tx.violations.slice(0, 2).map((v) => (
                            <span key={v} className="px-2 py-1 bg-gray-700 rounded text-xs">
                              {translateViolation(v)}
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
