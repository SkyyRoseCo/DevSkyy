'use strict';
/** Archive projection of one canonical stylesheet; never a rendered-DOM purge. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const THEME = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const postcss = require(path.join(THEME, 'node_modules/postcss'));
const CleanCSS = require(path.join(THEME, 'node_modules/clean-css'));
const GROUPS = {
  content: ['sr2-journal', 'sr2-journal-entry', 'sr2-journal-card', 'sr2-journal-fallback', 'sr2-story', 'sr2-search', 'sr2-not-found', 'sr2-generic-page', 'sr2-generic-head', 'sr2-page-copy', 'sr2-page-hero', 'sr2-preorder-hero', 'sr2-preorder-steps', 'sr2-commerce-preview', 'sr2-service-links', 'sr2-page', 'sr2-page-arrival', 'sr2-page-grid', 'sr2-index-list', 'sr2-press-list', 'sr2-garment-grid', 'sr2-title-editorial', 'sr2-wishlist'],
  transactions: ['sr2-cart', 'sr2-c-cart', 'sr2-c-summary', 'sr2-c-checkout', 'sr2-c-account', 'sr2-c-service', 'sr2-checkout', 'sr2-thankyou', 'woocommerce-checkout', 'woocommerce-account', 'woocommerce-cart', 'woocommerce-form-track-order', 'woocommerce-checkout-review-order'],
  legacyWorlds: ['sr-home', 'sr2-black-rose-scene', 'sr2-scene-hotspot', 'sr2-scene-card'],
  // 2026-09-22 whole-site primitives owned by world/home/PDP chapters. The Shop archive composes
  // sr2-band / sr2-title-display / sr2-lede / sr2-editorial-link only, so those stay unowned.
  editorialWorlds: ['sr2-arrival', 'sr2-chapter', 'sr2-title-chapter'],
  product: ['sr2-c-variation', 'sr2-c-option-list', 'sr2-c-option', 'woocommerce-product-details__short-description', 'variations_form'],
};
const CONSUMERS = {
  content: ['page.php', 'index.php', 'home.php', 'archive.php', 'single.php', 'search.php', '404.php', 'template-parts/v2-commerce-preview.php', 'template-parts/journal-press-fallback.php', 'page-wishlist.php', 'page-lookbook.php', 'template-parts/v2-about.php', 'template-parts/v2-preorder.php', 'template-parts/pages/contact.php', 'template-parts/pages/service.php', 'template-parts/pages/journal-entry.php'],
  transactions: ['woocommerce/cart/cart.php', 'woocommerce/checkout/form-checkout.php', 'woocommerce/checkout/thankyou.php', 'page.php', 'template-parts/v2-commerce-preview.php'],
  legacyWorlds: ['assets/css/legacy-world-components.css', 'preserved non-archive legacy component contract'],
  editorialWorlds: ['front-page.php', '404.php', 'template-parts/home/editorial-hero.php', 'template-parts/home/editorial-collection.php', 'template-parts/collections/arrival.php', 'template-parts/collections/chapters.php', 'template-parts/collections/story.php', 'template-parts/collections/index.php', 'template-parts/collections/next-world.php', 'template-parts/immersive/world.php', 'template-parts/commerce/town-line.php', 'woocommerce/single-product.php', 'template-parts/v2-preorder.php'],
  product: ['woocommerce/single-product.php', 'template-parts/commerce/product-hero.php'],
};
const INPUTS = ['design-tokens', 'shop-page', 'controls', 'global-shell', 'visual-recovery', 'mascot'];
const INLINE_ALLOWANCE = 100000;
const INLINE_WARNING = 96000;
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function classifySelector(selector) {
  // Only a positive, leading owner class is eligible. :not/:has and arbitrary
  // ancestor mentions cannot establish ownership of a matched Shop element.
  const match = selector.trim().match(/^\.([a-zA-Z0-9_-]+)(?=[\s.:#>+~\[]|$)/);
  if (match) {
    for (const [group, families] of Object.entries(GROUPS)) {
      if (families.some(family => match[1] === family || match[1].startsWith(family + '__') || match[1].startsWith(family + '--'))) return group;
    }
  }
  if (/^\.woocommerce\s+div\.product(?=[\s.:#>+~\[]|$)/.test(selector.trim())) return 'product';
  return null;
}
function project(source) {
  const tree = postcss.parse(source);
  const classification = [];
  let index = 0;
  tree.walkRules(rule => {
    const ancestors = [];
    for (let node = rule.parent; node && node.type !== 'root'; node = node.parent) ancestors.unshift('@' + node.name + ' ' + node.params);
    const keyframe = ancestors.some(value => /^@(?:-\w+-)?keyframes\b/.test(value));
    const selectors = postcss.list.comma(rule.selector);
    const owners = selectors.map(classifySelector);
    const excluded = !keyframe && selectors.length > 0 && owners.every(Boolean);
    classification.push({ index: index++, selector: rule.selector, wrappers: ancestors, ruleSha256: sha(rule.toString()), disposition: excluded ? 'EXCLUDE_FROM_NATIVE_ARCHIVE' : 'PRESERVE', owners: excluded ? [...new Set(owners)] : [] });
    if (excluded) rule.remove();
  });
  tree.walkAtRules(rule => { if (rule.nodes && rule.nodes.length === 0) rule.remove(); });
  const result = new CleanCSS({ level: { 1: { specialComments: 0 } } }).minify(tree.toString());
  assert.equal(result.errors.length, 0, result.errors.join('\n'));
  return { css: result.styles, classification };
}
function safe(root, name) {
  assert.ok(/^[a-z-]+(?:\.min)?\.(?:css|json)$/.test(name), 'Unsafe projection path');
  const file = path.join(root, name);
  for (let entry = file; ; entry = path.dirname(entry)) {
    try { assert.ok(!fs.lstatSync(entry).isSymbolicLink(), 'Symlink projection path'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (path.dirname(entry) === entry) break;
  }
  return file;
}
function build({ root = path.join(THEME, 'assets/css'), check = false } = {}) {
  const source = fs.readFileSync(safe(root, 'theme.css'));
  const fullMin = fs.readFileSync(safe(root, 'theme.min.css'));
  const projection = project(source.toString());
  const bytes = Buffer.from(projection.css);
  const manifest = {
    schema: 'skyyrose.archive-theme-projection.v1',
    toolchain: { postcss: require(path.join(THEME, 'node_modules/postcss/package.json')).version, cleanCss: require(path.join(THEME, 'node_modules/clean-css/package.json')).version },
    source: { file: 'theme.css', sha256: sha(source), bytes: source.length },
    originalMin: { file: 'theme.min.css', sha256: sha(fullMin), bytes: fullMin.length },
    output: { file: 'archive-theme.min.css', sha256: sha(bytes), bytes: bytes.length },
    ownerFamilies: GROUPS, ownerConsumers: CONSUMERS, classification: projection.classification,
  };
  assert.deepEqual(manifest.toolchain, { postcss: '8.5.28', cleanCss: '5.3.3' }, 'Unpinned projection toolchain');
  const outputs = [['archive-theme.min.css', bytes], ['archive-theme.json', Buffer.from(JSON.stringify(manifest, null, 2) + '\n')]];
  // Original component bytes remain independently delivered by native Core.
  const sources = INPUTS.map(name => {
    const file = name + '.min.css';
    const bytes = fs.readFileSync(safe(root, file));
    return { file, sha256: sha(bytes), bytes: bytes.length };
  });
  const receipt = { schema: 'skyyrose.archive-style-inputs.v1', sources };
  // inc/archive-style-bundle.php only inlines the Shop sheets while all seven stay within Core's widened 100,000 B allowance.
  const inlineTotal = bytes.length + sources.reduce((total, row) => total + row.bytes, 0);
  assert.ok(inlineTotal <= INLINE_ALLOWANCE, 'Shop inline allowance exceeded: ' + inlineTotal + ' B > ' + INLINE_ALLOWANCE);
  if (inlineTotal > INLINE_WARNING) console.warn('archive-style-bundle: Shop inline total ' + inlineTotal + ' B is within ' + (INLINE_ALLOWANCE - inlineTotal) + ' B of the ' + INLINE_ALLOWANCE + ' B allowance');
  outputs.push(['archive-style-inputs.json', Buffer.from(JSON.stringify(receipt, null, 2) + '\n')]);
  outputs.forEach(([name]) => safe(root, name));
  for (const [name, payload] of outputs) {
    const destination = safe(root, name);
    if (check) { assert.ok(fs.existsSync(destination) && fs.readFileSync(destination).equals(payload), 'Stale archive projection: ' + name); continue; }
    const temporary = destination + '.' + crypto.randomUUID() + '.tmp';
    try { fs.writeFileSync(temporary, payload, { flag: 'wx' }); safe(root, name); fs.renameSync(temporary, destination); }
    finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
  }
  return manifest;
}
module.exports = { INPUTS, GROUPS, INLINE_ALLOWANCE, project, classifySelector, safe, sha, build };
if (require.main === module) console.log(build({ check: process.argv.includes('--check') }).output);
