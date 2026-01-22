import { useState } from 'react';
import { User, Lock, ArrowRight, Shield, Zap } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { DarkModeToggle } from '../components/DarkModeToggle';

interface LoginPageProps {
  onLogin: (userId: string, password: string) => Promise<void>;
  onSwitchToRegister: () => void;
}

export function LoginPage({ onLogin, onSwitchToRegister }: LoginPageProps) {
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { darkMode } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await onLogin(userId, password);
    } catch (err: any) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="flex flex-col md:flex-row min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
        {/* Left Panel - Decorative */}
        <div className="hidden md:flex w-1/2 bg-[#020617] relative overflow-hidden items-center justify-center">
          {/* Ambient glows */}
          <div className="absolute inset-0 z-0">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-[120px]"></div>
          </div>

          {/* Data streams */}
          <div className="absolute inset-0 overflow-hidden">
            {[20, 40, 60, 80].map((left, i) => (
              <div
                key={i}
                className="absolute w-px h-24 bg-gradient-to-b from-transparent via-teal-500 to-transparent"
                style={{
                  left: `${left}%`,
                  animation: `stream 3s linear infinite`,
                  animationDelay: `${i * 0.5}s`,
                }}
              />
            ))}
          </div>

          <div className="relative z-10 p-12 w-full max-w-lg">
            <div className="mb-12">
              <div className="flex items-center space-x-2 mb-4">
                <span className="inline-block px-3 py-1 bg-teal-500/20 text-teal-400 text-xs font-bold tracking-widest uppercase rounded-full border border-teal-500/30">
                  FinTech Bank
                </span>
              </div>
              <h1 className="text-4xl lg:text-5xl font-bold text-white leading-tight mb-6">
                Proteja sus activos con{' '}
                <span className="text-teal-400">Tecnología FinTech inteligente</span>
              </h1>
              <p className="text-slate-400 text-lg leading-relaxed">
                Prevenga el fraude en tiempo real y asegure cada transacción con un motor avanzado que evalúa riesgos automáticamente, para que su negocio opere con total confianza.
              </p>
            </div>

            {/* Stats Card */}
            <div className="backdrop-blur-lg bg-white/5 rounded-xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-teal-500/20 rounded-lg flex items-center justify-center">
                    <Shield className="w-5 h-5 text-teal-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Monitoreo activo</p>
                    <p className="text-white font-medium">99.9% Tasa de protección</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-teal-400 text-sm font-bold flex items-center">
                    <Zap className="w-4 h-4 mr-1" />
                    Live
                  </p>
                </div>
              </div>
              {/* Bar chart */}
              <div className="flex items-end space-x-2 h-24">
                {[40, 70, 50, 90, 60, 85, 45].map((height, i) => (
                  <div
                    key={i}
                    className={`w-full rounded-t-sm ${i === 6 ? 'bg-indigo-600/60' : 'bg-teal-500'}`}
                    style={{ height: `${height}%`, opacity: 0.3 + (i * 0.1) }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Login Form */}
        <div className="w-full md:w-1/2 flex flex-col justify-center items-center px-6 py-12 bg-white dark:bg-slate-900">
          <div className="w-full max-w-md">
            {/* Logo and Title */}
            <div className="flex flex-col items-center mb-10">
              <div className="flex items-center gap-3 mb-2">
                <div className="relative w-10 h-8">
                  <div className="absolute inset-0 bg-teal-500 -skew-x-12 rounded-sm"></div>
                  <div className="absolute inset-0 left-3 bg-teal-500/40 -skew-x-12 rounded-sm"></div>
                </div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">FinTech Bank</h2>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 tracking-[0.2em] uppercase font-medium mb-8">
                Digital Finance Partner
              </p>
              <h3 className="text-lg text-slate-600 dark:text-slate-300 font-medium">
                Inicia sesión en tu cuenta
              </h3>
            </div>

            {/* Login Card */}
            <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-700">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Usuario Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Usuario
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="text"
                      value={userId}
                      onChange={(e) => setUserId(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none dark:text-white placeholder:text-slate-400"
                      placeholder="tu_usuario"
                      required
                    />
                  </div>
                </div>

                {/* Contraseña Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Contraseña
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none dark:text-white placeholder:text-slate-400"
                      placeholder="••••••••"
                      required
                    />
                  </div>
                </div>

                {/* Remember & Forgot Password */}
                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center text-slate-600 dark:text-slate-400 cursor-pointer">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-600 mr-2"
                    />
                    Recuérdame
                  </label>
                  <a href="#" className="text-indigo-600 hover:underline font-medium">
                    ¿Olvidaste tu contraseña?
                  </a>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
                    {error}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3.5 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all transform active:scale-[0.98] shadow-lg shadow-indigo-600/30 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                  <ArrowRight className="w-5 h-5" />
                </button>
              </form>

              {/* Register Link */}
              <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-700 text-center">
                <p className="text-slate-600 dark:text-slate-400">
                  ¿No tienes cuenta?{' '}
                  <button
                    onClick={onSwitchToRegister}
                    className="text-indigo-600 hover:underline font-bold ml-1"
                  >
                    Regístrate aquí
                  </button>
                </p>
              </div>
            </div>

            {/* Footer */}
            <p className="mt-12 text-center text-xs text-slate-400 dark:text-slate-500 uppercase tracking-widest font-medium">
              © 2024 Fraud Detection Engine. Secure Systems.
            </p>
          </div>

          {/* Dark Mode Toggle Button */}
          <DarkModeToggle />
        </div>

        <style>{`
          @keyframes stream {
            0% { transform: translateY(-100px); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translateY(500px); opacity: 0; }
          }
        `}</style>
      </div>
    </div>
  );
}
