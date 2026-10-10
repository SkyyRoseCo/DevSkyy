"""Specialist agents for Elite Web Builder.

Each agent is defined as an AgentSpec with role, system prompt, and capabilities.
Import individual specs or use ALL_SPECS for the complete team.

Note: Sub-modules use CWD-relative absolute imports (e.g., ``from agents.base
import ...``).  When running via ``run.py`` the CWD is ``elite_web_builder/``
so these resolve correctly.  For external imports from the project root, use
the subprocess helper in ``scripts/verify_pipelines.py``.
"""

import sys
from pathlib import Path

_EWB_ROOT = str(Path(__file__).resolve().parent.parent)
if _EWB_ROOT not in sys.path:
    sys.path.insert(0, _EWB_ROOT)

from agents.accessibility import ACCESSIBILITY_SPEC
from agents.backend_dev import BACKEND_DEV_SPEC
from agents.base import AgentCapability, AgentOutput, AgentRole, AgentSpec
from agents.design_system import DESIGN_SYSTEM_SPEC
from agents.frontend_dev import FRONTEND_DEV_SPEC
from agents.performance import PERFORMANCE_SPEC
from agents.provider_adapters import (
    LLMMessage,
    LLMResponse,
    get_adapter,
)
from agents.qa import QA_SPEC
from agents.runtime import AgentRuntime
from agents.seo_content import SEO_CONTENT_SPEC

ALL_SPECS: tuple[AgentSpec, ...] = (
    DESIGN_SYSTEM_SPEC,
    FRONTEND_DEV_SPEC,
    BACKEND_DEV_SPEC,
    ACCESSIBILITY_SPEC,
    PERFORMANCE_SPEC,
    SEO_CONTENT_SPEC,
    QA_SPEC,
)

__all__ = [
    "AgentCapability",
    "AgentOutput",
    "AgentRole",
    "AgentSpec",
    "ACCESSIBILITY_SPEC",
    "BACKEND_DEV_SPEC",
    "DESIGN_SYSTEM_SPEC",
    "FRONTEND_DEV_SPEC",
    "PERFORMANCE_SPEC",
    "QA_SPEC",
    "SEO_CONTENT_SPEC",
    "ALL_SPECS",
    "AgentRuntime",
    "LLMMessage",
    "LLMResponse",
    "get_adapter",
]
