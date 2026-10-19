#!/usr/bin/env bash
# Install the pinned gltfpack v1.2 (zeux/meshoptimizer) for this host into .tools/bin.
#
# Usage: bash scripts/install_gltfpack.sh [DEST_DIR]      (default: <repo>/.tools/bin)
#
# Fails closed: unsupported platform, download error, or SHA256 mismatch all exit non-zero
# and leave nothing installed. Hashes are the `digest` values published by the GitHub
# Releases API for tag v1.2 (https://api.github.com/repos/zeux/meshoptimizer/releases/tags/v1.2).
set -euo pipefail

GLTFPACK_VERSION="v1.2"
RELEASE_BASE="https://github.com/zeux/meshoptimizer/releases/download/${GLTFPACK_VERSION}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="${1:-${REPO_ROOT}/.tools/bin}"

case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)
    ASSET="gltfpack-macos.zip"
    SHA256="9f5288a6ad585bef3befbc2907c9f9b9fdeeb0b5a29eaa57f0fe15521b82eb28"
    ;;
  Darwin-x86_64)
    ASSET="gltfpack-macos-intel.zip"
    SHA256="bcbd379f212552a84ca19fc986750ce8a4c3fd6c13344df6dbcff7bbf6bc121c"
    ;;
  Linux-x86_64)
    ASSET="gltfpack-ubuntu.zip"
    SHA256="ebc236f5f6c08c7e5c5750476a187d24805d44d8c680449c4b7369c333f817b1"
    ;;
  *)
    echo "install_gltfpack: unsupported platform $(uname -s)-$(uname -m); no v1.2 binary published" >&2
    exit 2
    ;;
esac

if command -v sha256sum > /dev/null 2>&1; then
  SHA_CMD=(sha256sum -c -)
else
  SHA_CMD=(shasum -a 256 -c -)
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "install_gltfpack: downloading ${ASSET} (${GLTFPACK_VERSION})"
curl -fsSL --retry 3 -o "${WORK_DIR}/${ASSET}" "${RELEASE_BASE}/${ASSET}"
echo "${SHA256}  ${WORK_DIR}/${ASSET}" | "${SHA_CMD[@]}"

unzip -q -o "${WORK_DIR}/${ASSET}" -d "${WORK_DIR}/unpacked"
BINARY="$(find "${WORK_DIR}/unpacked" -type f -name 'gltfpack*' ! -name '*.txt' | head -n 1)"
if [[ -z "${BINARY}" ]]; then
  echo "install_gltfpack: archive contained no gltfpack binary" >&2
  exit 1
fi

mkdir -p "${DEST_DIR}"
install -m 0755 "${BINARY}" "${DEST_DIR}/gltfpack"
"${DEST_DIR}/gltfpack" -v
echo "install_gltfpack: installed ${DEST_DIR}/gltfpack (export GLTFPACK_BIN=${DEST_DIR}/gltfpack)"
