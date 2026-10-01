import { acceptedBinding, createViewer } from './product-glb-viewer.mjs';
import { createThreeRenderer } from './product-glb-three.mjs';

/** One controller per native PDP selection; never rewrite a binding to match an option. */
export function mountProductView(root) {
  const config = JSON.parse(root.dataset.config);
  const form = root.closest('.summary')?.querySelector('form.variations_form');
  const open = root.querySelector('[data-viewer-open]');
  const stage = root.querySelector('[data-viewer-stage]');
  const status = root.querySelector('[data-viewer-status]');
  let viewer;
  let generation = 0;
  let pending;
  let disposed = false;
  const resolveProduct = async (selection, { signal } = {}) => {
    const response = await fetch(config.endpoint, {
      method: 'POST', cache: 'no-store', credentials: 'same-origin', signal,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sku: config.sku, variation_id: selection.variation_id, attributes: selection.attributes }),
    });
    if (!response.ok) throw new Error('Product selection changed');
    return response.json();
  };
  const refresh = async () => {
    const current = ++generation;
    pending?.abort();
    pending = new AbortController();
    viewer?.dispose();
    viewer = null;
    open.hidden = true;
    stage.hidden = true;
    status.textContent = 'Choose a product option to explore its available views.';
    const variationId = form ? Number(form.querySelector('[name="variation_id"]')?.value) : 0;
    if (form && !variationId) return;
    const attributes = form ? Object.fromEntries(Array.from(new FormData(form).entries()).filter(([key]) => key.startsWith('attribute_'))) : {};
    try {
      const product = await resolveProduct({ variation_id: variationId, attributes }, { signal: pending.signal });
      if (disposed || current !== generation || !root.isConnected) return;
      const binding = acceptedBinding(config.manifest, config.sku, config.registrySha, root.ownerDocument.baseURI);
      if (binding.product_id !== product.product_id || binding.variation_id !== product.variation_id || binding.native_sku !== product.native_sku || JSON.stringify(Object.entries(binding.attributes).sort()) !== JSON.stringify(Object.entries(product.attributes).sort())) throw new Error('No accepted view for this option');
      viewer = createViewer(root, {
        products: [product], manifest: config.manifest, registrySha: config.registrySha,
        resolveProduct, rendererFactory: options => createThreeRenderer(options, config.vendorBase),
      });
      open.hidden = false;
    } catch (error) {
      if (disposed || current !== generation) return;
      status.textContent = '3D view unavailable for this selection. Product details remain available.';
    }
  };
  const onOpen = () => { stage.hidden = false; };
  const onBack = () => { stage.hidden = true; };
  open.addEventListener('click', onOpen);
  root.querySelector('[data-viewer-back]').addEventListener('click', onBack);
  const observer = new MutationObserver(() => { if (!root.isConnected) dispose(); });
  observer.observe(root.ownerDocument.body, { childList: true, subtree: true });
  const jqueryForm = form && globalThis.jQuery ? globalThis.jQuery(form) : null;
  jqueryForm?.on('found_variation.skyyroseGLB reset_data.skyyroseGLB', refresh);
  form?.addEventListener('change', refresh);
  const dispose = () => {
    if (disposed) return;
    disposed = true;
    ++generation;
    pending?.abort();
    viewer?.dispose();
    observer.disconnect();
    jqueryForm?.off('.skyyroseGLB', refresh);
    form?.removeEventListener('change', refresh);
    open.removeEventListener('click', onOpen);
    root.querySelector('[data-viewer-back]').removeEventListener('click', onBack);
    globalThis.removeEventListener('pagehide', dispose);
  };
  refresh();
  return { dispose, refresh };
}

const controllers = new Map();
function mountViews() {
  for (const root of document.querySelectorAll('[data-product-glb]')) {
    if (controllers.has(root)) continue;
    try { controllers.set(root, mountProductView(root)); } catch { /* Native links remain available. */ }
  }
}
globalThis.addEventListener('pagehide', () => {
  for (const controller of controllers.values()) controller.dispose();
  controllers.clear();
});
globalThis.addEventListener('pageshow', mountViews);
mountViews();
