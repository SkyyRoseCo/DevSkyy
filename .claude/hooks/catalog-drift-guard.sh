#!/usr/bin/env bash
# catalog-drift-guard.sh — PostToolUse hook: warn on drift after editing catalog/registry files.
#
# Fires after Edit/Write/MultiEdit. Checks if the edited file is a catalog
# or registry file, and if so runs the validator in --quiet mode.
# Prints a warning (non-blocking) if checks fail — the pre-commit hook blocks.

set -euo pipefail

# ── Resolve paths ──────────────────────────────────────────────────────────
REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null || echo "")"
if [[ -z "$REPO_ROOT" ]]; then
  exit 0
fi

# ── Gate: only fire on catalog/registry files ─────────────────────────────
# Claude Code passes the edited file path via CLAUDE_TOOL_INPUT_FILE_PATH env var.
# If not set (older harness), read from the hook's stdin JSON.
EDITED_FILE="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"

if [[ -z "$EDITED_FILE" ]]; then
  # Claude Code passes tool input as JSON on stdin. Slurp ALL of it — JSON is
  # multi-line, so reading a single line truncates it and silently no-ops the
  # guard. `timeout 1 cat` reads everything but never hangs on an idle stdin.
  STDIN_JSON="$(timeout 1 cat 2>/dev/null || true)"
  if [[ -n "$STDIN_JSON" ]]; then
    EDITED_FILE="$(printf '%s' "$STDIN_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('file_path',''))" 2>/dev/null || true)"
  fi
fi

# Normalize to relative path for pattern matching
REL_FILE="${EDITED_FILE#"$REPO_ROOT/"}"

CATALOG_PATTERNS=(
  "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv"
  "wordpress-theme/skyyrose-flagship/data/visual-manifest.json"
  "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
  "wordpress-theme/skyyrose-flagship/data/product-similarities.json"
  "skyyrose/elite_studio/sku_resolver.py"
  "skyyrose/elite_studio/logo_registry.py"
  "skyyrose/elite_studio/commerce.py"
)

# Per feedback_canonical_sources_only.md (locked 2026-05-27): dossier .md
# files are the second authoritative source and any touch must announce.
DOSSIER_GLOB_PREFIX="wordpress-theme/skyyrose-flagship/data/dossiers/"

MATCHED=0
for pattern in "${CATALOG_PATTERNS[@]}"; do
  if [[ "$REL_FILE" == "$pattern" ]]; then
    MATCHED=1
    break
  fi
done

if [[ "$MATCHED" == "0" && "$REL_FILE" == "$DOSSIER_GLOB_PREFIX"*.md ]]; then
  MATCHED=1
fi

if [[ "$MATCHED" == "0" ]]; then
  exit 0
fi

# ── Detect Python ──────────────────────────────────────────────────────────
PYTHON=""
for candidate in \
    "${REPO_ROOT}/.venv/bin/python3" \
    "$(command -v python3 2>/dev/null || true)"; do
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  exit 0
fi

# ── Regenerate + verify per-collection SOT (when a SOT master is edited) ───
# data/collections/*.json are a GENERATED VIEW of three masters (catalog CSV,
# visual-manifest.json, logo-registry.json). Editing a master without
# regenerating leaves the view stale — the exact drift that caused repeated
# wrong-file pick-ups. Regenerate + verify in-session so the view never lags.
# Placed BEFORE the optional catalog-validator gate so a repo without that
# validator still keeps the SOT current.
# SOT masters. Collection identity (canon) lives in logo-registry.json's collections section.
SOT_MASTERS=(
  "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv"
  "wordpress-theme/skyyrose-flagship/data/visual-manifest.json"
  "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
)
SOT_DATA_DIR="${REPO_ROOT}/wordpress-theme/skyyrose-flagship/data"
SOT_TRIGGER=0
for master in "${SOT_MASTERS[@]}"; do
  if [[ "$REL_FILE" == "$master" ]]; then
    SOT_TRIGGER=1
    break
  fi
done
# Full SOT pipeline: design-tokens (from the registry's collections) → per-folder sot.json → designer
# hubs → verify. Editing any master without regenerating leaves the generated view
# stale — the exact drift that caused repeated wrong-file pick-ups.
if [[ "$SOT_TRIGGER" == "1" && -f "${SOT_DATA_DIR}/build-collection-sot.py" ]]; then
  if "$PYTHON" "${SOT_DATA_DIR}/gen-design-tokens.py" >/dev/null 2>&1 \
    && "$PYTHON" "${SOT_DATA_DIR}/build-collection-sot.py" >/dev/null 2>&1 \
    && "$PYTHON" "${SOT_DATA_DIR}/gen-collection-hub.py" >/dev/null 2>&1; then
    if "$PYTHON" "${SOT_DATA_DIR}/verify-collection-sot.py" >/dev/null 2>&1; then
      echo ""
      echo "[catalog-drift-guard] SOT pipeline regenerated + verified (design-tokens + sot.json + hubs) after ${REL_FILE} edit."
      echo ""
    else
      echo ""
      echo "[catalog-drift-guard] WARNING: SOT regenerated but verification FAILED after editing ${REL_FILE}."
      echo "  Run: python3 wordpress-theme/skyyrose-flagship/data/verify-collection-sot.py   (to see details)"
      echo ""
    fi
  else
    echo ""
    echo "[catalog-drift-guard] WARNING: SOT pipeline regeneration FAILED after editing ${REL_FILE}."
    echo "  Run the generators in wordpress-theme/skyyrose-flagship/data/ to see details."
    echo ""
  fi
fi

# ── Regenerate registry projections + verify the single entry point ───────
# The registry is the authored SOT; the CSV, the dossier .md files and every
# generated manifest are projections of it. Editing the registry without
# re-running the sync leaves those projections stale until CI notices — so the
# sync runs here, in-session, on every edit.
#
# Then the entry point every agent calls (skyyrose.core.product.get_product) is
# exercised across all SKUs. It fails closed, so a registry edit that breaks a
# record surfaces immediately rather than at the next render or ad build.
ORGANIZER="${REPO_ROOT}/scripts/organize_product_registry.py"
if [[ -f "$ORGANIZER" ]]; then
  ORG_OUT="$("$PYTHON" "$ORGANIZER" --check --quiet 2>&1)" || true
  case "$ORG_OUT" in
    *"registry organized"*)
      echo "[catalog-drift-guard] ${ORG_OUT}"
      ;;
    *"order"*)
      # Ordering alone is cosmetic and fixed by --apply; never block on it.
      echo "[catalog-drift-guard] registry schema-valid; ${ORG_OUT}"
      ;;
    *)
      echo ""
      echo "[catalog-drift-guard] WARNING: registry schema/consistency check FAILED."
      echo "  ${ORG_OUT}"
      echo "  Run: python scripts/organize_product_registry.py --check   (to see details)"
      echo ""
      ;;
  esac
fi

SYNC="${REPO_ROOT}/scripts/sync_product_registry.py"
if [[ -f "$SYNC" ]]; then
  if "$PYTHON" "$SYNC" >/dev/null 2>&1; then
    echo "[catalog-drift-guard] registry projections regenerated after ${REL_FILE} edit."
  else
    echo ""
    echo "[catalog-drift-guard] WARNING: projection sync FAILED after editing ${REL_FILE}."
    echo "  Run: python scripts/sync_product_registry.py   (to see details)"
    echo ""
  fi
fi

ENTRY_CHECK="$(
  "$PYTHON" - <<'PYEOF' 2>&1
import sys

try:
    from skyyrose.core.product import gap_report, get_all_products
except Exception as exc:  # import-time failure is itself the finding
    print(f"IMPORT_FAILED {exc}")
    sys.exit(1)

try:
    records = get_all_products()
except Exception as exc:
    print(f"RESOLVE_FAILED {exc}")
    sys.exit(1)

undeclared = [
    f"{sku}.{field}"
    for sku, rec in records.items()
    for field, value in rec["content"].items()
    if value is None and f"content.{field}" not in rec["gaps"]
]
if undeclared:
    print(f"UNDECLARED_BLANKS {', '.join(undeclared[:5])}")
    sys.exit(1)
print(f"OK {len(records)} SKUs, {len(gap_report())} with declared gaps")
PYEOF
)" || true

case "$ENTRY_CHECK" in
  OK*)
    echo "[catalog-drift-guard] product entry point verified: ${ENTRY_CHECK#OK }"
    ;;
  *)
    echo ""
    echo "[catalog-drift-guard] WARNING: product entry point check FAILED after editing ${REL_FILE}."
    echo "  ${ENTRY_CHECK}"
    echo "  Run: python -m skyyrose.core.product --gaps   (to see details)"
    echo ""
    ;;
esac

VALIDATOR="${REPO_ROOT}/scripts/validate_catalog_consistency.py"
if [[ ! -f "$VALIDATOR" ]]; then
  exit 0
fi

# ── Run validator (quiet, non-blocking) ────────────────────────────────────
if ! "$PYTHON" "$VALIDATOR" --quiet 2>/dev/null; then
  echo ""
  echo "[catalog-drift-guard] WARNING: Catalog consistency check failed after editing ${REL_FILE}."
  echo "  Run: make validate-catalog   (to see details)"
  echo "  Fix: make sync-catalog-dry   (preview auto-fixes)"
  echo "  The pre-commit hook will block commits until checks pass."
  echo ""
fi

# Always announce the touch so the active agent re-reads the source before
# any subsequent product claim. Memory may be stale; canonical files won.
echo ""
echo "[catalog-drift-guard] CANONICAL PRODUCT DATA TOUCHED: ${REL_FILE}"
echo "  Before claiming any product fact, read it through the single entry point:"
echo "    from skyyrose.core.product import get_product   (or: python -m skyyrose.core.product <sku>)"
echo "  Never the CSV, a dossier file, or a hardcoded assets/images/products/ path."
echo ""

exit 0
