# Deployment catalog replica

`skyyrose-catalog.csv` is a byte-for-byte deployment replica of the catalog
projection of the product registry
(`wordpress-theme/skyyrose-flagship/data/logo-registry.json`, the one editable
product source). Vercel deploys this project from `frontend/`, so its
serverless functions cannot read the monorepo parent at runtime.

Never edit it. `python scripts/sync_product_registry.py` regenerates it with
the other projections, and `--check` fails CI the moment it drifts.
