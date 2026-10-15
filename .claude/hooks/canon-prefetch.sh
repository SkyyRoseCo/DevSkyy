#!/usr/bin/env bash
# UserPromptSubmit hook — structural enforcement of DevSkyy AP-16
# ("Glob Fishing Instead of Consulting Canonical Source").
#
# Per cerebrum.md: before any task, name the canonical source. Examples:
#   Catalog → wordpress-theme/skyyrose-flagship/data/logo-registry.json (via skyyrose.core.product.get_product)
#   Brand   → knowledge-base/seed/from-interview.md
#   ADRs    → knowledge-base/decisions/
#
# Detects when the user prompt mentions a domain that has a single
# canonical source-of-truth file and injects a directive telling Claude
# to READ THAT FILE before answering — with a 24h per-topic cache so the
# same topic doesn't re-nudge on every prompt in a working session.

set -euo pipefail

# shellcheck source=lib/common.sh
source "$(dirname "$0")/lib/common.sh"

if [[ "${CANON_PREFETCH_DISABLE:-0}" == "1" ]]; then
    exit 0
fi

payload=$(cat)
prompt=$(read_field "$payload" '.prompt')
[[ -z "$prompt" ]] && exit 0

cache_dir=$(ensure_cache_topic "canon-cache")
ttl=$((24 * 3600))

# Detect mentions of domains that have a canonical source-of-truth.
# Format: <canonical-topic-name>|<case-insensitive-regex>
matches=$(scan_patterns "$prompt" <<'PATTERNS'
catalog|product[._ -]?catalog|skyyrose-catalog|all skus|product list|sku [a-z]{2,3}-[0-9]{3}|catalog\.csv|logo-registry|get_product|product registry
brand|skyyrose brand|brand canon|brand voice|brand identity|brand guidelines|brand-canon
collection|black[._ -]?rose|love[._ -]?hurts|signature collection|kids capsule
imagery-pipeline|elite[._ -]?studio|nano[._ -]?banana|render pipeline|imagery pipeline
adr|architecture decision|adr-[0-9]|architectural decision
managed-agents|claude[._ -]?agent[._ -]?sdk|multi[._ -]?agent orchestrator
preorder|pre[._ -]?order|preorder gateway
theme|wordpress theme|skyyrose-flagship|skyyrose flagship|flagship[ -]?2
PATTERNS
)

[[ -z "$matches" ]] && exit 0

# For each match, check 24h cache. Build directive only for stale topics.
stale=()
while IFS= read -r topic; do
    [[ -z "$topic" ]] && continue
    if ! is_fresh "$cache_dir/$topic" "$ttl"; then
        stale+=("$topic")
    fi
done <<< "$matches"

(( ${#stale[@]} == 0 )) && exit 0

# Map each stale topic to its canonical source file(s).
build_directive() {
    local out="[canon-prefetch] DevSkyy AP-16 (Glob Fishing): user prompt mentions: "
    out+="$(IFS=,; echo "${stale[*]}").\n\n"
    out+="Before answering, READ the canonical source(s) for each:\n"
    local t
    for t in "${stale[@]}"; do
        case "$t" in
            catalog)
                out+="  - catalog → wordpress-theme/skyyrose-flagship/data/logo-registry.json (root symlink logo-registry.json) — the ONE product SOT (33 SKUs). Corey (founder) is authoritative on his products.\n"
                out+="    Read ONE entry point: from skyyrose.core.product import get_product  /  python -m skyyrose.core.product <sku>\n"
                out+="    skyyrose-catalog.csv, dossiers, sot-images.json, collection sot.json are GENERATED projections — never the source; after a registry edit run python scripts/sync_product_registry.py (--check before handoff)\n"
                ;;
            brand)
                out+="  - brand → knowledge-base/seed/from-interview.md (PRIMARY brand canon, Corey-authored; wins over derived docs)\n"
                ;;
            collection)
                out+="  - collection → knowledge-base/seed/from-interview.md (collection narratives) + logo-registry.json collections.<slug> (identity SOT); templates: V1 skyyrose-flagship/template-collection-*.php, V2 skyyrose-flagship-2/template-collection.php\n"
                ;;
            imagery-pipeline)
                out+="  - imagery pipeline → docs/NANO_BANANA.md and skyyrose/elite_studio/ (canonical hub); NEVER call FASHN/Tripo/Meshy outside their agent wrappers\n"
                ;;
            adr)
                out+="  - ADR / architectural decision → knowledge-base/decisions/ (numbered ADRs); docs/SKYYROSE_V2_MASTER_PLAN.md §1 has locked decisions\n"
                ;;
            managed-agents)
                out+="  - managed agents → docs/MANAGED_AGENTS.md (two-stack architecture, recipes, smoke tests, pitfalls)\n"
                ;;
            preorder)
                out+="  - preorder → wordpress-theme/skyyrose-flagship/inc/woocommerce-preorder.php + template-preorder-gateway.php\n"
                ;;
            theme)
                out+="  - theme → TWO themes, name which before editing: V1 wordpress-theme/skyyrose-flagship/ (\"SkyyRose\", text domain skyyrose, SKYYROSE_VERSION) and V2 wordpress-theme/skyyrose-flagship-2/ (\"SkyyRose Flagship 2\", text domain skyyrose-flagship-2, SKYYROSE2_VERSION). Read that theme's CLAUDE.md + functions.php. skyyrose.co + staging serve the Flagship 2 lineage; deploys go through scripts/deploy-staging.sh / deploy-production.sh (STOP-AND-SHOW)\n"
                ;;
        esac
    done
    out+="\nThis directive fires once per 24h per topic. After you Read the canonical file(s), touch the cache marker to suppress:\n"
    out+="  touch '$cache_dir/<topic>'  (or just answer — silence is fine if you already read it)\n\n"
    out+="Per cerebrum.md AP-16: if you cannot name the canonical source for a task, STOP and ask — don't grep."
    printf '%s' "$out"
}

emit_user_prompt_context "$(build_directive)"
exit 0
