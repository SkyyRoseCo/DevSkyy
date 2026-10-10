/** Local route trace: actual observer timeline plus CDP timings; never inferred field CWV. */
const fs = require('node:fs');
const path = require('node:path');
const { requireQa, base, out, validateLabel } = require('./runtime.cjs');
const label = process.argv[2] || 'trace';
validateLabel(label);
const names = (process.env.V2_TRACE_ROUTES || 'home,shop,pdp').split(',');
const routes = {
  home: '/',
  shop: '/shop/',
  collection: '/collections/signature/',
  pdp: '/product/sg-005/',
  cart: '/cart/',
  checkout: '/checkout/',
};
(async () => {
  const browser = await requireQa('playwright').chromium.launch();
  const rows = [];
  try {
    for (const name of names) {
      if (!routes[name]) throw Error('Unknown route');
      const c = await browser.newContext({
        viewport: {
          width: Number(process.env.V2_TRACE_WIDTH || 390),
          height: Number(process.env.V2_TRACE_WIDTH || 390) < 768 ? 844 : 1000,
        },
        deviceScaleFactor: 1,
        reducedMotion: 'no-preference',
      });
      await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
      await c.addInitScript(() => {
        window.sr2Trace = { lcp: [], shifts: [], longTasks: [], events: [] };
        const note = (kind, data = {}) => window.sr2Trace.events.push({ kind, at: performance.now(), ...data });
        for (const [type, key, convert] of [
          [
            'largest-contentful-paint',
            'lcp',
            e => ({
              start: e.startTime,
              render: e.renderTime,
              load: e.loadTime,
              size: e.size,
              url: e.url,
              tag: e.element?.tagName,
              element: e.element?.outerHTML?.slice(0, 2000),
              currentSrc: e.element?.currentSrc,
            }),
          ],
          ['layout-shift', 'shifts', e => ({ start: e.startTime, value: e.value, recent: e.hadRecentInput })],
          ['longtask', 'longTasks', e => ({ start: e.startTime, duration: e.duration, name: e.name })],
        ])
          try {
            new PerformanceObserver(l => l.getEntries().forEach(e => window.sr2Trace[key].push(convert(e)))).observe({
              type,
              buffered: true,
            });
          } catch {}
        addEventListener('DOMContentLoaded', () => {
          note('DOMContentLoaded');
          document.fonts.ready.then(() => note('fonts-ready-after-dom'));
        });
        document.fonts.addEventListener('loadingdone', () => note('fonts-loadingdone'));
        addEventListener('load', () => note('load'));
        for (const ev of ['loadstart', 'loadeddata', 'playing', 'error'])
          document.addEventListener(
            ev,
            e => {
              if (e.target instanceof HTMLMediaElement) note('video-' + ev, { src: e.target.currentSrc });
            },
            true
          );
        document.fonts.ready.then(() => note('initial-font-set-ready'));
      });
      const p = await c.newPage();
      const session = await c.newCDPSession(p);
      await session.send('Network.enable');
      await session.send('Network.setCacheDisabled', { cacheDisabled: true });
      if (process.env.V2_TRACE_THROTTLE === 'devtools') {
        await session.send('Network.emulateNetworkConditions', {
          offline: false,
          latency: 562.5,
          downloadThroughput: (1474.56 * 1024) / 8,
          uploadThroughput: (675 * 1024) / 8,
        });
        await session.send('Emulation.setCPUThrottlingRate', { rate: 4 });
      }
      if (['cart', 'checkout'].includes(name)) {
        await p.goto(base + routes.pdp);
        await p.locator('select[name="attribute_size"]').selectOption('M');
        await p.locator('.woocommerce-variation-add-to-cart-enabled').waitFor();
        await Promise.all([p.waitForNavigation(), p.locator('button.single_add_to_cart_button').click()]);
      }
      const network = new Map();
      session.on('Network.requestWillBeSent', e =>
        network.set(e.requestId, {
          url: e.request.url,
          start: e.timestamp,
          initiator: e.initiator,
          type: e.type,
          priority: e.request.initialPriority,
        })
      );
      session.on('Network.responseReceived', e => {
        const n = network.get(e.requestId);
        if (n)
          Object.assign(n, {
            responseAt: e.timestamp,
            status: e.response.status,
            timing: e.response.timing,
            protocol: e.response.protocol,
            headers: e.response.headers,
          });
      });
      session.on('Network.loadingFinished', e => {
        const n = network.get(e.requestId);
        if (n) Object.assign(n, { end: e.timestamp, bytes: e.encodedDataLength });
      });
      const errors = [];
      p.on('pageerror', e => errors.push(e.message));
      await session.send('Tracing.start', {
        categories: 'devtools.timeline,loading,blink.user_timing,disabled-by-default-devtools.timeline',
        transferMode: 'ReturnAsStream',
      });
      await p.goto(base + routes[name]);
      await p.waitForTimeout(Number(process.env.V2_TRACE_WINDOW_MS || 10000));
      const state = await p.evaluate(() => ({
        ...window.sr2Trace,
        navigation: performance.getEntriesByType('navigation').map(e => e.toJSON()),
        resources: performance.getEntriesByType('resource').map(e => e.toJSON()),
        images: [...document.images]
          .filter(e => e.getBoundingClientRect().top < innerHeight)
          .map(e => ({
            src: e.currentSrc,
            complete: e.complete,
            width: e.naturalWidth,
            loading: e.loading,
            priority: e.fetchPriority,
            decoding: e.decoding,
            sizes: e.sizes,
            rect: e.getBoundingClientRect().toJSON(),
          })),
        preloads: [...document.querySelectorAll('link[rel=preload]')].map(e => e.outerHTML),
      }));
      await p.screenshot({ path: path.join(out, label + '-' + name + '.png') });
      const done = new Promise(resolve => session.once('Tracing.tracingComplete', resolve));
      await session.send('Tracing.end');
      const { stream } = await done;
      const chunks = [];
      for (;;) {
        const d = await session.send('IO.read', { handle: stream });
        chunks.push(d.data);
        if (d.eof) break;
      }
      await session.send('IO.close', { handle: stream });
      fs.writeFileSync(path.join(out, label + '-' + name + '.trace.json'), chunks.join(''));
      const row = {
        name,
        base,
        profile: process.env.V2_TRACE_THROTTLE || 'unthrottled',
        state,
        network: [...network.values()],
        errors,
      };
      rows.push(row);
      fs.writeFileSync(path.join(out, label + '-observations.json'), JSON.stringify(rows, null, 2));
      console.log(
        name,
        state.lcp.map(e => ({ at: e.start, tag: e.tag, url: e.url }))
      );
      await c.close();
    }
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
