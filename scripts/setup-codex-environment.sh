#!/usr/bin/env bash
# Idempotent Codex worktree setup. Creates a local locked Python environment
# with the development tools required by repository verification.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_VENV="$PROJECT_ROOT/.venv"

if ! command -v uv >/dev/null 2>&1; then
	echo "error: uv is required to create the DevSkyy .venv" >&2
	exit 1
fi

if [[ -x "$PROJECT_VENV/bin/python" ]] \
	&& [[ -x "$PROJECT_VENV/bin/pytest" ]] \
	&& [[ -x "$PROJECT_VENV/bin/ruff" ]] \
	&& [[ -x "$PROJECT_VENV/bin/black" ]] \
	&& "$PROJECT_VENV/bin/python" -c "from PIL import Image" >/dev/null 2>&1; then
	echo "DevSkyy .venv already satisfies the Codex verification toolchain."
	exit 0
fi

cd "$PROJECT_ROOT"
uv sync --frozen --extra dev

"$PROJECT_VENV/bin/python" --version
"$PROJECT_VENV/bin/pytest" --version
"$PROJECT_VENV/bin/ruff" --version
"$PROJECT_VENV/bin/black" --version
"$PROJECT_VENV/bin/python" -c "from PIL import Image; print(f'Pillow {Image.__version__}')"
