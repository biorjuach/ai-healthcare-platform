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
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
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
        if (error.response?.status === 401) {
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
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
    const response: AxiosResponse<ApiResponse<{ user: User; token: string }>> = await this.api.post('/api/auth/login/', credentials);
    return response.data.data!;
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
    const response: AxiosResponse<ApiResponse<{ user: User; token: string }>> = await this.api.post('/api/auth/register/', userData);
    return response.data.data!;
  }

  async logout(): Promise<void> {
    await this.api.post('/api/auth/logout/');
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.get('/api/auth/profile/');
    return response.data.data!;
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
    const response: AxiosResponse<ApiResponse<SymptomAnalysis>> = await this.api.post('/api/symptoms/analyze/', symptomData);
    return response.data.data!;
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
    const response: AxiosResponse<ApiResponse<SymptomReport>> = await this.api.post('/api/symptoms/submit/', symptomData);
    return response.data.data!;
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
    const response: AxiosResponse<ApiResponse<any>> = await this.api.get('/api/patient/dashboard/');
    return response.data.data!;
  }

  async getPatientSymptoms(): Promise<SymptomReport[]> {
    const response: AxiosResponse<ApiResponse<SymptomReport[]>> = await this.api.get('/api/patient/symptoms/');
    return response.data.data!;
  }

  async getPatientAppointments(): Promise<Appointment[]> {
    const response: AxiosResponse<ApiResponse<Appointment[]>> = await this.api.get('/api/patient/appointments/');
    return response.data.data!;
  }

  // Appointments
  async createAppointment(appointmentData: {
    doctor?: number;
    hospital?: string;
    date: string;
    time: string;
    notes?: string;
    symptoms?: string;
  }): Promise<Appointment> {
    const response: AxiosResponse<ApiResponse<Appointment>> = await this.api.post('/api/appointments/', appointmentData);
    return response.data.data!;
  }

  async updateAppointment(id: number, appointmentData: Partial<Appointment>): Promise<Appointment> {
    const response: AxiosResponse<ApiResponse<Appointment>> = await this.api.put(`/api/appointments/${id}/`, appointmentData);
    return response.data.data!;
  }

  async cancelAppointment(id: number): Promise<void> {
    await this.api.delete(`/api/appointments/${id}/`);
  }

  // Doctors
  async getDoctors(): Promise<Doctor[]> {
    const response: AxiosResponse<ApiResponse<Doctor[]>> = await this.api.get('/api/doctors/');
    return response.data.data!;
  }

  // Emergency
  async getEmergencyAlerts(): Promise<EmergencyAlert[]> {
    const response: AxiosResponse<ApiResponse<EmergencyAlert[]>> = await this.api.get('/api/emergency/alerts/');
    return response.data.data!;
  }

  async updateEmergencyStatus(id: number, status: 'active' | 'resolved' | 'escalated'): Promise<EmergencyAlert> {
    const response: AxiosResponse<ApiResponse<EmergencyAlert>> = await this.api.put(`/api/emergency/update-status/${id}/`, { status });
    return response.data.data!;
  }

  // Health Tips
  async getHealthTips(language: 'en' | 'sw' = 'en'): Promise<HealthTip[]> {
    const response: AxiosResponse<ApiResponse<HealthTip[]>> = await this.api.get(`/api/health-tips/?language=${language}`);
    return response.data.data!;
  }

  // Notifications
  async getNotifications(): Promise<Notification[]> {
    const response: AxiosResponse<ApiResponse<Notification[]>> = await this.api.get('/api/notifications/');
    return response.data.data!;
  }

  async markNotificationAsRead(id: number): Promise<void> {
    await this.api.put(`/api/notifications/${id}/read/`);
  }

  // User Profile
  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.put('/api/auth/profile/', profileData);
    return response.data.data!;
  }

  // Hospital Capacity
  async getHospitalCapacity(): Promise<{
    total_beds: number;
    available_beds: number;
    icu_beds: number;
    available_icu: number;
    emergency_rooms: number;
    available_emergency: number;
  }> {
    const response: AxiosResponse<ApiResponse<any>> = await this.api.get('/api/hospital/capacity/');
    return response.data.data!;
  }
}

export const apiService = new ApiService();
export default apiService;
