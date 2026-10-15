#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { webpDimensions, outputPath, VERSION, SCENE } = require('./build-scene-posters.cjs');

const THEME = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const APPROVED = 'APPROVED FINAL — IMPLEMENT';
const COLLECTIONS = { signature: 'SIG', 'black-rose': 'BR', 'love-hurts': 'LH' };
const IDS = Object.values(COLLECTIONS).flatMap(prefix => [1, 2, 3].map(order => `${prefix}-COMMERCE-${order}`));
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function equalSet(actual, expected, message) {
  assert.deepEqual([...actual].sort(), [...expected].sort(), message);
}

function safeAsset(theme, relative) {
  assert.equal(typeof relative, 'string', 'Asset path must be a string');
  assert(/^assets\/scroll-world\/[A-Za-z0-9_./-]+$/.test(relative), `Invalid scene asset path: ${relative}`);
  assert(!relative.split('/').some(segment => !segment || segment === '..' || segment === '.'), `Unsafe scene asset path: ${relative}`);
  const absolute = path.join(theme, relative);
  assert(fs.existsSync(absolute), `Missing scene asset: ${relative}`);
  const root = fs.realpathSync(theme) + path.sep;
  assert(fs.realpathSync(absolute).startsWith(root), `Scene asset escapes theme: ${relative}`);
  assert(fs.statSync(absolute).isFile(), `Scene asset is not a file: ${relative}`);
  return absolute;
}

/** Validate the local approved selection, never infer approval from a filename. */
function validateManifest(manifest, motion, theme = THEME) {
  assert.equal(manifest.schema_version, 1, 'Unsupported approved scene schema');
  assert.equal(manifest.approval_scope, 'LOCAL_INTEGRATION_ONLY', 'Scene approval does not grant deployment');
  assert(manifest.scenes && typeof manifest.scenes === 'object', 'Missing approved scenes');
  equalSet(Object.keys(manifest.scenes), IDS, 'Exactly the established nine scenes are required');
  equalSet(Object.keys(motion.scenes || {}), IDS, 'Motion selection contains missing or extra scenes');
  assert.deepEqual(manifest.poster_derivation, {tool:'cwebp', version:VERSION, quality:90, method:6, resize:'width-preserve-aspect', scene_ids:[SCENE]}, 'Unsupported poster derivation policy');
  let mediaBytes = 0;
  let derivativeBytes = 0;
  for (const id of IDS) {
    const scene = manifest.scenes[id];
    const selected = motion.scenes[id];
    assert.equal(scene.scene_id, id, `${id}: ID mismatch`);
    assert.equal(scene.approval_status, APPROVED, `${id}: scene is not approved final`);
    assert.equal(id, `${COLLECTIONS[scene.collection]}-COMMERCE-${scene.order}`, `${id}: collection or order drift`);
    assert.equal(selected.collection, scene.collection, `${id}: motion collection drift`);
    assert.equal(selected.founder_approved_visual, true, `${id}: visual approval missing`);
    assert.equal(selected.local_wiring_authorized, true, `${id}: local wiring approval missing`);
    assert(Array.isArray(scene.source_reference) && scene.source_reference.length >= 2, `${id}: explicit approval evidence required`);
    for (const reference of scene.source_reference) {
      assert(reference.path && /^[a-f0-9]{64}$/.test(reference.sha256), `${id}: unbound source evidence`);
      const repository = path.resolve(theme, '../..');
      const evidence = path.resolve(repository, reference.path);
      assert(evidence.startsWith(repository + path.sep), `${id}: evidence path escapes repository`);
      assert(fs.existsSync(evidence), `${id}: missing source evidence`);
      assert.equal(digest(fs.readFileSync(evidence)), reference.sha256, `${id}: source approval evidence drift`);
    }
    assert(Array.isArray(scene.required_runtime_assets), `${id}: missing runtime assets`);
    equalSet(scene.required_runtime_assets.map(asset => asset.role), ['poster', 'desktop', 'mobile'], `${id}: undeclared scene layers or missing required assets`);
    for (const asset of scene.required_runtime_assets) {
      assert.equal(asset.path, `assets/scroll-world/${selected[asset.role]}`, `${id}: ${asset.role} selection drift`);
      assert(/^[a-f0-9]{64}$/.test(asset.sha256), `${id}: invalid asset hash`);
      const bytes = fs.readFileSync(safeAsset(theme, asset.path));
      assert.equal(bytes.length, asset.bytes, `${id}: ${asset.role} byte drift`);
      assert.equal(digest(bytes), asset.sha256, `${id}: ${asset.role} hash drift`);
      mediaBytes += bytes.length;
      if (asset.role !== 'poster') {
        const variant = (selected.variants || []).find(item => `assets/scroll-world/${item.asset}` === asset.path);
        assert(variant, `${id}: missing source delivery receipt`);
        assert.equal(variant.sha256, asset.sha256, `${id}: delivery receipt hash drift`);
        assert.equal(variant.bytes, asset.bytes, `${id}: delivery receipt size drift`);
      }
    }
    equalSet((selected.variants || []).map(item => item.asset), [selected.desktop, selected.mobile], `${id}: extra motion variants`);
    const derivatives = scene.responsive_posters || [];
    if (id !== SCENE) {
      assert.deepEqual(derivatives, [], `${id}: unauthorized supporting derivatives`);
    } else {
      assert.deepEqual(derivatives.map(asset => asset.width), [640, 1024], `${id}: exact two approved delivery widths required`);
      const parent = scene.required_runtime_assets.find(asset => asset.role === 'poster');
      for (const derivative of derivatives) {
        assert.equal(derivative.path, outputPath(derivative.width), `${id}: unauthorized derivative path`);
        assert.equal(derivative.source_path, parent.path, `${id}: foreign derivative parent`);
        assert.equal(derivative.source_sha256, parent.sha256, `${id}: foreign derivative provenance`);
        assert.equal(derivative.classification, 'SUPPORTING ASSET — REQUIRED', `${id}: derivative is not a supporting asset`);
        const bytes = fs.readFileSync(safeAsset(theme, derivative.path));
        assert.equal(digest(bytes), derivative.sha256, `${id}: derivative hash drift`);
        assert.equal(bytes.length, derivative.bytes, `${id}: derivative byte drift`);
        assert.deepEqual(webpDimensions(bytes), {width:derivative.width, height:derivative.height}, `${id}: derivative dimension drift`);
        assert.equal(derivative.height, Math.round(derivative.width * scene.desktop_composition.height / scene.desktop_composition.width), `${id}: derivative aspect ratio drift`);
        derivativeBytes += bytes.length;
      }
    }
    assert.equal(scene.motion_controller, 'assets/js/collection-scene-motion.js', `${id}: undeclared controller`);
    assert(fs.existsSync(path.join(theme, scene.motion_controller)), `${id}: missing controller`);
    assert.equal(scene.desktop_composition?.fit, 'contain', `${id}: full composition must survive desktop`);
    assert(scene.desktop_composition.width > 0 && scene.desktop_composition.height > 0, `${id}: missing reference dimensions`);
    assert.equal(scene.mobile_composition?.fit, 'contain', `${id}: full composition must survive mobile`);
    assert.equal(scene.mobile_composition.cta_always_available, true, `${id}: CTA cannot depend on motion`);
    assert.equal(scene.cta?.collection_path, `/collections/${scene.collection}/#shop`, `${id}: non-native collection CTA`);
    assert.equal(scene.cta.product_resolver, 'wc_get_product_id_by_sku', `${id}: native SKU resolver required`);
    assert(Array.isArray(scene.cta.product_bindings) && scene.cta.product_bindings.length > 0, `${id}: missing product bindings`);
    assert(scene.cta.product_bindings.every(sku => /^(?:sg|br|lh)-\d{3}$/.test(sku)), `${id}: invalid product binding`);
    assert.equal(new Set(scene.cta.product_bindings).size, scene.cta.product_bindings.length, `${id}: duplicate product binding`);
  }
  return { scenes: IDS.length, runtime_media_assets: IDS.length * 3, media_bytes: mediaBytes, supporting_derivatives: 2, supporting_derivative_bytes: derivativeBytes };
}

/** Attest actual PHP resolver output; prevent a legacy fallback from selecting extra art. */
function validateResolved(manifest, resolved) {
  const seen = [];
  for (const [collection, record] of Object.entries(resolved)) {
    assert(Array.isArray(record.scenes), `${collection}: resolver scenes missing`);
    for (const [index, scene] of record.scenes.entries()) {
      const approved = manifest.scenes[scene.scene_id];
      assert(approved, `${scene.scene_id}: unapproved resolved scene`);
      assert.equal(collection, approved.collection, `${scene.scene_id}: resolved collection drift`);
      assert.equal(index + 1, approved.order, `${scene.scene_id}: resolved order drift`);
      seen.push(scene.scene_id);
      const assets = Object.fromEntries(approved.required_runtime_assets.map(asset => [asset.role, asset.path]));
      assert.equal(scene.source, 'scroll-world', `${scene.scene_id}: unexpected image provider`);
      assert.equal(`assets/scroll-world/${scene.image}`, assets.poster, `${scene.scene_id}: undeclared resolved poster`);
      assert(scene.scene_motion, `${scene.scene_id}: missing approved motion binding`);
      for (const role of ['poster', 'desktop', 'mobile']) {
        assert.equal(`assets/scroll-world/${scene.scene_motion[role]}`, assets[role], `${scene.scene_id}: undeclared resolved ${role}`);
      }
      assert.deepEqual(scene.product_bindings, approved.cta.product_bindings, `${scene.scene_id}: product binding drift`);
      assert.deepEqual(scene.model_layers, [], `${scene.scene_id}: undeclared model layer`);
      assert.deepEqual(scene.hero_composition?.variants, [], `${scene.scene_id}: undeclared poster srcset`);
      if (scene.responsive_posters !== undefined) {
        assert.deepEqual(scene.responsive_posters, approved.responsive_posters || [], `${scene.scene_id}: undeclared responsive delivery`);
      }
      assert.equal(scene.placeholder_active, false, `${scene.scene_id}: historical placeholder active`);
    }
  }
  equalSet(seen, IDS, 'Resolved runtime must contain exactly the approved nine scenes');
  return { resolved_scenes: seen.length };
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    assert(args.length === 0 || (args.length === 2 && args[0] === '--resolved'), 'Usage: check-approved-scroll-world-scenes.cjs [--resolved FILE]');
    const manifest = readJson(path.join(THEME, 'data/approved-scroll-world-scenes.json'));
    const result = validateManifest(manifest, readJson(path.join(THEME, 'data/collection-scene-motion.json')));
    if (args.length) Object.assign(result, validateResolved(manifest, readJson(path.resolve(args[1]))));
    console.log(JSON.stringify({ status: 'PASS_APPROVED_SCENE_SELECTION', ...result, resolved_selection_checked: Boolean(args.length), browser_visual_qa: 'NOT_PERFORMED_BY_THIS_GUARD' }, null, 2));
  } catch (error) {
    console.error(`Approved scene guard: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = { validateManifest, validateResolved, safeAsset, IDS, APPROVED };
