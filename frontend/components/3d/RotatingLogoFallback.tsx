'use client';

import { motion } from 'framer-motion';

interface RotatingLogoFallbackProps {
  text: string;
  color: string;
  className?: string;
}

export default function RotatingLogoFallback({ text, color, className = '' }: RotatingLogoFallbackProps) {
  return (
    <div className={`w-full h-[200px] flex items-center justify-center ${className}`}>
      <motion.div
        animate={{ rotateY: 360 }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        style={{ perspective: 800 }}
      >
        <h3
          className='text-4xl md:text-5xl font-display tracking-[0.15em]'
          style={{
            color,
            textShadow: `0 0 40px ${color}40, 0 0 80px ${color}20`,
          }}
        >
          {text}
        </h3>
      </motion.div>
    </div>
  );
}
