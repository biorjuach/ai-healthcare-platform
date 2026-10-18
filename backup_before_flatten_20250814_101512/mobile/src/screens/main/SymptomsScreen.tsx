import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Card,
  useTheme,
  ActivityIndicator,
  Chip,
} from 'react-native-paper';
import axios from 'axios';
import { API_URL } from '../../config';
import { useAuth } from '../../contexts/AuthContext';

const SymptomsScreen = () => {
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<any>(null);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const { theme } = useTheme();

  const handleAnalyze = async () => {
    if (!symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await axios.post(
        `${API_URL}/patients/${user?.id}/analyze_symptoms/`,
        { symptoms }
      );
      setDiagnosis(response.data);
    } catch (err) {
      setError('Failed to analyze symptoms. Please try again.');
      console.error('Error analyzing symptoms:', err);
    } finally {
      setLoading(false);
    }
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

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.title}>Describe Your Symptoms</Text>
            <Text style={styles.subtitle}>
              Please provide detailed information about your symptoms
            </Text>

            <TextInput
              label="Symptoms"
              value={symptoms}
              onChangeText={setSymptoms}
              mode="outlined"
              multiline
              numberOfLines={4}
              style={styles.input}
              placeholder="Example: I have been experiencing fever, cough, and fatigue for the past 3 days..."
            />

            {error ? (
              <Text style={[styles.error, { color: theme.colors.error }]}>
                {error}
              </Text>
            ) : null}

            <Button
              mode="contained"
              onPress={handleAnalyze}
              style={styles.button}
              loading={loading}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Analyze Symptoms'}
            </Button>
          </Card.Content>
        </Card>

        {diagnosis && (
          <Card style={styles.card}>
            <Card.Content>
              <Text style={styles.title}>Analysis Results</Text>

              <View style={styles.resultSection}>
                <Text style={styles.label}>Probable Diagnosis:</Text>
                <Text style={styles.value}>{diagnosis.diagnosis_result.diagnosis}</Text>
              </View>

              <View style={styles.resultSection}>
                <Text style={styles.label}>Confidence:</Text>
                <Text style={styles.value}>
                  {(diagnosis.diagnosis_result.confidence * 100).toFixed(1)}%
                </Text>
              </View>

              <View style={styles.resultSection}>
                <Text style={styles.label}>Severity:</Text>
                <Chip
                  mode="outlined"
                  style={[
                    styles.severityChip,
                    { borderColor: getSeverityColor(diagnosis.diagnosis_result.severity) },
                  ]}
                  textStyle={{
                    color: getSeverityColor(diagnosis.diagnosis_result.severity),
                  }}
                >
                  {diagnosis.diagnosis_result.severity.toUpperCase()}
                </Chip>
              </View>

              <View style={styles.resultSection}>
                <Text style={styles.label}>Identified Symptoms:</Text>
                <View style={styles.symptomsList}>
                  {diagnosis.diagnosis_result.extracted_symptoms.map(
                    (symptom: string, index: number) => (
                      <Chip
                        key={index}
                        style={styles.symptomChip}
                        mode="outlined"
                      >
                        {symptom}
                      </Chip>
                    )
                  )}
                </View>
              </View>

              {diagnosis.diagnosis_result.severity === 'critical' && (
                <View style={styles.emergencySection}>
                  <Text style={[styles.emergencyText, { color: theme.colors.error }]}>
                    ⚠️ EMERGENCY: Please seek immediate medical attention
                  </Text>
                </View>
              )}
            </Card.Content>
          </Card>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  scrollContent: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 16,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
  error: {
    marginBottom: 16,
    textAlign: 'center',
  },
  resultSection: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  value: {
    fontSize: 18,
  },
  severityChip: {
    alignSelf: 'flex-start',
  },
  symptomsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  symptomChip: {
    margin: 4,
  },
  emergencySection: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#FFEBEE',
    borderRadius: 8,
  },
  emergencyText: {
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default SymptomsScreen; 