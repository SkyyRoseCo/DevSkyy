/* Small progressive states; native links, approved media and Woo events retain authority. */
(() => {
  'use strict';
  if (document.documentElement.dataset.sr2PremiumInitialized) return;
  document.documentElement.dataset.sr2PremiumInitialized = 'true';
  document.querySelectorAll('.sr2-c-editorial-card').forEach((card) => {
    if (card.dataset.premiumInitialized) return;
    card.dataset.premiumInitialized = 'true';
    const image = card.querySelector('.sr2-c-editorial-card__product-image');
    const failure = card.querySelector('[data-card-image-error]');
    const settle = () => {
      const failed = image.complete && image.naturalWidth === 0;
      card.dataset.imageState = failed ? 'error' : image.complete ? 'ready' : 'loading';
      if (failure) failure.hidden = !failed;
    };
    if (image) { image.addEventListener('load', settle); image.addEventListener('error', settle); settle(); }
    card.addEventListener('pointerdown', () => { card.dataset.touchState = 'active'; });
    const release = () => { delete card.dataset.touchState; };
    card.addEventListener('pointerup', release);
    card.addEventListener('pointercancel', release);
    card.addEventListener('pointerleave', release);
  });
  if (window.jQuery) {
    const queues = new Map();
    const requests = new WeakMap();
    const feedback = (card, state) => {
      if (!card) return;
      card.dataset.cartState = state;
      const status = card.querySelector('[data-card-cart-feedback]');
      if (status) { status.textContent = state === 'success' ? status.dataset.added : state === 'error' ? status.dataset.failed : ''; status.hidden = !status.textContent; }
    };
    window.jQuery(document.body).on('adding_to_cart.sr2Premium', (_event, $button, data) => {
      const card = $button?.[0]?.closest('.sr2-c-editorial-card');
      if (!card) return;
      feedback(card, 'loading');
      const id = String(data?.product_id || $button[0].dataset.product_id || '');
      if (id) queues.set(id, [...(queues.get(id) || []), { card, button: $button[0] }]);
    }).on('added_to_cart.sr2Premium', (_event, _fragments, _hash, $button) => {
      feedback($button?.[0]?.closest('.sr2-c-editorial-card'), 'success');
    });
    // Observe only Woo's own add-to-cart transport, pairing concurrent requests to their initiating cards.
    window.jQuery(document).on('ajaxSend.sr2Premium', (_event, xhr, settings) => {
      let url;
      try { url = new URL(settings.url, location.href); } catch { return; }
      if (url.origin !== location.origin || url.searchParams.get('wc-ajax') !== 'add_to_cart') return;
      const id = String(typeof settings.data === 'string' ? new URLSearchParams(settings.data).get('product_id') || '' : settings.data?.product_id || '');
      const queue = queues.get(id);
      if (queue?.length) { requests.set(xhr, queue.shift()); if (!queue.length) queues.delete(id); }
    }).on('ajaxError.sr2Premium', (_event, xhr) => {
      const request = requests.get(xhr);
      feedback(request?.card, 'error');
      request?.button.classList.remove('loading');
      request?.button.removeAttribute('aria-busy');
    }).on('ajaxComplete.sr2Premium', (_event, xhr) => { requests.delete(xhr); });
    window.addEventListener('pagehide', () => queues.clear());
  }
  const typeTargets = [...document.querySelectorAll('[data-sr2-type-motion="editorial"], [data-sr2-type-motion="collection"], [data-sr2-type-motion="statement"]')];
  if (typeTargets.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(({ target, isIntersecting }) => {
        if (isIntersecting) { target.classList.add('is-type-visible'); observer.unobserve(target); }
      });
    }, { threshold: 0.1 });
    const observe = () => typeTargets.filter(target => !target.classList.contains('is-type-visible')).forEach(target => observer.observe(target));
    observe();
    window.addEventListener('pagehide', () => observer.disconnect());
    window.addEventListener('pageshow', observe);
  }
  const nav = document.querySelector('.sr2-house-nav__collections');
  const entries = nav ? [...nav.querySelectorAll('.sr2-house-nav__preview-entry')] : [];
  if (entries.length && !nav.dataset.previewInitialized) {
    nav.dataset.previewInitialized = 'true';
    const stage = document.createElement('figure');
    stage.id = 'sr2-nav-preview-stage';
    stage.className = 'sr2-house-nav__preview-stage';
    const image = document.createElement('img');
    image.width = 1024; image.height = 576; image.alt = ''; image.decoding = 'async'; image.hidden = true;
    const caption = document.createElement('figcaption');
    stage.append(image, caption);
    nav.querySelector('.sr2-house-nav__previews').before(stage);
    nav.classList.add('is-preview-enhanced');
    let generation = 0;
    let active;
    let pendingImage;
    const preview = async (entry) => {
      if (active === entry) return;
      active = entry;
      const current = ++generation;
      const source = entry.querySelector('img');
      const link = entry.querySelector('a');
      const label = link.querySelector('span')?.textContent || '';
      entries.forEach(item => item.querySelector('button').setAttribute('aria-pressed', String(item === entry)));
      stage.dataset.state = 'loading';
      stage.setAttribute('aria-busy', 'true');
      const next = new Image();
      pendingImage = next;
      next.src = source.currentSrc || source.src;
      try {
        let timer;
        try { await Promise.race([next.decode(), new Promise((_, reject) => { timer = setTimeout(() => reject(Error('Preview timed out')), 8000); })]); }
        finally { clearTimeout(timer); }
        if (current !== generation) return;
        image.src = next.src;
        image.hidden = false;
        caption.textContent = label;
        stage.dataset.state = 'ready';
      } catch {
        if (current !== generation) return;
        image.hidden = true;
        caption.textContent = label;
        stage.dataset.state = 'error';
      } finally {
        if (current === generation) stage.removeAttribute('aria-busy');
      }
    };
    entries.forEach(entry => {
      const button = entry.querySelector('button');
      button.hidden = false;
      button.addEventListener('click', () => preview(entry));
      entry.querySelector('a').addEventListener('focus', () => preview(entry));
      entry.addEventListener('pointerenter', event => { if (event.pointerType !== 'touch') preview(entry); });
    });
    const menu = document.querySelector('[data-sr2-menu]');
    const cancel = () => {
      generation += 1;
      if (pendingImage) pendingImage.src = '';
      pendingImage = null;
      active = null;
      stage.removeAttribute('aria-busy');
    };
    if (menu) {
      const observer = new MutationObserver(() => {
        if (menu.getAttribute('aria-expanded') === 'true') preview(active || entries[0]);
        else cancel();
      });
      const observe = () => observer.observe(menu, { attributes: true, attributeFilter: ['aria-expanded'] });
      observe();
      window.addEventListener('pagehide', () => { observer.disconnect(); cancel(); });
      window.addEventListener('pageshow', observe);
    }
  }
})();
