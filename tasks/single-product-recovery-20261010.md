# Single-product branch scoped recovery — 2026-10-10

Source: `feat/single-product-entry-point` at
`1693beec2336ad1fc5a68c2b5fa7dee9aaad3fdf`. Main baseline:
`388f618e408fba59e2ce11a4575e6f88acf202d9`. Primary checkout remains
`feat/single-product-entry-point` at `ce34a5ab3a8bed704f13155d4c624eac770edd44`;
its 417 tracked changes and 42 untracked entries were preserved. Recovery used a
separate sparse worktree. No main merge, deployment, generation or paid provider
call was performed.

The [186-path inventory](single-product-recovery-inventory-20261010.json)
assigns every path from the original investigation to a scoped PR, current-main
retention, or an explicit review hold. Path overlap routes ownership; it is not
a claim that older source bytes should replace a newer PR implementation. Held
work remains on the source branch and is not described as finished or
merge-ready.

## New scoped PRs

| PR                                                       | Scope                                                | Evidence and limits                                                                                                                                                                                                                            |
| -------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [#1052](https://github.com/SkyyRoseCo/DevSkyy/pull/1052) | Fail-closed GLB QC and packaged harness              | 79 focused tests; architect source review passed. No live browser render qualification.                                                                                                                                                        |
| [#1053](https://github.com/SkyyRoseCo/DevSkyy/pull/1053) | Python cleanup limited to the edited content         | Stacked on #1030. 53 passed, one existing PHPCS-tooling skip. Architect reproduced and reviewed a fix for intervening-edit loss. Last-moment bytes/identity comparison is not filesystem compare-and-swap.                                     |
| [#1054](https://github.com/SkyyRoseCo/DevSkyy/pull/1054) | Standalone Blender worker and isolated router        | **Draft.** 85 offline tests; one real-Blender integration test deselected. Router is admin-only and unmounted; no compose activation. Redis delivery, full-job leases/backoff, Docker, rendering and artifact-store qualification remain open. |
| [#1055](https://github.com/SkyyRoseCo/DevSkyy/pull/1055) | Registry-driven web GLB builder and pinned installer | 26 offline tests; installer syntax and three official release digests checked. Fixes repeated-run overwrite bypass and unexpected-error summary crash. No binary installation or product-model publication.                                    |
| [#1056](https://github.com/SkyyRoseCo/DevSkyy/pull/1056) | Experimental HTTP session adapter                    | **Draft.** 32 mocked tests. No application activation; provider, account and billing contracts remain unqualified. Unsupported zero-cost/access interpretations were removed.                                                                  |
| [#1058](https://github.com/SkyyRoseCo/DevSkyy/pull/1058) | Catalog CI watch paths                               | Four manifest/projection paths asserted in both push and PR filters. Job behavior and dependency pins unchanged.                                                                                                                               |

Normal formatter, mypy, fast-unit and freshness hooks passed on the Python
recovery commits. The catalog `sync_product_registry.py --check` passed on
current main. Source changes do not alter founder product specifications, media
bindings, production permissions or V2 release holds.

## Existing scopes synchronized

PRs [#1029](https://github.com/SkyyRoseCo/DevSkyy/pull/1029),
[#1030](https://github.com/SkyyRoseCo/DevSkyy/pull/1030),
[#1031](https://github.com/SkyyRoseCo/DevSkyy/pull/1031),
[#1034](https://github.com/SkyyRoseCo/DevSkyy/pull/1034),
[#1041](https://github.com/SkyyRoseCo/DevSkyy/pull/1041),
[#1047](https://github.com/SkyyRoseCo/DevSkyy/pull/1047) and
[#1051](https://github.com/SkyyRoseCo/DevSkyy/pull/1051) were updated with main
using expected-head checks, without force-pushing or switching occupied
worktrees. #1053 was updated after its #1030 parent moved.

The V2 port owner completed the in-progress merge and left a clean worktree
before the final server-side update brought in main's dependency-only #1045
change. The current V2 pinned build inputs did not include those five changed
files. This synchronization does not clear the V2 **HOLD — founder merges**
rule. #1037 remains the capture/history parent represented by #1051 and was not
duplicated or rewritten.

At the recorded check, these scoped heads were zero commits behind their
declared base; #1053's base is #1030, which contains main. CI was still running
or queued. Earlier bot startup failures are not source-test failures, and no
green merge claim is made. Always refresh the exact head, reviews and required
checks before merging.

## Retained and held work

- Preserve current main's newer founder corrections, dependency remediation and
  source authority. Never restore the omnibus registry or lockfiles wholesale.
- Keep the V1 PDP 3D gallery/enqueue/CSS work together for a dedicated PHP,
  token/build, desktop/mobile and commerce review. Do not conflate it with V2.
- Reconcile Comfy contracts, asset receipts, source paths, hashes and generated
  scene authority together. No historical approval is converted into current
  creative acceptance. The MPS guard needs malformed-header failure handling
  before adoption.
- Replace GLB triage's filename-prefix reference guesses with explicit registry
  bindings before its Keep/Reject controls are used.
- Keep Auggie hooks and context adapters inactive pending safety/contract tests.
  The historical hooks allow malformed/paid events, and the context adapter can
  index obsolete product-fact sources.
- Repair the multi-agent product-copy tool before adopting instructions that
  claim it reads complete current product records. The existing tool still reads
  retired override files.
- Preserve pinned main document bytes and current local instructions. Four
  compared Constitution JSON files were semantically equal despite formatting
  changes; the remaining prose differences require a separate pinned-document
  review.
- Consolidate direct-command formatter-ignore coverage separately with existing
  main ownership checks and #1031. Preserve legacy hook compatibility rather
  than replaying tests that expect the old executable to be deleted.

No source branch or existing PR was deleted. The recovery worktree's untracked
`.venv`, `.husky/_` links and `ready.glb` were excluded from every commit; the
last file's originating run was not established and it was preserved.

## Exact-head synchronization snapshot

Checked at `2026-10-11T00:29:29+00:00` against main
`388f618e408fba59e2ce11a4575e6f88acf202d9`. These are observations, not promises
about later CI or branch changes.

| PR    | Observed head                              | Base                         | Behind base | Pending checks | Failed checks |
| ----- | ------------------------------------------ | ---------------------------- | ----------- | -------------- | ------------- |
| #1029 | `d4452b8f1862b6abc874e94add8d907f6827a3f8` | `main`                       | 0           | 7              | None observed |
| #1030 | `fb09ad4384a72f6e946d7050b39c03b67460aae2` | `main`                       | 0           | 14             | None observed |
| #1031 | `109bef04e3130b22721dca17300b04001f3602ec` | `main`                       | 0           | 6              | None observed |
| #1034 | `9a430ee8da885f98a775be0b619a54c8e4103995` | `main`                       | 0           | 15             | None observed |
| #1041 | `17b8052c890fd048a717afd318f23ebbec84da58` | `main`                       | 0           | 14             | None observed |
| #1047 | `2a2454e82d3d73ba29c641d0941a6bdb15b6872e` | `main`                       | 0           | 10             | None observed |
| #1051 | `8bcc3b274ed509353765cde8ebce8064698ad30b` | `main`                       | 0           | 13             | None observed |
| #1052 | `c2f01941aace92bec2d8a403b0ae158737b99b18` | `main`                       | 0           | 8              | None observed |
| #1053 | `a975d6f31abb147e9784c51e51fe4354c42a02f6` | `fix/hook-paths-project-dir` | 0           | 3              | None observed |
| #1054 | `484d6ac4ae89d3c79b96cd87cc690eba8ffaf0c6` | `main`                       | 0           | 11             | None observed |
| #1055 | `87c2c0428610e2682019b939acd20b1076f3458f` | `main`                       | 0           | 15             | None observed |
| #1056 | `b5aadf507440db58d4af320a179a9eda316106e3` | `main`                       | 0           | 7              | None observed |
| #1058 | `114486dae380beb4d48b12b090e6de0911c11bbf` | `main`                       | 0           | 18             | None observed |
