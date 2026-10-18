import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { MaterialIcons, MaterialCommunityIcons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import { usePost } from '../../hooks/useApiCall';
import ConnectionStatusComponent from '../../components/ConnectionStatus';

interface SymptomReportScreenProps {
  navigation: any;
}

interface SymptomAnalysis {
  severity: string;
  confidence: number;
  is_emergency: boolean;
  diagnosis: string;
  disease_predictions: any;
  risk_assessment: any;
  recommended_doctor: any;
}

const SymptomReportScreen: React.FC<SymptomReportScreenProps> = ({ navigation }) => {
  const [symptomText, setSymptomText] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [bodyLocation, setBodyLocation] = useState('');
  const [duration, setDuration] = useState('');
  const [severity, setSeverity] = useState('low');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<SymptomAnalysis | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [location, setLocation] = useState<any>(null);

  const languages = [
    { label: 'English', value: 'english' },
    { label: 'Swahili', value: 'swahili' },
  ];

  const severityLevels = [
    { label: 'Low', value: 'low' },
    { label: 'Medium', value: 'medium' },
    { label: 'High', value: 'high' },
    { label: 'Critical', value: 'critical' },
  ];

  const bodyLocations = [
    'Head',
    'Chest',
    'Abdomen',
    'Back',
    'Arms',
    'Legs',
    'Neck',
    'Face',
    'Eyes',
    'Ears',
    'Nose',
    'Throat',
    'General',
  ];

  const durationOptions = [
    'Less than 1 hour',
    '1-6 hours',
    '6-24 hours',
    '1-3 days',
    '3-7 days',
    'More than 1 week',
  ];

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location permission is required for emergency services.');
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({});
      setLocation(currentLocation);
    } catch (error) {
      console.log('Error getting location:', error);
    }
  };

  // Use the robust API hook for symptom analysis
  const {
    data: analysisData,
    loading: isAnalyzing,
    error: analysisError,
    retry: retryAnalysis,
  } = usePost('/symptoms/analyze/', {
          symptoms: symptomText,
          language: selectedLanguage,
  }, {
    autoFetch: false,
    retryOnError: true,
    retryAttempts: 3,
    onSuccess: (data) => {
        setAnalysis(data);
        
        // Check for emergency
        if (data.is_emergency) {
          Alert.alert(
            'EMERGENCY ALERT',
            'This appears to be an emergency. Please seek immediate medical attention or call emergency services.',
            [
              {
                text: 'Call Emergency',
                onPress: () => callEmergencyServices(),
                style: 'destructive',
              },
              {
                text: 'Continue',
                onPress: () => setCurrentStep(3),
              },
            ]
          );
        } else {
          setCurrentStep(3);
        }
    },
    onError: (error) => {
      Alert.alert('Error', error || 'Failed to analyze symptoms');
    },
  });

  const analyzeSymptoms = async () => {
    if (!symptomText.trim()) {
      Alert.alert('Error', 'Please describe your symptoms');
      return;
    }
    
    // The hook will handle the API call automatically
    retryAnalysis();
  };

  // Use the robust API hook for symptom submission
  const {
    data: submitData,
    loading: isSubmitting,
    error: submitError,
    retry: retrySubmit,
  } = usePost('/symptoms/submit/', {
          patient_id: 1, // This should come from user context
          symptoms: symptomText,
          input_method: 'app',
          language: selectedLanguage,
  }, {
    autoFetch: false,
    retryOnError: true,
    retryAttempts: 3,
    onSuccess: (data) => {
        Alert.alert(
          'Success',
          'Your symptom report has been submitted successfully. A healthcare provider will review it shortly.',
          [
            {
              text: 'OK',
              onPress: () => navigation.navigate('Dashboard'),
            },
          ]
        );
    },
    onError: (error) => {
      Alert.alert('Error', error || 'Failed to submit symptom report');
    },
  });

  const submitSymptomReport = async () => {
    if (!analysis) return;
    
    // The hook will handle the API call automatically
    retrySubmit();
  };

  const callEmergencyServices = () => {
    // This would integrate with phone dialer
    Alert.alert('Emergency Services', 'Please call emergency services immediately.');
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
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

  const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Step 1: Describe Your Symptoms</Text>
      
      <View style={styles.languageContainer}>
        <Text style={styles.label}>Language:</Text>
        <Picker
          selectedValue={selectedLanguage}
          onValueChange={setSelectedLanguage}
          style={styles.picker}
        >
          {languages.map((lang) => (
            <Picker.Item key={lang.value} label={lang.label} value={lang.value} />
          ))}
        </Picker>
      </View>

      <Text style={styles.label}>Describe your symptoms in detail:</Text>
      <TextInput
        style={styles.textInput}
        multiline
        numberOfLines={6}
        placeholder={
          selectedLanguage === 'swahili'
            ? 'Elezea dalili zako kwa undani...'
            : 'Describe your symptoms in detail...'
        }
        value={symptomText}
        onChangeText={setSymptomText}
        textAlignVertical="top"
      />

      <View style={styles.bodyLocationContainer}>
        <Text style={styles.label}>Body Location:</Text>
        <Picker
          selectedValue={bodyLocation}
          onValueChange={setBodyLocation}
          style={styles.picker}
        >
          <Picker.Item label="Select body location" value="" />
          {bodyLocations.map((location) => (
            <Picker.Item key={location} label={location} value={location} />
          ))}
        </Picker>
      </View>

      <View style={styles.durationContainer}>
        <Text style={styles.label}>Duration:</Text>
        <Picker
          selectedValue={duration}
          onValueChange={setDuration}
          style={styles.picker}
        >
          <Picker.Item label="Select duration" value="" />
          {durationOptions.map((option) => (
            <Picker.Item key={option} label={option} value={option} />
          ))}
        </Picker>
      </View>

      <View style={styles.severityContainer}>
        <Text style={styles.label}>Perceived Severity:</Text>
        <Picker
          selectedValue={severity}
          onValueChange={setSeverity}
          style={styles.picker}
        >
          {severityLevels.map((level) => (
            <Picker.Item key={level.value} label={level.label} value={level.value} />
          ))}
        </Picker>
      </View>

      <TouchableOpacity
        style={styles.button}
        onPress={analyzeSymptoms}
        disabled={isAnalyzing}
      >
        {isAnalyzing ? (
          <ActivityIndicator color="#ffffff" />
        ) : (
          <Text style={styles.buttonText}>
            {selectedLanguage === 'swahili' ? 'Chambua Dalili' : 'Analyze Symptoms'}
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );

  const renderStep2 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Step 2: AI Analysis</Text>
      <ActivityIndicator size="large" color="#007AFF" />
      <Text style={styles.analyzingText}>
        {selectedLanguage === 'swahili'
          ? 'AI inachambua dalili zako...'
          : 'AI is analyzing your symptoms...'}
      </Text>
    </View>
  );

  const renderStep3 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Step 3: Analysis Results</Text>
      
      {analysis && (
        <View style={styles.analysisContainer}>
          <View style={styles.severityIndicator}>
            <Text style={styles.severityLabel}>Severity Level:</Text>
            <View
              style={[
                styles.severityBadge,
                { backgroundColor: getSeverityColor(analysis.severity) },
              ]}
            >
              <Text style={styles.severityText}>{analysis.severity.toUpperCase()}</Text>
            </View>
          </View>

          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceLabel}>
              Confidence: {Math.round(analysis.confidence * 100)}%
            </Text>
            <View style={styles.confidenceBar}>
              <View
                style={[
                  styles.confidenceFill,
                  { width: `${analysis.confidence * 100}%` },
                ]}
              />
            </View>
          </View>

          <View style={styles.diagnosisContainer}>
            <Text style={styles.diagnosisLabel}>Preliminary Diagnosis:</Text>
            <Text style={styles.diagnosisText}>{analysis.diagnosis}</Text>
          </View>

          {analysis.risk_assessment && (
            <View style={styles.riskContainer}>
              <Text style={styles.riskLabel}>Risk Assessment:</Text>
              <Text style={styles.riskText}>
                Level: {analysis.risk_assessment.risk_level}
              </Text>
              <Text style={styles.riskText}>
                Score: {Math.round(analysis.risk_assessment.risk_score * 100)}%
              </Text>
            </View>
          )}

          {analysis.recommended_doctor && (
            <View style={styles.doctorContainer}>
              <Text style={styles.doctorLabel}>Recommended Doctor:</Text>
              <Text style={styles.doctorText}>
                Dr. {analysis.recommended_doctor.user.first_name}{' '}
                {analysis.recommended_doctor.user.last_name}
              </Text>
              <Text style={styles.specializationText}>
                {analysis.recommended_doctor.specialization}
              </Text>
            </View>
          )}

          {analysis.is_emergency && (
            <View style={styles.emergencyContainer}>
              <MaterialIcons name="warning" size={24} color="#ff0000" />
              <Text style={styles.emergencyText}>
                This appears to be an emergency. Please seek immediate medical attention.
              </Text>
            </View>
          )}
        </View>
      )}

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={() => setCurrentStep(1)}
        >
          <Text style={styles.secondaryButtonText}>Back</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={submitSymptomReport}>
          <Text style={styles.buttonText}>
            {selectedLanguage === 'swahili' ? 'Wasilisha Ripoti' : 'Submit Report'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ConnectionStatusComponent 
        onRetry={() => {
          if (analysisError) retryAnalysis();
          if (submitError) retrySubmit();
        }}
        showDetails={true}
      />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
          <View style={styles.header}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <MaterialIcons name="arrow-back" size={24} color="#007AFF" />
            </TouchableOpacity>
            <Text style={styles.headerTitle}>
              {selectedLanguage === 'swahili' ? 'Ripoti ya Dalili' : 'Symptom Report'}
            </Text>
          </View>

          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  { width: `${(currentStep / 3) * 100}%` },
                ]}
              />
            </View>
            <Text style={styles.progressText}>
              Step {currentStep} of 3
            </Text>
          </View>

          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333333',
  },
  progressContainer: {
    padding: 16,
    backgroundColor: '#ffffff',
  },
  progressBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 14,
    color: '#666666',
    textAlign: 'center',
  },
  stepContainer: {
    padding: 16,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 20,
  },
  languageContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  picker: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
  },
  textInput: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 120,
    marginBottom: 16,
  },
  bodyLocationContainer: {
    marginBottom: 16,
  },
  durationContainer: {
    marginBottom: 16,
  },
  severityContainer: {
    marginBottom: 24,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  analyzingText: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    marginTop: 16,
  },
  analysisContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  severityIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  severityLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginRight: 12,
  },
  severityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  severityText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  confidenceContainer: {
    marginBottom: 16,
  },
  confidenceLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  confidenceBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
  diagnosisContainer: {
    marginBottom: 16,
  },
  diagnosisLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  diagnosisText: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 20,
  },
  riskContainer: {
    marginBottom: 16,
  },
  riskLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  riskText: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 4,
  },
  doctorContainer: {
    marginBottom: 16,
  },
  doctorLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  doctorText: {
    fontSize: 14,
    color: '#333333',
    fontWeight: '500',
    marginBottom: 4,
  },
  specializationText: {
    fontSize: 14,
    color: '#666666',
  },
  emergencyContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff5f5',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#ff0000',
  },
  emergencyText: {
    fontSize: 14,
    color: '#ff0000',
    fontWeight: '500',
    marginLeft: 8,
    flex: 1,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  secondaryButton: {
    backgroundColor: '#f8f9fa',
    borderWidth: 1,
    borderColor: '#007AFF',
    flex: 0.48,
  },
  secondaryButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default SymptomReportScreen; 