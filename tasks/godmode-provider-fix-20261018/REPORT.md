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

- Use Opus 5.5 adaptive thinking and low effort with the existing bounded output
  and dollar limits. Manual thinking configuration is a separate compatibility
  defect, documented by Anthropic's Opus 5.5 migration guide.
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

## Current gate and next action

**BLOCKED_PROVIDER_USAGE_LIMIT. Production remains OFF.** No valid Claude
artifact was produced and Codex has therefore not reviewed one in the live
sequence. Existing failed runs, uncertain usage and reservations remain
recorded. A separate `PROVIDER_DIAGNOSIS_RECORDED` event was appended to GOD
MODE's durable audit log; no accepted memory or owner acceptance was written.

The owner has said they will raise the API limit. After confirmation it is
applied, create a fresh exact-plan approved run, execute the full canonical
packet (all 15 preorder products and eight migrated skill entrypoints), validate
Claude coverage, then run independent Codex review bound to that artifact's
hash. A metadata lookup, fixture result, or configuration check cannot
substitute for that sequence. Production/release requires its separate owner
authority even after analysis passes.

## Validation

- 84 focused runtime, adapter and workflow tests passed.
- Explicit mypy checks passed for both changed runtime modules.
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
