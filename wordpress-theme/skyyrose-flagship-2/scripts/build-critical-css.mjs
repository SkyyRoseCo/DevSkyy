#!/usr/bin/env node

/**
 * Deterministic critical structural CSS for the Home first view.
 *
 * Reads the contract in assets/css/critical/home.contract.json, extracts only
 * the rules whose selectors name a first-view structure (header, hero stage,
 * first-viewport typography, primary controls, rotating-mark container) from
 * the same source stylesheets the theme enqueues, keeps the @font-face
 * declarations so font discovery starts before the full sheets arrive, and
 * writes a minified file that the theme inlines on the front page.
 *
 * The output is derived from source bytes only; it never reads a rendered
 * page. `--check` fails when the file is stale, over budget, or when a class
 * in the first-view templates has no rule in the output.
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import CleanCSS from 'clean-css';
import postcss from 'postcss';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const themeDir = path.resolve(scriptDir, '..');
const checkOnly = process.argv.includes('--check');
const contractPath = path.join(themeDir, 'assets', 'css', 'critical', 'home.contract.json');
const contract = JSON.parse(fs.readFileSync(contractPath, 'utf8'));

const IDENT = /[A-Za-z0-9_-]/; // Output convention matches build-assets.mjs: no trailing newline.
const normalize = (text) => text.replace(/\s+/g, ' ').trim();
const excludePatterns = contract.excludeSelectorPatterns.map((pattern) => new RegExp(pattern));
const baseSelectors = new Set(contract.baseSelectors.map(normalize));
const keepMedia = new Set(contract.keepMedia.map(normalize));
const keepKeyframes = new Set(contract.keepKeyframes || []);

function tokenMatches(selector, token) {
  let index = selector.indexOf(token);
  while (index !== -1) {
    const next = selector[index + token.length];
    if (next === undefined || !IDENT.test(next)) return true;
    index = selector.indexOf(token, index + 1);
  }
  return false;
}

/** Split a selector list on top-level commas only; `:is(a, b)` stays one part. */
function splitSelectors(selector) {
  const parts = [];
  let depth = 0;
  let current = '';
  for (const char of selector) {
    if (char === '(' || char === '[') depth += 1;
    if (char === ')' || char === ']') depth -= 1;
    if (char === ',' && depth === 0) { parts.push(current); current = ''; continue; }
    current += char;
  }
  parts.push(current);
  return parts;
}

function wantedParts(selector) {
  return splitSelectors(selector).map(normalize).filter((part) => {
    if (!part) return false;
    if (excludePatterns.some((pattern) => pattern.test(part))) return false;
    if (baseSelectors.has(part)) return true;
    return contract.tokens.some((token) => tokenMatches(part, token));
  });
}

function filterContainer(container, out) {
  container.each((node) => {
    if (node.type === 'rule') {
      const parts = wantedParts(node.selector);
      if (parts.length === 0) return;
      const clone = node.clone();
      clone.selector = parts.join(',');
      // Closed overlays occupy no first-view layout. Their full declarations
      // remain in the external sheet; inline only their hidden-state property.
      const noScript = node.parent.type === 'atrule' && normalize(node.parent.params || '') === '(scripting: none)';
      const properties = noScript ? undefined : contract.criticalDeclarations?.[normalize(clone.selector)];
      if (properties) clone.walkDecls((decl) => { if (!properties.includes(decl.prop)) decl.remove(); });
      clone.raws.before = '\n';
      out.append(clone);
      return;
    }
    if (node.type === 'atrule' && node.name === 'keyframes' && keepKeyframes.has(node.params)) {
      out.append(node.clone());
      return;
    }
    if (node.type === 'atrule' && node.name === 'font-face') {
      const family = node.nodes?.find((decl) => decl.prop === 'font-family')?.value.replace(/^["']|["']$/g, '');
      if (contract.keepFontFaces && (!contract.fontFamilies || contract.fontFamilies.includes(family))) out.append(node.clone());
      return;
    }
    if (node.type === 'atrule' && node.name === 'media' && keepMedia.has(normalize(node.params))) {
      const media = postcss.atRule({ name: 'media', params: node.params });
      filterContainer(node, media);
      if (media.nodes && media.nodes.length > 0) out.append(media);
    }
  });
}

/** Keep only the custom properties the kept rules reference, transitively. */
function pruneCustomProperties(root) {
  const referenced = new Set();
  const collect = (value) => { for (const match of value.matchAll(/var\(\s*(--[A-Za-z0-9_-]+)/g)) referenced.add(match[1]); };
  root.walkDecls((decl) => { if (!decl.prop.startsWith('--')) collect(decl.value); });
  let changed = true;
  while (changed) {
    changed = false;
    root.walkDecls((decl) => {
      if (decl.prop.startsWith('--') && referenced.has(decl.prop)) {
        const before = referenced.size;
        collect(decl.value);
        if (referenced.size !== before) changed = true;
      }
    });
  }
  root.walkDecls((decl) => { if (decl.prop.startsWith('--') && !referenced.has(decl.prop)) decl.remove(); });
  root.walkRules((rule) => { if (rule.nodes.length === 0) rule.remove(); });
  root.walkAtRules('media', (atRule) => { if (!atRule.nodes || atRule.nodes.length === 0) atRule.remove(); });
}

function build() {
  const out = postcss.root();
  for (const name of contract.sources) {
    const sourcePath = path.join(themeDir, 'assets', 'css', name);
    const root = postcss.parse(fs.readFileSync(sourcePath, 'utf8'), { from: sourcePath });
    filterContainer(root, out);
  }
  pruneCustomProperties(out);
  // Inline styles resolve url() against the document, not assets/css/.
  const css = out.toString().replace(/url\((['"]?)\.\.\//g, `url($1${contract.assetsPlaceholder}/`);
  if (process.env.CRITICAL_DEBUG) fs.writeFileSync(process.env.CRITICAL_DEBUG, css, 'utf8');
  // The assembled sheet must re-parse before minification; a broken selector
  // would otherwise silently truncate everything after it.
  postcss.parse(css, { from: 'critical-home.css' });
  const result = new CleanCSS({ level: { 1: { specialComments: 0 } } }).minify(css);
  if (result.errors.length > 0 || result.warnings.length > 0) throw new Error(result.errors.concat(result.warnings).join('; '));
  return result.styles;
}

function templateClasses() {
  const classes = new Map();
  for (const template of contract.templates) {
    let text = fs.readFileSync(path.join(themeDir, template.file), 'utf8');
    const start = text.indexOf(template.from);
    if (start === -1) throw new Error(`${template.file}: marker not found: ${template.from}`);
    const end = text.indexOf(template.to, start + template.from.length);
    if (end === -1) throw new Error(`${template.file}: marker not found: ${template.to}`);
    text = text.slice(start, end);
    for (const region of template.stripRegions || []) text = text.replace(new RegExp(region, 'g'), '');
    for (const match of text.matchAll(/class="([^"]*)"/g)) {
      for (const token of match[1].split(/\s+/)) {
        if (/^(sr2|skyyrose)-[A-Za-z0-9_-]+$/.test(token)) classes.set(token, template.file);
      }
    }
  }
  return classes;
}

function coverage(css) {
  const uncovered = [];
  for (const [token, file] of templateClasses()) {
    if (tokenMatches(css, `.${token}`)) continue;
    if (contract.allowUnstyled[token]) continue;
    uncovered.push(`${token} (${file})`);
  }
  return uncovered;
}

function main() {
  const destination = path.join(themeDir, contract.output);
  const css = build();
  const bytes = Buffer.byteLength(css, 'utf8');
  const problems = [];
  if (bytes > contract.budgetBytes) problems.push(`critical CSS is ${bytes} bytes; budget is ${contract.budgetBytes}`);
  problems.push(...coverage(css).map((token) => `first-view class has no critical rule: ${token}`));
  for (const required of ['@font-face', '.sr2-house-header', '.sr2-archive-scene', '.sr2-brand-media', '[data-recovery-hero-video]', '.sr2-control--primary', ':root']) {
    if (!css.includes(required)) problems.push(`required structure missing from critical CSS: ${required}`);
  }
  if (checkOnly) {
    const current = fs.existsSync(destination) ? fs.readFileSync(destination, 'utf8') : null;
    if (current !== css) problems.push(`stale or missing: ${path.relative(themeDir, destination)} (run npm run build:critical)`);
  } else {
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, css, 'utf8');
  }
  if (problems.length > 0) {
    console.error(problems.map((problem) => `  - ${problem}`).join('\n'));
    process.exit(1);
  }
  console.log(`${checkOnly ? 'Verified' : 'Built'} ${path.relative(themeDir, destination)}: ${bytes} bytes (budget ${contract.budgetBytes}).`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
