# Efficient production — verified examples

**Coverage: `PARTIAL`.** The examples below verify local method-history and OS
admission behavior only. Provider authentication, paid execution, visual
approval, staging, production release, and the entire skill are not covered by
these tests.

## Correct: block an unadmitted operation at the OS boundary

**Request and context.** Prepare a source-bound creative operation in an
isolated local test environment. The fixture represents an operation; it is not
a real SKU, generated asset, authenticated provider session, staging site, or
production release. The inspected candidate checkout was
`/Users/theceo/.codex/worktrees/card-gap-integration/DevSkyy`, detached at HEAD
`a662e707d698a687d7d1d2efed3975b9aa7325b9`; the relevant code was dirty and
uncommitted.

**What to do.** Check the exact method binding and current admission at
preparation and again when claiming the operation. Stop before adding an
operation or touching provider capabilities, pricing, or spend when admission
is absent or stale. If a prior attempt failed, keep that history; permit only a
causally justified, bounded qualification until the exact candidate is
independently reviewed.

**What not to do.** Treat a passed status check or a new operation ID as
permission to skip admission. This can reach expensive or external work without
current method evidence. The correction is to enforce the shared policy at
every host entry point and before dispatch, not only in an agent instruction.

**Expected versus observed.** Expected: missing admission raises
`METHOD_ADMISSION_REQUIRED` before an operation row is created. Observed:
`test_sunburst_prepare_cannot_skip_embedded_policy` and
`test_sunburst_claim_rechecks_policy_after_preparation` passed; the governor
test also verifies admission occurs before provider capability calls, quotes,
and ledger reservation. A local offline run of the three cited test files
completed with exit code 0 and **31 passed** on 2026-10-04.

**Evidence.** `REPRODUCED_LOCAL`; source snapshot read and tested 2026-10-04.
Candidate HEAD and
primary sources: `skyyrose/elite_studio/creative/efficient_production.py`,
lines 238–275, SHA-256
`c711b5c9bc1a298ce279fb0fb192799edbe746c51b6fe5a1026a496c19f9332b`;
`tests/test_efficiency_host_seams.py`, lines 9–59, SHA-256
`312b6c0a26604052fcb431913d0049a00786765f35a362e6963df64d6ee05c94`;
and `tests/test_efficient_production.py`, lines 56–73, SHA-256
`74b431b1d606f1908b5f8807262f347d25ee2831164a76a236bcc996c9c0c916`.
Command from that checkout:

```text
/Users/theceo/DevSkyy/.venv/bin/python -m pytest -q -rA tests/test_efficient_production.py tests/test_efficiency_host_seams.py tests/test_sunburst_workflow_adoption.py
```

Authentication: `NOT_APPLICABLE`; these isolated tests used local fixtures and
transport spies. No generation, provider call, upload, spend, or deployment
occurred.

**Limits and refresh trigger.** The tested checkout was detached and dirty; this
receipt does not prove the code is integrated into the main checkout or any
deployed OS. Revalidate if the candidate is rebased, files or hashes change,
the policy boundary changes, or a live environment is in scope. This test does
not establish authentication, cost ceilings, one-network-attempt behavior,
visual fidelity, or release authority.

## Incorrect: rename a failed method to escape its history

**Request and context.** In the same synthetic local fixture, a method receives
a `REVISE` result. A caller then changes unrelated job, context, source, prompt,
and quality fields, gives the next attempt a new operation ID, and tries to
claim the method again.

**What not to do.** Assume those identifiers and settings make the failure
history irrelevant. The tested method key intentionally excludes them, so this
attempt is denied with `FAILED_METHOD`; changing quality is not evidence that
the cause was fixed.

**Correction.** Preserve the original failure and identify its cause. Record a
real changed control or source with evidence and expected effect. Admit that
single causal correction as `QUALIFICATION_ONLY`; do not use it for production
or bulk work. Retain the original negative event even if the qualification
passes.

**Expected versus observed.** Expected: the unrelated changes cannot clear the
failed method; only an evidenced causal correction can enter qualification,
which remains unable to authorize bulk production. Observed:
`test_unrelated_job_prompt_source_and_quality_cannot_reset_failure`,
`test_named_single_causal_correction_runs_qualification_only_and_retains_history`,
and `test_qualification_cannot_authorize_production` all passed in the 31-test
run recorded above. This is a reproduced synthetic test case, not a claim that
a live user or provider attempted the bypass.

**Evidence.** `REPRODUCED_LOCAL`, verified 2026-10-04. The prior sources,
checkout identity, command, hashes, and `NOT_APPLICABLE` authentication state
are recorded above. Test locators in `tests/test_efficient_production.py`:
lines 117–136, 67–73, and 214–265. The key construction is in
`skyyrose/elite_studio/creative/efficient_production.py`, lines 47–72.

**Limits and refresh trigger.** This proves only the tested local synthetic
policy behavior. It does not establish correct classification of every real
historical provider event. Refresh this example when the method-key fields,
admission states, persistence layer, or correction policy changes.
