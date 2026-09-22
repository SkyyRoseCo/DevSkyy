/* Native WooCommerce owns product options, validation, stock and cart submission. */
(() => {
  'use strict';
  const dialog = document.querySelector('#sr2-quick-view-dialog');
  if (!dialog || dialog.dataset.commerceInitialized) return;
  dialog.dataset.commerceInitialized = 'true';
  const purchase = dialog.querySelector('[data-quick-view-purchase]');
  const status = dialog.querySelector('[data-quick-view-status]');
  const link = dialog.querySelector('[data-quick-view-url]');
  if (!purchase || !status || !link) return;
  let request;
  let generation = 0;
  let activeUrl = '';
  let requestedOpener;
  let activeOpener;
  const cardState = (state) => {
    const card = activeOpener?.closest('.sr2-c-editorial-card');
    if (card) card.dataset.quickViewState = state;
    activeOpener?.setAttribute('aria-expanded', state === 'closed' ? 'false' : 'true');
  };
  document.addEventListener('click', (event) => {
    const opener = event.target.closest?.('[data-quick-view]');
    if (opener && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey && event.button === 0) requestedOpener = opener;
  }, true);
  const clean = () => {
    cardState('closed');
    generation += 1;
    request?.abort();
    request = null;
    if (window.jQuery) window.jQuery(purchase).empty();
    else purchase.replaceChildren();
    purchase.removeAttribute('aria-busy');
    status.textContent = '';
    activeUrl = '';
  };
  const sameOrigin = (value, base = location.href) => {
    const url = new URL(value, base);
    if (url.origin !== location.origin || !['http:', 'https:'].includes(url.protocol) || url.username || url.password) throw Error('Nonlocal product');
    return url;
  };
  let variationRuntime;
  const ensureVariationRuntime = () => {
    if (window.jQuery?.fn?.wc_variation_form) return Promise.resolve();
    if (variationRuntime) return variationRuntime;
    variationRuntime = new Promise((resolve, reject) => {
      const marker = document.querySelector('script[data-sr2-variation-src]');
      if (!marker || !window.jQuery) { reject(Error('Variation runtime unavailable')); return; }
      let src;
      try { src = sameOrigin(marker.dataset.sr2VariationSrc).href; }
      catch (error) { reject(error); return; }
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      if (marker.nonce) script.nonce = marker.nonce;
      if (marker.integrity) script.integrity = marker.integrity;
      if (marker.crossOrigin) script.crossOrigin = marker.crossOrigin;
      let settled = false;
      const finish = (error) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        script.onload = null;
        script.onerror = null;
        if (error) { script.remove(); reject(error); }
        else resolve();
      };
      const timer = setTimeout(() => finish(Error('Variation runtime timed out')), 10000);
      script.onload = () => finish(window.jQuery?.fn?.wc_variation_form ? null : Error('Variation runtime unavailable'));
      script.onerror = () => finish(Error('Variation runtime failed'));
      document.head.append(script);
    });
    return variationRuntime;
  };
  const load = async () => {
    if (!dialog.open) { clean(); return; }
    if (activeUrl === link.href) return;
    clean();
    activeUrl = link.href;
    activeOpener = requestedOpener;
    cardState('loading');
    const current = generation;
    request = new AbortController();
    const controller = request;
    let timedOut = false;
    const deadline = setTimeout(() => { timedOut = true; controller.abort(); }, 12000);
    purchase.setAttribute('aria-busy', 'true');
    status.textContent = status.dataset.loading;
    try {
      const url = sameOrigin(link.href);
      const response = await fetch(url.href, { credentials: 'same-origin', redirect: 'error', signal: controller.signal, headers: { Accept: 'text/html' } });
      if (!response.ok || !response.headers.get('content-type')?.includes('text/html')) throw Error('Product unavailable');
      const responseUrl = sameOrigin(response.url || url.href);
      if (Number(response.headers.get('content-length')) > 2 * 1024 * 1024) throw Error('Product response too large');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let html = '';
      let bytes = 0;
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        bytes += chunk.value.byteLength;
        if (bytes > 2 * 1024 * 1024) {
          await reader.cancel();
          throw Error('Product response too large');
        }
        html += decoder.decode(chunk.value, { stream: true });
      }
      html += decoder.decode();
      // Template content stays inert: parsing a full PDP must not fetch its gallery/media.
      const template = document.createElement('template');
      template.innerHTML = html;
      const page = template.content;
      if (current !== generation || !dialog.open) return;
      const marker = page.querySelector('meta[name="sr2-quick-view-product"]');
      if (!marker || !/^\d+$/.test(marker.content)) throw Error('Product not public');
      const product = page.getElementById(`product-${marker.content}`);
      const form = product?.querySelector('form.cart');
      if (!form || !['simple', 'variable'].includes(marker.dataset.productType)) throw Error('Use product page');
      if (form.querySelector('script, iframe, object, embed') || form.querySelector('[formaction]')) throw Error('Unsupported purchase form');
      // Never import executable attributes or embedded scripts from the document.
      for (const element of [form, ...form.querySelectorAll('*')]) {
        for (const attribute of [...element.attributes]) {
          if (/^on/i.test(attribute.name) || attribute.name === 'srcdoc') element.removeAttribute(attribute.name);
        }
        for (const name of ['href', 'src', 'action']) {
          if (element.hasAttribute(name)) sameOrigin(element.getAttribute(name), responseUrl.href);
        }
      }
      form.action = sameOrigin(form.getAttribute('action') || responseUrl.href, responseUrl.href).href;
      form.method = 'post';
      form.removeAttribute('target');
      // IDs are isolated from any underlying PDP; keep native label relationships.
      const ids = new Map();
      form.querySelectorAll('[id]').forEach((element, index) => {
        const id = `sr2-qv-${current}-${index}`;
        ids.set(element.id, id);
        element.id = id;
      });
      form.removeAttribute('id');
      form.querySelectorAll('[for], [aria-describedby], [aria-labelledby]').forEach((element) => {
        for (const attribute of ['for', 'aria-describedby', 'aria-labelledby']) {
          if (element.hasAttribute(attribute)) element.setAttribute(attribute, element.getAttribute(attribute).split(/\s+/).map((id) => ids.get(id) || id).join(' '));
        }
      });
      const variable = form.matches('.variations_form');
      if (variable) {
        await ensureVariationRuntime();
        if (current !== generation || !dialog.open) return;
        if (controller.signal.aborted) throw Error('Product request timed out');
      }
      const price = product.querySelector('.summary .price');
      const stock = product.querySelector('.summary > .stock');
      if (price) dialog.querySelector('[data-quick-view-price]').textContent = price.textContent.trim();
      dialog.querySelector('[data-quick-view-availability]').textContent = stock?.textContent.trim() || '';
      purchase.append(document.importNode(form, true));
      const nativeForm = purchase.querySelector('form');
      nativeForm.addEventListener('submit', (event) => {
        if (event.defaultPrevented) return;
        if (nativeForm.dataset.submitting === 'true') { event.preventDefault(); return; }
        nativeForm.dataset.submitting = 'true';
        nativeForm.querySelector('.single_add_to_cart_button')?.setAttribute('aria-busy', 'true');
        if (status.dataset.submitting) status.textContent = status.dataset.submitting;
        cardState('submitting');
        queueMicrotask(() => {
          if (!event.defaultPrevented) return;
          delete nativeForm.dataset.submitting;
          nativeForm.querySelector('[aria-busy]')?.removeAttribute('aria-busy');
          if (current === generation && dialog.open) { status.textContent = status.dataset.ready; cardState('ready'); }
        });
      });
      if (variable) {
        const image = dialog.querySelector('[data-quick-view-image]');
        const originalImage = image ? { src: image.getAttribute('src'), alt: image.alt } : null;
        const $form = window.jQuery(nativeForm);
        const button = nativeForm.querySelector('.single_add_to_cart_button');
        button?.setAttribute('aria-disabled', 'true');
        $form.on('show_variation.sr2QuickView', (_event, _variation, purchasable) => {
          if (current === generation && dialog.open) button?.setAttribute('aria-disabled', String(!purchasable));
        });
        $form.on('hide_variation.sr2QuickView', () => {
          if (current === generation && dialog.open) button?.setAttribute('aria-disabled', 'true');
        });
        $form.on('found_variation.sr2QuickView', (_event, variation) => {
          if (current !== generation || !dialog.open || !image || !variation?.image?.src) return;
          const source = new URL(variation.image.src, responseUrl.href);
          if (!['https:', 'http:'].includes(source.protocol)) return;
          image.src = source.href;
          image.alt = variation.image.alt || originalImage.alt;
        });
        $form.on('reset_data.sr2QuickView', () => {
          if (current === generation && dialog.open && image && originalImage) {
            image.setAttribute('src', originalImage.src || '');
            image.alt = originalImage.alt;
          }
        });
        $form.wc_variation_form();
      }
      status.textContent = status.dataset.ready;
      cardState('ready');
    } catch (error) {
      if (current !== generation || (error.name === 'AbortError' && !timedOut)) return;
      purchase.replaceChildren();
      status.textContent = status.dataset.error;
      cardState('error');
    } finally {
      clearTimeout(deadline);
      if (current === generation) purchase.removeAttribute('aria-busy');
    }
  };
  new MutationObserver(load).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  new MutationObserver(() => { if (dialog.open) load(); }).observe(link, { attributes: true, attributeFilter: ['href'] });
  window.addEventListener('pageshow', () => {
    const form = purchase.querySelector('form');
    if (form) { delete form.dataset.submitting; form.querySelector('[aria-busy]')?.removeAttribute('aria-busy'); status.textContent = status.dataset.ready; }
  });
  dialog.addEventListener('close', () => { if (!dialog.open) clean(); });
})();
