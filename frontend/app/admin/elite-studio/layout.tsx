'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Sparkles,
  Activity,
  Users,
  Pencil,
  LayoutGrid,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const ELITE_NAV = [
  { title: 'Command Center', href: '/admin/elite-studio', icon: LayoutGrid, exact: true },
  { title: 'Operations', href: '/admin/elite-studio/operations', icon: Activity },
  { title: 'Characters', href: '/admin/elite-studio/characters', icon: Users },
  { title: 'Design Co-Pilot', href: '/admin/elite-studio/design', icon: Pencil },
];

function EliteStudioNav() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-1" aria-label="Elite Studio navigation">
      {ELITE_NAV.map((item) => {
        const isActive = item.exact
          ? pathname === item.href
          : pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
              isActive
                ? 'bg-[#B76E79]/15 text-[#B76E79]'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
            {item.title}
          </Link>
        );
      })}
    </nav>
  );
}

export default function EliteStudioLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-6">
      {/* Section header with sub-navigation */}
      <div className="border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#B76E79] to-[#D4AF37]">
            <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Elite Studio</h2>
          </div>
        </div>

        <Suspense fallback={<div className="h-8" aria-hidden="true" />}>
          <EliteStudioNav />
        </Suspense>
      </div>

      {children}
    </div>
  );
}
