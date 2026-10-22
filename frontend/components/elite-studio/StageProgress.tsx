'use client';

import { motion } from 'framer-motion';

interface StageProgressProps {
  stageTimings: Record<string, number>;
  status: 'queued' | 'running' | 'completed' | 'failed';
  className?: string;
}

// Canonical stage order for the Elite Studio compositor pipeline
const STAGE_ORDER = ['bg_removal', 'prompt_engineering', 'relighting', 'inpainting', 'shadow_generation', 'qa_gate'];

function formatStageName(key: string): string {
  return key
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function formatMs(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function StageProgress({ stageTimings, status, className = '' }: StageProgressProps) {
  const timingEntries = Object.entries(stageTimings);
  if (timingEntries.length === 0) {
    return <div className={`text-sm text-gray-500 ${className}`}>No stage data available yet.</div>;
  }

  // Build ordered stage list — use canonical order where possible, append unknown stages at end
  const knownKeys = new Set(STAGE_ORDER);
  const orderedKeys = [
    ...STAGE_ORDER.filter(k => stageTimings[k] !== undefined),
    ...Object.keys(stageTimings).filter(k => !knownKeys.has(k)),
  ];

  const totalMs = orderedKeys.reduce((sum, k) => sum + (stageTimings[k] ?? 0), 0);
  const completedCount = orderedKeys.length;
  const totalCount = status === 'completed' ? completedCount : Math.max(STAGE_ORDER.length, completedCount);

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Overall progress bar */}
      <div className='space-y-1.5'>
        <div className='flex items-center justify-between text-xs text-gray-400'>
          <span>
            {completedCount} / {totalCount} stages
          </span>
          <span>{formatMs(totalMs)} total</span>
        </div>
        <div className='h-2 w-full overflow-hidden rounded-full bg-gray-800'>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(completedCount / totalCount) * 100}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className={`h-full rounded-full ${
              status === 'failed'
                ? 'bg-red-500'
                : status === 'completed'
                  ? 'bg-gradient-to-r from-[#B76E79] to-[#D4AF37]'
                  : 'bg-gradient-to-r from-blue-500 to-[#B76E79] animate-pulse'
            }`}
          />
        </div>
      </div>

      {/* Individual stage rows */}
      <div className='space-y-2'>
        {orderedKeys.map((key, idx) => {
          const ms = stageTimings[key] ?? 0;
          const widthPct = totalMs > 0 ? (ms / totalMs) * 100 : 0;

          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className='flex items-center gap-3'
            >
              <div className='w-32 shrink-0 truncate text-right text-xs text-gray-400'>{formatStageName(key)}</div>
              <div className='flex-1 h-1.5 rounded-full bg-gray-800 overflow-hidden'>
                <div className='h-full rounded-full bg-[#B76E79]/60' style={{ width: `${widthPct}%` }} />
              </div>
              <div className='w-14 shrink-0 text-right text-xs font-mono text-gray-400'>{formatMs(ms)}</div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
