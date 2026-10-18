/**
 * Authentication context backed by the PlantCare API (JWT).
 *
 * The token is stored in localStorage; passwords are never stored on the
 * client — they are hashed server-side with bcrypt. This replaces the old
 * localStorage btoa() "auth" which was reversible and not real authentication.
 */

import React, { useState, useEffect, useCallback } from 'react';
import * as api from '../api/client';
import { AuthContext } from './useAuth.js';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!api.getToken()) {
        setLoading(false);
        return;
      }
      try {
        const me = await api.fetchMe();
        if (!cancelled) setUser(me);
      } catch {
        // Token invalid/expired — clear it silently.
        api.setToken(null);
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

  const logout = useCallback(() => {
    api.setToken(null);
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
