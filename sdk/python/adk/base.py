"""
ADK Base Module
===============

Core abstractions for DevSkyy's multi-framework agent system.

This module provides:
- Unified agent interface across all ADK frameworks
- Common configuration and result types
- Tool definition standards
- Capability declarations
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _get_tracer():
    """Lazy-load tracer to avoid circular import (adk ← core → adk)."""
    try:
        from core.telemetry.tracer import get_tracer

        return get_tracer("adk.agent")
    except ImportError:
        return None


class _NullSpanCtx:
    """No-op context manager when tracing is unavailable."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def set_attribute(self, key, value):
        pass

    def record_exception(self, exc):
        pass


# =============================================================================
# Enums
# =============================================================================


class ADKProvider(StrEnum):
    """Supported ADK frameworks"""

    GOOGLE = "google_adk"  # Google Agent Development Kit
    PYDANTIC = "pydantic_ai"  # PydanticAI
    CREWAI = "crewai"  # CrewAI
    AUTOGEN = "autogen"  # Microsoft AutoGen
    AGNO = "agno"  # Agno (ultra-fast)
    LANGGRAPH = "langgraph"  # LangGraph


class AgentCapability(StrEnum):
    """Agent capabilities"""

    # Core capabilities
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    PLANNING = "planning"

    # Tool usage
    TOOL_CALLING = "tool_calling"
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATIONS = "file_operations"

    # Multimodal
    VISION = "vision"
    AUDIO = "audio"
    IMAGE_GENERATION = "image_generation"

    # Specialized
    ECOMMERCE = "ecommerce"
    WORDPRESS = "wordpress"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    CUSTOMER_SUPPORT = "customer_support"
    THREE_D_GENERATION = "3d_generation"
    VIRTUAL_TRYON = "virtual_tryon"


class AgentStatus(StrEnum):
    """Agent execution status"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelTier(StrEnum):
    """Model performance tier"""

    FLAGSHIP = "flagship"  # GPT-4o, Claude Opus, Gemini Ultra
    STANDARD = "standard"  # GPT-4o-mini, Claude Sonnet, Gemini Pro
    FAST = "fast"  # GPT-4o-mini, Claude Haiku, Gemini Flash
    LOCAL = "local"  # Ollama, local models


# =============================================================================
# Configuration Models
# =============================================================================


class ToolDefinition(BaseModel):
    """Tool definition for agents"""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description for LLM")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Parameter schema")
    required_params: list[str] = Field(default_factory=list, description="Required parameters")
    handler: str | None = Field(None, description="Handler function path")
    requires_confirmation: bool = Field(False, description="Requires human approval")

    class Config:
        arbitrary_types_allowed = True


class AgentConfig(BaseModel):
    """Universal agent configuration"""

    # Identity
    name: str = Field(..., description="Agent name")
    description: str = Field("", description="Agent description")
    version: str = Field("1.0.0", description="Agent version")

    # Model settings
    model: str = Field("gpt-4o-mini", description="LLM model ID")
    provider: ADKProvider = Field(ADKProvider.PYDANTIC, description="ADK framework")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(4096, ge=1, description="Max output tokens")

    # Behavior
    system_prompt: str = Field("", description="System instructions")
    capabilities: list[AgentCapability] = Field(default_factory=list)
    tools: list[ToolDefinition] = Field(default_factory=list)

    # Execution
    timeout: float = Field(300.0, description="Execution timeout in seconds")
    max_iterations: int = Field(10, description="Max reasoning iterations")
    retry_attempts: int = Field(3, description="Retry attempts on failure")

    # Memory
    enable_memory: bool = Field(True, description="Enable conversation memory")
    memory_window: int = Field(10, description="Messages to keep in memory")

    # SkyyRose specific
    brand_context: str = Field(
        "SkyyRose. Premium streetwear brand based in Oakland.",
        description="Brand context for responses",
    )

    class Config:
        use_enum_values = True


# =============================================================================
# Result Models
# =============================================================================


class ToolCallResult(BaseModel):
    """Result from a tool call"""

    tool_name: str
    arguments: dict[str, Any]
    result: Any
    success: bool
    error: str | None = None
    duration_ms: float = 0


class AgentResult(BaseModel):
    """Result from agent execution"""

    # Identity
    agent_name: str
    agent_provider: ADKProvider

    # Output
    content: str
    structured_output: dict[str, Any] | None = None

    # Execution metadata
    status: AgentStatus = AgentStatus.COMPLETED
    iterations: int = 0
    tool_calls: list[ToolCallResult] = Field(default_factory=list)

    # Performance
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0
    cost_usd: float = 0

    # Timestamps
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    # Error handling
    error: str | None = None
    error_type: str | None = None

    # Extensible metadata for technique selection, correlation, etc.
    metadata: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"AgentResult({self.agent_name}, status={self.status}, tokens={self.total_tokens})"


# =============================================================================
# Base Agent Abstract Class
# =============================================================================


class BaseDevSkyyAgent(ABC):
    """
    Base class for all DevSkyy agents.

    Provides unified interface across all ADK frameworks:
    - Google ADK
    - PydanticAI
    - CrewAI
    - AutoGen
    - Agno
    - LangGraph

    Example:
        class MyAgent(BaseDevSkyyAgent):
            async def execute(self, prompt: str) -> AgentResult:
                # Implementation
                pass

        agent = MyAgent(config)
        result = await agent.run("Hello!")
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.provider = config.provider
        self._status = AgentStatus.IDLE
        self._memory: list[dict[str, Any]] = []
        self._tools: dict[str, Callable] = {}
        self._initialized = False

        logger.info(f"Initializing agent: {self.name} ({self.provider})")

    @property
    def status(self) -> AgentStatus:
        return self._status

    @abstractmethod
    async def execute(self, prompt: str, **kwargs) -> AgentResult:
        """Execute agent with given prompt"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources"""
        pass

    async def run(self, prompt: str, **kwargs) -> AgentResult:
        """
        Run agent with full lifecycle management.

        Args:
            prompt: Input prompt
            **kwargs: Additional arguments

        Returns:
            AgentResult with execution details
        """
        start_time = datetime.now(UTC)
        tracer = _get_tracer()

        span_ctx = (
            tracer.start_as_current_span(f"agent.run.{self.name}") if tracer else _NullSpanCtx()
        )

        with span_ctx as span:
            if tracer:
                span.set_attribute("agent.name", self.name)
                span.set_attribute("agent.provider", self.provider)

            try:
                # Initialize if needed
                if not self._initialized:
                    await self.initialize()
                    self._initialized = True

                self._status = AgentStatus.RUNNING

                # Execute
                result = await asyncio.wait_for(
                    self.execute(prompt, **kwargs),
                    timeout=self.config.timeout,
                )

                self._status = AgentStatus.COMPLETED
                result.completed_at = datetime.now(UTC)
                result.latency_ms = (result.completed_at - start_time).total_seconds() * 1000

                # Update memory
                if self.config.enable_memory:
                    self._update_memory(prompt, result.content)

                if tracer:
                    span.set_attribute("agent.status", result.status.value)
                    span.set_attribute("agent.latency_ms", result.latency_ms)
                return result

            except TimeoutError:
                self._status = AgentStatus.FAILED
                if tracer:
                    span.set_attribute("agent.status", "failed")
                    span.set_attribute("agent.error_type", "TimeoutError")
                return AgentResult(
                    agent_name=self.name,
                    agent_provider=self.provider,
                    content="",
                    status=AgentStatus.FAILED,
                    error=f"Execution timed out after {self.config.timeout}s",
                    error_type="TimeoutError",
                    started_at=start_time,
                    completed_at=datetime.now(UTC),
                )
            except Exception as e:
                self._status = AgentStatus.FAILED
                if tracer:
                    span.record_exception(e)
                    span.set_attribute("agent.status", "failed")
                    span.set_attribute("agent.error_type", type(e).__name__)
                logger.error(f"Agent {self.name} failed: {e}", exc_info=True)
                return AgentResult(
                    agent_name=self.name,
                    agent_provider=self.provider,
                    content="",
                    status=AgentStatus.FAILED,
                    error=str(e),
                    error_type=type(e).__name__,
                    started_at=start_time,
                    completed_at=datetime.now(UTC),
                )

    def _update_memory(self, prompt: str, response: str) -> None:
        """Update conversation memory"""
        self._memory.append({"role": "user", "content": prompt})
        self._memory.append({"role": "assistant", "content": response})

        # Trim to window size
        max_messages = self.config.memory_window * 2
        if len(self._memory) > max_messages:
            self._memory = self._memory[-max_messages:]

    def register_tool(self, name: str, handler: Callable, description: str = "") -> None:
        """Register a tool handler"""
        self._tools[name] = handler
        logger.debug(f"Registered tool: {name}")

    def get_memory(self) -> list[dict[str, Any]]:
        """Get conversation memory"""
        return self._memory.copy()

    def clear_memory(self) -> None:
        """Clear conversation memory"""
        self._memory.clear()

    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        self._initialized = False
        self._status = AgentStatus.IDLE
        logger.info(f"Agent {self.name} cleaned up")


# =============================================================================
# Agent Factory
# =============================================================================


@dataclass
class AgentFactory:
    """
    Factory for creating agents with any ADK framework.

    Example:
        factory = AgentFactory()
        agent = factory.create(
            name="assistant",
            provider=ADKProvider.PYDANTIC,
            model="gpt-4o-mini"
        )
    """

    _registry: dict[ADKProvider, type[BaseDevSkyyAgent]] = field(default_factory=dict)

    def register(self, provider: ADKProvider, agent_class: type[BaseDevSkyyAgent]) -> None:
        """Register an agent class for a provider"""
        self._registry[provider] = agent_class
        logger.info(f"Registered {agent_class.__name__} for {provider}")

    def create(
        self,
        name: str,
        provider: ADKProvider = ADKProvider.PYDANTIC,
        model: str = "gpt-4o-mini",
        **kwargs,
    ) -> BaseDevSkyyAgent:
        """Create an agent instance"""
        if provider not in self._registry:
            raise ValueError(f"No agent registered for provider: {provider}")

        config = AgentConfig(
            name=name,
            provider=provider,
            model=model,
            **kwargs,
        )

        agent_class = self._registry[provider]
        return agent_class(config)

    def list_providers(self) -> list[ADKProvider]:
        """List registered providers"""
        return list(self._registry.keys())


# Global factory instance
agent_factory = AgentFactory()


# =============================================================================
# Utility Functions
# =============================================================================


def get_api_key(provider: str) -> str | None:
    """Get API key for provider from environment"""
    key_map = {
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "google": ["GOOGLE_API_KEY", "GOOGLE_AI_API_KEY", "GEMINI_API_KEY"],
        "gemini": ["GOOGLE_API_KEY", "GOOGLE_AI_API_KEY", "GEMINI_API_KEY"],
        "mistral": ["MISTRAL_API_KEY"],
        "cohere": ["COHERE_API_KEY"],
        "groq": ["GROQ_API_KEY"],
    }

    env_vars = key_map.get(provider.lower(), [])
    for var in env_vars:
        val = os.getenv(var)
        if val:
            return val
    return None


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate cost in USD for model usage"""
    # Prices per 1M tokens (as of Dec 2025)
    prices = {
        # OpenAI
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "o1-preview": {"input": 15.00, "output": 60.00},
        # Anthropic
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        # Google
        "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        # Groq (fast inference)
        "llama-3.1-70b": {"input": 0.59, "output": 0.79},
        "llama-3.1-8b": {"input": 0.05, "output": 0.08},
    }

    # Find matching model
    for model_key, price in prices.items():
        if model_key in model.lower():
            input_cost = (input_tokens / 1_000_000) * price["input"]
            output_cost = (output_tokens / 1_000_000) * price["output"]
            return input_cost + output_cost

    # Default estimate
    return (input_tokens + output_tokens) / 1_000_000 * 1.0


# =============================================================================
# Export
# =============================================================================

__all__ = [
    # Enums
    "ADKProvider",
    "AgentCapability",
    "AgentStatus",
    "ModelTier",
    # Models
    "ToolDefinition",
    "AgentConfig",
    "ToolCallResult",
    "AgentResult",
    # Base class
    "BaseDevSkyyAgent",
    # Factory
    "AgentFactory",
    "agent_factory",
    # Utilities
    "get_api_key",
    "estimate_cost",
]
