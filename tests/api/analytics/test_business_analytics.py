"""Tests for Business Analytics API endpoints.

Tests cover:
- GET /analytics/business/overview
- GET /analytics/business/sales
- GET /analytics/business/products
- GET /analytics/business/collections
- GET /analytics/business/funnel
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.v1.analytics.business import (
    BusinessOverview,
    ComparisonPeriod,
    FunnelStage,
    MetricValue,
    ProductPerformance,
    TimeGranularity,
    TimeseriesDataPoint,
    calculate_change,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_user() -> MagicMock:
    """Mock authenticated user."""
    user = MagicMock()
    user.sub = "test-user-123"
    return user


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session."""
    session = AsyncMock()
    return session


# =============================================================================
# Unit Tests - Helper Functions
# =============================================================================


class TestCalculateChange:
    """Tests for calculate_change helper function."""

    def test_positive_change(self) -> None:
        """Test positive percentage change."""
        change_pct, trend = calculate_change(120.0, 100.0)
        assert change_pct == 20.0
        assert trend == "up"

    def test_negative_change(self) -> None:
        """Test negative percentage change."""
        change_pct, trend = calculate_change(80.0, 100.0)
        assert change_pct == -20.0
        assert trend == "down"

    def test_flat_change(self) -> None:
        """Test flat/minimal change."""
        change_pct, trend = calculate_change(100.5, 100.0)
        assert change_pct == 0.5
        assert trend == "flat"

    def test_zero_previous(self) -> None:
        """Test when previous value is zero."""
        change_pct, trend = calculate_change(100.0, 0.0)
        assert change_pct == 100.0
        assert trend == "up"

    def test_zero_to_zero(self) -> None:
        """Test when both values are zero."""
        change_pct, trend = calculate_change(0.0, 0.0)
        assert change_pct == 0.0
        assert trend == "flat"


# =============================================================================
# Unit Tests - Pydantic Models
# =============================================================================


class TestMetricValue:
    """Tests for MetricValue model."""

    def test_minimal_metric(self) -> None:
        """Test metric with only required field."""
        metric = MetricValue(value=100.0)
        assert metric.value == 100.0
        assert metric.previous_value is None
        assert metric.change_pct is None
        assert metric.trend is None

    def test_full_metric(self) -> None:
        """Test metric with all fields."""
        metric = MetricValue(
            value=120.0,
            previous_value=100.0,
            change_pct=20.0,
            trend="up",
        )
        assert metric.value == 120.0
        assert metric.previous_value == 100.0
        assert metric.change_pct == 20.0
        assert metric.trend == "up"


class TestBusinessOverview:
    """Tests for BusinessOverview model."""

    def test_business_overview(self) -> None:
        """Test business overview construction."""
        overview = BusinessOverview(
            total_revenue=MetricValue(value=10000.0),
            order_count=MetricValue(value=50.0),
            average_order_value=MetricValue(value=200.0),
            unique_customers=MetricValue(value=45.0),
            period_start="2024-01-01T00:00:00",
            period_end="2024-01-31T23:59:59",
        )
        assert overview.total_revenue.value == 10000.0
        assert overview.order_count.value == 50.0
        assert overview.comparison_period is None


class TestTimeseriesDataPoint:
    """Tests for TimeseriesDataPoint model."""

    def test_datapoint_minimal(self) -> None:
        """Test data point with minimal fields."""
        dp = TimeseriesDataPoint(timestamp="2024-01-01", value=100.0)
        assert dp.timestamp == "2024-01-01"
        assert dp.value == 100.0
        assert dp.breakdown is None

    def test_datapoint_with_breakdown(self) -> None:
        """Test data point with breakdown."""
        dp = TimeseriesDataPoint(
            timestamp="2024-01-01",
            value=100.0,
            breakdown={"category_a": 60.0, "category_b": 40.0},
        )
        assert dp.breakdown["category_a"] == 60.0


class TestProductPerformance:
    """Tests for ProductPerformance model."""

    def test_product_performance(self) -> None:
        """Test product performance construction."""
        product = ProductPerformance(
            product_id="prod-123",
            sku="SKU-001",
            name="Test Product",
            collection="Black Rose",
            views=1000,
            add_to_cart=100,
            purchases=50,
            revenue=2500.0,
            conversion_rate=5.0,
            inventory_count=25,
            inventory_status="in_stock",
        )
        assert product.sku == "SKU-001"
        assert product.conversion_rate == 5.0
        assert product.inventory_status == "in_stock"


class TestFunnelStage:
    """Tests for FunnelStage model."""

    def test_funnel_stage(self) -> None:
        """Test funnel stage construction."""
        stage = FunnelStage(
            stage="traffic",
            count=10000,
            conversion_rate=100.0,
        )
        assert stage.stage == "traffic"
        assert stage.count == 10000
        assert stage.value is None


# =============================================================================
# Unit Tests - Enums
# =============================================================================


class TestEnums:
    """Tests for enum values."""

    def test_time_granularity(self) -> None:
        """Test TimeGranularity enum values."""
        assert TimeGranularity.HOURLY.value == "hourly"
        assert TimeGranularity.DAILY.value == "daily"
        assert TimeGranularity.WEEKLY.value == "weekly"
        assert TimeGranularity.MONTHLY.value == "monthly"

    def test_comparison_period(self) -> None:
        """Test ComparisonPeriod enum values."""
        assert ComparisonPeriod.PREVIOUS.value == "previous"
        assert ComparisonPeriod.YEAR_OVER_YEAR.value == "yoy"


# =============================================================================
# Integration Tests - API Endpoints
# =============================================================================


class TestBusinessOverviewEndpoint:
    """Tests for GET /analytics/business/overview endpoint."""

    @pytest.mark.asyncio
    async def test_overview_success(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test successful overview retrieval."""
        # Mock the database query result
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.order_count = 100
        mock_row.total_revenue = 15000.0
        mock_row.avg_order_value = 150.0
        mock_row.unique_customers = 85
        mock_result.one.return_value = mock_row
        mock_db_session.execute.return_value = mock_result

        # Import the endpoint function
        from api.v1.analytics.business import get_business_overview

        # Call the endpoint
        with patch(
            "api.v1.analytics.business.get_current_user",
            return_value=mock_user,
        ):
            response = await get_business_overview(
                period_days=30,
                comparison=None,
                user=mock_user,
                db=mock_db_session,
            )

        assert response.status == "success"
        assert response.period_days == 30
        assert response.overview.total_revenue.value == 15000.0
        assert response.overview.order_count.value == 100

    @pytest.mark.asyncio
    async def test_overview_with_comparison(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test overview with comparison period."""
        # Mock current period result
        current_result = MagicMock()
        current_row = MagicMock()
        current_row.order_count = 120
        current_row.total_revenue = 18000.0
        current_row.avg_order_value = 150.0
        current_row.unique_customers = 100
        current_result.one.return_value = current_row

        # Mock comparison period result
        comparison_result = MagicMock()
        comparison_row = MagicMock()
        comparison_row.order_count = 100
        comparison_row.total_revenue = 15000.0
        comparison_row.avg_order_value = 150.0
        comparison_row.unique_customers = 85
        comparison_result.one.return_value = comparison_row

        # Set up mock to return different results for each call
        mock_db_session.execute.side_effect = [current_result, comparison_result]

        from api.v1.analytics.business import get_business_overview

        response = await get_business_overview(
            period_days=30,
            comparison=ComparisonPeriod.PREVIOUS,
            user=mock_user,
            db=mock_db_session,
        )

        assert response.status == "success"
        assert response.overview.total_revenue.previous_value == 15000.0
        assert response.overview.total_revenue.change_pct == 20.0
        assert response.overview.total_revenue.trend == "up"


class TestSalesTimeseriesEndpoint:
    """Tests for GET /analytics/business/sales endpoint."""

    @pytest.mark.asyncio
    async def test_sales_timeseries_success(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test successful sales timeseries retrieval."""
        # Mock orders query result
        mock_order = MagicMock()
        mock_order.created_at = datetime.now(UTC)
        mock_order.total = 150.0

        orders_result = MagicMock()
        orders_result.scalars.return_value.all.return_value = [mock_order]

        # Mock breakdown query result
        breakdown_result = MagicMock()
        breakdown_row = MagicMock()
        breakdown_row.category = "Jewelry"
        breakdown_row.collection = "Black Rose"
        breakdown_row.revenue = 150.0
        breakdown_result.all.return_value = [breakdown_row]

        mock_db_session.execute.side_effect = [orders_result, breakdown_result]

        from api.v1.analytics.business import get_sales_timeseries

        response = await get_sales_timeseries(
            period_days=7,
            granularity=TimeGranularity.DAILY,
            comparison=None,
            user=mock_user,
            db=mock_db_session,
        )

        assert response.status == "success"
        assert response.granularity == "daily"
        assert response.total_revenue == 150.0


class TestProductPerformanceEndpoint:
    """Tests for GET /analytics/business/products endpoint."""

    @pytest.mark.asyncio
    async def test_product_performance_success(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test successful product performance retrieval."""
        mock_row = MagicMock()
        mock_row.id = "prod-123"
        mock_row.sku = "SKU-001"
        mock_row.name = "Test Product"
        mock_row.collection = "Black Rose"
        mock_row.quantity = 50
        mock_row.order_count = 10
        mock_row.units_sold = 15
        mock_row.revenue = 750.0

        result = MagicMock()
        result.all.return_value = [mock_row]
        mock_db_session.execute.return_value = result

        from api.v1.analytics.business import get_product_performance

        response = await get_product_performance(
            period_days=30,
            limit=50,
            sort_by="revenue",
            user=mock_user,
            db=mock_db_session,
        )

        assert response.status == "success"
        assert response.total_products == 1
        assert response.products[0].sku == "SKU-001"
        assert response.products[0].views is None
        assert response.products[0].add_to_cart is None
        assert response.products[0].conversion_rate is None


class TestCollectionMetricsEndpoint:
    """Tests for GET /analytics/business/collections endpoint."""

    @pytest.mark.asyncio
    async def test_collection_metrics_success(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test successful collection metrics retrieval."""
        # Mock collection query result
        collection_row = MagicMock()
        collection_row.collection = "Black Rose"
        collection_row.product_count = 25
        collection_row.revenue = 5000.0
        collection_row.order_count = 50

        collection_result = MagicMock()
        collection_result.all.return_value = [collection_row]

        # Mock top products query result
        top_products_result = MagicMock()
        top_products_result.all.return_value = [("SKU-001",), ("SKU-002",)]

        mock_db_session.execute.side_effect = [collection_result, top_products_result]

        from api.v1.analytics.business import get_collection_metrics

        response = await get_collection_metrics(
            period_days=30,
            user=mock_user,
            db=mock_db_session,
        )

        assert response.status == "success"
        assert response.total_revenue == 5000.0
        assert len(response.collections) == 1
        assert response.collections[0].collection_name == "Black Rose"


class TestConversionFunnelEndpoint:
    """Tests for GET /analytics/business/funnel endpoint."""

    @pytest.mark.asyncio
    async def test_unconfigured_funnel_does_not_invent_traffic_from_orders(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
        monkeypatch,
    ) -> None:
        """Missing analytics must stay unknown regardless of operational orders."""
        monkeypatch.delenv("SKYYROSE_ANALYTICS_SECRET", raising=False)

        from api.v1.analytics.business import get_conversion_funnel

        response = await get_conversion_funnel(
            period_days=30,
            comparison=None,
            user=mock_user,
            db=mock_db_session,
        )

        assert response.status == "unavailable"
        assert len(response.stages) == 5
        assert response.stages[0].stage == "traffic"
        assert response.stages[-1].stage == "purchase_complete"
        assert all(stage.count is None for stage in response.stages)
        assert all(stage.conversion_rate is None for stage in response.stages)
        assert response.stages[-1].value is None
        assert response.overall_conversion_rate is None
        mock_db_session.execute.assert_not_awaited()


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_data(
        self,
        mock_user: MagicMock,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test handling of empty data."""
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.order_count = 0
        mock_row.total_revenue = None
        mock_row.avg_order_value = None
        mock_row.unique_customers = 0
        mock_result.one.return_value = mock_row
        mock_db_session.execute.return_value = mock_result

        from api.v1.analytics.business import get_business_overview

        response = await get_business_overview(
            period_days=30,
            comparison=None,
            user=mock_user,
            db=mock_db_session,
        )

        assert response.status == "success"
        assert response.overview.total_revenue.value == 0.0
        assert response.overview.order_count.value == 0

    def test_period_days_validation(self) -> None:
        """Test period_days parameter validation."""
        # This would be tested via FastAPI TestClient in integration tests
        # Here we just verify the Query constraints are properly defined
        import inspect

        from api.v1.analytics.business import get_business_overview

        sig = inspect.signature(get_business_overview)
        period_days_param = sig.parameters["period_days"]
        # Verify default value
        assert period_days_param.default.default == 30
