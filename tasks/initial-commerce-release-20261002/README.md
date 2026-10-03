# Initial product-commerce release — evidence through 2 October 2026, 23:54 UTC

**Release readiness: HOLD.** The local commerce candidate is prepared; hosted acceptance and actual installed-baseline recovery remain incomplete. Corey deferred the four immersive worlds, shared engine and Worlds hub. They are no longer initial release prerequisites. A later, explicit “Fix those gaps” instruction authorized the bounded merchant corrections below. Deployment, activation, publication, payments, credential changes and a controlled checkpoint retry remain unauthorized.

## Initial scope and source decisions

The 33-product native Woo catalog, home/shop/product discovery, four collection pages, cart, checkout and truthful service/size information form the initial scope. Native Woo prices remain authoritative. No stock ownership, remaining quantity, preorder date or narrower enabled SKU set was invented.

[scope.json](scope.json) proposes exactly five production drafts: Signature10427, Black Rose10428, Love Hurts10429, Kids Capsule10430 and Size Guide10436. Worlds hub10431 and four worlds10432–10435 remain draft; existing Collections9327, Cart9451, Checkout9452 and merchant pages are preserved. The old ten-page publisher must be revised and reviewed before any publication approval. Page hashes are retained snapshots and must be re-read before an operation.

The candidate points initial world navigation to collection shopping, filters only exact same-origin deferred routes, and uses temporary302 redirects with no-cache headers for postponed routes. Unrelated/external links and stored admin menus are preserved. Retired legacy aliases retain their existing301 behavior. Deferred world source/assets remain packaged; their launch acceptance is deferred. This local change has not been installed.

The installed staging delta has an explicit file-by-file decision in [installed-enhancement-decisions.json](evidence/installed-enhancement-decisions.json): defer its coherent optional editorial/highlight block (13changed runtime files and5extras), exclude35existing nonrelease authoring/QA extras, and retain candidate source. Nine independent source permission fixes were safely adopted: generated public files0644/directories0755, private incomplete temporary output, atomic replacement and a read-only deployment preflight. No owner dirty tree was copied or edited and no deployment ran.

BR007's founder-supported dossier correction remains isolated in `a6bdf54321e727f21a8b5c2b41417d31b2617274`; canonical registrySHA256 `d14fb9ef09528581e552d4c4be007c8da7610d239c2017b68baf96c31ae93d8e`. It states that Love Hurts is only on the side, not across the back. Immutable certification separately binds the reviewed registry and precisely nine commerce source paths; all other source pins remain frozen. BR001/BR004/BR007 mismatched card fronts remain blocked; GLB acceptance remains empty/disabled.

## Current identities and ownership

Staging blog256563697 at `https://staging-7e48-skyyrose.wpcomstaging.com` is active V2 `skyyrose-flagship-2`2.5.0. Its23:54:07UTC read-only census still has639files, with every earlier installed hash unchanged: [final census](evidence/staging-installed-final.json), [identity](evidence/staging-final-identity.json). Production blog238510894 at `https://skyyrose.co` is active V1 `skyyrose-flagship`. These targets are distinct. No theme activation or page publication occurred.

PR1000's last authenticated base receipt is OPEN/DRAFT at `a662e707d698a687d7d1d2efed3975b9aa7325b9`,21successful/6skipped checks. That green CI does not qualify this newer feature branch. Existing integration4035 owns its dirty preservation/runtime work; card-gap-integration owns the optional installed enhancement work. This task uses isolated `codex/initial-commerce-release-20261002`; their files remain untouched. Read-only Codex task APIs supplied existing results; no existing agent was messaged.

The original599-file ZIP comparison had586same/13changed/40extra/0missing staging files. Those counts describe the original package, not the newer candidate. The final deliverable receipt outside the checkout binds the exact final commit, ZIP and deterministic rebuild; it supersedes earlier package receipts. The separate docs feature branch was independently pushed at `fb5c3cd95c68e62c4eb18c824dff6cef3a51707a`.

PR1006 is separately preserved OPEN/DRAFT at `319ce7cf6b5bacad72cf435c47c21ce39e8ca1f5`, main/base `7892b797d838e67e62c862a6698a5b42b6dccaee`. Its new typography is **not integrated or installed**. Four builder/certification files overlap this branch and require a reviewed union followed by verification. Its CI run37073761428 fails the root dependency audit; root package/lock were not changed by that PR. Downstream root checks skipped; passing V2 checks do not erase that failure. [Reconciliation](parallel-review/pr1006-reconciliation.json) preserves exact paths and findings.

The separate task `01a0fefc-e4d2-7641-a68c-8bd43b44400e` owns review/budget setup. Corey approved20USD aggregate/month including PR-branch fixes, but the inspected current workflows have no verified shared hard cap. Current main's review workflow has no draft guard; PR1006 already had a successful review despite draft. No paid workflow was requested here. [Workflow facts](parallel-review/WORKFLOW-FACTS.md) retain source hashes and boundaries; no review workflow/settings/credentials were edited.

## Merchant corrections and live result

[Merchant outcome](merchant/MERCHANT-OUTCOME.json) records the reviewed runnerSHA256 `611c0c8d5ea37c18039f2bf9c2d48fbc028d4a62aabc30edaa72c493ef456cbf` and operation `0bf6f801-1f5d-41e6-b2b2-6c37508c327d` at23:31:19–23:31:27UTC. Kids9955/kids-001 and9956/kids-002 received only existing approved front images, native featured attachments10437/10438. Both native65prices, existing images/history, unmanaged stock/null quantity/instock and other protected fields were preserved. No production orders/payments were read or mutated.

Independent native readback and served asset hashes pass. Ordinary PDPs initially retained cached placeholder HTML; the installed host's two-URL purge succeeded without a global purge. At23:42:47UTC both ordinary public PDPs returned200, included the approved filenames and no awaiting-image placeholder: [final rendered evidence](merchant/production-kids-final-rendered-verification.json). These checks establish native assignment and served identity, not full browser, garment, size or payment acceptance. The durable operation journal is retained; [RECOVERY.md](merchant/RECOVERY.md) requires exact postimage comparison and refuses foreign changes before any separately authorized restore.

LH006 production9879 remains simple,95, Size One Size with no native variations. The canonical sizes are S/M/L/XL/2XL/3XL. A descriptive label edit alone cannot provide size selection or persist selected size to a native cart/order. The prepared conversion preserves prices/images/history and unmanaged inventory;40native offline fixture assertions cover selectors, all six cart additions, old simple-cart invalidation/reselection, partial failure rollback and guarded recovery. **Live conversion NOT RUN:** automatic approval review rejected its existing-cart consequence without exact approval. An explicit question remains pending; no retry/dispatch ran after rejection.

Final production reconciliation passes33/33parent prices and preorder flags,32/33declared sizes: [receipt](evidence/production-reconciliation-final.json). Fifteen preorders have no ship date. Unmanaged inventory is not automatically a release failure; truthful availability and fulfillment/policy responsibility still need acceptance under existing ownership.

## Verification and limits

| Check | Result | Scope |
|---|---|---|
| Native Kids image assignment, protected fields, served bytes/public PDP HTML | PASS | Two production products only |
| LH006 native size conversion | NOT RUN / BLOCKED | Explicit cart-reselection approval pending |
| Permission builders / preflight | PASS |32builder tests,21preflight tests |
| Initial navigation / temporary deferred redirects | PASS |37assertions |
| Immutable source certification | PASS |29tests; unauthorized drift remains rejected |
| BR007 focused registry/compatibility | PASS |60tests |
| Native merchant fixture | PASS |40assertions; copied local WP7.1.2/Woo11.1.2/SQLite; external HTTP blocked |
| Retained sanitizer vs inert successor | PASS offline |2intercepted local browser tests; no live checkpoint |
| Consumed capture diagnosis | PASS offline diagnosis; checkpoint FAIL unchanged | Four unsupported lifecycle shapes per profile; cookie absence/page faults not inferred |
| Activation-option recovery helper | PASS synthetic only |7tests; installed-baseline recovery NOT RUN |
| Full clean final package / repeat | See final external receipt | Declared toolchain and pinned native gallery fixture; no hosted deployment |
| New branch CI | NOT RUN | Base PR green and PR1006 results are separate |
| Hosted active-theme mobile/cart/checkout/payment acceptance | NOT RUN | Requires separately approved controlled successor |
| Actual installed-baseline recovery | NOT RUN | Source V1 archive is not installed V1 baseline |
| Preorder promise / truthful media and availability | HOLD | Controlling policy and enabled offers require owner acceptance |
| Deployment/theme activation/page publication/payment | NOT RUN | No authorization used |

[Verification aggregate](evidence/verification-successor.json) and adjacent qualified logs retain local results. The full package uses existing Node22.23.2/npm10.9.8/Python3.12.12/Pillow12.3.0 and seven hash-pinned WP7.1/Woo11.1.0 gallery fixture files. No host toolchain changes, dependency downloads or new imagery generation occurred.

The consumed V1 checkpoint remains FAIL. Pure hash-pinned classifier replay identifies four unsupported request shapes per profile; original large UNKNOWN totals are not independently established page faults. The exact retained sanitizer reproduces a HANDLER error and extra image request in an isolated comparator, while the inert utility does neither. Historical mobile error causation remains **unproven** without original timing/stacks. This evidence does not reopen the consumed operation or wire the successor into live capture.

## Remaining decisions and approved-next-step packet

1. Merchant: approve or decline the exact LH006 native variation conversion, including removal of old simple-cart entries with native notice/reselection. No new size facts or stock ownership decision is needed for the prepared conversion.
2. Merchant: identify the controlling preorder promise/policy version and truthful presentation for15absent ship dates; accept availability/fulfillment under existing ownership. No new reservation/decrement feature is required by this task.
3. Release owner: approve exact candidate/target, narrowed five-page delta, revised publisher and separately reviewed controlled acceptance/recovery steps in [APPROVAL-AND-RECOVERY.md](APPROVAL-AND-RECOVERY.md). Explicit analytics disablement/deferral can avoid making receiver delivery a commerce blocker, provided consent/privacy and checkout independence pass.

Four immersive worlds, shared world engine, Worlds hub, 3D/GLB acceptance, optional analytics delivery, optional installed editorial enhancements and new creative imagery remain post-launch scope. Typography PR1006 is an independent reviewed integration choice. This packet does not declare the storefront finished.
