import React, { createContext, useContext, useState } from 'react';

interface UserContextType {
  userId: string;
  setUserId: (userId: string) => void;
  isAuthenticated: boolean;
  token: string | null;
  login: (userId: string, token: string, email: string, fullName: string) => void;
  logout: () => void;
  userEmail: string | null;
  userFullName: string | null;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

const USER_ID_STORAGE_KEY = 'fraud_detection_user_id';
const TOKEN_STORAGE_KEY = 'fraud_detection_token';
const USER_EMAIL_STORAGE_KEY = 'fraud_detection_user_email';
const USER_FULLNAME_STORAGE_KEY = 'fraud_detection_user_fullname';

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userId, setUserIdState] = useState<string>(() => {
    const stored = localStorage.getItem(USER_ID_STORAGE_KEY);
    return stored || '';
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  });

  const [userEmail, setUserEmail] = useState<string | null>(() => {
    return localStorage.getItem(USER_EMAIL_STORAGE_KEY);
  });

  const [userFullName, setUserFullName] = useState<string | null>(() => {
    return localStorage.getItem(USER_FULLNAME_STORAGE_KEY);
  });

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return !!localStorage.getItem(TOKEN_STORAGE_KEY);
  });

  const setUserId = (newUserId: string) => {
    setUserIdState(newUserId);
    localStorage.setItem(USER_ID_STORAGE_KEY, newUserId);
  };

  const login = (userId: string, token: string, email: string, fullName: string) => {
    setUserIdState(userId);
    setToken(token);
    setUserEmail(email);
    setUserFullName(fullName);
    setIsAuthenticated(true);
    
    localStorage.setItem(USER_ID_STORAGE_KEY, userId);
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    localStorage.setItem(USER_EMAIL_STORAGE_KEY, email);
    localStorage.setItem(USER_FULLNAME_STORAGE_KEY, fullName);
  };

  const logout = () => {
    setUserIdState('');
    setToken(null);
    setUserEmail(null);
    setUserFullName(null);
    setIsAuthenticated(false);
    
    localStorage.removeItem(USER_ID_STORAGE_KEY);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_EMAIL_STORAGE_KEY);
    localStorage.removeItem(USER_FULLNAME_STORAGE_KEY);
  };

  return (
    <UserContext.Provider value={{ 
      userId, 
      setUserId, 
      isAuthenticated, 
      token, 
      login, 
      logout,
      userEmail,
      userFullName
    }}>
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
