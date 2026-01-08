/**
 * HUMAN REVIEW (Maria Paula Gutierrez):
 * La IA cargaba datos sin mostrar estado de carga.
 * Agregué estados de loading/error para que el usuario
 * sepa qué está pasando mientras se cargan los datos.
 */
import { useEffect, useState } from 'react';
import { getMetrics, getTransactionsLog } from '@/services/api';
import type { Metrics, Transaction } from '@/types';
import KPICard from '@/components/dashboard/KPICard';
import TrendChart from '@/components/dashboard/TrendChart';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [metricsData, transactionsData] = await Promise.all([
        getMetrics(),
        getTransactionsLog(undefined, 10),
      ]);
      setMetrics(metricsData);
      setRecentTransactions(transactionsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Transacciones"
          value={metrics?.totalTransactions.toLocaleString() || '0'}
          trend="+145"
          icon="📈"
        />
        <KPICard
          title="% Bloqueadas"
          value={`${metrics?.blockedRate.toFixed(1)}%` || '0%'}
          trend="-0.2%"
          trendColor="green"
          icon="🔒"
        />
        <KPICard
          title="% En Revisión"
          value={`${metrics?.suspiciousRate.toFixed(1)}%` || '0%'}
          trend="+0.5%"
          trendColor="yellow"
          icon="⚠️"
        />
        <KPICard
          title="Avg Risk Score"
          value={`${metrics?.avgRiskScore || 0}/100`}
          trend="→ 0"
          icon="📊"
        />
      </div>

      {/* Chart */}
      <TrendChart />

      {/* Recent Transactions */}
      <div className="bg-admin-surface rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Transacciones Recientes</h2>
          <a href="/transactions" className="text-admin-primary hover:underline">
            Ver todas →
          </a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400">ID</th>
                <th className="text-left py-3 px-4 text-gray-400">Monto</th>
                <th className="text-left py-3 px-4 text-gray-400">Usuario</th>
                <th className="text-left py-3 px-4 text-gray-400">Fecha</th>
                <th className="text-left py-3 px-4 text-gray-400">Estado</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((tx) => (
                <tr key={tx.id} className="border-b border-gray-700 hover:bg-gray-700">
                  <td className="py-3 px-4 text-sm">#{tx.id}</td>
                  <td className="py-3 px-4 font-medium">${tx.amount.toLocaleString()}</td>
                  <td className="py-3 px-4 text-sm text-gray-400">{tx.userId}</td>
                  <td className="py-3 px-4 text-sm text-gray-400">
                    {new Date(tx.date).toLocaleString('es-ES', {
                      day: '2-digit',
                      month: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`
                        px-3 py-1 rounded-full text-xs font-semibold
                        ${tx.status === 'APPROVED' ? 'bg-green-900 text-green-300' : ''}
                        ${tx.status === 'SUSPICIOUS' ? 'bg-yellow-900 text-yellow-300' : ''}
                        ${tx.status === 'REJECTED' ? 'bg-red-900 text-red-300' : ''}
                      `}
                    >
                      {tx.status === 'APPROVED' && '✓ APPROVED'}
                      {tx.status === 'SUSPICIOUS' && '⚠ SUSPICIOUS'}
                      {tx.status === 'REJECTED' && '⛔ REJECTED'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
