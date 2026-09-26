/** Deterministic house guide. No external chat request, HTML answers, or commerce writes. */
(function () {
  'use strict';
  if (window.skyyRoseConcierge) return;
  var dialog = document.getElementById('skyy-ask-dialog');
  var invite = document.getElementById('skyyrose-mascot-recall');
  var stage = document.getElementById('skyyrose-mascot');
  var log = document.getElementById('skyy-conversation');
  var form = document.getElementById('skyy-ask-form');
  var input = document.getElementById('skyy-ask-input');
  var pause = document.getElementById('skyy-motion-toggle');
  var hero = document.getElementById('skyy-hero-stage');
  var dialogStage = document.getElementById('skyy-dialog-stage');
  var heroChat = document.getElementById('skyy-hero-chat');
  var heroDismiss = document.getElementById('skyy-hero-dismiss');
  if (!dialog || !invite || !stage || !log || !form || !input) return;
  var data = window.SKYY_GUIDE_DATA || {};
  var intents = Array.isArray(data.intents) ? data.intents : [];
  var products = Array.isArray(data.products) ? data.products : [];
  var guideAvailable = Array.isArray(data.products) && Array.isArray(data.intents);
  var minimized = false;
  stage.dataset.chat = 'closed';
  var timer;
  var closeTimer;
  var returnFocus;
  var paused = false;
  var homeReady = false;
  var homeVisible = false;
  var SESSION_DISMISSED = 'skyy:dismissed';
  function readSession(key) {
    try {
      return window.sessionStorage.getItem(key);
    } catch (_) {
      return null;
    }
  }
  function writeSession(key, value) {
    try {
      if (value === null) window.sessionStorage.removeItem(key);
      else window.sessionStorage.setItem(key, value);
    } catch (_) {
      /* Private mode only loses the memory, never the guide. */
    }
  }
  // Dismissed = gone for the session (rulebook); the recall pill is her only way back.
  var homeDismissed = readSession(SESSION_DISMISSED) === '1';
  // Rested = she has greeted and nobody engaged; the pill holds her place so page content is never shielded.
  var homeRested = false;
  var restTimer;
  var restAfter = hero ? parseInt(hero.dataset.restAfter || '0', 10) || 0 : 0;
  var homeEntered = false;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  function lightweight() {
    return reduced.matches || !!(navigator.connection && navigator.connection.saveData);
  }
  var presence = document.getElementById('skyy-presence-status');
  var portrait = stage.querySelector('.skyyrose-mascot__image');
  if (portrait)
    portrait.addEventListener('error', function () {
      var fallback = safeUrl(portrait.dataset.fallbackSrc);
      if (fallback && portrait.src !== fallback) {
        portrait.src = fallback;
        stage.dataset.posterFallback = 'true';
      }
    });
  var renderFailed = false;
  var presenceFrame = null;
  function cancelPresenceFrame() {
    if (presenceFrame !== null && window.cancelAnimationFrame) window.cancelAnimationFrame(presenceFrame);
    presenceFrame = null;
    if (stage.dataset.presence === 'entering') setPresence('static');
  }
  function setPresence(state) {
    if (stage.dataset.presence === state) return;
    stage.dataset.presence = state;
    if (presence) {
      var key = state === 'entering' ? 'loading' : state;
      presence.textContent = presence.dataset[key] || presence.dataset.static || '';
    }
  }
  function staticPresence() {
    cancelPresenceFrame();
    if (lightweight()) setPresence(navigator.connection?.saveData ? 'saving' : 'reduced');
    else setPresence(renderFailed ? 'failed' : 'static');
  }
  function revealPresence() {
    if (lightweight()) return staticPresence();
    renderFailed = false;
    // The renderer selects its fallback before this documented event. Keep
    // that SAME portrait in the layer stack; opacity now owns the handoff.
    if (portrait) portrait.style.display = 'block';
    if (stage.dataset.presence === 'live' || stage.dataset.presence === 'entering') return;
    setPresence('entering');
    var reveal = function () {
      presenceFrame = null;
      if (lightweight() || renderFailed || document.hidden || stage.hidden) return staticPresence();
      setPresence('live');
    };
    if (window.requestAnimationFrame)
      presenceFrame = window.requestAnimationFrame(function () {
        presenceFrame = window.requestAnimationFrame(reveal);
      });
    else reveal();
  }
  document.addEventListener('skyy:3d-visible', revealPresence);
  document.addEventListener('skyy:3d-loading', function () {
    if (!renderFailed && !lightweight()) setPresence('loading');
  });
  document.addEventListener('skyy:3d-fallback', function () {
    renderFailed = !lightweight();
    staticPresence();
  });
  reduced.addEventListener('change', staticPresence);
  navigator.connection?.addEventListener?.('change', staticPresence);
  staticPresence();

  function overlayOpen() {
    var classes = document.body && document.body.classList;
    return !!(
      document.querySelector('dialog[open]') ||
      (classes && (classes.contains('sr2-nav-open') || classes.contains('sr2-overlay-open')))
    );
  }
  function syncHome() {
    if (!hero || dialog.open || stage.parentElement !== hero) return;
    var otherOverlay = overlayOpen();
    var visible = homeVisible && !homeDismissed && !homeRested && !document.hidden && !otherOverlay;
    stage.dataset.visibility = document.hidden
      ? 'document-hidden'
      : homeDismissed
        ? 'dismissed'
        : homeRested
          ? 'rested'
        : !homeVisible
          ? 'offscreen'
          : otherOverlay
            ? 'covered'
            : 'visible';
    stage.hidden = homeDismissed || homeRested;
    // The recall pill is shown only while she is dismissed or rested.
    invite.hidden = !(homeDismissed || homeRested);
    stage.dataset.motionPaused = String(paused || lightweight());
    if (!visible) {
      clearTimeout(timer);
      emit('hidden');
      return;
    }
    if (!homeReady || lightweight() || renderFailed) {
      emit('show');
      return;
    }
    if (!window.skyyRoseMascot3D?.isReady()) {
      emit('loading');
      document.dispatchEvent(new CustomEvent('skyy:prepare'));
      return;
    }
    if (!homeEntered) {
      homeEntered = true;
      emit('walking-in');
      settle(1600);
    } else {
      emit('show');
    }
  }
  function restoreHome() {
    if (!hero) return;
    // Re-inserting a node blurs any focused descendant; only move her when she is elsewhere.
    if (stage.parentElement !== hero) hero.appendChild(stage);
    stage.dataset.location = 'hero';
    syncHome();
  }
  function focusHome() {
    // Her dock opener is the natural return; the recall pill only while dismissed.
    if (hero && stage.parentElement === hero && !stage.hidden && heroChat && heroChat.getClientRects().length)
      heroChat.focus({ preventScroll: true });
    else if (!invite.hidden) invite.focus({ preventScroll: true });
  }
  function restHome() {
    if (!hero || dialog.open || homeDismissed || stage.parentElement !== hero) return;
    if (hero.matches(':hover') || hero.contains(document.activeElement)) return scheduleRest();
    homeRested = true;
    syncHome();
  }
  function scheduleRest() {
    clearTimeout(restTimer);
    if (restAfter > 0 && hero && !homeRested && !homeDismissed) restTimer = setTimeout(restHome, restAfter);
  }
  function recall() {
    // A recall clears the session dismissal and any rest; she stays in the dock after the chat.
    homeDismissed = false;
    homeRested = false;
    clearTimeout(restTimer);
    writeSession(SESSION_DISMISSED, null);
    if (hero) {
      // Restore her dock first (this hides the pill) and hand focus to its Ask
      // Skyy button: the shell's overlay lifecycle records document.activeElement
      // as the dialog opener, so both lifecycles return focus to the same visible
      // control instead of a hidden pill or the header menu.
      syncHome();
      if (heroChat && heroChat.getClientRects().length) heroChat.focus({ preventScroll: true });
    }
    open();
  }
  function normalize(value) {
    return String(value || '')
      .toLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, ' ')
      .trim();
  }
  function includes(query, phrase) {
    return phrase && (' ' + query + ' ').includes(' ' + normalize(phrase) + ' ');
  }
  function safeUrl(value) {
    if (typeof value !== 'string' || !value.trim()) return '';
    try {
      var url = new URL(value, location.href);
      return url.origin === location.origin && /^https?:$/.test(url.protocol) ? url.href : '';
    } catch (_) {
      return '';
    }
  }
  function emit(state) {
    stage.dataset.state = state;
    if (state === 'hidden') cancelPresenceFrame();
    if (!dialog.open && (state === 'idle' || (state === 'show' && (lightweight() || renderFailed)))) scheduleRest();
    if (
      (state === 'loading' || state === 'walking-in') &&
      !window.skyyRoseMascot3D?.isReady() &&
      !renderFailed &&
      !lightweight()
    )
      setPresence('loading');
    document.dispatchEvent(new CustomEvent('skyy:' + state));
  }
  function settle(delay) {
    clearTimeout(timer);
    timer = setTimeout(function () {
      var action = window.skyyRoseMascot3D?.getCurrentAction?.();
      if (action && action.toLowerCase() !== 'skyy_idle' && !lightweight()) return;
      if (dialog.open || (hero && stage.parentElement === hero && homeVisible && !homeDismissed)) emit('idle');
    }, delay);
  }
  document.addEventListener('skyy:action-complete', function () {
    if (dialog.open || (hero && stage.parentElement === hero && homeVisible && !homeDismissed)) emit('idle');
  });
  function add(text, speaker, links) {
    var firstMessage = log.children.length === 0;
    var entry = document.createElement('div');
    entry.className = 'skyy-message skyy-message--' + speaker;
    var label = document.createElement('strong');
    label.textContent = speaker === 'visitor' ? 'You' : 'Skyy';
    var paragraph = document.createElement('p');
    paragraph.textContent = text;
    entry.append(label, paragraph);
    (links || []).forEach(function (item) {
      var href = safeUrl(item.url || item.link);
      if (!href) return;
      var anchor = document.createElement('a');
      anchor.href = href;
      anchor.textContent = item.label || item.name || 'Explore';
      entry.appendChild(anchor);
    });
    log.appendChild(entry);
    while (log.children.length > 20) log.firstElementChild.remove();
    log.scrollTop = firstMessage ? 0 : log.scrollHeight;
  }
  function answer(question) {
    var query = normalize(question);
    if (!query) return;
    stage.dataset.conversation = 'thinking';
    document.dispatchEvent(new CustomEvent('skyy:thinking'));
    add(question, 'visitor');
    if (!guideAvailable) {
      stage.dataset.conversation = 'chat-failure';
      add('The house guide is unavailable right now. You can still browse the shop or contact the house.', 'skyy', [
        { url: invite.href, label: 'Contact the house' },
      ]);
      emit('idle');
      return;
    }
    var exact = products.filter(function (p) {
      return includes(query, p.sku) || includes(query, p.name);
    });
    var found = exact.length
      ? exact
      : products.filter(function (p) {
          var title = normalize(p.name + ' ' + (p.collection || ''));
          var words = query.split(' ').filter(function (word) {
            return (
              word.length > 2 &&
              !['the', 'show', 'find', 'for', 'with', 'have', 'want', 'some', 'please', 'products', 'product'].includes(
                word
              )
            );
          });
          return (
            words.length > 0 &&
            words.every(function (word) {
              return includes(title, word);
            })
          );
        });
    var match = intents
      .map(function (intent) {
        var patterns = Array.isArray(intent.patterns) ? intent.patterns : [];
        return {
          intent: intent,
          score: patterns.reduce(function (score, pattern) {
            return includes(query, pattern) ? Math.max(score, normalize(pattern).length) : score;
          }, 0),
        };
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })[0];
    if (found.length) {
      add(
        'Here are matching pieces from our catalog. Open a product for its current price, available options, and purchase details.',
        'skyy',
        found.slice(0, 4).map(function (p) {
          return { url: p.url, label: p.name + (p.sku ? ' · ' + p.sku : '') };
        })
      );
    } else if (match && match.score) {
      var intent = match.intent;
      add(String(intent.answer || ''), 'skyy', intent.link ? [{ url: intent.link, label: intent.label }] : []);
    } else {
      add(
        'I can help you find a piece by name or SKU, explore a collection, or point you to our site information. For a question about an order, please contact the house.',
        'skyy',
        Object.values(data.pages || {})
          .filter(function (p) {
            return p && /contact|shop/i.test(p.label || '');
          })
          .slice(0, 2)
      );
    }
    stage.dataset.conversation = found.length
      ? 'gesture'
      : /^(hi|hello|hey)( skyy)?$/.test(query)
        ? 'greeting'
        : 'talking';
    emit(found.length ? 'joy' : /^(hi|hello|hey)( skyy)?$/.test(query) ? 'wave' : 'speaking');
    settle(2400);
  }
  function open() {
    if (dialog.open || typeof dialog.showModal !== 'function') return;
    if (overlayOpen()) return;
    returnFocus = document.activeElement;
    stage.hidden = false;
    // Open before reparenting: the shell's overlay lifecycle records the
    // active element at beforetoggle as the opener, and her Ask Skyy button
    // must still be rendered in the dock at that instant.
    dialog.showModal();
    if (dialogStage) dialogStage.appendChild(stage);
    stage.dataset.location = 'dialog';
    minimized = false;
    stage.dataset.chat = 'open';
    stage.dataset.visibility = 'visible';
    stage.dataset.conversation = 'greeting';
    invite.setAttribute('aria-expanded', 'true');
    if (!log.children.length)
      add(
        data.greeting || "I'm Skyy, your guide to the house. Which piece or collection would you like to explore?",
        'skyy'
      );
    emit('walking-in');
    settle(1600);
    input.focus({ preventScroll: true });
  }
  input.addEventListener('input', function () {
    if (dialog.open) {
      stage.dataset.conversation = 'listening';
      document.dispatchEvent(new CustomEvent('skyy:listening'));
    }
  });
  document.getElementById('skyy-ask-minimize')?.addEventListener('click', function () {
    minimized = true;
    close();
  });
  invite.addEventListener('click', function (event) {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.altKey ||
      event.shiftKey ||
      typeof dialog.showModal !== 'function'
    )
      return;
    event.preventDefault();
    recall();
  });
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var question = input.value.trim().slice(0, 300);
    if (!question) {
      input.focus();
      return;
    }
    input.value = '';
    answer(question);
    input.focus({ preventScroll: true });
  });
  function close() {
    if (closeTimer || !dialog.open) return;
    clearTimeout(timer);
    emit('exit');
    // Move her stage back into the dock now: some engines do not fire the dialog's
    // `beforetoggle` event, and the 'close' handler below needs her opener (Ask
    // Skyy) already in the dock to hand focus back to it instead of stranding it.
    if (hero && stage.parentElement === dialogStage) {
      hero.appendChild(stage);
      stage.dataset.location = 'hero';
    }
    var animate =
      stage.dataset.renderer === '3d' && !paused && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!animate) {
      dialog.close();
      return;
    }
    closeTimer = setTimeout(function () {
      closeTimer = null;
      dialog.close();
    }, 450);
  }
  document.getElementById('skyy-ask-cancel').addEventListener('click', close);
  // The shell's overlay lifecycle returns focus to its recorded opener the
  // instant the dialog closes. Move her stage back to the dock first so that
  // opener (her Ask Skyy button) is rendered when that happens; the close
  // handler below still owns the final focus decision where beforetoggle is
  // unsupported.
  dialog.addEventListener('beforetoggle', function (event) {
    if (event.newState !== 'closed' || !hero || stage.parentElement !== dialogStage) return;
    hero.appendChild(stage);
    stage.dataset.location = 'hero';
  });
  dialog.addEventListener('close', function () {
    clearTimeout(timer);
    clearTimeout(closeTimer);
    closeTimer = null;
    emit('hidden');
    stage.dataset.chat = minimized ? 'minimized' : 'closed';
    invite.setAttribute('aria-expanded', 'false');
    var active = document.activeElement;
    // Native dialog normally restores its opener itself. Restore only when
    // focus is still stranded in the closing dialog/body, never over a new task.
    var needsFocus = active === document.body || active === dialog || dialog.contains(active);
    // A hero opener belongs to this moving stage. Reparent it out of the
    // closed dialog before focusing; hidden dialog descendants cannot focus.
    restoreHome();
    if (needsFocus) {
      if (
        returnFocus &&
        returnFocus !== document.body &&
        returnFocus !== dialog &&
        returnFocus.isConnected &&
        returnFocus.getClientRects().length &&
        !(hero?.contains(returnFocus) && (!homeVisible || homeDismissed))
      )
        returnFocus.focus({ preventScroll: true });
      else focusHome();
    }
  });
  var chips = document.getElementById('skyy-chips');
  var suggestions = Array.isArray(data.suggestions)
    ? intents.filter(function (i) {
        return data.suggestions.includes(i.id);
      })
    : intents;
  suggestions.slice(0, 4).forEach(function (intent) {
    var pattern = (intent.patterns || [])[0];
    if (!pattern) return;
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'skyy-chip';
    button.textContent = intent.label || pattern;
    button.addEventListener('click', function () {
      answer(pattern);
    });
    chips.appendChild(button);
  });
  if (pause) {
    document.addEventListener('skyy:3d-ready', function () {
      pause.hidden = false;
    });
    document.addEventListener('skyy:3d-visible', function () {
      pause.hidden = false;
    });
    document.addEventListener('skyy:3d-fallback', function () {
      pause.hidden = true;
    });
    pause.addEventListener('click', function () {
      paused = !paused;
      pause.setAttribute('aria-pressed', String(paused));
      pause.textContent = paused ? 'Resume character' : 'Pause character';
      document.dispatchEvent(new CustomEvent('skyy:motion', { detail: { paused: paused } }));
      stage.dataset.motionPaused = String(paused || lightweight());
      stage.dataset.motion = paused ? 'paused' : 'active';
    });
  }
  document.addEventListener('visibilitychange', function () {
    stage.dataset.visibility = document.hidden ? 'document-hidden' : dialog.open ? 'visible' : stage.dataset.visibility;
  });
  window.addEventListener('pagehide', function () {
    clearTimeout(timer);
    clearTimeout(closeTimer);
    closeTimer = null;
    cancelPresenceFrame();
    emit('hidden');
  });
  window.addEventListener('pageshow', function (event) {
    if (event.persisted && dialog.open) {
      emit('walking-in');
      settle(1600);
    } else if (event.persisted) syncHome();
  });
  if (hero && dialogStage) {
    var rect = hero.getBoundingClientRect();
    homeVisible = rect.bottom > 0 && rect.top < window.innerHeight;
    restoreHome();
    heroChat?.addEventListener('click', open);
    hero.addEventListener('pointerenter', function () { clearTimeout(restTimer); });
    hero.addEventListener('pointerleave', scheduleRest);
    hero.addEventListener('focusin', function () { clearTimeout(restTimer); });
    hero.addEventListener('focusout', scheduleRest);
    heroDismiss?.addEventListener('click', function () {
      // Dismissed = gone for the session; the recall pill takes her place and the focus.
      homeDismissed = true;
      writeSession(SESSION_DISMISSED, '1');
      syncHome();
      invite.focus({ preventScroll: true });
    });
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          homeVisible = entries[0].isIntersecting;
          syncHome();
        },
        { threshold: 0.05 }
      );
      observer.observe(hero);
    }
    document.addEventListener('skyy:3d-ready', syncHome);
    document.addEventListener('visibilitychange', syncHome);
    reduced.addEventListener('change', syncHome);
    navigator.connection?.addEventListener?.('change', syncHome);
    if ('MutationObserver' in window) {
      var overlays = new MutationObserver(syncHome);
      overlays.observe(document.body, { attributes: true, attributeFilter: ['class'] });
      document.querySelectorAll('dialog').forEach(function (el) {
        overlays.observe(el, { attributes: true, attributeFilter: ['open'] });
      });
    }
  }
  window.skyyRoseConcierge = Object.freeze({
    open: open,
    prepareHome: function () {
      homeReady = true;
      syncHome();
    },
  });
})();
