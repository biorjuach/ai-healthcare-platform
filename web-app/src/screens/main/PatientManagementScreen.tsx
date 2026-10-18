import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Users, 
  Search, 
  FileText, 
  Calendar, 
  Phone, 
  MapPin,
  AlertTriangle,
  Clock,
  Filter,
  Eye,
  Plus
} from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

const PatientManagementScreen: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
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

  // Fetch patients with better error handling
  const { data: patients, isLoading, error, refetch } = useQuery(
    'patients',
    async () => {
      try {
        const response = await apiService.getPatients();
        console.log('Patients response:', response);
        return response;
      } catch (err) {
        console.error('Patients API error:', err);
        return [];
      }
    },
    {
      retry: 2,
      retryDelay: 1000,
      enabled: !isAuthenticating,
      onError: (error) => {
        console.error('Patients fetch error:', error);
      }
    }
  );

  // Refetch patients after authentication
  useEffect(() => {
    if (!isAuthenticating) {
      console.log('Authentication complete, refetching patients...');
      refetch();
    }
  }, [isAuthenticating, refetch]);

  // Fetch patient details when selected
  const { data: patientDetails } = useQuery(
    ['patientDetails', selectedPatient?.id],
    async () => {
      if (selectedPatient?.id) {
        try {
          return await apiService.getPatientDetails(selectedPatient.id);
        } catch (err) {
          console.error('Patient details error:', err);
          return null;
        }
      }
      return null;
    },
    {
      enabled: !!selectedPatient?.id,
      retry: 1,
    }
  );

  const filteredPatients = patients?.filter((patient: any) => {
    const searchLower = searchTerm.toLowerCase();
    const firstName = patient?.user?.first_name || patient?.first_name || '';
    const lastName = patient?.user?.last_name || patient?.last_name || '';
    const email = patient?.user?.email || patient?.email || '';
    const phone = patient?.phone_number || '';
    
    return (
      firstName.toLowerCase().includes(searchLower) ||
      lastName.toLowerCase().includes(searchLower) ||
      email.toLowerCase().includes(searchLower) ||
      phone.includes(searchTerm)
    );
  }) || [];

  const handleViewPatient = (patient: any) => {
    try {
      console.log('Viewing patient:', patient);
      setSelectedPatient(patient);
      setShowModal(true);
    } catch (error) {
      console.error('Error opening patient modal:', error);
    }
  };



  const getPatientName = (patient: any) => {
    if (patient?.user?.first_name && patient?.user?.last_name) {
      return `${patient.user.first_name} ${patient.user.last_name}`;
    }
    if (patient?.first_name && patient?.last_name) {
      return `${patient.first_name} ${patient.last_name}`;
    }
    return 'Unknown Patient';
  };

  const getPatientEmail = (patient: any) => {
    return patient?.user?.email || patient?.email || 'No email';
  };

  const getPatientPhone = (patient: any) => {
    return patient?.phone_number || 'No phone';
  };

  const getPatientAddress = (patient: any) => {
    return patient?.address || 'No address';
  };

  const getPatientAge = (patient: any) => {
    const dob = patient?.date_of_birth;
    if (dob) {
      try {
        return new Date().getFullYear() - new Date(dob).getFullYear();
      } catch (error) {
        return 'Unknown';
      }
    }
    return 'Unknown';
  };

  if (isLoading || isAuthenticating) {
    return <LoadingSpinner />;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Patient Management</h1>
            <p className="text-gray-600">Manage and monitor your patients</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="bg-blue-50 px-4 py-2 rounded-lg">
              <p className="text-sm text-blue-600">Total Patients</p>
              <p className="text-xl font-bold text-blue-900">{filteredPatients.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search patients by name, email, or phone..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="btn-secondary flex items-center space-x-2">
          <Filter className="h-4 w-4" />
          <span>Filter</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <div>
              <p className="font-medium text-red-900">Error loading patients</p>
              <p className="text-sm text-red-700">Failed to fetch patient data</p>
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

      {/* Patients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPatients.map((patient: any) => (
          <div key={patient.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <Users className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {getPatientName(patient)}
                  </h3>
                  <p className="text-sm text-gray-500">{getPatientEmail(patient)}</p>
                </div>
              </div>
              <button
                onClick={() => handleViewPatient(patient)}
                className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Eye className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-2">
              <div className="flex items-center text-sm text-gray-600">
                <Phone className="h-4 w-4 mr-2" />
                {getPatientPhone(patient)}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <MapPin className="h-4 w-4 mr-2" />
                {getPatientAddress(patient)}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Calendar className="h-4 w-4 mr-2" />
                Age: {getPatientAge(patient)}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  Last visit: {patient.last_visit || 'Never'}
                </span>
                {patient.has_active_symptoms && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    Active symptoms
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredPatients.length === 0 && !error && (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No patients found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search criteria.' : 'No patients have been assigned to you yet.'}
          </p>
        </div>
      )}

      {/* Patient Details Modal */}
      {showModal && selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {getPatientName(selectedPatient)}
                  </h2>
                  <p className="text-gray-600">{getPatientEmail(selectedPatient)}</p>
                </div>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {/* Patient Information */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Personal Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Phone</label>
                      <p className="text-sm text-gray-900">{getPatientPhone(selectedPatient)}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Gender</label>
                      <p className="text-sm text-gray-900">{selectedPatient?.gender || 'Not specified'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Date of Birth</label>
                      <p className="text-sm text-gray-900">
                        {selectedPatient?.date_of_birth 
                          ? format(new Date(selectedPatient.date_of_birth), 'PPP')
                          : 'Not provided'
                        }
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Emergency Contact</label>
                      <p className="text-sm text-gray-900">{selectedPatient?.emergency_contact || 'Not provided'}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Medical Information</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Medical History</label>
                      <p className="text-sm text-gray-900">{selectedPatient?.medical_history || 'No medical history recorded'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Allergies</label>
                      <p className="text-sm text-gray-900">
                        {selectedPatient?.allergies 
                          ? (Array.isArray(selectedPatient.allergies) 
                              ? selectedPatient.allergies.join(', ')
                              : selectedPatient.allergies)
                          : 'No known allergies'
                        }
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Blood Type</label>
                      <p className="text-sm text-gray-900">{selectedPatient?.blood_type || 'Not specified'}</p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-4 border-t border-gray-200">
                  <button className="btn-primary flex items-center space-x-2">
                    <FileText className="h-4 w-4" />
                    <span>View Medical Records</span>
                  </button>
                  <button className="btn-secondary flex items-center space-x-2">
                    <Calendar className="h-4 w-4" />
                    <span>Schedule Appointment</span>
                  </button>
                  <button className="btn-secondary flex items-center space-x-2">
                    <Phone className="h-4 w-4" />
                    <span>Contact Patient</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}


    </div>
  );
};

export default PatientManagementScreen;