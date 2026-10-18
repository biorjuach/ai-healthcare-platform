import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Snackbar,
  Tooltip,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  SpeedDial,
  SpeedDialIcon,
  SpeedDialAction,
  Fade,
  Zoom,
  Slide,
  Grow,
  Fab,
  Badge,
  Avatar,
  CardActionArea,
  Collapse,
  AlertTitle,
  Skeleton,
  Rating,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  People,
  LocalHospital,
  Emergency,
  Notifications,
  Refresh,
  Visibility,
  AccessTime,
  Search,
  ExpandMore,
  Lightbulb,
  Info,
  Settings,
  Assessment,
  NotificationsActive,
  TrendingUp,
  TrendingDown,
  Speed,
  Timeline,
  Analytics,
  Dashboard as DashboardIcon,
  Add,
  Edit,
  Delete,
  Star,
  StarBorder,
  Favorite,
  FavoriteBorder,
  ThumbUp,
  ThumbDown,
  Share,
  Download,
  Print,
  Email,
  Phone,
  LocationOn,
  Schedule,
  PriorityHigh,
  Warning,
  Check,
  Close,
  ExpandLess,
  KeyboardArrowUp,
  KeyboardArrowDown,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area } from 'recharts';
import ConnectionStatus from './ConnectionStatus';
import { 
  useDashboardStats, 
  useEmergencyAlerts, 
  useHospitalCapacity, 
  useSymptomAnalysis,
  useConnectionStatus 
} from '../hooks/useApiCall';
import { apiService } from '../services/apiService';

interface DashboardProps {}

interface EmergencyAlert {
  id: number;
  patientName?: string; // Optional for backward compatibility
  patient?: {
    id: number;
    user: {
      id: number;
      username: string;
      email: string;
      first_name: string;
      last_name: string;
      profile: any;
    };
    // ... other patient fields
  };
  symptom?: string | {
    id: number;
    description: string;
    severity: string;
    body_location: string;
    duration: string;
    // ... other symptom fields
  };
  severity: string;
  severity_level?: string; // New API uses this
  location: string;
  status: string;
  createdAt: string;
  created_at?: string; // New API uses this
  assigned_responder?: any;
  emergency_type?: string;
  response_time?: number;
  resolved_at?: string;
}

interface Recommendation {
  id: number;
  type: 'system' | 'patient' | 'resource' | 'emergency';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  actionable: boolean;
  action?: string;
  impact: string;
  createdAt: string;
}

interface SystemInfo {
  name: string;
  version: string;
  description: string;
  features: string[];
  capabilities: string[];
  targetUsers: string[];
  deploymentLocation: string;
}

const Dashboard: React.FC<DashboardProps> = () => {
  // API hooks for robust data fetching
  const {
    data: systemStats,
    loading: statsLoading,
    error: statsError,
    refetch: refetchStats,
    retry: retryStats
  } = useDashboardStats();

  const {
    data: emergencyAlertsData,
    loading: alertsLoading,
    error: alertsError,
    refetch: refetchAlerts,
    retry: retryAlerts
  } = useEmergencyAlerts();

  const {
    data: hospitalCapacityData,
    loading: capacityLoading,
    error: capacityError,
    refetch: refetchCapacity,
    retry: retryCapacity
  } = useHospitalCapacity();

  const {
    data: symptomAnalysisData,
    loading: symptomsLoading,
    error: symptomsError,
    refetch: refetchSymptoms,
    retry: retrySymptoms
  } = useSymptomAnalysis();

  const connectionStatus = useConnectionStatus();

  // Local state
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [selectedEmergency, setSelectedEmergency] = useState<EmergencyAlert | null>(null);
  const [emergencyDialogOpen, setEmergencyDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showNotifications, setShowNotifications] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [systemInfoExpanded, setSystemInfoExpanded] = useState<string | false>(false);
  const [realTimeUpdates, setRealTimeUpdates] = useState(true);

  // New interactive state variables
  const [expandedCards, setExpandedCards] = useState<{ [key: string]: boolean }>({});
  const [favoriteAlerts, setFavoriteAlerts] = useState<number[]>([]);
  const [selectedChartType, setSelectedChartType] = useState<'line' | 'bar' | 'area'>('line');
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showAnimations, setShowAnimations] = useState(true);
  const [selectedView, setSelectedView] = useState<'overview' | 'analytics' | 'emergencies' | 'performance'>('overview');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const [recentActivities, setRecentActivities] = useState<any[]>([]);
  const [quickActions, setQuickActions] = useState<any[]>([]);
  const [systemHealth, setSystemHealth] = useState<'excellent' | 'good' | 'warning' | 'critical'>('good');
  const [performanceMetrics, setPerformanceMetrics] = useState({
    responseTime: 0,
    uptime: 99.9,
    activeUsers: 0,
    systemLoad: 0
  });

  // Extract data from API responses
  const emergencyAlerts = emergencyAlertsData?.emergency_alerts || [];
  const hospitalCapacity = hospitalCapacityData?.departments || [];
  const symptomAnalysis = symptomAnalysisData || null;

  // Overall loading and connection status
  const isLoading = statsLoading || alertsLoading || capacityLoading || symptomsLoading;
  const isConnected = connectionStatus.isConnected;
  const hasError = statsError || alertsError || capacityError || symptomsError;

  // Dynamic data for charts based on real data or fallback
  const symptomTrendData = symptomAnalysis?.trend_data || [
    { date: 'Mon', reports: 45, emergencies: 3 },
    { date: 'Tue', reports: 52, emergencies: 5 },
    { date: 'Wed', reports: 38, emergencies: 2 },
    { date: 'Thu', reports: 67, emergencies: 8 },
    { date: 'Fri', reports: 41, emergencies: 4 },
    { date: 'Sat', reports: 29, emergencies: 1 },
    { date: 'Sun', reports: 33, emergencies: 2 },
  ];

  const communicationData = symptomAnalysis?.communication_channels || [
    { channel: 'Mobile App', percentage: 45 },
    { channel: 'SMS', percentage: 30 },
    { channel: 'Voice Calls', percentage: 15 },
    { channel: 'Web Portal', percentage: 10 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  // Sample recommendations data
  const sampleRecommendations: Recommendation[] = [
    {
      id: 1,
      type: 'emergency',
      title: 'Increase Emergency Response Team',
      description: 'High emergency volume detected. Consider adding 2 more emergency response personnel.',
      priority: 'high',
      category: 'Staffing',
      actionable: true,
      action: 'Contact HR for emergency staff allocation',
      impact: 'Reduce response time by 30%',
      createdAt: new Date().toISOString(),
    },
    {
      id: 2,
      type: 'resource',
      title: 'Optimize Bed Allocation',
      description: 'ICU occupancy at 95%. Consider transferring stable patients to general wards.',
      priority: 'critical',
      category: 'Resource Management',
      actionable: true,
      action: 'Review patient status and transfer eligible cases',
      impact: 'Free up 3 ICU beds',
      createdAt: new Date().toISOString(),
    },
    {
      id: 3,
      type: 'system',
      title: 'Update AI Model',
      description: 'Symptom analysis accuracy has improved. Consider retraining model with new data.',
      priority: 'medium',
      category: 'AI Optimization',
      actionable: true,
      action: 'Schedule model retraining',
      impact: 'Improve accuracy by 5%',
      createdAt: new Date().toISOString(),
    },
    {
      id: 4,
      type: 'patient',
      title: 'Follow-up Required',
      description: '15 patients with chronic conditions haven\'t reported symptoms in 7 days.',
      priority: 'medium',
      category: 'Patient Care',
      actionable: true,
      action: 'Send automated follow-up messages',
      impact: 'Improve patient engagement',
      createdAt: new Date().toISOString(),
    },
  ];

  // Sample system information
  const sampleSystemInfo: SystemInfo = {
    name: 'AI Healthcare Platform',
    version: '2.1.0',
    description: 'A comprehensive, AI-powered healthcare platform designed to bridge the gap between patients and healthcare providers through intelligent symptom analysis, multi-channel communication, and emergency response systems.',
    features: [
      'AI-Powered Symptom Analysis',
      'Multi-Channel Accessibility (Mobile, SMS, Voice, Web)',
      'Emergency Response System',
      'Real-time Health Monitoring',
      'Multi-language Support (English & Swahili)',
      'Community Health Worker Integration'
    ],
    capabilities: [
      'Intelligent diagnosis using ML algorithms',
      'Real-time emergency detection and alerts',
      'GPS-based location tracking',
      'Voice-to-text processing',
      'Automated appointment scheduling',
      'Predictive health analytics'
    ],
    targetUsers: [
      'Healthcare Providers (Doctors, Nurses)',
      'Patients in resource-limited settings',
      'Community Health Workers',
      'Hospital Administrators',
      'Emergency Response Teams'
    ],
    deploymentLocation: 'Makueni County Referral Hospital, Kenya',
  };

  // Initialize mock data and system info
  useEffect(() => {
    setRecommendations(sampleRecommendations);
    setSystemInfo(sampleSystemInfo);
  }, []);

  // Set up real-time updates
  useEffect(() => {
    if (!realTimeUpdates) return;

    const interval = setInterval(() => {
      refetchStats();
      refetchAlerts();
      refetchCapacity();
      refetchSymptoms();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [realTimeUpdates, refetchStats, refetchAlerts, refetchCapacity, refetchSymptoms]);

  // Handle connection restoration
  useEffect(() => {
    if (isConnected && hasError) {
      // Auto-retry when connection is restored
      setTimeout(() => {
        if (statsError) retryStats();
        if (alertsError) retryAlerts();
        if (capacityError) retryCapacity();
        if (symptomsError) retrySymptoms();
      }, 1000);
    }
  }, [isConnected, hasError, statsError, alertsError, capacityError, symptomsError, retryStats, retryAlerts, retryCapacity, retrySymptoms]);

  const handleEmergencyClick = (emergency: EmergencyAlert) => {
    setSelectedEmergency(emergency);
    setEmergencyDialogOpen(true);
  };

  const handleEmergencyStatusUpdate = async (status: string, notes?: string) => {
    if (!selectedEmergency) return;

    try {
      // Call the API to update emergency status
      const response = await apiService.updateEmergencyStatus(selectedEmergency.id, status);
      
      // Close dialog first
      setEmergencyDialogOpen(false);
      
      // Show success message
      setSnackbarMessage(`Emergency status updated to ${status} successfully!`);
      setSnackbarOpen(true);
      
      // Refresh emergency alerts data to get updated information
      await refetchAlerts();
      
      // Optionally refresh other data too
      refetchStats();
      
    } catch (error: any) {
      console.error('Error updating emergency status:', error);
      
      // Close dialog on error too
      setEmergencyDialogOpen(false);
      
      // Handle different types of errors
      let errorMessage = 'Emergency status update failed.';
      
      if (error.type === 'network') {
        errorMessage = 'Network error - please check your connection and try again.';
      } else if (error.type === 'server') {
        errorMessage = 'Server error - please try again later.';
      } else if (error.type === 'validation') {
        errorMessage = `Validation error: ${error.message}`;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      
      setSnackbarMessage(errorMessage);
      setSnackbarOpen(true);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '#ff0000';
      case 'high':
        return '#ff6600';
      case 'medium':
        return '#ffcc00';
      case 'low':
        return '#00cc00';
      default:
        return '#666666';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'error';
      case 'resolved':
        return 'success';
      case 'in_progress':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Interactive functions
  const handleRecommendationAction = (recommendation: Recommendation) => {
    setSnackbarMessage(`Action taken: ${recommendation.action}`);
    setSnackbarOpen(true);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (type: 'severity' | 'status', value: string) => {
    if (type === 'severity') {
      setFilterSeverity(value);
    } else {
      setFilterStatus(value);
    }
  };



  const handleRealTimeToggle = () => {
    setRealTimeUpdates(!realTimeUpdates);
    setSnackbarMessage(`Real-time updates ${!realTimeUpdates ? 'enabled' : 'disabled'}`);
    setSnackbarOpen(true);
  };

  const filteredEmergencyAlerts = (emergencyAlerts || []).filter((alert: EmergencyAlert) => {
    if (!alert || !alert.id) return false; // Skip invalid alerts
    
    // Handle new API structure where patientName and symptom might be objects or undefined
    const patientName = typeof alert.patientName === 'string' ? alert.patientName : 
                       (alert.patient?.user?.first_name && alert.patient?.user?.last_name) ? 
                       `${alert.patient.user.first_name} ${alert.patient.user.last_name}` : 
                       'Unknown Patient';
    
    const symptomText = typeof alert.symptom === 'string' ? alert.symptom : 
                       (alert.symptom?.description || 'No symptoms recorded');
    
    const alertLocation = alert.location || 'Unknown location';
    
    const matchesSearch = searchTerm === '' || 
                         patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         symptomText.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alertLocation.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSeverity = filterSeverity === 'all' || getSeverityDisplay(alert) === filterSeverity;
    const matchesStatus = filterStatus === 'all' || (alert.status || 'active') === filterStatus;
    
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return '#ff0000';
      case 'high':
        return '#ff6600';
      case 'medium':
        return '#ffcc00';
      case 'low':
        return '#00cc00';
      default:
        return '#666666';
    }
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'emergency':
        return <Emergency />;
      case 'resource':
        return <LocalHospital />;
      case 'system':
        return <Settings />;
      case 'patient':
        return <People />;
      default:
        return <Lightbulb />;
    }
  };

  // Helper functions to safely extract values from emergency alerts
  const getPatientDisplayName = (alert: EmergencyAlert): string => {
    if (!alert) return 'Unknown Patient';
    
    if (typeof alert.patientName === 'string') {
      return alert.patientName;
    }
    if (alert.patient?.user?.first_name && alert.patient?.user?.last_name) {
      return `${alert.patient.user.first_name} ${alert.patient.user.last_name}`;
    }
    if (alert.patient?.user?.first_name) {
      return alert.patient.user.first_name;
    }
    return 'Unknown Patient';
  };

  const getSymptomDisplayText = (alert: EmergencyAlert): string => {
    if (typeof alert.symptom === 'string') {
      return alert.symptom;
    }
    if (alert.symptom?.description) {
      return alert.symptom.description;
    }
    return 'Unknown Symptom';
  };

  const getSeverityDisplay = (alert: EmergencyAlert): string => {
    if (!alert) return 'Unknown';
    return alert.severity_level || alert.severity || 'medium';
  };

  // Interactive helper functions
  const toggleCardExpansion = (cardId: string) => {
    setExpandedCards(prev => ({
      ...prev,
      [cardId]: !prev[cardId]
    }));
  };

  const toggleFavoriteAlert = (alertId: number) => {
    setFavoriteAlerts(prev => 
      prev.includes(alertId) 
        ? prev.filter(id => id !== alertId)
        : [...prev, alertId]
    );
  };

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'refresh':
        refetchAlerts(); // Assuming refetchAlerts is the correct one for refresh
        showSnackbar('Data refreshed successfully', 'success');
        break;
      case 'export':
        exportData();
        break;
      case 'print':
        window.print();
        break;
      case 'fullscreen':
        setIsFullscreen(!isFullscreen);
        break;
      default:
        break;
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  const exportData = () => {
    const data = {
      emergencyAlerts,
      systemStats,
      timestamp: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showSnackbar('Data exported successfully', 'success');
  };

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return '#4caf50';
      case 'good': return '#8bc34a';
      case 'warning': return '#ff9800';
      case 'critical': return '#f44336';
      default: return '#8bc34a';
    }
  };

  const getSystemHealthIcon = (health: string) => {
    switch (health) {
      case 'excellent': return <CheckCircle color="success" />;
      case 'good': return <CheckCircle color="success" />;
      case 'warning': return <Warning color="warning" />;
      case 'critical': return <Error color="error" />;
      default: return <CheckCircle color="success" />;
    }
  };

  const simulateRealTimeUpdates = () => {
    if (autoRefresh && realTimeUpdates) { // Use realTimeUpdates state
      setTimeout(() => {
        refetchAlerts(); // Assuming refetchAlerts is the correct one for refresh
        updatePerformanceMetrics();
        setNotificationCount(prev => prev + Math.floor(Math.random() * 3));
      }, 30000); // Update every 30 seconds
    }
  };

  const updatePerformanceMetrics = () => {
    setPerformanceMetrics({
      responseTime: Math.random() * 100 + 50,
      uptime: 99.9 - Math.random() * 0.1,
      activeUsers: Math.floor(Math.random() * 50) + 10,
      systemLoad: Math.random() * 100
    });
  };

  return (
    <Box sx={{ 
      p: 3, 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated background particles */}
      <Box sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity: 0.1,
        pointerEvents: 'none',
        zIndex: 0
      }}>
        {[...Array(20)].map((_, i) => (
          <Box
            key={i}
            sx={{
              position: 'absolute',
              width: 4,
              height: 4,
              borderRadius: '50%',
              background: '#fff',
              animation: `float ${3 + i * 0.2}s ease-in-out infinite`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              '@keyframes float': {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: 'translateY(-20px)' }
              }
            }}
          />
        ))}
      </Box>

      {/* Header with interactive controls */}
      <Fade in timeout={1000}>
        <Box sx={{ position: 'relative', zIndex: 1, mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h3" fontWeight="bold" color="white" gutterBottom>
                🏥 AI Healthcare Dashboard
              </Typography>
              <Typography variant="subtitle1" color="rgba(255,255,255,0.8)">
                Real-time monitoring and intelligent healthcare management
              </Typography>
            </Box>
            
            <Box display="flex" gap={2} alignItems="center">
              <ConnectionStatus />
              
              <ToggleButtonGroup
                value={selectedView}
                exclusive
                onChange={(_, newValue) => newValue && setSelectedView(newValue)}
                size="small"
                sx={{ bgcolor: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}
              >
                <ToggleButton value="overview" sx={{ color: 'white' }}>
                  <DashboardIcon sx={{ mr: 1 }} />
                  Overview
                </ToggleButton>
                <ToggleButton value="analytics" sx={{ color: 'white' }}>
                  <Analytics sx={{ mr: 1 }} />
                  Analytics
                </ToggleButton>
                <ToggleButton value="emergencies" sx={{ color: 'white' }}>
                  <Emergency sx={{ mr: 1 }} />
                  Emergencies
                </ToggleButton>
                <ToggleButton value="performance" sx={{ color: 'white' }}>
                  <Speed sx={{ mr: 1 }} />
                  Performance
                </ToggleButton>
              </ToggleButtonGroup>

              <Badge badgeContent={notificationCount} color="error">
                <IconButton 
                  color="inherit" 
                  onClick={() => showSnackbar('Notifications panel opened', 'info')}
                  sx={{ color: 'white' }}
                >
                  <Notifications />
                </IconButton>
              </Badge>

              <IconButton 
                color="inherit" 
                onClick={() => handleQuickAction('refresh')}
                sx={{ color: 'white' }}
              >
                <Refresh />
              </IconButton>
        </Box>
          </Box>

          {/* System Health Status */}
          <Slide direction="up" in timeout={800}>
            <Card sx={{ 
              bgcolor: 'rgba(255,255,255,0.1)', 
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.2)'
            }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={2}>
                    {getSystemHealthIcon(systemHealth)}
        <Box>
                      <Typography variant="h6" color="white">
                        System Health: {systemHealth.toUpperCase()}
          </Typography>
                      <Typography variant="body2" color="rgba(255,255,255,0.8)">
                        Response Time: {performanceMetrics.responseTime.toFixed(1)}ms | 
                        Uptime: {performanceMetrics.uptime.toFixed(1)}% | 
                        Active Users: {performanceMetrics.activeUsers}
          </Typography>
        </Box>
                  </Box>
                  
                  <Box display="flex" gap={1}>
          <FormControlLabel
            control={
              <Switch
                          checked={autoRefresh} 
                          onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
                      label="Auto Refresh"
                      sx={{ color: 'white' }}
                    />
                    <FormControlLabel
                      control={
                        <Switch 
                          checked={showAnimations} 
                          onChange={(e) => setShowAnimations(e.target.checked)}
                          color="primary"
                        />
                      }
                      label="Animations"
                      sx={{ color: 'white' }}
          />
        </Box>
      </Box>
              </CardContent>
            </Card>
          </Slide>
        </Box>
      </Fade>

      {/* System Information Accordion */}
      <Accordion 
        expanded={systemInfoExpanded === 'system'} 
        onChange={() => setSystemInfoExpanded(systemInfoExpanded === 'system' ? false : 'system')}
        sx={{ mb: 3 }}
      >
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box display="flex" alignItems="center" gap={1}>
            <Info color="primary" />
            <Typography variant="h6">About This System</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {systemInfo && (
            <Box display="flex" flexWrap="wrap" gap={3}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  System Overview
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Name:</strong> {systemInfo.name} v{systemInfo.version}
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Location:</strong> {systemInfo.deploymentLocation}
                </Typography>
                <Typography variant="body2" paragraph>
                  {systemInfo.description}
                </Typography>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Key Features
                </Typography>
                <List dense>
                  {systemInfo.features.map((feature, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon>
                        <CheckCircle color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={feature} />
                    </ListItem>
                  ))}
                </List>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Target Users
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {systemInfo.targetUsers.map((user, index) => (
                    <Chip key={index} label={user} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>

      {/* System Statistics Cards */}
      <Box display="flex" flexWrap="wrap" gap={3} sx={{ mb: 3 }}>
        <Grow in timeout={1200}>
          <Box sx={{ flex: 1, minWidth: 200 }}>
            <CardActionArea onClick={() => toggleCardExpansion('patients')}>
              <Card sx={{ 
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                }
              }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Patients
                  </Typography>
                      <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                    {systemStats?.totalPatients || 0}
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={1}>
                        <TrendingUp color="success" fontSize="small" />
                        <Typography variant="body2" color="success.main">
                          +12% this week
                  </Typography>
                </Box>
                    </Box>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                      <People sx={{ fontSize: 30 }} />
                    </Avatar>
              </Box>
            </CardContent>
          </Card>
            </CardActionArea>
          </Box>
        </Grow>

        <Grow in timeout={1400}>
          <Box sx={{ flex: 1, minWidth: 200 }}>
            <CardActionArea onClick={() => toggleCardExpansion('doctors')}>
              <Card sx={{ 
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                }
              }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Doctors
                  </Typography>
                      <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                    {systemStats?.totalDoctors || 0}
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={1}>
                        <CheckCircle color="success" fontSize="small" />
                        <Typography variant="body2" color="success.main">
                          All available
                  </Typography>
                </Box>
                    </Box>
                    <Avatar sx={{ bgcolor: 'secondary.main', width: 56, height: 56 }}>
                      <LocalHospital sx={{ fontSize: 30 }} />
                    </Avatar>
              </Box>
            </CardContent>
          </Card>
            </CardActionArea>
          </Box>
        </Grow>

        <Grow in timeout={1600}>
          <Box sx={{ flex: 1, minWidth: 200 }}>
            <CardActionArea onClick={() => toggleCardExpansion('emergencies')}>
              <Card sx={{ 
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                }
              }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Emergencies
                  </Typography>
                      <Typography variant="h4" component="div" color="error" sx={{ fontWeight: 'bold' }}>
                    {systemStats?.activeEmergencies || 0}
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={1}>
                        <PriorityHigh color="error" fontSize="small" />
                        <Typography variant="body2" color="error.main">
                          Requires attention
                  </Typography>
                </Box>
                    </Box>
                    <Avatar sx={{ bgcolor: 'error.main', width: 56, height: 56 }}>
                      <Emergency sx={{ fontSize: 30 }} />
                    </Avatar>
              </Box>
            </CardContent>
          </Card>
            </CardActionArea>
          </Box>
        </Grow>

        <Grow in timeout={1800}>
          <Box sx={{ flex: 1, minWidth: 200 }}>
            <CardActionArea onClick={() => toggleCardExpansion('response')}>
              <Card sx={{ 
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                }
              }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                        Avg Response Time
                  </Typography>
                      <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                        {performanceMetrics.responseTime.toFixed(0)}ms
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1} mt={1}>
                        <Speed color="info" fontSize="small" />
                        <Typography variant="body2" color="info.main">
                          Excellent
                  </Typography>
                </Box>
                    </Box>
                    <Avatar sx={{ bgcolor: 'info.main', width: 56, height: 56 }}>
                      <Speed sx={{ fontSize: 30 }} />
                    </Avatar>
              </Box>
            </CardContent>
          </Card>
            </CardActionArea>
          </Box>
        </Grow>
      </Box>

      {/* AI Recommendations Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <Lightbulb color="primary" />
              <Typography variant="h6">AI-Powered Recommendations</Typography>
            </Box>
            <Chip 
              label={`${recommendations.length} recommendations`} 
              color="primary" 
              size="small" 
            />
          </Box>
          
          <Box display="flex" flexWrap="wrap" gap={2}>
            {recommendations.map((recommendation) => (
              <Box key={recommendation.id} sx={{ flex: 1, minWidth: 300 }}>
                <Card variant="outlined" sx={{ 
                  borderLeft: `4px solid ${getPriorityColor(recommendation.priority)}`,
                  '&:hover': { boxShadow: 2 }
                }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getRecommendationIcon(recommendation.type)}
                        <Typography variant="subtitle1" fontWeight="bold">
                          {recommendation.title}
                        </Typography>
                      </Box>
                      <Chip 
                        label={recommendation.priority} 
                        size="small"
                        sx={{ 
                          backgroundColor: getPriorityColor(recommendation.priority),
                          color: 'white'
                        }}
                      />
                    </Box>
                    
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {recommendation.description}
                    </Typography>
                    
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Chip label={recommendation.category} size="small" variant="outlined" />
                      <Typography variant="caption" color="textSecondary">
                        Impact: {recommendation.impact}
                      </Typography>
                    </Box>
                    
                    {recommendation.actionable && recommendation.action && (
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => handleRecommendationAction(recommendation)}
                        sx={{ mt: 1 }}
                      >
                        {recommendation.action}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Charts and Analytics */}
      <Box display="flex" flexWrap="wrap" gap={3} sx={{ mb: 3 }}>
        {/* Symptom Trends Chart */}
        <Box sx={{ flex: 1, minWidth: 600 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Symptom Reports Trend (Last 7 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={symptomTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line
                    type="monotone"
                    dataKey="reports"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Total Reports"
                  />
                  <Line
                    type="monotone"
                    dataKey="emergencies"
                    stroke="#ff0000"
                    strokeWidth={2}
                    name="Emergencies"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>

        {/* Communication Channels */}
        <Box sx={{ flex: 1, minWidth: 400 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Communication Channels
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={communicationData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ channel, percentage }) => `${channel}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="percentage"
                  >
                    {communicationData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Emergency Alerts and Hospital Capacity */}
      <Box display="flex" flexWrap="wrap" gap={3} sx={{ mb: 3 }}>
        {/* Enhanced Emergency Alerts */}
        <Box sx={{ flex: 1, minWidth: 600 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Active Emergency Alerts
                </Typography>
                <Chip
                  label={`${filteredEmergencyAlerts.length} Active`}
                  color="error"
                  size="small"
                />
              </Box>
              
              {/* Search and Filter Controls */}
              <Box display="flex" gap={2} mb={2}>
                <TextField
                  size="small"
                  placeholder="Search patients or symptoms..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ flexGrow: 1 }}
                />
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Severity</InputLabel>
                  <Select
                    value={filterSeverity}
                    label="Severity"
                    onChange={(e) => handleFilterChange('severity', e.target.value)}
                  >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={filterStatus}
                    label="Status"
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                  >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="in_progress">In Progress</MenuItem>
                    <MenuItem value="resolved">Resolved</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              {filteredEmergencyAlerts.length === 0 ? (
                <Alert severity="info">
                  {emergencyAlerts.length === 0 
                    ? 'No active emergency alerts at this time.'
                    : 'No alerts match your search criteria.'
                  }
                </Alert>
              ) : (
                <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                  <Table stickyHeader size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Patient</TableCell>
                        <TableCell>Symptom</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredEmergencyAlerts.map((alert: EmergencyAlert) => (
                        <TableRow key={alert.id} hover>
                          <TableCell>
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {getPatientDisplayName(alert)}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {alert.location}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={getSymptomDisplayText(alert)}>
                              <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                                {getSymptomDisplayText(alert)}
                              </Typography>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={getSeverityDisplay(alert)}
                              size="small"
                              sx={{
                                backgroundColor: getSeverityColor(getSeverityDisplay(alert)),
                                color: 'white',
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={alert.status}
                              color={getStatusColor(alert.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View details">
                              <IconButton
                                size="small"
                                onClick={() => handleEmergencyClick(alert)}
                              >
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Hospital Capacity */}
        <Box sx={{ flex: 1, minWidth: 400 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Hospital Capacity
              </Typography>
              
              {hospitalCapacity.map((dept: any) => (
                <Box key={dept.department} mb={2}>
                                     <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                     <Typography variant="body2" fontWeight="medium">
                       {dept.department}
                     </Typography>
                     <Typography variant="body2" color="textSecondary">
                       {dept.occupied_beds}/{dept.total_beds} beds
                     </Typography>
                   </Box>
                   <LinearProgress
                     variant="determinate"
                     value={(dept.occupied_beds / dept.total_beds) * 100}
                     sx={{
                       height: 8,
                       borderRadius: 4,
                       backgroundColor: '#e0e0e0',
                       '& .MuiLinearProgress-bar': {
                         backgroundColor: (dept.occupied_beds / dept.total_beds) * 100 > 80 ? '#ff0000' : 
                                         (dept.occupied_beds / dept.total_beds) * 100 > 60 ? '#ffcc00' : '#00cc00',
                       },
                     }}
                   />
                   <Box display="flex" justifyContent="space-between" mt={0.5}>
                     <Typography variant="caption" color="textSecondary">
                       {dept.available_doctors} doctors available
                     </Typography>
                     <Typography variant="caption" color="textSecondary">
                       {Math.round((dept.occupied_beds / dept.total_beds) * 100)}% occupied
                     </Typography>
                   </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Top Symptoms and System Performance */}
      <Box display="flex" flexWrap="wrap" gap={3}>
        {/* Top Symptoms */}
        <Box sx={{ flex: 1, minWidth: 600 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Reported Symptoms
              </Typography>
              <List>
                {symptomAnalysis?.topSymptoms.map((symptom: any, index: number) => (
                  <React.Fragment key={symptom.name}>
                    <ListItem>
                      <ListItemIcon>
                        <Chip
                          label={index + 1}
                          size="small"
                          color="primary"
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={symptom.name}
                        secondary={`${symptom.count} reports`}
                      />
                      <Typography variant="body2" color="textSecondary">
                        {Math.round((symptom.count / (symptomAnalysis?.totalReports || 1)) * 100)}%
                      </Typography>
                    </ListItem>
                    {index < symptomAnalysis.topSymptoms.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* System Performance */}
        <Box sx={{ flex: 1, minWidth: 400 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Performance
              </Typography>
              
              <Box mb={3}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">AI Confidence Score</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {Math.round((symptomAnalysis?.averageConfidence || 0) * 100)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(symptomAnalysis?.averageConfidence || 0) * 100}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box mb={3}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Response Time</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {connectionStatus.responseTime || 0}ms
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min((connectionStatus.responseTime || 0) / 1000 * 100, 100)}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: (connectionStatus.responseTime || 0) < 500 ? '#00cc00' : 
                                      (connectionStatus.responseTime || 0) < 1000 ? '#ffcc00' : '#ff0000',
                    },
                  }}
                />
              </Box>

              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  System Status
                </Typography>
                <Box display="flex" gap={1}>
                  <Chip
                    icon={<CheckCircle />}
                    label="AI Services"
                    color="success"
                    size="small"
                  />
                  <Chip
                    icon={<CheckCircle />}
                    label="Database"
                    color="success"
                    size="small"
                  />
                  <Chip
                    icon={<CheckCircle />}
                    label="SMS Gateway"
                    color="success"
                    size="small"
                  />
                  <Chip
                    icon={<CheckCircle />}
                    label="Voice Gateway"
                    color="success"
                    size="small"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Enhanced Emergency Alert Dialog */}
      <Dialog
        open={emergencyDialogOpen}
        onClose={() => setEmergencyDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Emergency color="error" />
            Emergency Alert Details
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedEmergency && (
            <Box>
              <Box display="flex" flexWrap="wrap" gap={2}>
                <Box sx={{ flex: 1, minWidth: 200 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Patient Name
                  </Typography>
                  <Typography variant="body1">
                    {getPatientDisplayName(selectedEmergency)}
                  </Typography>
                </Box>
                <Box sx={{ flex: 1, minWidth: 200 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Severity
                  </Typography>
                  <Chip
                    label={getSeverityDisplay(selectedEmergency)}
                    sx={{
                      backgroundColor: getSeverityColor(getSeverityDisplay(selectedEmergency)),
                      color: 'white',
                    }}
                  />
                </Box>
                <Box sx={{ flex: 1, minWidth: 200 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Symptom Description
                  </Typography>
                  <Typography variant="body1">
                    {getSymptomDisplayText(selectedEmergency)}
                  </Typography>
                </Box>
                <Box sx={{ flex: 1, minWidth: 200 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Location
                  </Typography>
                  <Typography variant="body1">
                    {selectedEmergency.location}
                  </Typography>
                </Box>
                <Box sx={{ flex: 1, minWidth: 200 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Reported At
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedEmergency.created_at || selectedEmergency.createdAt).toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmergencyDialogOpen(false)}>
            Close
          </Button>
          <Button
            onClick={() => handleEmergencyStatusUpdate('in_progress')}
            color="warning"
            startIcon={<AccessTime />}
          >
            Mark In Progress
          </Button>
          <Button
            onClick={() => handleEmergencyStatusUpdate('resolved')}
            color="success"
            startIcon={<CheckCircle />}
          >
            Mark Resolved
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      />

      {/* Speed Dial for quick actions */}
      <SpeedDial
        ariaLabel="Quick actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Refresh />}
          tooltipTitle="Refresh Data"
          onClick={() => {
            refetchStats();
            refetchAlerts();
            refetchCapacity();
            refetchSymptoms();
          }}
        />
        <SpeedDialAction
          icon={<Notifications />}
          tooltipTitle="Notifications"
          onClick={() => showSnackbar('Notifications panel opened', 'info')}
        />
        <SpeedDialAction
          icon={<Assessment />}
          tooltipTitle="Analytics"
          onClick={() => {/* Navigate to analytics */}}
        />
        <SpeedDialAction
          icon={<Settings />}
          tooltipTitle="Settings"
          onClick={() => {/* Handle settings */}}
        />
      </SpeedDial>

      {/* Floating Action Button */}
      <SpeedDial
        ariaLabel="Quick Actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Refresh />}
          tooltipTitle="Refresh Data"
          onClick={() => handleQuickAction('refresh')}
        />
        <SpeedDialAction
          icon={<Download />}
          tooltipTitle="Export Data"
          onClick={() => handleQuickAction('export')}
        />
        <SpeedDialAction
          icon={<Print />}
          tooltipTitle="Print Report"
          onClick={() => handleQuickAction('print')}
        />
        <SpeedDialAction
          icon={<Share />}
          tooltipTitle="Share Dashboard"
          onClick={() => showSnackbar('Share feature coming soon!', 'info')}
        />
      </SpeedDial>

      {/* Enhanced Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity={snackbarOpen ? 'success' : 'info'} // Assuming severity is based on open state
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>

      {/* Expanded Card Details */}
      {Object.entries(expandedCards).map(([cardId, isExpanded]) => (
        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <Card sx={{ mt: 2, mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {cardId.charAt(0).toUpperCase() + cardId.slice(1)} Details
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Detailed information about {cardId} will be displayed here.
              </Typography>
            </CardContent>
          </Card>
        </Collapse>
      ))}

      {/* Quick Actions Panel */}
      <Box sx={{ 
        position: 'fixed', 
        top: '50%', 
        right: 16, 
        transform: 'translateY(-50%)',
        zIndex: 1000
      }}>
        <Card sx={{ 
          bgcolor: 'rgba(255,255,255,0.9)', 
          backdropFilter: 'blur(10px)',
          borderRadius: 2
        }}>
          <CardContent sx={{ p: 1 }}>
            <Box display="flex" flexDirection="column" gap={1}>
              <Tooltip title="System Health" placement="left">
                <IconButton 
                  size="small"
                  onClick={() => showSnackbar(`System Health: ${systemHealth}`, 'info')}
                >
                  {getSystemHealthIcon(systemHealth)}
                </IconButton>
              </Tooltip>
              <Tooltip title="Performance Metrics" placement="left">
                <IconButton 
                  size="small"
                  onClick={() => showSnackbar(`Response Time: ${performanceMetrics.responseTime.toFixed(1)}ms`, 'info')}
                >
                  <Speed />
                </IconButton>
              </Tooltip>
              <Tooltip title="Notifications" placement="left">
                <IconButton 
                  size="small"
                  onClick={() => showSnackbar(`${notificationCount} new notifications`, 'info')}
                >
                  <Badge badgeContent={notificationCount} color="error">
                    <Notifications />
                  </Badge>
                </IconButton>
              </Tooltip>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Dashboard; 