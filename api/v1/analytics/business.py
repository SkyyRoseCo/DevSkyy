"""Business Metrics API Endpoints for SkyyRose Admin Dashboard.

This module provides endpoints for:
- Revenue, orders, and AOV overview
- Sales timeseries with breakdown
- Product performance metrics
- Collection-level metrics (Black Rose, Love Hurts, Signature)
- Conversion funnel analytics

Version: 1.0.0
"""

import logging
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.analytics.event_store import read_summary
from api.v1.analytics.ingest import get_analytics_settings, require_analytics_reporter
from database.db import Order, OrderItem, Product, get_db
from security.jwt_oauth2_auth import TokenPayload, get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analytics/business", tags=["Business Analytics"])


# =============================================================================
# Enums
# =============================================================================


class TimeGranularity(StrEnum):
    """Time granularity for timeseries data."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ComparisonPeriod(StrEnum):
    """Period for comparison metrics."""

    PREVIOUS = "previous"  # vs previous period
    YEAR_OVER_YEAR = "yoy"  # vs same period last year


# =============================================================================
# Request/Response Models
# =============================================================================


class MetricValue(BaseModel):
    """A metric with current value and optional comparison."""

    value: float
    previous_value: float | None = None
    change_pct: float | None = None
    trend: Literal["up", "down", "flat"] | None = None


class BusinessOverview(BaseModel):
    """Business overview metrics."""

    total_revenue: MetricValue
    order_count: MetricValue
    average_order_value: MetricValue
    unique_customers: MetricValue
    period_start: str
    period_end: str
    comparison_period: str | None = None


class BusinessOverviewResponse(BaseModel):
    """Response model for business overview."""

    status: str
    timestamp: str
    period_days: int
    overview: BusinessOverview


class TimeseriesDataPoint(BaseModel):
    """A single data point in a timeseries."""

    timestamp: str
    value: float
    breakdown: dict[str, float] | None = None


class SalesBreakdown(BaseModel):
    """Sales breakdown by category."""

    by_category: dict[str, float]
    by_collection: dict[str, float]
    by_payment_method: dict[str, float] | None = None


class SalesTimeseriesResponse(BaseModel):
    """Response model for sales timeseries."""

    status: str
    timestamp: str
    granularity: str
    period_start: str
    period_end: str
    total_revenue: float
    data_points: list[TimeseriesDataPoint]
    breakdown: SalesBreakdown
    comparison: list[TimeseriesDataPoint] | None = None


class ProductPerformance(BaseModel):
    """Product performance metrics."""

    product_id: str
    sku: str
    name: str
    collection: str | None
    views: int | None
    add_to_cart: int | None
    purchases: int
    revenue: float
    conversion_rate: float | None
    inventory_count: int
    inventory_status: Literal["in_stock", "low_stock", "out_of_stock"]
    sales_source: Literal["operational_order_database"] = "operational_order_database"
    engagement_source: Literal["unavailable"] = "unavailable"


class ProductPerformanceResponse(BaseModel):
    """Response model for product performance."""

    status: str
    timestamp: str
    period_days: int
    total_products: int
    products: list[ProductPerformance]
    top_performers: list[str]
    needs_attention: list[str]


class CollectionMetrics(BaseModel):
    """Metrics for a single collection."""

    collection_name: str
    product_count: int
    total_revenue: float
    order_count: int
    avg_order_value: float
    top_products: list[str]
    revenue_share_pct: float


class CollectionMetricsResponse(BaseModel):
    """Response model for collection metrics."""

    status: str
    timestamp: str
    period_days: int
    collections: list[CollectionMetrics]
    total_revenue: float


class FunnelStage(BaseModel):
    """A stage in the conversion funnel."""

    stage: str
    count: int | None
    value: float | None = None
    conversion_rate: float | None = None
    drop_off_rate: float | None = None


class ConversionFunnelResponse(BaseModel):
    """Response model for conversion funnel."""

    status: str
    timestamp: str
    period_days: int
    stages: list[FunnelStage]
    overall_conversion_rate: float | None
    comparison: dict[str, Any] | None = None
    coverage: dict[str, Any] | None = None
    commerce: dict[str, Any] | None = None


# =============================================================================
# Helper Functions
# =============================================================================


def calculate_change(current: float, previous: float) -> tuple[float, str]:
    """Calculate percentage change and trend."""
    if previous == 0:
        return (100.0 if current > 0 else 0.0, "up" if current > 0 else "flat")

    change_pct = ((current - previous) / previous) * 100
    if change_pct > 1:
        trend = "up"
    elif change_pct < -1:
        trend = "down"
    else:
        trend = "flat"

    return (round(change_pct, 2), trend)


async def get_period_metrics(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
) -> dict[str, Any]:
    """Get business metrics for a specific period."""
    query = select(
        func.count(Order.id).label("order_count"),
        func.sum(Order.total).label("total_revenue"),
        func.avg(Order.total).label("avg_order_value"),
        func.count(func.distinct(Order.user_id)).label("unique_customers"),
    ).where(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.status != "cancelled",
    )

    result = await db.execute(query)
    row = result.one()

    return {
        "order_count": row.order_count or 0,
        "total_revenue": float(row.total_revenue or 0),
        "avg_order_value": float(row.avg_order_value or 0),
        "unique_customers": row.unique_customers or 0,
    }


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/overview",
    response_model=BusinessOverviewResponse,
    status_code=status.HTTP_200_OK,
)
async def get_business_overview(
    period_days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    comparison: ComparisonPeriod | None = Query(default=None, description="Comparison period"),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessOverviewResponse:
    """Get business overview metrics.

    Returns revenue, orders, AOV, and unique customers for the specified period.
    Optionally includes comparison with previous period or same period last year.

    Args:
        period_days: Number of days to analyze (1-365)
        comparison: Optional comparison period (previous, yoy)
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        BusinessOverviewResponse with key business metrics
    """
    logger.info(f"Getting business overview for user {user.sub}: {period_days} days")

    try:
        now = datetime.now(UTC)
        period_end = now
        period_start = now - timedelta(days=period_days)

        # Get current period metrics
        current_metrics = await get_period_metrics(db, period_start, period_end)

        # Get comparison metrics if requested
        comparison_metrics = None
        comparison_period_str = None

        if comparison == ComparisonPeriod.PREVIOUS:
            comp_end = period_start
            comp_start = comp_end - timedelta(days=period_days)
            comparison_metrics = await get_period_metrics(db, comp_start, comp_end)
            comparison_period_str = f"{comp_start.date()} to {comp_end.date()}"
        elif comparison == ComparisonPeriod.YEAR_OVER_YEAR:
            comp_end = period_end - timedelta(days=365)
            comp_start = period_start - timedelta(days=365)
            comparison_metrics = await get_period_metrics(db, comp_start, comp_end)
            comparison_period_str = f"{comp_start.date()} to {comp_end.date()} (YoY)"

        # Build metric values with comparisons
        def build_metric(current: float, previous: float | None) -> MetricValue:
            if previous is not None:
                change_pct, trend = calculate_change(current, previous)
                return MetricValue(
                    value=current,
                    previous_value=previous,
                    change_pct=change_pct,
                    trend=trend,
                )
            return MetricValue(value=current)

        overview = BusinessOverview(
            total_revenue=build_metric(
                current_metrics["total_revenue"],
                comparison_metrics["total_revenue"] if comparison_metrics else None,
            ),
            order_count=build_metric(
                current_metrics["order_count"],
                comparison_metrics["order_count"] if comparison_metrics else None,
            ),
            average_order_value=build_metric(
                current_metrics["avg_order_value"],
                comparison_metrics["avg_order_value"] if comparison_metrics else None,
            ),
            unique_customers=build_metric(
                current_metrics["unique_customers"],
                comparison_metrics["unique_customers"] if comparison_metrics else None,
            ),
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            comparison_period=comparison_period_str,
        )

        return BusinessOverviewResponse(
            status="success",
            timestamp=now.isoformat(),
            period_days=period_days,
            overview=overview,
        )

    except Exception as e:
        logger.error(f"Failed to get business overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business overview: {str(e)}",
        )


@router.get(
    "/sales",
    response_model=SalesTimeseriesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_sales_timeseries(
    period_days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    granularity: TimeGranularity = Query(
        default=TimeGranularity.DAILY, description="Time granularity"
    ),
    comparison: ComparisonPeriod | None = Query(default=None, description="Comparison period"),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SalesTimeseriesResponse:
    """Get sales timeseries with breakdown.

    Returns sales data over time with breakdowns by category and collection.

    Args:
        period_days: Number of days to analyze (1-365)
        granularity: Time granularity (hourly, daily, weekly, monthly)
        comparison: Optional comparison period
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        SalesTimeseriesResponse with timeseries data and breakdowns
    """
    logger.info(f"Getting sales timeseries for user {user.sub}: {period_days} days, {granularity}")

    try:
        now = datetime.now(UTC)
        period_end = now
        period_start = now - timedelta(days=period_days)

        # Get orders in period
        orders_query = (
            select(Order)
            .where(
                Order.created_at >= period_start,
                Order.created_at < period_end,
                Order.status != "cancelled",
            )
            .order_by(Order.created_at)
        )
        result = await db.execute(orders_query)
        orders = result.scalars().all()

        # Build timeseries data points
        data_points: list[TimeseriesDataPoint] = []

        if granularity == TimeGranularity.DAILY:
            # Group by day
            daily_totals: dict[str, float] = {}
            for order in orders:
                day_key = order.created_at.strftime("%Y-%m-%d")
                daily_totals[day_key] = daily_totals.get(day_key, 0) + order.total

            current = period_start
            while current < period_end:
                day_key = current.strftime("%Y-%m-%d")
                data_points.append(
                    TimeseriesDataPoint(
                        timestamp=day_key,
                        value=daily_totals.get(day_key, 0),
                    )
                )
                current += timedelta(days=1)

        # Get breakdown by category and collection
        breakdown_query = (
            select(
                Product.category,
                Product.collection,
                func.sum(OrderItem.total).label("revenue"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                Order.created_at >= period_start,
                Order.created_at < period_end,
                Order.status != "cancelled",
            )
            .group_by(Product.category, Product.collection)
        )

        breakdown_result = await db.execute(breakdown_query)
        breakdown_rows = breakdown_result.all()

        by_category: dict[str, float] = {}
        by_collection: dict[str, float] = {}

        for row in breakdown_rows:
            category = row.category or "Uncategorized"
            collection = row.collection or "No Collection"
            revenue = float(row.revenue or 0)

            by_category[category] = by_category.get(category, 0) + revenue
            by_collection[collection] = by_collection.get(collection, 0) + revenue

        total_revenue = sum(order.total for order in orders)

        return SalesTimeseriesResponse(
            status="success",
            timestamp=now.isoformat(),
            granularity=granularity.value,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            total_revenue=total_revenue,
            data_points=data_points,
            breakdown=SalesBreakdown(
                by_category=by_category,
                by_collection=by_collection,
            ),
            comparison=None,
        )

    except Exception as e:
        logger.error(f"Failed to get sales timeseries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sales timeseries: {str(e)}",
        )


@router.get(
    "/products",
    response_model=ProductPerformanceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_product_performance(
    period_days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum products to return"),
    sort_by: Literal["revenue", "orders", "conversion"] = Query(
        default="revenue", description="Sort field"
    ),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductPerformanceResponse:
    """Get product performance metrics.

    Returns product-level metrics including views, conversions, revenue, and inventory.

    Args:
        period_days: Number of days to analyze (1-365)
        limit: Maximum number of products to return
        sort_by: Field to sort by (revenue, orders, conversion)
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        ProductPerformanceResponse with product performance data
    """
    logger.info(f"Getting product performance for user {user.sub}: {period_days} days")

    try:
        now = datetime.now(UTC)
        period_start = now - timedelta(days=period_days)

        # Get product sales data with period filtering
        product_sales_query = (
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.collection,
                Product.quantity,
                func.count(func.distinct(Order.id)).label("order_count"),
                func.sum(case((Order.id.is_not(None), OrderItem.quantity), else_=0)).label(
                    "units_sold"
                ),
                func.sum(case((Order.id.is_not(None), OrderItem.total), else_=0)).label("revenue"),
            )
            .outerjoin(OrderItem, OrderItem.product_id == Product.id)
            .outerjoin(
                Order,
                (Order.id == OrderItem.order_id)
                & (Order.created_at >= period_start)
                & (Order.created_at <= now)
                & (Order.status != "cancelled"),
            )
            .where(Product.is_active == True)  # noqa: E712
            .group_by(Product.id, Product.sku, Product.name, Product.collection, Product.quantity)
        )

        result = await db.execute(product_sales_query)
        product_rows = result.all()

        products: list[ProductPerformance] = []
        top_performers: list[str] = []
        needs_attention: list[str] = []

        LOW_STOCK_THRESHOLD = 10

        for row in product_rows:
            # Sales records do not measure browsing, carts, or a conversion denominator.
            views = None
            add_to_cart = None
            purchases = row.order_count or 0
            revenue = float(row.revenue or 0)

            conversion_rate = None

            # Determine inventory status
            if row.quantity == 0:
                inventory_status = "out_of_stock"
            elif row.quantity <= LOW_STOCK_THRESHOLD:
                inventory_status = "low_stock"
            else:
                inventory_status = "in_stock"

            product = ProductPerformance(
                product_id=row.id,
                sku=row.sku,
                name=row.name,
                collection=row.collection,
                views=views,
                add_to_cart=add_to_cart,
                purchases=purchases,
                revenue=revenue,
                conversion_rate=conversion_rate,
                inventory_count=row.quantity,
                inventory_status=inventory_status,
            )
            products.append(product)

            # Track top performers and products needing attention
            if revenue > 0:
                top_performers.append(row.sku)
            if inventory_status in ("out_of_stock", "low_stock"):
                needs_attention.append(row.sku)

        # Sort products
        if sort_by == "revenue":
            products.sort(key=lambda p: p.revenue, reverse=True)
        elif sort_by == "orders":
            products.sort(key=lambda p: p.purchases, reverse=True)
        elif sort_by == "conversion":
            products.sort(key=lambda p: p.conversion_rate or 0, reverse=True)

        # Apply limit
        products = products[:limit]
        top_performers = top_performers[:10]

        return ProductPerformanceResponse(
            status="success",
            timestamp=now.isoformat(),
            period_days=period_days,
            total_products=len(products),
            products=products,
            top_performers=top_performers,
            needs_attention=needs_attention[:10],
        )

    except Exception as e:
        logger.error(f"Failed to get product performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product performance: {str(e)}",
        )


@router.get(
    "/collections",
    response_model=CollectionMetricsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_collection_metrics(
    period_days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CollectionMetricsResponse:
    """Get collection-level metrics.

    Returns metrics for each SkyyRose collection (Black Rose, Love Hurts, Signature, etc.).

    Args:
        period_days: Number of days to analyze (1-365)
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        CollectionMetricsResponse with per-collection metrics
    """
    logger.info(f"Getting collection metrics for user {user.sub}: {period_days} days")

    try:
        now = datetime.now(UTC)
        period_start = now - timedelta(days=period_days)

        # Get collection-level metrics with period filtering
        collection_query = (
            select(
                Product.collection,
                func.count(func.distinct(Product.id)).label("product_count"),
                func.sum(OrderItem.total).label("revenue"),
                func.count(func.distinct(Order.id)).label("order_count"),
            )
            .outerjoin(OrderItem, OrderItem.product_id == Product.id)
            .outerjoin(
                Order,
                (Order.id == OrderItem.order_id)
                & (Order.created_at >= period_start)
                & (Order.status != "cancelled"),
            )
            .where(
                Product.is_active == True,  # noqa: E712
            )
            .group_by(Product.collection)
        )

        result = await db.execute(collection_query)
        collection_rows = result.all()

        collections: list[CollectionMetrics] = []
        total_revenue = 0.0

        # First pass: calculate total revenue
        for row in collection_rows:
            total_revenue += float(row.revenue or 0)

        # Second pass: build collection metrics
        for row in collection_rows:
            collection_name = row.collection or "Uncategorized"
            revenue = float(row.revenue or 0)
            order_count = row.order_count or 0

            # Calculate AOV for collection
            avg_order_value = revenue / order_count if order_count > 0 else 0.0

            # Calculate revenue share
            revenue_share = (revenue / total_revenue * 100) if total_revenue > 0 else 0.0

            # Get top products for this collection
            top_products_query = (
                select(Product.sku)
                .join(OrderItem, OrderItem.product_id == Product.id)
                .where(Product.collection == row.collection)
                .group_by(Product.sku)
                .order_by(func.sum(OrderItem.total).desc())
                .limit(3)
            )
            top_products_result = await db.execute(top_products_query)
            top_products = [r[0] for r in top_products_result.all()]

            collection_metrics = CollectionMetrics(
                collection_name=collection_name,
                product_count=row.product_count or 0,
                total_revenue=revenue,
                order_count=order_count,
                avg_order_value=round(avg_order_value, 2),
                top_products=top_products,
                revenue_share_pct=round(revenue_share, 2),
            )
            collections.append(collection_metrics)

        # Sort by revenue (highest first)
        collections.sort(key=lambda c: c.total_revenue, reverse=True)

        return CollectionMetricsResponse(
            status="success",
            timestamp=now.isoformat(),
            period_days=period_days,
            collections=collections,
            total_revenue=total_revenue,
        )

    except Exception as e:
        logger.error(f"Failed to get collection metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection metrics: {str(e)}",
        )


@router.get(
    "/funnel",
    response_model=ConversionFunnelResponse,
    status_code=status.HTTP_200_OK,
)
async def get_conversion_funnel(
    period_days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    comparison: ComparisonPeriod | None = Query(default=None, description="Comparison period"),
    user: TokenPayload = Depends(require_analytics_reporter),
    db: AsyncSession = Depends(get_db),
) -> ConversionFunnelResponse:
    """Get conversion funnel analytics.

    Returns funnel stages: traffic -> product views -> add to cart -> checkout -> complete.

    Args:
        period_days: Number of days to analyze (1-365)
        comparison: Optional comparison period
        user: Authenticated user (from JWT token)
        db: Database session

    Returns:
        ConversionFunnelResponse with funnel stage metrics
    """
    logger.info(f"Getting conversion funnel for user {user.sub}: {period_days} days")

    now = datetime.now(UTC)
    try:
        settings = get_analytics_settings()
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        return ConversionFunnelResponse(
            status="unavailable",
            timestamp=now.isoformat(),
            period_days=period_days,
            stages=[
                FunnelStage(stage=name, count=None)
                for name in (
                    "traffic",
                    "product_views",
                    "add_to_cart",
                    "checkout_started",
                    "purchase_complete",
                )
            ],
            overall_conversion_rate=None,
            coverage={"status": "unavailable", "missing": ["configured_storefront_analytics"]},
            commerce={"verified_purchases": None, "verified_revenue": None, "currency": None},
        )
    summary = await read_summary(
        db,
        settings.site_id,
        settings.environment,
        now - timedelta(days=period_days),
        now,
        period_days,
    )
    metrics = summary["metrics"]
    # Stage counts are independently observed events. They cannot prove that the
    # same sessions progressed in order, so conversion and drop-off remain unknown.
    names = {
        "traffic": "sessions",
        "product_views": "product_views",
        "add_to_cart": "add_to_cart",
        "checkout_started": "checkout_started",
        "purchase_complete": "consented_purchases",
    }
    return ConversionFunnelResponse(
        status=summary["coverage"]["status"],
        timestamp=now.isoformat(),
        period_days=period_days,
        stages=[FunnelStage(stage=name, count=metrics[key]) for name, key in names.items()],
        overall_conversion_rate=None,
        comparison=None,
        coverage=summary["coverage"],
        commerce={
            key: metrics[key] for key in ("verified_purchases", "verified_revenue", "currency")
        },
    )
