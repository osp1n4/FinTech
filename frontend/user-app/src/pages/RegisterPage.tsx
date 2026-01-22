import { useState } from 'react';
import { Lock, Mail, User, UserPlus, ArrowLeft } from 'lucide-react';
import { DarkModeToggle } from '../components/DarkModeToggle';
import { useTheme } from '../context/ThemeContext';

interface RegisterPageProps {
  onRegisterSuccess: (email: string) => void;
  onSwitchToLogin: () => void;
}

export function RegisterPage({ onRegisterSuccess, onSwitchToLogin }: RegisterPageProps) {
  const [userId, setUserId] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { darkMode } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          email,
          password,
          full_name: fullName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al registrar usuario');
      }

      setSuccess(true);
      setTimeout(() => {
        onRegisterSuccess(email);
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Error al registrar usuario');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className={darkMode ? 'dark' : ''}>
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4">
          <div className="w-full max-w-md">
            <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-700 text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <UserPlus className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">¡Registro Exitoso!</h2>
              <p className="text-gray-600 dark:text-slate-400 mb-4">
                Tu cuenta ha sido creada correctamente. Se ha enviado un correo de verificación a <strong>{email}</strong>.
              </p>
              <p className="text-sm text-gray-500 dark:text-slate-500">
                Por favor, verifica tu email antes de iniciar sesión.
              </p>
              <p className="text-sm text-indigo-600 dark:text-indigo-400 mt-2">
                Redirigiendo a verificación...
              </p>
            </div>
          </div>
        </div>
        <DarkModeToggle />
      </div>
    );
  }

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
                Prevenga el fraude en tiempo real y asegure cada transacción con un motor avanzado que evalúa riesgos automáticamente.
              </p>
            </div>

            {/* Stats Card */}
            <div className="backdrop-blur-lg bg-white/5 rounded-xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-teal-500/20 rounded-lg flex items-center justify-center">
                    <UserPlus className="w-5 h-5 text-teal-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Seguridad garantizada</p>
                    <p className="text-white font-medium">Crea tu cuenta en segundos</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Register Form */}
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
              <h3 className="text-lg text-slate-700 dark:text-slate-200 font-medium">
                Crea tu cuenta nueva
              </h3>
            </div>

            {/* Register Card */}
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
                      minLength={3}
                    />
                  </div>
                </div>

                {/* Full Name Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Nombre Completo
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none dark:text-white placeholder:text-slate-400"
                      placeholder="Juan Pérez"
                      required
                    />
                  </div>
                </div>

                {/* Email Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none dark:text-white placeholder:text-slate-400"
                      placeholder="tu@email.com"
                      required
                    />
                  </div>
                </div>

                {/* Password Field */}
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
                      minLength={6}
                    />
                  </div>
                </div>

                {/* Confirm Password Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Confirmar Contraseña
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none dark:text-white placeholder:text-slate-400"
                      placeholder="••••••••"
                      required
                    />
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 dark:bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 dark:hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    'Registrando...'
                  ) : (
                    <>
                      <UserPlus className="w-5 h-5" />
                      Crear Cuenta
                    </>
                  )}
                </button>
              </form>

              {/* Login Link */}
              <div className="mt-6 text-center">
                <button
                  onClick={onSwitchToLogin}
                  className="text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-700 dark:hover:text-indigo-300 flex items-center justify-center gap-2 mx-auto transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Volver al Login
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <DarkModeToggle />
    </div>
  );
}
