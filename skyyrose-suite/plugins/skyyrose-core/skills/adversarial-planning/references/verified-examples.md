# Adversarial Planning: Verified Examples

Coverage for the current implementation: PARTIAL. Local CLI control-flow,
manifest round-tripping, sync rollback, and reconciliation cases are tested
with mocks; no authenticated model-to-model call or real execution review has
been run. The Workflow adapter is deliberately disabled pending trusted
runtime readiness and durable one-time execution state. Authentication for
the mocked examples below is NOT_APPLICABLE. Never treat a mock as proof of
provider availability, paid-call success, media approval, or deployment.

## Correct: plan from R5 without clearing or creating imagery

**Request and context:** Prepare a source-bound remediation plan for the 37 held
media roles in R5. The target is local planning only; image generation,
provider calls, staging changes, and release acceptance are out of scope.

**What to do:** Preserve the 81-role denominator, 44 currently covered roles,
and 37 gated roles. Keep LH-002 and LH-005 as explicit gated card/PDP bindings.
For any Love Hurts imagery plan, resolve their product facts through the
canonical registry and preserve the founder-supplied artwork path and hash
before source selection. Return a remediation plan; do not claim that any
missing media is approved.

**What not to do:** Treat a model-generated image, dashboard count, or mock
workflow result as clearing a role. Correct by keeping role reconciliation,
source fidelity, visual approval, and release acceptance as separate gates.

**Expected versus observed:** Expected status is PLAN_READY only when the
independent mock challenger has no blocking objection. The reproduced test
asserts that the task preserves all 37 gated roles and the Love Hurts source
binding, never calls execute, and retains provider/media/deployment counts at
zero. It does not establish a real model response or media review.

**Evidence:**

- SOURCE_VERIFIED from the on-disk R5 record at
  /Users/theceo/.codex/worktrees/card-gap-integration/DevSkyy/tasks/v2-creative-review/v2-imagery-reset-20261002/next-phases-20261003/source-certification/reconciliation-r5-20261004/ROLE-CENSUS-RECONCILIATION-R5.json,
  SHA-256 ddc910227f3e4db480ca24d7f6e683ff8576706044f02e4735476f8d5c2f2542.
  Locators: revision, classification, census, verification,
  independent_code_review, and release_state. Verified 2026-10-04.
- SOURCE_VERIFIED from the founder artwork adoption record at
  /Users/theceo/.codex/worktrees/card-gap-integration/DevSkyy/tasks/v2-creative-review/v2-imagery-reset-20261002/next-phases-20261003/source-association/love-hurts-founder-artwork-20261003/ACTUAL-FOUNDER-ARTWORK-ADOPTION-R1.json,
  SHA-256 fa6089d6ed29f869a916e268292c078723d59c8d492f28a3b0d5bacdbc7b5f07.
  Locators: founder_verbatim, affected_skus, source, and changes. Its recorded
  artwork SHA-256 is a9b96c60811a92b34dd8b5700317603a16f0976ea863c5d255a4762935d363a8.
- REPRODUCED_LOCAL when the test suite passes:
  pytest -q tests/test_adversarial_planning_skill.py::test_r5_mocked_plan_preserves_all_37_gates_and_love_hurts_artwork_source.
  The minimized input is
  tests/fixtures/adversarial_planning/r5_reconciliation.json; its source hash
  pins the original record. The test uses a mock runner and makes no provider
  call.
- The later founder prose repair for LH-005 is recorded at
  /Users/theceo/.codex/worktrees/card-gap-integration/DevSkyy/tasks/v2-creative-review/v2-imagery-reset-20261002/next-phases-20261003/source-association/love-hurts-founder-artwork-20261003/ACTUAL-FOUNDER-ARTWORK-PROSE-REPAIR-R2.json,
  SHA-256 757dce7d3cc260556f917bfca00cd8e214176956b816c01f170ec41c30974632.
  Locators: changes, changed_product, and independent_review. This is a
  historical source-association receipt, not proof that any new visual was
  generated or approved.

**Authentication:** NOT_APPLICABLE for the reproduced mock test. A separate
HISTORICAL_OBSERVED CLI status check on 2026-10-04 reported Claude Code
loggedIn=true and auth method claude.ai; email and organization fields were
not retained. The permitted scope was claude auth status --json only. No model
request was made during that status check. This does not verify access for a
future request or another account.

The redacted receipt is
references/evidence/cli-preflight-20261004.json. Its authentication, versions,
effective_codex_model, codex_doctor, and Claude model-alias fields record the
actual allowlisted output of the read-only preflight and `claude --help`; the
help confirms `fable` is accepted as a `--model` alias. The receipt contains no
email, organization ID, token, or model response.

**Limits and refresh trigger:** Recheck the R5 SHA and current registry before
using this fixture in a future plan. R5 explicitly classifies itself as a
deterministic source reconciliation, not media review or release. A changed
source hash, product authority record, CLI version, account, project trust,
endpoint, or doctor result requires fresh evidence.

## Correct: separate preflight from paid planning

**Request and context:** A repository task selects the local CLI with
plan_only. Authentication and provider checks must pass before the first model
request.

**What to do:** Run prepare, display its manifest, then ask for exact lowercase
y bound to the displayed manifest_sha256. Recheck the task hash,
configuration, authentication, readiness, and ten-minute expiry immediately
before calling a model. The manifest lists the provider, model source,
three-round cap, maximum calls, and cost/quota as unknown where unavailable.

**What not to do:** Accept a stale hash, uppercase Y, changed task, expired
manifest, or substituted Codex model. Correct by returning BLOCKED and
preparing a new manifest.

**Expected versus observed:** The required unit test covers lowercase y,
wrong hash, modified task, changed preflight, expiry, and call counts. It is a
local gate test; no paid model request was made by the test.

**Evidence:** REPRODUCED_LOCAL after passing
pytest -q tests/test_adversarial_planning_skill.py::test_manifest_is_mode_bound_and_requires_fresh_hash_bound_y.
The implementation is in scripts/adversarial_planning_cli.py, functions
prepare_manifest and validate_approval.

**Authentication:** NOT_APPLICABLE to the unit test. A live account check
must be repeated for every run; the historical Claude CLI status observation
above does not authorize or prove model access.

**Limits and refresh trigger:** Any change to either provider, model source,
task, selected mode, call count, local checkout, or auth/readiness state
invalidates the approval.

## Correct: resolve Codex provider routing from supported config scopes

**Request and context:** A trusted repository contains its own `.codex/config.toml`,
and the user config may contain a custom OpenAI endpoint. The runner must prove
that the challenger uses the intended OpenAI service before a paid call.

**What to do:** Resolve model preferences using Codex's documented precedence,
but exclude project-local `model_provider`, `model_providers`, and
`openai_base_url` from provider routing because Codex ignores those keys at the
project scope. Validate the applicable system/user `openai_base_url` and
`model_providers.openai.base_url`. Stop on a non-OpenAI provider, malformed
route, or unverified endpoint.

**What not to do:** Shallow-merge the project `model_providers` table over the
user table and then report `OpenAI Codex CLI`; an unrelated project provider
entry can conceal an unverified user endpoint. Correct by resolving provider
routing only from the documented machine/user layers.

**Evidence:** SOURCE_VERIFIED from the official [Codex configuration
basics](https://developers.openai.com/codex/config-basic) and [configuration
reference](https://developers.openai.com/codex/config-reference), checked
2026-10-04. The reference identifies project-level provider-routing keys that
Codex ignores and documents `openai_base_url` as the built-in OpenAI endpoint
override. REPRODUCED_LOCAL after passing:

- `pytest -q tests/test_adversarial_planning_skill.py::test_project_provider_table_cannot_mask_user_openai_endpoint`
- `pytest -q tests/test_adversarial_planning_skill.py::test_codex_openai_base_url_override_is_validated`
- `pytest -q tests/test_adversarial_planning_skill.py::test_project_provider_setting_cannot_mask_user_non_openai_provider`
- `pytest -q tests/test_adversarial_planning_skill.py::test_project_provider_routes_are_ignored_when_user_uses_default_openai`

These tests use temporary TOML and make no provider calls.

**Authentication:** NOT_APPLICABLE to these offline tests. Their pass status
does not authenticate either provider.

**Limits and refresh trigger:** The read-only resolver covers documented
system/user TOML and the trusted-project status. It does not establish a future
account, paid call, or remote managed route. If Codex changes its config
precedence or route diagnostics, block and update this check from fresh
official documentation and observed CLI output.

## Incorrect, illustrative: treat every doctor failure as harmless

**Request and context:** A noninteractive process runs under TERM=dumb, and
Codex doctor reports a terminal color/cursor limitation alongside healthy
authentication, configuration, installation, network, and runtime checks.

**What not to do:** Ignore every failed doctor status because this known
terminal warning is cosmetic, or accept any diagnostic that merely mentions a
cursor, color, or terminal. That could allow an authentication or provider
failure to reach a paid request.

**Correction and reason:** Ignore only the single terminal.env failure when
all critical checks are healthy, TERM is dumb, the invocation is
noninteractive, and the diagnostic exactly matches the observed
TERM=dumb color/cursor warning. Block on any extra detail, duplicate identity,
other, missing, or unknown failure.

**Expected versus observed:** ILLUSTRATIVE_UNEXECUTED policy example. Local
test cases reproduce the terminal-only exception and verify that real,
unknown, interactive, and non-dumb failures block:
pytest -q tests/test_adversarial_planning_skill.py::test_doctor_allows_only_the_noninteractive_dumb_terminal_exception
and pytest -q tests/test_adversarial_planning_skill.py::test_doctor_blocks_real_and_unknown_failures.

**Evidence:** SOURCE_VERIFIED by this skill's readiness policy and
REPRODUCED_LOCAL by the listed tests, when they pass. No external request is
made by those tests.

**Authentication:** NOT_APPLICABLE for local tests.

**Limits and refresh trigger:** If Codex changes the doctor JSON schema or
critical check identifiers, fail closed and update the classifier only after
inspecting fresh official output.

## Incorrect, illustrative: force execution on round three

**Request and context:** Claude and Codex still disagree about a source
assumption after the third challenge.

**What not to do:** Declare a winner and execute because the round cap was
reached. The cap limits debate; it does not prove the plan is safe.

**Correction and reason:** Return NEEDS_REVIEW with the unresolved objection
and the evidence or decision needed next. Execution is allowed only after
convergence, a plan_and_execute manifest, and its typed approval.

**Expected versus observed:** ILLUSTRATIVE_UNEXECUTED negative case. The
reproduced test verifies exactly three rounds, NEEDS_REVIEW, and zero
execution calls:
pytest -q tests/test_adversarial_planning_skill.py::test_unresolved_debate_stops_at_three_and_never_executes.

**Evidence:** REPRODUCED_LOCAL by that mock-runner test when it passes. No
production task was executed.

**Authentication:** NOT_APPLICABLE for the local mock.

**Limits and refresh trigger:** The maximum remains three rounds. Do not
increase it to force agreement.
