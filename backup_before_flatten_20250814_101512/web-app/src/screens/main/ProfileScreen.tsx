import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from 'react-query';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Shield, 
  Settings,
  Edit,
  Save,
  X,
  Heart,
  Pill,
  AlertTriangle,
  FileText
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

interface ProfileFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  emergency_contact?: string;
  insurance_info?: string;
  medical_history?: string;
  allergies?: string;
  medications?: string;
}

const ProfileScreen: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('personal');
  const { user, updateUser } = useAuth();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone_number: user?.phone_number || '',
      date_of_birth: user?.date_of_birth || '',
      gender: user?.gender || 'other',
      address: user?.address || '',
      emergency_contact: user?.emergency_contact || '',
      insurance_info: user?.insurance_info || '',
      medical_history: user?.medical_history || '',
      allergies: user?.allergies?.join(', ') || '',
      medications: user?.medications?.join(', ') || '',
    },
  });

  // Update profile mutation
  const updateMutation = useMutation(
    (data: Partial<ProfileFormData>) => apiService.updateProfile(data),
    {
      onSuccess: (updatedUser) => {
        updateUser(updatedUser);
        setIsEditing(false);
        toast.success('Profile updated successfully');
      },
      onError: () => {
        toast.error('Failed to update profile');
      },
    }
  );

  const onSubmit = (data: ProfileFormData) => {
    const updateData = {
      ...data,
      allergies: data.allergies ? data.allergies.split(',').map(a => a.trim()).filter(a => a.length > 0) : [],
      medications: data.medications ? data.medications.split(',').map(m => m.trim()).filter(m => m.length > 0) : [],
    };
    updateMutation.mutate(updateData);
  };

  const handleCancel = () => {
    setIsEditing(false);
    reset();
  };

  const tabs = [
    { id: 'personal', name: 'Personal Info', icon: User },
    { id: 'medical', name: 'Medical History', icon: Heart },
    { id: 'emergency', name: 'Emergency Contacts', icon: AlertTriangle },
    { id: 'settings', name: 'Settings', icon: Settings },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
          <p className="text-gray-600">Manage your personal information and preferences</p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="btn-primary flex items-center"
          >
            <Edit className="h-4 w-4 mr-2" />
            Edit Profile
          </button>
        )}
      </div>

      {/* Profile Overview */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <User className="h-8 w-8 text-primary-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {user?.first_name} {user?.last_name}
            </h2>
            <p className="text-gray-600">{user?.email}</p>
            <p className="text-sm text-gray-500">Patient ID: {user?.id}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="mt-6">
          {/* Personal Information Tab */}
          {activeTab === 'personal' && (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    {...register('first_name', { required: 'First name is required' })}
                    type="text"
                    disabled={!isEditing}
                    className="input-field"
                  />
                  {errors.first_name && (
                    <p className="mt-1 text-sm text-danger-600">{errors.first_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    {...register('last_name', { required: 'Last name is required' })}
                    type="text"
                    disabled={!isEditing}
                    className="input-field"
                  />
                  {errors.last_name && (
                    <p className="mt-1 text-sm text-danger-600">{errors.last_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    {...register('email', { 
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                    type="email"
                    disabled={!isEditing}
                    className="input-field"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-danger-600">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    {...register('phone_number')}
                    type="tel"
                    disabled={!isEditing}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date of Birth
                  </label>
                  <input
                    {...register('date_of_birth')}
                    type="date"
                    disabled={!isEditing}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gender
                  </label>
                  <select
                    {...register('gender')}
                    disabled={!isEditing}
                    className="input-field"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address
                </label>
                <textarea
                  {...register('address')}
                  rows={3}
                  disabled={!isEditing}
                  className="input-field"
                />
              </div>

              {isEditing && (
                <div className="flex justify-end space-x-3">
                  <button type="button" onClick={handleCancel} className="btn-secondary">
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={updateMutation.isLoading}
                    className="btn-primary"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </form>
          )}

          {/* Medical History Tab */}
          {activeTab === 'medical' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Medical History
                </label>
                <textarea
                  {...register('medical_history')}
                  rows={4}
                  disabled={!isEditing}
                  className="input-field"
                  placeholder="Describe your medical history, past surgeries, chronic conditions..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Allergies
                </label>
                <input
                  {...register('allergies')}
                  type="text"
                  disabled={!isEditing}
                  className="input-field"
                  placeholder="e.g., penicillin, peanuts, latex (separate with commas)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Medications
                </label>
                <input
                  {...register('medications')}
                  type="text"
                  disabled={!isEditing}
                  className="input-field"
                  placeholder="e.g., aspirin, insulin, blood pressure medication (separate with commas)"
                />
              </div>

              {isEditing && (
                <div className="flex justify-end space-x-3">
                  <button type="button" onClick={handleCancel} className="btn-secondary">
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit(onSubmit)}
                    disabled={updateMutation.isLoading}
                    className="btn-primary"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Emergency Contacts Tab */}
          {activeTab === 'emergency' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emergency Contact
                </label>
                <input
                  {...register('emergency_contact')}
                  type="text"
                  disabled={!isEditing}
                  className="input-field"
                  placeholder="Name and phone number of emergency contact"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Insurance Information
                </label>
                <textarea
                  {...register('insurance_info')}
                  rows={3}
                  disabled={!isEditing}
                  className="input-field"
                  placeholder="Insurance provider, policy number, group number..."
                />
              </div>

              <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertTriangle className="h-5 w-5 text-warning-600 mr-2" />
                  <div>
                    <h3 className="font-medium text-warning-900">Emergency Information</h3>
                    <p className="text-warning-700 text-sm">
                      This information will be shared with emergency services when needed.
                    </p>
                  </div>
                </div>
              </div>

              {isEditing && (
                <div className="flex justify-end space-x-3">
                  <button type="button" onClick={handleCancel} className="btn-secondary">
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit(onSubmit)}
                    disabled={updateMutation.isLoading}
                    className="btn-primary"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Privacy & Security</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Data Sharing</p>
                      <p className="text-sm text-gray-600">Allow sharing of health data with healthcare providers</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Location Services</p>
                      <p className="text-sm text-gray-600">Allow location access for emergency services</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Notifications</p>
                      <p className="text-sm text-gray-600">Receive appointment reminders and health alerts</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Account</h3>
                <div className="space-y-4">
                  <button className="btn-secondary w-full justify-start">
                    <Shield className="h-4 w-4 mr-2" />
                    Change Password
                  </button>
                  <button className="btn-secondary w-full justify-start">
                    <FileText className="h-4 w-4 mr-2" />
                    Download Health Records
                  </button>
                  <button className="btn-danger w-full justify-start">
                    <X className="h-4 w-4 mr-2" />
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileScreen;
