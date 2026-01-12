import React from 'react';
import { motion } from 'framer-motion';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { RiskScoreBar } from './RiskScoreBar';
import { formatCurrency } from '@/utils/formatters';
import { translateViolation } from '@/utils/translations';
import type { TransactionResponse, TransactionRequest } from '@/types/transaction';

interface ResultDisplayProps {
  result: TransactionResponse;
  transaction: TransactionRequest;
  onNewTransaction: () => void;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({
  result,
  transaction,
  onNewTransaction,
}) => {
  const getStatusConfig = () => {
    switch (result.status) {
      case 'APPROVED':
        return {
          icon: '✓',
          iconColor: 'text-user-approved',
          iconBg: 'bg-green-100',
          title: '¡Transacción Aprobada!',
          titleColor: 'text-green-700',
          cardBg: 'bg-green-50',
          message: 'Tu transacción fue procesada exitosamente.',
        };
      case 'SUSPICIOUS':
        return {
          icon: '⚠',
          iconColor: 'text-user-warning',
          iconBg: 'bg-yellow-100',
          title: 'Transacción Sospechosa',
          titleColor: 'text-yellow-700',
          cardBg: 'bg-yellow-50',
          message:
            'Detectamos actividad inusual en esta transacción. Por tu seguridad, necesitamos que confirmes si fuiste tú quien realizó esta operación. Una vez autentiques, nuestro equipo bancario verificará y procesará la transacción. Recibirás una notificación cuando se complete la revisión.',
        };
      case 'REJECTED':
        return {
          icon: '✗',
          iconColor: 'text-user-error',
          iconBg: 'bg-red-100',
          title: 'Transacción Rechazada',
          titleColor: 'text-red-700',
          cardBg: 'bg-red-50',
          message:
            'Por tu seguridad, esta transacción ha sido bloqueada. Contacta a nuestro equipo de soporte si consideras que es un error.',
        };
      default:
        return {
          icon: '?',
          iconColor: 'text-gray-500',
          iconBg: 'bg-gray-100',
          title: 'Estado Desconocido',
          titleColor: 'text-gray-700',
          cardBg: 'bg-gray-50',
          message: 'Ocurrió un error inesperado.',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <Card>
      <div className="text-center space-y-6">
        {/* Ícono de Estado */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="inline-flex items-center justify-center"
        >
          <div
            className={`w-20 h-20 rounded-full ${config.iconBg} flex items-center justify-center`}
          >
            <span className={`text-4xl ${config.iconColor}`}>{config.icon}</span>
          </div>
        </motion.div>

        {/* Título */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className={`text-2xl font-bold ${config.titleColor}`}
        >
          {config.title}
        </motion.h2>

        {/* Resumen de Transacción */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={`p-6 ${config.cardBg} rounded-xl space-y-3`}
        >
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">Monto:</span>
            <span className="text-lg font-bold text-gray-900">
              {formatCurrency(transaction.amount)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">Usuario:</span>
            <span className="text-sm text-gray-900">{transaction.userId}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">Estado:</span>
            <span className={`text-sm font-semibold ${config.titleColor}`}>
              {result.status} {config.icon}
            </span>
          </div>
          <div className="pt-2">
            <RiskScoreBar score={result.riskScore} status={result.status} />
          </div>
        </motion.div>

        {/* Alertas/Violaciones */}
        {result.violations && result.violations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-left"
          >
            <h3 className="text-sm font-semibold text-gray-700 mb-2">
              {result.status === 'REJECTED' ? 'Violaciones Detectadas:' : 'Alertas Detectadas:'}
            </h3>
            <ul className="space-y-2">
              {result.violations.map((violation, index) => (
                <li
                  key={index}
                  className={`text-sm flex items-start ${config.titleColor}`}
                >
                  <span className="mr-2">•</span>
                  <span>{translateViolation(violation)}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Mensaje Explicativo */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-sm text-gray-600"
        >
          {config.message}
        </motion.p>

        {/* Botón de Nueva Transacción */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <Button variant="secondary" onClick={onNewTransaction}>
            Nueva Transacción
          </Button>
        </motion.div>
      </div>
    </Card>
  );
};
