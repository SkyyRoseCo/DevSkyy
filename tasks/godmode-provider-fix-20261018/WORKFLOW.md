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
