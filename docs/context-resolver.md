# Context Resolver — hardened production contract v1

The resolver resolves declared intent, owner rules and field-owned product
truth. It emits a compact execution context by default and retains full audit
evidence separately. It never changes product sources or authorizes publishing,
deployment or spend.

```sh
.venv/bin/python -m skyyrose.core.context_resolver docs/examples/context-resolver-abstract.json
.venv/bin/python -m skyyrose.core.context_resolver docs/examples/context-resolver-abstract.json --audit
```

Exit codes: 0 for nonblocked context, 1 for BLOCKED, 2 for invalid schema or
source-integrity error. The Python `resolve_context()` result remains the full
audit-capable model; use `execution_context(result)` for downstream execution.
Existing raw snapshots are audit evidence, not permission to use stale copy.

## Content intent and input consistency

`content_intent` separates medium, production_type, content_role, shot_role,
distribution_channels, intended_use, audience, representation_mode and
lifecycle_stage. The executable
[example](examples/context-resolver-abstract.json) is an image/editorial still
with no distribution selected yet, not a film channel.

The eight taxonomy families cover commerce, web/digital experience,
campaign/editorial, film, social, advertising, CRM and physical/OOH. Extend
terms through explicit `register_taxonomy_term()`; unknown terms fail instead of
being guessed. Taxonomy content and implementation are bound into resolution
identity. Platform dimensions and changing channel rules belong to
execution-time adapters, never the Constitution.

Top-level lifecycle/use/audience/product mode remain compatibility fields and
must match the intent. `channel` is deprecated: if supplied it must match the
sole explicit distribution channel; it cannot substitute for medium. Populated
collection/brief fields cannot have absence reasons. Null values require
reasons. Shots bind SKUs and corresponding views; undeclared SKUs, BACK with
front-only requirements and unsupported SIDE references block. Exact-product
detail shots require explicit detail requirements.

## Product authority

The complete reader remains `get_product(sku)`. Execution projects owned
identity, structured garment facts, placement-specific technique, registry
preorder state, requested references with hashes, protected characteristics,
scoped founder corrections and negative constraints. Editorial
descriptions—including catalog description text—are not product authority and
are excluded by default.

For br-001, the front placement is embossed and the registry preorder flag is
false. Conflicting enriched copy remains audit-only. Valid back embroidery in
the dossier is preserved in audit; the system does not globally replace or ban
the word embroidered. Desired registry commerce state is not fresh live
WooCommerce purchasability.

Authority states are AUTHORITATIVE_CURRENT, DERIVED_CURRENT, STALE, SUPERSEDED,
CONFLICTED and UNKNOWN. Field metadata retains source ownership; catalog state
is never relabeled a founder specification. Required detail aliases resolve
against safe owned facts. Unsupported/unresolved requested details block rather
than falling back to marketing prose.

Conflicting dimension statements remain named CONFLICTED evidence. A
source-composite can preserve the reference's exact visible scale without
inventing a measurement axis. Explicit dimensional requirements or
reconstructive production requiring those dimensions block. No authoritative
fact is modified to make a downstream job pass.

## Lifecycle

| Stage | Context / job state                                                                               |
| ----- | ------------------------------------------------------------------------------------------------- |
| M1    | RESEARCH_READY if required research context resolves                                              |
| M2    | PLANNING_READY: exploratory context and declared fidelity path; not final work or approval        |
| M3    | PROTOTYPE_READY within declared evidence constraints                                              |
| M4    | CANDIDATE_READY                                                                                   |
| M5    | Resolver caps at CANDIDATE_READY; complete job planning can become PRODUCTION_READY               |
| M6–M7 | Complete job plan can be PRODUCTION_READY; complete artifact evidence can yield RELEASE_CANDIDATE |
| M8    | LEARNING_READY context; no automatic constitutional promotion                                     |
| M9    | ARCHIVE_READY context; not proof that an archive operation occurred                               |

Any required gap yields BLOCKED. Campaign/film/advertising production or
customer-facing production at M5–M7 requires campaign authority context. A null
brief is allowed at internal M2 when explicitly recorded. Missing
film/story/sound/continuity or interactive/fallback/commerce fields are early
planning gaps and late-stage blockers. Release-candidate evidence cannot advance
an M2 job. None of these states authorizes an action.

`resolution_status` preserves the former READY / READY_WITH_NONBLOCKING_GAPS /
BLOCKED source-availability summary. Use the primary lifecycle `status` for
workflow decisions. `release_ready` and `action_authorized` remain false on
resolver results.

## Compact execution and complete audit

Execution includes objective, content intent, lifecycle, safe product
projection, requested reference hashes, scoped palette policy, stable rule IDs
and inclusion reasons, verification requirements, explicit absences, gaps and
audit linkage. The job-level bundle adds production method, novelty, saturation,
derivatives and Bay Area discovery territory. It does not prescribe a landmark.

Audit retains raw assembled products, relevant raw registry/dossier records,
marketing evidence, conflicting values, all considered rules,
inclusion/exclusion reasons, source hashes, complete decisions and context. To
compare representations, run the resolver on the tracked example with and
without `--audit`:
`.venv/bin/python -m skyyrose.core.context_resolver docs/examples/context-resolver-abstract.json --audit`.

Every call hashes current inputs, reader references, selected policies, taxonomy
and implementations. Product inputs are checked before and after reading;
tracked files are rechecked before return. There is no stale-success cache.

## Limits and verification

The product conflict adapter uses owned structured fields and conservative claim
detection; it is not a general semantic adjudicator for every historical
sentence. Unvalidated editorial copy is excluded even if no known conflict
pattern matches. Required missing facts block. Human-authored source corrections
remain authoritative without third-party reconfirmation.

Free-text intent is retained, not executed as policy. No pixel inspection,
reviewer authentication, live-commerce fetch or publishing system is
implemented. Source files are trusted repository inputs. Changing a file hash
proves a version change, not owner identity.

See [job workflow](creative-job-workflow.md), `tests/test_context_hardening.py`,
`tests/test_content_intent.py`, and the existing resolver/product suites.
