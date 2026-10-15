# CRITICAL WORKFLOW DIRECTIVE - DO NOT SKIP

## User's Explicit Instruction

**Date**: 2025-12-25
**Context**: During codebase refactor and TypeScript compilation fixes

### THE RULE

**DO NOT MOVE ON TO ANY TASK UNTIL ALL ERRORS ARE FIXED**

When encountering errors (TypeScript, pre-commit hooks, linting, etc.):

1. STOP all forward progress
2. FIX the error completely
3. VERIFY the fix works
4. ONLY THEN proceed to next task

### Current Blocking Errors Status

**RESOLVED**: All TypeScript compilation errors fixed (23 errors resolved)

- ✅ api/agents.py indentation fixed
- ✅ HotspotManager callback signatures fixed
- ✅ Window.lottie global declaration added
- ✅ ParticleConfig null type fixed
- ✅ All raycaster intersection null checks added
- ✅ userData property access fixed with bracket notation
- ✅ Unused variables removed
- Commit: `1be47198 fix(typescript): resolve all TypeScript compilation errors`

- **RUFF/LINTING**: Multiple issues in various files:
  - Type annotation style (UP007: use `X | Y` instead of `Union[X, Y]`)
  - Unused variables (F841)
  - isinstance checks (UP038)
  - SIM118 violations

- **MARKDOWN**: Various missing language specifications in code blocks

### DO NOT PROCEED TO

- Phase 1 git commit
- Phase 2 file deletions
- Phase 3 requirements consolidation
- Phase 4 config fixes
- Phase 5 logging conversion
- Phase 6 documentation

**UNTIL ALL ABOVE ERRORS ARE RESOLVED**

### Acknowledgment

User explicitly stated this while in the middle of fixing TypeScript compilation errors. This takes absolute priority over all other tasks and cleanup work.
