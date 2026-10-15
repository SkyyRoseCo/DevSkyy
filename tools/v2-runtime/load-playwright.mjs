/**
 * Fail-closed Playwright resolution for the browser-based release tools.
 *
 * Resolution order: the repository root install (npm install at the repo
 * root declares @playwright/test), a DEVSKYY_ROOT override, the primary
 * DevSkyy checkout under the home directory (git worktrees have no root
 * node_modules), then any install visible from this file. When none resolves
 * the tool prints one UNVERIFIED line and exits 3 so a missing harness is
 * never mistaken for a passing measurement or policy run.
 */
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';

export function loadPlaywright() {
  const candidates = [
    ['repository root', new URL('../../package.json', import.meta.url)],
    ['DEVSKYY_ROOT', process.env.DEVSKYY_ROOT ? path.join(process.env.DEVSKYY_ROOT, 'package.json') : null],
    ['primary checkout', path.join(os.homedir(), 'DevSkyy', 'package.json')],
    ['tool location', import.meta.url],
  ].filter(([, base]) => base);
  const tried = [];
  for (const [label, base] of candidates) {
    const require = createRequire(base);
    for (const name of ['@playwright/test', 'playwright']) {
      try {
        return require(name);
      } catch (error) {
        if (error.code !== 'MODULE_NOT_FOUND') throw error;
        tried.push(`${name} via ${label}`);
      }
    }
  }
  console.error('UNVERIFIED: playwright not installed — run `npm install` at the repository root (or set DEVSKYY_ROOT to a checkout that has it).');
  console.error(`  tried: ${tried.join('; ')}`);
  process.exit(3);
}
