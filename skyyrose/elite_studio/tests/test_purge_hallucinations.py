from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts import purge_hallucinations
from scripts.purge_hallucinations import purge
from skyyrose.core.paths import WP_PRODUCTS_DIR


def test_purge_logic():
    # Mock files
    mock_files = []

    # Rule 1 target
    m0 = MagicMock(spec=Path)
    m0.name = "lh-005-model.jpg"
    m0.is_file.return_value = True
    m0.stat.return_value.st_size = 100 * 1024
    mock_files.append(m0)

    # Rule 2 target
    m1 = MagicMock(spec=Path)
    m1.name = "po-001.jpg"
    m1.is_file.return_value = True
    m1.stat.return_value.st_size = 100 * 1024
    mock_files.append(m1)

    # Rule 3 target
    m2 = MagicMock(spec=Path)
    m2.name = "br-001-model.jpg"
    m2.is_file.return_value = True
    m2.stat.return_value.st_size = 2 * 1024 * 1024  # 2MB
    mock_files.append(m2)

    # Safe file
    m3 = MagicMock(spec=Path)
    m3.name = "br-001.jpg"
    m3.is_file.return_value = True
    m3.stat.return_value.st_size = 500 * 1024  # 500KB
    mock_files.append(m3)

    with patch("scripts.purge_hallucinations.PRODUCTS_DIR") as mock_dir:
        mock_dir.exists.return_value = True
        mock_dir.iterdir.return_value = mock_files

        purge(apply=True)

        # Verify unlinks
        m0.unlink.assert_called_once()
        m1.unlink.assert_called_once()
        m2.unlink.assert_called_once()
        m3.unlink.assert_not_called()


def _fixture_dir(tmp_path):
    files = {
        "lh-005-model.jpg": 100 * 1024,  # accessory model shot
        "po-001.jpg": 100 * 1024,  # non-existent collection
        "br-001-model.jpg": 2 * 1024 * 1024,  # oversized model shot
        "br-001.jpg": 500 * 1024,  # keep
        "sg-007-front.jpg": 100 * 1024,  # accessory, but not a model shot: keep
    }
    for name, size in files.items():
        (tmp_path / name).write_bytes(b"\0" * size)
    return tmp_path


def test_default_run_lists_but_deletes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(purge_hallucinations, "PRODUCTS_DIR", _fixture_dir(tmp_path))
    before = sorted(p.name for p in tmp_path.iterdir())
    matches = purge()
    assert sorted(p.name for p in matches) == ["br-001-model.jpg", "lh-005-model.jpg", "po-001.jpg"]
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_cli_deletes_only_with_apply(tmp_path, monkeypatch):
    monkeypatch.setattr(purge_hallucinations, "PRODUCTS_DIR", _fixture_dir(tmp_path))
    purge_hallucinations.main([])
    assert (tmp_path / "po-001.jpg").exists()
    purge_hallucinations.main(["--apply"])
    assert sorted(p.name for p in tmp_path.iterdir()) == ["br-001.jpg", "sg-007-front.jpg"]


def test_accessories_come_from_the_registry(tmp_path, monkeypatch):
    records = {
        "zz-001": {"catalog": {"render_is_accessory": "1"}},
        "lh-005": {"catalog": {"render_is_accessory": "0"}},
    }
    monkeypatch.setattr(purge_hallucinations, "all_skus", lambda: list(records))
    monkeypatch.setattr(purge_hallucinations, "get_product", records.__getitem__)
    assert purge_hallucinations.accessory_skus() == ["zz-001"]
    (tmp_path / "zz-001-model.jpg").write_bytes(b"\0")
    (tmp_path / "lh-005-model.jpg").write_bytes(b"\0")
    monkeypatch.setattr(purge_hallucinations, "PRODUCTS_DIR", tmp_path)
    assert [p.name for p in purge()] == ["zz-001-model.jpg"]


def test_real_registry_accessories_and_canonical_dir():
    assert sorted(purge_hallucinations.accessory_skus()) == ["lh-005", "sg-007"]
    assert purge_hallucinations.PRODUCTS_DIR == WP_PRODUCTS_DIR
