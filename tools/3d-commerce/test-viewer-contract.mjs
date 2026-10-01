import test from 'node:test';
import assert from 'node:assert/strict';
import { acceptedBinding, validateEmbeddedGLB } from './viewer.mjs';
import { disposeParsedScenes } from './three-renderer.mjs';

test('dispose all parsed scenes, shared resources, skeleton bone textures and decoded images once', () => {
  const calls = [];
  const resource = name => ({ dispose: () => calls.push(name) });
  const image = { close: () => calls.push('decoded-image') };
  const texture = { ...resource('texture'), isTexture: true, source: { data: image } };
  const otherTexture = { ...resource('other-texture'), isTexture: true, source: { data: image } };
  const boneTexture = resource('bone-texture');
  const skeleton = { boneTexture, dispose: () => calls.push('skeleton') };
  const first = {
    geometry: resource('default-geometry'),
    material: { ...resource('default-material'), map: texture },
    skeleton,
  };
  const second = {
    geometry: resource('other-geometry'),
    material: { ...resource('other-material'), map: texture, normalMap: otherTexture },
    skeleton,
  };
  const root = objects => ({ traverse: visit => objects.forEach(visit) });
  const scene = root([first]);
  disposeParsedScenes({ scene, scenes: [scene, root([first, second])] });
  assert.deepEqual(
    calls.sort(),
    [
      'default-geometry',
      'default-material',
      'other-geometry',
      'other-material',
      'texture',
      'other-texture',
      'bone-texture',
      'skeleton',
      'decoded-image',
    ].sort()
  );
  assert.equal(skeleton.boneTexture, null);
});

function glb(document) {
  const json = new TextEncoder().encode(JSON.stringify(document));
  const padded = Math.ceil(json.length / 4) * 4;
  const bytes = new ArrayBuffer(28 + padded + 4);
  const data = new DataView(bytes);
  data.setUint32(0, 0x46546c67, true);
  data.setUint32(4, 2, true);
  data.setUint32(8, bytes.byteLength, true);
  data.setUint32(12, padded, true);
  data.setUint32(16, 0x4e4f534a, true);
  new Uint8Array(bytes, 20, padded).fill(32);
  new Uint8Array(bytes, 20, json.length).set(json);
  data.setUint32(20 + padded, 4, true);
  data.setUint32(24 + padded, 0x004e4942, true);
  return bytes;
}
const base = { asset: { version: '2.0' }, buffers: [{ byteLength: 4 }] };
test('exact standalone BIN accepted', () => assert.deepEqual(validateEmbeddedGLB(glb(base)), base));
for (const uri of [
  'remote.bin',
  '../escape.png',
  'https://example.invalid/a',
  'data:image/png;base64,AA==',
  '',
  null,
]) {
  for (const kind of ['buffers', 'images'])
    test(`reject ${kind} URI ${uri}`, () => {
      assert.throws(() => validateEmbeddedGLB(glb({ ...base, [kind]: [{ uri }] })), /URI resources/);
    });
}
for (const delta of [
  { buffers: [{ byteLength: 4 }, { byteLength: 4 }] },
  { buffers: [{ byteLength: 8 }] },
  { bufferViews: [{ buffer: 1, byteLength: 4 }] },
  { bufferViews: [{ buffer: 0, byteOffset: 3, byteLength: 4 }] },
  { images: [{ mimeType: 'image/svg+xml', bufferView: 0 }] },
  { extensionsUsed: '' },
  { extensionsRequired: ['KHR_materials_ior'] },
  { materials: [{ extensions: { KHR_materials_ior: { ior: 2.5 } } }] },
  { meshes: [{ primitives: [{ extensions: { KHR_draco_mesh_compression: {} } }] }] },
])
  test(`reject unbound buffer/image/extension ${JSON.stringify(delta)}`, () =>
    assert.throws(() => validateEmbeddedGLB(glb({ ...base, ...delta }))));
const sha = 'a'.repeat(64);
const entry = {
  sku: 'fixture-a',
  native_sku: 'fixture-a',
  product_id: 1,
  variation_id: 0,
  attributes: {},
  registry_sha256: sha,
  sha256: sha,
  byte_length: 40,
  asset_url: '/fixture.glb',
  product_fidelity: 'PASS',
  qc_binding: 'PASS',
  creative_approval: 'FOUNDER_APPROVED',
  license: 'PASS',
  runtime_budget: 'PASS',
  publication_authorized: true,
  approval_id: 'SYNTHETIC-TEST-ONLY',
};
const manifest = {
  schema: 'skyyrose.accepted-glb-runtime.v1',
  entries: [entry],
  registry_sha256: sha,
  publication_authorized: true,
};
test('synthetic accepted binding is exact', () =>
  assert.equal(
    acceptedBinding(manifest, 'fixture-a', sha, 'http://127.0.0.1:8123/').asset_url,
    'http://127.0.0.1:8123/fixture.glb'
  ));
for (const altered of [
  { ...manifest, schema: 'skyyrose.glb-candidates.v2' },
  { ...manifest, registry_sha256: 'b'.repeat(64) },
  { ...manifest, publication_authorized: false },
  { ...manifest, entries: [entry, entry] },
  { ...manifest, entries: [{ ...entry, asset_url: 'https://example.invalid/a' }] },
  { ...manifest, entries: [{ ...entry, asset_url: 'javascript:alert(1)' }] },
  { ...manifest, entries: [{ ...entry, sha256: '' }] },
  { ...manifest, entries: [{ ...entry, creative_approval: 'BLOCKED' }] },
])
  test(`reject stale/unaccepted/duplicate/unsafe manifest ${JSON.stringify(altered)}`, () =>
    assert.throws(() => acceptedBinding(altered, 'fixture-a', sha, 'http://127.0.0.1:8123/')));
test('unknown asset identity fails', () =>
  assert.throws(() => acceptedBinding(manifest, 'unknown', sha, 'http://127.0.0.1:8123/')));
