import React from 'react';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { useConnectionStatus } from '../contexts/ConnectionContext';

const ConnectionStatus: React.FC = () => {
  const { connectionStatus, checkConnection } = useConnectionStatus();

  const getStatusColor = () => {
    if (!connectionStatus.isConnected) return 'text-danger-600';
    if (connectionStatus.responseTime > 2000) return 'text-warning-600';
    return 'text-secondary-600';
  };

  const getStatusIcon = () => {
    if (!connectionStatus.isConnected) {
      return <WifiOff className="h-4 w-4 animate-pulse" />;
    }
    if (connectionStatus.responseTime > 2000) {
      return <AlertCircle className="h-4 w-4" />;
    }
    return <Wifi className="h-4 w-4" />;
  };

  const getStatusText = () => {
    if (!connectionStatus.isConnected) return 'Disconnected';
    if (connectionStatus.responseTime > 2000) return 'Slow';
    return 'Connected';
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`flex items-center space-x-1 ${getStatusColor()}`}>
        {getStatusIcon()}
        <span className="text-xs font-medium">{getStatusText()}</span>
      </div>
      
      {connectionStatus.isConnected && (
        <span className="text-xs text-gray-500">
          {connectionStatus.responseTime}ms
        </span>
      )}
      
      {!connectionStatus.isConnected && (
        <button
          onClick={checkConnection}
          className="text-xs text-primary-600 hover:text-primary-700 underline"
        >
          Retry
        </button>
      )}
    </div>
  );
};

export default ConnectionStatus;
