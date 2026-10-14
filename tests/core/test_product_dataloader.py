"""
Tests for Product DataLoader - N+1 Query Prevention
====================================================

Verifies that ProductDataLoader batches DB queries to prevent N+1 problems.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.graphql.dataloaders.product_loader import ProductDataLoader


class MockProduct:
    """Mock Product model for testing"""

    def __init__(self, sku: str, name: str, price: float):
        self.sku = sku
        self.name = name
        self.price = price
        self.collection = "test-collection"
        self.images = [f"{sku}-front.jpg"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestProductDataLoader:
    """Test ProductDataLoader batching and caching behavior"""

    async def test_batch_load_products_by_sku(self):
        """
        Test that DataLoader batches multiple SKU requests into one DB query

        Expected behavior:
        - Request products with SKUs: ['br-001', 'br-002', 'br-003']
        - DataLoader should make ONLY 1 database query (not 3)
        - All products should be returned in correct order
        """
        # Arrange
        mock_products = [
            MockProduct("br-001", "Black Rose Crewneck", 79.99),
            MockProduct("br-002", "Black Rose Hoodie", 89.99),
            MockProduct("br-003", "Black Rose T-Shirt", 39.99),
        ]

        # Create mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_products
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock the database manager
        with patch("api.graphql.dataloaders.product_loader.DatabaseManager") as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.session.return_value.__aenter__.return_value = mock_session
            mock_db_instance.session.return_value.__aexit__.return_value = AsyncMock()
            mock_db_class.return_value = mock_db_instance

            # Act
            loader = ProductDataLoader()
            products = await loader.load_many(["br-001", "br-002", "br-003"])

            # Assert
            assert len(products) == 3
            assert products[0].sku == "br-001"
            assert products[1].sku == "br-002"
            assert products[2].sku == "br-003"
            # Verify only ONE database call was made (batching)
            assert mock_session.execute.call_count == 1

    async def test_dataloader_caches_within_request(self):
        """
        Test that DataLoader caches results within a single request

        Expected behavior:
        - First load: Fetches from database
        - Second load (same SKU): Returns from cache, NO new DB query
        """
        # Arrange
        mock_product = MockProduct("br-001", "Black Rose Crewneck", 79.99)

        # Create mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_product]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock the database manager
        with patch("api.graphql.dataloaders.product_loader.DatabaseManager") as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.session.return_value.__aenter__.return_value = mock_session
            mock_db_instance.session.return_value.__aexit__.return_value = AsyncMock()
            mock_db_class.return_value = mock_db_instance

            # Act
            loader = ProductDataLoader()
            product1 = await loader.load("br-001")  # First load - hits DB
            product2 = await loader.load("br-001")  # Second load - should be cached

            # Assert
            assert product1.sku == "br-001"
            assert product2.sku == "br-001"
            # Verify only ONE database call was made (caching worked)
            assert mock_session.execute.call_count == 1

    async def test_dataloader_handles_missing_products(self):
        """
        Test that DataLoader gracefully handles missing products

        Expected behavior:
        - Request 3 SKUs, but only 2 exist in database
        - Should return [Product, Product, None]
        - No errors raised
        """
        # Arrange
        mock_products = [
            MockProduct("br-001", "Black Rose Crewneck", 79.99),
            MockProduct("br-002", "Black Rose Hoodie", 89.99),
            # br-999 does NOT exist
        ]

        # Create mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_products
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock the database manager
        with patch("api.graphql.dataloaders.product_loader.DatabaseManager") as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.session.return_value.__aenter__.return_value = mock_session
            mock_db_instance.session.return_value.__aexit__.return_value = AsyncMock()
            mock_db_class.return_value = mock_db_instance

            # Act
            loader = ProductDataLoader()
            products = await loader.load_many(["br-001", "br-002", "br-999"])

            # Assert
            assert len(products) == 3
            assert products[0] is not None
            assert products[1] is not None
            assert products[2] is None  # Missing product

    async def test_dataloader_concurrent_requests_batching(self):
        """
        Test that concurrent requests are batched into single DB query

        Expected behavior:
        - Multiple async tasks request different products simultaneously
        - DataLoader should batch all requests into ONE database query
        - This is the key N+1 prevention mechanism
        """
        # Arrange
        mock_products = [
            MockProduct(f"br-{i:03d}", f"Product {i}", float(i * 10)) for i in range(1, 11)
        ]

        # Create mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_products
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock the database manager
        with patch("api.graphql.dataloaders.product_loader.DatabaseManager") as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.session.return_value.__aenter__.return_value = mock_session
            mock_db_instance.session.return_value.__aexit__.return_value = AsyncMock()
            mock_db_class.return_value = mock_db_instance

            # Act
            loader = ProductDataLoader()
            # Simulate concurrent GraphQL requests
            import asyncio

            results = await asyncio.gather(
                loader.load("br-001"),
                loader.load("br-002"),
                loader.load("br-003"),
                loader.load("br-004"),
                loader.load("br-005"),
            )

            # Assert
            assert len(results) == 5
            # Verify only ONE database query was made for all 5 concurrent requests
            assert mock_session.execute.call_count == 1

    async def test_dataloader_empty_sku_list(self):
        """
        Test that DataLoader handles empty SKU list gracefully

        Expected behavior:
        - Empty list input
        - Returns empty list
        - No database queries made
        """
        # Arrange
        loader = ProductDataLoader()

        # Act
        products = await loader.load_many([])

        # Assert
        assert products == []


@pytest.mark.unit
async def test_integration_graphql_prevents_n_plus_one():
    """
    Integration test: a GraphQL query selecting 100 products by SKU runs the
    real Strawberry schema and must hit the database exactly once.

    The 100 aliased `product(sku:)` fields resolve concurrently; the
    DataLoader in the request context coalesces them into one batched query.
    """
    from api.graphql.schema import schema

    skus = [f"br-{i:03d}" for i in range(1, 101)]
    products = [
        SimpleNamespace(
            id=i,
            sku=sku,
            name=f"Product {sku}",
            description="",
            price=10.0,
            compare_price=None,
            collection="test-collection",
            is_active=True,
            images_json=None,
        )
        for i, sku in enumerate(skus, start=1)
    ]

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = products
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("api.graphql.dataloaders.product_loader.DatabaseManager") as mock_db_class:
        mock_db_instance = MagicMock()
        mock_db_instance.session.return_value.__aenter__.return_value = mock_session
        mock_db_instance.session.return_value.__aexit__.return_value = AsyncMock()
        mock_db_class.return_value = mock_db_instance

        loader = ProductDataLoader()
        query = (
            "query {\n"
            + "\n".join(
                f'  p{i}: product(sku: "{sku}") {{ sku name }}' for i, sku in enumerate(skus)
            )
            + "\n}"
        )

        result = await schema.execute(query, context_value={"product_loader": loader})

    assert result.errors is None
    assert result.data is not None
    assert [result.data[f"p{i}"]["sku"] for i in range(100)] == skus
    # 100 resolved products, ONE database call
    assert mock_session.execute.call_count == 1
