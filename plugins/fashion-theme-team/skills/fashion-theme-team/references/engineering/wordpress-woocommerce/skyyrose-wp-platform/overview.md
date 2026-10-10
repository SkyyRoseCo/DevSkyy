# SkyyRose WordPress Platform

Load when: a task touches `<theme-root>` PHP, its CSS/JS build, its WooCommerce integration, or its Three.js scenes. Not for generic WordPress questions with no SkyyRose surface, and not for the Next.js dashboard at `frontend/` (that is devskyy.app, a different host entirely).

Provenance: embedded from the DevSkyy skill `skyyrose-wp-platform` (`SKILL.md`); source hash, license, and every adaptation are recorded in [`../index.md`](../index.md).

> Placeholders: `<theme-root>` is the theme directory (in DevSkyy: `wordpress-theme/skyyrose-flagship`); `<theme-workspace>` is its parent, where `package.json` and the Node build live (in DevSkyy: `wordpress-theme/`); `<repo-root>` is the host checkout root.
>
> Host repo (DevSkyy): the skill names this file cites (`wordpress-router`, `threejs-animation`, `3d-rigging-pipeline`, `wp-plugin-development`, `wp-playground`, `wc-pdp-correctness`, `woocommerce-webhooks`, and the fifteen generic skills listed below) are DevSkyy-installed skills, not plugin skills. Inside this plugin, the four reference files under this directory and `../wc-pdp-correctness.md` carry the doctrine.

"SkyyRose" This skill exists because a generic WordPress reference can't
carry that -- it doesn't know the difference between Black Rose's gothic armor and Love Hurts'
"bloodline that raised me," it doesn't know the mascot is the face of the brand, and it doesn't
know a wrong-garment render is the single most repeated defect on this project. Every section
below is written for THIS storefront, not a portable template that happens to mention it.

It replaces what fifteen scattered generic skills (`wp-block-development`, `wp-block-themes`,
`wordpress-plugin-core`, `wordpress-router`, `wp-performance`, `wp-plugin-development`,
`wp-rest-api`, `woocommerce*`, `wc-pdp-correctness`, `immersive-interactive-architect`,
`css-cascade-discipline`, `accessibility`, `seo`, `web-vitals-budgets`) covered in the abstract.
Those stay installed -- disabling them is a separate, confirmed decision -- but nothing in
this skill borrows their generic framing. If a section here could apply unchanged to any other
WooCommerce theme, it's wrong and should be rewritten until it can't.

## When to use

Load this skill when any of these is observably true:

- the task edits a file under `<theme-root>/` (PHP, CSS, JS, `theme.json`,
  `templates/*.html`, `patterns/*.php`)
- the task changes shipped CSS/JS and therefore needs `npm run build` + a `.min` re-verify
- the task reads or writes WooCommerce product/order state for skyyrose.co
- the task touches the mascot, `assets/js/skyy-3d.js`, or anything under `assets/scenes/`
- the task prepares a release candidate or bumps `SKYYROSE_VERSION` (the deploy itself is
  outside plugin scope -- see the Procedure boundary note below)

**Do NOT use this skill when:**

- the repo kind is unknown — run `wordpress-router` first to classify, then come back
  (Host repo (DevSkyy): `wordpress-router` is a DevSkyy skill)
- the work is in `frontend/` (Next.js dashboard on Vercel, `devskyy.app`) — different stack,
  different host, no theme build
- the work is pure Blender/rig authoring with no WP surface — that is `3d-rigging-pipeline`
- the work is a generic WordPress plugin unrelated to this storefront — `wp-plugin-development`

## Inputs

| Required before you start                | How to confirm it exists                                                                                                                                                                                      | If absent                                                                                                                                              |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Theme root                               | `test -d <theme-root>`                                                                                                                                                                                        | STOP — you are in the wrong tree or a sparse worktree                                                                                                  |
| Node deps for the build                  | `test -d <theme-workspace>/node_modules`                                                                                                                                                                      | `cd <theme-workspace> && npm install` before any `npm run build`                                                                                       |
| PHP tooling (phpcs/phpstan)              | `test -x <theme-root>/vendor/bin/phpcs`                                                                                                                                                                       | `composer install` in `<theme-root>/`. Do NOT skip the gate and report "clean" — an absent linter is a dead gate, not a pass                           |
| WooCommerce creds (only for REST work)   | `grep -c WOOCOMMERCE_KEY .env.wordpress` (Host repo (DevSkyy): keys live in `.env.wordpress`)                                                                                                                 | STOP. Never fabricate live product state from the product registry or its CSV projection; the registry says what _should_ be true, REST says what _is_ |
| Product source of truth + image bindings | `logo-registry.json` (in DevSkyy a root symlink to `<theme-root>/data/logo-registry.json`)                                                                                                                    | STOP — no product or imagery decision without it. Filenames are not identity; the registry's image bindings are                                        |
| Deploy credentials                       | Outside plugin scope — the Fashion Theme Team builds and reviews candidates only; production deploys, live WooCommerce/media writes, and paid calls belong to the host repo's STOP-AND-SHOW approval process. | Not an input to this plugin's work                                                                                                                     |

Sparse worktrees (since 2026-07-12) exclude `assets/renders/` and screenshots. If an eyes-on
imagery gate needs those, run it in the main checkout — do not declare the aspect passed here.

## Brand doctrine (the part a generic skill has no way to know)

- **Four collections, four identities, never interchangeable**: Signature (gold `#D4AF37`,
  Archivo headings, Pinyon Script name-lockup, city-tour immersive world), Black Rose (silver
  `#C0C0C0`, Archivo headings with Cinzel as engraved-caps accent, SkyyRose Black Rose Script
  name-lockup, gothic cathedral immersive world, armor as its visual language), Love Hurts
  (crimson `#DC143C`, Archivo headings, SkyyRose Love Hurts Graffiti name-lockup, romantic
  castle immersive world, "the bloodline that raised me" -- that line belongs to Love Hurts
  alone, never borrowed for another collection), Kids Capsule (rose gold `#B76E79`, Archivo
  headings, Grand Hotel name-lockup). Collection name-lockups are bespoke-script images, never
  live type; interior copy is unified (Archivo display, Hanken Grotesk body/UI, Anton UI caps).
  Rose Gold `#B76E79` is also the global accent
  across the whole storefront; `#0A0A0A` is the dark background every collection sits on.
- **Cut fonts stay cut**: Playfair Display, Cormorant Garamond, Bebas Neue, Yellowtail were
  removed 2026-07-10 and must never reappear in `theme.json`, `assets/css/`, or a pattern.
- **Crimson `#DC143C` is 3.63:1 on `#0A0A0A`** — below WCAG AA for body text. Fills, borders and
  glows only; de-emphasised text uses `--color-text-muted` (`#B3B3B3`, 9.44:1).
- **Visual lineage is Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels — never
  European luxury.** This is a locked canon decision, not a style preference. A build,
  render, or copy pass that reaches for European-luxury visual language is wrong regardless
  of how polished it looks.
- **The mascot is the face of the brand** -- a full-body walk-on presence, not a chatbot, not
  a decorative widget. Its rig integrity (see `threejs-immersive.md`) is treated with the same
  seriousness as the product photography.
- **Real products only.** No hallucinated or never-made renders reach this storefront. Product
  facts and product imagery resolve through the single editable product source of truth,
  `logo-registry.json` (in DevSkyy a root symlink to `<theme-root>/data/logo-registry.json`):
  its `products[sku]` records own commerce fields, colors, sizes, fit, materials, design spec,
  and image bindings. The catalog CSV and per-SKU dossiers are generated projections, read
  through sanctioned readers and never authored. Never a filename guess -- see
  `woocommerce-integration.md`.
- **The founder is the authority on the brand's own story and his own products.** Corey, the
  founder and maker, is authoritative on his product specifications: his confirmations are
  recorded as `FOUNDER_CONFIRMED`, and no third-party verification is demanded of his facts.
  His bio and product dossiers are founder-authored, not ML-drafted -- this skill documents how
  the engineering serves that voice, it does not generate brand narrative itself.

## Router — which reference file for which task

| Task                                                                                                                                                                | Read                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Templates, patterns, blocks, `.min` build pipeline, enqueue/template routing                                                                                        | `build-and-templates.md`                                                                                                                                                                       |
| WooCommerce REST v3, webhooks, product sync, PDP correctness                                                                                                        | `woocommerce-integration.md` (and `../wc-pdp-correctness.md`)                                                                                                                                  |
| The mascot, the four immersive worlds, anything in `skyy-3d.js` or `assets/scenes/`                                                                                 | `threejs-immersive.md` (and `../../threejs-immersive/index.md` for the Three.js runtime side; Host repo (DevSkyy): `threejs-animation` + `3d-rigging-pipeline` for the Blender/animation side) |
| Accessibility, SEO/schema, Core Web Vitals, CSS cascade discipline, CSP/nonce security -- the gates that keep the storefront feeling like the brand it claims to be | `quality-gates.md`                                                                                                                                                                             |

Read only the reference file(s) the task actually needs -- this router file plus one
reference file is the normal footprint, not all four.

## Procedure

1. Classify the surface and open exactly one reference file from the router table above.
2. Read the code you are about to change (`Read`/`Grep`, `file:line`). No claim about this
   theme survives without a tool call from this session behind it.
3. For any non-stdlib API (WooCommerce REST, three.js, WP core function signatures), run
   Context7 `resolve-library-id` → `query-docs` before writing the call. Training data is stale.
4. Make the edit. Files stay under 800 lines, functions under 50; escape on output, nonce +
   capability on every write path; text domain is `skyyrose`.
5. If you touched `assets/css/**` or `assets/js/**`, run `cd <theme-workspace> && npm run build`.
   Production serves `.min` — a source-only edit ships nothing.
6. If you touched shipped CSS/JS/PHP that is about to deploy, bump the version **triple** to the
   same value: `functions.php` `SKYYROSE_VERSION`, `style.css` `Version:`, `readme.txt`
   `Stable tag:`. That constant is the cache-bust param on ~52 enqueue calls.
7. Run the Verification block below. Read the actual output.
8. Fix the cause and re-run, max 5 attempts. Same error twice in a row → stop and report.
9. Deploying: Outside plugin scope — the Fashion Theme Team builds and reviews candidates
   only; production deploys, live WooCommerce/media writes, and paid calls belong to the host
   repo's STOP-AND-SHOW approval process. Review knowledge to carry: theme deploy is an atomic
   hot-swap — production loses any file the source tree lacks.

## Universal discipline (applies to every reference file below)

Every capability below exists to protect one thing: nothing about SkyyRose ships generic,
half-verified, or unchecked against the real brand. Three non-negotiable layers, inherited by
every reference file -- do not restate them per-section there:

**1. efficient-production discipline.** Before any tool call: do I already have this? No
re-reading a file already read this session. No rebuilding `.min` assets you haven't actually
changed source for. Batch parallel reads/greps instead of issuing them one at a time. Zero
`TODO`/placeholder/dummy data in delivered PHP or JS. Every factual claim about this theme's
code traces to a `Read`/`Grep` call from this session, not memory of an earlier session.

**2. Boris Cherny's verification philosophy (tip #14, verbatim).** "Give Claude a way to
verify its work... invest in domain-specific verification, it 2-3x's quality." Every section
below names a _specific, re-derivable_ verification method using a real authoritative source
for this project -- never "looks correct," never a self-graded pass from the same script that
made the change. If you cannot name what tool call proves a claim, the claim isn't done yet.

**3. Production-gate before "done."** Match this project's existing Loop Protocol: write the
change, run the real check for that domain (phpcs, `.min` rebuild + curl, WooCommerce REST
read-back, Playwright, Context7 lookup), read the actual output, fix if it fails, repeat up to
5 times, stop and report if the same error repeats twice. Never claim "deployed" or "fixed"
without the check's actual output from this session.

## Verification

Run from `<repo-root>`. At minimum,
checks 1 and 2 on every change; 3 after any CSS/JS edit; 5 when reviewing a deploy the host
repo has already performed.

**1 — Aspect gate (the repo's own, 17 CLI aspects):**

```bash
cd <theme-workspace> && npm run verify:theme
```

PASS: final line reads `VERIFY PASS — 0 fail, 0 warn`. `[test]`
The 4 BROWSER/VISION aspects print SKIP. **A SKIP is not a PASS** — `responsive`,
`a11y-interactive`, `cwv` are closed by the caller running Playwright/axe/Lighthouse;
`product-fidelity` is closed by a human or agent reading the actual pixels against the
registry-bound reference. Name whichever you left open in your report.

**2 — PHP standards and static analysis:**

```bash
cd <theme-root> && vendor/bin/phpcs --standard=.phpcs.xml -s .
cd <theme-root> && vendor/bin/phpstan analyse -c phpstan.neon
```

PASS for phpcs: `0 errors`. `[repro]`
phpstan has a **144-error standing baseline** — a raw count is not a verdict. Attribute your
delta: extract the pristine tree and diff the _contents_, never the state.

```bash
S=$(mktemp -d) && git archive HEAD <theme-root> | tar -x -C "$S"
```

PASS: your changed files appear in neither the pristine run's output nor add new lines to it.
`[test]` Never `git stash` for this — the stash stack is shared across worktrees.

**3 — The shipped bytes, not the source:**

```bash
cd <theme-workspace> && npm run build && bash <theme-root>/scripts/verify-theme.sh --only min-sync
```

PASS: `[PASS] min-sync   every .min css/js byte-identical to a fresh build`. `[test]`

**4 — Version triple is one value:**

```bash
grep -h "SKYYROSE_VERSION\|^Version:\|^Stable tag:" \
  <theme-root>/{functions.php,style.css,readme.txt} | head -3
```

PASS: all three print the same version. `[repo]` A changed asset without a bump leaves returning
visitors on stale cached CSS.

**5 — Live, cache-busted (review of a host-repo deploy only):**

```bash
curl -sI "https://skyyrose.co/?cb=$(date +%s)" | head -1
curl -s "https://skyyrose.co/wp-content/themes/skyyrose-flagship/style.css?cb=$(date +%s)" | grep -m1 '^Version'
```

PASS: `HTTP/2 200`, and the Version line equals the `SKYYROSE_VERSION` you shipped. `[live]`
NEVER `WebFetch` here — it strips `<script>`, hiding JSON-LD and OG data. Cache-bust always;
Batcache serves stale. Only a `[live]` probe licenses the word "production" in a severity claim.

**Prove the gate can fail before you trust it.** Break one input once — e.g. append a stray byte
to a `.min.css`, re-run check 3, confirm `min-sync` goes red, then `npm run build` to restore. A
gate never observed failing is a guess with a citation.

**A gate that dies is not a gate that passed.** If `verify-theme.sh` errors, times out, or is
killed, its zero-findings output is an artifact — re-run it or verify by hand (bug-230, ×6).

## Verification sources this skill trusts (and why)

| Claim type                                               | Authoritative check                                                                                    | Never substitute                                                                                                                                                                         |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PHP syntax/style                                         | `php -l` + `vendor/bin/phpcs --standard=.phpcs.xml -s .`                                               | Reading the code and assuming it's valid                                                                                                                                                 |
| Live HTML/JSON-LD/headers                                | `curl -s "URL?cb=$(date +%s)"` (cache-busted)                                                          | `WebFetch` -- it strips `<script>` tags, silently hiding JSON-LD/OG data                                                                                                                 |
| Visual/rendering result                                  | Playwright or Chrome DevTools MCP screenshot, desktop + mobile                                         | Trusting a curl 200 as "the page rendered correctly"                                                                                                                                     |
| WooCommerce/product state                                | Live REST v3 read via `.env.wordpress` BasicAuth                                                       | The product registry (`logo-registry.json`) or its CSV projection alone -- the registry is the source of truth for what _should_ be true, REST is the source of truth for what _is_ live |
| Product imagery ↔ SKU match                              | Reading the actual pixels (vision) against the reference bound in `logo-registry.json` `products[sku]` | The filename or a generated manifest -- both can lie, and wrong-garment imagery is this project's most repeated defect                                                                   |
| Library/API usage (WP, WooCommerce, Elementor, three.js) | Context7 `resolve-library-id` → `query-docs`                                                           | Memory of the API shape -- training data predates recent WP/WC/three.js releases                                                                                                         |
| `.min` build actually changed                            | Diff or byte-size check on the `.min` output itself                                                    | Confirming the source file changed and stopping there                                                                                                                                    |

## Worked example

Task: confirm the theme is deploy-shaped before opening a change.

```bash
cd <repo-root>/<theme-workspace>
bash <theme-root>/scripts/verify-theme.sh --only min-sync
bash <theme-root>/scripts/verify-theme.sh --only templates
```

Observed 2026-07-29 `[test]`:

```
[PASS] min-sync               every .min css/js byte-identical to a fresh build
------------------------------------------------------------
VERIFY PASS — 0 fail, 0 warn. (SKIP = needs browser/vision; verify those separately.)
[PASS] templates              funnel templates + WC overrides present
```

Then the version triple:

```bash
grep -n "SKYYROSE_VERSION" <theme-root>/functions.php
grep -n "^Version" <theme-root>/style.css
grep -n "Stable tag" <theme-root>/readme.txt | head -1
```

Observed `[repo]`: `functions.php:21: define( 'SKYYROSE_VERSION', '1.12.9' );` ·
`style.css:12:Version:             1.12.9` · `readme.txt:7:Stable tag: 1.12.9` — triple in sync.
Note the scope: this is `[repo]`. Live was 1.12.8 at last probe, so the repo is one bump ahead
of production and that delta is **undeployed**, not "deployed and stale" — a claim I have not
probed this session and therefore do not make.

## Failure modes

| Symptom                                         | Cause                                                                                                                                                                                                                         | Fix                                                                                                 |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| CSS/JS edit has no effect on the live site      | Production serves `.min`; the source edit never rebuilt                                                                                                                                                                       | `npm run build`, re-run `--only min-sync`                                                           |
| Returning visitors see the old design           | `SKYYROSE_VERSION` triple not bumped — the cache-bust param on ~52 enqueues is unchanged                                                                                                                                      | Bump all three files to one value                                                                   |
| Files present locally vanish after deploy       | Theme deploy is an atomic hot-swap; Host repo (DevSkyy): `preflight_completeness()` (`scripts/deploy-theme.sh:313`) only checks **git-tracked** files, so untracked riders are invisible to it and silently dropped (bug-252) | `git add -f` the rider to put it under the gate                                                     |
| `curl` says 200 but the page is visually broken | An HTTP code is not a render                                                                                                                                                                                                  | Playwright/Chrome DevTools screenshot at 390px and desktop                                          |
| JSON-LD / OG tags "missing"                     | `WebFetch` strips `<script>`                                                                                                                                                                                                  | `curl -s "URL?cb=$(date +%s)" \| grep`                                                              |
| A collection page shows the wrong garment       | Imagery resolved by filename instead of the image bindings in `logo-registry.json` (read through a sanctioned reader such as `skyyrose.core.sot_images`)                                                                      | Re-resolve via the registry and read the pixels; this is the project's #1 recurring defect (lh-005) |
| Report says "0 findings" but the gate crashed   | Fail-open: a dead gate read as a pass (bug-230, ×6)                                                                                                                                                                           | Re-run by hand; an errored gate is an artifact                                                      |
| "Found a production bug" from a repo read alone | Scope jump — `[repo]` evidence carrying `[live]` severity (bug-287, ×2)                                                                                                                                                       | State scope before severity, or go probe production                                                 |

## See also

- `../../threejs-immersive/index.md` — the plugin's Three.js runtime reference (this skill's
  `threejs-immersive.md` covers the WP-specific loading/CSP wiring, not general three.js API).
  Host repo (DevSkyy): the original cross-reference was the `threejs-animation` skill
- Host repo (DevSkyy): `3d-rigging-pipeline` — Blender-side authoring for anything this theme's Three.js scenes play back
- `../wc-pdp-correctness.md` (Host repo (DevSkyy): also `woocommerce-webhooks`) — this skill's
  `woocommerce-integration.md` is the stack-specific entry point, not a replacement for their detail
- Host repo (DevSkyy): `wp-playground` — a disposable WP instance when you need to boot this theme without touching prod
