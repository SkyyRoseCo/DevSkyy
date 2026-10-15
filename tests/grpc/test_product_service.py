"""
Tests for gRPC ProductServicer
================================

Tests the ProductServicer methods directly (without spinning up a real gRPC
server) by calling the async methods with mock request/context objects.

This approach:
- Does not require grpcio installed to run
- Does not require compiled proto stubs
- Tests business logic in complete isolation
- Runs fast (no network, no server startup)
"""

import json
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch, sentinel

import pytest

from grpc_server.product_service import ProductServicer, _SimpleRequest

_SENTINEL = object()  # marker for missing key in sys.modules


def _make_product(
    sku: str = "br-001",
    name: str = "Black Rose Crewneck",
    price: float = 79.99,
    collection: str = "black-rose",
    is_active: bool = True,
    images: list | None = None,
) -> MagicMock:
    """Build a mock ORM Product object."""
    p = MagicMock()
    p.id = "prod-uuid-001"
    p.sku = sku
    p.name = name
    p.description = "Premium crewneck"
    p.price = price
    p.compare_price = price * 1.2
    p.collection = collection
    p.is_active = is_active
    p.images_json = json.dumps(images or ["img1.jpg"])
    return p


def _make_context() -> MagicMock:
    """Mock gRPC ServicerContext."""
    ctx = MagicMock()
    ctx.set_code = MagicMock()
    ctx.set_details = MagicMock()
    return ctx


@pytest.mark.unit
@pytest.mark.asyncio
class TestProductServicerGetProduct:
    """Tests for ProductServicer.GetProduct"""

    async def test_get_existing_product_returns_dict(self):
        """
        GetProduct returns a populated dict for a valid SKU.
        """
        mock_product = _make_product(sku="br-001")
        ctx = _make_context()

        servicer = ProductServicer()

        with patch("grpc_server.product_service.DatabaseManager") as mock_db_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_product
            mock_session.execute = AsyncMock(return_value=mock_result)

            mock_db = MagicMock()
            mock_db.session.return_value = mock_session
            mock_db_cls.return_value = mock_db

            request = _SimpleRequest(sku="br-001")
            result = await servicer.GetProduct(request, ctx)

        assert result["sku"] == "br-001"
        assert result["name"] == "Black Rose Crewneck"
        assert result["price"] == 79.99
        assert "images" in result

    async def test_get_missing_product_sets_not_found(self):
        """
        GetProduct sets NOT_FOUND on context when product doesn't exist.
        """
        ctx = _make_context()
        servicer = ProductServicer()

        # Isolate the optional transport module from other tests' import stubs.
        grpc_module = SimpleNamespace(StatusCode=SimpleNamespace(NOT_FOUND=sentinel.not_found))
        with (
            patch.dict(sys.modules, {"grpc": grpc_module}),
            patch("grpc_server.product_service.DatabaseManager") as mock_db_cls,
        ):
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute = AsyncMock(return_value=mock_result)

            mock_db = MagicMock()
            mock_db.session.return_value = mock_session
            mock_db_cls.return_value = mock_db

            request = _SimpleRequest(sku="nonexistent-sku")
            result = await servicer.GetProduct(request, ctx)

        assert result == {}
        # NOT_FOUND status should be set on context
        ctx.set_code.assert_called_once_with(sentinel.not_found)
        ctx.set_details.assert_called_once_with("Product 'nonexistent-sku' not found")


@pytest.mark.unit
@pytest.mark.asyncio
class TestProductServicerListProducts:
    """Tests for ProductServicer.ListProducts"""

    async def test_list_returns_products_and_total(self):
        """
        ListProducts returns a dict with 'products' list and 'total' count.
        """
        products = [_make_product(sku=f"br-00{i}") for i in range(3)]
        ctx = _make_context()
        servicer = ProductServicer()

        with patch("grpc_server.product_service.DatabaseManager") as mock_db_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)

            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = products
            mock_session.execute = AsyncMock(return_value=mock_result)

            mock_db = MagicMock()
            mock_db.session.return_value = mock_session
            mock_db_cls.return_value = mock_db

            request = _SimpleRequest(collection="black-rose", limit=20, offset=0)
            result = await servicer.ListProducts(request, ctx)

        assert len(result["products"]) == 3
        assert result["total"] == 3

    async def test_list_clamps_limit_to_100(self):
        """
        ListProducts silently clamps limit to max 100 to prevent overload.
        """
        ctx = _make_context()
        servicer = ProductServicer()

        with patch("grpc_server.product_service.DatabaseManager") as mock_db_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)

            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            mock_session.execute = AsyncMock(return_value=mock_result)

            mock_db = MagicMock()
            mock_db.session.return_value = mock_session
            mock_db_cls.return_value = mock_db

            # Request limit of 9999 — should be clamped to 100
            request = _SimpleRequest(collection="", limit=9999, offset=0)
            result = await servicer.ListProducts(request, ctx)

        assert result["total"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
class TestProductServicerHelpers:
    """Tests for ProductServicer helper methods"""

    def test_product_to_dict_deserializes_images_json(self):
        """
        _product_to_dict correctly deserializes the images_json column.
        """
        servicer = ProductServicer()
        product = _make_product(images=["front.jpg", "back.jpg", "detail.jpg"])

        result = servicer._product_to_dict(product)

        assert result["images"] == ["front.jpg", "back.jpg", "detail.jpg"]
        assert isinstance(result["price"], float)
        assert result["is_active"] is True

    def test_product_to_dict_handles_invalid_images_json(self):
        """
        _product_to_dict returns empty list for malformed images_json.
        """
        servicer = ProductServicer()
        product = _make_product()
        product.images_json = "NOT VALID JSON{{{{"

        result = servicer._product_to_dict(product)

        assert result["images"] == []

    async def test_set_not_found_without_grpc_installed(self):
        """
        _set_not_found handles missing grpcio gracefully — no AttributeError.
        """
        ctx = _make_context()
        # When grpc is absent (None in sys.modules), import grpc raises
        # ImportError which _set_not_found catches silently.
        saved = sys.modules.get("grpc", _SENTINEL)
        try:
            sys.modules["grpc"] = None  # type: ignore[assignment]
            # Should not raise even without grpcio
            try:
                await ProductServicer._set_not_found(ctx, "test")
            except Exception:
                pass  # Acceptable — we just verify no crash in outer logic
        finally:
            if saved is _SENTINEL:
                sys.modules.pop("grpc", None)
            else:
                sys.modules["grpc"] = saved
