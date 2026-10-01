# Repository consolidation: safe local inventory

Stream 5 owns the inventory CLI, its fixture tests, and this evidence package.
The current execution scope permits local edits, tests, read-only discovery, and
scoped local commits. Push, merge, deployment, provider generation, live
mutation, deletion, disruptive relocation, and archive transfer are held.

The product registry, product projections, theme/build outputs, preorder,
Governor/analytics/Fly, and GLB/composite verification remain with their domain
owners. No product fact or binding is changed here. Corey is the founder/maker;
his exact latest corrections remain authoritative as `FOUNDER_CONFIRMED` in
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`. Complete product
reads use `from skyyrose.core.product import get_product`.

## Delivered behavior

`scripts/repository_inventory.py` emits JSON to stdout using Python's standard
library and Git supporting `--no-lazy-fetch` (verified Git 2.50.1). Its
immutable snapshot axis records the exact source commit, Git modes, blob/gitlink
sizes, classified paths, and candidate duplicate groups. Its independent
checkout axis distinguishes tracked, untracked, and ignored paths, missing
files, regular files, symlinks, directories, and gitlinks.

Default content analysis is off. Git reads its own configuration/index/ignore
metadata to enumerate paths; the CLI never invokes Git status or diff, which can
inspect tracked content and execute clean filters. Working-content cleanliness
is explicitly UNKNOWN (`dirty: null`); index changes and untracked path presence
are separate metadata indicators. Optional locks, fsmonitor, interactive prompts
and lazy fetching of partial-clone objects are disabled. Missing local Git
objects fail instead of contacting a remote. `--hash-worktree` hashes bounded
tracked regular files; untracked and ignored content remains unopened. Known
sensitive paths, credential stores, and agent configuration receive
metadata-only records and no content hashes or Git object IDs. This is a
conservative **path policy**, not a secret scanner: arbitrary secrets hidden in
otherwise ordinary source files cannot be identified without reading those
files. Never use this tool as proof that a repository contains no secrets.

Content inspection refuses symlinks at each directory component and at the file
itself. It detects identity/size/mtime/ctime changes during a read. Binary,
non-UTF-8, unsupported, oversized, inaccessible, generated/dependency, and
budget-exhausted paths have explicit skipped statuses. Gitlinks and nested Git
repositories remain metadata; their contents are not traversed.

`--candidate PATH` scans bounded tracked text for exact and case-folded literal
occurrences of that full repository-relative path. Edges contain file, line,
target, match type, and source/build/test/documentation layer; never source
snippets. Comments and examples can match. Basenames, import aliases, computed
paths, generated rewrites, CMS/database/CDN bindings and runtime consumers are
outside this graph. Zero matches does not establish that a file is unused.

All byte totals are logical/apparent bytes. Hardlinks, Git compression, retained
history, public URLs, independent editable originals and required packaging can
prevent any apparent duplicate from yielding removable storage. Purpose labels
are heuristic and ownership remains unresolved. No duplicate is approved for
removal. The measured reduction from this batch is **zero bytes**; its benefit
is repeatable discovery and explicit coverage rather than repository shrinkage.

## Reproduce

Run from the repository root on POSIX systems supporting descriptor-relative
opens and `O_NOFOLLOW` (verified here on macOS). Write full inventories outside
the checkout so the report does not inventory its own output. These local
commands need no authentication. The default exit code reports whether inventory
succeeded; `--require-complete-references` returns 1 for a partial or unrun
graph, and invalid/inaccessible inputs return 2. Even a complete literal scan is
not runtime acceptance or removal permission.

```sh
python3 scripts/repository_inventory.py \
  --snapshot 7892b797d838e67e62c862a6698a5b42b6dccaee \
  > /tmp/devskyy-base-inventory.json

python3 scripts/repository_inventory.py \
  --candidate scripts/scan_product_inventory.py \
  --candidate logo-registry.json \
  --candidate wordpress-theme/skyyrose-flagship-2/functions.php \
  > /tmp/devskyy-reference-inventory.json

python3 -m unittest discover -s tests/scripts -p test_repository_inventory.py -v
ruff check scripts/repository_inventory.py tests/scripts/test_repository_inventory.py
black --check scripts/repository_inventory.py tests/scripts/test_repository_inventory.py
isort --check-only scripts/repository_inventory.py tests/scripts/test_repository_inventory.py
python3 scripts/sync_product_registry.py --check
git diff --check
```

`--max-file-bytes` defaults to 2 MiB; `--max-total-bytes` defaults to 64 MiB per
analysis. Hash and reference analysis have independent budgets. Lists and keys
are sorted. Capture timestamps belong in receipts, outside stable report data.
The worktree census is non-atomic and changes with local artifacts.

## Current proposal reconciliation

Authenticated read-only GitHub discovery, captured on 2026-10-01 UTC as account
`SkyyRoseLLC`, refreshed
[PR #897](https://github.com/SkyyRoseCo/DevSkyy/pull/897) and current main.
Credentials were not printed or written to evidence.

- Main: `7892b797d838e67e62c862a6698a5b42b6dccaee`.
- Proposal head: `ffb59a068c5e04367884dfe90a0cb0892bc61b19`.
- PR state: OPEN; GitHub reported MERGEABLE at capture time. This supersedes the
  dated conflicted-state anchor, but does not establish green checks.
- Comparison: three commits ahead, 99 behind; merge base
  `4d6c5333f6bdc9a133464f54843b585dbcb77413`. The unique file is the 109-line
  `docs/architecture/monorepo-consolidation.md`, absent from the frozen base.
- Historical metrics describe `268e8fef8c865db1b9329b01e54ab14fd260a2ab`, not
  this base. The old 1,130-file / 683,989,940-byte archive estimate lacks an
  exact selection manifest. It remains unvalidated.
- Retain the useful recommendations: immutable source SHA, per-path manifests,
  consumer classification, byte-integrity checks and reversible approved
  batches. Proposed `apps/`, `packages/`, `services/` moves and the private
  archive target remain proposals. No replacement architecture or approved
  destination is established by this stream.
- Review comments and replies were read. The formatter-resolution finding
  `4002776154` has a later recorded reply describing a non-reproduction; this
  stream did not independently rerun that domain suite. The workflow-token
  finding `4002776166` remains a coordinator-owned discovery anchor. Review
  resolution and current-head hosted checks are separate from local tool tests.
- A refreshed list contains 23 open non-Dependabot PRs. All API comparisons have
  commits ahead of the frozen base. They are candidates for unique-delta review,
  not confirmed active/salvageable/superseded classifications. Seven comparisons
  reached the API's 300-file limit and need fuller diff evidence. None was
  closed, merged, renamed, or archived.

Raw capture files, including the full proposal and comments, remain in the local
ignored `.artifacts/consolidation-20261001/` directory. The maintained summary,
hashes, PR comparison inventory, and acceptance rows are in
[`evidence.json`](evidence.json). They do not convert the unmerged proposal into
an operating contract. A specifically named current Production OS file was not
located in this checkout; the supplied assignment and applicable `AGENTS.md` are
the verified execution contract, and that file-location gap remains explicit.

## Affected consumers and recovery

| Path/boundary                                   | Observed consumer                              | Verification and limit                                                  |
| ----------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------- |
| `scripts/repository_inventory.py`               | Direct documented CLI; fixture test import     | Real Git repositories and filesystem fixtures; no app imports changed   |
| `tests/scripts/test_repository_inventory.py`    | Standard-library unittest discovery            | Isolated fixtures, no root pytest bootstrap or live provider            |
| `docs/consolidation/*`                          | Reviewer/operator documentation                | JSON parsing, formatting, reference and diff checks                     |
| `Dockerfile`, `Dockerfile.api`, `.dockerignore` | Broad `COPY . .`; `!scripts/` source inclusion | Static inclusion inspected; containers not built, entrypoints unchanged |
| `pyproject.toml`                                | Explicit package discovery excludes `scripts`  | Inspection establishes CLI is not a new installed console entrypoint    |
| `.wolf` session records                         | Repository navigation/session protocol         | Narrow append/update only; no persistent global agent memory update     |
| V2, preorder, analytics, GLB, workflows         | Other streams' active files                    | No changes; runtime/build/release gates remain with owners              |

The local commit contains additions and session-record updates only. It needs no
migration or application rollback. Reverting the scoped commit removes the
CLI/docs/tests and reverses its log additions. Preserve ignored raw evidence
separately before any future worktree removal; Git cannot restore untracked or
ignored artifacts. No external archive, customer record, runtime asset, or
configuration was transferred or modified.

The disruptive-operation manifest is intentionally empty in `evidence.json`.
Before any future move/delete batch, the owner must supply old/new path, Git OID
and SHA-256, type/size, reason, all known consumers, ownership, intended Git
operation, stable public-route handling, specific approval, a materialized
restore destination, and a tested restore procedure. Missing reference or a
directory named archive grants no permission. Preservation is the default.

## Acceptance state

Safe local tooling is LOCAL CODE COMPLETE: its 20-test receipt, scoped checks
and independent reviews pass. Overall consolidation remains BLOCKED: artifact
ownership, complete runtime consumer evidence, disruptive-batch approval,
materialized restore tests, and measured reduction do not yet exist. MERGED,
RUNTIME ACCEPTED and RELEASED remain NOT RUN under current authority. The
machine ledger names the exact remaining owner/action for each requirement.

The documentation-only closing preservation and owner handoff is in
[`COORDINATOR-HANDOFF.md`](COORDINATOR-HANDOFF.md), with exact dependency,
bug-identity, raw-artifact and retention-target evidence in
[`closing-evidence.json`](closing-evidence.json). It does not expand integration
or disruptive-operation authority.

The later shared-ledger collision and stream 5's `bug-377` → `bug-383`
correction are recorded in
[`identity-correction.json`](identity-correction.json). It supersedes the
historical no-conflict disposition for current note integration; the original
dependency sets and raw evidence remain intact.

The current rolling checkpoint is
[`rolling-coordination.json`](rolling-coordination.json). It records later peer
ID collisions, integration ownership of the pending final mapping, exact adopted
tooling hashes and local evidence-copy verification. Historical receipts remain
intact; source adoption does not certify removal or restore readiness.
