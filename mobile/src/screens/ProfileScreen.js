import React, { useState, useCallback } from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';
import * as api from '../api/client';
import Button from '../components/Button';
import { Card, Field, StateMessage } from '../components/UI';
import { colors, spacing } from '../theme';

export default function ProfileScreen({ navigation }) {
  const { user, isAuthenticated, loading, logout, updateProfile } = useAuth();
  const [plants, setPlants] = useState([]);
  const [plantsError, setPlantsError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [saveMessage, setSaveMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useFocusEffect(
    useCallback(() => {
      if (!isAuthenticated) return;
      setUsername(user?.username || '');
      setEmail(user?.email || '');
      (async () => {
        setPlantsError(null);
        try {
          setPlants(await api.listPlants());
        } catch (err) {
          setPlantsError(err.message);
        }
      })();
    }, [isAuthenticated, user]),
  );

  if (loading) {
    return (
      <View style={styles.screen}>
        <View style={styles.container}>
          <StateMessage>Loading…</StateMessage>
        </View>
      </View>
    );
  }

  if (!isAuthenticated) {
    return (
      <View style={styles.screen}>
        <View style={styles.container}>
          <StateMessage>
            Sign in to manage your account and see your plant collection on
            this device.
          </StateMessage>
          <Button title="Sign In" onPress={() => navigation.navigate('Login')} />
        </View>
      </View>
    );
  }

  const handleSave = async () => {
    setSaving(true);
    setSaveMessage('');
    try {
      await updateProfile({ username: username.trim(), email: email.trim() });
      setSaveMessage('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (err) {
      setSaveMessage(err.message || 'Error updating profile');
    } finally {
      setSaving(false);
    }
  };

  const handleDeletePlant = (plant) => {
    Alert.alert('Remove plant', `Remove ${plant.name} from your collection?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: async () => {
          try {
            await api.deletePlant(plant.id);
            setPlants(plants.filter((p) => p.id !== plant.id));
          } catch (err) {
            setPlantsError(err.message);
          }
        },
      },
    ]);
  };

  const handleLogout = () => {
    Alert.alert('Sign out', 'Sign out of PlantCare?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: () => logout() },
    ]);
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.container}>
      <View style={styles.avatarRow}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{user?.username?.charAt(0).toUpperCase()}</Text>
        </View>
        <View style={styles.headerText}>
          <Text style={styles.title}>{user?.username}</Text>
          <Text style={styles.email}>{user?.email}</Text>
          {user?.createdAt ? (
            <Text style={styles.joined}>
              Joined {new Date(user.createdAt).toLocaleDateString()}
            </Text>
          ) : null}
        </View>
      </View>

      {saveMessage ? <StateMessage kind="success">{saveMessage}</StateMessage> : null}

      <Card>
        <View style={styles.sectionHeader}>
          <Text style={styles.h2}>Account</Text>
          {!isEditing && (
            <Button title="Edit" variant="secondary" onPress={() => setIsEditing(true)} />
          )}
        </View>

        {isEditing ? (
          <View>
            <Field
              label="Username"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              editable={!saving}
            />
            <Field
              label="Email"
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
              editable={!saving}
            />
            <View style={styles.actionRow}>
              <Button title={saving ? 'Saving…' : 'Save'} onPress={handleSave} loading={saving} style={styles.actionBtn} />
              <Button
                title="Cancel"
                variant="secondary"
                onPress={() => {
                  setUsername(user?.username || '');
                  setEmail(user?.email || '');
                  setIsEditing(false);
                }}
                disabled={saving}
                style={styles.actionBtn}
              />
            </View>
          </View>
        ) : (
          <View>
            <Text style={styles.detail}>Username: {user?.username}</Text>
            <Text style={styles.detail}>Email: {user?.email}</Text>
          </View>
        )}
      </Card>

      <Card>
        <Text style={styles.h2}>Your Plants</Text>
        {plantsError ? <StateMessage kind="error">{plantsError}</StateMessage> : null}
        {!plantsError && plants.length === 0 ? (
          <Text style={styles.detail}>No plants in your collection yet.</Text>
        ) : (
          plants.map((plant) => (
            <View key={plant.id} style={styles.plantRow}>
              <View style={styles.plantInfo}>
                <Text style={styles.plantName}>{plant.name}</Text>
                <Text style={styles.plantMeta}>
                  Next watering:{' '}
                  {plant.next_watering_at
                    ? new Date(plant.next_watering_at).toLocaleDateString()
                    : '—'}
                </Text>
              </View>
              <Button title="Remove" variant="danger" onPress={() => handleDeletePlant(plant)} />
            </View>
          ))
        )}
      </Card>

      <Button title="Sign Out" variant="danger" onPress={handleLogout} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  container: { padding: spacing.md, paddingBottom: spacing.xl },
  avatarRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.md },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { color: colors.white, fontSize: 26, fontWeight: '800' },
  headerText: { flex: 1 },
  title: { fontSize: 24, fontWeight: '800', color: colors.primaryDark },
  email: { fontSize: 14, color: colors.muted },
  joined: { fontSize: 12, color: colors.muted, marginTop: 2 },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  h2: { fontSize: 17, fontWeight: '700', color: colors.primaryDark },
  detail: { fontSize: 14, color: colors.text, marginBottom: spacing.xs },
  actionRow: { flexDirection: 'row', gap: spacing.sm },
  actionBtn: { flex: 1 },
  plantRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.sm,
  },
  plantInfo: { flex: 1 },
  plantName: { fontSize: 15, fontWeight: '700', color: colors.primaryDark },
  plantMeta: { fontSize: 12, color: colors.muted },
});
