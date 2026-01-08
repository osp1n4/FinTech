/**
 * HUMAN REVIEW (Maria Paula Gutierrez):
 * La IA usó datos falsos (mock) en el gráfico.
 * Lo cambié para mostrar datos reales del servidor
 * porque los datos falsos no coincidían con las estadísticas.
 */
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTrends } from '@/services/api';
import type { TrendData } from '@/types';

const TrendChart: React.FC = () => {
  const [data, setData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrends();
  }, []);

  const loadTrends = async () => {
    try {
      const trends = await getTrends();
      setData(trends);
    } catch (error) {
      console.error('Error loading trends:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-admin-surface rounded-xl p-6">
        <h2 className="text-xl font-bold mb-6">Tendencia de Transacciones (Últimas 24h)</h2>
        <div className="flex items-center justify-center h-[300px]">
          <div className="text-gray-400">Cargando tendencias...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-admin-surface rounded-xl p-6">
      <h2 className="text-xl font-bold mb-6">Tendencia de Transacciones (Últimas 24h)</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="time" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#374151',
              border: 'none',
              borderRadius: '8px',
              color: '#F9FAFB',
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="approved" stroke="#10B981" name="Aprobadas" strokeWidth={2} />
          <Line type="monotone" dataKey="suspicious" stroke="#FBBF24" name="Sospechosas" strokeWidth={2} />
          <Line type="monotone" dataKey="rejected" stroke="#F87171" name="Rechazadas" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
