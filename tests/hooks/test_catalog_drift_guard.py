"""catalog-drift-guard.sh reads the real PostToolUse payload and resolves the repo
root from the edited file — so it fires from any worktree, and never from the
checkout it happens to be wired in.

Runs against throwaway git repos only: they carry none of the generators, so no
tracked projection can be rewritten by a test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.hooks.conftest import HOOK_DIRS, add_worktree, git, init_repo, run_hook

HOOK = "catalog-drift-guard.sh"
DATA = "wordpress-theme/skyyrose-flagship/data"
REGISTRY = f"{DATA}/logo-registry.json"
CSV = f"{DATA}/skyyrose-catalog.csv"
FILES = {REGISTRY: '{"products": {}}\n', CSV: "sku,name\n", "README.md": "# x\n"}


def _payload(path: Path) -> dict:
    return {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(path), "old_string": "a", "new_string": "b"},
    }


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo", FILES)


def test_registry_edit_announces_canonical_data(flavor: str, repo: Path) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(repo / REGISTRY), cwd=repo)
    assert result.returncode == 0, result.stderr
    assert f"CANONICAL PRODUCT DATA TOUCHED: {REGISTRY}" in result.stdout
    assert "skyyrose.core.product import get_product" in result.stdout
    assert "regenerated" not in result.stdout  # no generator exists in the tmp repo
    assert git(repo, "status", "--porcelain") == ""  # nothing tracked was rewritten


def test_readme_edit_is_silent(flavor: str, repo: Path) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(repo / "README.md"), cwd=repo)
    assert result.returncode == 0
    assert result.stdout == "" and result.stderr == ""


def test_registry_edit_in_a_worktree_fires(flavor: str, repo: Path, tmp_path: Path) -> None:
    """Root is resolved from the edited file: a worktree path matches the pattern."""
    wt = add_worktree(repo, tmp_path / "wt")
    (wt / REGISTRY).write_text('{"products": {"x": {}}}\n')
    # cwd is deliberately elsewhere — the hook must not depend on it.
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(wt / REGISTRY), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert f"CANONICAL PRODUCT DATA TOUCHED: {REGISTRY}" in result.stdout


def test_edit_through_root_symlink_resolves_to_registry(flavor: str, repo: Path) -> None:
    link = repo / "logo-registry.json"
    link.symlink_to(Path(REGISTRY))
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(link), cwd=repo)
    assert result.returncode == 0, result.stderr
    assert f"CANONICAL PRODUCT DATA TOUCHED: {REGISTRY}" in result.stdout


def test_csv_edit_is_named_a_projection(flavor: str, repo: Path) -> None:
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(repo / CSV), cwd=repo)
    assert result.returncode == 0, result.stderr
    assert f"PRODUCT PROJECTION EDITED: {CSV}" in result.stdout
    assert "sync_product_registry.py" in result.stdout
    assert "SOT master" not in result.stdout


def test_visual_manifest_edit_is_named_the_imagery_master(flavor: str, tmp_path: Path) -> None:
    """visual-manifest.json is the editable non-product imagery master (sot_common.py loads
    it as a master) — never a registry projection an agent should 'move into the registry'."""
    manifest = f"{DATA}/visual-manifest.json"
    repo = init_repo(tmp_path / "repo", {**FILES, manifest: "{}\n"})
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(repo / manifest), cwd=repo)
    assert result.returncode == 0, result.stderr
    assert f"NON-PRODUCT IMAGERY MASTER EDITED: {manifest}" in result.stdout
    assert "PROJECTION" not in result.stdout
    assert "Apply the change in the registry" not in result.stdout


def test_similarities_edit_names_its_real_generator(flavor: str, tmp_path: Path) -> None:
    similarities = f"{DATA}/product-similarities.json"
    repo = init_repo(tmp_path / "repo", {**FILES, similarities: "{}\n"})
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(repo / similarities), cwd=repo)
    assert result.returncode == 0, result.stderr
    assert f"GENERATED FILE EDITED: {similarities}" in result.stdout
    assert "scripts/build_product_similarities.py" in result.stdout
    assert "sync_product_registry.py" not in result.stdout.split("GENERATED FILE EDITED")[1]


def test_file_outside_any_repo_is_silent(flavor: str, tmp_path: Path) -> None:
    loose = tmp_path / "loose" / REGISTRY
    loose.parent.mkdir(parents=True)
    loose.write_text("{}")
    result = run_hook(HOOK_DIRS[flavor] / HOOK, _payload(loose), cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


def test_hook_has_no_stale_targets() -> None:
    for flavor in HOOK_DIRS:
        text = (HOOK_DIRS[flavor] / HOOK).read_text()
        assert "commerce.py" not in text, flavor
        assert "SOT master" not in text, flavor
        assert ".tool_input.file_path" in text, flavor


def test_codex_mirror_is_identical() -> None:
    assert (HOOK_DIRS["claude"] / HOOK).read_bytes() == (HOOK_DIRS["codex"] / HOOK).read_bytes()
