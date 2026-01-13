import { useEffect } from 'react';

type ToastProps = Readonly<{ id: string; title?: string; message: string; type?: 'info'|'success'|'error'|'warning'; onClose?: (id: string)=>void }>;

export default function Toast({ id, title, message, type='info', onClose }: ToastProps) {
  useEffect(() => {
    const t = setTimeout(() => onClose?.(id), 4500);
    return () => clearTimeout(t);
  }, [id, onClose]);

  const style = {
    info: 'bg-white text-slate-800 border border-slate-200',
    success: 'bg-emerald-50 text-emerald-800 border border-emerald-100',
    error: 'bg-rose-50 text-rose-800 border border-rose-100',
    warning: 'bg-amber-50 text-amber-800 border border-amber-100',
  }[type];

  const icon = { info: 'ℹ️', success: '✅', error: '⛔', warning: '⚠️' }[type];

  return (
    <div className={`shadow rounded-lg px-4 py-3 ${style} max-w-sm`} role="alert">
      <div className="flex gap-3 items-start">
        <div className="text-2xl leading-none">{icon}</div>
        <div className="flex-1">
          {title && <div className="font-semibold text-sm mb-1">{title}</div>}
          <div className="text-sm">{message}</div>
        </div>
      </div>
    </div>
  );
}
