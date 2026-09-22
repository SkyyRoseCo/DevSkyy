/**
 * Viewport-scoped collection films. Heroes have their own unchanged controller.
 */
(() => {
  'use strict';
  const init = () => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const small = window.matchMedia('(max-width: 767px)');
    const hoverPointer = window.matchMedia('(hover: hover) and (pointer: fine)');
    const connection = navigator.connection;
    const states = [];
    let active = null;
    let observer = null;
    let preparationObserver = null;
    let suspended = false;
    const automatic = () => !reduced.matches && !(connection && connection.saveData);
    const visibleRatio = (entry) => {
      const viewport = entry.rootBounds || { width: window.innerWidth, height: window.innerHeight };
      const capacity = Math.min(entry.boundingClientRect.width, viewport.width) *
        Math.min(entry.boundingClientRect.height, viewport.height);
      return entry.isIntersecting && capacity > 0 ?
        Math.min(1, entry.intersectionRect.width * entry.intersectionRect.height / capacity) : 0;
    };
    const preparePoster = (state) => {
      if (state.prepared) return;
      state.prepared = true;
      const poster = state.frame.querySelector('[data-scene-poster]');
      if (poster) {
        if (poster.dataset.srcset) poster.srcset = poster.dataset.srcset;
        poster.src = poster.dataset.src;
      }
      state.scene.dataset.scenePrepared = 'poster';
    };
    const status = (state) => {
      state.scene.dataset.sceneMotionState = state.failed ? 'error' :
        suspended ? 'suspended' : document.hidden ? 'document-hidden' :
        state.shopping ? 'shopping' : !automatic() && !state.optIn ? 'static' : state.paused ? 'paused' :
        state.wanted && state.pending ? 'loading' : state.wanted && !state.video.paused ? 'playing' :
        state.manualRequired ? 'play-required' : state.ratio < 0.15 ? 'offscreen' : 'poster';
      const messages = {
        error: 'Film unavailable. You can retry or shop the still.',
        shopping: 'Hotspots use the still. Play motion returns to the film.',
        static: 'Motion is off for your device preferences. Play motion is optional.',
        paused: 'Film paused. Shopping remains available.',
        loading: 'Loading collection film.',
        playing: 'Film playing. Product hotspots pause the film.',
        'play-required': 'Your browser paused autoplay. Select Play motion.',
        poster: 'Collection film ready.',
        offscreen: 'Film pauses outside the viewing area.'
      };
      const message = messages[state.scene.dataset.sceneMotionState] || 'Film paused.';
      if (state.note.textContent !== message) state.note.textContent = message;
    };
    const buttonText = (state) => {
      status(state);
      if (state.failed) return;
      const playing = !state.video.paused || state.pending;
      state.button.textContent = playing ? 'Pause motion' : 'Play motion';
      state.button.setAttribute('aria-label', (playing ? 'Pause' : 'Play') + ' motion: ' + state.label);
    };
    const stop = (state) => {
      state.wanted = false;
      state.video.pause();
      state.frame.classList.remove('is-motion-ready');
      buttonText(state);
    };
    const fail = (state) => {
      state.failed = true;
      state.pending = false;
      stop(state);
      state.frame.classList.remove('is-motion-ready');
      state.button.textContent = 'Retry motion';
      state.button.setAttribute('aria-label', 'Retry motion: ' + state.label);
      state.button.disabled = false;
    };
    const start = (state) => {
      preparePoster(state);
      state.wanted = true;
      if (state.pending || !state.video.paused) return;
      if (!state.video.getAttribute('src')) {
        const slow = connection && /^(slow-2g|2g|3g)$/.test(connection.effectiveType || '');
        state.video.src = (small.matches || slow || state.frame.clientWidth <= 767) ?
          state.video.dataset.mobileSrc : state.video.dataset.desktopSrc;
        state.video.muted = true;
        state.video.defaultMuted = true;
        state.video.load();
      }
      state.pending = true;
      buttonText(state);
      const attempt = state.video.play();
      Promise.resolve(attempt).then(() => {
        state.pending = false;
        if (!state.wanted || suspended || document.hidden || active !== state) state.video.pause();
        buttonText(state);
      }).catch((error) => {
        state.pending = false;
        if (error && error.name === 'AbortError') {
          buttonText(state);
          if (state.wanted && active === state && !document.hidden && !suspended) start(state);
          return;
        }
        if (error && error.name === 'NotAllowedError') {
          state.manualRequired = true;
          state.wanted = false;
          buttonText(state);
          return;
        }
        fail(state);
      });
    };
    const sync = (preferred) => {
      const candidates = document.hidden || suspended ? [] : states.filter((state) =>
        (state.ratio >= 0.15 || (state === preferred && state.optIn)) &&
        !state.failed && !state.paused && !state.shopping &&
        !state.manualRequired && (automatic() || state.optIn)
      );
      candidates.sort((a, b) => b.ratio - a.ratio);
      const next = candidates.includes(preferred) ? preferred : (candidates[0] || null);
      states.forEach((state) => { if (state !== next && (state.wanted || !state.video.paused)) stop(state); });
      active = next;
      if (next) {
        start(next);
        // Prepare one approved still ahead, never a speculative video request.
        // Previously loaded films remain attached for immediate reverse reuse.
        const upcoming = states[states.indexOf(next) + 1];
        if (automatic() && upcoming && !upcoming.prepared) {
          preparePoster(upcoming);
        }
      }
      states.forEach(status);
    };
    document.querySelectorAll('[data-collection-scene-motion]').forEach((video) => {
      if (video.dataset.motionInitialized) return;
      const frame = video.closest('.sr2-hero-commerce__frame');
      const button = frame && frame.closest('[data-scene-id]')?.querySelector('[data-scene-motion-toggle]');
      if (!button) return;
      video.dataset.motionInitialized = 'true';
      const note = document.createElement('p');
      note.className = 'sr2-scene-motion__status';
      note.id = video.id + '-status';
      button.parentElement.append(note);
      button.setAttribute('aria-describedby', note.id);
      const state = {
        video, frame, button, note, scene: frame.closest('[data-scene-id]'), label: video.dataset.sceneLabel || 'Collection scene',
        ratio: 0, wanted: false, pending: false, paused: false,
        optIn: false, manualRequired: false, failed: false, shopping: false, hoverShopping: false
      };
      states.push(state);
      const hotspotLayer = state.scene.querySelector('[data-scene-hotspots]');
      const shopButton = state.scene.querySelector('[data-scene-shop-toggle]');
      const poster = frame.querySelector('[data-scene-poster]');
      const setShopping = (enabled, returnFocus = false, synchronize = true) => {
        if (!hotspotLayer || !shopButton) return;
        if (enabled && (!poster || !poster.complete || !poster.naturalWidth)) return;
        state.shopping = enabled;
        if (!enabled) state.hoverShopping = false;
        state.scene.dataset.shopMode = enabled ? 'still' : 'film';
        hotspotLayer.hidden = !enabled;
        shopButton.setAttribute('aria-pressed', String(enabled));
        shopButton.textContent = enabled ? 'Return to film' : 'Product hotspots';
        if (enabled) frame.style.setProperty('--scene-tooltip-width', Math.max(80, frame.clientWidth * 0.42) + 'px');
        if (enabled) stop(state);
        if (synchronize) sync();
        if (returnFocus) shopButton.focus();
      };
      if (hotspotLayer && shopButton && poster) {
        const showHoverHotspots = () => {
          if (!hoverPointer.matches || state.shopping || !poster.complete || !poster.naturalWidth) return;
          setShopping(true);
          state.hoverShopping = state.shopping;
        };
        const dismissHoverHotspots = () => {
          if (!state.hoverShopping || frame.matches(':hover') || hotspotLayer.contains(document.activeElement)) return;
          setShopping(false);
        };
        const ready = () => {
          shopButton.hidden = !poster.naturalWidth;
          if (frame.matches(':hover')) showHoverHotspots();
        };
        poster.addEventListener('load', ready);
        poster.addEventListener('error', () => { setShopping(false, false, false); shopButton.hidden = true; });
        if (poster.complete) ready();
        frame.addEventListener('pointerenter', (event) => {
          if (event.pointerType === 'mouse' || event.pointerType === 'pen') showHoverHotspots();
        });
        frame.addEventListener('pointerleave', dismissHoverHotspots);
        hotspotLayer.addEventListener('focusout', () => {
          window.requestAnimationFrame(dismissHoverHotspots);
        });
        shopButton.addEventListener('click', () => {
          state.hoverShopping = false;
          setShopping(!state.shopping);
          if (state.shopping) {
            hotspotLayer.querySelector('[data-hotspot-sku]')?.focus();
          }
        });
        state.scene.addEventListener('keydown', (event) => {
          if (event.key === 'Escape' && state.shopping) {
            event.preventDefault();
            event.stopPropagation();
            setShopping(false, true);
          }
        });
        const rows = Array.from(state.scene.querySelectorAll('[data-scene-product-sku]'));
        const highlight = (sku) => rows.forEach((row) => row.classList.toggle('is-hotspot-selected', row.dataset.sceneProductSku === sku));
        hotspotLayer.querySelectorAll('[data-hotspot-sku]').forEach((link) => {
          link.dataset.labelSide = parseFloat(link.style.getPropertyValue('--hotspot-x')) > 50 ? 'left' : 'right';
          link.dataset.labelVertical = parseFloat(link.style.getPropertyValue('--hotspot-y')) > 65 ? 'above' : 'below';
          link.addEventListener('pointerenter', () => highlight(link.dataset.hotspotSku));
          link.addEventListener('pointerleave', () => { if (document.activeElement !== link) highlight(''); });
          link.addEventListener('focus', () => highlight(link.dataset.hotspotSku));
          link.addEventListener('blur', () => highlight(''));
        });
      }
      button.hidden = false;
      button.addEventListener('click', () => {
        if (state.failed) {
          state.failed = false;
          state.pending = false;
          video.removeAttribute('src');
        }
        if (state.shopping) setShopping(false, false, false);
        if ((!video.paused || state.pending) && state.wanted) {
          state.paused = true;
          stop(state);
          sync();
        } else {
          state.paused = false;
          state.optIn = true;
          state.manualRequired = false;
          if (!('IntersectionObserver' in window)) state.ratio = 1;
          sync(state);
          if (state.ratio < 0.15) frame.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'auto' });
        }
      });
      video.addEventListener('playing', () => {
        if (!state.wanted || active !== state || document.hidden || suspended) {
          video.pause();
          return;
        }
        frame.classList.add('is-motion-ready');
        buttonText(state);
      });
      video.addEventListener('pause', () => buttonText(state));
      video.addEventListener('error', () => { fail(state); sync(); });
    });
    if (!states.length) return;
    if ('IntersectionObserver' in window) {
      preparationObserver = new IntersectionObserver((entries) => {
        if (suspended) return;
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const state = states.find((item) => item.frame === entry.target);
          if (state) preparePoster(state);
          preparationObserver.unobserve(entry.target);
        });
      }, { rootMargin: '240px 0px', threshold: 0 });
      states.forEach((state) => preparationObserver.observe(state.frame));
      observer = new IntersectionObserver((entries) => {
        if (suspended) return;
        entries.forEach((entry) => {
          const state = states.find((item) => item.frame === entry.target);
          if (state) state.ratio = visibleRatio(entry);
        });
        sync();
      }, { threshold: [0, 0.01, 0.1, 0.15, 0.25, 0.5, 0.75, 1] });
      states.forEach((state) => observer.observe(state.frame));
    } else states.forEach(preparePoster);
    const preferencesChanged = () => {
      states.forEach((state) => { state.optIn = false; });
      sync();
    };
    if (reduced.addEventListener) reduced.addEventListener('change', preferencesChanged);
    else if (reduced.addListener) reduced.addListener(preferencesChanged);
    if (connection && connection.addEventListener) connection.addEventListener('change', preferencesChanged);
    let resizeFrame = 0;
    window.addEventListener('resize', () => {
      if (resizeFrame) return;
      resizeFrame = window.requestAnimationFrame(() => {
        resizeFrame = 0;
        if (suspended) return;
        states.forEach((state) => {
          state.frame.style.setProperty('--scene-tooltip-width', Math.max(80, state.frame.clientWidth * 0.42) + 'px');
        });
      });
    }, { passive: true });
    document.addEventListener('visibilitychange', () => sync());
    window.addEventListener('pagehide', () => {
      suspended = true;
      window.cancelAnimationFrame(resizeFrame);
      resizeFrame = 0;
      observer?.disconnect();
      preparationObserver?.disconnect();
      active = null;
      states.forEach((state) => { state.ratio = 0; stop(state); });
    });
    window.addEventListener('pageshow', () => {
      suspended = false;
      states.forEach((state) => observer?.observe(state.frame));
      states.forEach((state) => { if (!state.prepared) preparationObserver?.observe(state.frame); });
      sync();
    });
    sync();
    window.skyyroseSceneMotionReady = true;
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
