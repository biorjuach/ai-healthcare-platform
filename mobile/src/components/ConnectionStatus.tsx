import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Animated,
} from 'react-native';
import { apiService, ConnectionStatus } from '../services/apiService';

interface ConnectionStatusProps {
  onRetry?: () => void;
  showDetails?: boolean;
}

const ConnectionStatusComponent: React.FC<ConnectionStatusProps> = ({
  onRetry,
  showDetails = false,
}) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    isConnected: false,
    lastCheck: new Date(),
    responseTime: 0,
  });
  const [isVisible, setIsVisible] = useState(false);
  const pulseAnim = new Animated.Value(1);

  useEffect(() => {
    // Initial check
    checkConnection();

    // Set up periodic checks
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!connectionStatus.isConnected) {
      setIsVisible(true);
      startPulseAnimation();
    } else {
      setIsVisible(false);
      stopPulseAnimation();
    }
  }, [connectionStatus.isConnected]);

  const checkConnection = () => {
    const status = apiService.getConnectionStatus();
    setConnectionStatus(status);
  };

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 0.5,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopPulseAnimation = () => {
    pulseAnim.stopAnimation();
    pulseAnim.setValue(1);
  };

  const handleRetry = () => {
    checkConnection();
    if (onRetry) {
      onRetry();
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
  };

  const getStatusColor = () => {
    return connectionStatus.isConnected ? '#4CAF50' : '#F44336';
  };

  const getStatusText = () => {
    if (connectionStatus.isConnected) {
      return `Connected (${connectionStatus.responseTime}ms)`;
    }
    return connectionStatus.error || 'Connection Lost';
  };

  const getStatusIcon = () => {
    return connectionStatus.isConnected ? '●' : '○';
  };

  if (!isVisible && connectionStatus.isConnected) {
    return null;
  }

  return (
    <Animated.View
      style={[
        styles.container,
        {
          opacity: pulseAnim,
          backgroundColor: getStatusColor(),
        },
      ]}
    >
      <View style={styles.content}>
        <Text style={styles.statusText}>
          {getStatusIcon()} {getStatusText()}
        </Text>
        
        {showDetails && (
          <Text style={styles.detailsText}>
            Last check: {connectionStatus.lastCheck.toLocaleTimeString()}
          </Text>
        )}

        <View style={styles.actions}>
          <TouchableOpacity style={styles.retryButton} onPress={handleRetry}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.dismissButton} onPress={handleDismiss}>
            <Text style={styles.dismissText}>×</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  statusText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  detailsText: {
    color: 'white',
    fontSize: 12,
    opacity: 0.8,
    marginLeft: 8,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  retryButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 8,
  },
  retryText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  dismissButton: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dismissText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default ConnectionStatusComponent;
