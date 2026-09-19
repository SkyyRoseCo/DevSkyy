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

const isByteStableOrManaged = file => {
  const normalized = file.replace(/\\/g, '/');
  return (
    /(^|\/)plugins\/fashion-theme-team\//.test(normalized) ||
    /(^|\/)Comfy\/receipts\//.test(normalized) ||
    /(^|\/)Comfy\/quarantine\//.test(normalized) ||
    // Canonical dossier generation owns these bytes; generic Markdown
    // formatting would desynchronize the checked-in placement brief.
    /(^|\/)skyyrose\/elite_studio\/assets\/golden\/[^/]+\/placement\.md$/.test(normalized) ||
    // The product registry and its dossier projections are byte-compared by
    // sync_product_registry.py --check and the registry is sha256-pinned in the
    // asset manifest; reformatting either one desynchronizes the SOT. The root
    // logo-registry.json is a symlink, so a write through it lands on the registry.
    /(^|\/)logo-registry\.json$/.test(normalized) ||
    /(^|\/)wordpress-theme\/skyyrose-flagship\/data\/dossiers\/[^/]+\.md$/.test(normalized) ||
    /\.(?:png|jpe?g|webp|gif|avif|mp4|mov|webm|mp3|wav|flac|safetensors|ckpt|pt|pth|bin)$/i.test(normalized)
  );
};

// Resolve directory aliases (for example /var versus /private/var on macOS)
// without following a symlink in the indexed filename itself.
const canonicalFile = file => path.join(realpathSync(path.dirname(file)), path.basename(file));
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
