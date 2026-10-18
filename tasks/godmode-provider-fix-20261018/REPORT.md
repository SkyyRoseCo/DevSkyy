# Claude provider diagnosis and governed recovery

Recorded 2026-10-18. Scope: source-packet Fashion analysis with Claude Opus 5.5
(`claude-opus-5-5`) and independent Codex GPT-6.1 Sol (`gpt-6.1-sol`).

## Confirmed provider rejection

One direct Messages request, using the configured Anthropic credential and a
tiny synthetic prompt without CLI extras or beta headers, returned HTTP 400:

> You have reached your specified API usage limits. You will regain access on
> 2026-11-01 at 00:00 UTC.

The sanitized `direct-messages-receipt.json` records exactly one request and its
scope. Authentication targeted Anthropic's Messages API with the configured
credential; the response did not identify the account, so none is inferred. The
provider's reset is October 31, 2026 at 17:00 America/Los_Angeles. This
establishes the current credential's rejection; it does not retrospectively
prove the cause of every historical SDK failure.

## Implemented fixes

- Use Opus 5.5 adaptive thinking and medium effort with the existing bounded
  output and dollar limits. Manual thinking configuration is a separate
  compatibility defect, documented by Anthropic's Opus 5.5 migration guide.
- Pin the installed Claude executable, version and binary hash in each immutable
  approval contract rather than silently choosing the SDK's older bundled CLI.
- Preserve fixed provider-error codes through SDK cleanup and process
  supervision. Classify the recorded usage-limit wording specifically, with
  actionable operator guidance even when the supervisor appends a phase. No raw
  provider text or credentials enter general runtime failure receipts.
- Defer successful assistant text until an error result confirms a failure, so
  normal analysis discussing a provider limit cannot poison diagnosis.
- Supply required Codex rollout-budget settings; the actual installed CLI
  accepts the isolated configuration without making a model request.
- Permit an additional qualification only through a trusted internal, one-use,
  expiring event bound to the exact run, plan, actor and adapter contract. No
  public grant endpoint, counter reset, refund of unknown usage, or automatic
  retry.

The offline wire fixture records actual outgoing configuration using a synthetic
key and a localhost server. It proves request fields, not live provider success.
Historical live harnesses now exit before credential lookup or network access.

## Current gate — live qualification passed

**PASSED_BOUNDED_FASHION_SKILL_ANALYSIS_ONLY. Production remains OFF.**

After the owner confirmed the API limit increase, four separately authorized
attempts were recorded. The first two produced valid worker artifacts and actual
Codex FAIL reviews; their unsupported assertions were rejected. The third
returned invalid JSON and was rejected before reviewer dispatch. No failed
result was edited into success, no reservation was reset, and no reviewer
criterion was weakened.

The root cause of repeated content errors was a shared prompt that directed the
skill-audit workflow into unsolicited campaign/product analysis. The fix routes
by workflow, names all eight skill targets, and verifies one finding per skill,
while retaining every preorder record and exact 15-SKU coverage. Medium effort
and 8,192 output tokens retain the same $1 SDK budget. Output-token exhaustion
now has an explicit failure classification. The third attempt's malformed JSON
alone does not prove that it exhausted tokens.

Run `6c938210-2fae-406c-a1e1-7352a1f65995` succeeded. Opus returned
`claude-opus-5-5`, which the host checked against the approved model. Its
schema, eight-skill findings and 15-SKU coverage passed. Independent Codex,
selected as `gpt-6.1-sol` through the frozen CLI argument, returned PASS with no
findings and a matching worker hash. Codex's selected argument is configuration
evidence, not a separate returned-provider-model attestation.

`LIVE-QUALIFICATION.json` preserves sanitized artifact evidence and the complete
attempt-status trail. Full source packets, approvals and event history remain in
GOD MODE's durable local SQLite state. Accepted memory remains unchanged and
human acceptance remains NOT_GRANTED. The successful Claude attempt reports
$0.4931913; this is not the total across all attempts. The malformed attempt's
cost is unknown and its reservation remains retained. Codex used the existing
ChatGPT allowance.

This qualifies the bounded skill-analysis workflow only. It does not qualify all
Fashion workflows, complete any film or garment-fidelity review, prove owner
browser login, or authorize production/deployment. Those gates remain separate.

## Validation

- 88 focused runtime, adapter and workflow tests passed.
- Explicit mypy checks passed for all three changed runtime modules.
- Ruff, Black and scoped diff checks passed.
- Independent architect and Python reviews found no remaining material defect
  within the bounded fix. Live success remains unverified, rather than inferred.
- One existing Starlette/httpx deprecation warning remains.

Examples: the recorded usage-limit rejection is the correct recovery case:
retain history, report the account limit, stop before Codex, and require a fresh
approved run after clearance. The explicit incorrect case is illustrative: reset
historical reservations or mark a fixture PASS as live qualification. Correct it
by preserving reservations and requiring real schema-valid worker and reviewer
artifacts.

Provider reference:
https://platform.claude.com/docs/en/models/opus-5-5/migration-guide
