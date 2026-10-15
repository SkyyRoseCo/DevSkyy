"""
JWT/OAuth2 Authentication System
================================

Production-grade authentication following RFC 7519 and OWASP guidelines.

Standards:
- RFC 7519: JSON Web Token (JWT)
- RFC 6749: OAuth 2.0 Authorization Framework
- OWASP Authentication Cheat Sheet
- OWASP Password Storage Cheat Sheet

Features:
- JWT access and refresh tokens (HS512)
- Argon2id password hashing (OWASP recommended)
- Token rotation and family tracking
- Token blacklisting for revocation
- Rate limiting for brute force protection
- RBAC with role hierarchy

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import os
import secrets
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from functools import wraps
from typing import Any, TypeVar

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# FastAPI imports needed at module level for Python 3.14+ annotation resolution
# (used in router endpoint type annotations evaluated at module load time)
from fastapi import Request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, EmailStr, Field, field_validator

try:
    import redis
    from redis import Redis
except ImportError:
    redis = None
    Redis = None

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


def _require_secret(env_var: str) -> str:
    """Return the env var value, or an ephemeral key with a loud warning.

    In production (ENVIRONMENT=production), missing secrets raise immediately.
    In development, an ephemeral key is generated with a warning so local
    workflows aren't blocked.
    """
    value = os.getenv(env_var)
    if value:
        return value
    if os.getenv("ENVIRONMENT", "").lower() == "production":
        raise RuntimeError(
            f"CRITICAL: {env_var} is not set. "
            f"Set {env_var} before starting the application in production."
        )
    ephemeral = secrets.token_urlsafe(64)
    logger.warning(
        "%s not set. Using ephemeral key — tokens will be invalid after restart. "
        "Set %s for production.",
        env_var,
        env_var,
    )
    return ephemeral


@dataclass
class JWTConfig:
    """
    JWT Configuration - All secrets from environment variables.

    Security Notes:
    - Never hardcode secrets
    - Use strong random keys (512-bit for HS512)
    - Short access token lifetime (15 min)
    - Validate all claims
    """

    # SECRET KEYS - Must be set via environment variables in production
    secret_key: str = field(default_factory=lambda: _require_secret("JWT_SECRET_KEY"))
    refresh_secret_key: str = field(
        default_factory=lambda: _require_secret("JWT_REFRESH_SECRET_KEY")
    )

    # Algorithm - HS512 for HMAC with SHA-512
    algorithm: str = "HS512"

    # Token expiration times (RFC 7519 compliant)
    access_token_expire_minutes: int = 15  # Short-lived for security
    refresh_token_expire_days: int = 7  # Longer for UX

    # Issuer and audience claims
    issuer: str = "devskyy-platform"
    audience: str = "devskyy-api"

    # Security settings
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15

    # Token family settings for rotation
    max_token_family_size: int = 100


# =============================================================================
# Enums and Models
# =============================================================================


class UserRole(StrEnum):
    """RBAC Roles - ordered by privilege level."""

    SUPER_ADMIN = "super_admin"  # Full system access
    ADMIN = "admin"  # Administrative access
    DEVELOPER = "developer"  # API and development access
    API_USER = "api_user"  # Standard API access
    READ_ONLY = "read_only"  # Read-only access
    GUEST = "guest"  # Minimal access


# Role hierarchy (higher can do everything lower can)
ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.SUPER_ADMIN: 100,
    UserRole.ADMIN: 80,
    UserRole.DEVELOPER: 60,
    UserRole.API_USER: 40,
    UserRole.READ_ONLY: 20,
    UserRole.GUEST: 0,
}


class TokenType(StrEnum):
    """Token types for different purposes."""

    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    VERIFY_EMAIL = "verify_email"
    API_KEY = "api_key"


@dataclass
class TokenPayload:
    """Decoded token payload structure."""

    sub: str  # Subject (user_id)
    jti: str  # JWT ID (unique identifier)
    type: TokenType  # Token type
    roles: list[str]  # User roles
    family_id: str | None = None  # Token family for rotation tracking
    tier: str = "free"  # Subscription tier (free, starter, pro, enterprise)
    exp: datetime | None = None  # Expiration time
    iat: datetime | None = None  # Issued at time
    iss: str | None = None  # Issuer
    aud: str | None = None  # Audience

    def has_role(self, role: UserRole) -> bool:
        """Check if payload has a specific role."""
        return role.value in self.roles

    def has_any_role(self, roles: set[UserRole]) -> bool:
        """Check if payload has any of the specified roles."""
        role_values = {r.value for r in roles}
        return bool(set(self.roles) & role_values)

    def get_highest_role(self) -> UserRole | None:
        """Get the highest privilege role."""
        max_level = -1
        highest = None

        for role_str in self.roles:
            try:
                role = UserRole(role_str)
                level = ROLE_HIERARCHY.get(role, 0)
                if level > max_level:
                    max_level = level
                    highest = role
            except ValueError:
                continue

        return highest


# =============================================================================
# Pydantic Models for API
# =============================================================================


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires
    refresh_expires_in: int  # Seconds until refresh token expires
    scope: str | None = None


class UserCreate(BaseModel):
    """User registration model with OWASP password validation."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    roles: list[UserRole] = Field(default=[UserRole.API_USER])

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """OWASP password strength validation."""
        errors = []

        if len(v) < 8:
            errors.append("at least 8 characters")
        if not any(c.isupper() for c in v):
            errors.append("uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            errors.append("special character")

        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")

        return v


class UserInDB(BaseModel):
    """User model as stored in database."""

    id: str
    username: str
    email: str
    hashed_password: str
    roles: list[str] = Field(default=[UserRole.API_USER.value])
    is_active: bool = True
    is_verified: bool = False
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.locked_until is None:
            return False
        return datetime.now(UTC) < self.locked_until


class TokenRequest(BaseModel):
    """Token request model for OAuth2 login."""

    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    """Token refresh request model."""

    refresh_token: str


# =============================================================================
# Password Hashing
# =============================================================================


class PasswordManager:
    """
    Secure password hashing using Argon2id.

    Reference: OWASP Password Storage Cheat Sheet
    https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

    Argon2id Parameters (OWASP 2023):
    - Memory: 64 MiB minimum
    - Iterations: 2 minimum
    - Parallelism: 1
    """

    def __init__(self) -> None:
        # Argon2id - winner of Password Hashing Competition
        self.argon2_hasher = PasswordHasher(
            time_cost=2,  # Number of iterations
            memory_cost=65536,  # 64 MiB memory
            parallelism=1,  # Parallel threads
            hash_len=32,  # Output hash length
            salt_len=16,  # Salt length
        )

        # BCrypt fallback for legacy systems (bcrypt library directly: passlib's
        # bcrypt backend probes with a >72-byte secret, which bcrypt 5.x rejects).
        self.bcrypt_rounds = 12

    def hash_password(self, password: str, use_argon2: bool = True) -> str:
        """Hash password using Argon2id (preferred) or BCrypt."""
        if use_argon2:
            return self.argon2_hasher.hash(password)
        return bcrypt.hashpw(
            self._bcrypt_secret(password), bcrypt.gensalt(rounds=self.bcrypt_rounds)
        ).decode("ascii")

    @staticmethod
    def _bcrypt_secret(password: str) -> bytes:
        """BCrypt reads at most 72 bytes; truncate as passlib did so old hashes verify."""
        return password.encode("utf-8")[:72]

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            # Try Argon2 first
            if hashed_password.startswith("$argon2"):
                self.argon2_hasher.verify(hashed_password, password)
                return True
            # Fall back to BCrypt
            return bcrypt.checkpw(self._bcrypt_secret(password), hashed_password.encode("ascii"))
        except VerifyMismatchError:
            return False
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if password needs rehashing (e.g., algorithm upgrade)."""
        if hashed_password.startswith("$argon2"):
            return self.argon2_hasher.check_needs_rehash(hashed_password)
        # BCrypt passwords should be migrated to Argon2
        return True


# =============================================================================
# Token Blacklist
# =============================================================================


class TokenBlacklist:
    """
    Token blacklist for revocation.

    In production, use Redis or database for persistence.
    Capped at 10,000 entries to prevent unbounded memory growth.
    """

    MAX_ENTRIES = 10_000

    def __init__(self) -> None:
        self._blacklist: dict[str, datetime] = {}  # jti -> expiry
        self._revoked_families: set[str] = set()  # Revoked token families

    def add(self, jti: str, expires_at: datetime) -> None:
        """Add token to blacklist."""
        self._blacklist[jti] = expires_at
        self._cleanup()
        # LRU eviction if over capacity
        while len(self._blacklist) > self.MAX_ENTRIES:
            oldest_jti = min(self._blacklist, key=self._blacklist.get)  # type: ignore[arg-type]
            del self._blacklist[oldest_jti]

    def revoke_family(self, family_id: str) -> None:
        """Revoke all tokens in a family (e.g., on security breach)."""
        self._revoked_families.add(family_id)

    def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted."""
        return jti in self._blacklist

    def is_family_revoked(self, family_id: str) -> bool:
        """Check if token family is revoked."""
        return family_id in self._revoked_families

    def _cleanup(self) -> None:
        """Remove expired entries."""
        now = datetime.now(UTC)
        expired = [jti for jti, exp in self._blacklist.items() if exp < now]
        for jti in expired:
            del self._blacklist[jti]


class RedisTokenBlacklist(TokenBlacklist):
    """
    Redis-backed token blacklist for distributed systems.

    Provides distributed token revocation with automatic expiration.
    Implements the same interface as TokenBlacklist for drop-in replacement.
    """

    def __init__(self, redis_client: Redis | None = None) -> None:
        """
        Initialize Redis-backed token blacklist.

        Args:
            redis_client: Redis client instance. If None, creates a new connection.

        Raises:
            RuntimeError: If Redis module is not installed.
        """
        if redis is None or Redis is None:
            msg = "redis package required for RedisTokenBlacklist. Install with: pip install redis"
            raise RuntimeError(msg)

        if redis_client is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self._redis = redis.from_url(redis_url, decode_responses=True)
        else:
            self._redis = redis_client

        # Key prefixes for Redis
        self._blacklist_prefix = "token_blacklist:"
        self._revoked_families_prefix = "token_families_revoked:"

    def add(self, jti: str, expires_at: datetime) -> None:
        """
        Add token to Redis blacklist with automatic expiration.

        Args:
            jti: Token ID (JWT 'jti' claim)
            expires_at: Token expiration datetime
        """
        key = f"{self._blacklist_prefix}{jti}"
        ttl = max(1, int((expires_at - datetime.now(UTC)).total_seconds()))
        self._redis.setex(key, ttl, "1")

    def revoke_family(self, family_id: str) -> None:
        """
        Revoke all tokens in a family.

        Args:
            family_id: Token family identifier
        """
        key = f"{self._revoked_families_prefix}{family_id}"
        # Set with 7-day TTL (refresh token lifetime)
        self._redis.setex(key, 7 * 24 * 60 * 60, "1")

    def is_blacklisted(self, jti: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            jti: Token ID to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        key = f"{self._blacklist_prefix}{jti}"
        return bool(self._redis.exists(key))

    def is_family_revoked(self, family_id: str) -> bool:
        """
        Check if token family is revoked.

        Args:
            family_id: Family ID to check

        Returns:
            True if family is revoked, False otherwise
        """
        key = f"{self._revoked_families_prefix}{family_id}"
        return bool(self._redis.exists(key))

    def _cleanup(self) -> None:
        """Not needed for Redis (automatic expiration via TTL)."""
        pass


# =============================================================================
# Rate Limiter
# =============================================================================


class RateLimiter:
    """
    Simple rate limiter for brute force protection.

    In production, use Redis for distributed rate limiting.
    """

    MAX_KEYS = 10_000

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,
    ) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[datetime]] = defaultdict(list)

    def _evict_if_needed(self) -> None:
        """Evict oldest keys if over capacity."""
        while len(self._attempts) > self.MAX_KEYS:
            oldest_key = next(iter(self._attempts))
            del self._attempts[oldest_key]

    def is_allowed(self, key: str) -> bool:
        """Check if action is allowed."""
        self._cleanup(key)
        return len(self._attempts[key]) < self.max_attempts

    def record_attempt(self, key: str) -> None:
        """Record an attempt."""
        self._cleanup(key)
        self._attempts[key].append(datetime.now(UTC))
        self._evict_if_needed()

    def get_remaining_attempts(self, key: str) -> int:
        """Get remaining attempts."""
        self._cleanup(key)
        return max(0, self.max_attempts - len(self._attempts[key]))

    def get_reset_time(self, key: str) -> datetime | None:
        """Get time when rate limit resets."""
        if not self._attempts[key]:
            return None
        oldest = min(self._attempts[key])
        return oldest + timedelta(seconds=self.window_seconds)

    def _cleanup(self, key: str) -> None:
        """Remove expired attempts."""
        cutoff = datetime.now(UTC) - timedelta(seconds=self.window_seconds)
        self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]


# =============================================================================
# JWT Manager
# =============================================================================


class JWTManager:
    """
    JWT token management with RFC 7519 compliance.

    Features:
    - Access and refresh token generation
    - Token validation with all claim checks
    - Token rotation with family tracking
    - Blacklisting for revocation

    Usage:
        manager = JWTManager()

        # Create tokens
        tokens = manager.create_token_pair(user_id="123", roles=["api_user"])

        # Validate token
        payload = manager.validate_token(tokens.access_token)

        # Refresh tokens
        new_tokens = manager.refresh_tokens(tokens.refresh_token)
    """

    def __init__(
        self,
        config: JWTConfig | None = None,
        blacklist: TokenBlacklist | None = None,
    ) -> None:
        self.config = config or JWTConfig()
        self.blacklist = blacklist or TokenBlacklist()

        # Warn if using default keys
        if "JWT_SECRET_KEY" not in os.environ:
            logger.warning(
                "JWT_SECRET_KEY not set. Using ephemeral key - "
                "tokens will be invalid after restart. "
                "Set JWT_SECRET_KEY for production."
            )

    def create_access_token(
        self,
        user_id: str,
        roles: list[str],
        family_id: str | None = None,
        tier: str = "free",
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create access token."""
        now = datetime.now(UTC)
        expires = now + timedelta(minutes=self.config.access_token_expire_minutes)

        claims = {
            "sub": user_id,
            "jti": secrets.token_urlsafe(16),
            "type": TokenType.ACCESS.value,
            "roles": roles,
            "family_id": family_id or secrets.token_urlsafe(8),
            "tier": tier,
            "iss": self.config.issuer,
            "aud": self.config.audience,
            "iat": now,
            "exp": expires,
        }

        if additional_claims:
            claims.update(additional_claims)

        return jwt.encode(
            claims,
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

    def create_refresh_token(
        self,
        user_id: str,
        roles: list[str],
        family_id: str,
        tier: str = "free",
    ) -> str:
        """Create refresh token."""
        now = datetime.now(UTC)
        expires = now + timedelta(days=self.config.refresh_token_expire_days)

        claims = {
            "sub": user_id,
            "jti": secrets.token_urlsafe(16),
            "type": TokenType.REFRESH.value,
            "roles": roles,
            "family_id": family_id,
            "tier": tier,
            "iss": self.config.issuer,
            "aud": self.config.audience,
            "iat": now,
            "exp": expires,
        }

        return jwt.encode(
            claims,
            self.config.refresh_secret_key,
            algorithm=self.config.algorithm,
        )

    def create_token_pair(
        self,
        user_id: str,
        roles: list[str],
        tier: str = "free",
        additional_claims: dict[str, Any] | None = None,
    ) -> TokenResponse:
        """Create access and refresh token pair."""
        family_id = secrets.token_urlsafe(8)

        access_token = self.create_access_token(
            user_id=user_id,
            roles=roles,
            family_id=family_id,
            tier=tier,
            additional_claims=additional_claims,
        )

        refresh_token = self.create_refresh_token(
            user_id=user_id,
            roles=roles,
            family_id=family_id,
            tier=tier,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_expire_minutes * 60,
            refresh_expires_in=self.config.refresh_token_expire_days * 86400,
        )

    def validate_token(
        self,
        token: str,
        expected_type: TokenType = TokenType.ACCESS,
    ) -> TokenPayload:
        """
        Validate token and return payload.

        Raises:
            InvalidTokenError: If token is invalid
            ExpiredSignatureError: If token is expired
        """
        secret = (
            self.config.refresh_secret_key
            if expected_type == TokenType.REFRESH
            else self.config.secret_key
        )

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                audience=self.config.audience,
            )
        except ExpiredSignatureError:
            raise
        except InvalidTokenError as e:
            raise InvalidTokenError(f"Token validation failed: {e}") from e

        # Validate token type
        if payload.get("type") != expected_type.value:
            raise InvalidTokenError(f"Invalid token type: expected {expected_type.value}")

        # Check blacklist
        jti = payload.get("jti")
        if jti and self.blacklist.is_blacklisted(jti):
            raise InvalidTokenError("Token has been revoked")

        # Check family revocation
        family_id = payload.get("family_id")
        if family_id and self.blacklist.is_family_revoked(family_id):
            raise InvalidTokenError("Token family has been revoked")

        return TokenPayload(
            sub=payload["sub"],
            jti=payload.get("jti", ""),
            type=TokenType(payload["type"]),
            roles=payload.get("roles", []),
            family_id=payload.get("family_id"),
            tier=payload.get("tier", "free"),
            exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
            iat=datetime.fromtimestamp(payload["iat"], tz=UTC),
            iss=payload.get("iss"),
            aud=payload.get("aud"),
        )

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Refresh tokens using refresh token.

        Implements token rotation - old refresh token is blacklisted.
        """
        # Validate refresh token
        payload = self.validate_token(refresh_token, TokenType.REFRESH)

        # Blacklist old refresh token
        if payload.exp:
            self.blacklist.add(payload.jti, payload.exp)

        # Create new token pair with same family and tier
        return TokenResponse(
            access_token=self.create_access_token(
                user_id=payload.sub,
                roles=payload.roles,
                family_id=payload.family_id,
                tier=payload.tier,
            ),
            refresh_token=self.create_refresh_token(
                user_id=payload.sub,
                roles=payload.roles,
                family_id=payload.family_id or secrets.token_urlsafe(8),
                tier=payload.tier,
            ),
            expires_in=self.config.access_token_expire_minutes * 60,
            refresh_expires_in=self.config.refresh_token_expire_days * 86400,
        )

    def revoke_token(self, token: str) -> None:
        """Revoke a specific token."""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
                options={"verify_exp": False},
            )
            jti = payload.get("jti")
            exp = datetime.fromtimestamp(payload.get("exp", 0), tz=UTC)
            if jti:
                self.blacklist.add(jti, exp)
        except Exception as e:
            logger.error(f"Error revoking token: {e}")

    def revoke_all_user_tokens(self, family_id: str) -> None:
        """Revoke all tokens for a user (e.g., password change, logout all)."""
        self.blacklist.revoke_family(family_id)


# =============================================================================
# FastAPI Dependencies
# =============================================================================

# OAuth2 scheme for token extraction - initialized lazily
_oauth2_scheme = None

T = TypeVar("T")


def _get_oauth2_scheme():
    """Lazily initialize OAuth2 scheme to avoid import issues."""
    global _oauth2_scheme
    if _oauth2_scheme is None:
        from fastapi.security import OAuth2PasswordBearer

        _oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
    return _oauth2_scheme


def _extract_token_from_header(auth_header: str) -> str | None:
    """Extract token from Authorization header value."""
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def get_current_user_dependency():
    """
    Create the get_current_user dependency with proper Header injection.

    This factory function is needed because we need to use Header() as a default
    value, which requires importing from fastapi at definition time.
    """
    from fastapi import Header, HTTPException, status

    async def _get_current_user(
        authorization: str | None = Header(None, alias="Authorization"),
    ) -> TokenPayload:
        """
        FastAPI dependency to get current authenticated user.

        Usage:
            @app.get("/me")
            async def get_me(user: TokenPayload = Depends(get_current_user)):
                return {"user_id": user.sub}
        """
        # Extract token from Authorization header
        token = _extract_token_from_header(authorization or "")

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            return jwt_manager.validate_token(token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    return _get_current_user


# Create the dependency - this is what gets exported
get_current_user = get_current_user_dependency()


def require_roles(*required_roles: UserRole) -> Callable:
    """
    Decorator/dependency to require specific roles.

    Usage:
        @app.delete("/admin/users/{id}")
        @require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
        async def delete_user(id: str, user: TokenPayload = Depends(get_current_user)):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Get user from kwargs (should be injected by get_current_user)
            user = kwargs.get("user")
            if not user:
                from fastapi import HTTPException, status

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )

            # Check if user has any required role
            if not user.has_any_role(set(required_roles)):
                from fastapi import HTTPException, status

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {[r.value for r in required_roles]}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def _create_role_checker_class():
    """Factory to create RoleChecker class with proper FastAPI Header injection."""
    from fastapi import Header, HTTPException, status

    class _RoleChecker:
        """
        FastAPI dependency for role-based access control.

        Usage:
            @app.get("/admin/users", dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
            async def get_users():
                ...

            # Or with multiple roles:
            @app.get("/admin/stats", dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.SUPER_ADMIN]))])
            async def get_stats():
                ...
        """

        def __init__(self, allowed_roles: list[UserRole]):
            """
            Initialize role checker with allowed roles.

            Args:
                allowed_roles: List of UserRole enums that are allowed access
            """
            self.allowed_roles = allowed_roles

        async def __call__(
            self, authorization: str | None = Header(None, alias="Authorization")
        ) -> TokenPayload:
            """
            Check if the current user has any of the allowed roles.

            Args:
                authorization: Authorization header value (injected by FastAPI)

            Returns:
                TokenPayload if user has required role

            Raises:
                HTTPException: 401 if not authenticated, 403 if insufficient permissions
            """
            # Extract token from Authorization header
            token = _extract_token_from_header(authorization or "")

            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            try:
                user = jwt_manager.validate_token(token)
            except ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except InvalidTokenError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e),
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user has any of the allowed roles
            if not user.has_any_role(set(self.allowed_roles)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {[r.value for r in self.allowed_roles]}",
                )

            return user

    return _RoleChecker


# Create the RoleChecker class - this is what gets exported
RoleChecker = _create_role_checker_class()


def service_or_user_auth_dependency(service_token_env: str = "WORDPRESS_SYNC_SERVICE_TOKEN"):
    """Dependency authorizing EITHER a valid Bearer JWT (any authenticated user)
    OR a machine-to-machine service token.

    Background workers (e.g. the BullMQ queue worker) call state-changing routes
    with no user session — they present X-Service-Token, compared constant-time
    against os.environ[service_token_env]. Fails closed: if the env token is unset
    the service-token path is disabled and only a valid JWT is accepted; a caller
    with neither always gets 401. Never reveals which path failed.
    """
    from fastapi import Header, HTTPException, status

    async def _service_or_user(
        authorization: str | None = Header(None, alias="Authorization"),
        x_service_token: str | None = Header(None, alias="X-Service-Token"),
    ) -> TokenPayload | dict[str, str]:
        # Machine-to-machine path: constant-time match against the configured token.
        expected = os.getenv(service_token_env, "")
        if x_service_token and expected and secrets.compare_digest(x_service_token, expected):
            return {"sub": "service", "auth": "service_token", "token_env": service_token_env}

        # User path: a valid Bearer JWT.
        token = _extract_token_from_header(authorization or "")
        if token:
            try:
                return jwt_manager.validate_token(token)
            except (ExpiredSignatureError, InvalidTokenError):
                pass  # fall through to the generic 401 — never leak which path failed

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _service_or_user


# Create the dependency - this is what gets exported
service_or_user_auth = service_or_user_auth_dependency()


# =============================================================================
# Module-level Instances
# =============================================================================

# Default instances for convenience
jwt_manager = JWTManager()
password_manager = PasswordManager()

# Module-level singleton — uses Redis if REDIS_URL is set
_redis_url = os.getenv("REDIS_URL", "")
if _redis_url and redis is not None:
    try:
        _redis_client = redis.from_url(_redis_url, decode_responses=True)
        token_blacklist = RedisTokenBlacklist(redis_client=_redis_client)
    except Exception as _e:
        logger.warning(f"Failed to initialize Redis token blacklist: {_e}")
        token_blacklist = TokenBlacklist()
else:
    token_blacklist = TokenBlacklist()


# =============================================================================
# Authentication Router
# =============================================================================


def _create_auth_router():
    """Create authentication router with endpoints."""
    from fastapi import APIRouter, Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordRequestForm as _OAuth2Form

    router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

    # Note: TokenRequest and TokenRefreshRequest are defined at module level
    # for Python 3.14+ annotation resolution compatibility

    async def verify_user_credentials(username: str, password: str) -> tuple[str, list[str]] | None:
        """
        Verify user credentials against database.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Tuple of (user_id, roles) if valid, None if invalid
        """
        try:
            from database.db import UserRepository, get_db

            # Get database session
            async for db in get_db():
                repo = UserRepository(db)

                # Try username first, then email
                user = await repo.get_by_username(username)
                if not user:
                    user = await repo.get_by_email(username)

                if not user:
                    logger.warning(f"User not found: {username}")
                    return None

                if not user.is_active:
                    logger.warning(f"Inactive user attempted login: {username}")
                    return None

                # Verify password
                if not password_manager.verify_password(password, user.hashed_password):
                    logger.warning(f"Invalid password for user: {username}")
                    return None

                # Update last login
                user.last_login = datetime.now(UTC)
                await db.commit()

                return (user.id, [user.role])

        except ImportError:
            # Database module not available - fall back to dev mode
            logger.warning("Database not configured - using development mode authentication")
            return None
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None

    # Rate limiter for login attempts (brute force protection)
    login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)

    @router.post("/token", response_model=TokenResponse)
    async def login_for_access_token(request: Request, form_data=Depends(_OAuth2Form)):
        """
        OAuth2 compatible token login with brute force protection.

        - **username**: User email or username
        - **password**: User password

        Returns access and refresh tokens.

        Rate Limit: 5 attempts per 5 minutes per IP/username
        """
        # Get client identifier for rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"login:{client_ip}:{form_data.username}"

        # Check rate limit before attempting authentication
        if not login_rate_limiter.is_allowed(rate_limit_key):
            logger.warning(f"Rate limit exceeded for login: {form_data.username} from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": "300"},
            )

        # Verify user credentials against database
        user_info = await verify_user_credentials(form_data.username, form_data.password)

        if not user_info:
            # Record failed attempt for rate limiting
            login_rate_limiter.record_attempt(rate_limit_key)

            # Check if we're in development mode (allow any credentials)
            # SECURITY: Restrict dev mode to localhost only and block in production
            dev_mode_enabled = os.environ.get("DEVSKYY_DEV_MODE", "").lower() == "true"
            environment = os.environ.get("ENVIRONMENT", "development").lower()
            is_localhost = client_ip in ("127.0.0.1", "localhost", "::1")

            if dev_mode_enabled and environment != "production" and is_localhost:
                logger.warning(
                    "DEV MODE: Accepting credentials (localhost only)",
                    extra={"client_ip": client_ip, "username": form_data.username},
                )
                user_info = (form_data.username, ["api_user"])
            elif dev_mode_enabled and environment == "production":
                logger.error(
                    "SECURITY: Dev mode attempted in production - BLOCKED",
                    extra={"client_ip": client_ip},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            elif dev_mode_enabled and not is_localhost:
                logger.warning(
                    "SECURITY: Dev mode auth attempted from non-localhost - BLOCKED",
                    extra={"client_ip": client_ip},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        user_id, roles = user_info

        # Create token pair
        tokens = jwt_manager.create_token_pair(
            user_id=user_id,
            roles=roles,
        )

        return tokens

    @router.post("/refresh", response_model=TokenResponse)
    async def refresh_access_token(request: TokenRefreshRequest):
        """
        Refresh access token using refresh token.

        Implements token rotation for security - old refresh token is invalidated.
        """
        try:
            new_tokens = jwt_manager.refresh_tokens(request.refresh_token)
            return new_tokens
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    @router.post("/logout")
    async def logout(
        request: TokenRefreshRequest,
        user: TokenPayload = Depends(get_current_user),
    ):
        """
        Logout user by revoking refresh token.

        The refresh token is added to the blacklist.
        """
        try:
            # Validate and blacklist the refresh token
            payload = jwt_manager.validate_token(request.refresh_token, TokenType.REFRESH)
            if payload.exp:
                token_blacklist.add(payload.jti, payload.exp)
            return {"message": "Successfully logged out"}
        except (ExpiredSignatureError, InvalidTokenError):
            # Token already invalid, consider logout successful
            return {"message": "Successfully logged out"}

    @router.get("/me")
    async def get_current_user_info(user: TokenPayload = Depends(get_current_user)):
        """Get current authenticated user information."""
        return {
            "user_id": user.sub,
            "roles": user.roles,
            "token_type": user.type.value,
            "issued_at": user.iat.isoformat() if user.iat else None,
            "expires_at": user.exp.isoformat() if user.exp else None,
        }

    @router.post("/register", status_code=status.HTTP_201_CREATED)
    async def register_user(user_data: UserCreate):
        """
        Register a new user account.

        - Validates password strength (OWASP rules)
        - Hashes password with Argon2id
        - Creates user in database
        - Returns access + refresh tokens
        """
        import uuid

        try:
            from database.db import UserRepository, get_db

            async for db in get_db():
                repo = UserRepository(db)

                # Check if username or email already exists
                existing = await repo.get_by_username(user_data.username)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Username already registered",
                    )
                existing = await repo.get_by_email(user_data.email)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already registered",
                    )

                # Hash password and create user
                hashed = password_manager.hash_password(user_data.password)
                user_id = str(uuid.uuid4())
                # Self-registration never grants elevated roles: a client-supplied
                # `roles` would otherwise let anyone mint a SUPER_ADMIN account.
                # Elevated accounts come from database/seed_admin.py only.
                role = UserRole.API_USER.value

                from database.db import User as UserModel

                new_user = UserModel(
                    id=user_id,
                    email=user_data.email,
                    username=user_data.username,
                    hashed_password=hashed,
                    role=role,
                    is_active=True,
                    is_verified=False,
                )
                db.add(new_user)
                await db.commit()

                # Generate tokens
                tokens = jwt_manager.create_token_pair(
                    user_id=user_id,
                    roles=[role],
                )

                logger.info(f"New user registered: {user_data.username}")
                return {
                    "message": "User registered successfully",
                    "user_id": user_id,
                    **tokens.model_dump(),
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed",
            )

    return router


# Create the auth router
auth_router = _create_auth_router()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Config
    "JWTConfig",
    # Enums
    "UserRole",
    "TokenType",
    "ROLE_HIERARCHY",
    # Models
    "TokenPayload",
    "TokenResponse",
    "UserCreate",
    "UserInDB",
    # Classes
    "PasswordManager",
    "JWTManager",
    "TokenBlacklist",
    "RateLimiter",
    "RoleChecker",
    # Dependencies
    "get_current_user",
    "require_roles",
    "service_or_user_auth",
    "service_or_user_auth_dependency",
    # Routers
    "auth_router",
    # Instances
    "jwt_manager",
    "password_manager",
    "token_blacklist",
]
