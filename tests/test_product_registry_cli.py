"""``python -m skyyrose.core.product_registry update`` writes through the registry.

Runs the CLI in a subprocess against a tmp COPY of the real registry so the
projections it regenerates land next to the copy, never next to the SOT.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REAL_REGISTRY = REPO / "wordpress-theme/skyyrose-flagship/data/logo-registry.json"


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    copy = tmp_path / "logo-registry.json"
    shutil.copyfile(REAL_REGISTRY, copy)
    return copy


def run_cli(registry: Path, sku: str, stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "skyyrose.core.product_registry",
            "update",
            sku,
            "--registry",
            str(registry),
        ],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
        timeout=60,
    )


def first_sku(registry: Path) -> str:
    return next(iter(json.loads(registry.read_text())["products"]))


def csv_row(registry: Path, sku: str) -> dict[str, str]:
    with (registry.parent / "skyyrose-catalog.csv").open(newline="") as handle:
        return next(row for row in csv.DictReader(handle) if row["sku"] == sku)


def test_update_changes_registry_and_regenerates_csv_projection(registry: Path) -> None:
    sku = first_sku(registry)
    original_bytes = REAL_REGISTRY.read_bytes()

    result = run_cli(registry, sku, json.dumps({"name": "CLI Renamed", "price": "123.45"}))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["sku"] == sku
    assert payload["changed"] == ["name", "price"]
    assert payload["registry"] == str(registry)

    catalog = json.loads(registry.read_text())["products"][sku]["catalog"]
    assert catalog["name"] == "CLI Renamed"
    assert catalog["price"] == "123.45"

    row = csv_row(registry, sku)
    assert row["name"] == "CLI Renamed"
    assert row["price"] == "123.45"
    assert (registry.parent / "dossiers").is_dir()
    assert REAL_REGISTRY.read_bytes() == original_bytes


def test_unchanged_value_reports_no_change(registry: Path) -> None:
    sku = first_sku(registry)
    name = json.loads(registry.read_text())["products"][sku]["catalog"]["name"]
    result = run_cli(registry, sku, json.dumps({"name": name}))
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["changed"] == []


def test_identity_field_is_rejected(registry: Path) -> None:
    sku = first_sku(registry)
    before = registry.read_bytes()
    result = run_cli(registry, sku, json.dumps({"sku": "zz-999"}))
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "identity" in payload["error"].lower()
    assert registry.read_bytes() == before
    assert not (registry.parent / "skyyrose-catalog.csv").exists()


def test_unknown_sku_is_rejected(registry: Path) -> None:
    result = run_cli(registry, "zz-999", json.dumps({"name": "x"}))
    assert result.returncode == 1
    assert json.loads(result.stdout) == {"ok": False, "error": "SKU not found: zz-999"}


@pytest.mark.parametrize("stdin", ["{not json", "[]", "{}", '"string"', ""])
def test_malformed_patch_fails_closed(registry: Path, stdin: str) -> None:
    sku = first_sku(registry)
    before = registry.read_bytes()
    result = run_cli(registry, sku, stdin)
    assert result.returncode == 1
    assert json.loads(result.stdout)["ok"] is False
    assert registry.read_bytes() == before
    assert not (registry.parent / "skyyrose-catalog.csv").exists()


def test_non_string_value_is_rejected(registry: Path) -> None:
    sku = first_sku(registry)
    result = run_cli(registry, sku, json.dumps({"price": 12}))
    assert result.returncode == 1
    assert "string" in json.loads(result.stdout)["error"]
