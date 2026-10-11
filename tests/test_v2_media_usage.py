"""Current accepted-source reuse authority cannot create or broaden pixel approval."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

from skyyrose.core.media_usage import validated_usage_roles

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"


@pytest.fixture
def usage_fixture(tmp_path):
    inventory = json.loads((THEME / "data/v2-media-eligibility.json").read_text())
    relative = "assets/v2-original/products/br-003.png"
    record = inventory["assets"][relative]
    adoptions = inventory["usage_adoptions"]
    grant = json.loads((THEME / adoptions[relative]["path"]).read_text())
    for name in [
        relative,
        adoptions[relative]["path"],
        grant["authorization"]["path"],
        record["review"]["path"],
    ]:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(THEME / name, destination)
    original = json.loads((THEME / record["review"]["path"]).read_text())
    owner = original["decision_source"]["path"]
    shutil.copyfile(THEME / owner, tmp_path / owner)
    return tmp_path, relative, copy.deepcopy(record), {relative: copy.deepcopy(adoptions[relative])}


def test_source_bound_additional_use_preserves_original_card_decision(usage_fixture, monkeypatch):
    theme, relative, record, adoptions = usage_fixture
    sys.path.insert(0, str(ROOT / "tools/v2-source-certification"))
    import package

    monkeypatch.setattr(package, "THEME", theme)
    inventory = {"assets": {relative: record}, "usage_adoptions": adoptions}
    assert record["roles"] == ["card_front"]
    assert package.eligible_media(relative, inventory)
    assert package.effective_media_roles(relative, inventory) == [
        "card_front",
        "pdp_on_model_front",
    ]
    assert record["roles"] == ["card_front"]
    inventory.pop("usage_adoptions")
    assert package.effective_media_roles(relative, inventory) == ["card_front"]


@pytest.mark.parametrize(
    "change",
    [
        "hash",
        "sku",
        "collection",
        "revoke",
        "missing",
        "receipt",
        "authority",
        "unsupported",
        "duplicate",
    ],
)
def test_reuse_grant_rejects_stale_or_broadened_authority(usage_fixture, change):
    theme, relative, record, adoptions = usage_fixture
    assert validated_usage_roles(relative, record, adoptions, theme) == ["pdp_on_model_front"]
    if change == "hash":
        record["sha256"] = "0" * 64
    elif change == "sku":
        record["skus"] = ["lh-005"]
    elif change == "collection":
        record["collections"] = ["love-hurts"]
    elif change == "revoke":
        record["status"] = "REVOKED"
    elif change == "missing":
        adoptions.clear()
    elif change == "receipt":
        (theme / adoptions[relative]["path"]).write_text("{}")
    elif change in {"authority", "unsupported", "duplicate"}:
        path = theme / adoptions[relative]["path"]
        grant = json.loads(path.read_text())
        if change == "authority":
            (theme / grant["authorization"]["path"]).write_text("{}")
        else:
            grant["roles"] = (
                ["production_publish"] if change == "unsupported" else ["pdp_on_model_front"] * 2
            )
            encoded = json.dumps(grant).encode()
            path.write_bytes(encoded)
            adoptions[relative]["sha256"] = hashlib.sha256(encoded).hexdigest()
    assert validated_usage_roles(relative, record, adoptions, theme) == []


def test_reuse_cannot_survive_revoked_original_founder_decision(usage_fixture, monkeypatch):
    theme, relative, record, adoptions = usage_fixture
    sys.path.insert(0, str(ROOT / "tools/v2-source-certification"))
    import package

    monkeypatch.setattr(package, "THEME", theme)
    inventory = {"assets": {relative: record}, "usage_adoptions": adoptions}
    assert package.effective_media_roles(relative, inventory) == [
        "card_front",
        "pdp_on_model_front",
    ]
    original = json.loads((theme / record["review"]["path"]).read_text())
    (theme / original["decision_source"]["path"]).write_text("{}")
    assert not package.eligible_media(relative, inventory)
    assert package.effective_media_roles(relative, inventory) == []
