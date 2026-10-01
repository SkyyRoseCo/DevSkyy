#!/usr/bin/env python3
"""
GLB candidate manifest — hash-bound local assets from a heuristic triage report.

A triage pass is not product, creative or release approval. Unbound historical
QC results remain BLOCKED. Missing, malformed or stale assets fail closed.

OUTPUT ONLY. Makes zero WordPress/WooCommerce writes and zero paid API calls — a
separate, explicitly-confirmed deploy step consumes this file.

Usage:
    python scripts/glb_publish_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skyyrose.core.product import get_product  # noqa: E402
from skyyrose.elite_studio.pipeline3d.glb_container import (  # noqa: E402
    read_glb,
    require_embedded_resources,
)


def build_publish_manifest(sku_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Bind candidate bytes and canonical identity without granting publication."""
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    registry_path = ROOT / "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
    registry_hash = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    for row in sku_rows:
        if row.get("verdict") != "pass":
            continue
        sku = row["sku"]
        if sku in seen:
            raise ValueError(f"Duplicate candidate SKU: {sku}")
        seen.add(sku)
        product = get_product(sku)
        source = product["provenance"]["sources"]["registry"]
        if (ROOT / source["path"]).resolve() != registry_path.resolve() or source[
            "sha256"
        ] != registry_hash[:16]:
            raise ValueError("Registry changed during candidate product reads")
        glb_path = Path(row["glb"]).resolve(strict=True)
        data = glb_path.read_bytes()
        container = read_glb(data)
        require_embedded_resources(container.document)
        digest = hashlib.sha256(data).hexdigest()
        reported_hash = row.get("glb_sha256")
        if reported_hash is not None and reported_hash != digest:
            raise ValueError(f"Stale QC artifact hash: {sku}")
        # Preserve the registry source identity, not a separate copy of product facts.
        entries.append(
            {
                "sku": sku,
                "glb_path": str(glb_path),
                "glb_bytes": len(data),
                "glb_sha256": digest,
                "registry_sha256": registry_hash,
                "product_entry_point": "skyyrose.core.product.get_product",
                "qc_binding": "PASS" if reported_hash == digest else "BLOCKED",
                "qc_binding_reason": (
                    "Artifact hash matches triage receipt"
                    if reported_hash == digest
                    else "Historical triage receipt has no artifact hash"
                ),
                "product_fidelity": "NOT RUN",
                "creative_approval": "BLOCKED",
                "publication_authorized": False,
                "color_delta_e": row.get("color_delta_e"),
                "master": row.get("master"),
            }
        )
    if hashlib.sha256(registry_path.read_bytes()).hexdigest() != registry_hash:
        raise ValueError("Registry changed during candidate product reads")
    return {
        "schema": "skyyrose.glb-candidates.v2",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "publication_authorized": False,
        "note": (
            "CANDIDATES ONLY — heuristic triage is not product or creative approval. "
            "No WordPress/WooCommerce writes, no paid API calls."
        ),
        "entries": entries,
        "summary": {"count": len(entries)},
    }


def main() -> None:
    report_path = ROOT / "renders/3d/qc/fidelity_report.json"
    if not report_path.exists():
        sys.exit(f"No fidelity_report.json at {report_path} — run scripts/glb_fidelity.py first")
    report = json.loads(report_path.read_text(encoding="utf-8"))

    manifest = build_publish_manifest(report["skus"])

    manifest_path = report_path.with_name("publish_manifest.json")
    tmp_path = manifest_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    os.replace(tmp_path, manifest_path)

    print(
        f"Candidate manifest -> {manifest_path} ({manifest['summary']['count']} candidate SKU(s))"
    )


if __name__ == "__main__":
    main()
