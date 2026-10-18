import Constants from 'expo-constants';
import { Platform } from 'react-native';

/**
 * Resolve the backend base URL:
 *  1. EXPO_PUBLIC_API_URL env var (set by EAS build profiles)
 *  2. app.json -> expo.extra.apiBaseUrl
 *  3. Defaults: Android emulator uses 10.0.2.2 (host loopback),
 *     everything else uses localhost.
 */
function resolveBaseUrl() {
  const fromEnv = process.env.EXPO_PUBLIC_API_URL;
  if (fromEnv) return fromEnv.replace(/\/$/, '');

  const fromConfig = Constants.expoConfig?.extra?.apiBaseUrl;
  if (fromConfig) return fromConfig.replace(/\/$/, '');

  if (Platform.OS === 'android') return 'http://10.0.2.2:8000';
  return 'http://localhost:8000';
}

export const API_BASE_URL = resolveBaseUrl();
