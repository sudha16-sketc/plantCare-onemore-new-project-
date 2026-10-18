import React from 'react';
import { Text } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { AuthProvider } from './src/context/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import GuideScreen from './src/screens/GuideScreen';
import IdentifyScreen from './src/screens/IdentifyScreen';
import PlantsScreen from './src/screens/PlantsScreen';
import PlantDetailScreen from './src/screens/PlantDetailScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import { colors } from './src/theme';

const Stack = createNativeStackNavigator();
const Tabs = createBottomTabNavigator();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    background: colors.background,
    card: colors.white,
    border: colors.border,
    text: colors.text,
  },
};

function TabIcon({ symbol, focused }) {
  return (
    <Text style={{ fontSize: 18, opacity: focused ? 1 : 0.55 }}>{symbol}</Text>
  );
}

function TabsNavigator() {
  return (
    <Tabs.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.white },
        headerTintColor: colors.primaryDark,
        headerTitleStyle: { fontWeight: '800' },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: { backgroundColor: colors.white },
      }}
    >
      <Tabs.Screen
        name="Guide"
        component={GuideScreen}
        options={{
          title: 'Care Guide',
          tabBarIcon: ({ focused }) => <TabIcon symbol="✨" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="Identify"
        component={IdentifyScreen}
        options={{
          tabBarIcon: ({ focused }) => <TabIcon symbol="📷" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="Plants"
        component={PlantsScreen}
        options={{
          title: 'My Plants',
          tabBarIcon: ({ focused }) => <TabIcon symbol="🪴" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ focused }) => <TabIcon symbol="👤" focused={focused} />,
        }}
      />
    </Tabs.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <NavigationContainer theme={theme}>
          <Stack.Navigator>
            <Stack.Screen
              name="Tabs"
              component={TabsNavigator}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="PlantDetail"
              component={PlantDetailScreen}
              options={({ route }) => ({
                title: route.params?.name || 'Plant',
              })}
            />
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ title: 'Sign In' }}
            />
          </Stack.Navigator>
          <StatusBar style="dark" />
        </NavigationContainer>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
