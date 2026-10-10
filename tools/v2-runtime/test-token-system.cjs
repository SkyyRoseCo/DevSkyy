const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {readTokens, resolveToken, projectTokens} = require('./sync-token-contract.cjs');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const tokens = readTokens(fs.readFileSync(path.join(theme, 'assets/css/design-tokens.css'), 'utf8'));
const editor = JSON.parse(fs.readFileSync(path.join(theme, 'theme.json'), 'utf8'));
function luminance(hex) {
  const expanded = hex.length === 4 ? '#' + [...hex.slice(1)].map(c => c + c).join('') : hex;
  const rgb = expanded.slice(1).match(/../g).map(c => parseInt(c, 16) / 255).map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4);
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
}
function contrast(a, b) { const values = [luminance(a), luminance(b)].sort((x,y) => y-x); return (values[0]+.05)/(values[1]+.05); }
test('editor projection is stable and preserves unrelated extension settings', () => {
  const input = structuredClone(editor);
  input.settings.custom.extension = {owner:'fixture',enabled:true};
  input.settings.color.palette.push({name:'Extension',slug:'fixture',color:'#abC123'});
  const before = structuredClone(input);
  const output = projectTokens(input, tokens);
  assert.deepEqual(input, before, 'projector must not mutate its input');
  assert.deepEqual(output.settings.custom.extension, input.settings.custom.extension);
  assert.deepEqual(output.settings.color.palette.at(-1), input.settings.color.palette.at(-1));
  assert.deepEqual(projectTokens(output, tokens), output, 'second projection must have no drift');
  assert.deepEqual(projectTokens(editor, tokens), editor, 'committed editor contract must be current');
});
test('runtime neutral/layout and semantic role changes reach the editor', () => {
  const changed = {...tokens, wide:'1600px', ink:'#ededed', 'type-commerce':'1.375rem'};
  const output = projectTokens(editor, changed);
  assert.equal(output.settings.layout.wideSize, '1600px');
  assert.equal(output.settings.color.palette.find(p => p.slug === 'text-secondary').color, '#EDEDED');
  assert.equal(output.settings.custom.typeRoles.commerce.size, '1.375rem');
  assert.equal(output.settings.typography.fontSizes.find(p => p.slug === 'commerce').size, '1.375rem');
});
test('missing and cyclic token graphs fail rather than silently generating broken editor CSS', () => {
  assert.throws(() => resolveToken(tokens, 'missing'), /Missing token/);
  assert.throws(() => resolveToken({a:'var(--sr2-b)',b:'var(--sr2-a)'}, 'a'), /Cyclic token/);
  const incomplete = {...tokens}; delete incomplete['font-display'];
  assert.throws(() => projectTokens(editor, incomplete), /Missing token font-display/);
});
test('house and collection action fills preserve normal-size label contrast', () => {
  for (const name of ['rose','gold','silver','crimson']) {
    assert(contrast(resolveToken(tokens,name), resolveToken(tokens,'color-on-action')) >= 4.5, `${name} action label contrast`);
  }
  for (const name of ['surface-page','surface-commerce','surface-raised']) {
    assert(contrast(resolveToken(tokens,'color-text'),resolveToken(tokens,name)) >= 4.5, `${name} text contrast`);
    assert(contrast(resolveToken(tokens,'color-text-muted'),resolveToken(tokens,name)) >= 4.5, `${name} secondary text contrast`);
    assert(contrast(resolveToken(tokens,'border-control'),resolveToken(tokens,name)) >= 3, `${name} control boundary contrast`);
  }
});
test('focus distinguishes light and dark surfaces and the layer order is strict', () => {
  assert(contrast(resolveToken(tokens,'focus-inner'),resolveToken(tokens,'focus-outer')) >= 3);
  const ordered = ['content','floating','commerce','guide','header','scrim','drawer','navigation','modal','toast','critical','skip'].map(name => Number(resolveToken(tokens,`layer-${name}`)));
  assert(ordered.every((value,index) => index === 0 || value > ordered[index-1]));
  assert.equal(resolveToken(tokens,'motion-interface'),resolveToken(tokens,'normal'));
});

// Model CSS inheritance at a child context: root aliases are already computed,
// then only declarations matching that child are recomputed. This catches aliases
// that look correct in the root source but keep the wrong inherited color.
function computeContext(css, selector, inherited) {
  const specified = {...inherited};
  for (const match of css.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    if (!match[1].split(',').map(part => part.trim()).includes(selector)) continue;
    Object.assign(specified, readTokens(`:root {${match[2]}}`));
  }
  return Object.fromEntries(Object.keys(specified).map(name => [name,resolveToken(specified,name)]));
}
test('collection action and legacy focus resolve from the local collection rather than inherited house rose', () => {
  const css = fs.readFileSync(path.join(theme, 'assets/css/design-tokens.css'), 'utf8');
  const inherited = Object.fromEntries(Object.keys(tokens).map(name => [name,resolveToken(tokens,name)]));
  for (const [slug,primitive] of Object.entries({signature:'gold','black-rose':'silver','love-hurts':'crimson','kids-capsule':'rose'})) {
    const context = computeContext(css, `[data-collection="${slug}"]`, inherited);
    assert.equal(context['color-action'],resolveToken(tokens,primitive),`${slug} local action color`);
    assert(context.focus.includes(resolveToken(tokens,primitive)),`${slug} local legacy focus accent`);
    assert(contrast(context['color-action'],context['color-on-action']) >= 4.5);
  }
});
test('light context maintains text and disabled-control contrast on every declared surface', () => {
  const css = fs.readFileSync(path.join(theme, 'assets/css/controls.css'), 'utf8');
  const inherited = Object.fromEntries(Object.keys(tokens).map(name => [name,resolveToken(tokens,name)]));
  const context = computeContext(css,'.sr2-surface--light',inherited);
  for (const name of ['surface-page','surface-commerce','surface-dialog','surface-raised']) {
    assert(contrast(context['color-text'],context[name]) >= 4.5,`light ${name} text`);
    assert(contrast(context['color-text-muted'],context[name]) >= 4.5,`light ${name} secondary/disabled text`);
  }
  assert(contrast(context['focus-inner'],context['focus-outer']) >= 3);
});

test('every source spacing reference resolves so route padding cannot become invalid at computed-value time', () => {
  const directory = path.join(theme, 'assets/css');
  for (const file of fs.readdirSync(directory).filter(name => name.endsWith('.css') && !name.endsWith('.min.css'))) {
    const css = fs.readFileSync(path.join(directory, file), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
    for (const match of css.matchAll(/var\(--sr2-(space-\d+)\s*\)/g)) {
      assert.doesNotThrow(() => resolveToken(tokens, match[1]), `${file}: ${match[1]} must exist`);
    }
  }
});
