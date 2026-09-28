# Brand archaeology, reconciliation and reusable context architecture

**SkyyRose / DevSkyy · investigation date 2026-09-23 · review proposal**

## 1. Finding and scope

The defensible model is a small founder-grounded identity layer, a reusable
expression grammar, distinct collection/channel/campaign contexts, and a
separate immutable product-truth interface. The present website is valuable
evidence of expression; it is not a complete definition of SkyyRose.

Following Corey’s current direction (E44), **staging is the primary visual
reference**. Fresh guest inspection covers all four collection worlds and their
story sections; [STAGING-VISUALS.md](STAGING-VISUALS.md) records the visual
analysis and captures. Production is retained as a comparison and drift source.
This strengthens staging’s authority for current expression, without converting
every scene device into permanent identity.

The best-supported identity candidates are Oakland specificity, Corey Foster’s
authorship and family origin, autobiography expressed through collections, and
gender-neutral presentation. Exact black backgrounds, metallic monuments, throne
rooms, particular bridges, font families and animation timings do not pass the
removal test as universal identity. Some are governed current implementation
choices; others are collection devices, historical proposals or disputed
prescriptions.

This is a broad, bounded investigation of available evidence, not a claim that
every file, asset, remote folder and historical approval was exhaustively
reviewed. It includes root authority instructions; founder interview and
decisions; brand YAML; collection identity and typography sources; V1/V2 and
dashboard code; generators/readers/tests; campaign/storyboard and 3D source;
path-scoped Git history; Google Drive source discovery and selected document
retrieval; authenticated WordPress site inventory; production and staging
browser samples. Forty-four meaningful evidence records are indexed in
`evidence.json` as E01–E44.

Baseline: `/Users/theceo/DevSkyy`, branch `feat/single-product-entry-point`,
HEAD `a5c40d311a9d02f43a86ada5db8025d0a80479ab`. The baseline had 465
modified/deleted tracked paths, no staged changes, and numerous untracked paths.
Relevant source files were already dirty. Current working-tree observations
therefore cannot be presented as committed remote or deployed identity. Existing
work was preserved. The separate artifact directory is the only authored change.

## 2. Source authority is field-specific

| Scope                                                    | Current owner / interface                                                                                  | Classification                                  | Boundary                                                                                                        |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Latest founder product corrections                       | Corey’s current instructions, recorded with `FOUNDER_CONFIRMED`                                            | AUTHORITATIVE                                   | Accept maker knowledge; verify execution, not the maker’s expertise.                                            |
| Product commercial/design/source fields                  | Root `logo-registry.json` symlink → original-theme `data/logo-registry.json::products`; `get_product(sku)` | CANONICAL                                       | CSV/dossiers are generated projections. No copied campaign product maps.                                        |
| Founder narrative and positioning                        | `knowledge-base/seed/from-interview.md`, applicable explicit later founder resolutions                     | AUTHORITATIVE                                   | Captured source includes superseded sections and redaction history; precedence is by subject, not blanket date. |
| Structured name/legal name/founder/origin/active tagline | `assets/brand/brand.yaml` via `BrandConfig.load()`                                                         | CANONICAL for these fields                      | YAML header overclaims global ownership. SOT excludes its font/collection mirrors from authority.               |
| Font roles                                               | Original-theme `data/brand/typography.json`                                                                | CANONICAL current design system                 | Exact families are current rules, not necessarily eternal identity.                                             |
| Collection identities                                    | Original-theme `data/collections/<slug>/identity.json`                                                     | CANONICAL within scope                          | Preserve nested pending/interim statuses; top-level verified does not approve every asset.                      |
| Logo/artwork/placements                                  | Registry and `LogoRegistry`; asset hierarchy as scoped guidance                                            | CANONICAL / AUTHORITATIVE                       | Brand chrome, collection marks and garment-exclusive graphics have different permissions.                       |
| Non-product images                                       | `visual-manifest.json` per SOT; candidate manifests/receipts for use status                                | CANONICAL identity references, scoped approvals | Identity, file existence, reviewed pixels and approved usage are separate.                                      |
| V1→component package assets                              | Original theme → `sync-theme-assets.mjs` → package                                                         | DERIVED                                         | A copied “canonical” token comment does not reverse the dependency.                                             |
| V2 CSS and runtime                                       | `--sr2-*`, templates/controllers, sampled deployed page                                                    | IMPLEMENTATION                                  | Strong evidence of actual expression; not authority to redefine product or founder truth.                       |
| Historical prompts, PDFs, old web directions             | Git history, Drive architect PDF, superseded storyboards                                                   | LEGACY / REFERENCE                              | Their imperative wording is historical data, not instructions to execute now.                                   |
| Motion proposal / local films                            | Explicit unapproved/candidate/release-blocked contracts                                                    | EXPERIMENTAL                                    | Do not promote by attractive appearance or existing files.                                                      |
| Untraced approvals, audience metrics, rights             | No sufficient record recovered                                                                             | UNKNOWN                                         | Remain unknown; never silently canonical.                                                                       |

Evidence: E01–E12, E17–E23, E28–E32, E37–E39. Authority classes are not one
global priority ladder: runtime is authoritative for what rendered, while the
registry is authoritative for what the garment is. A live mismatch is a drift
finding, not a new source of product truth.

## 3. History and actual usage

Verified history shows meaningful evolution: `c8aae48e2` (May 3) introduced the
founder KB; `e70c41262` (May 24) added canon audit/stories/questions;
`143d86459` and `02e8eca4b` (May 25) locked and reconciled the reference set;
`c2090be9b` (June 18) carried immersive hero prompts; `aa71f6c5e` and
`f43ca0f64` (June 22) changed typography and one-way asset sync; `616d3e678` /
`0a4bbc258` (July 14) synchronized the font canon; `f2f01bbcf` (August 25) added
V2 storefront/environment presets. Newness documents sequence, not automatic
approval. September retirement changes are present in this dirty working tree.
The retirement task explicitly warns that edited historical snapshots are no
longer original evidence.

Actual source dependencies were traced: V1 includes generated brand PHP; the
component package copies original-theme assets; V2 enqueues its tokens, theme
and motion controllers. In the bounded pair `theme.css + immersive.css`, 41 of
45 V2 token declarations are referenced via `var()`. Four absent from those two
consumers are not proven dead across the repository. The same sample contains 91
`--sr2-void`, 24 `--sr2-paper`, 67 display-font and 26 caps-font references.
This establishes implementation emphasis, not visual area, customer exposure or
brand necessity.

Fresh browser samples at production and staging confirm different page
compositions. Both sampled bodies compute to dark backgrounds with Hanken
Grotesk body text. Production H1 computes to Hanken Grotesk; staging H1 to
Archivo. Staging includes collection chapters, films/product links, and an
explicit Kids throne story. Guest Kids desktop and mobile samples show the
throne/mascot artwork. Mobile emulation at 390×844 reports document width 390
and visible motion/character pause controls. Desktop and mobile readbacks also
differ in headings and their computed families; timing, responsive rendering and
cache/deployment identity were not isolated, so this is an observation, not a
diagnosed CSS defect.

The public web reader could load production but not staging; the browser loaded
staging successfully. Availability failure in one tool is not proof a site is
offline. Homepage browser contexts carried an admin bar; guest Kids did not. No
cart, form, purchase, account mutation or CMS write was performed.
[Production](https://skyyrose.co/) and
[staging](https://staging-7e48-skyyrose.wpcomstaging.com/) are observed
expressions, not declarations of universal brand law. See E33–E36 and the
captured evidence files.

## 4. Brand conflict register

| ID / subject                         | Source A                                                                            | Source B                                                                                                       | Runtime / history                                                                                                         | Likely authority and resolution                                                                                                                                                                        | Confidence / owner need                                                              |
| ------------------------------------ | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| C01 Whole-file canon                 | YAML says it is the brand SOT; April Drive PDF says the theme supersedes everything | SOT partitions ownership by field                                                                              | Real generator consumes only a structured subset; YAML names a nonexistent generator                                      | Use field ownership, existing actual generator; neither historical PDF nor YAML header controls all domains                                                                                            | High; no new owner decision                                                          |
| C02 Tagline and deployed copy        | Current YAML active tagline is empty; retirement task forbids replacement           | Injector contains a different positive slogan; production greeting and WP site description retain retired copy | Observed live, saved text redacted; no production fix authorized here                                                     | Current owner retirement wins. Remove stale injection/metadata in separately authorized remediation; do not invent a new slogan                                                                        | High; no reconfirmation of retirement needed                                         |
| C03 Signature place                  | YAML/eval use SF/Golden Gate framing                                                | Recorded founder answer identifies Bay Bridge/Oakland connection                                               | Staging also uses Golden Gate scene/copy; current scene may be an expression, not an origin claim                         | Preserve founder origin. A Golden Gate environment does not rewrite a Bay Bridge garment or geography fact. Trace exact scene approval before broader use                                              | High on origin; medium on scene permission. No repeat origin question                |
| C04 Blue and palette scope           | Interview bans blue; voice rubric rigidly locks palette                             | Semantic info blue, registry-permitted recolors, Drive colored master filenames                                | Source contradiction; Signature staging visibly contains blue-gray sky (E43); Drive names are metadata, not use approvals | Preserve exact product colors. Do not infer permission for blue campaign worlds from UI status colors or archived masters                                                                              | High conflict; owner scope decision only for new nonproduct exception                |
| C05 Cathedral and lineage            | Founder reference set excludes European museum/vault/cathedral lineage              | LH Beast/cathedral and BR cathedral scene definitions                                                          | Later V2 scenic source exists; blanket prohibition and scene lineage have different scopes                                | Do not globalize cathedral into DNA or silently declare old prohibition revoked. Existing scene records need candidate-bound approval tracing                                                          | Medium; owner only if unresolved usage is needed                                     |
| C06 Kids grammar                     | Bright/playroom YAML; June prompt forbids throne/cartoon/front-facing child         | Heir identity, later V2 full-color throne/mascot; reveal contract still requests review                        | Guest staging visibly uses throne on desktop/mobile                                                                       | Heir/family context has support; the mandatory future world treatment is not resolved merely by deployment                                                                                             | High conflict; owner chooses future scope if a binding Kids direction is needed      |
| C07 Typography                       | Current typography.json and V2 roles                                                | Older PDF, injector, old story guidance; separate dashboard font stack                                         | Production H1 and guest Kids headings differ from staging home roles                                                      | Current font owner controls storefront implementation; dashboard scope stays separate. Artwork scripts are not generic UI fonts                                                                        | High; no eternal-font invariant; runtime cause unverified                            |
| C08 Motion numbers                   | Eval prescribes 150/250/400/800ms                                                   | V2 uses 180/420/900ms; another contract is unapproved                                                          | Active enqueues and pause/fallback source exist                                                                           | Keep exact values in scoped implementation. Proposed motion grammar must not promote unapproved specification                                                                                          | High; no owner need for classification                                               |
| C09 Existing brand injector          | Function offers reusable brand context                                              | Stale enum, missing Kids, wrong accent/font/tagline, CSV cache key, exception fallback                         | 27 passing reader/catalog tests do not establish literal brand correctness                                                | Treat as a consumer needing remediation, not the new canonical assembler                                                                                                                               | High source evidence; cache stale behavior is inferred risk, not reproduced mutation |
| C10 Verified versus approved         | Collection identity top-level `verified`                                            | Nested hero `interim-pending-mj`                                                                               | Newer deployed assets do not update old nested record automatically                                                       | Resolve and carry status per field/asset/use; fail if required approval unavailable                                                                                                                    | High; no automatic approval                                                          |
| C11 Campaign versus partnership      | Historical transit-specific film                                                    | Explicit superseding fictional house train storyboard                                                          | Local previsualization/release-blocked status; runtime use is separate evidence                                           | Current fictional direction wins; do not claim transit affiliation, cleared release or finished provider film                                                                                          | High; no resurrection of superseded direction                                        |
| C12 Registry versus dossier/commerce | One editable product registry, generated dossiers                                   | Dossier-first instruction; older docs call WooCommerce product authority                                       | Current reader/projections pass                                                                                           | Embedded dossier-first within registry is the coherent proposal. Registry owns desired facts; Woo owns current session/variation purchasability. Mismatch is drift, not permission to overwrite source | High implementation; clarify wording in future documentation change, no edits now    |
| C13 Similarity equals brand          | Visual centroid gate numerically scores proximity                                   | ADR says global gate lacks settled false-pass measurement                                                      | No fresh 100-example discrimination experiment run                                                                        | Similarity is a quality feature, never brand authority, novelty limit, or product verification                                                                                                         | High; no owner need                                                                  |
| C14 Sustainability/market claims     | 2025 Drive overview uses broad sustainability and old prices                        | Current product registry governs factual fields; no general claim substantiation recovered                     | Historical text has different prices/names                                                                                | Do not import those prices or environmental claims; retain family/origin corroboration as historical evidence only                                                                                     | High; missing support is not evidence the claim is false                             |

No conflict was silently repaired during discovery. Resolved founder decisions
remain resolved. Open decisions concern scope or new creative direction, not
proving product facts again.

## 5. Invariant candidate review

This is the owner-review matrix. Strong existing source instructions remain
binding in their present scope; promoting a principle to permanent cross-channel
invariant is a separate classification decision.

| Candidate                                               | Evidence                                        | Removal test                                                                                                  | Creative range test                                                                     | Proposed level / confidence                                |
| ------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Oakland-specific authored identity                      | E03, E06, E08; family/Oakland corroboration E38 | Removing it severs repeatedly explicit origin and author relationship                                         | Documentary portrait and abstract studio campaign can both preserve truthful authorship | L1 candidate / high                                        |
| Collections as autobiography                            | E03, E06–E07                                    | Replacing memoir chapters with arbitrary aesthetic labels contradicts explicit positioning                    | Still-life, film and spatial story can express the same chapter                         | L1 candidate / high                                        |
| Gender-neutral presentation                             | E03; historical corroboration E38               | Replacing it with gendered audience framing contradicts explicit founder positioning                          | Casting, styling and composition remain varied; factual garment records stay exact      | L1 candidate / high                                        |
| Family/legacy relationship                              | E03, E11, E33–E38                               | Erasing founder/daughter connection changes named origin; requiring every image to show family is unsupported | Product detail film and intergenerational story both possible                           | L1 candidate / medium-high                                 |
| Specificity instead of generic luxury filler            | E03, E13                                        | Removing it weakens distinct voice but is less uniquely defining alone                                        | Spare copy and dense editorial can both be concrete                                     | L2 grammar / high                                          |
| Story, atmosphere, product as deliberate narrative beat | E03, E24–E26, E34                               | Brand could exist without interactive website; losing narrative would weaken expression                       | Still editorial, live film and optional 3D all qualify                                  | L2 grammar / high                                          |
| Legibility, usable routes, preference-aware enhancement | E21, E24–E26, E30                               | Necessary quality standard, not unique cultural identity                                                      | Multiple media and capabilities supported                                               | L2 experience standard / high as source-supported proposal |
| Exact current typography stack                          | E10, E21–E23, E37                               | Font evolution already occurred without erasing the brand                                                     | Hierarchy survives alternate authorized typography eras                                 | L4 current system / high                                   |
| Black/dark everywhere                                   | E04, E11–E12, E21, E33–E36                      | Not established as essential independent of present expression                                                | Universal mandate would preclude otherwise recognizable campaigns                       | L3 palette context / L4 surface, not L1                    |
| Monuments/chrome/throne/rose dome                       | E09, E24, E27, E34–E36                          | Removing one device leaves narrative, marks and products recognizable                                         | Alternatives can retain symbolism without repeating the room                            | L3 concept / L4 realization / high                         |
| Five named external references                          | E08                                             | Source of active design guidance, not the brand’s own immutable identity                                      | Different moves from permitted references create range                                  | L3 reference policy / high                                 |
| No active tagline                                       | E04–E05                                         | Future owner-approved policy could change without identity replacement                                        | Current absence is explicit; no invented alternatives                                   | Current policy constraint, not timeless philosophy         |

The product-fidelity boundary is mandatory truth preservation, not a creative
adjective. It does not need to win an aesthetic removal test.

## 6. Visual, voice and experience DNA

| Domain                      | Supported behavior                                                                                               | Evidence classification              | Portable level and limit                                                                       |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------- |
| Palette                     | Rose gold, gold, silver and crimson distinguish brand/collection roles; V2 adjusts UI crimson for contrast       | EXPLICIT / CONFLICTED scopes         | Collection palette L3, exact UI values L4; do not recolor garments to match UI                 |
| Typography                  | Separate display, body, utility and accent roles; distinct collection artwork                                    | EXPLICIT; runtime partial divergence | Role separation L2; families and CSS values L4                                                 |
| Hierarchy/spacing/density   | Editorial emphasis, large headings, constrained reading width; drop density is an active reference move          | EXPLICIT and source-observed         | L2 hierarchy, L3 density by drop/channel, L4 scales; not one permanent page grid               |
| Composition/negative space  | Founder reference set favors photographic narrative, logo recognition and place; V2 adds monumental environments | EXPLICIT / CONFLICTED expression     | Art direction is supported; one central pedestal or full-screen scene is not required          |
| Photography/product framing | Real people/places and garment detail in reference guidance; current pages mix on-body assets and scene images   | EXPLICIT / STRONGLY_OBSERVED         | Product accuracy locked; photo method/context varies within approved use                       |
| Lighting/material/texture   | Collection-specific gold/silver/crimson, dark environmental scenes, brand/artwork material identities            | EXPLICIT / STRONGLY_OBSERVED         | Specific light rigs, marble, chrome and atmospheric fog are devices, not universal obligations |
| Shapes/layout               | V2 rectangular controls, tokenized panels and immersive sections; editorial and commerce coexist                 | STRONGLY_OBSERVED implementation     | L4; do not export component anatomy as universal identity                                      |
| Motion/tempo/transitions    | Reveals should carry story; controls and capability/preference fallbacks exist in source                         | EXPLICIT / observed controls         | L2 proposed grammar; exact durations, easing, parallax and chapters L4                         |
| 3D/camera/depth             | Scene hotspots connect to products; posters keep routes available when 3D cannot run                             | EXPLICIT source, limited runtime     | L2 environmental discovery; L3 scene worlds; L4 renderer/camera. Not every campaign needs 3D   |
| Responsive adaptation       | Same context can be composed differently; sampled mobile keeps controls and fitting width                        | STRONGLY_OBSERVED sample             | L2 usability principle; no full responsive or accessibility certification                      |
| Sonic identity              | No durable sonic system established; sampled film contract is silent/local                                       | UNKNOWN                              | Do not invent canonical music, sonic logo or voice casting                                     |

“Cinematic” is supported behaviorally by scene composition, narrative
progression, controlled reveal, place as story and connected product discovery
(E03, E08, E24–E26). It does not necessarily mean constant camera motion, dark
grading, artificial grain or a film effect on every element. “Luxury” is
supported through concrete garment detail, deliberate presentation and the
streetwear/heritage positioning; it does not authorize claims about unrecorded
materials, manufacture, scarcity or sustainability. “Immersive” describes an
experience option with navigable worlds and fallbacks, not a WebGL requirement.
“Playful” appears in some Kids sources but conflicts with others; it is not
established as master voice. “Disruptive” and “experimental” are not
sufficiently substantiated as universal promises.

Voice distinctions:

- **Core:** source-specific, direct, Oakland-grounded, personal rather than
  generic aspiration. Avoid the filler and price-apology patterns in E13; keep
  founder wording exact where quoted.
- **Collection:** Black Rose is declarative/resolved; Love Hurts carries family,
  emotional weight and Beast perspective; Signature conveys beginning/origin;
  Kids centers the heir/next generation. Some sentences called founder quotes
  originate in templates, so their evidence status must remain
  implementation-derived.
- **Campaign/editorial:** metaphor, scene titles and chapter rhythm may vary.
  Current “house/world/chapter” language is observed expression, not a required
  sentence template.
- **Product:** names, materials, fit, construction, logos, price and
  availability need source resolution. Product copy may improve articulation
  without adding facts. Gender-neutral presentation never silently renames a
  canonical product field.
- **UX:** action-led labels and clear selection/pause/route controls; uppercase
  treatment is visual implementation. Emotional copy must not obscure price,
  variants or purchase state.

Audience evidence supports inclusive/gender-neutral positioning, Oakland
cultural grounding and a Kids context involving children and their purchasers.
It does not establish measured customer ages, incomes, demographics, acquisition
economics or a validated segmentation model. Historical “SF premium shopper”
language is not customer research.

## 7. Creative saturation register

Counts below are bounded source observations, not campaign exposure or
effectiveness measurements. Repetition can build recognition; saturation risk is
a proposed creative assessment.

| Device                               | Frequency / origin                                                                | Current use                              | Classification                                  | Risk / future guidance                                                                                           |
| ------------------------------------ | --------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Dark/black surfaces                  | 91 void-token references in two V2 CSS consumers; four identity palettes use dark | Both sampled home bodies and Kids world  | L3/L4                                           | Medium-high if inherited everywhere; **available**, rotate where authorized, never infer a new palette exception |
| Warm/light counterpoints             | 24 paper-token references in same CSS sample                                      | Source-supported alternative surfaces    | L4                                              | Low; evidence current system is not literally all-black                                                          |
| Monuments                            | “monument” occurs in 4/4 V2 immersive template files                              | Current scene vocabulary/assets          | L3/L4                                           | High if every channel repeats; **rotate**, not master invariant                                                  |
| Cathedral                            | Text in 2/4 immersive templates                                                   | BR/LH scene definitions                  | L3/L4, disputed lineage                         | Medium-high; **available only within verified scope**, no universal default                                      |
| Throne                               | Text in 2/4 templates; one LH hit rejects an empty throne                         | Positive motif confirmed in Kids runtime | Kids context/device                             | High contamination risk; **do not require outside context**                                                      |
| Chrome/metallic marks                | Asset hierarchy and Drive variant names; no global pixel-frequency count          | Recognition in scoped marks/scenes       | Asset identity or scene treatment depending use | Medium; **required when exact approved asset demands it**, optional environmental material                       |
| Brand monogram                       | Explicit chrome asset rule; repeated navigation/source references                 | Brand recognition                        | Scoped asset policy / grammar                   | Low if faithful; **required in governed chrome**, scale/prominence varies by channel                             |
| Collection script lockups            | Font/artwork declarations across collection sources                               | Collection identity mark                 | L3 artwork                                      | Identity-building; **preserve mark**, avoid applying lettering to all copy                                       |
| Bridge/night/gold-light scene        | YAML, storyboards and current staging descriptions                                | Current worlds                           | L3/L4                                           | Medium-high; **rotate** scenery without changing origin or garment graphic                                       |
| “House/world/chapter” phrases        | Repeated in two homepage text captures; no complete copy-corpus count             | Navigation/editorial metaphor            | L2 narrative mechanism / L3 phrasing            | Medium; **available**, not mandatory copy formula                                                                |
| Royal Procession / three-part reveal | One Kids controller and candidate contract                                        | Kids/home concept                        | L3/L4                                           | Medium; **rotate**, not universal motion philosophy                                                              |
| Train reveal                         | Current/superseded storyboard pair                                                | Jersey-specific local concept            | Campaign                                        | High if used generically; **scoped**, no inferred partnership or release                                         |
| Camera/spotlight/render settings     | Present in immersive source; no produced-shot count                               | 3D implementation                        | L4                                              | Unknown exposure; **available**, not identity criteria                                                           |

Do not train a “brand correct” gate solely on these recent scenes. E32’s global
centroid can reward visual similarity and repetition; it cannot decide whether a
novel but factually faithful direction is on brand. Novelty assessment should
compare conceptual difference while separately enforcing truth and identity
constraints.

## 8. Preserve truth while allowing expression

The following is a **proposed context policy**, not permission to override
existing restrictions.

| Domain                                                                 | Freedom                             | Boundary                                                                                                       |
| ---------------------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Product facts, graphics, proportions, approved colorways, measurements | NONE                                | Resolve exact SKU/view; preserve founder wording/ranges. Missing is a gap, not invitation to invent.           |
| Price/sale price/availability/preorder/variants                        | NONE                                | Registry facts and current Woo purchase state must agree; stale values block factual publication.              |
| Factual/legal/rights/partnership claims                                | NONE                                | Require applicable evidence; do not infer from moodboards or logo presence.                                    |
| Master/collection asset geometry                                       | NONE without explicit authorization | Use approved asset variants and permitted roles.                                                               |
| Brand narrative identity                                               | LOW                                 | Expression can vary; origin, author and history cannot be fictionalized.                                       |
| Voice expression                                                       | MODERATE                            | Preserve factual fields, retired-copy exclusion and scoped copy policy.                                        |
| Typography treatment                                                   | MODERATE                            | Current site uses current font owner; new campaigns may explore only within approved brief or marked proposal. |
| Motion treatment                                                       | MODERATE–HIGH                       | Narrative purpose, usable controls and fallbacks remain; exact effects optional.                               |
| Composition/lighting/environment                                       | HIGH within permitted scope         | No product alteration, unsupported palette exception, lineage reversal or asset-use expansion.                 |
| Campaign story/visual metaphor                                         | HIGH                                | Narrative can be new without inventing brand history, garment claims or partnerships.                          |
| New channels/concepts                                                  | OPEN for proposals                  | Unapproved concepts stay proposals; release/spend/use authority is separate.                                   |

**Must preserve:** source-backed identity and approved mark roles. **Should
express:** specificity, intentional narrative and legibility. **May vary:**
collection/channel/campaign treatment. **Open territory:** novel proposals
within explicit constraints. **Must not alter:** product, factual and legal
truth. Freedom is not inherited as an override: a HIGH environment freedom does
not cancel a NONE product-color rule.

## 9. Product truth is a separate plane

Current registry: 33 products—14 Black Rose, 5 Love Hurts, 12 Signature, 2 Kids
Capsule. `get_all_products()` resolved all records; returned image-role bindings
point to existing files. That is file-existence evidence, not visual or
live-media approval.

Use `from skyyrose.core.product import get_product` or
`.venv/bin/python -m skyyrose.core.product <sku>`. Preserve the returned
catalog/garment/dossier/images/render-sources/logos/content/corrections/authority/provenance
structure. Some enriched content, alt text and corrections are read from
referenced side stores; the complete reader does not mean every output byte is
physically registry-owned. Narrow readers remain valid for narrow needs.

Protected fields include SKU/name, variants/colorways,
fit/silhouette/construction, graphics/placements/dimensions, materials/features,
sizing, price/sale price, collection, approved media role/view, factual claims
and preorder state. Live WooCommerce remains the authority for current session,
selected variation, totals, stock/addability and transaction outcome; it must
conform to intended catalog facts. Do not choose a live mismatch as an implicit
catalog edit.

Current reader gap totals: 16 missing `back_packshot`; 3 missing `back`; 14 each
missing enriched long/short copy, SEO, Instagram, TikTok and alt-text
enrichment. Every product has a base description. Do not report these as 14
products with no description. The `gaps` array currently covers image/content
gaps; it is not exhaustive validation of every garment measurement or job
requirement.

The “dossier first” instruction can coherently mean adding founder prose to the
registry-embedded dossier before deriving garment fields and regenerating
readable mirrors. This package proposes that clarification; it made no catalog
edits. No remote-main/all-worktree parity or exhaustive
latest-founder-correction comparison was established.

## 10. Brand drift map

| Duplicated truth                   | Probable owner                                 | Consumers / risk                                                 | Future consolidation, not performed                                                        |
| ---------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Tagline/copy policy                | Current founder retirement + YAML state        | Injector, CMS metadata, greetings, old prompts: high             | Source-resolve empty value; scan generated and runtime text; preserve no-replacement state |
| Font roles                         | typography.json                                | YAML mirrors, V1/V2, package, prompts, PDF: high                 | Field-scoped generated adapters; separate dashboard and artwork roles                      |
| Color semantics                    | Scoped brand/collection owners                 | CSS, eval, injector, UI contrast adjustments: high               | Separate brand color, product color and accessible UI token fields                         |
| Collection names/slugs/story seeds | identity.json + registry collection bindings   | YAML, Python enums, templates, CMS: high                         | Explicit aliases `kids` / `kids_capsule` / `kids-capsule`; reject unknown collection keys  |
| Product facts                      | Unified products registry                      | CSV, dossier exports, prompts, static components, live Woo: high | Reuse complete reader, task-specific gaps and parity checks; no new product corpus         |
| Logo/media identity and use        | Registry/manifests + scoped founder decisions  | Asset directories, Drive variants, scene derivatives: high       | Hash/role/use-bound references and approval state, never filename-based permission         |
| World/campaign direction           | Applicable approved brief                      | Old LOCKED prompts, local scenes, storyboards: high              | Versioned context records with supersedes/expiry/approval evidence                         |
| Motion rules                       | Scoped experience contract plus implementation | Eval, unapproved proposal, V2 controllers: medium                | Separate principle from timing adapter; do not declare one current global system           |
| Brand embeddings                   | Validated model/dataset contract               | Visual gates: medium-high                                        | Track training set and limits; never let similarity ratify canon                           |
| Generator documentation            | Actual build graph                             | YAML’s stale script name: medium                                 | Correct docs in later scoped remediation; verify output freshness                          |

## 11. Proposed minimal reusable package

Use the five logical roles implemented by this review package: an entry point,
narrative reconciliation, indexed evidence, a context manifest, and
validation/source snapshots. There is no need to create empty per-channel
folders. When contexts grow, split records by domain without changing IDs or
ownership.

The machine manifest has scoped rules, authorities, status, evidence IDs,
confidence, exceptions, creative freedom and last validation. It explicitly
distinguishes existing source instructions from proposed invariant
classification. References resolve current source content; the package does not
copy catalog values or re-author founder history.

Resolution model:

1. Identify brand, job, collection, channel, SKUs, intended use, mode
   (research/preview/release) and required roles.
2. Load current identity/owner policy and product truth independently. Verify
   actual source digests, not CSV modification time.
3. Select expression grammar, collection context, channel requirements and an
   explicitly identified campaign version. Do not inject every historic
   campaign.
4. Resolve each field by domain owner and applicable scope. A narrower campaign
   cannot override protected identity/product facts. Unknown or tied conflicting
   authority yields a named conflict, not last-write-wins.
5. Carry approval per asset and intended use. Observed deployment, source
   presence, candidate review and paid-provider execution remain separate
   states.
6. Emit a reproducible bundle: rule IDs, source pointers/digests, selected
   contexts, locked product references, exclusions, conflicts and task-required
   gaps.
7. Research/preview may include unresolved proposals with labels. Release blocks
   required unknowns/conflicts; optional marketing enrichment can remain a
   visible gap.

Example: a Kids Instagram image brief loads core identity, applicable
visual/voice grammar, Kids identity, `get_product(kids-001)`, chosen asset/view
and a named campaign brief. It does not automatically load a throne, Black Rose
cathedral, legacy pastel palette or old Drive price. Without a current approved
campaign direction it returns a **preview context with unresolved art-direction
scope**, not permission to publish. Instagram placement specifications must be
checked when an execution job is created; no obsolete platform dimensions are
enshrined here.

Other adapters: Creative OS reads grammar/freedom/saturation; Ads OS adds
evidence for claims, audience assumptions and offer freshness; Production OS
consumes exact asset/view/use constraints; image/video/3D workflows receive
product locks and scoped environment choices; web/ecommerce adds current
type/UI/Woo adapters; copywriting adds voice and retired-copy constraints. New
brands use independent namespaces and owners. None should inherit SkyyRose’s
collection palettes or cultural claims by template default.

No production resolver, new dependency or migration was installed. The manifest
is a systematic assembly specification, validated as structured data, not a
claim of an integrated runtime API.

## 12. Owner decisions and adoption boundary

Ready for review: the L1 candidate classifications; the boundaries on creative
freedom; whether future Kids art direction mandates the current throne treatment
or permits other heir-centered worlds; scope of new nonproduct palette/lineage
exceptions; and any final approvals missing for a specific asset’s new use.
Decisions should record owner, date, exact scope, source evidence, supersession
and allowed exceptions. This package does not fabricate those decisions.

Already resolved and not asked again: founder product facts, no active tagline,
the recorded Signature origin answer, product-registry ownership and current
website font-source ownership.

Adoption should first repair the stale injector and resolve high-risk
source/generator drift in a separately scoped change, then exercise context
bundles against representative jobs. Suggested contract cases: unknown SKU
rejects; missing requested back view blocks render; proposed campaign cannot
overwrite price; accessibility UI red cannot recolor garment; Kids context does
not import BR scene; retired slogan is excluded; unsupported sustainability
claim blocks; unknown channel remains unknown; exact source change invalidates
cache; candidate-only approvals never become release-ready.

## 13. Verification and limitations

Executed: product projection check passed; 27 focused product/context-catalog
tests passed; all 33 products resolved; file existence checked for returned
image-role bindings. Manifest/evidence referential checks and file hashes are
recorded in `validation.json` and `source-snapshot.json`. Application/theme
builds were not needed for this additive research package. Existing generator
freshness, production parity, payment, full accessibility, reduced-motion
runtime execution and provider/rights clearance were not certified.

Connected sources: Drive search returned matching project sources; selected 2025
overview and April 2026 architect PDF were read, a top brand folder was listed,
and a bounded 30-item logo-folder page was inspected. The logo folder may
contain more entries. Source metadata is not pixel inspection or current
approval. WordPress inventory returned production and staging plus two
unlaunched simple sites; no need to change or elevate those sites. Figma
capability is available, but no project file URL was found in the bounded
brand/design/source scan; no Figma library content was asserted. Ads
performance, social-account audience evidence, provider histories and physical
packaging standards remain unverified.

The investigation answers where the strongest available truth lives and how to
keep it from being overwritten by repetition. It deliberately leaves genuinely
unestablished facts and approvals visible.
