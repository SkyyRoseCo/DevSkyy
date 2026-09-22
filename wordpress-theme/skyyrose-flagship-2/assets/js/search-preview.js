/** Native search previews. Enqueue after theme.js; CSS after global-shell/controls.
 * Never intercept submission, copy server markup into the live DOM, or fetch media.
 */
(() => {
  'use strict';
  const dialog = document.querySelector('#sr2-search-dialog');
  const form = dialog?.querySelector('.sr2-search-dialog__form');
  const input = form?.querySelector('[data-search-input]');
  const preview = dialog?.querySelector('[data-search-preview]');
  const list = preview?.querySelector('[data-search-preview-results]');
  const status = preview?.querySelector('[role="status"]');
  if (!input || !list || !status || !window.fetch || !window.AbortController || dialog.dataset.searchPreviewInitialized) return;
  dialog.dataset.searchPreviewInitialized = 'true';

  const MAX_RESULTS = 6;
  let timer;
  let controller;
  let revision = 0;
  let composing = false;
  const clear = () => {
    revision += 1;
    window.clearTimeout(timer);
    controller?.abort();
    controller = null;
    list.replaceChildren();
    list.removeAttribute('aria-busy');
  };
  const message = (key) => { status.textContent = preview.dataset[key] || ''; };
  const safeURL = (value) => {
    try {
      const url = new URL(value, form.action);
      return /^https?:$/.test(url.protocol) && url.origin === window.location.origin && !url.username && !url.password ? url : null;
    } catch { return null; }
  };
  const readResults = (html) => {
    // Template contents are inert: unlike detached documents, no media is loaded.
    const template = document.createElement('template');
    template.innerHTML = html;
    const root = template.content.querySelector('main.sr2-search');
    if (!root) throw new Error('Not a native search response');
    const rows = [];
    const seen = new Set();
    root.querySelectorAll('[data-search-group]').forEach((group) => {
      const context = group.querySelector('.sr2-section-head h2')?.textContent.trim() || '';
      group.querySelectorAll('.sr2-c-editorial-card__title a, .sr2-search__result h2 a').forEach((link) => {
        const url = safeURL(link.getAttribute('href'));
        const title = link.textContent.trim();
        if (!url || !title || seen.has(url.href) || rows.length >= MAX_RESULTS) return;
        seen.add(url.href);
        const collection = link.closest('.sr2-c-editorial-card')?.querySelector('.sr2-c-editorial-card__collection')?.textContent.trim();
        rows.push({ url: url.href, title, context: collection ? `${context} · ${collection}` : context });
      });
    });
    // An unexpected card contract must not masquerade as zero real results.
    if (!rows.length && !root.querySelector('.sr2-search__empty')) throw new Error('Unrecognized search results');
    return rows;
  };
  const search = async (query, ownRevision) => {
    if (!dialog.open || ownRevision !== revision) return;
    const url = safeURL(form.action);
    if (!url) { message('error'); return; }
    url.searchParams.set('s', query);
    const request = new AbortController();
    controller = request;
    const deadline = window.setTimeout(() => request.abort(), 10000);
    message('loading');
    list.setAttribute('aria-busy', 'true');
    try {
      const response = await window.fetch(url.href, { signal: request.signal, credentials: 'same-origin', redirect: 'error', headers: { Accept: 'text/html' } });
      if (!response.ok || (response.url && !safeURL(response.url)) || !/text\/html/i.test(response.headers.get('content-type') || '')) throw new Error('Search response failed');
      const html = await response.text();
      if (html.length > 1500000) throw new Error('Search response exceeds preview limit');
      if (ownRevision !== revision || !dialog.open) return;
      if (request.signal.aborted) throw new Error('Search timed out');
      const rows = readResults(html);
      rows.forEach(({ url: href, title, context }) => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        const label = document.createElement('span');
        const group = document.createElement('small');
        link.href = href;
        label.textContent = title;
        group.textContent = context;
        link.append(label, group);
        item.append(link);
        list.append(item);
      });
      if (rows.length) status.textContent = preview.dataset.count.replace('%d', String(rows.length));
      else message('empty');
    } catch {
      if (ownRevision === revision && dialog.open) message('error');
    } finally {
      window.clearTimeout(deadline);
      if (ownRevision === revision) {
        list.removeAttribute('aria-busy');
        controller = null;
      }
    }
  };
  const schedule = () => {
    clear();
    message('idle');
    const query = input.value.trim();
    if (!dialog.open || composing || query.length < 2) return;
    const ownRevision = revision;
    timer = window.setTimeout(() => search(query, ownRevision), 280);
  };
  input.addEventListener('input', schedule);
  input.addEventListener('compositionstart', () => { composing = true; clear(); message('idle'); });
  input.addEventListener('compositionend', () => { composing = false; schedule(); });
  // Focus remains with the customer; results are ordinary Tab/Enter links.
  dialog.addEventListener('close', () => { clear(); message('idle'); });
  // Attribute observation also handles overlay swaps and native open/close.
  new MutationObserver(() => {
    if (!dialog.open) { clear(); message('idle'); }
    else schedule();
  }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  form.addEventListener('submit', clear);
  preview.hidden = false;
  message('idle');
})();
