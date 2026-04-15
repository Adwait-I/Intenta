/**
 * INTENTA — Loading Animation Component
 * Animated pulsing orb with orbit rings — premium loading indicator.
 */
import React, { useEffect, useRef } from 'react';
import {
  View,
  StyleSheet,
  Animated,
  Easing,
  Text,
} from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  label?: string;
}

export default function LoadingAnimation({ label = 'Processing intent...' }: Props) {
  const pulse = useRef(new Animated.Value(1)).current;
  const rotate = useRef(new Animated.Value(0)).current;
  const rotate2 = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Fade in
    Animated.timing(opacity, {
      toValue: 1,
      duration: 400,
      useNativeDriver: true,
    }).start();

    // Pulsing orb
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, { toValue: 1.2, duration: 900, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.timing(pulse, { toValue: 1.0, duration: 900, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
      ])
    ).start();

    // Orbit ring 1
    Animated.loop(
      Animated.timing(rotate, { toValue: 1, duration: 2400, easing: Easing.linear, useNativeDriver: true })
    ).start();

    // Orbit ring 2 (reverse)
    Animated.loop(
      Animated.timing(rotate2, { toValue: -1, duration: 3600, easing: Easing.linear, useNativeDriver: true })
    ).start();
  }, []);

  const spin1 = rotate.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '360deg'] });
  const spin2 = rotate2.interpolate({ inputRange: [-1, 0], outputRange: ['-360deg', '0deg'] });

  return (
    <Animated.View style={[styles.container, { opacity }]}>
      {/* Outer ring */}
      <Animated.View style={[styles.ring, styles.ringOuter, { transform: [{ rotate: spin1 }] }]}>
        <View style={styles.ringDot} />
      </Animated.View>

      {/* Middle ring */}
      <Animated.View style={[styles.ring, styles.ringMiddle, { transform: [{ rotate: spin2 }] }]}>
        <View style={[styles.ringDot, styles.ringDotAccent]} />
      </Animated.View>

      {/* Core orb */}
      <Animated.View style={[styles.orb, { transform: [{ scale: pulse }] }]}>
        <View style={styles.orbInner} />
      </Animated.View>

      <Text style={styles.label}>{label}</Text>
      <Text style={styles.sublabel}>SuperAgent is reasoning...</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.xl,
  },
  ring: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'flex-start',
    borderRadius: 9999,
    borderWidth: 1.5,
  },
  ringOuter: {
    width: 140,
    height: 140,
    borderColor: 'rgba(124,58,237,0.4)',
  },
  ringMiddle: {
    width: 100,
    height: 100,
    borderColor: 'rgba(6,182,212,0.4)',
  },
  ringDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: theme.colors.brand.primary,
    marginTop: -5,
  },
  ringDotAccent: {
    backgroundColor: theme.colors.brand.accent,
  },
  orb: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(124,58,237,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
    ...theme.shadows.glow,
  },
  orbInner: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: theme.colors.brand.primary,
  },
  label: {
    marginTop: 100,
    color: theme.colors.text.primary,
    fontSize: theme.typography.sizes.lg,
    fontWeight: theme.typography.weights.semibold,
    textAlign: 'center',
  },
  sublabel: {
    marginTop: theme.spacing.sm,
    color: theme.colors.text.muted,
    fontSize: theme.typography.sizes.sm,
  },
});
