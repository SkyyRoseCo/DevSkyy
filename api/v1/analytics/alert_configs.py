"""Alert Configuration API Endpoints for Admin Dashboard.

This module provides CRUD endpoints for alert configurations:
- GET /analytics/alert-configs - List alert configs with pagination/filtering
- POST /analytics/alert-configs - Create new alert config
- GET /analytics/alert-configs/{id} - Get single alert config
- PUT /analytics/alert-configs/{id} - Update alert config
- DELETE /analytics/alert-configs/{id} - Delete alert config

Version: 1.0.0
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from security import RoleChecker, TokenPayload, UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Create router
# Real FastAPI dependency (security.require_roles is a decorator: wrapping it in
# Depends() made FastAPI treat its `func` parameter as a query param, so
# `?func=x` skipped authentication entirely).
_require_analytics_admin = RoleChecker([UserRole.ADMIN, UserRole.SUPER_ADMIN])

router = APIRouter(prefix="/analytics/alert-configs", tags=["Alert Configuration"])


# =============================================================================
# Enums
# =============================================================================


class ConditionType(StrEnum):
    """Alert condition types."""

    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    RATE = "rate"


class ConditionOperator(StrEnum):
    """Condition comparison operators."""

    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"


class SeverityLevel(StrEnum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class NotificationChannel(StrEnum):
    """Notification channel types."""

    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    IN_APP = "in_app"


# =============================================================================
# Request/Response Models
# =============================================================================


class AlertConfigBase(BaseModel):
    """Base model for alert configuration."""

    name: str = Field(..., min_length=1, max_length=255, description="Alert config name")
    description: str | None = Field(None, max_length=2000, description="Alert description")
    metric_name: str = Field(..., min_length=1, max_length=255, description="Metric to monitor")
    condition_type: ConditionType = Field(
        default=ConditionType.THRESHOLD, description="Type of condition"
    )
    condition_operator: ConditionOperator = Field(
        default=ConditionOperator.GT, description="Comparison operator"
    )
    threshold_value: Decimal | None = Field(None, description="Threshold value for comparison")
    threshold_unit: str | None = Field(None, max_length=50, description="Unit for threshold")
    window_duration_seconds: int = Field(
        default=300, ge=60, le=86400, description="Evaluation window (60-86400 seconds)"
    )
    evaluation_interval_seconds: int = Field(
        default=60, ge=10, le=3600, description="Evaluation interval (10-3600 seconds)"
    )
    cooldown_seconds: int = Field(
        default=300, ge=60, le=86400, description="Cooldown between alerts (60-86400 seconds)"
    )
    severity: SeverityLevel = Field(default=SeverityLevel.WARNING, description="Alert severity")
    is_enabled: bool = Field(default=True, description="Whether alert is active")
    notification_channels: list[str] = Field(
        default_factory=list, description="Notification channels"
    )
    notification_config: dict[str, Any] = Field(
        default_factory=dict, description="Channel-specific notification config"
    )
    filters: dict[str, Any] = Field(default_factory=dict, description="Additional filters")


class AlertConfigCreate(AlertConfigBase):
    """Request model for creating an alert config."""

    pass


class AlertConfigUpdate(BaseModel):
    """Request model for updating an alert config."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    metric_name: str | None = Field(None, min_length=1, max_length=255)
    condition_type: ConditionType | None = None
    condition_operator: ConditionOperator | None = None
    threshold_value: Decimal | None = None
    threshold_unit: str | None = Field(None, max_length=50)
    window_duration_seconds: int | None = Field(None, ge=60, le=86400)
    evaluation_interval_seconds: int | None = Field(None, ge=10, le=3600)
    cooldown_seconds: int | None = Field(None, ge=60, le=86400)
    severity: SeverityLevel | None = None
    is_enabled: bool | None = None
    notification_channels: list[str] | None = None
    notification_config: dict[str, Any] | None = None
    filters: dict[str, Any] | None = None


class AlertConfigResponse(BaseModel):
    """Response model for a single alert config."""

    id: str
    name: str
    description: str | None
    metric_name: str
    condition_type: ConditionType
    condition_operator: ConditionOperator
    threshold_value: Decimal | None
    threshold_unit: str | None
    window_duration_seconds: int
    evaluation_interval_seconds: int
    cooldown_seconds: int
    severity: SeverityLevel
    is_enabled: bool
    notification_channels: list[str]
    notification_config: dict[str, Any]
    filters: dict[str, Any]
    created_by: str | None
    updated_by: str | None
    created_at: str
    updated_at: str


class AlertConfigListResponse(BaseModel):
    """Response model for alert config list."""

    status: str
    timestamp: str
    total: int
    page: int
    page_size: int
    configs: list[AlertConfigResponse]


class AlertConfigCreateResponse(BaseModel):
    """Response model for create operation."""

    status: str
    message: str
    config: AlertConfigResponse


class AlertConfigUpdateResponse(BaseModel):
    """Response model for update operation."""

    status: str
    message: str
    config: AlertConfigResponse


class AlertConfigDeleteResponse(BaseModel):
    """Response model for delete operation."""

    status: str
    message: str
    deleted_id: str


# =============================================================================
# Helper Functions
# =============================================================================


def parse_notification_channels(channels: Any) -> list[str]:
    """Parse notification channels from database format."""
    if channels is None:
        return []
    if isinstance(channels, list):
        return [str(c) for c in channels]
    return []


def parse_json_field(data: Any) -> dict[str, Any]:
    """Parse JSON field safely."""
    if data is None:
        return {}
    if isinstance(data, dict):
        return data
    return {}


def row_to_response(row: Any) -> AlertConfigResponse:
    """Convert database row to response model."""
    return AlertConfigResponse(
        id=str(row.id),
        name=row.name,
        description=row.description,
        metric_name=row.metric_name,
        condition_type=ConditionType(row.condition_type),
        condition_operator=ConditionOperator(row.condition_operator),
        threshold_value=row.threshold_value,
        threshold_unit=row.threshold_unit,
        window_duration_seconds=row.window_duration_seconds or 300,
        evaluation_interval_seconds=row.evaluation_interval_seconds or 60,
        cooldown_seconds=row.cooldown_seconds or 300,
        severity=SeverityLevel(row.severity) if row.severity else SeverityLevel.WARNING,
        is_enabled=row.is_enabled if row.is_enabled is not None else True,
        notification_channels=parse_notification_channels(row.notification_channels),
        notification_config=parse_json_field(row.notification_config),
        filters=parse_json_field(row.filters),
        created_by=str(row.created_by) if row.created_by else None,
        updated_by=str(row.updated_by) if row.updated_by else None,
        created_at=row.created_at.isoformat() if row.created_at else "",
        updated_at=row.updated_at.isoformat() if row.updated_at else "",
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "",
    response_model=AlertConfigListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Alert Configs",
    description="Get paginated list of alert configurations with optional filters.",
)
async def list_alert_configs(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=200, description="Items per page"),
    severity: SeverityLevel | None = Query(default=None, description="Filter by severity"),
    is_enabled: bool | None = Query(default=None, description="Filter by enabled status"),
    metric_name: str | None = Query(default=None, description="Filter by metric name"),
    search: str | None = Query(default=None, max_length=100, description="Search by name"),
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AlertConfigListResponse:
    """List alert configurations with pagination and filters.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        severity: Filter by severity level
        is_enabled: Filter by enabled status
        metric_name: Filter by metric name
        search: Search by config name
        user: Authenticated user
        db: Database session

    Returns:
        AlertConfigListResponse with paginated configs
    """
    logger.info(f"Listing alert configs for user {user.sub}: page={page}")

    try:
        conditions = []
        params: dict[str, Any] = {}

        if severity:
            conditions.append("severity = :severity")
            params["severity"] = severity.value

        if is_enabled is not None:
            conditions.append("is_enabled = :is_enabled")
            params["is_enabled"] = is_enabled

        if metric_name:
            conditions.append("metric_name = :metric_name")
            params["metric_name"] = metric_name

        if search:
            conditions.append("name ILIKE :search")
            params["search"] = f"%{search}%"

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Count total
        count_query = text(
            f"""  # nosec B608 — parameterized SQLAlchemy text(); conditions are static literals, user values in params dict
            SELECT COUNT(*) FROM alert_configs
            WHERE {where_clause}
        """
        )
        count_result = await db.execute(count_query, params)
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        data_query = text(
            f"""  # nosec B608 — parameterized SQLAlchemy text(); conditions are static literals, user values in params dict
            SELECT
                id, name, description, metric_name,
                condition_type, condition_operator,
                threshold_value, threshold_unit,
                window_duration_seconds, evaluation_interval_seconds,
                cooldown_seconds, severity, is_enabled,
                notification_channels, notification_config, filters,
                created_by, updated_by, created_at, updated_at
            FROM alert_configs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """
        )

        result = await db.execute(data_query, params)
        rows = result.fetchall()

        configs = [row_to_response(row) for row in rows]

        return AlertConfigListResponse(
            status="success",
            timestamp=datetime.now(UTC).isoformat(),
            total=total,
            page=page,
            page_size=page_size,
            configs=configs,
        )

    except Exception as e:
        logger.error(f"Failed to list alert configs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list alert configs: {str(e)}",
        )


@router.post(
    "",
    response_model=AlertConfigCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Alert Config",
    description="Create a new alert configuration.",
)
async def create_alert_config(
    request: AlertConfigCreate,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AlertConfigCreateResponse:
    """Create a new alert configuration.

    Args:
        request: Alert config data
        user: Authenticated admin user
        db: Database session

    Returns:
        AlertConfigCreateResponse with created config
    """
    logger.info(f"Creating alert config '{request.name}' by user {user.sub}")

    try:
        config_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        # Convert notification_channels list to PostgreSQL array format
        channels_array = (
            "{" + ",".join(request.notification_channels) + "}"
            if request.notification_channels
            else "{}"
        )

        insert_query = text("""
            INSERT INTO alert_configs (
                id, name, description, metric_name,
                condition_type, condition_operator,
                threshold_value, threshold_unit,
                window_duration_seconds, evaluation_interval_seconds,
                cooldown_seconds, severity, is_enabled,
                notification_channels, notification_config, filters,
                created_by, updated_by, created_at, updated_at
            ) VALUES (
                :id, :name, :description, :metric_name,
                :condition_type, :condition_operator,
                :threshold_value, :threshold_unit,
                :window_duration_seconds, :evaluation_interval_seconds,
                :cooldown_seconds, :severity, :is_enabled,
                :notification_channels, :notification_config::jsonb, :filters::jsonb,
                :created_by, :updated_by, :created_at, :updated_at
            )
            RETURNING *
        """)

        import json

        result = await db.execute(
            insert_query,
            {
                "id": config_id,
                "name": request.name,
                "description": request.description,
                "metric_name": request.metric_name,
                "condition_type": request.condition_type.value,
                "condition_operator": request.condition_operator.value,
                "threshold_value": request.threshold_value,
                "threshold_unit": request.threshold_unit,
                "window_duration_seconds": request.window_duration_seconds,
                "evaluation_interval_seconds": request.evaluation_interval_seconds,
                "cooldown_seconds": request.cooldown_seconds,
                "severity": request.severity.value,
                "is_enabled": request.is_enabled,
                "notification_channels": channels_array,
                "notification_config": json.dumps(request.notification_config),
                "filters": json.dumps(request.filters),
                "created_by": user.sub,
                "updated_by": user.sub,
                "created_at": now,
                "updated_at": now,
            },
        )
        await db.commit()

        row = result.fetchone()
        config = row_to_response(row)

        return AlertConfigCreateResponse(
            status="success",
            message=f"Alert config '{request.name}' created successfully",
            config=config,
        )

    except Exception as e:
        logger.error(f"Failed to create alert config: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert config: {str(e)}",
        )


@router.get(
    "/{config_id}",
    response_model=AlertConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Alert Config",
    description="Get a single alert configuration by ID.",
)
async def get_alert_config(
    config_id: str,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AlertConfigResponse:
    """Get a single alert configuration.

    Args:
        config_id: Alert config UUID
        user: Authenticated user
        db: Database session

    Returns:
        AlertConfigResponse

    Raises:
        404: Config not found
    """
    logger.info(f"Getting alert config {config_id} for user {user.sub}")

    try:
        query = text("""
            SELECT
                id, name, description, metric_name,
                condition_type, condition_operator,
                threshold_value, threshold_unit,
                window_duration_seconds, evaluation_interval_seconds,
                cooldown_seconds, severity, is_enabled,
                notification_channels, notification_config, filters,
                created_by, updated_by, created_at, updated_at
            FROM alert_configs
            WHERE id = :config_id
        """)

        result = await db.execute(query, {"config_id": config_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert config {config_id} not found",
            )

        return row_to_response(row)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get alert config {config_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alert config: {str(e)}",
        )


@router.put(
    "/{config_id}",
    response_model=AlertConfigUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Alert Config",
    description="Update an existing alert configuration.",
)
async def update_alert_config(
    config_id: str,
    request: AlertConfigUpdate,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AlertConfigUpdateResponse:
    """Update an alert configuration.

    Args:
        config_id: Alert config UUID
        request: Fields to update
        user: Authenticated admin user
        db: Database session

    Returns:
        AlertConfigUpdateResponse with updated config

    Raises:
        404: Config not found
    """
    logger.info(f"Updating alert config {config_id} by user {user.sub}")

    try:
        # Check if config exists
        check_query = text("SELECT id FROM alert_configs WHERE id = :config_id")
        result = await db.execute(check_query, {"config_id": config_id})
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert config {config_id} not found",
            )

        # Build update query dynamically
        updates = []
        params: dict[str, Any] = {"config_id": config_id, "updated_by": user.sub}

        if request.name is not None:
            updates.append("name = :name")
            params["name"] = request.name

        if request.description is not None:
            updates.append("description = :description")
            params["description"] = request.description

        if request.metric_name is not None:
            updates.append("metric_name = :metric_name")
            params["metric_name"] = request.metric_name

        if request.condition_type is not None:
            updates.append("condition_type = :condition_type")
            params["condition_type"] = request.condition_type.value

        if request.condition_operator is not None:
            updates.append("condition_operator = :condition_operator")
            params["condition_operator"] = request.condition_operator.value

        if request.threshold_value is not None:
            updates.append("threshold_value = :threshold_value")
            params["threshold_value"] = request.threshold_value

        if request.threshold_unit is not None:
            updates.append("threshold_unit = :threshold_unit")
            params["threshold_unit"] = request.threshold_unit

        if request.window_duration_seconds is not None:
            updates.append("window_duration_seconds = :window_duration_seconds")
            params["window_duration_seconds"] = request.window_duration_seconds

        if request.evaluation_interval_seconds is not None:
            updates.append("evaluation_interval_seconds = :evaluation_interval_seconds")
            params["evaluation_interval_seconds"] = request.evaluation_interval_seconds

        if request.cooldown_seconds is not None:
            updates.append("cooldown_seconds = :cooldown_seconds")
            params["cooldown_seconds"] = request.cooldown_seconds

        if request.severity is not None:
            updates.append("severity = :severity")
            params["severity"] = request.severity.value

        if request.is_enabled is not None:
            updates.append("is_enabled = :is_enabled")
            params["is_enabled"] = request.is_enabled

        if request.notification_channels is not None:
            channels_array = (
                "{" + ",".join(request.notification_channels) + "}"
                if request.notification_channels
                else "{}"
            )
            updates.append("notification_channels = :notification_channels")
            params["notification_channels"] = channels_array

        if request.notification_config is not None:
            import json

            updates.append("notification_config = :notification_config::jsonb")
            params["notification_config"] = json.dumps(request.notification_config)

        if request.filters is not None:
            import json

            updates.append("filters = :filters::jsonb")
            params["filters"] = json.dumps(request.filters)

        updates.append("updated_by = :updated_by")

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        update_clause = ", ".join(updates)
        update_query = text(
            f"""  # nosec B608 — parameterized SQLAlchemy text(); conditions are static literals, user values in params dict
            UPDATE alert_configs
            SET {update_clause}
            WHERE id = :config_id
            RETURNING *
        """
        )

        result = await db.execute(update_query, params)
        await db.commit()

        row = result.fetchone()
        config = row_to_response(row)

        return AlertConfigUpdateResponse(
            status="success",
            message=f"Alert config {config_id} updated successfully",
            config=config,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update alert config {config_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert config: {str(e)}",
        )


@router.delete(
    "/{config_id}",
    response_model=AlertConfigDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Alert Config",
    description="Delete an alert configuration.",
)
async def delete_alert_config(
    config_id: str,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AlertConfigDeleteResponse:
    """Delete an alert configuration.

    Args:
        config_id: Alert config UUID
        user: Authenticated admin user
        db: Database session

    Returns:
        AlertConfigDeleteResponse

    Raises:
        404: Config not found
    """
    logger.info(f"Deleting alert config {config_id} by user {user.sub}")

    try:
        # Check if config exists
        check_query = text("SELECT id, name FROM alert_configs WHERE id = :config_id")
        result = await db.execute(check_query, {"config_id": config_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert config {config_id} not found",
            )

        config_name = row.name

        # Delete the config (cascade will handle alert_history)
        delete_query = text("DELETE FROM alert_configs WHERE id = :config_id")
        await db.execute(delete_query, {"config_id": config_id})
        await db.commit()

        return AlertConfigDeleteResponse(
            status="success",
            message=f"Alert config '{config_name}' deleted successfully",
            deleted_id=config_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete alert config {config_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete alert config: {str(e)}",
        )
