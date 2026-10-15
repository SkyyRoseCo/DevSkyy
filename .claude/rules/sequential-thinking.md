# Sequential Thinking (Auto-Trigger)

Use the Sequential Thinking MCP tool
(`mcp__sequential-thinking__sequentialthinking`) **proactively** — do not wait
for the user to ask.

## When to Use

Automatically invoke sequential thinking when:

- **Multi-step planning**: Tasks requiring 3+ implementation steps with
  dependencies
- **Complex debugging**: Bugs with multiple possible root causes or cross-file
  interactions
- **Architecture decisions**: Trade-offs between approaches, system design,
  refactoring strategy
- **Dependency analysis**: Determining execution order, identifying circular
  dependencies, migration planning
- **Ambiguous requirements**: Breaking down vague requests into concrete,
  ordered action items

## When NOT to Use

Skip sequential thinking for:

- Simple file edits, renames, or single-step fixes
- Direct questions with factual answers (use Read/Grep instead)
- Tasks where the path forward is obvious and unambiguous
- Quick lookups or status checks

## Usage Pattern

1. Call the tool at the START of complex tasks, before writing any code
2. Use `thought` parameter to reason through each step
3. Set `nextThoughtNeeded: true` to continue chains until resolution
4. The final thought should produce a concrete action plan
5. Then execute the plan — do not re-deliberate unless blocked
