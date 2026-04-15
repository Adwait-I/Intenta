/**
 * INTENTA — Login Screen
 * Local JWT Authentication (no Firebase, no cloud services)
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { signIn, signUp } from '../services/localAuth';
import { theme } from '../theme/theme';

export default function LoginScreen() {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setError('');
  };

  const showError = (msg: string) => {
    setError(msg);
    if (Platform.OS !== 'web') {
      Alert.alert('Error', msg);
    }
  };

  const handleSubmit = async () => {
    setError('');
    const trimmedEmail = email.trim().toLowerCase();
    const trimmedPassword = password.trim();

    if (!trimmedEmail || !trimmedPassword) {
      showError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    try {
      if (isLoginMode) {
        await signIn(trimmedEmail, trimmedPassword);
        // AppNavigator's onAuthStateChanged listener handles navigation automatically
      } else {
        if (trimmedPassword.length < 8) {
          showError('Password must be at least 8 characters and contain a letter and a number.');
          return;
        }
        await signUp(trimmedEmail, trimmedPassword);
        // Auto-login after signup
        await signIn(trimmedEmail, trimmedPassword);
      }
    } catch (err: any) {
      showError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={['#0A0A1A', '#11112B', '#0A0A1A']} style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Header / Logo */}
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Text style={styles.logoSymbol}>✦</Text>
          </View>
          <Text style={styles.title}>INTENTA</Text>
          <Text style={styles.subtitle}>
            {isLoginMode ? 'Welcome back. Sign in below.' : 'Create your INTENTA architect account.'}
          </Text>
          {/* Local auth badge */}
          <View style={styles.localBadge}>
            <View style={styles.localBadgeDot} />
            <Text style={styles.localBadgeText}>100% Local · No Cloud</Text>
          </View>
        </View>

        {/* Form */}
        <View style={styles.form}>
          {/* Error Banner */}
          {error ? (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>EMAIL ADDRESS</Text>
            <TextInput
              style={styles.input}
              placeholder="you@company.com"
              placeholderTextColor={theme.colors.text.muted}
              autoCapitalize="none"
              keyboardType="email-address"
              autoCorrect={false}
              value={email}
              onChangeText={setEmail}
            />
          </View>

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>PASSWORD</Text>
            <TextInput
              style={styles.input}
              placeholder={isLoginMode ? '••••••••' : 'Min 8 chars, letter + number'}
              placeholderTextColor={theme.colors.text.muted}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />
          </View>

          <TouchableOpacity
            style={[styles.buttonContainer, loading && styles.buttonDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            <LinearGradient
              colors={['#7C3AED', '#4F46E5', '#3B82F6']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.button}
            >
              <Text style={styles.buttonText}>
                {loading ? 'Processing...' : (isLoginMode ? 'Sign In  →' : 'Create Account  →')}
              </Text>
            </LinearGradient>
          </TouchableOpacity>

          {/* Toggle Mode */}
          <TouchableOpacity onPress={toggleMode} style={styles.switchButton}>
            <Text style={styles.switchText}>
              {isLoginMode
                ? "Don't have an account?  Sign up"
                : "Already have an account?  Sign in"}
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  keyboardView: {
    flex: 1,
    justifyContent: 'center',
    padding: theme.spacing.xl,
  },
  header: {
    alignItems: 'center',
    marginBottom: theme.spacing['2xl'],
  },
  logoContainer: {
    width: 64,
    height: 64,
    borderRadius: 20,
    backgroundColor: 'rgba(124,58,237,0.2)',
    borderWidth: 1.5,
    borderColor: 'rgba(124,58,237,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.md,
  },
  logoSymbol: { fontSize: 28, color: '#A78BFA' },
  title: {
    fontSize: 32,
    fontWeight: '900',
    color: theme.colors.text.primary,
    letterSpacing: 4,
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    color: theme.colors.text.muted,
    fontSize: 14,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  localBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: theme.radii.full,
    backgroundColor: 'rgba(16,185,129,0.1)',
    borderWidth: 1,
    borderColor: 'rgba(16,185,129,0.25)',
    marginTop: 4,
  },
  localBadgeDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#10B981',
  },
  localBadgeText: { color: '#10B981', fontSize: 11, fontWeight: '600' },
  form: { width: '100%', maxWidth: 400, alignSelf: 'center' },
  errorBanner: {
    backgroundColor: 'rgba(239,68,68,0.12)',
    borderRadius: theme.radii.md,
    borderWidth: 1,
    borderColor: 'rgba(239,68,68,0.3)',
    padding: 12,
    marginBottom: theme.spacing.md,
  },
  errorText: { color: '#FCA5A5', fontSize: 13, lineHeight: 18 },
  inputWrapper: { marginBottom: theme.spacing.lg },
  inputLabel: {
    color: theme.colors.brand.primary,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.5,
    marginBottom: 6,
  },
  input: {
    backgroundColor: theme.colors.bg.card,
    borderRadius: theme.radii.md,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    color: theme.colors.text.primary,
    padding: 16,
    fontSize: 16,
  },
  buttonContainer: {
    borderRadius: theme.radii.full,
    ...theme.shadows.button,
    marginTop: theme.spacing.md,
  },
  buttonDisabled: { opacity: 0.6 },
  button: { paddingVertical: 18, borderRadius: theme.radii.full, alignItems: 'center' },
  buttonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '700', letterSpacing: 0.5 },
  switchButton: { marginTop: theme.spacing.xl, alignItems: 'center' },
  switchText: { color: theme.colors.text.secondary, fontSize: 14, fontWeight: '500' },
});
