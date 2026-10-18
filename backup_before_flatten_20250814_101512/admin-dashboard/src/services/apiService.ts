import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Configuration
const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000,
  healthCheckInterval: 30000, // 30 seconds
};

// Types
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

export interface ConnectionStatus {
  isConnected: boolean;
  lastCheck: Date;
  responseTime: number;
  errorMessage?: string;
  isHealthy: boolean;
}

export type ErrorType = 'network' | 'server' | 'auth' | 'validation' | 'timeout' | 'unknown';

export interface ApiError {
  type: ErrorType;
  message: string;
  status?: number;
  details?: any;
}

// API Service Class
class ApiService {
  private axiosInstance: AxiosInstance;
  private connectionStatus: ConnectionStatus = {
    isConnected: false,
    lastCheck: new Date(),
    responseTime: 0,
    isHealthy: false,
  };
  private healthCheckInterval?: NodeJS.Timeout;
  private retryCount = 0;
  private requestStartTimes = new Map<string, number>();

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
        const requestId = `${config.method}-${config.url}`;
        this.requestStartTimes.set(requestId, Date.now());
        
        // Add authentication token if available
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
      },
      (error) => {
        return Promise.reject(this.createError('network', 'Request failed', error));
      }
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        const requestId = `${response.config.method}-${response.config.url}`;
        const startTime = this.requestStartTimes.get(requestId);
        if (startTime) {
          const responseTime = Date.now() - startTime;
          this.requestStartTimes.delete(requestId);
          
          // Update connection status on successful response
          this.updateConnectionStatus(true, responseTime);
        }

        return response;
      },
      async (error: AxiosError) => {
        const requestId = error.config ? `${error.config.method}-${error.config.url}` : 'unknown';
        const startTime = this.requestStartTimes.get(requestId);
        if (startTime) {
          this.requestStartTimes.delete(requestId);
        }

        const apiError = this.handleError(error);
        
        // Retry logic for certain types of errors
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

  private createError(type: ErrorType, message: string, originalError?: any): ApiError {
    return {
      type,
      message,
      status: originalError?.response?.status,
      details: originalError?.response?.data,
    };
  }

  private handleError(error: AxiosError): ApiError {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return this.createError('timeout', 'Request timed out', error);
    }

    if (!error.response) {
      return this.createError('network', 'Network error - unable to reach server', error);
    }

    const status = error.response.status;
    const message = (error.response.data as any)?.message || error.message;

    switch (status) {
      case 401:
        return this.createError('auth', 'Authentication required', error);
      case 403:
        return this.createError('auth', 'Access denied', error);
      case 404:
        return this.createError('server', 'Resource not found', error);
      case 422:
        return this.createError('validation', 'Validation error', error);
      case 500:
        return this.createError('server', 'Internal server error', error);
      case 502:
      case 503:
      case 504:
        return this.createError('server', 'Service temporarily unavailable', error);
      default:
        return this.createError('unknown', message || 'An unexpected error occurred', error);
    }
  }

  private shouldRetry(error: AxiosError): boolean {
    // Retry on network errors, timeouts, and 5xx server errors
    return (
      !error.response ||
      error.code === 'ECONNABORTED' ||
      (error.response.status >= 500 && error.response.status < 600)
    );
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private updateConnectionStatus(isConnected: boolean, responseTime: number, errorMessage?: string) {
    this.connectionStatus = {
      isConnected,
      lastCheck: new Date(),
      responseTime,
      errorMessage,
      isHealthy: isConnected && responseTime < API_CONFIG.timeout,
    };
  }

  private async performHealthCheck(): Promise<void> {
    try {
      const startTime = Date.now();
      const response = await this.axiosInstance.get('/api/health/', { timeout: 5000 });
      const responseTime = Date.now() - startTime;
      
      this.updateConnectionStatus(true, responseTime);
    } catch (error) {
      this.updateConnectionStatus(false, 0, 'Health check failed');
    }
  }

  private startHealthCheck(): void {
    // Perform initial health check
    this.performHealthCheck();
    
    // Set up periodic health checks
    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck();
    }, API_CONFIG.healthCheckInterval);
  }

  public stopHealthCheck(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
  }

  public getConnectionStatus(): ConnectionStatus {
    return { ...this.connectionStatus };
  }

  public async get<T = any>(url: string, config?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.get<T>(url, config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  public async post<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.post<T>(url, data, config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  public async put<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.put<T>(url, data, config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  public async patch<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.patch<T>(url, data, config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  public async delete<T = any>(url: string, config?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.axiosInstance.delete<T>(url, config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Specific API methods for the dashboard
  public async getDashboardStats(): Promise<ApiResponse<any>> {
    return this.get('/api/analytics/dashboard/');
  }

  public async getEmergencyAlerts(): Promise<ApiResponse<any>> {
    return this.get('/api/emergency/alerts/');
  }

  public async getHospitalCapacity(): Promise<ApiResponse<any>> {
    return this.get('/api/hospital/capacity/');
  }

  public async updateEmergencyStatus(alertId: number, status: string): Promise<ApiResponse<any>> {
    return this.post('/api/emergency/update-status/', {
      alert_id: alertId,
      status: status,
    });
  }

  public async getSymptomAnalysis(): Promise<ApiResponse<any>> {
    return this.get('/api/analytics/symptoms/');
  }

  public async getSystemHealth(): Promise<ApiResponse<any>> {
    return this.get('/api/health/');
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
