import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
        {label}
      </label>
      <input
        className={`
          w-full h-12 px-4 rounded-lg border
          ${error ? 'border-red-300 focus:ring-red-500 focus:border-red-500 dark:border-red-800 dark:focus:ring-red-500' : 'border-gray-300 focus:ring-user-primary focus:border-user-primary dark:border-slate-700 dark:focus:ring-indigo-500 dark:focus:border-indigo-500'}
          focus:outline-none focus:ring-2
          text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500
          dark:bg-slate-900
          transition-colors duration-200
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
};
