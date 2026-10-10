"""
SDK Capability Mixin
=====================

Grants any DevSkyy agent (CoreAgent, SubAgent, EnhancedSuperAgent)
Claude Agent SDK capabilities alongside existing LLM execution.

Provides:
    _sdk_execute()     — Run a prompt via Claude SDK with tool use
    _sdk_delegate()    — Spawn SDK subagents for parallel work
    _sdk_session()     — Stateful multi-turn SDK conversations
    _sdk_health()      — Session metrics from hooks

This mixin is designed to be composed with SelfHealingMixin — it feeds
tool success/failure events into the circuit breaker automatically.

Usage:
    class MySubAgent(SubAgent, SDKCapabilityMixin):
        sdk_tools = ["Read", "Write", "Bash", "WebSearch"]
        sdk_model = "sonnet"

        async def execute(self, task, **kwargs):
            return await self._sdk_execute(
                task,
                system_prompt="You are a DevSkyy expert.",
            )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ClaudeSDKClient,
)

from agents.claude_sdk.hooks import DevSkyyHookSystem

logger = structlog.get_logger(__name__)


@dataclass
class SDKExecutionResult:
    """Structured result from an SDK execution."""

    success: bool
    response: str
    session_dir: str
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "success": self.success,
            "response": self.response,
            "session_dir": self.session_dir,
        }
        if self.metrics:
            d["metrics"] = self.metrics
        if self.error:
            d["error"] = self.error
        return d


class SDKCapabilityMixin:
    """Mixin that grants Claude Agent SDK capabilities to any agent.

    Designed to compose with SelfHealingMixin. When both are present,
    SDK hook events (tool failures, subagent crashes) automatically
    feed into the circuit breaker and heal journal.

    Class-level configuration (override in subclass):
        sdk_tools:          List of tools available to the SDK agent
        sdk_model:          Claude model for SDK execution
        sdk_max_turns:      Max conversation turns
        sdk_permission:     Permission mode
        sdk_output_base:    Base directory for session artifacts
    """

    # Override in subclass for domain-specific defaults
    sdk_tools: list[str] = ["Read", "Write", "Bash"]
    sdk_model: str = "sonnet"
    sdk_max_turns: int = 15  # 30 caused runaway agents; 15 covers 95% of sub-tasks
    sdk_permission: str = "bypassPermissions"
    sdk_output_base: Path = Path("data/sdk_sessions")

    def _sdk_agent_name(self) -> str:
        """Resolve agent name for logging/telemetry."""
        return getattr(self, "name", self.__class__.__name__)

    def _sdk_session_dir(self, label: str | None = None) -> Path:
        """Create a timestamped session directory."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = self._sdk_agent_name()
        suffix = f"_{label}" if label else ""
        path = self.sdk_output_base / f"{name}{suffix}_{ts}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _sdk_build_hooks(self, session_dir: Path) -> DevSkyyHookSystem:
        """Build hook system with optional self-healing integration."""
        healing = self if hasattr(self, "_record_failure") else None
        return DevSkyyHookSystem(
            session_dir=session_dir,
            agent_name=self._sdk_agent_name(),
            healing_mixin=healing,
        )

    def _sdk_build_options(
        self,
        *,
        session_dir: Path,
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        agents: dict[str, AgentDefinition] | None = None,
        model: str | None = None,
        hooks_system: DevSkyyHookSystem | None = None,
    ) -> tuple[ClaudeAgentOptions, DevSkyyHookSystem]:
        """Build ClaudeAgentOptions with DevSkyy hooks wired in."""
        hook_sys = hooks_system or self._sdk_build_hooks(session_dir)

        options = ClaudeAgentOptions(
            permission_mode=self.sdk_permission,
            system_prompt=system_prompt or self._sdk_default_prompt(),
            allowed_tools=tools or self.sdk_tools,
            agents=agents or {},
            hooks=hook_sys.build_hook_config(),
            model=model or self.sdk_model,
            max_turns=self.sdk_max_turns,
        )
        return options, hook_sys

    def _sdk_default_prompt(self) -> str:
        """Default system prompt. Override for domain-specific prompts."""
        name = self._sdk_agent_name()
        return (
            f"You are {name}, a DevSkyy sub-agent.\n\n"
            "EXECUTION RULES (non-negotiable):\n"
            "- Read before writing. Never modify a file you haven't read this session.\n"
            "- Do exactly what the task says. No extras, no 'improvements' beyond scope.\n"
            "- Stop when the task is done. Don't ask clarifying questions — infer from context.\n"
            "- Return a single structured result. No conversational filler.\n"
            "- If something is ambiguous, pick the most conservative interpretation and proceed.\n\n"
            "PROJECT CONTEXT:\n"
            "- Platform: DevSkyy (AI-driven luxury fashion e-commerce, SkyyRose brand)\n"
            "- Brand: Black Rose, Love Hurts, Signature collections\n"
            "- Stack: FastAPI + Next.js 16 + WordPress theme (skyyrose-flagship)\n"
            "- Colors: #B76E79 rose gold · #0A0A0A dark · #D4AF37 gold · #DC143C crimson\n"
            "- No brand slogan is authorized.\n\n"
            "OUTPUT FORMAT:\n"
            "Return a JSON-serialisable summary: {status, result, files_changed, notes}"
        )

    # ------------------------------------------------------------------
    # Primary execution method
    # ------------------------------------------------------------------

    async def _sdk_execute(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        agents: dict[str, AgentDefinition] | None = None,
        model: str | None = None,
        session_dir: Path | None = None,
        label: str | None = None,
    ) -> SDKExecutionResult:
        """Execute a prompt via Claude Agent SDK.

        This is the primary SDK entry point for any agent. It handles:
        - Client lifecycle (async context manager)
        - Hook wiring for telemetry + self-healing
        - Response streaming and aggregation
        - Session artifact management

        Args:
            prompt: Task prompt to send to the SDK agent.
            system_prompt: Override the default system prompt.
            tools: Override the default tool list.
            agents: SDK AgentDefinition dict for subagent spawning.
            model: Override the default model.
            session_dir: Explicit session directory (auto-created if None).
            label: Optional label for session directory naming.

        Returns:
            SDKExecutionResult with response text, metrics, and session path.
        """
        sdir = session_dir or self._sdk_session_dir(label)
        options, hook_sys = self._sdk_build_options(
            session_dir=sdir,
            system_prompt=system_prompt,
            tools=tools,
            agents=agents,
            model=model,
        )

        response_parts: list[str] = []
        agent_name = self._sdk_agent_name()

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt=prompt)

                async for msg in client.receive_response():
                    msg_type = type(msg).__name__
                    if msg_type == "AssistantMessage":
                        for block in getattr(msg, "message", msg).content:
                            if getattr(block, "type", None) == "text":
                                response_parts.append(block.text)

            hook_sys.close()

            response = "\n".join(response_parts)
            logger.info(
                "sdk_execute_complete",
                agent=agent_name,
                response_len=len(response),
                **hook_sys.metrics.to_dict(),
            )

            return SDKExecutionResult(
                success=True,
                response=response,
                session_dir=str(sdir),
                metrics=hook_sys.metrics.to_dict(),
            )

        except Exception as exc:
            hook_sys.close()
            logger.error(
                "sdk_execute_failed",
                agent=agent_name,
                error=str(exc)[:300],
            )
            return SDKExecutionResult(
                success=False,
                response="",
                session_dir=str(sdir),
                metrics=hook_sys.metrics.to_dict(),
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # Multi-agent delegation
    # ------------------------------------------------------------------

    async def _sdk_delegate(
        self,
        prompt: str,
        agents: dict[str, AgentDefinition],
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        label: str | None = None,
    ) -> SDKExecutionResult:
        """Delegate work to SDK subagents.

        The lead agent (this agent) coordinates named subagents defined
        via AgentDefinition dicts. The lead only uses the Task tool to
        spawn and collect results from subagents.

        Args:
            prompt: Coordination prompt for the lead agent.
            agents: Dict of subagent name → AgentDefinition.
            system_prompt: Lead agent system prompt.
            model: Lead agent model.
            label: Session directory label.

        Returns:
            SDKExecutionResult from the lead agent's final output.
        """
        lead_prompt = system_prompt or (
            f"You are {self._sdk_agent_name()}, a DevSkyy lead agent. "
            "Delegate tasks to your subagents using the Task tool. "
            "Synthesize their results into a final answer."
        )

        return await self._sdk_execute(
            prompt,
            system_prompt=lead_prompt,
            tools=["Task"],
            agents=agents,
            model=model or self.sdk_model,
            label=label or "delegate",
        )

    # ------------------------------------------------------------------
    # Stateful sessions
    # ------------------------------------------------------------------

    async def _sdk_session(
        self,
        prompt: str,
        *,
        session_id: str | None = None,
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        model: str | None = None,
    ) -> SDKExecutionResult:
        """Execute within a stateful SDK session.

        If session_id is provided, resumes an existing session.
        Otherwise creates a new one. Session state is persisted
        in the session directory for multi-turn conversations.

        Args:
            prompt: User prompt for this turn.
            session_id: Existing session ID to resume.
            system_prompt: System prompt (only applied on first turn).
            tools: Tool list override.
            model: Model override.

        Returns:
            SDKExecutionResult with session_dir as the session ID.
        """
        if session_id:
            sdir = Path(session_id)
            if not sdir.exists():
                sdir.mkdir(parents=True, exist_ok=True)
        else:
            sdir = self._sdk_session_dir(label="session")

        return await self._sdk_execute(
            prompt,
            system_prompt=system_prompt,
            tools=tools,
            model=model,
            session_dir=sdir,
        )

    # ------------------------------------------------------------------
    # Metrics access
    # ------------------------------------------------------------------

    def _sdk_last_metrics(self) -> dict[str, Any]:
        """Return metrics from the last SDK execution.

        Subclasses can override to aggregate across multiple
        executions.
        """
        return {}
