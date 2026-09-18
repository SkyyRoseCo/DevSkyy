'use client';

import { lazy, Suspense, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight, Play, Sparkles } from 'lucide-react';
import type { CollectionConfig } from '@/lib/collections';
import CollectionTabBar from '@/components/collections/CollectionTabBar';

const RotatingLogoFallback = lazy(
  () => import('@/components/3d/RotatingLogoFallback')
);

export default function CollectionsLanding({ collections }: { collections: CollectionConfig[] }) {

  return (
    <>
      {/* Header with spacing for fixed nav */}
      <header className="relative pt-32 pb-16 px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <p className="text-[#B76E79] text-xs tracking-[0.4em] uppercase mb-4 flex items-center justify-center gap-2">
            <Sparkles size={12} />
            Three Immersive Worlds
            <Sparkles size={12} />
          </p>
          <h1 className="text-5xl md:text-7xl font-display text-white mb-6">
            Collections
          </h1>
          <p className="text-white/40 max-w-lg mx-auto text-sm leading-relaxed">
            Each collection is a portal into a different universe of luxury
            fashion. Explore AI-crafted designs, immersive 3D scenes, and
            exclusive pieces waiting to be yours.
          </p>
        </motion.div>

        {/* Decorative gradient line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="w-24 h-px bg-gradient-to-r from-transparent via-[#B76E79] to-transparent mx-auto mt-8"
        />
      </header>

      {/* Full-Width Collection Showcases */}
      <section className="px-4 md:px-8 pb-28 max-w-7xl mx-auto space-y-16">
        {collections.map((collection, index) => {
          const totalProducts = collection.scenes.reduce(
            (sum, s) => sum + s.products.length,
            0
          );

          return (
            <motion.div
              key={collection.slug}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.7, delay: index * 0.1 }}
            >
              <Link
                href={`/collections/${collection.slug}`}
                className="group block relative overflow-hidden rounded-2xl border border-white/5 hover:border-white/15 transition-all duration-700"
              >
                {/* Large panoramic hero card */}
                <div className="relative aspect-[21/9] md:aspect-[3/1] overflow-hidden">
                  <CollectionCardImage
                    heroImage={collection.heroImage}
                    heroImageAvailable={collection.heroImageAvailable}
                    name={collection.name}
                    accentColor={collection.accentColor}
                    bgColor={collection.bgColor}
                  />

                  {/* Gradient overlays */}
                  <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

                  {/* Hover shimmer */}
                  <div className="absolute inset-0 shimmer opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

                  {/* Top accent line */}
                  <motion.div
                    className="absolute top-0 left-0 right-0 h-[2px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{ backgroundColor: collection.accentColor }}
                  />
                </div>

                {/* Content overlay */}
                <div className="absolute inset-0 flex items-end p-6 md:p-12">
                  <div className="flex-1">
                    <p
                      className="text-xs tracking-[0.3em] uppercase mb-2"
                      style={{ color: collection.accentColor }}
                    >
                      {collection.tagline}
                    </p>
                    <h2 className="text-3xl md:text-5xl font-display text-white mb-3 group-hover:tracking-wider transition-all duration-700">
                      {collection.name}
                    </h2>
                    <p className="text-white/40 text-sm leading-relaxed max-w-lg mb-4 hidden md:block">
                      {collection.description}
                    </p>

                    {/* Stats row */}
                    <div className="flex gap-4 text-white/25 text-xs tracking-wider">
                      <span>{totalProducts} pieces</span>
                      <span>&middot;</span>
                      <span>
                        {collection.scenes.length}{' '}
                        {collection.scenes.length === 1 ? 'scene' : 'scenes'}
                      </span>
                      <span>&middot;</span>
                      <span>3D Experience</span>
                    </div>

                    {/* Hover CTA */}
                    <div
                      className="mt-6 inline-flex items-center gap-2 text-sm tracking-[0.1em] opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500"
                      style={{ color: collection.accentColor }}
                    >
                      <Play size={14} />
                      <span>Enter Experience</span>
                      <ArrowRight
                        size={14}
                        className="group-hover:translate-x-1 transition-transform"
                      />
                    </div>
                  </div>

                  {/* Rotating logo initial on the right */}
                  <div className="hidden lg:block w-[250px] shrink-0">
                    <Suspense fallback={null}>
                      <RotatingLogoFallback
                        text={collection.name.charAt(0)}
                        color={collection.accentColor}
                      />
                    </Suspense>
                  </div>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </section>

      {/* Pre-order CTA */}
      <section className="py-20 px-4 text-center border-t border-white/5">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="text-[#B76E79] text-xs tracking-[0.3em] uppercase mb-4">
            Limited Availability
          </p>
          <h2 className="text-3xl md:text-4xl font-display text-white mb-4">
            Ready to Own the Future?
          </h2>
          <p className="text-white/30 text-sm mb-8 max-w-md mx-auto">
            Pre-order from all three collections and join the SkyyRose Inner
            Circle.
          </p>
          <Link
            href="/pre-order"
            className="inline-flex items-center gap-2 px-8 py-3 bg-[#B76E79] text-white text-sm tracking-[0.15em] uppercase rounded-full hover:bg-[#D4A5B0] transition-all duration-300 glow-rose"
          >
            <span>Pre-Order Now</span>
            <ArrowRight size={16} />
          </Link>
        </motion.div>
      </section>

      {/* Brand Footer */}
      <footer className="border-t border-white/5 py-12 px-4 text-center pb-24">
        <p className="text-white/20 text-xs tracking-[0.2em] uppercase">
          Luxury Grows from Concrete.
        </p>
        <p className="text-white/10 text-xs mt-2 tracking-wider">
          SkyyRose LLC &copy; 2026
        </p>
      </footer>

      <CollectionTabBar />
    </>
  );
}

function CollectionCardImage({
  heroImage,
  heroImageAvailable,
  name,
  accentColor,
  bgColor,
}: {
  heroImage: string;
  heroImageAvailable?: boolean;
  name: string;
  accentColor: string;
  bgColor: string;
}) {
  const [imageError, setImageError] = useState(false);

  if (heroImageAvailable === false || imageError) {
    return (
      <div
        className="absolute inset-0 flex items-center justify-center"
        style={{
          background: `linear-gradient(135deg, ${bgColor}, ${accentColor}10, ${bgColor})`,
        }}
      >
        <span
          className="text-8xl font-display opacity-20"
          style={{ color: accentColor }}
        >
          {name}
        </span>
      </div>
    );
  }

  return (
    <Image
      src={heroImage}
      alt={`${name} collection`}
      fill
      sizes="(max-width: 768px) 100vw, 90vw"
      className="object-cover transition-transform duration-1000 group-hover:scale-105"
      onError={() => setImageError(true)}
    />
  );
}
