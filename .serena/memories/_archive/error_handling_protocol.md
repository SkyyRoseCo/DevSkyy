# Error Handling Protocol

## CRITICAL RULE: Never Skip Errors

When ANY error occurs during development, testing, or deployment:

### 1. ACKNOWLEDGE

- Stop current task immediately
- Read and understand the full error message
- Identify root cause before proceeding

### 2. FIX

- Address the error directly - no workarounds
- If the error reveals a deeper issue, fix that too
- Test the fix to confirm it resolves the issue

### 3. HARDEN

- Add validation/guards to prevent similar errors
- Update tests to catch this case
- Consider if other code has the same vulnerability
- Document the fix if it's a pattern others should know

### 4. VERIFY

- Re-run the operation that failed
- Confirm zero errors before moving on
- Check for any related issues exposed by the fix

## Anti-Patterns to Avoid

- ❌ `continue-on-error: true` without handling
- ❌ Skipping failing tests
- ❌ Suppressing warnings without investigation
- ❌ Moving on with "will fix later"
- ❌ Assuming errors are "just noise"

## Examples

### Bad

```bash
# Just move on and hope it works
python script.py || true
```

### Good

```bash
# Acknowledge, fix, verify
python script.py
if [ $? -ne 0 ]; then
    echo "ERROR: Script failed - investigating..."
    # Fix the issue
    # Re-run to verify
fi
```

## Apply To

- CI/CD pipeline failures
- Test failures
- Linting/type errors
- Security scan findings
- Runtime exceptions
- Build errors
- Import errors

**Remember: Every error is a signal. Ignoring it creates tech debt and production risk.**
