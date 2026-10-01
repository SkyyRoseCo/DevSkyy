/** Portable enhancement: native links are server-rendered and always remain usable. */
const HEX = /^[a-f0-9]{64}$/;
const SKU = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function localURL(raw, base) {
  const url = new URL(raw, base);
  if (
    !['http:', 'https:'].includes(url.protocol) ||
    url.origin !== new URL(base).origin ||
    url.username ||
    url.password
  ) {
    throw new Error('Unsafe product or asset URL');
  }
  return url.href;
}

export function acceptedBinding(manifest, sku, registrySha, base) {
  if (
    !HEX.test(registrySha) ||
    manifest?.schema !== 'skyyrose.accepted-glb-runtime.v1' ||
    manifest.registry_sha256 !== registrySha ||
    manifest.publication_authorized !== true ||
    !Array.isArray(manifest.entries)
  ) {
    throw new Error('Unaccepted or stale asset manifest');
  }
  const seen = new Set();
  for (const entry of manifest.entries) {
    if (!SKU.test(entry.sku) || seen.has(entry.sku)) throw new Error('Unknown or duplicate asset identity');
    seen.add(entry.sku);
  }
  const entry = manifest.entries.find(item => item.sku === sku);
  if (
    !entry ||
    entry.registry_sha256 !== registrySha ||
    !HEX.test(entry.sha256) ||
    !Number.isSafeInteger(entry.byte_length) ||
    entry.byte_length < 20 ||
    !Number.isSafeInteger(entry.product_id) ||
    entry.product_id <= 0 ||
    !Number.isSafeInteger(entry.variation_id) ||
    entry.variation_id < 0 ||
    typeof entry.native_sku !== 'string' ||
    !entry.attributes ||
    typeof entry.attributes !== 'object' ||
    entry.product_fidelity !== 'PASS' ||
    entry.qc_binding !== 'PASS' ||
    entry.creative_approval !== 'FOUNDER_APPROVED' ||
    entry.license !== 'PASS' ||
    entry.runtime_budget !== 'PASS' ||
    entry.publication_authorized !== true ||
    typeof entry.approval_id !== 'string' ||
    !entry.approval_id.trim()
  ) {
    throw new Error('Product asset has no accepted binding');
  }
  return { ...entry, asset_url: localURL(entry.asset_url, base) };
}

export function validateEmbeddedGLB(bytes) {
  const data = new DataView(bytes);
  if (
    bytes.byteLength < 20 ||
    data.getUint32(0, true) !== 0x46546c67 ||
    data.getUint32(4, true) !== 2 ||
    data.getUint32(8, true) !== bytes.byteLength
  )
    throw new Error('Invalid GLB container');
  let offset = 12;
  let document;
  let chunks = 0;
  let binaryLength = 0;
  while (offset < bytes.byteLength) {
    if (offset + 8 > bytes.byteLength) throw new Error('Truncated GLB chunk');
    const length = data.getUint32(offset, true);
    const type = data.getUint32(offset + 4, true);
    offset += 8;
    if (length % 4 || offset + length > bytes.byteLength) throw new Error('Invalid GLB chunk length');
    if (chunks === 0) {
      if (type !== 0x4e4f534a) throw new Error('GLB JSON must be first');
      document = JSON.parse(new TextDecoder().decode(bytes.slice(offset, offset + length)));
    } else {
      if (chunks !== 1 || type !== 0x004e4942) throw new Error('Unexpected GLB chunk');
      binaryLength = length;
    }
    offset += length;
    chunks += 1;
  }
  if (!document || document.asset?.version !== '2.0') throw new Error('Invalid glTF identity');
  for (const key of ['buffers', 'images']) {
    if (document[key] === undefined) continue;
    if (
      !Array.isArray(document[key]) ||
      document[key].some(item => !item || typeof item !== 'object' || Array.isArray(item) || Object.hasOwn(item, 'uri'))
    ) {
      throw new Error('URI resources are prohibited');
    }
  }
  const buffers = document.buffers || [];
  if (
    buffers.length > 1 ||
    (buffers.length &&
      (!Number.isSafeInteger(buffers[0].byteLength) ||
        buffers[0].byteLength <= 0 ||
        buffers[0].byteLength > binaryLength))
  ) {
    throw new Error('Only the embedded BIN buffer is permitted');
  }
  const views = document.bufferViews || [];
  if (
    !Array.isArray(views) ||
    views.some(
      view =>
        !view ||
        view.buffer !== 0 ||
        !buffers.length ||
        !Number.isSafeInteger(view.byteOffset ?? 0) ||
        (view.byteOffset ?? 0) < 0 ||
        !Number.isSafeInteger(view.byteLength) ||
        view.byteLength <= 0 ||
        (view.byteOffset ?? 0) + view.byteLength > buffers[0].byteLength
    )
  )
    throw new Error('Invalid embedded buffer view');
  if (
    (document.images || []).some(
      item =>
        !Number.isSafeInteger(item.bufferView) ||
        !views[item.bufferView] ||
        !['image/png', 'image/jpeg'].includes(item.mimeType)
    )
  )
    throw new Error('Invalid embedded image');
  // Embedded ordinary geometry only. Extension decoders may otherwise fetch unbound resources.
  for (const key of ['extensionsUsed', 'extensionsRequired']) {
    if (document[key] !== undefined && (!Array.isArray(document[key]) || document[key].length))
      throw new Error('Unqualified glTF extensions');
  }
  const objects = [document];
  while (objects.length) {
    const object = objects.pop();
    if (!object || typeof object !== 'object') continue;
    if (
      Object.hasOwn(object, 'extensions') &&
      (!object.extensions ||
        typeof object.extensions !== 'object' ||
        Array.isArray(object.extensions) ||
        Object.keys(object.extensions).length)
    )
      throw new Error('Unqualified nested glTF extensions');
    objects.push(...Object.values(object).filter(value => value && typeof value === 'object'));
  }
  return document;
}

async function fetchVerified(binding, signal, maxBytes) {
  if (binding.byte_length > maxBytes) throw new Error('Asset exceeds byte budget');
  const response = await fetch(binding.asset_url, {
    signal,
    redirect: 'error',
    credentials: 'same-origin',
    cache: 'no-store',
  });
  if (!response.ok || !response.body) throw new Error('Asset download failed');
  const reader = response.body.getReader();
  const chunks = [];
  let size = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.length;
      if (size > binding.byte_length || size > maxBytes) throw new Error('Asset byte count changed');
      chunks.push(value);
    }
  } catch (error) {
    await reader.cancel().catch(() => {});
    throw error;
  }
  if (size !== binding.byte_length) throw new Error('Asset byte count changed');
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.length;
  }
  const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), byte =>
    byte.toString(16).padStart(2, '0')
  ).join('');
  if (digest !== binding.sha256) throw new Error('Asset hash changed');
  validateEmbeddedGLB(bytes.buffer);
  return bytes.buffer;
}

/** resolveProduct must call the owner's current native read-only resolver on each open/retry. */
export function createViewer(
  root,
  { products, manifest, registrySha, resolveProduct, rendererFactory, timeoutMs = 15000, maxBytes = 16 * 1024 * 1024 }
) {
  const status = root.querySelector('[data-viewer-status]');
  const stage = root.querySelector('[data-viewer-stage]');
  const retry = root.querySelector('[data-viewer-retry]');
  const back = root.querySelector('[data-viewer-back]');
  const reset = root.querySelector('[data-viewer-reset]');
  if (!status || !stage || !retry || !back || !reset || typeof resolveProduct !== 'function')
    throw new Error('Missing viewer contract');
  const accepted = structuredClone(manifest);
  const native = new Map();
  for (const product of products) {
    if (
      !SKU.test(product.sku) ||
      native.has(product.sku) ||
      !Number.isSafeInteger(product.product_id) ||
      product.product_id <= 0 ||
      !Number.isSafeInteger(product.variation_id) ||
      product.variation_id < 0
    )
      throw new Error('Invalid native product map');
    native.set(product.sku, { ...structuredClone(product), url: localURL(product.url, root.ownerDocument.baseURI) });
  }
  if (accepted?.entries?.some(entry => !native.has(entry.sku))) throw new Error('Unknown asset SKU');
  const listeners = new AbortController();
  let pending;
  let renderer;
  let generation = 0;
  let selected;
  let opener;
  let disposed = false;
  let pointer;
  const on = (element, event, callback) => element.addEventListener(event, callback, { signal: listeners.signal });
  const display = (state, text) => {
    root.dataset.viewerState = state;
    status.textContent = text;
    stage.setAttribute('aria-busy', String(state === 'loading'));
    retry.hidden = state !== 'error';
    reset.disabled = state !== 'ready';
  };
  const clear = () => {
    generation += 1;
    pending?.abort();
    pending = undefined;
    renderer?.dispose();
    renderer = undefined;
    pointer = undefined;
    stage.replaceChildren();
  };
  const fail = () => {
    clear();
    display('error', '3D view unavailable. You can still explore the product details.');
  };
  async function open(sku, trigger) {
    if (disposed) return;
    clear();
    selected = sku;
    opener = trigger || opener;
    stage.hidden = false;
    back.hidden = false;
    display('loading', 'Loading 3D view. Product details remain available.');
    pending = new AbortController();
    const controller = pending;
    const token = generation;
    const timer = setTimeout(() => {
      if (token === generation) fail();
    }, timeoutMs);
    let created;
    try {
      const product = native.get(sku);
      if (!product) throw new Error('Unknown native SKU');
      const current = await resolveProduct(structuredClone(product), { signal: controller.signal });
      if (token !== generation || disposed) return;
      const sameAttributes = a => JSON.stringify(Object.entries(a || {}).sort());
      if (
        !current ||
        current.sku !== sku ||
        current.product_id !== product.product_id ||
        current.variation_id !== product.variation_id ||
        current.registry_sha256 !== registrySha ||
        current.available !== true ||
        current.native_sku !== product.native_sku ||
        sameAttributes(current.attributes) !== sameAttributes(product.attributes) ||
        localURL(current.url, root.ownerDocument.baseURI) !== product.url
      )
        throw new Error('Stale native selection');
      const binding = acceptedBinding(accepted, sku, registrySha, root.ownerDocument.baseURI);
      if (
        binding.product_id !== current.product_id ||
        binding.variation_id !== current.variation_id ||
        binding.native_sku !== current.native_sku ||
        sameAttributes(binding.attributes) !== sameAttributes(current.attributes)
      )
        throw new Error('Asset belongs to another native selection');
      const bytes = await fetchVerified(binding, controller.signal, maxBytes);
      if (token !== generation || disposed) return;
      // A detached mount prevents a late renderer factory from attaching into a newer selection.
      const mount = root.ownerDocument.createElement('div');
      created = await rendererFactory({
        mount,
        bytes,
        onContextLost: () => {
          if (token === generation && !disposed) fail();
        },
      });
      if (token !== generation || disposed) {
        created.dispose();
        return;
      }
      renderer = created;
      stage.replaceChildren(mount);
      display('ready', '3D view ready. Drag to rotate, or use arrow keys.');
      stage.focus();
    } catch {
      if (token === generation && !disposed) {
        created?.dispose();
        fail();
      }
    } finally {
      clearTimeout(timer);
    }
  }
  on(root, 'click', event => {
    const trigger = event.target.closest('[data-viewer-open]');
    if (trigger && root.contains(trigger)) open(trigger.dataset.viewerOpen, trigger);
  });
  on(retry, 'click', () => open(selected));
  on(reset, 'click', () => renderer?.reset());
  const close = () => {
    clear();
    selected = undefined;
    stage.hidden = true;
    back.hidden = true;
    display('idle', 'Explore product details or open a 3D view.');
    opener?.focus();
  };
  on(back, 'click', close);
  on(root, 'keydown', event => {
    if (event.key === 'Escape' && selected) {
      event.preventDefault();
      close();
    }
  });
  on(stage, 'keydown', event => {
    const delta = { ArrowLeft: [-0.15, 0], ArrowRight: [0.15, 0], ArrowUp: [0, -0.15], ArrowDown: [0, 0.15] }[
      event.key
    ];
    if (delta && renderer) {
      event.preventDefault();
      renderer.rotate(...delta);
    }
    if (event.key === 'Home' && renderer) {
      event.preventDefault();
      renderer.reset();
    }
  });
  on(stage, 'pointerdown', event => {
    if (!renderer || pointer || event.button !== 0) return;
    pointer = { id: event.pointerId, x: event.clientX, y: event.clientY };
    stage.setPointerCapture(event.pointerId);
  });
  on(stage, 'pointermove', event => {
    if (pointer?.id !== event.pointerId || !renderer) return;
    renderer.rotate((event.clientX - pointer.x) * 0.01, (event.clientY - pointer.y) * 0.01);
    pointer.x = event.clientX;
    pointer.y = event.clientY;
  });
  const release = event => {
    if (pointer?.id === event.pointerId) pointer = undefined;
  };
  on(stage, 'pointerup', release);
  on(stage, 'pointercancel', release);
  on(stage, 'lostpointercapture', release);
  display('idle', 'Explore product details or open a 3D view.');
  return {
    open,
    close,
    dispose() {
      if (disposed) return;
      disposed = true;
      clear();
      listeners.abort();
      stage.hidden = true;
      back.hidden = true;
      display('disposed', 'Explore product details.');
    },
  };
}
