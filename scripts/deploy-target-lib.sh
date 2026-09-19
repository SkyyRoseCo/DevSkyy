#!/usr/bin/env bash
# scripts/deploy-target-lib.sh -- shared body of deploy-staging.sh / deploy-production.sh
#
# Sourced by the two wrappers, never executed. Provides:
#   deploy_target_main <target> <env_file> <theme_dir> [engine args...]
#
# The wrappers own target selection (founder directive 2026-09-18: separate
# staging and production scripts). This lib validates the chosen env file
# against the chosen target WITHOUT sourcing it (no secret enters the wrapper
# process; the engine sources the file itself), pins DEPLOY_TARGET / ENV_FILE /
# THEME_DIR_OVERRIDE, and execs scripts/deploy-theme.sh.
#
# One-shot override flags (consumed here, never forwarded to the engine's
# argv; each becomes an env var the exec'd engine alone sees):
#   --allow-new-theme-folder       -> ALLOW_NEW_THEME_FOLDER=1
#   --allow-theme-identity-change  -> ALLOW_THEME_IDENTITY_CHANGE=1
# The same variables (and PUBLIC_URL / WORDPRESS_URL / PREFLIGHT_SKIP_COMPLETENESS)
# are refused when they arrive from the caller's environment.
#
# Every refusal exits 1 with a plain-language reason. Gates fail CLOSED: a
# missing file, a missing URL, an unexpected host, an SSH account that does not
# belong to the host, userinfo in the URL, or an unexpected theme folder all
# refuse -- nothing defaults to production.

dt_log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1" >&2; }
dt_log_info()  { echo -e "\033[0;34m[INFO]\033[0m $1"; }

# Value of KEY=... from an env file, last assignment wins, surrounding quotes
# stripped. grep-based on purpose -- `source` would execute the file.
dt_env_value() {
    local file="$1" key="$2" raw
    raw="$(grep -E "^[[:space:]]*(export[[:space:]]+)?${key}=" "$file" | tail -1 || true)"
    [[ -n "$raw" ]] || return 0
    raw="${raw#*=}"
    raw="${raw%\"}"; raw="${raw#\"}"
    raw="${raw%\'}"; raw="${raw#\'}"
    printf '%s' "$raw"
}

# Lower-cased host of a URL (scheme, port, path, query and fragment stripped).
dt_url_host() {
    printf '%s' "$1" | sed -E 's#^[A-Za-z][A-Za-z0-9+.-]*://##; s#[/:?#].*$##' | tr '[:upper:]' '[:lower:]'
}

# The URL authority: everything between :// and the first /. Userinfo ('@')
# in it means the host dt_url_host() returns is not the host curl would use.
dt_url_authority() {
    local rest="${1#*://}"
    printf '%s' "${rest%%/*}"
}

# WP.com SSH/SFTP account for a public host: "<first DNS label, leading www.
# removed>.wordpress.com" (skyyrose.co -> skyyrose.wordpress.com;
# staging-7e48-skyyrose.wpcomstaging.com -> staging-7e48-skyyrose.wordpress.com).
dt_expected_ssh_user() {
    local host="${1#www.}"
    printf '%s.wordpress.com' "${host%%.*}"
}

# Inherited target-selection and override variables are rejected, not merged:
# a caller who exports ENV_FILE=.env.wordpress and runs deploy-staging.sh has
# a mismatch between intent and command, and an exported ALLOW_* override is
# a habit, not a decision. The safe answer is to stop.
dt_refuse_inherited() {
    local v
    for v in ENV_FILE THEME_DIR_OVERRIDE DEPLOY_TARGET PUBLIC_URL WORDPRESS_URL \
             ALLOW_THEME_IDENTITY_CHANGE ALLOW_NEW_THEME_FOLDER PREFLIGHT_SKIP_COMPLETENESS; do
        if [[ -n "${!v:-}" ]]; then
            dt_log_error "$v is already set in the environment -- the deploy wrappers own target selection and overrides and accept no inherited value. Unset $v and re-run (overrides: --allow-new-theme-folder / --allow-theme-identity-change)."
            exit 1
        fi
    done
}

dt_check_host() {
    local target="$1" host="$2"
    case "$target" in
        production)
            if [[ "$host" == "skyyrose.co" || "$host" == "www.skyyrose.co" ]]; then
                return 0
            fi
            dt_log_error "PUBLIC_URL host '${host}' is not skyyrose.co -- refusing a PRODUCTION deploy to it"
            ;;
        staging)
            if [[ "$host" == *.wpcomstaging.com ]]; then
                return 0
            fi
            dt_log_error "PUBLIC_URL host '${host}' is not a *.wpcomstaging.com staging host -- refusing a STAGING deploy to it (skyyrose.co is production)"
            ;;
        *)
            dt_log_error "Unknown target '${target}'"
            ;;
    esac
    return 1
}

# The SSH destination must belong to the target site: SSH_USER must be the
# host's own WP.com account and SFTP_USER (when set) must equal SSH_USER. The
# values are read into locals and never printed -- only the expected account
# (derived from the public URL) and the offending key name are.
dt_check_ssh_destination() {
    local env_file="$1" host="$2" expected ssh_user sftp_user
    expected="$(dt_expected_ssh_user "$host")"
    ssh_user="$(dt_env_value "$env_file" SSH_USER)"
    sftp_user="$(dt_env_value "$env_file" SFTP_USER)"
    if [[ "$ssh_user" != "$expected" ]]; then
        dt_log_error "SSH_USER in ${env_file} does not belong to host ${host}: expected '${expected}' (derived from PUBLIC_URL) -- refusing; the SSH destination must be the target site's own account"
        return 1
    fi
    if [[ -n "$sftp_user" && "$sftp_user" != "$ssh_user" ]]; then
        dt_log_error "SFTP_USER in ${env_file} differs from SSH_USER (expected both to be '${expected}') -- refusing"
        return 1
    fi
    return 0
}

DT_HOST=""
DT_FOLDER=""
# Validates the env file against the target; sets DT_HOST / DT_FOLDER.
dt_validate_env_file() {
    local target="$1" env_file="$2" url theme_path
    if [[ ! -f "$env_file" ]]; then
        dt_log_error "Env file missing: ${env_file} -- copy ${env_file}.example, fill in the ${target} credentials, then re-run"
        exit 1
    fi
    url="$(dt_env_value "$env_file" PUBLIC_URL)"
    [[ -n "$url" ]] || url="$(dt_env_value "$env_file" WORDPRESS_URL)"
    if [[ -z "$url" ]]; then
        dt_log_error "${env_file} has no PUBLIC_URL (or WORDPRESS_URL) -- refusing to deploy to an unknown site"
        exit 1
    fi
    if [[ "$(dt_url_authority "$url")" == *@* ]]; then
        dt_log_error "PUBLIC_URL/WORDPRESS_URL in ${env_file} carries userinfo ('@' in the authority) -- the real host would differ from the one checked; refusing"
        exit 1
    fi
    DT_HOST="$(dt_url_host "$url")"
    dt_check_host "$target" "$DT_HOST" || exit 1
    dt_check_ssh_destination "$env_file" "$DT_HOST" || exit 1
    theme_path="$(dt_env_value "$env_file" WP_THEME_PATH)"
    DT_FOLDER="$(basename "${theme_path:-/}")"
    if [[ "$DT_FOLDER" != "skyyrose-flagship-2" ]]; then
        dt_log_error "WP_THEME_PATH in ${env_file} ends in '${DT_FOLDER:-?}' -- expected 'skyyrose-flagship-2'; refusing"
        if [[ "$target" == "production" ]]; then
            dt_log_error "Production still points at the pre-cutover folder. That is expected until the founder-approved env switch: set WP_THEME_PATH=.../skyyrose-flagship-2 in .env.wordpress as the first cutover step, then re-run."
        fi
        exit 1
    fi
}

# Splits the wrapper's own one-shot flags from the args forwarded to the
# engine. DT_ENGINE_ARGS may be empty: expand it with the
# ${arr[@]+"${arr[@]}"} idiom (bash 3.2 + set -u).
DT_ENGINE_ARGS=()
DT_ALLOW_NEW_FOLDER=0
DT_ALLOW_IDENTITY_CHANGE=0
dt_parse_flags() {
    local a
    for a in "$@"; do
        case "$a" in
            --allow-new-theme-folder)      DT_ALLOW_NEW_FOLDER=1 ;;
            --allow-theme-identity-change) DT_ALLOW_IDENTITY_CHANGE=1 ;;
            *)                             DT_ENGINE_ARGS+=("$a") ;;
        esac
    done
}

# Exports the consumed flags as the engine's internal override variables --
# only into the process about to be exec'd, never before dt_refuse_inherited.
dt_export_overrides() {
    if [[ "$DT_ALLOW_NEW_FOLDER" == 1 ]]; then
        export ALLOW_NEW_THEME_FOLDER=1
        dt_log_info "--allow-new-theme-folder: the engine may create a theme folder the site does not have yet"
    fi
    if [[ "$DT_ALLOW_IDENTITY_CHANGE" == 1 ]]; then
        export ALLOW_THEME_IDENTITY_CHANGE=1
        dt_log_info "--allow-theme-identity-change: the engine may replace a live theme whose Name/Text Domain differ"
    fi
}

dt_usage() {
    local target="$1" env_file="$2"
    echo "Usage: deploy-${target}.sh [--dry-run] [--with-maintenance]"
    echo "       [--allow-new-theme-folder] [--allow-theme-identity-change] [--help]"
    echo ""
    echo "Deploy wordpress-theme/skyyrose-flagship-2 to the ${target} site described by"
    echo "  ${env_file}"
    echo "then hand off to scripts/deploy-theme.sh (the engine) with the same options."
    echo ""
    echo "One-shot overrides (consumed here, handed to the engine as env vars):"
    echo "  --allow-new-theme-folder       first deploy into a folder the site lacks"
    echo "                                 (live style.css 404)"
    echo "  --allow-theme-identity-change  replace a live theme whose Theme Name /"
    echo "                                 Text Domain differ from the source"
    echo ""
    echo "Refuses when the env file is missing, its PUBLIC_URL/WORDPRESS_URL host is not"
    echo "the ${target} host or carries userinfo, its SSH_USER is not that host's own"
    echo "'<first label>.wordpress.com' account, SFTP_USER differs from SSH_USER, or its"
    echo "WP_THEME_PATH does not end in skyyrose-flagship-2."
    echo "ENV_FILE / THEME_DIR_OVERRIDE / DEPLOY_TARGET / PUBLIC_URL / WORDPRESS_URL /"
    echo "ALLOW_NEW_THEME_FOLDER / ALLOW_THEME_IDENTITY_CHANGE / PREFLIGHT_SKIP_COMPLETENESS"
    echo "must NOT be set by the caller."
}

deploy_target_main() {
    local target="$1" env_file="$2" theme_dir="$3"
    shift 3
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        dt_usage "$target" "$env_file"
        exit 0
    fi
    dt_refuse_inherited
    dt_parse_flags "$@"
    dt_validate_env_file "$target" "$env_file"
    if [[ ! -d "$theme_dir" ]]; then
        dt_log_error "Theme source directory missing: ${theme_dir}"
        exit 1
    fi
    dt_log_info "Target ${target}: host ${DT_HOST} | theme folder ${DT_FOLDER} | source ${theme_dir}"
    export DEPLOY_TARGET="$target" ENV_FILE="$env_file" THEME_DIR_OVERRIDE="$theme_dir"
    dt_export_overrides
    exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/deploy-theme.sh" \
        ${DT_ENGINE_ARGS[@]+"${DT_ENGINE_ARGS[@]}"}
}
