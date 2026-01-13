type NotificationType = 'success' | 'warning' | 'info';

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: NotificationType;
  read: boolean;
}

interface NotificationDropdownProps {
  notifications: Notification[];
  onClose: () => void;
}

const getNotificationColor = (type: NotificationType): string => {
  if (type === 'success') return 'bg-green-500';
  if (type === 'warning') return 'bg-yellow-500';
  return 'bg-blue-500';
};

const NotificationItem = ({ notification }: { notification: Notification }) => (
  <div className="p-4 hover:bg-gray-50 border-b border-gray-100 last:border-b-0">
    <div className="flex items-start gap-3">
      <div className={`w-2 h-2 rounded-full mt-2 ${getNotificationColor(notification.type)}`}></div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{notification.title}</p>
        <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
        <p className="text-xs text-gray-400 mt-1">{notification.time}</p>
      </div>
    </div>
  </div>
);

const EmptyNotifications = () => (
  <div className="p-8 text-center text-gray-500">
    <div className="w-12 h-12 mx-auto mb-2 opacity-30">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
      </svg>
    </div>
    <p className="text-sm">No tienes notificaciones</p>
  </div>
);

export const NotificationDropdown = ({ notifications, onClose }: NotificationDropdownProps) => {
  return (
    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">Notificaciones</h3>
      </div>
      <div className="max-h-96 overflow-y-auto">
        {notifications.length === 0 ? (
          <EmptyNotifications />
        ) : (
          notifications.map((notification) => (
            <NotificationItem key={notification.id} notification={notification} />
          ))
        )}
      </div>
      <div className="p-3 border-t border-gray-200 text-center">
        <button 
          onClick={onClose}
          className="text-sm text-user-primary hover:text-indigo-700 font-medium"
        >
          Cerrar
        </button>
      </div>
    </div>
  );
};
