# Elite Studio product briefs and visual QA

Product data comes from the single editable registry at
`wordpress-theme/skyyrose-flagship/data/logo-registry.json` (root
`logo-registry.json` is its symlink). Read complete records through
`skyyrose.core.product.get_product`; CSVs, dossiers and manifests are
projections or consumers. Corey is the founder and maker: preserve his exact
specifications and latest corrections. QA checks our output against those facts.

## Build a brief without generating media

```python
from skyyrose.elite_studio.prompts.enhancer import PromptEnhancer

brief = PromptEnhancer().enhance(
    "Photograph the garment in a naturally lit studio.",
    sku="br-001",
    required_views=("front",),
)
print(brief.brief_status, brief.gaps)
```

This deterministic operation reads current product authority. `gaps` lists all
known omissions; `blocking_gaps` identifies requirements of the chosen
operation, and `optional_gaps` preserves other visible omissions. `brief_status`
is `incomplete` only when that operation has blockers; an unknown SKU raises.
Never invent a value to fill a gap.

The explicit `operation` defaults to `"render"` independently of detected
creative intent. Supported contracts:

| Operation  | Required data                                                      | Views                                                                                  |
| ---------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| `render`   | Nonblank garment color, fit, materials and features specifications | At least one explicit `front`/`back`; every requested render-source binding must exist |
| `seo`      | Existing editorial `content.seo_meta`                              | None                                                                                   |
| `alt-text` | At least one nonblank existing alt-text value                      | None                                                                                   |

SEO and alt-text contracts assess deliverable completeness, not whether an agent
can begin drafting. Alt-text readiness does not certify coverage for every
image. An absent unrequested back binding, SEO copy, or editorial enrichment
remains visible but does not block a front render. Unsupported operations/views
raise. No view substitutes for another, and storefront image fallbacks cannot
satisfy a render-source requirement. Nulls and founder wording remain unchanged.

Central consumers can call
`product_readiness(get_product(sku), "render", required_views=("front",))` from
`skyyrose.core.product`. Its result includes explicit required fields,
readiness, blocking/optional gaps and categories. `get_product` retains the
legacy flat `gaps` list and adds `gap_categories`, with additive garment and
render-source gaps. This checks data and bindings only: asset
existence/readability, visual fidelity, and generation authority still require
their existing separate gates. Enhancement scores measure prompt structure, not
product correctness or authorization. Product briefs bypass the semantic cache.
Optional creative context is subordinate to product constraints.

To propose a genuinely new design, explicitly select both `new_design=True` and
`intent="design-ideation"`. Category defaults are proposals only. Supplying an
existing SKU still selects product grounding.

Before drafting or reviewing generation prompts, read
[the imagery prompting standard](/Users/theceo/.codex/creative-standards/imagery-prompting.md).
Generated briefs cite it; provider controls with no selected provider are not
applicable. A brief does not authorize generation, spending or publishing.

## Visual QA contract

`await QualityAgent().verify(candidate_path, expected_spec, sku=sku, view="front")`
is a provider operation, not an offline check. Run it only within authorized
provider scope. Use `mode="scene_composite"` for scene integration checks.

Preflight requires one SKU, an explicit front/back view, the corresponding
registry-bound reference binary, and a readable candidate. An optional
`reference_path` must match that binding. Both judges receive the labeled image
pair; the result records hashes and provenance. Legacy calls lacking this
evidence return a failed verification before judge dispatch.

Each judge must provide nonblank evidence for silhouette, construction, artwork,
lettering, color and placement. Hidden or illegible details cannot count as a
match. Integration has separate lighting, edge, shadow, scale, perspective and
occlusion findings. Local validation computes scores and requires both judges to
pass; provider totals cannot override identity mismatches. Malformed, truncated,
refused or failed judge responses do not approve the asset.

Downstream callers require all three fields: `success`,
`overall_status == "pass"` and `recommendation == "approve"`. Classifier
confidence alone cannot approve. Failed candidates are retained for inspection
but do not advance to compositing.

## Provider settings and verification

OpenAI Chat Completions adapters share
[`OpenAIChatSettings`](../core/openai_settings.py). Unsupported model
capabilities and settings raise before I/O. This allowlist does not claim that
unregistered models do not exist. Model changes require updating the capability
contract and transport tests. Current QA budgets are 1,600 output tokens for
flat-lay and 2,400 for scenes, with one transport attempt per judge. The
orchestration OpenAI SDK owns its retries; web-builder fallback owns retry
decisions outside its SDK call.

Run the bounded offline suite from the repository root:

```sh
bash tasks/prompt-model-audit/verify.sh
```

See the
[implementation report](../../tasks/prompt-model-audit/IMPLEMENTATION.md) and
[product-truth scope](../../tasks/prompt-model-audit/PRODUCT-TRUTH-SCOPE.md).
The suite uses fixtures and mocked transports; it does not establish live visual
judge accuracy, account access, cost, latency, deployment or release acceptance.

## Registry consumer contracts

`get_product` includes the verbatim dossier `full_text` and legacy `catalog_row`
projection. Complete-product consumers preserve corrections and provenance.
`render_reference(record, "front" | "back")` resolves an explicit bound asset,
checks repository containment/readable nonempty bytes, and records its digest.
It never guesses filenames or substitutes another view. Legacy vision preflight,
vision analysis and 3D input validation run this check before provider dispatch.

Canonical OAI dossiers and corrections preserve founder text even when it
contains composition-related phrases. External fixture dossiers retain their
explicit sanitizer behavior. SkyyRoseCatalogSource preserves its existing
row/dossier contract and exposes the complete record as `ProductRecord.product`;
golden references remain separate evaluation fixtures.

See
[all four follow-ups](../../tasks/prompt-model-audit/FOLLOWUPS-IMPLEMENTATION.md)
for migration boundaries and offline evidence. Generation remains on hold.
