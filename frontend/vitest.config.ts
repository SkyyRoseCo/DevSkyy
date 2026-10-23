import path from 'node:path';

import { defineConfig } from 'vitest/config';

// Scoped deliberately, not by default glob. Most of the dashboard cannot be
// imported under vitest: `lib/wp/client.ts` sits behind a `server-only`
// boundary the resolver cannot satisfy, and anything reaching into next-auth
// or next/server drags the framework in. Both included patterns are
// framework-free by construction:
//   - lib/wp/**       — the WP-wiring modules (auth-policy, signature, throttle)
//   - tests/**        — node-only suites; api-auth-coverage reads route files
//                       from disk and imports only lib/api-public-routes,
//                       which has no imports at all.
// Keep that property when adding a suite here. A test that cannot import its
// subject gets skipped, and a skipped security test reads exactly like a
// passing one.
export default defineConfig({
  test: {
    environment: 'node',
    include: [
      'lib/wp/**/*.test.ts', 'tests/**/*.test.ts',
      // Bounded provider client and isolated React form with mocked API transport.
      'lib/api/endpoints/god-mode.test.ts',
      'app/admin/god-mode/page.test.tsx',
    ],
    // tests/e2e is Playwright's (playwright.config.ts testDir) — running those
    // specs under vitest fails on missing Playwright globals, not on the code.
    exclude: ['**/node_modules/**', '**/.git/**', 'tests/e2e/**'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
});
