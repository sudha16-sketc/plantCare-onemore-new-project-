import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { colors, radius, spacing } from '../theme';

export function Field({ label, ...inputProps }) {
  return (
    <View style={styles.field}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <TextInput
        style={styles.input}
        placeholderTextColor={colors.muted}
        {...inputProps}
      />
    </View>
  );
}

export function Card({ children, style }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function StateMessage({ kind = 'info', children }) {
  return (
    <View
      style={[
        styles.state,
        kind === 'error' && styles.stateError,
        kind === 'success' && styles.stateSuccess,
      ]}
    >
      <Text
        style={[
          styles.stateText,
          kind === 'error' && styles.stateErrorText,
        ]}
      >
        {children}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  field: {
    marginBottom: spacing.md,
  },
  label: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.primaryDark,
    marginBottom: spacing.xs,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: radius.sm,
    backgroundColor: colors.white,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
    color: colors.text,
    minHeight: 44,
  },
  card: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  state: {
    backgroundColor: '#f1f8f4',
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  stateError: {
    backgroundColor: colors.dangerBg,
  },
  stateSuccess: {
    backgroundColor: colors.successBg,
  },
  stateText: {
    color: colors.accent,
    textAlign: 'center',
    fontSize: 14,
  },
  stateErrorText: {
    color: colors.danger,
  },
});
