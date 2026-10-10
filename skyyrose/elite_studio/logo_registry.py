"""Logo Registry — Canonical loader for SkyyRose logo metadata + path resolution.

Reads the canonical registry at:
  wordpress-theme/skyyrose-flagship/data/logo-registry.json

The registry has two categories of logo:

1. **Centralized logos** — single file, lives under `assets/images/logos/`.
   Entry has a `file` field naming the canonical filename. Examples:
   `sr-monogram-rose-gold`, `black-roses-cloud-cluster`, `heart-rose-composite`.

2. **Per-SKU co-located patches** — same graphic copied into each using SKU's
   product folder. Entry has `co_located_per_sku: true` plus a `filename` field.
   Resolved at consumption time via:
     `assets/images/products/<sku_folders[sku]>/<filename>`
   Examples: `nfl-authentic-collection-card`, `mlb-authentic-collection-card`,
   `nba-authentic-collection-card`, `hockey-championship-card`.

This module is the only authoritative resolver. Do NOT hardcode logo paths
elsewhere — any renderer that needs a logo image should call
`LogoRegistry.image_path(sku, logo_id)`.

Typical usage:

    from skyyrose.elite_studio.logo_registry import LogoRegistry

    reg = LogoRegistry.load()
    # Centralized logo (any SKU resolution works):
    sr_path = reg.image_path(sku="br-005", logo_id="sr-monogram-rose-gold")
    # Per-SKU co-located patch:
    nfl_path = reg.image_path(sku="br-008", logo_id="nfl-authentic-collection-card")
    # Placements for a SKU:
    for placement in reg.placements_for("br-012"):
        print(placement["logo_id"], placement["position"])
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skyyrose.core.catalog_loader import CATALOG_CSV, PROJECT_ROOT
from skyyrose.core.hashing import sha256_of_file
from skyyrose.core.paths import THEME_ROOT, WP_LOGOS_DIR, WP_PRODUCTS_DIR

REGISTRY_JSON: Path = CATALOG_CSV.parent / "logo-registry.json"


class RegistryContractError(ValueError):
    """A required SKU decoration contract is missing from the sole registry."""


class LogoNotFoundError(KeyError):
    """Raised when a requested logo_id is not registered."""


class SkuFolderUnknownError(KeyError):
    """Raised when a per-SKU patch needs a folder mapping that is not in the registry."""


@dataclass(frozen=True)
class LogoEntry:
    logo_id: str
    description: str
    primary_color: str
    recolor_allowed: bool
    co_located_per_sku: bool
    filename: str
    collection: str | None
    category: str | None
    site_wide: bool


class LogoRegistry:
    """Read-only loader for logo-registry.json."""

    def __init__(self, raw: dict[str, Any], source: Path | None = None) -> None:
        self._raw = raw
        self._source = source
        self.version: int = int(raw.get("version", 0))
        self.brand_primary: str = raw.get("brand_primary", "")
        self._logos: dict[str, LogoEntry] = {
            logo_id: _entry_from_raw(logo_id, data)
            for logo_id, data in (raw.get("logos") or {}).items()
        }
        self._sku_folders: dict[str, str] = {
            sku: folder
            for sku, folder in (raw.get("sku_folders") or {}).items()
            if not sku.startswith("_")
        }
        self._sku_logos: dict[str, dict[str, Any]] = raw.get("sku_logos") or {}

    @classmethod
    def load(cls, path: Path | None = None) -> LogoRegistry:
        target = path or REGISTRY_JSON
        with target.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        return cls(raw, source=target)

    # ─── Logo lookups ────────────────────────────────────────────────────

    def has_logo(self, logo_id: str) -> bool:
        return logo_id in self._logos

    def get_logo(self, logo_id: str) -> LogoEntry:
        try:
            return self._logos[logo_id]
        except KeyError as exc:
            raise LogoNotFoundError(f"logo_id {logo_id!r} not in registry") from exc

    def all_logos(self) -> dict[str, LogoEntry]:
        return dict(self._logos)

    def sport_patches(self) -> dict[str, LogoEntry]:
        """All per-SKU co-located sport-patch logos."""
        return {lid: e for lid, e in self._logos.items() if e.co_located_per_sku}

    # ─── Path resolution ─────────────────────────────────────────────────

    def image_path(self, *, sku: str, logo_id: str) -> Path:
        """Return absolute filesystem path for a logo's image as it applies to ``sku``.

        For centralized logos: resolves to ``<theme>/assets/images/logos/<file>``.
        For ``co_located_per_sku`` patches: resolves to
        ``<theme>/assets/images/products/<sku_folders[sku]>/<filename>``.

        Raises:
            LogoNotFoundError: if logo_id is not in the registry
            SkuFolderUnknownError: if logo is per-SKU but the SKU has no folder mapping
        """
        entry = self.get_logo(logo_id)
        if entry.co_located_per_sku:
            folder = self._sku_folders.get(sku)
            if not folder:
                raise SkuFolderUnknownError(
                    f"logo {logo_id!r} requires a per-SKU folder mapping but "
                    f"sku {sku!r} is not in sku_folders. Add it to the registry."
                )
            return WP_PRODUCTS_DIR / folder / entry.filename
        return WP_LOGOS_DIR / entry.filename

    def sku_folder(self, sku: str) -> str | None:
        return self._sku_folders.get(sku)

    # ─── Placement lookups ───────────────────────────────────────────────

    def placements_for(self, sku: str) -> list[dict[str, Any]]:
        return deepcopy(self._sku_entry(sku).get("placements") or [])

    def _sku_entry(self, sku: str) -> dict[str, Any]:
        if sku in self._sku_logos:
            return self._sku_logos[sku]
        component = self._raw.get("render_components", {}).get(sku)
        if not component:
            raise RegistryContractError(f"SKU {sku!r} is absent from logo-registry.json")
        parent = component["parent_sku"]
        if parent not in self._sku_logos:
            raise RegistryContractError(f"Component {sku!r} has unknown parent {parent!r}")
        entry = deepcopy(self._sku_logos[parent])
        entry["placements"] = [
            placement
            for placement in entry.get("placements", [])
            if placement.get("position") in component["placement_positions"]
        ]
        entry["component"] = deepcopy(component)
        # Parent artwork bindings can describe another piece of the set.
        entry.pop("render_reference", None)
        return entry

    def skus(self) -> list[str]:
        return sorted(sku for sku in self._sku_logos if not sku.startswith("_"))

    def primary_reference_for(self, sku: str) -> Path | None:
        """Resolve the SKU's patch or first logo, honoring registered colorway files."""
        placements = self.placements_for(sku)
        # Required sports artwork must resolve from its actual logo record;
        # a supplemental colorway binding cannot replace it with another mark.
        sport_patch = next(
            (p for p in placements if self.get_logo(p["logo_id"]).co_located_per_sku),
            None,
        )
        if sport_patch is not None:
            return self.image_path(sku=sku, logo_id=sport_patch["logo_id"])
        binding = self._sku_entry(sku).get("render_reference") or {}
        if binding.get("status") == "UNBOUND":
            raise RegistryContractError(
                f"{sku}: {binding.get('reason', 'render reference unbound')}"
            )
        if binding.get("kind") == "garment_artwork":
            return self._garment_artwork_path(sku, binding)
        if binding.get("path"):
            return self._repo_path(sku, binding["path"], "render reference")
        if not placements:
            return None
        return self.image_path(sku=sku, logo_id=placements[0]["logo_id"])

    def reference_kind_for(self, sku: str) -> str:
        """Distinguish a complete source garment from standalone logo artwork."""
        if self.patch_sport_for(sku):
            return "patch"
        binding = self._sku_entry(sku).get("render_reference") or {}
        return "garment" if binding.get("kind") == "garment_artwork" else "logo"

    @staticmethod
    def _repo_path(sku: str, path_text: object, what: str) -> Path:
        """Resolve a registry-relative path; bytes at the result get uploaded, so it must stay in-repo."""
        if not isinstance(path_text, str) or not path_text:
            raise RegistryContractError(f"{sku}: {what} path is missing")
        relative = Path(path_text)
        if relative.is_absolute() or ".." in relative.parts:
            raise RegistryContractError(f"{sku}: {what} path must stay within the repository")
        path = (PROJECT_ROOT / relative).resolve()
        if not path.is_relative_to(PROJECT_ROOT.resolve()):
            raise RegistryContractError(f"{sku}: {what} path escapes the repository")
        return path

    def _garment_artwork_path(self, sku: str, binding: dict[str, Any]) -> Path:
        """Check execution against the exact founder-bound source; never alter its art."""
        path_text = binding.get("path")
        digest = binding.get("sha256")
        if binding.get("status") != "BOUND" or binding.get("view") != "front":
            raise RegistryContractError(f"{sku}: garment artwork must be BOUND to the front view")
        path = self._repo_path(sku, path_text, "garment artwork")
        expected_front = (
            self._raw.get("products", {}).get(sku, {}).get("render_sources", {}).get("front")
        )
        if not expected_front or path != (PROJECT_ROOT / expected_front).resolve():
            raise RegistryContractError(
                f"{sku}: garment artwork does not match this product's registered front"
            )
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise RegistryContractError(f"{sku}: garment artwork requires its registered SHA-256")
        if not path.is_file():
            raise RegistryContractError(
                f"{sku}: bound garment artwork file is missing: {path_text}"
            )
        if sha256_of_file(path) != f"sha256:{digest}":
            raise RegistryContractError(f"{sku}: bound garment artwork hash mismatch: {path_text}")
        return path

    def patch_sport_for(self, sku: str) -> str | None:
        for placement in self.placements_for(sku):
            logo = self._raw["logos"][placement["logo_id"]]
            if logo.get("co_located_per_sku"):
                if not logo.get("sport"):
                    raise RegistryContractError(
                        f"Patch {placement['logo_id']} has no registered sport"
                    )
                return str(logo["sport"])
        return None

    def decoration_sizing_for(self, sku: str, *, required: bool = False) -> dict[str, Any]:
        """Return founder specifications verbatim; never infer sizes from another source."""
        entry = self._sku_entry(sku)
        sizing = entry.get("decoration_sizing") or {}
        is_jersey = any(
            self.get_logo(p["logo_id"]).co_located_per_sku for p in entry.get("placements", [])
        )
        if (required or is_jersey) and not sizing.get("items"):
            raise RegistryContractError(f"SKU {sku!r} requires registered decoration sizing")
        if (required or is_jersey) and not any(
            item.get("kind") == "patch" and item.get("dimension_inches")
            for item in sizing.get("items", [])
        ):
            raise RegistryContractError(f"SKU {sku!r} requires registered patch dimensions")
        return deepcopy(sizing)

    def prompt_instructions(self, sku: str, *, require_sizing: bool = False) -> str:
        """Deterministic decoration contract shared by generation and placement briefs.

        Includes literal source-size text and structured dimensions, preserving ranges
        and relative proportions without inventing typography point sizes.
        """
        sizing = self.decoration_sizing_for(sku, required=require_sizing)
        entry = self._sku_entry(sku)
        contract = {
            key: deepcopy(value)
            for key, value in entry.items()
            if key not in {"name", "dossier_reference", "decoration_sizing"}
        }
        if sizing:
            contract["decoration_sizing"] = sizing
        lines = [
            f"CANONICAL LOGO AND DECORATION CONTRACT — SKU {sku}",
            "Source: wordpress-theme/skyyrose-flagship/data/logo-registry.json",
            "This registry is the sole authority for artwork, lettering, placements and "
            "decoration dimensions. It overrides conflicting dossier prose, cached briefs "
            "and prior prompt corrections. Preserve founder specifications exactly; "
            "do not infer dimensions or add collection logos to blank garments.",
            "Apply only decorations visible from the requested garment view; do not move "
            "back decorations to the front or change the requested composition.",
            json.dumps(contract, ensure_ascii=False, sort_keys=True, indent=2),
        ]
        return "\n".join(lines)

    def has_sku(self, sku: str) -> bool:
        return sku in self._sku_logos


def _entry_from_raw(logo_id: str, data: dict[str, Any]) -> LogoEntry:
    co_located = bool(data.get("co_located_per_sku", False))
    filename = data.get("filename") or data.get("file") or ""
    return LogoEntry(
        logo_id=logo_id,
        description=str(data.get("description", "")),
        primary_color=str(data.get("primary_color", "")),
        recolor_allowed=bool(data.get("recolor_allowed", False)),
        co_located_per_sku=co_located,
        filename=str(filename),
        collection=data.get("collection"),
        category=data.get("category"),
        site_wide=bool(data.get("site_wide", False)),
    )


__all__ = [
    "REGISTRY_JSON",
    "THEME_ROOT",
    "LogoEntry",
    "LogoNotFoundError",
    "LogoRegistry",
    "RegistryContractError",
    "SkuFolderUnknownError",
]
