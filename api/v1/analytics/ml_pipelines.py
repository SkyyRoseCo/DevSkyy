# api/v1/analytics/ml_pipelines.py
"""
ML Pipeline Analytics API for DevSkyy Admin Dashboard.

Provides endpoints for monitoring ML pipeline performance including:
- 3D generation pipelines (Tripo, Replicate)
- Image description pipelines (Gemini, HuggingFace)
- Asset processing pipelines
- Provider-level cost and performance metrics

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from security import RoleChecker, TokenPayload, UserRole

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Real FastAPI dependency (security.require_roles is a decorator: wrapping it in
# Depends() made FastAPI treat its `func` parameter as a query param, so
# `?func=x` skipped authentication entirely).
_require_analytics_admin = RoleChecker([UserRole.ADMIN, UserRole.SUPER_ADMIN])

router = APIRouter(prefix="/analytics/ml", tags=["ML Analytics"])


# =============================================================================
# Enums
# =============================================================================


class TimeRange(StrEnum):
    """Time range options for analytics queries."""

    HOUR_1 = "1h"
    HOURS_24 = "24h"
    DAYS_7 = "7d"
    DAYS_30 = "30d"
    DAYS_90 = "90d"


class MLProvider(StrEnum):
    """ML service providers."""

    REPLICATE = "replicate"
    TRIPO = "tripo"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"
    OPENAI = "openai"


class PipelineType(StrEnum):
    """Types of ML pipelines."""

    THREE_D_GENERATION = "3d_generation"
    IMAGE_DESCRIPTION = "image_description"
    ASSET_PROCESSING = "asset_processing"
    EMBEDDING = "embedding"
    RERANKING = "reranking"


class JobStatus(StrEnum):
    """ML job statuses."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Response Models
# =============================================================================


class LatencyPercentiles(BaseModel):
    """Latency percentile metrics."""

    p50: float = Field(description="50th percentile latency in seconds")
    p95: float = Field(description="95th percentile latency in seconds")
    p99: float = Field(description="99th percentile latency in seconds")


class PipelineMetrics(BaseModel):
    """Metrics for a single pipeline type."""

    pipeline_type: PipelineType
    total_jobs: int = Field(description="Total number of jobs")
    completed_jobs: int = Field(description="Number of completed jobs")
    failed_jobs: int = Field(description="Number of failed jobs")
    success_rate: float = Field(description="Success rate as percentage")
    avg_duration_seconds: float = Field(description="Average job duration in seconds")
    latency: LatencyPercentiles
    total_cost_usd: Decimal = Field(description="Total cost in USD")


class ProviderMetrics(BaseModel):
    """Metrics for a single ML provider."""

    provider: MLProvider
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    success_rate: float
    avg_duration_seconds: float
    latency: LatencyPercentiles
    total_cost_usd: Decimal
    cost_per_job_usd: Decimal
    api_errors: int = Field(description="Number of API errors")
    rate_limit_hits: int = Field(description="Number of rate limit hits")


class ThreeDMetrics(BaseModel):
    """Metrics specific to 3D generation pipeline."""

    total_models_generated: int
    successful_models: int
    failed_models: int
    success_rate: float
    avg_generation_time_seconds: float
    avg_fidelity_score: float | None = Field(description="Average fidelity score (0-100)")
    models_below_threshold: int = Field(description="Models below 95% fidelity")
    total_cost_usd: Decimal
    by_provider: list[ProviderMetrics]


class DescriptionMetrics(BaseModel):
    """Metrics specific to image description pipeline."""

    total_descriptions: int
    successful_descriptions: int
    failed_descriptions: int
    success_rate: float
    avg_processing_time_seconds: float
    avg_token_count: int | None
    total_cost_usd: Decimal
    by_provider: list[ProviderMetrics]


class AssetMetrics(BaseModel):
    """Metrics specific to asset processing pipeline."""

    total_assets_processed: int
    successful_processing: int
    failed_processing: int
    success_rate: float
    avg_processing_time_seconds: float
    total_storage_bytes: int
    total_cost_usd: Decimal


class MLOverviewResponse(BaseModel):
    """Overview of all ML pipelines."""

    time_range: TimeRange
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    total_jobs: int
    total_completed: int
    total_failed: int
    overall_success_rate: float
    total_cost_usd: Decimal
    pipelines: list[PipelineMetrics]
    top_errors: list[dict[str, Any]] = Field(description="Top 5 error types")


class ThreeDAnalyticsResponse(BaseModel):
    """Response for 3D generation analytics."""

    time_range: TimeRange
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: ThreeDMetrics
    hourly_trend: list[dict[str, Any]] = Field(description="Hourly job counts")


class DescriptionAnalyticsResponse(BaseModel):
    """Response for image description analytics."""

    time_range: TimeRange
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: DescriptionMetrics
    hourly_trend: list[dict[str, Any]] = Field(description="Hourly job counts")


class AssetAnalyticsResponse(BaseModel):
    """Response for asset processing analytics."""

    time_range: TimeRange
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: AssetMetrics


class ProviderAnalyticsResponse(BaseModel):
    """Response for provider-level analytics."""

    time_range: TimeRange
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    providers: list[ProviderMetrics]
    total_cost_usd: Decimal


# =============================================================================
# Helper Functions
# =============================================================================


def get_time_range_start(time_range: TimeRange) -> datetime:
    """Calculate start datetime from time range."""
    now = datetime.now(UTC)
    if time_range == TimeRange.HOUR_1:
        return now - timedelta(hours=1)
    elif time_range == TimeRange.HOURS_24:
        return now - timedelta(hours=24)
    elif time_range == TimeRange.DAYS_7:
        return now - timedelta(days=7)
    elif time_range == TimeRange.DAYS_30:
        return now - timedelta(days=30)
    elif time_range == TimeRange.DAYS_90:
        return now - timedelta(days=90)
    return now - timedelta(hours=24)


def generate_mock_latency() -> LatencyPercentiles:
    """Generate mock latency percentiles for demo."""
    import random

    base = random.uniform(0.5, 2.0)
    return LatencyPercentiles(
        p50=round(base, 3),
        p95=round(base * 1.5, 3),
        p99=round(base * 2.0, 3),
    )


def generate_mock_pipeline_metrics(
    pipeline_type: PipelineType,
    time_range: TimeRange,
) -> PipelineMetrics:
    """Generate mock pipeline metrics for demo."""
    import random

    total = random.randint(100, 1000)
    completed = int(total * random.uniform(0.85, 0.98))
    failed = total - completed

    return PipelineMetrics(
        pipeline_type=pipeline_type,
        total_jobs=total,
        completed_jobs=completed,
        failed_jobs=failed,
        success_rate=round((completed / total) * 100, 2) if total > 0 else 0,
        avg_duration_seconds=round(random.uniform(1.0, 30.0), 2),
        latency=generate_mock_latency(),
        total_cost_usd=Decimal(str(round(total * random.uniform(0.01, 0.10), 2))),
    )


def generate_mock_provider_metrics(
    provider: MLProvider,
    time_range: TimeRange,
) -> ProviderMetrics:
    """Generate mock provider metrics for demo."""
    import random

    total = random.randint(50, 500)
    completed = int(total * random.uniform(0.85, 0.98))
    failed = total - completed
    cost = round(total * random.uniform(0.02, 0.15), 2)

    return ProviderMetrics(
        provider=provider,
        total_jobs=total,
        completed_jobs=completed,
        failed_jobs=failed,
        success_rate=round((completed / total) * 100, 2) if total > 0 else 0,
        avg_duration_seconds=round(random.uniform(1.0, 30.0), 2),
        latency=generate_mock_latency(),
        total_cost_usd=Decimal(str(cost)),
        cost_per_job_usd=Decimal(str(round(cost / total, 4))) if total > 0 else Decimal("0"),
        api_errors=random.randint(0, 10),
        rate_limit_hits=random.randint(0, 5),
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/overview",
    response_model=MLOverviewResponse,
    summary="Get ML Pipeline Overview",
    description="Get summary metrics across all ML pipelines.",
)
async def get_ml_overview(
    time_range: TimeRange = Query(
        default=TimeRange.HOURS_24,
        description="Time range for analytics",
    ),
    current_user: TokenPayload = Depends(_require_analytics_admin),
) -> MLOverviewResponse:
    """
    Get overview of all ML pipelines.

    Requires admin or analyst role.
    """
    pipelines = [
        generate_mock_pipeline_metrics(pt, time_range)
        for pt in [
            PipelineType.THREE_D_GENERATION,
            PipelineType.IMAGE_DESCRIPTION,
            PipelineType.ASSET_PROCESSING,
        ]
    ]

    total_jobs = sum(p.total_jobs for p in pipelines)
    total_completed = sum(p.completed_jobs for p in pipelines)
    total_failed = sum(p.failed_jobs for p in pipelines)
    total_cost = sum(p.total_cost_usd for p in pipelines)

    return MLOverviewResponse(
        time_range=time_range,
        total_jobs=total_jobs,
        total_completed=total_completed,
        total_failed=total_failed,
        overall_success_rate=(
            round((total_completed / total_jobs) * 100, 2) if total_jobs > 0 else 0
        ),
        total_cost_usd=total_cost,
        pipelines=pipelines,
        top_errors=[
            {"error_type": "timeout", "count": 15, "percentage": 35.0},
            {"error_type": "rate_limit", "count": 10, "percentage": 23.0},
            {"error_type": "invalid_input", "count": 8, "percentage": 19.0},
            {"error_type": "provider_error", "count": 6, "percentage": 14.0},
            {"error_type": "network_error", "count": 4, "percentage": 9.0},
        ],
    )


@router.get(
    "/3d",
    response_model=ThreeDAnalyticsResponse,
    summary="Get 3D Generation Analytics",
    description="Get metrics for 3D model generation pipeline.",
)
async def get_3d_analytics(
    time_range: TimeRange = Query(
        default=TimeRange.HOURS_24,
        description="Time range for analytics",
    ),
    provider: MLProvider | None = Query(
        default=None,
        description="Filter by provider",
    ),
    current_user: TokenPayload = Depends(_require_analytics_admin),
) -> ThreeDAnalyticsResponse:
    """
    Get 3D generation pipeline analytics.

    Includes metrics broken down by provider (Tripo, Replicate).
    """
    import random

    providers = [MLProvider.TRIPO, MLProvider.REPLICATE]
    if provider:
        providers = [provider]

    provider_metrics = [generate_mock_provider_metrics(p, time_range) for p in providers]

    total = sum(p.total_jobs for p in provider_metrics)
    completed = sum(p.completed_jobs for p in provider_metrics)
    failed = sum(p.failed_jobs for p in provider_metrics)
    total_cost = sum(p.total_cost_usd for p in provider_metrics)

    metrics = ThreeDMetrics(
        total_models_generated=total,
        successful_models=completed,
        failed_models=failed,
        success_rate=round((completed / total) * 100, 2) if total > 0 else 0,
        avg_generation_time_seconds=round(random.uniform(15.0, 45.0), 2),
        avg_fidelity_score=round(random.uniform(92.0, 98.0), 1),
        models_below_threshold=random.randint(0, int(total * 0.05)),
        total_cost_usd=total_cost,
        by_provider=provider_metrics,
    )

    # Generate hourly trend
    hourly_trend = []
    for i in range(24):
        hourly_trend.append(
            {
                "hour": i,
                "jobs": random.randint(5, 50),
                "success_rate": round(random.uniform(85.0, 99.0), 1),
            }
        )

    return ThreeDAnalyticsResponse(
        time_range=time_range,
        metrics=metrics,
        hourly_trend=hourly_trend,
    )


@router.get(
    "/descriptions",
    response_model=DescriptionAnalyticsResponse,
    summary="Get Image Description Analytics",
    description="Get metrics for image description pipeline.",
)
async def get_description_analytics(
    time_range: TimeRange = Query(
        default=TimeRange.HOURS_24,
        description="Time range for analytics",
    ),
    provider: MLProvider | None = Query(
        default=None,
        description="Filter by provider",
    ),
    current_user: TokenPayload = Depends(_require_analytics_admin),
) -> DescriptionAnalyticsResponse:
    """
    Get image description pipeline analytics.

    Includes metrics broken down by provider (Gemini, HuggingFace).
    """
    import random

    providers = [MLProvider.GEMINI, MLProvider.HUGGINGFACE]
    if provider:
        providers = [provider]

    provider_metrics = [generate_mock_provider_metrics(p, time_range) for p in providers]

    total = sum(p.total_jobs for p in provider_metrics)
    completed = sum(p.completed_jobs for p in provider_metrics)
    failed = sum(p.failed_jobs for p in provider_metrics)
    total_cost = sum(p.total_cost_usd for p in provider_metrics)

    metrics = DescriptionMetrics(
        total_descriptions=total,
        successful_descriptions=completed,
        failed_descriptions=failed,
        success_rate=round((completed / total) * 100, 2) if total > 0 else 0,
        avg_processing_time_seconds=round(random.uniform(0.5, 3.0), 2),
        avg_token_count=random.randint(100, 500),
        total_cost_usd=total_cost,
        by_provider=provider_metrics,
    )

    # Generate hourly trend
    hourly_trend = []
    for i in range(24):
        hourly_trend.append(
            {
                "hour": i,
                "jobs": random.randint(20, 200),
                "success_rate": round(random.uniform(90.0, 99.5), 1),
            }
        )

    return DescriptionAnalyticsResponse(
        time_range=time_range,
        metrics=metrics,
        hourly_trend=hourly_trend,
    )


@router.get(
    "/assets",
    response_model=AssetAnalyticsResponse,
    summary="Get Asset Processing Analytics",
    description="Get metrics for asset processing pipeline.",
)
async def get_asset_analytics(
    time_range: TimeRange = Query(
        default=TimeRange.HOURS_24,
        description="Time range for analytics",
    ),
    current_user: TokenPayload = Depends(_require_analytics_admin),
) -> AssetAnalyticsResponse:
    """
    Get asset processing pipeline analytics.

    Includes storage and processing metrics.
    """
    import random

    total = random.randint(500, 5000)
    completed = int(total * random.uniform(0.92, 0.99))
    failed = total - completed

    metrics = AssetMetrics(
        total_assets_processed=total,
        successful_processing=completed,
        failed_processing=failed,
        success_rate=round((completed / total) * 100, 2) if total > 0 else 0,
        avg_processing_time_seconds=round(random.uniform(0.1, 2.0), 2),
        total_storage_bytes=random.randint(100_000_000, 10_000_000_000),
        total_cost_usd=Decimal(str(round(total * 0.001, 2))),
    )

    return AssetAnalyticsResponse(
        time_range=time_range,
        metrics=metrics,
    )


@router.get(
    "/providers",
    response_model=ProviderAnalyticsResponse,
    summary="Get Provider Analytics",
    description="Get metrics broken down by ML provider.",
)
async def get_provider_analytics(
    time_range: TimeRange = Query(
        default=TimeRange.HOURS_24,
        description="Time range for analytics",
    ),
    current_user: TokenPayload = Depends(_require_analytics_admin),
) -> ProviderAnalyticsResponse:
    """
    Get provider-level analytics.

    Shows cost and performance metrics per provider.
    """
    providers = [
        generate_mock_provider_metrics(p, time_range)
        for p in [
            MLProvider.TRIPO,
            MLProvider.REPLICATE,
            MLProvider.GEMINI,
            MLProvider.HUGGINGFACE,
        ]
    ]

    total_cost = sum(p.total_cost_usd for p in providers)

    return ProviderAnalyticsResponse(
        time_range=time_range,
        providers=providers,
        total_cost_usd=total_cost,
    )
