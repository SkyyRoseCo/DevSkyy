# DevSkyy Environment Variables Manifest

**Version**: 3.0.0
**Last Updated**: 2026-01-16

This document provides a complete reference for all environment variables required by each service in the DevSkyy platform.

---

## Quick Start

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Generate security keys (REQUIRED for production)
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"
python -c "import secrets, base64; print('ENCRYPTION_MASTER_KEY=' + base64.b64encode(secrets.token_bytes(32)).decode())"

# 3. Fill in your API keys and database credentials
# 4. Deploy to each platform with the appropriate subset of variables
```

---

## Table of Contents

1. [Backend API (Render)](#backend-api-render)
2. [Frontend Dashboard (Vercel)](#frontend-dashboard-vercel)
3. [WordPress Integration](#wordpress-integration)
4. [HuggingFace Spaces](#huggingface-spaces)
5. [CI/CD (GitHub Actions)](#cicd-github-actions)

---

## Backend API (Render)

**Platform**: Render.com
**Service Type**: Web Service
**Entry Point**: `main_enterprise.py`

### Required Variables

| Variable | Description | Example | Validation |
|----------|-------------|---------|------------|
| `JWT_SECRET_KEY` | Secret key for JWT tokens | 64+ character random string | Min 64 chars, URL-safe base64 |
| `ENCRYPTION_MASTER_KEY` | AES-256-GCM encryption key | Base64-encoded 32-byte key | Exactly 44 chars (32 bytes base64) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host/db` | Valid asyncpg URL |
| `ENVIRONMENT` | Deployment environment | `production` | `development`, `staging`, `production` |

### LLM Providers (At least one required)

| Variable | Description | Example | Provider |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` | Anthropic |
| `GOOGLE_AI_API_KEY` | Google AI API key | `AIza...` | Google |
| `MISTRAL_API_KEY` | Mistral API key | `...` | Mistral |
| `COHERE_API_KEY` | Cohere API key | `...` | Cohere |
| `GROQ_API_KEY` | Groq API key | `gsk_...` | Groq |

### 3D Asset Generation

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TRIPO_API_KEY` | Tripo3D API key | `tr_...` | If using Tripo3D |
| `HUGGINGFACE_API_TOKEN` | HuggingFace API token | `hf_...` | For HF Spaces/models |
| `FASHN_API_KEY` | FASHN virtual try-on key | `fashn_...` | For virtual try-on |

### Caching & Monitoring

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | None (optional) |
| `SENTRY_DSN` | Sentry error tracking | `https://...@sentry.io/...` | None (optional) |
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | `true` | `true` |

### Application Settings

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `DEBUG` | Enable debug mode | `false` | `false` |
| `LOG_LEVEL` | Logging level | `INFO` | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `https://app.devskyy.app,https://skyyrose.com` | Required |
| `API_URL` | Backend API URL | `https://api.devskyy.app` | Required |
| `FRONTEND_URL` | Frontend URL | `https://app.devskyy.app` | Required |

### Database Pool Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_POOL_SIZE` | Connection pool size | `10` |
| `DB_MAX_OVERFLOW` | Max overflow connections | `20` |
| `DB_POOL_TIMEOUT` | Pool timeout in seconds | `30` |

### Rate Limiting

| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_IP_PER_MINUTE` | API requests per minute per client IP | `100` |
| `RATE_LIMIT_IP_PER_HOUR` / `RATE_LIMIT_IP_BURST` | Per-IP hourly value (advisory: only the per-minute window is enforced) / burst (blacklist threshold) | 60x / 2x per-minute |
| `RATE_LIMIT_USER_*` / `RATE_LIMIT_API_KEY_*` | Same three settings for the per-user / per-API-key rules (defined but not yet applied by `enforce_rate_limit`, which enforces only the per-IP rule) | `200` / `1000` per minute |

### Render.yaml Example

```yaml
services:
  - type: web
    name: devskyy-api
    env: python
    buildCommand: pip install -e .
    startCommand: uvicorn main_enterprise:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET_KEY
        sync: false
      - key: ENCRYPTION_MASTER_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: devskyy-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: devskyy-redis
          property: connectionString
```

---

## Frontend Dashboard (Vercel)

**Platform**: Vercel
**Framework**: Next.js 15
**Root Directory**: `frontend`

### Required Variables

| Variable | Description | Example | Where to Set |
|----------|-------------|---------|--------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://api.devskyy.app` | Vercel Dashboard |
| `NEXT_PUBLIC_SITE_URL` | Frontend URL | `https://app.devskyy.app` | vercel.json |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_TELEMETRY_DISABLED` | Disable Next.js telemetry | `1` |
| `VERCEL_ENV` | Vercel environment | Auto-set by Vercel |

### Vercel Dashboard Setup

1. Go to Project Settings > Environment Variables
2. Add variables for each environment (Production, Preview, Development)

```
NEXT_PUBLIC_API_URL=https://api.devskyy.app  (Production)
NEXT_PUBLIC_API_URL=https://staging-api.devskyy.app  (Preview)
NEXT_PUBLIC_API_URL=http://localhost:8000  (Development)
```

---

## WordPress Integration

**Platform**: WordPress hosting (WP Engine, Kinsta, etc.)
**Theme**: skyyrose-immersive (Shoptimizer child theme)

### Required for Backend

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `WORDPRESS_URL` | WordPress site URL | `https://skyyrose.com` | No trailing slash |
| `WORDPRESS_USERNAME` | WordPress admin user | `admin` | For REST API |
| `WORDPRESS_APP_PASSWORD` | Application password | `xxxx-xxxx-xxxx-xxxx` | Generate in WP Admin |
| `WOOCOMMERCE_KEY` | WooCommerce API key | `ck_...` | Consumer key |
| `WOOCOMMERCE_SECRET` | WooCommerce API secret | `cs_...` | Consumer secret |

### WordPress wp-config.php

Add these constants to your WordPress configuration:

```php
// Enable REST API authentication
define('DEVSKYY_API_URL', 'https://api.devskyy.app');
define('DEVSKYY_API_KEY', 'your-shared-api-key');

// 3D Asset Settings
define('SKYYROSE_3D_ENABLED', true);
define('SKYYROSE_MODELS_PATH', '/wp-content/uploads/3d-models/');

// Performance
define('WP_CACHE', true);
define('COMPRESS_CSS', true);
define('COMPRESS_SCRIPTS', true);
```

### Generating WooCommerce API Keys

1. Go to WooCommerce > Settings > Advanced > REST API
2. Click "Add Key"
3. Description: "DevSkyy Integration"
4. User: Select admin user
5. Permissions: Read/Write
6. Click "Generate API Key"
7. Copy the Consumer Key (ck_...) and Consumer Secret (cs_...)

---

## HuggingFace Spaces

**Platform**: HuggingFace
**Deployment**: `hf-spaces/`

### Required Secrets (Set in HF Space Settings)

| Secret | Description | Spaces Using It |
|--------|-------------|-----------------|
| `HF_TOKEN` | HuggingFace API token | All spaces |
| `OPENAI_API_KEY` | OpenAI API key | product-analyzer, product-photography |
| `ANTHROPIC_API_KEY` | Anthropic API key | product-analyzer |

### Space-Specific Variables

#### 3D Converter (`hf-spaces/3d-converter/`)
```
ENABLE_GPU=false
MAX_FILE_SIZE_MB=100
OUTPUT_FORMAT=glb
```

#### FLUX Upscaler (`hf-spaces/flux-upscaler/`)
```
ENABLE_GPU=true
MAX_UPSCALE=4
MODEL_ID=stabilityai/stable-diffusion-xl-base-1.0
```

#### Virtual Try-On (`hf-spaces/virtual-tryon/`)
```
ENABLE_GPU=true
FASHN_API_KEY=fashn_...
MODEL_ENDPOINT=https://api.fashn.ai/v1
```

#### Product Analyzer (`hf-spaces/product-analyzer/`)
```
ENABLE_GPU=true
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Deploying to HuggingFace

```bash
# Set secrets first (via HF CLI or web interface)
huggingface-cli login --token $HF_TOKEN

# Deploy all spaces
cd hf-spaces
./deploy-all-spaces.sh
```

---

## CI/CD (GitHub Actions)

**Platform**: GitHub Actions
**Config**: `.github/workflows/`

### Required Secrets

| Secret | Description | Where to Get |
|--------|-------------|--------------|
| `VERCEL_TOKEN` | Vercel deployment token | vercel.com/account/tokens |
| `VERCEL_ORG_ID` | Vercel organization ID | vercel.com/[org]/settings |
| `VERCEL_PROJECT_ID` | Vercel project ID | vercel.com/[org]/[project]/settings |
| `RENDER_DEPLOY_HOOK` | Render staging deploy hook | render.com/dashboard |
| `RENDER_PROD_DEPLOY_HOOK` | Render production deploy hook | render.com/dashboard |
| `CODECOV_TOKEN` | Codecov upload token | codecov.io/gh/[org]/[repo]/settings |

### Optional Secrets

| Secret | Description | Purpose |
|--------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Slack notifications | Deployment alerts |
| `SENTRY_AUTH_TOKEN` | Sentry release tracking | Error monitoring |
| `GITHUB_TOKEN` | GitHub API access | Auto-generated |

### Setting GitHub Secrets

1. Go to Repository > Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Add each secret with its value

---

## Validation Checklist

Before deploying, verify:

### Backend (Render)
- [ ] `JWT_SECRET_KEY` is 64+ characters, randomly generated
- [ ] `ENCRYPTION_MASTER_KEY` is exactly 44 characters (base64)
- [ ] `DATABASE_URL` starts with `postgresql+asyncpg://`
- [ ] At least one LLM provider API key is set
- [ ] `CORS_ORIGINS` includes all frontend domains

### Frontend (Vercel)
- [ ] `NEXT_PUBLIC_API_URL` points to production backend
- [ ] Environment variables set for all environments

### WordPress
- [ ] Application password generated (not regular password)
- [ ] WooCommerce REST API keys have Read/Write permissions
- [ ] `WORDPRESS_URL` has no trailing slash

### HuggingFace
- [ ] `HF_TOKEN` has write access for deployments
- [ ] GPU spaces have proper hardware configured

### CI/CD
- [ ] All deploy hooks are valid and active
- [ ] Vercel tokens have project access
- [ ] Codecov token is for correct repository

---

## Security Best Practices

1. **Never commit secrets** - All `.env` files are gitignored
2. **Rotate regularly** - Change keys every 90 days minimum
3. **Use separate keys** - Different keys for dev/staging/production
4. **Audit access** - Review who has access to secrets quarterly
5. **Monitor usage** - Set up alerts for unusual API usage

### Key Rotation Procedure

```bash
# 1. Generate new key
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 2. Update in platform (Render/Vercel/etc.)
# 3. Deploy new version
# 4. Verify functionality
# 5. Revoke old key after 24 hours
```

---

## Troubleshooting

### "Invalid JWT_SECRET_KEY"
- Ensure key is at least 64 characters
- Use only URL-safe characters (a-z, A-Z, 0-9, -, _)

### "Database connection failed"
- Verify URL format: `postgresql+asyncpg://user:pass@host:5432/dbname`
- Check network/firewall allows connection
- Ensure database user has required permissions

### "CORS error"
- Verify `CORS_ORIGINS` includes the requesting domain
- Include both `http://` and `https://` if needed
- Restart backend after changing CORS settings

### "LLM API error"
- Verify API key is valid and has credits
- Check rate limits haven't been exceeded
- Ensure the key has required permissions/scopes

---

**Document Owner**: DevSkyy Platform Team
**Next Review**: Quarterly or on major version changes
