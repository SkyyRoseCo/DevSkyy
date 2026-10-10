/** Runtime CSS owns primitives; this adapter projects supported values into the editor. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

function readTokens(css) {
  const root = css.match(/:root\s*\{([^}]+)\}/);
  assert(root, 'Missing canonical root token block');
  return Object.fromEntries([...root[1].matchAll(/--sr2-([\w-]+):\s*([^;]+);/g)].map(m => [m[1], m[2].trim()]));
}
function resolveToken(tokens, name, ancestors = []) {
  assert(tokens[name], `Missing token ${name}`);
  assert(!ancestors.includes(name), `Cyclic token reference: ${[...ancestors, name].join(' -> ')}`);
  return tokens[name].replace(/var\(--sr2-([\w-]+)\)/g, (_, ref) => resolveToken(tokens, ref, [...ancestors, name]));
}
function projectTokens(current, tokens) {
  const next = structuredClone(current);
  const token = name => resolveToken(tokens, name);
  const mapEntries = (entries, mapping, key) => {
    for (const [slug, name] of Object.entries(mapping)) {
      const entry = entries.find(p => p.slug === slug);
      assert(entry, `Missing editor preset ${slug}`);
      entry[key] = key === 'color' ? token(name).toUpperCase() : token(name);
    }
  };
  mapEntries(
    next.settings.color.palette,
    {
      'concrete-black': 'void',
      surface: 'surface-commerce',
      white: 'white',
      'text-secondary': 'color-text',
      'text-muted': 'color-text-muted',
      border: 'border-solid',
      'rose-gold': 'rose',
      'signature-gold': 'gold',
      'black-rose-silver': 'silver',
      'love-hurts-crimson': 'crimson',
    },
    'color'
  );
  mapEntries(
    next.settings.spacing.spacingSizes,
    {
      '2-xs': 'space-1',
      xs: 'space-2',
      small: 'space-4',
      medium: 'space-6',
      large: 'space-10',
      xl: 'space-16',
      '2-xl': 'space-24',
    },
    'size'
  );
  mapEntries(
    next.settings.typography.fontFamilies,
    {
      archivo: 'font-display',
      'hanken-grotesk': 'font-body',
      anton: 'font-ui',
      cinzel: 'font-caps',
    },
    'fontFamily'
  );
  mapEntries(
    next.settings.typography.fontSizes,
    {
      small: 'type-utility',
      body: 'type-body',
      lead: 'type-editorial',
      'display-small': 'type-editorial',
      display: 'type-display',
    },
    'size'
  );
  for (const role of ['monument', 'commerce', 'index']) {
    const existing = next.settings.typography.fontSizes.find(p => p.slug === role);
    const entry = { name: role[0].toUpperCase() + role.slice(1), slug: role, size: token(`type-${role}`) };
    if (existing) Object.assign(existing, entry);
    else next.settings.typography.fontSizes.push(entry);
  }
  Object.assign(next.settings.layout, { contentSize: token('content'), wideSize: token('wide') });
  Object.assign(next.settings.custom.motion, {
    'house-ease': token('ease'),
    fast: token('fast'),
    standard: token('normal'),
    slow: token('slow'),
    micro: token('motion-micro'),
    interface: token('motion-interface'),
    editorial: token('motion-editorial'),
    scene: token('motion-scene'),
    commerce: token('motion-commerce'),
    cinematic: token('motion-cinematic'),
    character: token('motion-character'),
    reveal: token('motion-reveal'),
    exit: token('motion-exit'),
    'micro-ease': token('ease-micro'),
    'spring-ease': token('ease-spring'),
    'enter-ease': token('ease-enter'),
    'exit-ease': token('ease-exit'),
    'expressive-ease': token('ease-expressive'),
    distance: token('motion-distance'),
    stagger: token('motion-stagger'),
  });
  next.settings.custom.materials = Object.fromEntries(
    ['paper', 'ink', 'glass', 'metal', 'atmosphere'].map(name => [name, token(`material-${name}`)])
  );
  next.settings.custom.layers = Object.fromEntries(
    [
      'content',
      'floating',
      'commerce',
      'guide',
      'header',
      'scrim',
      'drawer',
      'navigation',
      'modal',
      'toast',
      'critical',
      'skip',
    ].map(name => [name, token(`layer-${name}`)])
  );
  Object.assign(next.settings.custom.focus, {
    color: token('focus-outer'),
    inner: token('focus-inner'),
    width: token('focus-width'),
    offset: token('focus-offset'),
  });
  next.settings.custom.controls = {
    size: token('control-size'),
    target: token('target-size'),
    border: token('border-control'),
  };
  next.settings.custom.layout = {
    reading: token('reading'),
    commerce: token('commerce-width'),
    gap: token('grid-gap'),
  };
  next.settings.custom.typeRoles = Object.fromEntries(
    ['monument', 'display', 'editorial', 'commerce', 'body', 'utility', 'index'].map(role => [
      role,
      {
        size: token(`type-${role}`),
        family: token(
          role === 'index'
            ? 'font-index'
            : ['monument', 'display', 'editorial'].includes(role)
              ? 'font-display'
              : role === 'utility'
                ? 'font-ui'
                : 'font-body'
        ),
        leading: token(`leading-${role === 'index' ? 'utility' : role}`),
      },
    ])
  );
  // Editor buttons use the same legible dark-on-accent treatment as native storefront buttons.
  next.styles.elements.button.color.text = 'var(--wp--preset--color--concrete-black)';
  next.styles.typography.lineHeight = token('leading-body');
  next.styles.color.text = 'var(--wp--preset--color--text-secondary)';
  return next;
}
function main() {
  const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
  const css = fs.readFileSync(path.join(theme, 'assets/css/design-tokens.css'), 'utf8');
  const file = path.join(theme, 'theme.json');
  const current = JSON.parse(fs.readFileSync(file, 'utf8'));
  const next = projectTokens(current, readTokens(css));
  if (process.argv.includes('--write')) {
    if (JSON.stringify(current) !== JSON.stringify(next)) fs.writeFileSync(file, JSON.stringify(next, null, 2) + '\n');
  } else assert.deepEqual(current, next, 'Editor tokens drift from runtime contract; run build:tokens');
  console.log('PASS runtime/editor colors, layout, type roles, spacing, controls, focus, motion and layer contract');
}
if (require.main === module) main();
module.exports = { readTokens, resolveToken, projectTokens };
