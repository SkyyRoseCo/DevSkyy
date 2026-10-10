---
name: efficient-production
description: >
  Evidence-led tool discipline and production execution controls. Reuse valid
  context, minimize rework, enforce source, authority, method, cost, quality, and
  release gates inside operating systems, and report only what evidence proves.
---

# Efficient Production

Efficient production means reaching a verified result with the least total rework,
delay, and controlled cost. It never means skipping a check that protects product
truth, authorization, security, quality, or release integrity. This skill governs
how work proceeds; it does not override higher-priority instructions, grant
spending or publishing authority, or prove that a runtime system enforces a rule.

Apply these rules whenever this skill is invoked or embedded in an agent or
operating system.

## 1. Establish the current state

- Confirm the effective checkout, branch or detached HEAD, and relevant staged,
  unstaged, and untracked changes before editing. Preserve unrelated work.
- Read the applicable project instructions and source of truth first. If
  `.wolf/anatomy.md` exists, use it to locate the right files; it is an index,
  not a substitute for reading source that must be changed or verified.
- Reuse evidence already in context while its source, version, and environment
  remain current. Re-read or rerun when a file changed, evidence may be stale,
  a failure exposed a new dependency, or a required check calls for it. Do not
  turn “avoid redundant reads” into “never verify again.”
- For SkyyRose product work, read product facts through
  `from skyyrose.core.product import get_product`; the root `logo-registry.json`
  is the editable product source. Founder and maker corrections are authoritative.
- Record the target environment explicitly: local fixture, candidate checkout,
  staging, or production. A result from one target does not establish another.

## 2. Use tools and checks efficiently

- Batch independent reads and searches. Keep dependent operations sequential,
  especially edits, approvals, claims, and external actions.
- Make searches evidence-focused. Broaden or split them when the first search
  does not answer the question; there is no fixed search-count limit.
- Delegate only when the user or applicable instructions authorize delegation
  and the subtask is genuinely independent. Parallel work is not a requirement.
- Do not fetch a stable or already-proven fact without a reason. Verify
  unfamiliar, current, contested, high-impact, or environment-specific claims
  against an authoritative source.
- Choose checks that exercise the changed behavior and its boundary conditions.
  Run broader suites when the integration surface requires them, not as a ritual
  for every small change.
- Compare the task diff with the starting state. A dirty checkout is not a clean
  task scope, and unrelated pre-existing changes must not be erased or reported
  as part of this task.

## 3. Embed efficiency in every production OS

For a system that prepares or executes production work, put the shared policy in
the trusted runtime path. A skill paragraph or checklist alone is not runtime
enforcement. Every entry point, worker, and retry path must use the same contract
and fail closed when its evidence is missing, stale, or out of scope.

Bind each operation to the requested deliverable, protected product facts, exact
source bytes, collection or customer context, method, provider and model where
applicable, prompt or configuration, actual controls, runtime version, owner
scope, and prior method history. Recompute the binding when any dependency changes.

Use explicit gates in this order:

1. **Resolve** current source truth, request scope, constraints, and existing
   history. Identify missing evidence rather than filling gaps by assumption.
2. **Admit** only the exact method and deliverable supported by current evidence.
   A missing, expired, changed, or revoked admission blocks progression.
3. **Check authority and cost** before provider capability calls, quotes,
   reservations, uploads, writes, or other consequential steps. Keep human
   approval and account access separate from technical readiness.
4. **Claim once and execute through the trusted host.** Recheck the original
   claim and admission immediately before an external dispatch or final write,
   including after callback-capable validation.
5. **Record what happened.** Persist the actual invocation, environment,
   outcome, artifact identity, and review evidence. An exception after adapter
   entry or an unknown result is not a confirmed stop; preserve the consumed
   claim and reconcile it before retrying.
6. **Review the exact output.** Technical validity, metadata, hashes, model
   success, and page load do not by themselves prove product fidelity, visual
   quality, accessibility, or release readiness.
7. **Accept or reuse exact evidence.** Reuse bytes only while their source,
   context, admission, and independent review remain valid. A stale artifact
   requires an explicit reviewed rejection or replacement path.
8. **Release separately.** Generation, spending, upload, staging, production
   deployment, publication, and founder acceptance are separate authorities.
   Passing an earlier gate never implies a later one.

For the SkyyRose Creative OS, `BLOCKED`, `QUALIFICATION_ONLY`, and
`PRODUCTION_ELIGIBLE` describe method admission only. A causal correction may
enter a bounded qualification run; that result does not authorize bulk output.
Preserve negative and unknown history across task IDs, journals, quality
settings, and folder changes. Do not retry an unknown provider outcome blindly.
Do not claim one host invocation means one billable provider attempt unless the
provider retry behavior is verified.

Before drafting, reviewing, or submitting image or video generation prompts,
read and cite the required [imagery prompting standard](/Users/theceo/.codex/creative-standards/imagery-prompting.md)
in the creative brief. It does not authorize generation or spending. For
SkyyRose visuals, keep product fidelity, collection identity, editorial quality,
natural scene integration, and the intended shopping context as independent
review criteria.

## 4. Verify before claiming completion

- Match validation to the change: meaningful focused tests for changed behavior,
  plus the owning package's lint, type, build, or integration checks where
  applicable. Report the exact commands and results; list failed, skipped, or
  unavailable checks.
- Production code must not ship unresolved implementation placeholders or
  fixture data as real customer or product data. `TODO`, `pass`, and test mocks
  are not automatic failures without context; inspect whether they leave the
  delivered path incomplete or unsafe.
- Every current codebase claim must trace to source read in the current task or
  to an explicitly identified durable receipt. Label historical, inferred, and
  unverified claims; hashes prove byte identity, not truth or visual quality.
- State completion against the requested scope. Do not turn a local test pass,
  simulated result, provider response, dashboard label, or public page into a
  claim of authenticated staging or production success.
- Follow the repository's documentation format. Use Markdown for ordinary
  procedures; use linked, accessible HTML when navigation or presentation makes
  it materially clearer.

## 5. Verified examples

The task-specific correct and incorrect examples, provenance, test receipt,
authentication state, limits, and refresh triggers are maintained in
[`references/verified-examples.md`](references/verified-examples.md). Recheck
those examples when the source code, policy boundary, provider behavior, or
target environment changes.
