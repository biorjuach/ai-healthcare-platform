import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Plus, 
  Calendar, 
  Clock, 
  MapPin, 
  User, 
  Phone,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import apiService from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

interface AppointmentFormData {
  doctor?: number;
  hospital?: string;
  date: string;
  time: string;
  notes?: string;
  symptoms?: string;
}

const AppointmentsScreen: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState<any>(null);
  const [formData, setFormData] = useState<AppointmentFormData>({
    date: '',
    time: '',
    hospital: '',
    notes: '',
    symptoms: '',
  });

  const queryClient = useQueryClient();

  const { data: appointments, isLoading, error } = useQuery(
    'patientAppointments',
    async () => {
      try {
        return await apiService.getPatientAppointments();
      } catch (err) {
        console.error('Appointments API error:', err);
        return []; // Return empty array as fallback
      }
    },
    {
      refetchInterval: 30000,
    }
  );

  const { data: doctors } = useQuery(
    'doctors',
    async () => {
      try {
        return await apiService.getDoctors();
      } catch (err) {
        console.error('Doctors API error:', err);
        return []; // Return empty array as fallback
      }
    },
    {
      staleTime: 300000, // 5 minutes
    }
  );

  // Create appointment mutation
  const createMutation = useMutation(
    (data: AppointmentFormData) => apiService.createAppointment(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('patientAppointments');
        queryClient.invalidateQueries('patientDashboard');
        setShowForm(false);
        setFormData({ date: '', time: '', hospital: '', notes: '', symptoms: '' });
        toast.success('Appointment scheduled successfully');
      },
      onError: () => {
        toast.error('Failed to schedule appointment');
      },
    }
  );

  // Update appointment mutation
  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: Partial<AppointmentFormData> }) =>
      apiService.updateAppointment(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('patientAppointments');
        queryClient.invalidateQueries('patientDashboard');
        setEditingAppointment(null);
        setFormData({ date: '', time: '', hospital: '', notes: '', symptoms: '' });
        toast.success('Appointment updated successfully');
      },
      onError: () => {
        toast.error('Failed to update appointment');
      },
    }
  );

  // Cancel appointment mutation
  const cancelMutation = useMutation(
    (id: number) => apiService.cancelAppointment(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('patientAppointments');
        queryClient.invalidateQueries('patientDashboard');
        toast.success('Appointment cancelled successfully');
      },
      onError: () => {
        toast.error('Failed to cancel appointment');
      },
    }
  );

  if (isLoading) return <LoadingSpinner />;
  // Don't show error screen, just continue with empty data
  if (error) {
    console.error('Appointments error:', error);
  }

  const upcomingAppointments = appointments?.filter((apt: any) => 
    new Date(apt.date) >= new Date() && apt.status !== 'cancelled'
  ) || [];

  const pastAppointments = appointments?.filter((apt: any) => 
    new Date(apt.date) < new Date() || apt.status === 'cancelled'
  ) || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-secondary-100 text-secondary-700';
      case 'scheduled': return 'bg-primary-100 text-primary-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'cancelled': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed': return <CheckCircle className="h-4 w-4" />;
      case 'scheduled': return <Calendar className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'cancelled': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingAppointment) {
      updateMutation.mutate({ id: editingAppointment.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (appointment: any) => {
    setEditingAppointment(appointment);
    setFormData({
      doctor: appointment.doctor,
      hospital: appointment.hospital || '',
      date: appointment.date,
      time: appointment.time,
      notes: appointment.notes || '',
      symptoms: appointment.symptoms || '',
    });
    setShowForm(true);
  };

  const handleCancel = (id: number) => {
    if (window.confirm('Are you sure you want to cancel this appointment?')) {
      cancelMutation.mutate(id);
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingAppointment(null);
    setFormData({ date: '', time: '', hospital: '', notes: '', symptoms: '' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
          <p className="text-gray-600">Manage your healthcare appointments</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Schedule Appointment
        </button>
      </div>

      {/* Appointment Form */}
      {showForm && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {editingAppointment ? 'Edit Appointment' : 'Schedule New Appointment'}
            </h2>
            <button onClick={resetForm} className="text-gray-400 hover:text-gray-600">
              <XCircle className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hospital/Clinic
                </label>
                <input
                  type="text"
                  value={formData.hospital}
                  onChange={(e) => setFormData({ ...formData, hospital: e.target.value })}
                  className="input-field"
                  placeholder="Enter hospital or clinic name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Doctor (Optional)
                </label>
                <select
                  value={formData.doctor || ''}
                  onChange={(e) => setFormData({ ...formData, doctor: Number(e.target.value) || undefined })}
                  className="input-field"
                >
                  <option value="">Select a doctor</option>
                  {doctors?.map((doctor: any) => (
                    <option key={doctor.id} value={doctor.id}>
                      Dr. {doctor.name} - {doctor.specialization}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date
                </label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="input-field"
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time
                </label>
                <input
                  type="time"
                  value={formData.time}
                  onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symptoms (Optional)
              </label>
              <textarea
                value={formData.symptoms}
                onChange={(e) => setFormData({ ...formData, symptoms: e.target.value })}
                rows={2}
                className="input-field"
                placeholder="Describe any symptoms you're experiencing..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (Optional)
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="input-field"
                placeholder="Any additional notes or concerns..."
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button type="button" onClick={resetForm} className="btn-secondary">
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isLoading || updateMutation.isLoading}
                className="btn-primary"
              >
                {createMutation.isLoading || updateMutation.isLoading ? 'Saving...' : 
                 editingAppointment ? 'Update Appointment' : 'Schedule Appointment'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Upcoming Appointments */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Appointments</h2>
        
        {upcomingAppointments.length > 0 ? (
          <div className="space-y-4">
            {upcomingAppointments.map((appointment: any) => (
              <div key={appointment.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {appointment.hospital || 'General Hospital'}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(appointment.status)}`}>
                        {getStatusIcon(appointment.status)}
                        <span>{appointment.status}</span>
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="h-4 w-4 mr-2" />
                        {format(new Date(appointment.date), 'MMM dd, yyyy')}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="h-4 w-4 mr-2" />
                        {appointment.time}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <MapPin className="h-4 w-4 mr-2" />
                        {appointment.hospital || 'General Hospital'}
                      </div>
                    </div>

                    {appointment.notes && (
                      <p className="text-sm text-gray-600 mb-3">{appointment.notes}</p>
                    )}

                    {appointment.symptoms && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700">Symptoms:</p>
                        <p className="text-sm text-gray-600">{appointment.symptoms}</p>
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(appointment)}
                      className="p-2 text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded"
                      title="Edit appointment"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleCancel(appointment.id)}
                      className="p-2 text-danger-600 hover:text-danger-700 hover:bg-danger-50 rounded"
                      title="Cancel appointment"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No upcoming appointments</h3>
            <p className="text-gray-600 mb-4">Schedule your first appointment to get started</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              Schedule Appointment
            </button>
          </div>
        )}
      </div>

      {/* Past Appointments */}
      {pastAppointments.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Past Appointments</h2>
          <div className="space-y-4">
            {pastAppointments.slice(0, 5).map((appointment: any) => (
              <div key={appointment.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {appointment.hospital || 'General Hospital'}
                    </h3>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                      <span>{format(new Date(appointment.date), 'MMM dd, yyyy')}</span>
                      <span>{appointment.time}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(appointment.status)}`}>
                        {appointment.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentsScreen;
