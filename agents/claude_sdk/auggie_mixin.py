"""
AuggieMixin — auggie-sdk CLI agent spawning for DevSkyy CoreAgents.

Complements SDKCapabilityMixin (Claude Agent SDK) with codebase-aware
Auggie process spawning. Use _auggie_run() when a task benefits from
live repo access and tool use via the auggie CLI.

Usage:
    class MySubAgent(SubAgent, AuggieMixin):
        async def execute(self, task: str, **kwargs):
            return self._auggie_run(task, model="haiku4.5", return_type=str)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RULES = [
    str(_REPO_ROOT / "AGENTS.md"),
    str(_REPO_ROOT / "CLAUDE.md"),
]


class AuggieMixin:
    """Grants auggie CLI agent spawning to any CoreAgent or SubAgent.

    Requires auggie-sdk: pip install auggie-sdk
    Requires authentication: auggie login
    """

    auggie_model: str = "sonnet4.5"
    auggie_max_turns: int = 10
    auggie_allow_indexing: bool = True

    # ------------------------------------------------------------------
    # Primary interface
    # ------------------------------------------------------------------

    def _auggie_run(
        self,
        task: str,
        *,
        model: str | None = None,
        max_turns: int | None = None,
        return_type: type = str,
        functions: list | None = None,
        extra_cli_args: list[str] | None = None,
    ) -> Any:
        """Run a task in a codebase-aware Auggie process.

        Args:
            task: Natural-language instruction for the agent.
            model: Override the default model.
            max_turns: Override the default max turns.
            return_type: Expected Python type for the result.
            functions: Python callables to expose as tools.
            extra_cli_args: Additional auggie CLI flags.

        Returns:
            Result coerced to return_type.
        """
        try:
            from auggie_sdk import Auggie
        except ImportError:
            raise RuntimeError("auggie-sdk not installed — run: pip install auggie-sdk") from None

        cli_args = [
            "--quiet",
            "--max-turns",
            str(max_turns or self.auggie_max_turns),
            *(extra_cli_args or []),
        ]

        agent = Auggie(
            workspace_root=str(_REPO_ROOT),
            model=model or self.auggie_model,
            allow_indexing=self.auggie_allow_indexing,
            rules=_RULES,
            cli_args=cli_args,
        )

        logger.debug(
            "[auggie_mixin] running task (model=%s): %s", model or self.auggie_model, task[:80]
        )
        return agent.run(task, return_type=return_type, functions=functions or [])

    def _auggie_delegate(
        self,
        agent_name: str,
        task: str,
        *,
        model: str | None = None,
        return_type: type = str,
    ) -> Any:
        """Spawn a named subagent from .augment/agents/.

        The agent must exist at .augment/agents/<agent_name>.md.
        """
        try:
            from auggie_sdk import Auggie
        except ImportError:
            raise RuntimeError("auggie-sdk not installed — run: pip install auggie-sdk") from None

        agent_path = _REPO_ROOT / ".augment" / "agents" / f"{agent_name}.md"
        if not agent_path.is_file():
            raise FileNotFoundError(f"Subagent definition not found: {agent_path}")

        cli_args = ["--agent", agent_name, "--quiet"]
        if model:
            cli_args += ["--model", model]

        agent = Auggie(
            workspace_root=str(_REPO_ROOT),
            cli_args=cli_args,
        )

        logger.info("[auggie_mixin] delegating to subagent '%s': %s", agent_name, task[:80])
        return agent.run(task, return_type=return_type)
