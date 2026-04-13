/**
 * INTENTA — App Navigator
 * Stack-based navigation with typed route params.
 * Auth gating uses local JWT service — no Firebase.
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LandingScreen from '../screens/LandingScreen';
import InputScreen from '../screens/InputScreen';
import OutputScreen from '../screens/OutputScreen';
import LoginScreen from '../screens/LoginScreen';
import { GenerateResponse } from '../services/api';
import { initAuth, onAuthStateChanged, LocalUser } from '../services/localAuth';

export type RootStackParamList = {
  Landing: undefined;
  Input: undefined;
  Output: { result: GenerateResponse; processingMs: number };
  Login: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  const [user, setUser] = React.useState<LocalUser | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Rehydrate any existing session from sessionStorage on web
    initAuth();

    const unsubscribe = onAuthStateChanged((u) => {
      setUser(u);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  if (loading) return null;

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName={user ? 'Landing' : 'Login'}
        screenOptions={{
          headerShown: false,
          animation: 'fade_from_bottom',
          contentStyle: { backgroundColor: '#0A0A1A' },
        }}
      >
        {user ? (
          <>
            <Stack.Screen name="Landing" component={LandingScreen} />
            <Stack.Screen name="Input" component={InputScreen} />
            <Stack.Screen name="Output" component={OutputScreen} />
          </>
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
