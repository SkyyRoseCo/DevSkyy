# WordPress Build Specification — SkyyRose Flagship Theme

> Master build guide for Elite Web Builder agents. Convert static HTML designs into WordPress PHP templates with AI photography integration.

## Site Connection

```
Blog ID:    238510894
Site URL:   https://skyyrose.co
Theme:      skyyrose-flagship (THE FLAGSHIP)
Platform:   WordPress.com Atomic (SSH/SFTP, custom PHP, full plugin access)
Homepage:   Page ID 9331 (static front page)
Timezone:   America/Los_Angeles (UTC-8)
```

## Design Source of Truth

The static HTML files in `wp-playground/SKyyRose Flagship/Flagship static/` are the **canonical design reference**. Every PHP template must faithfully reproduce these designs. Do NOT use the root-level HTML variants (they are heavier experimental versions with different fonts).

### Reference Files (9 pages)

| Static HTML | WordPress Template | Lines |
|------------|-------------------|-------|
| `homepage.html` | `front-page.php` | 1151 |
| `collection-black-rose.html` | `template-collection-black-rose.php` | 818 |
| `collection-love-hurts.html` | `template-collection-love-hurts.php` | 817 |
| `collection-signature.html` | `template-collection-signature.php` | 880 |
| `single-product.html` | `woocommerce/single-product.php` | 925 |
| `about.html` | `template-about.php` | 608 |
| `contact.html` | `template-contact.php` | 346 |
| `cart.html` | `woocommerce/cart/cart.php` | 670 |
| `checkout.html` | `woocommerce/checkout/form-checkout.php` | 813 |

---

## Design System (CSS Custom Properties)

### Base Variables (ALL pages share these)

```css
:root {
  /* Core palette */
  --bg-dark: #0A0A0A;
  --bg-card: #111111;
  --text-primary: #FFFFFF;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.5);
  --border-subtle: rgba(255, 255, 255, 0.1);

  /* Collection accents (OFFICIAL — owner-confirmed) */
  --black-rose: #C0C0C0;         /* Metallic Silver */
  --love-hurts: #DC143C;         /* Crimson Red */
  --signature-gold: #D4AF37;     /* Gold */
  --kids-capsule: #FFB6C1;       /* Pink */

  /* Brand-level accents */
  --rose-gold: #B76E79;          /* Primary brand color (Signature owns this) */
  --accent-gold: #D4AF37;        /* Gold */
  --metallic-silver: #C0C0C0;    /* Silver */
  --accent-hover: rgba(255, 255, 255, 0.05);

  /* Transitions */
  --transition-smooth: all 0.3s ease;
  --transition-spring: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Official Brand & Collection Logos

#### Primary Brand Mark
| Asset | File | Description |
|-------|------|-------------|
| **SR Monogram** | `branding/primary/sr-monogram.jpeg` | Rose gold "SR" calligraphy intertwined with rose bloom. **THE** brand logo — header, favicon, loading screen, footer, watermarks. |

#### Collection Logos
| Collection | Asset | File | Description |
|-----------|-------|------|-------------|
| **SIGNATURE** | Geometric Rose | `branding/signature/sr-rose-geometric.png` | Rose gold metallic cutout rose, clean geometric lines. Collection badge/icon. |
| **SIGNATURE** | Glass Wordmark | `branding/signature/signature-3d-wordmark.png` | "The Skyy Rose COLLECTION" in 3D glass/crystal typography. Hero/banner asset. |
| **LOVE HURTS** | Enamel Pin | `branding/love-hurts/love-hurts-enamel-pin.jpeg` | "Love Hurts" crimson script + cracked heart in thorns. 3D metallic pin style. Collection badge. |
| **LOVE HURTS** | Neon Star | `branding/love-hurts/love-hurts-neon-star.jpeg` | Red neon star frame with rose + cracked heart on pedestal. Hero/feature image. |
| **LOVE HURTS** | Heart & Roses | `branding/love-hurts/love-hurts-heart-roses.png` | Full-color illustration — cracked heart, thorns, roses, blood-drip script. Lookbook graphic. |
| **BLACK ROSE** | Crystal Star | `branding/black-rose/black-rose-crystal-star.jpeg` | Crystal star trophy with black rose inside, heart-shaped walnut base. Collection badge. |
| **BLACK ROSE** | Letter Logo | `branding/black-rose/black-rose-letter-logo.png` | "The Black Rose Collection" glossy black 3D script with small rose icon beneath. Hero/banner wordmark. |

#### Logo Processing (REQUIRED before theme use)
- Remove backgrounds → transparent PNG (use `rembg` or manual masking)
- Export 3 sizes: icon (64px), badge (256px), hero (1024px)
- WebP + PNG dual format
- Clean edges — no white halos after bg removal

#### Logo Placement Map
```
Header:          SR Monogram (48px height, rose gold on dark bg)
Footer:          SR Monogram (64px) + "The Skyy Rose Collection" text
Loading screen:  SR Monogram (120px, breathe animation)
Favicon:         SR Monogram (32x32 + 180x180 apple-touch)
Collection hero: Collection-specific logo centered above heading
Product cards:   NO logo — clean display (photo + name + price only)
Immersive pages: Collection logo watermark (bottom-right, 8% opacity)
```

---

### Official Collection Colors (OWNER-CONFIRMED)

| Collection | Official Colors | Hex Values |
|-----------|----------------|------------|
| **BLACK ROSE** | Black, White, Metallic Silver | `#000000`, `#FFFFFF`, `#C0C0C0` |
| **LOVE HURTS** | Red, Crimson, Black, White | `#FF0000`, `#DC143C`, `#000000`, `#FFFFFF` |
| **SIGNATURE** | Rose Gold *(primary brand color)*, Gold | `#B76E79`, `#D4AF37` |
| **KIDS CAPSULE** | Pink, Lavender | `#FFB6C1`, `#E6E6FA` |

### Collection-Specific Extended Variables

```css
/* BLACK ROSE — Black, White, Metallic Silver */
.collection-black-rose {
  --collection-accent: #C0C0C0;    /* Metallic Silver */
  --collection-black: #000000;
  --collection-white: #FFFFFF;
  --collection-gradient: linear-gradient(135deg, #C0C0C0, #000000);
  /* Floating emoji: 🥀🌹 with floatUp keyframe */
  /* Mood: monochromatic gothic, silver + black contrast */
}

/* LOVE HURTS — Red, Crimson, Black, White */
.collection-love-hurts {
  --collection-accent: #DC143C;    /* Crimson */
  --love-hurts-red: #FF0000;
  --love-hurts-crimson: #DC143C;
  --love-hurts-dark: #8B0000;      /* Deep crimson for shadows */
  --collection-gradient: linear-gradient(135deg, #DC143C, #8B0000);
  /* Floating emoji: ♥ with floatHeart keyframe, 15 hearts */
  /* Mood: passionate, blood red + black drama */
}

/* SIGNATURE — Rose Gold + Gold (PRIMARY BRAND COLORS) */
.collection-signature {
  --collection-accent: #B76E79;    /* Rose Gold — THE brand color */
  --signature-gold: #D4AF37;       /* Gold */
  --signature-cream: #F5F0E6;
  --champagne: #F7E7CE;
  --bronze: #CD7F32;
  --collection-gradient: linear-gradient(135deg, #D4AF37, #B76E79);
  /* Art deco repeating-linear-gradient overlay at 45deg */
  /* Mood: elevated luxury, warm metallics */
}

/* KIDS CAPSULE — Pink + Lavender */
.collection-kids {
  --collection-accent: #FFB6C1;    /* Pink */
  --kids-lavender: #E6E6FA;
  --kids-gradient: linear-gradient(135deg, #FFB6C1, #E6E6FA);
  /* Mood: joyful, playful sophistication */
}
```

### Typography

```css
/* Font stack — MUST use Inter + Playfair Display */
/* DO NOT use Montserrat, Cormorant Garamond, or other fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&display=swap');

body { font-family: 'Inter', -apple-system, sans-serif; }
h1, h2, h3, .display-text { font-family: 'Playfair Display', serif; }

/* Size scale */
--font-xs: 0.75rem;   /* 12px — badges, labels */
--font-sm: 0.875rem;  /* 14px — captions */
--font-base: 1rem;    /* 16px — body */
--font-lg: 1.25rem;   /* 20px — subheadings */
--font-xl: 1.75rem;   /* 28px — section headings */
--font-2xl: 2.625rem; /* 42px — hero headlines */
--font-3xl: 3.5rem;   /* 56px — homepage hero */
```

### Film Grain Overlay (ALL pages)

Every page must include a film grain SVG overlay for the luxury texture effect:

```css
.film-grain::after {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,..."); /* SVG noise filter */
  /* OR use CSS noise: */
  background: repeating-conic-gradient(#fff 0 0.0001%, transparent 0 0.0002%) 50% 50%/200px 200px;
  mix-blend-mode: overlay;
}
```

### Responsive Breakpoints

```css
@media (max-width: 1200px) { /* Tablet landscape */ }
@media (max-width: 768px)  { /* Tablet portrait — stack grids */ }
@media (max-width: 480px)  { /* Mobile — full-width cards */ }
```

---

## Shared Components

### Header / Navbar

```
Structure: Fixed position, dark background with backdrop-filter blur
┌─────────────────────────────────────────────────────────────┐
│  SKYY ROSE (gradient text)  │  NAV LINKS  │  🔍  👤  🛒(n)  │
│  (logo link to /)           │  Collections │  (icon buttons)  │
│                             │  About       │                   │
│                             │  Contact     │                   │
└─────────────────────────────────────────────────────────────┘
```

- Background: `rgba(10, 10, 10, 0.95)` with `backdrop-filter: blur(20px)`
- Logo text: gradient `linear-gradient(135deg, #D4AF37, #B76E79)` with `-webkit-background-clip: text`
- Nav links: `rgba(255, 255, 255, 0.7)` → white on hover, underline animation
- Sticky on scroll with shadow transition
- Mobile: hamburger menu (slide-in from right)

### Footer (5-Column Grid)

```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│  BRAND   │   SHOP   │  HELP    │  LEGAL   │  SOCIAL  │
│  Logo    │  Black   │  FAQ     │  Privacy │  IG      │
│  Tagline │  Love    │  Shipping│  Terms   │  TikTok  │
│          │  Sig     │  Returns │  Cookie  │  Twitter │
│          │  Kids    │  Contact │          │  Pinterest│
└──────────┴──────────┴──────────┴──────────┴──────────┘
│  Newsletter signup bar  │  © 2024 The Skyy Rose Collection  │
```

- Background: `#0A0A0A`, border-top: `1px solid rgba(255,255,255,0.1)`
- Grid: `grid-template-columns: 2fr 1fr 1fr 1fr 1fr` at desktop
- Links: `rgba(255,255,255,0.5)` → `#D4AF37` on hover
- Mobile: stack to single column

### Product Card Component

```
┌──────────────────────────┐
│  [AI Model Photo]        │  ← 3:4 aspect ratio
│                          │
│  ♥  👁  🛒  (hover only) │  ← Quick actions overlay
├──────────────────────────┤
│  Product Name            │  ← Inter 600
│  $XXX                    │  ← Collection accent color
└──────────────────────────┘
```

- Card: `background: #111`, `border: 1px solid rgba(255,255,255,0.05)`
- Hover: `translateY(-8px)`, `box-shadow: 0 20px 60px rgba(0,0,0,0.5)`
- Image: AI fashion model photo (front view) from `products/{sku}/{sku}-model-front.jpg`
- Quick actions: fade-in overlay at bottom on hover
- Price color: matches collection accent variable

### Toast Notifications

- Position: fixed bottom-right
- Slide in from right, auto-dismiss after 3s
- Dark glass style: `rgba(17,17,17,0.95)` with backdrop blur
- Green check for success, gold for info

---

## Page Templates

### 1. front-page.php (Homepage)

**Reference:** `Flagship static/homepage.html` (1151 lines)

#### Sections (in order):

1. **Hero Section** (100vh)
   - Badge: "Oakland Luxury Streetwear" (letter-spacing: 6px, uppercase)
   - Headline: "Where Love Meets Luxury" — gradient text (#D4AF37 → #B76E79)
   - Subtext: "Crafted for those who dare to stand out"
   - CTA buttons: "Shop Collections" (filled) + "Pre-Order Now" (outline)
   - Background: animated floating orbs (3 circles: 500px, 400px, 300px with blur + slow movement)

2. **Collections Showcase** (3 cards)
   - Section heading: "Explore Our World"
   - Three 600px-tall cards side by side
   - Each card: background image + gradient overlay + collection name + tagline
   - Hover: scale up, reveal "Explore" button
   - Cards: BLACK ROSE (#8B0000), LOVE HURTS (#B76E79), SIGNATURE (#D4AF37)

3. **Featured Products** (4 product cards)
   - Section heading: "New Arrivals"
   - Grid: `repeat(4, 1fr)` at desktop, `repeat(2, 1fr)` at mobile
   - Use product card component with AI model photos
   - Quick view + wishlist + add-to-cart actions

4. **Brand Story Section**
   - 2-column layout: text left, image right
   - Heading: "Born in Oakland, Crafted with Love"
   - Body text about the brand origin + founder vision
   - CTA: "Our Story" button → about page

5. **Newsletter Signup**
   - Full-width dark section with subtle gradient
   - Heading: "Join the Movement"
   - Email input + subscribe button
   - Text: "Be the first to know about drops, exclusives, and events"

6. **Footer** (shared component)

### 2. template-collection-black-rose.php

**Reference:** `Flagship static/collection-black-rose.html` (818 lines)

#### Visual Identity:
- Floating roses animation: 🥀 and 🌹 emojis floating upward with `floatUp` keyframe
- Collection accent: `--black-rose: #8B0000`

#### Sections:
1. **Hero** (70vh) — "LIMITED EDITION" badge, collection name + tagline, gradient overlay
2. **Filter Bar** — Categories: All, Hoodies, Jackets, Tees, Pants + sort dropdown
3. **Products Grid** — 8 products (br-001..008) rendered with AI model photos, data attributes for filtering
4. **Collection Story** — Brand narrative about Black Rose
5. **CTA** — "Enter the Garden" → immersive page link

**CRITICAL: Replace placeholder names** (Thorn Hoodie, Midnight Jacket, etc.) with canonical names from `photo_generation.md`.

### 3. template-collection-love-hurts.php

**Reference:** `Flagship static/collection-love-hurts.html` (817 lines)

#### Visual Identity:
- Floating hearts: ♥ emoji with `floatHeart` keyframe (15 hearts, random positions)
- Extended palette: `--love-hurts-light: #D4A5AD`, `--burgundy: #722F37`, `--rose-gold: #E8C4C4`
- Pulsing collection badge animation

#### Sections:
1. **Hero** (70vh) — Pulsing badge, gradient text, "Every scar tells a story"
2. **Story Section** — Blockquote with emotional narrative
3. **Products Grid** — 5 products (lh-001..005) with AI model photos
4. **Emotion Cards** (3) — Vulnerability 💔, Transformation 🌹, Resilience ✨
5. **CTA** — "Wear Your Story" → immersive page link

**CRITICAL: Replace placeholder names** (Heartbreak Hoodie, Tears Bomber, etc.) with canonical names.

### 4. template-collection-signature.php

**Reference:** `Flagship static/collection-signature.html` (880 lines)

#### Visual Identity:
- Art deco pattern overlay: `repeating-linear-gradient(45deg, ...)` at low opacity
- Extended palette: `--signature-cream: #F5F0E6`, `--champagne: #F7E7CE`, `--bronze: #CD7F32`
- Pulsing ring animation (600px gold circle behind heading)

#### Sections:
1. **Hero** (70vh) — Pulsing gold ring, collection name, "The Art of Everyday Luxury"
2. **Craftsmanship Section** — 2-column grid with 4 features:
   - Premium Materials, Expert Construction, Timeless Design, Limited Production
3. **Products Grid** — 14 products (sg-001..014) with AI model photos
4. **Quality Promise** (4 cards) — Lifetime Warranty, Free Repairs, Premium Packaging, Authenticity Card
5. **CTA** — "Invest in Excellence" → immersive page link

**CRITICAL: Replace placeholder names** (Foundation Blazer, Essential Trouser, etc.) with canonical names.

### 5. template-collection-kids-capsule.php

No static HTML reference exists. **Derive from other collection templates** with:
- Accent: `#FFB6C1` pink + `#E6E6FA` lavender
- Playful gradient backgrounds, rounded corners on cards
- 2 products only (kids-001, kids-002)
- Voice: "Joyful luxury, playful sophistication"
- No immersive page link (no kids immersive scene)

### 6. woocommerce/single-product.php

**Reference:** `Flagship static/single-product.html` (925 lines)

#### Layout:
```
┌───────────────────────┬────────────────────────┐
│   STICKY GALLERY      │    PRODUCT INFO         │
│   [Main Image 600px]  │    Breadcrumb           │
│   [4 Thumbnails]      │    Product Name (h1)    │
│                       │    Price                │
│                       │    Color selector (3)   │
│                       │    Size selector (XS-XXL)│
│                       │    Quantity (±)          │
│                       │    [Add to Cart] [♥]    │
│                       │    Accordion: Details   │
│                       │    Accordion: Sizing    │
│                       │    Accordion: Shipping  │
└───────────────────────┴────────────────────────┘
│            Related Products (4 cards)            │
└──────────────────────────────────────────────────┘
```

- Gallery: AI model photos (front as main, back + detail as thumbnails)
- Size buttons: `border: 1px solid rgba(255,255,255,0.2)`, active = collection accent
- Accordion: CSS-only toggle with `+`/`−` indicator
- Add to cart: full-width button with collection accent background
- Related: 4-card grid using same product card component

### 7. template-about.php

**Reference:** `Flagship static/about.html` (608 lines)

#### Sections:
1. **Hero** — "Born in Oakland, Built with Love"
2. **Story Sections** (2) — Alternating image/text grid (`.reverse` class flips order)
3. **Timeline** — 2019→2024, 4 milestones, vertical center line with dots
4. **Values Grid** (4 cards) — Authenticity, Craftsmanship, Community, Evolution
5. **Founder Section** — 1/3 + 2/3 grid with signature quote

### 8. template-contact.php

**Reference:** `Flagship static/contact.html` (346 lines)

#### Sections:
1. **Contact Info** — Location: Oakland, CA | Email: hello@skyyrose.co | Social: @skyyrose
2. **Contact Form** — Name, email, subject dropdown, message, submit button
3. **FAQ Accordion** (5 items) — Shipping, returns, sizing, international, limited edition

### 9. WooCommerce Cart Override

**Reference:** `Flagship static/cart.html` (670 lines)

#### Layout:
```
┌───────────────────────────┬──────────────────┐
│   CART ITEMS LIST         │  ORDER SUMMARY    │
│   [Image] Name Qty Price  │  Subtotal         │
│   [Image] Name Qty Price  │  Shipping         │
│   ...                     │  Promo Code       │
│                           │  ─────────────    │
│                           │  Total            │
│                           │  [Checkout]       │
└───────────────────────────┴──────────────────┘
```

- Cart item: 150px image + details + price/remove (3-column grid)
- Empty cart state: "Your cart is empty" with CTA to shop
- Sticky order summary sidebar (400px)
- Promo code input field
- Free shipping threshold: $150
- JS: uses `skyyrose_cart` localStorage key for SPA cart bridge

### 10. WooCommerce Checkout Override

**Reference:** `Flagship static/checkout.html` (813 lines)

#### Layout:
- Minimal navbar (logo + "🔒 Secure Checkout" badge)
- 4-step progress indicator: Cart ✓ → Information → Payment → Confirmation
- Contact info section
- Shipping address form
- Shipping methods: Standard $15 | Express $25 | Overnight $45
- Payment form: card number, name, expiry, CVV
- Sticky order summary sidebar (420px)
- Success modal with generated order number (SR-2025-XXXXXX)
- Tax rate: 8.75%, free standard shipping over $150

### 11. 404.php

No static reference. **Create branded 404 page:**
- Dark background matching site theme
- Large "404" in Playfair Display with gold gradient
- "Page Not Found" subtext
- Collection quick links (3 cards)
- "Return Home" CTA button

---

## Immersive Interactive Pages (Image-Based Scenes)

**CRITICAL CHANGE:** These pages use **high-resolution AI scene images with interactive product hotspots** — NOT Three.js WebGL rendering. The scenes are rich, cinematic photographs with clickable hotspot markers overlaid via CSS/JS.

### Design Reference: drakerelated.com

The immersive pages should follow the interaction pattern of **drakerelated.com** — Drake's official lifestyle site that uses room-based exploration with hotspot beacons:

- **Full-screen scene image** as backdrop (responsive, covers viewport)
- **Hotspot beacons** positioned via **percentage-based coordinates** (e.g., 28.9% X, 59.3% Y) — responsive across all screen sizes
- **Directional indicators** on beacons (left/right arrows showing navigation flow)
- **Room-to-room navigation** — clicking a beacon transitions to a new scene view
- **Smooth transitions** between scene views (fade/crossfade, not hard cuts)
- **Minimal UI overlay** — the scene image is the star, UI is glass/transparent
- **Products discoverable through exploration**, not traditional grid browsing

The SkyyRose version adapts this pattern: instead of rooms in a house, the user explores **themed collection environments** (Garden, Ballroom, Runway) with product hotspots that reveal purchase panels.

### Scene Architecture

Each immersive page follows this pattern:

```
┌─────────────────────────────────────────────────────────────┐
│  FULL-SCREEN SCENE IMAGE (cover, parallax-scroll)           │
│                                                             │
│     ⊕ hotspot 1 (product)     ⊕ hotspot 2 (product)       │
│                                                             │
│              ⊕ hotspot 3 (product)                          │
│                                                             │
│  [Navigation arrows ← →] to switch between scene views     │
├─────────────────────────────────────────────────────────────┤
│  GLASSMORPHISM PRODUCT PANEL (slide-up on hotspot click)    │
│  ┌──────┬──────────────────────────────────────────────┐    │
│  │ IMG  │  Product Name (canonical)                     │    │
│  │      │  $XXX   Sizes: XS S M L XL XXL              │    │
│  │      │  [Add to Cart]  [View Details →]             │    │
│  └──────┴──────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  FILM GRAIN + VIGNETTE OVERLAY                              │
│  COLLECTION TAB BAR (fixed bottom)                          │
└─────────────────────────────────────────────────────────────┘
```

### Hotspot Design (drakerelated.com Product-In-Scene Pattern)

**CRITICAL:** Hotspots are NOT abstract floating dots on a generic background. The products themselves are **visible IN the scene image** — a crewneck draped on an iron garment rack, joggers laying across a velvet chair, a bomber jacket on a mannequin, shorts folded on a stone pedestal. The hotspot beacon sits directly ON the visible product.

This is the drakerelated.com approach: their hotspot is literally a shirt on a rack, sneakers on a shelf, a hoodie laying across a bed. The scene image is composed with products placed naturally in the environment.

#### Hotspot Beacon (sits on visible product)
```css
.hotspot {
  position: absolute;
  width: 32px; height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid var(--collection-accent);
  cursor: pointer;
  animation: hotspot-pulse 2s ease-in-out infinite;
  backdrop-filter: blur(4px);
}
.hotspot::after {
  content: '+';
  color: var(--collection-accent);
  font-size: 18px;
  display: flex; align-items: center; justify-content: center;
}
@keyframes hotspot-pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0.4); }
  50% { transform: scale(1.1); box-shadow: 0 0 0 12px rgba(var(--accent-rgb), 0); }
}
```

#### Hotspot Click Behavior (DUAL action)
Each hotspot does TWO things:
1. **Quick panel** — Glassmorphism slide-up panel with product thumbnail, name, price, sizes, add-to-cart
2. **"View Details →" link** — Links to the **collection landing page** (`/collection/black-rose/`) OR the **single product page** (`/product/{slug}/`) depending on context

```html
<a href="/collection/black-rose/" class="hotspot" style="left: 34.2%; top: 48.7%;"
   data-sku="br-001" data-name="BLACK Rose Crewneck" data-price="$120">
  <span class="hotspot-beacon">+</span>
</a>
```

The `<a>` tag wrapping ensures SEO crawlability and keyboard navigation. JS intercepts the click to show the quick panel first; the "View Details →" button inside the panel follows the href.

### Scene Images (AI-Generated with Products IN Scene)

**CRITICAL:** The scene images must be composed with **actual SkyyRose products placed naturally in the environment** — on racks, mannequins, pedestals, furniture, laid across surfaces. Products are part of the photograph, not overlaid digitally. The hotspot beacons simply mark where to look.

The owner has provided reference images for each scene. Agents must regenerate these scenes at production resolution (3840x2160) combining the reference angles and compositing SkyyRose product assets into the environment.

#### BLACK ROSE — "The Garden"

**Reference image:** Gothic garden with wrought-iron garment racks, white/dark roses, rain-slicked cobblestone path, cathedral backdrop, moody atmospheric lighting

- **Scene 1 (main):** Garden entrance with iron arch, garment racks displaying Black Rose products, rose bushes, stone benches, rain effect
- **Products IN the scene (visible, not overlaid):**
  - br-001 crewneck **draped on an iron garment rack** (left side)
  - br-004 hoodie **hanging from a wrought-iron hook** on the arch
  - br-005 signature hoodie **laid across a stone bench** among rose petals
  - br-006 sherpa jacket **on a dress mannequin** near the cathedral wall
  - br-008 hooded dress **displayed on a tall mannequin** at end of cobblestone path
- **Hotspot beacons:** One pulsing beacon on each visible product — 5 total
- **Each hotspot links to:** `/collection/black-rose/` (collection landing) with `#product-{sku}` anchor, OR `/product/{slug}/` (product detail page)
- **Mood:** Mysterious, rainy, moonlit — dark romance

#### LOVE HURTS — "The Ballroom"

**Reference images (2 — combine into dual-view scene):**

1. **Baroque ballroom** — Ornate gold/crimson stained glass windows, crystal chandeliers with candles, marble floor scattered with rose petals, glass dome centerpiece with rose bush, tiered platform/stage
2. **Candlelit manor** — Teal-lit abandoned manor, large chandelier, glowing rose under glass dome on red pedestal, garments on mannequins, dark columns

- **Scene 1 (main — ballroom):**
  - lh-004 varsity jacket **draped over an ornate gold chair** near the stained glass
  - lh-005 bomber jacket **on a dress mannequin** on the tiered stage platform
  - lh-001 The Fannie **laid across a velvet chaise lounge** scattered with rose petals
- **Scene 2 (alt view — manor):**
  - lh-002 joggers **folded on a dark wooden pedestal** near the glowing rose dome
  - lh-003 basketball shorts **hanging from a wrought-iron coat stand** by the columns
- **Navigation:** Arrow buttons or drag/swipe to transition between views
- **Each hotspot links to:** `/collection/love-hurts/` or `/product/{slug}/`
- **Mood:** Dramatic, passionate, candlelit warmth — baroque grandeur

#### SIGNATURE — "The Runway" (Multi-Room — drakerelated.com style)

**14 products = 3 scene rooms** with arrow/swipe navigation between them, exactly like drakerelated.com's room transitions (Studio → Bedroom → Closet). Each room holds 4-5 products max for a clean, browsable layout.

**Reference images (3 scenes):**

1. **The Runway** (Bay Bridge) — Glass-walled fashion venue, massive floor-to-ceiling windows, Bay Bridge panorama through the back wall, white runway extending toward the bridge, **garment racks flanking both sides** with clothing already displayed, chrome front-row seating, industrial overhead lighting rig. First-person POV walking down the runway.
2. **The Showroom** (Grand hall) — Wide-angle fashion showroom, runway center, massive glass back wall with Golden Gate Bridge panorama, display screens on walls, product display cases flanking the runway, palm trees, luxury fixtures.
3. **The Fitting Room** (Intimate) — To be generated: intimate glass-walled dressing area with mirrors, gold-accented furniture, a clothing rack, and the bridge visible through a side window. Warm lighting, premium feel.

##### Room 1: "The Runway" (entry view)
- sg-001 The Bay Set **hanging on the left garment rack** (closest to camera)
- sg-002 Stay Golden Set **hanging on the right garment rack** (near the windows)
- sg-003 The Signature Tee **laid flat on a front-row chrome chair**
- sg-004 The Signature Tee — White **on a mannequin** at the runway entrance
- sg-005 Stay Golden Tee **draped over the runway pedestal edge**
- **Navigation arrow →** at right edge transitions to The Showroom

##### Room 2: "The Showroom" (middle view)
- sg-006 Mint & Lavender Hoodie **on a mannequin** in a glass display case (left side)
- sg-009 The Sherpa Jacket **on a mannequin** in a glass display case (right side)
- sg-010 The Bridge Series Shorts **folded on a brushed-gold shelf** between cases
- sg-013 Mint & Lavender Crewneck Set **displayed on a mannequin pair** near the panorama wall
- sg-014 Pastel Chevron Tracksuit Set **on a styled display table** center stage
- **Navigation ← →** arrows to go back to Runway or forward to Fitting Room

##### Room 3: "The Fitting Room" (end view)
- sg-007 The Signature Beanie **on a hat stand** beside the mirror
- sg-008 The Signature Beanie **laid on a velvet cushion** on a gold accent chair
- sg-011 The Signature Beanie — Grey **hanging from a wall hook** near the window
- sg-012 The Signature Beanie — Orange **on a floating shelf** with the bridge view behind
- **Navigation ←** arrow back to The Showroom

- **Each hotspot links to:** `/collection/signature/` or `/product/{slug}/`
- **Room transition:** Smooth crossfade (0.6s ease) between scenes, matching drakerelated.com's feel
- **Mood:** Elevated, sun-drenched, prestigious — Bay Area luxury, natural light flooding through glass

### Scene Interaction JavaScript

```javascript
// Scene viewer with hotspots
class ImmersiveScene {
  constructor(containerId, scenes, products) {
    this.container = document.getElementById(containerId);
    this.scenes = scenes;      // Array of { src, hotspots: [{x, y, sku}] }
    this.products = products;  // Product data from WooCommerce
    this.currentView = 0;
  }

  renderHotspots() {
    // Position absolute hotspot markers on scene image
    // Click handler opens product panel
  }

  switchView(direction) {
    // CSS transition between scene views
    // Fade or slide animation
  }

  openProductPanel(sku) {
    // Slide-up glassmorphism panel with product info
    // Product image, name, price, sizes, add-to-cart
  }
}
```

### Glassmorphism UI Panels (from preorder-gateway pattern)

```css
.scene-panel {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  max-height: 50vh;
  background: rgba(10, 10, 10, 0.92);
  backdrop-filter: blur(40px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  transform: translateY(100%);
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.scene-panel.open { transform: translateY(0); }
```

### Vignette Overlay (all immersive pages)

```css
.vignette {
  position: fixed; inset: 0;
  pointer-events: none;
  background: radial-gradient(ellipse at center, transparent 35%, rgba(2, 0, 4, 0.8));
  z-index: 89;
}
```

---

## Pre-Order Gateway

**Reference:** `wp-playground/SKyyRose Flagship/preorder-gateway.html`

**Template:** `template-preorder-gateway.php`

### Structure:
1. **Loading screen** — Brand logo (breathe animation), progress bar, italic loading text
2. **Fixed navbar** — Glass effect, brand mark + text, nav links, cart button with count badge
3. **Exclusive member banner** — Sign-in CTA for early access, auth state toggle
4. **Collection tabs** — All | Black Rose | Love Hurts | Signature (fixed bottom UI)
5. **Product grid** — `grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))`
6. **Product modal** — 360° preview area, name, price, sizes, add-to-cart + wishlist
7. **Cart sidebar** — Slide-in from right (400px), items list, total, checkout button
8. **Sign-in panel** — Slide-in from right (420px), email/password, member perks list

### Key Design Patterns:
- Fonts: Playfair Display (display), Bebas Neue (UI buttons), Space Mono (labels), Cormorant Garamond (body)
- Ultra-dark: `--db: #020004` background
- Glass panels: `rgba(255,255,255,0.03)` + `backdrop-filter: blur(20px)`
- Accent colors per tab: Rose Gold (all), Crimson (black-rose), Rose (#E91E63 love-hurts), Gold (signature)
- Film grain at 2% + vignette overlay

---

## AI Photography Integration

This theme uses AI-generated fashion model images showing real models wearing the EXACT SkyyRose products. See `knowledge/photo_generation.md` for the complete pipeline.

### Image Workflow for WordPress

```
1. Generate fashion model images
   → python skyyrose_elite_studio.py produce {sku}
   → OR node skyyrose/build/generate-fashion-models.js {sku}

2. Optimize for web
   → node skyyrose/build/optimize-images.js
   → Outputs: WebP (primary) + JPEG (fallback) in 4 sizes (480/768/1024/2048px)

3. Upload to WordPress Media Library
   → wpcom-mcp-content-authoring (media.create)
   → Alt text: "{Product Name} — Model wearing {garment type}"

4. Reference in templates
   → Use <picture> with srcset for responsive delivery
   → WebP source first, JPEG fallback
```

### Image Placement Map

| Image Type | Template | Placement |
|-----------|----------|-----------|
| Fashion model (front) | Collection landing, product hero, lookbook grid | Primary product image |
| Fashion model (back) | Product detail thumbnails, lookbook secondary | Hover/alternate view |
| Scene backgrounds | Immersive pages | Full-screen backdrop with hotspots |
| Ad creatives | Homepage hero, marketing banners | Promotional sections |

### Responsive Image Pattern (WordPress PHP)

```php
<picture>
  <source srcset="<?php echo get_template_directory_uri(); ?>/assets/images/products/<?php echo $sku; ?>/<?php echo $sku; ?>-model-front.webp" type="image/webp">
  <img
    src="<?php echo get_template_directory_uri(); ?>/assets/images/products/<?php echo $sku; ?>/<?php echo $sku; ?>-model-front.jpg"
    alt="<?php echo esc_attr($product_name); ?> — Model wearing <?php echo esc_attr($garment_type); ?>"
    width="1024" height="1536"
    loading="lazy"
    class="product-image"
  >
</picture>
```

### Product Names (Canonical — NEVER abbreviate)

Full mapping in `knowledge/photo_generation.md`. Quick reference:

| SKU | Canonical Name |
|-----|---------------|
| br-001 | BLACK Rose Crewneck |
| br-002 | BLACK Rose Joggers |
| br-003 | BLACK is Beautiful Jersey |
| br-004 | BLACK Rose Hoodie |
| br-005 | BLACK Rose Hoodie — Signature Edition |
| br-006 | BLACK Rose Sherpa Jacket |
| br-007 | BLACK Rose × Love Hurts Basketball Shorts |
| br-008 | Women's BLACK Rose Hooded Dress |
| lh-001 | The Fannie |
| lh-002 | Love Hurts Joggers |
| lh-003 | Love Hurts Basketball Shorts |
| lh-004 | Love Hurts Varsity Jacket |
| lh-005 | Love Hurts Bomber Jacket |
| sg-001 | The Bay Set |
| sg-002 | Stay Golden Set |
| sg-003 | The Signature Tee |
| sg-004 | The Signature Tee — White |
| sg-005 | Stay Golden Tee |
| sg-006 | Mint & Lavender Hoodie |
| sg-007 | The Signature Beanie |
| sg-008 | The Signature Beanie |
| sg-009 | The Sherpa Jacket |
| sg-010 | The Bridge Series Shorts |
| sg-011 | The Signature Beanie — Grey |
| sg-012 | The Signature Beanie — Orange |
| sg-013 | Mint & Lavender Crewneck Set |
| sg-014 | Pastel Chevron Tracksuit Set |
| kids-001 | Kids Colorblock Hoodie Set — Purple/Pink |
| kids-002 | Kids Colorblock Hoodie Set — Black/Red/White |

---

## MCP Tools Workflow

### Reading (no confirmation needed)
- `wpcom-mcp-content-authoring` action="list" — discover operations
- `wpcom-mcp-content-authoring` action="describe" — get operation schema
- `wpcom-mcp-site-editor-context` action="get" — theme presets, blocks, styles
- `wpcom-mcp-site-settings` — site configuration
- `wpcom-mcp-site-plugins` — installed plugins
- `wpcom-mcp-site-statistics` — traffic and performance data

### Writing (ALWAYS confirm with user first)
- `wpcom-mcp-content-authoring` action="execute" — create/update/delete content
- Include `user_confirmed` param with user's confirmation response

### Mandatory Content Creation Workflow

```
STEP 1: Get design context
  → wpcom-mcp-site-editor-context (theme.active → theme.presets)

STEP 2: Browse patterns
  → wpcom-mcp-content-authoring (patterns.list → patterns.get)

STEP 3: Compose content
  → Use preset SLUGS not hardcoded values
  → CORRECT: has-gold-color, has-crimson-background-color
  → WRONG:   style="color: #D4AF37"

STEP 4: Create as DRAFT
  → wpcom-mcp-content-authoring (pages.create, status: "draft")
  → NEVER publish without explicit user approval

STEP 5: Show links
  → Edit: https://skyyrose.co/wp-admin/post.php?post={id}&action=edit
  → Preview: https://skyyrose.co/?p={id}&preview=true

STEP 6: Check warnings
  → Read _content_warnings in response
  → If markup was stripped, retry with simpler blocks
```

---

## Brand Voice

- **Tagline:** "Where Love Meets Luxury"
- **Tone:** Sophisticated, bold, intimate — not corporate
- **Copy style:** Short, punchy sentences. Address the customer directly. Evoke emotion.
- **Collection voices:**
  - BLACK ROSE: Gothic elegance, dark romance, mystery
  - LOVE HURTS: Dramatic, passionate, fearless
  - SIGNATURE: Elevated, confident, refined
  - KIDS CAPSULE: Joyful luxury, playful sophistication

---

## Premium Theme Marketplace Requirements

This theme must be **complete enough to sell on a premium theme marketplace** (e.g., ThemeForest). The quality bar is set by sites like **drakerelated.com** — every element must be polished, functional, and demonstrate the theme's full capabilities.

### Required Theme Components
- [ ] **Homepage** — Hero with animated orbs, collection showcase, featured products, brand story, newsletter
- [ ] **Collection Landing Pages** (4) — One per collection with lookbook grid, product cards, mood imagery, floating effects
- [ ] **Product Detail Pages** — AI model gallery (front/back) + flat-lay product shots, size guide, add-to-cart, related products
- [ ] **Pre-order Gateway** — Glassmorphism UI, collection tabs, product modal, cart sidebar, member sign-in
- [ ] **Immersive Experiences** (3) — Scene-image exploration with product hotspots (drakerelated.com room pattern)
- [ ] **About Page** — Brand story, founder narrative, timeline, values
- [ ] **Contact Page** — Form, social links, FAQ accordion
- [ ] **Blog/Journal** — Fashion editorial posts with rich media
- [ ] **Cart & Checkout** — WooCommerce-powered, on-brand dark styling, multi-step checkout
- [ ] **404 Page** — Branded, helpful, on-theme

### Demo Content (All 28 Products)
Every product must be populated with:
- [ ] Canonical product name (from product mapper)
- [ ] Full description + short description (from the product registry: `python -m skyyrose.core.product <sku>` → `content`)
- [ ] AI fashion model images (front + back views)
- [ ] Flat-lay product photos (clean background, square 1:1 ratio) for grid display
- [ ] Collection assignment
- [ ] SEO meta description
- [ ] Social media copy (Instagram + TikTok)
- [ ] Proper categorization and tagging

### Product Display (drakerelated.com Premium Feel)

The product display must feel premium like drakerelated.com but using our **AI fashion model imagery** (models wearing real SkyyRose products — already generated):

- **Product cards**: Clean, minimal — AI model photo + name + price. Generous whitespace. Dark card background.
- **Primary imagery**: AI fashion model photos (front view) — models wearing the exact product. These are already generated and look beautiful.
- **Hover/secondary**: AI model back view or alternate angle on hover
- **Aspect ratio**: Portrait (3:4) for product cards matching model photo proportions
- **Typography**: Large product name (Inter 600), price below in collection accent color, minimal secondary info
- **Scarcity signals**: "Limited Edition" badges, "Only X Left" when stock is low, "Pre-Order" for upcoming drops
- **Craft descriptions**: Emphasize real technique from ML-verified overrides — "embroidered", "silicone appliqué", "laser-engraved leather" (use actual brandingTech from product overrides, NOT generic marketing copy)
- **SOLD OUT state**: Dark overlay + "SOLD OUT" badge (for pre-launch products awaiting drop)
- **Hover effect**: Subtle `translateY(-8px)` + shadow, quick-view/wishlist/cart action buttons fade in from bottom
- **Grid spacing**: Generous gaps (24px+), breathing room like drakerelated.com — NOT cramped grid

### Theme Quality Standards
- [ ] WCAG 2.2 AA accessible (contrast, ARIA, keyboard nav)
- [ ] Mobile-first responsive (320px → 2560px)
- [ ] Core Web Vitals optimized (LCP < 2.5s, CLS < 0.1, INP < 200ms)
- [ ] SEO-ready (structured data, meta tags, sitemap)
- [ ] Cross-browser tested (Chrome, Safari, Firefox, Edge)
- [ ] RTL-ready layout structure
- [ ] Print stylesheet for product pages
- [ ] Schema.org Product markup on all product pages

---

## Critical Rules

1. **STATIC HTML IS LAW** — Every PHP template must match the static HTML design exactly.
2. **INTER + PLAYFAIR DISPLAY** — These are the ONLY body/heading fonts. Never use Montserrat.
3. **DARK THEME DEFAULT** — Background is `#0A0A0A`, not white. Film grain overlay on all pages.
4. **DRAFT FIRST** — Never publish directly. Always create as draft.
5. **PRESET SLUGS** — Use design token slugs in WordPress blocks, never hardcoded hex/px.
6. **CONFIRM WRITES** — Describe the action, wait for user OK.
7. **CHECK WARNINGS** — Read `_content_warnings` after every save.
8. **REST ROUTE** — Use `index.php?rest_route=` NOT `/wp-json/`.
9. **NO SECRETS** — Never include API keys, passwords, or tokens in content.
10. **MEDIA FIRST** — Upload images via media tools before referencing in content.
11. **EXACT PRODUCT NAMES** — Use canonical names from product mapper, NEVER abbreviate.
12. **AI IMAGES REQUIRED** — Every product page must feature AI fashion model imagery.
13. **IMAGE-BASED IMMERSIVE** — Use scene images with hotspots, NOT Three.js WebGL.
14. **COLLECTION FLOATING EFFECTS** — Black Rose: floating roses 🥀🌹, Love Hurts: floating hearts ♥, Signature: art deco pattern overlay.
15. **QUALITY GATE** — AI images must pass dual-provider quality check before upload.
16. **BRAND CONSISTENCY** — Every page must feel like the same dark luxury brand.

## Deployment Checklist

Before marking any story as GREEN:
- [ ] Matches static HTML design reference exactly
- [ ] Uses Inter + Playfair Display fonts (not Montserrat)
- [ ] Dark theme (#0A0A0A) with film grain overlay
- [ ] Content created as draft (not published)
- [ ] Design tokens used (no hardcoded values in WP blocks)
- [ ] Brand voice matches collection personality
- [ ] Mobile responsive (768px and 480px verified)
- [ ] Images have alt text (accessibility)
- [ ] No `_content_warnings` in API response
- [ ] AI model images uploaded and referenced (front + back views)
- [ ] Product names match canonical mapper exactly
- [ ] Collection floating effects present (roses/hearts/art deco)
- [ ] Immersive pages use scene images with hotspots (not WebGL)
- [ ] User shown edit + preview URLs
