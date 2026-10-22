#!/usr/bin/env bash
#
# scripts/secret-scan.sh — the gitleaks gate shared by .husky/pre-commit and
# .husky/pre-push.
#
#   secret-scan.sh staged  [--hook NAME] [--repo DIR]   scan the index (pre-commit)
#   secret-scan.sh push    [--hook NAME] [--repo DIR]   scan the commits being pushed;
#                                                       pre-push ref lines on stdin
#   secret-scan.sh version                              pinned vs installed version
#
# Fails CLOSED (bug-230): a missing or broken gitleaks, an unreadable config or a
# scanner error blocks with an actionable message — it never passes quietly.
# Findings block too. gitleaks runs with --exit-code 2 so the two causes stay
# distinguishable (2 = findings, 1 = scanner error).
#
# Never prints a secret: gitleaks always runs with --redact, its output goes to
# a temp file, and the only finding fields echoed are rule id, file, commit short
# sha and line (bug-357: a key-side token can be the secret, so even the matched
# line is never shown).
#
# Bypass ONE invocation, loudly logged, same pattern as WOLF_HANDOFF_SKIP:
#   SECRETS_SCAN_SKIP=1 git commit …      SECRETS_SCAN_SKIP=1 git push …
# There is no other bypass in this script.
#
# Version: GITLEAKS_VERSION is the single pin; .github/workflows/security-gate.yml
# installs the same one so a commit that passes here passes CI. Install locally
# with `brew install gitleaks`. Drift inside major 8 warns; another major blocks
# (the CLI surface changed between majors).

set -u

GITLEAKS_VERSION="8.30.1"
SCRIPT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

MODE="${1:-}"
[ $# -gt 0 ] && shift
HOOK="secret-scan"
REPO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --hook)
      HOOK="$2"
      shift 2
      ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    *)
      echo "secret-scan: unknown argument '$1'" >&2
      exit 1
      ;;
  esac
done

say() { echo "secret-scan ($HOOK): $*"; }
die() {
  echo "✗ secret-scan ($HOOK): $*" >&2
  exit 1
}

case "$MODE" in
  staged | push | version) ;;
  *) die "usage: secret-scan.sh staged|push|version [--hook NAME] [--repo DIR]" ;;
esac

# ── the single bypass ──────────────────────────────────────────────────────────
if [ "${SECRETS_SCAN_SKIP:-0}" = "1" ] && [ "$MODE" != "version" ]; then
  echo "⚠ secret-scan ($HOOK): SECRETS_SCAN_SKIP=1 — gitleaks gate BYPASSED for this one $MODE scan. Rotate anything you knowingly skipped." >&2
  exit 0
fi

# ── scanner present and sane ───────────────────────────────────────────────────
if ! command -v gitleaks > /dev/null 2>&1; then
  die "gitleaks is not installed, so the secrets gate cannot run (fail-closed).
  Install: brew install gitleaks      (pinned: $GITLEAKS_VERSION; CI installs the same)
  Bypass this ONE $MODE: SECRETS_SCAN_SKIP=1"
fi
INSTALLED="$(gitleaks version 2> /dev/null | tr -d '[:space:]')"
INSTALLED="${INSTALLED#v}"
[ -n "$INSTALLED" ] || die "'gitleaks version' printed nothing — the binary is broken. Reinstall: brew reinstall gitleaks"
if [ "${INSTALLED%%.*}" != "${GITLEAKS_VERSION%%.*}" ]; then
  die "gitleaks $INSTALLED installed, major ${GITLEAKS_VERSION%%.*} required (pinned $GITLEAKS_VERSION). brew upgrade gitleaks"
fi
if [ "$MODE" = "version" ]; then
  echo "pinned=$GITLEAKS_VERSION installed=$INSTALLED"
  [ "$INSTALLED" = "$GITLEAKS_VERSION" ]
  exit $?
fi
if [ "$INSTALLED" != "$GITLEAKS_VERSION" ]; then
  echo "⚠ secret-scan ($HOOK): gitleaks $INSTALLED installed, CI pins $GITLEAKS_VERSION — rule sets may differ. brew upgrade gitleaks" >&2
fi
# v8.19 replaced `detect`/`protect` with `git`/`dir`; the old spellings still
# exist as deprecated aliases but we use whichever the installed binary owns.
if gitleaks git --help > /dev/null 2>&1; then MODERN=1; else MODERN=0; fi

# ── repo and config ────────────────────────────────────────────────────────────
[ -n "$REPO" ] || REPO="$(git rev-parse --show-toplevel 2> /dev/null)"
[ -n "$REPO" ] && [ -d "$REPO" ] || die "not inside a git repository (pass --repo DIR)"
CONFIG="$REPO/.gitleaks.toml"
[ -f "$CONFIG" ] || CONFIG="$SCRIPT_ROOT/.gitleaks.toml"
[ -f "$CONFIG" ] && [ -r "$CONFIG" ] || die ".gitleaks.toml not found/readable in $REPO or $SCRIPT_ROOT — the gate cannot run. Restore it: git checkout origin/main -- .gitleaks.toml"

# ── one gitleaks run; prints findings as rule/file/commit/line only ────────────
LOG="$(mktemp "${TMPDIR:-/tmp}/secret-scan-log.XXXXXX")"
REPORT="$(mktemp "${TMPDIR:-/tmp}/secret-scan-report.XXXXXX")"
trap 'rm -f "$LOG" "$REPORT"' EXIT

summarize() {
  # The JSON report is parsed by field NAME only; Match/Secret/Line are never read.
  awk '
    /^[[:space:]]*"(RuleID|File|Commit|StartLine)":/ {
      k = $1; sub(/^[[:space:]]*"/, "", k); sub(/".*/, "", k)
      v = $0; sub(/^[^:]*:[[:space:]]*/, "", v); sub(/,[[:space:]]*$/, "", v); gsub(/"/, "", v)
      f[k] = v
    }
    /^[[:space:]]*}/ && ("RuleID" in f) {
      printf "    %-24s %s", f["RuleID"], f["File"]
      if (f["Commit"] != "") printf "  @ %s", substr(f["Commit"], 1, 7)
      printf "  line %s\n", f["StartLine"]
      delete f
    }' "$REPORT"
}

run_scan() { # $1 = human label for messages, $2… = mode-specific gitleaks flags
  label="$1"
  shift
  : > "$REPORT"
  if [ "$MODERN" = 1 ]; then
    (cd "$REPO" && gitleaks git --no-banner --redact --exit-code 2 --config "$CONFIG" \
      -f json -r "$REPORT" "$@" "$REPO") > "$LOG" 2>&1
  else
    (cd "$REPO" && gitleaks "$LEGACY_CMD" --no-banner --redact --exit-code 2 --config "$CONFIG" \
      -f json -r "$REPORT" --source "$REPO" "$@") > "$LOG" 2>&1
  fi
  rc=$?
  case "$rc" in
    0) return 0 ;;
    2)
      n="$(grep -c '"RuleID"' "$REPORT" 2> /dev/null || echo '?')"
      echo "✗ secret-scan ($HOOK): gitleaks found $n potential secret(s) in $label:" >&2
      summarize >&2
      echo "  Remove the secret and rotate it if it was ever real. A documented false positive is" >&2
      echo "  allowlisted in .gitleaks.toml (with the reason) — never by weakening the gate." >&2
      echo "  Bypass this ONE $MODE: SECRETS_SCAN_SKIP=1" >&2
      return 1
      ;;
    *)
      echo "✗ secret-scan ($HOOK): gitleaks exited $rc (scanner error, not a finding) — fix the scanner, the gate stays closed:" >&2
      sed 's/^/    /' "$LOG" >&2
      echo "  Bypass this ONE $MODE: SECRETS_SCAN_SKIP=1" >&2
      return 1
      ;;
  esac
}

case "$MODE" in
  staged)
    LEGACY_CMD="protect"
    run_scan "staged content" --staged || exit 1
    say "staged content clean (gitleaks $INSTALLED)"
    ;;
  push)
    LEGACY_CMD="detect"
    REFS="$(cat)"
    if [ -z "$(printf '%s' "$REFS" | tr -d '[:space:]')" ]; then
      say "no refs on stdin — nothing to scan"
      exit 0
    fi
    scanned=0
    while read -r local_ref local_sha remote_ref remote_sha; do
      [ -n "$local_ref" ] || continue
      case "$local_sha" in
        *[!0]*) ;;
        *)
          say "skip $remote_ref (deletion)"
          continue
          ;;
      esac
      case "$remote_sha" in
        *[!0]*)
          range="$remote_sha..$local_sha"
          what="$remote_ref ${remote_sha:0:7}..${local_sha:0:7}"
          ;;
        *)
          range="$local_sha --not --remotes"
          what="$remote_ref (new branch: commits not on any remote)"
          ;;
      esac
      run_scan "$what" --log-opts="$range" || exit 1
      scanned=$((scanned + 1))
    done << EOF
$REFS
EOF
    say "$scanned ref(s) clean (gitleaks $INSTALLED)"
    ;;
esac
