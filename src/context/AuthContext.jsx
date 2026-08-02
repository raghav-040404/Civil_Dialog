import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';
import { tokenStorage } from '../utils/tokenStorage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = tokenStorage.getUser();
    const token = tokenStorage.getToken();
    if (storedUser && token) {
      setUser(storedUser);
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (credentials) => {
    const data = await authService.login(credentials);
    tokenStorage.setToken(data.access_token);
    if (data.refresh_token) tokenStorage.setRefreshToken(data.refresh_token);
    tokenStorage.setUser(data.user);
    setUser(data.user);
    return data;
  }, []);

  const register = useCallback(async (userData) => {
    const data = await authService.register(userData);
    tokenStorage.setToken(data.access_token);
    if (data.refresh_token) tokenStorage.setRefreshToken(data.refresh_token);
    tokenStorage.setUser(data.user);
    setUser(data.user);
    return data;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      tokenStorage.clearAll();
      setUser(null);
    }
  }, []);

  const updateUser = useCallback((updates) => {
    const updated = { ...user, ...updates };
    tokenStorage.setUser(updated);
    setUser(updated);
  }, [user]);

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser, isAdmin, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

export default AuthContext;
