# Contributing to DevSkyy Dashboard

> **Last Updated:** 2026-02-20 | **Source:** package.json, .env.example

Enterprise AI Platform - Next.js 16 + React 19 + TypeScript + Vercel

---

## Table of Contents

- [Development Workflow](#development-workflow)
- [Available Scripts](#available-scripts)
- [Environment Setup](#environment-setup)
- [Testing Procedures](#testing-procedures)
- [Code Quality](#code-quality)
- [Deployment](#deployment)

---

## Development Workflow

### Prerequisites

- **Node.js:** 22.x or later
- **Package Manager:** pnpm (v10.x)
- **Git:** Latest version
- **Fly CLI:** `brew install flyctl` (for deployments; app `devskyy-dashboard`)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/The-Skyy-Rose-Collection-LLC/DevSkyy.git
cd DevSkyy/frontend

# 2. Install dependencies
pnpm install

# 3. Set up environment variables
cp ../.env.example .env.local
# Edit .env.local with your API keys

# 4. Start development server
pnpm dev
```

The dashboard will be available at http://localhost:3000

---

## Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| **Development** |
| `dev` | `next dev` | Start Next.js development server with hot reload |
| `build` | `next build` | Create optimized production build |
| `start` | `next start` | Start production server (after build) |
| `lint` | `next lint` | Run ESLint to check code quality |
| **Testing** |
| `test:e2e` | `playwright test` | Run end-to-end tests with Playwright |
| `test:e2e:ui` | `playwright test --ui` | Run E2E tests with interactive UI |
| **Deployment** |
| `deploy` | `flyctl deploy --config fly.toml --ha=false` | Type-check, lint, test, build, then deploy to Fly (`devskyy-dashboard`) |
| `deploy:prod` / `deploy:auto` / `deploy:auto:prod` | `npm run deploy` | Aliases of `deploy` (single Fly production app) |

### Usage Examples

**Development:**
```bash
# Start dev server
pnpm dev

# In another terminal, run tests
pnpm test:e2e:ui
```

**Building:**
```bash
# Build and verify
pnpm build
pnpm start

# Lint code
pnpm lint
```

**Deployment:**
```bash
# Quick deploy to preview
pnpm deploy

# Deploy to production with automated checks
pnpm deploy:auto:prod
```

**Environment Management:**
```bash
# Non-secret runtime config lives in fly.toml [env]; secrets are Fly secrets
flyctl secrets list -a devskyy-dashboard
```

---

## Environment Setup

### Required Environment Variables

Create `.env.local` with the following variables:

#### Application Settings
```bash
# Environment
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
```

#### API URLs
```bash
FRONTEND_URL=http://localhost:3000
API_URL=http://localhost:8000
```

#### AI Provider API Keys
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
GOOGLE_AI_API_KEY=...
```

#### 3D Asset Generation
```bash
# HuggingFace (Primary)
HF_TOKEN=hf_...
HF_3D_MODEL_PRIMARY=tencent/Hunyuan3D-2
HF_3D_MODEL_FALLBACK=stabilityai/TripoSR

# Tripo3D (Fallback)
TRIPO_API_KEY=your-tripo3d-api-key

# FASHN Virtual Try-On
FASHN_API_KEY=your-fashn-api-key
```

#### WordPress/WooCommerce
```bash
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
WOOCOMMERCE_KEY=ck_...
WOOCOMMERCE_SECRET=cs_...
```

#### Security (Production)
```bash
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
JWT_SECRET_KEY=your-jwt-secret-key-64-chars-minimum

# Generate with: python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
ENCRYPTION_MASTER_KEY=your-base64-encoded-32-byte-key
```

#### Database
```bash
# Development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./devskyy.db

# Production (PostgreSQL)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/devskyy

# Connection Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

#### Optional Services
```bash
# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Klaviyo Marketing
KLAVIYO_PRIVATE_KEY=pk_xxxxxxxxxxxx
KLAVIYO_PUBLIC_KEY=pk_xxxxxxxxxxxx
KLAVIYO_LIST_ID=XXXXXX

# Stripe Payments
STRIPE_API_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Monitoring
SENTRY_DSN=https://...
PROMETHEUS_ENABLED=true
```

#### Performance Tuning
```bash
# Caching
EMBEDDING_CACHE_SIZE=1024
RESPONSE_CACHE_TTL=300
VECTOR_SEARCH_CACHE_TTL=300
RERANKING_CACHE_TTL=1800

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Parallel Processing
MAX_PARALLEL_INGESTION=5
```

### Environment Files

| File | Purpose | Tracked |
|------|---------|---------|
| `.env.example` | Template with all variables | ✅ Yes |
| `.env.local` | Local development (from Vercel) | ❌ No |
| `.env.production` | Production values (Vercel) | ❌ No |
| `.env.staging` | Staging environment | ❌ No |

### Pulling Environment Variables

```bash
# Copy the template; production secrets live in Fly (flyctl secrets list -a devskyy-dashboard)
cp .env.example .env.local
```

---

## Testing Procedures

### End-to-End Tests

We use **Playwright** for E2E testing. Tests are located in `tests/e2e/`.

#### Running Tests

```bash
# Run all tests (headless)
pnpm test:e2e

# Run with UI (interactive mode)
pnpm test:e2e:ui

# Run specific test file
pnpm test:e2e tests/e2e/settings-page.spec.ts

# Run tests in debug mode
pnpm test:e2e --debug
```

#### Writing Tests

**Example Test:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.devskyy.app/admin/feature');
    await page.waitForLoadState('networkidle');
  });

  test('should display feature correctly', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Feature Title');
    await expect(page.getByRole('button', { name: /Submit/i })).toBeVisible();
  });
});
```

#### Test Coverage

Current test files:
- `tests/e2e/settings-page.spec.ts` - Settings page (13 tests) ✅

### Manual Testing Checklist

Before submitting PR:
- [ ] All pages load without errors
- [ ] Navigation between pages works
- [ ] Forms validate correctly
- [ ] API calls succeed
- [ ] Animations smooth (60fps)
- [ ] Responsive design (320px - 1920px)
- [ ] No console errors
- [ ] Lighthouse score > 90

---

## Code Quality

### TypeScript

- **Strict mode:** Enabled
- **Type checking:** Run automatically during build
- **tsconfig.json:** Located at project root

```bash
# Manual type check
pnpm build
```

### Linting

```bash
# Run ESLint
pnpm lint

# Auto-fix issues
pnpm lint --fix
```

### Code Style

- **Immutability:** Always create new objects, never mutate
- **File size:** Max 800 lines per file
- **Function size:** Max 50 lines per function
- **No console.log:** Remove before committing
- **No hardcoded values:** Use environment variables

**Good Example:**
```typescript
// ✅ Immutable
const updatedUser = { ...user, name: newName };

// ❌ Mutation
user.name = newName;
```

### Pre-commit Hooks

Configured in `~/.claude/settings.json`:
- Auto-format with Prettier
- TypeScript type checking
- Console.log detection

---

## Deployment

### Vercel Deployment

**Project:** devskyy
**Organization:** skkyroseco
**Region:** iad1 (Washington, D.C.)

#### Manual Deployment

```bash
# Preview deployment
pnpm deploy

# Production deployment
pnpm deploy:prod
```

#### Automated Deployment (Recommended)

Includes pre-checks, build verification, and smoke tests:

```bash
# Preview with checks
pnpm deploy:auto

# Production with full checks
pnpm deploy:auto:prod
```

**Automated deployment includes:**
1. ✅ Vercel CLI check
2. ✅ Project link verification
3. ✅ Environment file check
4. ✅ TypeScript compilation
5. ✅ Next.js build
6. ✅ Deployment to Vercel
7. ✅ Smoke tests (production only)

#### Deployment Checklist

Before deploying to production:
- [ ] All tests passing
- [ ] Build succeeds locally
- [ ] No TypeScript errors
- [ ] No console.log statements
- [ ] Environment variables configured in Vercel
- [ ] PR approved and merged
- [ ] CHANGELOG updated

#### Rollback

If deployment fails:

```bash
# Option 1: Vercel Dashboard
# Go to Deployments → Previous deployment → Promote to Production

# Option 2: Git revert
git revert <commit-hash>
git push origin main

# Option 3: Disable feature flag
# Update environment variable in Vercel dashboard
```

---

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── admin/             # Admin dashboard pages
│   │   ├── page.tsx       # Main dashboard
│   │   ├── settings/      # Settings page
│   │   ├── monitoring/    # Monitoring page
│   │   ├── round-table/   # LLM competitions
│   │   ├── 3d-pipeline/   # 3D generation
│   │   └── ...            # Other admin pages
│   ├── api/               # API routes
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── 3d/               # 3D viewer components
│   ├── dashboard/        # Dashboard components
│   ├── ui/               # UI primitives
│   └── shared/           # Shared components
├── lib/                   # Utilities & services
│   ├── api/              # API clients
│   ├── autonomous/       # Autonomous agents
│   ├── vercel/           # Vercel SDK
│   ├── wordpress/        # WordPress integration
│   └── fonts.ts          # Typography system
├── tests/                 # Test files
│   └── e2e/              # Playwright E2E tests
├── public/               # Static assets
│   └── models/           # 3D model files (.glb)
├── scripts/              # Build & deploy scripts
├── docs/                 # Documentation
├── package.json          # Dependencies & scripts
├── next.config.js        # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS config
├── tsconfig.json         # TypeScript config
├── Dockerfile            # Fly image (standalone Next.js)
└── fly.toml              # Fly app config (devskyy-dashboard)
```

---

## Stack

### Core Technologies

- **Framework:** Next.js 16 (App Router)
- **UI Library:** React 19
- **Language:** TypeScript 5.9
- **Styling:** Tailwind CSS 3.4
- **Build Tool:** Turbopack
- **Package Manager:** pnpm 10.x

### Key Dependencies

- **3D Rendering:** @react-three/fiber, @react-three/drei, three.js
- **Animations:** framer-motion
- **UI Components:** Radix UI primitives
- **Forms:** Zod validation
- **Charts:** Recharts
- **Icons:** lucide-react
- **Testing:** Playwright

### Typography System

- **Display Font:** Playfair Display (headings)
- **Body Font:** Cormorant Garamond (text)
- **Mono Font:** Space Mono (code)

### Design Tokens

- **Primary Color:** Rose Gold (#B76E79)
- **Secondary Colors:** #8B5465, #D4A5B0
- **Spacing:** Golden ratio (1.618rem, 2.618rem, 4.236rem)
- **Theme:** Dark mode with luxury gradients

---

## Resources

- **Documentation:** `/docs`
- **Runbook:** `/docs/RUNBOOK.md`
- **Environment Reference:** `/.env.example`
- **Fly app:** `devskyy-dashboard` (`flyctl status -a devskyy-dashboard`)
- **Production URL:** https://www.devskyy.app

---

## Getting Help

- **Issues:** Create GitHub issue with `[frontend]` tag
- **Questions:** Ask in team Slack #devskyy-dev
- **Documentation:** Check `/docs` directory first

---

**Version:** 1.0.0
**Platform:** DevSkyy Enterprise AI
**Organization:** SkyyRose LLC
