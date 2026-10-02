# DevSkyy

**AI-driven luxury fashion commerce and creative operations for SkyyRose.**

[![CI](https://github.com/SkyyRoseCo/DevSkyy/actions/workflows/ci.yml/badge.svg)](https://github.com/SkyyRoseCo/DevSkyy/actions)
[![Python 3.12–3.14](https://img.shields.io/badge/python-3.12%E2%80%933.14-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Last updated:** 2026-10-02. Source baseline:
`a662e707d698a687d7d1d2efed3975b9aa7325b9`.

## Current release state

The five workstreams are integrated into a frozen candidate. The current
production scope is the V2 WordPress storefront with native WooCommerce and
existing approved media. Production acceptance remains a separate gate from
source checks, CI, packaging, and staging qualification.

V1 (`skyyrose-flagship`) and V2 (`skyyrose-flagship-2`) must be delivered as
**separate installable WordPress theme packages**, each with its own directory,
theme identity, bootstrap, assets, and required data. Neither package may require
the sibling theme to be installed. See [production status](docs/PRODUCTION_STATUS.md#separate-theme-packages-and-installed-identity)
for package evidence and the distinction between source V1 and the currently
installed theme in the legacy directory.

| Surface                                                             | Implementation                                                              | Release boundary                                                                                                              |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [Customer site](https://skyyrose.co)                                | WordPress.com and native WooCommerce; captured active installation and separate V2 candidate | Actual theme identity, runtime holds, activation, and acceptance are recorded in [production status](docs/PRODUCTION_STATUS.md) |
| [Existing staging](https://staging-7e48-skyyrose.wpcomstaging.com/) | `wordpress-theme/skyyrose-flagship-2/`, version 2.5.0                       | Captured staging qualification is separate from production acceptance; see [production status](docs/PRODUCTION_STATUS.md)     |
| Agent dashboard                                                     | Next.js 16, React 19, `frontend/`                                           | Integrated source; dashboard/Fly deployment is outside this storefront cutover                                                |
| API and creative operations                                         | FastAPI, Python, `main_enterprise.py`, `skyyrose/`                          | Integrated source; API/Governor/provider execution is outside this cutover                                                    |

Read [current production status](docs/PRODUCTION_STATUS.md) for the dated actual
state, literal receipt identities, and remaining gates, and the
[runbook](docs/RUNBOOK.md) for the ordered operator procedure. Source CI,
conditional execution clearance, verified installation, deployment, and
production browser acceptance are separate states. The status document is the
maintained snapshot; implementation tables and historical task receipts do not
replace it.

## Local setup

Run from the repository root. Python's supported range is **3.12–3.14**, as
declared in [pyproject.toml](pyproject.toml). Root tooling requires Node.js 22+
and npm 10+ (`.nvmrc` pins 22.19.0); V2 requires Node.js 22+ and npm 9+. Each
JavaScript workspace has its own manifest and lockfile.

```bash
# Python API and local test tooling, using the committed lockfile
uv sync --locked --extra dev --python 3.13

# Independent JavaScript workspaces
npm ci
(cd frontend && npm ci)
(cd wordpress-theme/skyyrose-flagship-2 && npm ci)
```

Configure the environment for the service being run using
[.env.example](.env.example) and the relevant package documentation. Keep
credentials in local environment files or the intended host's secret store.
Installing dependencies does not authorize provider calls or deployment.

Start the API and dashboard in separate terminals:

```bash
uv run --locked --extra dev python -m uvicorn main_enterprise:app --reload --port 8000
```

```bash
cd frontend
npm run dev
```

For a local container stack, use the configured Compose workflow in
[docs/DOCKER.md](docs/DOCKER.md). `make install` installs the base Python
package; `make dev` installs development dependencies and root npm dependencies.
Neither starts the API.

## Architecture and ownership

| Area                 | Entry points and directories                                                                                | Responsibility                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Python API           | [main_enterprise.py](main_enterprise.py), `api/`, `security/`, `database/`                                  | Authenticated API, persistence, integrations, and operational endpoints                             |
| Agents and workflows | `agents/`, `orchestration/`, `services/`, `skyyrose/elite_studio/`                                          | Agent execution, creative workflow state, governance, and provider adapters                         |
| Dashboard            | [frontend/package.json](frontend/package.json), `frontend/app/`, `frontend/components/`, `frontend/lib/`    | Next.js application, owner reports, and operator interfaces                                         |
| Shared TypeScript    | [package.json](package.json), `src/`                                                                        | Services, commerce utilities, collection experiences, and tests                                     |
| Production V1 theme  | [wordpress-theme/skyyrose-flagship/](wordpress-theme/skyyrose-flagship/)                                    | Original WordPress/WooCommerce theme, captured V1 baseline, and canonical product registry location |
| V2 theme candidate   | [wordpress-theme/skyyrose-flagship-2/](wordpress-theme/skyyrose-flagship-2/)                                | Storefront templates, native commerce adapters, consent, deterministic build, and packaging         |
| Release operations   | `tools/production-runtime/`, `tasks/integration-release-20261001/`, `tasks/production-final-pass-20261001/` | Scoped operational source, integration record, guarded page/MU operations, and release evidence     |

These are independently validated surfaces. A successful root TypeScript test
does not validate the dashboard or either theme, and a storefront deployment
does not deploy the API or Governor. See the
[WordPress codemap](docs/CODEMAPS/wordpress.md) and
[integration adoption manifest](tasks/integration-release-20261001/adoption-manifest.json)
for concrete source relationships and adopted work.

## Product authority

The one editable product source is [logo-registry.json](logo-registry.json), a
symlink to
[wordpress-theme/skyyrose-flagship/data/logo-registry.json](wordpress-theme/skyyrose-flagship/data/logo-registry.json).
Its unified `products[sku]` records own commerce facts, garment specifications,
copy, source/image bindings, and founder corrections. CSVs, dossiers, asset
manifests, and V2 presentation data are compatibility projections or consumers.

Read a complete product through the single entry point:

```python
from skyyrose.core.product import get_product

product = get_product("br-001")
gaps = product["gaps"]
```

Non-Python consumers can use the identical JSON interface:

```bash
uv run --locked python -m skyyrose.core.product br-001
uv run --locked python scripts/sync_product_registry.py --check
```

Unknown SKUs raise; absent facts are named in `gaps`. Corey is the founder and
maker: his latest direct specifications are authoritative and recorded as
`FOUNDER_CONFIRMED`. Preserve his exact wording, dimensions, ranges, artwork,
and placements. Apply scoped corrections to the registry first, using its update
API; after direct registry edits regenerate projections with
`scripts/sync_product_registry.py`. Do not create independent product fact maps.
See [SOT.md](SOT.md) and [the product reader](skyyrose/core/product.py).

## Validation

Run checks in the workspace that owns the change. The commands below are
interfaces verified from the manifests; they are not claims that a fresh full
suite passed in this documentation update.

| Directory                              | Checks                                                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Repository root, Python                | `uv run --locked --extra dev python -m pytest tests/ -v`; configured Ruff, Black, and mypy checks      |
| Repository root, TypeScript            | `npm run lint`, `npm run type-check`, `npm test`, `npm run build`                                      |
| `frontend/`                            | `npm run lint`, `npm run type-check`, `npm test`, `npm run build`, `npm run test:e2e`                  |
| `wordpress-theme/`, V1                 | `npm run verify:full`                                                                                  |
| `wordpress-theme/skyyrose-flagship-2/` | `npm run build`, `npm run check:assets`, `npm run lint:php`, `npm run verify`, `npm run package:theme` |

`make test-fast` stops on the first failure and inherits pytest's configured
marker exclusions. `make ci` checks root Python and TypeScript, with
non-blocking legacy mypy/TypeScript-test paths; it does not run all
dashboard/theme checks or replace mandatory exact-head CI. Use direct checks and
the release's explicit gate list when determining acceptance.

Edit theme source and rebuild affected tracked `.min.css`/`.min.js` outputs in
the correct package. New source, registry, certification, or artifact bytes
invalidate the corresponding frozen evidence and require review again.

## Deployment and documentation

The current storefront cutover uses the exact reviewed V2 theme ZIP, a separately hashed
Search privacy MU extension, and ten owned new pages. Use the
[runbook](docs/RUNBOOK.md), [production status](docs/PRODUCTION_STATUS.md), and
[WordPress configuration record](docs/WORDPRESS_CONFIGURATION_STATUS.md).
Production requires explicit scope authorization, exact-head CI, reviewed
operation/evidence bindings, actual target readback, browser acceptance, and
independent review. Local setup commands and public HTTP responses do not supply
those gates.

Additional references: [repository agent instructions](AGENTS.md),
[Docker operations](docs/DOCKER.md), [security guidance](docs/SECURITY.md), and
[documentation directory](docs/).

## License

The platform is [MIT licensed](LICENSE). The V2 WordPress package declares
`GPL-2.0-or-later` in its
[manifest](wordpress-theme/skyyrose-flagship-2/package.json); follow the
applicable package and asset licensing terms.
