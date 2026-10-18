import React, { useState, useCallback } from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import * as api from '../api/client';
import Button from '../components/Button';
import { Card, Field, StateMessage } from '../components/UI';
import { colors, spacing } from '../theme';

function formatDateTime(value) {
  return value
    ? new Date(value).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : '—';
}

export default function PlantDetailScreen({ route, navigation }) {
  const { id } = route.params;
  const [plant, setPlant] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [plantData, historyData] = await Promise.all([
        api.getPlant(id),
        api.wateringHistory(id),
      ]);
      setPlant(plantData);
      setHistory(historyData);
    } catch (err) {
      setError(err.message);
    }
  }, [id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const flash = (message) => {
    setNotice(message);
    setTimeout(() => setNotice(null), 3000);
  };

  const handleWater = async () => {
    setSaving(true);
    setError(null);
    try {
      await api.recordWatering(id, notes.trim() || undefined);
      setNotes('');
      flash('Watering recorded');
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handlePostpone = async () => {
    try {
      await api.postponeWatering(id, 1);
      flash('Watering postponed by 1 day');
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleToggleReminder = async () => {
    try {
      await api.updateReminder(id, { reminder_enabled: !plant.reminder_enabled });
      flash(`Reminder ${plant.reminder_enabled ? 'disabled' : 'enabled'}`);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = () => {
    Alert.alert('Remove plant', `Remove ${plant.name} from your collection?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: async () => {
          try {
            await api.deletePlant(id);
            navigation.goBack();
          } catch (err) {
            setError(err.message);
          }
        },
      },
    ]);
  };

  if (error && !plant) {
    return (
      <View style={styles.screen}>
        <View style={styles.container}>
          <StateMessage kind="error">{error}</StateMessage>
          <Button title="Back" variant="secondary" onPress={() => navigation.goBack()} />
        </View>
      </View>
    );
  }

  if (!plant) {
    return (
      <View style={styles.screen}>
        <View style={styles.container}>
          <StateMessage>Loading plant…</StateMessage>
        </View>
      </View>
    );
  }

  const overdue =
    plant.reminder_enabled &&
    plant.next_watering_at &&
    new Date(plant.next_watering_at) <= new Date();

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.container}>
      <View style={styles.headerRow}>
        <View style={styles.headerText}>
          <Text style={styles.title}>{plant.name}</Text>
          {overdue ? (
            <View style={styles.overdueBadge}>
              <Text style={styles.overdueText}>Needs water</Text>
            </View>
          ) : null}
          {plant.species ? <Text style={styles.species}>{plant.species}</Text> : null}
        </View>
      </View>

      {notice ? <StateMessage kind="success">{notice}</StateMessage> : null}
      {error ? <StateMessage kind="error">{error}</StateMessage> : null}

      <Card>
        <Text style={styles.h2}>Details</Text>
        <DetailRow label="Location" value={plant.location} />
        <DetailRow label="Climate" value={plant.climate} />
        <DetailRow label="Soil" value={plant.soil_type} />
        <DetailRow label="Sunlight" value={plant.sunlight} />
        <DetailRow label="Watering interval" value={`Every ${plant.watering_interval_days} days`} />
        <DetailRow label="Last watered" value={formatDateTime(plant.last_watered_at)} />
        <DetailRow label="Next watering" value={formatDateTime(plant.next_watering_at)} />
        {plant.care_notes ? (
          <View style={styles.notesBlock}>
            <Text style={styles.h3}>Care notes</Text>
            <Text style={styles.p}>{plant.care_notes}</Text>
          </View>
        ) : null}
      </Card>

      <Card>
        <Text style={styles.h2}>Record a watering</Text>
        <Field
          label="Notes (optional)"
          value={notes}
          onChangeText={setNotes}
          placeholder="e.g. Deep watering"
          multiline
          maxLength={500}
          editable={!saving}
        />
        <View style={styles.actionRow}>
          <Button
            title={saving ? 'Saving…' : 'I watered this'}
            onPress={handleWater}
            loading={saving}
            style={styles.actionBtn}
          />
          <Button title="Postpone 1 day" variant="secondary" onPress={handlePostpone} style={styles.actionBtn} />
        </View>
      </Card>

      <Card>
        <Text style={styles.h2}>Watering history</Text>
        {history.length === 0 ? (
          <Text style={styles.p}>No waterings recorded yet.</Text>
        ) : (
          history.map((event) => (
            <View key={event.id} style={styles.historyRow}>
              <Text style={styles.historyDate}>{formatDateTime(event.watered_at)}</Text>
              {event.notes ? <Text style={styles.historyNotes}>{event.notes}</Text> : null}
            </View>
          ))
        )}
      </Card>

      <View style={styles.footerActions}>
        <Button
          title={plant.reminder_enabled ? 'Mute reminder' : 'Enable reminder'}
          variant="secondary"
          onPress={handleToggleReminder}
          style={styles.actionBtn}
        />
        <Button title="Remove plant" variant="danger" onPress={handleDelete} style={styles.actionBtn} />
      </View>
    </ScrollView>
  );
}

function DetailRow({ label, value }) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value || '—'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  container: { padding: spacing.md, paddingBottom: spacing.xl },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  headerText: { flex: 1 },
  title: { fontSize: 26, fontWeight: '800', color: colors.primaryDark },
  species: { fontSize: 14, fontStyle: 'italic', color: colors.muted, marginTop: 2 },
  overdueBadge: {
    alignSelf: 'flex-start',
    backgroundColor: colors.dangerBorder,
    borderRadius: 999,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginTop: 4,
  },
  overdueText: { fontSize: 11, fontWeight: '700', color: '#5c1014' },
  h2: { fontSize: 17, fontWeight: '700', color: colors.primaryDark, marginBottom: spacing.sm },
  h3: { fontSize: 14, fontWeight: '700', color: colors.accent, marginBottom: 2 },
  p: { fontSize: 14, color: colors.text, lineHeight: 20 },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    borderBottomStyle: 'dashed',
    paddingVertical: 6,
    gap: spacing.sm,
  },
  detailLabel: { fontSize: 13, color: colors.muted },
  detailValue: { fontSize: 13, color: colors.primaryDark, fontWeight: '700', flexShrink: 1, textAlign: 'right' },
  notesBlock: { marginTop: spacing.sm },
  actionRow: { flexDirection: 'row', gap: spacing.sm },
  actionBtn: { flex: 1 },
  historyRow: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    borderBottomStyle: 'dashed',
    paddingVertical: 6,
  },
  historyDate: { fontSize: 13, color: colors.primaryDark, fontWeight: '600' },
  historyNotes: { fontSize: 13, color: colors.muted, fontStyle: 'italic' },
  footerActions: { flexDirection: 'row', gap: spacing.sm },
});
