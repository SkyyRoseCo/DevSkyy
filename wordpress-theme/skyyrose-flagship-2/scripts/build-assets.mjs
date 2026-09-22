#!/usr/bin/env node

/** Deterministic V2 CSS/JS source-to-min build. */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import CleanCSS from 'clean-css';
import postcss from 'postcss';
import { minify } from 'terser';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const themeDir = path.resolve(scriptDir, '..');
const checkOnly = process.argv.includes('--check');

function sourceFiles(directory, extension) {
  return fs
    .readdirSync(directory, { withFileTypes: true })
    .filter(entry => entry.isFile() && entry.name.endsWith(extension) && !entry.name.endsWith(`.min${extension}`))
    .map(entry => path.join(directory, entry.name))
    .sort();
}

function verifyOrWrite(sourcePath, output) {
  const destination = sourcePath.replace(/\.(css|js)$/, '.min.$1');
  if (checkOnly) {
    return fs.existsSync(destination) && fs.readFileSync(destination, 'utf8') === output;
  }
  fs.writeFileSync(destination, output, 'utf8');
  return true;
}

function readCss(sourcePath) {
  const source = fs.readFileSync(sourcePath, 'utf8');
  // CleanCSS may silently repair broken declarations into different selectors.
  // The default PostCSS parser rejects malformed syntax with file/line evidence.
  postcss.parse(source, { from: sourcePath });
  return source;
}

function minifyCss(source) {
  const result = new CleanCSS({ level: { 1: { specialComments: 0 } } }).minify(source);
  if (result.errors.length > 0) {
    throw new Error(result.errors.join('; '));
  }
  return result.styles;
}

async function minifyJs(sourcePath) {
  const source = fs.readFileSync(sourcePath, 'utf8');
  const result = await minify(source, {
    compress: { passes: 2, drop_console: true },
    mangle: true,
    format: { comments: false },
  });
  if (typeof result.code !== 'string') {
    throw new Error('Terser returned no code.');
  }
  return result.code;
}

async function main() {
  const cssSources = sourceFiles(path.join(themeDir, 'assets', 'css'), '.css');
  const jsSources = sourceFiles(path.join(themeDir, 'assets', 'js'), '.js');
  // Validate every CSS input before writing any asset; a later invalid file
  // must not leave an earlier stylesheet rebuilt from a rejected source set.
  const cssInputs = cssSources.map(sourcePath => ({ sourcePath, source: readCss(sourcePath) }));
  const stale = [];
  for (const { sourcePath, source } of cssInputs) {
    if (!verifyOrWrite(sourcePath, minifyCss(source))) stale.push(path.relative(themeDir, sourcePath));
  }
  for (const sourcePath of jsSources) {
    if (!verifyOrWrite(sourcePath, await minifyJs(sourcePath))) stale.push(path.relative(themeDir, sourcePath));
  }
  if (stale.length > 0) {
    console.error(`Generated assets are stale or missing:\n${stale.map(file => `  - ${file}`).join('\n')}`);
    process.exit(1);
  }
  console.log(`${checkOnly ? 'Verified' : 'Built'} ${cssSources.length} CSS and ${jsSources.length} JS assets.`);
}

main().catch(error => {
  console.error(error.message);
  process.exit(1);
});
