import { useState, FormEvent } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface VerifyResponse {
  success: boolean;
  message: string;
  admin_id: string;
}

export default function VerifyEmailPage() {
  const [token, setToken] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Obtener email y admin_id del state de navegación
  const email = location.state?.email || '';
  const admin_id = location.state?.admin_id || '';

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Solo permitir números y máximo 6 dígitos
    if (/^\d{0,6}$/.test(value)) {
      setToken(value);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validar código de 6 dígitos
    if (token.length !== 6) {
      toast.error('El código debe tener 6 dígitos');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/admin/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al verificar email');
      }

      const data: VerifyResponse = await response.json();

      toast.success(data.message || '¡Email verificado exitosamente!');
      
      // Esperar 1 segundo antes de redirigir para que el usuario vea el mensaje
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error('Error al verificar email. Intenta nuevamente.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 px-4">
      <div className="max-w-md w-full space-y-8 bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
          </div>
          <h2 className="text-3xl font-bold text-white">Verifica tu Email</h2>
          {email && (
            <p className="mt-2 text-gray-400">
              Hemos enviado un código de 6 dígitos a <br />
              <span className="font-semibold text-purple-400">{email}</span>
            </p>
          )}
          {!email && (
            <p className="mt-2 text-gray-400">
              Ingresa el código de 6 dígitos que recibiste en tu email
            </p>
          )}
        </div>

        {/* Formulario */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Token Input */}
            <div>
              <label htmlFor="token" className="block text-sm font-medium text-gray-300 mb-1">
                Código de Verificación
              </label>
              <input
                id="token"
                name="token"
                type="text"
                inputMode="numeric"
                pattern="\d{6}"
                required
                value={token}
                onChange={handleInputChange}
                maxLength={6}
                className="appearance-none relative block w-full px-3 py-3 border border-gray-600 bg-gray-700 placeholder-gray-400 text-white text-center text-2xl tracking-widest rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                placeholder="000000"
                disabled={isLoading}
                autoComplete="off"
              />
              <p className="mt-2 text-xs text-gray-400 text-center">
                Ingresa el código de 6 dígitos
              </p>
            </div>

            {/* Info adicional si hay admin_id */}
            {admin_id && (
              <div className="bg-gray-700 border border-gray-600 rounded-lg p-3">
                <p className="text-sm text-gray-300">
                  <span className="font-semibold">Admin ID:</span>{' '}
                  <span className="text-purple-400">{admin_id}</span>
                </p>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={isLoading || token.length !== 6}
              className="group relative w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <span className="flex items-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Verificando...
                </span>
              ) : (
                'Verificar Email'
              )}
            </button>
          </div>

          {/* Links adicionales */}
          <div className="space-y-3 text-center">
            <p className="text-sm text-gray-400">
              ¿No recibiste el código?{' '}
              <button
                type="button"
                className="font-medium text-purple-500 hover:text-purple-400 transition"
                onClick={() => toast.info('Función de reenvío próximamente')}
              >
                Reenviar código
              </button>
            </p>
            <p className="text-sm text-gray-400">
              <Link
                to="/login"
                className="font-medium text-purple-500 hover:text-purple-400 transition"
              >
                Volver al inicio de sesión
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
