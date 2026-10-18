import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Activity, 
  Calendar, 
  User, 
  Wifi, 
  WifiOff,
  LogOut,
  Bell
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useConnectionStatus } from '../contexts/ConnectionContext';
import ConnectionStatus from './ConnectionStatus';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { connectionStatus } = useConnectionStatus();

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Symptoms', href: '/symptoms', icon: Activity },
    { name: 'Appointments', href: '/appointments', icon: Calendar },
    { name: 'Profile', href: '/profile', icon: User },
  ];

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                AI Healthcare Platform
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <ConnectionStatus />
              
              <div className="flex items-center space-x-2">
                <Bell className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-500">Notifications</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">
                  {user?.first_name} {user?.last_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
          <div className="p-4">
            <nav className="space-y-2">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`nav-link ${isActive ? 'active' : ''}`}
                  >
                    <item.icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
