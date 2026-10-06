"""
DevSkyy Agent Development Kit (ADK) Integration
===============================================

Enterprise-grade multi-framework agent system integrating:
- Google ADK (v1.20.0) - Production-grade multi-agent framework
- PydanticAI (v1.30.1) - Type-safe agent framework
- CrewAI (v1.6.1) - Role-based collaboration
- AutoGen (v0.7.5) - Microsoft's actor-model agents
- Agno (v2.3.11) - Ultra-fast lightweight agents
- LangGraph (v1.0.4) - Graph-based workflows

For SkyyRose.

Usage:
    from adk import CommerceAgent, SuperAgentOrchestrator

    # Create and use super agent
    commerce = CommerceAgent()
    await commerce.initialize()
    result = await commerce.run("Check inventory for BLACK ROSE jacket")

    # Or use orchestrator for intelligent routing
    orchestrator = SuperAgentOrchestrator()
    await orchestrator.initialize()
    result = await orchestrator.route("Generate marketing content for new collection")
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# Lazy import registry: name → (module_path, attribute)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Base classes
    "ADKProvider": ("adk.base", "ADKProvider"),
    "AgentCapability": ("adk.base", "AgentCapability"),
    "AgentConfig": ("adk.base", "AgentConfig"),
    "AgentFactory": ("adk.base", "AgentFactory"),
    "AgentResult": ("adk.base", "AgentResult"),
    "AgentStatus": ("adk.base", "AgentStatus"),
    "BaseDevSkyyAgent": ("adk.base", "BaseDevSkyyAgent"),
    "ModelTier": ("adk.base", "ModelTier"),
    "ToolCallResult": ("adk.base", "ToolCallResult"),
    "ToolDefinition": ("adk.base", "ToolDefinition"),
    "agent_factory": ("adk.base", "agent_factory"),
    "estimate_cost": ("adk.base", "estimate_cost"),
    "get_api_key": ("adk.base", "get_api_key"),
    # Super Agents
    "SuperAgentType": ("adk.super_agents", "SuperAgentType"),
    "BaseSuperAgent": ("adk.super_agents", "BaseSuperAgent"),
    "CommerceAgent": ("adk.super_agents", "CommerceAgent"),
    "CreativeAgent": ("adk.super_agents", "CreativeAgent"),
    "MarketingAgent": ("adk.super_agents", "MarketingAgent"),
    "SupportAgent": ("adk.super_agents", "SupportAgent"),
    "OperationsAgent": ("adk.super_agents", "OperationsAgent"),
    "AnalyticsAgent": ("adk.super_agents", "AnalyticsAgent"),
    "SuperAgentOrchestrator": ("adk.super_agents", "SuperAgentOrchestrator"),
    "create_super_agent": ("adk.super_agents", "create_super_agent"),
    # PydanticAI
    "PydanticAIAgent": ("adk.pydantic_adk", "PydanticAIAgent"),
    "ProductAnalysis": ("adk.pydantic_adk", "ProductAnalysis"),
    "CustomerIntent": ("adk.pydantic_adk", "CustomerIntent"),
    "ContentPlan": ("adk.pydantic_adk", "ContentPlan"),
    "InventoryForecast": ("adk.pydantic_adk", "InventoryForecast"),
    "ProductAnalyzerAgent": ("adk.pydantic_adk", "ProductAnalyzerAgent"),
    "CustomerIntentAgent": ("adk.pydantic_adk", "CustomerIntentAgent"),
    "ContentPlannerAgent": ("adk.pydantic_adk", "ContentPlannerAgent"),
    "create_pydantic_agent": ("adk.pydantic_adk", "create_pydantic_agent"),
    "create_structured_agent": ("adk.pydantic_adk", "create_structured_agent"),
    # CrewAI
    "CrewAIAgent": ("adk.crewai_adk", "CrewAIAgent"),
    "create_crew": ("adk.crewai_adk", "create_crew"),
    # AutoGen
    "AutoGenAgent": ("adk.autogen_adk", "AutoGenAgent"),
    "create_autogen_team": ("adk.autogen_adk", "create_autogen_team"),
    # Agno
    "AgnoAgent": ("adk.agno_adk", "AgnoAgent"),
    "create_agno_agent": ("adk.agno_adk", "create_agno_agent"),
    # Google ADK
    "GoogleADKAgent": ("adk.google_adk", "GoogleADKAgent"),
    "GoogleMultiAgent": ("adk.google_adk", "GoogleMultiAgent"),
    "create_google_agent": ("adk.google_adk", "create_google_agent"),
    # ADK Workflow Agents
    "PipelineType": ("adk.workflow_agents", "PipelineType"),
    "TokenSavings": ("adk.workflow_agents", "TokenSavings"),
    "WorkflowPipelineAgent": ("adk.workflow_agents", "WorkflowPipelineAgent"),
    "create_product_launch_pipeline": ("adk.workflow_agents", "create_product_launch_pipeline"),
    "create_content_creation_pipeline": ("adk.workflow_agents", "create_content_creation_pipeline"),
    "create_customer_journey_pipeline": ("adk.workflow_agents", "create_customer_journey_pipeline"),
    "create_quality_assurance_pipeline": (
        "adk.workflow_agents",
        "create_quality_assurance_pipeline",
    ),
    "create_campaign_blitz_pipeline": ("adk.workflow_agents", "create_campaign_blitz_pipeline"),
    "get_pipeline": ("adk.workflow_agents", "get_pipeline"),
    "estimate_pipeline_savings": ("adk.workflow_agents", "estimate_pipeline_savings"),
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> Any:
    """Lazy-load ADK components on first access.

    This prevents import-time failures when optional dependencies (Google ADK,
    Agno, CrewAI, etc.) are not installed or the Python version is too old.
    """
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        try:
            mod = importlib.import_module(module_path)
            return getattr(mod, attr)
        except (ImportError, AttributeError) as exc:
            logger.debug("ADK lazy import failed for %s.%s: %s", module_path, attr, exc)
            raise ImportError(
                f"Cannot import '{name}' from '{module_path}'. "
                f"Install the required dependencies or use Python 3.11+. "
                f"Original error: {exc}"
            ) from exc
    raise AttributeError(f"module 'adk' has no attribute {name!r}")
