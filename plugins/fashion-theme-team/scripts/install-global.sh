#!/usr/bin/env bash
# Install one lazy router with access to the complete canonical package.
set -euo pipefail
plugin_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
install_home="${FASHION_INSTALL_HOME:-$HOME}"
mode="${1:---check}"
case "$mode" in --check|--apply|--remove) ;; *) echo 'Usage: install-global.sh [--check|--apply|--remove]' >&2; exit 2 ;; esac
name=fashion-theme-team-global
# Gemini also supports .agents/skills; its native location is explicit here.
targets=("$install_home/.agents/skills/$name" "$install_home/.cursor/skills/$name" "$install_home/.gemini/skills/$name")
# Check ALL collisions before making changes. Never overwrite unrelated skills.
for target in "${targets[@]}"; do
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -L "$target" || ! -f "$target/.fashion-team-managed" || "$(cat "$target/.fashion-team-managed")" != "$plugin_root" ]]; then
      echo "CONFLICT: $target" >&2; exit 1
    fi
    if [[ ! -L "$target/package" || "$(readlink "$target/package")" != "$plugin_root" ]]; then
      echo "CONFLICT: $target/package" >&2; exit 1
    fi
  fi
done
status=0
for target in "${targets[@]}"; do
  case "$mode" in
    --apply)
      mkdir -p "$target"
      printf '%s\n' "$plugin_root" > "$target/.fashion-team-managed"
      [[ -L "$target/package" ]] || ln -s "$plugin_root" "$target/package"
      cat > "$target/SKILL.md" <<SKILL
---
name: fashion-theme-team-global
description: Use the complete SkyyRose Fashion Theme Team across projects for fashion commerce strategy, design systems, WooCommerce engineering, product fidelity and release evidence.
---

Read \`$target/package/portable/PORTABLE-PROMPT.md\`, then
\`$target/package/skills/fashion-theme-team/SKILL.md\`.
The complete package root is \`$target/package\`.
Resolve skill, brain, reference, agent and script paths against that root.
Load only the relevant skills and charters; never recursively ingest the package.
Use only tools actually available in this host. Missing independent review or
execution capability remains an explicit outstanding gate.
SKILL
      echo "INSTALLED: $target" ;;
    --check)
      if [[ -f "$target/SKILL.md" && -f "$target/package/portable/PORTABLE-PROMPT.md" ]]; then
        echo "PASS: $target"
      else echo "MISSING: $target"; status=1; fi ;;
    --remove)
      if [[ -f "$target/.fashion-team-managed" ]]; then
        rm "$target/SKILL.md" "$target/package" "$target/.fashion-team-managed"
        rmdir "$target" || true
        echo "REMOVED managed files: $target"
      fi ;;
  esac
done
exit "$status"
