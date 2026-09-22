'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { validateManifest, validateResolved, safeAsset } = require('./check-approved-scroll-world-scenes.cjs');
const { buildPosters, webpDimensions } = require('./build-scene-posters.cjs');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const manifest = JSON.parse(fs.readFileSync(path.join(theme, 'data/approved-scroll-world-scenes.json')));
const motion = JSON.parse(fs.readFileSync(path.join(theme, 'data/collection-scene-motion.json')));
const firstId = 'SIG-COMMERCE-1';
function changed(callback) {
  const copy = structuredClone(manifest);
  callback(copy.scenes[firstId], copy);
  return copy;
}
function resolverFixture() {
  const result = {signature:{scenes:[]}, 'black-rose':{scenes:[]}, 'love-hurts':{scenes:[]}, 'kids-capsule':{scenes:[]}};
  for (const approved of Object.values(manifest.scenes)) {
    const assets = Object.fromEntries(approved.required_runtime_assets.map(asset => [asset.role, asset.path.replace('assets/scroll-world/', '')]));
    result[approved.collection].scenes.push({
      scene_id: approved.scene_id, source: 'scroll-world', image: assets.poster,
      scene_motion: {...assets}, product_bindings: [...approved.cta.product_bindings],
      model_layers: [], hero_composition: {variants:[]}, placeholder_active: false
    });
  }
  return result;
}

test('existing explicit approval evidence binds exactly nine final selections and 27 file hashes', () => {
  const result = validateManifest(manifest, motion);
  assert.equal(result.scenes, 9);
  assert.equal(result.runtime_media_assets, 27);
  assert(result.media_bytes > 0);
});

test('every non-final classification fails closed', () => {
  for (const status of ['SUPERSEDED', 'PROTOTYPE', 'CANDIDATE / REVIEW', 'SOURCE MASTER', 'UNKNOWN', 'SUPPORTING ASSET — REQUIRED']) {
    assert.throws(() => validateManifest(changed(scene => { scene.approval_status = status; }), motion), /not approved final/);
  }
});

test('missing, duplicate-by-ID and tenth historical scenes cannot enter canonical selection', () => {
  assert.throws(() => validateManifest(changed((scene, copy) => { delete copy.scenes['LH-COMMERCE-3']; }), motion), /Exactly the established nine/);
  assert.throws(() => validateManifest(changed((scene, copy) => { copy.scenes['SIG-COMMERCE-4'] = scene; }), motion), /Exactly the established nine/);
  assert.throws(() => validateManifest(changed(scene => { scene.scene_id = 'SIG-COMMERCE-2'; }), motion), /ID mismatch/);
});

test('changing scene order or collection is rejected', () => {
  assert.throws(() => validateManifest(changed(scene => { scene.order = 2; }), motion), /collection or order drift/);
  assert.throws(() => validateManifest(changed(scene => { scene.collection = 'black-rose'; }), motion), /collection or order drift/);
});

test('approval evidence and media hashes cannot silently drift', () => {
  assert.throws(() => validateManifest(changed(scene => { scene.source_reference[0].sha256 = '0'.repeat(64); }), motion), /source approval evidence drift/);
  assert.throws(() => validateManifest(changed(scene => { scene.required_runtime_assets[0].sha256 = '0'.repeat(64); }), motion), /poster hash drift/);
  assert.throws(() => validateManifest(changed(scene => { scene.required_runtime_assets[0].bytes += 1; }), motion), /poster byte drift/);
});

test('a required scene asset cannot escape the local theme', () => {
  assert.throws(() => safeAsset(theme, 'assets/scroll-world/../../functions.php'), /Unsafe scene asset path/);
  assert.throws(() => safeAsset(theme, 'https://example.com/candidate.webp'), /Invalid scene asset path/);
  assert.throws(() => safeAsset(theme, 'assets/scroll-world/missing-unapproved-file.webp'), /Missing scene asset/);
});

test('historical candidate layers and extra delivery variants are rejected', () => {
  assert.throws(() => validateManifest(changed(scene => { scene.required_runtime_assets.push({...scene.required_runtime_assets[0], role:'candidate-overlay'}); }), motion), /undeclared scene layers/);
  const changedMotion = structuredClone(motion);
  changedMotion.scenes[firstId].variants.push({...changedMotion.scenes[firstId].variants[0], asset:'historical.mp4'});
  assert.throws(() => validateManifest(manifest, changedMotion), /extra motion variants/);
});

test('legacy motion selection requires both explicit visual approval and local wiring authorization', () => {
  for (const flag of ['founder_approved_visual', 'local_wiring_authorized']) {
    const changedMotion = structuredClone(motion);
    changedMotion.scenes[firstId][flag] = false;
    assert.throws(() => validateManifest(manifest, changedMotion), /approval missing/);
  }
});

test('a historical tenth selection in the legacy motion manifest is blocked', () => {
  const changedMotion = structuredClone(motion);
  changedMotion.scenes['SIG-COMMERCE-4'] = changedMotion.scenes[firstId];
  assert.throws(() => validateManifest(manifest, changedMotion), /Motion selection contains missing or extra/);
});

test('non-native CTA destinations cannot be smuggled into a scene contract', () => {
  assert.throws(() => validateManifest(changed(scene => { scene.cta.collection_path = 'https://example.com'; }), motion), /non-native collection CTA/);
  assert.throws(() => validateManifest(changed(scene => { scene.cta.product_resolver = 'invented-product'; }), motion), /native SKU resolver required/);
});

test('resolved nine-scene selection is accepted with zero invented Kids chapters', () => {
  assert.deepEqual(validateResolved(manifest, resolverFixture()), {resolved_scenes:9});
});

test('actual resolver cannot add an undeclared poster, video, overlay, srcset or placeholder', () => {
  const mutations = [
    [scene => { scene.image = 'candidate.webp'; }, /undeclared resolved poster/],
    [scene => { scene.scene_motion.desktop = 'candidate.mp4'; }, /undeclared resolved desktop/],
    [scene => { scene.model_layers.push({asset:'candidate.webp'}); }, /undeclared model layer/],
    [scene => { scene.hero_composition.variants.push({asset:'candidate.webp',width:500}); }, /undeclared poster srcset/],
    [scene => { scene.placeholder_active = true; }, /historical placeholder active/]
  ];
  for (const [mutate, expected] of mutations) {
    const resolved = resolverFixture(); mutate(resolved.signature.scenes[0]);
    assert.throws(() => validateResolved(manifest, resolved), expected);
  }
});

test('resolved missing, extra and reordered chapters are rejected', () => {
  const missing = resolverFixture(); missing['love-hurts'].scenes.pop();
  assert.throws(() => validateResolved(manifest, missing), /exactly the approved nine/);
  const extra = resolverFixture(); extra['kids-capsule'].scenes.push({scene_id:'KIDS-COMMERCE-1'});
  assert.throws(() => validateResolved(manifest, extra), /unapproved resolved scene/);
  const reordered = resolverFixture(); reordered.signature.scenes.reverse();
  assert.throws(() => validateResolved(manifest, reordered), /resolved order drift/);
});

test('resolved commerce identities remain bound to approved real SKU selection', () => {
  const resolved = resolverFixture(); resolved.signature.scenes[0].product_bindings.push('sg-999');
  assert.throws(() => validateResolved(manifest, resolved), /product binding drift/);
});

test('supporting BR3 derivatives reproduce exactly with pinned cwebp and preserve parent hash', () => {
  const before = fs.readFileSync(path.join(theme, manifest.scenes['BR-COMMERCE-3'].required_runtime_assets.find(asset => asset.role === 'poster').path));
  const result = buildPosters();
  assert.equal(result.status, 'PASS_REPRODUCIBLE_SCENE_POSTERS');
  assert.equal(result.outputs.length, 2);
  assert.deepEqual(fs.readFileSync(path.join(theme, manifest.scenes['BR-COMMERCE-3'].required_runtime_assets.find(asset => asset.role === 'poster').path)), before);
});

test('foreign responsive poster parents, hashes, dimensions and delivery paths are rejected', () => {
  const mutations = [
    [asset => { asset.source_path = 'assets/scroll-world/foreign.png'; }, /foreign derivative parent/],
    [asset => { asset.source_sha256 = '0'.repeat(64); }, /foreign derivative provenance/],
    [asset => { asset.sha256 = '0'.repeat(64); }, /derivative hash drift/],
    [asset => { asset.height += 10; }, /derivative dimension drift/],
    [asset => { asset.path = 'assets/scroll-world/foreign.webp'; }, /unauthorized derivative path/]
  ];
  for (const [mutate, expected] of mutations) {
    const copy = structuredClone(manifest); mutate(copy.scenes['BR-COMMERCE-3'].responsive_posters[0]);
    assert.throws(() => validateManifest(copy, motion), expected);
  }
});

test('the BR3 engineering derivative scope cannot expand to other scenes or widths', () => {
  const other = structuredClone(manifest);
  other.scenes[firstId].responsive_posters = other.scenes['BR-COMMERCE-3'].responsive_posters;
  assert.throws(() => validateManifest(other, motion), /unauthorized supporting derivatives/);
  const extra = structuredClone(manifest);
  extra.scenes['BR-COMMERCE-3'].responsive_posters.push({...extra.scenes['BR-COMMERCE-3'].responsive_posters[0], width:1440});
  assert.throws(() => validateManifest(extra, motion), /exact two approved delivery widths/);
});

test('resolver cannot add an unapproved responsive poster delivery', () => {
  const resolved = resolverFixture();
  resolved['black-rose'].scenes[2].responsive_posters = [...manifest.scenes['BR-COMMERCE-3'].responsive_posters];
  assert.deepEqual(validateResolved(manifest, resolved), {resolved_scenes:9});
  resolved['black-rose'].scenes[2].responsive_posters.push({path:'assets/scroll-world/foreign.webp'});
  assert.throws(() => validateResolved(manifest, resolved), /undeclared responsive delivery/);
});

test('corrupt and truncated WebP containers are rejected', () => {
  assert.throws(() => webpDimensions(Buffer.from('not an image')), /Invalid WebP container/);
  const asset = manifest.scenes['BR-COMMERCE-3'].responsive_posters[0];
  const bytes = fs.readFileSync(path.join(theme, asset.path));
  assert.deepEqual(webpDimensions(bytes), {width:640,height:427});
  assert.throws(() => webpDimensions(bytes.subarray(0, 24)), /Truncated WebP chunk/);
});
