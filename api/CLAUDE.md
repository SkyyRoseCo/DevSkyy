# api/

Scoped context for the FastAPI surface (~83 files, 30+ routers across two
layers). Loads on top of root.

## Hard rules

- **SSRF guard is MANDATORY for any endpoint taking a caller-provided URL.**
  `from security.ssrf_protection import ssrf_protection` then
  `ssrf_protection.validate_url(v)` inside the Pydantic validator. Pattern:
  `api/v1/assets.py:120`, `api/v1/media.py:89`. This was a P1 finding (PR #649).
  No exceptions.
- **Every new endpoint explicitly decides its auth posture** — public /
  `Depends(get_current_user)` (`security.jwt_oauth2_auth`) / rate-limited. Auth
  is OPT-IN, not default. Read-only catalog endpoints are intentionally public;
  cost-bearing LLM endpoints (e.g. `/catalog/answer`) are deliberately public,
  bounded by a per-IP rate limit (20 req/min) and a response cache — rationale
  in the `api/v1/catalog.py` module docstring. Don't add a billed endpoint
  without a gate.

## Two-layer routing contract

- **`api/v1/*.py`** routers declare their OWN `prefix` (e.g.
  `APIRouter(prefix="/catalog")`); `main_enterprise.py` adds `/api/v1` at mount.
  Final path = `/api/v1` + declared prefix. They export `router` (renamed in
  `api/v1/__init__.py`).
- **`api/*.py`** (non-versioned) routers declare NO prefix and export
  `{name}_router` (e.g. `agents_router`, `dashboard_router`). Most are mounted
  under `/api/v1`; a few (e.g. `agents_router`, `gdpr_router`) mount with NO
  prefix. Match the export-naming + prefix convention of the layer you add to,
  and check the mount in `main_enterprise.py`.
