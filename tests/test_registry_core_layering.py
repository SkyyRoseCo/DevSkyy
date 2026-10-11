"""The product registry and V2 presentation generator stay below the creative engine.

``skyyrose.core`` is the bottom layer. Reviewed card fronts are validated
against ``skyyrose.core.native_review``; importing the paid creative production
engine from that path would invert the dependency flow and drag provider and
spend code into every catalog build.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = (
    ROOT / "wordpress-theme/skyyrose-flagship-2/scripts/build-product-presentation-registry.py"
)

PROBE = """
import runpy, sys
sys.argv = [sys.argv[1], "--check"]
code = 0
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit as exc:
    code = exc.code or 0
leaked = sorted(m for m in sys.modules if m.startswith("skyyrose.elite_studio.creative"))
print("LEAKED=" + ",".join(leaked))
sys.exit(code)
"""


def test_presentation_registry_build_never_imports_creative_engine():
    result = subprocess.run(
        [sys.executable, "-c", PROBE, str(GENERATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    leaked_line = [line for line in result.stdout.splitlines() if line.startswith("LEAKED=")]
    assert leaked_line, result.stdout + result.stderr
    assert leaked_line[-1] == "LEAKED=", leaked_line[-1]
    assert result.returncode == 0, result.stdout + result.stderr


def test_core_sources_do_not_import_creative_engine():
    offenders = [
        str(path.relative_to(ROOT))
        for path in (ROOT / "skyyrose/core").rglob("*.py")
        if "elite_studio.creative" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
