import { useTheme } from '../context/ThemeContext';

export function DarkModeToggle() {
  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <button
      onClick={toggleDarkMode}
      className="fixed bottom-6 right-6 p-3 bg-white dark:bg-slate-800 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 transition-all hover:scale-110 z-50"
      aria-label={darkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
    >
      {darkMode ? (
        <span className="text-amber-400">☀️</span>
      ) : (
        <span className="text-slate-700">🌙</span>
      )}
    </button>
  );
}
