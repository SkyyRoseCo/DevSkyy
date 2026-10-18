# Claude worker qualification — fix and remaining gate

Date: 2026-10-18. Models selected by owner: Claude Opus 5.5 and Codex GPT-6.1
Sol. Scope: bounded source-packet Fashion analysis; no media production or
release.

## Confirmed root cause repaired

The first adapter supplied a string prompt together with `can_use_tool`. Claude
Agent SDK 0.2.82 rejects that combination before creating/connecting its
transport. The adapter now supplies one streamed user message. A regression uses
the actual installed SDK with an injected offline transport. A separate one-off
reproduction matches the exact saved adapter hash from commit e2efee812 and
proves zero transport connections. The original reservation remains in history
with a single, idempotent no-dispatch attestation; no ambiguous failure was
refunded.

## Further evidence

- The next live qualification timed out at 100 seconds; usage is unknown and its
  reservation remains consumed. Its cause is not established.
- A manually authorized bounded configuration uses 1,024 thinking tokens, low
  effort, 4,096 maximum output tokens and strict JSON text checked locally,
  retaining every tool restriction. That attempt failed with an insufficiently
  specific `provider_error` diagnostic. It did not produce a validated artifact.
- Diagnostics now unwrap nested SDK exception groups and retain only fixed safe
  error/phase categories. No arbitrary provider text, reasoning or credentials
  enter receipts. This improvement has offline regression proof, not another
  live success claim.
- Real SDK startup/initialization handshake passed without submitting a prompt.
- Authenticated Anthropic model listing confirmed Opus 5.5; token-count
  validation accepted the bounded thinking configuration. Neither proves a
  completion.

## Current state

GOD MODE has two implemented analysis workflows, exact-plan approvals, durable
memory, immutable source/worker bindings, allowance accounting and independent
review gates. Canonical packets include all 15 preorder products and all four
collection identity documents. The skill audit includes all eight migrated skill
entrypoints; linked references absent from a packet remain evidence gaps.

The Claude live workflow is NOT qualified. Codex has not received a successful
Claude artifact and therefore has not run in the live sequence. Production stays
disabled. Current daily potentially billable qualification allowance is
exhausted; there is no automatic retry, cap increase or release of unknown
usage.

Next gate: a fresh explicit plan under an available/approved allowance, with the
new safe phase diagnostics, must produce a validated Claude artifact and bound
Codex review. Real owner-dashboard login is separately untested; local service
qualification used current-chat authorization, never a minted founder JWT.

Source-level fixes and offline checks may continue without another provider
call.
