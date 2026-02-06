/**
 * Authentication hook for RedFlag AI
 *
 * Manages user authentication state and provides login/logout functions.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api/client';
import { User, LoginRequest, SignupRequest, TokenResponse } from '@/lib/types/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false,
  });

  /**
   * Initialize auth state from localStorage
   */
  useEffect(() => {
    const initAuth = () => {
      const token = localStorage.getItem('access_token');
      const userStr = localStorage.getItem('user');

      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          setAuthState({
            user,
            token,
            isLoading: false,
            isAuthenticated: true,
          });
        } catch (error) {
          console.error('Failed to parse user from localStorage:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setAuthState({
            user: null,
            token: null,
            isLoading: false,
            isAuthenticated: false,
          });
        }
      } else {
        setAuthState({
          user: null,
          token: null,
          isLoading: false,
          isAuthenticated: false,
        });
      }
    };

    initAuth();
  }, []);

  /**
   * Login user
   */
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    try {
      // Login request (FastAPI OAuth2 format)
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post<TokenResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token } = response.data;

      // Store token
      localStorage.setItem('access_token', access_token);

      // Fetch user details
      const userResponse = await api.get<User>('/auth/me');
      const user = userResponse.data;

      // Store user
      localStorage.setItem('user', JSON.stringify(user));

      // Update state
      setAuthState({
        user,
        token: access_token,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }, []);

  /**
   * Signup new user
   */
  const signup = useCallback(async (data: SignupRequest): Promise<void> => {
    try {
      // Signup request
      await api.post('/auth/signup', data);

      // Auto-login after signup
      await login(data.email, data.password);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  }, [login]);

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    setAuthState({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,
    });
  }, []);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      const response = await api.get<User>('/auth/me');
      const user = response.data;

      localStorage.setItem('user', JSON.stringify(user));

      setAuthState((prev) => ({
        ...prev,
        user,
      }));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      logout();
      throw error;
    }
  }, [logout]);

  return {
    user: authState.user,
    token: authState.token,
    isLoading: authState.isLoading,
    isAuthenticated: authState.isAuthenticated,
    login,
    signup,
    logout,
    refreshUser,
  };
};
