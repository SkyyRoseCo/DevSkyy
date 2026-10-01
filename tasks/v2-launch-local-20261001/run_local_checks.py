"""Run independent, local launch gates; record failures without hiding later checks.

No provider, deployment, order, payment, push, or merge commands are included.
Use the declared V2 Python/Node toolchain and hash-pinned native source fixture.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
EVIDENCE = Path(os.environ.get("STREAM1_EVIDENCE_DIR", str(HERE / "evidence"))).resolve()
PYTHON = ROOT / ".venv/bin/python"
NODE = Path("/Users/theceo/.hermes/node/bin/node")
NPM = Path("/Users/theceo/.hermes/node/lib/node_modules/npm/bin/npm-cli.js")


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_status_before = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
    )
    env = dict(os.environ)
    env["PATH"] = ":".join(
        ["/tmp/stream1-v2-venv/bin", str(NODE.parent), "/opt/homebrew/bin", "/usr/bin", "/bin"]
    )
    env["V2_WP_FIXTURE"] = "/tmp/stream1-native-downloads/wordpress"
    checks: list[tuple[str, str, list[str], Path]] = [
        (
            "registry-sync",
            "Registry-owned projections match current source",
            [str(PYTHON), "scripts/sync_product_registry.py", "--check"],
            ROOT,
        ),
        (
            "asset-manifest",
            "All asset bindings are hash-current",
            [str(PYTHON), "scripts/build_asset_manifest.py", "--check"],
            ROOT,
        ),
        (
            "python-regression",
            "Product identity, canonical migration, brand and FAQ positive/negative paths",
            [
                str(PYTHON),
                "-m",
                "pytest",
                "--no-cov",
                "-q",
                "skyyrose/elite_studio/tests/test_brand.py",
                "tests/test_product_entry_point.py",
                "tests/test_registry_organization.py",
                "tests/test_unified_product_registry.py",
                "tests/test_collection_sot_guard.py",
                "tests/test_storefront_card_migration.py",
                "tests/test_brand_php_generation.py",
                "tests/test_faq_candidate.py",
                "tests/wordpress/test_collection_page_manager.py",
            ],
            ROOT,
        ),
        (
            "brand-enforcement",
            "Retired tagline does not appear as active source content",
            [
                str(PYTHON),
                "-m",
                "pytest",
                "--no-cov",
                "-q",
                "skyyrose/elite_studio/tests/test_brand_enforcement.py",
            ],
            ROOT,
        ),
        (
            "runtime-js",
            "Motion, menu, responsive commerce, loading and error contracts",
            [
                str(NODE),
                "--test",
                *[str(p) for p in sorted((ROOT / "tools/v2-runtime").glob("test-*.cjs"))],
            ],
            ROOT,
        ),
    ]
    for name in (
        "check:assets",
        "check:i18n",
        "check:registry",
        "check:tokens",
        "check:card-renditions",
        "check:font-delivery",
        "check:frame-delivery",
        "check:approved-scenes",
        "check:scene-posters",
        "lint:php",
        "build",
        "verify",
        "package:theme",
    ):
        checks.append(
            (
                "v2-" + name.replace(":", "-"),
                name + " from owning V2 package",
                [str(NODE), str(NPM), "run", name],
                THEME,
            )
        )
    for name in (
        "test-commerce-page-assets.php",
        "test-pdp-approved-fronts.php",
        "test-pdp-gallery.php",
        "test-launch-readiness.php",
        "test-product-media.php",
        "test-product-card.php",
        "test-pdp-summary.php",
        "test-pdp-delivery.php",
        "test-collection-routes.php",
        "test-home-labels.php",
        "test-cart-contract.php",
        "test-checkout-truth.php",
    ):
        checks.append(
            (
                name.removesuffix(".php"),
                "Native and source runtime contract: " + name,
                ["php", "tools/v2-runtime/" + name],
                ROOT,
            )
        )
    for name in (
        "test-performance.php",
        "test-critical-rendering.php",
        "test-global-shell-contract.php",
        "test-seo-indexing.php",
        "test-prelaunch-safety.php",
    ):
        checks.append(
            (
                name.removesuffix(".php"),
                "Theme safety contract: " + name,
                ["php", "scripts/" + name],
                THEME,
            )
        )
    results = []
    for requirement, expected, command, cwd in checks:
        timestamp = datetime.now(UTC).isoformat()
        output = EVIDENCE / (requirement + ".log")
        try:
            result = subprocess.run(
                command, cwd=cwd, env=env, capture_output=True, text=True, timeout=180
            )
            log = result.stdout + result.stderr
            code = result.returncode
            status = "PASS" if code == 0 else "FAIL"
        except subprocess.TimeoutExpired as error:
            log = "TIMEOUT: " + str(error)
            code, status = None, "BLOCKED"
        output.write_text(log)
        results.append(
            {
                "requirement_id": requirement,
                "layer": "LOCAL",
                "expected_behavior": expected,
                "observed_result": "exit " + str(code),
                "status": status,
                "tested_sha": sha,
                "artifact_sha256": hashlib.sha256(log.encode()).hexdigest(),
                "environment": "isolated local worktree; no external mutation",
                "timestamp_utc": timestamp,
                "command": command,
                "cwd": str(cwd),
                "evidence": str(output.relative_to(ROOT)),
                "remaining_owner": (
                    None
                    if status == "PASS"
                    else "stream4" if requirement == "v2-build" else "stream1/coordinator"
                ),
            }
        )
        print(requirement + ": " + status, flush=True)
    (EVIDENCE / "local-checks.json").write_text(
        json.dumps(
            {
                "tested_sha": sha,
                "ending_sha": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
                ).strip(),
                "tracked_status_before": source_status_before,
                "tracked_status_after": subprocess.check_output(
                    ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
                ),
                "checks": results,
            },
            indent=2,
        )
        + "\n"
    )
    return 0 if all(row["status"] == "PASS" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
