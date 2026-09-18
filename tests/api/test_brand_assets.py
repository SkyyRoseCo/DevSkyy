# tests/api/test_brand_assets.py
"""Tests for brand assets API endpoints.

Implements US-013: Brand asset ingestion for training.

Author: DevSkyy Platform Team
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

import api.v1.brand_assets as brand_assets_module
from api.v1.brand_assets import (
    AssetApprovalStatus,
    BrandAsset,
    BrandAssetCategory,
    ColorPalette,
    VisualFeatures,
    _asset_to_row,
    router,
)
from database.db import DatabaseConfig, DatabaseManager, db_manager

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_user() -> MagicMock:
    """Create mock authenticated user."""
    from security.jwt_oauth2_auth import TokenPayload, TokenType

    return TokenPayload(
        sub="user_123",
        jti="test_jti_123",
        type=TokenType.ACCESS,
        roles=["user", "admin"],
        exp=datetime.now(UTC),
        iat=datetime.now(UTC),
    )


@pytest.fixture
async def client(mock_user: MagicMock):
    """ASGI test client backed by a fresh in-memory DB, isolated per test.

    Mirrors tests/test_auth_endpoints.py's db_manager reset pattern: the
    module-level singleton backs both the FastAPI get_db dependency and
    process_bulk_ingestion's background-task session, so it must be reset
    and reinitialized per test rather than overridden via
    dependency_overrides alone.
    """
    from security.jwt_oauth2_auth import get_current_user

    if db_manager._engine:
        await db_manager.close()
        db_manager._instance = None

    mgr = DatabaseManager()
    await mgr.initialize(DatabaseConfig(url="sqlite+aiosqlite:///:memory:"))

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await mgr.close()
    mgr._instance = None


async def _save_asset(asset: BrandAsset) -> None:
    """Persist a BrandAsset directly, bypassing the API (test setup only)."""
    async with db_manager.session() as session:
        session.add(_asset_to_row(asset))


def _pin_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    *,
    features: VisualFeatures | None = None,
) -> None:
    """Patch both ingestion pipeline steps to deterministic, assertable outputs.

    The real steps fail open — upload_to_r2 silently no-ops without R2
    credentials (r2_key=None) and extract_visual_features returns fabricated
    brand defaults on any error — so unpatched tests cannot distinguish a
    working pipeline from a broken one. Pinning both lets tests assert the
    persisted BrandAsset carries the pipeline's actual outputs.

    Every test that POSTs to /ingest/bulk must pin (or patch both steps
    itself). Unpinned, BulkIngestionRequest.extract_features defaults to True
    and the BackgroundTask runs inline under ASGITransport, so the POST does
    not return until extract_visual_features has made one real HTTPS GET per
    asset — the suite's duration becomes the network's (bug-333/334: 100
    assets blew the pytest timeout; the per-asset commits cost ~0.06s total).
    No test in this file should leave the process.
    """

    async def fake_upload(
        image_url: str,
        asset_id: str,
        category: BrandAssetCategory,
        *,
        correlation_id: str | None = None,
    ) -> tuple[str | None, int, int | None, int | None, str | None]:
        return f"brand/{category.value}/{asset_id}.png", 1234, 800, 600, "image/png"

    async def fake_extract(
        image_url: str,
        *,
        correlation_id: str | None = None,
    ) -> VisualFeatures:
        return features if features is not None else VisualFeatures()

    monkeypatch.setattr(brand_assets_module, "upload_to_r2", fake_upload)
    monkeypatch.setattr(brand_assets_module, "extract_visual_features", fake_extract)


# =============================================================================
# Bulk Ingestion Tests
# =============================================================================


class TestBulkIngestion:
    """Tests for bulk ingestion endpoints."""

    @pytest.mark.asyncio
    async def test_bulk_ingest_single_asset(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should start bulk ingestion with single asset."""
        # Pinned for determinism/speed only — unpinned, the inline background
        # task makes a real HTTPS GET per asset (see test_bulk_ingest_max_100_assets).
        _pin_pipeline(monkeypatch)
        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [
                    {
                        "url": "https://example.com/product1.jpg",
                        "category": "product",
                        "metadata": {"campaign": "Spring 2024"},
                    }
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()
        # The endpoint returns the freshly created job before background
        # processing starts, so its status is always exactly "pending".
        assert data["status"] == "pending"
        assert data["total"] == 1
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_bulk_ingest_multiple_assets(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should handle multiple assets."""
        # Pinned for determinism/speed only — unpinned, the inline background
        # task makes a real HTTPS GET per asset (see test_bulk_ingest_max_100_assets).
        _pin_pipeline(monkeypatch)
        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [
                    {"url": "https://example.com/img1.jpg", "category": "product"},
                    {"url": "https://example.com/img2.jpg", "category": "lifestyle"},
                    {"url": "https://example.com/img3.jpg", "category": "campaign"},
                ],
                "campaign_name": "Black Rose Collection",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_bulk_ingest_max_100_assets(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should accept up to 100 assets and process every one of them."""
        # Pinned so the inline background task never leaves the process. Unpinned,
        # extract_visual_features issues one real HTTPS GET per asset (example.com
        # 404 -> fallback), and 100 network round-trips at 0.1-0.4s each is what
        # blew the pytest timeout (bug-333) — the per-asset commits cost ~0.06s total.
        _pin_pipeline(monkeypatch)
        assets = [
            {"url": f"https://example.com/img{i}.jpg", "category": "product"} for i in range(100)
        ]

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={"assets": assets},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 100

        job = (await client.get(f"/brand-assets/ingest/{data['id']}")).json()
        assert job["status"] == "completed"
        assert job["processed"] == 100
        assert job["succeeded"] == 100
        assert job["failed"] == 0
        assert len(job["results"]) == 100

    @pytest.mark.asyncio
    async def test_bulk_ingest_over_limit(self, client: AsyncClient) -> None:
        """Should reject over 100 assets."""
        assets = [
            {"url": f"https://example.com/img{i}.jpg", "category": "product"} for i in range(101)
        ]

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={"assets": assets},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_bulk_ingest_with_auto_approve(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should persist the asset as approved when auto_approve is requested."""
        # Pinned for determinism/speed only (no real R2/Gemini calls); pipeline
        # fidelity is asserted by test_bulk_ingest_persists_pipeline_outputs.
        _pin_pipeline(monkeypatch)

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [{"url": "https://example.com/img.jpg", "category": "product"}],
                "auto_approve": True,
            },
        )
        assert response.status_code == 200
        job_id = response.json()["id"]

        job = (await client.get(f"/brand-assets/ingest/{job_id}")).json()
        assert job["status"] == "completed"
        asset_id = job["results"][0]["asset_id"]

        asset = (await client.get(f"/brand-assets/assets/{asset_id}")).json()
        assert asset["approval_status"] == "approved"

    @pytest.mark.asyncio
    async def test_bulk_ingest_persists_pipeline_outputs(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Persisted asset must carry the pipeline's outputs, not fallback defaults.

        Job status/counts alone cannot detect a broken pipeline (both steps
        fail open), so this test pins upload_to_r2 and extract_visual_features
        to known values and asserts the asset fetched via GET
        /brand-assets/assets/{id} carries exactly those values.
        """
        pinned = VisualFeatures(
            color_palette=ColorPalette(
                primary="#123456",
                secondary=["#654321"],
                accent="#ABCDEF",
            ),
            style_tags=["pinned-tag"],
            quality_score=0.91,
        )
        _pin_pipeline(monkeypatch, features=pinned)

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={"assets": [{"url": "https://example.com/img.jpg", "category": "product"}]},
        )
        assert response.status_code == 200
        job_id = response.json()["id"]

        job = (await client.get(f"/brand-assets/ingest/{job_id}")).json()
        assert job["status"] == "completed"
        assert job["succeeded"] == 1
        assert job["failed"] == 0
        assert job["results"][0]["success"] is True
        asset_id = job["results"][0]["asset_id"]

        asset_response = await client.get(f"/brand-assets/assets/{asset_id}")
        assert asset_response.status_code == 200
        asset = asset_response.json()
        assert asset["r2_key"] == f"brand/product/{asset_id}.png"
        assert asset["file_size_bytes"] == 1234
        assert asset["width"] == 800
        assert asset["height"] == 600
        assert asset["mime_type"] == "image/png"
        assert asset["visual_features"]["color_palette"]["primary"] == "#123456"
        assert asset["visual_features"]["color_palette"]["secondary"] == ["#654321"]
        assert asset["visual_features"]["color_palette"]["accent"] == "#ABCDEF"
        assert asset["visual_features"]["style_tags"] == ["pinned-tag"]
        assert asset["visual_features"]["quality_score"] == 0.91

    @pytest.mark.asyncio
    async def test_bulk_ingest_upload_failure_marks_job_failed(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A raising pipeline step must surface as a failed result, not silent success."""

        async def broken_upload(
            image_url: str,
            asset_id: str,
            category: BrandAssetCategory,
            *,
            correlation_id: str | None = None,
        ) -> tuple[str | None, int, int | None, int | None, str | None]:
            raise RuntimeError("R2 upload exploded")

        monkeypatch.setattr(brand_assets_module, "upload_to_r2", broken_upload)

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={"assets": [{"url": "https://example.com/img.jpg", "category": "product"}]},
        )
        assert response.status_code == 200
        job_id = response.json()["id"]

        job = (await client.get(f"/brand-assets/ingest/{job_id}")).json()
        assert job["status"] == "failed"
        assert job["succeeded"] == 0
        assert job["failed"] == 1
        result = job["results"][0]
        assert result["success"] is False
        assert result["asset_id"] is None
        assert "R2 upload exploded" in result["error"]

    @pytest.mark.asyncio
    async def test_bulk_ingest_mixed_results_marks_job_partial(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Mixed success/failure across assets must yield status "partial", not silent completed/failed."""
        good_url = "https://example.com/good.jpg"
        bad_url = "https://example.com/bad.jpg"

        async def fake_upload(
            image_url: str,
            asset_id: str,
            category: BrandAssetCategory,
            *,
            correlation_id: str | None = None,
        ) -> tuple[str | None, int, int | None, int | None, str | None]:
            if image_url == bad_url:
                raise RuntimeError("R2 upload exploded")
            return f"brand/{category.value}/{asset_id}.png", 1234, 800, 600, "image/png"

        async def fake_extract(
            image_url: str,
            *,
            correlation_id: str | None = None,
        ) -> VisualFeatures:
            return VisualFeatures()

        monkeypatch.setattr(brand_assets_module, "upload_to_r2", fake_upload)
        monkeypatch.setattr(brand_assets_module, "extract_visual_features", fake_extract)

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [
                    {"url": good_url, "category": "product"},
                    {"url": bad_url, "category": "product"},
                ],
            },
        )
        assert response.status_code == 200
        job_id = response.json()["id"]

        job = (await client.get(f"/brand-assets/ingest/{job_id}")).json()
        assert job["status"] == "partial"
        assert job["succeeded"] == 1
        assert job["failed"] == 1
        assert job["processed"] == 2

        results_by_url = {result["url"]: result for result in job["results"]}
        good_result = results_by_url[good_url]
        assert good_result["success"] is True
        assert good_result["asset_id"] is not None

        bad_result = results_by_url[bad_url]
        assert bad_result["success"] is False
        assert bad_result["asset_id"] is None
        assert "R2 upload exploded" in bad_result["error"]

        asset_response = await client.get(f"/brand-assets/assets/{good_result['asset_id']}")
        assert asset_response.status_code == 200
        asset_id = good_result["asset_id"]
        assert asset_response.json()["r2_key"] == f"brand/product/{asset_id}.png"

    @pytest.mark.asyncio
    async def test_bulk_ingest_extract_features_false_skips_extraction(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """extract_features=False must persist no features and never call the extractor."""
        extract_calls: list[str] = []

        async def fake_upload(
            image_url: str,
            asset_id: str,
            category: BrandAssetCategory,
            *,
            correlation_id: str | None = None,
        ) -> tuple[str | None, int, int | None, int | None, str | None]:
            return None, 0, None, None, None

        async def recording_extract(
            image_url: str,
            *,
            correlation_id: str | None = None,
        ) -> VisualFeatures:
            extract_calls.append(image_url)
            return VisualFeatures()

        monkeypatch.setattr(brand_assets_module, "upload_to_r2", fake_upload)
        monkeypatch.setattr(brand_assets_module, "extract_visual_features", recording_extract)

        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [{"url": "https://example.com/img.jpg", "category": "product"}],
                "extract_features": False,
            },
        )
        assert response.status_code == 200
        job_id = response.json()["id"]

        job = (await client.get(f"/brand-assets/ingest/{job_id}")).json()
        assert job["status"] == "completed"
        asset_id = job["results"][0]["asset_id"]

        asset = (await client.get(f"/brand-assets/assets/{asset_id}")).json()
        assert asset["visual_features"] is None
        assert extract_calls == []

    @pytest.mark.asyncio
    async def test_get_ingestion_job(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should retrieve ingestion job status."""
        # Pinned for determinism/speed only — see _pin_pipeline.
        _pin_pipeline(monkeypatch)
        # Create job
        create_response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [{"url": "https://example.com/img.jpg", "category": "product"}],
            },
        )
        job_id = create_response.json()["id"]

        # Get job
        response = await client.get(f"/brand-assets/ingest/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, client: AsyncClient) -> None:
        """Should return 404 for non-existent job."""
        response = await client.get("/brand-assets/ingest/nonexistent_id")
        assert response.status_code == 404


# =============================================================================
# Asset CRUD Tests
# =============================================================================


class TestAssetCrud:
    """Tests for asset CRUD operations."""

    async def _create_test_asset(self, client: AsyncClient) -> str:
        """Helper to create a test asset."""
        asset = BrandAsset(
            url="https://example.com/test.jpg",
            category=BrandAssetCategory.PRODUCT,
        )
        await _save_asset(asset)
        return asset.id

    @pytest.mark.asyncio
    async def test_list_assets_empty(self, client: AsyncClient) -> None:
        """Should return empty list when no assets."""
        response = await client.get("/brand-assets/assets")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["assets"] == []

    @pytest.mark.asyncio
    async def test_list_assets_with_data(self, client: AsyncClient) -> None:
        """Should list all assets."""
        await self._create_test_asset(client)
        await self._create_test_asset(client)

        response = await client.get("/brand-assets/assets")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_assets_filter_by_category(self, client: AsyncClient) -> None:
        """Should filter by category."""
        product = BrandAsset(
            url="https://example.com/product.jpg",
            category=BrandAssetCategory.PRODUCT,
        )
        await _save_asset(product)

        lifestyle = BrandAsset(
            url="https://example.com/lifestyle.jpg",
            category=BrandAssetCategory.LIFESTYLE,
        )
        await _save_asset(lifestyle)

        response = await client.get("/brand-assets/assets?category=product")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["assets"][0]["category"] == "product"

    @pytest.mark.asyncio
    async def test_list_assets_filter_by_status(self, client: AsyncClient) -> None:
        """Should filter by approval status."""
        pending = BrandAsset(
            url="https://example.com/pending.jpg",
            category=BrandAssetCategory.PRODUCT,
            approval_status=AssetApprovalStatus.PENDING,
        )
        await _save_asset(pending)

        approved = BrandAsset(
            url="https://example.com/approved.jpg",
            category=BrandAssetCategory.PRODUCT,
            approval_status=AssetApprovalStatus.APPROVED,
        )
        await _save_asset(approved)

        response = await client.get("/brand-assets/assets?approval_status=approved")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_get_asset_by_id(self, client: AsyncClient) -> None:
        """Should get asset by ID."""
        asset_id = await self._create_test_asset(client)

        response = await client.get(f"/brand-assets/assets/{asset_id}")

        assert response.status_code == 200
        assert response.json()["id"] == asset_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_asset(self, client: AsyncClient) -> None:
        """Should return 404 for non-existent asset."""
        response = await client.get("/brand-assets/assets/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_approve_asset(self, client: AsyncClient) -> None:
        """Should approve an asset."""
        asset_id = await self._create_test_asset(client)

        response = await client.patch(f"/brand-assets/assets/{asset_id}/approve")

        assert response.status_code == 200
        data = response.json()
        assert data["approval_status"] == "approved"

    @pytest.mark.asyncio
    async def test_reject_asset(self, client: AsyncClient) -> None:
        """Should reject an asset."""
        asset_id = await self._create_test_asset(client)

        response = await client.patch(
            f"/brand-assets/assets/{asset_id}/reject",
            params={"reason": "Low quality"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approval_status"] == "rejected"

    @pytest.mark.asyncio
    async def test_delete_asset(self, client: AsyncClient) -> None:
        """Should delete an asset."""
        asset_id = await self._create_test_asset(client)

        response = await client.delete(f"/brand-assets/assets/{asset_id}")

        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # Verify deleted
        get_response = await client.get(f"/brand-assets/assets/{asset_id}")
        assert get_response.status_code == 404


# =============================================================================
# Training Readiness Tests
# =============================================================================


class TestTrainingReadiness:
    """Tests for training readiness assessment."""

    @pytest.mark.asyncio
    async def test_training_readiness_empty(self, client: AsyncClient) -> None:
        """Should report not ready when empty."""
        response = await client.get("/brand-assets/training-readiness")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["total_assets"] == 0
        assert data["approved_assets"] == 0

    @pytest.mark.asyncio
    async def test_training_readiness_below_minimum(self, client: AsyncClient) -> None:
        """Should report not ready below minimum."""
        # Create 50 approved assets
        for i in range(50):
            asset = BrandAsset(
                url=f"https://example.com/img{i}.jpg",
                category=BrandAssetCategory.PRODUCT,
                approval_status=AssetApprovalStatus.APPROVED,
            )
            await _save_asset(asset)

        response = await client.get("/brand-assets/training-readiness?minimum_assets=100")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["approved_assets"] == 50

    @pytest.mark.asyncio
    async def test_training_readiness_needs_review(self, client: AsyncClient) -> None:
        """Should report needs review when pending assets could meet minimum."""
        # Create 50 approved and 60 pending
        for i in range(50):
            approved = BrandAsset(
                url=f"https://example.com/approved{i}.jpg",
                category=BrandAssetCategory.PRODUCT,
                approval_status=AssetApprovalStatus.APPROVED,
            )
            await _save_asset(approved)

        for i in range(60):
            pending = BrandAsset(
                url=f"https://example.com/pending{i}.jpg",
                category=BrandAssetCategory.LIFESTYLE,
                approval_status=AssetApprovalStatus.PENDING,
            )
            await _save_asset(pending)

        response = await client.get("/brand-assets/training-readiness?minimum_assets=100")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "needs_review"
        # Check that review recommendation exists somewhere in recommendations
        recommendations_str = str(data["recommendations"]).lower()
        assert "review" in recommendations_str or "pending" in recommendations_str

    @pytest.mark.asyncio
    async def test_training_readiness_ready(self, client: AsyncClient) -> None:
        """Should report ready when minimum met."""
        # Create 150 approved assets
        for i in range(150):
            asset = BrandAsset(
                url=f"https://example.com/img{i}.jpg",
                category=BrandAssetCategory.PRODUCT,
                approval_status=AssetApprovalStatus.APPROVED,
            )
            await _save_asset(asset)

        response = await client.get("/brand-assets/training-readiness?minimum_assets=100")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["approved_assets"] == 150
        assert data["estimated_training_time"] is not None


# =============================================================================
# Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for brand assets statistics."""

    @pytest.mark.asyncio
    async def test_stats_empty(self, client: AsyncClient) -> None:
        """Should return zero stats when empty."""
        response = await client.get("/brand-assets/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_stats_with_data(self, client: AsyncClient) -> None:
        """Should return accurate statistics."""
        # Create assets with different categories and statuses
        for i, cat in enumerate(
            [
                BrandAssetCategory.PRODUCT,
                BrandAssetCategory.LIFESTYLE,
                BrandAssetCategory.CAMPAIGN,
            ]
        ):
            asset = BrandAsset(
                url=f"https://example.com/{cat.value}.jpg",
                category=cat,
                approval_status=(
                    AssetApprovalStatus.APPROVED if i % 2 == 0 else AssetApprovalStatus.PENDING
                ),
                visual_features=VisualFeatures(
                    color_palette=ColorPalette(primary="#000"),
                    quality_score=0.8,
                ),
            )
            await _save_asset(asset)

        response = await client.get("/brand-assets/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert "by_category" in data
        assert "by_approval_status" in data
        assert data["average_quality_score"] > 0


# =============================================================================
# Persistence Tests
# =============================================================================


class TestPersistence:
    """Tests that data survives a fresh DB session (the point of this store)."""

    @pytest.mark.asyncio
    async def test_asset_survives_new_session(self, client: AsyncClient) -> None:
        """An asset written in one session must be readable from a new one."""
        asset = BrandAsset(
            url="https://example.com/durable.jpg",
            category=BrandAssetCategory.PRODUCT,
        )
        async with db_manager.session() as write_session:
            write_session.add(_asset_to_row(asset))

        async with db_manager.session() as read_session:
            from database.models_brand_assets import BrandAssetRecord

            row = await read_session.get(BrandAssetRecord, asset.id)
            assert row is not None
            assert row.url == asset.url

    @pytest.mark.asyncio
    async def test_ingestion_job_survives_new_session(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A job written in one session must be readable from a new one."""
        # Pinned for determinism/speed only — see _pin_pipeline.
        _pin_pipeline(monkeypatch)
        response = await client.post(
            "/brand-assets/ingest/bulk",
            json={
                "assets": [{"url": "https://example.com/durable-job.jpg", "category": "product"}]
            },
        )
        job_id = response.json()["id"]

        async with db_manager.session() as read_session:
            from database.models_brand_assets import IngestionJobRecord

            row = await read_session.get(IngestionJobRecord, job_id)
            assert row is not None
            assert row.total == 1
