import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URL } from '../config';

// API Response Types
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  error?: string;
}

export interface ConnectionStatus {
  isConnected: boolean;
  lastCheck: Date;
  responseTime: number;
  error?: string;
}

// Error Types
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

export interface ApiError {
  type: ErrorType;
  message: string;
  statusCode?: number;
  originalError?: any;
}

// Configuration
const API_CONFIG = {
  baseURL: API_URL,
  timeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000,
  healthCheckInterval: 30000, // 30 seconds
};

class ApiService {
  private axiosInstance: AxiosInstance;
  private connectionStatus: ConnectionStatus = {
    isConnected: false,
    lastCheck: new Date(),
    responseTime: 0,
  };
  private healthCheckInterval?: NodeJS.Timeout;
  private retryCount = 0;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.startHealthCheck();
  }

  private setupInterceptors() {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(this.createApiError(error, ErrorType.UNKNOWN_ERROR));
      }
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        this.updateConnectionStatus(true, Date.now() - response.config.metadata?.startTime || 0);
        return response;
      },
      async (error: AxiosError) => {
        const apiError = this.createApiError(error);
        
        // Handle retries for network errors
        if (this.shouldRetry(error) && this.retryCount < API_CONFIG.retryAttempts) {
          this.retryCount++;
          await this.delay(API_CONFIG.retryDelay * this.retryCount);
          return this.axiosInstance.request(error.config!);
        }

        this.retryCount = 0;
        this.updateConnectionStatus(false, 0, apiError.message);
        return Promise.reject(apiError);
      }
    );
  }

  private createApiError(error: AxiosError, type?: ErrorType): ApiError {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return {
        type: ErrorType.TIMEOUT_ERROR,
        message: 'Request timed out. Please check your connection.',
        statusCode: 408,
        originalError: error,
      };
    }

    if (!error.response) {
      return {
        type: ErrorType.NETWORK_ERROR,
        message: 'Network error. Please check your internet connection.',
        originalError: error,
      };
    }

    const statusCode = error.response.status;
    let errorType = type || ErrorType.UNKNOWN_ERROR;
    let message = 'An unexpected error occurred.';

    switch (statusCode) {
      case 401:
        errorType = ErrorType.AUTH_ERROR;
        message = 'Authentication required. Please log in again.';
        break;
      case 403:
        errorType = ErrorType.AUTH_ERROR;
        message = 'Access denied. You do not have permission for this action.';
        break;
      case 404:
        message = 'Resource not found.';
        break;
      case 422:
        errorType = ErrorType.VALIDATION_ERROR;
        message = 'Invalid data provided. Please check your input.';
        break;
      case 500:
        errorType = ErrorType.SERVER_ERROR;
        message = 'Server error. Please try again later.';
        break;
      default:
        if (statusCode >= 500) {
          errorType = ErrorType.SERVER_ERROR;
          message = 'Server error. Please try again later.';
        } else if (statusCode >= 400) {
          errorType = ErrorType.VALIDATION_ERROR;
          message = 'Request error. Please check your input.';
        }
    }

    return {
      type: errorType,
      message: error.response.data?.message || message,
      statusCode,
      originalError: error,
    };
  }

  private shouldRetry(error: AxiosError): boolean {
    return (
      error.code === 'ECONNABORTED' ||
      error.message.includes('timeout') ||
      (!error.response && error.code !== 'ERR_CANCELED') ||
      (error.response && error.response.status >= 500)
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private updateConnectionStatus(isConnected: boolean, responseTime: number, error?: string) {
    this.connectionStatus = {
      isConnected,
      lastCheck: new Date(),
      responseTime,
      error,
    };
  }

  private startHealthCheck() {
    this.healthCheckInterval = setInterval(async () => {
      try {
        const startTime = Date.now();
        await this.axiosInstance.get('/health/');
        this.updateConnectionStatus(true, Date.now() - startTime);
      } catch (error) {
        this.updateConnectionStatus(false, 0, 'Health check failed');
      }
    }, API_CONFIG.healthCheckInterval);
  }

  private getAuthToken(): string | null {
    // This should be implemented based on your auth storage
    return null;
  }

  // Public methods
  public getConnectionStatus(): ConnectionStatus {
    return { ...this.connectionStatus };
  }

  public async request<T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    url: string,
    data?: any,
    config?: any
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.request({
        method,
        url,
        data,
        ...config,
        metadata: { startTime: Date.now() },
      });

      return {
        status: 'success',
        data: response.data,
      };
    } catch (error) {
      const apiError = error as ApiError;
      return {
        status: 'error',
        error: apiError.message,
      };
    }
  }

  // Convenience methods
  public async get<T = any>(url: string, config?: any): Promise<ApiResponse<T>> {
    return this.request('GET', url, undefined, config);
  }

  public async post<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    return this.request('POST', url, data, config);
  }

  public async put<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    return this.request('PUT', url, data, config);
  }

  public async patch<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    return this.request('PATCH', url, data, config);
  }

  public async delete<T = any>(url: string, config?: any): Promise<ApiResponse<T>> {
    return this.request('DELETE', url, undefined, config);
  }

  // Cleanup
  public destroy() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
  }
}

// Singleton instance
export const apiService = new ApiService();

// Export types
export type { ApiResponse, ConnectionStatus, ApiError };
