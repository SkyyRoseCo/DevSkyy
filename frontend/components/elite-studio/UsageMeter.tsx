'use client';

import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { eliteStudioClient } from '@/lib/elite-studio-client';
import { Skeleton } from '@/components/ui/skeleton';

interface UsageMeterProps {
  className?: string;
}

function CircleMeter({ used, total, label, color }: { used: number; total: number; label: string; color: string }) {
  const pct = total > 0 ? Math.min(1, used / total) : 0;
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - pct);

  return (
    <div className='flex flex-col items-center gap-2'>
      <div className='relative h-20 w-20'>
        <svg className='h-full w-full -rotate-90' viewBox='0 0 72 72'>
          {/* Track */}
          <circle cx='36' cy='36' r={radius} fill='none' stroke='#1f2937' strokeWidth='6' />
          {/* Progress */}
          <motion.circle
            cx='36'
            cy='36'
            r={radius}
            fill='none'
            stroke={color}
            strokeWidth='6'
            strokeLinecap='round'
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </svg>
        <div className='absolute inset-0 flex flex-col items-center justify-center'>
          <span className='text-sm font-bold text-white'>{Math.round(pct * 100)}%</span>
        </div>
      </div>
      <div className='text-center'>
        <p className='text-xs font-medium text-white'>{label}</p>
        <p className='text-xs text-gray-500'>
          {used.toLocaleString()} / {total.toLocaleString()}
        </p>
      </div>
    </div>
  );
}

export function UsageMeter({ className = '' }: UsageMeterProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['elite-studio', 'usage'],
    queryFn: () => eliteStudioClient.getUsage(),
    refetchInterval: 60_000,
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className={`flex gap-6 ${className}`}>
        {[0, 1, 2].map(i => (
          <div key={i} className='flex flex-col items-center gap-2'>
            <Skeleton className='h-20 w-20 rounded-full bg-gray-800' />
            <Skeleton className='h-3 w-16 bg-gray-800' />
            <Skeleton className='h-3 w-12 bg-gray-800' />
          </div>
        ))}
      </div>
    );
  }

  if (error || !data) {
    return <div className={`text-xs text-gray-500 ${className}`}>Usage data unavailable.</div>;
  }

  return (
    <div className={`flex flex-wrap gap-6 ${className}`}>
      <CircleMeter used={data.renders_used} total={data.renders_quota} label='Renders' color='#B76E79' />
      <CircleMeter used={data.models_3d_used} total={100} label='3D Models' color='#D4AF37' />
      <CircleMeter used={data.social_packs_used} total={50} label='Social Packs' color='#6366f1' />
    </div>
  );
}
