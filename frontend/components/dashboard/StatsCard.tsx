'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { motion } from 'framer-motion';

interface StatsCardProps {
  /** Card title */
  title: string;
  /** Main value to display */
  value: string | number;
  /** Description below the value */
  description: string;
  /** Icon component */
  icon: React.ComponentType<{ className?: string }>;
  /** Trend text */
  trend?: string;
  /** Trend direction for coloring */
  trendDirection?: 'up' | 'down' | 'neutral';
  /** Optional className */
  className?: string;
}

/**
 * Enhanced Dashboard stats card with animations and glassmorphism.
 */
export function StatsCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  trendDirection = 'up',
  className = '',
}: StatsCardProps) {
  const trendColors = {
    up: 'text-green-400',
    down: 'text-red-400',
    neutral: 'text-gray-400',
  };

  const TrendIcon = {
    up: TrendingUp,
    down: TrendingDown,
    neutral: Minus,
  }[trendDirection];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className={`glass group relative overflow-hidden rounded-xl p-6 ${className}`}
    >
      <div className='absolute -right-4 -top-4 h-24 w-24 rounded-full bg-rose-500/10 blur-3xl transition-colors group-hover:bg-rose-500/20' />

      <div className='flex flex-row items-center justify-between pb-2'>
        <span className='text-sm font-medium text-gray-400 group-hover:text-gray-300 transition-colors'>{title}</span>
        <div className='rounded-lg bg-white/5 p-2 group-hover:bg-rose-500/10 transition-colors'>
          <Icon className='h-4 w-4 text-rose-400' aria-hidden='true' />
        </div>
      </div>

      <div className='mt-2 text-3xl font-bold tracking-tight text-white'>{value}</div>
      <p className='mt-1 text-sm text-gray-500'>{description}</p>

      {trend && (
        <div className={`mt-4 flex items-center text-xs font-semibold ${trendColors[trendDirection]}`}>
          <div className='flex items-center rounded-full bg-white/5 px-2 py-1'>
            <TrendIcon className='mr-1 h-3 w-3' aria-hidden='true' />
            <span>{trend}</span>
          </div>
        </div>
      )}
    </motion.div>
  );
}

export default StatsCard;
