import { execFileSync } from 'node:child_process';
import { lstatSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

/** Git cannot stash tracked descendants of a directory replaced by a symlink. */
export function backupMode(root) {
  const names = args => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).split('\0').filter(Boolean);
  const tracked = names(['ls-files', '-z']);
  const blocked = tracked.some(name => {
    let parent = path.dirname(name);
    while (parent !== '.') {
      try {
        if (lstatSync(path.join(root, parent)).isSymbolicLink()) return true;
      } catch (error) {
        if (error.code !== 'ENOENT' && error.code !== 'ENOTDIR') throw error;
      }
      parent = path.dirname(parent);
    }
    return false;
  });
  if (!blocked) return '';
  const staged = new Set(names(['diff', '--cached', '--name-only', '-z']));
  if (names(['diff', '--name-only', '-z']).some(name => staged.has(name))) {
    throw new Error(
      'Skill symlink migration prevents Git backup, and partially staged files need that backup. Fully stage only the intended files or finish the migration before committing.'
    );
  }
  return '--no-stash';
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    const root = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
    const mode = backupMode(root);
    if (mode)
      process.stderr.write(
        'Tracked files beneath migrated symlinks prevent Git backup; running staged checks without stash (no partially staged files).\n'
      );
    process.stdout.write(mode);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
