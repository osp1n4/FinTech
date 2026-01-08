import axios from 'axios';
import type { Rule, Transaction, Metrics, TrendData } from '@/types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Analyst-ID': import.meta.env.VITE_ANALYST_ID || 'analyst_demo',
  },
});

// Rules
export const getRules = async (): Promise<Rule[]> => {
  const response = await api.get('/api/v1/admin/rules');
  return response.data;
};

export const updateRule = async (ruleId: string, parameters: any): Promise<any> => {
  const response = await api.put(`/api/v1/admin/rules/${ruleId}`, { parameters });
  return response.data;
};

export const createRule = async (rule: {
  name: string;
  type: string;
  parameters: any;
  enabled?: boolean;
  order?: number;
}): Promise<any> => {
  const response = await api.post('/api/v1/admin/rules', rule);
  return response.data;
};

export const deleteRule = async (ruleId: string): Promise<any> => {
  const response = await api.delete(`/api/v1/admin/rules/${ruleId}`);
  return response.data;
};

export const reorderRules = async (ruleIds: string[]): Promise<any> => {
  const response = await api.post('/api/v1/admin/rules/reorder', { ruleIds });
  return response.data;
};

// Transactions
export const getTransactionsLog = async (
  status?: string,
  limit: number = 100
): Promise<Transaction[]> => {
  const params: any = { limit };
  if (status) params.status = status;
  const response = await api.get('/api/v1/admin/transactions/log', { params });
  return response.data;
};

export const reviewTransaction = async (
  transactionId: string,
  decision: 'APPROVED' | 'REJECTED',
  comment?: string
): Promise<any> => {
  console.log('🌐 API reviewTransaction:', { transactionId, decision, comment });
  console.log('🌐 URL:', `/api/v1/transaction/review/${transactionId}`);
  console.log('🌐 Body:', { decision, analyst_comment: comment });
  
  const response = await api.put(`/api/v1/transaction/review/${transactionId}`, {
    decision,
    analyst_comment: comment,
  });
  
  console.log('🌐 Response:', response);
  return response.data;
};

// Metrics
export const getMetrics = async (): Promise<Metrics> => {
  const response = await api.get('/api/v1/admin/metrics');
  return response.data;
};

export const getTrends = async (): Promise<TrendData[]> => {
  const response = await api.get('/api/v1/admin/trends');
  return response.data;
};

export default api;
