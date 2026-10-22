'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowLeft, CreditCard, Lock, Trash2, Minus, Plus, ShoppingBag } from 'lucide-react';
import { useCartStore } from '@/lib/stores/cart-store';

export default function CheckoutPage() {
  const { items, removeItem, updateQuantity, clearCart, subtotal } = useCartStore();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const total = subtotal();
  const shipping = total > 200 ? 0 : 15;
  const tax = total * 0.0875; // CA sales tax

  async function handleCheckout() {
    setProcessing(true);
    setError(null);

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: items.map(i => ({
            productId: i.productId,
            name: i.productName,
            size: i.size,
            quantity: i.quantity,
            price: i.price,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error('Checkout failed. Please try again.');
      }

      const { url } = await response.json();

      if (url) {
        // Redirect to Stripe Checkout
        window.location.href = url;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Checkout failed');
    } finally {
      setProcessing(false);
    }
  }

  if (items.length === 0) {
    return (
      <div className='min-h-screen flex items-center justify-center px-4'>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className='text-center'>
          <ShoppingBag size={48} className='text-white/20 mx-auto mb-4' />
          <h2 className='text-2xl font-display text-white mb-2'>Your cart is empty</h2>
          <p className='text-white/40 text-sm mb-6'>Explore our collections and add items to get started.</p>
          <Link
            href='/pre-order'
            className='inline-flex items-center gap-2 px-6 py-3 bg-[#B76E79] text-white text-sm tracking-[0.15em] uppercase rounded-lg hover:bg-[#D4A5B0] transition-colors'
          >
            <ArrowLeft size={16} />
            Browse Collections
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className='min-h-screen pt-20 pb-24 px-4'>
      <div className='max-w-4xl mx-auto'>
        {/* Header */}
        <div className='flex items-center justify-between mb-8'>
          <div>
            <Link
              href='/pre-order'
              className='text-white/40 text-xs tracking-wider hover:text-white/60 transition-colors flex items-center gap-1 mb-2'
            >
              <ArrowLeft size={14} />
              Continue Shopping
            </Link>
            <h1 className='text-3xl font-display text-white'>Checkout</h1>
          </div>
          <button
            onClick={clearCart}
            className='text-white/30 text-xs tracking-wider hover:text-red-400 transition-colors'
          >
            Clear Cart
          </button>
        </div>

        <div className='grid lg:grid-cols-3 gap-8'>
          {/* Cart Items */}
          <div className='lg:col-span-2 space-y-4'>
            {items.map(item => (
              <motion.div
                key={`${item.productId}-${item.size}`}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className='flex items-center gap-4 p-4 rounded-xl border border-white/5 bg-white/[0.02]'
              >
                <div className='flex-1'>
                  <p className='text-white text-sm font-medium'>{item.productName}</p>
                  <p className='text-white/30 text-xs mt-0.5'>
                    {item.collection} &middot; Size: {item.size}
                  </p>
                </div>

                {/* Quantity */}
                <div className='flex items-center gap-2'>
                  <button
                    onClick={() => updateQuantity(item.productId, item.size, item.quantity - 1)}
                    className='w-7 h-7 rounded border border-white/10 flex items-center justify-center text-white/40 hover:text-white hover:border-white/20 transition-colors'
                  >
                    <Minus size={12} />
                  </button>
                  <span className='text-white text-sm w-6 text-center'>{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.productId, item.size, item.quantity + 1)}
                    className='w-7 h-7 rounded border border-white/10 flex items-center justify-center text-white/40 hover:text-white hover:border-white/20 transition-colors'
                  >
                    <Plus size={12} />
                  </button>
                </div>

                {/* Price */}
                <span className='text-white/60 text-sm w-20 text-right'>
                  ${(item.price * item.quantity).toLocaleString()}
                </span>

                {/* Remove */}
                <button
                  onClick={() => removeItem(item.productId, item.size)}
                  className='text-white/20 hover:text-red-400 transition-colors'
                >
                  <Trash2 size={14} />
                </button>
              </motion.div>
            ))}
          </div>

          {/* Order Summary */}
          <div className='lg:col-span-1'>
            <div className='sticky top-24 p-6 rounded-xl border border-white/5 bg-white/[0.02]'>
              <h3 className='text-lg font-display text-white mb-4'>Order Summary</h3>

              <div className='space-y-3 text-sm'>
                <div className='flex justify-between'>
                  <span className='text-white/40'>Subtotal</span>
                  <span className='text-white'>${total.toLocaleString()}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-white/40'>Shipping</span>
                  <span className='text-white'>{shipping === 0 ? 'Free' : `$${shipping}`}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-white/40'>Tax</span>
                  <span className='text-white'>${tax.toFixed(2)}</span>
                </div>
                <div className='border-t border-white/5 pt-3 flex justify-between'>
                  <span className='text-white font-medium'>Total</span>
                  <span className='text-white text-lg font-display'>${(total + shipping + tax).toFixed(2)}</span>
                </div>
              </div>

              {error && <p className='text-red-400 text-xs mt-4'>{error}</p>}

              <button
                onClick={handleCheckout}
                disabled={processing}
                className='w-full mt-6 px-6 py-4 bg-[#B76E79] text-white text-sm tracking-[0.15em] uppercase rounded-lg hover:bg-[#D4A5B0] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2'
              >
                {processing ? (
                  'Processing...'
                ) : (
                  <>
                    <CreditCard size={16} />
                    Complete Purchase
                  </>
                )}
              </button>

              <div className='flex items-center justify-center gap-1 mt-3 text-white/20 text-xs'>
                <Lock size={10} />
                <span>Secured by Stripe</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
