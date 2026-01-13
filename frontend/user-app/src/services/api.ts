import axios from 'axios';
import type { TransactionRequest, TransactionResponse } from '@/types/transaction';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token JWT a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Si el token expiró o es inválido, limpiar la sesión
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('userId');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userFullName');
      globalThis.location.reload();
    }
    
    return Promise.reject(error);
  }
);

export const validateTransaction = async (
  transaction: TransactionRequest
): Promise<TransactionResponse> => {
  const response = await api.post<TransactionResponse>(
    `/api/v1/transaction/validate`,
    transaction
  );
  return response.data;
};

export const getUserTransactions = async (userId: string) => {
  const response = await api.get(`/api/v1/user/transactions/${userId}`);
  return response.data;
};

export const authenticateTransaction = async (transactionId: string, confirmed: boolean) => {
  const response = await api.post(`/api/v1/user/transaction/${transactionId}/authenticate`, {
    confirmed
  });
  return response.data;
};

export default api;
