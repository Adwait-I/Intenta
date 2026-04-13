/**
 * INTENTA — Web Dashboard
 * Authenticated landing showcasing user history and creation CTA.
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  StatusBar,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { theme } from '../theme/theme';
import { fetchSessions, fetchSessionById } from '../services/api';
import { signOut, getCurrentUser } from '../services/localAuth';

const { width } = Dimensions.get('window');

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Landing'>;
};

export default function LandingScreen({ navigation }: Props) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const userEmail = getCurrentUser()?.email || 'user@intenta.local';

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    const data = await fetchSessions();
    setSessions(data);
    setLoading(false);
  };

  const openSession = async (sessionId: string) => {
    try {
      const fullSessionData = await fetchSessionById(sessionId);
      if (fullSessionData) {
        navigation.navigate('Output', { result: fullSessionData, processingMs: 0 }); // pass full result to original viewer, 0ms indicates history load
      } else {
        console.error("Failed to load session details");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSignOut = () => {
    signOut();
    // AppNavigator's onAuthStateChanged listener handles redirect to Login
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#05050A" />

      {/* Top Navigation Bar */}
      <View style={styles.navbar}>
        <View style={styles.navLeft}>
            <View style={styles.navLogoBox}>
              <Text style={styles.navLogoSymbol}>✦</Text>
            </View>
            <Text style={styles.navTitle}>INTENTA</Text>
        </View>

        <View style={styles.navRight}>
          <Text style={styles.navEmail}>{userEmail}</Text>
          <TouchableOpacity style={styles.logoutButton} onPress={handleSignOut}>
            <Text style={styles.logoutText}>Sign Out</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        
        {/* Banner Section */}
        <LinearGradient
          colors={['#140833', '#11112B']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.banner}
        >
          <View style={styles.bannerContent}>
            <Text style={styles.bannerTitle}>Design Enterprise Systems Using Local AI</Text>
            <Text style={styles.bannerSubtitle}>
              Instantly generate production-grade architectures and tech stacks by typing your business intent.
            </Text>
            
            <TouchableOpacity
              onPress={() => navigation.navigate('Input')}
              activeOpacity={0.85}
              style={styles.ctaWrapper}
            >
              <LinearGradient
                colors={['#7C3AED', '#4F46E5']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.ctaButton}
              >
                <Text style={styles.ctaText}>✦ Create New Architecture</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
          
          {/* Subtle Background Glow inside banner */}
          <View style={styles.bannerGlow} />
        </LinearGradient>

        {/* History Section */}
        <View style={styles.historySection}>
          <Text style={styles.sectionTitle}>Your Recent Designs</Text>

          {loading ? (
            <View style={styles.loaderBox}>
              <ActivityIndicator color={theme.colors.brand.primary} size="large" />
              <Text style={styles.loaderText}>Loading designs...</Text>
            </View>
          ) : sessions.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptySymbol}>📁</Text>
              <Text style={styles.emptyText}>You haven't generated any systems yet.</Text>
            </View>
          ) : (
            <View style={styles.grid}>
              {sessions.map((session, i) => {
                const date = new Date(session.created_at).toLocaleDateString();
                const goal = session.data?.intent?.goal || 'Unknown Intent';
                const domain = session.data?.intent?.domain || 'Unknown Domain';
                const pattern = session.data?.architecture?.pattern || 'Microservices';
                
                return (
                  <TouchableOpacity 
                    key={session.session_id || i} 
                    style={styles.card}
                    activeOpacity={0.8}
                    onPress={() => openSession(session.session_id)}
                  >
                    <View style={styles.cardHeader}>
                      <Text style={styles.cardDomain}>{domain.toUpperCase()}</Text>
                      <Text style={styles.cardDate}>{date}</Text>
                    </View>
                    
                    <Text style={styles.cardGoal} numberOfLines={2}>
                      "{goal}"
                    </Text>
                    
                    <View style={styles.cardFooter}>
                      <View style={styles.patternChip}>
                        <Text style={styles.patternText}>{pattern}</Text>
                      </View>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </View>
          )}
        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#05050A',
  },
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.xl,
    paddingVertical: theme.spacing.lg,
    backgroundColor: '#0A0A1A',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
  },
  navLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  navLogoBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: 'rgba(124,58,237,0.2)',
    borderWidth: 1,
    borderColor: 'rgba(124,58,237,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  navLogoSymbol: {
    color: '#A78BFA',
    fontSize: 16,
    fontWeight: '900',
  },
  navTitle: {
    color: theme.colors.text.primary,
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 2,
  },
  navRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  navEmail: {
    color: theme.colors.text.muted,
    fontSize: 13,
    fontWeight: '500',
    display: width < 600 ? 'none' : 'flex',
  },
  logoutButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: theme.radii.md,
    backgroundColor: 'rgba(239,68,68,0.1)',
    borderWidth: 1,
    borderColor: 'rgba(239,68,68,0.3)',
  },
  logoutText: {
    color: '#FCA5A5',
    fontSize: 13,
    fontWeight: '600',
  },
  scrollContent: {
    padding: theme.spacing.xl,
    paddingBottom: 60,
  },
  banner: {
    borderRadius: theme.radii.xl,
    padding: theme.spacing['2xl'],
    position: 'relative',
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(124,58,237,0.3)',
    marginBottom: theme.spacing['2xl'],
  },
  bannerContent: {
    position: 'relative',
    zIndex: 10,
    maxWidth: 600,
  },
  bannerTitle: {
    fontSize: 32,
    fontWeight: '800',
    color: '#F0F0FF',
    lineHeight: 40,
    marginBottom: theme.spacing.sm,
  },
  bannerSubtitle: {
    fontSize: 15,
    color: theme.colors.text.secondary,
    lineHeight: 24,
    marginBottom: theme.spacing.xl,
  },
  ctaWrapper: {
    alignSelf: 'flex-start',
    borderRadius: theme.radii.full,
    ...theme.shadows.button,
  },
  ctaButton: {
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: theme.radii.full,
  },
  ctaText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  bannerGlow: {
    position: 'absolute',
    right: -50,
    bottom: -100,
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: '#7C3AED',
    opacity: 0.15,
    shadowColor: '#7C3AED',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 1,
    shadowRadius: 100,
    zIndex: 1,
  },
  historySection: {
    width: '100%',
  },
  sectionTitle: {
    color: theme.colors.text.primary,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: theme.spacing.lg,
  },
  loaderBox: {
    padding: 60,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loaderText: {
    color: theme.colors.text.muted,
    marginTop: 12,
    fontSize: 13,
  },
  emptyState: {
    padding: 60,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.bg.card,
    borderRadius: theme.radii.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  emptySymbol: {
    fontSize: 32,
    marginBottom: 8,
  },
  emptyText: {
    color: theme.colors.text.muted,
    fontSize: 14,
  },
  grid: {
    flexDirection: width > 800 ? 'row' : 'column',
    flexWrap: 'wrap',
    gap: 16,
  },
  card: {
    width: (width > 800 ? 'calc(33.333% - 11px)' : '100%') as any,
    backgroundColor: theme.colors.bg.card,
    borderRadius: theme.radii.lg,
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  cardDomain: {
    color: theme.colors.brand.accent,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
  },
  cardDate: {
    color: theme.colors.text.muted,
    fontSize: 11,
  },
  cardGoal: {
    color: theme.colors.text.primary,
    fontSize: 15,
    lineHeight: 22,
    fontWeight: '500',
    marginBottom: theme.spacing.lg,
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  patternChip: {
    backgroundColor: 'rgba(79,70,229,0.15)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: theme.radii.full,
    borderWidth: 1,
    borderColor: 'rgba(79,70,229,0.3)',
  },
  patternText: {
    color: '#A5B4FC',
    fontSize: 11,
    fontWeight: '600',
  },
});
