import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/rules', label: 'Reglas', icon: '⚙️' },
    { path: '/transactions', label: 'Transacciones', icon: '💳' },
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-admin-surface border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
             <div className="flex items-center justify-between">
               <div className="flex items-center space-x-6">
                 <img src="assets/logo-full.svg" alt="Fintech Bank-Admin" className="h-28" />
               </div>

               <div className="hidden md:flex items-center justify-center flex-1">
                 <div className="flex items-center space-x-8">
                   {navItems.map((item) => (
                     <Link
                       key={item.path}
                       to={item.path}
                       role="button"
                       aria-label={item.label}
                       className={`
                         px-6 py-3 rounded-full text-base font-semibold shadow-sm transform transition-all duration-150
                         ${
                           location.pathname === item.path
                             ? 'bg-gradient-to-r from-admin-primary to-admin-primary-700 text-white scale-105'
                             : 'bg-transparent text-gray-300 hover:bg-admin-hover hover:text-white hover:scale-105'
                         }
                       `}
                     >
                       {item.label}
                     </Link>
                   ))}
                 </div>
               </div>

               <div className="flex items-center space-x-6">
                 <span className="text-base text-gray-200">María G.</span>
                 <div className="w-12 h-12 rounded-full bg-admin-primary flex items-center justify-center text-white font-semibold">
                   MG
                 </div>
               </div>
             </div>
        </div>
      </header>

      {/* Navigation moved into header for compact layout */}

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">{children}</main>
    </div>
  );
};

export default Layout;
