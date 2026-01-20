import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [adminName, setAdminName] = useState('Admin');
  const [adminInitials, setAdminInitials] = useState('AD');
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Obtener el nombre del admin desde localStorage
    const fullName = localStorage.getItem('admin_full_name');
    if (fullName) {
      setAdminName(fullName);
      // Generar iniciales (primeras letras de cada palabra)
      const initials = fullName
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
      setAdminInitials(initials);
    }
  }, []);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    // Limpiar localStorage
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_id');
    localStorage.removeItem('admin_email');
    localStorage.removeItem('admin_full_name');
    
    // Redirigir al login
    navigate('/login');
  };

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
                 <span className="text-base text-gray-200">{adminName}</span>
                 <div className="relative" ref={dropdownRef}>
                   <button
                     onClick={() => setShowDropdown(!showDropdown)}
                     className="w-12 h-12 rounded-full bg-admin-primary flex items-center justify-center text-white font-semibold hover:bg-admin-primary-700 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-admin-primary focus:ring-offset-2 focus:ring-offset-gray-800"
                   >
                     {adminInitials}
                   </button>
                   
                   {/* Dropdown Menu */}
                   {showDropdown && (
                     <div className="absolute right-0 mt-2 w-56 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-1 z-50">
                       <div className="px-4 py-3 border-b border-gray-700">
                         <p className="text-sm text-gray-400">Sesión iniciada como</p>
                         <p className="text-sm font-medium text-white truncate">{adminName}</p>
                       </div>
                       <button
                         onClick={handleLogout}
                         className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors flex items-center space-x-2"
                       >
                         <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                           <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                         </svg>
                         <span>Cerrar sesión</span>
                       </button>
                     </div>
                   )}
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
