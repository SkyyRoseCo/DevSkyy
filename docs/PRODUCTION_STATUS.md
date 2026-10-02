# Current production status and release boundaries

**Last updated:** 2026-10-02. **Latest browser/preservation observation:** 2026-10-02
12:23:59 UTC (05:23:59 PDT), recorded from actual operation receipts.
**Additive classification review:** 2026-10-02 12:31:25 UTC (05:31:25 PDT).
Individual CI and browser observations retain their own timestamps below.
**Installed theme identity read:** 2026-10-02 12:49:09 UTC (05:49:09 PDT).
**Operational source:** `a662e707d698a687d7d1d2efed3975b9aa7325b9`.

This is a dated operator snapshot of the integrated release. It supplements the
retained task records; it does not change their historical states or authorize
execution. Refresh the snapshot from the release coordinator's actual receipts
before using it for a new operation. The documentation commit is separate from
the frozen operational source and does not rebuild the approved package.

## What is established

| Gate or surface                 | Observed result                                                                                                                                                       | Evidence limit                                                                                                                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Five workstreams                | Scoped source adopted and integrated                                                                                                                                  | The adoption manifest includes open inventory, asset/device, policy, and Governor runtime holds                                                                                               |
| Functional source               | Frozen at `299f694702ac2dcc61a0f30aa34e4b3ef12f9118`                                                                                                                  | Local tests are bounded integration evidence                                                                                                                                                  |
| Clean V2 package                | Source `5950592d922706dd67fc0320e8c5f3dc005a47b7`; repeat bytes and installed-file checks passed                                                                      | Packaging does not establish live production behavior                                                                                                                                         |
| Existing staging                | V2 2.5.0 installed; all 599 reviewed file hashes matched                                                                                                              | Staging has 220 product/variation records; it cannot establish parity with production's 33 simple products                                                                                    |
| Production                      | `https://skyyrose.co`, active directory `skyyrose-flagship`; ten owned pages remain unchanged drafts; latest scoped post-read matches its pre-read | Active header identifies older SkyyRose Flagship 2 v2.3.1, not proven canonical source V1. Earlier verification matched 599 inactive V2 files; latest scoped read does not repeat that census or 33 prices. No V2 activation or `DEPLOYED` |
| Procedure and acceptance inputs | Exact headless-shell diagnostic collection and local V2 qualification independently reviewed | The later passive diagnostic is COMPLETE, but its current acceptance remains FAILED; local V2 qualification is not live acceptance |
| Exact operational-head CI       | `CI_PASS`: 21 mandatory successful checks, 6 intentional skips, no pending/failure/cancellation                                                                       | Single targeted Playwright retry: 62 passed (31 Chromium, 31 mobile), 0 failed/skipped/flaky; source CI is separate from production acceptance                                                |
| Execution clearance             | The native V1 checkpoint and separately cleared passive diagnostic attempts are consumed | The latest diagnostic completed its observation scope. Its completion does not clear a retry, V2 activation, or publication |
| V1 Search checkpoint            | October 1 desktop/mobile acceptance remains FAIL; October 2 passive diagnostic collected complete evidence with process exit 0 | One emitted `tk_ai` declaration still fails the frozen response-cookie rule; 423 requests remain UNKNOWN under that classifier. Diagnostic completion is not checkpoint acceptance |
| Production V2 acceptance        | Not executed                                                                                                                                                          | No V2 activation, `DEPLOYED`, or `PRODUCTION_ACCEPTED`; complete accepted V1 Search/privacy capture, activation, and six-profile V2 acceptance remain required                                |

## Latest passive diagnostic and current hold

The separately reviewed, passive desktop home-to-Search diagnostic completed on
**2026-10-02 at 12:23:00 UTC (05:23:00 PDT)** with **process exit 0**. Its
completion seal records **COMPLETE collection** and **current acceptance
FAILED**. Native capture and Playwright each recorded **482 requests**, with
matching identities, complete lifecycle evidence, and all **seven owned
processes stopped**. Search returned HTTP **200**, **27 total results**, and
**10 returned rows**. This diagnostic did not attempt PDP or no-results flows.

The additional evidence narrows the two outstanding findings:

1. Search emitted one `Set-Cookie` declaration named `tk_ai`. Blocked-cookie and
   exempted-cookie fields are present, but both lists are empty. Saved cookie
   jars and all **55 captured sent-cookie-name rows** are empty. These are
   observations, **not proof of explicit rejection, acceptance, transient
   storage, or no transmission across UNKNOWN rows**. The frozen rule rejects
   the emitted name, so its FAIL remains unchanged.
2. The **423 UNKNOWN rows** now divide into **399 Font requests with explicit
   CSP failure metadata** and **24 memory-cache-shaped requests: 16 Script and
   8 Font**. The former have the exact `request → failed` sequence with a
   present empty error string, `canceled=false`, and `blockedReason=csp`. The
   latter have `request → cache → response → finished`, HTTP 200, and zero
   encoded bytes. The current classifier still reports UNKNOWN; source-backed
   predicates and controlled local server tests must qualify any successor.

The additive classification was recorded at **12:28:58 UTC**, and its
independent review passed at **12:31:25 UTC**. That later review validates the
immutable evidence and classification; it does not move the operational
observation time or pass production acceptance. The prior failed runs remain retained.
An earlier October 2 diagnostic stopped before navigation on an exact browser
identity mismatch. Subsequent local full-Chrome trials exposed native favicon
requests absent from Playwright's page events; those failures were preserved.
The successful passive diagnostic uses the explicitly pinned
**HeadlessChrome/143.0.7499.4** executable and unchanged strict coverage checks.

The separate V2 harness also passed its **six-profile local qualification** on
that explicit headless-shell runtime, including both 31-second consent
observations and clock-shift controls. This is local harness evidence only;
V2 has not been activated or tested live.

An authenticated scoped preservation read at **12:23:59 UTC (05:23:59 PDT)**
matches the complete result of the immediate pre-read. V1 remains active, the
owned MU source matches, all ten owned pages remain unchanged drafts, and six
protected merchant pages match their snapshots. A separately reviewed earlier
homepage snapshot difference consists only of the serialized Elementor CSS
cache timestamp; no actor or mechanism is inferred. The post-read does not
repeat the **33-product price check or 599-file inactive V2 census**. CI remains
separately dated **October 1 at 18:10:27 UTC**.

The next work is bounded local qualification of CSP/cache classifications and
Search credentials behavior, with an explicit review of the privacy test's
relationship to the original storage, transmission, and tracker requirements.
Source/configuration inference must remain distinct from actual browser
configuration. No historical FAIL is rewritten, and no new site journey or
production mutation follows from local qualification alone.

| October 2 evidence | SHA-256 |
| --- | --- |
| Passive diagnostic freeze manifest, 143 members | `7ecceca79ed919d84f514b717ea4c7afe683d143791a7973b1cc6cb487be475d` |
| Actual diagnostic manifest, 8 members | `58b31b4ab48147531058923c9502daff7866ad4ee74cbad970aebc26da8f2bf2` |
| COMPLETE collection / FAILED acceptance seal | `88f338e5622e1c0a16fa73be49f41219f97767adf40288542ac2507b1b3d6135` |
| Additive actual classification | `10281b17ff25909c8bd655b41ca686d47ef23cd4d7c1f9039b06894c62e6807a` |
| Independent classification review | `9b96f883ed1deb03509f5ef5de7629aaf70c330ca720ecfbeaf9e0c823ce172c` |
| Scoped post-read at 12:23:59 UTC | `f5b1cacc06f065045ad186ee7d830867d8205043e3f0d566765518bb73637532` |
| Explicit-shell V2 local review | `9a9e655c78faff4c398c62e8c62d9202652a76dfbf9abfbf1936778803293095` |

## October 1 native checkpoint history

The reviewed native-capture successor was frozen as **79 members** after **31
combined local tests passed** and independent source, procedure, runtime, and
relocated default-mode review. The single live V1 checkpoint completed at
**18:17:40 UTC (11:17:40 PDT)** with **process exit 1** and **FAIL in both
desktop and mobile profiles**. Its valid FAIL completion seal binds all **21
operational evidence members**; all member hashes and lengths match. The
original 79 frozen members remain unchanged. Evidence integrity passed;
production acceptance did not.

Both profiles reached a positive Search response: HTTP **200**, **27 total
results**, and **10 returned rows**. Each then stopped at the privacy check.
The native PDP and no-results journeys were **not attempted in this run**.
The finalized run records no global capture exceptions and confirms transport
exit; those facts do not resolve the request-level UNKNOWN results.

Two distinct findings require correction and review:

1. The Search service response contains the `Set-Cookie` **name** `tk_ai`.
   The captured request's sent-cookie names and saved browser-cookie
   observations are empty. This proves the response header was present; it
   **does not prove that the browser stored or sent the cookie**. The frozen
   acceptance contract expressly forbids that response-cookie name, so the
   result remains FAIL. The capture does not retain blocked-cookie reasons,
   and they cannot be reconstructed from these records.
2. Each profile retains **423 UNKNOWN requests**: **399 Font requests** with
   `request → failed` and insufficient failure metadata, plus **8 Font and 16
   Script requests** with a memory-cache-shaped sequence. The latter have a
   cache event, HTTP 200 response, and completed zero-byte transfer, but their
   resource types are outside the reviewed Image/Stylesheet memory-cache
   qualification. Neither a failure event nor absent ExtraInfo proves that a
   request was unsent. The original classification's total of 407 Font rows
   must not be read as 407 failed Font requests.

At that checkpoint, the correction work was local: retain native failure and blocked/exempted-cookie
diagnostics without values, qualify Font/Script cache behavior separately with
actual local server observations, and investigate a supported Search privacy
correction. The operational classifier and response-cookie policy remain
unchanged. The later diagnostic and local V2 qualification above advance that
investigation without supplying production acceptance or clearing the V1
findings. Any proposed operational successor needs independent review and
fresh scoped clearance before another live checkpoint.

A fresh authenticated, read-only preservation check at **19:21:43 UTC
(12:21:43 PDT)** confirms V1 remains active, the installed MU still matches its
owned source, the homepage and six protected merchant pages match their
snapshots, and all ten owned pages remain unchanged drafts. It produced no
warnings or stderr. This read **did not revalidate the 33 product prices or all
599 installed V2 files**. The latest retained CI refresh is separately dated
**18:10:27 UTC (11:10:27 PDT)**: 21 SUCCESS and 6 expected SKIP at the frozen
application head. No production mutation or second browser attempt followed
the failed native checkpoint within that October 1 snapshot.

## Earlier execution history

The cancelled Playwright job is `110435542010` in CI run `36880002499` on exact
`a662e707…`. Its preserved complete log records about 16 minutes in checkout, 3
minutes in Python dependencies, 28 seconds in frontend npm installation, and 10
minutes 38 seconds in browser OS dependencies with slow APT mirror retries. No
Playwright tests started in that attempt.

Astra recorded `ONE_BOUNDED_TARGETED_RETRY_REVIEW_PASS` after the complete log
review. Integration dispatched exactly one targeted retry on the same frozen
head and workflow run. Successor job `110451737866`, run attempt 2, started at
15:45:10 UTC and completed successfully at 15:59:04 UTC. The actual Playwright
test step ran from 15:56:46 to 15:58:50 UTC: **62 passed** (31 Chromium and 31
mobile), with **0 failed, skipped, or flaky tests**.

The final authenticated Code Review receipt records **21 mandatory SUCCESS / 6
intentional SKIP**, with no pending, failed, cancelled, or unexpected skipped
checks. The original 20 SUCCESS / 6 intentional SKIP / 1 CANCELLED attempt and
its full log remain preserved. GitHub inherited the earlier successful same-head
upstream results for attempt 2; this does not claim every upstream suite ran
again. No workflow, source, dependencies, browser selection, timeout, or test
changes were made, and no fetch-depth contingency was needed.

GitHub's actual tested checkout was merge commit
`30fdd5940fb7ce4951b8c95c63f2784dc930a3a6`, with parents `7892b797…` and
`a662e707…`. Authenticated tree readback establishes that its tree
`40cad1a67e8efa99ddc0843dbf6ceffb53f55e49` equals the frozen operational `a662`
tree. PR #1000 remains open, draft, and unmerged at the same head.

Astra issued `FINAL_COMBINED_CLEARANCE_PASS`, with architect PASS, after review
of the final CI receipt, combined 12 evidence bindings, adoption record, and
actual target identity. The coordinator's durable
`CLEAR_TO_EXECUTE_SCOPED_CUTOVER` receipt closes both the CI and
acceptance/procedure conditions and sends the sole writer the reviewed execution
signal within the existing human scope.

The receipt supplies **conditional scoped execution clearance**, not proof of
installation or live V2 acceptance. Immediate authenticated target, source,
artifact, option/page preimage, native configuration, and ownership guards
remain required before each mutation.

The inactive installation command returned exit 0 under the reviewed clearance.
Subsequent readback and independent review established all **599 exact installed
V2 files** and preservation of active V1, its file/option baseline, and native
products/prices. The coordinator released the initial
precondition-classification hold at **16:27:08 UTC**. The original intent,
attempt, and initially held readback remain immutable; the later hold-release
receipt supplies the reviewed outcome.

The sole writer prepared **ten owned draft pages, IDs 10427–10436**. Read-only
MU ownership and draft-page readbacks passed. The first MU command's ambiguous
CLI warning is retained without a retry; its precise cause remains **UNKNOWN**.
Fresh bootstrap checks were clean, and the later ownership/readback evidence
establishes the installed reviewed extension without rewriting that attempt.

At **16:33:58 UTC**, the authenticated hosting account `skyyroseco`, Production
`skyyrose.co`, separately confirmed **"Object cache cleared."** and **"Global
edge cache cleared."** Post-cache readback and the **16:34:25 UTC**
`MU_INSTALLED_CACHE_CLEARED` signal bind the installed MU, draft ownership,
cache clear, and still-active V1. These receipts establish installation and
cache clearing, not public runtime acceptance.

The frozen **`checkpoint-v1-live-20261001t1634`** failed in both desktop and
mobile profiles between **16:34:41 and 16:35:41 UTC**, each timing out after
**25 seconds** while awaiting a Search response. Its initial normal-home
observations found no tracking handles or owned visitor/session identifiers;
that narrow observation does not establish the complete privacy or Search gate.
The failed results, per-profile receipts, and evidence manifest are preserved.

The **16:37:50 UTC** read-only diagnostic verified a **test-query/matcher
encoding mismatch**: both `+` and `%20` query forms returned Search API HTTP
200, 27 total results and 10 result rows, with no JavaScript errors. The
observed response query encoding did not satisfy the original predicate; `%20`
navigation displayed the intended `Black Rose` input. The original failed run
remains preserved. Its timeout does not establish a production Search outage.

The bounded query correction passed **34 focused offline tests** and
Ruff/Black/mypy checks, with independent Python and Astra
source/procedure/freeze review. The coordinator issued
`RESUME_V1_SEARCH_CHECKPOINT_ONLY` at **16:46:38 UTC**, bound to the successor
**39-file freeze** and corrected procedure. That signal allowed only the actual
V1 desktop/mobile checkpoint; it did not clear V2 activation or publication. The
original 26-file freeze and first failed 14-file run remain unchanged.

The corrected **`checkpoint-v1-query-corrected-20261001t1647`** completed both
profiles from **16:47:11 to 16:47:23 UTC** and printed PASS with process exit 0.
Each intended-query Search journey returned HTTP 200, 27 total results and 10
rows, opened the returned native product and checked its native form, and
completed a no-results Search journey with HTTP 200 and zero results. Four
privacy observations per profile completed. These establish completed functional
journeys and recorded observations, not accepted privacy capture completeness.

The full attempt stderr contains **three `TargetClosedError` occurrences**; that
count does not prove three distinct lost requests. The request callback reads
`all_headers` before appending its record, and profile PASS/receipt
serialization occurs before context closure. Missing callback request
identities/timing leave capture completeness **UNKNOWN**. Empty frontend
JavaScript error arrays do not establish the observer's health or prove harmless
teardown. The **16:48:48 UTC** immutable instrumentation-hold receipt preserves
the process result and verifies the run's **22 evidence members** without
accepting V1 checkpoint PASS.

That instrumentation hold led to the reviewed native-capture successor and the
later failed checkpoint described above. The earlier printed PASS and its
incomplete observation record remain historical evidence; they have not been
relabeled as accepted. The timeout, privacy, product-click, empty-result, and
native-form gates remain required. The verifier correction did not change the
application, MU, theme package, or operational head. A verifier failure alone
does not establish a production regression or require MU rollback.

At this snapshot, **all next production writes are held**. V1 remains active;
the ten owned pages remain drafts. No V2 activation, `DEPLOYED`, or
`PRODUCTION_ACCEPTED` is established. Source CI and conditional execution
clearance remain separate valid receipts, but neither overrides unresolved
runtime privacy and observation findings. Any changed or unknown precondition also stops
the next mutation for read-only reconciliation under the reviewed stop/recovery
rules. Never blindly retry an uncertain mutation or substitute diagnostic
results for required acceptance evidence.

The authenticated target snapshots report WordPress **7.1.2**, WooCommerce
**11.1.2**, and PHP **8.4.26** on production and existing staging. These are
captured versions, not a promise that hosting versions remain unchanged. Recheck
them with the site identity immediately before execution.

## Exact candidate identities

| Binding                                         | SHA-256 or revision                                                |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| Operational source                              | `a662e707d698a687d7d1d2efed3975b9aa7325b9`                         |
| Functional source                               | `299f694702ac2dcc61a0f30aa34e4b3ef12f9118`                         |
| Clean package source                            | `5950592d922706dd67fc0320e8c5f3dc005a47b7`                         |
| V2 ZIP: 599 members, 176,928,301 bytes          | `47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16` |
| Separate Search privacy MU extension            | `afc2f6d8a4ae6280de28b6c1306564cc86053acc713c52e5ab0b5717b3ef58f2` |
| Ten-page plan                                   | `dc7ca358d530cc44aeea75771236573e48088cd7f99b545941b3b05cbbd7b44e` |
| Cutover candidate manifest                      | `7b52fb62b0c49e52785e2fc1be6cc2a3dd0d020407e128ead3dd8341ade7c1b3` |
| Initial acceptance freeze: 26 files             | `22b30db9d34eda875acbcc64a26a172bdd2d7e051cadcb4ce41a5c66e8d0b0d1` |
| Initial acceptance procedure                    | `8944f3fe7f461117ec57bec7fc852835c2110bcd534481afc797d33e56ca887e` |
| Initial V2 acceptance harness                   | `0573e738c95a18528bce4e3dd6631c5a5f2c78e9b9fcd2ee083e21ef6807497d` |
| Combined release evidence manifest: 12 bindings | `ef053fa175b69913469c33a259c91afb61eff811e004eff4e09457145e20e2a2` |
| Procedure/source review receipt                 | `cd7d6b16d322dd2ab7ecec19be9f2ff3fff72663aa5a4876be56b5a67647e2ff` |
| Final exact-head CI receipt                     | `23c467bf8dbde980ab3c22f95f84d324cbdf72acac3368bed37c031289d5eeb4` |
| Scoped pre-execution clearance receipt          | `4f90c881ea90674736aa8828e50a34f27f1c604903f9ac6b32d19803149ba286` |
| Inactive V2 installation intent                 | `db924ba569058bb1a2f961756229e919c521270d2c701f9a8ee03f0cdf94c9a6` |
| Inactive V2 command-attempt receipt             | `317bcbe7625e1a6c9a32dcf790167585f3a1802d82da5ca269b686ea3abc5f9a` |
| Inactive V2 installed-file readback             | `e7aa2feeee905f9ddcc861715d436a38c5a2b09ad9346ea8a268ff16e731d68d` |
| Initial precondition hold-release receipt       | `ae25567c5c50f1b1e6c1c1565a1083298fc273fa44c675305ea353d076ab3f2c` |
| MU installed ownership readback                 | `0cf5882765f84601b26654bdbfad25e4d6d682e6e3680378be8f390953eaa449` |
| Ten-draft readback and warning trace            | `39ef314f8a1aa0487dff7107826e297ca24597a0f79d60be681a94cb446afba0` |
| Authenticated hosting cache-clear receipt       | `b2f1ca21cd5dd89f3eaaa4f6d0c769a1c5e98241e4bbff429047974bb6480330` |
| Post-cache MU readback                          | `92b5f00ef60b281ef26a99dc3340b8a271182181fac84a43ce7e6c2011137bcb` |
| Installed MU/cache-cleared checkpoint signal    | `8ef3f92ae55f1890459fdf041741dda5a9b48db3ffcab9d61895a126fa7c2b76` |
| Failed desktop/mobile V1 checkpoint results     | `3fe1b7e41d47af56a36d2806ffb77910cd1bd19f2b90e5f5db12ffd0cfc7d632` |
| Failed V1 checkpoint evidence manifest          | `2268ca39ac746befa045d321f5442e3581a5f081c35a94f405d910c4a9cac1c2` |
| Read-only Search encoding diagnostic            | `5759ca5b0c911f4a457c7d3c4e43094481bfdc638f655667702d6f86ac1a8534` |
| Query-correction reviewed freeze: 39 files      | `1e721925eee5b09703e79d6044c58a3b68ad178514c4ba15891073a27d9fcaeb` |
| Query-correction reviewed procedure             | `ccac68f3acf2929d799add6e9fc9b32103fd0a5440cc680db13bd6fe8cb9a7b1` |
| Query-corrected V1 checkpoint-only resume       | `0c3c674257fa393f52f2c89a8658ae8c295aa8bcd8660ec03b729c3cfbd96e5c` |
| Query-corrected checkpoint full command attempt | `508b4b2c67acb7c651ea488cc21d3fee789a75df7941d296a57c7c383f32fe65` |
| Query-corrected printed profile results         | `a179db54b46d9c08ec2578227e4285f63b1287808916031aecc4f648dc0a0f13` |
| Query-corrected run evidence manifest: 22 files | `62559d1f25143f9342d497042493bc0ddca2a3b2a7d2d889505bd77e1c91f59f` |
| Query-corrected instrumentation-hold receipt    | `676635d31ad6980784a13f0a92564160c80bdbeb442b4a8626b4c31b69f3adab` |
| Native V1 combined source review                | `9c57a0cff8dc388d6ba348df1352b72564c4c00ccfe9db06ef85e96879f01874` |
| Native V1 reviewed freeze: 79 members            | `d99c81cb9c56bdc3f6e5a2d91d323e76734d539583e3e697640ed8076b69b9d2` |
| Native V1 freeze identity review                | `963b4b657f1b340345e3acc645cacd3b8039bd3c9fbf1d0c58f1bdb89278ba51` |
| Native V1 checkpoint-only clearance (consumed)   | `10ca8f91a3e3732f3e209847f528b439c57b81e44da5830702b2b400adc405bd` |
| Native V1 actual command attempt: exit 1         | `a9f64f211dad558f1bbd13d9be9a76d7a6dfedbb7e71e1a0d5fed9fc523a5ae0` |
| Native V1 failed-run manifest: 21 members        | `e97385294af740e63064cf8ea70d4ba9421be896dbbb3e4e359f9e2f89cd5251` |
| Native V1 valid FAIL completion seal             | `4b7d61b7faac9d1afe75b54202a1bf78b22f2e23795152062237e89d08847bc5` |
| Native V1 finalized FAIL run receipt              | `501c952d8738aeb80bfecc7f321cded45245318f90da6b0d4463af5a8dc867cb` |
| CI refresh before native V1: 18:10:27 UTC         | `c6e32070524ad38ed4d70a5acb39096b3fade996858e4ca7b3b0dda98d77ce11` |
| Post-failure preservation read: 19:21:43 UTC      | `bd2f5297f004b22d71675924a79ddac8af503ff28a6704b6c1416402d01e081f` |

The Search extension is a separate artifact; it does not change the V2 ZIP.
Recomputing hashes of changed files cannot approve a successor. Match the
literal reviewed bindings and invalidate clearance when the operational source
or any required source/artifact/receipt bytes change.

## Separate theme packages and installed identity

The October 2 requirement is to deliver **two independently installable theme
packages**: V1 rooted at `skyyrose-flagship/`, and V2 rooted at
`skyyrose-flagship-2/`. Each must contain its own theme metadata, bootstrap,
assets, and required data without a sibling-theme runtime dependency or parent
`Template` declaration. Both remain consumers of the single editable product
registry; package separation does not create a second source of product facts.

Two separate ZIP artifacts are prepared:

| Package | Theme root and source identity | ZIP size / files | SHA-256 |
| --- | --- | --- | --- |
| V1 source candidate | `skyyrose-flagship/`; SkyyRose 2.2.4 from exact `a662e707…` | 278,189,195 bytes / 1,724 files | `55a2552c2841b591453567b6ed1f3baa31c7c4a0da28e76ad55765988471502b` |
| Frozen V2 release candidate | `skyyrose-flagship-2/`; SkyyRose Flagship 2 v2.5.0 | 176,928,301 bytes / 599 files | `47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16` |

The bounded V2 audit found a single V2 root, no symlinks or V1 paths, and no
parent or sibling runtime dependency. V2 bytes are unchanged. The clean-source
V1 package completed at **12:55:56 UTC**, with offline checks completed at
**12:57:11 UTC**. It retains all 64 literal bootstrap includes and all 1,598
eligible source files under `inc`, `assets`, and `data`; its 165 PHP files pass
syntax checks. Archive files match the clean source, with no symlinks, parent
`Template` header, or detected PHP references to the sibling theme.

V1 package construction and offline checks are bound by
`separate-theme-packaging/review-packet-7f1104ed.json` in the local execution
evidence directory, SHA-256
`f4e89e3bcb83b61b205a8bac4ffd08fbc6ec8edbc6f91b6b8f71cd7d58c86f21`.
These checks do not execute V1's bootstrap inside WordPress or establish
browser/runtime acceptance. V1 is a separate source candidate, not an assumed
copy of the current live theme or an equivalent rollback.

An authenticated read at **12:49:09 UTC** found distinct, non-symlink installed
theme directories and inspected `style.css`, `functions.php`, and `index.php`
in each. Its identity comparison is:

| Identity | Theme folder | Theme header | Meaning |
| --- | --- | --- | --- |
| Canonical source V1 at `a662e707…` | `skyyrose-flagship` | SkyyRose 2.2.4; text domain `skyyrose` | Source for the separate V1 candidate |
| Current active installation | `skyyrose-flagship` | SkyyRose Flagship 2 v2.3.1; text domain `skyyrose-flagship-2` | Directory name does not establish source V1 equivalence |
| Reviewed inactive V2 installation | `skyyrose-flagship-2` | SkyyRose Flagship 2 v2.5.0; text domain `skyyrose-flagship-2` | Separate reviewed V2 release candidate |

The receipt is
`production-separate-theme-install-isolation-20261002t124909.json`, SHA-256
`2814d0e3bc7eaa71295d469b659e0770d5231d53c985f14ac5b1a57ddc1372ba`,
in the local execution evidence directory. This read covers the two roots and
three entry files each, **not their entire runtime dependency closure**. It
does not identify who installed the older header or when. The additive
`production-active-theme-entrypoint-baseline-comparison-20261002.json`
(SHA-256 `57158065867a9a0e4be7cef0105209730c15e59a632cc26ca6759296cb7428e5`)
independently confirms that all three active entry-file hashes match both the
earlier rollback baseline and preapplication read. This is a preexisting
identity mismatch, with no new drift in those three files; it does not establish
current whole-tree equality or a tested restore. Historical references
to “active V1” name the legacy directory/checkpoint; they must not be read as
proof of canonical V1 content. Preserve the actual captured installation for
recovery. Do not relabel or replace it, or call a new source V1 ZIP an equivalent
rollback, on the strength of a folder name.

## Scoped storefront release

The current cutover preserves the **33 published simple products**, their native
WooCommerce IDs and prices, full-payment checkout, unmanaged quantities, and
existing null shipping-date promises. Registry edition sizes do not establish
remaining inventory balances. No conversion to variations, size allocation,
stock cap, reservation lifecycle, or fulfillment-date promise is part of this
release.

The allowed candidate consists of the reviewed V2 theme and existing approved
media, the separately reviewed Search privacy MU extension, and ten owned new
pages. Existing merchant pages, WooCommerce cart/checkout/shop/account IDs,
shortcodes, options, customer records, orders, and payment behavior are
preserved. No product type, size, inventory, price, order, payment, or customer
mutation is included. API, dashboard, Fly, Governor, paid providers/generation,
unaccepted GLBs, mascot activation, database synchronization/import, demo
import, deletion, and backup pruning are outside the cutover.

The single editable product authority remains
[logo-registry.json](../logo-registry.json), resolving to the original theme's
[unified product registry](../wordpress-theme/skyyrose-flagship/data/logo-registry.json).
Use [get_product](../skyyrose/core/product.py) for complete reads. Corey's
latest maker specifications remain `FOUNDER_CONFIRMED`; missing facts remain
gaps. Native production configuration snapshots bind the acceptance tests to
existing store records and do not become an alternative product source.

## Execution and acceptance order

The reviewed [runbook](RUNBOOK.md) preserves this order. Source clearance,
inactive installation, draft preparation, and MU/cache readback are recorded at
this snapshot. The V1 Search/privacy checkpoint must pass with complete
observation capture before activation; later runtime states still require actual
evidence:

1. `CI_PASS` and `CLEAR_TO_EXECUTE_SCOPED_CUTOVER` are recorded for exact
   `a662e707…`. The sole writer must refresh immediate target/preimage/ownership
   guards before each mutation; clearance does not override a failed or unknown
   guard.
2. Install exact V2 while inactive and prepare only the ten owned drafts.
   Install the Search privacy MU extension and record actual object/global edge
   cache clearing. With V1 still active, require actual desktop and mobile
   Search checkpoint evidence before activation.
3. Guard all ten captured activation-option preimages; use native WordPress core
   theme switching and next-bootstrap handling/readback. Publish only the ten
   owned drafts, clear caches, and verify the exact 599 files, page mappings,
   unchanged native configuration, and prices. Record actual `DEPLOYED`
   evidence.
4. Require all six desktop/mobile × no-choice/Decline/Accept-then-revoke browser
   profiles, native cart/remove/Undo, Search/PDP, and checkout rendering.
   Checkout is render-only; do not create an order or initiate payment.
5. The coordinator and independent Astra reviewer inspect the actual required
   evidence and hashes before `PRODUCTION_ACCEPTED`. `DEPLOYED` alone is a
   separate state.

Any gating failure or unknown outcome stops the next mutation. Preserve the
journal, reconcile read-only, and use the reviewed ownership/preimage guarded
recovery. Never blindly retry an uncertain result. Recovery also requires actual
readback and public-flow evidence.

## Evidence access and freshness

Portable committed references:

- [Integration adoption manifest](../tasks/integration-release-20261001/adoption-manifest.json):
  adopted source, functional/package identities, bounded local tests, and
  remaining holds.
- [Frozen cutover candidate](../tasks/production-final-pass-20261001/cutover-candidate-manifest.json):
  target, artifacts, page/MU ownership, rollback boundaries, and historical
  state at freeze.
- [Page plan](../tasks/production-final-pass-20261001/evidence/production-v2-page-plan-final.json)
  and
  [page operator](../tasks/production-final-pass-20261001/apply_v2_pages.php):
  ten new routes and guarded prepare/publish/recovery source.
- [MU publisher](../tools/production-runtime/publish-search-privacy.php) and
  [extension](../tools/production-runtime/search-tracking-privacy.php):
  separately hashed Search correction.

New final-clearance and runtime receipts are retained in the coordinator's local
release packet. They are **not assumed to be committed with this
documentation**. On the current operator machine the packet is at
`/Users/theceo/.codex/worktrees/4035/DevSkyy/tasks/production-readiness-redteam-20261001/final-clearance/`,
with execution/readback records in
`/Users/theceo/.codex/worktrees/4035/DevSkyy/tasks/production-final-pass-20261001/evidence/`.
The final-clearance packet contains
`clear-to-execute-scoped-cutover-a662e707d.json`,
`precondition-hold-release-a662e707d.json`, `ci-pass-a662e707d.json`,
`ci-e2e-targeted-retry-dispatch-110435542010.json`,
`ci-e2e-targeted-retry-identity-110451737866.json`,
`acceptance-review-pass-receipt.json`,
`combined-release-evidence-manifest.json`, `acceptance-procedure.md`, and
`frozen-acceptance/acceptance-freeze-manifest.json`. The failed V1 checkpoint is
under
`frozen-acceptance/evidence/production-v2-acceptance/checkpoint-v1-live-20261001t1634/`,
including `results.json`, `evidence-manifest.json`, and desktop/mobile receipts.
The execution evidence folder contains the installation, draft/MU readbacks,
`production-mu-hosting-cache-clear.json`,
`production-mu-installed-cache-cleared-signal.json`, and
`production-search-query-encoding-diagnostic.json`,
`production-v1-query-corrected-checkpoint-attempt.json`, and
`production-v1-query-corrected-checkpoint-instrumentation-hold.json`. The
reviewed query-correction packet is retained under
`final-clearance/frozen-acceptance-query-correction/`, with the corrected run in
`evidence/production-v2-acceptance/checkpoint-v1-query-corrected-20261001t1647/`.
Its freeze/procedure identities and
`final-clearance/resume-v1-search-checkpoint-query-corrected.json` are
separately bound in the table above; their recorded PASS/review states do not
override the later instrumentation hold.

The subsequent native-capture packet is
`final-clearance/frozen-acceptance-v1-native/`. Its actual failed run is under
`evidence/production-v2-acceptance/checkpoint-v1-native-20261001t181458/`,
including per-profile receipts, `run-receipt.json`, `evidence-manifest.json`, and
`completion-seal.json`. The parent final-clearance folder contains
`v1-native-combined-source-review-pass.json`,
`v1-native-freeze-identity-review-pass.json`,
`v1-native-checkpoint-only-resume.json`, and
`ci-revalidated-before-v1-native.json`. The execution evidence folder retains
`production-v1-native-checkpoint-attempt.json`, the original
`production-v1-native-checkpoint-failure-classification.json`, and
`production-v1-native-preflight-20261001t192136.json`. Original failed-run
artifacts are preserved; later diagnoses must add evidence rather than rewrite
their recorded observations.

The October 2 passive diagnostic packet is
`final-clearance/frozen-native-search-diagnostic-d3667d04-4eb8-46c0-bdf9-d6f857cea2a3/`.
Its actual output is under
`evidence/production-v2-acceptance/local-v1-native-live-diagnostic/diagnostic-8baf50fb-b33e-4492-9f22-e55054621959/`
inside that frozen packet. The parent final-clearance directory retains
`native-search-diagnostic-actual-classification-d3667d04.json`,
`native-search-diagnostic-actual-classification-review-d3667d04.json`, and
`v2-explicit-shell-local-review-pass.json`. The execution evidence directory
retains the post-read
`production-v1-native-preflight-20261002t122351.json` and its `-raw.json`
companion. The reviewed homepage cache timestamp delta is
`final-clearance/native-diagnostic-fresh-preservation-cache-delta-20261002t120133.json`.
These are local receipts, not files implicitly included in this documentation
commit.

Obtain the current packet from the coordinator and verify its pinned identities
before execution; an unavailable receipt is an explicit gate gap.

The candidate manifest and adoption manifest preserve earlier pending statuses.
Their historical success or hold fields must be read with the later dated
coordinator receipt, without rewriting the originals. This snapshot does not
claim whole-platform E2E completion, accepted GLBs, durable live Governor
qualification, real payment acceptance, or skill-library compliance.
