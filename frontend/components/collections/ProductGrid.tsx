'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import ProductCard from './ProductCard';
import type { CollectionProduct, CollectionConfig } from '@/lib/collections';

interface ProductGridProps {
  collection: CollectionConfig;
  activeSceneIndex: number;
  onQuickView: (product: CollectionProduct) => void;
}

export default function ProductGrid({ collection, activeSceneIndex, onQuickView }: ProductGridProps) {
  const activeScene = collection.scenes[activeSceneIndex];

  const allProducts = useMemo(() => collection.scenes.flatMap(s => s.products), [collection.scenes]);

  return (
    <section id='collection-products' className='relative py-20 px-4 md:px-8'>
      {/* Section Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className='text-center mb-16'
      >
        <p className='text-xs tracking-[0.3em] uppercase mb-3' style={{ color: collection.accentColor }}>
          {activeScene.name}
        </p>
        <h2 className='text-3xl md:text-4xl font-display text-white mb-4'>The Collection</h2>
        <p className='text-white/40 max-w-lg mx-auto text-sm leading-relaxed'>{activeScene.description}</p>
      </motion.div>

      {/* Scene Tab Bar (for multi-scene collections) */}
      {collection.scenes.length > 1 && (
        <div className='flex justify-center gap-1 mb-12'>
          {collection.scenes.map((scene, idx) => (
            <span
              key={scene.id}
              className='px-3 py-1 text-xs tracking-wider rounded-full transition-all'
              style={{
                backgroundColor: idx === activeSceneIndex ? `${collection.accentColor}20` : 'transparent',
                color: idx === activeSceneIndex ? collection.accentColor : 'rgba(255,255,255,0.3)',
              }}
            >
              {scene.name}
            </span>
          ))}
        </div>
      )}

      {/* Product Grid */}
      <div className='max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8'>
        {activeScene.products.map((product, index) => (
          <ProductCard
            key={product.id}
            product={product}
            accentColor={collection.accentColor}
            index={index}
            onQuickView={onQuickView}
          />
        ))}
      </div>

      {/* Total count */}
      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className='text-center mt-12 text-white/20 text-xs tracking-[0.2em] uppercase'
      >
        {allProducts.length} pieces in {collection.name}
      </motion.p>
    </section>
  );
}
