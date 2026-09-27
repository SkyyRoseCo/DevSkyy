---
name: Interactive Web Development
description: Expert knowledge in building interactive, dynamic web experiences with React, Vue, Svelte, animations, and user interactions. Triggers on keywords like "interactive", "animation", "dynamic", "react", "vue", "svelte", "gsap", "framer motion", "scroll animations", "parallax", "hover effects", "transitions".
version: 1.0.0
---

# Interactive Web Development

Build engaging, interactive web experiences with modern JavaScript frameworks, animation libraries, and interaction patterns.

## When to Use This Skill

Activate when working on:
- React, Vue, or Svelte components with rich interactions
- Scroll-based animations and parallax effects
- Hover states, transitions, and micro-interactions
- Form animations and validation UX
- Loading states and skeleton screens
- Interactive data visualizations
- Gesture-based interfaces
- State management for complex UIs

## Core Technologies

### React Ecosystem

**React + TypeScript** for type-safe components:

> Install: `npm install framer-motion@^11`  (v11 is required; the import path stays `"framer-motion"`)

```typescript
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ProductCardProps {
  product: Product;
  onQuickView: (id: string) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onQuickView }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      className="product-card"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <motion.img
        src={product.image}
        alt={product.name}
        animate={{ scale: isHovered ? 1.1 : 1 }}
        transition={{ duration: 0.3 }}
      />

      <AnimatePresence>
        {isHovered && (
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            onClick={() => onQuickView(product.id)}
          >
            Quick View
          </motion.button>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
```

**React Hooks** for complex state logic:
```typescript
function useIntersectionObserver(
  ref: RefObject<Element>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
    }, options);

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [ref, options]);

  return isIntersecting;
}

// Usage: Lazy load 3D viewer
function ProductViewer({ modelUrl }: { modelUrl: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const isVisible = useIntersectionObserver(ref, { threshold: 0.5 });

  return (
    <div ref={ref}>
      {isVisible && <ThreeJSViewer modelUrl={modelUrl} />}
    </div>
  );
}
```

### Animation Libraries

**Framer Motion** for React animations (install: `npm install framer-motion@^11` — this skill targets **Framer Motion v11**; the package name remains `framer-motion`, not the older `motion` standalone):
```typescript
import { motion, useScroll, useTransform } from 'framer-motion';

function ParallaxSection() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 0.5, 0]);

  return (
    <motion.section style={{ y, opacity }}>
      <h2>SkyyRose Collection</h2>
      <p></p>
    </motion.section>
  );
}
```

**GSAP** for advanced scroll animations:
```typescript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

useEffect(() => {
  gsap.to('.product-grid', {
    scrollTrigger: {
      trigger: '.product-grid',
      start: 'top center',
      end: 'bottom center',
      scrub: 1,
    },
    scale: 1.1,
    opacity: 1,
  });
}, []);
```

**React Spring** for physics-based animations:
```typescript
import { useSpring, animated } from '@react-spring/web';

function BouncyButton() {
  const [{ scale }, api] = useSpring(() => ({ scale: 1 }));

  return (
    <animated.button
      style={{ scale }}
      onMouseDown={() => api.start({ scale: 0.9 })}
      onMouseUp={() => api.start({ scale: 1 })}
    >
      Add to Cart
    </animated.button>
  );
}
```

### Next.js App Router & React Server Components

> **Critical for the SkyyRose dashboard (`frontend/`) — Next.js 16 App Router + React 19 with Cache Components mode.**

#### The RSC / Client Boundary Rule

`motion.*` components, all Framer Motion hooks (`useScroll`, `useTransform`, `useReducedMotion`, `useInView`, …), `useState`, `useEffect`, and any browser-only API require a client-side runtime. Any file that uses them **must** start with:

```typescript
'use client';
```

Placing that directive on a Server Component causes a build error. The directive propagates down — once a component is a Client Component, its children can also use client APIs.

#### Architectural Pattern: Server shell → Client leaf

Keep pages and layouts as **Server Components** so they can `async/await` data fetches and avoid shipping unnecessary JS. Push all animation into small `"use client"` leaf components that accept plain, serialisable props.

```
app/
  collections/
    [slug]/
      page.tsx          ← Server Component — fetches data, zero animation
      HeroAnimated.tsx  ← Client Component — owns all motion.* / hooks
      ProductGrid.tsx   ← Server Component — renders static product list
      ProductCardAnimated.tsx  ← Client Component — holo-card interaction
```

#### Concrete example: server page + animated hero leaf

```typescript
// app/collections/[slug]/page.tsx  — Server Component (no directive needed)
import { notFound } from 'next/navigation';
import { getCollection } from '@/lib/catalog';
import HeroAnimated from './HeroAnimated';
import ProductGrid from './ProductGrid';

interface Props {
  params: Promise<{ slug: string }>;
}

export default async function CollectionPage({ params }: Props) {
  const { slug } = await params;
  const collection = await getCollection(slug);
  if (!collection) notFound();

  return (
    <main>
      {/* Serialisable props only — no functions, no class instances */}
      <HeroAnimated
        title={collection.title}
        tagline={collection.tagline}
        accentColor={collection.accentColor}
      />
      <ProductGrid products={collection.products} />
    </main>
  );
}
```

```typescript
// app/collections/[slug]/HeroAnimated.tsx  — Client Component
'use client';

import { motion, useReducedMotion } from 'framer-motion';

interface HeroAnimatedProps {
  title: string;
  tagline: string;
  accentColor: string;
}

export default function HeroAnimated({ title, tagline, accentColor }: HeroAnimatedProps) {
  const shouldReduceMotion = useReducedMotion();

  const variants = {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 40 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <section className="collection-hero">
      <motion.h1
        variants={variants}
        initial="hidden"
        animate="visible"
        transition={{ duration: shouldReduceMotion ? 0 : 0.6, ease: 'easeOut' }}
        style={{ color: accentColor }}
      >
        {title}
      </motion.h1>
      <motion.p
        variants={variants}
        initial="hidden"
        animate="visible"
        transition={{ duration: shouldReduceMotion ? 0 : 0.6, delay: 0.15, ease: 'easeOut' }}
      >
        {tagline}
      </motion.p>
    </section>
  );
}
```

#### Cache Components mode: `<Suspense>` is mandatory

The SkyyRose dashboard runs with `cacheComponents: true`. Any component that reads request-time values — `usePathname()`, `useSearchParams()`, `cookies()`, `headers()`, or `use(params)` / `use(searchParams)` — causes a build failure **unless** it is wrapped in a `<Suspense>` boundary. This applies even when those reads happen inside a `"use client"` component.

Two safe patterns:

**Pattern A — wrap at the mount point** (good for layout chrome: sidebar, nav, mascot bubble):

```typescript
// app/layout.tsx — Server Component
import { Suspense } from 'react';
import ActiveLinkHighlight from '@/components/ActiveLinkHighlight'; // uses usePathname()

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav>
          <Suspense fallback={null}>
            <ActiveLinkHighlight />
          </Suspense>
        </nav>
        {children}
      </body>
    </html>
  );
}
```

**Pattern B — internal split** (good for reusable pages and data-heavy components):

```typescript
// components/FilterPanel.tsx — split into shell + content
'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import FilterSkeleton from './FilterSkeleton';

function FilterPanelContent() {
  // Safe: wrapped in <Suspense> by the shell below
  const searchParams = useSearchParams();
  const active = searchParams.get('collection') ?? 'all';

  return <div className="filter-panel" data-active={active}>…</div>;
}

export default function FilterPanel() {
  return (
    <Suspense fallback={<FilterSkeleton />}>
      <FilterPanelContent />
    </Suspense>
  );
}
```

Build output confirmation: routes using `<Suspense>` around dynamic readers render as `◐ (Partial Prerender)` — a static shell streamed immediately with the dynamic slice filled in. Routes missing `<Suspense>` fail with:

```
Error: Route "/path": Uncached data was accessed outside of <Suspense>.
```

#### Quick checklist for App Router + Framer Motion

- [ ] Any file importing from `'framer-motion'` has `'use client';` at the top
- [ ] Pages and layouts contain no `motion.*` imports — only leaf children do
- [ ] Props passed from server to client components are plain and serialisable (strings, numbers, arrays of primitives)
- [ ] `usePathname()` / `useSearchParams()` / `cookies()` / `headers()` are inside a `<Suspense>` boundary
- [ ] `useReducedMotion()` is called inside every animated leaf (respect `prefers-reduced-motion`)

### Vue 3 Composition API

```vue
<template>
  <Transition name="fade">
    <div v-if="isVisible" class="modal">
      <div class="modal-content" @click.stop>
        <slot />
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const isVisible = ref(props.show);

const handleEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape') emit('close');
};

onMounted(() => {
  document.addEventListener('keydown', handleEscape);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape);
});
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
```

### Svelte for Simple Interactions

```svelte
<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';

  export let items: Product[] = [];

  let selectedItem: Product | null = null;
</script>

{#each items as item (item.id)}
  <div
    class="item"
    in:fly={{ y: 50, duration: 300, easing: quintOut }}
    out:fade={{ duration: 200 }}
    on:click={() => selectedItem = item}
  >
    <img src={item.image} alt={item.name} />
    <h3>{item.name}</h3>
  </div>
{/each}

{#if selectedItem}
  <div transition:fade>
    <ProductDetail product={selectedItem} />
  </div>
{/if}
```

## Interaction Patterns

### Scroll-Based Interactions

**Reveal on Scroll:**
```typescript
function RevealOnScroll({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const isVisible = useIntersectionObserver(ref);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isVisible ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}
```

**Stagger Children:**
```typescript
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

<motion.div variants={container} initial="hidden" animate="show">
  {products.map(product => (
    <motion.div key={product.id} variants={item}>
      <ProductCard product={product} />
    </motion.div>
  ))}
</motion.div>
```

### Gesture-Based Interactions

**Drag and Drop:**
```typescript
import { motion } from 'framer-motion';

<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 0 }}
  dragElastic={0.2}
  onDragEnd={(event, info) => {
    if (info.offset.x > 100) {
      // Swiped right
      onNextProduct();
    }
  }}
>
  <ProductImage />
</motion.div>
```

**Touch Gestures:**
```typescript
import { useGesture } from '@use-gesture/react';
import { useSpring, animated } from '@react-spring/web';

function SwipeableCard() {
  const [{ x, opacity }, api] = useSpring(() => ({ x: 0, opacity: 1 }));

  const bind = useGesture({
    onDrag: ({ movement: [mx], direction: [xDir], velocity: [vx] }) => {
      const trigger = vx > 0.2;
      const dir = xDir < 0 ? -1 : 1;

      if (!trigger) {
        api.start({ x: 0, opacity: 1 });
      } else {
        api.start({ x: dir * 300, opacity: 0 });
        setTimeout(() => onSwipe(dir), 300);
      }
    }
  });

  return <animated.div {...bind()} style={{ x, opacity }} />;
}
```

### Micro-Interactions

**Button Feedback:**
```typescript
const ButtonWithFeedback: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  const [{ scale, backgroundColor }, api] = useSpring(() => ({
    scale: 1,
    backgroundColor: '#B76E79'
  }));

  const handleClick = () => {
    api.start({
      scale: 0.95,
      config: { tension: 300, friction: 10 }
    });
    setTimeout(() => api.start({ scale: 1 }), 100);
    onClick();
  };

  return (
    <animated.button
      style={{ scale, backgroundColor }}
      onClick={handleClick}
      onHoverStart={() => api.start({ backgroundColor: '#A65E69' })}
      onHoverEnd={() => api.start({ backgroundColor: '#B76E79' })}
    >
      Add to Cart
    </animated.button>
  );
};
```

**Loading States:**
```typescript
function LoadingButton({ isLoading, onClick, children }) {
  return (
    <motion.button
      onClick={onClick}
      disabled={isLoading}
      animate={{ width: isLoading ? 40 : 'auto' }}
    >
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="spinner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, rotate: 360 }}
            exit={{ opacity: 0 }}
            transition={{ rotate: { repeat: Infinity, duration: 1 } }}
          >
            ⏳
          </motion.div>
        ) : (
          <motion.span
            key="text"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {children}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );
}
```

## Performance Optimization

**Lazy Loading Components:**
```typescript
import { lazy, Suspense } from 'react';

const Heavy3DViewer = lazy(() => import('./Heavy3DViewer'));

function ProductPage() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <Heavy3DViewer />
    </Suspense>
  );
}
```

**Memoization:**
```typescript
import { memo, useMemo } from 'react';

const ProductCard = memo(({ product }: { product: Product }) => {
  const discountedPrice = useMemo(
    () => calculateDiscount(product.price, product.discount),
    [product.price, product.discount]
  );

  return <div>{discountedPrice}</div>;
});
```

**Virtual Scrolling:**
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function ProductList({ products }: { products: Product[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: products.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 350,
    overscan: 5
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(item => (
          <div
            key={item.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${item.start}px)`
            }}
          >
            <ProductCard product={products[item.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

## SkyyRose-Specific Patterns

### Luxury Transition Timings

```typescript
export const skyyrose = {
  transitions: {
    fast: { duration: 0.15, ease: 'easeOut' },
    base: { duration: 0.3, ease: 'easeInOut' },
    slow: { duration: 0.6, ease: [0.43, 0.13, 0.23, 0.96] },
    spring: { type: 'spring', stiffness: 300, damping: 30 }
  },
  colors: {
    primary: '#B76E79',
    primaryHover: '#A65E69',
    secondary: '#2C2C2C'
  }
};
```

### Rose Gold Gradient Animations

```typescript
function RoseGoldShimmer() {
  return (
    <motion.div
      className="shimmer"
      animate={{
        backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: 'linear'
      }}
      style={{
        background: 'linear-gradient(90deg, #B76E79 0%, #E8C5A5 50%, #B76E79 100%)',
        backgroundSize: '200% 100%'
      }}
    />
  );
}
```

## WordPress Interactive Development

### Architecture Rules

- **Theme directory**: `wordpress-theme/skyyrose-flagship/` — the ONLY production theme
- **Target site**: `skyyrose.co` (NOT devskyy.app — that's the agent dashboard)
- **Extend via hooks** — never modify WordPress core
- **Escape on output** (`esc_html()`, `esc_attr()`, `esc_url()`) — sanitize on input (`sanitize_text_field()`)
- **Nonce + capability checks** on all write actions
- **Vanilla JS via CDN** for interactive features — NOT React/Vue bundled builds
- **Progressive enhancement** — pages must work without JS, then layer interactivity

### Enqueueing Interactive Assets

Use the theme's engine helper for consistent min/non-min switching:

```php
<?php
/**
 * Enqueue an interactive experience with CSS + JS pair.
 * Uses the theme's skyyrose_enqueue_engine() helper from inc/enqueue-engines.php.
 *
 * Files must exist as: assets/css/{slug}.css and assets/js/{slug}.js
 * Minified variants: assets/css/{slug}.min.css and assets/js/{slug}.min.js
 */
function skyyrose_enqueue_interactive_experience() {
    // Only load on immersive template pages.
    if ( ! is_page_template( 'template-immersive-black-rose.php' ) ) {
        return;
    }

    // Three.js via CDN (never bundle — use exact version for stability).
    wp_enqueue_script(
        'threejs',
        'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
        array(),
        'r128',
        true
    );

    // GSAP via CDN.
    wp_enqueue_script(
        'gsap',
        'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js',
        array(),
        '3.12.2',
        true
    );

    wp_enqueue_script(
        'gsap-scrolltrigger',
        'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js',
        array( 'gsap' ),
        '3.12.2',
        true
    );

    // Collection-specific experience (depends on Three.js + GSAP).
    skyyrose_enqueue_engine(
        'skyyrose-blackrose-experience',
        'experiences/blackrose-experience',
        array( 'skyyrose-design-tokens' ),
        array( 'threejs', 'gsap', 'gsap-scrolltrigger' )
    );
}
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_interactive_experience' );
```

### Passing Product Data to JS (wp_localize_script)

Never hardcode product data in JS. Use `wp_localize_script()` for WooCommerce integration:

```php
<?php
function skyyrose_localize_experience_data() {
    if ( ! is_page_template( 'template-immersive-black-rose.php' ) ) {
        return;
    }

    // Get collection products via WooCommerce.
    $products = wc_get_products( array(
        'category' => array( 'black-rose' ),
        'status'   => 'publish',
        'limit'    => 20,
    ) );

    $product_data = array();
    foreach ( $products as $product ) {
        $product_data[] = array(
            'id'        => $product->get_id(),
            'name'      => esc_html( $product->get_name() ),
            'price'     => $product->get_price_html(),
            'image'     => wp_get_attachment_url( $product->get_image_id() ),
            'permalink' => esc_url( $product->get_permalink() ),
            'sku'       => esc_html( $product->get_sku() ),
        );
    }

    wp_localize_script( 'skyyrose-blackrose-experience', 'skyyRoseProducts', array(
        'products' => $product_data,
        'ajaxUrl'  => admin_url( 'admin-ajax.php' ),
        'nonce'    => wp_create_nonce( 'skyyrose_experience_nonce' ),
        'siteUrl'  => esc_url( home_url() ),
    ) );
}
add_action( 'wp_enqueue_scripts', 'skyyrose_localize_experience_data' );
```

### Interactive Hotspots in PHP Templates

Product hotspots rendered server-side, enhanced client-side:

```php
<?php
/**
 * Render a product hotspot for Three.js to pick up.
 *
 * @param WC_Product $product  WooCommerce product object.
 * @param array      $position 3D position array ['x', 'y', 'z'].
 */
function skyyrose_render_hotspot( $product, $position ) {
    if ( ! $product instanceof WC_Product ) {
        return;
    }
    ?>
    <div class="sr-hotspot"
         data-product-id="<?php echo esc_attr( $product->get_id() ); ?>"
         data-sku="<?php echo esc_attr( $product->get_sku() ); ?>"
         data-position-x="<?php echo esc_attr( $position['x'] ); ?>"
         data-position-y="<?php echo esc_attr( $position['y'] ); ?>"
         data-position-z="<?php echo esc_attr( $position['z'] ); ?>"
         aria-label="<?php echo esc_attr( $product->get_name() ); ?>"
         role="button"
         tabindex="0">
        <span class="sr-hotspot__pulse"></span>
    </div>
    <?php
}
```

### AJAX Handlers for Interactive Features

```php
<?php
/**
 * AJAX: Add to cart from immersive experience.
 * Nonce verified. Capability not required (public action).
 */
function skyyrose_ajax_add_to_cart() {
    check_ajax_referer( 'skyyrose_experience_nonce', 'nonce' );

    $product_id = absint( $_POST['product_id'] ?? 0 );
    $quantity   = absint( $_POST['quantity'] ?? 1 );

    if ( ! $product_id || ! wc_get_product( $product_id ) ) {
        wp_send_json_error( array( 'message' => 'Invalid product.' ), 400 );
    }

    $cart_item_key = WC()->cart->add_to_cart( $product_id, $quantity );

    if ( $cart_item_key ) {
        wp_send_json_success( array(
            'message'    => 'Added to cart.',
            'cart_count' => WC()->cart->get_cart_contents_count(),
            'cart_total' => WC()->cart->get_cart_total(),
        ) );
    }

    wp_send_json_error( array( 'message' => 'Could not add to cart.' ), 500 );
}
add_action( 'wp_ajax_skyyrose_add_to_cart', 'skyyrose_ajax_add_to_cart' );
add_action( 'wp_ajax_nopriv_skyyrose_add_to_cart', 'skyyrose_ajax_add_to_cart' );
```

### Client-Side AJAX Pattern (Vanilla JS)

```javascript
/**
 * Add to cart from an immersive experience hotspot.
 * Uses the nonce and ajaxUrl from wp_localize_script.
 */
async function addToCartFromHotspot(productId) {
    const form = new FormData();
    form.append('action', 'skyyrose_add_to_cart');
    form.append('nonce', window.skyyRoseProducts.nonce);
    form.append('product_id', productId);
    form.append('quantity', 1);

    try {
        const res = await fetch(window.skyyRoseProducts.ajaxUrl, {
            method: 'POST',
            body: form,
            credentials: 'same-origin',
        });
        const data = await res.json();

        if (data.success) {
            updateCartBadge(data.data.cart_count);
            showToast(`Added to cart — ${data.data.cart_total}`);
        } else {
            showToast(data.data.message, 'error');
        }
    } catch (err) {
        console.error('Cart error:', err);
        showToast('Something went wrong.', 'error');
    }
}
```

### Scroll Animations with GSAP (WordPress-safe)

```javascript
/**
 * WordPress-safe GSAP initialization.
 * Wait for DOMContentLoaded — never use jQuery wrapper in new code.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Guard: only run on pages with the experience container.
    const container = document.getElementById('sr-experience');
    if (!container) return;

    gsap.registerPlugin(ScrollTrigger);

    // Stagger product cards into view.
    gsap.from('.sr-product-card', {
        scrollTrigger: {
            trigger: '.sr-product-grid',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse',
        },
        y: 60,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: 'power2.out',
    });

    // Parallax hero background.
    gsap.to('.sr-hero__bg', {
        scrollTrigger: {
            trigger: '.sr-hero',
            start: 'top top',
            end: 'bottom top',
            scrub: true,
        },
        y: '30%',
        ease: 'none',
    });

    // Respect reduced motion preference.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        ScrollTrigger.getAll().forEach(function (trigger) {
            trigger.kill();
        });
        // Remove all GSAP inline styles so content is visible.
        gsap.set('.sr-product-card, .sr-hero__bg', { clearProps: 'all' });
    }
});
```

### WordPress REST API for Dynamic Content

```javascript
/**
 * Fetch product data via WooCommerce REST API (public, read-only).
 * Use index.php?rest_route= NOT /wp-json/ (WordPress.com compatible).
 */
async function fetchCollectionProducts(collectionSlug) {
    const baseUrl = window.skyyRoseProducts.siteUrl;
    const url = `${baseUrl}/index.php?rest_route=/wc/v3/products&category=${collectionSlug}&per_page=20`;

    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
    });

    if (!res.ok) throw new Error(`API ${res.status}`);
    return res.json();
}
```

### CSS Custom Properties for Interactive States

```css
/**
 * SkyyRose interactive design tokens.
 * Defined in assets/css/design-tokens.css, consumed by all JS.
 */
:root {
    /* Brand palette */
    --sr-rose-gold: #B76E79;
    --sr-dark: #0A0A0A;
    --sr-silver: #C0C0C0;
    --sr-crimson: #DC143C;
    --sr-gold: #D4AF37;

    /* Transitions — luxury = slightly slower */
    --sr-transition-fast: 150ms ease-out;
    --sr-transition-base: 300ms ease-in-out;
    --sr-transition-slow: 600ms cubic-bezier(0.43, 0.13, 0.23, 0.96);

    /* Z-index scale for overlays */
    --sr-z-hotspot: 10;
    --sr-z-product-card: 20;
    --sr-z-modal: 100;
    --sr-z-toast: 200;
}

/* Reduced motion: flatten all transitions */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}

/* Hotspot pulse animation */
.sr-hotspot__pulse {
    position: absolute;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--sr-rose-gold);
    animation: sr-pulse 2s ease-in-out infinite;
}

@keyframes sr-pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50%      { transform: scale(1.6); opacity: 0; }
}
```

### File Organization

```
wordpress-theme/skyyrose-flagship/
├── assets/
│   ├── css/
│   │   ├── design-tokens.css          ← Brand variables (consumed by all JS)
│   │   ├── immersive.css              ← Base immersive styles
│   │   └── experiences/               ← Per-collection CSS
│   └── js/
│       ├── immersive-world.js         ← Core Three.js engine
│       ├── immersive-wc-bridge.js     ← WooCommerce ↔ Three.js data bridge
│       └── experiences/               ← Per-collection experiences
│           ├── experience-base.js     ← SkyyRoseExperience base class
│           ├── blackrose-experience.js
│           ├── lovehurts-experience.js
│           ├── signature-experience.js
│           ├── luxury-animations.js
│           └── init-3d.js
├── inc/
│   ├── enqueue.php                    ← Global asset loading
│   ├── enqueue-engines.php            ← skyyrose_enqueue_engine() helper
│   ├── enqueue-features.php           ← Feature-specific scripts
│   └── immersive-ajax.php             ← AJAX handlers for 3D experiences
└── template-immersive-*.php           ← PHP templates with data-* attributes
```

### Security Checklist for Interactive Features

- [ ] All AJAX handlers use `check_ajax_referer()` with nonces
- [ ] Product IDs validated with `absint()` before WooCommerce queries
- [ ] All output escaped: `esc_html()`, `esc_attr()`, `esc_url()`
- [ ] No inline `<script>` — all JS via `wp_enqueue_script()`
- [ ] `wp_localize_script()` for passing data to JS (not inline JSON)
- [ ] REST API endpoint uses `index.php?rest_route=` (not `/wp-json/`)
- [ ] `credentials: 'same-origin'` on all fetch calls
- [ ] `$wpdb->prepare()` for any custom queries (never concatenate)
- [ ] Capability checks on admin-only AJAX actions
- [ ] No `eval()`, `innerHTML` with user data, or `document.write()`

## Accessibility

Ensure animations respect user preferences:

```typescript
import { useReducedMotion } from 'framer-motion';

function AccessibleAnimation() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={{ opacity: 1 }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.6 }}
    >
      Content
    </motion.div>
  );
}
```

### WordPress Accessibility Essentials

- All hotspots have `role="button"`, `tabindex="0"`, and `aria-label`
- Keyboard navigation: Enter/Space activates hotspots, Escape closes modals
- `prefers-reduced-motion` kills all GSAP timelines and CSS animations
- Focus trap inside modals (product cards, quick view)
- Screen reader announcements via `wp_localize_script()` providing alt text
- Color contrast: SkyyRose rose gold (#B76E79) on dark (#0A0A0A) passes WCAG AA
