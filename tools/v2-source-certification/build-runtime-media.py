"""Compile verified media decisions into a small installable display policy.

Private decisions remain source/build inputs, never runtime proof documents.
This projection creates no product facts, pixels, roles or media permissions.
"""

import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("verified_theme_package", HERE / "package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def compile_policy():
    theme = package.THEME
    inventory = json.loads((theme / "data/v2-media-eligibility.json").read_text())
    boundary_path = HERE / "package-boundary.json"
    boundary = json.loads(boundary_path.read_text())
    original_selected = [p for p, v in boundary["files"].items() if v["release"]]
    # All original, hash-bound approvals are still validated at build time.
    production = package.validate_scope(inventory, theme)
    policy = package.runtime_media_policy(inventory)
    assets = policy["assets"]
    approved = set(production["masters"])
    for entry in production["masters"].values():
        approved.update(x["path"] for x in entry["delivery_files"])
    if not approved <= assets.keys():
        raise ValueError("Approved production display assets omitted")
    raw = (json.dumps(policy, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    (theme / "data/runtime-media.json").write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    gate = theme / "inc/v2-media-eligibility.php"
    source = gate.read_text()
    source, count = re.subn(
        r"hash_equals\( '(?:RUNTIME_MEDIA_SHA256|[a-f0-9]{64})', hash_file\( 'sha256', \$runtime \) \)",
        f"hash_equals( '{digest}', hash_file( 'sha256', $runtime ) )",
        source,
    )
    if count != 1:
        raise ValueError("Expected one runtime manifest binding")
    gate.write_text(source)
    excluded = []
    for relative, row in boundary["files"].items():
        evidence = relative.startswith("data/v2-media-reviews/") or relative in {
            "README.md", "CHANGELOG.md", "data/v2-media-eligibility.json",
            "data/v2-canonical-media.json", "data/v2-required-media-roles.json",
        }
        withheld = relative in inventory["assets"] and relative not in assets
        if evidence or withheld:
            if row["release"]:
                excluded.append(relative)
            row.update(release=False, category="AUTHORING ONLY", reason=(
                "Private/source approval evidence compiled into runtime-media.json"
                if evidence else "No effective approved runtime display role"
            ))
    boundary["files"]["data/runtime-media.json"] = {
        "release": True, "category": "RUNTIME SOURCE",
        "reason": "Compact hash-bound approved media display policy",
    }
    boundary_path.write_text(json.dumps(boundary, indent=2) + "\n")
    return {
        "policy_sha256": digest, "policy_bytes": len(raw), "approved_assets": len(assets),
        "approved_production_files": len(approved), "removed_package_entries": excluded,
        "previous_selected_count": len(original_selected),
    }


if __name__ == "__main__":
    print(json.dumps(compile_policy(), indent=2))
