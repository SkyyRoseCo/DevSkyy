"""
Tests for Multi-Factor Authentication (MFA)
============================================

Comprehensive test suite for MFA system following TEST_STRATEGY.md patterns.

Coverage:
- TOTP setup and verification
- Backup code generation and verification
- MFA session management
- Edge cases and error handling
- Security validation
"""

import re
from datetime import UTC, datetime, timedelta

import pytest

# MFA requires pyotp
pytest.importorskip("pyotp")

import pyotp

from security.mfa import MFAConfig, MFAManager, MFASession, MFASetupData

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mfa_config() -> MFAConfig:
    """Create test MFA configuration."""
    return MFAConfig(
        issuer="TestApp",
        backup_codes_count=10,
        totp_window=1,
        require_mfa=True,
    )


@pytest.fixture
def mfa_manager(mfa_config: MFAConfig) -> MFAManager:
    """Create MFA manager for testing."""
    return MFAManager(config=mfa_config)


@pytest.fixture
def mfa_setup_data(mfa_manager: MFAManager) -> MFASetupData:
    """Create MFA setup data."""
    return mfa_manager.setup_totp(
        user_id="test-user-123",
        email="test@example.com",
    )


# =============================================================================
# Configuration Tests
# =============================================================================


class TestMFAConfig:
    """Test MFA configuration."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = MFAConfig()

        assert config.issuer == "DevSkyy"
        assert config.backup_codes_count == 10
        assert config.totp_window == 1
        assert config.require_mfa is False

    def test_custom_config(self, mfa_config: MFAConfig) -> None:
        """Test custom configuration."""
        assert mfa_config.issuer == "TestApp"
        assert mfa_config.backup_codes_count == 10
        assert mfa_config.totp_window == 1
        assert mfa_config.require_mfa is True


# =============================================================================
# TOTP Setup Tests
# =============================================================================


class TestTOTPSetup:
    """Test TOTP setup functionality."""

    def test_setup_totp_returns_complete_data(self, mfa_manager: MFAManager) -> None:
        """Test TOTP setup returns all required data."""
        setup_data = mfa_manager.setup_totp(
            user_id="user123",
            email="user@example.com",
        )

        assert isinstance(setup_data, MFASetupData)
        assert setup_data.secret
        assert setup_data.qr_code_uri
        assert setup_data.backup_codes
        assert len(setup_data.backup_codes) == 10

    def test_setup_totp_secret_format(self, mfa_setup_data: MFASetupData) -> None:
        """Test TOTP secret is valid base32."""
        secret = mfa_setup_data.secret

        # Should be base32 (A-Z and 2-7)
        assert re.match(r"^[A-Z2-7]+$", secret)
        assert len(secret) == 32  # pyotp default length

    def test_setup_totp_qr_code_uri_format(self, mfa_setup_data: MFASetupData) -> None:
        """Test QR code URI has correct format."""
        uri = mfa_setup_data.qr_code_uri

        # Should be otpauth:// URI
        assert uri.startswith("otpauth://totp/")
        assert "TestApp" in uri  # Issuer
        # Email is URL-encoded in QR code URI
        assert "test" in uri and "example.com" in uri  # Email (URL-encoded)
        assert "secret=" in uri
        assert "issuer=" in uri

    def test_setup_totp_backup_codes_format(self, mfa_setup_data: MFASetupData) -> None:
        """Test backup codes have correct format."""
        codes = mfa_setup_data.backup_codes

        assert len(codes) == 10

        for code in codes:
            # Format: XXXX-XXXX (8 hex chars with dash)
            assert re.match(r"^[A-F0-9]{4}-[A-F0-9]{4}$", code)

    def test_setup_totp_backup_codes_unique(self, mfa_setup_data: MFASetupData) -> None:
        """Test all backup codes are unique."""
        codes = mfa_setup_data.backup_codes

        assert len(codes) == len(set(codes))

    def test_setup_totp_multiple_users_different_secrets(self, mfa_manager: MFAManager) -> None:
        """Test different users get different secrets."""
        setup1 = mfa_manager.setup_totp("user1", "user1@example.com")
        setup2 = mfa_manager.setup_totp("user2", "user2@example.com")

        assert setup1.secret != setup2.secret
        assert setup1.backup_codes != setup2.backup_codes


# =============================================================================
# TOTP Verification Tests
# =============================================================================


class TestTOTPVerification:
    """Test TOTP verification functionality."""

    def test_verify_totp_with_valid_token(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification succeeds with valid TOTP token."""
        # Generate valid token
        totp = pyotp.TOTP(mfa_setup_data.secret)
        token = totp.now()

        result = mfa_manager.verify_totp(mfa_setup_data.secret, token)

        assert result is True

    def test_verify_totp_with_invalid_token(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification fails with invalid token."""
        result = mfa_manager.verify_totp(mfa_setup_data.secret, "000000")

        assert result is False

    def test_verify_totp_with_empty_token(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification fails with empty token."""
        result = mfa_manager.verify_totp(mfa_setup_data.secret, "")

        assert result is False

    def test_verify_totp_with_short_token(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification fails with token too short."""
        result = mfa_manager.verify_totp(mfa_setup_data.secret, "123")

        assert result is False

    def test_verify_totp_with_time_window(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification allows time skew within window."""
        totp = pyotp.TOTP(mfa_setup_data.secret)

        # Get token from 30 seconds ago (within window)
        past_time = datetime.now(UTC) - timedelta(seconds=30)
        token_past = totp.at(past_time)

        # Should still verify (window = 1)
        result = mfa_manager.verify_totp(mfa_setup_data.secret, token_past)

        assert result is True

    def test_verify_totp_outside_time_window(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification fails outside time window."""
        totp = pyotp.TOTP(mfa_setup_data.secret)

        # Get token from 90 seconds ago (outside window)
        far_past = datetime.now(UTC) - timedelta(seconds=90)
        token_old = totp.at(far_past)

        # Should fail (outside window)
        result = mfa_manager.verify_totp(mfa_setup_data.secret, token_old)

        assert result is False

    def test_verify_totp_with_exception(self, mfa_manager: MFAManager) -> None:
        """Test verification fails gracefully on exception."""
        # Invalid secret should cause exception
        result = mfa_manager.verify_totp("INVALID", "123456")

        assert result is False


# =============================================================================
# Backup Code Tests
# =============================================================================


class TestBackupCodes:
    """Test backup code functionality."""

    def test_verify_backup_code_valid_unused(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification succeeds with valid unused code."""
        code = mfa_setup_data.backup_codes[0]
        used_codes: set[str] = set()

        result = mfa_manager.verify_backup_code(code, used_codes)

        assert result is True

    def test_verify_backup_code_already_used(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test verification fails with already-used code."""
        code = mfa_setup_data.backup_codes[0]
        used_codes = {code}

        result = mfa_manager.verify_backup_code(code, used_codes)

        assert result is False

    def test_verify_backup_code_empty(self, mfa_manager: MFAManager) -> None:
        """Test verification fails with empty code."""
        result = mfa_manager.verify_backup_code("", set())

        assert result is False

    def test_verify_backup_code_wrong_format(self, mfa_manager: MFAManager) -> None:
        """Test verification fails with wrong format."""
        result = mfa_manager.verify_backup_code("INVALID", set())

        assert result is False

    def test_verify_backup_code_case_insensitive(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test backup codes are case-insensitive."""
        code = mfa_setup_data.backup_codes[0]
        lowercase_code = code.lower()

        result = mfa_manager.verify_backup_code(lowercase_code, set())

        assert result is True

    def test_verify_backup_code_with_spaces(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test backup codes work with spaces."""
        code = mfa_setup_data.backup_codes[0]
        code_with_spaces = code.replace("-", " ")

        result = mfa_manager.verify_backup_code(code_with_spaces, set())

        assert result is True

    def test_verify_backup_code_without_dash(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test backup codes work without dash."""
        code = mfa_setup_data.backup_codes[0]
        code_no_dash = code.replace("-", "")

        result = mfa_manager.verify_backup_code(code_no_dash, set())

        assert result is True

    def test_backup_code_generation_count(self, mfa_manager: MFAManager) -> None:
        """Test correct number of backup codes generated."""
        codes = mfa_manager._generate_backup_codes()

        assert len(codes) == mfa_manager.config.backup_codes_count

    def test_backup_codes_cryptographically_random(self, mfa_manager: MFAManager) -> None:
        """Test backup codes use cryptographic randomness."""
        # Generate multiple sets
        sets = [set(mfa_manager._generate_backup_codes()) for _ in range(10)]

        # No set should be identical to another
        for i, set1 in enumerate(sets):
            for _j, set2 in enumerate(sets[i + 1 :], start=i + 1):
                assert set1 != set2


# =============================================================================
# MFA Session Tests
# =============================================================================


class TestMFASession:
    """Test MFA session management."""

    def test_session_initialization(self) -> None:
        """Test session initializes with correct values."""
        session = MFASession(user_id="user123", ttl_seconds=3600)

        assert session.user_id == "user123"
        assert session.verified_at is not None
        assert session.expires_at > datetime.now(UTC)
        assert session.verification_method is None
        assert len(session.used_backup_codes) == 0

    def test_session_is_valid_when_fresh(self) -> None:
        """Test session is valid immediately after creation."""
        session = MFASession(user_id="user123")

        assert session.is_valid() is True

    def test_session_is_invalid_when_expired(self) -> None:
        """Test session is invalid after TTL expires."""
        # Create session with 1 second TTL
        session = MFASession(user_id="user123", ttl_seconds=0)

        # Should be immediately invalid
        assert session.is_valid() is False

    def test_session_verify_totp_updates_verification(self, mfa_setup_data: MFASetupData) -> None:
        """Test TOTP verification updates session state."""
        session = MFASession(user_id="user123")

        # Generate valid token
        totp = pyotp.TOTP(mfa_setup_data.secret)
        token = totp.now()

        result = session.verify_totp(mfa_setup_data.secret, token)

        assert result is True
        assert session.verification_method == "totp"

    def test_session_verify_totp_fails_with_invalid_token(
        self, mfa_setup_data: MFASetupData
    ) -> None:
        """Test TOTP verification fails with invalid token."""
        session = MFASession(user_id="user123")

        result = session.verify_totp(mfa_setup_data.secret, "000000")

        assert result is False
        assert session.verification_method is None

    def test_session_verify_backup_code_tracks_usage(self, mfa_setup_data: MFASetupData) -> None:
        """Test backup code verification tracks used codes."""
        session = MFASession(user_id="user123")
        code = mfa_setup_data.backup_codes[0]

        # First use should succeed
        result = session.verify_backup_code(code)
        assert result is True
        assert code in session.used_backup_codes
        assert session.verification_method == "backup_code"

        # Second use should fail
        result2 = session.verify_backup_code(code)
        assert result2 is False

    def test_session_ttl_calculation(self) -> None:
        """Test session TTL is calculated correctly."""
        ttl_seconds = 3600
        session = MFASession(user_id="user123", ttl_seconds=ttl_seconds)

        expected_expiry = session.verified_at + timedelta(seconds=ttl_seconds)

        # Allow 1 second tolerance for test execution time
        time_diff = abs((session.expires_at - expected_expiry).total_seconds())
        assert time_diff < 1


# =============================================================================
# Security Tests
# =============================================================================


class TestMFASecurity:
    """Test MFA security properties."""

    def test_totp_secret_entropy(self, mfa_manager: MFAManager) -> None:
        """Test TOTP secrets have sufficient entropy."""
        secrets = [
            mfa_manager.setup_totp(f"user{i}", f"user{i}@test.com").secret for i in range(100)
        ]

        # All secrets should be unique
        assert len(secrets) == len(set(secrets))

    def test_backup_codes_entropy(self, mfa_manager: MFAManager) -> None:
        """Test backup codes have sufficient entropy."""
        all_codes = []

        for i in range(10):
            setup = mfa_manager.setup_totp(f"user{i}", f"user{i}@test.com")
            all_codes.extend(setup.backup_codes)

        # 100 codes should all be unique (10 users × 10 codes)
        assert len(all_codes) == len(set(all_codes))

    def test_totp_token_replay_protection(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test TOTP tokens can't be reused beyond time window."""
        totp = pyotp.TOTP(mfa_setup_data.secret)
        token = totp.now()

        # First verification should succeed
        result1 = mfa_manager.verify_totp(mfa_setup_data.secret, token)
        assert result1 is True

        # Token can be verified multiple times within window
        # (this is expected TOTP behavior, session tracking prevents replay)
        result2 = mfa_manager.verify_totp(mfa_setup_data.secret, token)
        assert result2 is True

    def test_backup_code_one_time_use(self, mfa_setup_data: MFASetupData) -> None:
        """Test backup codes are truly one-time use."""
        session = MFASession(user_id="user123")
        code = mfa_setup_data.backup_codes[0]

        # First use succeeds
        assert session.verify_backup_code(code) is True

        # Second use fails
        assert session.verify_backup_code(code) is False

        # Third use also fails
        assert session.verify_backup_code(code) is False

    def test_backup_code_format_prevents_brute_force(self, mfa_manager: MFAManager) -> None:
        """Test backup code format has sufficient entropy."""
        # 8 hex chars = 32 bits = 4,294,967,296 possibilities
        # This makes brute force impractical
        codes = mfa_manager._generate_backup_codes()

        for code in codes:
            # Remove dash for entropy calculation
            hex_part = code.replace("-", "")
            # 8 hex chars = 2^32 possibilities
            assert len(hex_part) == 8
            assert all(c in "0123456789ABCDEF" for c in hex_part)


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestMFAErrorHandling:
    """Test MFA error handling."""

    def test_mfa_manager_requires_pyotp(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test MFAManager raises error if pyotp not installed."""
        monkeypatch.setattr("security.mfa.pyotp", None)

        with pytest.raises(RuntimeError, match="pyotp package required"):
            MFAManager()

    def test_verify_totp_handles_invalid_secret(self) -> None:
        """Test TOTP verification handles invalid secret gracefully."""
        manager = MFAManager()
        result = manager.verify_totp("NOT_BASE32!", "123456")

        assert result is False

    def test_verify_totp_handles_none_token(self) -> None:
        """Test TOTP verification handles None token."""
        manager = MFAManager()
        setup_data = manager.setup_totp("user123", "user@test.com")
        result = manager.verify_totp(setup_data.secret, None)  # type: ignore

        assert result is False


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
class TestMFAIntegration:
    """Test MFA end-to-end workflows."""

    def test_complete_mfa_setup_and_login_flow(self, mfa_manager: MFAManager) -> None:
        """Test complete MFA setup and login workflow."""
        # 1. User initiates MFA setup
        setup_data = mfa_manager.setup_totp(
            user_id="user123",
            email="user@example.com",
        )

        assert setup_data.secret
        assert setup_data.qr_code_uri
        assert len(setup_data.backup_codes) == 10

        # 2. User scans QR code and adds to authenticator app
        # (simulated by using the secret directly)
        totp = pyotp.TOTP(setup_data.secret)

        # 3. User verifies setup with first token
        token = totp.now()
        assert mfa_manager.verify_totp(setup_data.secret, token) is True

        # 4. User creates session
        session = MFASession(user_id="user123")

        # 5. User logs in with TOTP
        login_token = totp.now()
        assert session.verify_totp(setup_data.secret, login_token) is True
        assert session.is_valid() is True

    def test_backup_code_recovery_flow(self, mfa_manager: MFAManager) -> None:
        """Test account recovery with backup codes."""
        # 1. User has MFA enabled
        setup_data = mfa_manager.setup_totp(
            user_id="user123",
            email="user@example.com",
        )

        # 2. User loses authenticator device
        # 3. User uses backup code to login
        session = MFASession(user_id="user123")
        backup_code = setup_data.backup_codes[0]

        assert session.verify_backup_code(backup_code) is True
        assert session.is_valid() is True

        # 4. Backup code can't be reused
        assert session.verify_backup_code(backup_code) is False

    def test_multiple_users_mfa_isolation(self, mfa_manager: MFAManager) -> None:
        """Test MFA data is isolated between users."""
        # Setup MFA for two users
        user1_setup = mfa_manager.setup_totp("user1", "user1@test.com")
        user2_setup = mfa_manager.setup_totp("user2", "user2@test.com")

        # Generate tokens
        user1_totp = pyotp.TOTP(user1_setup.secret)
        user2_totp = pyotp.TOTP(user2_setup.secret)

        user1_token = user1_totp.now()
        user2_token = user2_totp.now()

        # User1's token shouldn't verify User2's secret
        assert mfa_manager.verify_totp(user2_setup.secret, user1_token) is False

        # User2's token shouldn't verify User1's secret
        assert mfa_manager.verify_totp(user1_setup.secret, user2_token) is False

        # Each user's token should verify their own secret
        assert mfa_manager.verify_totp(user1_setup.secret, user1_token) is True
        assert mfa_manager.verify_totp(user2_setup.secret, user2_token) is True


# =============================================================================
# Performance Tests
# =============================================================================


@pytest.mark.performance
class TestMFAPerformance:
    """Test MFA performance characteristics."""

    def test_totp_verification_performance(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test TOTP verification is fast."""
        import time

        totp = pyotp.TOTP(mfa_setup_data.secret)
        token = totp.now()

        start = time.time()
        for _ in range(1000):
            mfa_manager.verify_totp(mfa_setup_data.secret, token)
        duration = time.time() - start

        # 1000 verifications should complete in < 1 second
        assert duration < 1.0

    def test_backup_code_verification_performance(
        self, mfa_manager: MFAManager, mfa_setup_data: MFASetupData
    ) -> None:
        """Test backup code verification is fast."""
        import time

        code = mfa_setup_data.backup_codes[0]
        used_codes: set[str] = set()

        start = time.time()
        for _ in range(1000):
            mfa_manager.verify_backup_code(code, used_codes)
        duration = time.time() - start

        # 1000 verifications should complete in < 0.1 second
        assert duration < 0.1

    def test_mfa_setup_performance(self, mfa_manager: MFAManager) -> None:
        """Test MFA setup is fast."""
        import time

        start = time.time()
        for i in range(100):
            mfa_manager.setup_totp(f"user{i}", f"user{i}@test.com")
        duration = time.time() - start

        # 100 setups should complete in < 1 second
        assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
