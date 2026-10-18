export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  emergency_contact?: string;
  insurance_info?: string;
  medical_history?: string;
  allergies?: string[];
  medications?: string[];
  user_type?: 'patient' | 'doctor' | 'admin';
  patient_profile?: PatientProfile;
  doctor_profile?: DoctorProfile;
}

export interface PatientProfile {
  id: number;
  user: number;
  medical_history: string;
  allergies: string;
  emergency_contacts: any[];
  blood_type?: string;
  insurance_info: any;
}

export interface DoctorProfile {
  id: number;
  user: number;
  specialization: string;
  license_number: string;
  hospital_affiliation: string;
  years_of_experience: number;
  availability: string[];
  consultation_fee: number;
}

export interface SymptomReport {
  id: number;
  patient: number;
  symptoms: string;
  body_location: string;
  duration: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  location_data?: {
    latitude: number;
    longitude: number;
    address: string;
  };
  language: 'en' | 'sw';
  created_at: string;
  updated_at: string;
}

export interface SymptomAnalysis {
  id: number;
  symptom_report: number;
  analysis_result: {
    severity: 'low' | 'medium' | 'high' | 'critical';
    emergency_detected: boolean;
    predicted_diseases: string[];
    recommended_doctors: string[];
    treatment_suggestions: string[];
    urgency_level: 'routine' | 'urgent' | 'emergency';
  };
  ai_confidence: number;
  created_at: string;
}

export interface Appointment {
  id: number;
  patient: number;
  doctor?: number;
  hospital?: string;
  date: string;
  time: string;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  symptoms?: string;
  created_at: string;
  updated_at: string;
}

export interface Doctor {
  id: number;
  name: string;
  specialization: string;
  hospital: string;
  phone_number: string;
  email: string;
  availability: string[];
  rating: number;
  experience_years: number;
}

export interface EmergencyAlert {
  id: number;
  patient: number;
  symptom_report: number;
  status: 'active' | 'resolved' | 'escalated';
  severity: 'low' | 'medium' | 'high' | 'critical';
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  created_at: string;
  resolved_at?: string;
}

export interface HealthTip {
  id: number;
  title: string;
  content: string;
  category: 'general' | 'nutrition' | 'exercise' | 'mental_health' | 'prevention';
  language: 'en' | 'sw';
  created_at: string;
}

export interface Notification {
  id: number;
  user: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  created_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

export interface ConnectionStatus {
  isConnected: boolean;
  responseTime: number;
  lastChecked: string;
  error?: string;
}
