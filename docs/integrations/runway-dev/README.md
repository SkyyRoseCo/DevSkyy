# Runway Dev governed integration for DevSkyy

## Chosen surface

Use a Runway Dev Model Router for this governed image path. The live `skyyrose.co` router now has a closed allowlist containing only `gpt_image_2_5_sunburst`, a 76-credit image ceiling, and capacity fallback disabled. There is a documentation conflict about whether that ceiling applies to each output or to the full generation when `outputCount` is greater than one, so multi-output is not qualified. The router does not force dry-run mode.

The local endpoint is `/api/runway-dev/dry-run`. It accepts only an allowed aspect ratio and constructs a fixed synthetic prompt, one image, no references, and 2K resolution. The request body is capped at 1 KiB before JSON validation. Response validation keeps the estimate separate from the router ceiling and rejects task IDs or artifacts. A dry-run has a zero generation reservation; it does not establish the maximum exposure for a later paid task.

## Desktop workspace and Developer API boundary

Use `https://app.runwayml.com/` in Chrome for human-directed media creation and review. Runway's current navigation guide lists Home, Agent, Tool, Apps, Workflows, Recents, Projects, and Assets; its Apps are focused, use-case-specific workflows. The Apps documentation explicitly says those Apps cannot be accessed through the API. Keep this Chrome workspace separate from the server-side Developer API route and `runway-dev-mcp`. The Dev MCP was used for read-only account/project checks and the requested router configuration; no browser session was opened and no media was generated during this qualification update.

The route is still hard-blocked before contacting Runway because the saved-router policy is not bound to server runtime and a real Scarce Resource Governor quota-authorization/audit adapter is unavailable. On 2026-09-26, the authenticated Runway Dev MCP returned the `skyyrose.co` API project, a 5,500-credit project balance, and GPT Image 2.5 Sunburst at 16 credits per image. I created the router, set the closed policy, and re-read version 2. No verified Governor candidate exists in this checkout, and environment flags cannot enable provider calls. The exact qualification state is recorded in [qualification.yaml](./qualification.yaml).

Runway’s current docs say the Node SDK does not yet support router dry-runs, so this route retains one raw HTTPS request with `dryRun: true` behind the Governor gate. It uses the documented API host and version header, disables caching, times out, and does not retry. A separate paid adapter has not been built; when the Governor and qualification contract exist, that path should use the official Node SDK and its documented task wait helper.

## Local configuration

The endpoint also requires its server configuration, but setting these values alone will not bypass the Governor gate. Keep the API secret server-side and never give it a `NEXT_PUBLIC_` prefix. The current local presence-only check found the Runway settings absent; it did not read or display any secret value.

    RUNWAY_DEV_DRY_RUN_ENABLED=true
    RUNWAY_DEV_API_BASE_URL=https://api.dev.runwayml.com
    RUNWAY_ROUTER_CONFIG_ID=<existing-approved-router-config-id>
    RUNWAYML_API_SECRET=<server-side-runway-dev-api-key>

The Chrome-installed Runway Web App is for manual media work; its credits are separate from the Developer API project balance. The read-only Dev MCP showed 5,500 credits in the `skyyrose.co` API project on 2026-09-26. Do not treat Web App credits as funding for this route or as a spend authorization.

After the Developer API organization and router configuration exist and the real Governor adapter is integrated, an authenticated dashboard session can submit:

    fetch('/api/runway-dev/dry-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ aspectRatio: '4:5' }),
    }).then((response) => response.json());

Runway documents dry-run as returning routing metadata and an estimated cost without creating a task, asset, or generation charge. It still makes a provider API request and is subject to Runway’s API rate limit. No dry-run or generation request has been made from this implementation.

## Deliberate boundaries

- This is a local starter in the DevSkyy Next.js dashboard. It has not been deployed.
- No Developer API organization, API key, or credits were created or changed. One Model Router was created and configured; its exact revision and digest are recorded in [qualification.yaml](./qualification.yaml).
- Presence-only local check on 2026-09-25: `REDIS_URL` and `NEXTAUTH_SECRET` were present; the Runway API secret, dry-run enable flag, API base URL, and router config ID were absent. Secret values were not read or printed. The Runway Python SDK imports successfully from the repository `.venv` as version 5.20.1; this does not prove API-key authentication.
- The endpoint sends only a fixed synthetic prompt; callers cannot submit prompts, references, model overrides, or output counts.
- A distributed per-user 60-second cooldown uses the existing `REDIS_URL` store and an atomic Redis Lua `SET NX`, with an HMAC-derived identity key. It fails closed if the shared store or HMAC secret is unavailable. The limiter runs before the Governor reservation and provider request. Local tests exercise the limiter contract; Redis was not contacted. The qualification gate currently prevents route requests from reaching the limiter or Runway.
- Local validation: on 2026-09-25, lint passed with 231 repository warnings and no errors; the production build passed with npm lifecycle scripts skipped to avoid running the unrelated scene-authority prebuild; the local built server returned 401 to an unauthenticated POST. On 2026-09-26, the four focused router suites passed all 26 tests after updating the runtime-binding gate reason, and the frontend TypeScript check passed. These checks prove local code behavior only; they do not verify server API-key authentication, runtime router binding, Redis connectivity, or Governor authorization.
- The Runway Dev MCP authenticated as Developer account ID 255723 and returned one owned/accessible API project, `skyyrose.co` (project ID `149ffed4-4b00-44d5-8e69-2536c30db85e`). It returned a 5,500-credit API-project balance and listed Sunburst at 16 credits per image. The router was created, configured, and re-read with version 2. The Developer organization/billing identity and server-side API-key scope remain unknown. No dry-run or generation request was made; the project balance remained 5,500 after configuration. The create operation briefly returned its default `allow_new_except` policy before the next update replaced it with the closed allowlist; no call was submitted by this task during that interval, but external concurrent use cannot be ruled out from the available task-history tools.
- Privacy and retention terms for a Developer API organization remain unverified. Do not submit private prompts or product references through this preflight.
- The pre-existing personal Runway Web App MCP and the newly connected `runway-dev-mcp` are separate surfaces. This task used read-only Dev MCP calls for account, project, router-list, model-catalog, and API-balance checks, followed by the requested router create/update/read. It did not use Chrome or the Web App for generation.
- Runway documents actual `cost.credits` on task detail, so a preserved Runway task ID can support provider-attested billing attribution. The integration does not yet bind a task ID to a Governor operation, and no live receipt was verified. The API documents task cancellation/deletion but does not promise zero charges or refunds for cancellation. Successful output URLs expire after 24–48 hours; the API docs say deleted-task output data is deleted, while prompt/input retention remains unspecified here.
- The Runway Dev homepage advertises no training on data and zero-data retention by default. The enterprise FAQ describes contractual no-training commitments and DPAs for third-party model use under enterprise terms. The actual Developer organization, plan, applicable agreement, privacy settings, and GPT Image 2.5 processing terms remain uninspected, so privacy/retention stay blocked for private material.
- This preflight does not qualify the provider for paid use. The router does not require `dryRun=true` or limit `outputCount`; an API-key holder calling Runway directly could make a paid call outside the app's interlock. Do not assume whether the 76-credit ceiling caps a multi-output request until Runway resolves the current docs/MCP-schema conflict. Lost-response recovery, Governor operation binding, local output storage/deletion, privacy terms, runtime router binding, and explicit Governor authorization remain separate gates.
- Before a real Governor can replace the deny interlock, its authorization must bind the authenticated principal and exact provider-quota operation to an operation identity, reservation decision, and audit record. That interface is unavailable in this checkout and has not been simulated.

## Official references

The Runway Dev integration docs were checked on 2026-09-25; the Chrome workspace, Model Router cap semantics, and pricing details were rechecked on 2026-09-26.

- Quickstart instructions: https://dev.runwayml.com/quickstart.txt
- Chrome-oriented creative workspace: https://help.runwayml.com/hc/en-us/articles/37425232841875-Getting-Started-with-Generative-Video (checked 2026-09-26)
- Workspace navigation: https://help.runwayml.com/hc/en-us/articles/24298206897043-Navigating-Runway (checked 2026-09-26)
- Apps and API availability: https://help.runwayml.com/hc/en-us/articles/45570040112531-Creating-with-Apps (checked 2026-09-26)
- Documentation index: https://docs.dev.runwayml.com/llms.txt
- API context: https://docs.dev.runwayml.com/ai-context.md
- Model Router overview and configuration: https://docs.dev.runwayml.com/model-routers/configuration.md
- Routed generation and dry-run behavior: https://docs.dev.runwayml.com/model-routers/generating.md
- Exact routed image request schema: https://docs.dev.runwayml.com/api.md
- Model identifiers: https://docs.dev.runwayml.com/guides/models.md
- Pricing: https://docs.dev.runwayml.com/guides/pricing.md
- API account setup and key handling: https://docs.dev.runwayml.com/guides/setup.md
- Task output links and expiry: https://docs.dev.runwayml.com/assets/outputs/
- Task retrieval/cancellation and SDK timeout behavior: https://docs.dev.runwayml.com/api.md and https://docs.dev.runwayml.com/api-details/sdks/
- Developer privacy claims and enterprise third-party-model commitments: https://dev.runwayml.com/ and https://help.runwayml.com/hc/en-us/articles/51248305153683-Enterprise-FAQ-Third-party-Models-in-Runway

The maintained, evidence-labeled skill examples are in [verified-examples.md](./verified-examples.md).
