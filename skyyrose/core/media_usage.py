"""Source-bound reuse grants; original visual decisions remain immutable.

This contract grants a placement of already accepted bytes. It does not create
an independent pixel review, permission to generate, or production publication.
Callers must validate the original source acceptance before using these roles.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ADDITIONAL_ROLES = frozenset(
    {"pdp_on_model_front", "collection_hero", "collection_story", "merchandise_scene"}
)
STAGING_TARGET = "https://staging-7e48-skyyrose.wpcomstaging.com"


def bound_document(theme: Path, binding: Any) -> dict[str, Any] | None:
    """Read only an exact, non-aliased JSON receipt inside the theme."""
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
        return None
    relative, digest = binding["path"], binding["sha256"]
    if (
        not isinstance(relative, str)
        or not re.fullmatch(r"data/v2-media-reviews/[A-Za-z0-9_.-]+\.json", relative)
        or not isinstance(digest, str)
        or not re.fullmatch(r"[a-f0-9]{64}", digest)
        or theme.is_symlink()
    ):
        return None
    file = theme
    for part in Path(relative).parts:
        file /= part
        if file.is_symlink():
            return None
    if not file.is_file() or not file.resolve().is_relative_to(theme.resolve()):
        return None
    raw = file.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        return None
    try:
        document = json.loads(raw)
    except (ValueError, UnicodeError):
        return None
    return document if isinstance(document, dict) else None


def validated_usage_roles(
    relative: str, record: dict[str, Any], adoptions: Any, theme: Path
) -> list[str]:
    """Return only roles explicitly granted to this original and its receipt."""
    if not isinstance(adoptions, dict) or record.get("status") not in {
        "INDEPENDENT_VISUAL_PASS",
        "FOUNDER_ACCEPTED",
    }:
        return []
    grant = bound_document(theme, adoptions.get(relative))
    if (
        not grant
        or grant.get("schema") != "skyyrose.media-usage-adoption.v1"
        or grant.get("status") != "AUTHORIZED_REUSE"
        or grant.get("authority") != "FOUNDER_CONFIRMED"
        or grant.get("target") != STAGING_TARGET
        or grant.get("source")
        != {
            "path": relative,
            "sha256": record.get("sha256"),
            "review": {k: record.get("review", {}).get(k) for k in ("path", "sha256")},
        }
        or grant.get("skus") != record.get("skus")
        or grant.get("collections") != record.get("collections")
    ):
        return []
    roles = grant.get("roles")
    if (
        not isinstance(roles, list)
        or not roles
        or any(not isinstance(role, str) or role not in ADDITIONAL_ROLES for role in roles)
        or len(set(roles)) != len(roles)
        or not isinstance(record.get("skus"), list)
        or len(record["skus"]) != 1
        or not isinstance(record.get("collections"), list)
        or len(record["collections"]) != 1
    ):
        return []
    authority = bound_document(theme, grant.get("authorization"))
    if (
        not authority
        or authority.get("schema") != "skyyrose.media-usage-authority.v1"
        or authority.get("authority") != "FOUNDER_CONFIRMED"
        or authority.get("decision_text") != "do it"
        or authority.get("mode") != "REUSE_APPROVED_UNCHANGED_MEDIA"
        or authority.get("target") != STAGING_TARGET
        or not authority.get("antecedent_scope")
        or not isinstance(authority.get("assignments"), dict)
        or authority["assignments"].get(relative)
        != {
            "source": grant["source"],
            "skus": grant["skus"],
            "collections": grant["collections"],
            "roles": roles,
        }
    ):
        return []
    return roles.copy()
