---
name: adversarial-planning
description: Build and test a plan with two independent providers before high-cost work. Claude Code using the Fable alias drafts and revises; OpenAI Codex challenges. Use for architecture, migrations, creative-production systems, and other work where a wrong plan is costly. Defaults to plan-only; never execute unresolved objections.
---

# Adversarial Planning

Claude/Fable is the planner. Codex, using its effective OpenAI configuration, is
the independent challenger. Different model names from the same provider do not
count as independent. If either provider, authentication, configuration,
network readiness, or the runner is unavailable, stop before making a model
request. Do not substitute another Claude model for Codex, or another provider
for Fable.

## Choose this workflow

Use adversarial planning when a wrong plan could cause a costly rebuild,
irreversible migration, substantial provider spend, or a product/release
failure. Skip it for small, obvious changes and use adversarial verification
when reviewing work that already exists.

The default mode is plan_only. Select plan_and_execute only when the user
explicitly asks for execution as part of this run. The only successful planning
outcomes are:

- BLOCKED: preflight, authentication, approval, or runner checks failed.
- NEEDS_REVIEW: blocking objections remain after at most three rounds, or
  execution review found a problem.
- PLAN_READY: independent reviewers converged and the run was plan_only.
- EXECUTION_COMPLETE: the converged plan was executed and the resulting work
  passed the independent review.

Round three is a final revision and challenge. It is never an execution
tie-breaker. Unresolved blocking objections return NEEDS_REVIEW.

## Providers and configuration

Use Claude Code's fable model alias for planning. Do not set a fallback model.
Use Codex CLI for challenge and, only in plan_and_execute mode, execution. Do
not pass a model override to codex exec. Let Codex apply the configuration it
would use from the selected working directory.

For manifest reporting, list a Codex model only when it is explicit in the
trusted project or user configuration. The documented precedence is command
line overrides, trusted project configuration, an explicitly selected profile,
user configuration, cloud-managed defaults, system configuration, then
built-in defaults. See the [Codex configuration
documentation](https://developers.openai.com/codex/config-basic). Codex ignores
provider-routing keys such as `model_provider`, `model_providers`, and
`openai_base_url` in project-local config; see the [configuration
reference](https://developers.openai.com/codex/config-reference/). Use trusted
project settings for model selection, but resolve provider routing only from
applicable system and user configuration. Validate both `openai_base_url` and
the effective `model_providers.openai.base_url`; never let a project provider
table shadow a machine or user route. If the effective provider or endpoint
cannot be verified, stop before any provider call.

This runner passes no model or profile override; Codex resolves its effective
model settings at invocation. If lower-priority managed/default settings make
the exact model unknown before the call, report runtime-resolved rather than
guessing. Block a known non-OpenAI provider or unverified custom endpoint.

Before work, inspect the task and run the read-only readiness checks:

- claude --version
- claude --help (verify `--model` advertises the `fable` alias)
- claude auth status --json
- codex --version
- codex doctor --json

Read only allowlisted status fields from auth output. Never print or retain
account email, tokens, session data, or raw doctor output. A nonzero doctor
exit is not itself enough to classify the result: parse the JSON. A sole
terminal.env failure may be ignored only when TERM is dumb, the invocation is
noninteractive, the diagnostic is limited to terminal color/cursor support,
and all critical authentication, configuration, installation, network, and
runtime checks pass. Any other failure or unrecognized state blocks.

The local command interface is
[adversarial_planning_cli.py](scripts/adversarial_planning_cli.py).
First prepare a manifest with the task text, selected mode, runner, provider
identities, model sources, maximum rounds and calls, and cost/quota estimates.
Unavailable cost or quota estimates must say unknown. Preparation makes no
model requests. Before a run, show the manifest, then require the exact typed
lowercase y and the displayed manifest hash. Recheck authentication,
configuration, provider readiness, task hash, and expiry before the first
model request. A changed or expired manifest requires fresh preparation and
approval.

Use the local_cli route for both modes. Prepare a manifest, review it, then
run with the same task file and manifest path. The run command requires
lowercase y and the displayed manifest hash; do not pass approval flags or pipe
a synthetic approval into the command. The runner invokes Claude Code with the
fable alias, then Codex CLI without a model or profile override, so Codex
resolves its effective configuration at invocation. If the exact Codex model
cannot be known before a call, the manifest says it is runtime-resolved.

From the repository root:

    python3 .claude/skills/adversarial-planning/scripts/adversarial_planning_cli.py prepare --task-file /path/to/task.md --manifest /tmp/adversarial-planning.json --mode plan_only --runner local_cli
    python3 .claude/skills/adversarial-planning/scripts/adversarial_planning_cli.py run --task-file /path/to/task.md --manifest /tmp/adversarial-planning.json

The Workflow adapter at
[adversarial-planning.wf.js](scripts/adversarial-planning.wf.js) currently
returns BLOCKED before any model call. Its present runtime cannot establish
fresh authenticated readiness for both providers, provide a trusted direct
Codex response channel, or atomically consume a one-time execution approval
with cumulative call accounting. Do not treat a prepared CLI manifest as
proof of Workflow readiness. Re-enable Workflow only after those runtime
capabilities are demonstrated and the adapter has corresponding tests.

The spend manifest counts provider CLI invocations, not underlying model
requests or internal turns. plan_only caps at six invocations; local
plan_and_execute caps at eight (up to four Claude CLI and four Codex CLI
invocations). Actual token usage, retries inside a CLI, price, and remaining
quota are not reliably exposed here, so cost and quota remain unknown.

## Debate contract

1. Write a concrete task with a scope, starting state, success conditions,
   exclusions, and evidence sources. Capture the task hash in the manifest.
2. Claude/Fable proposes implementable steps, affected files, a check for each
   step that can fail, risks, and blocking unknowns.
3. Codex independently checks source assumptions, missing cases, feasibility,
   verification quality, permissions, and failure recovery. Preserve Codex's
   own response as evidence; do not present a Claude paraphrase as a Codex
   judgment.
4. Claude revises against the specific challenge. Codex decides whether each
   blocking objection is resolved.
5. Stop at convergence or after three rounds. If any blocking objection remains,
   return NEEDS_REVIEW with its evidence and next decision. Do not execute.
6. In plan_only, return PLAN_READY after convergence. Do not edit files.
7. In plan_and_execute, execute only the converged plan. Review actual changed
   files and command results with Claude in read-only mode. Return
   EXECUTION_COMPLETE only when that review passes; otherwise NEEDS_REVIEW.

Image generation and publishing/deployment are separate authorization gates.
The planning manifest never authorizes either. If an approved execution plan
includes one, the local CLI requests a separate typed approval for that action
immediately before execution. Without it, return NEEDS_REVIEW and do not
perform that action. Display the converged plan and its SHA-256, then require
lowercase y and that hash for each separate gate. The disabled Workflow adapter
accepts no continuation bundle and cannot execute.

For repository tasks, preserve existing changes, inspect the active checkout,
and keep execution within the manifest's file and action scope. If the checkout
has unrelated dirty work and the executor cannot isolate the task safely,
return NEEDS_REVIEW rather than overwriting it.

## Image and SkyyRose tasks

Before planning, drafting, reviewing, or submitting image/video generation
prompts, read and cite
[/Users/theceo/.codex/creative-standards/imagery-prompting.md](/Users/theceo/.codex/creative-standards/imagery-prompting.md)
in the creative brief. Apply its collection understanding, natural scene
integration, fidelity, and review rules. Mark unsupported provider controls
not applicable. This requirement grants no generation, spend, or publishing
authority.

For SkyyRose products, read product facts only through
from skyyrose.core.product import get_product and the canonical
wordpress-theme/skyyrose-flagship/data/logo-registry.json. Founder Corey is the
maker and authority for his product details and supplied artwork. Preserve
founder-confirmed artwork, placement, wording, and dimensions. Report missing
registry facts as gaps; do not invent them. Keep evidence labels explicit:
source-verified, recorded observation, reproduced local test, or verified live.

## Examples and maintenance

Task-specific examples and their evidence limits are maintained in
[references/verified-examples.md](references/verified-examples.md). Do not
promote an illustrative example to an observed result. Authentication
observations identify the checked CLI and its permitted scope; they do not
prove a paid model request succeeded.

The canonical editable copy is .claude/skills/adversarial-planning. Keep the
tracked plugin distribution and active project/home installs synchronized with
scripts/sync_adversarial_planning_skill.py. Inspect divergent content before
replacing it. Run the helper with --check in validation and --sync only after
reviewing what will be replaced or pruned. Do not edit disposable plugin
caches.
