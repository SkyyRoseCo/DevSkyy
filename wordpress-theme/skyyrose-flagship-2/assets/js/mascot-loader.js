/** Native invitation; dock walk-on timing and invitation-owned guide loading. */
(function () {
  'use strict';
  var config = window.SKYY_LOADER_CONFIG || {};
  var invite = document.getElementById('skyyrose-mascot-recall');
  if (!invite || !config.mascotUrl) return;
  var pending;
  var threePending;
  var home = document.getElementById('skyy-hero-stage');
  // Rulebook: the host greets arrivals ~4.5 s after load; never a pop-in, and
  // never more than three unprompted walk-ons in one session.
  var WALK_IN_DELAY_MS = 4500;
  var AUTO_ENTRY_CAP = 3;
  var SESSION_DISMISSED = 'skyy:dismissed';
  var SESSION_ENTRIES = 'skyy:entries';
  function readSession(key) {
    try {
      return window.sessionStorage.getItem(key);
    } catch (_) {
      return null;
    }
  }
  function writeSession(key, value) {
    try {
      window.sessionStorage.setItem(key, value);
    } catch (_) {
      /* Private mode or a full quota only loses the count, never the guide. */
    }
  }
  function loadGuide() {
    if (!pending) pending = script(config.mascotUrl);
    return pending;
  }
  function localUrl(value) {
    try {
      var url = new URL(value, location.href);
      return url.origin === location.origin && /^https?:$/.test(url.protocol) ? url.href : '';
    } catch (_) {
      return '';
    }
  }
  function script(value) {
    return new Promise(function (resolve, reject) {
      var src = localUrl(value);
      if (!src) {
        reject(new Error('Skyy script must be local'));
        return;
      }
      var el = document.createElement('script');
      var timer = setTimeout(function () {
        finish(new Error('Skyy script timed out'));
      }, 15000);
      function finish(error) {
        clearTimeout(timer);
        el.onload = el.onerror = null;
        if (error) {
          el.remove();
          reject(error);
        } else resolve();
      }
      el.async = true;
      el.src = src;
      el.onload = function () {
        finish();
      };
      el.onerror = function () {
        finish(new Error('Skyy script unavailable'));
      };
      document.head.appendChild(el);
    });
  }
  function lightweight() {
    return (
      !!(navigator.connection && navigator.connection.saveData) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    );
  }
  function overlayOpen() {
    var classes = document.body && document.body.classList;
    return !!(
      document.querySelector('dialog[open]') ||
      (classes && (classes.contains('sr2-nav-open') || classes.contains('sr2-overlay-open')))
    );
  }
  function loadThree() {
    if (threePending || !config.skyy3dUrl || lightweight()) return;
    window.SKYY_3D_CONFIG = window.SKYY_3D_CONFIG || {};
    window.SKYY_3D_CONFIG.startVisible = true;
    document.dispatchEvent(new CustomEvent('skyy:3d-loading'));
    threePending = script(config.skyy3dUrl).catch(function () {
      window.SKYY_3D_CONFIG.loadFailed = true;
      document.dispatchEvent(new CustomEvent('skyy:3d-fallback'));
    });
  }
  document.addEventListener('skyy:walking-in', loadThree);
  document.addEventListener('skyy:prepare', loadThree);
  var converted = false;
  function convertToContact() {
    // A real contact link remains the fallback; a second activation follows it.
    if (converted) return;
    converted = true;
    config.mascotUrl = '';
    var labels = document.getElementById('skyy-presence-status')?.dataset || {};
    if (labels.guideFailed) invite.title = labels.guideFailed;
    invite.removeAttribute('aria-haspopup');
    invite.removeAttribute('aria-controls');
    invite.removeAttribute('aria-expanded');
    var label = invite.querySelector?.('span');
    if (label && labels.contact) label.textContent = labels.contact;
    var fallback = invite.cloneNode(true);
    // The dock keeps its recall hidden until a dismissal; a plain contact link
    // must be reachable, so the converted pill is always shown.
    fallback.hidden = false;
    fallback.removeAttribute('hidden');
    var ownedFocus = document.activeElement === invite;
    invite.replaceWith(fallback);
    if (ownedFocus) fallback.focus({ preventScroll: true });
  }
  if (home) {
    // Mount the lightweight canonical portrait promptly. The heavy renderer
    // waits for the actual hero image, page load and character intent.
    loadGuide().catch(convertToContact);
    var heroImage = home.closest('[data-recovery-hero]')?.querySelector('picture img, img');
    var poster = heroImage?.decode ? heroImage.decode().catch(function () {}) : Promise.resolve();
    var loaded =
      document.readyState === 'complete'
        ? Promise.resolve()
        : new Promise(function (resolve) {
            window.addEventListener('load', resolve, { once: true });
          });
    var heroIntent = false;
    var heroReady = false;
    var heroPrepared = false;
    function prepareInvitedHero() {
      if (!heroIntent || !heroReady || heroPrepared) return;
      heroPrepared = true;
      window.skyyRoseConcierge?.prepareHome();
    }
    function intendHero() {
      heroIntent = true;
      prepareInvitedHero();
    }
    function networkAllowsAutoWalk() {
      // The 3D chain is 2.4–3.3 MB; only an unprompted entry is gated, never a visitor's intent.
      var connection = navigator.connection;
      if (connection && (connection.saveData || (connection.effectiveType && connection.effectiveType !== '4g'))) return false;
      return !(navigator.deviceMemory && navigator.deviceMemory < 4);
    }
    function autoWalkAllowed() {
      if (lightweight() || overlayOpen() || readSession(SESSION_DISMISSED) === '1' || !networkAllowsAutoWalk()) return false;
      return (parseInt(readSession(SESSION_ENTRIES) || '0', 10) || 0) < AUTO_ENTRY_CAP;
    }
    function autoWalk() {
      // Pointer or keyboard intent may already have brought her in.
      if (heroPrepared) return;
      if (document.hidden) {
        // A background tab greets on its return instead of walking unseen.
        document.addEventListener(
          'visibilitychange',
          function () {
            if (!document.hidden) autoWalk();
          },
          { once: true }
        );
        return;
      }
      if (!autoWalkAllowed()) return;
      writeSession(SESSION_ENTRIES, String((parseInt(readSession(SESSION_ENTRIES) || '0', 10) || 0) + 1));
      intendHero();
    }
    // Pointer/keyboard intent still brings her in early; otherwise the host
    // greets shortly after load unless motion, data or the visitor says no.
    var character = document.getElementById('skyyrose-mascot-trigger');
    character?.addEventListener('pointerenter', intendHero, { once: true });
    character?.addEventListener('pointerdown', intendHero, { once: true });
    home.addEventListener('focusin', function (event) {
      if (event.target?.id === 'skyy-hero-chat') intendHero();
    });
    loaded.then(function () {
      setTimeout(function () {
        // Yield to the page's own work first; the greeting is never worth a long task.
        if (window.requestIdleCallback) window.requestIdleCallback(autoWalk, { timeout: 2000 });
        else autoWalk();
      }, WALK_IN_DELAY_MS);
    });
    Promise.all([loadGuide(), poster, loaded])
      .then(function () {
        heroReady = true;
        prepareInvitedHero();
      })
      .catch(function () {});
  }
  invite.addEventListener('click', function (event) {
    var dialog = document.getElementById('skyy-ask-dialog');
    if (!dialog || typeof dialog.showModal !== 'function') return;
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.altKey ||
      event.shiftKey
    )
      return;
    if (window.skyyRoseConcierge) return;
    event.preventDefault();
    var invitedFrom = document.activeElement;
    invite.setAttribute('aria-busy', 'true');
    loadGuide()
      .then(function () {
        invite.removeAttribute('aria-busy');
        if (window.skyyRoseConcierge) {
          if (!document.hidden && (document.activeElement === invitedFrom || document.activeElement === invite))
            window.skyyRoseConcierge.open();
        } else throw new Error('Skyy guide unavailable');
      })
      .catch(function () {
        invite.removeAttribute('aria-busy');
        convertToContact();
      });
  });
})();
