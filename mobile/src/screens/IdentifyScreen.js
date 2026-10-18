import React, { useState } from 'react';
import { View, Text, Image, ScrollView, StyleSheet, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as api from '../api/client';
import Button from '../components/Button';
import { Card, StateMessage } from '../components/UI';
import { colors, spacing, radius } from '../theme';

const SEVERITY_COLORS = {
  none: colors.accent,
  mild: '#95d5b2',
  moderate: colors.warning,
  severe: colors.danger,
  unclear: colors.muted,
};

async function pickFromCamera() {
  const permission = await ImagePicker.requestCameraPermissionsAsync();
  if (!permission.granted) {
    Alert.alert('Camera access needed', 'Allow camera access to photograph a plant.');
    return null;
  }
  const result = await ImagePicker.launchCameraAsync({
    mediaTypes: ['images'],
    quality: 0.8,
  });
  if (result.canceled) return null;
  return result.assets[0];
}

async function pickFromLibrary() {
  const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!permission.granted) {
    Alert.alert('Photo access needed', 'Allow photo library access to choose a picture.');
    return null;
  }
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images'],
    quality: 0.8,
  });
  if (result.canceled) return null;
  return result.assets[0];
}

export default function IdentifyScreen() {
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const choosePhoto = async () => {
    const picked = await pickFromLibrary();
    if (picked) {
      setPhoto(picked);
      setResult(null);
      setError(null);
    }
  };

  const takePhoto = async () => {
    const picked = await pickFromCamera();
    if (picked) {
      setPhoto(picked);
      setResult(null);
      setError(null);
    }
  };

  const reset = () => {
    setPhoto(null);
    setResult(null);
    setError(null);
  };

  const analyze = async () => {
    if (!photo) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.analyzePhoto(photo);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.analysis;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.container}>
      <Text style={styles.title}>Identify a plant</Text>
      <Text style={styles.subtitle}>
        Take a photo or pick one from your library to identify the plant and
        check visible symptoms.
      </Text>

      <Card>
        <View style={styles.actions}>
          <Button title="Take photo" onPress={takePhoto} style={styles.actionBtn} />
          <Button title="Choose photo" variant="secondary" onPress={choosePhoto} style={styles.actionBtn} />
        </View>

        {photo && (
          <View style={styles.previewWrap}>
            <Image source={{ uri: photo.uri }} style={styles.preview} resizeMode="cover" />
            <Text style={styles.previewMeta}>
              {photo.fileName || 'photo'}{' '}
              {photo.fileSize ? `· ${Math.round(photo.fileSize / 1024)} KB` : ''}
            </Text>
          </View>
        )}

        <View style={styles.actions}>
          <Button
            title={loading ? 'Analyzing…' : 'Analyze photo'}
            onPress={analyze}
            disabled={!photo}
            loading={loading}
            style={styles.actionBtn}
          />
          {(photo || result) && (
            <Button title="Reset" variant="secondary" onPress={reset} disabled={loading} style={styles.actionBtn} />
          )}
        </View>

        {loading && (
          <Text style={styles.loadingHint}>
            Asking the AI model… this can take up to a minute.
          </Text>
        )}
        {error ? <StateMessage kind="error">{error}</StateMessage> : null}
      </Card>

      {analysis && (
        <>
          <Card>
            <Text style={styles.h2}>Identification</Text>
            <Text style={styles.identified}>{analysis.identification.likely_name}</Text>
            <View
              style={[
                styles.confidence,
                { backgroundColor: SEVERITY_COLORS[analysis.identification.confidence] || colors.muted },
              ]}
            >
              <Text style={styles.confidenceText}>
                {analysis.identification.confidence} confidence
              </Text>
            </View>
            <Text style={styles.p}>{analysis.identification.confidence_reasoning}</Text>

            {(analysis.identification.possible_species || []).length > 0 && (
              <>
                <Text style={styles.h3}>Possible species</Text>
                {analysis.identification.possible_species.map((s) => (
                  <Text key={s} style={styles.li}>• {s}</Text>
                ))}
              </>
            )}
          </Card>

          {(analysis.observations || []).length > 0 && (
            <Card>
              <Text style={styles.h2}>Observations</Text>
              {analysis.observations.map((obs, i) => (
                <View key={`${obs.observation}-${i}`} style={styles.observationRow}>
                  <View
                    style={[
                      styles.severity,
                      { backgroundColor: SEVERITY_COLORS[obs.severity] || colors.muted },
                    ]}
                  >
                    <Text style={styles.severityText}>{obs.severity}</Text>
                  </View>
                  <Text style={styles.observationText}>{obs.observation}</Text>
                </View>
              ))}
            </Card>
          )}

          {(analysis.possible_causes || []).length > 0 && (
            <Card>
              <Text style={styles.h2}>Possible causes</Text>
              {analysis.possible_causes.map((c) => (
                <Text key={c} style={styles.li}>• {c}</Text>
              ))}
            </Card>
          )}

          {(analysis.care_recommendations || []).length > 0 && (
            <Card>
              <Text style={styles.h2}>Care recommendations</Text>
              {analysis.care_recommendations.map((r) => (
                <Text key={r} style={styles.li}>• {r}</Text>
              ))}
            </Card>
          )}

          <Card>
            <Text style={styles.disclaimer}>{analysis.disclaimer}</Text>
            <Text style={styles.meta}>
              {result.metadata?.model ? `Model: ${result.metadata.model} · ` : ''}
              {result.metadata?.processing_time_seconds != null
                ? `${result.metadata.processing_time_seconds.toFixed(1)}s · `
                : ''}
              {analysis.source === 'mock' ? 'demo result (mock AI)' : 'AI-generated result'}
            </Text>
          </Card>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  container: { padding: spacing.md, paddingBottom: spacing.xl },
  title: { fontSize: 26, fontWeight: '800', color: colors.primaryDark },
  subtitle: { fontSize: 14, color: colors.muted, marginTop: spacing.xs, marginBottom: spacing.md },
  actions: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.sm },
  actionBtn: { flex: 1 },
  previewWrap: { marginBottom: spacing.md },
  preview: { width: '100%', height: 240, borderRadius: radius.md, borderWidth: 1, borderColor: colors.borderStrong },
  previewMeta: { fontSize: 12, color: colors.muted, marginTop: spacing.xs },
  loadingHint: { fontSize: 13, color: colors.accent, textAlign: 'center', marginTop: spacing.sm },
  h2: { fontSize: 17, fontWeight: '700', color: colors.primaryDark, marginBottom: spacing.xs },
  h3: { fontSize: 14, fontWeight: '700', color: colors.accent, marginTop: spacing.sm, marginBottom: 2 },
  identified: { fontSize: 22, fontWeight: '800', color: colors.primaryDark, marginBottom: spacing.xs },
  confidence: { alignSelf: 'flex-start', borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4, marginBottom: spacing.sm },
  confidenceText: { color: colors.white, fontWeight: '700', fontSize: 12 },
  p: { fontSize: 14, color: colors.textMuted, lineHeight: 20 },
  li: { fontSize: 14, color: colors.text, lineHeight: 20 },
  observationRow: { flexDirection: 'row', alignItems: 'flex-start', gap: spacing.sm, marginBottom: spacing.sm },
  severity: { borderRadius: 4, paddingHorizontal: 6, paddingVertical: 2 },
  severityText: { color: colors.white, fontSize: 10, fontWeight: '700', textTransform: 'uppercase' },
  observationText: { flex: 1, fontSize: 14, color: colors.text, lineHeight: 20 },
  disclaimer: { fontSize: 13, color: colors.accent, lineHeight: 19 },
  meta: { fontSize: 12, color: colors.muted, marginTop: spacing.sm },
});
