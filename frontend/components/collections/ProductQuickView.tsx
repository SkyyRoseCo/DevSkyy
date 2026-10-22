'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X } from 'lucide-react';
import type { CollectionProduct } from '@/lib/collections';
import { useCartStore } from '@/lib/stores/cart-store';

interface ProductQuickViewProps {
  product: CollectionProduct | null;
  accentColor: string;
  onClose: () => void;
}

export default function ProductQuickView({ product, accentColor, onClose }: ProductQuickViewProps) {
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [imageError, setImageError] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  // Focus trap
  useEffect(() => {
    if (!product) return;
    previousFocus.current = document.activeElement as HTMLElement;
    closeButtonRef.current?.focus();
    setSelectedSize(null);
    setImageError(false);

    return () => {
      previousFocus.current?.focus();
    };
  }, [product]);

  // Escape key
  useEffect(() => {
    if (!product) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab' && panelRef.current) {
        const focusable = panelRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [product, onClose]);

  const addItem = useCartStore(state => state.addItem);

  const handleAddToCart = useCallback(() => {
    if (!product || !selectedSize) return;
    addItem({
      productId: product.id,
      productName: product.name,
      collection: '',
      size: selectedSize,
      price: product.price,
    });
    onClose();
  }, [product, selectedSize, addItem, onClose]);

  return (
    <AnimatePresence>
      {product && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className='fixed inset-0 z-50 bg-black/60 backdrop-blur-sm'
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            ref={panelRef}
            role='dialog'
            aria-modal='true'
            aria-label={`${product.name} details`}
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className='fixed bottom-0 left-0 right-0 z-50 max-h-[85vh] overflow-y-auto rounded-t-2xl'
            style={{
              background: 'linear-gradient(180deg, rgba(20,20,20,0.98) 0%, rgba(10,10,10,0.99) 100%)',
              backdropFilter: 'blur(24px) saturate(1.4)',
            }}
          >
            {/* Handle bar */}
            <div className='sticky top-0 z-10 flex justify-center pt-3 pb-2 bg-inherit'>
              <div className='w-10 h-1 rounded-full bg-white/20' />
            </div>

            {/* Close button */}
            <button
              ref={closeButtonRef}
              onClick={onClose}
              className='absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10 transition-all'
              aria-label='Close product details'
            >
              <X size={18} />
            </button>

            <div className='px-6 pb-8 pt-2'>
              <div className='flex flex-col md:flex-row gap-8'>
                {/* Image */}
                <div className='relative w-full md:w-1/2 aspect-[3/4] rounded-lg overflow-hidden bg-white/[0.02]'>
                  {!imageError && product.image ? (
                    // See ProductCard.tsx: SOT paths are theme assets served by
                    // skyyrose.co, not the dashboard's public/ dir — next/image
                    // throws synchronously on an unconfigured host before onError
                    // can fire, so a plain <img> degrades gracefully instead.
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={`/${product.image.replace(/^\/+/, '')}`}
                      alt={product.name}
                      className='absolute inset-0 h-full w-full object-cover'
                      onError={() => setImageError(true)}
                    />
                  ) : (
                    <div className='absolute inset-0 flex items-center justify-center'>
                      <div
                        className='w-24 h-24 rounded-full flex items-center justify-center'
                        style={{ backgroundColor: `${accentColor}15` }}
                      >
                        <span className='text-4xl font-display' style={{ color: accentColor }}>
                          {product.name.charAt(0)}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className='flex-1 flex flex-col justify-between'>
                  <div>
                    <h2 className='text-2xl md:text-3xl font-display text-white tracking-wide'>{product.name}</h2>
                    <p className='text-xl mt-2 tracking-wider' style={{ color: accentColor }}>
                      ${product.price}
                    </p>

                    {product.description && (
                      <p className='text-white/50 text-sm mt-4 leading-relaxed'>{product.description}</p>
                    )}

                    {/* Sizes */}
                    <div className='mt-8'>
                      <p className='text-white/40 text-xs tracking-[0.15em] uppercase mb-3'>Size</p>
                      <div className='flex flex-wrap gap-2'>
                        {product.sizes.map(size => (
                          <button
                            key={size}
                            onClick={() => setSelectedSize(size)}
                            className='min-w-[48px] h-10 px-3 rounded-md text-sm tracking-wider border transition-all'
                            style={{
                              borderColor: selectedSize === size ? accentColor : 'rgba(255,255,255,0.1)',
                              backgroundColor: selectedSize === size ? `${accentColor}15` : 'transparent',
                              color: selectedSize === size ? accentColor : 'rgba(255,255,255,0.6)',
                            }}
                          >
                            {size}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className='flex gap-3 mt-8'>
                    <button
                      onClick={handleAddToCart}
                      disabled={!selectedSize}
                      className='flex-1 h-12 rounded-lg text-sm tracking-[0.15em] uppercase font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed'
                      style={{
                        backgroundColor: selectedSize ? accentColor : 'transparent',
                        color: selectedSize ? '#000' : 'rgba(255,255,255,0.3)',
                        border: selectedSize ? 'none' : '1px solid rgba(255,255,255,0.1)',
                      }}
                    >
                      Add to Cart
                    </button>
                    <button className='h-12 px-6 rounded-lg text-sm tracking-[0.15em] uppercase border border-white/10 text-white/60 hover:text-white hover:border-white/20 transition-all'>
                      Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
