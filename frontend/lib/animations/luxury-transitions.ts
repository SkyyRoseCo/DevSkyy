import { Variants, Transition } from 'motion/react';

/**
 * SkyyRose Luxury Animation Library
 * Production-grade animations for immersive experiences
 */

// Easing curves
export const luxuryEasing = {
  smooth: [0.43, 0.13, 0.23, 0.96],
  elegant: [0.6, -0.05, 0.01, 0.99],
  swift: [0.65, 0, 0.35, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
} as const;

// Duration presets
export const duration = {
  instant: 0.15,
  fast: 0.3,
  normal: 0.5,
  slow: 0.8,
  elegant: 1.2,
} as const;

// Page transitions
export const pageTransition: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.normal,
      ease: luxuryEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.smooth,
    },
  },
};

// Product reveal animations
export const productReveal: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.9,
    rotateY: -10,
  },
  visible: {
    opacity: 1,
    scale: 1,
    rotateY: 0,
    transition: {
      duration: duration.elegant,
      ease: luxuryEasing.elegant,
    },
  },
};

// Stagger container for product grids
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

// Individual product card
export const productCard: Variants = {
  hidden: {
    opacity: 0,
    y: 30,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: duration.normal,
      ease: luxuryEasing.smooth,
    },
  },
  hover: {
    scale: 1.03,
    y: -5,
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.swift,
    },
  },
  tap: {
    scale: 0.98,
  },
};

// Fade in from direction
export const fadeInDirection = {
  up: {
    initial: { opacity: 0, y: 40 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -40 },
  },
  down: {
    initial: { opacity: 0, y: -40 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 40 },
  },
  left: {
    initial: { opacity: 0, x: 40 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -40 },
  },
  right: {
    initial: { opacity: 0, x: -40 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 40 },
  },
} as const;

// Luxury modal/overlay
export const modalOverlay: Variants = {
  hidden: {
    opacity: 0,
    backdropFilter: 'blur(0px)',
  },
  visible: {
    opacity: 1,
    backdropFilter: 'blur(10px)',
    transition: {
      duration: duration.normal,
    },
  },
  exit: {
    opacity: 0,
    backdropFilter: 'blur(0px)',
    transition: {
      duration: duration.fast,
    },
  },
};

export const modalContent: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 20,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: duration.normal,
      ease: luxuryEasing.elegant,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: {
      duration: duration.fast,
    },
  },
};

// Rose gold shimmer effect
export const shimmer: Variants = {
  initial: {
    backgroundPosition: '-200% center',
  },
  animate: {
    backgroundPosition: '200% center',
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// Parallax scroll effect
export const parallaxScroll = (speed: number = 0.5) => ({
  initial: { y: 0 },
  animate: (scrollY: number) => ({
    y: scrollY * speed,
  }),
});

// Magnetic hover effect
export const magneticHover = {
  rest: { x: 0, y: 0 },
  hover: (mousePosition: { x: number; y: number }) => ({
    x: mousePosition.x * 0.3,
    y: mousePosition.y * 0.3,
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.swift,
    },
  }),
};

// Text reveal animation (word by word)
export const textReveal: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

export const textWord: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.normal,
      ease: luxuryEasing.smooth,
    },
  },
};

// Luxury button animations
export const luxuryButton: Variants = {
  rest: {
    scale: 1,
    backgroundColor: '#B76E79',
  },
  hover: {
    scale: 1.05,
    backgroundColor: '#8B5A62',
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.swift,
    },
  },
  tap: {
    scale: 0.95,
  },
};

// Image loading animation
export const imageLoad: Variants = {
  loading: {
    scale: 1.1,
    filter: 'blur(10px)',
  },
  loaded: {
    scale: 1,
    filter: 'blur(0px)',
    transition: {
      duration: duration.slow,
      ease: luxuryEasing.elegant,
    },
  },
};

// 3D card tilt effect
export const cardTilt = {
  rest: {
    rotateX: 0,
    rotateY: 0,
  },
  tilt: (mouse: { x: number; y: number }) => ({
    rotateX: mouse.y * 10,
    rotateY: mouse.x * 10,
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.swift,
    },
  }),
};

// Scroll-triggered fade in
export const scrollFadeIn: Variants = {
  hidden: {
    opacity: 0,
    y: 50,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.slow,
      ease: luxuryEasing.elegant,
    },
  },
};

// Navigation menu animations
export const navMenu: Variants = {
  closed: {
    opacity: 0,
    height: 0,
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.smooth,
    },
  },
  open: {
    opacity: 1,
    height: 'auto',
    transition: {
      duration: duration.normal,
      ease: luxuryEasing.smooth,
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};

export const navItem: Variants = {
  closed: {
    opacity: 0,
    x: -20,
  },
  open: {
    opacity: 1,
    x: 0,
    transition: {
      duration: duration.fast,
      ease: luxuryEasing.smooth,
    },
  },
};

// Hero section animations
export const heroTitle: Variants = {
  hidden: {
    opacity: 0,
    y: 100,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.elegant,
      ease: luxuryEasing.elegant,
    },
  },
};

export const heroSubtitle: Variants = {
  hidden: {
    opacity: 0,
    y: 50,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.elegant,
      ease: luxuryEasing.elegant,
      delay: 0.2,
    },
  },
};

export const heroCTA: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: duration.normal,
      ease: luxuryEasing.bounce,
      delay: 0.4,
    },
  },
};

// Utility: Create custom spring transition
export function createSpring(stiffness: number = 300, damping: number = 30): Transition {
  return {
    type: 'spring',
    stiffness,
    damping,
  };
}

// Utility: Create custom ease transition
export function createEase(duration: number = 0.5, ease: readonly number[] = luxuryEasing.smooth): Transition {
  return {
    duration,
    ease: ease as any,
  };
}
