/**
 * Authentication context backed by the PlantCare API (JWT).
 * Token is stored in AsyncStorage; passwords live only server-side.
 */

import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import * as api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const token = await api.getToken();
        if (!token) return;
        const me = await api.fetchMe();
        if (!cancelled) setUser(me);
      } catch {
        await api.setToken(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const signup = useCallback(async (email, password, username) => {
    const created = await api.register(email, username, password);
    setUser(created);
    return created;
  }, []);

  const login = useCallback(async (email, password) => {
    const logged = await api.login(email, password);
    setUser(logged);
    return logged;
  }, []);

  const logout = useCallback(async () => {
    await api.setToken(null);
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (fields) => {
    const updated = await api.updateMe(fields);
    setUser(updated);
    return updated;
  }, []);

  const value = {
    user,
    loading,
    signup,
    login,
    logout,
    updateProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
