'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'motion/react';
import { Menu, X } from 'lucide-react';

const NAV_LINKS = [
  { href: '/', label: 'Home' },
  { href: '/collections', label: 'Collections' },
  { href: '/pre-order', label: 'Pre-Order' },
];

export default function SiteNav() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 50);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled ? 'bg-black/80 backdrop-blur-xl border-b border-white/5' : 'bg-transparent'
        }`}
      >
        <div className='max-w-7xl mx-auto px-6 py-4 flex items-center justify-between'>
          {/* Logo */}
          <Link href='/' className='group flex items-center gap-3'>
            <span className='text-2xl font-display tracking-[0.15em] text-white group-hover:text-[#B76E79] transition-colors duration-300'>
              SKYYROSE
            </span>
          </Link>

          {/* Desktop Links */}
          <div className='hidden md:flex items-center gap-8'>
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className='text-sm tracking-[0.15em] uppercase text-white/60 hover:text-[#B76E79] transition-colors duration-300'
              >
                {link.label}
              </Link>
            ))}
            <Link
              href='/pre-order'
              className='px-6 py-2 text-sm tracking-[0.15em] uppercase border border-[#B76E79]/50 text-[#B76E79] hover:bg-[#B76E79] hover:text-white transition-all duration-300 rounded-full'
            >
              Shop Now
            </Link>
          </div>

          {/* Mobile Toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className='md:hidden text-white/70 hover:text-white transition-colors'
            aria-label='Toggle menu'
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className='fixed inset-0 z-40 bg-black/95 backdrop-blur-xl flex flex-col items-center justify-center gap-8'
          >
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className='text-2xl font-display tracking-[0.2em] uppercase text-white/80 hover:text-[#B76E79] transition-colors'
              >
                {link.label}
              </Link>
            ))}
            <Link
              href='/pre-order'
              onClick={() => setMobileOpen(false)}
              className='mt-4 px-8 py-3 text-sm tracking-[0.15em] uppercase border border-[#B76E79]/50 text-[#B76E79] hover:bg-[#B76E79] hover:text-white transition-all duration-300 rounded-full'
            >
              Shop Now
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
