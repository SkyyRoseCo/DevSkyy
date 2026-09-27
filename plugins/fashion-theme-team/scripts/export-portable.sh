#!/usr/bin/env bash
set -euo pipefail
plugin_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output="${1:?Usage: export-portable.sh /absolute/path/fashion-theme-team.tar.gz}"
[[ "$output" = /* && ! -e "$output" ]] || { echo 'Output must be absolute and must not exist' >&2; exit 2; }
# Fixed package roots; never include repository metadata, credentials or local output.
tar -C "$plugin_root" --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.pytest_cache' --exclude='.mypy_cache' --exclude='.ruff_cache' \
  --exclude='.DS_Store' --exclude='.coverage' --exclude='node_modules' \
  --exclude='.env' --exclude='.env.*' --exclude='runtime/elite_web_builder/output' \
  -czf "$output" .codex-plugin .claude-plugin agents hooks skills scripts \
  vendor runtime portable tasks requirements-verify.txt requirements-formatting.txt \
  pyproject.toml formatting.toml .prettierrc.json .prettierignore .editorconfig
shasum -a 256 "$output"
