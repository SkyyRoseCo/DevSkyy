import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, realpathSync } from 'node:fs';
import path from 'node:path';

// lint-staged uses string-argv, not a shell: backslash quote escapes are not
// decoded. Choose an enclosing quote absent from the filename instead.
const quotePath = file => {
  if (!file.includes('"')) return `"${file}"`;
  if (!file.includes("'")) return `'${file}'`;
  throw new Error(`Cannot safely pass a filename containing both quote styles to lint-staged: ${file}`);
};

// Snapshot the index before formatters mutate it. A merge imports already
// committed files from MERGE_HEAD; only our changes and resolutions need fixes.
const repositoryRoot = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
const mergeHeadPath = execFileSync('git', ['rev-parse', '--git-path', 'MERGE_HEAD'], {
  cwd: repositoryRoot,
  encoding: 'utf8',
}).trim();
const mergeHeadFile = path.resolve(repositoryRoot, mergeHeadPath);
const mergeHeads = existsSync(mergeHeadFile)
  ? readFileSync(mergeHeadFile, 'utf8').trim().split(/\s+/).filter(Boolean)
  : [];
if (mergeHeads.length > 1) {
  throw new Error(
    'lint-staged does not support octopus merges; merge one branch at a time to preserve incoming files.'
  );
}
const mergeChanges =
  mergeHeads.length === 1
    ? new Set(
        execFileSync('git', ['diff', '--cached', '--name-only', '-z', '--no-renames', 'MERGE_HEAD', '--'], {
          cwd: repositoryRoot,
          encoding: 'utf8',
        })
          .split('\0')
          .filter(Boolean)
          .map(file => path.resolve(repositoryRoot, file))
      )
    : null;

// The files a program owns are listed ONCE, in data/machine-managed-files.json,
// with each file's owning program and the reason. This config reads that list
// instead of keeping its own copy: two hand-maintained lists is exactly how
// .wolf/buglog.json ended up in neither, and prettier rewrote 1,643 lines of it.
// tests/test_machine_managed_files.py fails if this file stops reading the
// registry, or if .prettierignore and the registry drift apart.
// Fails CLOSED and says why: without the registry there is no way to know which
// files a program owns, and the safe assumption is not "none of them". Raising
// here refuses the whole commit rather than letting formatters loose on
// generated output. lint-staged reports only "Failed to read config from file",
// so the cause has to come from this message.
const registryPath = path.join(repositoryRoot, 'data', 'machine-managed-files.json');
const managedPatterns = (() => {
  let entries;
  try {
    entries = JSON.parse(readFileSync(registryPath, 'utf8')).entries;
  } catch (error) {
    throw new Error(
      `lint-staged: cannot read the machine-managed-files registry at ${registryPath} ` +
        `(${error.message}). Refusing to run: without it this config cannot tell which ` +
        'files a program owns, and formatting one means fighting its generator forever.'
    );
  }
  if (!Array.isArray(entries) || entries.length === 0) {
    throw new Error(
      `lint-staged: ${registryPath} lists no entries. Refusing to run rather than treating ` +
        'an empty registry as "nothing is machine-managed".'
    );
  }
  return entries.map(entry => entry.pattern);
})();

// .prettierignore uses gitignore syntax; this covers the subset the registry
// uses: a leading "/" anchors to the repo root, a trailing "/" matches a whole
// directory, "**" spans directories and "*" stays within one segment.
const patternToRegExp = pattern => {
  let body = pattern.trim();
  const anchored = body.startsWith('/');
  if (anchored) body = body.slice(1);
  const directoryOnly = body.endsWith('/');
  if (directoryOnly) body = body.replace(/\/$/, '');
  // Decided while walking the segments rather than via a placeholder
  // character: a sentinel byte would make this file binary to git, and a
  // config nobody can read a line diff of is a config nobody reviews.
  const segments = body.split('/');
  let source = '';
  segments.forEach((segment, index) => {
    const last = index === segments.length - 1;
    if (segment === '**') {
      // Spans directories: 'a/**/b' must also match 'a/b'.
      source += last ? '.*' : '(?:.*/)?';
      return;
    }
    source += segment
      .replace(/[.+^${}()|[\]\\]/g, '\\$&')
      .replace(/\*/g, '[^/]*')
      .replace(/\?/g, '[^/]');
    if (!last) source += '/';
  });
  const prefix = anchored || body.includes('/') ? '^' : '^(?:.*/)?';
  return new RegExp(`${prefix}${source}${directoryOnly ? '(?:/.*)?' : ''}$`);
};

const managedMatchers = managedPatterns.map(patternToRegExp);

// Binaries are not in the registry because no formatter claims to own them;
// they are here so a media file staged alongside code never reaches a
// formatter command that would rewrite it.
const BINARY_FILE = /\.(?:png|jpe?g|webp|gif|avif|mp4|mov|webm|mp3|wav|flac|safetensors|ckpt|pt|pth|bin)$/i;

// Resolve directory aliases (for example /var versus /private/var on macOS)
// without following a symlink in the indexed filename itself. git reports the
// REAL path of the toplevel while a caller may hand us one that still goes
// through the symlink; comparing the two directly yields a "../../.." relative
// path that matches no pattern, which would silently protect nothing. Only the
// deepest EXISTING ancestor is resolved, because lint-staged also names deleted
// files and this must answer for a path rather than require one.
const canonicalFile = file => {
  const absolute = path.resolve(file);
  const trailing = [path.basename(absolute)];
  let current = path.dirname(absolute);
  for (;;) {
    try {
      return path.join(realpathSync(current), ...trailing);
    } catch {
      const parent = path.dirname(current);
      if (parent === current) return absolute;
      trailing.unshift(path.basename(current));
      current = parent;
    }
  }
};

const canonicalRoot = canonicalFile(repositoryRoot);

const isByteStableOrManaged = file => {
  const relative = path.relative(canonicalRoot, canonicalFile(file)).replace(/\\/g, '/');
  return managedMatchers.some(matcher => matcher.test(relative)) || BINARY_FILE.test(relative);
};

const mutableFiles = files =>
  files.filter(
    file => !isByteStableOrManaged(file) && (mergeChanges === null || mergeChanges.has(canonicalFile(file)))
  );

const commandsFor = (commands, files) => {
  const selected = mutableFiles(files);
  if (selected.length === 0) return [];
  const paths = selected.map(quotePath).join(' ');
  return commands.map(command => `${command} ${paths}`);
};

/** @type {import('lint-staged').Configuration} */
export default {
  // Python: normalize imports, apply safe lint fixes, format, then reject only
  // findings that cannot be fixed automatically. lint-staged appends paths.
  '*.py': files => commandsFor(['isort', 'ruff check --fix', 'black', 'ruff check'], files),

  // Prettier-supported source and content languages. Shell and TOML support
  // comes from the explicitly pinned plugins in .prettierrc.js.
  '*.{js,jsx,ts,tsx,mjs,cjs,json,jsonc,yaml,yml,md,mdx,css,scss,less,html,htm,graphql,gql,sh,bash,zsh,toml,sql,ipynb}':
    files => commandsFor(['prettier --write --ignore-unknown'], files),
  '*.{xml,svg}': files => commandsFor(['python3 scripts/format_markup.py'], files),
  '{Dockerfile,**/Dockerfile,.husky/*}': files => commandsFor(['prettier --write --ignore-unknown'], files),

  // Root application JS/TS: apply ESLint fixes after Prettier.
  'src/**/*.{ts,tsx,js,jsx,mjs,cjs}': files => commandsFor(['eslint --fix --no-error-on-unmatched-pattern'], files),

  // Frontend JS/TS: apply ESLint fixes on staged files only.
  // Do NOT use --max-warnings 0 (242 existing warnings would block every commit)
  // ESLint exits non-zero on errors, zero on warnings-only -- this is correct behavior
  // Must run from frontend/ dir -- root node_modules/eslint has ajv crash (ESLint v9 + @eslint/eslintrc)
  // A wrapper changes directory without nesting shell quoting inside string-argv.
  'frontend/**/*.{ts,tsx,js,jsx,mjs}': files => commandsFor(['bash scripts/lint-staged-frontend.sh'], files),

  // Frontend TypeScript type check: whole-project (function prevents file arg appending)
  // tsc ignores tsconfig.json when given individual file arguments on CLI
  'frontend/**/*.{ts,tsx}': files =>
    mutableFiles(files).length ? 'tsc --noEmit --project frontend/tsconfig.json' : [],

  // WordPress PHP: PHPCBF applies every safe WPCS fix before php -l validates
  // syntax. The formatter wrapper groups files by wordpress-theme/<theme>/ and
  // applies THAT theme's own ruleset (V1 `.phpcs.xml`, V2 `phpcs.xml` — text
  // domain, prefixes); a theme with
  // no ruleset is skipped with a notice, never formatted under another theme's
  // standard. The wrapper accepts PHPCBF's "changes applied" status.
  'wordpress-theme/**/*.php': files => commandsFor(['bash scripts/php-format.sh', 'bash scripts/php-lint.sh'], files),
};
