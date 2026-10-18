import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import {
  Card,
  Text,
  Button,
  useTheme,
  TextInput,
  Avatar,
  ActivityIndicator,
} from 'react-native-paper';
import axios from 'axios';
import { API_URL } from '../../config';
import { useAuth } from '../../contexts/AuthContext';

interface Profile {
  user: {
    first_name: string;
    last_name: string;
    email: string;
  };
  date_of_birth: string;
  gender: string;
  phone_number: string;
  address: string;
  emergency_contact: string;
  blood_type: string;
  allergies: string;
  chronic_conditions: string;
}

const ProfileScreen = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState('');
  const { user, signOut } = useAuth();
  const { theme } = useTheme();

  // Form state
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    emergency_contact: '',
    blood_type: '',
    allergies: '',
    chronic_conditions: '',
  });

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/patients/${user?.id}/`);
      setProfile(response.data);
      setFormData({
        first_name: response.data.user.first_name,
        last_name: response.data.user.last_name,
        phone_number: response.data.phone_number,
        address: response.data.address,
        emergency_contact: response.data.emergency_contact,
        blood_type: response.data.blood_type,
        allergies: response.data.allergies,
        chronic_conditions: response.data.chronic_conditions,
      });
      setError('');
    } catch (err) {
      setError('Failed to fetch profile');
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleUpdateProfile = async () => {
    try {
      await axios.patch(`${API_URL}/patients/${user?.id}/`, formData);
      setEditing(false);
      fetchProfile();
      Alert.alert('Success', 'Profile updated successfully');
    } catch (err) {
      setError('Failed to update profile');
      console.error('Error updating profile:', err);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (err) {
      setError('Failed to sign out');
      console.error('Error signing out:', err);
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
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Avatar.Text
          size={80}
          label={`${profile?.user.first_name[0]}${profile?.user.last_name[0]}`}
          style={styles.avatar}
        />
        <Text style={styles.name}>
          {profile?.user.first_name} {profile?.user.last_name}
        </Text>
        <Text style={styles.email}>{profile?.user.email}</Text>
      </View>

      <Card style={styles.card}>
        <Card.Content>
          {editing ? (
            <>
              <TextInput
                label="First Name"
                value={formData.first_name}
                onChangeText={(text) =>
                  setFormData({ ...formData, first_name: text })
                }
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Last Name"
                value={formData.last_name}
                onChangeText={(text) =>
                  setFormData({ ...formData, last_name: text })
                }
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Phone Number"
                value={formData.phone_number}
                onChangeText={(text) =>
                  setFormData({ ...formData, phone_number: text })
                }
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Address"
                value={formData.address}
                onChangeText={(text) =>
                  setFormData({ ...formData, address: text })
                }
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Emergency Contact"
                value={formData.emergency_contact}
                onChangeText={(text) =>
                  setFormData({ ...formData, emergency_contact: text })
                }
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Blood Type"
                value={formData.blood_type}
                onChangeText={(text) =>
                  setFormData({ ...formData, blood_type: text })
                }
                mode="outlined"
                style={styles.input}
              />
              <TextInput
                label="Allergies"
                value={formData.allergies}
                onChangeText={(text) =>
                  setFormData({ ...formData, allergies: text })
                }
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.input}
              />
              <TextInput
                label="Chronic Conditions"
                value={formData.chronic_conditions}
                onChangeText={(text) =>
                  setFormData({ ...formData, chronic_conditions: text })
                }
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.input}
              />
            </>
          ) : (
            <>
              <View style={styles.infoRow}>
                <Text style={styles.label}>Phone Number:</Text>
                <Text style={styles.value}>{profile?.phone_number}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.label}>Address:</Text>
                <Text style={styles.value}>{profile?.address}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.label}>Emergency Contact:</Text>
                <Text style={styles.value}>{profile?.emergency_contact}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.label}>Blood Type:</Text>
                <Text style={styles.value}>{profile?.blood_type}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.label}>Allergies:</Text>
                <Text style={styles.value}>{profile?.allergies}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.label}>Chronic Conditions:</Text>
                <Text style={styles.value}>{profile?.chronic_conditions}</Text>
              </View>
            </>
          )}

          {error ? (
            <Text style={[styles.error, { color: theme.colors.error }]}>
              {error}
            </Text>
          ) : null}

          <View style={styles.buttonContainer}>
            {editing ? (
              <>
                <Button
                  mode="contained"
                  onPress={handleUpdateProfile}
                  style={styles.button}
                >
                  Save Changes
                </Button>
                <Button
                  mode="outlined"
                  onPress={() => setEditing(false)}
                  style={styles.button}
                >
                  Cancel
                </Button>
              </>
            ) : (
              <Button
                mode="contained"
                onPress={() => setEditing(true)}
                style={styles.button}
              >
                Edit Profile
              </Button>
            )}
          </View>
        </Card.Content>
      </Card>

      <Button
        mode="outlined"
        onPress={handleSignOut}
        style={[styles.button, styles.signOutButton]}
      >
        Sign Out
      </Button>
    </ScrollView>
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
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#FFFFFF',
  },
  avatar: {
    marginBottom: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  email: {
    fontSize: 16,
    color: '#666',
  },
  card: {
    margin: 16,
    elevation: 4,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  label: {
    flex: 1,
    fontSize: 16,
    fontWeight: 'bold',
  },
  value: {
    flex: 2,
    fontSize: 16,
  },
  input: {
    marginBottom: 16,
  },
  buttonContainer: {
    marginTop: 16,
  },
  button: {
    marginBottom: 8,
  },
  signOutButton: {
    margin: 16,
  },
  error: {
    textAlign: 'center',
    marginBottom: 16,
  },
});

export default ProfileScreen; 