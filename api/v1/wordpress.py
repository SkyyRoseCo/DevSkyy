"""WordPress Integration API.

Provides endpoints for syncing content (posts/pages) and checking connection status.
Product sync is handled by wordpress_integration.py.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from integrations.wordpress_com_client import create_wordpress_client
from security.jwt_oauth2_auth import service_or_user_auth

router = APIRouter(tags=["wordpress"], prefix="/wordpress")


class WordPressSyncRequest(BaseModel):
    """Request to sync content to WordPress."""

    post_type: str = "post"
    title: str
    content: str
    status: str = "draft"


class WordPressSyncResponse(BaseModel):
    """Response from WordPress sync."""

    success: bool
    wordpress_id: int | None = None
    url: str | None = None
    error: str | None = None


def _get_wp_creds() -> dict[str, str | None]:
    """Get WordPress credentials from environment."""
    site_url = os.getenv("WORDPRESS_SITE_URL", os.getenv("WORDPRESS_URL", ""))
    if not site_url:
        raise HTTPException(status_code=503, detail="WORDPRESS_SITE_URL not configured")
    return {
        "site_url": site_url,
        "api_token": os.getenv("WORDPRESS_API_TOKEN") or None,
        "username": os.getenv("WP_AUTH_USER") or None,
        "app_password": os.getenv("WP_AUTH_PASS") or None,
    }


@router.post("/sync", response_model=WordPressSyncResponse, summary="Sync content to WordPress")
async def sync_to_wordpress(
    request: WordPressSyncRequest,
    _principal=Depends(service_or_user_auth),
):
    """Create a post/page on WordPress.

    Auth: a user JWT (dashboard) OR the X-Service-Token machine-to-machine token
    (background queue worker). See security.jwt_oauth2_auth.service_or_user_auth.
    """
    creds = _get_wp_creds()
    try:
        async with await create_wordpress_client(**creds) as client:
            result = await client.create_post(
                title=request.title,
                content=request.content,
                status=request.status,
            )
            return WordPressSyncResponse(
                success=True,
                wordpress_id=result.get("id"),
                url=result.get("link"),
            )
    except Exception as e:
        return WordPressSyncResponse(success=False, error=str(e))


@router.get("/status", summary="WordPress connection status")
async def get_wordpress_status(_principal=Depends(service_or_user_auth)) -> dict[str, Any]:
    """Check WordPress connection by fetching site info."""
    creds = _get_wp_creds()
    try:
        async with await create_wordpress_client(**creds) as client:
            # Fetch site root info
            info = await client._wp_request("GET", "/wp-json/")
            return {
                "connected": True,
                "site_url": creds["site_url"],
                "name": info.get("name", ""),
                "description": info.get("description", ""),
                "url": info.get("url", ""),
            }
    except Exception as e:
        return {
            "connected": False,
            "site_url": creds["site_url"],
            "error": str(e),
        }
