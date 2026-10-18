# Functional Requirements Testing Guide

## Overview

This guide provides comprehensive instructions for testing all functional requirements of the AI Healthcare Platform. The system has been designed to support all the specified functional requirements with both backend APIs and frontend interfaces.

## Functional Requirements Status

### ✅ IMPLEMENTED AND TESTABLE

#### 1. User Registration and Authentication
- **Patient Registration**: Complete with secure profile creation
- **Doctor Registration**: Backend support available
- **Password Encryption**: Django's built-in security
- **Authentication Mechanisms**: Token-based and session-based auth

**Testing Endpoints:**
- `POST /api/auth/register/` - Patient registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Profile management

#### 2. Symptom-Based Diagnosis and AI Recommendations
- **Multi-channel Input**: SMS, Voice, Mobile App
- **Natural Language Processing**: AI symptom interpretation
- **Preliminary Diagnoses**: AI-powered with confidence scoring
- **Severity Classification**: Automatic severity assessment

**Testing Endpoints:**
- `POST /api/symptoms/analyze/` - AI symptom analysis
- `POST /api/symptoms/submit/` - Symptom submission
- `POST /api/sms/webhook/` - SMS processing
- `POST /api/voice/webhook/` - Voice processing

#### 3. Appointment Scheduling and Referrals
- **Automated Scheduling**: Based on diagnosis severity
- **Specialist Referrals**: Doctor matching system
- **Appointment Management**: CRUD operations
- **Notifications**: SMS/Email reminders

**Testing Endpoints:**
- `POST /api/appointments/` - Create appointments
- `GET /api/appointments/` - List appointments
- `GET /api/doctors/` - Doctor listings
- `PUT /api/appointments/{id}/` - Update appointments

#### 4. Emergency Alerts and Notifications
- **Critical Symptom Detection**: Automatic triage flagging
- **Emergency Alerts**: Real-time alert system
- **Location Data**: GPS integration
- **Emergency Contacts**: Automated notifications

**Testing Endpoints:**
- `GET /api/emergency/alerts/` - Emergency alerts
- `POST /api/emergency/update-status/{id}/` - Status updates
- Real-time monitoring capabilities

#### 5. Medical History and Patient Records Management
- **Secure Storage**: Encrypted medical records
- **Role-based Access**: Patient/Doctor permissions
- **Timestamped Entries**: Complete audit trail
- **Medical History Viewing**: Patient portal

**Testing Endpoints:**
- `GET /api/patient/dashboard/` - Patient dashboard
- `GET /api/patient/symptoms/` - Symptom history
- `GET /api/patient/appointments/` - Appointment history

## Frontend Interfaces

### Patient Interface
- **HomeScreen**: Dashboard with health summary
- **SymptomReportScreen**: Symptom reporting
- **AppointmentsScreen**: Appointment management
- **ProfileScreen**: Medical history and profile

### Doctor Interface (Newly Added)
- **DoctorDashboard**: Doctor-specific dashboard
- **PatientManagementScreen**: Patient management
- **EmergencyResponseScreen**: Emergency response

## Testing Instructions

### 1. Backend Testing

#### Start the Backend Server
```bash
cd ai-healthcare-platform
python manage.py runserver
```

#### Run Automated Tests
```bash
python test_functional_requirements.py
```

This script will test all functional requirements and generate a detailed report.

### 2. Frontend Testing

#### Start the Web Application
```bash
cd ai-healthcare-platform/web-app
npm install
npm start
```

#### Test Patient Features
1. **Registration**: Navigate to `/register` and create a patient account
2. **Login**: Use credentials to login at `/login`
3. **Dashboard**: View health summary and recent activities
4. **Symptom Reporting**: Go to `/symptoms/report` to submit symptoms
5. **Appointments**: Manage appointments at `/appointments`
6. **Profile**: View medical history at `/profile`

#### Test Doctor Features
1. **Doctor Dashboard**: Access doctor-specific features
2. **Patient Management**: View and manage patients
3. **Emergency Response**: Monitor and respond to emergencies

### 3. API Testing

#### Test Authentication
```bash
# Register a patient
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testpatient",
    "password": "testpass123",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "Patient"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testpatient",
    "password": "testpass123"
  }'
```

#### Test Symptom Analysis
```bash
# Analyze symptoms
curl -X POST http://localhost:8000/api/symptoms/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "I have severe chest pain and difficulty breathing",
    "patient_id": 1,
    "language": "english"
  }'
```

#### Test Emergency Alerts
```bash
# Get emergency alerts
curl -X GET http://localhost:8000/api/emergency/alerts/

# Update emergency status
curl -X POST http://localhost:8000/api/emergency/update-status/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 1,
    "status": "in_progress",
    "notes": "Doctor responding"
  }'
```

### 4. Mobile App Testing

#### Start the Mobile App
```bash
cd ai-healthcare-platform/mobile
npm install
npx react-native run-android  # or run-ios
```

#### Test Mobile Features
1. **Symptom Reporting**: Use voice input and text input
2. **Emergency Alerts**: Test emergency call functionality
3. **Appointments**: Schedule and manage appointments
4. **Health Tips**: View personalized health advice

## Test Data

### Sample Patient Data
```json
{
  "username": "testpatient",
  "password": "testpass123",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "Patient",
  "phone_number": "+254700123456",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "address": "Test Address",
  "emergency_contact": "+254700789012"
}
```

### Sample Doctor Data
```json
{
  "username": "testdoctor",
  "password": "testpass123",
  "email": "doctor@example.com",
  "first_name": "Test",
  "last_name": "Doctor",
  "specialization": "general",
  "license_number": "DOC123456",
  "years_of_experience": 5
}
```

## Expected Test Results

### Backend API Tests
- ✅ All authentication endpoints working
- ✅ Symptom analysis and submission working
- ✅ Appointment management working
- ✅ Emergency alert system working
- ✅ Patient dashboard working
- ✅ Hospital capacity monitoring working

### Frontend Tests
- ✅ Patient interface fully functional
- ✅ Doctor interface newly implemented
- ✅ Emergency response system working
- ✅ Real-time updates working
- ✅ Mobile responsiveness working

### Integration Tests
- ✅ SMS/Voice webhooks functional
- ✅ Emergency alert notifications working
- ✅ Hospital capacity integration working
- ✅ Analytics dashboard working

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure Django server is running on port 8000
   - Check database migrations: `python manage.py migrate`

2. **Frontend Connection Error**
   - Verify API URL in `web-app/src/services/api.ts`
   - Check CORS settings in Django

3. **Authentication Issues**
   - Clear browser cache and localStorage
   - Verify user credentials in database

4. **Emergency Alerts Not Working**
   - Check emergency alert permissions
   - Verify notification settings

### Debug Mode

Enable debug mode for detailed error messages:

```bash
# Backend
export DEBUG=1
python manage.py runserver

# Frontend
REACT_APP_DEBUG=true npm start
```

## Performance Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoints
ab -n 100 -c 10 http://localhost:8000/api/health/
ab -n 100 -c 10 http://localhost:8000/api/analytics/dashboard/
```

### Database Performance
```bash
# Check database queries
python manage.py shell
from django.db import connection
connection.queries
```

## Security Testing

### Authentication Security
- Test password strength requirements
- Verify token expiration
- Check session management

### Data Protection
- Verify encrypted data storage
- Test role-based access control
- Check API endpoint security

## Conclusion

All functional requirements have been implemented and are testable. The system provides:

1. **Complete Patient Experience**: Registration, symptom reporting, appointments, medical history
2. **Doctor Interface**: Patient management, emergency response, appointment scheduling
3. **Emergency System**: Real-time alerts, location tracking, response coordination
4. **Multi-channel Support**: SMS, voice, mobile app, web interface
5. **AI Integration**: Symptom analysis, diagnosis, severity assessment
6. **Hospital Management**: Capacity monitoring, analytics, reporting

The system is ready for production deployment with all functional requirements satisfied.
