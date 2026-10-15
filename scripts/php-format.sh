#!/usr/bin/env bash
# Auto-format staged WordPress PHP files with THEIR theme's WPCS ruleset.
#
# Every wordpress-theme/<theme>/ directory declares its own coding standard
# (.phpcs.xml, or phpcs.xml — PHPCS's own discovery order). Files are grouped
# by theme and each group is passed to phpcbf with that theme's ruleset, so one
# theme's text domain and prefixes are never applied to another theme's code.
# A theme with no ruleset is skipped with a printed notice — it is never
# formatted under a foreign standard. The phpcbf binary is a shared tool (it
# lives in the flagship vendor tree); the standard it applies is per theme.
#
# PHPCBF returns 1 when it successfully fixes violations, so this wrapper
# normalizes 0 and 1 to success while preserving real tool/config failures.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2> /dev/null || pwd)"
THEMES_DIR="$REPO_ROOT/wordpress-theme"
PHPCBF="${PHPCBF:-$THEMES_DIR/skyyrose-flagship/vendor/bin/phpcbf}"

if [[ ! -x "$PHPCBF" ]]; then
  echo "PHP formatter missing: $PHPCBF" >&2
  echo "Run: cd '$THEMES_DIR/skyyrose-flagship' && composer install" >&2
  exit 2
fi

# The ruleset a theme directory declares, in PHPCS's own discovery order.
ruleset_for() {
  local dir="$1" name
  for name in .phpcs.xml phpcs.xml .phpcs.xml.dist phpcs.xml.dist; do
    if [[ -f "$dir/$name" ]]; then
      printf '%s\n' "$dir/$name"
      return 0
    fi
  done
  return 1
}

# The wordpress-theme/<theme>/ slug a file belongs to, or nothing.
theme_of() {
  local file="$1" rel
  case "$file" in
    /*) rel="${file#"$REPO_ROOT"/}" ;;
    *) rel="$file" ;;
  esac
  case "$rel" in
    wordpress-theme/*/*)
      rel="${rel#wordpress-theme/}"
      printf '%s\n' "${rel%%/*}"
      ;;
  esac
}

declare -a files=()
for file in "$@"; do
  case "$file" in
    -*) continue ;;
  esac
  [[ -f "$file" ]] || continue
  files+=("$file")
done

if [[ ${#files[@]} -eq 0 ]]; then
  exit 0
fi

# Distinct theme slugs, in first-seen order (bash 3.2: no associative arrays).
themes=""
for file in "${files[@]}"; do
  theme="$(theme_of "$file")"
  if [[ -z "$theme" ]]; then
    echo "php-format: skipping $file — not under wordpress-theme/<theme>/, no ruleset applies" >&2
    continue
  fi
  case " $themes " in
    *" $theme "*) ;;
    *) themes="$themes $theme" ;;
  esac
done

worst=0
for theme in $themes; do
  theme_dir="$THEMES_DIR/$theme"
  if ! standard="$(ruleset_for "$theme_dir")"; then
    echo "php-format: NOTICE — wordpress-theme/$theme has no PHPCS ruleset (.phpcs.xml / phpcs.xml / *.dist); its PHP is left unformatted (another theme's standard is never applied)" >&2
    continue
  fi

  declare -a group=()
  for file in "${files[@]}"; do
    [[ "$(theme_of "$file")" == "$theme" ]] && group+=("$file")
  done

  echo "php-format: wordpress-theme/$theme → ${standard#"$REPO_ROOT"/} (${#group[@]} file(s))"
  "$PHPCBF" --standard="$standard" --extensions=php --report=summary "${group[@]}"
  status=$?

  # 0: already clean. 1: all fixable violations were repaired.
  if [[ "$status" -gt 1 && "$status" -gt "$worst" ]]; then
    worst=$status
  fi
done

exit "$worst"
