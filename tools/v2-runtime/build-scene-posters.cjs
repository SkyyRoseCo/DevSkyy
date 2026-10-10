#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');

const THEME = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const VERSION = '1.6.0\nlibsharpyuv: 0.4.2';
const SCENE = 'BR-COMMERCE-3';
const SOURCE = 'assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/black-rose/br-commerce-3-five-jersey-lounge-a-black-founder-approved-v1.png';
const outputPath = width => `assets/scroll-world/derived/approved-scenes/br-commerce-3-poster-${width}w.webp`;
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

/** Read WebP dimensions without decoding pixels or introducing another runtime dependency. */
function webpDimensions(bytes) {
  assert(bytes.length >= 20 && bytes.toString('ascii', 0, 4) === 'RIFF' && bytes.toString('ascii', 8, 12) === 'WEBP', 'Invalid WebP container');
  for (let offset = 12; offset + 8 <= bytes.length;) {
    const kind = bytes.toString('ascii', offset, offset + 4);
    const length = bytes.readUInt32LE(offset + 4);
    const start = offset + 8;
    assert(start + length <= bytes.length, 'Truncated WebP chunk');
    if (kind === 'VP8 ' && length >= 10) {
      assert.equal(bytes.toString('hex', start + 3, start + 6), '9d012a', 'Invalid VP8 frame');
      return {width: bytes.readUInt16LE(start + 6) & 0x3fff, height: bytes.readUInt16LE(start + 8) & 0x3fff};
    }
    if (kind === 'VP8L' && length >= 5) {
      assert.equal(bytes[start], 0x2f, 'Invalid VP8L frame');
      const bits = bytes.readUInt32LE(start + 1);
      return {width: (bits & 0x3fff) + 1, height: ((bits >>> 14) & 0x3fff) + 1};
    }
    if (kind === 'VP8X' && length >= 10) {
      return {width: bytes.readUIntLE(start + 4, 3) + 1, height: bytes.readUIntLE(start + 7, 3) + 1};
    }
    offset = start + length + (length % 2);
  }
  throw new Error('WebP dimensions unavailable');
}

function buildPosters({theme = THEME, check = true} = {}) {
  const manifest = JSON.parse(fs.readFileSync(path.join(theme, 'data/approved-scroll-world-scenes.json')));
  const policy = manifest.poster_derivation;
  assert.deepEqual(policy, {tool:'cwebp', version:VERSION, quality:90, method:6, resize:'width-preserve-aspect', scene_ids:[SCENE]}, 'Unsupported poster derivation policy');
  const version = execFileSync('cwebp', ['-version'], {encoding:'utf8'}).trim();
  assert.equal(version, VERSION, 'Pinned cwebp/libsharpyuv version required for reproducible poster output');
  const scene = manifest.scenes[SCENE];
  assert.equal(scene.approval_status, 'APPROVED FINAL — IMPLEMENT', 'BR3 source must remain approved final');
  const source = scene.required_runtime_assets.find(asset => asset.role === 'poster');
  assert.equal(source.path, SOURCE, 'Only the exact approved BR3 parent is authorized');
  const sourcePath = path.join(theme, SOURCE);
  assert(fs.realpathSync(sourcePath).startsWith(fs.realpathSync(theme) + path.sep), 'Source escapes theme');
  assert.equal(digest(fs.readFileSync(sourcePath)), source.sha256, 'Approved parent hash drift');
  assert.deepEqual(scene.responsive_posters.map(asset => asset.width), [640, 1024], 'Only two approved BR3 delivery widths are authorized');
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'skyyrose-scene-posters-'));
  try {
    const outputs = [];
    for (const derivative of scene.responsive_posters) {
      assert.equal(derivative.path, outputPath(derivative.width), 'Unexpected derivative destination');
      assert.equal(derivative.source_path, source.path, 'Foreign poster parent');
      assert.equal(derivative.source_sha256, source.sha256, 'Foreign poster provenance');
      const generated = path.join(temporary, `${derivative.width}.webp`);
      execFileSync('cwebp', ['-quiet', '-q', '90', '-m', '6', '-resize', String(derivative.width), '0', sourcePath, '-o', generated], {stdio:'pipe'});
      const bytes = fs.readFileSync(generated);
      assert.equal(digest(bytes), derivative.sha256, 'Encoded poster differs from committed manifest');
      assert.equal(bytes.length, derivative.bytes, 'Encoded poster size differs from committed manifest');
      assert.deepEqual(webpDimensions(bytes), {width:derivative.width, height:derivative.height}, 'Encoded poster dimension drift');
      const destination = path.join(theme, derivative.path);
      const directory = path.dirname(destination);
      if (!check) fs.mkdirSync(directory, {recursive:true});
      assert(fs.realpathSync(directory).startsWith(fs.realpathSync(theme) + path.sep), 'Derivative destination escapes theme');
      if (check) {
        assert.equal(digest(fs.readFileSync(destination)), derivative.sha256, 'Committed derivative differs from reproducible build');
      } else {
        assert(!fs.existsSync(destination) || !fs.lstatSync(destination).isSymbolicLink(), 'Refusing symlink output');
        fs.writeFileSync(destination, bytes);
      }
      outputs.push({path:derivative.path, bytes:bytes.length, sha256:derivative.sha256});
    }
    return {status:check ? 'PASS_REPRODUCIBLE_SCENE_POSTERS' : 'BUILT_SCENE_POSTERS', tool_version:VERSION, outputs};
  } finally {
    fs.rmSync(temporary, {recursive:true, force:true});
  }
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    assert(args.length <= 1 && (!args.length || ['--check', '--write'].includes(args[0])), 'Usage: build-scene-posters.cjs [--check|--write]');
    console.log(JSON.stringify(buildPosters({check:args[0] !== '--write'}), null, 2));
  } catch (error) {
    console.error(`Scene poster build: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {buildPosters, webpDimensions, outputPath, VERSION, SOURCE, SCENE};
