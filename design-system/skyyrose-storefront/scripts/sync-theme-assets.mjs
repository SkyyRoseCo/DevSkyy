// scripts/sync-theme-assets.mjs
// One-way sync: WP theme assets -> package src. `--check` asserts no drift (exit 1 on diff).
import { readFileSync, writeFileSync, mkdirSync, readdirSync, copyFileSync, existsSync, unlinkSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const PKG = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const THEME = resolve(PKG, '../../wordpress-theme/skyyrose-flagship')
const CHECK = process.argv.includes('--check')

// [source theme file, dest package file] — verbatim CSS copies (single source of truth).
const CSS_MAP = [
  ['assets/css/design-tokens.css', 'src/tokens/tokens.css'],
  ['assets/css/commercial-polish.css', 'src/styles/commercial-polish.css'],
  ['assets/css/product-card-holo.css', 'src/components/HoloCard/holo-card.css'],
]

// Font directory: woff2 files live directly in assets/fonts/.
const FONT_DIR = resolve(THEME, 'assets/fonts')
const FONT_DEST = resolve(PKG, 'src/fonts')

// ---------------------------------------------------------------------------
// CANON font set — the ONLY families referenced by DS components + tokens.
// Source of truth = data/brand/typography.json (SOT.md) + shipped assets/fonts/*.woff2:
//   - universal roles (in theme.json fontFamilies -> woff2Map): Archivo (display),
//     Hanken Grotesk (body/UI), Anton (UI caps/accent), Cinzel (engraved accent), Inter (fallback)
//   - per-collection name-scripts (NOT in theme.json fontFamilies -> CURATED below):
//     SkyyRose Black Rose Script, SkyyRose Love Hurts Graffiti, Pinyon Script, Grand Hotel
//   - RETIRED 2026-07-10, excluded: Playfair Display, Cormorant Garamond, Bebas Neue, Yellowtail
//     (woff2 removed from the theme). Pacifico/Kaushan Script were removed 2026-10-14,
//     superseded by the bespoke BR/LH scripts.
// ---------------------------------------------------------------------------
const CANON_WOFF2 = new Set([
  'archivo-latin.woff2',
  'hanken-grotesk-latin.woff2',
  'anton-latin.woff2',
  'cinzel-latin.woff2',
  'inter-latin.woff2',
  'inter-latin-ext.woff2',
  'skyyrose-black-rose-script-latin.woff2',
  'skyyrose-love-hurts-graffiti-latin.woff2',
  'pinyon-script-latin.woff2',
  'grand-hotel-latin.woff2',
])

let drift = 0
function ensure(dir) { mkdirSync(dir, { recursive: true }) }

for (const [rel, dstRel] of CSS_MAP) {
  const src = readFileSync(resolve(THEME, rel), 'utf8')
  const dstPath = resolve(PKG, dstRel)
  ensure(dirname(dstPath))
  let cur = ''
  try { cur = readFileSync(dstPath, 'utf8') } catch { /* missing */ }
  if (CHECK) {
    if (cur !== src) { console.error(`DRIFT: ${dstRel} differs from theme ${rel}`); drift++ }
  } else {
    writeFileSync(dstPath, src)
    console.log(`synced ${dstRel}`)
  }
}

// ---------------------------------------------------------------------------
// Font sync: parse theme.json fontFamilies to get AUTHORITATIVE family names,
// weights, and styles — but filter to CANON_WOFF2 only (legacy families are
// excluded). Collection script fonts not in theme.json fontFamilies (Yellowtail,
// Pinyon Script, Kaushan Script) use a curated name map.
// ---------------------------------------------------------------------------

function buildFontsCss() {
  const themeJsonPath = resolve(THEME, 'theme.json')
  const themeData = JSON.parse(readFileSync(themeJsonPath, 'utf8'))
  const fontFamilies = themeData?.settings?.typography?.fontFamilies ?? []

  // Build woff2 -> { family, weight, style } from theme.json, canon-filtered.
  const woff2Map = new Map()
  for (const fam of fontFamilies) {
    // family name may be a comma-separated stack like "'Inter', -apple-system, ..."
    const familyName = fam.fontFamily.split(',')[0].trim().replace(/^['"]|['"]$/g, '')
    for (const face of (fam.fontFace ?? [])) {
      for (const src of (face.src ?? [])) {
        // src format: "file:./assets/fonts/<filename>.woff2"
        const m = src.match(/file:\.\/assets\/fonts\/(.+\.woff2)/)
        if (m && CANON_WOFF2.has(m[1])) {
          woff2Map.set(m[1], {
            family: familyName,
            weight: face.fontWeight ?? '400',
            style: face.fontStyle ?? 'normal',
          })
        }
      }
    }
  }

  // Curated names for collection script fonts not in theme.json fontFamilies.
  // These names match the per-collection --skyyrose-font-script values in tokens.css
  // (BR=SkyyRose Black Rose Script, LH=SkyyRose Love Hurts Graffiti, SIG=Pinyon Script, KC=Grand Hotel).
  const CURATED = new Map([
    ['skyyrose-black-rose-script-latin.woff2',   { family: 'SkyyRose Black Rose Script',   weight: '400', style: 'normal' }],
    ['skyyrose-love-hurts-graffiti-latin.woff2', { family: 'SkyyRose Love Hurts Graffiti', weight: '400', style: 'normal' }],
    ['pinyon-script-latin.woff2',                { family: 'Pinyon Script',                weight: '400', style: 'normal' }],
    ['grand-hotel-latin.woff2',                  { family: 'Grand Hotel',                  weight: '400', style: 'normal' }],
  ])

  // Iterate canon set in deterministic order for reproducible output.
  const lines = []
  for (const f of [...CANON_WOFF2].sort()) {
    const meta = woff2Map.get(f) ?? CURATED.get(f)
    if (!meta) {
      // Should not happen — CANON_WOFF2 is curated; warn loudly.
      console.warn(`sync: no family mapping for canon file ${f} — check theme.json or CURATED map`)
      continue
    }
    lines.push(
      `@font-face{font-family:'${meta.family}';src:url('./${f}') format('woff2');` +
      `font-weight:${meta.weight};font-style:${meta.style};font-display:swap;}`
    )
  }
  return lines.join('\n') + '\n'
}

ensure(FONT_DEST)
const generatedFontsCss = buildFontsCss()
const fontsCssPath = resolve(FONT_DEST, 'fonts.css')
let curFonts = ''
try { curFonts = readFileSync(fontsCssPath, 'utf8') } catch { /* missing */ }

if (CHECK) {
  // Verify only canon files are present and match the theme source.
  for (const f of CANON_WOFF2) {
    const dst = resolve(FONT_DEST, f)
    let same = false
    try { same = readFileSync(dst).equals(readFileSync(resolve(FONT_DIR, f))) } catch { same = false }
    if (!same) { console.error(`DRIFT: font ${f} missing/differs`); drift++ }
  }
  // Verify no legacy woff2 files remain in src/fonts/.
  const destFiles = readdirSync(FONT_DEST).filter((f) => f.endsWith('.woff2'))
  for (const f of destFiles) {
    if (!CANON_WOFF2.has(f)) { console.error(`DRIFT: legacy font ${f} present in src/fonts/ — remove it`); drift++ }
  }
  if (curFonts !== generatedFontsCss) { console.error('DRIFT: fonts.css out of date'); drift++ }
} else {
  // Copy only canon files.
  for (const f of CANON_WOFF2) copyFileSync(resolve(FONT_DIR, f), resolve(FONT_DEST, f))
  // Remove any non-canon woff2 that may exist from a previous sync.
  const destFiles = readdirSync(FONT_DEST).filter((f) => f.endsWith('.woff2'))
  for (const f of destFiles) {
    if (!CANON_WOFF2.has(f)) {
      unlinkSync(resolve(FONT_DEST, f))
      console.log(`removed legacy font ${f}`)
    }
  }
  writeFileSync(fontsCssPath, generatedFontsCss)
  console.log(`synced ${CANON_WOFF2.size} canon fonts + fonts.css (family names from theme.json)`)
}

if (CHECK && drift > 0) { console.error(`sync:check FAILED — ${drift} drifted artifact(s); run \`npm run sync\``); process.exit(1) }
if (CHECK) console.log('sync:check OK')
