#!/usr/bin/env node
/**
 * scripts/verify-formatter-ignores.mjs — prove that Prettier cannot rewrite a
 * derived, vendored, or integrity-pinned file.
 *
 * Why this exists (2026-09-17, bug-332): lint-staged runs Prettier and RE-STAGES
 * what it formatted, AFTER the diff a human reviewed. Every pre-commit gate was
 * green and none could have caught it, because the damage happened between
 * approval and commit — it expanded three.module.min.js 691,648 -> 952,111 bytes
 * and mutated .wolf/anatomy.md's content (__init__.py -> **init**.py).
 *
 * Two classes are load-bearing:
 *   - BYTE-GATED: a generator owns the bytes and a gate compares them to a fresh
 *     build. A reformat makes that gate unsatisfiable — it reports STALE, --fix
 *     regenerates, lint-staged reformats again on the retry. The only exit is
 *     --no-verify, which is how a gate becomes a formality.
 *   - PINNED / SERVED: a sha256 pin or a production payload. A reformat breaks
 *     the pin or ships a file several times larger than the source it minifies.
 *
 * `prettier --check` passing is NOT proof of any of this: it reports success for
 * ignored files too. getFileInfo().ignored is the only thing that actually proves it.
 *
 * Fails CLOSED: an unreadable ignore file, a missing Prettier, or a path that has
 * disappeared is a failure, not a skip. A gate that cannot run has not passed.
 *
 * Usage: node scripts/verify-formatter-ignores.mjs [--quiet]
 */

import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { dirname, join, resolve } from 'node:path';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const QUIET = process.argv.includes('--quiet');

/**
 * One representative path per protected class. A class is listed here because a
 * named gate, pin, or production surface depends on its bytes — not because it
 * looks generated.
 */
const PROTECTED = [
  // Served to production; build-{css,js}.js --check owns them byte-for-byte.
  ['wordpress-theme/skyyrose-flagship/assets/js/product-3d-viewer.min.js', 'theme .min js (served in production)'],
  ['wordpress-theme/skyyrose-flagship/assets/css/single-product.min.css', 'theme .min css (served in production)'],
  // sha256-pinned vendored trees.
  [
    'wordpress-theme/skyyrose-flagship/assets/js/lib/three-0.170.0/three.module.min.js',
    'vendored three (VENDOR.md sha256)',
  ],
  [
    'wordpress-theme/skyyrose-flagship/assets/js/lib/three-0.170.0/basis/basis_transcoder.js',
    'vendored basis transcoder',
  ],
  ['wordpress-theme/skyyrose-flagship/assets/js/lib/draco/draco_decoder.js', 'vendored draco (flagship)'],
  ['wordpress-theme/skyyrose-flagship-2/assets/js/lib/draco/draco_decoder.js', 'vendored draco (flagship-2)'],
  ['public/draco/draco_decoder.js', 'vendored draco (dashboard)'],
  [
    'plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-architecture/SKILL.md',
    'vendored skill (source-registry.json sha256, 234 files)',
  ],
  // Byte-gated generator outputs.
  [
    'wordpress-theme/skyyrose-flagship/assets/css/design-tokens.css',
    'gen-design-tokens.py (verify-collection-sot byte check)',
  ],
  ['docs/campaigns/sot-lookbook.html', 'build-lookbook-from-sot.py (validate_catalog_consistency byte check)'],
  ['wordpress-theme/skyyrose-flagship/data/lookbook-sot.json', 'build-lookbook-sot.py (byte check)'],
  ['wordpress-theme/skyyrose-flagship/data/collections/black-rose/sot.json', 'build-collection-sot.py (byte check)'],
  [
    'wordpress-theme/skyyrose-flagship/data/dossiers/black-is-beautiful-jersey-series-0-baseball-classic-giants.md',
    'registry projection (sync_product_registry.py --check, CI)',
  ],
  // Tool-written: the writer owns the bytes, so a reformat is permanent churn.
  ['wordpress-theme/skyyrose-flagship/data/logo-registry.json', 'product registry SOT (registry update API writes it)'],
  ['wordpress-theme/skyyrose-flagship/data/editorial-index.json', 'build-editorial-index.js (tab-indented)'],
  ['wordpress-theme/skyyrose-flagship/data/collections/black-rose/index.html', 'gen-collection-hub.py (deployed)'],
  ['assets/products/manifest.json', 'build_asset_manifest.py (content-hashed)'],
  ['wordpress-theme/skyyrose-flagship/data/v7-cards.json', 'build_v7_cards.py (v7_cards_current CI byte check)'],
  ['wordpress-theme/skyyrose-flagship/data/site-guide.json', 'build-site-guide.py'],
  ['wordpress-theme/skyyrose-flagship/data/product-embeddings.json', 'generate_product_embeddings.py'],
  // Machine-maintained logs parsed line-by-line; proseWrap orphans continuation lines.
  ['.wolf/anatomy.md', 'OpenWolf anatomy (anatomy_filter_main.py parses per line)'],
  ['.wolf/memory.md', 'append-only cross-session log'],
  ['.wolf/cerebrum.md', 'cross-LLM learning log'],
  ['.wolf/buglog.json', 'bug ledger (wolf-memory MCP appends)'],
  ['tasks/phase-e-manifest.md', 'regen_phase_e_manifest_auto.py AUTO regions'],
];

/**
 * Prettier invoked from a subdirectory does NOT discover the repo-root
 * .prettierignore, so a package script that runs there needs --ignore-path or it
 * can re-create the whole damage class in one command.
 */
const SUBDIR_SCRIPTS = [['wordpress-theme/package.json', ['format', 'format:check'], '../.prettierignore']];

function fail(msg) {
  console.error(`\x1b[31m  ✗\x1b[0m ${msg}`);
  return 1;
}
function ok(msg) {
  if (!QUIET) console.log(`\x1b[32m  ✓\x1b[0m ${msg}`);
}

/**
 * Resolve Prettier from any workspace that installs it. The CI job with Node
 * (wordpress-theme) installs only its own dependencies, so a root-only lookup
 * would fail there and turn a tooling gap into a red gate. Ignore matching is
 * gitignore-style and does not differ between 3.x minors, so either copy proves
 * the same thing.
 */
const require = createRequire(import.meta.url);
let prettier = null;
const searched = [];
for (const base of [ROOT, join(ROOT, 'wordpress-theme'), join(ROOT, 'frontend')]) {
  searched.push(base);
  try {
    prettier = require(require.resolve('prettier', { paths: [base] }));
    break;
  } catch {
    /* try the next workspace */
  }
}
if (!prettier) {
  console.error(
    `\x1b[31m  ✗\x1b[0m cannot load prettier from any of: ${searched.join(', ')} —\n` +
      `      the ignore gate could not run, so it fails closed. Run npm install.`
  );
  process.exit(1);
}

const ignorePath = join(ROOT, '.prettierignore');
try {
  readFileSync(ignorePath, 'utf8');
} catch (err) {
  console.error(`\x1b[31m  ✗\x1b[0m cannot read .prettierignore: ${err.message}`);
  process.exit(1);
}

let failures = 0;

for (const [rel, why] of PROTECTED) {
  const abs = join(ROOT, rel);
  // getFileInfo() never touches the disk: it answers `ignored: true` for a path
  // that does not exist, as long as a rule matches the string. So a renamed or
  // re-versioned file (three-0.170.0 -> three-0.171.0) would leave this entry
  // passing while verifying nothing. A representative that is gone is a failure.
  if (!existsSync(abs)) {
    failures += fail(
      `${rel} does not exist — ${why}.\n` +
        `      The gate cannot vouch for a file it cannot see. If it moved, update PROTECTED\n` +
        `      (and check the new path is still covered by .prettierignore).`
    );
    continue;
  }
  let info;
  try {
    info = await prettier.getFileInfo(abs, { ignorePath });
  } catch (err) {
    failures += fail(`${rel} — getFileInfo threw: ${err.message}`);
    continue;
  }
  if (!info.ignored) {
    failures += fail(
      `${rel} is NOT ignored by prettier — ${why}.\n` +
        `      lint-staged would reformat and re-stage it after your diff was reviewed.\n` +
        `      Fix: add a rule covering it to .prettierignore.`
    );
  }
}

for (const [pkgRel, scriptNames, expectedFlag] of SUBDIR_SCRIPTS) {
  let pkg;
  try {
    pkg = JSON.parse(readFileSync(join(ROOT, pkgRel), 'utf8'));
  } catch (err) {
    failures += fail(`${pkgRel} — could not read/parse: ${err.message}`);
    continue;
  }
  for (const name of scriptNames) {
    if (typeof pkg.scripts?.[name] !== 'string') {
      failures += fail(`${pkgRel} script "${name}" is missing — the ignore gate cannot verify it.`);
    }
  }
  // Every script that runs prettier, not only the ones named above: a later
  // "format:all" would otherwise reformat the vendored tree with this gate still green.
  for (const [name, body] of Object.entries(pkg.scripts ?? {})) {
    if (typeof body === 'string' && /\bprettier\b/.test(body) && !body.includes(`--ignore-path ${expectedFlag}`)) {
      failures += fail(
        `${pkgRel} script "${name}" runs prettier without --ignore-path ${expectedFlag}.\n` +
          `      From that directory prettier does not see the repo-root .prettierignore,\n` +
          `      so one run reformats every .min and vendored file under it.`
      );
    }
  }
}

if (failures === 0) {
  ok(`${PROTECTED.length} derived/pinned paths are prettier-ignored; subdirectory scripts carry --ignore-path`);
  process.exit(0);
}
console.error(`\x1b[31mformatter-ignore gate: ${failures} unprotected path(s)\x1b[0m`);
process.exit(1);
