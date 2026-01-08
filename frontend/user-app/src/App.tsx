import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from './components/ui/Card';
import { TransactionForm } from './components/TransactionForm';
import { ResultDisplay } from './components/ResultDisplay';
import { TransactionsPage } from './pages/TransactionsPage';
import { UserSelector } from './components/UserSelector';
import { validateTransaction } from './services/api';
import type { TransactionRequest, TransactionResponse, TransactionStatus } from './types/transaction';

type Page = 'new-transaction' | 'my-transactions';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('new-transaction');
  const [status, setStatus] = useState<TransactionStatus>('idle');
  const [result, setResult] = useState<TransactionResponse | null>(null);
  const [currentTransaction, setCurrentTransaction] = useState<TransactionRequest | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (transaction: TransactionRequest) => {
    setStatus('loading');
    setError(null);
    setCurrentTransaction(transaction);

    try {
      const response = await validateTransaction(transaction);
      setResult(response);
      setStatus('success');
    } catch (err) {
      setError('Ocurrió un error al procesar tu transacción. Por favor, intenta de nuevo.');
      setStatus('error');
      console.error('Error:', err);
    }
  };

  const handleNewTransaction = () => {
    setStatus('idle');
    setResult(null);
    setCurrentTransaction(null);
    setError(null);
  };

  // Si estamos en la página de transacciones, mostrarla
  if (currentPage === 'my-transactions') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-xl font-bold text-gray-900">FinTech Bank</h1>
            <div className="flex gap-4 items-center">
              <UserSelector />
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage('new-transaction')}
                  className="px-4 py-2 text-gray-600 hover:text-user-primary hover:bg-gray-50 rounded-lg transition-colors"
                >
                  Nueva Transacción
                </button>
                <button
                  onClick={() => setCurrentPage('my-transactions')}
                  className="px-4 py-2 bg-user-primary text-white rounded-lg font-medium"
                >
                  Mis Transacciones
                </button>
              </div>
            </div>
          </div>
        </nav>
        <TransactionsPage />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      {/* Navigation */}
      <div className="max-w-md mx-auto mb-6 space-y-4">
        {/* User Selector */}
        <div className="flex justify-center">
          <UserSelector />
        </div>
        
        {/* Page Navigation */}
        <div className="flex gap-2 bg-white rounded-lg shadow-sm p-2">
          <button
            onClick={() => setCurrentPage('new-transaction')}
            className="flex-1 px-4 py-2 bg-user-primary text-white rounded-lg font-medium"
          >
            Nueva Transacción
          </button>
          <button
            onClick={() => setCurrentPage('my-transactions')}
            className="flex-1 px-4 py-2 text-gray-600 hover:text-user-primary hover:bg-gray-50 rounded-lg transition-colors"
          >
            Mis Transacciones
          </button>
        </div>
      </div>

      <div className="max-w-md mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            FinTech Bank
          </h1>
          <p className="text-gray-600">
            Generación de transacciones seguras
          </p>
        </motion.div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {status === 'idle' || status === 'loading' ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <Card>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Realizar una Transferencia
                </h2>
                <TransactionForm onSubmit={handleSubmit} isLoading={status === 'loading'} />
              </Card>
            </motion.div>
          ) : status === 'success' && result && currentTransaction ? (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <ResultDisplay
                result={result}
                transaction={currentTransaction}
                onNewTransaction={handleNewTransaction}
              />
            </motion.div>
          ) : status === 'error' ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <Card>
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-red-100 flex items-center justify-center">
                    <span className="text-4xl text-red-600">⚠</span>
                  </div>
                  <h2 className="text-xl font-bold text-red-700">Error</h2>
                  <p className="text-gray-600">{error}</p>
                  <button
                    onClick={handleNewTransaction}
                    className="w-full py-3 bg-user-primary text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Intentar de Nuevo
                  </button>
                </div>
              </Card>
            </motion.div>
          ) : null}
        </AnimatePresence>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 text-center text-sm text-gray-500"
        >
          Powered by FinTech Bank v1.0
        </motion.div>
      </div>
    </div>
  );
}

export default App;
