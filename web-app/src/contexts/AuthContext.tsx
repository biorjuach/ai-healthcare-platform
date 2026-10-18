import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthState, LoginCredentials } from '../types';
import apiService from '../services/api';
import toast from 'react-hot-toast';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: {
    username: string;
    password: string;
    email: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    date_of_birth?: string;
    gender?: string;
    address?: string;
    emergency_contact?: string;
    medical_history?: string;
    allergies?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User }
  | { type: 'SET_TOKEN'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: Partial<User> };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_USER':
      return { ...state, user: action.payload, isAuthenticated: true, loading: false };
    case 'SET_TOKEN':
      return { ...state, token: action.payload };
    case 'LOGOUT':
      return { user: null, token: null, isAuthenticated: false, loading: false };
    case 'UPDATE_USER':
      return { ...state, user: state.user ? { ...state.user, ...action.payload } : null };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing auth on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('authToken');
      const userData = localStorage.getItem('user');

      console.log('=== AUTH INITIALIZATION ===');
      console.log('Token from localStorage:', token ? 'Present' : 'Missing');
      console.log('User data from localStorage:', userData ? 'Present' : 'Missing');

      if (token && userData) {
        try {
          dispatch({ type: 'SET_TOKEN', payload: token });
          const user = JSON.parse(userData);
          console.log('Parsed user data:', user);
          dispatch({ type: 'SET_USER', payload: user });
          
          // Don't validate token immediately - let the user stay logged in
          // Token validation will happen on the first API call
          console.log('Auth data restored from localStorage');
        } catch (error) {
          console.error('Error parsing user data:', error);
          // Clear invalid data
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        console.log('No auth data found, setting loading to false');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
      console.log('==========================');
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      console.log('=== LOGIN ATTEMPT ===');
      console.log('Credentials:', credentials);
      dispatch({ type: 'SET_LOADING', payload: true });
      const { user, token } = await apiService.login(credentials);
      
      console.log('Login successful, user:', user);
      console.log('Login successful, token:', token ? 'Present' : 'Missing');
      
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      dispatch({ type: 'SET_TOKEN', payload: token });
      dispatch({ type: 'SET_USER', payload: user });
      
      // Small delay to ensure state is set before any redirects
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('========================');
      toast.success('Login successful!');
    } catch (error) {
      console.error('Login error in AuthContext:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
      
      // More specific error messages
      let errorMessage = 'Login failed. Please check your credentials.';
      if (error instanceof Error) {
        if (error.message.includes('Network Error')) {
          errorMessage = 'Network error. Please check your connection.';
        } else if (error.message.includes('timeout')) {
          errorMessage = 'Request timeout. Please try again.';
        } else if (error.message.includes('401')) {
          errorMessage = 'Invalid username or password.';
        }
      }
      
      toast.error(errorMessage);
      throw error;
    }
  };

  const register = async (userData: {
    username: string;
    password: string;
    email: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
    date_of_birth?: string;
    gender?: string;
    address?: string;
    emergency_contact?: string;
    medical_history?: string;
    allergies?: string;
  }) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const { user, token } = await apiService.register(userData);
      
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      dispatch({ type: 'SET_TOKEN', payload: token });
      dispatch({ type: 'SET_USER', payload: user });
      
      toast.success('Registration successful!');
    } catch (error) {
      dispatch({ type: 'SET_LOADING', payload: false });
      toast.error('Registration failed. Please check your information.');
      throw error;
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API error:', error);
    } finally {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      dispatch({ type: 'LOGOUT' });
      toast.success('Logged out successfully');
    }
  };

  const updateUser = async (userData: Partial<User>) => {
    try {
      const updatedUser = await apiService.updateProfile(userData);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      dispatch({ type: 'SET_USER', payload: updatedUser });
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
      throw error;
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
