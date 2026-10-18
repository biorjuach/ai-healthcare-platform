import { useState, useEffect, useCallback } from 'react';
import { apiService, ApiResponse, ErrorType } from '../services/apiService';

// Types
export interface UseApiCallOptions<T = any> {
  url?: string;
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  data?: any;
  config?: any;
  autoFetch?: boolean;
  dependencies?: any[];
  onSuccess?: (data: T) => void;
  onError?: (error: any) => void;
  retryOnError?: boolean;
  retryAttempts?: number;
}

export interface UseApiCallReturn<T = any> {
  data: T | null;
  loading: boolean;
  error: any;
  refetch: () => Promise<void>;
  retry: () => Promise<void>;
  clearError: () => void;
  isConnected: boolean;
  responseTime: number;
}

// Main hook for API calls
export function useApiCall<T = any>(options: UseApiCallOptions<T>): UseApiCallReturn<T> {
  const {
    url,
    method = 'GET',
    data,
    config,
    autoFetch = true,
    dependencies = [],
    onSuccess,
    onError,
    retryOnError = true,
    retryAttempts = 3,
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: any;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const [isConnected, setIsConnected] = useState(true);
  const [responseTime, setResponseTime] = useState(0);

  // Monitor connection status
  useEffect(() => {
    const checkConnection = () => {
      const status = apiService.getConnectionStatus();
      setIsConnected(status.isConnected);
      setResponseTime(status.responseTime);
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  const makeRequest = useCallback(async (): Promise<void> => {
    if (!url) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      let response: ApiResponse<T>;

      switch (method) {
        case 'GET':
          response = await apiService.get<T>(url, config);
          break;
        case 'POST':
          response = await apiService.post<T>(url, data, config);
          break;
        case 'PUT':
          response = await apiService.put<T>(url, data, config);
          break;
        case 'PATCH':
          response = await apiService.patch<T>(url, data, config);
          break;
        case 'DELETE':
          response = await apiService.delete<T>(url, config);
          break;
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }

      setState({
        data: response.data,
        loading: false,
        error: null,
      });

      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error,
      }));

      if (onError) {
        onError(error);
      }

      // Auto-retry on network errors if enabled
      if (retryOnError && error.type === 'network' && retryAttempts > 0) {
        setTimeout(() => {
          makeRequest();
        }, 2000);
      }
    }
  }, [url, method, data, config, onSuccess, onError, retryOnError, retryAttempts]);

  const refetch = useCallback(async (): Promise<void> => {
    await makeRequest();
  }, [makeRequest]);

  const retry = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, error: null }));
    await makeRequest();
  }, [makeRequest]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Auto-fetch when dependencies change
  useEffect(() => {
    if (autoFetch) {
      makeRequest();
    }
  }, [autoFetch, ...dependencies]);

  // Re-fetch when connection is restored
  useEffect(() => {
    if (isConnected && state.error && state.error.type === 'network') {
      retry();
    }
  }, [isConnected, state.error]);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    refetch,
    retry,
    clearError,
    isConnected,
    responseTime,
  };
}

// Convenience hooks for specific HTTP methods
export function useGet<T = any>(url: string, options?: Omit<UseApiCallOptions<T>, 'url' | 'method'>) {
  return useApiCall<T>({ url, method: 'GET', ...options });
}

export function usePost<T = any>(url: string, data?: any, options?: Omit<UseApiCallOptions<T>, 'url' | 'method' | 'data'>) {
  return useApiCall<T>({ url, method: 'POST', data, ...options });
}

export function usePut<T = any>(url: string, data?: any, options?: Omit<UseApiCallOptions<T>, 'url' | 'method' | 'data'>) {
  return useApiCall<T>({ url, method: 'PUT', data, ...options });
}

export function usePatch<T = any>(url: string, data?: any, options?: Omit<UseApiCallOptions<T>, 'url' | 'method' | 'data'>) {
  return useApiCall<T>({ url, method: 'PATCH', data, ...options });
}

export function useDelete<T = any>(url: string, options?: Omit<UseApiCallOptions<T>, 'url' | 'method'>) {
  return useApiCall<T>({ url, method: 'DELETE', ...options });
}

// Specialized hooks for dashboard data
export function useDashboardStats() {
  return useApiCall({
    url: '/api/analytics/dashboard/',
    method: 'GET',
    autoFetch: true,
    retryOnError: true,
  });
}

export function useEmergencyAlerts() {
  return useApiCall({
    url: '/api/emergency/alerts/',
    method: 'GET',
    autoFetch: true,
    retryOnError: true,
  });
}

export function useHospitalCapacity() {
  return useApiCall({
    url: '/api/hospital/capacity/',
    method: 'GET',
    autoFetch: true,
    retryOnError: true,
  });
}

export function useSymptomAnalysis() {
  return useApiCall({
    url: '/api/analytics/symptoms/',
    method: 'GET',
    autoFetch: true,
    retryOnError: true,
  });
}

export function useSystemHealth() {
  return useApiCall({
    url: '/api/health/',
    method: 'GET',
    autoFetch: true,
    retryOnError: true,
  });
}

// Hook for connection status
export function useConnectionStatus() {
  const [status, setStatus] = useState(apiService.getConnectionStatus());

  useEffect(() => {
    const updateStatus = () => {
      setStatus(apiService.getConnectionStatus());
    };

    updateStatus();
    const interval = setInterval(updateStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return status;
}
