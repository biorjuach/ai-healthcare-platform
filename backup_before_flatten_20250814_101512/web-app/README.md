# AI Healthcare Platform - Web Application

A modern, responsive web-based version of the AI Healthcare Platform mobile app, built with React, TypeScript, and Tailwind CSS.

## 🚀 Features

### Core Functionality
- **🔐 Secure Authentication** - JWT-based authentication with session management
- **🏠 Health Dashboard** - Real-time health summary with AI-powered insights
- **📝 Symptom Reporting** - Multi-step AI-powered symptom analysis
- **📅 Appointment Management** - Schedule, edit, and cancel appointments
- **👤 Profile Management** - Complete user profile with medical history
- **🔗 Connection Monitoring** - Real-time backend connectivity status

### AI-Powered Features
- **🧠 Symptom Analysis** - AI-powered symptom assessment and disease prediction
- **🚨 Emergency Detection** - Automatic emergency detection with location services
- **💡 Health Recommendations** - Personalized health tips and treatment suggestions
- **📊 Health Analytics** - Symptom trends and health statistics

### User Experience
- **📱 Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **🌍 Multi-language Support** - English and Swahili interfaces
- **⚡ Real-time Updates** - Live data synchronization with backend
- **🔔 Toast Notifications** - User-friendly feedback and alerts
- **🎨 Modern UI/UX** - Clean, intuitive interface with Tailwind CSS

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query** - Server state management
- **React Hook Form** - Form handling and validation
- **Lucide React** - Beautiful icons
- **Framer Motion** - Smooth animations

### Backend Integration
- **Axios** - HTTP client for API communication
- **JWT Authentication** - Secure token-based auth
- **Real-time Health Checks** - Connection monitoring
- **RESTful API** - Complete backend integration

## 📦 Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend server running (see main project README)

### Setup Instructions

#### Option 1: Automated Setup (Recommended)

**For Windows:**
```cmd
cd web-app
setup.bat
```

**For Linux/Mac:**
```bash
cd web-app
chmod +x setup.sh
./setup.sh
```

#### Option 2: Manual Setup

1. **Navigate to the web-app directory**
   ```bash
   cd web-app
   ```

2. **Clean up any existing installation**
   ```bash
   # Remove existing node_modules and package-lock.json
   rm -rf node_modules package-lock.json
   ```

3. **Install dependencies with legacy peer deps**
   ```bash
   npm install --legacy-peer-deps
   ```
   
   If that fails, try:
   ```bash
   npm install --force
   ```

4. **Configure environment variables**
   Create a `.env` file in the web-app directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```

5. **Start the development server**
   ```bash
   npm start
   ```

6. **Open your browser**
   Navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
web-app/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── ConnectionStatus.tsx
│   │   └── LoadingSpinner.tsx
│   ├── contexts/
│   │   ├── AuthContext.tsx
│   │   └── ConnectionContext.tsx
│   ├── screens/
│   │   ├── auth/
│   │   │   └── LoginScreen.tsx
│   │   └── main/
│   │       ├── HomeScreen.tsx
│   │       ├── SymptomsScreen.tsx
│   │       ├── SymptomReportScreen.tsx
│   │       ├── AppointmentsScreen.tsx
│   │       └── ProfileScreen.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── README.md
```

## 🔧 Configuration

### Tailwind CSS
The app uses Tailwind CSS with custom color schemes for healthcare theming:
- Primary: Blue shades for main actions
- Secondary: Green shades for success states
- Danger: Red shades for errors and emergencies
- Warning: Orange shades for warnings

### API Configuration
The app is configured to connect to the Django backend at `http://localhost:8000` by default. Update the `REACT_APP_API_URL` environment variable to point to your backend server.

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Static Hosting
The built files in the `build/` directory can be deployed to any static hosting service:
- Netlify
- Vercel
- AWS S3
- GitHub Pages

### Environment Variables for Production
Set the following environment variables in your hosting platform:
- `REACT_APP_API_URL` - Your production backend URL

## 🔐 Authentication

The web app uses JWT-based authentication:
1. Users log in with username/password
2. JWT token is stored in localStorage
3. Token is automatically included in API requests
4. Automatic logout on token expiration

### Demo Credentials
- Username: `patient1`
- Password: `testpass123`

## 📱 Responsive Design

The web app is fully responsive and optimized for:
- **Desktop** (1024px+) - Full sidebar navigation
- **Tablet** (768px - 1023px) - Adaptive layout
- **Mobile** (< 768px) - Mobile-first design

## 🔗 API Integration

The web app integrates with the following backend endpoints:

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Symptoms
- `POST /api/symptoms/analyze/` - AI symptom analysis
- `POST /api/symptoms/submit/` - Submit symptom report
- `GET /api/patient/symptoms/` - Get patient symptoms

### Appointments
- `GET /api/patient/appointments/` - Get patient appointments
- `POST /api/appointments/` - Create appointment
- `PUT /api/appointments/{id}/` - Update appointment
- `DELETE /api/appointments/{id}/` - Cancel appointment

### Dashboard
- `GET /api/patient/dashboard/` - Patient dashboard data
- `GET /api/hospital/capacity/` - Hospital capacity info
- `GET /api/health/` - Health check endpoint

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Run Tests with Coverage
```bash
npm test -- --coverage
```

## 🐛 Troubleshooting

### Common Issues

1. **npm install fails with ERESOLVE errors**
   ```bash
   # Solution 1: Use legacy peer deps
   npm install --legacy-peer-deps
   
   # Solution 2: Force install
   npm install --force
   
   # Solution 3: Clean install
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

2. **'react-scripts' is not recognized**
   - This usually happens when npm install fails
   - Follow the solutions above for ERESOLVE errors
   - Ensure you're in the correct directory (web-app)

3. **TypeScript version conflicts**
   - The project uses TypeScript 4.9.5 for compatibility with react-scripts
   - If you see TypeScript version errors, run: `npm install --legacy-peer-deps`

4. **Backend Connection Failed**
   - Ensure the Django backend is running on port 8000
   - Check CORS settings in Django
   - Verify the `REACT_APP_API_URL` environment variable

5. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install --legacy-peer-deps`
   - Check TypeScript errors: `npx tsc --noEmit`

6. **Authentication Issues**
   - Clear browser localStorage
   - Check JWT token expiration
   - Verify backend authentication endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the AI Healthcare Platform and follows the same license terms.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the backend API documentation
3. Open an issue in the repository

---

**Built with ❤️ for better healthcare access**
