# Agent Orchestration

## Available Agents

Located in `~/.claude/agents/`:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| planner | Implementation planning | Complex features, refactoring |
| architect | System design | Architectural decisions |
| tdd-guide | Test-driven development | New features, bug fixes |
| code-reviewer | Code review | After writing code |
| security-reviewer | Security analysis | Before commits |
| build-error-resolver | Fix build errors | When build fails |
| e2e-runner | E2E testing | Critical user flows |
| refactor-cleaner | Dead code cleanup | Code maintenance |
| doc-updater | Documentation | Updating docs |
| python-reviewer | Python code review | Python code changes |
| typescript-reviewer | TS/JS code review | Frontend code changes |

## Model Routing

Project default is `"model": "opusplan"` in `.claude/settings.json`: Opus in plan
mode (shift+tab), Sonnet once the plan is approved and execution starts. Opus plans,
Sonnet builds; flip back to plan mode for a new feature, a design trade-off, or a
fix that failed once.

Subagent model resolution (Claude Code sub-agents docs, verified 2026-10-14):

1. the per-invocation `model` parameter
2. the agent file's `model` frontmatter (`inherit` = the main conversation's model)
3. `CLAUDE_CODE_SUBAGENT_MODEL` (this repo: `fable`)
4. the main conversation's model

`CLAUDE_CODE_SUBAGENT_MODEL` alone does not change the built-in Explore and Plan
subagents; that also needs `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`. Every agent in
`.claude/agents/` pins its own `model`, so the env var only reaches unpinned agents.
Pin mechanical agents (search, docs, build errors) to `haiku`, implementers to
`sonnet`, planners and red-team reviewers to `opus` or `fable`.

## Immediate Agent Usage

No user prompt needed:

1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Bug fix or new feature - Use **tdd-guide** agent
4. Architectural decision - Use **architect** agent
