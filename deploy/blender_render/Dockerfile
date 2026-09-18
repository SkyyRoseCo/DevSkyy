# syntax=docker/dockerfile:1.7
# Blender headless render worker — Cycles turntable stills + gltfpack web GLBs.
# Consumes the `blender_render` Redis stream; see pipelines/blender_render/.
#
# amd64 ONLY: Blender publishes no Linux ARM64 build, so on Apple Silicon this image runs
# under emulation (slow but correct). Always build/run with --platform=linux/amd64.
#
# Build:
#   docker build --platform=linux/amd64 -f deploy/blender_render/Dockerfile \
#     -t devskyy/blender-render-worker:5.2.0 .
#
# One-shot local job (LocalKeyedStore bind-mounted, no cloud, no Redis):
#   docker run --rm --platform=linux/amd64 \
#     -v /path/to/store:/var/data/render-artifacts \
#     devskyy/blender-render-worker:5.2.0 python -m pipelines.blender_render.oneshot \
#     --job-type render_stills --sku br-006 --source-key sources/br-006.glb --count 2 --resolution 512
#
# download.blender.org answers curl with HTTP 403 (Cloudflare challenge; observed in this
# build 2026-09-17), so the default source is an official mirror listed at
# https://www.blender.org/download/. Override with
#   --build-arg BLENDER_URL=https://<mirror>/release/Blender5.2/blender-5.2.0-linux-x64.tar.xz
# The pinned SHA256 (from the official blender-5.2.0.sha256 manifest, identical on
# mirror.clarkson.edu and ftp.nluug.nl 2026-09-17) is what guarantees integrity, not the host.
#
# Base images are pinned by multi-arch index digest (docker buildx imagetools inspect,
# 2026-09-17); apt packages float within bookworm, pip within the ranges in
# requirements-blender-render.txt.

ARG BLENDER_VERSION=5.2.0
ARG BLENDER_SHA256=96f6c181a30f4950607839dc84d42a354b250d8a0231b098b59b7bc69c351c48
ARG BLENDER_URL=https://mirror.clarkson.edu/blender/release/Blender5.2/blender-5.2.0-linux-x64.tar.xz
# gltfpack v1.2 ubuntu build — digest from the GitHub Releases API (zeux/meshoptimizer, tag v1.2).
ARG GLTFPACK_SHA256=ebc236f5f6c08c7e5c5750476a187d24805d44d8c680449c4b7369c333f817b1
ARG GLTFPACK_URL=https://github.com/zeux/meshoptimizer/releases/download/v1.2/gltfpack-ubuntu.zip

# ----------------------------------------------------------------------------- fetch stage
FROM --platform=linux/amd64 debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171 AS fetch
ARG BLENDER_SHA256
ARG BLENDER_URL
ARG GLTFPACK_SHA256
ARG GLTFPACK_URL

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl xz-utils unzip \
  && rm -rf /var/lib/apt/lists/*

# Blender: download → verify pinned SHA256 (build fails on mismatch) → unpack to /opt/blender.
RUN set -eux; \
    curl -fsSL --retry 3 -A "Mozilla/5.0 devskyy-blender-worker" -o /tmp/blender.tar.xz "$BLENDER_URL"; \
    echo "$BLENDER_SHA256  /tmp/blender.tar.xz" | sha256sum -c -; \
    mkdir -p /opt/blender; \
    tar -xJf /tmp/blender.tar.xz --strip-components=1 -C /opt/blender; \
    rm -f /tmp/blender.tar.xz

# gltfpack: same download → verify → install dance.
RUN set -eux; \
    curl -fsSL --retry 3 -o /tmp/gltfpack.zip "$GLTFPACK_URL"; \
    echo "$GLTFPACK_SHA256  /tmp/gltfpack.zip" | sha256sum -c -; \
    mkdir -p /tmp/gltfpack; \
    unzip -q /tmp/gltfpack.zip -d /tmp/gltfpack; \
    install -m 0755 "$(find /tmp/gltfpack -type f -name 'gltfpack*' ! -name '*.txt' | head -n 1)" /opt/gltfpack; \
    /opt/gltfpack -v; \
    rm -rf /tmp/gltfpack /tmp/gltfpack.zip

# --------------------------------------------------------------------------- runtime stage
FROM --platform=linux/amd64 python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PYTHONPATH=/app \
  BLENDER_BIN=/opt/blender/blender \
  GLTFPACK_BIN=/usr/local/bin/gltfpack \
  RENDER_ARTIFACT_STORE=local \
  RENDER_ARTIFACT_DIR=/var/data/render-artifacts \
  RENDER_OUTPUT_PREFIX=render-jobs \
  LOG_LEVEL=INFO

# X11/GL runtime libraries Blender links even in background (-b) mode.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 \
    libxcursor1 libxinerama1 libxrandr2 libsm6 libice6 \
    libgl1 libegl1 libgomp1 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=fetch /opt/blender /opt/blender
COPY --from=fetch /opt/gltfpack /usr/local/bin/gltfpack

WORKDIR /app
# Root-level like requirements-trellis.txt: .dockerignore is an allowlist that admits
# requirements*.txt at the root but excludes deploy/.
COPY requirements-blender-render.txt /app/requirements-blender-render.txt
RUN pip install -r /app/requirements-blender-render.txt

# Only the modules `import pipelines.blender_render.worker` reaches (measured, not guessed).
COPY core/__init__.py /app/core/__init__.py
COPY core/errors/ /app/core/errors/
COPY pipelines/__init__.py /app/pipelines/__init__.py
COPY pipelines/clothing_3d/ /app/pipelines/clothing_3d/
COPY pipelines/blender_render/ /app/pipelines/blender_render/
COPY services/__init__.py /app/services/__init__.py
COPY services/ml/ /app/services/ml/
COPY services/storage/ /app/services/storage/
COPY services/three_d/ /app/services/three_d/
COPY skyyrose/__init__.py /app/skyyrose/__init__.py
COPY skyyrose/core/ /app/skyyrose/core/
COPY skyyrose/elite_studio/__init__.py skyyrose/elite_studio/models.py /app/skyyrose/elite_studio/
COPY skyyrose/elite_studio/pipeline3d/ /app/skyyrose/elite_studio/pipeline3d/
# Product SOT (read-only inside the image; resolved relative to skyyrose/core/product_registry.py).
COPY wordpress-theme/skyyrose-flagship/data/logo-registry.json /app/wordpress-theme/skyyrose-flagship/data/logo-registry.json

# Fail the BUILD if any import is missing, the registry can't load, or Blender can't start headless.
RUN python -c "import pipelines.blender_render.worker, pipelines.blender_render.models as m; m.known_skus()" \
    && /opt/blender/blender -b --version | head -n 1 \
    && gltfpack -v

RUN mkdir -p "$RENDER_ARTIFACT_DIR" \
  && useradd --create-home --uid 10001 worker \
  && chown -R worker:worker /app /var/data
USER worker

# Cheap liveness (no Blender spawn: a Cycles job already saturates the CPU cap, and a full
# Blender start every minute would flap). Blender itself was exercised at build time above.
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import os,sys; sys.exit(0 if os.access(os.environ['BLENDER_BIN'], os.X_OK) and os.access(os.environ['GLTFPACK_BIN'], os.X_OK) else 1)"

ENTRYPOINT ["python", "-m", "pipelines.blender_render.worker"]
