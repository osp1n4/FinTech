import React, { useState, useEffect } from 'react';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { LocationInput } from './LocationInput';
import { generateDeviceId } from '@/utils/formatters';
import { useUser } from '@/context/UserContext';
import type { TransactionRequest } from '@/types/transaction';

interface TransactionFormProps {
  onSubmit: (transaction: TransactionRequest) => void;
  isLoading: boolean;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({
  onSubmit,
  isLoading,
}) => {
  const { userId, setUserId } = useUser();
  
  // Generar deviceId específico para este usuario
  const deviceId = React.useMemo(() => generateDeviceId(userId), [userId]);
  
  const [formData, setFormData] = useState<TransactionRequest>({
    amount: 0,
    userId: userId,
    location: '', // Vacío para que el usuario ingrese o use GPS
    deviceId: deviceId,
    transactionType: 'transfer',
    description: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof TransactionRequest, string>>>({});

  // Actualizar formData cuando cambie el userId o deviceId del contexto
  useEffect(() => {
    setFormData((prev) => ({
      ...prev,
      userId: userId,
      deviceId: deviceId,
    }));
  }, [userId, deviceId]);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof TransactionRequest, string>> = {};

    if (!formData.amount || formData.amount <= 0) {
      newErrors.amount = 'El monto debe ser mayor a 0';
    }

    if (!formData.userId.trim()) {
      newErrors.userId = 'El ID de usuario es requerido';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'La ubicación es requerida';
    }

    if (!formData.deviceId.trim()) {
      newErrors.deviceId = 'El ID del dispositivo es requerido';
    }

    if (!formData.description?.trim()) {
      newErrors.description = 'La descripción es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (field: keyof TransactionRequest) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field === 'amount' ? Number.parseFloat(e.target.value) || 0 : e.target.value;
    
    // Si cambia el userId, actualizar el contexto
    if (field === 'userId') {
      setUserId(value as string);
    }
    
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Limpiar error al editar
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Input
        label="Monto de la Transferencia"
        type="number"
        step="0.01"
        placeholder="0.00"
        value={formData.amount || ''}
        onChange={handleChange('amount')}
        error={errors.amount}
        disabled={isLoading}
      />

      <Input
        label="ID de Usuario"
        type="text"
        placeholder="user_12345"
        value={formData.userId}
        onChange={handleChange('userId')}
        error={errors.userId}
        disabled={isLoading}
      />

      <LocationInput
        value={formData.location}
        onChange={(value) => {
          setFormData(prev => ({ ...prev, location: value }));
          if (errors.location) {
            setErrors(prev => ({ ...prev, location: undefined }));
          }
        }}
        error={errors.location}
        disabled={isLoading}
      />

      <Input
        label="ID del Dispositivo"
        type="text"
        placeholder="mobile_ABC123"
        value={formData.deviceId}
        onChange={handleChange('deviceId')}
        error={errors.deviceId}
        disabled={isLoading}
      />

      <div>
        <label htmlFor="transaction-type-select" className="block text-sm font-medium text-gray-700 mb-2">
          Tipo de Transacción
        </label>
        <select
          id="transaction-type-select"
          value={formData.transactionType}
          onChange={(e) => setFormData(prev => ({ ...prev, transactionType: e.target.value as any }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-user-primary focus:border-transparent"
          disabled={isLoading}
        >
          <option value="transfer">Transferencia a otra persona</option>
          <option value="payment">Pago de servicio público</option>
          <option value="recharge">Recarga de celular</option>
          <option value="deposit">Depósito</option>
        </select>
      </div>

      <Input
        label="Descripción / Destinatario"
        type="text"
        placeholder="Ej: Juan Pérez, Servicio de luz, etc."
        value={formData.description || ''}
        onChange={(e) => {
          setFormData(prev => ({ ...prev, description: e.target.value }));
          if (errors.description) {
            setErrors(prev => ({ ...prev, description: undefined }));
          }
        }}
        error={errors.description}
        disabled={isLoading}
      />

      <Button type="submit" isLoading={isLoading}>
        Realizar Transacción
      </Button>
    </form>
  );
};
