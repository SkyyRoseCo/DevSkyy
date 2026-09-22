#!/usr/bin/env bash
set -euo pipefail
THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$THEME_DIR"
npm run build
npm run verify
python3 ../../tools/v2-source-certification/package.py
