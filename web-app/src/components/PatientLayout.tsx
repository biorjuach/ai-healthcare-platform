import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './Layout';
import HomeScreen from '../screens/main/HomeScreen';
import SymptomsScreen from '../screens/main/SymptomsScreen';
import SymptomReportScreen from '../screens/main/SymptomReportScreen';
import AppointmentsScreen from '../screens/main/AppointmentsScreen';
import ProfileScreen from '../screens/main/ProfileScreen';

const PatientLayout: React.FC = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomeScreen />} />
        <Route path="/symptoms" element={<SymptomsScreen />} />
        <Route path="/symptoms/report" element={<SymptomReportScreen />} />
        <Route path="/appointments" element={<AppointmentsScreen />} />
        <Route path="/profile" element={<ProfileScreen />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
};

export default PatientLayout;
