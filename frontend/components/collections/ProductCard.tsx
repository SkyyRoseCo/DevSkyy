'use client';

import { useState, useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'motion/react';
import type { CollectionProduct } from '@/lib/collections';

interface ProductCardProps {
  product: CollectionProduct;
  accentColor: string;
  index: number;
  onQuickView: (product: CollectionProduct) => void;
}

export default function ProductCard({ product, accentColor, index, onQuickView }: ProductCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useSpring(useTransform(y, [-100, 100], [5, -5]), {
    stiffness: 300,
    damping: 30,
  });
  const rotateY = useSpring(useTransform(x, [-100, 100], [-5, 5]), {
    stiffness: 300,
    damping: 30,
  });

  function handleMouse(e: React.MouseEvent) {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    x.set(e.clientX - rect.left - rect.width / 2);
    y.set(e.clientY - rect.top - rect.height / 2);
  }

  function handleMouseLeave() {
    x.set(0);
    y.set(0);
    setIsHovered(false);
  }

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, delay: index * 0.1, ease: 'easeOut' }}
      style={{ rotateX, rotateY, transformPerspective: 1000 }}
      onMouseMove={handleMouse}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      className='group relative cursor-pointer'
      onClick={() => onQuickView(product)}
    >
      {/* Card */}
      <div className='relative overflow-hidden rounded-lg bg-white/[0.02] border border-white/5 backdrop-blur-sm transition-all duration-300 group-hover:border-white/10 group-hover:bg-white/[0.04]'>
        {/* Image */}
        <div className='relative aspect-[3/4] overflow-hidden bg-gradient-to-b from-white/[0.03] to-transparent'>
          {!imageError && product.image ? (
            // SOT paths are theme assets served by skyyrose.co, not the dashboard's
            // own public/ dir — next/image throws synchronously on an unconfigured
            // host before onError can ever fire, so a plain <img> with graceful
            // onError degrade is the established pattern here (see
            // app/admin/catalog/page.tsx's ImagePreview for the same tradeoff).
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={`/${product.image.replace(/^\/+/, '')}`}
              alt={product.name}
              className='absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105'
              onError={() => setImageError(true)}
            />
          ) : (
            <div className='absolute inset-0 flex items-center justify-center'>
              <div className='text-center'>
                <div
                  className='w-16 h-16 mx-auto mb-3 rounded-full flex items-center justify-center'
                  style={{ backgroundColor: `${accentColor}15` }}
                >
                  <span className='text-2xl font-display' style={{ color: accentColor }}>
                    {product.name.charAt(0)}
                  </span>
                </div>
                <p className='text-white/30 text-xs tracking-wider'>Preview</p>
              </div>
            </div>
          )}

          {/* Quick View Overlay */}
          <motion.div
            initial={false}
            animate={{ opacity: isHovered ? 1 : 0 }}
            transition={{ duration: 0.2 }}
            className='absolute inset-0 bg-black/40 flex items-center justify-center'
          >
            <span
              className='px-6 py-2.5 rounded-full text-sm tracking-[0.15em] uppercase border backdrop-blur-sm'
              style={{
                color: accentColor,
                borderColor: accentColor,
                backgroundColor: 'rgba(0,0,0,0.5)',
              }}
            >
              Quick View
            </span>
          </motion.div>
        </div>

        {/* Info */}
        <div className='p-4'>
          <h3 className='text-white text-sm font-display tracking-wide truncate'>{product.name}</h3>
          <div className='flex items-center justify-between mt-2'>
            <span className='text-sm tracking-wider' style={{ color: accentColor }}>
              ${product.price}
            </span>
            <span className='text-white/30 text-xs'>
              {product.sizes.length === 1 ? product.sizes[0] : `${product.sizes.length} sizes`}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
