# Initial product-commerce release — 2 October 2026

**Release readiness: HOLD.** Local corrections and source verification pass; hosted commerce acceptance and recovery qualification are incomplete. Corey's 2 October voice direction defers the four immersive worlds, shared world engine and Worlds hub. They are no longer initial launch prerequisites. This packet does not authorize a controlled checkpoint retry, deployment, activation, publication, product writes, inventory changes or payment actions.

## What can enter the initial release

The existing 33-product catalog, native Woo prices, ordinary home/shop/product discovery, four collection landing pages, cart, checkout and truthful service/size information form the initial scope. Published product count is not an acceptance result: sizes, media, availability and commercial promises must work for every offer actually enabled. A narrower SKU set requires an explicit merchant decision; none was silently selected here.

The proposed publication delta is only five current production drafts: Signature10427, Black Rose10428, Love Hurts10429, Kids Capsule10430 and Size Guide10436. Their exact paths, templates and content hashes are in [scope.json](scope.json). The hub10431 and worlds10432–10435 remain draft. Existing merchant pages, including Collections9327, Cart9451 and Checkout9452, are preserved. The old ten-page publisher/clearance is incompatible with this scope and must be revised and reviewed before approval. Deferred destinations must also be removed or redirected from initial navigation; publication alone does not resolve route links.

Optional analytics delivery, 3D viewers, new editorial imagery, immersive chapters, world transitions and Worlds hub acceptance can be deferred. Initial privacy/consent behavior and checkout independence remain mandatory if their code is retained. Receiver failure is not independently a launch prerequisite when analytics is explicitly disabled and its failure cannot harm commerce. No safe operational deferral has been activated by this task.

## Current identity and ownership

[live, read-only] Staging blog256563697 is `https://staging-7e48-skyyrose.wpcomstaging.com`, active `skyyrose-flagship-2`2.5.0. Production blog238510894 is `https://skyyrose.co`, active `skyyrose-flagship` V1. They are distinct targets. All ten prepared production pages are still drafts; the existing public merchant pages remain published.

[repo/live, read-only] PR1000 is OPEN/DRAFT at `a662e707d698a687d7d1d2efed3975b9aa7325b9`, with21successful and6skipped checks. Three paid Claude jobs and deployment jobs were skipped. This is base-candidate CI, not CI for the new branch.

Existing integration4035 owns that release branch and dirty preservation/runtime work. Coordinator69e2 and integration task results were read through Codex read-only task APIs; historical checkpoints were not promoted to current facts. Existing card-gap-integration owns the installed staging enhancements. Other tasks' files were not edited or messaged. Work here uses the isolated checkout on `codex/initial-commerce-release-20261002`.

[live/repo] Current staging has **639files**, rather than the historical614 or packaged599. Compared with the original599-file package:586identical,13changed,40added,0missing. All13changed bytes and the added garment-highlight module match the dirty card-gap-integration tree. They include commerce/layout/media changes and cannot be adopted by copying its broad dirty tree. [The census comparison](evidence/staging-package-comparison.json) identifies the actual delta; its inclusion/exclusion still needs owner review and a coherent commit/package. The installed payload is not the new local candidate, nor the original ZIP.

The historical original ZIP identity is SHA256 `47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16`,176928301bytes,599files. It is historical, not a hash for the corrected candidate.

## Concrete corrections and findings

[repo/test] Commit `a6bdf54321e727f21a8b5c2b41417d31b2617274` corrects only BR007's founder-supported dossier: “Love Hurts is only on the side not across the back.” It regenerates the compatibility dossier and adds regression coverage. Prices, preorder flags, images, other products and approval decisions remain byte/semantic unchanged. The new canonical registry hash is `d14fb9ef09528581e552d4c4be007c8da7610d239c2017b68baf96c31ae93d8e`.

The certification contract binds that immutable registry commit separately from the existing reviewed source299f694. Negative drift tests and an exact only-dossier comparison prohibit blanket hash reapproval. Presentation output changes only two registry digest fields. BR001/BR004/BR007 card fronts remain blocked for product mismatch; GLB acceptance stays empty/disabled. Existing image hashes establish identity, not new full-pixel garment approval.

[live/read-only] Both sites have exactly33published canonical parent SKUs; all33native prices and preorder flags match the canonical reader. Production has33simple products; staging has31variable and2simple products. Fifteen are preorders on each target, all with absent ship dates. All33parents have unmanaged stock, null quantity and `instock`; edition size is not remaining stock. No quantity or decrement ownership was chosen.

[live/repo] LH006 production9879 is simple with descriptive Size `One Size`, variation=false. Canonical and staging sizes are S,M,L,XL,2XL,3XL; staging is variable. [The exact proposed merchant delta](lh006-proposed-correction.json) changes only the descriptive Size options. That alone does **not** add a native selector or selected-size cart/order persistence: the installed native simple template renders quantity and an add button. Fresh read-only LH006 rendered HTML confirms only those two controls in production, while staging renders `attribute_size` and native variation identifiers (see [rendered controls](evidence/lh006-rendered-size-controls.json)). Do not describe this small edit as a size-flow fix. A reviewed variable migration (or an existing proven size-capture extension) is required if purchasable size selection is intended. Current staging variations are a reference, not authorization to migrate production. Migration must preserve native price, existing attachments and preorder facts and leave stock ownership untouched until decided. Production sizing acceptance applies beyond this one inaccurate label.

[live/read-only] Kids native attachments are empty in production. This task checked rendered pages before calling that a defect: both current V1 PDPs return200 and render `Awaiting product image` placeholders. V2 staging PDPs return200 and render the existing approved theme fronts; both served image files match the local approved SHA256. [The fallback receipt](evidence/kids-rendered-fallback.json) records exact URLs/hashes. V2 therefore has an existing front remedy; no new image generation is required. These HTML and byte checks do not prove browser visibility, variation behavior or new garment fidelity review.

[live/read-only] Staging enables BACS/cheque/COD; Stripe is disabled with testmode=yes. Production enables WooPayments/wallets and Stripe; Stripe reports testmode=no. These flags do not prove authorization, settlement, webhook handling, refund behavior or available payment methods at checkout. No payment or order action ran.

## Acceptance matrix

| Gate | Result | Evidence / remaining work |
|---|---|---|
| Source/base PR identity | PASS | Authenticated PR/check-run receipt at a662;21success/6skip |
| Target separation, active themes and page preservation | PASS (read-only configuration) | Current authenticated target/census/page receipts; not runtime acceptance |
| Parent SKU/native price/preorder reconciliation | PASS |33/33 each; canonical reader and offline projection; four fail-closed identity tests |
| Production declared sizes | FAIL | LH006 One Size differs; no live write |
| Actual size selection/cart/order persistence | NOT RUN | Production simple/staging variable divergence; approval needed for bounded native acceptance |
| BR007 correction and registry compatibility | PASS |60focused tests; correction receipt and generated check |
| Immutable certification tests | PASS |28tests; all other pins remain reviewed source |
| Full local theme verify | PASS | Exact declared Node22.23.2/npm10.9.8/Python3.12.12; pinned native fixture; qualified log |
| Inert snapshot successor utility | PASS (isolated fixture) |1browser test; root attrs corrected after review; not wired to a live checkpoint |
| Production Kids gallery | FAIL (current V1 HTML) |2placeholder PDPs; staging V2 existing fronts/hash identity pass |
| Hosted V2 mobile/navigation/cart/checkout/payment | NOT RUN | No current authorized controlled acceptance; original V1 checkpoint remains consumed FAIL |
| Product fidelity and truthful availability | NOT RUN / HOLD | Blocked fronts remain excluded; enabled offers need faithful fallback/availability acceptance |
| Preorder promise/policy ownership | HOLD |15null ship dates; controlling wording/version and null-date policy unresolved |
| Truthful availability / optional inventory expansion | NOT RUN | Existing unmanaged stock can retain its operating ownership if availability is truthful; new finite-allocation/reservation/decrement behavior needs a separate owner decision |
| Installed enhancement inclusion | HOLD |639installed vs599packaged; owner dirty delta not integrated |
| Verified installed-baseline recovery | NOT RUN | Existing7synthetic helper tests do not prove hosted recovery |
| Deployment/activation/publication/payment | NOT RUN | No authority used or granted |

Initial full-verify attempts failed because the workstation Node22 binary's existing simdutf34 dependency was no longer on its default path, then because the pinned native fixture was unset. Both logs remain. A local wrapper resolves the already installed9.0.0 dylib, with no host changes or downloads; the existing seven-file native fixture validates its pins before execution. The qualified full run passes. The isolated browser's initial macOS sandbox launch failure also remains separately recorded; its successful run was a local intercepted fixture outside that sandbox.

## Smallest owner decisions and operational approvals

1. Merchant: controlling preorder promise/policy version and how absent ship dates should be presented for the 15 offers; verify truthful availability under the existing operating ownership. Unchanged unmanaged stock is not automatically disqualifying. A new finite-allocation/reservation/decrement feature, or an actually unresolved fulfillment responsibility, needs a separate decision. The task chooses neither dates nor inventory policy.
2. Merchant/integration: preserve simple products only with proven size capture, or review a native variation migration; LH006's six canonical sizes need no new founder fact. Review the exact installed639-file enhancement delta for the chosen package.
3. Release owner: exact narrowed five-page publication delta and a revised publisher/clearance; explicit safe analytics deferral if receiver remains unavailable. Worlds are already deferred by Corey and need no renewed launch decision.

Separately authorize the controlled live acceptance successor only after diagnosing unsupported lifecycle request rows offline and reviewing its instrumentation; the scope change does not reopen the consumed V1 checkpoint. Its four unsupported request shapes per profile caused global capture qualification failure; large UNKNOWN totals are not independently established page faults. Mobile HANDLER/sanitizer causation remains unproven. The isolated successor utility here is not a checkpoint fix or retry permission.

## Deployment and recovery sequence requiring approval

After source ownership/inclusion is resolved, freeze a clean exact commit and repeat deterministic package verification. Preserve actual production active V1 bytes/configuration/pages and installed staging639 bytes as separately hashed recovery artifacts. Existing installed V1 was79files/version2.3.1, while a source V1 package was1724files: substituting that package is not verified restoration. Test the reviewed recovery helper against the **actual installed** baseline with route, theme, draft/page and permission checks.

Request explicit approval for the resulting exact package/target and the narrowed controlled acceptance sequence. Only then deliver to staging, reconcile installed runtime hashes, perform mobile/no-JS/reduced-motion/native cart/checkout and approved test-payment acceptance, and validate product media/size/availability/policy. A production activation/publication request must separately name its exact package, five page IDs and hashes, preserved merchant pages, expected behavior, and tested recovery. No production order/payment action is implied by a site release approval.

Commit/push authority arrived later from the parent: publish already completed qualified work on feature branches only. The completed docs branch was pushed and independently verified at `fb5c3cd95c68e62c4eb18c824dff6cef3a51707a` as `codex/production-readiness-docs-20261001`. This task must keep PRs draft: ready-for-review would run three Claude provider workflows and spending approval remains unanswered. No merge, force-push or main update is authorized.

## Deferred after launch

Four immersive worlds, shared world engine, Worlds hub, 3D/GLB runtime, optional analytics delivery/enhancements, new editorial/hero imagery and additional creative enhancements. Existing media holds and faithful product constraints carry forward. Completion of these local changes does not mean the storefront or full release is finished.
