# Testing Requirements

Coverage threshold (85%) and the TDD loop live in root `CLAUDE.md` §3.

Test Types (ALL required):

1. **Unit Tests** - Individual functions, utilities, components
2. **Integration Tests** - API endpoints, database operations (in
   `tests/integration/`)
3. **E2E Tests** - Critical user flows (Playwright)

No mocks in integration/e2e tests.

## Agent Support

- **tdd-guide** - Use PROACTIVELY for new features, enforces write-tests-first
- **e2e-runner** - Playwright E2E testing specialist
