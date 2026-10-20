"""Exact production uses of unchanged media; no deployment authority."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from skyyrose.core.media_usage import bound_document

TARGET = "https://skyyrose.co"
SITE_ID = "238510894"
APPROVAL_SHA = "9b0f55aa5cfb61f222602a7908436c28be688b4fdc504f542567a4e1011e1717"
ROLES = {
    "card_front",
    "pdp_on_model_front",
    "collection_hero",
    "collection_story",
    "merchandise_scene",
}
EXCLUDED = "assets/v2-original/scenes/lh-004-back-hood-l2.webp"


def exact_file(theme: Path, relative: str, digest: str) -> bool:
    if (
        not isinstance(relative, str)
        or not re.fullmatch(r"(?:assets|data)/[A-Za-z0-9_./-]+", relative)
        or ".." in Path(relative).parts
    ):
        return False
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        return False
    p = theme
    for part in Path(relative).parts:
        p /= part
        if p.is_symlink():
            return False
    return (
        not theme.is_symlink()
        and p.is_file()
        and hashlib.sha256(p.read_bytes()).hexdigest() == digest
    )


def normalize_approval(approval: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    """Caller verifies original approval bytes before this deterministic projection."""
    masters = {}
    for row in approval["scope"]["rows"]:
        relative = row["asset"]
        record = inventory["assets"][relative]
        if relative in masters or row["sha256"] != record["sha256"]:
            raise ValueError("Duplicate or changed approved master")
        masters[relative] = {
            "sha256": row["sha256"],
            "review": {k: record["review"][k] for k in ("path", "sha256")},
            "skus": record["skus"],
            "collections": record["collections"],
            "roles": row["approved_roles"],
            "delivery_files": row["delivery_files"],
            "creative_treatment": row["creative_treatment"],
        }
    return {
        "schema": "skyyrose.production-media-authority.v1",
        "authority": "FOUNDER_CONFIRMED",
        "principal": "Corey",
        "decision_text": approval["authority"]["message_text"],
        "message_id": approval["authority"]["message_id"],
        "message_time_utc": approval["authority"]["message_time_utc"],
        "approval_receipt_sha256": APPROVAL_SHA,
        "target": TARGET,
        "expected_site_id": SITE_ID,
        "media_use_authorized": True,
        "deployment_authorized": False,
        "scope": {"masters": 22, "delivery_files": 113, "role_memberships": 53},
        "excluded_roles": [{"asset": EXCLUDED, "role": "collection_scene_back"}],
        "masters": masters,
    }


def _authority(
    inventory: dict[str, Any], theme: Path, *, target: str = TARGET, site_id: str = SITE_ID
) -> dict[str, Any] | None:
    doc = bound_document(theme, inventory.get("production_media_authority"))
    if (
        not doc
        or target != TARGET
        or site_id != SITE_ID
        or doc.get("schema") != "skyyrose.production-media-authority.v1"
        or doc.get("authority") != "FOUNDER_CONFIRMED"
        or doc.get("principal") != "Corey"
        or doc.get("decision_text") != "all of them are approved"
        or doc.get("message_id") != "Sentinel_a6f502418ee48191a8bcccc21a97916d"
        or doc.get("approval_receipt_sha256") != APPROVAL_SHA
        or doc.get("target") != target
        or doc.get("expected_site_id") != site_id
        or doc.get("media_use_authorized") is not True
        or doc.get("deployment_authorized") is not False
        or doc.get("scope") != {"masters": 22, "delivery_files": 113, "role_memberships": 53}
        or doc.get("excluded_roles") != [{"asset": EXCLUDED, "role": "collection_scene_back"}]
    ):
        return None
    masters = doc.get("masters")
    if not isinstance(masters, dict) or len(masters) != 22:
        return None
    files, memberships = set(masters), 0
    for relative, entry in masters.items():
        if not isinstance(entry, dict):
            return None
        record = inventory.get("assets", {}).get(relative, {})
        if (
            any(entry.get(k) != record.get(k) for k in ("sha256", "skus", "collections"))
            or entry.get("review")
            != {k: record.get("review", {}).get(k) for k in ("path", "sha256")}
            or not isinstance(entry.get("skus"), list)
            or len(entry["skus"]) != 1
            or not isinstance(entry.get("collections"), list)
            or len(entry["collections"]) != 1
        ):
            return None
        roles, deliveries = entry.get("roles"), entry.get("delivery_files")
        if (
            not isinstance(roles, list)
            or not roles
            or any(not isinstance(r, str) or r not in ROLES for r in roles)
            or len(set(roles)) != len(roles)
            or not isinstance(deliveries, list)
            or entry.get("creative_treatment") != "APPROVED_AS_PRESENTED_IN_22_IMAGE_SAFARI_GALLERY"
        ):
            return None
        memberships += len(roles)
        for delivery in deliveries:
            if (
                not isinstance(delivery, dict)
                or set(delivery) != {"path", "sha256"}
                or not isinstance(delivery["path"], str)
                or delivery["path"] in files
            ):
                return None
            child = inventory.get("assets", {}).get(delivery["path"], {})
            if (
                child.get("sha256") != delivery["sha256"]
                or child.get("source_path") != relative
                or child.get("source_sha256") != entry["sha256"]
                or child.get("skus") != entry["skus"]
                or child.get("collections") != entry["collections"]
            ):
                return None
            files.add(delivery["path"])
    return doc if len(files) == 135 and memberships == 53 else None


def authority(
    inventory: dict[str, Any], theme: Path, *, target: str = TARGET, site_id: str = SITE_ID
) -> dict[str, Any] | None:
    try:
        return _authority(inventory, theme, target=target, site_id=site_id)
    except (TypeError, KeyError, AttributeError, ValueError, OSError):
        return None


def production_roles(
    relative: str,
    record: dict[str, Any],
    inventory: dict[str, Any],
    theme: Path,
    *,
    target: str = TARGET,
    site_id: str = SITE_ID,
) -> list[str] | None:
    """None means outside the approval; [] refuses a governed or invalid request.

    This validates the intended approval recipient, not an installed-site login.
    Source acceptance is checked separately by the PHP and package provenance gates.
    """
    if "production_media_authority" not in inventory:
        return []  # Production consumers never fall back when the authority is missing.
    doc = authority(inventory, theme, target=target, site_id=site_id)
    if doc is None:
        return []
    if record != inventory.get("assets", {}).get(relative):
        return []
    master = relative if relative in doc["masters"] else record.get("source_path")
    if not isinstance(master, str) or master not in doc["masters"]:
        return None
    entry = doc["masters"][master]
    files = {master: entry["sha256"], **{x["path"]: x["sha256"] for x in entry["delivery_files"]}}
    if (
        relative not in files
        or record.get("sha256") != files[relative]
        or not exact_file(theme, relative, files[relative])
        or not exact_file(theme, master, entry["sha256"])
        or bound_document(theme, entry["review"]) is None
    ):
        return []
    return entry["roles"].copy()


def validate_scope(inventory: dict[str, Any], theme: Path) -> dict[str, Any]:
    doc = authority(inventory, theme)
    if doc is None:
        raise ValueError("Missing or invalid exact production media authority")
    for master, entry in doc["masters"].items():
        for relative in [master, *[x["path"] for x in entry["delivery_files"]]]:
            if (
                production_roles(relative, inventory["assets"].get(relative, {}), inventory, theme)
                != entry["roles"]
            ):
                raise ValueError("Production media body or binding refused: " + relative)
    return doc
