'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import type { CollectionConfig } from '@/lib/collections';

interface CollectionHeroProps {
  collection: CollectionConfig;
  activeSceneIndex: number;
  onSceneChange: (index: number) => void;
}

export default function CollectionHero({
  collection,
  activeSceneIndex,
  onSceneChange,
}: CollectionHeroProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [showTitle, setShowTitle] = useState(true);
  const activeScene = collection.scenes[activeSceneIndex];
  const hasMultipleScenes = collection.scenes.length > 1;

  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 300);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!isLoaded) return;
    const timer = setTimeout(() => setShowTitle(false), 4000);
    return () => clearTimeout(timer);
  }, [isLoaded]);

  const handleScroll = useCallback(() => {
    const target = document.getElementById('collection-products');
    target?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  return (
    <section
      className="relative w-full h-screen overflow-hidden"
      style={{ backgroundColor: collection.bgColor }}
    >
      {/* Loading Screen */}
      <AnimatePresence>
        {!isLoaded && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
            className="absolute inset-0 z-50 flex items-center justify-center"
            style={{ backgroundColor: collection.bgColor }}
          >
            <motion.div
              animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="text-center"
            >
              <span
                className="text-5xl font-display tracking-[0.3em]"
                style={{ color: collection.accentColor }}
              >
                SR
              </span>
              <p className="mt-4 text-sm tracking-[0.2em] text-white/40 uppercase">
                Loading Experience
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scene Background Layers */}
      {collection.scenes.map((scene, idx) => (
        <div
          key={scene.id}
          className="absolute inset-0 transition-opacity duration-[600ms]"
          style={{ opacity: idx === activeSceneIndex ? 1 : 0 }}
        >
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{ backgroundImage: `url(${scene.backgroundImage})` }}
          />
          {/* Fallback gradient when image not loaded */}
          <div
            className="absolute inset-0"
            style={{
              background: `radial-gradient(ellipse at center, ${collection.bgColor}00 0%, ${collection.bgColor} 70%)`,
            }}
          />
        </div>
      ))}

      {/* Vignette Overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.6) 100%)',
        }}
      />

      {/* Film Grain Effect */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] mix-blend-overlay">
        <svg width="100%" height="100%">
          <filter id="grain">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.65"
              numOctaves="3"
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#grain)" />
        </svg>
      </div>

      {/* Collection Title Overlay */}
      <AnimatePresence>
        {showTitle && isLoaded && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="absolute inset-0 flex items-center justify-center z-10"
          >
            <div className="text-center">
              <motion.h1
                initial={{ opacity: 0, letterSpacing: '0.5em' }}
                animate={{ opacity: 1, letterSpacing: '0.2em' }}
                transition={{ duration: 1.2, delay: 0.3 }}
                className="text-6xl md:text-8xl font-display text-white mb-4"
              >
                {collection.name}
              </motion.h1>
              {collection.tagline && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.8, delay: 0.8 }}
                  className="text-lg md:text-xl tracking-[0.15em] uppercase"
                  style={{ color: collection.accentColor }}
                >
                  {collection.tagline}
                </motion.p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scene Navigation (multi-room) */}
      {hasMultipleScenes && isLoaded && (
        <>
          {/* Left/Right Arrows */}
          <button
            onClick={() =>
              onSceneChange(
                (activeSceneIndex - 1 + collection.scenes.length) %
                  collection.scenes.length
              )
            }
            className="absolute left-4 md:left-8 top-1/2 -translate-y-1/2 z-20 w-12 h-12 rounded-full bg-black/30 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/70 hover:text-white hover:bg-black/50 transition-all"
            aria-label="Previous room"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </button>
          <button
            onClick={() =>
              onSceneChange(
                (activeSceneIndex + 1) % collection.scenes.length
              )
            }
            className="absolute right-4 md:right-8 top-1/2 -translate-y-1/2 z-20 w-12 h-12 rounded-full bg-black/30 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/70 hover:text-white hover:bg-black/50 transition-all"
            aria-label="Next room"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M9 18l6-6-6-6" />
            </svg>
          </button>

          {/* Dots + Room Name */}
          <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-3">
            <div className="flex gap-2">
              {collection.scenes.map((scene, idx) => (
                <button
                  key={scene.id}
                  onClick={() => onSceneChange(idx)}
                  className="w-2 h-2 rounded-full transition-all duration-300"
                  style={{
                    backgroundColor:
                      idx === activeSceneIndex
                        ? collection.accentColor
                        : 'rgba(255,255,255,0.3)',
                    transform:
                      idx === activeSceneIndex ? 'scale(1.5)' : 'scale(1)',
                  }}
                  aria-label={`Go to ${scene.name}`}
                />
              ))}
            </div>
            <AnimatePresence mode="wait">
              <motion.span
                key={activeScene.id}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="text-xs tracking-[0.2em] uppercase text-white/50"
              >
                {activeScene.name}
              </motion.span>
            </AnimatePresence>
          </div>
        </>
      )}

      {/* Scroll Down Indicator */}
      {isLoaded && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          onClick={handleScroll}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-2 text-white/40 hover:text-white/70 transition-colors"
        >
          <span className="text-xs tracking-[0.2em] uppercase">Explore</span>
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          >
            <ChevronDown size={20} />
          </motion.div>
        </motion.button>
      )}
    </section>
  );
}
