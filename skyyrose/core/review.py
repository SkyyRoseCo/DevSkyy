"""Ghost-mannequin review and approval — atomic CSV writes, audit logs.

Phase 17 (REV-01..04). The CLI entrypoints in scripts/approve_ghost.py and
scripts/reject_ghost.py are thin wrappers; all logic lives here so it stays
testable without subprocess plumbing.

Public surface:
    approve(sku, *, root=None) -> ApprovalResult
    reject(sku, reason, *, root=None) -> RejectionResult
    atomic_csv_write(rows, fieldnames, csv_path) -> None
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import shutil
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

CATALOG_REL = "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv"
GHOST_REL = "renders/ghost-mannequin"
APPROVED_SUBDIR = "approved"
FRONT_MODEL_COL = "front_model_image"
GHOST_FILENAME_FMT = "{sku}-ghost-front.webp"
# Approved ghost renders are copied into the THEME's deployable assets tree so the
# storefront resolves front_model_image via get_theme_file_uri(). The repo-local
# renders/ path is NOT shipped by deploy-theme.sh, so it must never be the CSV value.
THEME_GHOST_REL = "wordpress-theme/skyyrose-flagship/assets/images/products/ghost"
FRONT_MODEL_VALUE_FMT = "assets/images/products/ghost/{sku}-ghost-front.webp"
APPROVALS_JSON = "approvals.json"
REJECTIONS_JSON = "rejections.json"

# Catalog SKUs follow {collection-prefix}-{3-digit-id}: br-001..015, sg-001..015,
# lh-002..005, kids-001..002. Derived from actual catalog 2026-05-19 — update the
# range if a new collection prefix is added.
_SKU_RE = re.compile(r"^[a-z]{2,4}-\d{3}$")

_log = logging.getLogger(__name__)


class ReviewError(Exception):
    """Reviewable failure — caller should print message and exit 1."""


@dataclass(frozen=True)
class ApprovalResult:
    sku: str
    approved_path: Path
    csv_path: Path
    timestamp: str


@dataclass(frozen=True)
class RejectionResult:
    sku: str
    reason: str
    file_path: Path
    timestamp: str


def _validate_sku(sku: str) -> None:
    """Reject any sku that could escape the ghost-mannequin dir or poison the CSV.

    The SKU is interpolated into file paths AND written into the catalog's
    front_model_image column which ships to WordPress. A traversal-looking
    string would break both. Allowlist regex defends both surfaces.
    """
    if not sku:
        raise ReviewError("sku is required")
    if not _SKU_RE.fullmatch(sku):
        raise ReviewError(
            f"invalid sku {sku!r}: must match {_SKU_RE.pattern} (e.g. br-001, sg-005, kids-002)"
        )


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _resolve_root(root: Path | str | None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[2]


def _catalog_path(root: Path) -> Path:
    return root / CATALOG_REL


def _ghost_dir(root: Path) -> Path:
    return root / GHOST_REL


def _approved_dir(root: Path) -> Path:
    return _ghost_dir(root) / APPROVED_SUBDIR


def _review_file(root: Path, sku: str) -> Path:
    return _ghost_dir(root) / GHOST_FILENAME_FMT.format(sku=sku)


def _approved_file(root: Path, sku: str) -> Path:
    return _approved_dir(root) / GHOST_FILENAME_FMT.format(sku=sku)


def atomic_csv_write(
    rows: Sequence[dict],
    fieldnames: Sequence[str],
    csv_path: Path,
) -> None:
    """Write rows to csv_path atomically via tempfile + os.replace().

    Same filesystem guaranteed because tmp file is created in the target's
    parent directory. SIGINT or crash between write and replace leaves the
    original file intact.
    """
    csv_path = Path(csv_path)
    parent = csv_path.parent
    fd, tmp_path = tempfile.mkstemp(dir=parent, prefix=".tmp_review_", suffix=".csv")
    try:
        try:
            handle = os.fdopen(fd, "w", newline="", encoding="utf-8")
        except BaseException:
            os.close(fd)
            raise
        with handle as f:
            writer = csv.DictWriter(f, fieldnames=list(fieldnames))
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp_path, csv_path)
    except BaseException:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise


def _atomic_json_write(records: list[dict], json_path: Path) -> None:
    parent = json_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=parent, prefix=".tmp_review_", suffix=".json")
    try:
        try:
            handle = os.fdopen(fd, "w", encoding="utf-8")
        except BaseException:
            os.close(fd)
            raise
        with handle as f:
            json.dump(records, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_path, json_path)
    except BaseException:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise


def _load_json_list(json_path: Path) -> list[dict]:
    if not json_path.exists():
        return []
    try:
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ReviewError(
            f"audit log corrupted (invalid JSON): {json_path} — "
            f"inspect and fix manually before re-running"
        ) from exc
    if not isinstance(data, list):
        raise ReviewError(f"{json_path} is not a JSON list")
    return data


def _read_catalog(csv_path: Path) -> tuple[list[dict], list[str]]:
    from skyyrose.core.catalog_loader import CATALOG_CSV, read_catalog_rows

    if csv_path.resolve() == CATALOG_CSV.resolve():
        rows = read_catalog_rows()
        return rows, list(rows[0])
    if not csv_path.exists():
        raise ReviewError(f"catalog not found: {csv_path}")
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ReviewError(f"catalog {csv_path} has no header row")
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    if FRONT_MODEL_COL not in fieldnames:
        raise ReviewError(f"catalog missing required column {FRONT_MODEL_COL!r}: {csv_path}")
    return rows, fieldnames


def _find_row_index(rows: Iterable[dict], sku: str) -> int:
    for idx, row in enumerate(rows):
        if row.get("sku") == sku:
            return idx
    raise ReviewError(f"SKU {sku!r} not in catalog")


def _safe_rollback_move(src: Path, dst: Path) -> None:
    """Move dst back to src; log but never raise so the caller's exc surfaces."""
    try:
        shutil.move(str(dst), str(src))
    except OSError as rollback_err:
        _log.warning(
            "rollback move failed after CSV error: %s — %s may be stranded",
            rollback_err,
            dst,
        )


def _best_effort_audit_log(records: list[dict], json_path: Path, action: str) -> None:
    """Append-only audit log writer.

    The commit (file move + CSV write) is already on disk when this is called.
    A log failure must not propagate — that would tell the caller the approval
    failed when it actually succeeded, prompting double-action.
    """
    try:
        _atomic_json_write(records, json_path)
    except OSError as log_err:
        _log.warning(
            "%s committed but audit log write failed: %s (log=%s)",
            action,
            log_err,
            json_path,
        )


def approve(sku: str, *, root: Path | str | None = None) -> ApprovalResult:
    """Move reviewed image to approved/ and update CSV front_model_image.

    Order of operations matters: file move first, then CSV update. If the CSV
    update fails the file move is rolled back so the review queue is not
    silently emptied. If the file move succeeds and the CSV write succeeds the
    operation is committed; audit log is best-effort thereafter.

    Raises ReviewError if:
        - sku does not match the catalog SKU pattern (path-traversal defense)
        - SKU file not in review dir (REV-02 structural gate)
        - SKU not present in catalog
        - approved/ destination already has a file for this SKU
    """
    _validate_sku(sku)

    base = _resolve_root(root)
    src = _review_file(base, sku)
    if not src.is_file():
        raise ReviewError(
            f"no review file for {sku}: expected {src} — "
            f"run ghost-mannequin agent or place file before approving"
        )

    approved_dir = _approved_dir(base)
    approved_dir.mkdir(parents=True, exist_ok=True)
    dst = _approved_file(base, sku)
    if dst.exists():
        raise ReviewError(
            f"already approved: {dst} exists — delete or run reject if you want to re-review"
        )

    csv_path = _catalog_path(base)
    rows, fieldnames = _read_catalog(csv_path)
    row_count_before = len(rows)
    idx = _find_row_index(rows, sku)

    # The CSV value must be a THEME-relative path (get_theme_file_uri-resolvable),
    # never the repo-local renders/ path, which the theme deploy does not ship.
    new_front = FRONT_MODEL_VALUE_FMT.format(sku=sku)
    theme_dst = base / THEME_GHOST_REL / GHOST_FILENAME_FMT.format(sku=sku)

    shutil.move(str(src), str(dst))
    try:
        # Deployable theme copy — what the storefront actually serves. The approved/
        # original stays put for the WooCommerce uploader to read.
        theme_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(dst), str(theme_dst))
        rows[idx] = {**rows[idx], FRONT_MODEL_COL: new_front}
        # Runtime invariant — survives python -O (unlike assert).
        if len(rows) != row_count_before:
            raise ReviewError(
                f"row count drift before write: expected {row_count_before}, got {len(rows)}"
            )
        from skyyrose.core.product_registry import PRODUCT_REGISTRY, update_catalog_fields

        registry_path = csv_path.parent / "logo-registry.json"
        if registry_path.exists() or registry_path.resolve() == PRODUCT_REGISTRY.resolve():
            update_catalog_fields(sku, {FRONT_MODEL_COL: new_front}, registry_path)
        else:
            # Explicit custom-root fixtures retain their standalone CSV behavior.
            atomic_csv_write(rows, fieldnames, csv_path)
    except BaseException:
        if theme_dst.exists():
            try:
                theme_dst.unlink()
            except OSError:
                pass
        if dst.exists() and not src.exists():
            _safe_rollback_move(src, dst)
        raise

    timestamp = _now_iso()
    approvals_path = _ghost_dir(base) / APPROVALS_JSON
    log = _load_json_list(approvals_path)
    log.append(
        {
            "sku": sku,
            "approved_path": str(dst.relative_to(base)),
            "csv_field": FRONT_MODEL_COL,
            "csv_value": new_front,
            "timestamp": timestamp,
        }
    )
    _best_effort_audit_log(log, approvals_path, action="approval")

    return ApprovalResult(sku=sku, approved_path=dst, csv_path=csv_path, timestamp=timestamp)


def reject(
    sku: str,
    reason: str,
    *,
    root: Path | str | None = None,
) -> RejectionResult:
    """Log rejection; leave review file in place; no CSV change.

    Raises ReviewError if sku is invalid, file is not in review dir, or reason is empty.
    """
    _validate_sku(sku)
    if not reason or not reason.strip():
        raise ReviewError("reason is required and may not be empty/whitespace")

    base = _resolve_root(root)
    src = _review_file(base, sku)
    if not src.is_file():
        raise ReviewError(f"no review file for {sku}: expected {src} — nothing to reject")

    timestamp = _now_iso()
    rejections_path = _ghost_dir(base) / REJECTIONS_JSON
    log = _load_json_list(rejections_path)
    log.append(
        {
            "sku": sku,
            "reason": reason.strip(),
            "file": str(src.relative_to(base)),
            "timestamp": timestamp,
        }
    )
    _best_effort_audit_log(log, rejections_path, action="rejection")

    return RejectionResult(sku=sku, reason=reason.strip(), file_path=src, timestamp=timestamp)
