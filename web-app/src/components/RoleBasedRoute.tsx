import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import PatientLayout from './PatientLayout';
import DoctorLayout from './DoctorLayout';
import LoadingSpinner from './LoadingSpinner';

const RoleBasedRoute: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return null; // Will be handled by parent auth check
  }

  // Determine user role
  const getUserRole = () => {
    // Check if user has doctor profile
    if (user.doctor_profile || user.user_type === 'doctor') {
      return 'doctor';
    }
    // Check if user has patient profile  
    if (user.patient_profile || user.user_type === 'patient') {
      return 'patient';
    }
    // Default to patient for backward compatibility
    return 'patient';
  };

  const userRole = getUserRole();

  // Route to appropriate interface based on role
  switch (userRole) {
    case 'doctor':
      return <DoctorLayout />;
    case 'patient':
      return <PatientLayout />;
    default:
      return <PatientLayout />; // Default fallback
  }
};

export default RoleBasedRoute;
