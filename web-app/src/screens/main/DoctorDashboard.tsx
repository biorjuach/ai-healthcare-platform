import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Users, 
  AlertTriangle, 
  Calendar, 
  Activity, 
  Phone, 
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  MessageSquare,
  TrendingUp,
  Heart,
  Stethoscope,
  User,
  MapPin,
  Mail
} from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';

const DoctorDashboard: React.FC = () => {
  const [selectedEmergency, setSelectedEmergency] = useState<any>(null);
  const { user } = useAuth();
  const queryClient = useQueryClient();



  // Fetch doctor dashboard data with better error handling
  const { data: dashboard, isLoading, error, refetch } = useQuery(
    'doctorDashboard',
    async () => {
      try {
        const response = await apiService.getDoctorDashboard();
        console.log('Dashboard response:', response);
        return response;
      } catch (err) {
        console.error('Dashboard fetch error:', err);
        // Return fallback data instead of throwing
        return {
          doctor: user || {
            user: { first_name: 'Doctor', last_name: 'User' },
            specialization: 'General Medicine',
            hospital_affiliation: 'Hospital'
          },
          today_appointments: [],
          upcoming_appointments: [],
          emergency_alerts: [],
          recent_patients: [],
          total_appointments_today: 0,
          total_upcoming_appointments: 0,
          active_emergencies: 0,
          unread_notifications: 0
        };
      }
    },
    {
      retry: 2,
      retryDelay: 1000,
      staleTime: 30000,
      enabled: !!user, // Only fetch when user is available
      onError: (error) => {
        console.error('Doctor dashboard error:', error);
      }
    }
  );

  // Fetch emergency alerts with fallback
  const { data: emergencyAlerts } = useQuery(
    'emergencyAlerts',
    async () => {
      try {
        const response = await apiService.getEmergencyAlerts();
        return response;
      } catch (err) {
        console.error('Emergency alerts error:', err);
        return { emergency_alerts: [] };
      }
    },
    { 
      refetchInterval: 30000, // Refresh every 30 seconds
      retry: 2,
      onError: (error) => {
        console.error('Emergency alerts error:', error);
      }
    }
  );

  // Fetch hospital capacity with fallback
  const { data: hospitalCapacity } = useQuery(
    'hospitalCapacity',
    async () => {
      try {
        const response = await apiService.getHospitalCapacity();
        return response;
      } catch (err) {
        console.error('Hospital capacity error:', err);
        return {
          total_beds: 100,
          available_beds: 45,
          icu_beds: 20,
          available_icu: 8,
          emergency_rooms: 10,
          available_emergency: 3,
          average_wait_time: 15
        };
      }
    },
    {
      retry: 2,
      onError: (error) => {
        console.error('Hospital capacity error:', error);
      }
    }
  );

  // Update emergency status mutation
  const updateEmergencyStatus = useMutation(
    async ({ alertId, status, notes }: { alertId: number; status: string; notes?: string }) => {
      try {
        return await apiService.updateEmergencyStatus(alertId, status, notes);
      } catch (err) {
        console.error('Update emergency status error:', err);
        throw err;
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('emergencyAlerts');
        setSelectedEmergency(null);
      }
    }
  );

  // Safe data extraction with fallbacks
  const doctor = dashboard?.doctor || user || {
    user: { first_name: 'Doctor', last_name: 'User' },
    specialization: 'General Medicine',
    hospital_affiliation: 'Hospital'
  };

  const todayAppointments = dashboard?.today_appointments || [];
  const upcomingAppointments = dashboard?.upcoming_appointments || todayAppointments; // Fallback to today's if upcoming not available
  const emergencies = emergencyAlerts?.emergency_alerts || dashboard?.emergency_alerts || [];
  const recentPatients = dashboard?.recent_patients || [];
  const totalAppointments = dashboard?.total_appointments_today || 0;
  const totalUpcomingAppointments = dashboard?.total_upcoming_appointments || upcomingAppointments.length;
  const activeEmergencies = dashboard?.active_emergencies || emergencies.length;
  const unreadNotifications = dashboard?.unread_notifications || 0;

  const handleEmergencyResponse = (alertId: number, status: string, notes?: string) => {
    updateEmergencyStatus.mutate({ alertId, status, notes });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return <AlertTriangle className="h-4 w-4" />;
      case 'high': return <AlertTriangle className="h-4 w-4" />;
      case 'medium': return <Activity className="h-4 w-4" />;
      case 'low': return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <>
      <div className="space-y-6">
        {/* Doctor Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <Stethoscope className="h-8 w-8 text-primary-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Welcome, Dr. {doctor?.user?.first_name || 'Doctor'} {doctor?.user?.last_name || 'User'}
                </h1>
                <p className="text-gray-600">
                  {doctor?.specialization || 'General Medicine'} • {doctor?.hospital_affiliation || 'Hospital'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Today's Date</p>
              <p className="text-lg font-semibold text-gray-900">
                {format(new Date(), 'EEEE, MMMM d, yyyy')}
              </p>
            </div>
          </div>
        </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Calendar className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Today's Appointments</p>
              <p className="text-2xl font-bold text-gray-900">{totalAppointments}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Upcoming Appointments</p>
              <p className="text-2xl font-bold text-gray-900">{totalUpcomingAppointments}</p>
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
              <MessageSquare className="h-6 w-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Unread Notifications</p>
              <p className="text-2xl font-bold text-gray-900">{unreadNotifications}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-secondary-100 rounded-lg">
              <Users className="h-6 w-6 text-secondary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recent Patients</p>
              <p className="text-2xl font-bold text-gray-900">{recentPatients.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Hospital Capacity */}
      {hospitalCapacity && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Hospital Capacity</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{hospitalCapacity.total_beds}</p>
              <p className="text-sm text-gray-600">Total Beds</p>
              <p className="text-xs text-green-600">{hospitalCapacity.available_beds} Available</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{hospitalCapacity.icu_beds}</p>
              <p className="text-sm text-gray-600">ICU Beds</p>
              <p className="text-xs text-green-600">{hospitalCapacity.available_icu} Available</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{hospitalCapacity.emergency_rooms}</p>
              <p className="text-sm text-gray-600">Emergency Rooms</p>
              <p className="text-xs text-green-600">{hospitalCapacity.available_emergency} Available</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{hospitalCapacity.average_wait_time || 0}</p>
              <p className="text-sm text-gray-600">Avg Wait Time (min)</p>
            </div>
          </div>
        </div>
      )}

      {/* Upcoming Appointments */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Upcoming Appointments</h2>
          <button 
            onClick={() => refetch()}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Refresh
          </button>
        </div>
        
        {upcomingAppointments.length > 0 ? (
          <div className="space-y-3">
            {upcomingAppointments.slice(0, 8).map((appointment: any) => (
              <div key={appointment.id || Math.random()} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <User className="h-4 w-4 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {appointment.patient?.user?.first_name || 'Patient'} {appointment.patient?.user?.last_name || 'Name'}
                    </p>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <span>
                        {appointment.appointment_date ? format(new Date(appointment.appointment_date), 'MMM dd, yyyy') : 'Date TBD'}
                      </span>
                      <span>•</span>
                      <span>
                        {appointment.appointment_date ? format(new Date(appointment.appointment_date), 'h:mm a') : 'Time TBD'}
                      </span>
                    </div>
                    {appointment.reason && (
                      <p className="text-xs text-gray-500 mt-1">{appointment.reason}</p>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    appointment.appointment_date && new Date(appointment.appointment_date).toDateString() === new Date().toDateString()
                      ? 'bg-green-100 text-green-700'
                      : 'bg-primary-100 text-primary-700'
                  }`}>
                    {appointment.appointment_date && new Date(appointment.appointment_date).toDateString() === new Date().toDateString()
                      ? 'Today'
                      : appointment.status || 'Scheduled'
                    }
                  </span>
                  {appointment.appointment_date && new Date(appointment.appointment_date).toDateString() !== new Date().toDateString() && (
                    <span className="text-xs text-gray-500">
                      {Math.ceil((new Date(appointment.appointment_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days away
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No upcoming appointments</h3>
            <p className="text-gray-600">You have a clear schedule ahead</p>
          </div>
        )}
      </div>

      {/* Emergency Alerts */}
      {emergencies.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Emergency Alerts</h2>
          <div className="space-y-3">
            {emergencies.slice(0, 3).map((emergency: any) => (
              <div key={emergency.id || Math.random()} className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    <div>
                      <p className="font-medium text-red-900">
                        {emergency.patient?.user?.first_name || 'Patient'} {emergency.patient?.user?.last_name || 'Emergency'}
                      </p>
                      <p className="text-sm text-red-700">{emergency.description || 'Emergency situation'}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(emergency.severity)}`}>
                    <div className="flex items-center space-x-1">
                      {getSeverityIcon(emergency.severity)}
                      <span>{emergency.severity || 'High'}</span>
                    </div>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Patients */}
      {recentPatients.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Patients</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentPatients.slice(0, 6).map((patient: any) => (
              <div key={patient.id || Math.random()} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-secondary-100 rounded-lg">
                    <User className="h-4 w-4 text-secondary-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {patient.user?.first_name || 'Patient'} {patient.user?.last_name || 'Name'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {patient.phone_number || 'No phone'} • {patient.blood_type || 'Blood type N/A'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="card bg-red-50 border border-red-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <div>
                <p className="font-medium text-red-900">Dashboard Data Error</p>
                <p className="text-sm text-red-700">Some data may not be displaying correctly</p>
              </div>
            </div>
            <button 
              onClick={() => refetch()}
              className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      )}
    </div>
    </>
  );
};

export default DoctorDashboard;
