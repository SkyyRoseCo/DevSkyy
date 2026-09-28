'use client';

import { useEffect, useRef } from 'react';
import type { CSSProperties, KeyboardEvent, PointerEvent, ReactNode } from 'react';
import type { OsWindow } from '@/lib/agent-os/window-manager';

interface OsWindowFrameProps {
  win: OsWindow;
  focused: boolean;
  onFocus: () => void;
  onClose: () => void;
  onMinimize: () => void;
  onMove: (x: number, y: number) => void;
  children: ReactNode;
}

/** Minimum strip of title bar that must stay inside the desktop when dragged. */
const KEEP_VISIBLE_PX = 160;

/**
 * One OS window. On `lg+` it is absolutely positioned from the window
 * manager's x/y (via CSS vars, so the coordinates never apply on mobile) and
 * dragged by its title bar. Below `lg` it renders as a stacked full-width
 * panel. Minimized windows stay mounted (`hidden`) so terminal history and
 * form input survive a minimize.
 */
export function OsWindowFrame({ win, focused, onFocus, onClose, onMinimize, onMove, children }: OsWindowFrameProps) {
  const ref = useRef<HTMLElement>(null);
  const drag = useRef<{ dx: number; dy: number } | null>(null);

  useEffect(() => {
    ref.current?.focus({ preventScroll: true });
  }, []);

  const startDrag = (e: PointerEvent<HTMLElement>) => {
    if (e.button !== 0 || (e.target as HTMLElement).closest('button')) return;
    drag.current = { dx: e.clientX - win.x, dy: e.clientY - win.y };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const continueDrag = (e: PointerEvent<HTMLElement>) => {
    if (!drag.current) return;
    const desktop = ref.current?.parentElement;
    const maxX = desktop ? desktop.clientWidth - KEEP_VISIBLE_PX : Number.POSITIVE_INFINITY;
    const maxY = desktop ? desktop.clientHeight - 48 : Number.POSITIVE_INFINITY;
    onMove(Math.min(e.clientX - drag.current.dx, maxX), Math.min(e.clientY - drag.current.dy, maxY));
  };

  const endDrag = (e: PointerEvent<HTMLElement>) => {
    drag.current = null;
    if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLElement>) => {
    if (e.key === 'Escape') {
      e.stopPropagation();
      onClose();
    }
  };

  const position = { '--wx': `${win.x}px`, '--wy': `${win.y}px`, zIndex: win.z } as CSSProperties;

  return (
    <section
      ref={ref}
      role='dialog'
      aria-label={win.title}
      tabIndex={-1}
      hidden={win.minimized}
      onKeyDown={onKeyDown}
      onPointerDownCapture={onFocus}
      style={position}
      className={`${win.minimized ? 'hidden' : 'flex'} flex-col w-full h-[460px] rounded-[10px] border overflow-hidden outline-none shadow-[0_24px_60px_rgba(0,0,0,.55)] lg:pointer-events-auto lg:absolute lg:left-[var(--wx)] lg:top-[var(--wy)] lg:w-[600px] lg:h-[440px] ${
        focused ? 'border-[#B76E79]/60' : 'border-[#2A2A2A]'
      }`}
    >
      <header
        onPointerDown={startDrag}
        onPointerMove={continueDrag}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        className='flex items-center gap-3 h-10 px-3.5 flex-none select-none border-b border-white/[0.06] lg:cursor-move lg:touch-none'
        style={{ background: focused ? '#16131A' : '#121214' }}
      >
        <div className='flex gap-1.5'>
          <button
            type='button'
            onClick={onClose}
            aria-label={`Close ${win.title}`}
            className='w-3.5 h-3.5 rounded-full bg-[#DC143C] hover:brightness-125 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
          />
          <button
            type='button'
            onClick={onMinimize}
            aria-label={`Minimize ${win.title}`}
            className='w-3.5 h-3.5 rounded-full bg-[#D4AF37] hover:brightness-125 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
          />
        </div>
        <h2
          className='flex-1 truncate text-center text-[12px] uppercase tracking-[0.18em] m-0'
          style={{ fontFamily: 'var(--font-cinzel)', color: focused ? '#FFFFFF' : '#B3B3B3' }}
        >
          {win.title}
        </h2>
        <span className='w-[42px]' aria-hidden />
      </header>
      <div className='flex-1 min-h-0 overflow-auto' style={{ background: '#0E0E10' }}>
        {children}
      </div>
    </section>
  );
}
