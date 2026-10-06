'use client';

import { lazy, Suspense, useEffect, useState, useRef } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight, Play, Sparkles, ChevronDown } from 'lucide-react';
import type { CollectionConfig } from '@/lib/collections';

const RotatingLogoFallback = lazy(
  () => import('@/components/3d/RotatingLogoFallback')
);

interface Particle {
  x: string;
  y: string;
  animY: [string, string, string];
  duration: number;
  delay: number;
}

interface HomePageProps {
  collections: CollectionConfig[];
}

export default function HomePage({ collections }: HomePageProps) {
  const [heroLoaded, setHeroLoaded] = useState(false);
  const [particles, setParticles] = useState<Particle[]>([]);
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.5], [1, 1.1]);
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, 100]);

  useEffect(() => {
    const timer = setTimeout(() => setHeroLoaded(true), 200);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // Generate particle values client-side only to avoid prerender Math.random() error
    setParticles(
      Array.from({ length: 30 }).map(() => ({
        x: `${Math.random() * 100}%`,
        y: `${Math.random() * 100}%`,
        animY: [
          `${Math.random() * 100}%`,
          `${Math.random() * 100}%`,
          `${Math.random() * 100}%`,
        ] as [string, string, string],
        duration: 8 + Math.random() * 12,
        delay: Math.random() * 5,
      }))
    );
  }, []);

  return (
    <>
      {/* ======== HERO SECTION ======== */}
      <section ref={heroRef} className="relative h-screen overflow-hidden">
        <motion.div
          style={{ opacity: heroOpacity, scale: heroScale, y: heroY }}
          className="absolute inset-0"
        >
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#0A0A0A] via-[#1A0A0F] to-[#0D0D0D]" />

          {/* Animated particles — values generated client-side only */}
          <div className="absolute inset-0 overflow-hidden">
            {particles.map((p, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full bg-[#B76E79]/30"
                initial={{ x: p.x, y: p.y, opacity: 0 }}
                animate={{ y: p.animY, opacity: [0, 0.6, 0] }}
                transition={{ duration: p.duration, repeat: Infinity, delay: p.delay }}
              />
            ))}
          </div>

          {/* Film grain */}
          <div className="absolute inset-0 pointer-events-none opacity-[0.03] mix-blend-overlay">
            <svg width="100%" height="100%">
              <filter id="hero-grain">
                <feTurbulence
                  type="fractalNoise"
                  baseFrequency="0.65"
                  numOctaves="3"
                  stitchTiles="stitch"
                />
              </filter>
              <rect width="100%" height="100%" filter="url(#hero-grain)" />
            </svg>
          </div>
        </motion.div>

        {/* Hero Content */}
        <div className="relative z-10 h-full flex flex-col items-center justify-center px-4">
          <AnimatePresence>
            {heroLoaded && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1.2 }}
                className="text-center max-w-4xl mx-auto"
              >
                {/* Pre-title */}
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.8 }}
                  className="text-[#B76E79] text-xs tracking-[0.4em] uppercase mb-6"
                >
                  Luxury Fashion Reimagined
                </motion.p>

                {/* Main title */}
                <motion.h1
                  initial={{ opacity: 0, y: 40, letterSpacing: '0.5em' }}
                  animate={{ opacity: 1, y: 0, letterSpacing: '0.08em' }}
                  transition={{ delay: 0.5, duration: 1.2, ease: 'easeOut' }}
                  className="text-6xl md:text-8xl lg:text-9xl font-display text-white mb-6"
                >
                  SKYYROSE
                </motion.h1>

                {/* Decorative line */}
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ delay: 1.5, duration: 0.8 }}
                  className="w-24 h-px bg-gradient-to-r from-transparent via-[#B76E79] to-transparent mx-auto my-8"
                />

                {/* CTA Buttons */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.8, duration: 0.8 }}
                  className="flex flex-col sm:flex-row items-center gap-4 justify-center"
                >
                  <Link
                    href="/collections"
                    className="group px-8 py-3 bg-[#B76E79] text-white text-sm tracking-[0.15em] uppercase rounded-full hover:bg-[#D4A5B0] transition-all duration-300 flex items-center gap-2"
                  >
                    <span>Explore Collections</span>
                    <ArrowRight
                      size={16}
                      className="group-hover:translate-x-1 transition-transform"
                    />
                  </Link>
                  <Link
                    href="/pre-order"
                    className="px-8 py-3 border border-white/20 text-white/70 text-sm tracking-[0.15em] uppercase rounded-full hover:border-[#B76E79]/50 hover:text-[#B76E79] transition-all duration-300"
                  >
                    Pre-Order Now
                  </Link>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Scroll indicator */}
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.5 }}
            onClick={() => {
              document
                .getElementById('collections-preview')
                ?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/30 hover:text-white/60 transition-colors"
          >
            <span className="text-xs tracking-[0.2em] uppercase">Discover</span>
            <motion.div
              animate={{ y: [0, 6, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <ChevronDown size={20} />
            </motion.div>
          </motion.button>
        </div>
      </section>

      {/* ======== AI FASHION MODELS SECTION ======== */}
      <section className="py-32 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A] via-[#0D0808] to-[#0A0A0A]" />

        <div className="relative z-10 max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <p className="text-[#B76E79] text-xs tracking-[0.3em] uppercase mb-4 flex items-center justify-center gap-2">
              <Sparkles size={14} />
              AI-Crafted Fashion
              <Sparkles size={14} />
            </p>
            <h2 className="text-4xl md:text-6xl font-display text-white mb-6">
              The Future Wears SkyyRose
            </h2>
            <p className="text-white/40 max-w-xl mx-auto text-sm leading-relaxed">
              Every piece designed with AI precision and human artistry.
              Models wearing 100% replica products, styled in SkyyRose branding.
            </p>
          </motion.div>

          {/* AI Model Showcase - 3 cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {collections.map((collection, i) => (
              <motion.div
                key={collection.slug}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="group relative"
              >
                <Link href={`/collections/${collection.slug}`}>
                  <div className="relative aspect-[3/4] overflow-hidden rounded-2xl border border-white/5 hover:border-white/15 transition-all duration-700">
                    {/* Background gradient placeholder for AI model image */}
                    <div
                      className="absolute inset-0"
                      style={{
                        background: `linear-gradient(135deg, ${collection.bgColor}, ${collection.accentColor}15, ${collection.bgColor})`,
                      }}
                    />

                    {/* AI Model placeholder with collection initial */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <motion.div
                          className="w-32 h-32 rounded-full mx-auto mb-4 flex items-center justify-center"
                          style={{
                            background: `radial-gradient(circle, ${collection.accentColor}20, transparent)`,
                            border: `1px solid ${collection.accentColor}30`,
                          }}
                          animate={{ scale: [1, 1.05, 1] }}
                          transition={{
                            repeat: Infinity,
                            duration: 3,
                            delay: i * 0.5,
                          }}
                        >
                          <span
                            className="text-5xl font-display"
                            style={{ color: collection.accentColor }}
                          >
                            {collection.name.charAt(0)}
                          </span>
                        </motion.div>
                        <p className="text-white/20 text-xs tracking-[0.2em] uppercase">
                          AI Fashion Model
                        </p>
                      </div>
                    </div>

                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all duration-500 flex items-end">
                      <div className="p-6 translate-y-4 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-500">
                        <p
                          className="text-xs tracking-[0.2em] uppercase mb-1"
                          style={{ color: collection.accentColor }}
                        >
                          {collection.tagline}
                        </p>
                        <h3 className="text-xl font-display text-white">
                          {collection.name}
                        </h3>
                      </div>
                    </div>

                    {/* Shimmer effect */}
                    <div className="absolute inset-0 shimmer opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ======== COLLECTIONS PREVIEW WITH ROTATING LOGOS ======== */}
      <section id="collections-preview" className="py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <p className="text-[#B76E79] text-xs tracking-[0.3em] uppercase mb-4">
              Three Worlds Await
            </p>
            <h2 className="text-4xl md:text-6xl font-display text-white mb-6">
              The Collections
            </h2>
            <div className="w-16 h-px bg-[#B76E79] mx-auto" />
          </motion.div>

          {/* Collections with rotating 3D logos */}
          <div className="space-y-32">
            {collections.map((collection, i) => {
              const isEven = i % 2 === 0;
              const totalProducts = collection.scenes.reduce(
                (sum, s) => sum + s.products.length,
                0
              );

              return (
                <motion.div
                  key={collection.slug}
                  initial={{ opacity: 0, y: 60 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-100px' }}
                  transition={{ duration: 0.8 }}
                  className={`flex flex-col ${
                    isEven ? 'md:flex-row' : 'md:flex-row-reverse'
                  } items-center gap-12 md:gap-16`}
                >
                  {/* Rotating 3D Logo */}
                  <div className="flex-1 w-full">
                    <Suspense
                      fallback={
                        <div className="h-[200px] flex items-center justify-center">
                          <div className="w-8 h-8 border-2 border-[#B76E79] border-t-transparent rounded-full animate-spin" />
                        </div>
                      }
                    >
                      <RotatingLogoFallback
                        text={collection.name}
                        color={collection.accentColor}
                      />
                    </Suspense>

                    {/* Hero image placeholder */}
                    <div
                      className="relative aspect-[16/10] rounded-2xl overflow-hidden mt-4 border border-white/5"
                      style={{
                        background: `linear-gradient(135deg, ${collection.bgColor}, ${collection.accentColor}10)`,
                      }}
                    >
                      <Image
                        src={collection.heroImage}
                        alt={`${collection.name} collection`}
                        fill
                        sizes="(max-width: 768px) 100vw, 50vw"
                        className="object-cover opacity-80"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                    </div>
                  </div>

                  {/* Collection Info */}
                  <div className="flex-1 w-full">
                    <p
                      className="text-xs tracking-[0.3em] uppercase mb-3"
                      style={{ color: collection.accentColor }}
                    >
                      {collection.tagline}
                    </p>
                    <h3 className="text-3xl md:text-4xl font-display text-white mb-4">
                      {collection.name}
                    </h3>
                    <p className="text-white/40 text-sm leading-relaxed mb-6">
                      {collection.description}
                    </p>

                    {/* Stats */}
                    <div className="flex gap-8 mb-8">
                      <div>
                        <p className="text-2xl font-display text-white">
                          {totalProducts}
                        </p>
                        <p className="text-white/30 text-xs tracking-wider uppercase">
                          Pieces
                        </p>
                      </div>
                      <div>
                        <p className="text-2xl font-display text-white">
                          {collection.scenes.length}
                        </p>
                        <p className="text-white/30 text-xs tracking-wider uppercase">
                          {collection.scenes.length === 1 ? 'Scene' : 'Scenes'}
                        </p>
                      </div>
                      <div>
                        <p className="text-2xl font-display text-white">3D</p>
                        <p className="text-white/30 text-xs tracking-wider uppercase">
                          Experience
                        </p>
                      </div>
                    </div>

                    {/* CTA */}
                    <div className="flex gap-4">
                      <Link
                        href={`/collections/${collection.slug}`}
                        className="group px-6 py-3 text-sm tracking-[0.1em] uppercase rounded-full transition-all duration-300 flex items-center gap-2 border"
                        style={{
                          borderColor: `${collection.accentColor}50`,
                          color: collection.accentColor,
                        }}
                      >
                        <Play size={14} />
                        <span>Enter Experience</span>
                      </Link>
                      <Link
                        href="/pre-order"
                        className="px-6 py-3 text-sm tracking-[0.1em] uppercase text-white/50 hover:text-white/80 transition-colors border border-white/10 hover:border-white/20 rounded-full"
                      >
                        Pre-Order
                      </Link>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ======== PRE-ORDER CTA SECTION ======== */}
      <section className="py-32 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A] via-[#150A0D] to-[#0A0A0A]" />

        {/* Animated accent glow */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full"
          style={{
            background:
              'radial-gradient(circle, rgba(183,110,121,0.08) 0%, transparent 70%)',
          }}
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 6, repeat: Infinity }}
        />

        <div className="relative z-10 text-center max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <p className="text-[#B76E79] text-xs tracking-[0.3em] uppercase mb-4">
              Limited Edition
            </p>
            <h2 className="text-4xl md:text-6xl font-display text-white mb-6">
              Be First to Own
            </h2>
            <p className="text-white/40 text-sm leading-relaxed mb-10 max-w-xl mx-auto">
              Secure your pieces before they sell out. Early adopters receive
              exclusive packaging, a signed certificate of authenticity, and
              lifetime membership to the SkyyRose Inner Circle.
            </p>

            <Link
              href="/pre-order"
              className="inline-flex items-center gap-3 px-10 py-4 bg-[#B76E79] text-white text-sm tracking-[0.2em] uppercase rounded-full hover:bg-[#D4A5B0] transition-all duration-300 glow-rose"
            >
              <span>Pre-Order All Collections</span>
              <ArrowRight size={18} />
            </Link>

            <p className="text-white/20 text-xs tracking-wider mt-6">
              Free shipping worldwide &middot; 30-day returns &middot; Secure
              checkout
            </p>
          </motion.div>
        </div>
      </section>

      {/* ======== FOOTER ======== */}
      <footer className="border-t border-white/5 py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            {/* Brand */}
            <div className="md:col-span-2">
              <h3 className="text-2xl font-display tracking-[0.15em] text-white mb-4">
                SKYYROSE
              </h3>
              <p className="text-white/30 text-sm leading-relaxed max-w-sm">
                Three immersive worlds of fashion,
                crafted with AI precision and human artistry.
              </p>
            </div>

            {/* Collections */}
            <div>
              <h4 className="text-white/60 text-xs tracking-[0.2em] uppercase mb-4">
                Collections
              </h4>
              <div className="space-y-2">
                {collections.map((c) => (
                  <Link
                    key={c.slug}
                    href={`/collections/${c.slug}`}
                    className="block text-white/30 text-sm hover:text-[#B76E79] transition-colors"
                  >
                    {c.name}
                  </Link>
                ))}
              </div>
            </div>

            {/* Links */}
            <div>
              <h4 className="text-white/60 text-xs tracking-[0.2em] uppercase mb-4">
                Company
              </h4>
              <div className="space-y-2">
                <Link
                  href="/pre-order"
                  className="block text-white/30 text-sm hover:text-[#B76E79] transition-colors"
                >
                  Pre-Order
                </Link>
                <span className="block text-white/30 text-sm">About</span>
                <span className="block text-white/30 text-sm">Contact</span>
              </div>
            </div>
          </div>

          {/* Bottom */}
          <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-white/15 text-xs tracking-wider">
              &copy; 2026 SkyyRose LLC. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
