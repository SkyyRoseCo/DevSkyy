"""Integration tests for auth API endpoints via ASGI client.

Tests the full HTTP request/response cycle for:
- POST /api/v1/auth/register
- POST /api/v1/auth/token
- GET /api/v1/auth/me
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
"""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from database.db import db_manager


@pytest.fixture
async def client():
    """ASGI test client with fresh in-memory database and reset rate limiter."""
    from main_enterprise import app

    # Reset rate limiter state so tests don't hit 429
    from security.rate_limiting import rate_limiter

    rate_limiter.sliding_windows.clear()
    rate_limiter.token_buckets.clear()

    # Reset singleton for test isolation
    if db_manager._engine:
        await db_manager.close()
        db_manager._instance = None

    from database.db import DatabaseConfig, DatabaseManager

    mgr = DatabaseManager()
    await mgr.initialize(DatabaseConfig(url="sqlite+aiosqlite:///:memory:"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await mgr.close()
    mgr._instance = None


async def _register(client, username=None, email=None, password="StrongP@ss1"):
    username = username or f"user_{uuid.uuid4().hex[:8]}"
    email = email or f"{username}@test.co"
    return await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


class TestRegisterRoleNotSelfAssignable:
    @pytest.mark.asyncio
    async def test_client_supplied_role_is_ignored(self, client):
        from security.jwt_oauth2_auth import jwt_manager

        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": f"esc_{uuid.uuid4().hex[:8]}",
                "email": f"esc_{uuid.uuid4().hex[:8]}@test.co",
                "password": "StrongP@ss1",
                "roles": ["super_admin"],
            },
        )
        assert resp.status_code == 201, resp.text
        payload = jwt_manager.validate_token(resp.json()["access_token"])
        assert [str(r) for r in payload.roles] == ["api_user"]


class TestRegisterEndpoint:
    @pytest.mark.asyncio
    async def test_register_success(self, client):
        resp = await _register(client, "newuser", "new@test.co")
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_id"]
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["message"] == "User registered successfully"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client):
        await _register(client, "dupuser", "dup1@test.co")
        resp = await _register(client, "dupuser", "dup2@test.co")
        assert resp.status_code == 409
        body = resp.json()
        msg = body.get("detail") or body.get("message", "")
        assert "Username" in msg

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        await _register(client, "user1", "same@test.co")
        resp = await _register(client, "user2", "same@test.co")
        assert resp.status_code == 409
        body = resp.json()
        msg = body.get("detail") or body.get("message", "")
        assert "Email" in msg

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "weakuser",
                "email": "weak@test.co",
                "password": "weak",
            },
        )
        assert resp.status_code == 422  # Validation error


class TestLoginEndpoint:
    @pytest.mark.asyncio
    async def test_login_success(self, client):
        await _register(client, "loginuser", "login@test.co", "StrongP@ss1")
        resp = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "loginuser",
                "password": "StrongP@ss1",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        await _register(client, "wrongpw", "wrong@test.co")
        resp = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "wrongpw",
                "password": "WrongPass!1",
            },
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        resp = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "ghost",
                "password": "GhostP@ss1",
            },
        )
        assert resp.status_code == 401


class TestMeEndpoint:
    @pytest.mark.asyncio
    async def test_me_authenticated(self, client):
        reg = await _register(client, "meuser", "me@test.co")
        token = reg.json()["access_token"]
        resp = await client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"]
        assert "roles" in data

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid.token.here",
            },
        )
        assert resp.status_code == 401


class TestRefreshEndpoint:
    @pytest.mark.asyncio
    async def test_refresh_success(self, client):
        reg = await _register(client, "refreshuser", "refresh@test.co")
        refresh = reg.json()["refresh_token"]
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"]

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid.refresh.token",
            },
        )
        assert resp.status_code == 401


class TestLogoutEndpoint:
    @pytest.mark.asyncio
    async def test_logout_success(self, client):
        reg = await _register(client, "logoutuser", "logout@test.co")
        access = reg.json()["access_token"]
        refresh = reg.json()["refresh_token"]
        resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh},
            headers={"Authorization": f"Bearer {access}"},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Successfully logged out"

    @pytest.mark.asyncio
    async def test_logout_unauthenticated(self, client):
        resp = await client.post(
            "/api/v1/auth/logout",
            json={
                "refresh_token": "some.token",
            },
        )
        assert resp.status_code == 401
