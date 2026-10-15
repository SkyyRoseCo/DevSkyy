/** Approved heroes and native scroll-world choreography. No scroll interception. */
(() => {
  'use strict';
  if (document.documentElement.dataset.recoveryInitialized) return;
  document.documentElement.dataset.recoveryInitialized = 'true';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const connection = navigator.connection;
  const heroes = [];
  let suspended = false;
  const allowed = () => !reduced.matches && !connection?.saveData;
  const sync = state => {
    const active = allowed() && state.visible && !state.paused && !document.hidden && !suspended;
    state.el.dataset.recoveryMotion = active ? 'running' : 'paused';
    state.button.hidden = !allowed();
    state.button.textContent = state.paused ? 'Play motion' : 'Pause motion';
    state.button.setAttribute('aria-pressed', String(state.paused));
    if (!state.video || state.failed || !state.posterReady) return;
    if (!active) {
      state.video.pause();
      if (!allowed()) state.el.classList.remove('is-hero-video-ready');
      return;
    }
    if (!state.loaded) {
      state.sources.forEach(source => {
        source.src = source.dataset.src;
      });
      state.video.muted = true;
      state.video.load();
      state.loaded = true;
    }
    if (state.pending || !state.video.paused) return;
    state.pending = true;
    Promise.resolve(state.video.play())
      .then(() => {
        state.pending = false;
        if (state.failed || !allowed() || !state.visible || state.paused || document.hidden || suspended)
          state.video.pause();
      })
      .catch(error => {
        state.pending = false;
        if (state.failed) return;
        if (error.name === 'AbortError') return;
        if (error.name === 'NotAllowedError') {
          state.paused = true;
          sync(state);
          return;
        }
        state.failed = true;
        state.el.classList.remove('is-hero-video-ready');
        state.el.classList.remove('is-hero-poster-ready');
      });
  };
  const observer =
    'IntersectionObserver' in window
      ? new IntersectionObserver(
          entries => {
            entries.forEach(entry => {
              const state = heroes.find(item => item.el === entry.target);
              if (state) {
                state.visible = entry.isIntersecting;
                sync(state);
              }
            });
          },
          { threshold: 0.12 }
        )
      : null;
  document.querySelectorAll('[data-recovery-hero]').forEach(el => {
    const button = el.querySelector('[data-recovery-motion-toggle]');
    if (!button) return;
    const video = el.querySelector('[data-recovery-hero-video]');
    const state = {
      el,
      button,
      video,
      paused: false,
      visible: !observer,
      loaded: false,
      pending: false,
      failed: false,
      posterReady: !video,
      sources: video ? [...video.querySelectorAll('source[data-src]')] : [],
    };
    heroes.push(state);
    button.addEventListener('click', () => {
      state.paused = !state.paused;
      sync(state);
    });
    if (video) {
      // Publish the browser-selected poster immediately; decoding the image
      // remains a separate gate for competing film requests and playback.
      const poster = el.querySelector('img');
      let posterFailed = false;
      const publishPoster = () => {
        if (state.failed || posterFailed || !poster?.currentSrc) return;
        // Until bytes exist, retain the picture rather than starting another
        // poster request or exposing an empty native video surface.
        if (!poster.naturalWidth) return;
        // Never fall back to img.src: that could fetch the desktop fallback
        // while <picture> has selected a different mobile resource.
        if (video.poster !== poster.currentSrc) video.poster = poster.currentSrc;
        el.classList.add('is-hero-poster-ready');
      };
      const failedPoster = () => {
        posterFailed = true;
        el.classList.remove('is-hero-poster-ready');
      };
      publishPoster();
      poster?.addEventListener('load', () => {
        if (state.loaded) return;
        posterFailed = false;
        publishPoster();
      });
      poster?.addEventListener('error', failedPoster);
      const prepare = (decoded = true) => {
        if (decoded) publishPoster();
        else failedPoster();
        state.posterReady = true;
        sync(state);
      };
      if (poster?.decode) poster.decode().then(prepare, () => prepare(false));
      else prepare();
      const failVideo = () => {
        state.failed = true;
        state.pending = false;
        video.pause();
        el.classList.remove('is-hero-video-ready');
        el.classList.remove('is-hero-poster-ready');
      };
      // Nested source exhaustion need not emit a video error or settle play().
      // Preserve native codec fallback until every activated candidate fails.
      const failedSources = new Set();
      state.sources.forEach(source =>
        source.addEventListener('error', () => {
          if (!state.loaded || state.failed) return;
          failedSources.add(source);
          if (state.sources.every(candidate => failedSources.has(candidate))) failVideo();
        })
      );
      video.addEventListener('playing', () => {
        const reveal = () => {
          if (!video.paused && allowed() && state.visible && !document.hidden && !suspended && !state.failed) {
            el.classList.add('is-hero-video-ready');
          }
        };
        // A playing event can precede the first composited frame. Keep the
        // approved poster until a frame is available, without a timed loader.
        if (video.requestVideoFrameCallback) video.requestVideoFrameCallback(reveal);
        else reveal();
      });
      video.addEventListener('error', failVideo);
    }
    observer?.observe(el);
    sync(state);
  });
  const syncAll = () => {
    document.documentElement.dataset.recoveryMotionAllowed = String(allowed());
    heroes.forEach(sync);
  };
  reduced.addEventListener('change', syncAll);
  connection?.addEventListener?.('change', syncAll);
  document.addEventListener('visibilitychange', syncAll);
  window.addEventListener('pagehide', () => {
    suspended = true;
    observer?.disconnect();
    syncAll();
  });
  window.addEventListener('pageshow', () => {
    suspended = false;
    heroes.forEach(state => observer?.observe(state.el));
    syncAll();
  });
  syncAll();

  // Home prints this controller inline before its collection rail is parsed;
  // bind rails once the document is parsed, immediately when it already is.
  const initRails = () =>
    document.querySelectorAll('[data-recovery-rail]').forEach(rail => {
      const track = rail.querySelector('[data-recovery-track]');
      if (!track) return;
      const items = [...track.children];
      const previous = rail.querySelector('[data-recovery-prev]');
      const next = rail.querySelector('[data-recovery-next]');
      const count = rail.querySelector('[data-recovery-count]');
      let index = 0;
      let frame = 0;
      const update = () => {
        frame = 0;
        const bounds = track.getBoundingClientRect();
        let distance = Infinity;
        items.forEach((item, i) => {
          const rect = item.getBoundingClientRect();
          const offset = rect.left - bounds.left;
          if (Math.abs(offset) < distance) {
            distance = Math.abs(offset);
            index = i;
          }
        });
        previous.disabled = index === 0;
        next.disabled = index === items.length - 1;
        const label = `${String(index + 1).padStart(2, '0')} / ${String(items.length).padStart(2, '0')}`;
        if (count.textContent !== label) count.textContent = label;
      };
      const move = target => {
        const item = items[Math.max(0, Math.min(items.length - 1, target))];
        const offset = item.getBoundingClientRect().left - track.getBoundingClientRect().left;
        track.scrollBy({ left: offset, behavior: allowed() ? 'smooth' : 'instant' });
      };
      previous.addEventListener('click', () => move(index - 1));
      next.addEventListener('click', () => move(index + 1));
      track.addEventListener('keydown', event => {
        if (event.target !== track || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        move(
          event.key === 'Home'
            ? 0
            : event.key === 'End'
              ? items.length - 1
              : index + (event.key === 'ArrowRight' ? 1 : -1)
        );
      });
      const schedule = () => {
        if (!frame) frame = requestAnimationFrame(update);
      };
      track.addEventListener('scroll', schedule, { passive: true });
      window.addEventListener('resize', schedule, { passive: true });
      reduced.addEventListener('change', schedule);
      connection?.addEventListener?.('change', schedule);
      window.addEventListener('pagehide', () => {
        cancelAnimationFrame(frame);
        frame = 0;
      });
      window.addEventListener('pageshow', schedule);
      rail.querySelector('.sr2-recovery-controls').hidden = false;
      update();
    });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initRails, { once: true });
  else initRails();
})();
