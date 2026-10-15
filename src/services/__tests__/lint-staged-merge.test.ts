import { execFileSync, spawnSync } from 'node:child_process';
import {
  chmodSync,
  copyFileSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';

const fixtures: string[] = [];
// Tests live under src/services/__tests__, three levels below repository root.
const source = path.resolve(import.meta.dirname, '../../../lint-staged.config.mjs');
// The config reads the machine-managed-files registry to decide which files a
// program owns. A fixture repo without it is not a repo this config can run in
// -- it fails closed by design, which `refuses to run without the registry`
// below pins down.
const registry = path.resolve(path.dirname(source), 'data/machine-managed-files.json');

function fixture() {
  const cwd = mkdtempSync(path.join(tmpdir(), 'devskyy-merge-hook-'));
  fixtures.push(cwd);
  const git = (...args: string[]) =>
    execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
  git('init', '-b', 'main');
  git('config', 'user.name', 'Offline Test');
  git('config', 'user.email', 'offline@example.invalid');
  git('config', 'core.hooksPath', '.no-hooks');
  git('config', 'commit.gpgsign', 'false');
  copyFileSync(source, path.join(cwd, 'lint-staged.config.mjs'));
  mkdirSync(path.join(cwd, 'data'), { recursive: true });
  copyFileSync(registry, path.join(cwd, 'data/machine-managed-files.json'));
  const write = (file: string, content: string) => {
    mkdirSync(path.dirname(path.join(cwd, file)), { recursive: true });
    writeFileSync(path.join(cwd, file), content);
  };
  const commit = (message: string) => {
    git('add', '.');
    git('commit', '-m', message);
  };
  return { cwd, git, write, commit };
}

afterEach(() => {
  for (const directory of fixtures.splice(0)) rmSync(directory, { recursive: true, force: true });
});

function commands(cwd: string, files: string[], afterImport = ''): Record<string, string | string[]> {
  const script = `import config from './lint-staged.config.mjs';
    import {execFileSync} from 'node:child_process';
    ${afterImport}
    const files = ${JSON.stringify(files.map(file => path.join(cwd, file)))};
    process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(config).map(([pattern, task]) => [pattern, task(files)]))));`;
  return JSON.parse(execFileSync(process.execPath, ['--input-type=module', '-e', script], { cwd, encoding: 'utf8' }));
}

describe('merge-aware lint-staged selection', () => {
  it('excludes byte-identical incoming files and unstaged changes across every task', () => {
    const repo = fixture();
    repo.write('base.txt', 'base');
    repo.commit('base');
    repo.git('checkout', '-b', 'incoming');
    const incoming = [
      'frontend/page.tsx',
      'src/incoming.ts',
      'script.py',
      'Dockerfile',
      'wordpress-theme/theme.php',
      'asset.svg',
    ];
    for (const file of incoming) repo.write(file, 'incoming bytes\n');
    repo.commit('incoming');
    repo.git('checkout', 'main');
    repo.git('merge', '--no-ff', '--no-commit', 'incoming');
    // An unstaged difference must not put an otherwise incoming file in scope.
    repo.write('frontend/page.tsx', 'unstaged edit\n');
    for (const value of Object.values(commands(repo.cwd, incoming))) expect(value).toEqual([]);
  });

  it('includes own staged changes and conflict resolutions, snapshotting before mutation', () => {
    const repo = fixture();
    repo.write('src/conflict.ts', 'base\n');
    repo.commit('base');
    repo.git('checkout', '-b', 'incoming');
    repo.write('src/conflict.ts', 'incoming\n');
    repo.commit('incoming');
    repo.git('checkout', 'main');
    repo.write('src/conflict.ts', 'ours\n');
    repo.commit('ours');
    expect(spawnSync('git', ['merge', '--no-ff', '--no-commit', 'incoming'], { cwd: repo.cwd }).status).toBe(1);
    repo.write('src/conflict.ts', 'resolved\n');
    repo.write('frontend/own.tsx', 'own\n');
    repo.git('add', 'src/conflict.ts', 'frontend/own.tsx');
    const result = commands(
      repo.cwd,
      ['src/conflict.ts', 'frontend/own.tsx'],
      "execFileSync('git', ['restore', '--source=MERGE_HEAD', '--staged', 'src/conflict.ts']);"
    );
    expect(result['src/**/*.{ts,tsx,js,jsx,mjs,cjs}']).toEqual([expect.stringContaining('src/conflict.ts')]);
    expect(result['frontend/**/*.{ts,tsx}']).toBe('tsc --noEmit --project frontend/tsconfig.json');
    expect(result['frontend/**/*.{ts,tsx,js,jsx,mjs}']).toEqual([expect.stringContaining('own.tsx')]);
  });

  it('keeps ordinary staged files eligible while preserving managed-byte exclusions', () => {
    const repo = fixture();
    repo.write('src/own.ts', 'own\n');
    repo.commit('base');
    const result = commands(repo.cwd, ['src/own.ts']);
    expect(result['src/**/*.{ts,tsx,js,jsx,mjs,cjs}']).toEqual([expect.stringContaining('src/own.ts')]);
    for (const value of Object.values(
      commands(repo.cwd, [
        'Comfy/receipts/receipt.json',
        'plugins/fashion-theme-team/SKILL.md',
        'skyyrose/elite_studio/assets/golden/lh-004/placement.md',
        'logo-registry.json',
        'wordpress-theme/skyyrose-flagship/data/logo-registry.json',
        'wordpress-theme/skyyrose-flagship/data/dossiers/black-rose-crewneck.md',
        'art.png',
      ])
    ))
      expect(value).toEqual([]);
  });
});

const lintStagedCli = path.resolve(path.dirname(source), 'node_modules/lint-staged/bin/lint-staged.js');

function runLintStaged(cwd: string) {
  return spawnSync(process.execPath, [lintStagedCli, '--config', 'test-config.mjs', '--concurrent', 'false'], {
    cwd,
    encoding: 'utf8',
    env: { ...process.env, PATH: `${path.join(cwd, 'bin')}${path.delimiter}${process.env.PATH ?? ''}` },
  });
}

function executable(repo: ReturnType<typeof fixture>, name: string, body: string) {
  repo.write(`bin/${name}`, `#!${process.execPath}\n${body}`);
  chmodSync(path.join(repo.cwd, 'bin', name), 0o755);
}

describe('real lint-staged execution', () => {
  it('refuses an empty frontend file list rather than running broad ESLint fixes', () => {
    const result = spawnSync('bash', [path.resolve(path.dirname(source), 'scripts/lint-staged-frontend.sh')], {
      encoding: 'utf8',
    });
    expect(result.status).toBe(1);
    expect(result.stderr).toContain('at least one staged filename');
  });

  it('passes exactly the intended frontend argv for plain, space, and apostrophe filenames', () => {
    const repo = fixture();
    repo.write('scripts/.keep', '');
    copyFileSync(
      path.resolve(path.dirname(source), 'scripts/lint-staged-frontend.sh'),
      path.join(repo.cwd, 'scripts/lint-staged-frontend.sh')
    );
    repo.write(
      'test-config.mjs',
      "import config from './lint-staged.config.mjs'; export default {'frontend/*.ts': config['frontend/**/*.{ts,tsx,js,jsx,mjs}']};"
    );
    repo.write(
      'frontend/node_modules/.bin/eslint',
      `#!${process.execPath}\nrequire('node:fs').writeFileSync('../argv.json', JSON.stringify(process.argv.slice(2)));`
    );
    chmodSync(path.join(repo.cwd, 'frontend/node_modules/.bin/eslint'), 0o755);
    repo.commit('base');
    const files = ['frontend/plain.ts', 'frontend/with space.ts', "frontend/o'neil.ts", 'frontend/double"quote.ts'];
    for (const file of files) repo.write(file, 'const value = 1;\n');
    repo.git('add', ...files);
    const result = runLintStaged(repo.cwd);
    expect(result.status, result.stdout + result.stderr).toBe(0);
    const argv = JSON.parse(readFileSync(path.join(repo.cwd, 'argv.json'), 'utf8')) as string[];
    expect(argv.slice(0, 2)).toEqual(['--fix', '--']);
    expect(
      argv
        .slice(2)
        .map(file => path.relative(realpathSync(repo.cwd), file))
        .sort()
    ).toEqual(files.sort());
  });

  it.each([false, true])('preserves partial staging through the normal stash workflow (failure=%s)', failure => {
    const repo = fixture();
    repo.write(
      'test-config.mjs',
      "import config from './lint-staged.config.mjs'; const key = Object.keys(config).find(key => key.startsWith('*.{js,')); export default {'*.txt': config[key]};"
    );
    executable(
      repo,
      'prettier',
      `const fs = require('node:fs'); for (const file of process.argv.slice(2).filter(arg => !arg.startsWith('--'))) { const text = fs.readFileSync(file, 'utf8'); if (text.includes('UNSTAGED')) throw new Error('Unstaged content leaked into formatter'); fs.writeFileSync(file, text.replace('STAGED', 'FORMATTED')); } process.exit(${failure ? 1 : 0});`
    );
    const baseline = ['base', ...Array.from({ length: 12 }, (_, index) => `line ${index}`), 'last', ''].join('\n');
    repo.write('sample.txt', baseline);
    repo.commit('base');
    const staged = baseline.replace('base', 'STAGED');
    const working = staged.replace('last', 'UNSTAGED');
    repo.write('sample.txt', staged);
    repo.git('add', 'sample.txt');
    repo.write('sample.txt', working);
    const result = runLintStaged(repo.cwd);
    expect(result.status, result.stdout + result.stderr).toBe(failure ? 1 : 0);
    expect(repo.git('show', ':sample.txt')).toBe((failure ? staged : staged.replace('STAGED', 'FORMATTED')).trim());
    expect(readFileSync(path.join(repo.cwd, 'sample.txt'), 'utf8')).toBe(
      failure ? working : working.replace('STAGED', 'FORMATTED')
    );
    expect(repo.git('stash', 'list')).toBe('');
  });

  it.each([
    ['missing', null],
    ['empty', '{"entries": []}'],
  ])('refuses to run when the machine-managed registry is %s', (_label, contents) => {
    // An unreadable or empty registry must BLOCK, not quietly mean "no file is
    // machine-managed" -- that reading is the fail-open shape (bug-230) which
    // would hand every generated file straight to a formatter.
    const repo = fixture();
    const registryInRepo = path.join(repo.cwd, 'data/machine-managed-files.json');
    if (contents === null) rmSync(registryInRepo);
    else writeFileSync(registryInRepo, contents);
    repo.write('sample.txt', 'x\n');
    repo.commit('base');

    const result = spawnSync(
      process.execPath,
      [
        '--input-type=module',
        '-e',
        "import('./lint-staged.config.mjs').catch(e => {console.error(e.message); process.exit(1);})",
      ],
      { cwd: repo.cwd, encoding: 'utf8' }
    );
    expect(result.status, result.stdout + result.stderr).toBe(1);
    expect(result.stderr).toContain('Refusing to run');
    expect(result.stderr).toContain('machine-managed-files.json');
  });

  it('rejects an actual octopus merge instead of treating its first head as the entire baseline', () => {
    const repo = fixture();
    repo.write('base.txt', 'base');
    repo.commit('base');
    repo.git('checkout', '-b', 'one');
    repo.write('one.txt', 'one');
    repo.commit('one');
    repo.git('checkout', 'main');
    repo.git('checkout', '-b', 'two');
    repo.write('two.txt', 'two');
    repo.commit('two');
    repo.git('checkout', 'main');
    repo.git('merge', '--no-ff', '--no-commit', 'one', 'two');
    expect(() => commands(repo.cwd, ['one.txt', 'two.txt'])).toThrow(/octopus merges/);
  });
});
