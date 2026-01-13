import { useEffect } from 'react';

type ToastProps = Readonly<{ id: string; title?: string; message: string; type?: 'info'|'success'|'error'|'warning'; onClose?: (id:string)=>void }>;

export default function Toast({ id, title, message, type='info', onClose }: ToastProps){
  useEffect(()=>{
    const t = setTimeout(()=> onClose?.(id), 4500);
    return ()=> clearTimeout(t);
  },[id,onClose]);

  const bg = { info: 'bg-slate-800 text-white', success: 'bg-emerald-600 text-white', error:'bg-rose-600 text-white', warning:'bg-amber-600 text-white'}[type];
  const icon = { info:'ℹ️', success:'✅', error:'⛔', warning:'⚠️'}[type];

  return (
    <div className={`rounded-lg shadow px-4 py-3 ${bg} max-w-md`} role="alert">
      <div className="flex gap-3 items-start">
        <div className="text-2xl">{icon}</div>
        <div className="flex-1">
          {title && <div className="font-semibold">{title}</div>}
          <div className="text-sm">{message}</div>
        </div>
      </div>
    </div>
  );
}
