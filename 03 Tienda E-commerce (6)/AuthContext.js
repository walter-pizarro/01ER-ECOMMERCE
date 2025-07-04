import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokens, setTokens] = useState({
    access_token: localStorage.getItem('access_token'),
    refresh_token: localStorage.getItem('refresh_token')
  });

  // Initialize auth state on app load
  useEffect(() => {
    initializeAuth();
  }, []);

  // Set up token refresh interval
  useEffect(() => {
    if (tokens.access_token) {
      const interval = setInterval(() => {
        refreshTokens();
      }, 50 * 60 * 1000); // Refresh every 50 minutes (tokens expire in 1 hour)

      return () => clearInterval(interval);
    }
  }, [tokens.access_token]);

  const initializeAuth = async () => {
    const accessToken = localStorage.getItem('access_token');
    
    if (accessToken) {
      try {
        // Verify token and get user info
        const response = await apiClient.get('/auth/me', {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        
        if (response.data.success) {
          setUser(response.data.user);
          setTokens({
            access_token: accessToken,
            refresh_token: localStorage.getItem('refresh_token')
          });
        } else {
          // Token is invalid, clear it
          clearAuth();
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        clearAuth();
      }
    }
    
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password
      });

      if (response.data.success) {
        const { user: userData, tokens: tokenData } = response.data;
        
        // Store tokens
        localStorage.setItem('access_token', tokenData.access_token);
        localStorage.setItem('refresh_token', tokenData.refresh_token);
        
        // Update state
        setUser(userData);
        setTokens(tokenData);
        
        return { success: true, user: userData };
      } else {
        return { 
          success: false, 
          error: response.data.error || 'Login failed' 
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Network error' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await apiClient.post('/auth/register', userData);

      if (response.data.success) {
        // Auto-login after successful registration
        return await login(userData.email, userData.password);
      } else {
        return { 
          success: false, 
          error: response.data.error || 'Registration failed' 
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Network error' 
      };
    }
  };

  const logout = async () => {
    try {
      // Call logout endpoint if token exists
      if (tokens.access_token) {
        await apiClient.post('/auth/logout', {}, {
          headers: { Authorization: `Bearer ${tokens.access_token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuth();
    }
  };

  const refreshTokens = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      clearAuth();
      return false;
    }

    try {
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      if (response.data.success) {
        const { tokens: newTokens } = response.data;
        
        // Store new tokens
        localStorage.setItem('access_token', newTokens.access_token);
        localStorage.setItem('refresh_token', newTokens.refresh_token);
        
        // Update state
        setTokens(newTokens);
        
        return true;
      } else {
        clearAuth();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuth();
      return false;
    }
  };

  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setTokens({ access_token: null, refresh_token: null });
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await apiClient.put('/auth/profile', profileData, {
        headers: { Authorization: `Bearer ${tokens.access_token}` }
      });

      if (response.data.success) {
        setUser(response.data.user);
        return { success: true, user: response.data.user };
      } else {
        return { 
          success: false, 
          error: response.data.error || 'Profile update failed' 
        };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Network error' 
      };
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      }, {
        headers: { Authorization: `Bearer ${tokens.access_token}` }
      });

      if (response.data.success) {
        return { success: true };
      } else {
        return { 
          success: false, 
          error: response.data.error || 'Password change failed' 
        };
      }
    } catch (error) {
      console.error('Password change error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Network error' 
      };
    }
  };

  // Helper function to check if user has specific role
  const hasRole = (role) => {
    return user?.roles?.includes(role) || false;
  };

  // Helper function to check if user is admin
  const isAdmin = () => {
    return hasRole('admin') || hasRole('manager');
  };

  const value = {
    user,
    tokens,
    loading,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshTokens,
    hasRole,
    isAdmin,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

