/**
 * House of Roses motion controller.
 *
 * Progressive enhancement only: the server-rendered film poster, transcript,
 * chapter links, and commerce links remain complete without this
 * file. CSS owns composition and transitions; this controller owns state,
 * cancellation, media eligibility, and accessible controls.
 *
 * @package SkyyRose_Flagship_2
 */

(() => {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const filmViewport = window.matchMedia('(min-width: 48em)');
  const filmScrollWorld = window.matchMedia('(min-width: 75em) and (hover: hover) and (pointer: fine)');
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const controllers = [];

  const dataSaving = () => Boolean(connection && connection.saveData);
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));

  const listenToMedia = (query, callback, signal) => {
    if (typeof query.addEventListener === 'function') {
      query.addEventListener('change', callback, { signal });
    } else if (typeof query.addListener === 'function') {
      query.addListener(callback);
      signal.addEventListener('abort', () => query.removeListener(callback), { once: true });
    }
  };


  const initFilm = (root) => {
    if (root.dataset.houseController === 'ready') return;

    const video = root.querySelector('[data-house-film-video]');
    if (!video) return;

    const sources = Array.from(video.querySelectorAll('source[data-src]'));
    const directSource = video.dataset.src || '';
    const toggle = root.querySelector('[data-house-film-toggle]');
    const sound = root.querySelector('[data-house-film-sound]');
    const status = root.querySelector('[data-house-film-status]');
    const scrollStage = root.querySelector('[data-scroll-world-stage]');
    const chapters = Array.from(root.querySelectorAll('[data-house-film-chapter][data-start]'));
    const abortController = new AbortController();
    const { signal } = abortController;
    let observer = null;
    let loaded = false;
    let inView = false;
    let userPaused = false;
    let completed = false;
    let autoplayAttempted = false;
    let resumeMutedPlayback = false;
    let scrollWorldActive = false;
    let scrollStart = 0;
    let scrollDistance = 1;
    let scrollFrame = 0;

    root.dataset.houseController = 'ready';
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;
    video.loop = false;
    video.preload = 'none';
    video.removeAttribute('autoplay');

    const hasSource = () => Boolean(sources.some((source) => source.dataset.src) || directSource);
    const mediaEligible = () => filmViewport.matches && !reducedMotion.matches && !dataSaving() && hasSource();

    const setStatus = (value, message = '', announce = false) => {
      root.dataset.houseFilmState = value;
      if (status && announce && message) status.textContent = message;
      root.dispatchEvent(new CustomEvent('house:filmstatechange', {
        bubbles: true,
        detail: { state: value }
      }));
    };

    const syncControls = () => {
      const eligible = mediaEligible();
      if (toggle) {
        toggle.hidden = !eligible;
        toggle.setAttribute('aria-pressed', String(!video.paused && !video.ended));
        toggle.textContent = completed ? 'Replay film' : (video.paused ? 'Play film' : 'Pause film');
      }
      if (sound) {
        sound.hidden = !eligible || !loaded;
        sound.setAttribute('aria-pressed', String(!video.muted));
        sound.textContent = video.muted ? 'Turn sound on' : 'Mute film';
      }
    };

    const unload = () => {
      video.pause();
      sources.forEach((source) => source.removeAttribute('src'));
      video.removeAttribute('src');
      if (loaded) video.load();
      loaded = false;
      resumeMutedPlayback = false;
      root.dataset.houseFilmMode = 'poster';
    };

    const load = () => {
      if (loaded || !mediaEligible()) return false;
      if (sources.length) {
        sources.forEach((source) => {
          if (source.dataset.src) source.src = source.dataset.src;
        });
      } else if (directSource) {
        video.src = directSource;
      }
      loaded = true;
      root.dataset.houseFilmMode = 'video';
      setStatus('loading');
      video.load();
      syncControls();
      return true;
    };

    const play = (sourceType) => {
      if (!mediaEligible()) return;
      load();
      if (completed || video.ended) {
        video.currentTime = 0;
        completed = false;
      }
      if (sourceType !== 'sound') video.muted = sourceType !== 'user-sound';
      video.play().then(() => {
        userPaused = false;
        setStatus('playing', sourceType.startsWith('user') ? 'Skyy Rose Tour previsualization playing.' : '', sourceType.startsWith('user'));
        syncControls();
      }).catch(() => {
        setStatus('poster', 'Film playback is unavailable. The poster, chapters, and collection links remain available.', true);
        syncControls();
      });
    };

    const pause = (reason, announce = false) => {
      if (!video.paused) video.pause();
      setStatus(reason, announce ? 'Skyy Rose Tour previsualization paused.' : '', announce);
      syncControls();
    };

    const updateChapter = () => {
      if (!chapters.length) return;
      const currentTime = video.currentTime || 0;
      let active = 0;
      chapters.forEach((chapter, index) => {
        if (currentTime >= Number.parseFloat(chapter.dataset.start || '0')) active = index;
      });
      chapters.forEach((chapter, index) => {
        const selected = index === active;
        chapter.dataset.houseFilmActive = selected ? 'true' : 'false';
        if (selected) {
          chapter.setAttribute('aria-current', 'true');
        } else {
          chapter.removeAttribute('aria-current');
        }
      });
      root.style.setProperty('--house-film-progress', video.duration ? String(currentTime / video.duration) : '0');
    };

    const updateScrollWorld = () => {
      scrollFrame = 0;
      if (!scrollWorldActive || !video.duration || document.hidden) return;
      const ratio = clamp((window.scrollY - scrollStart) / scrollDistance, 0, 1);
      const targetTime = ratio * video.duration;
      if (Math.abs(video.currentTime - targetTime) > 0.03) video.currentTime = targetTime;
      updateChapter();
    };

    const requestScrollWorldUpdate = () => {
      if (!scrollWorldActive || scrollFrame) return;
      scrollFrame = window.requestAnimationFrame(updateScrollWorld);
    };

    const disableScrollWorld = () => {
      if (!scrollWorldActive) return;
      scrollWorldActive = false;
      if (scrollFrame) window.cancelAnimationFrame(scrollFrame);
      scrollFrame = 0;
      root.classList.remove('is-scroll-world');
      root.style.height = '';
    };

    const layoutScrollWorld = () => {
      const eligible = root.hasAttribute('data-house-film-scroll-world')
        && scrollStage
        && filmScrollWorld.matches
        && !reducedMotion.matches
        && mediaEligible()
        && loaded
        && video.duration;
      if (!eligible) {
        disableScrollWorld();
        return;
      }
      scrollWorldActive = true;
      video.pause();
      root.classList.add('is-scroll-world');
      const headerHeight = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sr2-header')) || 0;
      const worldTop = root.getBoundingClientRect().top + window.scrollY;
      scrollDistance = Math.max(window.innerHeight * 4, chapters.length * window.innerHeight * 0.72);
      scrollStart = worldTop - headerHeight;
      root.style.height = `${scrollStage.offsetHeight + scrollDistance}px`;
      requestScrollWorldUpdate();
    };

    const maybeAutoplay = () => {
      if (root.hasAttribute('data-house-film-scroll-world') && filmScrollWorld.matches && !reducedMotion.matches) return;
      const requested = root.dataset.houseFilmAutoplay === 'true' || root.dataset.houseFilmAutoplay === 'once';
      if (!requested || autoplayAttempted || !inView || document.hidden || !mediaEligible()) return;
      autoplayAttempted = true;
      play('auto');
    };

    const prepareScrollWorld = () => {
      if (
        !root.hasAttribute('data-house-film-scroll-world')
        || !filmScrollWorld.matches
        || reducedMotion.matches
        || !inView
        || !mediaEligible()
      ) return false;
      load();
      if (video.readyState >= 1) layoutScrollWorld();
      return true;
    };

    const eligibilityChanged = () => {
      if (!mediaEligible()) {
        unload();
        setStatus('poster');
      } else if (inView && !prepareScrollWorld()) {
        maybeAutoplay();
      }
      syncControls();
    };

    toggle?.addEventListener('click', () => {
      if (!video.paused && !video.ended) {
        userPaused = true;
        pause('paused-user', true);
      } else {
        play('user');
      }
    }, { signal });

    sound?.addEventListener('click', () => {
      if (!loaded || video.paused) return;
      video.muted = !video.muted;
      setStatus(video.muted ? 'playing-muted' : 'playing-sound', video.muted ? 'Film muted.' : 'Film sound on.', true);
      syncControls();
    }, { signal });

    video.addEventListener('loadedmetadata', () => {
      setStatus('ready');
      layoutScrollWorld();
      syncControls();
    }, { signal });
    video.addEventListener('play', syncControls, { signal });
    video.addEventListener('pause', syncControls, { signal });
    video.addEventListener('timeupdate', updateChapter, { passive: true, signal });
    video.addEventListener('ended', () => {
      completed = true;
      userPaused = true;
      setStatus('complete', 'Skyy Rose Tour previsualization complete.', true);
      syncControls();
    }, { signal });
    video.addEventListener('error', () => {
      loaded = false;
      root.dataset.houseFilmMode = 'poster';
      setStatus('error', 'Film playback is unavailable. The poster, chapters, and collection links remain available.', true);
      syncControls();
    }, { signal });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        resumeMutedPlayback = !video.paused && video.muted && !userPaused;
        pause('paused-hidden');
      } else if (resumeMutedPlayback && inView && mediaEligible()) {
        resumeMutedPlayback = false;
        play('auto-resume');
      }
    }, { signal });

    listenToMedia(reducedMotion, eligibilityChanged, signal);
    listenToMedia(filmViewport, eligibilityChanged, signal);
    listenToMedia(filmScrollWorld, layoutScrollWorld, signal);
    connection?.addEventListener?.('change', eligibilityChanged, { signal });
    window.addEventListener('scroll', requestScrollWorldUpdate, { passive: true, signal });
    window.addEventListener('resize', layoutScrollWorld, { passive: true, signal });

    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver((entries) => {
        inView = Boolean(entries[0]?.isIntersecting);
        if (inView) {
          if (prepareScrollWorld()) {
            resumeMutedPlayback = false;
          } else if (resumeMutedPlayback && mediaEligible()) {
            resumeMutedPlayback = false;
            play('auto-resume');
          } else {
            maybeAutoplay();
          }
        } else if (!video.paused) {
          resumeMutedPlayback = video.muted && !userPaused;
          pause('paused-offscreen');
        }
      }, { threshold: 0.35 });
      observer.observe(root);
    } else {
      inView = true;
    }

    const cleanup = () => {
      video.pause();
      disableScrollWorld();
      observer?.disconnect();
      abortController.abort();
      root.style.removeProperty('--house-film-progress');
      delete root.dataset.houseController;
    };

    eligibilityChanged();
    maybeAutoplay();
    controllers.push(cleanup);
  };

  const init = () => {
    document.querySelectorAll('[data-house-film]').forEach(initFilm);
  };

  const cleanupAll = () => {
    while (controllers.length) controllers.pop()();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }

  window.addEventListener('pagehide', cleanupAll, { once: true });
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) init();
  });
})();
