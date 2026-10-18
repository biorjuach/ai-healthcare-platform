// API Configuration
export const API_URL = 'http://localhost:8000/api';

// App Configuration
export const APP_CONFIG = {
  name: 'AI Healthcare Platform',
  version: '2.1.0',
  description: 'AI-powered healthcare platform for resource-limited settings',
  hospital: {
    name: 'Makueni County Referral Hospital',
    address: 'Makueni, Kenya',
    phone: '+254700000000',
    email: 'info@makuenihospital.com',
  },
  features: {
    symptomAnalysis: true,
    emergencyResponse: true,
    multiChannel: true,
    aiRecommendations: true,
  },
};

// Development Configuration
export const DEV_CONFIG = {
  mockData: true, // Set to false when backend is connected
  backendUrl: 'http://localhost:8000',
  timeout: 10000, // 10 seconds
}; 