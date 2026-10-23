"""
DevSkyy Agents Module
=====================

Hierarchical agent system: 8 Core Agents + 1 Orchestrator.

Core Agents (agents/core/):
    Orchestrator → routes, escalates, Round Table consensus
    ├── CommerceCoreAgent    — products, orders, pricing, inventory
    ├── ContentCoreAgent     — pages, blogs, SEO, copy
    ├── CreativeCoreAgent    — design system, brand, assets
    ├── MarketingCoreAgent   — campaigns, social, audience
    ├── OperationsCoreAgent  — deploy, security, health, code quality
    ├── AnalyticsCoreAgent   — data, trends, conversion
    ├── ImageryCoreAgent     — photos, VTON, 3D models
    └── WebBuilderCoreAgent  — theme generation, deployment

Legacy Agents (backward compat — still importable):
- CommerceAgent, CreativeAgent, MarketingAgent, etc.
- FashnTryOnAgent, TripoAssetAgent, MeshyAgent, etc.

Universal Self-Healing:
- Every agent inherits SelfHealingMixin
- diagnose() → heal() → health_check() → circuit_breaker()
- Escalation: sub-agent → core → orchestrator → human

Lazy loading (PEP 562)
----------------------
Every public name is resolved on first attribute access, so ``import agents``
avoids pulling the whole agent tree (claude_agent_sdk +
mcp, aiohttp, scipy via ``llm``, fastapi via ``core.runtime``) at package load.
``from agents import X`` keeps working for every name in ``__all__``; a submodule
whose optional dependency is missing behaves exactly as the previous eager
try/except did — names that fell back to ``None`` still resolve to ``None``, the
rest raise ``AttributeError`` (``ImportError`` under ``from agents import``).
"""

from __future__ import annotations

import importlib
import logging as _logging
from typing import TYPE_CHECKING

_logger = _logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover — static analysis only, never executed
    from .analytics_agent import AnalyticsAgent
    from .base_super_agent import (
        EnhancedSuperAgent,
        LearningRecord,
        LLMProvider,
        LLMRoundTableInterface,
        MLCapabilitiesModule,
        MLPrediction,
        PromptEngineeringModule,
        PromptTechniqueResult,
        RoundTableEntry,
        RoundTableResult,
        SelfLearningModule,
        SuperAgentType,
        TaskCategory,
    )
    from .claude_sdk import (
        ClaudeSDKBaseAgent,
        DevSkyyHookSystem,
        EmailAutomationAgent,
        ExcelHandlerAgent,
        ResearchAgent,
        SDKCapabilityMixin,
        SDKExecutionResult,
        SDKSubAgent,
        SessionManager,
        ToolProfile,
    )
    from .coding_doctor_agent import (
        CodeIssue,
        CodingDoctorAgent,
        FileReview,
        HealthCheckType,
        HealthReport,
        IssueCategory,
        SeverityLevel,
        create_coding_doctor,
    )
    from .collection_content_agent import CollectionContentAgent
    from .commerce_agent import CommerceAgent
    from .core import (
        CircuitBreakerState,
        CoreAgent,
        CoreAgentType,
        Diagnosis,
        FailureCategory,
        HealCycleResult,
        HealResult,
        HealthStatus,
        Orchestrator,
        SelfHealingMixin,
        SubAgent,
    )
    from .creative_agent import CreativeAgent, VisualTaskType
    from .fashn_agent import (
        FashnConfig,
        FashnTask,
        FashnTaskStatus,
        FashnTryOnAgent,
        GarmentCategory,
        TryOnMode,
        TryOnResult,
    )
    from .marketing_agent import MarketingAgent
    from .meshy_agent import (
        COLLECTION_STYLES,
        MeshyAgent,
        MeshyAssetValidation,
        MeshyConfig,
        MeshyGenerationResult,
        MeshyMode,
        MeshyTask,
        MeshyTaskStatus,
        OutputFormat,
        get_meshy_agent,
    )
    from .operations_agent import OperationsAgent
    from .security_ops_agent import SecurityOpsAgent
    from .skyyrose_content_agent import (
        BrandDNA,
        ContentStatus,
        ContentType,
        GeneratedContent,
        SkyyRoseContentAgent,
    )
    from .skyyrose_imagery_agent import (
        GeneratedImage,
        ImageryBatch,
        ImageryPurpose,
        ModelPose,
        SkyyRoseImageryAgent,
    )
    from .support_agent import SupportAgent
    from .tripo_agent import (
        COLLECTION_PROMPTS,
        GARMENT_TEMPLATES,
    )
    from .tripo_agent import SKYYROSE_BRAND_DNA as TRIPO_BRAND_DNA
    from .tripo_agent import GenerationResult as TripoGenerationResult
    from .tripo_agent import (
        ModelFormat,
        ModelStyle,
        TripoAssetAgent,
        TripoConfig,
        TripoTask,
        TripoTaskStatus,
    )
    from .visual_generation import (
        SKYYROSE_BRAND_DNA,
        AspectRatio,
        ConversationEditor,
        GenerationRequest,
        GenerationResult,
        GenerationType,
        GoogleImagenClient,
        GoogleVeoClient,
        HuggingFaceFluxClient,
        ImageQuality,
        VisualGenerationRouter,
        VisualProvider,
        create_visual_router,
    )
    from .wordpress_asset_agent import (
        GalleryResult,
        MediaUploadResult,
        Model3DUploadResult,
        ProductAssetResult,
        WordPressAssetAgent,
        WordPressAssetConfig,
    )


def _exports(submodule: str, *names: str, **aliases: str) -> dict[str, tuple[str, str]]:
    """Map public names to ``(submodule, attribute)`` for one submodule."""
    mapping = {name: (submodule, name) for name in names}
    mapping.update({alias: (submodule, attr) for alias, attr in aliases.items()})
    return mapping


# Public name -> (relative submodule, attribute inside it). Resolved on demand
# by ``__getattr__`` and cached into the module globals.
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # Core Agent Hierarchy (NEW)
    **_exports(
        "core",
        "CircuitBreakerState",
        "CoreAgent",
        "CoreAgentType",
        "Diagnosis",
        "FailureCategory",
        "HealCycleResult",
        "HealResult",
        "HealthStatus",
        "Orchestrator",
        "SelfHealingMixin",
        "SubAgent",
    ),
    # Legacy agents (backward compat)
    **_exports("analytics_agent", "AnalyticsAgent"),
    **_exports(
        "base_super_agent",
        "EnhancedSuperAgent",
        "LearningRecord",
        "LLMProvider",
        "LLMRoundTableInterface",
        "MLCapabilitiesModule",
        "MLPrediction",
        "PromptEngineeringModule",
        "PromptTechniqueResult",
        "RoundTableEntry",
        "RoundTableResult",
        "SelfLearningModule",
        "SuperAgentType",
        "TaskCategory",
    ),
    **_exports(
        "coding_doctor_agent",
        "CodeIssue",
        "CodingDoctorAgent",
        "FileReview",
        "HealthCheckType",
        "HealthReport",
        "IssueCategory",
        "SeverityLevel",
        "create_coding_doctor",
    ),
    **_exports("collection_content_agent", "CollectionContentAgent"),
    **_exports("commerce_agent", "CommerceAgent"),
    **_exports("creative_agent", "CreativeAgent", "VisualTaskType"),
    **_exports(
        "fashn_agent",
        "FashnConfig",
        "FashnTask",
        "FashnTaskStatus",
        "FashnTryOnAgent",
        "GarmentCategory",
        "TryOnMode",
        "TryOnResult",
    ),
    **_exports("marketing_agent", "MarketingAgent"),
    **_exports("operations_agent", "OperationsAgent"),
    **_exports("security_ops_agent", "SecurityOpsAgent"),
    **_exports(
        "skyyrose_content_agent",
        "BrandDNA",
        "ContentStatus",
        "ContentType",
        "GeneratedContent",
        "SkyyRoseContentAgent",
    ),
    **_exports(
        "skyyrose_imagery_agent",
        "GeneratedImage",
        "ImageryBatch",
        "ImageryPurpose",
        "ModelPose",
        "SkyyRoseImageryAgent",
    ),
    **_exports("support_agent", "SupportAgent"),
    **_exports(
        "meshy_agent",
        "COLLECTION_STYLES",
        "MeshyAgent",
        "MeshyAssetValidation",
        "MeshyConfig",
        "MeshyGenerationResult",
        "MeshyMode",
        "MeshyTask",
        "MeshyTaskStatus",
        "OutputFormat",
        "get_meshy_agent",
    ),
    **_exports(
        "tripo_agent",
        "COLLECTION_PROMPTS",
        "GARMENT_TEMPLATES",
        "ModelFormat",
        "ModelStyle",
        "TripoAssetAgent",
        "TripoConfig",
        "TripoTask",
        "TripoTaskStatus",
        TRIPO_BRAND_DNA="SKYYROSE_BRAND_DNA",
        TripoGenerationResult="GenerationResult",
    ),
    # Visual Generation (primary source for brand DNA and generation types)
    **_exports(
        "visual_generation",
        "SKYYROSE_BRAND_DNA",
        "AspectRatio",
        "ConversationEditor",
        "GenerationRequest",
        "GenerationResult",
        "GenerationType",
        "GoogleImagenClient",
        "GoogleVeoClient",
        "HuggingFaceFluxClient",
        "ImageQuality",
        "VisualGenerationRouter",
        "VisualProvider",
        "create_visual_router",
    ),
    **_exports(
        "claude_sdk",
        "ClaudeSDKBaseAgent",
        "DevSkyyHookSystem",
        "EmailAutomationAgent",
        "ExcelHandlerAgent",
        "ResearchAgent",
        "SDKCapabilityMixin",
        "SDKExecutionResult",
        "SDKSubAgent",
        "SessionManager",
        "ToolProfile",
    ),
    **_exports(
        "wordpress_asset_agent",
        "GalleryResult",
        "MediaUploadResult",
        "Model3DUploadResult",
        "ProductAssetResult",
        "WordPressAssetAgent",
        "WordPressAssetConfig",
    ),
}

# Names the eager package used to bind to ``None`` when their submodule's
# optional dependency was missing. Everything else was simply absent.
_NONE_ON_IMPORT_ERROR: frozenset[str] = frozenset(
    {
        "AnalyticsAgent",
        "CollectionContentAgent",
        "CommerceAgent",
        "CreativeAgent",
        "VisualTaskType",
        "MarketingAgent",
        "OperationsAgent",
        "SecurityOpsAgent",
        "SupportAgent",
        "ClaudeSDKBaseAgent",
        "ResearchAgent",
        "EmailAutomationAgent",
        "ExcelHandlerAgent",
        "SessionManager",
        "SDKCapabilityMixin",
        "SDKExecutionResult",
        "SDKSubAgent",
        "DevSkyyHookSystem",
        "ToolProfile",
    }
)


def __getattr__(name: str) -> object:
    """Resolve a public export (or a submodule) on first access, then cache it."""
    if name.startswith("_"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    export = _LAZY_EXPORTS.get(name)
    if export is None:
        # ``agents.core`` style submodule access without an explicit import.
        try:
            return importlib.import_module(f"{__name__}.{name}")
        except ImportError as exc:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    submodule, attribute = export
    try:
        value = getattr(importlib.import_module(f".{submodule}", __name__), attribute)
    except ImportError as exc:
        _logger.debug("%s unavailable (%s.%s): %s", name, __name__, submodule, exc)
        if name not in _NONE_ON_IMPORT_ERROR:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
        value = None
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


__all__ = [
    # Core Agent Hierarchy (NEW)
    "SelfHealingMixin",
    "CoreAgent",
    "CoreAgentType",
    "SubAgent",
    "Orchestrator",
    "FailureCategory",
    "CircuitBreakerState",
    "Diagnosis",
    "HealResult",
    "HealCycleResult",
    "HealthStatus",
    # Enhanced Super Agent - Types (Legacy)
    "SuperAgentType",
    "TaskCategory",
    "LLMProvider",
    # Enhanced Super Agent - Data classes
    "PromptTechniqueResult",
    "MLPrediction",
    "LearningRecord",
    "RoundTableEntry",
    "RoundTableResult",
    # Enhanced Super Agent - Modules
    "PromptEngineeringModule",
    "MLCapabilitiesModule",
    "SelfLearningModule",
    "LLMRoundTableInterface",
    # Enhanced Super Agent - Base
    "EnhancedSuperAgent",
    # 6 SuperAgents + Coding Doctor
    "CollectionContentAgent",
    "CommerceAgent",
    "CreativeAgent",
    "VisualTaskType",
    "MarketingAgent",
    "SupportAgent",
    "OperationsAgent",
    "AnalyticsAgent",
    "SecurityOpsAgent",
    # Coding Doctor Agent
    "CodingDoctorAgent",
    "create_coding_doctor",
    "HealthCheckType",
    "HealthReport",
    "FileReview",
    "CodeIssue",
    "IssueCategory",
    "SeverityLevel",
    # FASHN Agent
    "FashnTryOnAgent",
    "FashnConfig",
    "FashnTask",
    "TryOnResult",
    "GarmentCategory",
    "TryOnMode",
    "FashnTaskStatus",
    # Meshy Agent
    "MeshyAgent",
    "MeshyConfig",
    "MeshyTask",
    "MeshyGenerationResult",
    "MeshyAssetValidation",
    "MeshyTaskStatus",
    "MeshyMode",
    "OutputFormat",
    "COLLECTION_STYLES",
    "get_meshy_agent",
    # Tripo Agent
    "TripoAssetAgent",
    "TripoConfig",
    "TripoTask",
    "TripoGenerationResult",
    "ModelFormat",
    "ModelStyle",
    "TripoTaskStatus",
    "TRIPO_BRAND_DNA",
    "COLLECTION_PROMPTS",
    "GARMENT_TEMPLATES",
    # Visual Generation (primary exports)
    "VisualProvider",
    "GenerationType",
    "AspectRatio",
    "ImageQuality",
    "GenerationRequest",
    "GenerationResult",
    "SKYYROSE_BRAND_DNA",
    "GoogleImagenClient",
    "GoogleVeoClient",
    "HuggingFaceFluxClient",
    "VisualGenerationRouter",
    "create_visual_router",
    "ConversationEditor",
    # SkyyRose Imagery Agent
    "SkyyRoseImageryAgent",
    "ImageryPurpose",
    "ModelPose",
    "GeneratedImage",
    "ImageryBatch",
    # SkyyRose Content Agent
    "SkyyRoseContentAgent",
    "ContentType",
    "ContentStatus",
    "GeneratedContent",
    "BrandDNA",
    # Claude Agent SDK — Standalone agents
    "ClaudeSDKBaseAgent",
    "ResearchAgent",
    "EmailAutomationAgent",
    "ExcelHandlerAgent",
    "SessionManager",
    # Claude Agent SDK — Deep integration
    "SDKCapabilityMixin",
    "SDKExecutionResult",
    "SDKSubAgent",
    "DevSkyyHookSystem",
    "ToolProfile",
    # WordPress Asset Agent
    "WordPressAssetAgent",
    "WordPressAssetConfig",
    "MediaUploadResult",
    "ProductAssetResult",
    "GalleryResult",
    "Model3DUploadResult",
]
