import React, { useState } from 'react';
import {
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import { Field, StateMessage } from '../components/UI';
import { colors, spacing } from '../theme';

export default function LoginScreen() {
  const { login, signup } = useAuth();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      if (isSignUp) {
        if (!username.trim()) throw new Error('Username is required');
        await signup(email.trim(), password, username.trim());
      } else {
        await login(email.trim(), password);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsSignUp(!isSignUp);
    setError('');
    setEmail('');
    setPassword('');
    setUsername('');
  };

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>PlantCare</Text>
        <Text style={styles.subtitle}>
          {isSignUp
            ? 'Create your account — plants sync securely to the server'
            : 'Welcome back'}
        </Text>

        {isSignUp && (
          <Field
            label="Username"
            value={username}
            onChangeText={setUsername}
            placeholder="Enter your username"
            autoCapitalize="none"
            maxLength={50}
            editable={!loading}
          />
        )}

        <Field
          label="Email"
          value={email}
          onChangeText={setEmail}
          placeholder="Enter your email"
          autoCapitalize="none"
          keyboardType="email-address"
          autoComplete="email"
          editable={!loading}
        />

        <Field
          label="Password"
          value={password}
          onChangeText={setPassword}
          placeholder={isSignUp ? 'At least 8 characters' : 'Enter your password'}
          secureTextEntry
          autoComplete={isSignUp ? 'new-password' : 'current-password'}
          editable={!loading}
        />

        {error ? <StateMessage kind="error">{error}</StateMessage> : null}

        <Button
          title={isSignUp ? 'Sign Up' : 'Sign In'}
          onPress={handleSubmit}
          loading={loading}
          style={styles.submit}
        />

        <Button
          title={isSignUp ? 'Have an account? Sign In' : "No account? Sign Up"}
          variant="secondary"
          onPress={switchMode}
          disabled={loading}
          style={styles.toggle}
        />

        <Text style={styles.note}>
          Accounts are stored server-side with bcrypt password hashing. You can
          also generate care guides without signing in.
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: {
    padding: spacing.lg,
    paddingTop: spacing.xl,
  },
  title: {
    fontSize: 30,
    fontWeight: '800',
    color: colors.primaryDark,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: 15,
    color: colors.muted,
    marginBottom: spacing.lg,
  },
  submit: { marginTop: spacing.sm },
  toggle: { marginTop: spacing.sm },
  note: {
    marginTop: spacing.lg,
    fontSize: 12,
    color: colors.muted,
    textAlign: 'center',
  },
});
