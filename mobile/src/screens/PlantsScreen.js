import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';
import * as api from '../api/client';
import Button from '../components/Button';
import { Card, Field, StateMessage } from '../components/UI';
import { colors, spacing } from '../theme';

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString() : '—';
}

function isOverdue(plant) {
  return (
    plant.reminder_enabled &&
    plant.next_watering_at &&
    new Date(plant.next_watering_at) <= new Date()
  );
}

function SignInPrompt() {
  return (
    <View style={styles.signedOut}>
      <StateMessage>
        Sign in to keep a plant collection on the server, get watering
        reminders, and track history across devices.
      </StateMessage>
    </View>
  );
}

export default function PlantsScreen({ navigation }) {
  const { isAuthenticated } = useAuth();
  const [plants, setPlants] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newPlant, setNewPlant] = useState({
    name: '',
    species: '',
    watering_interval_days: '7',
  });

  const load = useCallback(async () => {
    if (!isAuthenticated) return;
    setError(null);
    try {
      setPlants(await api.listPlants());
    } catch (err) {
      setError(err.message);
    }
  }, [isAuthenticated]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const flash = (message) => {
    setNotice(message);
    setTimeout(() => setNotice(null), 3000);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const handleWater = async (plant) => {
    try {
      await api.recordWatering(plant.id);
      flash(`Watered ${plant.name}`);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handlePostpone = async (plant) => {
    try {
      await api.postponeWatering(plant.id, 1);
      flash(`Postponed ${plant.name}'s watering by 1 day`);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = (plant) => {
    Alert.alert('Remove plant', `Remove ${plant.name} from your collection?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: async () => {
          try {
            await api.deletePlant(plant.id);
            flash(`Removed ${plant.name}`);
            load();
          } catch (err) {
            setError(err.message);
          }
        },
      },
    ]);
  };

  const handleAdd = async () => {
    if (!newPlant.name.trim()) {
      setError('Please enter a plant name.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await api.createPlant({
        name: newPlant.name.trim(),
        species: newPlant.species.trim() || null,
        watering_interval_days: parseInt(newPlant.watering_interval_days, 10) || 7,
      });
      flash(`Added ${newPlant.name.trim()}`);
      setNewPlant({ name: '', species: '', watering_interval_days: '7' });
      setShowAdd(false);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated) {
    return <SignInPrompt />;
  }

  const renderItem = ({ item }) => {
    const overdue = isOverdue(item);
    return (
      <Card style={overdue ? styles.cardOverdue : undefined}>
        <View style={styles.cardHeader}>
          <Text
            style={styles.plantName}
            onPress={() => navigation.navigate('PlantDetail', { id: item.id, name: item.name })}
          >
            {item.name}
          </Text>
          {overdue && (
            <View style={styles.overdueBadge}>
              <Text style={styles.overdueText}>Needs water</Text>
            </View>
          )}
        </View>
        {item.species ? <Text style={styles.species}>{item.species}</Text> : null}

        <View style={styles.metaRow}>
          <View style={styles.metaCell}>
            <Text style={styles.metaLabel}>Last watered</Text>
            <Text style={styles.metaValue}>{formatDate(item.last_watered_at)}</Text>
          </View>
          <View style={styles.metaCell}>
            <Text style={styles.metaLabel}>Next</Text>
            <Text style={styles.metaValue}>{formatDate(item.next_watering_at)}</Text>
          </View>
          <View style={styles.metaCell}>
            <Text style={styles.metaLabel}>Every</Text>
            <Text style={styles.metaValue}>{item.watering_interval_days}d</Text>
          </View>
        </View>

        <View style={styles.cardActions}>
          <Button title="Watered" onPress={() => handleWater(item)} style={styles.cardBtn} />
          {overdue && (
            <Button
              title="Postpone"
              variant="secondary"
              onPress={() => handlePostpone(item)}
              style={styles.cardBtn}
            />
          )}
          <Button
            title="Remove"
            variant="danger"
            onPress={() => handleDelete(item)}
            style={styles.cardBtn}
          />
        </View>
      </Card>
    );
  };

  return (
    <View style={styles.screen}>
      <FlatList
        data={plants}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListHeaderComponent={
          <>
            <View style={styles.headerRow}>
              <Text style={styles.title}>My Plants</Text>
              <Button
                title={showAdd ? 'Close' : '+ Add'}
                variant="secondary"
                onPress={() => setShowAdd(!showAdd)}
              />
            </View>

            {notice ? <StateMessage kind="success">{notice}</StateMessage> : null}
            {error ? <StateMessage kind="error">{error}</StateMessage> : null}

            {showAdd && (
              <Card>
                <Field
                  label="Name *"
                  value={newPlant.name}
                  onChangeText={(v) => setNewPlant({ ...newPlant, name: v })}
                  placeholder="e.g. Kitchen Basil"
                  editable={!saving}
                />
                <Field
                  label="Species"
                  value={newPlant.species}
                  onChangeText={(v) => setNewPlant({ ...newPlant, species: v })}
                  placeholder="e.g. Ocimum basilicum"
                  editable={!saving}
                />
                <Field
                  label="Water every (days)"
                  value={newPlant.watering_interval_days}
                  onChangeText={(v) => setNewPlant({ ...newPlant, watering_interval_days: v })}
                  keyboardType="numeric"
                  editable={!saving}
                />
                <Button title="Save plant" onPress={handleAdd} loading={saving} />
              </Card>
            )}
          </>
        }
        ListEmptyComponent={
          !error ? (
            <StateMessage>
              No plants yet. Add one above, or generate a care guide from the
              Guide tab.
            </StateMessage>
          ) : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  container: { padding: spacing.md, paddingBottom: spacing.xl },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  title: { fontSize: 26, fontWeight: '800', color: colors.primaryDark },
  signedOut: { flex: 1, backgroundColor: colors.background, padding: spacing.md, justifyContent: 'center' },
  cardOverdue: { borderColor: colors.dangerBorder, backgroundColor: '#fff8f8' },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, flexWrap: 'wrap' },
  plantName: { fontSize: 18, fontWeight: '800', color: colors.primaryDark },
  species: { fontSize: 13, fontStyle: 'italic', color: colors.muted, marginBottom: spacing.xs },
  overdueBadge: { backgroundColor: colors.dangerBorder, borderRadius: 999, paddingHorizontal: 8, paddingVertical: 2 },
  overdueText: { fontSize: 11, fontWeight: '700', color: '#5c1014' },
  metaRow: { flexDirection: 'row', marginTop: spacing.sm, gap: spacing.md },
  metaCell: { flex: 1 },
  metaLabel: { fontSize: 10, textTransform: 'uppercase', color: '#74c69d', letterSpacing: 0.5 },
  metaValue: { fontSize: 13, color: colors.primaryDark, fontWeight: '600' },
  cardActions: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md, flexWrap: 'wrap' },
  cardBtn: { flexGrow: 1 },
});
