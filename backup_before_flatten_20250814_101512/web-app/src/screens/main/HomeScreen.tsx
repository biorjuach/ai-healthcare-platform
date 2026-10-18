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

// Debug: Check if apiService is properly imported
console.log('API Service imported:', apiService);
console.log('API Service methods:', Object.keys(apiService));
import LoadingSpinner from '../../components/LoadingSpinner';

const HomeScreen: React.FC = () => {
  // Use try-catch to handle API service issues
  const { data: dashboard, isLoading, error, refetch } = useQuery(
    'patientDashboard',
    async () => {
      try {
        return await apiService.getPatientDashboard();
      } catch (err) {
        console.error('Dashboard API error:', err);
        throw err;
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
  
  // Don't show error screen, just continue with fallback data
  if (error) {
    console.error('Dashboard error:', error);
  }

  // Debug: Show if we have data
  console.log('Dashboard data:', dashboard);
  console.log('Health tips:', healthTips);
  console.log('Hospital capacity:', hospitalCapacity);

  const recentSymptoms = dashboard?.recent_symptoms || [];
  const upcomingAppointments = dashboard?.upcoming_appointments || [];
  const healthSummary = dashboard?.health_summary || { total_symptoms: 0, recent_diagnoses: [], severity_distribution: {} };

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
          Welcome back!
        </h1>
        <p className="text-gray-600">
          Here's your health summary for today
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
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Activity className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Symptoms</p>
              <p className="text-2xl font-bold text-gray-900">{healthSummary.total_symptoms || 0}</p>
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
              <p className="text-2xl font-bold text-gray-900">{dashboard?.unread_notifications || 0}</p>
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
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                <div key={symptom.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{symptom.symptoms}</p>
                    <p className="text-sm text-gray-600">{symptom.body_location}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(symptom.severity)}`}>
                    {symptom.severity}
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
                <div key={appointment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{appointment.hospital || 'General Hospital'}</p>
                    <p className="text-sm text-gray-600">
                      {format(new Date(appointment.date), 'MMM dd, yyyy')} at {appointment.time}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    appointment.status === 'confirmed' ? 'bg-secondary-100 text-secondary-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {appointment.status}
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
      </div>

      {/* Health Tips */}
      {healthTips && healthTips.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Today's Health Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {healthTips.slice(0, 2).map((tip: any) => (
              <div key={tip.id} className="p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">{tip.title}</h3>
                <p className="text-sm text-gray-600">{tip.content}</p>
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
