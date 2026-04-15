/**
 * INTENTA — Result Card Component
 * Expandable card displaying one section of the generated output.
 */
import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  LayoutAnimation,
  Platform,
  UIManager,
} from 'react-native';
import { theme } from '../theme/theme';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

interface Props {
  title: string;
  icon: string;
  accentColor?: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  badge?: string;
  forceExpanded?: boolean;
}

export default function ResultCard({
  title,
  icon,
  accentColor = theme.colors.brand.primary,
  children,
  defaultExpanded = false,
  badge,
  forceExpanded = false,
}: Props) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  
  const isActuallyExpanded = expanded || forceExpanded;
  const rotateValue = isActuallyExpanded ? 1 : 0;
  
  const rotateAnim = useRef(new Animated.Value(rotateValue)).current;

  // Sync animation if it changes externally
  React.useEffect(() => {
    Animated.timing(rotateAnim, {
      toValue: isActuallyExpanded ? 0 : 1, // Actually 0 means rotated in the original code
      duration: 250,
      useNativeDriver: true,
    }).start();
  }, [isActuallyExpanded]);

  const toggle = () => {
    if (forceExpanded) return; // Disallow toggle if forced
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    Animated.timing(rotateAnim, {
      toValue: expanded ? 0 : 1, // toggle direction
      duration: 250,
      useNativeDriver: true,
    }).start();
    setExpanded(!expanded);
  };

  const arrowRotate = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],
  });

  return (
    <View style={[styles.card, { borderColor: isActuallyExpanded ? accentColor + '60' : theme.colors.border.default }]}>
      {/* Header */}
      <TouchableOpacity
        style={styles.header}
        onPress={toggle}
        activeOpacity={0.75}
      >
        <View style={[styles.iconContainer, { backgroundColor: accentColor + '20' }]}>
          <Text style={[styles.icon, { color: accentColor }]}>{icon}</Text>
        </View>

        <Text style={styles.title}>{title}</Text>

        {badge && (
          <View style={[styles.badge, { backgroundColor: accentColor + '25' }]}>
            <Text style={[styles.badgeText, { color: accentColor }]}>{badge}</Text>
          </View>
        )}

        <Animated.Text style={[styles.arrow, { transform: [{ rotate: arrowRotate }] }]}>
          ▾
        </Animated.Text>
      </TouchableOpacity>

      {/* Content */}
      {isActuallyExpanded && (
        <View style={styles.content}>
          <View style={[styles.divider, { backgroundColor: accentColor + '30' }]} />
          {children}
        </View>
      )}
    </View>
  );
}

export function InfoRow({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={[styles.infoValue, accent ? { color: accent } : {}]}>{value}</Text>
    </View>
  );
}

export function TagList({ tags, color }: { tags: string[]; color?: string }) {
  return (
    <View style={styles.tagList}>
      {tags.map((tag, i) => (
        <View key={i} style={[styles.tag, { backgroundColor: (color || theme.colors.brand.primary) + '20', borderColor: (color || theme.colors.brand.primary) + '40' }]}>
          <Text style={[styles.tagText, { color: color || theme.colors.brand.primary }]}>{tag}</Text>
        </View>
      ))}
    </View>
  );
}

export function BulletList({ items, color }: { items: string[]; color?: string }) {
  return (
    <View>
      {items.map((item, i) => (
        <View key={i} style={styles.bulletRow}>
          <Text style={[styles.bullet, { color: color || theme.colors.brand.accent }]}>◆</Text>
          <Text style={styles.bulletText}>{item}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.bg.card,
    borderRadius: theme.radii.lg,
    borderWidth: 1.5,
    marginBottom: theme.spacing.md,
    overflow: 'hidden',
    ...theme.shadows.card,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: theme.spacing.md,
    gap: theme.spacing.sm,
  },
  iconContainer: {
    width: 38,
    height: 38,
    borderRadius: theme.radii.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    fontSize: 18,
  },
  title: {
    flex: 1,
    color: theme.colors.text.primary,
    fontSize: theme.typography.sizes.md,
    fontWeight: theme.typography.weights.semibold,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: theme.radii.full,
  },
  badgeText: {
    fontSize: theme.typography.sizes.xs,
    fontWeight: theme.typography.weights.bold,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  arrow: {
    color: theme.colors.text.muted,
    fontSize: 16,
    marginLeft: 4,
  },
  content: {
    paddingHorizontal: theme.spacing.md,
    paddingBottom: theme.spacing.md,
  },
  divider: {
    height: 1,
    marginBottom: theme.spacing.md,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  infoLabel: {
    color: theme.colors.text.muted,
    fontSize: theme.typography.sizes.sm,
    flex: 1,
  },
  infoValue: {
    color: theme.colors.text.primary,
    fontSize: theme.typography.sizes.sm,
    fontWeight: theme.typography.weights.medium,
    flex: 2,
    textAlign: 'right',
  },
  tagList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: theme.spacing.xs,
  },
  tag: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: theme.radii.full,
    borderWidth: 1,
  },
  tagText: {
    fontSize: theme.typography.sizes.xs,
    fontWeight: theme.typography.weights.semibold,
  },
  bulletRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
    gap: 8,
  },
  bullet: {
    fontSize: 8,
    marginTop: 4,
  },
  bulletText: {
    flex: 1,
    color: theme.colors.text.secondary,
    fontSize: theme.typography.sizes.sm,
    lineHeight: 20,
  },
});
