'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Crown, ArrowRight, Gift } from 'lucide-react';
import Link from 'next/link';

const POPUP_DISMISSED_KEY = 'skyyrose-popup-dismissed';
const POPUP_DELAY_MS = 8000;

export default function IncentivePopup() {
  const [visible, setVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    // Don't show if already dismissed this session
    if (typeof window === 'undefined') return;
    const dismissed = sessionStorage.getItem(POPUP_DISMISSED_KEY);
    if (dismissed) return;

    const timer = setTimeout(() => {
      setVisible(true);
    }, POPUP_DELAY_MS);

    return () => clearTimeout(timer);
  }, []);

  function dismiss() {
    setVisible(false);
    sessionStorage.setItem(POPUP_DISMISSED_KEY, 'true');
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
    setTimeout(() => {
      dismiss();
    }, 3000);
  }

  return (
    <AnimatePresence>
      {visible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={dismiss}
            className='fixed inset-0 z-[60] bg-black/60 backdrop-blur-sm'
          />

          {/* Popup */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className='fixed inset-x-4 bottom-8 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 z-[61] max-w-lg w-full'
          >
            <div className='relative rounded-2xl border border-white/10 bg-[#0D0D0D] overflow-hidden'>
              {/* Accent gradient top bar */}
              <div className='h-1 bg-gradient-to-r from-[#C0C0C0] via-[#B76E79] to-[#DC143C]' />

              {/* Close button */}
              <button
                onClick={dismiss}
                className='absolute top-4 right-4 text-white/30 hover:text-white/70 transition-colors z-10'
                aria-label='Close'
              >
                <X size={20} />
              </button>

              <div className='p-8'>
                <AnimatePresence mode='wait'>
                  {submitted ? (
                    <motion.div
                      key='success'
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className='text-center py-8'
                    >
                      <motion.div
                        className='w-16 h-16 rounded-full bg-[#B76E79]/20 flex items-center justify-center mx-auto mb-4'
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      >
                        <Gift size={28} className='text-[#B76E79]' />
                      </motion.div>
                      <h3 className='text-2xl font-display text-white mb-2'>Welcome to the Inner Circle</h3>
                      <p className='text-white/40 text-sm'>Check your inbox for your exclusive 15% off code.</p>
                    </motion.div>
                  ) : (
                    <motion.div key='form' initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      {/* Icon */}
                      <div className='flex items-center justify-center mb-6'>
                        <div className='w-14 h-14 rounded-full bg-gradient-to-br from-[#B76E79]/20 to-[#D4AF37]/10 flex items-center justify-center'>
                          <Crown size={24} className='text-[#D4AF37]' />
                        </div>
                      </div>

                      <div className='text-center mb-6'>
                        <p className='text-[#D4AF37] text-xs tracking-[0.3em] uppercase mb-2'>Exclusive Offer</p>
                        <h3 className='text-2xl md:text-3xl font-display text-white mb-3'>Join the Inner Circle</h3>
                        <p className='text-white/40 text-sm leading-relaxed'>
                          Get <span className='text-[#B76E79] font-semibold'>15% off</span> your first pre-order plus
                          early access to new drops, behind-the-scenes content, and exclusive member-only pieces.
                        </p>
                      </div>

                      {/* Perks list */}
                      <div className='space-y-2 mb-6'>
                        {[
                          '15% off first pre-order',
                          'Early access to new collections',
                          'Exclusive member-only designs',
                          'Behind-the-scenes AI fashion content',
                        ].map(perk => (
                          <div key={perk} className='flex items-center gap-2 text-white/50 text-xs'>
                            <div className='w-4 h-4 rounded-full bg-[#B76E79]/10 flex items-center justify-center shrink-0'>
                              <div className='w-1.5 h-1.5 rounded-full bg-[#B76E79]' />
                            </div>
                            <span>{perk}</span>
                          </div>
                        ))}
                      </div>

                      {/* Email Form */}
                      <form onSubmit={handleSubmit} className='space-y-3'>
                        <input
                          type='email'
                          value={email}
                          onChange={e => setEmail(e.target.value)}
                          placeholder='your@email.com'
                          required
                          className='w-full px-5 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-[#B76E79]/50 transition-colors'
                        />
                        <button
                          type='submit'
                          className='w-full px-6 py-3 bg-[#B76E79] text-white text-sm tracking-[0.15em] uppercase rounded-xl hover:bg-[#D4A5B0] transition-all duration-300 flex items-center justify-center gap-2'
                        >
                          <span>Claim My 15% Off</span>
                          <ArrowRight size={16} />
                        </button>
                      </form>

                      <button
                        onClick={dismiss}
                        className='w-full text-center text-white/20 text-xs mt-4 hover:text-white/40 transition-colors'
                      >
                        No thanks, I&apos;ll pay full price
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
