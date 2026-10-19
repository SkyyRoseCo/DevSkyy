# Workflow Orchestration

> Operating doctrine for any non-trivial work in DevSkyy. Pairs with
> [development-workflow.md](./development-workflow.md) (the _what_ — research,
> TDD, review) and [agents.md](./agents.md) (the _who_ — which agents to
> invoke).

This file governs _how_ a task moves from request → done: when to plan, when to
delegate, how to verify, how to learn from corrections.

---

## 1. Subagent Strategy

- Use subagents liberally to keep the main context window clean.
- Offload research, exploration, and parallel analysis to subagents.
- For complex problems, throw more compute at it via subagents.
- One task per subagent for focused execution.

> Subagent selection lives in [agents.md](./agents.md). Default to parallel
> dispatch when work is independent.

## 2. Self-Improvement Loop

- After ANY correction from the user: update `tasks/lessons.md` with the
  pattern.
- Write rules for yourself that prevent the same mistake.
- Ruthlessly iterate on these lessons until mistake rate drops.
- Review lessons at session start for the relevant project.

> This rule operationalizes the **Self-Correction** clause in `CLAUDE.md`: fix →
> name lesson → commit fix + lesson together. Cerebrum (`.wolf/cerebrum.md`) and
> `tasks/lessons.md` are both update targets — cerebrum for project-wide
> gotchas, `tasks/lessons.md` for behavioral patterns.

## 3. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant
  solution."
- Skip this for simple, obvious fixes — don't over-engineer.
- Challenge your own work before presenting it.

> Balance against the existing **Critical Rules**: don't add abstractions beyond
> what the task requires. Elegance ≠ premature abstraction. Three similar lines
> beats a generic helper used once.
