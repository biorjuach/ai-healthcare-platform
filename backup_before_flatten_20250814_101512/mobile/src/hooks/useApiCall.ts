import { useState, useEffect, useCallback } from 'react';
import { apiService, ApiResponse, ErrorType } from '../services/apiService';

interface UseApiCallOptions<T> {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  data?: any;
  autoFetch?: boolean;
  fallbackData?: T;
  retryOnError?: boolean;
  retryAttempts?: number;
  retryDelay?: number;
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
  onRetry?: () => void;
}

interface UseApiCallReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  retry: () => Promise<void>;
  clearError: () => void;
  isConnected: boolean;
}

export function useApiCall<T = any>(options: UseApiCallOptions<T>): UseApiCallReturn<T> {
  const {
    url,
    method = 'GET',
    data,
    autoFetch = true,
    fallbackData,
    retryOnError = true,
    retryAttempts = 3,
    retryDelay = 1000,
    onSuccess,
    onError,
    onRetry,
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: string | null;
    retryCount: number;
  }>({
    data: fallbackData || null,
    loading: false,
    error: null,
    retryCount: 0,
  });

  const [isConnected, setIsConnected] = useState(true);

  // Monitor connection status
  useEffect(() => {
    const checkConnection = () => {
      const status = apiService.getConnectionStatus();
      setIsConnected(status.isConnected);
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  const makeRequest = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      let response: ApiResponse<T>;

      switch (method) {
        case 'GET':
          response = await apiService.get<T>(url);
          break;
        case 'POST':
          response = await apiService.post<T>(url, data);
          break;
        case 'PUT':
          response = await apiService.put<T>(url, data);
          break;
        case 'PATCH':
          response = await apiService.patch<T>(url, data);
          break;
        case 'DELETE':
          response = await apiService.delete<T>(url);
          break;
        default:
          throw new Error('Invalid HTTP method');
      }

      if (response.status === 'success' && response.data) {
        setState(prev => ({
          ...prev,
          data: response.data,
          loading: false,
          retryCount: 0,
        }));
        onSuccess?.(response.data);
      } else {
        throw new Error(response.error || 'Request failed');
      }
    } catch (error: any) {
      const errorMessage = error.message || 'An unexpected error occurred';
      
      setState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false,
        retryCount: prev.retryCount + 1,
      }));

      onError?.(errorMessage);

      // Auto-retry logic
      if (retryOnError && state.retryCount < retryAttempts) {
        setTimeout(() => {
          makeRequest();
        }, retryDelay * (state.retryCount + 1));
      }
    }
  }, [url, method, data, retryOnError, retryAttempts, retryDelay, state.retryCount, onSuccess, onError]);

  const refetch = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, retryCount: 0 }));
    await makeRequest();
  }, [makeRequest]);

  const retry = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, retryCount: 0 }));
    onRetry?.();
    await makeRequest();
  }, [makeRequest, onRetry]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      makeRequest();
    }
  }, [autoFetch, makeRequest]);

  // Re-fetch when connection is restored
  useEffect(() => {
    if (isConnected && state.error && state.retryCount > 0) {
      refetch();
    }
  }, [isConnected, state.error, state.retryCount, refetch]);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    refetch,
    retry,
    clearError,
    isConnected,
  };
}

// Specialized hooks for common operations
export function useGet<T = any>(url: string, options?: Partial<UseApiCallOptions<T>>) {
  return useApiCall<T>({ url, method: 'GET', ...options });
}

export function usePost<T = any>(url: string, data?: any, options?: Partial<UseApiCallOptions<T>>) {
  return useApiCall<T>({ url, method: 'POST', data, autoFetch: false, ...options });
}

export function usePut<T = any>(url: string, data?: any, options?: Partial<UseApiCallOptions<T>>) {
  return useApiCall<T>({ url, method: 'PUT', data, autoFetch: false, ...options });
}

export function usePatch<T = any>(url: string, data?: any, options?: Partial<UseApiCallOptions<T>>) {
  return useApiCall<T>({ url, method: 'PATCH', data, autoFetch: false, ...options });
}

export function useDelete<T = any>(url: string, options?: Partial<UseApiCallOptions<T>>) {
  return useApiCall<T>({ url, method: 'DELETE', autoFetch: false, ...options });
}
