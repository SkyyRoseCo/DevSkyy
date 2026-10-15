"""API v1 Package.

This package contains all v1 API routers:
- analytics/business: Business metrics (revenue, orders, AOV, funnel)
- assets: Asset processing and job status
- code: Code scanning and fixing
- commerce: Bulk products and dynamic pricing
- hf_spaces: HuggingFace Spaces integration
- marketing: Marketing campaigns
- media: 3D generation and media processing
- ml: Machine learning predictions
- monitoring: System metrics and agent directory
- orchestration: Multi-agent workflows
- wordpress: WordPress/WooCommerce integration
- wordpress_theme: WordPress theme generation
- training_status: LoRA training progress monitoring
- sync: Asset synchronization pipeline (HF ↔ DevSkyy ↔ WordPress)
- social_media: Social media content generation, scheduling, and analytics

Version: 1.0.0

"""

from api.v1.analytics.business import router as business_router
from api.v1.analytics.dashboard import router as analytics_dashboard_router
from api.v1.approval import router as approval_router
from api.v1.assets import router as assets_router
from api.v1.autonomous import router as autonomous_router
from api.v1.brand_assets import router as brand_assets_router
from api.v1.catalog import router as catalog_router
from api.v1.claude_sdk import router as claude_sdk_router
from api.v1.code import router as code_router
from api.v1.commerce import router as commerce_router
from api.v1.competitors import router as competitors_router
from api.v1.context_dev import router as context_dev_router
from api.v1.descriptions import router as descriptions_router
from api.v1.hf_spaces import hf_spaces_router
from api.v1.lora import lora_router
from api.v1.marketing import router as marketing_router
from api.v1.media import router as media_router
from api.v1.ml import router as ml_router
from api.v1.monitoring import router as monitoring_router
from api.v1.orchestration import router as orchestration_router
from api.v1.render_jobs import router as render_jobs_router
from api.v1.social_media import router as social_media_router
from api.v1.sync import sync_router
from api.v1.training_status import training_router
from api.v1.wordpress_agent import router as wordpress_agent_router
from api.v1.wordpress_theme import router as wordpress_theme_router

__all__ = [
    "approval_router",
    "assets_router",
    "brand_assets_router",
    "business_router",
    "analytics_dashboard_router",
    "catalog_router",
    "code_router",
    "commerce_router",
    "competitors_router",
    "context_dev_router",
    "descriptions_router",
    "hf_spaces_router",
    "marketing_router",
    "media_router",
    "ml_router",
    "autonomous_router",
    "monitoring_router",
    "orchestration_router",
    "render_jobs_router",
    "social_media_router",
    "wordpress_agent_router",
    "wordpress_theme_router",
    "lora_router",
    "training_router",
    "sync_router",
    "claude_sdk_router",
]
