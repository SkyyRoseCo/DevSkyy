'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import LuxuryProductViewer, { preloadModel } from '@/components/3d/LuxuryProductViewer';
import {
  pageTransition,
  staggerContainer,
  productCard,
  heroTitle,
  heroSubtitle,
  heroCTA,
  luxuryButton,
} from '@/lib/animations/luxury-transitions';

interface Product {
  id: string;
  name: string;
  collection: string;
  price: string;
  modelUrl: string;
  imageUrl: string;
  blurhash: string;
}

export default function LuxuryProductShowcase() {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [products] = useState<Product[]>([
    {
      id: '1',
      name: 'Midnight Rose Jacket',
      collection: 'Black Rose Collection',
      price: '$2,499',
      modelUrl: '/models/black-rose-jacket.glb',
      imageUrl: '/images/products/black-rose-jacket.webp',
      blurhash: 'L45#5m00~q00_3-;IU-;?b-;M{xu',
    },
    {
      id: '2',
      name: 'Signature Leather Dress',
      collection: 'Signature Collection',
      price: '$3,799',
      modelUrl: '/models/signature-dress.glb',
      imageUrl: '/images/products/signature-dress.webp',
      blurhash: 'L78N1b00~q00_3-;IU-;?b-;M{xu',
    },
    {
      id: '3',
      name: 'Love Hurts Ensemble',
      collection: 'Love Hurts Collection',
      price: '$4,299',
      modelUrl: '/models/love-hurts-ensemble.glb',
      imageUrl: '/images/products/love-hurts.webp',
      blurhash: 'L95#5m00~q00_3-;IU-;?b-;M{xu',
    },
  ]);

  // Preload 3D models
  useEffect(() => {
    products.forEach((product) => {
      preloadModel(product.modelUrl);
    });
  }, [products]);

  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageTransition}
      className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950"
    >
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Animated background gradient */}
        <motion.div
          animate={{
            backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute inset-0 bg-gradient-to-br from-[#B76E79]/20 via-transparent to-[#8B5A62]/20"
          style={{
            backgroundSize: '400% 400%',
          }}
        />

        <div className="relative z-10 text-center px-6">
          <motion.h1
            variants={heroTitle}
            className="text-7xl md:text-9xl font-light text-white mb-6 tracking-wider"
          >
            THE SKYY ROSE
            <br />
            <span className="text-[#B76E79]">COLLECTION</span>
          </motion.h1>

          <motion.p
            variants={heroSubtitle}
            className="text-xl md:text-2xl text-gray-300 mb-12 tracking-widest"
          >
            OAKLAND LUXURY STREETWEAR
          </motion.p>

          <motion.button
            variants={heroCTA}
            whileHover="hover"
            whileTap="tap"
            className="px-12 py-4 bg-[#B76E79] text-white rounded-full text-lg tracking-wider hover:bg-[#8B5A62] transition-colors"
            onClick={() => {
              document.getElementById('products')?.scrollIntoView({
                behavior: 'smooth',
              });
            }}
          >
            EXPLORE COLLECTIONS
          </motion.button>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2"
        >
          <div className="w-6 h-10 border-2 border-[#B76E79] rounded-full p-1">
            <motion.div
              animate={{ y: [0, 16, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-1 h-2 bg-[#B76E79] rounded-full mx-auto"
            />
          </div>
        </motion.div>
      </section>

      {/* Product Grid */}
      <section id="products" className="py-24 px-6 max-w-7xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          variants={staggerContainer}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {products.map((product) => (
            <motion.div
              key={product.id}
              variants={productCard}
              whileHover="hover"
              whileTap="tap"
              onClick={() => setSelectedProduct(product)}
              className="group cursor-pointer"
            >
              {/* Product Card */}
              <div className="relative aspect-[3/4] rounded-lg overflow-hidden bg-slate-900">
                {/* Blurhash placeholder */}
                <div
                  className="absolute inset-0"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(
                      `<svg xmlns="http://www.w3.org/2000/svg"><filter id="b"><feGaussianBlur stdDeviation="20"/></filter><rect width="100%" height="100%" fill="${product.blurhash}" filter="url(#b)"/></svg>`
                    )}")`,
                  }}
                />

                {/* Product image */}
                <motion.img
                  src={product.imageUrl}
                  alt={product.name}
                  className="absolute inset-0 w-full h-full object-cover"
                  initial={{ opacity: 0, scale: 1.1 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.8 }}
                />

                {/* Hover overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="absolute bottom-6 left-6 right-6">
                    <motion.button
                      variants={luxuryButton}
                      className="w-full py-3 bg-[#B76E79] text-white rounded-full tracking-wider"
                    >
                      VIEW IN 3D
                    </motion.button>
                  </div>
                </div>
              </div>

              {/* Product info */}
              <div className="mt-4 text-center">
                <h3 className="text-xl font-light text-white tracking-wider mb-1">
                  {product.name}
                </h3>
                <p className="text-[#B76E79] text-sm tracking-widest mb-2">
                  {product.collection}
                </p>
                <p className="text-white text-lg font-light">{product.price}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* 3D Viewer Modal */}
      {selectedProduct && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSelectedProduct(null)}
          className="fixed inset-0 bg-black/80 backdrop-blur-lg z-50 flex items-center justify-center p-6"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-6xl h-[80vh]"
          >
            <LuxuryProductViewer
              modelUrl={selectedProduct.modelUrl}
              productName={selectedProduct.name}
              environment="studio"
              enableAR={true}
              autoRotate={true}
              showEffects={true}
            />

            {/* Close button */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setSelectedProduct(null)}
              className="absolute top-6 right-6 w-12 h-12 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white transition-colors"
            >
              ✕
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  );
}
