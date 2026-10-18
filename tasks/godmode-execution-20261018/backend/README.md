# GOD MODE workstation execution host

> Historical review snapshot: describes the bounded runtime at the time of this
> review. The adjacent chat subsequently committed the fixes in `e2efee812` and
> added worker adapters; consult the current code and worker checkpoint for
> their current qualification status.

This is a real bounded executor for source-inspection and offline Fashion
verifier workflows. It is not a production media agent, provider proxy, remote
shell, or distributed cloud queue. The dashboard transport calls this
authenticated service. It has no credential-loading or paid generation
capability.

## Run the host

From the selected current DevSkyy checkout, using its installed dependencies:

```sh
export GOD_MODE_RUNTIME_PROFILE=workstation
export GOD_MODE_DB_PATH=/Users/theceo/Library/Application\ Support/DevSkyy/god-mode/runtime.sqlite
.venv/bin/python -m uvicorn skyyrose.godmode_runtime.api:create_app --factory --host 127.0.0.1 --port 8011
```

The backend JWT signing configuration must match the authenticated dashboard
transport. No signing material belongs in this document or browser bundle.
Existing `security.jwt_oauth2_auth.get_current_user` validates the bearer token;
server-verified roles and subject own every action. `developer`, `admin`,
`super_admin` may operate; only admin/super_admin approve runs, promote memory,
and independently review. Anonymous access returns401; roleless/read-only
access403. Cross-actor run IDs are hidden from non-owner operators.

`GOD_MODE_FASHION_ROOT` is an operator-controlled canonical package root
override, never a browser argument. Default is
`/Users/theceo/plugins/fashion-theme-team`. `GOD_MODE_DB_PATH` must be absolute.
Missing workstation profile or database configuration fails503; deployed
staging/production ENVIRONMENT fails503. This is intentionally one workstation
execution host with SQLite WAL, not a qualified multiworker database system.
Start with one uvicorn worker. No auto-replay: interrupted work requires a newly
created/approved run.

## Actual execution contract

- POST `/api/v1/god-mode/runs`: fixed SkyyRose project, one allowlisted
  workflow, idempotency key. No command/path/actor/model injection fields.
- Plan hashes bind workflow steps, timeout, canonical
  skill/registry/canon/executor source hashes, and exact owner-accepted memory
  snapshot.
- Explicit owner approval binds the exact plan and expires after15minutes. Any
  source or accepted-memory drift invalidates it. A transactional state claim
  serializes the entire workstation executor and prevents duplicate launch;
  approval cannot be reused after completion/cancellation.
- `source-audit` actually reads the current migrated skills and writes a durable
  assignment artifact with skill headings/hashes and scope. Its method is
  explicitly deterministic inspection, not an LLM or specialist-agent execution
  claim.
- `campaign-readiness` additionally runs actual
  `sync_product_registry.py --check` and `workflow_guard.py verify`
  subprocesses.
- `fashion-verification` additionally runs actual canonical
  `verify-skyyrose-migration.py`.
- Fixed Python commands use no shell, a sanitized environment, temporary HOME,
  per-step90second wall limit,1MB output bound and16KB redacted receipt.
  Cancellation is polled every100ms and kills the owned process group, including
  descendants. Children are cleaned even if their parent already exited.
- Durable events/steps/artifact digests survive process restart. Expired RUNNING
  leases become INTERRUPTED, never silently requeued. Every late
  receipt/error/finalization checks active execution state, so
  recovered/cancelled workers cannot overwrite the record.
- Independent review binds exact plan+artifact hash and requires a different
  authenticated human from submitter/approver/executor. It remains separate from
  mechanical success, founder acceptance, media quality, deployment and release.
  An approval or review never authorizes provider spending.

GET `/status`, `/workflows`, `/runs`, `/runs/{id}` expose sanitized operational
state. POST run `/approve`, `/execute`, `/cancel` performs real state
transitions. POST `/review` records independent human observations. Execution is
synchronous bounded work; UI may inspect/cancel through a second request. A
client disconnect does not imply cancellation; use `/cancel`.

## Durable project memory

POST `/memory` records decision/observation/handoff text with provenance and
authenticated author. New records are UNTRUSTED. Private drafts are visible to
their author and owners; only explicit owner promotion makes a record shared
OWNER_ACCEPTED context. Revisions append records and retain superseded history;
developers cannot revise another actor's note or a promoted shared note.
Credentials matching common patterns are rejected; this is hygiene, not complete
data-loss prevention. Do not enter secrets.

Retrieval is literal bounded search scoped to the configured SkyyRose project.
Retrieved text is data, never executable instructions or approval.
Owner-accepted memory is frozen into run plans; changes invalidate pending
approvals. Memory cannot change `get_product(sku)`, the product registry,
founder facts, repository instructions or permissions. No changes are made to
the human `.wolf/memory.md` or global model memory by this service.

Daily per-actor quotas:100 run submissions and100 memory records; response
limits50 runs and100 notes. Same idempotency key+actor+workflow returns the same
run without creating side effects. Cross-actor key collisions return409.

Run visibility is applied before the 50-result limit so other operators cannot
crowd a user's runs out of the list. Single-run polling also recovers expired
leases. A cancellation committed before terminal finalization wins over success,
including the interval after the last process poll.

The 100-note limit applies only to display/search results. Approval snapshots
contain every current owner-accepted memory, with deterministic ordering.
Accepted descendants supersede accepted ancestors across intermediate drafts;
promotion rejects competing branches and promotion of an obsolete ancestor.
Historical records remain available, while execution receives only the current
accepted revision of each lineage.

## Evidence and remaining gaps

Hard-crash process cleanup is not qualified. Cooperative cancellation and normal
executor cleanup terminate the owned process group, and durable recovery
prevents automatic replay and late state writes. If the execution host itself is
killed with SIGKILL, cleanup code cannot run and a child process can survive
until it exits. The existing child-process test covers the verifier parent
exiting while the runtime remains alive; it does not establish host-death
cleanup. Keep this runtime restricted to its fixed read-only checks. Qualify a
supervisor/watchdog and actual active-host-crash behavior before enabling model
workers, writes, provider jobs or other effects. The restart integration receipt
establishes a graceful stop/start with persistent records, not hard-crash
cleanup or failover.

`tests/test_godmode_runtime.py` contains reproduced local positive/negative
tests for actual fixed-script execution, exact-hash approval, source/memory
drift, reuse denial, cancellation, single executor claims, recovery fencing,
orphan cleanup, independent review, memory trust/isolation, role denials and
body identity injection. Authentication here is synthetic local JWT-dependency
tests, not a deployed account claim. See parent's integration receipts for live
host/browser qualification.

Correct example: an owner approves a source-bound campaign-readiness run; the
executor launches the two actual fixed verifier scripts, records exit/output
digests, then consumes approval. Incorrect tested case: rerun with the same
approval or changed canon; the service rejects it409 and source drift revokes
the run. The correction is create a fresh plan and obtain approval of that exact
plan. Mechanical success never proves garment pixels or creative acceptance.

Read-only Codex/other agent mission execution is UNQUALIFIED because the current
CLI configuration can inherit unrestricted project tools and broad filesystem
reads. There is no agent adapter behind a display-only capability flag. Media
generation, deployment, spending and publication remain unavailable. SQLite
durability/backups and workstation availability are operator responsibilities;
no cloud failover qualification is claimed.
