import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ConnectionStatusProvider } from './contexts/ConnectionContext';
import LoginScreen from './screens/auth/LoginScreen';
import RegisterScreen from './screens/auth/RegisterScreen';
import RoleBasedRoute from './components/RoleBasedRoute';
import LoadingSpinner from './components/LoadingSpinner';
import apiService from './services/api';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth();

  // Health check query
  const { data: connectionStatus } = useQuery(
    'healthCheck',
    apiService.healthCheck,
    {
      refetchInterval: 30000, // Check every 30 seconds
      refetchOnWindowFocus: false,
    }
  );

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginScreen />} />
        <Route path="/register" element={<RegisterScreen />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return <RoleBasedRoute />;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ConnectionStatusProvider>
        <AppRoutes />
      </ConnectionStatusProvider>
    </AuthProvider>
  );
};

export default App;
