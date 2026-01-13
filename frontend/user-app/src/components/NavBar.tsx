import { UserSelector } from './UserSelector';
import { NotificationDropdown } from './NotificationDropdown';

type NotificationType = 'success' | 'warning' | 'info';

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: NotificationType;
  read: boolean;
}

interface NavBarProps {
  readonly currentPage: string;
  readonly notifications: Notification[];
  readonly showNotifications: boolean;
  readonly onPageChange: (page: 'home' | 'new-transaction' | 'my-transactions') => void;
  readonly onToggleNotifications: () => void;
  readonly onCloseNotifications: () => void;
}

export const NavBar = ({
  currentPage,
  notifications,
  showNotifications,
  onPageChange,
  onToggleNotifications,
  onCloseNotifications
}: NavBarProps) => (
  <nav className="bg-white shadow-sm border-b sticky top-0 z-10">
    <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold bg-gradient-to-r from-user-primary to-indigo-700 bg-clip-text text-transparent">
        FinTech Bank
      </h1>
      <div className="flex gap-4 items-center">
        <UserSelector />
        {/* Campanita de notificaciones */}
        <div className="relative">
          <button 
            onClick={onToggleNotifications}
            className="relative p-2 text-gray-600 hover:text-user-primary transition-colors" 
            title="Notificaciones"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            {/* Badge de notificaciones */}
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            )}
          </button>
          
          {/* Dropdown de notificaciones */}
          {showNotifications && (
            <NotificationDropdown 
              notifications={notifications} 
              onClose={onCloseNotifications} 
            />
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onPageChange('home')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentPage === 'home'
                ? 'bg-user-primary text-white'
                : 'text-gray-600 hover:text-user-primary hover:bg-gray-50'
            }`}
          >
            Inicio
          </button>
          <button
            onClick={() => onPageChange('new-transaction')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentPage === 'new-transaction'
                ? 'bg-user-primary text-white'
                : 'text-gray-600 hover:text-user-primary hover:bg-gray-50'
            }`}
          >
            Nueva Transacción
          </button>
          <button
            onClick={() => onPageChange('my-transactions')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentPage === 'my-transactions'
                ? 'bg-user-primary text-white'
                : 'text-gray-600 hover:text-user-primary hover:bg-gray-50'
            }`}
          >
            Mis Transacciones
          </button>
        </div>
      </div>
    </div>
  </nav>
);
