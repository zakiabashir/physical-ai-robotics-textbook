import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext({
  user: null,
  token: null,
  login: async () => {},
  logout: async () => {},
  register: async () => {},
  loading: true,
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    // Only access localStorage on client side
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('authUser');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    try {
      const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();

      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to get user info');
      }

      const userData = await userResponse.json();

      // Store token and user
      if (typeof window !== 'undefined') {
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('authUser', JSON.stringify(userData));
      }

      setToken(data.access_token);
      setUser(userData);

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  }, []);

  const register = useCallback(async (username, password, email) => {
    try {
      const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
          email: email || '',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error.message };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      if (token) {
        const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app';
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call success
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
      }
      setToken(null);
      setUser(null);
    }
  }, [token]);

  // Google Sign-In handler
  const googleSignIn = useCallback(async (googleToken) => {
    try {
      const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: googleToken,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Google Sign-In failed');
      }

      const data = await response.json();

      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to get user info');
      }

      const userData = await userResponse.json();

      // Store token and user
      if (typeof window !== 'undefined') {
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('authUser', JSON.stringify(userData));
      }

      setToken(data.access_token);
      setUser(userData);

      return { success: true };
    } catch (error) {
      console.error('Google Sign-In error:', error);
      return { success: false, error: error.message };
    }
  }, []);

  const value = {
    user,
    token,
    login,
    logout,
    register,
    googleSignIn,
    loading,
    isAuthenticated: !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};