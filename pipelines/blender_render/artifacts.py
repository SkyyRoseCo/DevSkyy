"""Keyed artifact storage for render jobs: fetch a source by key, publish outputs by key.

Why not reuse :mod:`pipelines.clothing_3d.storage`? Its :class:`ArtifactStore` protocol is
``store(bundle) -> StoredArtifact`` — a write-only, bundle-shaped contract (GLB + USDZ +
thumbnail) with no fetch-by-key. Render jobs need the inverse direction too (pull the source
GLB the API validated), so this module is the thinnest keyed adapter: two backends behind one
``fetch`` / ``put`` / ``exists`` protocol, the same local-vs-S3 split and the same lazy
``boto3`` import as the clothing store.

Every path is derived from a key that :func:`validate_artifact_key` already vetted; the local
backend re-checks containment after resolution as defence in depth.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from pipelines.blender_render.models import ArtifactRef, validate_artifact_key


class ArtifactNotFoundError(FileNotFoundError):
    """The requested key does not exist in the store."""


class ArtifactStoreConfigError(RuntimeError):
    """The environment does not describe a usable store (fail closed, never guess)."""


@runtime_checkable
class KeyedArtifactStore(Protocol):
    async def fetch(self, key: str, dest: Path) -> Path: ...

    async def put(self, src: Path, key: str, *, content_type: str) -> ArtifactRef: ...

    async def exists(self, key: str) -> bool: ...

    async def delete(self, key: str) -> None: ...


class LocalKeyedStore:
    """Filesystem store rooted at ``base_dir``; keys map to relative paths beneath it."""

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        candidate = (self.base_dir / key).resolve()
        if candidate != self.base_dir and self.base_dir not in candidate.parents:
            raise ValueError(f"key escapes the store root: {key!r}")
        return candidate

    async def fetch(self, key: str, dest: Path) -> Path:
        source = self._path_for(key)
        if not source.is_file():
            raise ArtifactNotFoundError(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copy2, source, dest)
        return dest

    async def put(self, src: Path, key: str, *, content_type: str) -> ArtifactRef:
        if not src.is_file():
            raise FileNotFoundError(src)
        target = self._path_for(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Atomic publish: readers never observe a half-written object at the final path.
        staging = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        try:
            await asyncio.to_thread(shutil.copy2, src, staging)
            os.replace(staging, target)
        finally:
            staging.unlink(missing_ok=True)
        return ArtifactRef(key=key, bytes=target.stat().st_size, content_type=content_type)

    async def exists(self, key: str) -> bool:
        return self._path_for(key).is_file()

    async def delete(self, key: str) -> None:
        self._path_for(key).unlink(missing_ok=True)


class S3KeyedStore:
    """S3 / S3-compatible (R2, MinIO) store. ``endpoint_url`` selects the compatible target."""

    def __init__(
        self,
        *,
        bucket: str,
        prefix: str = "",
        endpoint_url: str | None = None,
        region: str | None = None,
    ) -> None:
        if not bucket:
            raise ArtifactStoreConfigError("S3 store requires a bucket name")
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.endpoint_url = endpoint_url or None
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import boto3  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("S3KeyedStore requires boto3 — pip install boto3") from exc
        self._client = boto3.client("s3", region_name=self.region, endpoint_url=self.endpoint_url)
        return self._client

    def _object_key(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    async def fetch(self, key: str, dest: Path) -> Path:
        if not await self.exists(key):
            raise ArtifactNotFoundError(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        client = self._get_client()
        await asyncio.to_thread(client.download_file, self.bucket, self._object_key(key), str(dest))
        return dest

    async def put(self, src: Path, key: str, *, content_type: str) -> ArtifactRef:
        if not src.is_file():
            raise FileNotFoundError(src)
        client = self._get_client()
        await asyncio.to_thread(
            client.upload_file,
            str(src),
            self.bucket,
            self._object_key(key),
            ExtraArgs={"ContentType": content_type},
        )
        return ArtifactRef(key=key, bytes=src.stat().st_size, content_type=content_type)

    async def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError  # type: ignore[import-not-found]

        client = self._get_client()
        try:
            await asyncio.to_thread(
                client.head_object, Bucket=self.bucket, Key=self._object_key(key)
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
        return True

    async def delete(self, key: str) -> None:
        client = self._get_client()
        await asyncio.to_thread(client.delete_object, Bucket=self.bucket, Key=self._object_key(key))


def build_artifact_store() -> KeyedArtifactStore:
    """``RENDER_ARTIFACT_STORE`` = ``local`` (default) | ``s3``. Misconfiguration raises."""
    backend = os.getenv("RENDER_ARTIFACT_STORE", "local").lower()
    if backend == "local":
        base_dir = os.getenv("RENDER_ARTIFACT_DIR")
        if not base_dir:
            raise ArtifactStoreConfigError("RENDER_ARTIFACT_DIR is required for the local store")
        return LocalKeyedStore(base_dir)
    if backend == "s3":
        bucket = os.getenv("RENDER_S3_BUCKET")
        if not bucket:
            raise ArtifactStoreConfigError("RENDER_S3_BUCKET is required for the s3 store")
        return S3KeyedStore(
            bucket=bucket,
            prefix=os.getenv("RENDER_S3_PREFIX", ""),
            endpoint_url=os.getenv("RENDER_S3_ENDPOINT_URL"),
            region=os.getenv("AWS_REGION"),
        )
    raise ArtifactStoreConfigError(f"unknown RENDER_ARTIFACT_STORE={backend!r}")


__all__ = [
    "ArtifactNotFoundError",
    "ArtifactStoreConfigError",
    "KeyedArtifactStore",
    "LocalKeyedStore",
    "S3KeyedStore",
    "build_artifact_store",
    "validate_artifact_key",
]
