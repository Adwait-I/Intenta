/**
 * INTENTA — Design System Theme
 * Premium dark color palette, typography, spacing, and shadow tokens.
 */

export const theme = {
  colors: {
    // Backgrounds
    bg: {
      primary: '#0A0A1A',
      secondary: '#11112B',
      card: '#16163A',
      cardHover: '#1E1E4A',
      overlay: 'rgba(10,10,26,0.85)',
    },

    // Brand purple-blue gradient
    brand: {
      primary: '#7C3AED',
      secondary: '#4F46E5',
      accent: '#06B6D4',
      glow: 'rgba(124,58,237,0.35)',
    },

    // Semantic
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',

    // Text
    text: {
      primary: '#F0F0FF',
      secondary: '#A0A0CC',
      muted: '#6B6B99',
      inverse: '#0A0A1A',
    },

    // Borders
    border: {
      default: 'rgba(124,58,237,0.25)',
      strong: 'rgba(124,58,237,0.55)',
      subtle: 'rgba(255,255,255,0.06)',
    },

    // Status indicators
    status: {
      critical: '#FF4D6D',
      high: '#FF8800',
      medium: '#FFD60A',
      low: '#06D6A0',
    },

    // Compliance tags
    compliance: {
      gdpr: '#4361EE',
      soc2: '#7209B7',
      hipaa: '#3A0CA3',
      pci: '#F72585',
    },
  },

  // Gradients (as arrays for LinearGradient)
  gradients: {
    hero: ['#0A0A1A', '#1A0533', '#0A0A1A'] as string[],
    card: ['#16163A', '#1A1A45'] as string[],
    brand: ['#7C3AED', '#4F46E5'] as string[],
    accent: ['#4F46E5', '#06B6D4'] as string[],
    button: ['#7C3AED', '#4F46E5', '#3B82F6'] as string[],
    danger: ['#EF4444', '#DC2626'] as string[],
  },

  typography: {
    fonts: {
      heading: 'System',
      body: 'System',
      mono: 'Courier New',
    },
    sizes: {
      xs: 11,
      sm: 13,
      md: 15,
      lg: 17,
      xl: 20,
      '2xl': 24,
      '3xl': 30,
      '4xl': 38,
      '5xl': 48,
    },
    weights: {
      regular: '400' as const,
      medium: '500' as const,
      semibold: '600' as const,
      bold: '700' as const,
      extrabold: '800' as const,
      black: '900' as const,
    },
    lineHeights: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
    },
  },

  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    '2xl': 48,
    '3xl': 64,
  },

  radii: {
    sm: 8,
    md: 14,
    lg: 20,
    xl: 28,
    full: 9999,
  },

  shadows: {
    card: {
      shadowColor: '#7C3AED',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.25,
      shadowRadius: 20,
      elevation: 8,
    },
    glow: {
      shadowColor: '#7C3AED',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.6,
      shadowRadius: 30,
      elevation: 12,
    },
    button: {
      shadowColor: '#4F46E5',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.4,
      shadowRadius: 16,
      elevation: 10,
    },
  },
} as const;

export type Theme = typeof theme;
