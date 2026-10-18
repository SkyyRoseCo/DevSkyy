# Current-authorized provider diagnosis and qualification

Current owner instruction (2026-10-18): “keep going and find the cause of the
Claude provider error. finish the live Opus 5.5 to Codex workflow test, keep
approvals and memory in GOD MODE, and keep production off until it passes.
commit and push the fix.”

The previous attempts and unknown usage remain recorded. A fresh diagnostic run
uses this current instruction, an exact immutable plan and a run-specific,
one-use additional-qualification authorization in GOD MODE. No daily counters
are reset and no ambiguous usage is refunded. No public/browser endpoint grants
this extension. Each grant binds the plan and adapter contract, expires with
approval, allows one run/two engine stages and a $1 Claude SDK budget. Codex
uses the existing ChatGPT allowance, without API-key fallback. No automatic
retries.

1. Inspect installed SDK and existing failure receipts, preserve
   source/permission restrictions and latest owner-selected models.
2. Reproduce locally where possible. Perform one explicitly approved diagnostic
   run with the current safe error/phase reporting. Persist every actual result.
3. Fix the evidenced cause and add regression coverage. Freeze source and model
   bindings before a new separately approved test.
4. Produce schema-valid Claude output covering all 15 canonical preorder SKUs;
   independently review its immutable hash with Codex. FAIL holds readiness.
5. Keep memory promotion, human review, production and release separate.
   Production remains off even after a bounded analysis test passes, until owner
   release.
6. Verify and push scoped implementation/evidence changes. Do not include
   unrelated shared-checkout work or credentials in the commit.

Correct example (SOURCE_VERIFIED): execute checks current owner approval, source
and accepted-memory drift; a new authorization is bound to the exact run/plan
and consumed transactionally. Source: skyyrose/godmode_runtime/service.py,
2026-10-18. Incorrect example (ILLUSTRATIVE_UNEXECUTED): clear prior
reservations or mark a model result as owner acceptance. Correction: retain
history, require the fresh run-specific grant and preserve the distinct owner
gates.

Authentication: actual model qualification uses current-chat service
authorization and credential-bound adapters, not a forged owner login. Record
actual provider results; model presence or metadata alone is not successful
completion evidence.

## Fresh owner continuation after limit update

On 2026-10-18 the owner confirmed the API limit was updated and explicitly
authorized completing the live Opus 5.5 to Codex test, retaining GOD MODE
approvals/memory and production OFF. Create a new run with this instruction, a
fresh expiring exact-plan grant and distinct idempotency key. Do not replay the
disabled historical harness or old approval.

### Actual first live review and correction

The limit-cleared run produced a valid Opus artifact, but the independent Codex
review returned FAIL for unsupported source claims. Preserve both artifacts.
Tighten the worker's source-location and field-presence rules and explicitly
bind the preorder-only census. Missing/null/explicit-gap distinctions, unknown
current correction status, and unverified pixel evidence must not be conflated.
Keep the reviewer unchanged and require a fresh plan/grant after these source
changes.

### Repeated-failure root cause

Independent fixer/architect review identified a task-scoping bug: the generic
worker instruction requested collection/product coverage even for a
skill-workflow audit, leading to unsolicited inaccurate catalog claims. Use an
explicit skill-audit instruction with one source-located finding for each
required skill; retain the complete product census and exact SKU coverage. The
packet names the eight targets and the host rejects omitted/duplicate skill
findings. Increase reasoning effort to medium within the same 4,096-token/$1
budget. Keep Codex's criteria unchanged.

The medium-effort attempt did not return valid JSON; its cause is not
established by the retained fixed error code. Add explicit
stop_reason=max_tokens failure classification, request concise eight-skill
findings, and permit 8,192 total output tokens within the unchanged $1 SDK
budget. A fresh approval binds these settings. No malformed output is repaired
into success and no reviewer result is bypassed.
