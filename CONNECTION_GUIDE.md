# Frontend-Backend Connection Guide

## Overview

The AI Healthcare Platform consists of:
- **Frontend**: React Admin Dashboard (port 3000) + React Native Mobile App
- **Backend**: Django REST API (port 8000)

## Current Status

✅ **Frontend**: Fully functional with mock data
❌ **Backend**: Needs to be started to enable real data

## How to Connect Frontend and Backend

### Step 1: Start the Backend Server

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies (if not already done)
pip install -r ../requirements.txt

# Start Django development server
python manage.py runserver 8000
```

### Step 2: Start the Frontend

```bash
# In a new terminal, navigate to admin dashboard
cd admin-dashboard

# Start React development server
npm start
```

### Step 3: Verify Connection

1. **Admin Dashboard**: 
   - Open `http://localhost:3000`
   - Look for "Backend Connected" chip (green = connected, red = offline)
   - Check browser console for connection logs

2. **Mobile App**:
   - Set `mockData: false` in `mobile/src/config.ts`
   - Run the mobile app
   - Check for real data vs mock data

## Connection Indicators

### Admin Dashboard
- **Green "Backend Connected"**: Backend is running and responding
- **Red "Backend Offline"**: Backend is not running, using mock data
- **Console logs**: Show connection attempts and fallback to mock data

### Mobile App
- **Mock Data**: When `DEV_CONFIG.mockData = true`
- **Real Data**: When backend is connected and `mockData = false`

## API Endpoints

The frontend tries to connect to these backend endpoints:

### Admin Dashboard
- `GET /api/analytics/dashboard/` - System statistics
- `GET /api/emergency/alerts/` - Emergency alerts
- `GET /api/hospital/capacity/` - Hospital capacity
- `POST /api/emergency/update-status/` - Update emergency status

### Mobile App
- `GET /api/patients/{id}/summary/` - Patient health summary
- `POST /api/auth/login/` - User authentication
- `GET /api/appointments/` - Patient appointments

## Troubleshooting

### Backend Won't Start
1. Check if port 8000 is available
2. Verify Python dependencies are installed
3. Check Django migrations: `python manage.py migrate`

### Frontend Can't Connect
1. Verify backend is running on `http://localhost:8000`
2. Check CORS settings in `backend/settings.py`
3. Look for network errors in browser console

### Mobile App Issues
1. Ensure `API_URL` is correct in `mobile/src/config.ts`
2. Check if device can reach `localhost:8000`
3. For physical devices, use your computer's IP address instead of localhost

## Development Workflow

1. **Start Backend First**: Always start Django server before frontend
2. **Check Connection**: Verify the connection status indicators
3. **Use Mock Data**: When backend is offline, frontend gracefully falls back to mock data
4. **Real Data**: When backend is connected, frontend uses real API data

## Configuration Files

### Admin Dashboard
- `admin-dashboard/package.json`: Proxy configuration for API calls
- `admin-dashboard/src/components/Dashboard.tsx`: API endpoints and error handling

### Mobile App
- `mobile/src/config.ts`: API URL and development settings
- `mobile/src/screens/main/HomeScreen.tsx`: Mock data fallback

### Backend
- `backend/settings.py`: CORS and server configuration
- `backend/urls.py`: API endpoint definitions

## Benefits of This Setup

1. **Graceful Degradation**: Frontend works with or without backend
2. **Development Flexibility**: Can develop frontend independently
3. **Clear Status Indicators**: Users know when backend is connected
4. **Mock Data**: Realistic data for testing and demonstration
5. **Easy Switching**: Toggle between mock and real data 