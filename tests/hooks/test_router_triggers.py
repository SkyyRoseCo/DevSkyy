"""Every agent named in ``.claude/hooks/router/triggers.json`` must resolve.

The task router (``.claude/hooks/router/router.py``) recommends agents by name.
A name that resolves to nothing sends a session hunting for an agent that does
not exist (audit 2026-09-18 §4e: ten phantom names, one wrong id).

Resolution rule
---------------
An agent name resolves when a tracked agent definition in this repo carries it,
either as the ``name:`` frontmatter value or as the file stem, in one of
``REPO_AGENT_DIRS`` (case-insensitive exact match).

``HOME_ONLY_AGENTS`` is the documented exception: user-level agents that live
only in ``~/.claude/agents`` (not tracked here). They are accepted by name
without a repo definition; when ``~/.claude/agents`` exists on the machine
running the test, they must also resolve there. Add a name to that set only
with the path it lives at — never to make a phantom name pass.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TRIGGERS = REPO_ROOT / ".claude" / "hooks" / "router" / "triggers.json"

# Tracked directories that hold agent definitions (``*.md`` with frontmatter).
REPO_AGENT_DIRS = (
    ".claude/agents",
    "plugins/*/agents",
    "skyyrose-suite/plugins/*/agents",
    "wordpress-copilot/agents",
)

# User-level agents (``~/.claude/agents/...``), by ``name:`` frontmatter.
HOME_ONLY_AGENTS = {
    "Backend Architect",  # ~/.claude/agents/integrations/mcp-memory/backend-architect-with-memory.md
    "Content Creator",  # ~/.claude/agents/marketing/marketing-content-creator.md
    "Accessibility Auditor",  # ~/.claude/agents/testing/testing-accessibility-auditor.md
    "typescript-reviewer",  # ~/.claude/agents/typescript-reviewer.md
}

_NAME_RE = re.compile(r"^name:\s*\"?([^\"\n]+?)\"?\s*$", re.MULTILINE)


def _frontmatter_name(path: Path) -> str | None:
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:4000]
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    match = _NAME_RE.search(head)
    return match.group(1).strip() if match else None


def _agent_names_under(root: Path, globs: tuple[str, ...]) -> set[str]:
    names: set[str] = set()
    for pattern in globs:
        for directory in root.glob(pattern):
            if not directory.is_dir():
                continue
            for path in directory.rglob("*.md"):
                names.add(path.stem.lower())
                name = _frontmatter_name(path)
                if name:
                    names.add(name.lower())
    return names


@pytest.fixture(scope="module")
def triggers() -> dict:
    assert TRIGGERS.is_file(), f"missing {TRIGGERS}"
    return json.loads(TRIGGERS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def repo_agent_names() -> set[str]:
    names = _agent_names_under(REPO_ROOT, REPO_AGENT_DIRS)
    assert names, "no agent definitions found under REPO_AGENT_DIRS"
    return names


def _named_agents(triggers: dict) -> list[tuple[str, str]]:
    return [
        (pattern.get("name", "?"), agent)
        for pattern in triggers.get("patterns", [])
        for agent in pattern.get("agents", [])
    ]


def test_triggers_json_has_patterns(triggers: dict) -> None:
    assert triggers.get("patterns"), "triggers.json has no patterns"


def test_every_agent_resolves(triggers: dict, repo_agent_names: set[str]) -> None:
    unresolved = [
        f"{pack}: {agent!r}"
        for pack, agent in _named_agents(triggers)
        if agent.lower() not in repo_agent_names and agent not in HOME_ONLY_AGENTS
    ]
    assert not unresolved, (
        "triggers.json names agents with no definition in REPO_AGENT_DIRS "
        "(and not in HOME_ONLY_AGENTS):\n  " + "\n  ".join(unresolved)
    )


def test_home_only_agents_are_not_also_repo_agents(repo_agent_names: set[str]) -> None:
    """A name in the exception set must actually be home-only, or the set rots."""
    stale = sorted(n for n in HOME_ONLY_AGENTS if n.lower() in repo_agent_names)
    assert not stale, f"now tracked in the repo — remove from HOME_ONLY_AGENTS: {stale}"


def test_home_only_agents_resolve_in_home_when_present() -> None:
    home_agents = Path.home() / ".claude" / "agents"
    if not home_agents.is_dir():
        pytest.skip("~/.claude/agents absent on this machine (CI)")
    home_names = _agent_names_under(home_agents.parent, ("agents",))
    missing = sorted(n for n in HOME_ONLY_AGENTS if n.lower() not in home_names)
    assert not missing, f"HOME_ONLY_AGENTS not found under {home_agents}: {missing}"
