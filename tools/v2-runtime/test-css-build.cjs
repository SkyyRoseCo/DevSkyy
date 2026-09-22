const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { createRequire } = require('node:module');

const themeDir = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const themeRequire = createRequire(path.join(themeDir, 'package.json'));
const postcss = themeRequire('postcss');

// Copy the actual builder, preserving its theme-relative layout. Dependency
// imports are read from the installed theme toolchain; all generated writes
// and intentionally malformed sources stay in the disposable fixture.
function fixture(t) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'sr2-css-build-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  fs.mkdirSync(path.join(directory, 'scripts'));
  fs.mkdirSync(path.join(directory, 'assets', 'css'), { recursive: true });
  fs.mkdirSync(path.join(directory, 'assets', 'js'), { recursive: true });
  fs.copyFileSync(path.join(themeDir, 'scripts', 'build-assets.mjs'), path.join(directory, 'scripts', 'build-assets.mjs'));
  fs.symlinkSync(path.join(themeDir, 'node_modules'), path.join(directory, 'node_modules'), 'dir');
  const css = name => path.join(directory, 'assets', 'css', name);
  const js = name => path.join(directory, 'assets', 'js', name);
  const run = (...args) => spawnSync(process.execPath, [path.join(directory, 'scripts', 'build-assets.mjs'), ...args], {
    cwd: directory,
    encoding: 'utf8',
    timeout: 15_000,
  });
  return { css, js, run };
}

for (const mode of [[], ['--check']]) {
  test(`actual CSS builder rejects a swallowed-selector declaration before any writes (${mode.length ? 'check' : 'build'})`, t => {
    const f = fixture(t);
    fs.writeFileSync(f.css('a-valid.css'), '.a { padding: 0; border: 1px solid white; }\n.b { display: flex; }\n');
    fs.writeFileSync(f.css('a-valid.min.css'), '/* preserve last accepted output */');
    // CleanCSS alone silently rewrites this to .a{padding:0}b.b{display:flex}.
    fs.writeFileSync(f.css('z-malformed.css'), '.a{padding:0;b}.b{display:flex}');
    fs.writeFileSync(f.js('later.js'), 'window.fixture = true;');
    const result = f.run(...mode);
    assert.equal(result.error, undefined);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stderr, /z-malformed\.css:1:\d+/);
    assert.match(result.stderr, /Unknown word/);
    assert.equal(fs.readFileSync(f.css('a-valid.min.css'), 'utf8'), '/* preserve last accepted output */');
    assert.equal(fs.existsSync(f.css('z-malformed.min.css')), false);
    assert.equal(fs.existsSync(f.js('later.min.js')), false);
  });
}

test('actual CSS builder preserves separate valid neighboring rules and verifies deterministic output', t => {
  const f = fixture(t);
  fs.writeFileSync(f.css('valid.css'), '.a { padding: 0; border: 1px solid #fff; }\n.b { display: flex; }\n@media (max-width: 48em) { .b { display: grid; } }\n');
  fs.writeFileSync(f.js('valid.js'), 'window.fixture = 1 + 2;');
  const built = f.run();
  assert.equal(built.error, undefined);
  assert.equal(built.status, 0, built.stderr);
  assert.match(built.stdout, /Built 1 CSS and 1 JS assets/);
  const output = fs.readFileSync(f.css('valid.min.css'), 'utf8');
  const rules = postcss.parse(output).nodes;
  assert.deepEqual(rules.filter(node => node.type === 'rule').map(node => node.selector), ['.a', '.b']);
  assert(rules[0].nodes.some(node => node.prop === 'border' && node.value === '1px solid #fff'));
  assert(rules[1].nodes.some(node => node.prop === 'display' && node.value === 'flex'));
  assert(rules.some(node => node.type === 'atrule' && node.nodes[0].selector === '.b'));
  assert.equal(fs.existsSync(f.js('valid.min.js')), true);
  const checked = f.run('--check');
  assert.equal(checked.status, 0, checked.stderr);
  assert.equal(fs.readFileSync(f.css('valid.min.css'), 'utf8'), output);
  fs.appendFileSync(f.css('valid.css'), '\n.c { display: block; }');
  const stale = f.run('--check');
  assert.equal(stale.status, 1, stale.stderr);
  assert.match(stale.stderr, /Generated assets are stale or missing/);
  assert.equal(fs.readFileSync(f.css('valid.min.css'), 'utf8'), output, 'check mode must not rewrite stale output');
});

test('actual CSS builder rejects an unclosed rule with source location', t => {
  const f = fixture(t);
  fs.writeFileSync(f.css('unclosed.css'), '.a { padding: 0;\n.b { display: flex; }');
  const result = f.run();
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /unclosed\.css:1:1/);
  assert.match(result.stderr, /Unclosed block/);
  assert.equal(fs.existsSync(f.css('unclosed.min.css')), false);
});
