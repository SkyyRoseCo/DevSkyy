/**
 * Success Celebration Component
 * Displays confetti animation and order confirmation after successful checkout
 *
 * @author DevSkyy Platform Team
 * @version 1.0.0
 */

import React, { useEffect, useRef, useState } from 'react';

/**
 * Props for SuccessCelebration component
 */
export interface SuccessCelebrationProps {
  orderId: string;
  orderTotal: number;
  currency?: string;
  customerEmail: string;
  onContinueShopping: () => void;
  onViewOrder?: (orderId: string) => void;
}

/**
 * Confetti particle interface
 */
interface ConfettiParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  rotation: number;
  rotationSpeed: number;
  color: string;
  size: number;
  opacity: number;
}

/**
 * SkyyRose brand colors for confetti
 */
const SKYYROSE_COLORS = [
  '#B76E79', // Rose gold primary
  '#D4A5AE', // Light rose
  '#8B5A63', // Dark rose
  '#E8C4CB', // Pale rose
  '#1A1A1A', // Black
  '#FFD700', // Gold accent
];

/**
 * Success Celebration Component
 */
export const SuccessCelebration: React.FC<SuccessCelebrationProps> = ({
  orderId,
  orderTotal,
  currency = 'USD',
  customerEmail,
  onContinueShopping,
  onViewOrder,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const particlesRef = useRef<ConfettiParticle[]>([]);

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setIsVisible(true), 100);

    // Initialize confetti
    initializeConfetti();
    startConfettiAnimation();

    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  /**
   * Initialize confetti particles
   */
  const initializeConfetti = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const particleCount = 150;
    const particles: ConfettiParticle[] = [];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: -20,
        vx: (Math.random() - 0.5) * 4,
        vy: Math.random() * 3 + 2,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 10,
        color: SKYYROSE_COLORS[Math.floor(Math.random() * SKYYROSE_COLORS.length)] ?? '#B76E79',
        size: Math.random() * 8 + 4,
        opacity: 1,
      });
    }

    particlesRef.current = particles;
  };

  /**
   * Start confetti animation loop
   */
  const startConfettiAnimation = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach((particle, index) => {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.rotation += particle.rotationSpeed;
        particle.vy += 0.1; // Gravity

        // Fade out when falling off screen
        if (particle.y > canvas.height) {
          particle.opacity -= 0.02;
        }

        // Draw particle
        ctx.save();
        ctx.translate(particle.x, particle.y);
        ctx.rotate((particle.rotation * Math.PI) / 180);
        ctx.globalAlpha = particle.opacity;
        ctx.fillStyle = particle.color;

        // Draw rectangle (confetti shape)
        ctx.fillRect(-particle.size / 2, -particle.size / 2, particle.size, particle.size * 1.5);

        ctx.restore();

        // Remove faded particles
        if (particle.opacity <= 0) {
          particlesRef.current.splice(index, 1);
        }
      });

      // Continue animation if particles remain
      if (particlesRef.current.length > 0) {
        animationFrameRef.current = requestAnimationFrame(animate);
      }
    };

    animate();
  };

  /**
   * Format currency
   */
  const formatCurrency = (amount: number, curr: string): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: curr,
    }).format(amount);
  };

  return (
    <div
      role='dialog'
      aria-modal='true'
      aria-labelledby='success-title'
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.5s ease',
      }}
    >
      {/* Confetti Canvas */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
        }}
      />

      {/* Success Card */}
      <div
        style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          padding: '48px',
          maxWidth: '500px',
          width: '90%',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          textAlign: 'center',
          transform: isVisible ? 'scale(1)' : 'scale(0.8)',
          transition: 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Success Icon */}
        <div
          style={{
            width: '80px',
            height: '80px',
            margin: '0 auto 24px',
            backgroundColor: '#B76E79',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: 'pulse 2s ease-in-out infinite',
          }}
        >
          <svg
            width='48'
            height='48'
            viewBox='0 0 24 24'
            fill='none'
            stroke='#FFFFFF'
            strokeWidth='3'
            strokeLinecap='round'
            strokeLinejoin='round'
          >
            <polyline points='20 6 9 17 4 12' />
          </svg>
        </div>

        {/* Success Message */}
        <h2
          id='success-title'
          style={{
            fontSize: '32px',
            fontWeight: 'bold',
            color: '#1A1A1A',
            marginBottom: '12px',
            fontFamily: 'Georgia, serif',
          }}
        >
          Order Confirmed!
        </h2>

        <p
          style={{
            fontSize: '16px',
            color: '#666666',
            marginBottom: '32px',
            lineHeight: '1.6',
          }}
        >
          Thank you for your purchase from SkyyRose. Your order has been successfully placed.
        </p>

        {/* Order Details */}
        <div
          style={{
            backgroundColor: '#F9F9F9',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '32px',
            textAlign: 'left',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '12px',
            }}
          >
            <span style={{ color: '#666666', fontSize: '14px' }}>Order Number:</span>
            <strong style={{ color: '#1A1A1A', fontSize: '14px' }}>{orderId}</strong>
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '12px',
            }}
          >
            <span style={{ color: '#666666', fontSize: '14px' }}>Total:</span>
            <strong style={{ color: '#B76E79', fontSize: '18px' }}>{formatCurrency(orderTotal, currency)}</strong>
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
            }}
          >
            <span style={{ color: '#666666', fontSize: '14px' }}>Confirmation Email:</span>
            <span style={{ color: '#1A1A1A', fontSize: '14px' }}>{customerEmail}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', flexDirection: 'column' }}>
          <button
            onClick={onContinueShopping}
            aria-label='Continue shopping'
            style={{
              backgroundColor: '#B76E79',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              padding: '16px 32px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(183, 110, 121, 0.3)',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.backgroundColor = '#A05D6B';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(183, 110, 121, 0.4)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.backgroundColor = '#B76E79';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(183, 110, 121, 0.3)';
            }}
          >
            Continue Shopping
          </button>

          {onViewOrder && (
            <button
              onClick={() => onViewOrder(orderId)}
              aria-label='View order details'
              style={{
                backgroundColor: 'transparent',
                color: '#B76E79',
                border: '2px solid #B76E79',
                borderRadius: '8px',
                padding: '14px 32px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.backgroundColor = '#B76E79';
                e.currentTarget.style.color = '#FFFFFF';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#B76E79';
              }}
            >
              View Order Details
            </button>
          )}
        </div>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              transform: scale(1);
            }
            50% {
              transform: scale(1.1);
            }
          }
        `}
      </style>
    </div>
  );
};

export default SuccessCelebration;
