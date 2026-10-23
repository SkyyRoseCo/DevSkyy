# Dashboard-provider execution

God Mode 2.5 exposes `dashboard_providers`, `dashboard_run_start`,
`dashboard_run_status`, and `dashboard_run_cancel` through both MCP transports.
The standalone CLI is `python3 tools/dashboard_runtime.py`.

These tools require the matching DevSkyy backend implementation at
`/api/v1/orchestration/god-mode`. Installing this plugin does not deploy that
backend. A 404/503 is a deployment/configuration blocker, not an empty success.

## Connection

Set `DEVSKYY_DASHBOARD_API` to the trusted HTTPS **backend origin**, without a
path. Set `DEVSKYY_DASHBOARD_TOKEN` to a dashboard administrator access token
issued by the existing login flow. This is not MCP_SERVICE_TOKEN and is not an
LLM provider key. Keep it in the host environment/secret manager. Never put it
in briefs, command arguments, committed files, or chat. Refresh expired access
through the dashboard's existing authentication flow.

Provider credentials remain on the server. Discovery reports configured
adapters, priced model IDs, enabled state, and authorized tools; configuration
does not prove live provider authentication. Select returned model IDs exactly.

## Executable mission

`dashboard_run_start` takes two strings: `request_json` and `idempotency_key`.
The JSON object requires:

- `mission`: all eleven fields defined by `tools/mission.py`.
- `provider`, `model`: values from discovery.
- `max_calls`: 1–8 total model calls, including follow-up tool turns.
- `max_output_tokens`: 128–8192 per model call.
- `timeout_seconds`: 10–300 total runtime seconds.
- `max_cost_usd`: positive finite authorized cap, at most 100.
- `tools`: exact discovered tool names, at most 16.
- `authorize_paid`: true only when the user has authorized the stated mission,
  provider and budget. A prose authority field is not an execution grant.

Use a fresh idempotency key for a genuinely new mission. Reuse the same key and
identical body after a transport interruption; never generate a new key merely
to retry an uncertain request. Persist the returned run ID and poll status.
Accepted requests remain recoverable with their original key even if execution or
provider/tool policy is later disabled. Expired authentication still requires signing
in as the original owner. The dashboard retains uncertain submissions across reloads
and authentication/policy errors.
CLI start supports larger briefs via `--request-file` and `--idempotency-key`.

The agent uses a bounded JSON action loop with the server's existing tool
registry. This permits adapters without compatible native tool calling.
Only server-allowlisted, registered read-only tools without additional permission
requirements are exposed. Mutating tools must use their independent approved
workflows; this runtime cannot infer publishing or production deployment grants.
No arbitrary shell, URL, credential, or handler is accepted from a model.

`completed` means a model returned a final deliverable. Verification remains
`NOT_RUN` and release remains `NOT_DEPLOYED` until independently evidenced.
Output includes a SHA-256 receipt. A provider/tool error, exhausted budget, or
malformed action cannot become a fake completed response.

Cancellation is cooperative at execution boundaries. An in-flight request may
still complete and incur cost. A lost worker/deadline becomes `unknown`; it is
not automatically resubmitted. Background work exists only while the backend
worker lives; interrupted runs require reconciliation, not silent recovery.

## Server configuration and limits

The backend requires `GODMODE_EXECUTION_ENABLED=1`, `GODMODE_EXECUTION_INSTANCE`
matching its actual `FLY_MACHINE_ID` (or hostname off Fly), an absolute
`GODMODE_RUN_DB` on a persistent local volume, and `GODMODE_MODEL_PRICES` mapping
`provider/model` to positive `input_per_million` and `output_per_million` USD
rates. Operators must verify conservative current tariffs before enabling a
model. Input UTF-8 bytes plus message overhead and maximum output tokens reserve
cost before every call; unused reservations are not released within a run.
These are application reservations based on configured rates, not a provider
billing guarantee. Reconcile actual charges and use provider account limits.

`GODMODE_ALLOWED_TOOLS` is a comma-separated server allowlist.
`GODMODE_LITELLM_MODELS` additionally enables explicitly configured gateway model
IDs; they also need tariffs. Router-native adapters use their configured keys.
No automatic cross-provider fallback or inference retry is used. SQLite enforces
owner-scoped idempotency and 2 active runs per owner / 8 per shared database.
Only the designated instance accepts execution/status/cancel; configure routing to it.
Deploy on one persistent-volume backend instance; multiple isolated databases
would not share those limits. Horizontal workers need a shared transactional
store before expansion.

## Verified example boundaries

Offline positive tests execute a fake provider's tool request through a test
tool and feed its result into the next model turn, then persist a final output
hash. Negative tests reject an unlisted shell tool, conflicting idempotency
reuse, cross-owner status reads, and insufficient cost reservation. The
correction is to choose a registered authorized tool, preserve the original
request key, authenticate as the owner, and obtain adequate scoped authority.
These tests verify dispatch contracts; they are not paid provider receipts.
