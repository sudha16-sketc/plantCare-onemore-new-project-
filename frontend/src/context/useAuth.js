/**
 * Auth context object + useAuth hook.
 *
 * The context lives here (not in AuthContext.jsx) so the provider file
 * exports only a component, keeping react-refresh fast-refresh happy.
 */

import { createContext, useContext } from 'react';

export const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
