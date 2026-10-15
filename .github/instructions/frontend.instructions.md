---
applyTo: 'frontend/**/*.{ts,tsx,js,jsx,css,scss}'
---

# Next.js frontend review guidance

- Follow the owning `frontend/AGENTS.md`, package scripts, and nearby route or
  component conventions. Preserve the React Server Component default; verify
  client boundaries, server-only secrets, environment handling, and API
  authorization at the point data is read or changed.
- Validate remote and route payloads at runtime, handle non-OK, malformed,
  unavailable, and aborted requests explicitly, and avoid retaining stale or
  misleading values after refresh failure. Use strict types; do not paper over
  data shape problems with `any` or unchecked assertions.
- For analytics, preserve configured site/environment scope, accepted-consent
  requirements, authentication, and synthetic-event exclusion. Only show
  verified purchases/revenue; keep unsupported attribution, consented-purchase,
  spend, and ROAS values unavailable instead of inferring them.
- For UI changes, check keyboard access, labels and announcements, focus,
  loading/error/empty states, small viewports, and hydration behavior. For
  commerce or dashboard flows, follow the data through the page, API route, and
  backend contract; a mock or HTTP 200 alone is not end-to-end evidence.
- Frontend checks belong in `frontend/`: `npm test`, `npm run type-check`,
  `npm run lint`, and `npm run build`, as applicable. Report only checks
  actually run and distinguish unit tests from browser/live validation.
