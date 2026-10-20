# Environment Variables Reference

**Version**: 3.3.0
**Last Updated**: 2026-02-24
**Status**: Complete

This document provides comprehensive reference for all environment variables used across the DevSkyy platform, including backend services, WordPress integration, MCP servers, and machine learning pipelines.

---

## Table of Contents

1. [Application Core](#application-core)
2. [Security (CRITICAL)](#security-critical)
3. [Database](#database)
4. [CORS & API URLs](#cors--api-urls)
5. [AI/ML Provider APIs](#aiml-provider-apis)
6. [3D Asset Generation](#3d-asset-generation)
7. [Virtual Try-On](#virtual-try-on)
8. [Meshy 3D Generation](#meshy-3d-generation)
9. [Social Media Pipeline](#social-media-pipeline)
10. [LLM Round Table](#llm-round-table)
11. [HuggingFace Spaces](#huggingface-spaces)
12. [WordPress/WooCommerce](#wordpresswoocommerce)
13. [Payments - Stripe](#payments---stripe)
14. [Email & Marketing](#email--marketing)
15. [Caching](#caching)
16. [Monitoring & Logging](#monitoring--logging)
17. [Rate Limiting](#rate-limiting)
18. [Performance Optimization](#performance-optimization)
19. [MCP Server Configuration](#mcp-server-configuration)
20. [Development Settings](#development-settings)

---

## Application Core

| Variable | Purpose | Format | Required | Default |
|----------|---------|--------|----------|---------|
| `ENVIRONMENT` | Deployment environment | `development`/`staging`/`production` | Yes | `development` |
| `DEBUG` | Debug mode (disable in production) | `true`/`false` | No | `false` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG`/`INFO`/`WARNING`/`ERROR` | No | `INFO` |

**Notes:**
- Set `DEBUG=false` in production for security
- `LOG_LEVEL=INFO` recommended for production, `DEBUG` for development

---

## Security (CRITICAL)

| Variable | Purpose | Generation Command | Required |
|----------|---------|-------------------|----------|
| `JWT_SECRET_KEY` | JWT token signing | `python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"` | **Yes** |
| `ENCRYPTION_MASTER_KEY` | AES-256-GCM encryption | `python -c "import secrets, base64; print('ENCRYPTION_MASTER_KEY=' + base64.b64encode(secrets.token_bytes(32)).decode())"` | **Yes** |

**Security Requirements:**
- `JWT_SECRET_KEY`: Minimum 64 characters, cryptographically random
- `ENCRYPTION_MASTER_KEY`: 32-byte base64-encoded key for AES-256-GCM
- **NEVER** commit these to version control
- Rotate keys on security incidents
- Use different keys for dev/staging/production

---

## Database

| Variable | Purpose | Format | Required | Default |
|----------|---------|--------|----------|---------|
| `DATABASE_URL` | Primary database connection | SQLAlchemy URL | Yes | `sqlite+aiosqlite:///./devskyy.db` |
| `DB_POOL_SIZE` | Connection pool size | Integer | No | `10` |
| `DB_MAX_OVERFLOW` | Max overflow connections | Integer | No | `20` |
| `DB_POOL_TIMEOUT` | Connection timeout (seconds) | Integer | No | `30` |

**Connection String Examples:**
```bash
# SQLite (Development)
DATABASE_URL=sqlite+aiosqlite:///./devskyy.db

# PostgreSQL (Production - Recommended)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/devskyy
```

**Performance Notes:**
- SQLite: Good for development, single-file database
- PostgreSQL: Recommended for production (better performance, concurrent writes)
- Connection pooling reduces overhead for frequent DB operations

---

## CORS & API URLs

| Variable | Purpose | Format | Required |
|----------|---------|--------|----------|
| `CORS_ORIGINS` | Allowed CORS origins | Comma-separated URLs | Yes |
| `FRONTEND_URL` | Frontend application URL | HTTPS URL | Yes |
| `API_URL` | Backend API URL | HTTPS URL | Yes |

**Example:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://app.devskyy.app,https://api.devskyy.app,https://staging.devskyy.com
FRONTEND_URL=https://app.devskyy.app
API_URL=https://api.devskyy.app
```

**Security Notes:**
- Never use `*` for `CORS_ORIGINS` in production
- Always use HTTPS in production
- Include all frontend domains that will call the API

---

## AI/ML Provider APIs

| Variable | Purpose | Get API Key From | Required |
|----------|---------|------------------|----------|
| `OPENAI_API_KEY` | OpenAI GPT models | https://platform.openai.com/api-keys | Optional* |
| `ANTHROPIC_API_KEY` | Claude models | https://console.anthropic.com/ | Optional* |
| `GOOGLE_AI_API_KEY` | Gemini models | https://ai.google.dev/ | Optional* |
| `HF_TOKEN` | HuggingFace models | https://huggingface.co/settings/tokens | Optional* |

**\*At least one AI provider is required for the platform to function.**

**Model Configuration (MCP Server):**
| Variable | Purpose | Default |
|----------|---------|---------|
| `DEFAULT_MODEL` | Primary model | `gpt-4o` |
| `FALLBACK_MODEL` | Backup model | `gpt-4o-mini` |
| `MAX_TOKENS` | Max response tokens | `4096` |
| `TEMPERATURE` | Response randomness | `0.7` |
| `TOP_P` | Nucleus sampling | `1.0` |
| `FREQUENCY_PENALTY` | Repetition penalty | `0.0` |
| `PRESENCE_PENALTY` | Topic diversity | `0.0` |

---

## 3D Asset Generation

### HuggingFace (Primary - Recommended)

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `HF_TOKEN` | HuggingFace API token | `hf_...` | Required |
| `HF_HOME` | Cache directory | Path | `./cache/huggingface` |
| `HF_3D_MODEL_PRIMARY` | Primary 3D model | Model ID | `tencent/Hunyuan3D-2` |
| `HF_3D_MODEL_FALLBACK` | Fallback 3D model | Model ID | `stabilityai/TripoSR` |

**Available Models:**
- `tencent/Hunyuan3D-2`: Best quality, production-grade
- `stabilityai/TripoSR`: Balanced quality/speed
- `InstantMesh`: Fast, good for previews

### Tripo3D (Fallback)

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `TRIPO_API_KEY` | Tripo3D API key | https://www.tripo3d.ai/dashboard | No |
| `TRIPO_API_BASE_URL` | API endpoint | URL | `https://api.tripo3d.ai/v2` |
| `TRIPO_OUTPUT_DIR` | Output directory | Path | `./generated_assets/3d` |

---

## Virtual Try-On

### FASHN Integration

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `FASHN_API_KEY` | FASHN API key | https://fashn.ai/dashboard | No |
| `FASHN_API_BASE_URL` | API endpoint | URL | `https://api.fashn.ai/v1` |
| `FASHN_OUTPUT_DIR` | Output directory | Path | `./generated_assets/tryon` |

---

## Meshy 3D Generation

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `MESHY_API_KEY` | Meshy API key | https://www.meshy.ai/settings/api | No |

**Meshy Features:**
- Text-to-3D: Generate 3D models from text descriptions
- Image-to-3D: Convert 2D images to 3D models
- API v2 endpoints with task-based async generation

---

## Social Media Pipeline

### Instagram
| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Graph API token | Meta Developer Portal > Instagram Basic Display API | No |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Business account ID | Instagram Business Settings | No |

### TikTok
| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `TIKTOK_ACCESS_TOKEN` | TikTok Marketing API token | https://developers.tiktok.com/ | No |

### X / Twitter
| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `TWITTER_API_KEY` | Twitter API key (consumer key) | https://developer.x.com/portal | No |
| `TWITTER_API_SECRET` | Twitter API secret | https://developer.x.com/portal | No |
| `TWITTER_ACCESS_TOKEN` | OAuth access token | https://developer.x.com/portal | No |
| `TWITTER_ACCESS_SECRET` | OAuth access secret | https://developer.x.com/portal | No |

### Facebook
| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `FACEBOOK_ACCESS_TOKEN` | Facebook page access token | https://developers.facebook.com/ | No |
| `FACEBOOK_PAGE_ID` | Facebook Page ID | Facebook Page Settings | No |

---

## LLM Round Table

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `ANTHROPIC_API_KEY` | Claude models | https://console.anthropic.com/ | Optional* |
| `OPENAI_API_KEY` | GPT-4 models | https://platform.openai.com/api-keys | Optional* |
| `GOOGLE_AI_API_KEY` | Gemini models | https://ai.google.dev/ | Optional* |
| `GROQ_API_KEY` | Llama via Groq | https://console.groq.com/ | Optional* |
| `MISTRAL_API_KEY` | Mistral models | https://console.mistral.ai/ | Optional* |
| `COHERE_API_KEY` | Cohere models | https://dashboard.cohere.com/ | Optional* |

**\*At least one LLM provider is required for the Round Table to function. All 6 are recommended for full competition mode.**

---

## HuggingFace Spaces

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `HF_TOKEN` | HuggingFace API token | https://huggingface.co/settings/tokens | Yes (for HF features) |

**SkyyRose Spaces:**
- `skyyrose/3d-converter` - 3D model conversion pipeline
- `skyyrose/lora-monitor` - LoRA training monitor
- `skyyrose/virtual-tryon` - Virtual try-on experience

---

## WordPress/WooCommerce

### WordPress.com Integration

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `WORDPRESS_SITE_URL` | WordPress site URL | N/A | Yes |
| `WORDPRESS_API_TOKEN` | OAuth2 token | https://developer.wordpress.com/apps/ | Yes |
| `WORDPRESS_USERNAME` | Admin username | WordPress admin | Yes |
| `WORDPRESS_APP_PASSWORD` | Application password | WP Admin > Users > Application Passwords | Yes |

### WooCommerce API

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `WOOCOMMERCE_KEY` | Consumer key (`ck_...`) | WP Admin > WooCommerce > Settings > Advanced > REST API | Yes |
| `WOOCOMMERCE_SECRET` | Consumer secret (`cs_...`) | WP Admin > WooCommerce > Settings > Advanced > REST API | Yes |
| `WC_WEBHOOK_SECRET` | Webhook signature secret | Set when creating webhooks | No |

**Application Password Setup:**
1. WP Admin > Users > Your Profile
2. Scroll to "Application Passwords"
3. Enter name (e.g., "DevSkyy Integration")
4. Click "Add New Application Password"
5. Copy the generated password (format: `xxxx-xxxx-xxxx-xxxx`)

**WooCommerce API Keys Setup:**
1. WooCommerce > Settings > Advanced > REST API
2. Click "Add Key"
3. Description: "DevSkyy Integration"
4. User: Select admin user
5. Permissions: Read/Write
6. Click "Generate API Key"

---

## Payments - Stripe

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `STRIPE_API_KEY` | Secret key | https://dashboard.stripe.com/apikeys | Yes |
| `STRIPE_PUBLISHABLE_KEY` | Publishable key | https://dashboard.stripe.com/apikeys | Yes |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature | https://dashboard.stripe.com/webhooks | No |

**Test Mode:**
- Use `sk_test_...` and `pk_test_...` keys for development
- Use `sk_live_...` and `pk_live_...` keys for production

---

## Email & Marketing

### SMTP Configuration

| Variable | Purpose | Format | Required |
|----------|---------|--------|----------|
| `SMTP_HOST` | SMTP server | Hostname | No |
| `SMTP_PORT` | SMTP port | Integer | No |
| `SMTP_USER` | SMTP username | Email | No |
| `SMTP_PASSWORD` | App password | String | No |

**Gmail Setup:**
1. Enable 2FA on Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password (not your Google password)

### Klaviyo Marketing

| Variable | Purpose | Get From | Required |
|----------|---------|----------|----------|
| `KLAVIYO_PRIVATE_KEY` | Private API key | https://www.klaviyo.com/account#api-keys-tab | No |
| `KLAVIYO_PUBLIC_KEY` | Public API key | https://www.klaviyo.com/account#api-keys-tab | No |
| `KLAVIYO_LIST_ID` | List identifier | Klaviyo Lists | No |

---

## Caching

| Variable | Purpose | Format | Required | Default |
|----------|---------|--------|----------|---------|
| `REDIS_URL` | Redis connection | Redis URL | No | `redis://localhost:6379/0` |
| `ENABLE_RESPONSE_CACHE` | Enable HTTP cache | `true`/`false` | No | `true` |
| `CACHE_TTL` | Cache TTL (seconds) | Integer | No | `300` |
| `CACHE_MAX_SIZE` | Max cached items | Integer | No | `1000` |

**Redis URL Format:**
```bash
redis://localhost:6379/0
redis://:password@localhost:6379/0  # With password
redis://redis.example.com:6379/0    # Remote server
```

---

## Monitoring & Logging

| Variable | Purpose | Format | Required | Default |
|----------|---------|--------|----------|---------|
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | `true`/`false` | No | `true` |
| `SENTRY_DSN` | Sentry error tracking | DSN URL | No | Empty |
| `LOG_FORMAT` | Log format | `json`/`text` | No | `json` |
| `LOG_FILE` | Log file path | Path | No | `/app/logs/mcp.log` |
| `MAX_LOG_SIZE` | Max log file size | Size string | No | `100MB` |
| `LOG_RETENTION_DAYS` | Log retention | Integer | No | `30` |

**Sentry Setup:**
1. Create project at https://sentry.io
2. Copy DSN from Project Settings > Client Keys
3. Format: `https://<key>@sentry.io/<project>`

---

## Rate Limiting

| Variable | Purpose | Format | Required | Default |
|----------|---------|--------|----------|---------|
| `RATE_LIMIT_IP_PER_MINUTE` | API requests per minute per client IP (enforced on every request) | Integer > 0 | No | `100` |
| `RATE_LIMIT_IP_PER_HOUR` / `RATE_LIMIT_IP_BURST` | Per-IP hourly value (advisory: only the per-minute window is enforced) / burst (blacklist threshold) | Integer > 0 | No | 60x / 2x per-minute |
| `RATE_LIMIT_USER_PER_MINUTE` (+ `_PER_HOUR`, `_BURST`) | Per-user default rule (defined but not yet applied by `enforce_rate_limit`, which enforces only the per-IP rule) | Integer > 0 | No | `200` |
| `RATE_LIMIT_API_KEY_PER_MINUTE` (+ `_PER_HOUR`, `_BURST`) | Per-API-key default rule (defined but not yet applied by `enforce_rate_limit`, which enforces only the per-IP rule) | Integer > 0 | No | `1000` |
| `REQUESTS_PER_MINUTE` | MCP server rate limit | Integer | No | `30` |
| `REQUESTS_PER_HOUR` | MCP server hourly limit | Integer | No | `500` |

**Recommended Production Settings:**
- API endpoints: 100 requests per 60 seconds
- MCP server: 30 requests per minute, 500 per hour
- Adjust based on traffic patterns and infrastructure capacity

---

## Performance Optimization

| Variable | Purpose | Format | Required | Default |
|----------|---------|--------|----------|---------|
| `EMBEDDING_CACHE_SIZE` | Embedding cache entries | Integer | No | `1024` |
| `RESPONSE_CACHE_TTL` | HTTP response cache TTL | Seconds | No | `300` |
| `VECTOR_SEARCH_CACHE_TTL` | Vector search cache TTL | Seconds | No | `300` |
| `RERANKING_CACHE_TTL` | Reranking cache TTL | Seconds | No | `1800` |
| `MAX_PARALLEL_INGESTION` | Parallel file ingestion workers | Integer | No | `5` |

**Performance Notes:**
- Higher cache sizes reduce API calls but increase memory usage
- Adjust TTL values based on data freshness requirements
- `MAX_PARALLEL_INGESTION`: Set based on CPU cores (typically 2-8)

---

## MCP Server Configuration

### Core Settings

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `MCP_SERVER_NAME` | Server name | String | `devskyy` |
| `MCP_SERVER_VERSION` | Server version | Semver | `1.0.0` |
| `MCP_HOST` | Server host | IP/hostname | `localhost` |
| `MCP_PORT` | Server port | Integer | `8002` |
| `MCP_WORKERS` | Worker processes | Integer | `1` |

### Request Handling

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `MAX_CONCURRENT_REQUESTS` | Max concurrent requests | Integer | `5` |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | Integer | `60` |
| `RETRY_ATTEMPTS` | Retry attempts | Integer | `3` |
| `RETRY_DELAY` | Retry delay (seconds) | Integer | `1` |

### Tool Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENABLE_COMPLETION_TOOL` | Enable text completion | `true` |
| `ENABLE_CODE_GENERATION_TOOL` | Enable code generation | `true` |
| `ENABLE_VISION_ANALYSIS_TOOL` | Enable vision analysis | `true` |
| `ENABLE_FUNCTION_CALLING_TOOL` | Enable function calling | `true` |
| `ENABLE_MODEL_SELECTION_TOOL` | Enable model selection | `true` |
| `ENABLE_AGENT_INTEGRATION_TOOL` | Enable agent integration | `true` |
| `ENABLE_CAPABILITIES_TOOL` | Enable capabilities query | `true` |

### Agent Integration

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `MAX_AGENTS` | Max concurrent agents | Integer | `6` |
| `AGENT_TIMEOUT` | Agent timeout (seconds) | Integer | `120` |
| `ENABLE_AGENT_CHAINING` | Allow agent chaining | `true`/`false` | `true` |
| `AGENT_REGISTRY_URL` | Agent registry endpoint | URL | `http://localhost:8000/api/agents` |

### DevSkyy Integration

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `DEVSKYY_API_URL` | DevSkyy API endpoint | URL | `http://localhost:8000` |
| `DEVSKYY_API_KEY` | DevSkyy API key | String | Required |
| `MCP_BACKEND` | MCP backend provider | `devskyy`/`critical-fuchsia-ape` | `devskyy` |

### Vision Analysis

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `VISION_MODEL` | Vision model | Model ID | `gpt-4o` |
| `MAX_IMAGE_SIZE` | Max image size | Size string | `20MB` |
| `SUPPORTED_IMAGE_FORMATS` | Allowed formats | CSV | `jpg,jpeg,png,gif,webp` |

### Code Generation

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `CODE_MODEL` | Code generation model | Model ID | `gpt-4o` |
| `MAX_CODE_LENGTH` | Max code length | Integer | `10000` |
| `ENABLE_CODE_EXECUTION` | Allow code execution | `true`/`false` | `false` |
| `SUPPORTED_LANGUAGES` | Supported languages | CSV | `python,javascript,typescript,html,css,sql` |

**Security Warning:**
- `ENABLE_CODE_EXECUTION` should be `false` in production
- Only enable in sandboxed/isolated environments

### Context Management

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `MAX_CONTEXT_LENGTH` | Max context tokens | Integer | `32000` |
| `CONTEXT_WINDOW_OVERLAP` | Overlap tokens | Integer | `1000` |
| `ENABLE_CONTEXT_COMPRESSION` | Enable compression | `true`/`false` | `true` |

---

## Development Settings

| Variable | Purpose | Format | Default |
|----------|---------|--------|---------|
| `ENABLE_DEBUG_MODE` | Enable debug mode | `true`/`false` | `false` |
| `ENABLE_PROFILING` | Enable profiling | `true`/`false` | `false` |
| `ENABLE_TRACE_LOGGING` | Enable trace logs | `true`/`false` | `false` |
| `ENABLE_METRICS` | Enable metrics | `true`/`false` | `true` |
| `METRICS_PORT` | Metrics endpoint port | Integer | `8003` |
| `HEALTH_CHECK_INTERVAL` | Health check interval (seconds) | Integer | `30` |

**Development vs Production:**

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `true` | `false` |
| `LOG_LEVEL` | `DEBUG` | `INFO` |
| `ENABLE_DEBUG_MODE` | `true` | `false` |
| `ENABLE_PROFILING` | `true` | `false` |
| `ENABLE_TRACE_LOGGING` | `true` | `false` |

---

## Environment File Locations

| File | Purpose | Used By |
|------|---------|---------|
| `.env` | Main application config | Backend, API, services |
| `.env.wordpress.example` | WordPress integration | WordPress sync, WooCommerce |
| `mcp_servers/.env` | MCP server config | MCP server, tools |
| `ml/.env` | ML pipeline config | ML models, training |
| `dev/.env` | Development overrides | Local development |

---

## Quick Setup

### Development Environment

```bash
# Copy example files
cp .env.example .env
cp .env.wordpress.example .env.wordpress
cp mcp_servers/.env.example mcp_servers/.env

# Generate security keys
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))" >> .env
python -c "import secrets, base64; print('ENCRYPTION_MASTER_KEY=' + base64.b64encode(secrets.token_bytes(32)).decode())" >> .env

# Set at least one AI provider
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env

# Configure WordPress (if using)
# Edit .env.wordpress with your credentials
```

### Production Deployment

1. **Never use example values in production**
2. **Generate unique security keys** for each environment
3. **Use PostgreSQL** instead of SQLite
4. **Enable Redis caching** for performance
5. **Configure Sentry** for error tracking
6. **Set DEBUG=false** and appropriate LOG_LEVEL
7. **Use HTTPS URLs** for all endpoints
8. **Enable rate limiting** and monitoring

---

## Security Checklist

- [ ] `JWT_SECRET_KEY` and `ENCRYPTION_MASTER_KEY` generated and unique
- [ ] All API keys stored in environment variables, not in code
- [ ] `DEBUG=false` in production
- [ ] HTTPS URLs used for all external endpoints
- [ ] Database credentials secured
- [ ] CORS origins restricted to known domains
- [ ] Rate limiting enabled
- [ ] Sentry DSN configured for error tracking
- [ ] Environment files added to `.gitignore`
- [ ] Production secrets stored in secure vault (AWS Secrets Manager, HashiCorp Vault, etc.)

---

## Troubleshooting

### "Missing environment variable" error

**Solution:** Verify the variable is set in the correct `.env` file:
```bash
# Check if variable exists
grep "VARIABLE_NAME" .env

# Verify variable is loaded
python -c "import os; print(os.getenv('VARIABLE_NAME'))"
```

### Database connection errors

**Solution:** Verify `DATABASE_URL` format:
```bash
# PostgreSQL
postgresql+asyncpg://user:password@host:port/database

# SQLite
sqlite+aiosqlite:///./relative/path/db.db
sqlite+aiosqlite:////absolute/path/db.db  # Note 4 slashes for absolute
```

### Redis connection errors

**Solution:** Verify Redis is running and `REDIS_URL` is correct:
```bash
# Test Redis connection
redis-cli ping  # Should return PONG

# Verify REDIS_URL format
redis://localhost:6379/0
```

### API key validation errors

**Solution:** Verify API keys are valid and have correct permissions:
- Check key hasn't expired
- Verify key has required scopes/permissions
- Test key with provider's API directly

---

**Document Owner**: DevSkyy Platform Team
**Next Review**: After environment changes or new service additions
