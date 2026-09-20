#!/usr/bin/env node
/**
 * Ask prettier and lint-staged themselves whether they would rewrite a file a
 * program owns.
 *
 * tests/test_machine_managed_files.py checks that the registry, .prettierignore
 * and this config agree on PAPER, with no dependencies, so it runs everywhere.
 * This script checks the same thing in PRACTICE — prettier's own ignore
 * resolution, and the real lint-staged task functions — which needs node and
 * node_modules, so it runs in the pre-commit hook and anywhere node is set up.
 *
 * Fails closed: a missing registry, an unreadable config or a sample that no
 * longer exists is an error, not a pass.
 *
 * Usage: node scripts/verify-formatter-ignores.mjs
 */

import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const repositoryRoot = execFileSync('git', ['rev-parse', '--show-toplevel'], {
  encoding: 'utf8',
}).trim();

const registryPath = path.join(repositoryRoot, 'data', 'machine-managed-files.json');
const failures = [];

const fail = message => failures.push(message);

if (!existsSync(registryPath)) {
  console.error(`verify-formatter-ignores: registry missing at ${registryPath}`);
  process.exit(1);
}

const registry = JSON.parse(readFileSync(registryPath, 'utf8'));
if (!Array.isArray(registry.entries) || registry.entries.length === 0) {
  console.error('verify-formatter-ignores: registry has no entries — refusing to pass');
  process.exit(1);
}

// Load prettier without exiting yet: the lint-staged half below needs only
// node and the config, so a checkout missing node_modules/prettier should
// still get that verdict. Absence is reported as a failure at the end — the
// gate never passes on a check it could not run.
let prettier = null;
let prettierError = null;
try {
  prettier = await import('prettier');
} catch (error) {
  prettierError =
    `cannot load prettier (${error.message}), so prettier's own ignore resolution is ` +
    'UNVERIFIED. Run npm install at the repo root.';
}

const lintStaged = await import(path.join(repositoryRoot, 'lint-staged.config.mjs')).catch(error => {
  console.error(`verify-formatter-ignores: cannot load lint-staged.config.mjs (${error.message})`);
  process.exit(1);
});
const tasks = Object.entries(lintStaged.default ?? {});
if (tasks.length === 0) {
  console.error('verify-formatter-ignores: lint-staged config exported no tasks');
  process.exit(1);
}

const commandsFor = file => {
  const produced = [];
  for (const [glob, task] of tasks) {
    const result = typeof task === 'function' ? task([file]) : task;
    const commands = Array.isArray(result) ? result : result ? [result] : [];
    if (commands.length > 0) produced.push([glob, commands[0].split(' ')[0]]);
  }
  return produced;
};

// Positive control. lint-staged reads the same registry this script does, so a
// registered file is skipped by construction — without this, "lint-staged would
// not touch it" could just mean the filter is inert and the check could never
// fail. An unowned file must still be picked up.
const control = ['README.md', 'package.json', 'pyproject.toml']
  .map(name => path.join(repositoryRoot, name))
  .find(existsSync);
if (!control) {
  console.error('verify-formatter-ignores: no control file found — cannot prove the filter works');
  process.exit(1);
}
if (commandsFor(control).length === 0) {
  console.error(
    `verify-formatter-ignores: lint-staged selects no task for ${path.basename(control)}, ` +
      'which nothing owns — the filter is inert, so its verdict on managed files is worthless'
  );
  process.exit(1);
}

for (const entry of registry.entries) {
  for (const sample of entry.samples) {
    const absolute = path.join(repositoryRoot, sample);
    if (!existsSync(absolute)) {
      // Worktrees are sparse; only judge what is actually here.
      continue;
    }

    if (prettier) {
      const info = await prettier.getFileInfo(absolute, {
        ignorePath: path.join(repositoryRoot, '.prettierignore'),
        resolveConfig: false,
      });
      if (!info.ignored) {
        fail(
          `prettier would format ${sample} (pattern ${entry.pattern}) — owned by ${entry.owner}`
        );
      }
    }

    // Catches a pattern lint-staged's translation gets wrong (anchoring, "**",
    // directory patterns) even though .prettierignore reads it correctly.
    for (const [glob, command] of commandsFor(absolute)) {
      fail(`lint-staged task ${glob} would run ${command} on ${sample} — owned by ${entry.owner}`);
    }
  }
}

if (failures.length > 0 || prettierError) {
  console.error('verify-formatter-ignores: machine-managed files are not protected:\n');
  for (const failure of failures) {
    console.error(`  - ${failure}`);
  }
  if (prettierError) console.error(`  - ${prettierError}`);
  console.error(
    '\nAdd the pattern to .prettierignore (and data/machine-managed-files.json) so the\n' +
      "formatter and the file's owning program stop overwriting each other."
  );
  process.exit(1);
}

const checked = registry.entries.reduce((total, entry) => total + entry.samples.length, 0);
console.log(
  `verify-formatter-ignores: ${registry.entries.length} patterns / ${checked} sample files ` +
    'are invisible to prettier and lint-staged'
);
