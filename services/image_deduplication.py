# services/image_deduplication.py
"""Image deduplication service using content hashing.

Implements US-003: WooCommerce auto-ingestion webhook.

Uses perceptual hashing (pHash) for image similarity detection
and SHA-256 for exact duplicate detection.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class HashAlgorithm(StrEnum):
    """Hash algorithms for deduplication."""

    SHA256 = "sha256"
    MD5 = "md5"
    PHASH = "phash"  # Perceptual hash for image similarity


@dataclass
class HashResult:
    """Result of hashing an image."""

    content_hash: str
    algorithm: HashAlgorithm
    file_size_bytes: int
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DuplicateCheckResult:
    """Result of checking for duplicates."""

    is_duplicate: bool
    existing_asset_id: str | None = None
    existing_version: int | None = None
    similarity_score: float | None = None  # For perceptual hash
    hash_match: str | None = None


class ImageDeduplicator:
    """Service for detecting duplicate images.

    Features:
    - SHA-256 for exact duplicate detection
    - Perceptual hashing for similar image detection
    - Caching of recent hashes for performance

    Usage:
        dedup = ImageDeduplicator()

        # Hash image content
        hash_result = dedup.compute_hash(image_bytes)

        # Check for duplicates
        result = await dedup.check_duplicate(hash_result.content_hash)
        if result.is_duplicate:
            print(f"Duplicate found: {result.existing_asset_id}")
    """

    def __init__(
        self,
        *,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        similarity_threshold: float = 0.95,
    ) -> None:
        """Initialize deduplicator.

        Args:
            algorithm: Hash algorithm to use
            similarity_threshold: Threshold for perceptual hash similarity (0-1)
        """
        self._algorithm = algorithm
        self._similarity_threshold = similarity_threshold

        # In-memory hash index (replace with database in production)
        self._hash_index: dict[str, dict[str, Any]] = {}

    def compute_hash(
        self,
        content: bytes,
        *,
        algorithm: HashAlgorithm | None = None,
    ) -> HashResult:
        """Compute hash of image content.

        Args:
            content: Raw image bytes
            algorithm: Override default algorithm

        Returns:
            HashResult with computed hash
        """
        algo = algorithm or self._algorithm

        if algo == HashAlgorithm.SHA256:
            content_hash = hashlib.sha256(content).hexdigest()
        elif algo == HashAlgorithm.MD5:
            content_hash = hashlib.md5(content, usedforsecurity=False).hexdigest()
        elif algo == HashAlgorithm.PHASH:
            content_hash = self._compute_phash(content)
        else:
            raise ValueError(f"Unsupported algorithm: {algo}")

        return HashResult(
            content_hash=content_hash,
            algorithm=algo,
            file_size_bytes=len(content),
        )

    def _compute_phash(self, content: bytes) -> str:
        """Compute perceptual hash for image similarity.

        Uses average hashing for simplicity. For production,
        consider using imagehash library with pHash.

        Args:
            content: Raw image bytes

        Returns:
            Perceptual hash string
        """
        try:
            import io

            from PIL import Image

            # Load image
            img = Image.open(io.BytesIO(content))

            # Resize to 8x8 for hashing
            img = img.resize((8, 8), Image.Resampling.LANCZOS)

            # Convert to grayscale
            img = img.convert("L")

            # Compute average
            pixels = list(img.get_flattened_data())
            avg = sum(pixels) // len(pixels)

            # Create hash based on whether pixel is above/below average
            bits = "".join("1" if p > avg else "0" for p in pixels)

            # Convert to hex
            return format(int(bits, 2), "016x")

        except Exception as e:
            logger.warning(f"Failed to compute pHash, falling back to SHA-256: {e}")
            return hashlib.sha256(content).hexdigest()

    async def check_duplicate(
        self,
        content_hash: str,
        *,
        correlation_id: str | None = None,
    ) -> DuplicateCheckResult:
        """Check if image already exists in the system.

        Args:
            content_hash: Hash of the image content
            correlation_id: Optional correlation ID

        Returns:
            DuplicateCheckResult with match info
        """
        # Check hash index
        if content_hash in self._hash_index:
            entry = self._hash_index[content_hash]
            logger.info(
                f"Duplicate found for hash {content_hash[:16]}...",
                extra={
                    "asset_id": entry.get("asset_id"),
                    "correlation_id": correlation_id,
                },
            )
            return DuplicateCheckResult(
                is_duplicate=True,
                existing_asset_id=entry.get("asset_id"),
                existing_version=entry.get("version"),
                hash_match=content_hash,
            )

        return DuplicateCheckResult(is_duplicate=False)

    async def check_similar(
        self,
        content: bytes,
        *,
        threshold: float | None = None,
        correlation_id: str | None = None,
    ) -> DuplicateCheckResult:
        """Check for similar images using perceptual hashing.

        Args:
            content: Raw image bytes
            threshold: Override similarity threshold
            correlation_id: Optional correlation ID

        Returns:
            DuplicateCheckResult with similarity score
        """
        threshold = threshold or self._similarity_threshold
        phash = self._compute_phash(content)

        # Compare with indexed hashes
        for indexed_hash, entry in self._hash_index.items():
            if entry.get("phash"):
                similarity = self._compare_phash(phash, entry["phash"])
                if similarity >= threshold:
                    logger.info(
                        f"Similar image found (similarity: {similarity:.2%})",
                        extra={
                            "asset_id": entry.get("asset_id"),
                            "correlation_id": correlation_id,
                        },
                    )
                    return DuplicateCheckResult(
                        is_duplicate=True,
                        existing_asset_id=entry.get("asset_id"),
                        existing_version=entry.get("version"),
                        similarity_score=similarity,
                    )

        return DuplicateCheckResult(is_duplicate=False)

    def _compare_phash(self, hash1: str, hash2: str) -> float:
        """Compare two perceptual hashes.

        Args:
            hash1: First hash
            hash2: Second hash

        Returns:
            Similarity score (0-1)
        """
        if len(hash1) != len(hash2):
            return 0.0

        # Convert to binary and count matching bits
        try:
            int1 = int(hash1, 16)
            int2 = int(hash2, 16)

            # XOR to find differing bits
            xor = int1 ^ int2

            # Count differing bits
            diff_bits = bin(xor).count("1")

            # Total bits
            total_bits = len(hash1) * 4

            # Similarity = 1 - (differing bits / total bits)
            return 1.0 - (diff_bits / total_bits)

        except ValueError:
            return 0.0

    async def register_hash(
        self,
        content_hash: str,
        asset_id: str,
        version: int = 1,
        *,
        phash: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Register a hash in the index.

        Args:
            content_hash: SHA-256 hash of content
            asset_id: Asset identifier
            version: Version number
            phash: Optional perceptual hash
            correlation_id: Optional correlation ID
        """
        self._hash_index[content_hash] = {
            "asset_id": asset_id,
            "version": version,
            "phash": phash,
            "registered_at": datetime.now(UTC),
        }

        logger.debug(
            f"Registered hash {content_hash[:16]}... for asset {asset_id}",
            extra={"correlation_id": correlation_id},
        )

    async def unregister_hash(
        self,
        content_hash: str,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Remove a hash from the index.

        Args:
            content_hash: Hash to remove
            correlation_id: Optional correlation ID

        Returns:
            True if removed, False if not found
        """
        if content_hash in self._hash_index:
            del self._hash_index[content_hash]
            logger.debug(
                f"Unregistered hash {content_hash[:16]}...",
                extra={"correlation_id": correlation_id},
            )
            return True
        return False

    def get_stats(self) -> dict[str, Any]:
        """Get deduplicator statistics.

        Returns:
            Dict with stats
        """
        return {
            "algorithm": self._algorithm.value,
            "similarity_threshold": self._similarity_threshold,
            "indexed_hashes": len(self._hash_index),
        }


# Module singleton
_deduplicator: ImageDeduplicator | None = None


def get_deduplicator() -> ImageDeduplicator:
    """Get or create the image deduplicator singleton."""
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = ImageDeduplicator()
    return _deduplicator


__all__ = [
    "HashAlgorithm",
    "HashResult",
    "DuplicateCheckResult",
    "ImageDeduplicator",
    "get_deduplicator",
]
