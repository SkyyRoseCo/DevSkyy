---
name: deploy
description: Production deployment pipeline with validation and rollback.
---

# DevSkyy Deployment Pipeline

## Phases
```
Pre-Flight → Security → Build → Test → Deploy → Verify → Smoke
```

## Pre-Flight
- No uncommitted changes
- On main branch
- Dependencies installed

## Security Gates
```bash
pip-audit --desc           # Python CVEs
npm audit                  # Node.js vulnerabilities
bandit -r . -x venv        # OWASP scan
```
**ABORT on CRITICAL/HIGH vulnerabilities**

## Quality Gates
```bash
pytest --cov=. --cov-report=term    # Tests + coverage
mypy .                               # Type checking
```
**ABORT if tests fail or coverage <70%**

## Deploy Commands
All are STOP-AND-SHOW (manifest → founder `y` → run).
```bash
cd frontend && npm run deploy:prod   # Frontend — Vercel, current but retiring (devskyy.app 402 DEPLOYMENT_DISABLED 2026-09-18; replacement host undecided)
docker-compose build && push         # Backend
bash scripts/deploy-staging.sh [--dry-run]     # WordPress theme skyyrose-flagship-2 → staging-7e48-skyyrose.wpcomstaging.com (.env.wordpress.staging)
bash scripts/deploy-production.sh [--dry-run]  # WordPress theme skyyrose-flagship-2 → skyyrose.co (.env.wordpress); scripts/deploy-theme.sh is the engine, refuses direct runs
```

## Post-Deploy Verification
- Health endpoint returns 200
- Database connectivity
- MCP server availability

## Related Tools
- **Agent**: `security-reviewer` before deploy
- **Command**: `/verify pre-pr` for full checks
- **MCP**: `health_check` for monitoring
