import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { backupMode } from './lint-staged-backup-mode.mjs';

function fixture(t, migrate = false) {
  const root = mkdtempSync(path.join(tmpdir(), 'staged-backup-test-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const git = (...args) => execFileSync('git', args, { cwd: root, stdio: 'pipe' });
  git('init');
  mkdirSync(path.join(root, 'skill'));
  writeFileSync(path.join(root, 'skill/SKILL.md'), 'original');
  writeFileSync(path.join(root, 'note.md'), 'original');
  git('add', '.');
  git(
    '-c',
    'user.name=Test',
    '-c',
    'user.email=test@example.invalid',
    '-c',
    'core.hooksPath=/dev/null',
    'commit',
    '-m',
    'fixture'
  );
  if (migrate) {
    rmSync(path.join(root, 'skill'), { recursive: true });
    mkdirSync(path.join(root, 'canonical'));
    symlinkSync('canonical', path.join(root, 'skill'));
  }
  return { root, git };
}

test('ordinary work keeps automatic stash backups', t => {
  assert.equal(backupMode(fixture(t).root), '');
});
test('migration permits fully staged files and preserves unrelated work', t => {
  const { root, git } = fixture(t, true);
  writeFileSync(path.join(root, 'note.md'), 'review');
  git('add', 'note.md');
  const before = git('diff').toString();
  assert.equal(backupMode(root), '--no-stash');
  assert.equal(git('diff').toString(), before);
});
test('migration refuses partial staging', t => {
  const { root, git } = fixture(t, true);
  writeFileSync(path.join(root, 'note.md'), 'staged');
  git('add', 'note.md');
  writeFileSync(path.join(root, 'note.md'), 'unstaged');
  assert.throws(() => backupMode(root), /partially staged/);
});
test('normal partial staging retains the original stash path', t => {
  const { root, git } = fixture(t);
  writeFileSync(path.join(root, 'note.md'), 'staged');
  git('add', 'note.md');
  writeFileSync(path.join(root, 'note.md'), 'unstaged');
  assert.equal(backupMode(root), '');
});
