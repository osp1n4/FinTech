import React, { createContext, useContext, useState } from 'react';

interface UserContextType {
  userId: string;
  setUserId: (userId: string) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

const USER_ID_STORAGE_KEY = 'fraud_detection_user_id';

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userId, setUserIdState] = useState<string>(() => {
    // Intentar recuperar el userId del localStorage
    const stored = localStorage.getItem(USER_ID_STORAGE_KEY);
    return stored || 'user_demo';
  });

  const setUserId = (newUserId: string) => {
    setUserIdState(newUserId);
    localStorage.setItem(USER_ID_STORAGE_KEY, newUserId);
  };

  return (
    <UserContext.Provider value={{ userId, setUserId }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
