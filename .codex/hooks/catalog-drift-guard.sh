#!/usr/bin/env bash
# catalog-drift-guard.sh — PostToolUse hook: regenerate + verify the product
# projections after an edit to the product registry (the ONE editable SOT), one
# of its generated projections, or one of its readers.
#
# Fires after Edit/Write/MultiEdit. Non-blocking: prints warnings; the pre-commit
# hook and CI block. Payload (Claude Code and Codex): JSON on stdin with
# `.tool_input.file_path` = the edited file. The repo root is resolved FROM THAT
# FILE, so the hook works in every worktree of this repo, not only the checkout
# it is wired from.

set -euo pipefail

# ── Edited file ────────────────────────────────────────────────────────────
EDITED_FILE="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"
if [[ -z "$EDITED_FILE" ]]; then
  PAYLOAD="$(cat 2>/dev/null || true)"
  if [[ -n "$PAYLOAD" ]]; then
    if command -v jq >/dev/null 2>&1; then
      EDITED_FILE="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // ""' 2>/dev/null || true)"
    elif command -v python3 >/dev/null 2>&1; then
      EDITED_FILE="$(printf '%s' "$PAYLOAD" | python3 -c 'import json, sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null || true)"
    else
      echo "[catalog-drift-guard] neither jq nor python3 on PATH — payload unreadable, drift guard NOT run." >&2
      exit 2
    fi
  fi
fi
[[ -n "$EDITED_FILE" && -e "$EDITED_FILE" ]] || exit 0

# ── Resolve paths from the edited file ─────────────────────────────────────
# Follow symlinks (repo-root logo-registry.json → the theme data file) so an
# edit through either path is recognised.
REAL_FILE="$(readlink -f "$EDITED_FILE" 2>/dev/null || printf '%s' "$EDITED_FILE")"
REPO_ROOT="$(git -C "$(dirname "$REAL_FILE")" rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$REPO_ROOT" ]] || exit 0   # outside any git checkout: nothing to guard
REL_FILE="${REAL_FILE#"$REPO_ROOT/"}"

# ── Gate: registry, its projections, or its readers ────────────────────────
# logo-registry.json is the ONE editable product SOT (CLAUDE.md). The CSV and
# the dossier .md files are projections generated from it by
# scripts/sync_product_registry.py; the Python readers below resolve it.
# visual-manifest.json is NOT a projection: it is the editable master for
# non-product imagery (sot_common.py loads it as a master). product-similarities
# .json is written by scripts/build_product_similarities.py, not by the sync.
DATA_DIR="wordpress-theme/skyyrose-flagship/data"
REGISTRY="${DATA_DIR}/logo-registry.json"
IMAGERY_MASTER="${DATA_DIR}/visual-manifest.json"
SIMILARITIES="${DATA_DIR}/product-similarities.json"
PROJECTIONS=(
  "${DATA_DIR}/skyyrose-catalog.csv"
)
DOSSIER_GLOB_PREFIX="${DATA_DIR}/dossiers/"
READERS=(
  "skyyrose/core/product.py"
  "skyyrose/core/product_registry.py"
  "skyyrose/elite_studio/sku_resolver.py"
  "skyyrose/elite_studio/logo_registry.py"
)

KIND=""
if [[ "$REL_FILE" == "$REGISTRY" ]]; then
  KIND="registry"
elif [[ "$REL_FILE" == "$DOSSIER_GLOB_PREFIX"*.md ]]; then
  KIND="projection"
elif [[ "$REL_FILE" == "$IMAGERY_MASTER" ]]; then
  KIND="imagery-master"
elif [[ "$REL_FILE" == "$SIMILARITIES" ]]; then
  KIND="generated"
fi
if [[ -z "$KIND" ]]; then
  for pattern in "${PROJECTIONS[@]}"; do
    [[ "$REL_FILE" == "$pattern" ]] && KIND="projection" && break
  done
fi
if [[ -z "$KIND" ]]; then
  for pattern in "${READERS[@]}"; do
    [[ "$REL_FILE" == "$pattern" ]] && KIND="reader" && break
  done
fi
[[ -n "$KIND" ]] || exit 0

# ── Detect Python ──────────────────────────────────────────────────────────
# Worktrees have no venv of their own — fall back to the primary checkout's
# (first entry of `git worktree list`), then PATH.
MAIN_WT="$(git -C "$REPO_ROOT" worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')"
PYTHON=""
for candidate in \
    "${REPO_ROOT}/.venv/bin/python3" \
    "${MAIN_WT:-/nonexistent}/.venv/bin/python3" \
    "$(command -v python3 2>/dev/null || true)"; do
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    PYTHON="$candidate"
    break
  fi
done
if [[ -z "$PYTHON" ]]; then
  echo "[catalog-drift-guard] no python3 found — projections NOT regenerated after editing ${REL_FILE}." >&2
  exit 2
fi

# Run every generator and check inside the edited file's checkout so that
# tree's registry, scripts and package are the ones exercised.
cd "$REPO_ROOT"

# ── Regenerate + verify per-collection SOT ─────────────────────────────────
# data/collections/*.json are a GENERATED VIEW built from the registry (and
# the projections the generators still read: the CSV and visual-manifest.json).
# Editing an input without regenerating leaves the view stale — the exact drift
# that caused repeated wrong-file pick-ups. Regenerate + verify in-session.
COLLECTION_INPUTS=(
  "$REGISTRY"
  "${DATA_DIR}/skyyrose-catalog.csv"
  "${DATA_DIR}/visual-manifest.json"
)
SOT_DATA_DIR="${REPO_ROOT}/${DATA_DIR}"
SOT_TRIGGER=0
for input in "${COLLECTION_INPUTS[@]}"; do
  if [[ "$REL_FILE" == "$input" ]]; then
    SOT_TRIGGER=1
    break
  fi
done
# Full SOT pipeline: design-tokens (from the registry's collections) → per-folder
# sot.json → designer hubs → verify.
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
      echo "  Run: python3 ${DATA_DIR}/verify-collection-sot.py   (to see details)"
      echo ""
    fi
  else
    echo ""
    echo "[catalog-drift-guard] WARNING: SOT pipeline regeneration FAILED after editing ${REL_FILE}."
    echo "  Run the generators in ${DATA_DIR}/ to see details."
    echo ""
  fi
fi

# ── Regenerate registry projections + verify the single entry point ───────
# The registry is the authored SOT; the CSV, the dossier .md files and every
# generated manifest are projections of it. Editing the registry without
# re-running the sync leaves those projections stale until CI notices — so the
# sync runs here, in-session, on every edit. (A direct edit to a projection is
# overwritten by this same sync: the registry wins.)
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
if [[ -f "$VALIDATOR" ]] && ! "$PYTHON" "$VALIDATOR" --quiet 2>/dev/null; then
  echo ""
  echo "[catalog-drift-guard] WARNING: Catalog consistency check failed after editing ${REL_FILE}."
  echo "  Run: make validate-catalog   (to see details)"
  echo "  Fix: make sync-catalog-dry   (preview auto-fixes)"
  echo "  The pre-commit hook will block commits until checks pass."
  echo ""
fi

# Always announce the touch so the active agent re-reads the source before
# any subsequent product claim. Memory may be stale; the registry wins.
echo ""
case "$KIND" in
  registry)
    echo "[catalog-drift-guard] CANONICAL PRODUCT DATA TOUCHED: ${REL_FILE}"
    ;;
  projection)
    echo "[catalog-drift-guard] PRODUCT PROJECTION EDITED: ${REL_FILE}"
    echo "  This file is generated from ${REGISTRY} by scripts/sync_product_registry.py;"
    echo "  the sync above regenerates it, so a direct edit does not survive. Apply the change in the registry."
    ;;
  imagery-master)
    echo "[catalog-drift-guard] NON-PRODUCT IMAGERY MASTER EDITED: ${REL_FILE}"
    echo "  This is the editable master for non-product imagery (SOT.md); the per-collection views"
    echo "  above regenerate from it. Product facts do not belong here — they live in ${REGISTRY}."
    ;;
  generated)
    echo "[catalog-drift-guard] GENERATED FILE EDITED: ${REL_FILE}"
    echo "  scripts/build_product_similarities.py writes this file, so a direct edit is overwritten on"
    echo "  its next run. Change the generator's inputs and re-run it instead."
    ;;
  reader)
    echo "[catalog-drift-guard] PRODUCT READER TOUCHED: ${REL_FILE}"
    ;;
esac
echo "  Before claiming any product fact, read it through the single entry point:"
echo "    from skyyrose.core.product import get_product   (or: python -m skyyrose.core.product <sku>)"
echo "  Never the CSV, a dossier file, or a hardcoded assets/images/products/ path."
echo ""

exit 0
