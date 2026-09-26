"""Field-owned execution facts; raw product evidence remains in the audit bundle.

Never modifies the registry or marketing copy. No NLP rewrite of founder facts.
"""

from __future__ import annotations

import re
from typing import Any

AUTHORITY_STATES = (
    "AUTHORITATIVE_CURRENT",
    "DERIVED_CURRENT",
    "STALE",
    "SUPERSEDED",
    "CONFLICTED",
    "UNKNOWN",
)


def _field(value: Any, source: str, authority: str = "FOUNDER_PRODUCT_SPECIFICATIONS") -> dict:
    return {
        "value": value,
        "source": source,
        "authority": authority,
        "status": "UNKNOWN" if value is None else "AUTHORITATIVE_CURRENT",
    }


def _strings(value: Any, path: str):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(item, f"{path}.{key}")


def project_product(record: dict, required_views: list[str], required_details: list[str]) -> dict:
    """Return separate execution and audit conflict views using explicit field ownership."""
    catalog = record.get("catalog", {})
    placements = record.get("logos", {}).get("placements", [])
    front = [p for p in placements if "front" in p.get("position", "").lower()]
    techniques = sorted({p["technique"] for p in front if p.get("technique")})
    treatment = techniques[0] if len(techniques) == 1 else (techniques or None)
    preorder_raw = catalog.get("is_preorder")
    preorder = {"0": False, "1": True, "false": False, "true": True}.get(str(preorder_raw).lower())
    fields = {
        "name": _field(record.get("name"), "catalog.name", "REGISTRY"),
        "collection": _field(record.get("collection"), "catalog.collection", "REGISTRY"),
        "color": _field(record.get("garment", {}).get("color"), "garment.color"),
        "front_treatment": _field(treatment, "logos.placements[position=front].technique"),
        "preorder": _field(
            preorder, "catalog.is_preorder", "REGISTRY_DESIRED_STATE_NOT_LIVE_COMMERCE"
        ),
    }
    for key in ("fit", "materials", "features"):
        fields[key] = _field(record.get("garment", {}).get(key), f"garment.{key}")
    conflicts = []
    excluded = []
    # Position-sensitive claim detection; legitimate back embroidery is never rewritten.
    for path, text in list(_strings(record.get("content", {}), "content")) + [
        ("catalog.description", catalog.get("description", "")),
    ]:
        if not text:
            continue
        excluded.append(
            {
                "source": path,
                "status": "UNKNOWN",
                "reason": "Editorial copy is not an owned product fact",
            }
        )
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            is_back = bool(re.search(r"\b(back|rear|back-neck)\b", sentence, re.I))
            is_front = bool(re.search(r"\b(front|chest|rose[s]?)\b", sentence, re.I))
            if (
                treatment == "embossed"
                and re.search(r"embroider", sentence, re.I)
                and (is_front or not is_back)
            ):
                conflicts.append(
                    {
                        "field": "front_treatment",
                        "source": path,
                        "value": sentence,
                        "status": "SUPERSEDED",
                        "resolution": "Use front placement technique",
                        "selected_source": fields["front_treatment"]["source"],
                    }
                )
            if preorder is False and re.search(r"\bpre[- ]?order", sentence, re.I):
                conflicts.append(
                    {
                        "field": "preorder",
                        "source": path,
                        "value": sentence,
                        "status": "STALE",
                        "resolution": "Use current registry preorder flag",
                        "selected_source": "catalog.is_preorder",
                    }
                )
    branding = record.get("dossier", {}).get("branding_block", "")
    spec = catalog.get("branding_spec", "")
    # Detect axis disagreement without selecting an unstated axis for size_inches.
    spec_axis = set(
        re.findall(r'\b(\d+(?:\.\d+)?)\s*(?:inches?|in\.?|["″])?\s*(wide|tall)\b', spec, re.I)
    )
    dossier_axis = set(
        re.findall(r'\b(\d+(?:\.\d+)?)\s*(?:inches?|in\.?|["″])?\s*(wide|tall)\b', branding, re.I)
    )
    dimension_conflict = bool(spec_axis and dossier_axis and spec_axis != dossier_axis)
    if dimension_conflict:
        conflicts.append(
            {
                "field": "decoration_dimensions",
                "source": "catalog.branding_spec vs dossier.branding_block",
                "value": {"catalog": spec, "dossier": branding},
                "status": "CONFLICTED",
                "resolution": "No inferred axis; preserve reference scale. Required dimensional reconstruction blocks.",
                "selected_source": None,
            }
        )
    safe_placements = [
        {
            k: v
            for k, v in p.items()
            if not (dimension_conflict and ("size" in k or "dimension" in k))
        }
        for p in placements
        if any(view.startswith("front") or view == "packshot" for view in required_views)
        and "front" in p.get("position", "").lower()
    ]
    # Back prose is not converted into guessed structured technique; its authoritative reference remains controlling.
    safe_details = {}
    gaps = []
    for key in required_details:
        if key in fields:
            value = fields[key]["value"]
        elif key.startswith("garment."):
            value = record.get("garment", {}).get(key.split(".", 1)[1])
        elif key == "catalog.is_preorder":
            value = preorder
        else:
            value = None
        if value is None or value == "" or value == {} or value == []:
            gaps.append(
                {
                    "field": key,
                    "status": "UNKNOWN",
                    "reason": "Required detail has no safe owned projection",
                }
            )
        else:
            safe_details[key] = (
                dict(fields[key])
                if key in fields
                else (
                    dict(fields["preorder"]) if key == "catalog.is_preorder" else _field(value, key)
                )
            )
    if dimension_conflict and any(
        re.search(r"dimension|size_inches|branding_spec", d) for d in required_details
    ):
        gaps.append(
            {
                "field": "decoration_dimensions",
                "status": "CONFLICTED",
                "reason": "Required dimension axis is unresolved",
            }
        )
    execution = {
        "sku": record["sku"],
        "mode": "EXACT_PRODUCT",
        "facts": fields,
        "required_views": required_views,
        "required_details": safe_details,
        "references": {view: record.get("images", {}).get(view) for view in required_views},
        "protected_placements": safe_placements,
        "negative_constraints": [
            "Preserve exact silhouette, proportions, color, artwork, logos, construction, placement and reference scale.",
            "No invented views, recoloring, moved marks, merged products or approximation presented as real SKU.",
        ],
        "founder_corrections": record.get("corrections", []),
        "permissions": {"product_mutation": False, "live_commerce_claims": False},
        "unresolved_required_gaps": gaps,
        "conflict_outcomes": [{k: v for k, v in c.items() if k != "value"} for c in conflicts],
        "excluded_editorial_sources": [e["source"] for e in excluded],
    }
    return {"execution": execution, "conflicts": conflicts, "excluded_editorial": excluded}
