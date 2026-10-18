import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Linking,
} from 'react-native';
import {
  Card,
  Text,
  Button,
  useTheme,
  ActivityIndicator,
  IconButton,
  Chip,
  Divider,
  List,
  Badge,
  Portal,
  Modal,
  Surface,
} from 'react-native-paper';
import axios from 'axios';
import { format } from 'date-fns';
import { API_URL, DEV_CONFIG } from '../../config';
import { useAuth } from '../../contexts/AuthContext';

interface HealthSummary {
  recent_diagnosis: string;
  severity: string;
  next_appointment: string;
  unread_alerts: number;
}

interface HealthTip {
  id: number;
  title: string;
  description: string;
  category: string;
  icon: string;
}

interface AIRecommendation {
  id: number;
  type: 'health' | 'appointment' | 'medication' | 'lifestyle';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  actionable: boolean;
  action?: string;
}

const HomeScreen = ({ navigation }: any) => {
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [healthTips, setHealthTips] = useState<HealthTip[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [showSystemInfo, setShowSystemInfo] = useState(false);
  const [selectedTip, setSelectedTip] = useState<HealthTip | null>(null);
  const { user } = useAuth();
  const { theme } = useTheme();

  // Sample health tips data
  const sampleHealthTips: HealthTip[] = [
    {
      id: 1,
      title: 'Stay Hydrated',
      description: 'Drink at least 8 glasses of water daily to maintain good health.',
      category: 'Wellness',
      icon: 'water',
    },
    {
      id: 2,
      title: 'Regular Exercise',
      description: '30 minutes of moderate exercise daily can improve your overall health.',
      category: 'Fitness',
      icon: 'run',
    },
    {
      id: 3,
      title: 'Healthy Diet',
      description: 'Include fruits, vegetables, and whole grains in your daily meals.',
      category: 'Nutrition',
      icon: 'food-apple',
    },
  ];

  // Sample AI recommendations
  const sampleRecommendations: AIRecommendation[] = [
    {
      id: 1,
      type: 'health',
      title: 'Schedule Follow-up',
      description: 'Based on your recent symptoms, we recommend a follow-up appointment.',
      priority: 'high',
      actionable: true,
      action: 'Book Appointment',
    },
    {
      id: 2,
      type: 'lifestyle',
      title: 'Improve Sleep',
      description: 'Your sleep patterns suggest room for improvement. Try going to bed earlier.',
      priority: 'medium',
      actionable: true,
      action: 'View Tips',
    },
    {
      id: 3,
      type: 'medication',
      title: 'Medication Reminder',
      description: 'Don\'t forget to take your prescribed medication on time.',
      priority: 'high',
      actionable: true,
      action: 'Set Reminder',
    },
  ];

  const fetchSummary = async () => {
    try {
      if (DEV_CONFIG.mockData) {
        // Use mock data when backend is not connected
        console.log('Using mock data - backend not connected');
        setSummary({
          recent_diagnosis: 'Common Cold',
          severity: 'Low',
          next_appointment: '2024-01-15T10:00:00Z',
          unread_alerts: 2,
        });
        setError('');
      } else {
        const response = await axios.get(`${API_URL}/patients/${user?.id}/summary/`);
        setSummary(response.data);
        setError('');
      }
    } catch (err) {
      console.log('Backend connection failed - using mock data');
      setSummary({
        recent_diagnosis: 'Common Cold',
        severity: 'Low',
        next_appointment: '2024-01-15T10:00:00Z',
        unread_alerts: 2,
      });
      setError('');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    // Load sample data
    setHealthTips(sampleHealthTips);
    setRecommendations(sampleRecommendations);
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchSummary();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return theme.colors.error;
      case 'high':
        return '#FFA000';
      case 'moderate':
        return '#FFC107';
      default:
        return theme.colors.primary;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return theme.colors.error;
      case 'medium':
        return '#FFA000';
      case 'low':
        return theme.colors.primary;
      default:
        return theme.colors.primary;
    }
  };

  const handleEmergencyCall = () => {
    Alert.alert(
      'Emergency Services',
      'Do you want to call emergency services?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Call', 
          onPress: () => Linking.openURL('tel:911') 
        },
      ]
    );
  };

  const handleRecommendationAction = (recommendation: AIRecommendation) => {
    Alert.alert(
      'Action Taken',
      `You selected: ${recommendation.action}`,
      [{ text: 'OK' }]
    );
  };

  const handleTipPress = (tip: HealthTip) => {
    setSelectedTip(tip);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <>
      <ScrollView
        style={styles.container}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {error ? (
          <Text style={[styles.error, { color: theme.colors.error }]}>
            {error}
          </Text>
        ) : null}

        <View style={styles.header}>
          <View>
            <Text style={styles.welcomeText}>
              Welcome back, {user?.first_name}!
            </Text>
            <Text style={styles.subtitle}>
              Your AI-powered health companion
            </Text>
          </View>
          <View style={styles.headerActions}>
            <IconButton
              icon="bell"
              size={24}
              onPress={() => navigation.navigate('Alerts')}
              badge={summary?.unread_alerts}
            />
            <IconButton
              icon="information"
              size={24}
              onPress={() => setShowSystemInfo(true)}
            />
          </View>
        </View>

        {/* System Information Card */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>About This Platform</Text>
            <Text style={styles.systemDescription}>
              This AI Healthcare Platform connects you with healthcare providers through intelligent symptom analysis, 
              multi-channel communication, and emergency response systems. Designed for Makueni County Referral Hospital.
            </Text>
            <View style={styles.featureChips}>
              <Chip icon="robot" style={styles.chip}>AI Symptom Analysis</Chip>
              <Chip icon="message" style={styles.chip}>Multi-channel Support</Chip>
              <Chip icon="emergency" style={styles.chip}>Emergency Response</Chip>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Health Status</Text>
            <View style={styles.healthStatus}>
              <Text style={styles.diagnosis}>
                Recent Diagnosis: {summary?.recent_diagnosis || 'No recent diagnosis'}
              </Text>
              <Text
                style={[
                  styles.severity,
                  { color: getSeverityColor(summary?.severity || 'low') },
                ]}
              >
                Severity: {summary?.severity?.toUpperCase() || 'LOW'}
              </Text>
            </View>
          </Card.Content>
        </Card>

        {/* AI Recommendations */}
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>AI Recommendations</Text>
              <Chip icon="lightbulb" size="small">
                {recommendations.length} suggestions
              </Chip>
            </View>
            {recommendations.map((recommendation) => (
              <View key={recommendation.id} style={styles.recommendationItem}>
                <View style={styles.recommendationHeader}>
                  <Text style={styles.recommendationTitle}>
                    {recommendation.title}
                  </Text>
                  <Chip
                    label={recommendation.priority}
                    size="small"
                    style={[
                      styles.priorityChip,
                      { backgroundColor: getPriorityColor(recommendation.priority) }
                    ]}
                  />
                </View>
                <Text style={styles.recommendationDescription}>
                  {recommendation.description}
                </Text>
                {recommendation.actionable && recommendation.action && (
                  <Button
                    mode="outlined"
                    onPress={() => handleRecommendationAction(recommendation)}
                    style={styles.actionButton}
                  >
                    {recommendation.action}
                  </Button>
                )}
                <Divider style={styles.divider} />
              </View>
            ))}
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Next Appointment</Text>
            {summary?.next_appointment ? (
              <View style={styles.appointmentInfo}>
                <Text style={styles.appointmentDate}>
                  {format(new Date(summary.next_appointment), 'PPp')}
                </Text>
                <Button
                  mode="contained"
                  onPress={() => navigation.navigate('Appointments')}
                  style={styles.button}
                >
                  View Details
                </Button>
              </View>
            ) : (
              <Text style={styles.noAppointment}>No upcoming appointments</Text>
            )}
          </Card.Content>
        </Card>

        {/* Health Tips */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Daily Health Tips</Text>
            {healthTips.map((tip) => (
              <TouchableOpacity
                key={tip.id}
                style={styles.tipItem}
                onPress={() => handleTipPress(tip)}
              >
                <View style={styles.tipContent}>
                  <IconButton
                    icon={tip.icon}
                    size={24}
                    color={theme.colors.primary}
                  />
                  <View style={styles.tipText}>
                    <Text style={styles.tipTitle}>{tip.title}</Text>
                    <Text style={styles.tipDescription}>{tip.description}</Text>
                    <Chip label={tip.category} size="small" style={styles.categoryChip} />
                  </View>
                </View>
              </TouchableOpacity>
            ))}
          </Card.Content>
        </Card>

        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Symptoms')}
            >
              <IconButton
                icon="stethoscope"
                size={32}
                color={theme.colors.primary}
              />
              <Text style={styles.actionText}>Report Symptoms</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Appointments')}
            >
              <IconButton
                icon="calendar"
                size={32}
                color={theme.colors.primary}
              />
              <Text style={styles.actionText}>Book Appointment</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Profile')}
            >
              <IconButton
                icon="account"
                size={32}
                color={theme.colors.primary}
              />
              <Text style={styles.actionText}>View Profile</Text>
            </TouchableOpacity>
          </View>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Emergency Contact</Text>
            <Text style={styles.emergencyText}>
              In case of emergency, please contact your nearest healthcare provider
              or call emergency services.
            </Text>
            <Button
              mode="contained"
              onPress={handleEmergencyCall}
              style={[styles.button, styles.emergencyButton]}
              icon="phone"
            >
              Call Emergency Services
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>

      {/* System Information Modal */}
      <Portal>
        <Modal
          visible={showSystemInfo}
          onDismiss={() => setShowSystemInfo(false)}
          contentContainerStyle={styles.modalContainer}
        >
          <Surface style={styles.modalSurface}>
            <Text style={styles.modalTitle}>About AI Healthcare Platform</Text>
            <ScrollView>
              <Text style={styles.modalText}>
                This platform is designed to bridge the gap between patients and healthcare providers 
                through intelligent symptom analysis, multi-channel communication, and emergency response systems.
              </Text>
              <Text style={styles.modalSubtitle}>Key Features:</Text>
              <List.Item title="AI-Powered Symptom Analysis" left={(props) => <List.Icon {...props} icon="robot" />} />
              <List.Item title="Multi-Channel Accessibility" left={(props) => <List.Icon {...props} icon="cellphone" />} />
              <List.Item title="Emergency Response System" left={(props) => <List.Icon {...props} icon="emergency" />} />
              <List.Item title="Real-time Health Monitoring" left={(props) => <List.Icon {...props} icon="monitor" />} />
              <List.Item title="Multi-language Support" left={(props) => <List.Icon {...props} icon="translate" />} />
              <List.Item title="Community Health Worker Integration" left={(props) => <List.Icon {...props} icon="account-group" />} />
            </ScrollView>
            <Button
              mode="contained"
              onPress={() => setShowSystemInfo(false)}
              style={styles.modalButton}
            >
              Close
            </Button>
          </Surface>
        </Modal>
      </Portal>

      {/* Health Tip Modal */}
      <Portal>
        <Modal
          visible={!!selectedTip}
          onDismiss={() => setSelectedTip(null)}
          contentContainerStyle={styles.modalContainer}
        >
          {selectedTip && (
            <Surface style={styles.modalSurface}>
              <Text style={styles.modalTitle}>{selectedTip.title}</Text>
              <Text style={styles.modalText}>{selectedTip.description}</Text>
              <Chip label={selectedTip.category} style={styles.categoryChip} />
              <Button
                mode="contained"
                onPress={() => setSelectedTip(null)}
                style={styles.modalButton}
              >
                Got it!
              </Button>
            </Surface>
          )}
        </Modal>
      </Portal>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  headerActions: {
    flexDirection: 'row',
  },
  card: {
    margin: 16,
    marginTop: 8,
    elevation: 4,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  systemDescription: {
    fontSize: 16,
    color: '#555',
    marginBottom: 16,
  },
  featureChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    backgroundColor: '#E0E0E0',
  },
  healthStatus: {
    marginBottom: 8,
  },
  diagnosis: {
    fontSize: 16,
    marginBottom: 8,
  },
  severity: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  appointmentInfo: {
    alignItems: 'center',
  },
  appointmentDate: {
    fontSize: 18,
    marginBottom: 16,
  },
  noAppointment: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  quickActions: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    alignItems: 'center',
  },
  actionText: {
    marginTop: 8,
    fontSize: 14,
  },
  button: {
    marginTop: 8,
  },
  emergencyButton: {
    backgroundColor: '#FF5252',
  },
  emergencyText: {
    fontSize: 16,
    marginBottom: 16,
    color: '#666',
  },
  error: {
    textAlign: 'center',
    margin: 16,
  },
  // New styles for AI Recommendations and Health Tips
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  priorityChip: {
    backgroundColor: '#FFA000', // Default to medium
  },
  recommendationItem: {
    marginBottom: 16,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  recommendationDescription: {
    fontSize: 16,
    color: '#555',
    marginBottom: 12,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  tipContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  tipText: {
    marginLeft: 12,
    flex: 1,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  tipDescription: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  categoryChip: {
    marginTop: 8,
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalSurface: {
    width: '90%',
    padding: 20,
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    elevation: 5,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 15,
  },
  modalText: {
    fontSize: 16,
    color: '#555',
    marginBottom: 20,
    textAlign: 'justify',
  },
  modalSubtitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  modalButton: {
    marginTop: 10,
  },
  actionButton: {
    marginTop: 8,
  },
  divider: {
    marginTop: 12,
  },
});

export default HomeScreen; 