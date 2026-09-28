"""Explainable job-scoped rule selection and lifecycle ceilings; no owner-rule mutation."""

from __future__ import annotations

from typing import Literal

LifecycleStatus = Literal[
    "RESEARCH_READY",
    "PLANNING_READY",
    "PROTOTYPE_READY",
    "CANDIDATE_READY",
    "PRODUCTION_READY",
    "RELEASE_CANDIDATE",
    "LEARNING_READY",
    "ARCHIVE_READY",
    "BLOCKED",
]

STAGES = {
    "M1": "RESEARCH_READY",
    "M2": "PLANNING_READY",
    "M3": "PROTOTYPE_READY",
    "M4": "CANDIDATE_READY",
    "M5": "CANDIDATE_READY",
    "M6": "CANDIDATE_READY",
    "M7": "CANDIDATE_READY",
    "M8": "LEARNING_READY",
    "M9": "ARCHIVE_READY",
}
LOCAL_TERRITORY = [
    "architecture",
    "bridges",
    "streets",
    "neighborhoods",
    "landscapes",
    "transit",
    "industrial environments",
    "waterfronts",
    "cultural locations",
    "natural geography",
]


def select_rules(
    rules: list[dict],
    *,
    exact: bool,
    kids: bool,
    major: bool,
    place: bool,
    medium: str,
    palette_ids: set[str],
) -> tuple[list[str], list[dict]]:
    baseline = {
        "A",
        "B",
        "C",
        "D.origin",
        "G1",
        "N",
        "F",
        "F2",
        "F3",
        "F4",
        "M-001",
        "PRODUCT_MODES",
        "S7-001",
        "S12-001",
    }
    reasons = dict.fromkeys(
        baseline, "Master identity, truth or authority boundary applies across jobs"
    )
    if exact:
        reasons.update(
            dict.fromkeys(
                ["F1", "FIDELITY_METHOD", "FIDELITY_GATE", "M-002", "P2-001", "P3-001"],
                "Actual SKU requires exact product truth and source-preserving method",
            )
        )
    if kids:
        reasons.update({f"K{i}-001": "Canonical Kids collection context" for i in range(1, 6)})
    if major:
        reasons.update(
            {
                f"S{i}-001": "Major initiative requires evolution, experiment and learning context"
                for i in range(1, 13)
            }
        )
        reasons["G8"] = "Major initiative creative evolution"
    if place:
        reasons.update(
            dict.fromkeys(
                ["A", "N6", "N6.discovery", "G3", "F10"],
                "Place is explicitly relevant; explore without prescribing a landmark",
            )
        )
    if medium in ("image", "video", "3d", "interactive", "physical", "mixed"):
        reasons.update(
            dict.fromkeys(
                ["G3", "G7", "F8", "F9"],
                "Visual/spatial expression; world freedom remains subordinate to protected truth",
            )
        )
    if medium in ("video", "interactive", "mixed"):
        reasons.update(
            dict.fromkeys(
                ["G2", "G4", "G5", "G6", "F7", "F12"],
                "Sequence or interaction requires intentional experience and recoverable control",
            )
        )
    if palette_ids:
        reasons.update(
            dict.fromkeys(
                palette_ids | {"P1-001", "P8-001"},
                "Requested palette domain; no cross-domain permission transfer",
            )
        )
    return (
        [r["id"] for r in rules if r["id"] in reasons],
        [
            {
                "id": r["id"],
                "included": r["id"] in reasons,
                "reason": reasons.get(
                    r["id"],
                    "Not required by declared medium, collection, product mode, palette, scale or place; retained in audit, not a permission to contradict protected truth",
                ),
            }
            for r in rules
        ],
    )
