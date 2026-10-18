import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ConnectionStatus } from '../types';
import apiService from '../services/api';

interface ConnectionContextType {
  connectionStatus: ConnectionStatus;
  checkConnection: () => Promise<void>;
}

const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);

const initialState: ConnectionStatus = {
  isConnected: false,
  responseTime: 0,
  lastChecked: new Date().toISOString(),
};

export const ConnectionStatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(initialState);

  const checkConnection = async () => {
    try {
      const status = await apiService.healthCheck();
      setConnectionStatus(status);
    } catch (error) {
      setConnectionStatus({
        isConnected: false,
        responseTime: 0,
        lastChecked: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  // Check connection on mount and set up periodic checks
  useEffect(() => {
    checkConnection();
    
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const value: ConnectionContextType = {
    connectionStatus,
    checkConnection,
  };

  return (
    <ConnectionContext.Provider value={value}>
      {children}
    </ConnectionContext.Provider>
  );
};

export const useConnectionStatus = (): ConnectionContextType => {
  const context = useContext(ConnectionContext);
  if (context === undefined) {
    throw new Error('useConnectionStatus must be used within a ConnectionStatusProvider');
  }
  return context;
};
