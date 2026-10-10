"""Analytics API module for DevSkyy admin dashboard."""

from api.v1.analytics.alert_configs import router as alert_configs_router
from api.v1.analytics.alerts import router as alerts_router
from api.v1.analytics.business import router as business_router
from api.v1.analytics.dashboard import router as analytics_dashboard_router
from api.v1.analytics.health import router as health_analytics_router
from api.v1.analytics.ingest import router as storefront_analytics_router
from api.v1.analytics.ml_pipelines import router as ml_analytics_router

__all__ = [
    "alert_configs_router",
    "alerts_router",
    "business_router",
    "analytics_dashboard_router",
    "health_analytics_router",
    "storefront_analytics_router",
    "ml_analytics_router",
]
