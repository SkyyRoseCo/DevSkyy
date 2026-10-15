/**
 * Consent-gated engagement events. Identifiers and the in-memory queue exist
 * only while explicit, readable consent is accepted. WordPress signs the relay;
 * the public page token is never the backend analytics secret.
 */
(function () {
  'use strict';

  var CONSENT_KEY = 'skyyrose_cookie_consent';
  var SESSION_KEY = 'skyy_analytics_session';
  var SESSION_IDLE_MS = 30 * 60 * 1000;
  var DELIVERY_TIMEOUT_MS = 15000;
  var CARD_SELECTOR = '.sr2-c-editorial-card[data-sku]';
  var queue = [];
  var sessionId = '';
  var running = false;
  var interval = null;
  var observer = null;
  var pending = null;
  var generation = 0;
  var MAX_QUEUE = 500;

  function accepted() {
    try {
      return (
        localStorage.getItem(CONSENT_KEY) === 'accepted' &&
        /(?:^|;\s*)skyyrose_cookie_consent=accepted(?:;|$)/.test(document.cookie)
      );
    } catch (e) {
      return false;
    }
  }

  function clearIdentifiers() {
    ['skyy_vh', 'skyy_analytics_session'].forEach(function (key) {
      try {
        localStorage.removeItem(key);
      } catch (e) {
        /* Storage may be blocked. */
      }
    });
    document.cookie = 'skyy_visitor=; Max-Age=0; Path=/; SameSite=Lax';
  }

  function uuid() {
    if (!window.crypto || !window.crypto.getRandomValues) return '';
    var bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    var hex = Array.from(bytes, function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
    return (
      hex.slice(0, 8) + '-' + hex.slice(8, 12) + '-' + hex.slice(12, 16) + '-' + hex.slice(16, 20) + '-' + hex.slice(20)
    );
  }

  function getSession() {
    try {
      var stored = localStorage.getItem(SESSION_KEY);
      var now = Date.now();
      var session = stored === null ? null : JSON.parse(stored);
      // Corrupt or future-dated state cannot establish an accepted session.
      if (
        stored !== null &&
        (!session ||
          typeof session.id !== 'string' ||
          !/^[a-f0-9]{32}$/.test(session.id) ||
          !Number.isSafeInteger(session.last_activity) ||
          session.last_activity <= 0 ||
          session.last_activity > now)
      )
        return '';
      var id = session && now - session.last_activity < SESSION_IDLE_MS ? session.id : uuid().replace(/-/g, '');
      if (!id) return '';
      var updated = JSON.stringify({ id: id, last_activity: now });
      localStorage.setItem(SESSION_KEY, updated);
      return localStorage.getItem(SESSION_KEY) === updated ? id : '';
    } catch (e) {
      return '';
    }
  }

  function pageType() {
    var path = window.location.pathname;
    if (path === '/') return 'home';
    if (/\/(?:checkout)(?:\/|$)/.test(path)) return 'checkout';
    if (/\/(?:cart)(?:\/|$)/.test(path)) return 'cart';
    if (/\/(?:product)(?:\/|$)/.test(path)) return 'product';
    if (/\/(?:immersive)(?:[-/]|$)/.test(path)) return 'immersive';
    if (/\/(?:collection|collections)(?:[-/]|$)/.test(path)) return 'collection';
    if (/\/(?:lookbook)(?:[-/]|$)/.test(path)) return 'lookbook';
    if (/\/(?:shop)(?:\/|$)/.test(path)) return 'shop';
    return 'other';
  }

  function token(value) {
    return typeof value === 'string' && /^[A-Za-z0-9_/.-]{1,160}$/.test(value) ? value : '';
  }

  function cardData(el) {
    if (!el || typeof el.closest !== 'function') return null;
    var card = el.closest(CARD_SELECTOR);
    if (!card) return null;
    var sku = token(card.dataset.sku || '');
    if (!sku) return null;
    return {
      target: sku,
      collection: token(card.dataset.collection || ''),
    };
  }

  function deliveryStatus(status) {
    document.dispatchEvent(new CustomEvent('skyyrose:analytics-delivery', { detail: { status: status } }));
  }

  function push(type, data, properties) {
    if (!running || !accepted()) {
      stop();
      return;
    }
    if (queue.length >= MAX_QUEUE) {
      deliveryStatus('queue_full');
      return;
    }
    // Read the shared session for every accepted event, including after idle.
    sessionId = getSession();
    if (!sessionId) {
      stop();
      return;
    }
    var id = uuid();
    if (!id) {
      stop();
      return;
    }
    var event = {
      event_id: id,
      session_id: sessionId,
      event_type: type,
      occurred_at: new Date().toISOString(),
      page_type: pageType(),
      synthetic: false,
    };
    if (data && data.target) event.target = data.target;
    if (data && data.collection && data.collection.length <= 100) event.collection = data.collection;
    if (properties) event.properties = properties;
    queue.push(event);
  }

  function flush() {
    if (!running || !accepted()) {
      stop();
      return;
    }
    if (pending || !queue.length) return;
    if (typeof fetch !== 'function') {
      deliveryStatus('unavailable');
      return;
    }
    var batch = queue.slice(0, 50);
    var ids = batch.map(function (event) {
      return event.event_id;
    });
    var epoch = generation;
    var controller = typeof AbortController === 'function' ? new AbortController() : null;
    var attempt = { controller: controller, timer: null };
    pending = attempt;
    attempt.timer = setTimeout(function () {
      if (epoch !== generation || pending !== attempt) return;
      if (controller) controller.abort();
      releaseAttempt(attempt);
      if (running && accepted()) deliveryStatus('unavailable');
      else stop();
    }, DELIVERY_TIMEOUT_MS);
    var key = window.skyyroseSEE && window.skyyroseSEE.key ? window.skyyroseSEE.key : '';
    var request;
    try {
      var configured = window.skyyroseSEE && window.skyyroseSEE.endpoint;
      if (!configured) throw new Error('analytics_endpoint_missing');
      var endpoint = new URL(configured, window.location.href);
      if (endpoint.origin !== window.location.origin) throw new Error('analytics_endpoint_origin');
      endpoint.searchParams.set('k', key);
      request = fetch(endpoint.href, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schema_version: 1, consent: 'accepted', events: batch }),
        credentials: 'same-origin',
        keepalive: true,
        signal: controller ? controller.signal : undefined,
      });
    } catch (e) {
      request = Promise.reject(e);
    }
    Promise.resolve(request)
      .then(function (response) {
        if (epoch !== generation || pending !== attempt || !running || !accepted()) return null;
        if (!response.ok) throw new Error('analytics_unavailable');
        return response.json();
      })
      .then(function (ack) {
        if (epoch !== generation || pending !== attempt || !running || !accepted()) return;
        if (
          ack.status !== 'accepted' ||
          !Array.isArray(ack.event_ids) ||
          ack.event_ids.length !== ids.length ||
          !Number.isInteger(ack.accepted) ||
          !Number.isInteger(ack.duplicates) ||
          ack.accepted < 0 ||
          ack.duplicates < 0 ||
          ack.accepted + ack.duplicates !== ids.length ||
          !ids.every(function (id, index) {
            return ack.event_ids[index] === id;
          })
        ) {
          throw new Error('analytics_invalid_ack');
        }
        queue = queue.filter(function (event) {
          return ids.indexOf(event.event_id) === -1;
        });
        deliveryStatus('accepted');
      })
      .catch(function () {
        if (epoch === generation && pending === attempt && running && accepted()) deliveryStatus('unavailable');
      })
      .finally(function () {
        releaseAttempt(attempt);
      });
  }

  function releaseAttempt(attempt) {
    if (attempt.timer !== null) clearTimeout(attempt.timer);
    attempt.timer = null;
    if (pending === attempt) pending = null;
  }

  function clicked(e) {
    var target = e.target;
    if (!target || typeof target.closest !== 'function') return;
    var action = target.closest(
      '.sr2-c-editorial-card__actions .button, .sr2-c-editorial-card__media, .sr2-c-editorial-card__title a'
    )
      ? 'buy'
      : target.closest('[data-analytics-wishlist]')
        ? 'wishlist'
        : target.closest('[data-quick-view]')
          ? 'quickview'
          : '';
    var data = action ? cardData(target) : null;
    // A CTA click is engagement; only a confirmed commerce hook may emit cart events.
    if (data) push('product_click', data, { action: action });
  }

  function start(event) {
    if (event && event.detail && event.detail.consent !== 'accepted') {
      stop();
      return;
    }
    if (!accepted()) {
      stop();
      return;
    }
    if (running) return;
    sessionId = getSession();
    if (!sessionId) {
      stop();
      return;
    }
    running = true;
    generation += 1;
    document.addEventListener('click', clicked);
    if ('IntersectionObserver' in window) {
      var viewed = new WeakSet();
      var epoch = generation;
      observer = new IntersectionObserver(
        function (entries) {
          if (epoch !== generation) return;
          entries.forEach(function (entry) {
            if (!entry.isIntersecting || viewed.has(entry.target)) return;
            var data = cardData(entry.target);
            if (data) {
              viewed.add(entry.target);
              push('product_view', data);
            }
            if (observer) observer.unobserve(entry.target);
          });
        },
        { threshold: 0.5 }
      );
      document.querySelectorAll(CARD_SELECTOR).forEach(function (el) {
        observer.observe(el);
      });
    }
    push('page_view');
    if (running) interval = setInterval(flush, 30000);
  }

  function stop() {
    running = false;
    generation += 1;
    queue = [];
    sessionId = '';
    if (interval) clearInterval(interval);
    interval = null;
    if (observer) observer.disconnect();
    observer = null;
    document.removeEventListener('click', clicked);
    if (pending) {
      var attempt = pending;
      releaseAttempt(attempt);
      if (attempt.controller) attempt.controller.abort();
    }
    clearIdentifiers();
  }

  document.addEventListener('skyyrose:consent-changed', start);
  document.addEventListener('skyyrose:consent-declined', stop);
  window.addEventListener('storage', function (e) {
    if (e.key === CONSENT_KEY || e.key === null) start();
  });
  // fetch keepalive can observe acknowledgements while the document survives.
  // sendBeacon cannot acknowledge durable storage and is deliberately unused.
  window.addEventListener('pagehide', flush);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
