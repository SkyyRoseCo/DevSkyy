> SUPERSEDED 2026-07-10/11 — fonts now per SOT.md → typography.json (Archivo / Hanken Grotesk / Anton / Cinzel / Inter + bespoke collection name-scripts; zero-CDN self-hosted woff2). Font/CDN references below are historical.

# DevSkyy Dashboard — Design System

## Brand Identity

| Element | Value |
|---------|-------|
| Brand | SkyyRose |
| Tagline | None authorised (founder decision 2026-10-06) |
| Aesthetic | Dark luxury, rose gold accents, glassmorphism |
| Feel | Bold, premium, urban-elevated |

---

## Color Palette

### Brand Colors (Tailwind: `luxury-*`)

| Token | Hex | Usage |
|-------|-----|-------|
| `luxury-rose-gold` | `#B76E79` | Primary brand color, CTAs, highlights |
| `luxury-rose-dark` | `#8B5465` | Hover states, borders |
| `luxury-rose-light` | `#D4A5B0` | Subtle backgrounds, muted text |
| `luxury-charcoal` | `#1A1A1A` | Primary background |
| `luxury-graphite` | `#2D2D2D` | Card backgrounds, elevated surfaces |

### Accent Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Gold | `#D4AF37` | Premium badges, accents |
| Rose 400 | `#fb7185` | Alerts, warm highlights |
| Rose 500 | `#f43f5e` | Destructive actions |
| Rose 600 | `#e11d48` | Active states |

### Semantic Colors (CSS Variables — auto dark mode)

These use HSL values via CSS custom properties in `globals.css`:

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `--background` | white | `#0a0a0a` | Page background |
| `--foreground` | near-black | near-white | Text |
| `--card` | white | `#0a0a0a` | Card surfaces |
| `--muted` | gray-50 | gray-900 | Subdued elements |
| `--border` | gray-200 | gray-800 | Borders |
| `--primary` | near-black | near-white | Primary buttons |
| `--destructive` | red | dark-red | Delete actions |
| `--sidebar-*` | Custom sidebar palette | Custom sidebar palette | Sidebar nav |

### Chart Colors

5 chart colors available as `--chart-1` through `--chart-5`. Light and dark variants defined in `globals.css`.

### Usage in Tailwind

```tsx
// Brand colors
<div className="bg-luxury-rose-gold text-white" />
<div className="border-luxury-rose-dark" />

// Semantic colors (auto dark mode)
<div className="bg-background text-foreground" />
<div className="bg-card border-border" />
<div className="text-muted-foreground" />
```

---

## Typography

### Font Stack

| Role | Font | Fallback | Tailwind Class | CSS Variable |
|------|------|----------|----------------|-------------|
| Display / Headings | Playfair Display | Georgia, serif | `font-display` | `--font-playfair` |
| Body | Cormorant Garamond | Georgia, serif | `font-body` | `--font-cormorant` |
| Monospace / Code | Space Mono | Courier New, monospace | `font-mono` | `--font-space-mono` |

### Heading Styles

All headings (`h1`–`h6`) use Playfair Display, `font-weight: 700`, `letter-spacing: -0.02em`.

### Body Text

Body text defaults to Cormorant Garamond (set on `<body>` in `globals.css`).

---

## Spacing

### Golden Ratio Utilities

| Token | Value | Usage |
|-------|-------|-------|
| `phi` | `1.618rem` (~26px) | Standard spacing unit |
| `phi-2` | `2.618rem` (~42px) | Section padding |
| `phi-3` | `4.236rem` (~68px) | Hero spacing |

### Standard Tailwind

Use standard Tailwind spacing (`p-4`, `gap-6`, `m-8`) for general layout. Reserve `phi-*` values for luxury/brand sections.

---

## Component Library

### shadcn/ui (Primary)

All UI primitives come from shadcn/ui, built on Radix UI:

| Component | File | Usage |
|-----------|------|-------|
| Button | `components/ui/button.tsx` | All clickable actions |
| Card | `components/ui/card.tsx` | Content containers |
| Dialog | `components/ui/dialog.tsx` | Modals |
| Tabs | `components/ui/tabs.tsx` | Section switching |
| Badge | `components/ui/badge.tsx` | Status labels |
| Input / Label | `components/ui/input.tsx` | Form fields |
| Switch | `components/ui/switch.tsx` | Toggles |
| Separator | `components/ui/separator.tsx` | Dividers |
| Sheet | `components/ui/sheet.tsx` | Side panels |
| Sidebar | `components/ui/sidebar.tsx` | Admin navigation |
| Skeleton | `components/ui/skeleton.tsx` | Loading states |
| Tooltip | `components/ui/tooltip.tsx` | Hover hints |
| Chart | `components/ui/chart.tsx` | Recharts wrapper |

### Adding New Components

```bash
npx shadcn@latest add [component-name]
```

This generates into `components/ui/` with the project's theme automatically applied.

---

## Custom Utilities (globals.css)

### Glassmorphism

```tsx
// Standard glass
<div className="glass" />
// backdrop-blur-xl, bg-white/[0.03], border-white/10, shadow

// Premium glass (with gradient overlay)
<div className="glass-premium" />
```

### Gradient Text

```tsx
<h1 className="luxury-text-gradient">SkyyRose</h1>
// Rose gold gradient: #D4A5B0 → #B76E79 → #8B5465

<span className="gradient-text">Highlighted</span>
// Rose gradient: rose-400 → rose-500 → rose-600

<span className="gradient-text-vibrant">Vibrant</span>
// Cyan → Blue → Purple
```

### Glow Effects

```tsx
<div className="glow-rose" />   // Rose gold box-shadow
<div className="glow-blue" />   // Blue box-shadow
<div className="glow-gold" />   // Gold box-shadow
<div className="pulse-glow" />  // Animated rose pulse
```

### Animations

```tsx
<div className="shimmer" />       // Horizontal shimmer sweep
<div className="float" />         // Gentle vertical float (6s cycle)
<div className="fade-in-up" />    // Fade in + slide up (0.6s)
<div className="animated-border" /> // Rose gold gradient border
```

### Selection Color

Text selection renders with rose gold tint (`rgba(183, 110, 121, 0.3)`).

### Custom Scrollbar

Dark theme scrollbar — dark track, gray thumb, lighter on hover.

---

## Dark Mode

- **Implementation**: Class-based (`dark:` prefix in Tailwind)
- **Provider**: `next-themes` (installed, toggle available)
- **Default**: Admin dashboard uses dark theme by default (`bg-gray-950`)
- **CSS Variables**: All semantic colors have light and dark variants in `globals.css`

```tsx
// This automatically adapts to dark mode:
<div className="bg-background text-foreground border-border" />

// Manual dark overrides:
<div className="bg-white dark:bg-gray-900" />
```

---

## Admin Dashboard Specifics

The admin dashboard (`/admin/*`) uses a dark-on-dark aesthetic:

| Element | Class |
|---------|-------|
| Page background | `bg-gray-950` |
| Sidebar | `bg-gray-900/50 backdrop-blur-sm` |
| Cards | `bg-gray-900 border-gray-800` |
| Headers | `bg-gray-900/50 backdrop-blur-sm border-gray-800` |
| Text primary | `text-white` |
| Text secondary | `text-gray-400` |
| Status online | `bg-green-500 animate-pulse` (2px dot) |

---

## Icons

**Library**: Lucide React (`lucide-react`)

```tsx
import { Home, Settings, BarChart3 } from 'lucide-react';

<Home className="h-4 w-4" />
<Settings className="h-5 w-5 text-gray-400" />
```

Standard sizes: `h-4 w-4` (inline), `h-5 w-5` (nav), `h-6 w-6` (feature).

---

## Charts

**Library**: Recharts 3.7, wrapped via `components/ui/chart.tsx`

Dashboard charts use these patterns:
- `ProviderPerformanceChart` — Bar chart for LLM win rates
- `CompetitionTrendChart` — Line chart for competition trends
- `AgentStatusChart` — Donut chart for agent status
- `PipelineMetricsChart` — Area chart for pipeline throughput

All charts defined in `components/dashboard/analytics-charts.tsx`.

---

## Do's and Don'ts

| Do | Don't |
|----|-------|
| Use `luxury-rose-gold` for brand accents | Don't use raw `#B76E79` inline |
| Use CSS variables for semantic colors | Don't hardcode light/dark hex values |
| Use shadcn/ui components | Don't install MUI, Chakra, or Ant Design |
| Use Tailwind utilities | Don't write CSS modules or styled-components |
| Use `font-display` for headings | Don't change the font stack |
| Use `glass` / `glass-premium` for overlays | Don't manually write backdrop-blur chains |
| Use Lucide for icons | Don't mix icon libraries |
