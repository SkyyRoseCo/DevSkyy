"""
Gate classification for the flagship-2 npm scripts.

The script list is read from package.json at call time, but permission to run a
script comes only from the explicit tables below. A script that appears in
package.json without an entry here is ``unclassified`` and refused: a new
script must be reviewed and classified before an agent can run it (fail closed).

Classes:
  check    read-only gate; running it must not change tracked files
  build    regenerates tracked theme outputs locally (never deploys)
  blocked  never runnable from this CLI (image generation, judge/provider
           probes, receipts that certify paid work, render pipelines)
"""

from __future__ import annotations

from dataclasses import dataclass

# Read-only gates and the God Mode X evidence categories each one exercises.
CHECK_GATES: dict[str, tuple[str, ...]] = {
    "verify": (
        "functional",
        "regression",
        "runtime",
        "performance",
        "quality",
        "external_contract",
        "security_data",
    ),
    "check:source-integrity": ("integration", "regression"),
    "check:registry": ("regression", "quality"),
    "check:assets": ("regression", "quality"),
    "check:critical": ("regression", "performance"),
    "check:i18n": ("regression", "quality"),
    "check:tokens": ("regression", "quality"),
    "check:card-renditions": ("regression", "quality"),
    "check:scene-posters": ("regression", "quality"),
    "check:font-delivery": ("regression", "performance"),
    "check:frame-delivery": ("regression", "performance"),
    "check:archive-theme": ("regression", "quality"),
    "check:approved-scenes": ("regression", "quality"),
    "check:commerce-scenes": ("regression", "quality"),
    "check:legacy-founder-scenes": ("regression", "quality"),
    "check:provisioning": ("functional",),
    "lint:php": ("quality",),
    "verify:workspace": ("integration",),
    "verify:workspace:strict": ("integration",),
}

# Local builds that rewrite tracked outputs. `build` and `package:theme` chain
# many of these; package:theme also runs verify and writes dist/.
BUILD_GATES: frozenset[str] = frozenset(
    {
        "build",
        "build:registry",
        "build:assets",
        "build:critical",
        "build:i18n",
        "build:tokens",
        "build:card-renditions",
        "build:scene-posters",
        "build:font-delivery",
        "build:frame-delivery",
        "build:archive-theme",
        "package:theme",
    }
)

_BLOCK_REASON = (
    "image-generation, judge-provider or render pipeline; it can make provider calls or "
    "certify paid work, which needs a founder STOP-AND-SHOW approval outside this CLI"
)
BLOCKED_PREFIXES: tuple[str, ...] = ("render:", "certify:", "workflow:", "author:")
BLOCKED_GATES: frozenset[str] = frozenset(
    {
        "build:image-generation-proof",
        "check:image-judge-availability",
        "check:image-generation-preflight",
        "check:image-generation-adversarial",
    }
)

# Gates whose chain includes tools/v2-runtime/test-pdp-gallery.php, which needs
# the hash-pinned native WordPress/WooCommerce fixture (V2_WP_FIXTURE).
NEEDS_WP_FIXTURE: frozenset[str] = frozenset({"verify", "package:theme"})

# A full run of these is what `check all` means. verify:workspace:strict is
# excluded because it requires the candidate handoff branch, which a feature
# branch never is.
CHECK_ALL_ORDER: tuple[str, ...] = (
    "check:source-integrity",
    "check:registry",
    "check:assets",
    "check:i18n",
    "check:tokens",
    "check:card-renditions",
    "check:scene-posters",
    "check:font-delivery",
    "check:frame-delivery",
    "check:archive-theme",
    "lint:php",
    "verify",
)


@dataclass(frozen=True)
class Gate:
    name: str
    kind: str  # check | build | blocked | unclassified
    command: str | None
    categories: tuple[str, ...] = ()
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "command": self.command,
            "categories": list(self.categories),
            "reason": self.reason,
        }


class GateRefusedError(RuntimeError):
    """The requested script may not be run from this CLI."""


def classify(name: str, scripts: dict[str, str]) -> Gate:
    command = scripts.get(name)
    if command is None:
        return Gate(name, "missing", None, reason="not defined in package.json")
    if name in BLOCKED_GATES or name.startswith(BLOCKED_PREFIXES):
        return Gate(name, "blocked", command, reason=_BLOCK_REASON)
    if name in CHECK_GATES:
        return Gate(name, "check", command, CHECK_GATES[name])
    if name in BUILD_GATES:
        return Gate(name, "build", command, ("regression",))
    return Gate(
        name,
        "unclassified",
        command,
        reason="new script; classify it in core/gates.py before it can run",
    )


def classify_all(scripts: dict[str, str]) -> list[Gate]:
    return [classify(name, scripts) for name in scripts]


def require_runnable(name: str, scripts: dict[str, str], kind: str) -> Gate:
    """Return the gate if it is of *kind*; otherwise raise with the reason."""
    gate = classify(name, scripts)
    if gate.kind != kind:
        detail = gate.reason or f"it is a {gate.kind} gate"
        raise GateRefusedError(f"Refusing to run {name!r} as {kind}: {gate.kind} — {detail}")
    return gate
