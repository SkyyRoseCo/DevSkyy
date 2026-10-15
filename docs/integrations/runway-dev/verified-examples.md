# Runway Dev verified examples

Scope: the installed third-party skills runway-dev and runway-dev-model-routers,
with the local dry-run starter in DevSkyy. This is a maintained project overlay
linked from both installed skill entrypoints; it does not alter the upstream
Runway skill repository.

Verification date: 2026-09-26. Official docs were retrieved from Runway Dev’s
llms.txt links and checked against the raw API reference. Local examples are
synthetic. The authenticated Runway Dev MCP verifies read access to Developer
account ID 255723 and its single owned/accessible API project, `skyyrose.co`; it
returned a 5,500-credit project balance and GPT Image 2.5 Sunburst at 16 credits
per image. A router was created and re-read with version 2, a Sunburst-only
allowlist, capacity fallback disabled, and a 76-credit image ceiling. The
official Router guide describes a hard per-generation ceiling, while the MCP
schema describes per-output enforcement; Sunburst billing multiplies per-image
price by outputCount, so the multi-output ceiling behavior remains unresolved.
Server-side API-key authentication, runtime binding, and dry-run enforcement
remain UNVERIFIED. A personal Runway Web App/MCP credit balance is a separate
pool.

## Shared skill: runway-dev

### Correct: integrate into the existing server boundary

- **Request and context:** Add Runway Dev routing to the existing non-empty
  DevSkyy Next.js dashboard. Dev MCP account/project read access is verified; no
  server API key, saved router, Governor authorization, or paid-call approval is
  verified.
- **What to do:** Inspect the app; keep the key in server-only environment
  variables; use current llms.txt task links; add an authenticated server route;
  proceed with account-independent implementation without creating a live
  organization or spending credits.
- **What not to do:** Scaffold a second app or treat the existing personal
  Runway MCP workspace as the Developer API account. Correct by implementing
  inside the existing app and keeping the two identity and billing paths
  separate.
- **Expected versus observed:** Expected: the route remains blocked until the
  saved-router policy is bound to runtime and the actual Governor integration
  exists. Observed: the authenticated dry-run route is present with hard
  qualification/Governor interlocks and a shared Redis limiter. The router has a
  Sunburst-only allowlist, a configured 76-credit image ceiling, and no capacity
  fallback. Four focused test files passed all 26 synthetic tests on 2026-09-26
  after the route-gate reason was renamed to reflect missing runtime binding. No
  dry-run or generation request, Redis connection, or BullMQ Lua command was
  made.
- **Evidence:** VERIFIED_LIVE_READ_ONLY — Runway Dev MCP `whoami`, owned and
  accessible project listings, `list_model_routers`, `list_models` for
  `/v1/text_to_image`, and `get_credit_balance`; checked 2026-09-26.
  REPRODUCED_LOCAL — `frontend/tests/runway-dev-router-dry-run.test.ts`,
  `frontend/tests/runway-dev-router-dry-run-route.test.ts`,
  `frontend/tests/runway-dev-router-dry-run-rate-limit.test.ts`, and
  `frontend/tests/runway-dev-router-dry-run-fixture-route.test.ts`; 4 files / 26
  tests passed. The fixture route uses mocks and does not establish
  authenticated generation behavior.
- **Authentication:** VERIFIED_LIVE for the connected Runway Dev MCP
  account/project and router-management scope only; server-side Developer API
  generation authentication is UNVERIFIED. Environment: Developer account ID
  255723; project ID `149ffed4-…-b85e`; project `skyyrose.co`; no email or API
  key recorded.
- **Limits and refresh trigger:** This is a point-in-time catalog and balance
  observation. The empty router list means no policy snapshot can be qualified.
  Refresh project, router, model catalog, and balance before any later
  operation; a balance is not authorization to spend.

### Incorrect: equate installed Runway MCP with Runway Dev API

- **Request and context:** A user reports a large Runway credit balance while
  the project is considering a Developer API gateway.
- **What not to do:** Assume the personal Web App/MCP balance pays for API
  generation or that MCP identity proves API organization access.
- **Correction and reason:** Record which connected surface was read. Runway
  explicitly documents separate Web App and API credit pools. Read the Developer
  API project separately before making a funding claim; a project balance still
  does not reveal the invoice identity or authorize spend.
- **Expected versus observed:** Expected by the source: balances are separate.
  Observed on 2026-09-25: the connected personal workspace showed 7,395 credits;
  no Developer API organization balance was read.
- **Evidence:** SOURCE_VERIFIED —
  https://docs.dev.runwayml.com/usage/workspace-reporting.md, paragraph
  distinguishing /v1/organization/usage from Web App credits; checked
  2026-09-25. HISTORICAL_OBSERVED — authenticated read-only Runway MCP whoami
  result, personal workspace only, 2026-09-25.
- **Authentication:** VERIFIED_LIVE for the connected Runway MCP personal
  workspace identity and balance query only; Runway Developer API key
  authentication remains UNVERIFIED.
- **Limits and refresh trigger:** The 7,395 result is a point-in-time
  personal-workspace observation, not an API balance or a future balance.

## Surface skill: runway-dev-model-routers

### Correct: dry-run the fixed, one-model image router over HTTP

- **Request and context:** Check a saved Model Router before any image
  operation. The configured router has a closed allowlist containing only
  gpt_image_2_5_sunburst, no capacity fallback, and a 76-credit image ceiling.
  Its behavior for multiple outputs is unresolved.
- **What to do:** Use the exact image router endpoint with dryRun set to true, a
  synthetic prompt, one 2K output, and no references. Require returned dryRun
  true, the expected config ID and model, a non-null policy-compliant ceiling,
  and an estimate no higher than that ceiling.
- **Illustrative request (not executed):**

      POST https://api.dev.runwayml.com/v1/generate/image
      Authorization: Bearer $RUNWAYML_API_SECRET
      X-Runway-Version: 2024-11-06
      Content-Type: application/json

      {
        "configId": "existing-approved-router-config-id",
        "dryRun": true,
        "input": {
          "promptText": "A neutral unbranded ceramic vessel on a plain warm-gray studio background.",
          "aspectRatio": "4:5",
          "resolution": "2k",
          "outputCount": 1
        }
      }

- **What not to do:** Use an arbitrary router ID, allow provider fallback to a
  different model, assume the 76-credit cap's multi-output semantics are
  settled, or assume the router forces dry-run mode. Current official
  documentation and the live MCP schema describe the cap differently. Keep
  multi-output blocked until this is resolved; bind the router snapshot to
  runtime and use documented dry-run only after the Governor authorizes the API
  quota operation. SDK dry-run support remains unavailable in the current docs.
- **Expected versus observed:** Expected by the docs: routing metadata and
  estimated cost, with no task, generated asset, or generation charge. Observed:
  no dry-run request was sent against Runway Dev; local contract and fixture
  tests exercise payload construction, fail-closed response validation, and
  route behavior only. The route remains blocked because the live router is not
  bound to runtime and this checkout has no verified Governor quota adapter.
- **Evidence:** SOURCE_VERIFIED —
  https://docs.dev.runwayml.com/model-routers/configuration.md, “Eligible
  models” and “Maximum credits per generation”;
  https://docs.dev.runwayml.com/model-routers/generating.md, “Generate image”
  and “Validate with a dry run”;
  https://docs.dev.runwayml.com/guides/pricing.md, GPT Image 2.5 Sunburst table;
  checked 2026-09-26. The MCP model-router schema also reports the live settings
  and describes its credit cap per output. REPRODUCED_LOCAL — all four focused
  route suites pass 26 synthetic tests.
- **Authentication:** Runway Dev MCP account/project/router management scope is
  VERIFIED_LIVE; Developer API generation authentication is UNVERIFIED. The
  illustrative request contains an environment-variable placeholder; no key was
  read or submitted.
- **Limits and refresh trigger:** The meaning of the 76-credit cap for
  outputCount greater than one remains unverified. It is not spend
  authorization. Check current pricing and router version, keep outputCount at
  one in the app, and require Governor authorization before any dry-run or paid
  request.

### Incorrect: assume the Node SDK honors dryRun

- **Request and context:** A developer wants a no-charge Model Router preflight.
- **What not to do:** Call the SDK generate.image.create method with dryRun true
  and rely on the extra property being interpreted as a no-charge dry-run.
- **Correction and reason:** The current Runway generating guide states that SDK
  dry-run support is coming soon. Use the documented HTTP endpoint with
  top-level dryRun true until SDK support is published; never test this
  assumption with a paid generation.
- **Expected versus observed:** Expected from docs: HTTP dry-run resolves the
  routing choice without creating a task or charge. Observed: no provider
  request was made; the code uses HTTP only for the dry-run route, with
  router-qualification and Governor interlocks before the request. The fixture
  test injects a mock provider response and is not live evidence.
- **Evidence:** SOURCE_VERIFIED —
  https://docs.dev.runwayml.com/model-routers/generating.md, “Validate with a
  dry run”; checked 2026-09-25.
- **Authentication:** UNVERIFIED for Runway Developer API.
- **Limits and refresh trigger:** Re-check SDK support when the official SDK/API
  version changes.

## Coverage

PARTIAL for these two declared skills. The project overlay gives each skill
source-verified correct and incorrect examples and records local tests.
Developer account/project access and the saved router policy are authenticated
through Dev MCP, but server API-key authentication, runtime binding, real
dry-run behavior, Governor binding, and paid task receipts remain unverified.
