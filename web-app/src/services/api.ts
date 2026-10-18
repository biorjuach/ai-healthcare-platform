import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  SymptomReport, 
  SymptomAnalysis, 
  Appointment, 
  Doctor, 
  EmergencyAlert, 
  HealthTip, 
  Notification,
  LoginCredentials,
  ApiResponse,
  ConnectionStatus
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        console.log('=== API REQUEST DEBUG ===');
        console.log('Request URL:', config.url);
        console.log('Auth token:', token ? 'Present' : 'Missing');
        console.log('Headers:', config.headers);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        console.log('Final headers:', config.headers);
        console.log('========================');
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        console.error('Error config:', error.config);
        console.error('Error response:', error.response);
        
        // Only auto-logout for 401 errors on protected endpoints, not on login/register
        if (error.response?.status === 401 && 
            !error.config.url?.includes('/api/auth/login/') && 
            !error.config.url?.includes('/api/auth/register/')) {
          console.log('401 error on protected endpoint, logging out user');
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          // Don't redirect immediately, let the component handle it
          // window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck(): Promise<ConnectionStatus> {
    const startTime = Date.now();
    try {
      const response = await this.api.get('/api/health/');
      const endTime = Date.now();
      return {
        isConnected: true,
        responseTime: endTime - startTime,
        lastChecked: new Date().toISOString(),
      };
    } catch (error) {
      return {
        isConnected: false,
        responseTime: 0,
        lastChecked: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    const response: AxiosResponse = await this.api.post('/api/auth/login/', credentials);
    // Backend returns { success: true, data: { user: {...}, token: "..." } }
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Login failed');
  }

  async register(userData: {
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
  }): Promise<{ user: User; token: string }> {
    const response: AxiosResponse = await this.api.post('/api/auth/register/', userData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Registration failed');
  }

  async logout(): Promise<void> {
    await this.api.post('/api/auth/logout/');
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse = await this.api.get('/api/auth/profile/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get user profile');
  }

  // Symptom Analysis
  async analyzeSymptoms(symptomData: {
    symptoms: string;
    body_location: string;
    duration: string;
    severity: string;
    description: string;
    language: 'en' | 'sw';
    location_data?: {
      latitude: number;
      longitude: number;
      address: string;
    };
  }): Promise<SymptomAnalysis> {
    const response: AxiosResponse = await this.api.post('/api/symptoms/analyze/', symptomData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Symptom analysis failed');
  }

  async submitSymptomReport(symptomData: {
    symptoms: string;
    body_location: string;
    duration: string;
    severity: string;
    description: string;
    language: 'en' | 'sw';
    location_data?: {
      latitude: number;
      longitude: number;
      address: string;
    };
  }): Promise<SymptomReport> {
    const response: AxiosResponse = await this.api.post('/api/symptoms/submit/', symptomData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to submit symptom report');
  }

  // Patient Dashboard
  async getPatientDashboard(): Promise<{
    recent_symptoms: SymptomReport[];
    upcoming_appointments: Appointment[];
    health_summary: {
      total_symptoms: number;
      recent_diagnoses: string[];
      severity_distribution: Record<string, number>;
    };
    unread_notifications: number;
  }> {
    const response: AxiosResponse = await this.api.get('/api/patient/dashboard/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get dashboard data');
  }

  async getPatientSymptoms(): Promise<SymptomReport[]> {
    const response: AxiosResponse = await this.api.get('/api/patient/symptoms/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get symptoms');
  }

  async getPatientAppointments(): Promise<Appointment[]> {
    const response: AxiosResponse = await this.api.get('/api/patient/appointments/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get appointments');
  }

  // Appointments - These endpoints need to be implemented in backend
  async createAppointment(appointmentData: {
    doctor?: number;
    hospital?: string;
    date: string;
    time: string;
    notes?: string;
    symptoms?: string;
  }): Promise<Appointment> {
    const response: AxiosResponse = await this.api.post('/api/appointments/', appointmentData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to create appointment');
  }

  async updateAppointment(id: number, appointmentData: Partial<Appointment>): Promise<Appointment> {
    const response: AxiosResponse = await this.api.put(`/api/appointments/${id}/`, appointmentData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to update appointment');
  }

  async cancelAppointment(id: number): Promise<void> {
    await this.api.delete(`/api/appointments/${id}/`);
  }

  // Doctors - This endpoint needs to be implemented in backend
  async getDoctors(): Promise<Doctor[]> {
    const response: AxiosResponse = await this.api.get('/api/doctors/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get doctors');
  }

  // Emergency
  async getEmergencyAlerts(): Promise<{ emergency_alerts: EmergencyAlert[] }> {
    const response: AxiosResponse = await this.api.get('/api/emergency/alerts/');
    return response.data;
  }

  async updateEmergencyStatus(alertId: number, status: string, notes?: string): Promise<EmergencyAlert> {
    const response: AxiosResponse = await this.api.post('/api/emergency/update-status/', { 
      alert_id: alertId, 
      status, 
      notes 
    });
    if (response.data.status === 'success') {
      return response.data.emergency_alert;
    }
    throw new Error(response.data.message || 'Failed to update emergency status');
  }

  // Doctor-specific endpoints (duplicates removed - using versions below)

  // Health Tips
  async getHealthTips(language: 'en' | 'sw' = 'en'): Promise<HealthTip[]> {
    const response: AxiosResponse = await this.api.get(`/api/health-tips/?language=${language}`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get health tips');
  }

  // Notifications - This endpoint needs to be implemented in backend
  async getNotifications(): Promise<Notification[]> {
    const response: AxiosResponse = await this.api.get('/api/notifications/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get notifications');
  }

  async markNotificationAsRead(id: number): Promise<void> {
    await this.api.put(`/api/notifications/${id}/read/`);
  }

  // User Profile
  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response: AxiosResponse = await this.api.put('/api/auth/profile/', profileData);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to update profile');
  }

  // Hospital Capacity
  async getHospitalCapacity(): Promise<{
    total_beds: number;
    available_beds: number;
    icu_beds: number;
    available_icu: number;
    emergency_rooms: number;
    available_emergency: number;
    average_wait_time?: number;
  }> {
    const response: AxiosResponse = await this.api.get('/api/hospital/capacity/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get hospital capacity');
  }

  // Patient Management (for doctors)
  async getPatients(): Promise<any[]> {
    const response: AxiosResponse = await this.api.get('/api/patients/');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get patients');
  }

  async getPatientDetails(patientId: number): Promise<any> {
    const response: AxiosResponse = await this.api.get(`/api/patients/${patientId}/`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to get patient details');
  }

  // Doctor Dashboard
  async getDoctorDashboard(): Promise<any> {
    const response: AxiosResponse = await this.api.get('/api/doctor/dashboard/');
    // Backend returns data directly, not wrapped in success/data structure
    return response.data;
  }


}

export const apiService = new ApiService();
export default apiService;
