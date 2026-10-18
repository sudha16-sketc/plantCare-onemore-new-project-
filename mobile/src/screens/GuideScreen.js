import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { useAuth } from '../context/AuthContext';
import * as api from '../api/client';
import Button from '../components/Button';
import { Field, Card, StateMessage } from '../components/UI';
import { colors, spacing } from '../theme';

const PLANT_TYPES = ['Vegetable', 'Flower', 'Indoor', 'Medicinal'];
const CLIMATES = ['Tropical', 'Temperate', 'Arid', 'Humid'];
const SOILS = ['Loamy', 'Sandy', 'Clay', 'Peaty', 'Chalky', 'Silty'];
const FREQUENCIES = ['Daily', 'Every 2-3 days', 'Weekly', 'Bi-weekly', 'Monthly'];
const EXPERIENCE = ['Beginner', 'Intermediate', 'Expert'];

const WATERING_INTERVAL_DAYS = {
  Daily: 1,
  'Every 2-3 days': 3,
  Weekly: 7,
  'Bi-weekly': 14,
  Monthly: 30,
};

const WATERING_HINTS = {
  Daily: 'every day',
  'Every 2-3 days': 'every 2–3 days',
  Weekly: 'once a week',
  'Bi-weekly': 'every two weeks',
  Monthly: 'once a month',
};

function OptionRow({ label, options, value, onChange }) {
  return (
    <View style={styles.optionGroup}>
      <Text style={styles.optionLabel}>{label}</Text>
      <View style={styles.optionRow}>
        {options.map((option) => {
          const selected = option === value;
          return (
            <Text
              key={option}
              onPress={() => onChange(option)}
              style={[styles.optionChip, selected && styles.optionChipSelected]}
            >
              {option}
            </Text>
          );
        })}
      </View>
    </View>
  );
}

export default function GuideScreen() {
  const { user } = useAuth();

  const [form, setForm] = useState({
    plant_name: '',
    plant_type: 'Vegetable',
    climate: 'Temperate',
    sunlight_hours: '6',
    soil_type: 'Loamy',
    watering_frequency: 'Weekly',
    experience_level: 'Beginner',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [guide, setGuide] = useState(null);
  const [saved, setSaved] = useState(false);

  const setField = (key, value) => setForm({ ...form, [key]: value });

  const handleGenerate = async () => {
    if (!form.plant_name.trim()) {
      setError('Please enter a plant name.');
      return;
    }
    setLoading(true);
    setError(null);
    setGuide(null);
    setSaved(false);
    try {
      const response = await api.generatePlantGuide({
        ...form,
        sunlight_hours: parseInt(form.sunlight_hours, 10) || 6,
      });

      let justSaved = false;
      if (user) {
        try {
          await api.createPlant({
            name: form.plant_name.trim(),
            species: form.plant_type || null,
            climate: form.climate || null,
            soil_type: form.soil_type || null,
            sunlight: `${form.sunlight_hours} hours`,
            watering_interval_days: WATERING_INTERVAL_DAYS[form.watering_frequency] || 7,
            care_notes: `Experience level: ${form.experience_level}`,
          });
          justSaved = true;
        } catch {
          // Non-fatal: the guide itself succeeded
        }
      }
      setSaved(justSaved);
      setGuide(response);
    } catch (err) {
      setError(err.message || 'Something went wrong. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setGuide(null);
    setError(null);
  };

  const g = guide?.plant_care_guidance;
  const isMock = guide?.plant_care_guidance?.ai_source === 'mock' || guide?.metadata?.ai_source === 'mock';

  if (guide && g) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.container}>
        <Button title="Create New Guide" variant="secondary" onPress={handleReset} />

        {isMock ? (
          <StateMessage>
            Demo mode: this guide was produced by the mock AI service, not the live model.
          </StateMessage>
        ) : null}
        {saved ? (
          <StateMessage kind="success">
            Saved to your collection with a watering reminder.
          </StateMessage>
        ) : null}

        <Card>
          <Text style={styles.h1}>{form.plant_name}</Text>
          <Text style={styles.p}>{g.plant_overview?.description}</Text>
          <Text style={styles.metaLine}>
            Difficulty: {g.plant_overview?.difficulty_level}
          </Text>
          {(g.plant_overview?.benefits || []).length > 0 && (
            <>
              <Text style={styles.h2}>Benefits</Text>
              {g.plant_overview.benefits.map((b) => (
                <Text key={b} style={styles.li}>• {b}</Text>
              ))}
            </>
          )}
        </Card>

        <Card>
          <Text style={styles.h2}>Growth stages</Text>
          {(g.growth_stages || []).map((stage) => (
            <View key={stage.stage_name} style={styles.block}>
              <Text style={styles.h3}>
                {stage.stage_name} · {stage.duration}
              </Text>
              <Text style={styles.p}>{stage.care_instructions}</Text>
              {(stage.key_indicators || []).map((k) => (
                <Text key={k} style={styles.li}>– {k}</Text>
              ))}
            </View>
          ))}
        </Card>

        <Card>
          <Text style={styles.h2}>Daily care</Text>
          <Text style={styles.h3}>Morning</Text>
          {(g.daily_care?.morning_routine || []).map((item) => (
            <Text key={item} style={styles.li}>• {item}</Text>
          ))}
          <Text style={styles.h3}>Afternoon</Text>
          {(g.daily_care?.afternoon_routine || []).map((item) => (
            <Text key={item} style={styles.li}>• {item}</Text>
          ))}
          <Text style={styles.h3}>Evening</Text>
          {(g.daily_care?.evening_routine || []).map((item) => (
            <Text key={item} style={styles.li}>• {item}</Text>
          ))}
          <Text style={styles.h3}>Weekly tasks</Text>
          {(g.daily_care?.weekly_tasks || []).map((item) => (
            <Text key={item} style={styles.li}>• {item}</Text>
          ))}
        </Card>

        <Card>
          <Text style={styles.h2}>Common problems</Text>
          {(g.common_problems || []).map((problem) => (
            <View key={problem.problem} style={styles.block}>
              <Text style={styles.h3}>{problem.problem}</Text>
              <Text style={styles.p}>
                Symptoms:{' '}
                {Array.isArray(problem.symptoms)
                  ? problem.symptoms.join(', ')
                  : problem.symptoms}
              </Text>
              <Text style={styles.p}>Solution: {problem.solution}</Text>
              <Text style={styles.p}>Prevention: {problem.prevention}</Text>
            </View>
          ))}
        </Card>

        {(g.additional_tips || []).length > 0 && (
          <Card>
            <Text style={styles.h2}>Extra tips</Text>
            {g.additional_tips.map((tip) => (
              <Text key={tip} style={styles.li}>• {tip}</Text>
            ))}
          </Card>
        )}

        {guide.visual_guide?.file_url ? (
          <Card>
            <Text style={styles.h2}>Visual guide</Text>
            <Button
              title="Open care guide presentation"
              variant="secondary"
              onPress={() => WebBrowser.openBrowserAsync(guide.visual_guide.file_url)}
            />
          </Card>
        ) : null}
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      <Text style={styles.title}>Care guide</Text>
      <Text style={styles.subtitle}>
        Answer a few questions and get a full AI care guide with growth stages,
        daily routines, and a downloadable presentation.
      </Text>

      <Field
        label="Plant name *"
        value={form.plant_name}
        onChangeText={(v) => setField('plant_name', v)}
        placeholder="e.g. Tomato"
        editable={!loading}
      />

      <OptionRow
        label="Type"
        options={PLANT_TYPES}
        value={form.plant_type}
        onChange={(v) => setField('plant_type', v)}
      />
      <OptionRow
        label="Climate"
        options={CLIMATES}
        value={form.climate}
        onChange={(v) => setField('climate', v)}
      />
      <OptionRow
        label="Soil"
        options={SOILS}
        value={form.soil_type}
        onChange={(v) => setField('soil_type', v)}
      />
      <OptionRow
        label={`Watering: ${WATERING_HINTS[form.watering_frequency]}`}
        options={FREQUENCIES}
        value={form.watering_frequency}
        onChange={(v) => setField('watering_frequency', v)}
      />
      <OptionRow
        label="Experience"
        options={EXPERIENCE}
        value={form.experience_level}
        onChange={(v) => setField('experience_level', v)}
      />

      <Field
        label="Sunlight hours per day"
        value={form.sunlight_hours}
        onChangeText={(v) => setField('sunlight_hours', v)}
        keyboardType="numeric"
        editable={!loading}
      />

      {error ? <StateMessage kind="error">{error}</StateMessage> : null}

      <Button
        title={loading ? 'Generating…' : 'Generate care guide'}
        onPress={handleGenerate}
        loading={loading}
      />
      {loading ? (
        <Text style={styles.loadingHint}>
          The AI model can take up to a minute to respond…
        </Text>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  container: { padding: spacing.md, paddingBottom: spacing.xl },
  title: { fontSize: 26, fontWeight: '800', color: colors.primaryDark },
  subtitle: { fontSize: 14, color: colors.muted, marginTop: spacing.xs, marginBottom: spacing.md },
  optionGroup: { marginBottom: spacing.md },
  optionLabel: { fontSize: 13, fontWeight: '700', color: colors.primaryDark, marginBottom: spacing.xs },
  optionRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  optionChip: {
    fontSize: 13,
    color: colors.primaryDark,
    backgroundColor: colors.successBg,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
    overflow: 'hidden',
  },
  optionChipSelected: {
    backgroundColor: colors.primary,
    color: colors.white,
    borderColor: colors.primary,
  },
  h1: { fontSize: 22, fontWeight: '800', color: colors.primaryDark, marginBottom: spacing.sm },
  h2: { fontSize: 17, fontWeight: '700', color: colors.primaryDark, marginTop: spacing.sm, marginBottom: spacing.xs },
  h3: { fontSize: 15, fontWeight: '700', color: colors.accent, marginTop: spacing.sm, marginBottom: 2 },
  p: { fontSize: 14, color: colors.text, marginBottom: spacing.xs, lineHeight: 20 },
  li: { fontSize: 14, color: colors.textMuted, marginBottom: 2, lineHeight: 20 },
  metaLine: { fontSize: 13, color: colors.muted, fontStyle: 'italic' },
  block: { marginTop: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.sm },
  loadingHint: { fontSize: 12, color: colors.muted, textAlign: 'center', marginTop: spacing.sm },
});
