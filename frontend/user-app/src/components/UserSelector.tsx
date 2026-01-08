import React, { useState } from 'react';
import { useUser } from '@/context/UserContext';

export const UserSelector: React.FC = () => {
  const { userId, setUserId } = useUser();
  const [isEditing, setIsEditing] = useState(false);
  const [tempUserId, setTempUserId] = useState(userId);

  const handleSave = () => {
    if (tempUserId.trim()) {
      setUserId(tempUserId.trim());
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setTempUserId(userId);
    setIsEditing(false);
  };

  const quickUsers = [
    { id: 'user_demo', label: 'Demo User' },
    { id: 'user_alice', label: 'Alice' },
    { id: 'user_bob', label: 'Bob' },
    { id: 'user_charlie', label: 'Charlie' },
    { id: 'Paula05', label: 'Paula05' },
  ];

  if (isEditing) {
    return (
      <div className="flex items-center gap-2 bg-white rounded-lg px-3 py-2 shadow-sm border border-gray-200">
        <span className="text-sm text-gray-600">Usuario:</span>
        <input
          type="text"
          value={tempUserId}
          onChange={(e) => setTempUserId(e.target.value)}
          className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="user_id"
          autoFocus
        />
        <button
          onClick={handleSave}
          className="px-2 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
        >
          ✓
        </button>
        <button
          onClick={handleCancel}
          className="px-2 py-1 bg-gray-400 text-white text-sm rounded hover:bg-gray-500"
        >
          ✕
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {/* Selector rápido */}
      <select
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        className="px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        {quickUsers.map((user) => (
          <option key={user.id} value={user.id}>
            {user.label}
          </option>
        ))}
        {/* Mostrar usuario actual si no está en la lista predefinida */}
        {!quickUsers.find(u => u.id === userId) && (
          <option value={userId}>
            {userId}
          </option>
        )}
      </select>

      {/* Botón para editar manualmente */}
      <button
        onClick={() => setIsEditing(true)}
        className="px-3 py-2 text-sm text-gray-600 hover:text-indigo-600 hover:bg-gray-50 rounded-lg transition-colors"
        title="Cambiar usuario"
      >
        ✏️
      </button>

      {/* Indicador de usuario actual */}
      <div className="hidden sm:flex items-center gap-1 px-2 py-1 bg-indigo-50 text-indigo-700 rounded text-xs font-medium">
        <span>👤</span>
        <span>{userId}</span>
      </div>
    </div>
  );
};
