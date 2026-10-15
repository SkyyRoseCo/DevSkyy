# DevSkyy Deployment Guide

## Vercel Integration Complete ✅

### Quick Start

```bash
# Deploy to preview
npm run deploy

# Deploy to production
npm run deploy:prod

# Automated deployment with pre-checks
npm run deploy:auto

# Automated production deployment
npm run deploy:auto:prod
```

---

## Features

### 1. Vercel SDK Integration

**Installed Packages:**
- `@vercel/analytics` - Real-time analytics
- `@vercel/speed-insights` - Performance monitoring
- `@vercel/node` - Vercel runtime utilities
- `vercel` - CLI for deployments

**Automatic Integration:**
- Analytics tracking on all pages
- Speed Insights monitoring
- Real-time performance metrics

### 2. Vercel Deployment Manager

**Location:** `/admin/vercel`

**Features:**
- View all deployments (production + preview)
- Promote preview deployments to production
- Manage environment variables
- Monitor deployment status in real-time
- View deployment logs and build events
- Manage projects and domains
- One-click rollback capabilities

**API Coverage:**
- ✅ Deployments (create, list, get, cancel, delete)
- ✅ Projects (create, update, delete, list)
- ✅ Environment Variables (CRUD operations)
- ✅ Domains (add, remove, list)
- ✅ Aliases (create, list)
- ✅ Logs & Events
- ✅ Analytics & Monitoring

### 3. WordPress Operations Manager

**Location:** `/admin/wordpress`

**Complete WordPress REST API Coverage:**

#### Content Management
- ✅ **Posts** - Create, read, update, delete, list, search
- ✅ **Pages** - Full CRUD operations
- ✅ **Categories** - Taxonomy management
- ✅ **Tags** - Tag operations
- ✅ **Comments** - Moderation and management

#### Media Management
- ✅ **Upload Media** - Direct file upload
- ✅ **Upload from URL** - Import from external URLs
- ✅ **Media Library** - List, update, delete media
- ✅ **Metadata Management** - Alt text, captions, descriptions

#### User Management
- ✅ **Create Users** - New user registration
- ✅ **Update Users** - Profile management
- ✅ **Delete Users** - With content reassignment
- ✅ **List Users** - Filter by role, search
- ✅ **Current User** - Get authenticated user info

#### Advanced Operations
- ✅ **Menu Management** - Navigation menus CRUD
- ✅ **Menu Items** - Add, remove, reorder menu items
- ✅ **Auto-Sync Collections** - Autonomous menu updates
- ✅ **Custom Taxonomies** - Custom term management
- ✅ **Post Types** - Custom post type support
- ✅ **Settings** - Site-wide configuration
- ✅ **Themes** - List themes, get active theme
- ✅ **Plugins** - List, activate, deactivate
- ✅ **Search** - Global search across all content
- ✅ **Gutenberg Blocks** - Block types and reusable blocks
- ✅ **Site Health** - Health check monitoring

---

## Environment Variables

### Required for Vercel

```bash
# .env.production
VERCEL_TOKEN=your_vercel_token_here
VERCEL_TEAM_ID=your_team_id_here (optional)
VERCEL_PROJECT_ID=your_project_id_here (optional)
```

### Required for WordPress

```bash
NEXT_PUBLIC_WORDPRESS_URL=https://skyyrose.co
NEXT_PUBLIC_WP_CONSUMER_KEY=ck_your_consumer_key
NEXT_PUBLIC_WP_CONSUMER_SECRET=cs_your_consumer_secret
```

### Feature Flags

```bash
NEXT_PUBLIC_ENABLE_AUTO_SYNC=true
NEXT_PUBLIC_ENABLE_AUTONOMOUS_AGENTS=true
```

---

## Deployment Scripts

### Manual Deployment

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod

# With specific options
vercel --prod --force --with-cache
```

### Automated Deployment

The automated deployment script (`scripts/deploy.ts`) includes:

1. **Pre-deployment Checks**
   - Vercel CLI installation check
   - Environment file validation
   - Configuration verification

2. **Build Process**
   - Full TypeScript type checking
   - Next.js production build
   - Static page generation

3. **Deployment**
   - Automatic deployment to Vercel
   - URL extraction and logging
   - Real-time progress monitoring

4. **Post-deployment Tasks**
   - Deployment readiness check
   - Smoke tests (production only)
   - Deployment logging

**Usage:**

```bash
# Preview deployment
npm run deploy:auto

# Production deployment
npm run deploy:auto:prod

# With options
tsx scripts/deploy.ts --prod --force --debug
```

**Available Flags:**
- `--prod, -p` - Deploy to production
- `--prebuilt` - Use pre-built output
- `--force` - Force new deployment
- `--skip-domain` - Skip domain checks
- `--with-cache` - Enable build cache
- `--debug` - Debug mode
- `--rollback` - Rollback to previous deployment

---

## Vercel CLI Commands

### Deployment Management

```bash
# List deployments
vercel ls

# View deployment details
vercel inspect <deployment-url>

# View deployment logs
vercel logs <deployment-url>

# Cancel deployment
vercel cancel <deployment-url>

# Remove deployment
vercel rm <deployment-url>
```

### Environment Variables

```bash
# Pull env vars from Vercel
npm run vercel:env:pull

# Push env vars to Vercel
npm run vercel:env:push

# Add env variable
vercel env add

# Remove env variable
vercel env rm <env-name>

# List env variables
vercel env ls
```

### Project Management

```bash
# Link local project to Vercel
vercel link

# View project settings
vercel project ls

# View domains
vercel domains ls

# Add domain
vercel domains add <domain>
```

---

## WordPress API Usage Examples

### Creating a Post

```typescript
import { getWordPressOperationsManager } from '@/lib/wordpress/operations-manager'

const wp = getWordPressOperationsManager()

await wp.createPost({
  title: 'My New Post',
  content: 'Post content here...',
  status: 'publish',
  categories: [1, 2],
  tags: [3, 4],
  featured_media: 123
})
```

### Uploading Media

```typescript
// From file
const file = new File([blob], 'image.jpg', { type: 'image/jpeg' })
await wp.uploadMedia(file, {
  title: 'Product Image',
  alt_text: 'Black Rose Collection'
})

// From URL
await wp.uploadMediaFromUrl('https://example.com/image.jpg', {
  title: 'External Image'
})
```

### Managing Menus

```typescript
import { getWordPressMenuManager } from '@/lib/wordpress/menu-manager'

const menuManager = getWordPressMenuManager()

// Sync collections to menu
await menuManager.syncCollectionsToMenu('primary', [
  { name: 'Black Rose', slug: 'black-rose', postId: 123 },
  { name: 'Love Hurts', slug: 'love-hurts', postId: 124 },
])

// Add custom menu item
await menuManager.createMenuItem(menuId, {
  title: 'Shop',
  url: 'https://skyyrose.co/shop',
  menu_order: 1
})
```

### Bulk Operations

```typescript
// List all posts
const posts = await wp.listPosts({ per_page: 100 })

// Search content
const results = await wp.search('black rose', {
  type: 'post',
  per_page: 20
})

// Update settings
await wp.updateSettings({
  title: 'SkyyRose Luxury Fashion',
  posts_per_page: 12
})
```

---

## Vercel API Usage Examples

### Deploying Programmatically

```typescript
import { getVercelDeploymentManager } from '@/lib/vercel/deployment-manager'

const vercel = getVercelDeploymentManager()

// Create deployment
const deployment = await vercel.createDeployment({
  name: 'devskyy-dashboard',
  files: [
    { file: 'index.html', data: '<html>...</html>' }
  ],
  target: 'production'
})

// Promote to production
await vercel.promoteToProduction(deployment.uid)
```

### Managing Environment Variables

```typescript
// Sync all env vars from .env.production
const envVars = {
  'NEXT_PUBLIC_API_URL': 'https://api.devskyy.app',
  'NEXT_PUBLIC_WORDPRESS_URL': 'https://skyyrose.co'
}

const result = await vercel.syncEnvVariables('devskyy-dashboard', envVars, [
  'production',
  'preview'
])

console.log(`Created: ${result.created}, Updated: ${result.updated}`)
```

### Monitoring Deployments

```typescript
// Get deployment status
const deployment = await vercel.getDeployment(deploymentId)
console.log(`State: ${deployment.state}`) // READY, BUILDING, ERROR

// Get deployment logs
const logs = await vercel.getDeploymentLogs(deploymentId)

// Get deployment checks
const checks = await vercel.getDeploymentChecks(deploymentId)

// Get analytics
const analytics = await vercel.getProjectAnalytics('devskyy-dashboard', {
  from: Date.now() - 7 * 24 * 60 * 60 * 1000, // Last 7 days
  to: Date.now()
})
```

---

## Autonomous WordPress Operations

The system can autonomously manage WordPress based on Round Table results:

### Auto-Sync Round Table → WordPress

```typescript
import { roundTableAutoTrigger } from '@/lib/autonomous/round-table-auto-trigger'

// Submit any task - automatically triggers Round Table + WordPress publish
const result = await roundTableAutoTrigger.processTask({
  prompt: 'Write a product description for Black Rose Leather Jacket',
  task_type: 'content_generation'
})

// Result includes:
// - Round Table competition results
// - Winner LLM response
// - WordPress post ID (published, not draft!)
```

### Auto-Sync Collections to Menu

```typescript
const menuManager = getWordPressMenuManager()

const result = await menuManager.syncCollectionsToMenu('primary', [
  { name: 'Black Rose', slug: 'black-rose' },
  { name: 'Love Hurts', slug: 'love-hurts' },
  { name: 'Signature', slug: 'signature' },
  { name: 'Kids Capsule', slug: 'kids-capsule' }
])

console.log(`Added: ${result.added.join(', ')}`)
```

---

## Monitoring & Analytics

### Vercel Analytics

Automatically enabled on all pages:

- Page views tracking
- User engagement metrics
- Geographic distribution
- Device and browser stats
- Real-time visitor count

**Access:** Vercel Dashboard → Analytics

### Vercel Speed Insights

Monitors Core Web Vitals:

- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)
- First Contentful Paint (FCP)
- Time to First Byte (TTFB)

**Access:** Vercel Dashboard → Speed Insights

### Custom Monitoring

```typescript
// Track custom events
import { track } from '@vercel/analytics'

track('wordpress_sync_completed', {
  postId: 123,
  collection: 'black-rose'
})

// Track performance
import { sendMetric } from '@vercel/speed-insights'

sendMetric({
  name: 'wordpress_api_latency',
  value: 245
})
```

---

## Troubleshooting

### Build Failures

```bash
# Check TypeScript errors
npm run build

# Check for linting issues
npm run lint

# Clear build cache
rm -rf .next
npm run build
```

### Deployment Failures

```bash
# View detailed logs
vercel logs <deployment-url> --follow

# Inspect deployment
vercel inspect <deployment-url>

# Redeploy with force
vercel --force
```

### WordPress Connection Issues

1. Verify credentials in `.env.production`
2. Test connection via `/admin/wordpress`
3. Check WordPress REST API enabled
4. Verify WooCommerce consumer keys valid
5. Check CORS settings if browser-based

### Vercel API Issues

1. Verify `VERCEL_TOKEN` is valid
2. Check token permissions (read/write)
3. Verify team/project IDs correct
4. Test connection via `/admin/vercel`

---

## Best Practices

### Deployment

1. **Always build locally first**
   ```bash
   npm run build
   ```

2. **Test in preview before production**
   ```bash
   npm run deploy        # Preview
   # Test thoroughly
   npm run deploy:prod   # Production
   ```

3. **Use environment-specific variables**
   - Preview: `.env.local`
   - Production: `.env.production`

4. **Monitor deployments**
   - Check build logs
   - Verify smoke tests pass
   - Monitor analytics after deployment

### WordPress

1. **Always use operations manager**
   - Don't make direct API calls
   - Use type-safe wrapper methods

2. **Handle errors gracefully**
   ```typescript
   try {
     await wp.createPost(post)
   } catch (error) {
     console.error('Post creation failed:', error)
     // Fallback logic
   }
   ```

3. **Batch operations efficiently**
   - Use pagination for large datasets
   - Implement rate limiting
   - Cache results when possible

4. **Validate before mutations**
   - Check post/page exists before update
   - Verify user permissions
   - Sanitize input data

---

## Security

### API Keys

- **Never commit** `.env` or `.env.production` files
- Use Vercel's encrypted environment variables
- Rotate keys regularly
- Use separate keys for development/production

### WordPress

- Enable WP REST API authentication
- Use Application Passwords or OAuth
- Implement rate limiting
- Validate all inputs
- Sanitize HTML content

### Vercel

- Use team-scoped tokens when possible
- Limit token permissions to minimum required
- Enable 2FA on Vercel account
- Audit deployment logs regularly

---

## Support

### Documentation

- [Vercel CLI Docs](https://vercel.com/docs/cli)
- [Vercel API Docs](https://vercel.com/docs/rest-api)
- [WordPress REST API Docs](https://developer.wordpress.org/rest-api/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

### Internal

- `/admin/vercel` - Vercel management UI
- `/admin/wordpress` - WordPress operations UI
- `/admin/autonomous` - Autonomous agents dashboard

### Issues

Report deployment issues:
```bash
vercel --debug > deployment-debug.log 2>&1
```

Report WordPress issues:
- Check connection status in `/admin/wordpress`
- Verify REST API enabled: `https://skyyrose.co/wp-json/`
- Test authentication with consumer keys
