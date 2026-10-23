'use client';

import { useMemo } from 'react';
import { signOut } from 'next-auth/react';
import { StatusDot } from './StatusPill';

interface TopBarProps {
  title: string;
}

export function TopBar({ title }: TopBarProps) {
  // Client-computed — a Server Component can't call `new Date()` during
  // prerendering under Next.js 16 Cache Components without first
  // establishing a dynamic boundary (connection()/fetch()), and this value
  // has no SEO/content weight that would justify that ceremony.
  const dateLabel = useMemo(
    () =>
      new Intl.DateTimeFormat('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      }).format(new Date()),
    []
  );

  return (
    <header
      className='sticky top-0 z-40 min-h-[68px] flex flex-wrap items-center gap-3 px-4 py-3 border-b border-white/[0.06] backdrop-blur-2xl backdrop-saturate-150 lg:h-[68px] lg:flex-nowrap lg:gap-6 lg:px-9 lg:py-0'
      style={{ background: 'rgba(8,8,10,.82)' }}
    >
      <div className='w-full min-w-0 lg:w-auto'>
        <h1
          className='text-[18px] uppercase tracking-[0.14em] text-white font-semibold m-0'
          style={{ fontFamily: 'var(--font-cinzel)' }}
        >
          {title}
        </h1>
        <div className='font-mono text-[10px] tracking-[0.14em] text-[#A0A0A0] mt-[3px]'>{dateLabel}</div>
      </div>
      <div className='hidden lg:block lg:flex-1' />
      <div className='flex items-center gap-2 font-mono text-[10px] tracking-[0.16em] text-[#B3B3B3] uppercase px-3.5 py-2 border border-white/10 rounded-md'>
        <StatusDot color='#5FBF7F' pulse size={7} />
        skyyrose.co · Live
      </div>
      <a
        href='/admin/collections'
        className='flex items-center gap-2.5 border border-white/10 rounded-md px-4 py-2 text-[#E0E0E0] text-[13px] tracking-[0.22em] hover:bg-white/5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
        style={{ fontFamily: 'var(--font-bebas-neue)' }}
      >
        New Drop
      </a>
      <button
        type='button'
        onClick={() => signOut({ callbackUrl: '/login' })}
        className='font-mono text-[10px] tracking-[0.16em] uppercase text-[#8A8A92] hover:text-[#E0E0E0] transition-colors px-3 py-2 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
      >
        Sign out
      </button>
    </header>
  );
}
