'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  ArrowRight,
  Check,
  Shield,
  Truck,
  RotateCcw,
  Star,
  Package,
  Crown,
  Sparkles,
  ShoppingBag,
} from 'lucide-react';
import type { CollectionConfig } from '@/lib/collections';
import { useCartStore, type CartItem } from '@/lib/stores/cart-store';

interface PreOrderPageProps {
  collections: CollectionConfig[];
}

export default function PreOrderPage({ collections }: PreOrderPageProps) {
  const [activeCollection, setActiveCollection] = useState<string>('all');
  const { items: cart, addItem, removeItem: removeCartItem, subtotal, itemCount } = useCartStore();
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const filteredCollections =
    activeCollection === 'all'
      ? collections
      : collections.filter((c) => c.slug === activeCollection);

  const totalCartValue = subtotal();

  function addToCart(
    productId: string,
    productName: string,
    collection: string,
    price: number,
    size: string
  ) {
    addItem({ productId, productName, collection, size, price });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || cart.length === 0) return;
    setSubmitted(true);
  }

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Banner */}
      <section className="relative py-24 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#150A0D] via-[#0A0A0A] to-[#0A0A0A]" />

        {/* Pulsing accent */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full"
          style={{
            background:
              'radial-gradient(circle, rgba(183,110,121,0.1) 0%, transparent 70%)',
          }}
          animate={{ scale: [1, 1.3, 1] }}
          transition={{ duration: 4, repeat: Infinity }}
        />

        <div className="relative z-10 text-center max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <Crown size={16} className="text-[#D4AF37]" />
              <p className="text-[#D4AF37] text-xs tracking-[0.3em] uppercase">
                Exclusive Pre-Order
              </p>
              <Crown size={16} className="text-[#D4AF37]" />
            </div>
            <h1 className="text-5xl md:text-7xl font-display text-white mb-6">
              Secure Your Pieces
            </h1>
            <p className="text-white/40 text-sm leading-relaxed max-w-xl mx-auto">
              Three legendary collections. Limited availability. Early adopters
              receive exclusive packaging, a signed certificate of authenticity,
              and lifetime membership to the SkyyRose Inner Circle.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Perks Bar */}
      <section className="border-y border-white/5 py-8 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: Truck, label: 'Free Worldwide Shipping' },
            { icon: RotateCcw, label: '30-Day Returns' },
            { icon: Shield, label: 'Secure Checkout' },
            { icon: Package, label: 'Exclusive Packaging' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-3">
              <Icon size={18} className="text-[#B76E79] shrink-0" />
              <span className="text-white/50 text-xs tracking-wider">
                {label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Collection Filter */}
      <section className="py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center gap-3 flex-wrap mb-12">
            <button
              onClick={() => setActiveCollection('all')}
              className={`px-5 py-2 text-xs tracking-[0.15em] uppercase rounded-full border transition-all duration-300 ${
                activeCollection === 'all'
                  ? 'bg-[#B76E79] text-white border-[#B76E79]'
                  : 'border-white/10 text-white/40 hover:border-white/20 hover:text-white/60'
              }`}
            >
              All Collections
            </button>
            {collections.map((c) => (
              <button
                key={c.slug}
                onClick={() => setActiveCollection(c.slug)}
                className={`px-5 py-2 text-xs tracking-[0.15em] uppercase rounded-full border transition-all duration-300 ${
                  activeCollection === c.slug
                    ? 'text-white'
                    : 'border-white/10 text-white/40 hover:border-white/20 hover:text-white/60'
                }`}
                style={
                  activeCollection === c.slug
                    ? {
                        backgroundColor: c.accentColor,
                        borderColor: c.accentColor,
                      }
                    : undefined
                }
              >
                {c.name}
              </button>
            ))}
          </div>

          {/* Collections Grid */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeCollection}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-24"
            >
              {filteredCollections.map((collection) => (
                <CollectionSection
                  key={collection.slug}
                  collection={collection}
                  cart={cart}
                  onAddToCart={addToCart}
                />
              ))}
            </motion.div>
          </AnimatePresence>
        </div>
      </section>

      {/* Cart / Checkout Section */}
      <section className="py-16 px-4 border-t border-white/5">
        <div className="max-w-3xl mx-auto">
          <AnimatePresence mode="wait">
            {submitted ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-16"
              >
                <motion.div
                  className="w-20 h-20 rounded-full bg-[#B76E79]/20 flex items-center justify-center mx-auto mb-6"
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Check size={32} className="text-[#B76E79]" />
                </motion.div>
                <h3 className="text-3xl font-display text-white mb-4">
                  You&apos;re on the List
                </h3>
                <p className="text-white/40 text-sm leading-relaxed max-w-md mx-auto mb-2">
                  We&apos;ll email you at{' '}
                  <span className="text-[#B76E79]">{email}</span> when your
                  pre-order is ready to ship. Welcome to the Inner Circle.
                </p>
                <p className="text-white/20 text-xs tracking-wider mt-4">
                  {cart.length} items &middot; $
                  {totalCartValue.toLocaleString()} total
                </p>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                <div className="text-center mb-8">
                  <h3 className="text-3xl font-display text-white mb-2">
                    Your Pre-Order
                  </h3>
                  <p className="text-white/30 text-xs tracking-wider">
                    {cart.length === 0
                      ? 'Select items above to begin'
                      : `${cart.length} item${cart.length !== 1 ? 's' : ''} selected`}
                  </p>
                </div>

                {cart.length > 0 && (
                  <div className="space-y-3 mb-8">
                    {cart.map((item) => (
                      <motion.div
                        key={`${item.productId}-${item.size}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-white/[0.02]"
                      >
                        <div>
                          <p className="text-white text-sm">{item.productName}</p>
                          <p className="text-white/30 text-xs">
                            {item.collection} &middot; Size: {item.size}
                            {item.quantity > 1 && ` &middot; Qty: ${item.quantity}`}
                          </p>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-white/60 text-sm">
                            ${(item.price * item.quantity).toLocaleString()}
                          </span>
                          <button
                            onClick={() => removeCartItem(item.productId, item.size)}
                            className="text-white/20 hover:text-red-400 transition-colors text-xs"
                          >
                            Remove
                          </button>
                        </div>
                      </motion.div>
                    ))}

                    <div className="flex justify-between items-center pt-4 border-t border-white/5">
                      <span className="text-white/40 text-sm">Total</span>
                      <span className="text-white text-xl font-display">
                        ${totalCartValue.toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}

                {/* Email form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email to pre-order"
                      required
                      className="w-full px-6 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-[#B76E79]/50 transition-colors"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={cart.length === 0}
                    className="w-full px-8 py-4 bg-[#B76E79] text-white text-sm tracking-[0.15em] uppercase rounded-xl hover:bg-[#D4A5B0] transition-all duration-300 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-2 glow-rose"
                  >
                    <span>
                      {cart.length === 0
                        ? 'Select Items to Continue'
                        : `Pre-Order ${cart.length} Item${cart.length !== 1 ? 's' : ''} — $${totalCartValue.toLocaleString()}`}
                    </span>
                    {cart.length > 0 && <ArrowRight size={16} />}
                  </button>
                </form>

                {/* Proceed to Checkout */}
                {cart.length > 0 && (
                  <Link
                    href="/checkout"
                    className="w-full mt-4 px-8 py-4 bg-white/[0.05] border border-white/10 text-white text-sm tracking-[0.15em] uppercase rounded-xl hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300 flex items-center justify-center gap-2"
                  >
                    <ShoppingBag size={16} />
                    <span>Proceed to Checkout</span>
                    <ArrowRight size={16} />
                  </Link>
                )}

                {/* Trust signals */}
                <div className="flex items-center justify-center gap-6 mt-6">
                  <div className="flex items-center gap-1 text-white/20 text-xs">
                    <Shield size={12} />
                    <span>SSL Encrypted</span>
                  </div>
                  <div className="flex items-center gap-1 text-white/20 text-xs">
                    <Star size={12} />
                    <span>Inner Circle Access</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-4 text-center pb-24">
        <p className="text-white/10 text-xs mt-2 tracking-wider">
          SkyyRose LLC &copy; 2026
        </p>
      </footer>
    </div>
  );
}

function CollectionSection({
  collection,
  cart,
  onAddToCart,
}: {
  collection: CollectionConfig;
  cart: CartItem[];
  onAddToCart: (
    productId: string,
    productName: string,
    collection: string,
    price: number,
    size: string
  ) => void;
}) {
  return (
    <div>
      {/* Collection Header */}
      <div className="flex items-center gap-4 mb-8">
        <div
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: collection.accentColor }}
        />
        <div>
          <p
            className="text-xs tracking-[0.2em] uppercase"
            style={{ color: collection.accentColor }}
          >
            {collection.tagline}
          </p>
          <h2 className="text-2xl md:text-3xl font-display text-white">
            {collection.name} Collection
          </h2>
        </div>
        <Link
          href={`/collections/${collection.slug}`}
          className="ml-auto text-xs tracking-wider text-white/30 hover:text-white/60 transition-colors hidden md:block"
        >
          View Full Experience &rarr;
        </Link>
      </div>

      {/* Products */}
      {collection.scenes.map((scene) => (
        <div key={scene.id} className="mb-8">
          {collection.scenes.length > 1 && (
            <p className="text-white/20 text-xs tracking-[0.15em] uppercase mb-4 pl-6 border-l border-white/5">
              {scene.name}
            </p>
          )}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {scene.products.map((product) => {
              const inCart = cart.some(
                (item) => item.productId === product.id
              );
              return (
                <ProductPreOrderCard
                  key={product.id}
                  id={product.id}
                  name={product.name}
                  price={product.price}
                  image={product.image}
                  sizes={product.sizes}
                  accentColor={collection.accentColor}
                  collectionName={collection.name}
                  inCart={inCart}
                  onAddToCart={onAddToCart}
                />
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function ProductPreOrderCard({
  id,
  name,
  price,
  image,
  sizes,
  accentColor,
  collectionName,
  inCart,
  onAddToCart,
}: {
  id: string;
  name: string;
  price: number;
  image: string;
  sizes: string[];
  accentColor: string;
  collectionName: string;
  inCart: boolean;
  onAddToCart: (
    productId: string,
    productName: string,
    collection: string,
    price: number,
    size: string
  ) => void;
}) {
  const [selectedSize, setSelectedSize] = useState('');
  const [imageError, setImageError] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className={`rounded-xl border overflow-hidden transition-all duration-300 ${
        inCart
          ? 'border-[#B76E79]/30 bg-[#B76E79]/5'
          : 'border-white/5 bg-white/[0.02] hover:border-white/10'
      }`}
    >
      {/* Image */}
      <div className="relative aspect-square overflow-hidden">
        {!imageError && image ? (
          // SOT paths are theme assets served by skyyrose.co, not the dashboard's
          // public/ dir — next/image throws synchronously on an unconfigured host
          // before onError can fire, so a plain <img> degrades gracefully instead.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`/${image.replace(/^\/+/, '')}`}
            alt={name}
            className="absolute inset-0 h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          <div
            className="absolute inset-0 flex items-center justify-center"
            style={{
              background: `linear-gradient(135deg, ${accentColor}10, transparent)`,
            }}
          >
            <span
              className="text-3xl font-display"
              style={{ color: accentColor }}
            >
              {name.charAt(0)}
            </span>
          </div>
        )}
        {inCart && (
          <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-[#B76E79] flex items-center justify-center">
            <Check size={14} className="text-white" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h4 className="text-white text-sm font-display mb-1 line-clamp-1">
          {name}
        </h4>
        <p
          className="text-lg font-display mb-3"
          style={{ color: accentColor }}
        >
          ${price}
        </p>

        {/* Size selector */}
        <div className="flex flex-wrap gap-1 mb-3">
          {sizes.map((size) => (
            <button
              key={size}
              onClick={() => setSelectedSize(size)}
              className={`px-2 py-1 text-[10px] tracking-wider rounded border transition-all ${
                selectedSize === size
                  ? 'border-[#B76E79] text-[#B76E79] bg-[#B76E79]/10'
                  : 'border-white/10 text-white/30 hover:border-white/20'
              }`}
            >
              {size}
            </button>
          ))}
        </div>

        {/* Add button */}
        <button
          onClick={() => {
            const size = selectedSize || sizes[0];
            onAddToCart(id, name, collectionName, price, size);
          }}
          disabled={inCart}
          className="w-full py-2 text-xs tracking-wider uppercase rounded-lg transition-all duration-300 disabled:opacity-40"
          style={{
            backgroundColor: inCart ? 'transparent' : `${accentColor}20`,
            color: accentColor,
            border: `1px solid ${accentColor}${inCart ? '30' : '40'}`,
          }}
        >
          {inCart ? 'Added' : 'Add to Pre-Order'}
        </button>
      </div>
    </motion.div>
  );
}
