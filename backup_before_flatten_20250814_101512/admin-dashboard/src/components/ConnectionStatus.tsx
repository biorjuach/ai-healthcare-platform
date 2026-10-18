import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Chip, 
  Typography, 
  Alert, 
  Button, 
  IconButton, 
  Tooltip,
  Collapse,
  LinearProgress,
  Snackbar
} from '@mui/material';
import { 
  CheckCircle, 
  Error, 
  Info, 
  Refresh, 
  ExpandMore, 
  ExpandLess,
  Warning,
  SignalCellular4Bar,
  SignalCellular0Bar
} from '@mui/icons-material';
import { useConnectionStatus } from '../hooks/useApiCall';
import { apiService } from '../services/apiService';

interface ConnectionStatusProps {
  backendConnected?: boolean;
  realTimeUpdates?: boolean;
  showDetails?: boolean;
  onRetry?: () => void;
  compact?: boolean;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  backendConnected: propBackendConnected,
  realTimeUpdates = true,
  showDetails = true,
  onRetry,
  compact = false
}) => {
  const connectionStatus = useConnectionStatus();
  const [expanded, setExpanded] = useState(false);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Use prop value if provided, otherwise use connection status
  const isConnected = propBackendConnected !== undefined ? propBackendConnected : connectionStatus.isConnected;
  const responseTime = connectionStatus.responseTime;
  const errorMessage = connectionStatus.errorMessage;

  const handleRetry = async () => {
    try {
      await apiService.getSystemHealth();
      setSnackbarMessage('Connection restored successfully!');
      setShowSnackbar(true);
      if (onRetry) {
        onRetry();
      }
    } catch (error) {
      setSnackbarMessage('Failed to restore connection. Please check your network.');
      setShowSnackbar(true);
    }
  };

  const getStatusColor = () => {
    if (isConnected) {
      if (responseTime < 500) return 'success';
      if (responseTime < 1000) return 'warning';
      return 'error';
    }
    return 'error';
  };

  const getStatusIcon = () => {
    if (isConnected) {
      if (responseTime < 500) return <SignalCellular4Bar />;
      if (responseTime < 1000) return <Warning />;
      return <Error />;
    }
    return <SignalCellular0Bar />;
  };

  const getStatusText = () => {
    if (isConnected) {
      if (responseTime < 500) return 'Excellent';
      if (responseTime < 1000) return 'Good';
      return 'Slow';
    }
    return 'Disconnected';
  };

  const getResponseTimeColor = () => {
    if (responseTime < 500) return '#4caf50';
    if (responseTime < 1000) return '#ff9800';
    return '#f44336';
  };

  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          icon={getStatusIcon()}
          label={getStatusText()}
          color={getStatusColor() as any}
          size="small"
          variant="outlined"
        />
        {isConnected && (
          <Typography variant="caption" color="textSecondary">
            {responseTime}ms
          </Typography>
        )}
        {!isConnected && (
          <Tooltip title="Retry connection">
            <IconButton size="small" onClick={handleRetry}>
              <Refresh />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 2 }}>
      {/* Main Status Alert */}
      <Alert 
        severity={isConnected ? 'success' : 'warning'}
        icon={getStatusIcon()}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {!isConnected && (
              <Button
                size="small"
                onClick={handleRetry}
                startIcon={<Refresh />}
                sx={{ minWidth: 'auto' }}
              >
                Retry
              </Button>
            )}
            {showDetails && (
              <IconButton
                size="small"
                onClick={() => setExpanded(!expanded)}
                sx={{ p: 0.5 }}
              >
                {expanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            )}
          </Box>
        }
        sx={{ mb: 1 }}
      >
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {isConnected 
              ? 'Backend server is connected and responding' 
              : 'Backend server is offline - using mock data'
            }
          </Typography>
          {isConnected && (
            <Typography variant="caption" color="textSecondary">
              Response time: {responseTime}ms • Last check: {connectionStatus.lastCheck.toLocaleTimeString()}
            </Typography>
          )}
        </Box>
      </Alert>

      {/* Connection Details */}
      <Collapse in={expanded && showDetails}>
        <Box sx={{ mb: 2 }}>
          <Alert severity="info" icon={<Info />} sx={{ mb: 1 }}>
            <Typography variant="body2">
              To connect to the backend, start the Django server with: 
              <code style={{ 
                marginLeft: 8, 
                backgroundColor: '#f5f5f5', 
                padding: '2px 4px',
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>
                python manage.py runserver 8000
              </code>
            </Typography>
          </Alert>

          {/* Status Indicators */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            <Chip
              icon={isConnected ? <CheckCircle /> : <Error />}
              label={isConnected ? 'Backend Connected' : 'Backend Offline'}
              color={isConnected ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
            <Chip
              icon={realTimeUpdates ? <CheckCircle /> : <Error />}
              label={realTimeUpdates ? 'Real-time Enabled' : 'Real-time Disabled'}
              color={realTimeUpdates ? 'success' : 'default'}
              variant="outlined"
              size="small"
            />
            <Chip
              icon={connectionStatus.isHealthy ? <CheckCircle /> : <Error />}
              label={connectionStatus.isHealthy ? 'System Healthy' : 'System Issues'}
              color={connectionStatus.isHealthy ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
          </Box>

          {/* Performance Metrics */}
          {isConnected && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Performance Metrics
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Typography variant="body2" color="textSecondary">
                  Response Time:
                </Typography>
                <Typography 
                  variant="body2" 
                  fontWeight="medium"
                  sx={{ color: getResponseTimeColor() }}
                >
                  {responseTime}ms
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={Math.min((responseTime / 1000) * 100, 100)}
                  sx={{ 
                    flexGrow: 1, 
                    height: 6, 
                    borderRadius: 3,
                    backgroundColor: '#e0e0e0',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getResponseTimeColor(),
                    }
                  }}
                />
              </Box>
            </Box>
          )}

          {/* Error Details */}
          {errorMessage && (
            <Alert severity="error" sx={{ mb: 1 }}>
              <Typography variant="body2">
                <strong>Error:</strong> {errorMessage}
              </Typography>
            </Alert>
          )}

          {/* Connection History */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Connection History
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Last successful connection: {connectionStatus.lastCheck.toLocaleString()}
            </Typography>
          </Box>
        </Box>
      </Collapse>

      {/* Snackbar for notifications */}
      <Snackbar
        open={showSnackbar}
        autoHideDuration={4000}
        onClose={() => setShowSnackbar(false)}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      />
    </Box>
  );
};

export default ConnectionStatus; 