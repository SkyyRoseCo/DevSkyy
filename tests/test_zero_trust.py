"""
Tests for Zero Trust Architecture

Comprehensive test suite for Zero Trust security components:
- Configuration validation
- Certificate generation and management
- mTLS handler functionality
- Certificate rotation
- Service identity validation
"""

import os
import shutil
import ssl
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cryptography import x509

from security.certificate_authority import (
    CertificateRevocationList,
    CertificateValidator,
    SelfSignedCA,
    VaultCA,
)
from security.mtls_handler import MTLSHandler
from security.zero_trust_config import (
    CertificateInfo,
    CertificateManager,
    ServiceIdentity,
    ZeroTrustConfig,
)


@pytest.fixture
def temp_cert_dir():
    """Create temporary directory for certificates"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def basic_config(temp_cert_dir):
    """Create basic Zero Trust configuration"""
    return ZeroTrustConfig(
        enabled=True,
        ca_type="self-signed",
        cert_dir=temp_cert_dir,
        auto_rotate=True,
        rotation_days=30,
        services=[
            ServiceIdentity(name="api", port=8000, require_mtls=True),
            ServiceIdentity(name="database", port=5432, require_mtls=True),
            ServiceIdentity(name="redis", port=6379, require_mtls=False),
        ],
    )


@pytest.fixture
def self_signed_ca(temp_cert_dir):
    """Create self-signed CA instance"""
    return SelfSignedCA(temp_cert_dir)


@pytest.fixture
def root_ca(self_signed_ca):
    """Generate root CA certificate"""
    return self_signed_ca.generate_root_ca(organization="TestOrg", validity_years=1)


class TestZeroTrustConfig:
    """Test ZeroTrustConfig class"""

    def test_config_initialization(self, basic_config):
        """Test configuration initialization"""
        assert basic_config.enabled is True
        assert basic_config.ca_type == "self-signed"
        assert basic_config.auto_rotate is True
        assert basic_config.rotation_days == 30
        assert len(basic_config.services) == 3

    def test_config_validation_invalid_ca_type(self, temp_cert_dir):
        """Test configuration validation rejects invalid CA type"""
        with pytest.raises(ValueError, match="Invalid ca_type"):
            ZeroTrustConfig(
                ca_type="invalid-type",
                cert_dir=temp_cert_dir,
            )

    def test_config_validation_rotation_days(self, temp_cert_dir):
        """Test configuration validation for rotation days"""
        with pytest.raises(ValueError, match="rotation_days must be >= 1"):
            ZeroTrustConfig(
                rotation_days=0,
                cert_dir=temp_cert_dir,
            )

    def test_config_validation_key_size(self, temp_cert_dir):
        """Test configuration validation for key size"""
        with pytest.raises(ValueError, match="key_size must be >= 2048"):
            ZeroTrustConfig(
                key_size=1024,
                cert_dir=temp_cert_dir,
            )

    def test_get_service(self, basic_config):
        """Test getting service by name"""
        api_service = basic_config.get_service("api")
        assert api_service is not None
        assert api_service.name == "api"
        assert api_service.port == 8000
        assert api_service.require_mtls is True

    def test_get_service_not_found(self, basic_config):
        """Test getting non-existent service"""
        service = basic_config.get_service("nonexistent")
        assert service is None

    def test_add_service(self, basic_config):
        """Test adding a service"""
        new_service = ServiceIdentity(
            name="new-service",
            port=9000,
            require_mtls=True,
        )
        basic_config.add_service(new_service)

        service = basic_config.get_service("new-service")
        assert service is not None
        assert service.port == 9000

    def test_add_service_replaces_existing(self, basic_config):
        """Test adding service replaces existing with same name"""
        original_count = len(basic_config.services)

        updated_service = ServiceIdentity(
            name="api",
            port=8080,  # Different port
            require_mtls=False,
        )
        basic_config.add_service(updated_service)

        # Count should remain the same
        assert len(basic_config.services) == original_count

        # Service should have updated values
        service = basic_config.get_service("api")
        assert service.port == 8080
        assert service.require_mtls is False

    def test_config_to_yaml(self, basic_config, temp_cert_dir):
        """Test saving configuration to YAML"""
        yaml_path = temp_cert_dir / "test_config.yaml"
        basic_config.to_yaml(yaml_path)

        assert yaml_path.exists()

        # Load and verify
        loaded_config = ZeroTrustConfig.from_yaml(yaml_path)
        assert loaded_config.enabled == basic_config.enabled
        assert loaded_config.ca_type == basic_config.ca_type
        assert len(loaded_config.services) == len(basic_config.services)

    def test_config_from_yaml_not_found(self, temp_cert_dir):
        """Test loading from non-existent YAML returns defaults"""
        config = ZeroTrustConfig.from_yaml(temp_cert_dir / "nonexistent.yaml")
        assert config.enabled is False
        assert len(config.services) == 0


class TestCertificateAuthority:
    """Test SelfSignedCA class"""

    def test_generate_root_ca(self, self_signed_ca):
        """Test root CA generation"""
        ca_cert, ca_key = self_signed_ca.generate_root_ca(
            organization="TestOrg",
            validity_years=1,
        )

        assert ca_cert is not None
        assert ca_key is not None

        # Verify certificate properties
        cn_attr = ca_cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        assert "TestOrg Root CA" in cn_attr[0].value

        # Verify it's a CA certificate
        basic_constraints = ca_cert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.BASIC_CONSTRAINTS
        )
        assert basic_constraints.value.ca is True

    def test_load_ca(self, self_signed_ca):
        """Test loading CA from disk"""
        # Generate first
        original_ca_cert, _ = self_signed_ca.generate_root_ca()

        # Load from disk
        loaded_ca_cert, loaded_ca_key = self_signed_ca.load_ca()

        assert loaded_ca_cert is not None
        assert loaded_ca_key is not None

        # Verify it's the same certificate
        assert loaded_ca_cert.serial_number == original_ca_cert.serial_number

    def test_load_ca_not_found(self, self_signed_ca):
        """Test loading CA when files don't exist"""
        with pytest.raises(FileNotFoundError):
            self_signed_ca.load_ca()

    def test_generate_service_cert(self, self_signed_ca, root_ca):
        """Test service certificate generation"""
        ca_cert, ca_key = root_ca

        service_cert, service_key = self_signed_ca.generate_service_cert(
            service_name="test-service",
            validity_days=30,
        )

        assert service_cert is not None
        assert service_key is not None

        # Verify certificate properties
        cn_attr = service_cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        assert cn_attr[0].value == "test-service"

        # Verify it's not a CA certificate
        basic_constraints = service_cert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.BASIC_CONSTRAINTS
        )
        assert basic_constraints.value.ca is False

        # Verify SAN names
        san_ext = service_cert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )
        san_names = [str(name.value) for name in san_ext.value]
        assert "test-service" in san_names
        assert "test-service.devskyy.local" in san_names

    def test_verify_certificate_valid(self, self_signed_ca, root_ca):
        """Test certificate verification with valid certificate"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert("test-service")

        # Verify certificate
        is_valid = self_signed_ca.verify_certificate(service_cert)
        assert is_valid is True

    @pytest.mark.slow
    def test_verify_certificate_expired(self, self_signed_ca, root_ca):
        """Test certificate verification with expired certificate"""
        from datetime import timedelta

        try:
            from freezegun import freeze_time
        except ImportError:
            pytest.skip("freezegun not installed")

        ca_cert, ca_key = root_ca

        # Generate a certificate with 1-day validity
        service_cert, _ = self_signed_ca.generate_service_cert(
            "test-service",
            validity_days=1,
        )

        # Verify it's valid now
        is_valid = self_signed_ca.verify_certificate(service_cert)
        assert is_valid is True

        # Travel 2 days into the future when cert is expired
        future_date = datetime.now() + timedelta(days=2)
        with freeze_time(future_date):
            is_valid = self_signed_ca.verify_certificate(service_cert)
            assert is_valid is False

    def test_revoke_certificate(self, self_signed_ca, root_ca):
        """Test certificate revocation"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert("test-service")

        # Revoke certificate
        self_signed_ca.revoke_certificate(service_cert.serial_number)

        # Verify it's revoked
        is_revoked = self_signed_ca.crl.is_revoked(service_cert.serial_number)
        assert is_revoked is True

        # Verification should fail
        is_valid = self_signed_ca.verify_certificate(service_cert, check_revocation=True)
        assert is_valid is False

    def test_get_certificate_info(self, self_signed_ca, root_ca, temp_cert_dir):
        """Test getting certificate information"""
        ca_cert, ca_key = root_ca

        service_cert, service_key = self_signed_ca.generate_service_cert("test-service")

        # Save certificate
        cert_path = temp_cert_dir / "test-cert.pem"
        with open(cert_path, "wb") as f:
            from cryptography.hazmat.primitives import serialization

            f.write(service_cert.public_bytes(serialization.Encoding.PEM))

        # Get info
        info = self_signed_ca.get_certificate_info(cert_path)

        assert info is not None
        assert "subject" in info
        assert "issuer" in info
        assert "serial_number" in info
        assert info["is_ca"] is False


class TestCertificateManager:
    """Test CertificateManager class"""

    def test_generate_cert(self, basic_config, self_signed_ca, root_ca):
        """Test certificate generation through manager"""
        ca_cert, ca_key = root_ca

        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key)

        assert cert is not None
        assert key is not None

    def test_save_and_load_cert(self, basic_config, self_signed_ca, root_ca):
        """Test saving and loading certificate"""
        ca_cert, ca_key = root_ca

        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key)

        # Save
        cert_path, key_path = manager.save_cert("test-service", cert, key)

        assert cert_path.exists()
        assert key_path.exists()

        # Verify permissions
        assert oct(os.stat(cert_path).st_mode)[-3:] == "644"
        assert oct(os.stat(key_path).st_mode)[-3:] == "600"

        # Load
        cert_info = manager.load_cert("test-service")
        assert cert_info is not None
        assert cert_info.common_name == "test-service"

    def test_verify_cert(self, basic_config, self_signed_ca, root_ca):
        """Test certificate verification through manager"""
        ca_cert, ca_key = root_ca

        manager = CertificateManager(basic_config)
        cert, _ = manager.generate_cert("test-service", ca_cert, ca_key)

        # Verify
        is_valid = manager.verify_cert(cert, ca_cert)
        assert is_valid is True

    def test_rotate_cert(self, basic_config, self_signed_ca, root_ca):
        """Test certificate rotation"""
        ca_cert, ca_key = root_ca

        manager = CertificateManager(basic_config)

        # Generate initial certificate
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key, validity_days=1)
        manager.save_cert("test-service", cert, key)

        # Rotate
        result = manager.rotate_cert("test-service", ca_cert, ca_key)
        assert result is True

        # Verify new certificate exists
        cert_info = manager.load_cert("test-service")
        assert cert_info is not None

    def test_check_rotation_needed(self, basic_config, self_signed_ca, root_ca):
        """Test checking which certificates need rotation"""
        ca_cert, ca_key = root_ca

        # Add test service to config
        from security.zero_trust_config import ServiceIdentity

        basic_config.add_service(ServiceIdentity(name="test-service", port=9000, require_mtls=True))

        manager = CertificateManager(basic_config)

        # Generate certificate expiring in 5 days
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key, validity_days=5)
        manager.save_cert("test-service", cert, key)

        # Check rotation
        needs_rotation = manager.check_rotation_needed()

        # Certificate with 5 days validity should need rotation (threshold is 7 days)
        assert "test-service" in needs_rotation

    def test_get_cert_status(self, basic_config, self_signed_ca, root_ca):
        """Test getting certificate status for all services"""
        ca_cert, ca_key = root_ca

        manager = CertificateManager(basic_config)

        # Generate certificates for services
        for service in basic_config.services:
            cert, key = manager.generate_cert(service.name, ca_cert, ca_key)
            manager.save_cert(service.name, cert, key)

        # Get status
        status = manager.get_cert_status()

        assert len(status) == len(basic_config.services)
        for service in basic_config.services:
            assert service.name in status
            assert "common_name" in status[service.name]


class TestMTLSHandler:
    """Test MTLSHandler class"""

    def test_enable_client_tls(self, basic_config, self_signed_ca, root_ca):
        """Test enabling client TLS"""
        ca_cert, ca_key = root_ca

        # Generate certificate for service
        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("api", ca_cert, ca_key)
        manager.save_cert("api", cert, key)

        # Create handler
        handler = MTLSHandler(basic_config)

        # Enable client TLS
        context = handler.enable_client_tls("api")

        assert context is not None
        assert isinstance(context, ssl.SSLContext)
        assert context.minimum_version == ssl.TLSVersion.TLSv1_3

    def test_enable_server_tls(self, basic_config, self_signed_ca, root_ca):
        """Test enabling server TLS"""
        ca_cert, ca_key = root_ca

        # Generate certificate for service
        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("api", ca_cert, ca_key)
        manager.save_cert("api", cert, key)

        # Create handler
        handler = MTLSHandler(basic_config)

        # Enable server TLS
        context = handler.enable_server_tls("api")

        assert context is not None
        assert isinstance(context, ssl.SSLContext)
        assert context.minimum_version == ssl.TLSVersion.TLSv1_3

    def test_verify_peer_certificate(self, basic_config, self_signed_ca, root_ca):
        """Test peer certificate verification"""
        ca_cert, ca_key = root_ca

        # Generate certificate
        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key)
        cert_path, _ = manager.save_cert("test-service", cert, key)

        # Create handler
        handler = MTLSHandler(basic_config)

        # Verify certificate
        is_valid = handler.verify_peer_certificate(cert_path, expected_service="test-service")
        assert is_valid is True

    def test_verify_peer_certificate_wrong_service(self, basic_config, self_signed_ca, root_ca):
        """Test peer certificate verification with wrong service name"""
        ca_cert, ca_key = root_ca

        # Generate certificate
        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key)
        cert_path, _ = manager.save_cert("test-service", cert, key)

        # Create handler
        handler = MTLSHandler(basic_config)

        # Verify with wrong expected service
        is_valid = handler.verify_peer_certificate(cert_path, expected_service="wrong-service")
        assert is_valid is False

    def test_validate_service_identity(self, basic_config, self_signed_ca, root_ca):
        """Test service identity validation"""
        ca_cert, ca_key = root_ca

        # Generate certificate
        service_cert, _ = self_signed_ca.generate_service_cert("test-service")

        # Create handler
        handler = MTLSHandler(basic_config)

        # Validate identity
        is_valid = handler.validate_service_identity(service_cert, "test-service")
        assert is_valid is True

    def test_verify_certificate_chain(self, basic_config, self_signed_ca, root_ca):
        """Test certificate chain verification"""
        ca_cert, ca_key = root_ca

        # Generate service certificate
        manager = CertificateManager(basic_config)
        cert, key = manager.generate_cert("test-service", ca_cert, ca_key)
        cert_path, _ = manager.save_cert("test-service", cert, key)

        # Create handler
        handler = MTLSHandler(basic_config)

        # Verify chain
        is_valid = handler.verify_certificate_chain(cert_path)
        assert is_valid is True


class TestCertificateRevocationList:
    """Test CertificateRevocationList class"""

    def test_crl_initialization(self, temp_cert_dir):
        """Test CRL initialization"""
        crl_path = temp_cert_dir / "crl.json"
        crl = CertificateRevocationList(crl_path)

        assert crl is not None
        assert len(crl.revoked_certs) == 0

    def test_revoke_certificate(self, temp_cert_dir):
        """Test revoking a certificate"""
        crl_path = temp_cert_dir / "crl.json"
        crl = CertificateRevocationList(crl_path)

        serial_number = 12345
        crl.revoke(serial_number)

        assert crl.is_revoked(serial_number) is True

    def test_crl_persistence(self, temp_cert_dir):
        """Test CRL persistence to disk"""
        crl_path = temp_cert_dir / "crl.json"

        # Create and revoke
        crl1 = CertificateRevocationList(crl_path)
        crl1.revoke(12345)
        crl1.save()

        # Load in new instance
        crl2 = CertificateRevocationList(crl_path)
        assert crl2.is_revoked(12345) is True

    def test_get_revocation_time(self, temp_cert_dir):
        """Test getting revocation time"""
        crl_path = temp_cert_dir / "crl.json"
        crl = CertificateRevocationList(crl_path)

        serial_number = 12345
        crl.revoke(serial_number)

        revocation_time = crl.get_revocation_time(serial_number)
        assert revocation_time is not None
        assert isinstance(revocation_time, datetime)


class TestCertificateValidator:
    """Test CertificateValidator class"""

    def test_check_certificate_expiry(self, self_signed_ca, root_ca):
        """Test certificate expiry checking"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert("test-service", validity_days=30)

        expiry_info = CertificateValidator.check_certificate_expiry(service_cert)

        assert expiry_info is not None
        assert expiry_info["is_expired"] is False
        assert expiry_info["not_yet_valid"] is False
        assert expiry_info["days_until_expiry"] > 0
        assert "not_valid_before" in expiry_info
        assert "not_valid_after" in expiry_info

    def test_extract_san_names(self, self_signed_ca, root_ca):
        """Test extracting SAN names"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert(
            "test-service",
            san_names=["extra.example.com", "192.168.1.1"],
        )

        san_names = CertificateValidator.extract_san_names(service_cert)

        assert "test-service" in san_names
        assert "test-service.devskyy.local" in san_names
        assert "extra.example.com" in san_names

    def test_get_certificate_fingerprint(self, self_signed_ca, root_ca):
        """Test getting certificate fingerprint"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert("test-service")

        fingerprint = CertificateValidator.get_certificate_fingerprint(service_cert)

        assert fingerprint is not None
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 produces 32 bytes = 64 hex chars


class TestCertificateInfo:
    """Test CertificateInfo class"""

    def test_certificate_info(self, self_signed_ca, root_ca):
        """Test CertificateInfo wrapper"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert("test-service")

        cert_info = CertificateInfo(service_cert)

        assert cert_info.common_name == "test-service"
        assert cert_info.is_expired is False
        assert cert_info.days_until_expiry > 0
        assert cert_info.fingerprint is not None

    def test_certificate_info_to_dict(self, self_signed_ca, root_ca):
        """Test converting CertificateInfo to dict"""
        ca_cert, ca_key = root_ca

        service_cert, _ = self_signed_ca.generate_service_cert("test-service")

        cert_info = CertificateInfo(service_cert)
        info_dict = cert_info.to_dict()

        assert "subject" in info_dict
        assert "issuer" in info_dict
        assert "serial_number" in info_dict
        assert "common_name" in info_dict
        assert "is_expired" in info_dict
        assert "days_until_expiry" in info_dict


class TestVaultCA:
    """Test VaultCA production implementation"""

    def test_vault_ca_requires_hvac(self, monkeypatch):
        """VaultCA raises RuntimeError when hvac cannot be imported"""
        # Setting a sys.modules entry to None makes `import hvac` raise ImportError,
        # simulating a missing library regardless of what is installed.
        monkeypatch.setitem(sys.modules, "hvac", None)

        with pytest.raises(RuntimeError, match="hvac library required"):
            VaultCA(
                vault_url="https://vault.example.com",
                vault_token="test-token",
            )

    def test_vault_ca_init_with_hvac(self):
        """Test VaultCA initialization when hvac is available (mocked)"""
        try:
            import hvac  # noqa: F401
        except ImportError:
            pytest.skip("hvac not installed")

        # Mock the hvac client to avoid actual Vault connection
        with patch("hvac.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.is_authenticated.return_value = True
            mock_client.return_value = mock_instance

            vault_ca = VaultCA(
                vault_url="https://vault.example.com",
                vault_token="test-token",
                pki_path="pki",
                pki_role="test-role",
            )

            assert vault_ca.vault_url == "https://vault.example.com"
            assert vault_ca.pki_path == "pki"
            assert vault_ca.pki_role == "test-role"
            mock_client.assert_called_once()

    def test_vault_ca_generate_cert_with_hvac(self):
        """Test VaultCA certificate generation (mocked)"""
        try:
            import hvac  # noqa: F401
        except ImportError:
            pytest.skip("hvac not installed")

        with patch("hvac.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.is_authenticated.return_value = True
            mock_instance.secrets.pki.generate_certificate.return_value = {
                "data": {
                    "certificate": "-----BEGIN CERTIFICATE-----\nMOCK\n-----END CERTIFICATE-----",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK\n-----END PRIVATE KEY-----",
                    "ca_chain": ["-----BEGIN CERTIFICATE-----\nCA\n-----END CERTIFICATE-----"],
                    "serial_number": "12:34:56:78",
                    "expiration": 1735689600,
                }
            }
            mock_client.return_value = mock_instance

            vault_ca = VaultCA(
                vault_url="https://vault.example.com",
                vault_token="test-token",
            )

            cert, key, chain = vault_ca.generate_service_cert(
                "test-service",
                validity_ttl="720h",
                san_names=["test.example.com"],
            )

            assert "BEGIN CERTIFICATE" in cert
            assert "BEGIN PRIVATE KEY" in key
            assert chain is not None

    def test_vault_ca_revoke_cert_with_hvac(self):
        """Test VaultCA certificate revocation (mocked)"""
        try:
            import hvac  # noqa: F401
        except ImportError:
            pytest.skip("hvac not installed")

        with patch("hvac.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.is_authenticated.return_value = True
            mock_instance.secrets.pki.revoke_certificate.return_value = {}
            mock_client.return_value = mock_instance

            vault_ca = VaultCA(
                vault_url="https://vault.example.com",
                vault_token="test-token",
            )

            result = vault_ca.revoke_certificate("12:34:56:78")
            assert result is True
            mock_instance.secrets.pki.revoke_certificate.assert_called_once()


class TestServiceIdentity:
    """Test ServiceIdentity class"""

    def test_service_identity_creation(self):
        """Test creating service identity"""
        service = ServiceIdentity(
            name="test-service",
            port=8000,
            require_mtls=True,
            allowed_peers=["service1", "service2"],
        )

        assert service.name == "test-service"
        assert service.port == 8000
        assert service.require_mtls is True
        assert len(service.allowed_peers) == 2

    def test_service_identity_to_dict(self):
        """Test converting ServiceIdentity to dict"""
        service = ServiceIdentity(
            name="test-service",
            port=8000,
            require_mtls=True,
        )

        service_dict = service.to_dict()

        assert service_dict["name"] == "test-service"
        assert service_dict["port"] == 8000
        assert service_dict["require_mtls"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
