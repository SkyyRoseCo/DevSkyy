"""SKU asset manifest — the content-hashed map of every asset each SKU consumes.

This is the spine that replaces *filename-as-truth*. The render pipeline's
source map (``scripts/oai_render/references.py``) resolves a SKU to its garment
techflats, logo/patch, and dossier by *path*; nothing today verifies that the
file at that path is still the file the founder approved. That gap caused the
bug-119 class (a mislabeled jpeg impersonated a mint techflat → 41 wrong-product
renders) and the "rename breaks silently mid-paid-run" class.

A manifest entry pins every asset path to a SHA-256 taken when the manifest was
generated. Two operations make it useful:

* :meth:`AssetManifest.verify` — before a paid batch, confirm every planned
  SKU's assets still exist and still hash to what was committed. Drift (missing
  file, changed content, new untracked asset) is reported, not discovered when
  the render call fails.
* :func:`build_records` + the committed ``manifest.json`` + a CI test that
  regenerates and diffs — any file rename/replace that isn't reflected in the
  manifest is a hard CI failure, so the manifest can never quietly fall out of
  sync with the tree.

This module is *pure*: it knows how to hash, serialize, and verify asset
records, but not where SKUs come from. The generator
(``scripts/build_asset_manifest.py``) owns the SKU→path resolution and feeds
records in, keeping ``skyyrose.core`` free of any dependency on the render
scripts. Hashing is delegated to :func:`skyyrose.core.hashing.sha256_of_file`
so the project has exactly one hash function.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from skyyrose.core.hashing import now_iso, sha256_of_file
from skyyrose.core.paths import PRODUCT_ASSETS, REPO_ROOT

MANIFEST_PATH = PRODUCT_ASSETS / "manifest.json"


@dataclass(frozen=True)
class AssetRecord:
    """One asset a SKU consumes, pinned to its content hash at generation time.

    Roles mirror the render pipeline's reference kinds — "garment",
    "garment-back", "logo", "patch" — plus wearer-relative physical
    authorities ("garment-wearer-left/right") and "dossier".
    """

    role: str
    path: str  # repo-root-relative POSIX path
    sha256: str | None  # "sha256:<hex>" when the file existed at generation; None when absent

    @property
    def exists(self) -> bool:
        """An asset is present iff it was hashable at generation time."""
        return self.sha256 is not None


@dataclass(frozen=True)
class SkuAssets:
    """Every asset one SKU references, plus the catalog facts that scope it."""

    sku: str
    name: str
    collection: str
    garment_type: str
    assets: list[AssetRecord] = field(default_factory=list)
    resolution_error: str | None = None

    def by_role(self, role: str) -> AssetRecord | None:
        for a in self.assets:
            if a.role == role:
                return a
        return None


@dataclass
class DriftFinding:
    """A single way a SKU's assets diverged from the committed manifest."""

    sku: str
    role: str
    path: str
    kind: str  # "missing" | "hash_mismatch"
    detail: str


@dataclass
class AssetManifest:
    """The full SKU→assets map, content-hashed and serializable."""

    version: int = 1
    generated_at: str = ""
    catalog_sha: str | None = None
    skus: dict[str, SkuAssets] = field(default_factory=dict)
    registry_sha: str | None = None
    registry_path: str = "wordpress-theme/skyyrose-flagship/data/logo-registry.json"

    # ── serialization ──────────────────────────────────────────────────────
    @classmethod
    def load(cls, path: Path | None = None) -> AssetManifest:
        p = path or MANIFEST_PATH
        if not p.exists():
            return cls()
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Asset manifest is corrupt (invalid JSON) at {p}: {exc}\n"
                "Delete it and run `python scripts/build_asset_manifest.py` to regenerate."
            ) from exc
        skus = {
            sku: SkuAssets(
                sku=entry["sku"],
                name=entry.get("name", ""),
                collection=entry.get("collection", ""),
                garment_type=entry.get("garment_type", ""),
                resolution_error=entry.get("resolution_error"),
                assets=[
                    AssetRecord(role=a["role"], path=a["path"], sha256=a.get("sha256"))
                    for a in entry.get("assets", [])
                ],
            )
            for sku, entry in raw.get("skus", {}).items()
        }
        return cls(
            version=int(raw.get("version", 1)),
            generated_at=raw.get("generated_at", ""),
            catalog_sha=raw.get("catalog_sha"),
            skus=skus,
            registry_sha=raw.get("registry_sha"),
            registry_path=raw.get("registry_path", cls.registry_path),
        )

    def to_payload(self) -> dict:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "catalog_sha": self.catalog_sha,
            **(
                {"registry_sha": self.registry_sha, "registry_path": self.registry_path}
                if self.registry_sha is not None or self.version >= 2
                else {}
            ),
            "skus": {
                sku: {
                    "sku": sa.sku,
                    "name": sa.name,
                    "collection": sa.collection,
                    "garment_type": sa.garment_type,
                    "assets": [asdict(a) for a in sa.assets],
                    **({"resolution_error": sa.resolution_error} if sa.resolution_error else {}),
                }
                for sku, sa in sorted(self.skus.items())
            },
        }

    def save(self, path: Path | None = None) -> Path:
        """Atomic write; stamps ``generated_at``."""
        p = path or MANIFEST_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        self.generated_at = now_iso()
        with tempfile.NamedTemporaryFile(
            "w", dir=p.parent, prefix=".manifest-", suffix=".tmp", delete=False, encoding="utf-8"
        ) as f:
            json.dump(self.to_payload(), f, indent=2, ensure_ascii=False)
            f.write("\n")
            tmp = Path(f.name)
        os.replace(tmp, p)
        return p

    # ── verification ───────────────────────────────────────────────────────
    def verify(self, skus: list[str] | None = None, base: Path | None = None) -> list[DriftFinding]:
        """Return every way the on-disk tree diverges from this manifest.

        ``skus=None`` checks every registered SKU; pass a subset to gate just
        the SKUs a batch will render. A file that exists but whose content hash
        no longer matches is the bug-119 signature (a different image now lives
        at a name the founder approved).
        """
        base = base or REPO_ROOT
        targets = skus if skus is not None else list(self.skus)
        findings: list[DriftFinding] = []
        if self.registry_sha is not None:
            registry_file = base / self.registry_path
            if not registry_file.is_file():
                findings.append(
                    DriftFinding(
                        "*",
                        "registry",
                        self.registry_path,
                        "missing",
                        "product registry is missing",
                    )
                )
            elif sha256_of_file(registry_file) != self.registry_sha:
                findings.append(
                    DriftFinding(
                        "*",
                        "registry",
                        self.registry_path,
                        "hash_mismatch",
                        "product authority changed; regenerate the asset manifest",
                    )
                )
        elif self.version >= 2:
            findings.append(
                DriftFinding(
                    "*",
                    "registry",
                    self.registry_path,
                    "registry_unpinned",
                    "manifest has no product authority hash; regenerate it",
                )
            )
        for sku in targets:
            sa = self.skus.get(sku)
            if sa is None:
                continue
            if sa.resolution_error:
                findings.append(
                    DriftFinding(sku, "resolution", "", "resolution_error", sa.resolution_error)
                )
            for a in sa.assets:
                if a.sha256 is None:
                    continue  # was absent at generation; not a regression
                fp = base / a.path
                if not fp.exists():
                    findings.append(
                        DriftFinding(sku, a.role, a.path, "missing", "file no longer on disk")
                    )
                    continue
                actual = sha256_of_file(fp)
                if actual != a.sha256:
                    findings.append(
                        DriftFinding(
                            sku,
                            a.role,
                            a.path,
                            "hash_mismatch",
                            f"content changed (was {a.sha256[:19]}…, now {actual[:19]}…)",
                        )
                    )
        return findings


def hash_if_present(path: Path) -> str | None:
    """SHA-256 of ``path``, or None if it does not exist. No exception on absence."""
    return sha256_of_file(path) if path.exists() else None


def to_repo_relative(path: Path) -> str:
    """POSIX path relative to the repo root, for stable cross-machine storage."""
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
