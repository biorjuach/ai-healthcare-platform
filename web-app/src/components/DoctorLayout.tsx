import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DoctorNavigation from './DoctorNavigation';
import DoctorDashboard from '../screens/main/DoctorDashboard';
import EmergencyResponseScreen from '../screens/main/EmergencyResponseScreen';
import PatientManagementScreen from '../screens/main/PatientManagementScreen';
import ProfileScreen from '../screens/main/ProfileScreen';

const DoctorLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <DoctorNavigation />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<DoctorDashboard />} />
          <Route path="/dashboard" element={<DoctorDashboard />} />
          <Route path="/emergency" element={<EmergencyResponseScreen />} />
          <Route path="/patients" element={<PatientManagementScreen />} />
          <Route path="/profile" element={<ProfileScreen />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  );
};

export default DoctorLayout;
