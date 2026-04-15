/**
 * INTENTA — Input Screen
 * Business intent text input with animated submit button and loading state.
 */
import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Animated,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { generateDesign } from '../services/api';
import { getCurrentUser } from '../services/localAuth';
import LoadingAnimation from '../components/LoadingAnimation';
import { theme } from '../theme/theme';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Input'>;
};

const EXAMPLE_PROMPTS = [
  'Build a GDPR-compliant fintech payment platform for 1M enterprise users with Jira integration',
  'Create a healthcare patient management system with HIPAA compliance for 500 hospitals',
  'Design a real-time e-commerce platform for 5M global shoppers with Salesforce and SAP integration',
  'Build an internal HR platform for 10,000 employees with SOC2 compliance',
];

export default function InputScreen({ navigation }: Props) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [focused, setFocused] = useState(false);

  const buttonScale = useRef(new Animated.Value(1)).current;

  const handleTextChange = (text: string) => {
    setInput(text);
    setCharCount(text.length);
  };

  const handleExamplePress = (example: string) => {
    setInput(example);
    setCharCount(example.length);
  };

  const handlePressIn = () => {
    Animated.spring(buttonScale, { toValue: 0.96, useNativeDriver: true, tension: 100 }).start();
  };

  const handlePressOut = () => {
    Animated.spring(buttonScale, { toValue: 1, useNativeDriver: true, tension: 100 }).start();
  };

  const handleGenerate = useCallback(async () => {
    const trimmed = input.trim();
    if (trimmed.length < 10) {
      Alert.alert('Too short', 'Please describe your intent in at least 10 characters.');
      return;
    }

    setLoading(true);
    const start = Date.now();

    try {
      const userEmail = getCurrentUser()?.email || 'user@intenta.local';
      const result = await generateDesign(trimmed, userEmail);
      const elapsed = Date.now() - start;
      navigation.navigate('Output', { result, processingMs: elapsed });
    } catch (err: any) {
      Alert.alert(
        'Generation Failed',
        err.message || 'Could not connect to INTENTA backend. Ensure Docker is running.',
        [{ text: 'OK' }]
      );
    } finally {
      setLoading(false);
    }
  }, [input, navigation]);

  if (loading) {
    return (
      <LinearGradient colors={['#0A0A1A', '#140833', '#0A0A1A']} style={styles.loadingContainer}>
        <StatusBar barStyle="light-content" />
        <LoadingAnimation label="Analyzing your intent..." />
      </LinearGradient>
    );
  }

  const canSubmit = input.trim().length >= 10;

  return (
    <LinearGradient colors={['#0A0A1A', '#11112B', '#0A0A1A']} style={styles.container}>
      <StatusBar barStyle="light-content" />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Back button */}
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>

          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.stepLabel}>STEP 1 OF 1</Text>
            <Text style={styles.title}>Describe Your{'\n'}Business Intent</Text>
            <Text style={styles.subtitle}>
              Tell INTENTA what you want to build. The more detail, the better the output.
            </Text>
          </View>

          {/* Text Input */}
          <View style={[styles.inputWrapper, focused && styles.inputWrapperFocused]}>
            <TextInput
              style={styles.textInput}
              placeholder="e.g. Build a GDPR-compliant payment platform for 1M enterprise users with Jira and GitHub integration..."
              placeholderTextColor={theme.colors.text.muted}
              multiline
              numberOfLines={6}
              value={input}
              onChangeText={handleTextChange}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              maxLength={2000}
              textAlignVertical="top"
              autoCorrect={false}
              autoCapitalize="none"
            />
            <Text style={[styles.charCount, charCount > 1500 && styles.charCountWarning]}>
              {charCount}/2000
            </Text>
          </View>

          {/* Generate Button */}
          <Animated.View style={{ transform: [{ scale: buttonScale }] }}>
            <TouchableOpacity
              onPress={handleGenerate}
              onPressIn={handlePressIn}
              onPressOut={handlePressOut}
              disabled={!canSubmit}
              activeOpacity={0.9}
            >
              <LinearGradient
                colors={canSubmit ? ['#7C3AED', '#4F46E5', '#3B82F6'] : ['#2D2D4A', '#2D2D4A']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={[styles.button, !canSubmit && styles.buttonDisabled]}
              >
                <Text style={[styles.buttonText, !canSubmit && styles.buttonTextDisabled]}>
                  {canSubmit ? '✦  Generate Enterprise Design' : 'Enter your intent above'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>

          {/* What we generate */}
          <View style={styles.outputHint}>
            <Text style={styles.outputHintTitle}>What INTENTA generates:</Text>
            <View style={styles.outputChips}>
              {['🏗 Architecture', '⚙️ Tech Stack', '📁 Code Blueprint', '🔒 Compliance', '🛡 Governance', '💡 Explainability'].map((o) => (
                <View key={o} style={styles.outputChip}>
                  <Text style={styles.outputChipText}>{o}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Example prompts */}
          <View style={styles.examplesSection}>
            <Text style={styles.examplesTitle}>Try an example:</Text>
            {EXAMPLE_PROMPTS.map((ex, i) => (
              <TouchableOpacity
                key={i}
                style={styles.exampleCard}
                onPress={() => handleExamplePress(ex)}
                activeOpacity={0.7}
              >
                <Text style={styles.exampleNumber}>{`0${i + 1}`}</Text>
                <Text style={styles.exampleText} numberOfLines={2}>{ex}</Text>
                <Text style={styles.exampleArrow}>→</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  scrollContent: { padding: theme.spacing.lg, paddingBottom: 60 },
  backButton: { marginBottom: theme.spacing.md },
  backText: { color: theme.colors.brand.primary, fontSize: 15, fontWeight: '600' },
  header: { marginBottom: theme.spacing.lg },
  stepLabel: {
    color: theme.colors.brand.accent,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 2,
    marginBottom: theme.spacing.sm,
  },
  title: {
    fontSize: 30,
    fontWeight: '800',
    color: theme.colors.text.primary,
    lineHeight: 36,
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    color: theme.colors.text.secondary,
    fontSize: 14,
    lineHeight: 21,
  },
  inputWrapper: {
    backgroundColor: theme.colors.bg.card,
    borderRadius: theme.radii.lg,
    borderWidth: 1.5,
    borderColor: theme.colors.border.default,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  inputWrapperFocused: {
    borderColor: theme.colors.brand.primary,
    ...theme.shadows.glow,
  },
  textInput: {
    color: theme.colors.text.primary,
    fontSize: 15,
    lineHeight: 24,
    minHeight: 140,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  charCount: {
    color: theme.colors.text.muted,
    fontSize: 11,
    textAlign: 'right',
    marginTop: theme.spacing.xs,
  },
  charCountWarning: { color: theme.colors.warning },
  button: {
    borderRadius: theme.radii.xl,
    paddingVertical: 18,
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
    ...theme.shadows.button,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  buttonTextDisabled: { color: theme.colors.text.muted },
  outputHint: {
    marginBottom: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: 'rgba(124,58,237,0.08)',
    borderRadius: theme.radii.lg,
    borderWidth: 1,
    borderColor: 'rgba(124,58,237,0.2)',
  },
  outputHintTitle: {
    color: theme.colors.text.secondary,
    fontSize: 13,
    fontWeight: '600',
    marginBottom: theme.spacing.sm,
  },
  outputChips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  outputChip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    backgroundColor: 'rgba(79,70,229,0.2)',
    borderRadius: theme.radii.full,
  },
  outputChipText: { color: '#A5B4FC', fontSize: 12, fontWeight: '500' },
  examplesSection: { marginTop: theme.spacing.sm },
  examplesTitle: {
    color: theme.colors.text.muted,
    fontSize: 13,
    fontWeight: '600',
    marginBottom: theme.spacing.sm,
    letterSpacing: 0.5,
  },
  exampleCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.bg.card,
    borderRadius: theme.radii.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    gap: theme.spacing.sm,
  },
  exampleNumber: {
    color: theme.colors.brand.primary,
    fontSize: 14,
    fontWeight: '800',
    width: 28,
  },
  exampleText: {
    flex: 1,
    color: theme.colors.text.secondary,
    fontSize: 13,
    lineHeight: 19,
  },
  exampleArrow: { color: theme.colors.text.muted, fontSize: 16 },
});
