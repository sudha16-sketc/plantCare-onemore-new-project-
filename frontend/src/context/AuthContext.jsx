import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [plants, setPlants] = useState([]);

  // Initialize from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedPlants = localStorage.getItem('plants');
    
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('user');
      }
    }
    
    if (storedPlants) {
      try {
        setPlants(JSON.parse(storedPlants));
      } catch (error) {
        console.error('Error parsing stored plants:', error);
        localStorage.removeItem('plants');
      }
    }
    
    setLoading(false);
  }, []);

  // Save user to localStorage when it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);

  // Save plants to localStorage when they change
  useEffect(() => {
    localStorage.setItem('plants', JSON.stringify(plants));
  }, [plants]);

  const signup = (email, password, username) => {
    // Check if user already exists
    const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
    const userExists = existingUsers.some((u) => u.email === email);
    
    if (userExists) {
      throw new Error('User already exists');
    }

    // Create new user
    const newUser = {
      id: Date.now().toString(),
      email,
      username,
      password: btoa(password), // Basic encoding (not secure - for demo only)
      createdAt: new Date().toISOString(),
    };

    // Store user in users list
    existingUsers.push(newUser);
    localStorage.setItem('users', JSON.stringify(existingUsers));

    // Set current user
    setUser({
      id: newUser.id,
      email: newUser.email,
      username: newUser.username,
      createdAt: newUser.createdAt,
    });

    return true;
  };

  const login = (email, password) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const foundUser = users.find((u) => u.email === email && u.password === btoa(password));

    if (!foundUser) {
      throw new Error('Invalid email or password');
    }

    setUser({
      id: foundUser.id,
      email: foundUser.email,
      username: foundUser.username,
      createdAt: foundUser.createdAt,
    });

    return true;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const addPlant = (plantData) => {
    const newPlant = {
      id: Date.now().toString(),
      ...plantData,
      addedAt: new Date().toISOString(),
    };

    setPlants([...plants, newPlant]);
    return newPlant;
  };

  const removePlant = (plantId) => {
    setPlants(plants.filter((p) => p.id !== plantId));
  };

  const updateUserProfile = (username, email) => {
    if (!user) return;

    const updatedUser = {
      ...user,
      username,
      email,
    };

    setUser(updatedUser);

    // Also update in users list
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const userIndex = users.findIndex((u) => u.id === user.id);
    if (userIndex !== -1) {
      users[userIndex] = {
        ...users[userIndex],
        username,
        email,
      };
      localStorage.setItem('users', JSON.stringify(users));
    }
  };

  const value = {
    user,
    loading,
    plants,
    signup,
    login,
    logout,
    addPlant,
    removePlant,
    updateUserProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
