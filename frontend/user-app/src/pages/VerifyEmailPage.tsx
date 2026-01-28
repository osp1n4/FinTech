import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { Mail, CheckCircle, ArrowLeft } from 'lucide-react';
import { DarkModeToggle } from '../components/DarkModeToggle';
import { useTheme } from '../context/ThemeContext';

interface VerifyEmailPageProps {
  email: string;
  onVerifySuccess: () => void;
  onBackToLogin: () => void;
}

export function VerifyEmailPage({ email, onVerifySuccess, onBackToLogin }: VerifyEmailPageProps) {
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { darkMode } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Token inválido o expirado');
      }

      onVerifySuccess();
    } catch (err: any) {
      setError(err.message || 'Error al verificar el email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <img src="assets/logo-full.svg" alt="FinTech Bank" className="mx-auto mb-2 h-28" />
            <p className="text-gray-600 dark:text-slate-400">Verifica tu cuenta</p>
          </div>

          <Card className="p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Verifica tu Email</h2>
              <p className="text-gray-600 dark:text-slate-400 text-sm">
                Hemos enviado un código de verificación a:
              </p>
              <p className="text-indigo-600 dark:text-indigo-400 font-medium mt-1">{email}</p>
              <p className="text-gray-500 dark:text-slate-500 text-xs mt-3">
                Por favor, revisa tu bandeja de entrada y spam.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
                  Código de Verificación
                </label>
                <input
                  type="text"
                  value={token}
                  onChange={(e) => {
                    const value = e.target.value.replaceAll(/\D/g, '').slice(0, 6);
                    setToken(value);
                  }}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-center text-2xl tracking-widest font-bold dark:text-white"
                  placeholder="000000"
                  required
                  maxLength={6}
                  pattern="[0-9]{6}"
                />
                <p className="text-xs text-gray-500 dark:text-slate-500 mt-2 text-center">
                  Ingresa el código de 6 dígitos que recibiste por email
                </p>
              </div>

              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  'Verificando...'
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Verificar Cuenta
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={onBackToLogin}
                className="text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-700 dark:hover:text-indigo-300 flex items-center justify-center gap-2 mx-auto text-sm"
              >
                <ArrowLeft className="w-4 h-4" />
                Volver al Login
              </button>
            </div>
          </Card>
        </motion.div>
        <DarkModeToggle />
      </div>
    </div>
  );
}
