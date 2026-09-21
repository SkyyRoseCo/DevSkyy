#!/usr/bin/env bash
# Import one or more KEY=VALUE lines into a gitignored env file.
#
# The source is the macOS clipboard by default, or --file PATH (use "-" for stdin).
# The target is rewritten atomically with mode 600: only NAME=VALUE lines with a
# non-empty value survive, the last value of a repeated key wins, and the summary
# prints key NAMES only — never a value.
#
# Fails closed: nothing is written when the source has no importable line, or when
# the target is not ignored by git (override that check with --force).
#
#   scripts/env_import.sh                          # clipboard -> .env.local
#   scripts/env_import.sh --file ~/Downloads/x.env # file -> .env.local
#   pass show hf | scripts/env_import.sh --file -  # stdin -> .env.local
set -euo pipefail

CLIPBOARD_CMD="${ENV_IMPORT_CLIPBOARD:-pbpaste}"
SOURCE_FILE=""
TARGET=""
FORCE=0

usage() {
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//' >&2
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --file)
      SOURCE_FILE="${2:-}"
      [ -n "$SOURCE_FILE" ] || usage
      shift 2
      ;;
    --target)
      TARGET="${2:-}"
      [ -n "$TARGET" ] || usage
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h | --help) usage ;;
    *)
      echo "env_import: unknown argument '$1'" >&2
      usage
      ;;
  esac
done

if [ -z "$TARGET" ]; then
  root="$(git rev-parse --show-toplevel 2> /dev/null || true)"
  [ -n "$root" ] || root="$(cd "$(dirname "$0")/.." && pwd)"
  TARGET="$root/.env.local"
fi

umask 077
work="$(mktemp -t env_import)"
incoming="$(mktemp -t env_import)"
trap 'rm -f "$work" "$incoming"' EXIT

if [ -n "$SOURCE_FILE" ]; then
  if [ "$SOURCE_FILE" = "-" ]; then
    cat > "$incoming"
  else
    [ -r "$SOURCE_FILE" ] || {
      echo "env_import: cannot read $SOURCE_FILE" >&2
      exit 4
    }
    cat "$SOURCE_FILE" > "$incoming"
  fi
else
  command -v "$CLIPBOARD_CMD" > /dev/null 2>&1 \
    || {
      echo "env_import: $CLIPBOARD_CMD not found; use --file PATH" >&2
      exit 4
    }
  "$CLIPBOARD_CMD" > "$incoming"
fi

# Count what the source actually offers before touching the target.
importable="$(grep -cE '^[A-Za-z_][A-Za-z0-9_]*=.+' "$incoming" || true)"
present="$(grep -cE '[^[:space:]]' "$incoming" || true)"
if [ "$importable" -eq 0 ]; then
  echo "env_import: no KEY=VALUE line in the source ($present non-blank lines) — nothing written." >&2
  echo "env_import: if you meant the clipboard, copy the keys (not this command) and rerun." >&2
  exit 3
fi

if [ "$FORCE" -ne 1 ] && ! git check-ignore -q "$TARGET" 2> /dev/null; then
  echo "env_import: $TARGET is not ignored by git — refusing to write secrets to it." >&2
  echo "env_import: add it to .gitignore, or pass --force if you are sure." >&2
  exit 5
fi

key_names() {
  grep -oE '^[A-Za-z_][A-Za-z0-9_]*=' "$1" 2> /dev/null | tr -d '=' | sort -u || true
}

before="$(key_names "$TARGET")"

# Last value of a repeated key wins; first appearance sets the order.
# The target may not exist yet, and a failed `cat` would abort the pipeline.
{
  [ -f "$TARGET" ] && cat "$TARGET" || true
  cat "$incoming"
} \
  | awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/ && $2 != "" {
      if (!($1 in seen)) { order[++n] = $1; seen[$1] = 1 }
      line[$1] = $0
    }
    END { for (i = 1; i <= n; i++) print line[order[i]] }' > "$work"

mv "$work" "$TARGET"
chmod 600 "$TARGET"

after="$(key_names "$TARGET")"
added="$(comm -13 <(printf '%s\n' "$before" | grep -v '^$' || true) \
  <(printf '%s\n' "$after" | grep -v '^$' || true) | tr '\n' ' ')"
total="$(printf '%s\n' "$after" | grep -c '[^[:space:]]' || true)"
skipped=$((present - importable))

echo "env_import: $TARGET now holds $total key(s): $(printf '%s\n' "$after" | tr '\n' ' ')"
if [ -n "${added// /}" ]; then
  echo "env_import: new this run: $added"
fi
if [ "$skipped" -gt 0 ]; then
  echo "env_import: skipped $skipped unparseable line(s)"
fi
exit 0
