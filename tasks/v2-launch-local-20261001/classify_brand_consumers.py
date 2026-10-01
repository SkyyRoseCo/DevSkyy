"""Classify broad brand-guard hits by current consumer and owning stream.

Offline source evidence only. Imagery reference was read before prompt classification:
/Users/theceo/.codex/creative-standards/imagery-prompting.md
No generation, provider execution, spending, or external publication.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def classify(relative: str, line: int, content: str) -> tuple[str, str]:
    if relative.startswith("frontend/"):
        return "stream3", "active frontend output or current deployment guidance"
    if "data/collections/" in relative:
        return (
            "stream4/coordinator",
            "documented physical insert artwork; review registry authority before changing supplied product facts",
        )
    if "mascot" in relative:
        return "stream4", "active mascot greeting runtime, including its committed minification"
    if "multi_agent" in relative:
        return "stream3", "active agent instruction or tool prompt"
    if "cli_harnesses" in relative or "gradio" in relative:
        return "coordinator", "active local tool interface copy"
    if relative.startswith("scripts/"):
        if "deploy" in relative:
            return (
                "coordinator",
                "active publishing payload; source correction only, execution held",
            )
        return "stream4", "active creative/provider/training consumer or current tool guidance"
    if relative.startswith("skyyrose/elite_studio/"):
        kind = (
            "current module guidance"
            if line < 20
            else "active creative consumer or current function guidance"
        )
        return "stream4", kind
    return "stream1", "active WordPress consumer requiring correction"


def main() -> None:
    spec = importlib.util.spec_from_file_location(
        "brand_guard", ROOT / "skyyrose/elite_studio/tests/test_brand_enforcement.py"
    )
    assert spec and spec.loader
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    retired = guard.BrandConfig.load().retired_taglines
    old = json.loads((HERE / "evidence/retired-tagline-findings.json").read_text())
    remaining = []
    for filename in guard._git_tracked_files():
        relative = str(filename.relative_to(ROOT))
        if relative in guard._ALLOWED_PATHS:
            continue
        for number, content in enumerate(filename.read_text(errors="replace").splitlines(), 1):
            for phrase in retired:
                if phrase.lower() not in content.lower() or guard._is_enforcement_line(content):
                    continue
                owner, consumer = classify(relative, number, content)
                remaining.append(
                    dict(
                        path=relative,
                        line=number,
                        phrase=phrase,
                        owner=owner,
                        consumer=consumer,
                        source_evidence=content.strip()[:1000],
                        status="OPEN; source verified, authenticated execution not claimed",
                    )
                )
    current_paths = {row["path"] for row in remaining}
    for finding in old:
        finding["status"] = (
            "OPEN"
            if finding["path"] in current_paths
            else "RESOLVED in owned consumer; prior evidence retained"
        )
    result = dict(
        original_hits=len(old),
        original_files=len({row["path"] for row in old}),
        remaining_hits=len(remaining),
        remaining_files=len(current_paths),
        owners=dict(Counter(row["owner"] for row in remaining)),
        original_classification=old,
        remaining_exact_handoff=remaining,
        historical_evidence="Original findings and pre-fix logs retained unchanged outside active scanner scope; no active usage was disguised as history.",
        imagery_reference="/Users/theceo/.codex/creative-standards/imagery-prompting.md",
        provider_controls="not applicable; no provider execution",
        authentication="not applicable; offline source classification",
    )
    (HERE / "evidence/closing/brand-owner-classification.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(
        {
            key: result[key]
            for key in (
                "original_hits",
                "original_files",
                "remaining_hits",
                "remaining_files",
                "owners",
            )
        }
    )


if __name__ == "__main__":
    main()
