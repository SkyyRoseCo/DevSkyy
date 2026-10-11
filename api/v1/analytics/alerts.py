"""Alert History and Acknowledgment API Endpoints for Admin Dashboard.

This module provides endpoints for:
- GET /analytics/alerts/history - List triggered alerts with filters
- GET /analytics/alerts/active - Currently active (unacknowledged) alerts
- POST /analytics/alerts/{id}/acknowledge - Acknowledge alert
- POST /analytics/alerts/{id}/resolve - Mark alert resolved
- POST /analytics/alerts/bulk-acknowledge - Bulk acknowledgment

Version: 1.0.0
"""

import json
import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

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

router = APIRouter(prefix="/analytics/alerts", tags=["Alert Management"])


# =============================================================================
# Enums
# =============================================================================


class AlertStatus(StrEnum):
    """Alert status enum."""

    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertSeverity(StrEnum):
    """Alert severity enum."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# =============================================================================
# Request/Response Models
# =============================================================================


class NotificationRecord(BaseModel):
    """Record of notification sent for an alert."""

    channel: str
    sent_at: str
    status: Literal["sent", "failed", "pending"]
    recipient: str | None = None
    error: str | None = None


class AlertMetadata(BaseModel):
    """Alert metadata including trigger details."""

    trigger_time: str
    metric_value: float | None = None
    threshold_value: float | None = None
    condition_type: str | None = None
    condition_operator: str | None = None
    window_duration_seconds: int | None = None
    notifications_sent: list[NotificationRecord] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class AlertHistoryItem(BaseModel):
    """Single alert history item."""

    id: str
    alert_config_id: str
    alert_name: str | None = None
    status: AlertStatus
    severity: AlertSeverity
    title: str
    message: str | None = None
    triggered_at: str
    resolved_at: str | None = None
    acknowledged_at: str | None = None
    acknowledged_by: str | None = None
    acknowledge_note: str | None = None
    metadata: AlertMetadata


class AlertHistoryResponse(BaseModel):
    """Response model for alert history list."""

    status: str
    timestamp: str
    total: int
    page: int
    page_size: int
    alerts: list[AlertHistoryItem]


class ActiveAlertsResponse(BaseModel):
    """Response model for active alerts."""

    status: str
    timestamp: str
    total: int
    critical_count: int
    warning_count: int
    info_count: int
    alerts: list[AlertHistoryItem]


class AcknowledgeRequest(BaseModel):
    """Request model for acknowledging an alert."""

    note: str | None = Field(None, max_length=1000, description="Optional acknowledgment note")


class AcknowledgeResponse(BaseModel):
    """Response model for acknowledge operation."""

    status: str
    alert_id: str
    acknowledged_at: str
    acknowledged_by: str
    note: str | None = None


class ResolveRequest(BaseModel):
    """Request model for resolving an alert."""

    resolution_note: str | None = Field(
        None, max_length=1000, description="Optional resolution note"
    )


class ResolveResponse(BaseModel):
    """Response model for resolve operation."""

    status: str
    alert_id: str
    resolved_at: str
    resolved_by: str
    note: str | None = None


class BulkAcknowledgeRequest(BaseModel):
    """Request model for bulk acknowledgment."""

    alert_ids: list[str] = Field(
        ..., min_length=1, max_length=100, description="Alert IDs to acknowledge"
    )
    note: str | None = Field(
        None, max_length=1000, description="Optional acknowledgment note for all alerts"
    )


class BulkAcknowledgeResult(BaseModel):
    """Result for a single alert in bulk operation."""

    alert_id: str
    success: bool
    error: str | None = None


class BulkAcknowledgeResponse(BaseModel):
    """Response model for bulk acknowledge operation."""

    status: str
    timestamp: str
    total_requested: int
    total_succeeded: int
    total_failed: int
    results: list[BulkAcknowledgeResult]


# =============================================================================
# Helper Functions
# =============================================================================


def parse_json_field(json_str: str | None) -> dict[str, Any] | list[Any]:
    """Parse JSON field safely."""
    if not json_str:
        return {}
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def build_alert_metadata(
    triggered_at: datetime,
    metric_value: float | None,
    threshold_value: float | None,
    notifications_sent_json: str | None,
    context_json: str | None,
    alert_config: Any | None = None,
) -> AlertMetadata:
    """Build alert metadata from database fields."""
    notifications = parse_json_field(notifications_sent_json)
    context = parse_json_field(context_json)

    notification_records = []
    if isinstance(notifications, list):
        for notif in notifications:
            if isinstance(notif, dict):
                notification_records.append(
                    NotificationRecord(
                        channel=notif.get("channel", "unknown"),
                        sent_at=notif.get("sent_at", ""),
                        status=notif.get("status", "pending"),
                        recipient=notif.get("recipient"),
                        error=notif.get("error"),
                    )
                )

    return AlertMetadata(
        trigger_time=triggered_at.isoformat() if triggered_at else "",
        metric_value=metric_value,
        threshold_value=threshold_value,
        condition_type=alert_config.condition_type if alert_config else None,
        condition_operator=alert_config.condition_operator if alert_config else None,
        window_duration_seconds=alert_config.window_duration_seconds if alert_config else None,
        notifications_sent=notification_records,
        context=context if isinstance(context, dict) else {},
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/history",
    response_model=AlertHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Alert History",
    description="Get paginated alert history with filters.",
)
async def get_alert_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=200, description="Items per page"),
    status_filter: AlertStatus | None = Query(default=None, description="Filter by status"),
    severity_filter: AlertSeverity | None = Query(default=None, description="Filter by severity"),
    alert_config_id: str | None = Query(default=None, description="Filter by alert config ID"),
    start_date: str | None = Query(default=None, description="Filter from date (ISO format)"),
    end_date: str | None = Query(default=None, description="Filter to date (ISO format)"),
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AlertHistoryResponse:
    """Get alert history with filters.

    Returns paginated list of triggered alerts with optional filtering
    by status, severity, alert config, and date range.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (1-200)
        status_filter: Filter by alert status (triggered, acknowledged, resolved)
        severity_filter: Filter by severity (info, warning, critical)
        alert_config_id: Filter by specific alert configuration
        start_date: Filter alerts triggered on or after this date (ISO format)
        end_date: Filter alerts triggered on or before this date (ISO format)
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        AlertHistoryResponse with paginated alert history
    """
    logger.info(f"Getting alert history for user {user.sub}: page={page}, page_size={page_size}")

    try:
        # Build base query
        conditions = []
        params: dict[str, Any] = {}

        if status_filter:
            conditions.append("ah.status = :status")
            params["status"] = status_filter.value

        if severity_filter:
            conditions.append("ah.severity = :severity")
            params["severity"] = severity_filter.value

        if alert_config_id:
            conditions.append("ah.alert_config_id = :alert_config_id")
            params["alert_config_id"] = alert_config_id

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                conditions.append("ah.triggered_at >= :start_date")
                params["start_date"] = start_dt
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid start_date format: {start_date}",
                )

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                conditions.append("ah.triggered_at <= :end_date")
                params["end_date"] = end_dt
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid end_date format: {end_date}",
                )

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Count total
        count_query = text(
            f"""  # nosec B608 — parameterized SQLAlchemy text(); conditions are static literals, user values in params dict
            SELECT COUNT(*) FROM alert_history ah
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
                ah.id,
                ah.alert_config_id,
                ah.status,
                ah.severity,
                ah.title,
                ah.message,
                ah.metric_value,
                ah.threshold_value,
                ah.context_json,
                ah.triggered_at,
                ah.resolved_at,
                ah.acknowledged_at,
                ah.acknowledged_by,
                ah.acknowledge_note,
                ah.notifications_sent_json,
                ac.name as alert_name,
                ac.condition_type,
                ac.condition_operator,
                ac.window_duration_seconds
            FROM alert_history ah
            LEFT JOIN alert_configs ac ON ah.alert_config_id = ac.id
            WHERE {where_clause}
            ORDER BY ah.triggered_at DESC
            LIMIT :limit OFFSET :offset
        """
        )

        result = await db.execute(data_query, params)
        rows = result.fetchall()

        alerts = []
        for row in rows:
            # Create a mock alert_config object for metadata building
            class MockConfig:
                condition_type = row.condition_type
                condition_operator = row.condition_operator
                window_duration_seconds = row.window_duration_seconds

            metadata = build_alert_metadata(
                triggered_at=row.triggered_at,
                metric_value=row.metric_value,
                threshold_value=row.threshold_value,
                notifications_sent_json=row.notifications_sent_json,
                context_json=row.context_json,
                alert_config=MockConfig(),
            )

            alert_item = AlertHistoryItem(
                id=str(row.id),
                alert_config_id=str(row.alert_config_id),
                alert_name=row.alert_name,
                status=AlertStatus(row.status),
                severity=AlertSeverity(row.severity),
                title=row.title,
                message=row.message,
                triggered_at=row.triggered_at.isoformat() if row.triggered_at else "",
                resolved_at=row.resolved_at.isoformat() if row.resolved_at else None,
                acknowledged_at=row.acknowledged_at.isoformat() if row.acknowledged_at else None,
                acknowledged_by=row.acknowledged_by,
                acknowledge_note=row.acknowledge_note,
                metadata=metadata,
            )
            alerts.append(alert_item)

        return AlertHistoryResponse(
            status="success",
            timestamp=datetime.now(UTC).isoformat(),
            total=total,
            page=page,
            page_size=page_size,
            alerts=alerts,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get alert history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alert history: {str(e)}",
        )


@router.get(
    "/active",
    response_model=ActiveAlertsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active Alerts",
    description="Get currently active (unacknowledged) alerts.",
)
async def get_active_alerts(
    severity_filter: AlertSeverity | None = Query(default=None, description="Filter by severity"),
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> ActiveAlertsResponse:
    """Get currently active (unacknowledged) alerts.

    Returns all alerts that are in 'triggered' status and have not been
    acknowledged. These require attention.

    Args:
        severity_filter: Optional filter by severity (info, warning, critical)
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        ActiveAlertsResponse with active alerts grouped by severity
    """
    logger.info(f"Getting active alerts for user {user.sub}")

    try:
        # Build query
        conditions = ["ah.status = 'triggered'"]
        params: dict[str, Any] = {}

        if severity_filter:
            conditions.append("ah.severity = :severity")
            params["severity"] = severity_filter.value

        where_clause = " AND ".join(conditions)

        # Get active alerts
        data_query = text(
            f"""  # nosec B608 — parameterized SQLAlchemy text(); conditions are static literals, user values in params dict
            SELECT
                ah.id,
                ah.alert_config_id,
                ah.status,
                ah.severity,
                ah.title,
                ah.message,
                ah.metric_value,
                ah.threshold_value,
                ah.context_json,
                ah.triggered_at,
                ah.resolved_at,
                ah.acknowledged_at,
                ah.acknowledged_by,
                ah.acknowledge_note,
                ah.notifications_sent_json,
                ac.name as alert_name,
                ac.condition_type,
                ac.condition_operator,
                ac.window_duration_seconds
            FROM alert_history ah
            LEFT JOIN alert_configs ac ON ah.alert_config_id = ac.id
            WHERE {where_clause}
            ORDER BY
                CASE ah.severity
                    WHEN 'critical' THEN 1
                    WHEN 'warning' THEN 2
                    WHEN 'info' THEN 3
                END,
                ah.triggered_at DESC
        """
        )

        result = await db.execute(data_query, params)
        rows = result.fetchall()

        alerts = []
        critical_count = 0
        warning_count = 0
        info_count = 0

        for row in rows:
            # Count by severity
            if row.severity == "critical":
                critical_count += 1
            elif row.severity == "warning":
                warning_count += 1
            else:
                info_count += 1

            # Create mock config for metadata
            class MockConfig:
                condition_type = row.condition_type
                condition_operator = row.condition_operator
                window_duration_seconds = row.window_duration_seconds

            metadata = build_alert_metadata(
                triggered_at=row.triggered_at,
                metric_value=row.metric_value,
                threshold_value=row.threshold_value,
                notifications_sent_json=row.notifications_sent_json,
                context_json=row.context_json,
                alert_config=MockConfig(),
            )

            alert_item = AlertHistoryItem(
                id=str(row.id),
                alert_config_id=str(row.alert_config_id),
                alert_name=row.alert_name,
                status=AlertStatus(row.status),
                severity=AlertSeverity(row.severity),
                title=row.title,
                message=row.message,
                triggered_at=row.triggered_at.isoformat() if row.triggered_at else "",
                resolved_at=row.resolved_at.isoformat() if row.resolved_at else None,
                acknowledged_at=row.acknowledged_at.isoformat() if row.acknowledged_at else None,
                acknowledged_by=row.acknowledged_by,
                acknowledge_note=row.acknowledge_note,
                metadata=metadata,
            )
            alerts.append(alert_item)

        return ActiveAlertsResponse(
            status="success",
            timestamp=datetime.now(UTC).isoformat(),
            total=len(alerts),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            alerts=alerts,
        )

    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active alerts: {str(e)}",
        )


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AcknowledgeResponse,
    status_code=status.HTTP_200_OK,
    summary="Acknowledge Alert",
    description="Acknowledge a triggered alert.",
)
async def acknowledge_alert(
    alert_id: str,
    request: AcknowledgeRequest,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> AcknowledgeResponse:
    """Acknowledge a triggered alert.

    Marks the alert as acknowledged, recording who acknowledged it and when.
    Only alerts in 'triggered' status can be acknowledged.

    Args:
        alert_id: The alert history ID to acknowledge
        request: Optional acknowledgment note
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        AcknowledgeResponse with acknowledgment details

    Raises:
        404: Alert not found
        400: Alert already acknowledged or resolved
    """
    logger.info(f"Acknowledging alert {alert_id} by user {user.sub}")

    try:
        # Check alert exists and is in triggered status
        check_query = text("""
            SELECT id, status FROM alert_history WHERE id = :alert_id
        """)
        result = await db.execute(check_query, {"alert_id": alert_id})
        alert_row = result.fetchone()

        if not alert_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found",
            )

        if alert_row.status == "acknowledged":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Alert {alert_id} is already acknowledged",
            )

        if alert_row.status == "resolved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Alert {alert_id} is already resolved",
            )

        # Update alert
        now = datetime.now(UTC)
        update_query = text("""
            UPDATE alert_history
            SET status = 'acknowledged',
                acknowledged_at = :acknowledged_at,
                acknowledged_by = :acknowledged_by,
                acknowledge_note = :acknowledge_note
            WHERE id = :alert_id
        """)

        await db.execute(
            update_query,
            {
                "alert_id": alert_id,
                "acknowledged_at": now,
                "acknowledged_by": user.sub,
                "acknowledge_note": request.note,
            },
        )
        await db.commit()

        return AcknowledgeResponse(
            status="success",
            alert_id=alert_id,
            acknowledged_at=now.isoformat(),
            acknowledged_by=user.sub,
            note=request.note,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}",
        )


@router.post(
    "/{alert_id}/resolve",
    response_model=ResolveResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve Alert",
    description="Mark an alert as resolved.",
)
async def resolve_alert(
    alert_id: str,
    request: ResolveRequest,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> ResolveResponse:
    """Resolve an alert.

    Marks the alert as resolved. Can resolve alerts in either
    'triggered' or 'acknowledged' status.

    Args:
        alert_id: The alert history ID to resolve
        request: Optional resolution note
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        ResolveResponse with resolution details

    Raises:
        404: Alert not found
        400: Alert already resolved
    """
    logger.info(f"Resolving alert {alert_id} by user {user.sub}")

    try:
        # Check alert exists and is not already resolved
        check_query = text("""
            SELECT id, status FROM alert_history WHERE id = :alert_id
        """)
        result = await db.execute(check_query, {"alert_id": alert_id})
        alert_row = result.fetchone()

        if not alert_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found",
            )

        if alert_row.status == "resolved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Alert {alert_id} is already resolved",
            )

        # Update alert
        now = datetime.now(UTC)

        # If resolving a triggered alert, also set acknowledged fields
        if alert_row.status == "triggered":
            update_query = text("""
                UPDATE alert_history
                SET status = 'resolved',
                    resolved_at = :resolved_at,
                    acknowledged_at = COALESCE(acknowledged_at, :acknowledged_at),
                    acknowledged_by = COALESCE(acknowledged_by, :acknowledged_by)
                WHERE id = :alert_id
            """)
            await db.execute(
                update_query,
                {
                    "alert_id": alert_id,
                    "resolved_at": now,
                    "acknowledged_at": now,
                    "acknowledged_by": user.sub,
                },
            )
        else:
            update_query = text("""
                UPDATE alert_history
                SET status = 'resolved',
                    resolved_at = :resolved_at
                WHERE id = :alert_id
            """)
            await db.execute(
                update_query,
                {
                    "alert_id": alert_id,
                    "resolved_at": now,
                },
            )

        await db.commit()

        return ResolveResponse(
            status="success",
            alert_id=alert_id,
            resolved_at=now.isoformat(),
            resolved_by=user.sub,
            note=request.resolution_note,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}",
        )


@router.post(
    "/bulk-acknowledge",
    response_model=BulkAcknowledgeResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk Acknowledge Alerts",
    description="Acknowledge multiple alerts at once.",
)
async def bulk_acknowledge_alerts(
    request: BulkAcknowledgeRequest,
    user: TokenPayload = Depends(_require_analytics_admin),
    db: AsyncSession = Depends(get_db),
) -> BulkAcknowledgeResponse:
    """Bulk acknowledge multiple alerts.

    Acknowledges multiple alerts in a single operation. Each alert is
    processed independently, so partial success is possible.

    Args:
        request: List of alert IDs to acknowledge and optional note
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        BulkAcknowledgeResponse with results for each alert
    """
    logger.info(f"Bulk acknowledging {len(request.alert_ids)} alerts by user {user.sub}")

    try:
        now = datetime.now(UTC)
        results: list[BulkAcknowledgeResult] = []
        succeeded = 0
        failed = 0

        for alert_id in request.alert_ids:
            try:
                # Check alert exists and status
                check_query = text("""
                    SELECT id, status FROM alert_history WHERE id = :alert_id
                """)
                result = await db.execute(check_query, {"alert_id": alert_id})
                alert_row = result.fetchone()

                if not alert_row:
                    results.append(
                        BulkAcknowledgeResult(
                            alert_id=alert_id,
                            success=False,
                            error="Alert not found",
                        )
                    )
                    failed += 1
                    continue

                if alert_row.status in ("acknowledged", "resolved"):
                    results.append(
                        BulkAcknowledgeResult(
                            alert_id=alert_id,
                            success=False,
                            error=f"Alert is already {alert_row.status}",
                        )
                    )
                    failed += 1
                    continue

                # Update alert
                update_query = text("""
                    UPDATE alert_history
                    SET status = 'acknowledged',
                        acknowledged_at = :acknowledged_at,
                        acknowledged_by = :acknowledged_by,
                        acknowledge_note = :acknowledge_note
                    WHERE id = :alert_id
                """)

                await db.execute(
                    update_query,
                    {
                        "alert_id": alert_id,
                        "acknowledged_at": now,
                        "acknowledged_by": user.sub,
                        "acknowledge_note": request.note,
                    },
                )

                results.append(
                    BulkAcknowledgeResult(
                        alert_id=alert_id,
                        success=True,
                    )
                )
                succeeded += 1

            except Exception as e:
                logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
                results.append(
                    BulkAcknowledgeResult(
                        alert_id=alert_id,
                        success=False,
                        error=str(e),
                    )
                )
                failed += 1

        await db.commit()

        return BulkAcknowledgeResponse(
            status="success" if failed == 0 else "partial",
            timestamp=now.isoformat(),
            total_requested=len(request.alert_ids),
            total_succeeded=succeeded,
            total_failed=failed,
            results=results,
        )

    except Exception as e:
        logger.error(f"Failed bulk acknowledge operation: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed bulk acknowledge operation: {str(e)}",
        )
