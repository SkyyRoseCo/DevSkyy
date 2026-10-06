'use client';

import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import CollectionHero from '@/components/collections/CollectionHero';
import ProductGrid from '@/components/collections/ProductGrid';
import ProductQuickView from '@/components/collections/ProductQuickView';
import CollectionTabBar from '@/components/collections/CollectionTabBar';
import type { CollectionConfig, CollectionProduct } from '@/lib/collections';

// Lazy load the 3D scene for performance
const CollectionScene = lazy(
  () => import('@/components/collections/CollectionScene')
);

interface CollectionExperienceProps {
  collection: CollectionConfig;
}

export default function CollectionExperience({
  collection,
}: CollectionExperienceProps) {
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [quickViewProduct, setQuickViewProduct] =
    useState<CollectionProduct | null>(null);

  // Keyboard navigation for scenes
  useEffect(() => {
    if (collection.scenes.length <= 1) return;
    if (quickViewProduct) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'ArrowLeft') {
        setActiveSceneIndex((prev) =>
          prev === 0 ? collection.scenes.length - 1 : prev - 1
        );
      } else if (e.key === 'ArrowRight') {
        setActiveSceneIndex((prev) =>
          prev === collection.scenes.length - 1 ? 0 : prev + 1
        );
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [collection.scenes.length, quickViewProduct]);

  // Swipe support for mobile
  useEffect(() => {
    if (collection.scenes.length <= 1) return;
    let startX = 0;
    let startY = 0;

    function handleTouchStart(e: TouchEvent) {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    }

    function handleTouchEnd(e: TouchEvent) {
      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const diffX = endX - startX;
      const diffY = endY - startY;

      // Only trigger on horizontal swipes > 50px with no excessive vertical movement
      if (Math.abs(diffX) < 50 || Math.abs(diffY) > Math.abs(diffX)) return;

      if (diffX < 0) {
        setActiveSceneIndex((prev) =>
          prev === collection.scenes.length - 1 ? 0 : prev + 1
        );
      } else {
        setActiveSceneIndex((prev) =>
          prev === 0 ? collection.scenes.length - 1 : prev - 1
        );
      }
    }

    window.addEventListener('touchstart', handleTouchStart, { passive: true });
    window.addEventListener('touchend', handleTouchEnd, { passive: true });
    return () => {
      window.removeEventListener('touchstart', handleTouchStart);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, [collection.scenes.length]);

  const handleQuickView = useCallback((product: CollectionProduct) => {
    setQuickViewProduct(product);
  }, []);

  const handleCloseQuickView = useCallback(() => {
    setQuickViewProduct(null);
  }, []);

  return (
    <div
      className="relative pb-20"
      style={
        {
          '--collection-accent': collection.accentColor,
          '--collection-bg': collection.bgColor,
        } as React.CSSProperties
      }
    >
      {/* Back Navigation */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5 }}
        className="fixed top-4 left-4 z-30"
      >
        <Link
          href="/collections"
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-black/30 backdrop-blur-sm border border-white/10 text-white/60 hover:text-white hover:bg-black/50 transition-all text-sm"
        >
          <ArrowLeft size={16} />
          <span className="hidden md:inline tracking-wider">Collections</span>
        </Link>
      </motion.div>

      {/* Immersive Hero with Scene Navigation */}
      <CollectionHero
        collection={collection}
        activeSceneIndex={activeSceneIndex}
        onSceneChange={setActiveSceneIndex}
      />

      {/* Collection Description */}
      <section className="py-16 px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto"
        >
          <p
            className="text-xs tracking-[0.3em] uppercase mb-4"
            style={{ color: collection.accentColor }}
          >
            {collection.tagline}
          </p>
          <h2 className="text-3xl md:text-4xl font-display text-white mb-6">
            {collection.name}
          </h2>
          <p className="text-white/40 text-sm leading-relaxed">
            {collection.description}
          </p>
          <div
            className="w-12 h-px mx-auto mt-8"
            style={{ backgroundColor: collection.accentColor }}
          />
        </motion.div>
      </section>

      {/* 3D Experience Section */}
      <section className="px-4 md:px-8 max-w-5xl mx-auto mb-16">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
        >
          <Suspense
            fallback={
              <div
                className="w-full h-[500px] md:h-[600px] rounded-lg flex items-center justify-center"
                style={{ backgroundColor: collection.bgColor }}
              >
                <div className="text-center">
                  <div className="w-12 h-12 border-2 border-[#B76E79] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-white/30 text-xs tracking-wider">
                    Loading 3D Experience
                  </p>
                </div>
              </div>
            }
          >
            <CollectionScene collection={collection} />
          </Suspense>
        </motion.div>
      </section>

      {/* Product Grid */}
      <ProductGrid
        collection={collection}
        activeSceneIndex={activeSceneIndex}
        onQuickView={handleQuickView}
      />

      {/* Quick View Modal */}
      <ProductQuickView
        product={quickViewProduct}
        accentColor={collection.accentColor}
        onClose={handleCloseQuickView}
      />

      {/* Collection Footer */}
      <footer className="border-t border-white/5 py-12 px-4 text-center pb-24">
        <p className="text-white/20 text-xs tracking-[0.2em] uppercase">
          {collection.name} Collection
        </p>
        <p className="text-white/10 text-xs mt-2 tracking-wider">
          SkyyRose
        </p>
      </footer>

      {/* Tab Bar */}
      <CollectionTabBar />
    </div>
  );
}
