/** Offline consent/transport fixtures. Authentication and live commerce: N/A. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const { JSDOM } = require('jsdom');
const renderedCard = require('./rendered-card.cjs')();
const theme = path.resolve(__dirname, '../..');
const bannerScript = fs
  .readFileSync(path.join(theme, 'template-parts/cookie-consent.php'), 'utf8')
  .match(/<script>([\s\S]*?)<\/script>/)[1];
const html = `<button id="outside">Outside</button><div class="product-grid__items"></div>
<div id="skyyrose-cookie-consent" class="cookie-consent cookie-consent--hidden" hidden style="position:fixed">
<a href="/privacy-policy/" id="privacy">Privacy</a><button id="skyyrose-cookie-accept">Accept</button><button id="skyyrose-cookie-decline">Decline</button></div>
${renderedCard}`;
function fixture({
  consent,
  blocked = false,
  reply,
  source = 'experience-analyzer.js',
  personalization = false,
  sharedStorage,
  now = Date.now(),
  session,
  legacyVisitor,
  noAbort = false,
  writeBlocked = false,
} = {}) {
  const dom = new JSDOM(html, { url: 'https://fixture.test/collections/fixture/', runScripts: 'outside-only' });
  const w = dom.window;
  Object.defineProperty(w.document, 'readyState', { value: 'complete' });
  const stored = sharedStorage || new Map(consent ? [['skyyrose_cookie_consent', consent]] : []);
  if (session !== undefined) stored.set('skyy_analytics_session', session);
  if (legacyVisitor) stored.set('skyy_vh', legacyVisitor);
  let clock = now;
  w.Date.now = () => clock;
  const writes = [];
  Object.defineProperty(w, 'localStorage', {
    value: {
      getItem(k) {
        if (blocked) throw new Error('blocked');
        return stored.get(k) ?? null;
      },
      setItem(k, v) {
        if (blocked || (writeBlocked && k === 'skyy_analytics_session')) throw new Error('blocked');
        stored.set(k, v);
        writes.push(k);
      },
      removeItem(k) {
        if (blocked) throw new Error('blocked');
        stored.delete(k);
      },
    },
  });
  const intervals = new Set();
  w.setInterval = fn => {
    intervals.add(fn);
    return fn;
  };
  w.clearInterval = fn => intervals.delete(fn);
  const timeouts = new Map();
  let nextTimer = 1;
  w.setTimeout = (fn, delay) => {
    const id = nextTimer++;
    timeouts.set(id, { fn, due: clock + delay });
    return id;
  };
  w.clearTimeout = id => timeouts.delete(id);
  w.requestIdleCallback = fn => fn();
  const observers = [];
  w.IntersectionObserver = class {
    constructor(callback) {
      this.callback = callback;
      this.disconnected = false;
      this.observed = new Set();
      observers.push(this);
    }
    observe(el) {
      this.observed.add(el);
    }
    unobserve(el) {
      this.observed.delete(el);
    }
    disconnect() {
      this.disconnected = true;
    }
  };
  const requests = [];
  if (noAbort) w.AbortController = undefined;
  w.fetch = (url, options) => {
    requests.push({ url, options, body: options.body ? JSON.parse(options.body) : null });
    if (reply) return reply(requests.at(-1));
    const ids = requests.at(-1).body?.events?.map(e => e.event_id) || [];
    return Promise.resolve({
      ok: true,
      json: async () =>
        personalization && !options.body
          ? { products: [] }
          : { status: 'accepted', event_ids: ids, accepted: ids.length, duplicates: 0 },
    });
  };
  const beacons = [];
  w.navigator.sendBeacon = (...args) => {
    beacons.push(args);
    return true;
  };
  const notices = [];
  ['accepted', 'declined', 'changed'].forEach(name =>
    w.document.addEventListener('skyyrose:consent-' + name, e => notices.push([name, e.detail.consent]))
  );
  w.document.getElementById('outside').focus();
  w.skyyroseSEE = { key: 'public-token', endpoint: '/store/wp-json/skyyrose/v1/analytics/events' };
  w.SkyyCurated = { restBase: '/?rest_route=/skyyrose/v1', collection: '', limit: 4 };
  w.eval(bannerScript);
  w.eval(fs.readFileSync(path.join(theme, 'assets/js', source), 'utf8'));
  if (personalization) w.eval(fs.readFileSync(path.join(theme, 'assets/js/personalization.js'), 'utf8'));
  const delivery = [];
  w.document.addEventListener('skyyrose:analytics-delivery', e => delivery.push(e.detail.status));
  return {
    w,
    dom,
    stored,
    writes,
    requests,
    beacons,
    intervals,
    timeouts,
    observers,
    notices,
    delivery,
    accept: () => w.document.getElementById('skyyrose-cookie-accept').click(),
    decline: () => w.document.getElementById('skyyrose-cookie-decline').click(),
    revoke: () => w.document.dispatchEvent(new w.CustomEvent('skyyrose:consent-revoke')),
    tick: () => intervals.forEach(fn => fn()),
    advance: ms => {
      clock += ms;
      timeouts.forEach((timer, id) => {
        if (timer.due <= clock) {
          timeouts.delete(id);
          timer.fn();
        }
      });
    },
    exit: () => w.dispatchEvent(new w.Event('pagehide')),
    close: () => dom.window.close(),
  };
}
const settle = () => new Promise(resolve => setImmediate(resolve));
for (const source of ['experience-analyzer.js', 'experience-analyzer.min.js']) {
  test(source + ': no choice, decline and reload create no analytics identifier, queue or beacon', async () => {
    for (const consent of [undefined, 'declined']) {
      const f = fixture({ consent, source });
      f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
      f.exit();
      f.tick();
      assert.equal(f.requests.length, 0);
      assert.equal(f.beacons.length, 0);
      assert.equal(f.intervals.size, 0);
      assert.equal(f.observers.length, 0);
      assert.equal(f.writes.includes('skyy_vh'), false);
      assert.equal(f.writes.includes('skyy_analytics_session'), false);
      f.close();
    }
  });
  test(source + ': explicit accept starts tracking, reports CTA engagement and matching ack drains queue', async () => {
    const f = fixture({ source });
    f.accept();
    assert.equal(f.stored.has('skyy_analytics_session'), true);
    assert.equal(f.stored.has('skyy_vh'), false);
    assert.equal(f.intervals.size, 1);
    assert.deepEqual(f.notices.slice(0, 2), [
      ['accepted', 'accepted'],
      ['changed', 'accepted'],
    ]);
    f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
    f.tick();
    await settle();
    assert.equal(f.requests.length, 1);
    assert.ok(f.requests[0].url.includes('/store/wp-json/skyyrose/v1/analytics/events'));
    const events = f.requests[0].body.events;
    assert.deepEqual(
      events.map(e => e.event_type),
      ['page_view', 'product_click']
    );
    assert.equal(events[1].properties.action, 'buy');
    assert.equal(events[1].page_type, 'collection');
    assert.equal(events[1].target, 'fixture-001');
    assert.equal(events[1].collection, 'fixture');
    assert.equal(events[0].session_id, JSON.parse(f.stored.get('skyy_analytics_session')).id);
    assert.match(events[0].event_id, /^[a-f0-9-]{36}$/);
    assert.equal(f.beacons.length, 0);
    f.tick();
    f.exit();
    assert.equal(f.requests.length, 1);
    f.close();
  });
  test(source + ': accepted reload starts, revocation deletes identifier and stops observers/queue/delivery', () => {
    const f = fixture({ consent: 'accepted', source });
    assert.equal(f.intervals.size, 1);
    f.revoke();
    assert.equal(f.stored.has('skyy_vh'), false);
    assert.equal(f.stored.has('skyy_analytics_session'), false);
    assert.equal(f.intervals.size, 0);
    assert.equal(f.observers[0].disconnected, true);
    f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
    f.tick();
    f.exit();
    assert.equal(f.requests.length, 0);
    assert.equal(f.beacons.length, 0);
    assert.ok(f.w.document.cookie.includes('skyyrose_cookie_consent=declined'));
    f.close();
  });
  test(source + ': unavailable storage fails closed even on accept', () => {
    const f = fixture({ consent: 'accepted', blocked: true, source });
    f.accept();
    f.exit();
    assert.equal(f.requests.length, 0);
    assert.equal(f.intervals.size, 0);
    assert.equal(f.observers.length, 0);
    assert.equal(f.beacons.length, 0);
    assert.deepEqual(f.notices.slice(0, 2), [
      ['declined', 'declined'],
      ['changed', 'declined'],
    ]);
    f.close();
  });
  test(source + ': transport failure and forged acknowledgement retain identical event IDs for retry', async () => {
    let attempt = 0;
    const f = fixture({
      consent: 'accepted',
      source,
      reply(request) {
        attempt += 1;
        if (attempt === 1) return Promise.reject(new Error('offline'));
        if (attempt === 2)
          return Promise.resolve({
            ok: true,
            json: async () => ({ status: 'accepted', accepted: 1, duplicates: 0, event_ids: ['forged'] }),
          });
        return Promise.resolve({
          ok: true,
          json: async () => ({
            status: 'accepted',
            accepted: 1,
            duplicates: 0,
            event_ids: request.body.events.map(e => e.event_id),
          }),
        });
      },
    });
    for (let i = 0; i < 3; i++) {
      f.tick();
      await settle();
    }
    assert.equal(f.requests.length, 3);
    assert.equal(f.requests[0].body.events[0].event_id, f.requests[2].body.events[0].event_id);
    f.tick();
    assert.equal(f.requests.length, 3);
    f.close();
  });
  test(source + ': revocation aborts in-flight delivery and ignores late acknowledgement', async () => {
    const resolutions = [];
    const f = fixture({ consent: 'accepted', source, reply: () => new Promise(resolve => resolutions.push(resolve)) });
    f.tick();
    const signal = f.requests[0].options.signal;
    const oldObserver = f.observers[0];
    f.revoke();
    assert.equal(signal.aborted, true);
    assert.equal(f.timeouts.size, 0);
    f.advance(15000);
    assert.deepEqual(f.delivery, []);
    f.accept();
    oldObserver.callback([{ target: f.w.document.querySelector('.sr2-c-editorial-card'), isIntersecting: true }]);
    f.tick();
    assert.equal(f.requests[1].body.events.length, 1);
    assert.notEqual(f.requests[0].body.events[0].session_id, f.requests[1].body.events[0].session_id);
    resolutions[0]({
      ok: true,
      json: async () => ({
        status: 'accepted',
        accepted: 1,
        duplicates: 0,
        event_ids: f.requests[0].body.events.map(e => e.event_id),
      }),
    });
    await settle();
    f.exit();
    assert.equal(f.requests.length, 2);
    assert.equal(f.timeouts.size, 1);
    resolutions[1]({
      ok: true,
      json: async () => ({
        status: 'accepted',
        accepted: 1,
        duplicates: 0,
        event_ids: f.requests[1].body.events.map(e => e.event_id),
      }),
    });
    await settle();
    f.tick();
    assert.equal(f.requests.length, 2);
    assert.deepEqual(f.delivery, ['accepted']);
    assert.equal(f.timeouts.size, 0);
    f.close();
  });
  test(source + ': actual PHP card observes one wrapper and resolves nested CTA SKU and collection', async () => {
    const f = fixture({ consent: 'accepted', source });
    const card = f.w.document.querySelector('.sr2-c-editorial-card[data-sku]');
    const buy = card.querySelector('.sr2-c-editorial-card__actions .button');
    const wishlist = card.querySelector('[data-quick-view]');
    assert.equal(card.tagName, 'ARTICLE');
    assert.equal(card.dataset.productId, undefined);
    assert.equal(buy.dataset.nativeProduct, '9');
    assert.equal(wishlist.dataset.quickViewName, 'Fixture product');
    assert.deepEqual([...f.observers[0].observed], [card]);
    f.observers[0].callback([{ target: card, isIntersecting: true }]);
    f.observers[0].callback([{ target: card, isIntersecting: true }]);
    assert.equal(f.observers[0].observed.size, 0);
    buy.click();
    wishlist.click();
    f.tick();
    await settle();
    assert.ok(f.requests[0].url.includes('/store/wp-json/skyyrose/v1/analytics/events'));
    const events = f.requests[0].body.events;
    assert.deepEqual(
      events.map(e => e.event_type),
      ['page_view', 'product_view', 'product_click', 'product_click']
    );
    assert.deepEqual(
      events.slice(1).map(e => [e.target, e.collection]),
      Array(3).fill(['fixture-001', 'fixture'])
    );
    assert.deepEqual(
      events.slice(2).map(e => e.properties.action),
      ['buy', 'quickview']
    );
    f.close();
  });
  test(source + ': consented tabs share an analytics session without the persistent visitor key', async () => {
    const now = Date.UTC(2026, 8, 29);
    const visitor = 'a'.repeat(32);
    const sharedStorage = new Map([
      ['skyyrose_cookie_consent', 'accepted'],
      ['skyy_vh', visitor],
    ]);
    const first = fixture({ sharedStorage, source, now });
    const firstSession = JSON.parse(sharedStorage.get('skyy_analytics_session'));
    const second = fixture({ sharedStorage, source, now: now + 60000 });
    const secondSession = JSON.parse(sharedStorage.get('skyy_analytics_session'));
    assert.equal(firstSession.id, secondSession.id);
    assert.notEqual(firstSession.id, visitor);
    assert.equal(secondSession.last_activity, now + 60000);
    first.advance(120000);
    first.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
    first.tick();
    second.tick();
    await settle();
    assert.equal(first.requests[0].body.events[1].session_id, second.requests[0].body.events[0].session_id);
    assert.equal(JSON.parse(sharedStorage.get('skyy_analytics_session')).last_activity, now + 120000);
    assert.equal(sharedStorage.get('skyy_vh'), visitor);
    first.close();
    second.close();
  });
  test(source + ': accepted pushes extend activity and exactly 30 idle minutes rotate the session', async () => {
    const now = Date.UTC(2026, 8, 29);
    const f = fixture({ consent: 'accepted', source, now });
    const initial = JSON.parse(f.stored.get('skyy_analytics_session')).id;
    for (let i = 1; i <= 2; i++) {
      f.advance(20 * 60000);
      f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
      assert.equal(JSON.parse(f.stored.get('skyy_analytics_session')).id, initial);
      assert.equal(JSON.parse(f.stored.get('skyy_analytics_session')).last_activity, now + i * 20 * 60000);
    }
    f.advance(30 * 60000);
    f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
    const rotated = JSON.parse(f.stored.get('skyy_analytics_session')).id;
    assert.notEqual(rotated, initial);
    f.tick();
    await settle();
    assert.deepEqual(
      f.requests[0].body.events.map(e => e.session_id),
      [initial, initial, initial, rotated]
    );
    f.close();
  });
  test(source + ': malformed or future session storage fails closed without a visitor fallback', () => {
    const now = Date.UTC(2026, 8, 29);
    for (const session of [
      '',
      'invalid-json',
      'null',
      '[]',
      JSON.stringify({ id: 'bad', last_activity: now }),
      JSON.stringify({ id: 'b'.repeat(32), last_activity: now + 1 }),
      JSON.stringify({ id: 'b'.repeat(32), last_activity: String(now) }),
      JSON.stringify({ id: 'b'.repeat(32), last_activity: 0 }),
    ]) {
      const f = fixture({ consent: 'accepted', source, now, session, legacyVisitor: 'a'.repeat(32) });
      f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
      f.tick();
      f.exit();
      assert.equal(f.requests.length, 0);
      assert.equal(f.intervals.size, 0);
      assert.equal(f.observers.length, 0);
      assert.equal(f.stored.has('skyy_analytics_session'), false);
      assert.equal(f.stored.has('skyy_vh'), false);
      f.close();
    }
  });
  test(source + ': session write failure or corruption during collection stops and clears queued events', () => {
    for (const writeBlocked of [false, true]) {
      const f = fixture({ consent: 'accepted', source, writeBlocked });
      if (!writeBlocked) f.stored.set('skyy_analytics_session', 'corrupt');
      f.w.document.querySelector('.sr2-c-editorial-card__actions .button').click();
      f.tick();
      f.exit();
      assert.equal(f.requests.length, 0);
      assert.equal(f.intervals.size, 0);
      assert.equal(f.stored.has('skyy_analytics_session'), false);
      f.close();
    }
  });
  test(
    source + ': a stalled fetch expires at 15 seconds and retries identical IDs even without AbortController',
    async () => {
      for (const noAbort of [false, true]) {
        let lateResolve;
        const f = fixture({
          consent: 'accepted',
          source,
          noAbort,
          reply(request) {
            if (!lateResolve)
              return new Promise(resolve => {
                lateResolve = resolve;
              });
            const ids = request.body.events.map(e => e.event_id);
            return Promise.resolve({
              ok: true,
              json: async () => ({ status: 'accepted', accepted: ids.length, duplicates: 0, event_ids: ids }),
            });
          },
        });
        f.tick();
        const signal = f.requests[0].options.signal;
        f.advance(14999);
        f.tick();
        assert.equal(f.requests.length, 1);
        if (signal) assert.equal(signal.aborted, false);
        f.advance(1);
        if (signal) assert.equal(signal.aborted, true);
        assert.deepEqual(f.delivery, ['unavailable']);
        f.tick();
        await settle();
        assert.equal(f.requests.length, 2);
        assert.deepEqual(f.requests[0].body.events, f.requests[1].body.events);
        lateResolve({
          ok: true,
          json: async () => ({
            status: 'accepted',
            accepted: 1,
            duplicates: 0,
            event_ids: f.requests[0].body.events.map(e => e.event_id),
          }),
        });
        await settle();
        f.tick();
        assert.equal(f.requests.length, 2);
        assert.deepEqual(f.delivery, ['unavailable', 'accepted']);
        assert.equal(f.timeouts.size, 0);
        f.close();
      }
    }
  );
  test(source + ': a late acknowledgement cannot drain the queue or release a newer pending attempt', async () => {
    const acknowledgements = [];
    const f = fixture({
      consent: 'accepted',
      source,
      reply: () => Promise.resolve({ ok: true, json: () => new Promise(resolve => acknowledgements.push(resolve)) }),
    });
    f.tick();
    await settle();
    f.advance(15000);
    f.tick();
    await settle();
    const ack = {
      status: 'accepted',
      accepted: 1,
      duplicates: 0,
      event_ids: f.requests[0].body.events.map(e => e.event_id),
    };
    acknowledgements[0](ack);
    await settle();
    f.tick();
    assert.equal(f.requests.length, 2);
    assert.equal(f.timeouts.size, 1);
    assert.deepEqual(f.delivery, ['unavailable']);
    f.advance(15000);
    assert.equal(f.requests[1].options.signal.aborted, true);
    f.tick();
    await settle();
    assert.equal(f.requests.length, 3);
    assert.deepEqual(f.requests[2].body.events, f.requests[0].body.events);
    acknowledgements[1](ack);
    await settle();
    f.tick();
    assert.equal(f.requests.length, 3);
    acknowledgements[2](ack);
    await settle();
    f.tick();
    assert.equal(f.requests.length, 3);
    assert.deepEqual(f.delivery, ['unavailable', 'unavailable', 'accepted']);
    assert.equal(f.timeouts.size, 0);
    f.close();
  });
}
test('banner restores focus, traps Tab, Escape declines and privacy event can reopen', () => {
  const f = fixture();
  const d = f.w.document;
  f.advance(100);
  assert.equal(d.activeElement.id, 'skyyrose-cookie-accept');
  d.getElementById('skyyrose-cookie-decline').focus();
  d.dispatchEvent(new f.w.KeyboardEvent('keydown', { key: 'Tab', cancelable: true }));
  assert.equal(d.activeElement.id, 'privacy');
  d.dispatchEvent(new f.w.KeyboardEvent('keydown', { key: 'Escape' }));
  assert.equal(d.activeElement.id, 'outside');
  assert.equal(f.stored.get('skyyrose_cookie_consent'), 'declined');
  d.dispatchEvent(new f.w.CustomEvent('skyyrose:consent-open'));
  f.advance(100);
  assert.equal(d.activeElement.id, 'skyyrose-cookie-accept');
  f.close();
});

for (const endpoint of ['', 'https://untrusted.test/ingest']) {
  test('V2 refuses missing or cross-origin endpoint: ' + endpoint, async () => {
    const f = fixture({ consent: 'accepted' });
    f.w.skyyroseSEE.endpoint = endpoint;
    f.tick();
    await settle();
    assert.equal(f.requests.length, 0);
    assert.ok(f.delivery.includes('unavailable'));
    f.close();
  });
}
