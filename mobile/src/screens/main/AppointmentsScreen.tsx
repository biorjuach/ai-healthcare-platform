import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import {
  Card,
  Text,
  Button,
  useTheme,
  ActivityIndicator,
  FAB,
  Portal,
  Dialog,
  TextInput,
} from 'react-native-paper';
import axios from 'axios';
import { format } from 'date-fns';
import { API_URL } from '../../config';
import { useAuth } from '../../contexts/AuthContext';

interface Appointment {
  id: number;
  doctor: {
    user: {
      first_name: string;
      last_name: string;
    };
    specialization: string;
  };
  hospital: {
    name: string;
    address: string;
  };
  appointment_date: string;
  status: string;
  notes: string;
}

const AppointmentsScreen = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [showNewAppointment, setShowNewAppointment] = useState(false);
  const [showDoctorSelection, setShowDoctorSelection] = useState(false);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedDoctorId, setSelectedDoctorId] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const { user } = useAuth();
  const { theme } = useTheme();

  const fetchAppointments = async () => {
    try {
      const response = await axios.get(`${API_URL}/appointments/`);
      setAppointments(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch appointments');
      console.error('Error fetching appointments:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
    // Fetch available doctors
    const fetchDoctors = async () => {
      try {
        const response = await axios.get(`${API_URL}/doctors/`);
        setDoctors(response.data);
      } catch (err) {
        console.error('Error fetching doctors:', err);
      }
    };
    fetchDoctors();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchAppointments();
  };

  const handleNewAppointment = async () => {
    if (!selectedDate || !selectedTime || !selectedDoctorId) {
      setError('Please select date, time and doctor');
      return;
    }

    try {
      const appointmentDateTime = `${selectedDate}T${selectedTime}`;
      await axios.post(`${API_URL}/api/appointments/`, {
        date: selectedDate,
        time: selectedTime,
        notes,
        doctor: selectedDoctorId,
        symptoms: notes || 'Regular checkup'
      });
      setShowNewAppointment(false);
      fetchAppointments();
    } catch (err) {
      setError('Failed to create appointment');
      console.error('Error creating appointment:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return theme.colors.primary;
      case 'completed':
        return '#4CAF50';
      case 'cancelled':
        return theme.colors.error;
      default:
        return '#757575';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {error ? (
          <Text style={[styles.error, { color: theme.colors.error }]}>
            {error}
          </Text>
        ) : null}

        {appointments.map((appointment) => (
          <Card key={appointment.id} style={styles.card}>
            <Card.Content>
              <View style={styles.appointmentHeader}>
                <Text style={styles.doctorName}>
                  Dr. {appointment.doctor.user.first_name}{' '}
                  {appointment.doctor.user.last_name}
                </Text>
                <Text
                  style={[
                    styles.status,
                    { color: getStatusColor(appointment.status) },
                  ]}
                >
                  {appointment.status.toUpperCase()}
                </Text>
              </View>

              <Text style={styles.specialization}>
                {appointment.doctor.specialization}
              </Text>

              <View style={styles.details}>
                <Text style={styles.hospitalName}>
                  {appointment.hospital.name}
                </Text>
                <Text style={styles.hospitalAddress}>
                  {appointment.hospital.address}
                </Text>
                <Text style={styles.dateTime}>
                  {format(new Date(appointment.appointment_date), 'PPp')}
                </Text>
              </View>

              {appointment.notes && (
                <Text style={styles.notes}>Notes: {appointment.notes}</Text>
              )}

              {appointment.status === 'scheduled' && (
                <Button
                  mode="outlined"
                  onPress={() => {
                    // Handle cancellation
                  }}
                  style={styles.cancelButton}
                >
                  Cancel Appointment
                </Button>
              )}
            </Card.Content>
          </Card>
        ))}
      </ScrollView>

      <Portal>
        <Dialog
          visible={showNewAppointment}
          onDismiss={() => setShowNewAppointment(false)}
        >
          <Dialog.Title>New Appointment</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="Select Doctor"
              value={doctors.find(d => d.id === selectedDoctorId) ? 
                `Dr. ${doctors.find(d => d.id === selectedDoctorId).user.first_name} ${doctors.find(d => d.id === selectedDoctorId).user.last_name} - ${doctors.find(d => d.id === selectedDoctorId).specialization}` : 
                ''}
              mode="outlined"
              style={styles.input}
              onPressIn={() => setShowDoctorSelection(true)}
              right={<TextInput.Icon icon="chevron-down" />}
            />
            <TextInput
              label="Date"
              value={selectedDate}
              onChangeText={setSelectedDate}
              mode="outlined"
              placeholder="YYYY-MM-DD"
              style={styles.input}
            />
            <TextInput
              label="Time"
              value={selectedTime}
              onChangeText={setSelectedTime}
              mode="outlined"
              placeholder="HH:MM"
              style={styles.input}
            />
            <TextInput
              label="Notes"
              value={notes}
              onChangeText={setNotes}
              mode="outlined"
              multiline
              numberOfLines={3}
              style={styles.input}
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setShowNewAppointment(false)}>Cancel</Button>
            <Button onPress={handleNewAppointment}>Schedule</Button>
          </Dialog.Actions>
        </Dialog>

        <Dialog
          visible={showDoctorSelection}
          onDismiss={() => setShowDoctorSelection(false)}
        >
          <Dialog.Title>Select Doctor</Dialog.Title>
          <Dialog.Content>
            <ScrollView style={styles.doctorList}>
              {doctors.map((doctor) => (
                <TouchableOpacity
                  key={doctor.id}
                  onPress={() => {
                    setSelectedDoctorId(doctor.id);
                    setShowDoctorSelection(false);
                  }}
                  style={[
                    styles.doctorOption,
                    selectedDoctorId === doctor.id && styles.selectedDoctorOption
                  ]}
                >
                  <View style={styles.doctorInfo}>
                    <Text style={styles.doctorName}>
                      Dr. {doctor.user.first_name} {doctor.user.last_name}
                    </Text>
                    <Text style={styles.doctorSpecialization}>
                      {doctor.specialization}
                    </Text>
                    <Text style={styles.doctorExperience}>
                      {doctor.years_of_experience} years of experience
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setShowDoctorSelection(false)}>Cancel</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      <FAB
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        icon="plus"
        onPress={() => setShowNewAppointment(true)}
      />
    </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  appointmentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  doctorName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  status: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  specialization: {
    fontSize: 16,
    color: '#666',
    marginBottom: 12,
  },
  details: {
    marginBottom: 12,
  },
  hospitalName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  hospitalAddress: {
    fontSize: 14,
    color: '#666',
  },
  dateTime: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  notes: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  cancelButton: {
    marginTop: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  input: {
    marginBottom: 16,
  },
  error: {
    textAlign: 'center',
    marginBottom: 16,
  },
  doctorList: {
    maxHeight: 300,
  },
  doctorOption: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  selectedDoctorOption: {
    backgroundColor: '#E3F2FD',
  },
  doctorInfo: {
    flex: 1,
  },
  doctorSpecialization: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  doctorExperience: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
});

export default AppointmentsScreen; 