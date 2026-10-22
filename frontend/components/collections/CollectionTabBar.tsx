'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'motion/react';
import { getAllCollections, type CollectionSlug } from '@/lib/collections';

export default function CollectionTabBar() {
  return (
    <Suspense fallback={null}>
      <CollectionTabBarContent />
    </Suspense>
  );
}

function CollectionTabBarContent() {
  const pathname = usePathname();
  const collections = getAllCollections();

  const activeSlug = pathname.split('/').pop() as CollectionSlug | undefined;

  return (
    <nav
      className='fixed bottom-0 left-0 right-0 z-40 border-t border-white/5'
      style={{
        background: 'linear-gradient(180deg, rgba(10,10,10,0.9) 0%, rgba(5,5,5,0.98) 100%)',
        backdropFilter: 'blur(20px) saturate(1.3)',
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      <div className='flex justify-around items-center h-14 max-w-lg mx-auto px-4'>
        <Link
          href='/collections'
          className='flex flex-col items-center gap-1 px-3 py-1 transition-colors'
          style={{
            color: pathname === '/collections' ? '#B76E79' : 'rgba(255,255,255,0.35)',
          }}
        >
          <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='1.5'>
            <rect x='3' y='3' width='7' height='7' />
            <rect x='14' y='3' width='7' height='7' />
            <rect x='3' y='14' width='7' height='7' />
            <rect x='14' y='14' width='7' height='7' />
          </svg>
          <span className='text-[10px] tracking-wider uppercase'>All</span>
        </Link>

        {collections.map(col => {
          const isActive = activeSlug === col.slug;
          return (
            <Link
              key={col.slug}
              href={`/collections/${col.slug}`}
              className='relative flex flex-col items-center gap-1 px-3 py-1 transition-colors'
              style={{
                color: isActive ? col.accentColor : 'rgba(255,255,255,0.35)',
              }}
            >
              {isActive && (
                <motion.div
                  layoutId='tab-indicator'
                  className='absolute -top-[1px] left-2 right-2 h-[2px] rounded-full'
                  style={{ backgroundColor: col.accentColor }}
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <div
                className='w-4 h-4 rounded-full border-2 transition-colors'
                style={{
                  borderColor: isActive ? col.accentColor : 'rgba(255,255,255,0.2)',
                  backgroundColor: isActive ? `${col.accentColor}30` : 'transparent',
                }}
              />
              <span className='text-[10px] tracking-wider uppercase whitespace-nowrap'>{col.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
