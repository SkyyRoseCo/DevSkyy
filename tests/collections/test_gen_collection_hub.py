import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "wordpress-theme/skyyrose-flagship/data"
GEN = DATA / "gen-collection-hub.py"


def _run_gen(out_dir: Path) -> None:
    """Run the hub generator, writing ALL output into `out_dir`.

    Every test gets its own pytest `tmp_path`, so the suite never mutates the tracked
    index.html files in data/collections/ (bug-231 recurrence #5 — the generator used
    to write straight into the tracked tree on every pytest run, dirtying the worktree).
    """
    subprocess.run(
        [sys.executable, str(GEN), "--out-dir", str(out_dir)],
        check=True,
    )


def test_hub_renders_all_sections_and_escapes(tmp_path):
    _run_gen(tmp_path)
    html = (tmp_path / "black-rose" / "index.html").read_text()
    identity = json.loads((DATA / "logo-registry.json").read_text())["collections"]["black-rose"]
    script_font = identity["fonts"]["script"]["family"]
    assert "<!DOCTYPE html>" in html
    assert "Black Rose" in html
    assert "#C0C0C0" in html  # palette swatch
    # font specimen must reflect the registry's collection identity, not a hardcoded family
    assert script_font in html
    assert "black-rose-lockup" in html  # lockup reference
    assert "../../assets/" in html  # image refs into canonical tree
    # no unescaped script injection from data
    assert "<script>alert" not in html
