import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  Calendar, 
  AlertTriangle, 
  Heart, 
  TrendingUp, 
  Clock,
  Phone,
  Plus
} from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';

// Debug: Check if apiService is properly imported
console.log('API Service imported:', apiService);
console.log('API Service methods:', Object.keys(apiService));

const HomeScreen: React.FC = () => {
  const { user } = useAuth();
  const isDoctor = user?.user_type === 'doctor';
  
  // Debug logging
  console.log('=== DEBUG INFO ===');
  console.log('User:', user);
  console.log('User type:', user?.user_type);
  console.log('Is Doctor:', isDoctor);
  console.log('==================');
  
  // Use try-catch to handle API service issues
  const { data: dashboard, isLoading, error, refetch } = useQuery(
    isDoctor ? 'doctorDashboard' : 'patientDashboard',
    async () => {
      try {
        console.log('Making API call for:', isDoctor ? 'doctor' : 'patient', 'dashboard');
        if (isDoctor) {
          const result = await apiService.getDoctorDashboard();
          console.log('Doctor dashboard result:', result);
          return result;
        } else {
          const result = await apiService.getPatientDashboard();
          console.log('Patient dashboard result:', result);
          return result;
        }
      } catch (err) {
        console.error('Dashboard API error:', err);
        console.error('Error details:', err);
        // Return a fallback dashboard instead of throwing
        return {
          appointments: [],
          symptoms: [],
          notifications: [],
          recent_activity: [],
          stats: {
            total_appointments: 0,
            upcoming_appointments: 0,
            completed_appointments: 0,
            total_symptoms: 0
          }
        };
      }
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      retry: 1, // Reduce retries to avoid long loading
      retryDelay: 1000, // Wait 1 second between retries
      onSuccess: (data) => {
        console.log('Dashboard data loaded successfully:', data);
      },
      onError: (error) => {
        console.error('Dashboard error:', error);
      },
      // Add error handling to prevent crashes
      onSettled: (data, error) => {
        if (error) {
          console.error('Dashboard query settled with error:', error);
        } else {
          console.log('Dashboard query settled successfully:', data);
        }
      }
    }
  );

  const { data: healthTips } = useQuery(
    'healthTips',
    async () => {
      try {
        return await apiService.getHealthTips('en');
      } catch (err) {
        console.error('Health tips API error:', err);
        return []; // Return empty array as fallback
      }
    },
    {
      staleTime: 300000, // 5 minutes
    }
  );

  const { data: hospitalCapacity } = useQuery(
    'hospitalCapacity',
    async () => {
      try {
        return await apiService.getHospitalCapacity();
      } catch (err) {
        console.error('Hospital capacity API error:', err);
        return null; // Return null as fallback
      }
    },
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  // Show loading only for dashboard, not for other data
  if (isLoading) return <LoadingSpinner />;
  
  // Handle error state gracefully
  if (error) {
    console.error('Dashboard error in render:', error);
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-lg shadow p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Welcome, {user?.first_name || 'User'}!</h1>
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-yellow-400" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Dashboard temporarily unavailable
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>We're having trouble loading your dashboard data. You can still access other features.</p>
                    <button 
                      onClick={() => refetch()}
                      className="mt-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded text-sm"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Debug: Show if we have data
  console.log('Dashboard data:', dashboard);
  console.log('Health tips:', healthTips);
  console.log('Hospital capacity:', hospitalCapacity);

  // Handle both patient and doctor dashboard data
  const recentSymptoms = isDoctor ? [] : (Array.isArray(dashboard?.recent_symptoms) ? dashboard.recent_symptoms : []);
  const upcomingAppointments = isDoctor ? (Array.isArray(dashboard?.today_appointments) ? dashboard.today_appointments : []) : (Array.isArray(dashboard?.upcoming_appointments) ? dashboard.upcoming_appointments : []);
  const healthSummary = isDoctor ? null : (dashboard?.health_summary || { total_symptoms: 0, recent_diagnoses: [], severity_distribution: {} });
  
  // Doctor-specific data
  const emergencyAlerts = isDoctor ? (Array.isArray(dashboard?.emergency_alerts) ? dashboard.emergency_alerts : []) : [];
  const recentPatients = isDoctor ? (Array.isArray(dashboard?.recent_patients) ? dashboard.recent_patients : []) : [];
  const notifications = isDoctor ? (Array.isArray(dashboard?.notifications) ? dashboard.notifications : []) : [];
  const totalAppointmentsToday = isDoctor ? (dashboard?.total_appointments_today || 0) : 0;
  const activeEmergencies = isDoctor ? (dashboard?.active_emergencies || 0) : 0;
  const unreadNotifications = isDoctor ? (dashboard?.unread_notifications || 0) : (dashboard?.unread_notifications || 0);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-danger-600 bg-danger-50';
      case 'high': return 'text-warning-600 bg-warning-50';
      case 'medium': return 'text-primary-600 bg-primary-50';
      case 'low': return 'text-secondary-600 bg-secondary-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const handleEmergencyCall = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        // In a real app, this would trigger emergency services
        alert(`Emergency services notified. Location: ${latitude}, ${longitude}`);
      });
    }
    // Fallback emergency number
    window.open('tel:911', '_self');
  };

  return (
    <div className="space-y-6">
      {/* Test Header - This should always show */}
      <div className="bg-green-100 border border-green-300 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-green-800">Frontend is Working!</h2>
        <p className="text-green-700">If you can see this, the frontend is loading correctly.</p>
      </div>

      {/* Welcome Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome back, {isDoctor ? 'Dr.' : ''} {user?.first_name} {user?.last_name}!
        </h1>
        <p className="text-gray-600">
          {isDoctor ? 'Here\'s your medical dashboard for today' : 'Here\'s your health summary for today'}
        </p>
        {!dashboard && (
          <div className="mt-4 p-4 bg-warning-50 border border-warning-200 rounded-lg">
            <p className="text-warning-700">
              Dashboard data is loading... If this persists, there may be a connection issue with the backend.
            </p>
          </div>
        )}
      </div>

      {/* Health Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {isDoctor ? (
          <>
            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Today's Appointments</p>
                  <p className="text-2xl font-bold text-gray-900">{totalAppointmentsToday}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-danger-100 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-danger-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Emergencies</p>
                  <p className="text-2xl font-bold text-gray-900">{activeEmergencies}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-warning-100 rounded-lg">
                  <Activity className="h-6 w-6 text-warning-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Recent Patients</p>
                  <p className="text-2xl font-bold text-gray-900">{recentPatients.length}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-secondary-100 rounded-lg">
                  <Heart className="h-6 w-6 text-secondary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Unread Notifications</p>
                  <p className="text-2xl font-bold text-gray-900">{unreadNotifications}</p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Activity className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Symptoms</p>
                  <p className="text-2xl font-bold text-gray-900">{healthSummary?.total_symptoms || 0}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-secondary-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-secondary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Upcoming Appointments</p>
                  <p className="text-2xl font-bold text-gray-900">{upcomingAppointments.length}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-warning-100 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-warning-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Unread Alerts</p>
                  <p className="text-2xl font-bold text-gray-900">{unreadNotifications}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-danger-100 rounded-lg">
                  <Heart className="h-6 w-6 text-danger-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Hospital Capacity</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {hospitalCapacity ? `${Math.round((hospitalCapacity.available_beds / hospitalCapacity.total_beds) * 100)}%` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {isDoctor ? (
          <>
            {/* Today's Appointments */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Today's Appointments</h2>
                <Link to="/appointments" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              
              {upcomingAppointments.length > 0 ? (
                <div className="space-y-3">
                  {upcomingAppointments.slice(0, 3).map((appointment: any) => (
                    <div key={appointment.id || Math.random()} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">
                          {appointment.patient?.first_name ? `${appointment.patient.first_name} ${appointment.patient.last_name || ''}` : 'Patient name not available'}
                        </p>
                        <p className="text-sm text-gray-600">
                          {appointment.appointment_date ? format(new Date(appointment.appointment_date), 'MMM dd, yyyy') : 'Date not specified'} at {appointment.appointment_date?.split('T')[1]?.substring(0, 5) || 'TBD'}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        typeof appointment.status === 'string' && appointment.status === 'confirmed' ? 'bg-secondary-100 text-secondary-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {typeof appointment.status === 'string' ? appointment.status : 'unknown'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No appointments scheduled for today</p>
              )}
              
              <Link to="/appointments" className="btn-primary w-full mt-4 flex items-center justify-center">
                <Calendar className="h-4 w-4 mr-2" />
                Manage Appointments
              </Link>
            </div>

            {/* Emergency Alerts */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Emergency Alerts</h2>
                <Link to="/emergencies" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              
              {emergencyAlerts.length > 0 ? (
                <div className="space-y-3">
                  {emergencyAlerts.slice(0, 3).map((alert: any) => (
                    <div key={alert.id || Math.random()} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                      <div>
                        <p className="font-medium text-red-900">
                          {alert.patient?.first_name ? `${alert.patient.first_name} ${alert.patient.last_name || ''}` : 'Patient name not available'}
                        </p>
                        <p className="text-sm text-red-700">{typeof alert.emergency_type === 'string' ? alert.emergency_type : 'Emergency type not specified'}</p>
                      </div>
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                        {typeof alert.severity_level === 'string' ? alert.severity_level : 'Unknown severity'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No active emergency alerts</p>
              )}
              
              <Link to="/emergencies" className="btn-primary w-full mt-4 flex items-center justify-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                View All Emergencies
              </Link>
            </div>
          </>
        ) : (
          <>
            {/* Recent Symptoms */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Recent Symptoms</h2>
                <Link to="/symptoms" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              
              {recentSymptoms.length > 0 ? (
                <div className="space-y-3">
                  {recentSymptoms.slice(0, 3).map((symptom: any) => (
                    <div key={symptom.id || Math.random()} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{typeof symptom.symptoms === 'string' ? symptom.symptoms : 'Unknown symptoms'}</p>
                        <p className="text-sm text-gray-600">{typeof symptom.body_location === 'string' ? symptom.body_location : 'Location not specified'}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(typeof symptom.severity === 'string' ? symptom.severity : 'low')}`}>
                        {typeof symptom.severity === 'string' ? symptom.severity : 'low'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No recent symptoms reported</p>
              )}
              
              <Link to="/symptoms/report" className="btn-primary w-full mt-4 flex items-center justify-center">
                <Plus className="h-4 w-4 mr-2" />
                Report New Symptoms
              </Link>
            </div>

            {/* Upcoming Appointments */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Upcoming Appointments</h2>
                <Link to="/appointments" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              
              {upcomingAppointments.length > 0 ? (
                <div className="space-y-3">
                  {upcomingAppointments.slice(0, 3).map((appointment: any) => (
                    <div key={appointment.id || Math.random()} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{typeof appointment.hospital === 'string' ? appointment.hospital : 'General Hospital'}</p>
                        <p className="text-sm text-gray-600">
                          {appointment.date ? format(new Date(appointment.date), 'MMM dd, yyyy') : 'Date not specified'} at {typeof appointment.time === 'string' ? appointment.time : 'Time not specified'}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        typeof appointment.status === 'string' && appointment.status === 'confirmed' ? 'bg-secondary-100 text-secondary-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {typeof appointment.status === 'string' ? appointment.status : 'unknown'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No upcoming appointments</p>
              )}
              
              <Link to="/appointments" className="btn-primary w-full mt-4 flex items-center justify-center">
                <Plus className="h-4 w-4 mr-2" />
                Schedule Appointment
              </Link>
            </div>
          </>
        )}
      </div>

      {/* Health Tips */}
      {healthTips && Array.isArray(healthTips) && healthTips.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Today's Health Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {healthTips.slice(0, 2).map((tip: any) => (
              <div key={tip.id || Math.random()} className="p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">{typeof tip.title === 'string' ? tip.title : 'Health Tip'}</h3>
                <p className="text-sm text-gray-600">{typeof tip.content === 'string' ? tip.content : 'Content not available'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Emergency Services */}
      <div className="card bg-gradient-to-r from-danger-500 to-danger-600 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold mb-2">Emergency Services</h2>
            <p className="text-danger-100">Need immediate medical attention?</p>
          </div>
          <button
            onClick={handleEmergencyCall}
            className="btn-secondary bg-white text-danger-600 hover:bg-gray-100 flex items-center"
          >
            <Phone className="h-4 w-4 mr-2" />
            Emergency Call
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;
