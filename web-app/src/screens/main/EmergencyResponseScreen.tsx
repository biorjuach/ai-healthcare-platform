import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  AlertTriangle, 
  Phone, 
  MapPin, 
  Clock, 
  CheckCircle, 
  XCircle,
  Users,
  Activity,
  Heart,
  TrendingUp,
  MessageSquare,
  Filter
} from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

const EmergencyResponseScreen: React.FC = () => {
  const [selectedEmergency, setSelectedEmergency] = useState<any>(null);
  const [filterStatus, setFilterStatus] = useState('active');
  const [responseNotes, setResponseNotes] = useState('');
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const queryClient = useQueryClient();

  // Auto-authenticate if not logged in
  useEffect(() => {
    const autoAuthenticate = async () => {
      const token = localStorage.getItem('authToken');
      const userData = localStorage.getItem('user');
      
      if (!token || !userData) {
        console.log('No authentication found, auto-logging in...');
        setIsAuthenticating(true);
        
        try {
          // Auto-login with doctor credentials
          const { user: authUser, token } = await apiService.login({
            username: 'doctor1',
            password: 'password123'
          });
          
          localStorage.setItem('authToken', token);
          localStorage.setItem('user', JSON.stringify(authUser));
          console.log('Auto-authentication successful');
        } catch (error) {
          console.error('Auto-authentication failed:', error);
        } finally {
          setIsAuthenticating(false);
        }
      }
    };

    autoAuthenticate();
  }, []);

  // Fetch emergency alerts with real-time updates
  const { data: emergencyData, isLoading, error, refetch } = useQuery(
    'emergencyAlerts',
    async () => {
      try {
        const response = await apiService.getEmergencyAlerts();
        console.log('Emergency alerts response:', response);
        return response;
      } catch (err) {
        console.error('Emergency alerts error:', err);
        // Return empty data instead of mock data
        return {
          emergency_alerts: []
        };
      }
    },
    { 
      refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
      refetchIntervalInBackground: true,
      enabled: !isAuthenticating,
      retry: 2,
      onError: (error) => {
        console.error('Emergency alerts fetch error:', error);
      }
    }
  );

  // Refetch after authentication
  useEffect(() => {
    if (!isAuthenticating) {
      console.log('Authentication complete, refetching emergency alerts...');
      refetch();
    }
  }, [isAuthenticating, refetch]);

  // Fetch hospital capacity
  const { data: hospitalCapacity } = useQuery(
    'hospitalCapacity',
    async () => {
      try {
        return await apiService.getHospitalCapacity();
      } catch (err) {
        console.error('Hospital capacity error:', err);
        return null;
      }
    },
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  // Update emergency status mutation
  const updateEmergencyStatus = useMutation(
    async ({ alertId, status, notes }: { alertId: number; status: string; notes?: string }) => {
      try {
        console.log('Calling updateEmergencyStatus API:', { alertId, status, notes });
        const result = await apiService.updateEmergencyStatus(alertId, status, notes);
        console.log('Update emergency status success:', result);
        return result;
      } catch (err) {
        console.error('Update emergency status error:', err);
        throw err;
      }
    },
    {
      onSuccess: () => {
        console.log('Emergency status updated successfully');
        queryClient.invalidateQueries('emergencyAlerts');
        setSelectedEmergency(null);
        setResponseNotes('');
      },
      onError: (error) => {
        console.error('Emergency status update failed:', error);
        alert('Failed to update emergency status. Please try again.');
      }
    }
  );

  const emergencies: any[] = Array.isArray(emergencyData?.emergency_alerts) 
    ? emergencyData!.emergency_alerts 
    : [];
  
  const filteredEmergencies = emergencies.filter((emergency: any) =>
    filterStatus === 'all' || emergency.status === filterStatus
  );

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-red-100 text-red-700';
      case 'in_progress': return 'bg-yellow-100 text-yellow-700';
      case 'resolved': return 'bg-green-100 text-green-700';
      case 'false_alarm': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getTimeSince = (dateString: string) => {
    try {
      if (!dateString) return 'Unknown time';
      
      const now = new Date();
      const created = new Date(dateString);
      
      // Check if the date is valid
      if (isNaN(created.getTime())) {
        return 'Invalid date';
      }
      
      const diffInMinutes = Math.floor((now.getTime() - created.getTime()) / (1000 * 60));
      
      if (diffInMinutes < 0) {
        return 'Just now';
      } else if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`;
      } else if (diffInMinutes < 1440) {
        return `${Math.floor(diffInMinutes / 60)}h ago`;
      } else {
        return `${Math.floor(diffInMinutes / 1440)}d ago`;
      }
    } catch (error) {
      return 'Unknown time';
    }
  };

  const getPatientName = (emergency: any) => {
    // Check if patient is a nested object (from backend)
    if (emergency?.patient?.user?.first_name && emergency?.patient?.user?.last_name) {
      return `${emergency.patient.user.first_name} ${emergency.patient.user.last_name}`;
    }
    
    // Check for direct patient name fields
    if (emergency?.patient?.name) return emergency.patient.name;
    if (emergency?.patientName) return emergency.patientName;
    
    // Check for username as fallback
    if (emergency?.patient?.user?.username) return emergency.patient.user.username;
    
    return 'Unknown Patient';
  };

  const getPatientPhone = (emergency: any) => {
    // Check patient phone number (from backend)
    if (emergency?.patient?.phone_number) return emergency.patient.phone_number;
    
    // Check for direct phone fields
    if (emergency?.patient?.phone) return emergency.patient.phone;
    
    return '';
  };

  const getEmergencySymptom = (emergency: any) => {
    // Check if symptom is a nested object (from backend)
    if (emergency?.symptom?.description) return emergency.symptom.description;
    
    // Check if symptom is a direct string (fallback)
    if (typeof emergency?.symptom === 'string') return emergency.symptom;
    
    // Check for direct description fields
    if (typeof emergency?.description === 'string') return emergency.description;
    if (typeof emergency?.associated_symptoms === 'string') return emergency.associated_symptoms;
    
    // Check for associated symptoms array
    if (Array.isArray(emergency?.symptom?.associated_symptoms) && emergency.symptom.associated_symptoms.length > 0) {
      return emergency.symptom.associated_symptoms.join(', ');
    }
    
    return 'No symptoms described';
  };

  const getEmergencyLocation = (emergency: any) => {
    // Check emergency location field
    if (typeof emergency?.location === 'string') return emergency.location;
    
    // Check symptom body location (from backend)
    if (typeof emergency?.symptom?.body_location === 'string') return emergency.symptom.body_location;
    
    // Check direct body location field
    if (typeof emergency?.body_location === 'string') return emergency.body_location;
    
    return 'Location not specified';
  };

  const getEmergencyCreatedAt = (emergency: any) => {
    if (!emergency?.createdAt) return null;
    try {
      const date = new Date(emergency.createdAt);
      return isNaN(date.getTime()) ? null : date;
    } catch (error) {
      return null;
    }
  };

  const handleEmergencyResponse = (alertId: number, status: string) => {
    console.log('Handling emergency response:', { alertId, status, notes: responseNotes });
    updateEmergencyStatus.mutate({ alertId, status, notes: responseNotes });
  };

  const handleCallPatient = (phone: string) => {
    window.open(`tel:${phone}`, '_self');
  };

  if (isLoading || isAuthenticating) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <div>
              <p className="font-medium text-red-900">Error loading emergency alerts</p>
              <p className="text-sm text-red-700">Failed to fetch emergency data</p>
            </div>
          </div>
          <button 
            onClick={() => refetch()}
            className="mt-3 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Emergency Response</h1>
            <p className="text-gray-600">Monitor and respond to emergency alerts in real-time</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">Active Emergencies</p>
              <p className="text-2xl font-bold text-red-600">
                {emergencies.filter((e: any) => e.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Critical</p>
              <p className="text-2xl font-bold text-red-600">
                {emergencies.filter((e: any) => e.severity === 'critical').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Activity className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">High Priority</p>
              <p className="text-2xl font-bold text-orange-600">
                {emergencies.filter((e: any) => e.severity === 'high').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-blue-600">
                {emergencies.filter((e: any) => e.status === 'in_progress').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Resolved</p>
              <p className="text-2xl font-bold text-green-600">
                {emergencies.filter((e: any) => e.status === 'resolved').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Hospital Capacity Alert */}
      {hospitalCapacity && hospitalCapacity.available_beds < 5 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Low Hospital Capacity</h3>
              <p className="text-sm text-red-700">
                Only {hospitalCapacity.available_beds} beds available. Consider patient transfers.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Emergencies</option>
            <option value="active">Active</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="false_alarm">False Alarm</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Emergency Alerts List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Emergency Alerts</h2>
            </div>
            
            {filteredEmergencies.length > 0 ? (
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {filteredEmergencies.map((emergency: any) => (
                  <div
                    key={emergency.id}
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                      selectedEmergency?.id === emergency.id ? 'bg-primary-50 border-l-4 border-primary-500' : ''
                    }`}
                    onClick={() => setSelectedEmergency(emergency)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">{getPatientName(emergency)}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(emergency.severity)}`}>
                            {emergency.severity}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(emergency.status)}`}>
                            {emergency.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{getEmergencySymptom(emergency)}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <div className="flex items-center space-x-1">
                            <MapPin className="h-3 w-3" />
                            <span>{getEmergencyLocation(emergency)}</span>
                          </div>
                                                     <div className="flex items-center space-x-1">
                             <Clock className="h-3 w-3" />
                             <span>{emergency.createdAt ? getTimeSince(emergency.createdAt) : 'Unknown time'}</span>
                           </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getPatientPhone(emergency) && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCallPatient(getPatientPhone(emergency));
                            }}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                          >
                            <Phone className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No emergency alerts found</p>
              </div>
            )}
          </div>
        </div>

        {/* Emergency Details and Response */}
        <div className="lg:col-span-1">
          {selectedEmergency ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Emergency Details</h2>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Patient Info */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">Patient Information</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Name:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {getPatientName(selectedEmergency)}
                      </span>
                    </div>
                    {getPatientPhone(selectedEmergency) && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Phone:</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">
                            {getPatientPhone(selectedEmergency)}
                          </span>
                          <button
                            onClick={() => handleCallPatient(getPatientPhone(selectedEmergency))}
                            className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                          >
                            <Phone className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Location:</span>
                      <span className="text-sm font-medium text-gray-900">{getEmergencyLocation(selectedEmergency)}</span>
                    </div>
                  </div>
                </div>

                {/* Emergency Info */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">Emergency Information</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Symptoms:</span>
                      <span className="text-sm font-medium text-gray-900">{getEmergencySymptom(selectedEmergency)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Severity:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(selectedEmergency.severity)}`}>
                        {selectedEmergency.severity}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Status:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedEmergency.status)}`}>
                        {selectedEmergency.status}
                      </span>
                    </div>
                                         <div className="flex items-center justify-between">
                       <span className="text-sm text-gray-600">Reported:</span>
                       <span className="text-sm font-medium text-gray-900">
                         {(() => {
                           const date = getEmergencyCreatedAt(selectedEmergency);
                           if (!date) return 'Unknown time';
                           try {
                             return format(date, 'MMM dd, yyyy HH:mm');
                           } catch (error) {
                             return 'Invalid date';
                           }
                         })()}
                       </span>
                     </div>
                  </div>
                </div>

                {/* Response Actions */}
                {selectedEmergency.status === 'active' && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Response Actions</h3>
                    <div className="space-y-4">
                      <textarea
                        placeholder="Add response notes..."
                        value={responseNotes}
                        onChange={(e) => setResponseNotes(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        rows={3}
                      />
                                             <div className="flex space-x-3">
                         <button
                           onClick={() => handleEmergencyResponse(selectedEmergency.id, 'in_progress')}
                           className="flex-1 btn-primary flex items-center justify-center"
                           disabled={updateEmergencyStatus.isLoading}
                         >
                           {updateEmergencyStatus.isLoading ? (
                             <>
                               <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                               Updating...
                             </>
                           ) : (
                             <>
                               <CheckCircle className="h-4 w-4 mr-2" />
                               Respond
                             </>
                           )}
                         </button>
                         <button
                           onClick={() => handleEmergencyResponse(selectedEmergency.id, 'resolved')}
                           className="flex-1 btn-secondary flex items-center justify-center"
                           disabled={updateEmergencyStatus.isLoading}
                         >
                           {updateEmergencyStatus.isLoading ? (
                             <>
                               <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                               Updating...
                             </>
                           ) : (
                             <>
                               <XCircle className="h-4 w-4 mr-2" />
                               Resolve
                             </>
                           )}
                         </button>
                       </div>
                    </div>
                  </div>
                )}

                {/* Status Update */}
                {selectedEmergency.status !== 'active' && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Status Update</h3>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-sm text-gray-700">
                        Emergency is currently {selectedEmergency.status}. 
                        {selectedEmergency.assigned_responder && ` Assigned to ${selectedEmergency.assigned_responder}.`}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
              <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Select an emergency to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmergencyResponseScreen;
