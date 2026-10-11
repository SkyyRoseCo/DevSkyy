# Dirty-checkout content scope — 2026-10-10

This supplements the committed-branch recovery ledger. The 417 tracked dirty
paths and 42 untracked status entries are not a single additional feature. Most
of the tracked change volume is an older local copy-retirement pass; current
main already contains that intent and later repairs. Whole-file inequality must
not be interpreted as missing work.

## Pinned comparison and limits

- Primary checkout: `/Users/theceo/DevSkyy`, `feat/single-product-entry-point`,
  HEAD `ce34a5ab3a8bed704f13155d4c624eac770edd44`.
- Main comparison: `4dca24190d56f5709422f1e677580f74f00293ce`. Main advanced
  during this session; this report uses that explicit SHA.
- Tracked snapshot: 417 paths, 3,742 additions and 2,638 deletions against
  primary HEAD. The staged settings delta is only a missing final newline; the
  unstaged settings change removes the autocompaction override.
- Original untracked snapshot: 42 status entries expanded to 823 paths. Campaign
  work continued concurrently: a later census found 721 campaign paths versus
  669 initially. Those later files are outside the original denominator and need
  their own refreshed inventory before extraction.
- An initial recheck found all tracked working-content hashes unchanged. The
  independent final review found 416 of 417 unchanged: `.wolf/memory.md` changed
  concurrently after capture. Preserve its original inventory hash and refresh
  before extracting its latest bytes. No primary source edits, resets, staging,
  merges, deployment, paid calls or memory updates were performed by this audit.
- Text merge simulation is mechanical triage, not semantic proof or permission
  to copy files. HEAD was used as the base for the uncommitted delta only; it is
  not asserted to be the branch/main merge base.

## Major scopes and disposition

| Scope                               | Actual content difference                                                                                                                                                                                                                                             | Main / PR relationship                                                                                                                                                                                                                                                                                        | Disposition                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Retired brand copy                  | 349 tracked files contain edit blocks touching the retired slogan: 307 only those blocks and 42 mixed with other edits. Includes prompts, frontend, V1/V2 themes, skills, fixtures and historical text. Empty-tagline behavior is a code change, not just formatting. | Main already merged the broad no-tagline change in #1011 (`25127a621`) and hardened its CI guard in #1018 (`1da7995fb`). Local guard and several callers are older and weaker.                                                                                                                                | Already represented at the feature level; reconcile residual hunks against main. Do not create a duplicate 349-file PR or restore stale local versions. Reject incidental deletions and malformed copy described below.                                                                                                                        |
| Product-dimension comparison        | `skyyrose/core/product_truth.py` matches measurements by view and decoration instead of comparing every dimension together; `tests/test_product_dimension_scope.py` adds four regressions.                                                                            | Main lacks this function/test. #1051 changes the same source file for exterior-placement handling but does not contain `_dimension_regions`.                                                                                                                                                                  | Useful independent candidate: `fix(registry): compare dimensions by decoration`. Combine both behaviors through a hunk-level integration test. Preserve all founder measurements verbatim; add range, fraction and unknown-placement coverage before declaring ready.                                                                          |
| Provider test isolation             | An autouse DNS fixture in `tests/services/test_three_d_providers.py` avoids actual DNS while retaining the URL validator's other checks.                                                                                                                              | Absent from main and current #828 head `1527898531b3327f893c636ea3f7a4f8418aa9ac`.                                                                                                                                                                                                                            | Useful narrow candidate: `test(3d): isolate provider tests from DNS`. Keep production SSRF validation unchanged; verify no DNS-specific case is masked by the fixture.                                                                                                                                                                         |
| MCP environment bootstrap           | `devskyy_mcp.py` loads `.env.wordpress`, then `.env`, both without overriding existing environment values.                                                                                                                                                            | This delta is absent from main. #909 owns a related environment-loader concern; its `config/load_env.py` and this MCP bootstrap need a shared precedence contract.                                                                                                                                            | Candidate only after synthetic precedence tests. Never read or publish real env values. Keep `.augment/settings.json`'s absolute interpreter path local or replace it with a portable mechanism in a separate configuration decision.                                                                                                          |
| Express wallet rendering            | Local untracked PHP plus test remove one Stripe wallet renderer when WooPayments is eligible.                                                                                                                                                                         | Main already merged #1017 (`6e1ec9b9b`); #1037 at `464c3e082fade134418b742731c134107de4776f` carries that more complete version: WooPay eligibility, discovered callback priorities, separator removal and pay-order hook. #1051 also carries the newer V2 base. Local version is 2.5.0; these PRs use 2.5.1. | Superseded by main and the V2 owner. Do not introduce the local implementation as a new PR or copy whole `functions.php`. Local 18-check pass does not cover the newer cases or live payments.                                                                                                                                                 |
| Adversarial-planning CLI / mirrors  | Fail-closed Workflow adapter, local CLI, model/readiness/approval gates, fixtures, sync rollback and examples.                                                                                                                                                        | Main already contains this system through #1018, with additional hardening. For example, main permits an absent gitignored project mirror in a fresh clone; local sync code still requires it. Workflow adapter differences inspected are quote/wrapping changes.                                             | Retain main implementation. Review any remaining local semantic delta individually; no replacement PR for the older bundle. Example coverage remains partial and offline tests do not prove live model access.                                                                                                                                 |
| Fashion Theme Team distribution     | Plugin 0.4-to-0.5 version change, 43 untracked packaging/portable/engineering-reference files, product registry routing, V2 target and verified examples.                                                                                                             | Substantive additions relative to main's older vendored plugin. Canonical plugin source must own distribution changes.                                                                                                                                                                                        | Separate distribution sync scope, with canonical-source parity, portable/install checks and declared example coverage. Do not mix into commerce or registry PRs.                                                                                                                                                                               |
| Agent / skill / setup guidance      | Read-only architect role/model, efficient-production rewrite, founder-prose/redaction rules, CLAUDE/rules deduplication, Husky setup instructions, community hook setting and autocompaction preference.                                                              | Mixed: existing hook-path work belongs to #1030/#1053; these additional preferences and policy edits are not equivalent to those PRs. Current main also has newer guidance that full-file copying would lose.                                                                                                 | Two review scopes: engineering guidance/setup docs, and intentional agent/config preferences. Extract only local hunks. Keep memory/log history separately. Removing the checkout ESLint suppression is not useful cleanup as submitted.                                                                                                       |
| Old Jersey film retirement          | Deletes three old media binaries plus their build script; storyboard notes point to a replacement workflow. Local `REJECTED-OLD-FILM.md` records the founder's rejection.                                                                                             | Old MP4 and build script are still present in the pinned #1037 and #1051 heads; deletion must be reconciled with their newer consumers.                                                                                                                                                                       | Genuine outstanding V2 scope. Coordinate removal and all consumer references in the V2 owner. Preserve rejection evidence; do not reintroduce rejected footage. No replacement-film acceptance is implied.                                                                                                                                     |
| New campaign and private prototypes | Initially 669 campaign files; later 721 files totaling about 725.6 MiB. Ten Love Hurts prototype files, two hero-motion previews, source bindings and delivery/evidence packages.                                                                                     | Not covered by the recovered source-code PRs. The campaign manifest explicitly says deployment false and founder acceptance pending.                                                                                                                                                                          | Retain local/private candidate work. Scope only a reviewed delivery package and manifest when adoption is authorized; never bulk-stage raw outputs, review frames, attempts or third-party assets. Love Hurts prototype uses get_product but historical image-role approvals require current source reconciliation before storefront adoption. |
| Evidence, logs, local environment   | Brand investigation (26 files), readiness (33), task evidence (9), `.wolf` changes, local skill symlinks, `.tripo`, nested worktree and `ready.glb`.                                                                                                                  | History and machine state are not feature implementation. Some paths already exist in main with different formatting or later changes.                                                                                                                                                                        | Preserve; select only redacted, task-relevant evidence for an owning PR. No blanket deletion or snapshot commit. `scripts/check_anthropic_key.py` is byte-identical to #1012 at `2c349310b1791c9dbab17a4c60493b435c602853`; keep that existing owner.                                                                                          |

## Concrete regressions / stale content to keep out of recovery

1. `_prototype/homepage/sections/close.html` deletes three empty status elements
   while inline submit handlers still dereference `status.classList` and
   `status.textContent`. This creates a null dereference on form submit. Empty
   functional elements are not retired brand copy.
2. V2 `functions.php` deletes `[data-house-header-status]`;
   `house-of-roses-motion.js` still uses it for collection announcements. The
   guard avoids a crash but announcements disappear.
3. Local V2 `inc/seo-indexing.php` builds the homepage title as the site name
   plus a separator and an empty translation. Other local changes join unrelated
   words, including `collectionsThree` and `SkyyRoseOakland`.
4. Local Python creative prompts retain stray quote characters after the brand
   name; main's corresponding prompt text is already cleaner.
5. Local `scripts/check_retired_brand_copy.py` fails on two `.wolf` files.
   Main's newer guard has explicit occurrence accounting and additional
   normalization/validation. Do not overwrite it with the older local checker or
   erase history to make this snapshot green.
6. `frontend/app/api/checkout/route.ts` removes the require-import lint
   suppression but keeps `require('stripe')`, and introduces trailing
   whitespace. No useful behavior change is established.
7. Whole-file replacement of V2 `functions.php`, the planning CLI or settings
   would drop later work. The local 2.5.0 version must not replace the 2.5.1 V2
   PR candidate.

## Checks reproduced for scoping

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_product_dimension_scope.py tests/test_adversarial_planning_skill.py tests/services/test_three_d_providers.py -q -p no:cacheprovider --no-cov`:
  exit 0, all 124 collected tests pass. These are local/offline tests, not live
  provider or commerce validation.
- `php wordpress-theme/skyyrose-flagship-2/scripts/test-express-checkout.php`:
  18 renderer/fallback checks pass; implementation is nonetheless superseded by
  #1037.
- `python scripts/sync_product_registry.py --check`: PASS, CSV and all product
  dossiers match the registry.
- `python scripts/check_retired_brand_copy.py`: FAIL, two violating local
  history files. This is the older local checker, not a validation of main's
  newer checker.
- `git diff HEAD --check`: FAIL, trailing whitespace at checkout route line 9.
- Live PR heads and main history inspected with Git/gh. Key-checker file
  compared byte-for-byte with #1012; no credential health call was made.
- Creative prompt content inspection followed
  `/Users/theceo/.codex/creative-standards/imagery-prompting.md`; no prompts
  were submitted. Skill-content scoping followed
  `/Users/theceo/.codex/skill-standards/verified-examples.md`; this is not
  certification of the skill library.

## Safe extraction order

1. Freeze per-scope content hashes; refresh the growing campaign inventory only
   when that scope is extracted.
2. Keep main's merged retirement and planning-tool implementations. Recover only
   demonstrated missing behavior.
3. Prepare DNS isolation and dimension comparison as narrow source/test scopes;
   reconcile the dimension change with #1051 and expand boundary tests.
4. Resolve the MCP loader scope against #909 with synthetic environment tests.
5. Route wallet work and old-film retirement through the V2 owner without
   changing its founder merge hold.
6. Sync the canonical plugin distribution separately, then recover reviewed
   guidance hunks. Keep local preferences and historical logs out of those
   diffs.
7. Treat campaign adoption, storefront release and founder acceptance as
   separate subsequent decisions.

No source PR is declared merge-ready by this scoping report. The primary dirty
work remains intact.

Independent architect review checked inventory counts, settings layers and
content hashes. Its sole requested correction was the concurrent memory-file
drift note above; no further scope blocker was found. This review does not
certify the candidate code for merge.
