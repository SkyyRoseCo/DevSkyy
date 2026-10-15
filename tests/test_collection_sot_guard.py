"""Tests for the per-collection SOT generator seam and its freshness guard.

Covers the regenerate-and-compare guard that makes ``collections/<slug>/sot.json`` a
generated view which cannot drift from canon (mirrors the ``v7_cards_current`` guard):
  * ``wordpress-theme/skyyrose-flagship/data/build-collection-sot.py``
        - ``build_documents()`` / ``serialize()`` — the pure builder + single byte-authority
          the writer (``main``) and the guard both render through.
  * ``scripts/validate_catalog_consistency.py``:
        - ``collection_sot_current`` — generated-artifact-up-to-date guard.

The generator and validator live outside an importable package, so both are loaded by file
path — the same mechanism the validator's guard uses in CI.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tests.sparse_guard import requires_tree

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_BUILD_COLLECTION_SOT = (
    _REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "build-collection-sot.py"
)
_COLLECTIONS_DIR = _REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "collections"
_SLUGS = ("black-rose", "love-hurts", "signature", "kids-capsule")


def _load(mod_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve cls.__module__ (py3.12+/3.14).
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


gen = _load("build_collection_sot", _BUILD_COLLECTION_SOT)
validator = _load(
    "validate_catalog_consistency", _REPO_ROOT / "scripts" / "validate_catalog_consistency.py"
)


# ---------------------------------------------------------------------------
# Generator seam — build_documents() / serialize()
# ---------------------------------------------------------------------------


class TestCollectionSotGenerator:
    def test_build_documents_real_tree_structure(self):
        """Against the real masters: one document per collection, all canon blocks present."""
        docs = gen.build_documents()
        assert set(docs) == set(_SLUGS)
        for slug, doc in docs.items():
            assert doc["collection"] == slug
            assert doc["_generated_by"].startswith("data/build-collection-sot.py")
            for key in ("story", "palette", "fonts", "lockup", "imagery", "logos", "products"):
                assert key in doc, f"{slug} document missing {key!r}"

    def test_serialize_deterministic_trailing_newline_ascii(self):
        doc = gen.build_documents()["black-rose"]
        a, b = gen.serialize(doc), gen.serialize(doc)
        assert a == b
        assert a.endswith("\n")
        # ensure_ascii=True is the historical on-disk format: the em-dash in
        # _generated_by is escaped (—), never a raw UTF-8 byte.
        assert "\\u2014" in a
        assert "—" not in a

    def test_updated_flag_propagates(self):
        dated = gen.build_documents(updated="2026-06-14")
        assert all(d["updated"] == "2026-06-14" for d in dated.values())
        assert all(d["updated"] == "GENERATED" for d in gen.build_documents().values())

    # build_documents() resolves imagery through assets/hub/manifest.json; in a
    # sparse worktree (assets/ excluded) it resolves hub->ghost fallback paths and
    # would report the (correct) committed sot.json as "stale". The freshness gate
    # runs in full checkouts and CI, where the hub tree is present.
    @requires_tree("assets/hub")
    def test_committed_files_are_fresh(self):
        """Every tracked sot.json equals fresh generator output — the guard's premise.

        If this fails the committed view drifted from the masters; run
        ``python wordpress-theme/skyyrose-flagship/data/build-collection-sot.py``.
        """
        for slug, doc in gen.build_documents().items():
            on_disk = (_COLLECTIONS_DIR / slug / "sot.json").read_text(encoding="utf-8")
            assert on_disk == gen.serialize(doc), f"{slug}/sot.json is stale vs generator output"


# ---------------------------------------------------------------------------
# Validator — collection_sot_current guard
# ---------------------------------------------------------------------------


class TestCollectionSotCurrentGuard:
    def _seed(self, tmp_path: Path, *, drift_slug: str | None = None, omit_slug: str | None = None):
        """Write fresh generator output into a tmp collections dir, optionally drifting/omitting."""
        for slug, doc in gen.build_documents().items():
            if slug == omit_slug:
                continue
            text = gen.serialize(doc)
            if slug == drift_slug:
                text = text.replace('"updated": "GENERATED"', '"updated": "HAND-EDIT"', 1)
            folder = tmp_path / slug
            folder.mkdir(parents=True)
            (folder / "sot.json").write_text(text, encoding="utf-8")

    def test_guard_passes_when_files_match(self, tmp_path, monkeypatch):
        self._seed(tmp_path)
        monkeypatch.setattr(validator, "_COLLECTIONS_DIR", tmp_path)
        result = validator.check_collection_sot_current()
        assert result.passed, result.message

    def test_guard_fails_on_drift(self, tmp_path, monkeypatch):
        self._seed(tmp_path, drift_slug="black-rose")
        monkeypatch.setattr(validator, "_COLLECTIONS_DIR", tmp_path)
        result = validator.check_collection_sot_current()
        assert not result.passed
        assert any("black-rose" in d for d in result.details)

    def test_guard_fails_on_missing_file(self, tmp_path, monkeypatch):
        self._seed(tmp_path, omit_slug="signature")
        monkeypatch.setattr(validator, "_COLLECTIONS_DIR", tmp_path)
        result = validator.check_collection_sot_current()
        assert not result.passed
        assert any("signature" in d for d in result.details)

    def test_guard_fails_on_orphaned_slug(self, tmp_path, monkeypatch):
        """A committed sot.json whose collection the generator no longer produces must fail.

        Removing a collection from the registry's collections section drops its slug from
        build_documents(); the leftover committed sot.json would otherwise pass unseen.
        """
        self._seed(tmp_path)
        retired = tmp_path / "retired-collection"
        retired.mkdir()
        (retired / "sot.json").write_text("{}\n", encoding="utf-8")
        monkeypatch.setattr(validator, "_COLLECTIONS_DIR", tmp_path)
        result = validator.check_collection_sot_current()
        assert not result.passed
        assert any("retired-collection" in d for d in result.details)

    def test_guard_skips_when_generator_absent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validator, "_BUILD_COLLECTION_SOT", tmp_path / "nope.py")
        result = validator.check_collection_sot_current()
        assert result.passed
        assert "skip" in result.message.lower()
