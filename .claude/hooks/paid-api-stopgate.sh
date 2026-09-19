#!/usr/bin/env bash
# PreToolUse hook — BLOCKING gate for paid / irreversible operations.
#
# Unlike the structural prefetch hooks, this gate is genuinely punitive
# because the action is non-reversible: money spent, production site
# touched, or data destroyed. CLAUDE.md STOP-AND-SHOW protocol explicitly
# mandates explicit confirmation BEFORE such operations.
#
# Fires on Bash tool calls whose command matches known cost / production
# patterns. Emits a manifest (file path, cost estimate, action) on stderr
# and exits 2, forcing Claude to show the manifest to the user and obtain
# explicit "y" / "yes" before retrying.
#
# Bypass: prepend "STOPSHOW_ACK=1 " to the Bash command (which is what
# Claude does after user confirms).

set -euo pipefail

# Fail closed on ANY internal error. For a PreToolUse hook, an exit status
# other than 2 lets the command run, so an unbound variable or a failed
# substitution under `set -eu` would silently un-gate every deploy. The trap
# cannot trust `$?`: macOS /bin/bash 3.2 reports 0 to an EXIT trap after a
# `set -u` abort (repro 2026-09-19). So every deliberate exit goes through
# allow() or block(), and any other exit is turned into a block.
GATE_DECIDED=0
allow() { GATE_DECIDED=1; exit 0; }
fail_closed_on_error() {
    if [[ "${GATE_DECIDED:-0}" != "1" ]]; then
        echo "[paid-api-stopgate] internal error — blocking to fail closed." >&2
        exit 2
    fi
}
trap fail_closed_on_error EXIT

# Fail-closed on missing dependencies: a paid-API gate that silently no-ops
# when jq is absent is worse than no gate at all (user assumes protection
# but operations slip through). See review HIGH finding 2026-05-22.
if ! command -v jq >/dev/null 2>&1; then
    echo "[paid-api-stopgate] FATAL: jq missing from PATH — blocking all Bash calls to fail closed." >&2
    echo "[paid-api-stopgate] Install jq: brew install jq" >&2
    GATE_DECIDED=1
    exit 2
fi

# shellcheck source=lib/common.sh
if [[ ! -f "$(dirname "$0")/lib/common.sh" ]]; then
    echo "[paid-api-stopgate] FATAL: lib/common.sh missing — blocking to fail closed." >&2
    GATE_DECIDED=1
    exit 2
fi
source "$(dirname "$0")/lib/common.sh"

if [[ "${PAID_API_STOPGATE_DISABLE:-0}" == "1" ]]; then
    allow
fi

payload=$(cat)
tool_name=$(read_field "$payload" '.tool_name')
[[ "$tool_name" == "Bash" ]] || allow

command=$(read_field "$payload" '.tool_input.command')
[[ -z "$command" ]] && allow

# Acknowledgement bypass — user already confirmed in this Bash call.
# CRITICAL: must match as a LEADING-PREFIX env assignment, not a substring
# anywhere in the command. Substring match was trivially bypassed by
# embedding the token in a string literal or flag value
# (e.g., --label="STOPSHOW_ACK=1"). See review CRITICAL 2026-05-22.
# 2026-07-07: also accept the token after OTHER leading env assignments
# (e.g. `ENV_FILE=/x STOPSHOW_ACK=1 bash ...`). Only assignment-shaped
# tokens ([A-Za-z_]NAME=value) are consumed from the very start of the
# command, so a token buried in a flag or string literal still never
# reaches command position and cannot bypass.
if [[ "$command" == "STOPSHOW_ACK=1 "* ]] || [[ "$command" == "env STOPSHOW_ACK=1 "* ]]; then
    allow
fi
stripped="${command#env }"
while [[ "$stripped" =~ ^([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*)[[:space:]]+ ]]; do
    if [[ "${BASH_REMATCH[1]}" == "STOPSHOW_ACK=1" ]]; then
        allow
    fi
    stripped="${stripped:${#BASH_REMATCH[0]}}"
done

block() {
    cat >&2 <<EOF
[paid-api-stopgate] BLOCKED — STOP-AND-SHOW required per DevSkyy CLAUDE.md.

  Category:  $1
  Estimate:  $2
  Command:   $command

This operation costs money, touches production, or is irreversible. Per the
STOP-AND-SHOW protocol you MUST:

  1. Print the exact manifest above to the user.
  2. Wait for explicit "y" / "yes" confirmation.
  3. Re-issue the Bash call with STOPSHOW_ACK=1 prepended:
       STOPSHOW_ACK=1 $command

Do NOT run the command without confirmation. Apologizing after spending
money or breaking the site is not acceptable. The bypass token signals
that the user has explicitly approved THIS specific invocation.
EOF
    GATE_DECIDED=1
    exit 2
}

# ---- Tier 1: substring rules, matched against the raw command ----
# Paid HTTP endpoints, paid render CLIs and destructive filesystem ops stay
# unanchored: any mention of them in a command is treated as a call.
# Each rule: <regex>:::<category>:::<estimate>  (`:::` keeps regex `|` intact).
SUBSTRING_RULES=(
    # renders/fashn.py, renders/generate.py and scripts/seedream_ghost_mannequin.py
    # no longer exist on main (verified 2026-09-18) — their rules were removed;
    # the direct-HTTP rules below still cover those vendors.
    'python.*tripo:::Tripo3D multiview / mesh generation:::~$0.10–$0.50 per dispatch'
    'python.*meshy:::Meshy 3D mesh / texture generation:::~$0.20–$1.00 per mesh'
    'python.*seedream.*--go:::Seedream-4 / fal image generation (paid):::~$0.06 per image (model-dependent)'
    # ---- OpenAI gpt-image-2 render pipeline (closes coverage gap 2026-06-18) ----
    '(oai-render-run\.py\s+generate|oai_render/cli\.py.*generate):::OpenAI gpt-image-2 render generate (paid):::~$0.40 per image (EST_COST_PER_IMAGE_USD), $50 hard run cap'
    # ---- Direct-HTTP coverage (closes review HIGH finding 2026-05-22) ----
    '(curl|wget|httpx|http\s+|python.*requests).*api\.fashn\.ai:::FASHN direct HTTP (paid):::~$0.075/sample + $0.025/bg-remove'
    '(curl|wget|httpx).*api\.openai\.com/v1/images:::OpenAI DALL-E direct HTTP (paid):::~$0.04 per image (DALL-E 3 standard)'
    '(curl|wget|httpx).*generativelanguage\.googleapis\.com.*(imagen|generateImage):::Gemini Imagen direct HTTP (paid):::~$0.04 per image'
    '(curl|wget|httpx).*fal\.(run|ai):::fal.ai direct HTTP (paid):::~$0.05 per call (model-dependent)'
    '(curl|wget|httpx).*api\.together\.xyz.*images:::Together.ai image direct HTTP (paid):::~$0.005–$0.05 per image'
    '(curl|wget|httpx).*api\.replicate\.com:::Replicate direct HTTP (paid):::variable per model, $0.001–$0.50 per prediction'
    '(curl|wget|httpx).*(platform\.tripo3d|api\.tripo3d):::Tripo3D direct HTTP (paid):::~$0.10–$0.50 per dispatch'
    '(curl|wget|httpx).*api\.meshy\.ai:::Meshy direct HTTP (paid):::~$0.20–$1.00 per mesh'
    'run_managed_agent\.sh.*--budget:::Managed agent run with budget (paid):::budgeted LLM spend'
    # ---- Destructive shell ops ----
    '(rm\s+-rf\s+/\s*$|rm\s+-rf\s+/\s+|rm\s+-rf\s+~|rm\s+-rf\s+\$\{?HOME\}?|rm\s+(-[a-z]*r[a-z]*f[a-z]*|-[a-z]*f[a-z]*r[a-z]*|--recursive.*--force|--force.*--recursive)\s+/):::Recursive delete of system / home directory:::IRREVERSIBLE data loss'
    'git\s+reset\s+--hard\s+(origin|HEAD~):::Hard reset:::destructive: discards local commits'
    '(npx\s+claude-mem.*delete|claude-mem\s+delete):::claude-mem deletion:::memory loss (semi-irreversible)'
)

for rule in "${SUBSTRING_RULES[@]}"; do
    pattern="${rule%%:::*}"
    rest="${rule#*:::}"
    if printf '%s' "$command" | grep -qE -- "$pattern"; then
        block "${rest%%:::*}" "${rest#*:::}"
    fi
done

# ---- Tier 2: program rules, matched per command segment (2026-09-19) ----
# Deploys and production mutations gate on the program that actually RUNS: a
# read-only mention (grep/cat/sed of a deploy script) passes, every executing
# shape is caught. The 2026-09-18 command-position anchor was too narrow — it
# let `(bash x)`, `timeout 60 bash x`, `bash -c "bash x"`, `bash "x"`,
# `bash x; echo`, `nohup … &`, `xargs … bash x` through (review 2026-09-19).
# Normalization:
#   1. drop quotes and backslashes — a quoted path or a `bash -c "…"` body
#      still executes, and `\`-continued lines become plain lines;
#   2. one segment per command: newline ; & | ( ) { } and backticks split;
#   3. strip leading wrappers from each segment until none is left: NAME=value
#      assignments, env/sudo/nohup/time/exec/command/caffeinate/eval/rtk,
#      shell keywords (if/then/do/…), timeout N, nice, xargs, `sh -c`.
# Every rule below is then anchored at the START of the segment.
# Regression matrix: tests/hooks/test_paid_api_stopgate.py.
P='([^[:space:]]*/)?'
RE_WRAP="^([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*|${P}(env|sudo|nohup|time|exec|command|builtin|caffeinate|noglob|eval|rtk|proxy|if|then|do|else|elif|while|until|!))([[:space:]]+-[^[:space:]]*)*[[:space:]]+"
RE_TIMEOUT="^${P}g?timeout([[:space:]]+-[A-Za-z]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+[0-9.]+[smhd]?[[:space:]]+"
RE_NICE="^${P}nice([[:space:]]+-n)?([[:space:]]+-?[0-9]+)?[[:space:]]+"
RE_XARGS="^${P}xargs([[:space:]]+-[A-Za-z0-9]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+"
RE_SHELL_C="^${P}(bash|sh|zsh)([[:space:]]+-[A-Za-z]+)*[[:space:]]+-[A-Za-z]*c[[:space:]]+"

strip_wrappers() {
    local s="$1" prev re
    while :; do
        prev="$s"
        s="${s#"${s%%[![:space:]]*}"}"
        for re in "$RE_WRAP" "$RE_TIMEOUT" "$RE_NICE" "$RE_XARGS" "$RE_SHELL_C"; do
            if [[ "$s" =~ $re ]]; then
                s="${s:${#BASH_REMATCH[0]}}"
                break
            fi
        done
        [[ "$s" == "$prev" ]] && break
    done
    printf '%s' "$s"
}

# `bash -n` parses without executing — a syntax check is not a deploy.
RE_SYNTAX_ONLY="^${P}(bash|sh|zsh)[[:space:]]+-n([[:space:]]|$)"
# An optional interpreter (with flags) and an optional path before the script.
RE_SCRIPT="^(${P}(bash|sh|zsh|source|\\.)([[:space:]]+-[^[:space:]]+)*[[:space:]]+)?${P}"
# npm/pnpm/yarn deploy scripts; BASH_REMATCH[5] is the script name.
RE_PKG_DEPLOY='^(npm|pnpm|yarn)([[:space:]]+(run|run-script|-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?))*[[:space:]]+(deploy(:[A-Za-z0-9:_-]+)?)([[:space:]]|$)'
RE_PKG_READ_ONLY='^deploy(:[A-Za-z0-9_-]+)*:dry$|^deploy:verify(:[A-Za-z0-9_-]+)*$'
RE_VERCEL='^(npx[[:space:]]+)?vercel([[:space:]]+[^[:space:]]+)*[[:space:]]+(deploy|--prod)([[:space:]=]|$)'
RE_FLY='^(fly|flyctl)([[:space:]]+[^[:space:]]+)*[[:space:]]+deploy([[:space:]]|$)'
RE_FORCE_PUSH='^git([[:space:]]+-[Cc][[:space:]]+[^[:space:]]+)*[[:space:]]+push([[:space:]]+[^[:space:]]+)*[[:space:]]+(--force(-with-lease)?(=[^[:space:]]*)?|-[A-Za-z]*f[A-Za-z]*|\+[^[:space:]]+)([[:space:]]|$)'
WP_BIN='(wp|wp-cli)([[:space:]]+--[^[:space:]]+)*[[:space:]]+'
WP_MUTATE="${WP_BIN}(theme[[:space:]]+(activate|delete|install)|option[[:space:]]+(update|set)[[:space:]]+(stylesheet|template)|db[[:space:]]+(import|reset|drop)|search-replace)([[:space:]]|$)"
WP_WRITE="${WP_BIN}(media[[:space:]]+import|post[[:space:]]+(create|update|delete))([[:space:]]|$)"

# Deploy-script rules: <basename regex>:::<category>:::<estimate>
# Two themes, two targets (2026-09-18): scripts/deploy-staging.sh → staging,
# scripts/deploy-production.sh → skyyrose.co; both wrap the engine
# scripts/deploy-theme.sh, which refuses to run without DEPLOY_TARGET and is
# gated as production when invoked directly. Each is its own STOP-AND-SHOW.
SCRIPT_RULES=(
    'deploy-staging\.sh:::WordPress STAGING deploy (staging-7e48-skyyrose.wpcomstaging.com):::none direct, but the staging theme is replaced'
    'deploy-production\.sh:::WordPress PRODUCTION deploy (skyyrose.co):::none direct, but production site touched'
    'deploy-theme\.sh:::WordPress PRODUCTION deploy (skyyrose.co) — scripts/deploy-theme.sh is the engine behind deploy-staging.sh / deploy-production.sh; run a wrapper instead:::none direct, but production site touched'
    'deploy-mu-plugin\.sh:::WordPress PRODUCTION deploy (skyyrose.co) — MU-plugin:::none direct, but production site touched'
)

check_scripts() {
    local seg="$1" rule re
    [[ "$seg" =~ $RE_SYNTAX_ONLY ]] && return 0
    for rule in "${SCRIPT_RULES[@]}"; do
        re="${RE_SCRIPT}${rule%%:::*}([[:space:]]|$)"
        if [[ "$seg" =~ $re ]]; then
            rule="${rule#*:::}"
            block "${rule%%:::*}" "${rule#*:::}"
        fi
    done
    return 0
}

check_programs() {
    local seg="$1" wp_anchor='^' re script
    if [[ "$seg" =~ $RE_PKG_DEPLOY ]]; then
        script="${BASH_REMATCH[5]}"  # captured before the next =~ overwrites BASH_REMATCH
        if ! [[ "$script" =~ $RE_PKG_READ_ONLY ]]; then
            block "npm run deploy (${script}) → WordPress staging/production or Vercel production (deploy:*:dry and deploy:verify* are read-only)" \
                "production or staging site touched (skyyrose.co, staging, or devskyy.app)"
        fi
    fi
    if [[ "$seg" =~ $RE_VERCEL ]]; then
        block "Dashboard production deploy (Vercel — retiring; devskyy.app returns 402)" \
            "none direct, but production site touched"
    fi
    if [[ "$seg" =~ $RE_FLY ]]; then
        block "API production deploy (Fly, api.devskyy.app)" "none direct, but the API host is replaced"
    fi
    if [[ "$seg" =~ $RE_FORCE_PUSH ]]; then
        block "Force push" "destructive: rewrites remote history"
    fi
    # Over ssh the remote command follows the host and any flag values, so the
    # wp-cli rules match at any word boundary inside an ssh segment.
    re="^${P}ssh[[:space:]]"
    [[ "$seg" =~ $re ]] && wp_anchor='(^|[[:space:]])'
    re="${wp_anchor}${WP_MUTATE}"
    if [[ "$seg" =~ $re ]]; then
        block "WordPress production mutation (wp theme activate/delete/install · option stylesheet/template · db import/reset/drop · search-replace)" \
            "production site state changed; theme cutover is its own STOP-AND-SHOW"
    fi
    re="${wp_anchor}${WP_WRITE}"
    if [[ "$seg" =~ $re ]]; then
        block "WordPress.com REST write (production)" "production data mutation"
    fi
    return 0
}

segments=$(printf '%s\n' "$command" | tr -d "\"'\\\\" | tr ';&|(){}`' '\n\n\n\n\n\n\n\n')
while IFS= read -r seg; do
    seg=$(strip_wrappers "$seg")
    [[ -z "$seg" ]] && continue
    check_scripts "$seg"
    check_programs "$seg"
done <<< "$segments"

allow
