(() => {
  'use strict';

  const root = document.documentElement;
  const body = document.body;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const header = document.querySelector('[data-site-header]');
  const menuButton = document.querySelector('[data-sr2-menu]');
  const menu = document.querySelector('[data-sr2-nav]');

  root.classList.add('sr2-motion-ready');

  let saveData = Boolean(navigator.connection?.saveData);
  if (reducedMotion || saveData) {
    root.classList.add('sr2-motion-reduced');
  }

  // Founder-approved rotating identity. Keep the reserved still immediately
  // usable; start the unchanged animation after critical page resources load.
  const brandMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const brandConnection = navigator.connection;
  document.querySelectorAll('[data-brand-animation]').forEach((image) => {
    const fallback = image.src;
    let nearViewport = image.dataset.brandAnimationMode !== 'viewport';
    let pageReady = document.readyState === 'complete';
    let imageFailed = false;
    let videoFailed = false;
    let video = null;
    let videoReady = false;
    let videoTimer = null;
    let playAttempt = 0;
    const wantsMotion = () => pageReady && nearViewport && !document.hidden && !brandMotion.matches && !brandConnection?.saveData;
    const showImage = () => { image.dataset.brandVideoActive = 'false'; };
    const failVideo = () => {
      videoFailed = true;
      playAttempt += 1;
      clearTimeout(videoTimer);
      if (video) { video.pause(); video.hidden = true; video.removeAttribute('src'); video.load(); }
      showImage();
      update();
    };
    const playVideo = () => {
      const attempt = ++playAttempt;
      video.play().then(() => {
        if (attempt !== playAttempt) return;
        if (!wantsMotion() || videoFailed) { video.pause(); return; }
        video.hidden = false;
        image.dataset.brandVideoActive = 'true';
      }).catch(() => {
        // A preference/proximity pause cancels pending play promises. That is
        // lifecycle cancellation, not a codec or delivery failure.
        if (attempt !== playAttempt || !wantsMotion()) return;
        failVideo();
      });
    };
    const update = () => {
      const animate = wantsMotion();
      image.dataset.brandAnimationLoaded = String(animate);
      if (!animate) {
        playAttempt += 1;
        if (video) { video.pause(); video.hidden = true; }
        showImage();
        if (image.src !== fallback) image.src = fallback;
        return;
      }
      if (!video && !videoFailed && image.dataset.brandVideo) {
        const candidate = document.createElement('video');
        if (!candidate.canPlayType('video/webm; codecs="vp9"')) videoFailed = true;
        else {
          video = candidate;
          video.muted = true;
          video.defaultMuted = true;
          video.playsInline = true;
          video.loop = true;
          video.preload = 'auto';
          video.hidden = true;
          video.setAttribute('aria-hidden', 'true');
          video.tabIndex = -1;
          video.addEventListener('error', failVideo, { once: true });
          video.addEventListener('loadeddata', () => {
            // Some engines decode VP9 but discard its alpha. Verify the exact
            // asset's transparent corner before revealing its first frame.
            try {
              const canvas = document.createElement('canvas');
              canvas.width = canvas.height = 1;
              const context = canvas.getContext('2d');
              context.drawImage(video, 0, 0, 1, 1, 0, 0, 1, 1);
              if (context.getImageData(0, 0, 1, 1).data[3] !== 0) { failVideo(); return; }
              clearTimeout(videoTimer);
              videoReady = true;
              if (wantsMotion()) playVideo();
            } catch { failVideo(); }
          }, { once: true });
          image.parentElement.append(video);
          videoTimer = setTimeout(failVideo, 12000);
          video.src = image.dataset.brandVideo;
          return;
        }
      }
      if (video && !videoFailed) {
        if (videoReady) playVideo();
        return;
      }
      const source = imageFailed ? fallback : image.dataset.brandAnimation;
      if (image.src !== source) image.src = source;
    };
    image.addEventListener('error', () => {
      imageFailed = true;
      update();
    });
    brandMotion.addEventListener?.('change', update);
    brandConnection?.addEventListener?.('change', update);
    document.addEventListener('visibilitychange', update);
    if (!nearViewport) {
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
          nearViewport = entries.some((entry) => entry.isIntersecting);
          update();
        }, { rootMargin: '320px 0px' });
        observer.observe(image);
      } else {
        // Unsupported observers still retain the approved animation.
        nearViewport = true;
      }
    }
    if (pageReady) update();
    else window.addEventListener('load', () => { pageReady = true; update(); }, { once: true });
  });

  /* One lifecycle owns shell navigation and every native dialog. Native modal
     semantics remain intact, including third-party/mascot showModal() calls. */
  const overlays = (() => {
    let active = null;
    let lock = null;
    const inertState = new Map();
    const wired = new WeakSet();
    const focusable = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
    const visible = (element) => element?.isConnected && !element.closest('[inert]') && element.getClientRects().length && getComputedStyle(element).visibility !== 'hidden';
    const controls = (scope) => [...scope.querySelectorAll(focusable)].filter(visible);
    const rememberStyle = (element, names) => names.map((name) => [name, element.style.getPropertyValue(name), element.style.getPropertyPriority(name)]);
    const restoreStyle = (element, values) => values.forEach(([name, value, priority]) => {
      if (value) element.style.setProperty(name, value, priority);
      else element.style.removeProperty(name);
    });
    const lockScroll = () => {
      if (lock) return;
      const gutter = Math.max(0, window.innerWidth - root.clientWidth);
      lock = {
        x: window.scrollX, y: window.scrollY,
        body: rememberStyle(body, ['position', 'top', 'left', 'width', 'overflow', 'padding-right']),
        root: rememberStyle(root, ['overflow', 'scroll-behavior', '--sr2-scrollbar']),
      };
      const padding = Number.parseFloat(getComputedStyle(body).paddingRight) || 0;
      body.style.setProperty('position', 'fixed');
      body.style.setProperty('top', `${-lock.y}px`);
      body.style.setProperty('left', `${-lock.x}px`);
      body.style.setProperty('width', '100%');
      body.style.setProperty('overflow', 'hidden');
      if (gutter) body.style.setProperty('padding-right', `${padding + gutter}px`);
      root.style.setProperty('overflow', 'hidden');
      root.style.setProperty('--sr2-scrollbar', `${gutter}px`);
      body.classList.add('sr2-overlay-open');
    };
    const unlockScroll = () => {
      if (!lock) return;
      const previous = lock;
      lock = null;
      restoreStyle(body, previous.body);
      restoreStyle(root, previous.root);
      body.classList.remove('sr2-overlay-open');
      // CSS smooth scrolling must not animate a restored body position.
      root.style.setProperty('scroll-behavior', 'auto');
      window.scrollTo(previous.x, previous.y);
      restoreStyle(root, previous.root);
    };
    const restoreInert = () => {
      inertState.forEach((value, element) => { element.inert = value; });
      inertState.clear();
    };
    const isolate = (scope) => {
      restoreInert();
      // Preserve all siblings along the active scope's ancestor path. A dialog
      // may live inside main/footer; never make its own ancestor inert.
      for (let node = scope; node && node !== body; node = node.parentElement) {
        if (!node.parentElement) break;
        [...node.parentElement.children].forEach((sibling) => {
          if (sibling === node || sibling.matches('script, style, link')) return;
          inertState.set(sibling, sibling.inert);
          sibling.inert = true;
        });
      }
    };
    const returnFocus = (opener) => {
      const target = visible(opener) ? opener : (visible(menuButton) ? menuButton : null);
      target?.focus({ preventScroll: true });

    };
    const close = (restoreFocus = true, keepLock = false) => {
      const previous = active;
      active = null;
      if (previous?.kind === 'navigation') {
        menu.classList.remove('is-open');
        menuButton.setAttribute('aria-expanded', 'false');
        menuButton.setAttribute('aria-label', 'Open site menu');
        body.classList.remove('sr2-nav-open');
      } else if (previous?.element.open) {
        previous.element.close();
      }
      restoreInert();
      if (!keepLock) unlockScroll();
      if (restoreFocus && previous) returnFocus(previous.opener);
    };
    const activate = (element, kind, opener) => {
      if (active?.element === element) return;
      // Capture the initiating control before closing another overlay restores
      // native dialog focus. Hidden menu links fall back to the menu trigger.
      const origin = opener || document.activeElement;
      close(false, true);
      document.querySelectorAll('dialog[open]').forEach((other) => {
        if (other !== element) other.close();
      });
      active = { element, kind, opener: origin };
      lockScroll();
      isolate(kind === 'navigation' ? header : element);
      header?.classList.remove('is-hidden');
    };
    const register = (dialog) => {
      if (wired.has(dialog)) return;
      wired.add(dialog);
      dialog.addEventListener('beforetoggle', (event) => {
        if (event.newState !== 'open') return;
        activate(dialog, 'dialog');
        // Another native listener may cancel beforetoggle. A canceled opening
        // must release the lock even though no open-attribute mutation occurs.
        window.queueMicrotask?.(() => {
          if (active?.element === dialog && !dialog.open) close();
        });
      });
      dialog.addEventListener('close', () => {
        if (active?.element === dialog && !dialog.open) close();
      });
      dialog.addEventListener('cancel', (event) => {
        if (active?.element !== dialog) return;
        event.preventDefault();
        close();
      });
    };
    const openDialog = (dialog, opener) => {
      if (typeof dialog?.showModal !== 'function') return false;
      register(dialog);
      activate(dialog, 'dialog', opener);
      try {
        if (!dialog.open) dialog.showModal();
        return true;
      } catch {
        close();
        return false;
      }
    };
    const setNavigation = (open) => {
      if (!menuButton || !menu || !header) return;
      if (!open) {
        if (active?.kind === 'navigation') close();
        return;
      }
      activate(menu, 'navigation', menuButton);
      menu.classList.add('is-open');
      menuButton.setAttribute('aria-expanded', 'true');
      menuButton.setAttribute('aria-label', 'Close site menu');
      body.classList.add('sr2-nav-open');
      controls(menu)[0]?.focus({ preventScroll: true });
    };
    const ensureFocus = () => {
      if (!active) return;
      const scope = active.kind === 'navigation' ? header : active.element;
      if (!scope.contains(document.activeElement) || !visible(document.activeElement)) {
        controls(scope)[0]?.focus({ preventScroll: true });
      }
    };
    document.querySelectorAll('dialog').forEach(register);
    // Observe inserted/native dialogs for browsers without beforetoggle support
    // and for external native showModal() callers; do not patch browser methods.
    if ('MutationObserver' in window) {
      new MutationObserver(() => {
        document.querySelectorAll('dialog').forEach(register);
        const openDialogs = [...document.querySelectorAll('dialog[open]')];
        const newlyOpened = openDialogs.find((dialog) => dialog !== active?.element);
        if (newlyOpened) activate(newlyOpened, 'dialog');
        else if (active?.kind === 'dialog' && (!active.element.open || !active.element.isConnected)) close();
        // Woo fragments can detach the focused remove link without firing
        // focusin. Repair only lost/hidden focus; preserve a valid field focus.
        ensureFocus();
      }).observe(body, { childList: true, subtree: true, attributes: true, attributeFilter: ['open'] });
    }
    document.addEventListener('keydown', (event) => {
      if (!active) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        // The same key must not reach guide/page handlers after focus returns.
        event.stopImmediatePropagation?.();
        close();
      } else if (event.key === 'Tab') {
        const scope = active.kind === 'navigation' ? header : active.element;
        const items = controls(scope);
        const first = items[0];
        const last = items[items.length - 1];
        if (!first) { event.preventDefault(); active.element.focus({ preventScroll: true }); }
        else if (!scope.contains(document.activeElement) || (event.shiftKey && document.activeElement === first)) {
          event.preventDefault(); (event.shiftKey ? last : first).focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault(); first.focus();
        }
      }
    }, true);
    document.addEventListener('focusin', (event) => {
      if (!active) return;
      const scope = active.kind === 'navigation' ? header : active.element;
      if (!scope.contains(event.target)) controls(scope)[0]?.focus({ preventScroll: true });
    });
    window.addEventListener('resize', () => {
      if (!active) return;
      const scope = active.kind === 'navigation' ? header : active.element;
      if (!visible(document.activeElement)) controls(scope)[0]?.focus({ preventScroll: true });
    }, { passive: true });
    // Clear state before leaving and on bfcache restoration, even if an opener
    // navigates away mid-transition. Scroll and inline-style snapshots are exact.
    window.addEventListener('pagehide', () => close(false));
    window.addEventListener('pageshow', () => close(false));
    return { close, openDialog, setNavigation, isOpen: () => Boolean(active) };
  })();
  const setMenu = (open) => overlays.setNavigation(open);
  if (menuButton && menu) {
    menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
    menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        if (!link.matches('[data-search-open], [data-bag-open]')) setMenu(false);
      });
    });
  }

  if (header) {
    let ticking = false;

    const updateHeader = () => {
      const currentY = window.scrollY;
      header.classList.toggle('is-scrolled', currentY > 48);
      // The house shell keeps navigation and commerce access stable on scroll.
      header.classList.remove('is-hidden');
      ticking = false;
    };

    header.addEventListener('focusin', () => header.classList.remove('is-hidden'));
    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(updateHeader);
    }, { passive: true });
  }

  /* Narrative photography can reveal as it enters the viewport. Structural
     headings, commerce cards, and service content must never begin hidden: a
     delayed observer or full-page capture must still render a complete page. */
  const revealTargets = document.querySelectorAll('.sr2-image-reveal');

  if ('IntersectionObserver' in window && !reducedMotion) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-seen');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    revealTargets.forEach((target) => {
      if (!target.classList.contains('sr2-image-reveal')) target.classList.add('sr2-reveal');
      revealObserver.observe(target);
    });
  } else {
    revealTargets.forEach((target) => target.classList.add('is-seen'));
  }

  /* Collection monuments are one distinct scene per world. Keep the motion
     declarative in CSS, and use this controller exclusively to prevent any
     animation work once the scene is off-screen, the tab is hidden, or the
     visitor explicitly asks for less data or motion. */
  document.querySelectorAll('[data-scene-motion]').forEach((scene) => {
    const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const hero = scene.closest('.sr2-collection-hero');
    const motionVideo = hero?.querySelector('[data-collection-hero-video]');
    const motionToggle = hero?.querySelector('[data-scene-motion-toggle]');
    const motionSources = motionVideo ? Array.from(motionVideo.querySelectorAll('source[data-src]')) : [];
    let motionLoaded = false;
    let motionReady = false;
    let motionFailed = false;
    let loadTimer = 0;
    let inViewport = false;
    let explicitlyPaused = false;

    const markMotionFailed = () => {
      motionFailed = true;
      motionReady = false;
      window.clearTimeout(loadTimer);
      hero?.classList.remove('has-motion-plate');
      if (motionVideo) {
        motionVideo.dataset.motionState = 'fallback';
        motionVideo.pause();
      }
    };

    const markMotionReady = () => {
      if (motionFailed) return;
      motionReady = true;
      window.clearTimeout(loadTimer);
      hero?.classList.add('has-motion-plate');
      if (motionVideo) motionVideo.dataset.motionState = 'ready';
      syncScene();
    };

    const loadMotion = () => {
      if (!motionVideo || motionLoaded || motionFailed) return;
      if (motionSources.length < 2 || motionSources.some((source) => !source.dataset.src)) {
        markMotionFailed();
        return;
      }
      motionLoaded = true;
      motionSources.forEach((source) => {
        source.src = source.dataset.src;
        delete source.dataset.src;
      });
      motionVideo.dataset.motionState = 'loading';
      motionVideo.addEventListener('canplay', markMotionReady, { once: true });
      motionVideo.addEventListener('error', markMotionFailed, { once: true });
      motionVideo.addEventListener('abort', markMotionFailed, { once: true });
      loadTimer = window.setTimeout(markMotionFailed, 12000);
      motionVideo.load();
    };

    const syncScene = () => {
      const motionAvailable = !motionPreference.matches && !saveData;
      const canAnimate = motionAvailable && !explicitlyPaused && !document.hidden;
      const state = canAnimate && inViewport ? 'running' : (canAnimate ? 'paused' : 'static');
      scene.dataset.sceneState = state;
      scene.dataset.sceneMode = motionPreference.matches ? 'reduced' : (saveData ? 'data-save' : 'cinematic');
      hero?.classList.toggle('is-scene-running', state === 'running');
      if (motionToggle) {
        motionToggle.hidden = !motionAvailable;
        motionToggle.setAttribute('aria-pressed', String(explicitlyPaused));
        motionToggle.textContent = explicitlyPaused ? 'Resume motion' : 'Pause motion';
      }
      if (motionVideo && !motionFailed && canAnimate && inViewport) {
        loadMotion();
        if (motionReady) motionVideo.play().catch(markMotionFailed);
      } else {
        motionVideo?.pause();
      }
    };

    motionToggle?.addEventListener('click', () => {
      explicitlyPaused = !explicitlyPaused;
      syncScene();
    });

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        inViewport = Boolean(entries[0]?.isIntersecting);
        syncScene();
      }, { rootMargin: '18% 0px', threshold: 0.01 });
      observer.observe(hero || scene);
      window.addEventListener('pagehide', () => observer.disconnect(), { once: true });
    } else {
      // A static scene is the correct progressive fallback; do not start an
      // infinite effect if visibility cannot be measured.
      inViewport = false;
    }

    document.addEventListener('visibilitychange', syncScene);
    if (motionPreference.addEventListener) {
      motionPreference.addEventListener('change', syncScene);
    } else if (motionPreference.addListener) {
      motionPreference.addListener(syncScene);
    }
    navigator.connection?.addEventListener?.('change', () => {
      saveData = Boolean(navigator.connection?.saveData);
      root.classList.toggle('sr2-motion-reduced', motionPreference.matches || saveData);
      syncScene();
    });
    syncScene();
  });

  const setupPinnedWorld = (world, rail, chapters, previous, next, count, progress) => {
    const stage = world.querySelector('[data-scroll-world-stage]');
    if (!stage) return false;

    // Scroll World is an expanded-desktop enhancement only. The rail remains a
    // native horizontal scroller at compact and medium widths, where a pinned
    // scene would compromise touch and keyboard reading order.
    const expandedPointer = window.matchMedia('(min-width: 1200px) and (hover: hover) and (pointer: fine)');
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    let start = 0;
    let distance = 1;
    let frame = 0;
    let layoutFrame = 0;
    let active = false;
    let resizeObserver = null;

    const setPosition = (ratio) => {
      const safeRatio = Math.min(1, Math.max(0, ratio));
      rail.style.transform = `translate3d(${-safeRatio * distance}px, 0, 0)`;
      if (progress) progress.style.transform = `scaleX(${1 + safeRatio * 3})`;
      if (count && chapters.length) {
        const current = Math.min(chapters.length - 1, Math.round(safeRatio * (chapters.length - 1)));
        count.textContent = `${String(current + 1).padStart(2, '0')} / ${String(chapters.length).padStart(2, '0')}`;
      }
    };

    const update = () => {
      frame = 0;
      if (!active || document.hidden) return;
      setPosition((window.scrollY - start) / distance);
    };

    const requestUpdate = () => {
      if (!active || frame) return;
      frame = window.requestAnimationFrame(update);
    };

    const layout = () => {
      layoutFrame = 0;
      if (!active) return;
      const headerHeight = Number.parseFloat(getComputedStyle(root).getPropertyValue('--sr2-header')) || 0;
      const worldTop = world.getBoundingClientRect().top + window.scrollY;
      distance = Math.max(1, rail.scrollWidth - stage.clientWidth);
      start = worldTop + stage.offsetTop - headerHeight;
      world.style.height = `${stage.offsetTop + stage.clientHeight + distance}px`;
      requestUpdate();
    };

    const requestLayout = () => {
      if (!active || layoutFrame) return;
      layoutFrame = window.requestAnimationFrame(layout);
    };

    const goToChapter = (offset) => {
      if (!active) {
        const first = chapters[0];
        const amount = first ? first.getBoundingClientRect().width + 24 : rail.clientWidth * 0.8;
        rail.scrollBy({ left: offset * amount, behavior: 'auto' });
        return;
      }
      const currentRatio = Math.min(1, Math.max(0, (window.scrollY - start) / distance));
      const current = Math.round(currentRatio * (chapters.length - 1));
      const target = Math.min(chapters.length - 1, Math.max(0, current + offset));
      const top = start + (target / Math.max(1, chapters.length - 1)) * distance;
      window.scrollTo({ top, behavior: 'auto' });
    };

    const disable = () => {
      if (!active) return;
      active = false;
      if (frame) window.cancelAnimationFrame(frame);
      if (layoutFrame) window.cancelAnimationFrame(layoutFrame);
      frame = 0;
      layoutFrame = 0;
      setPosition(0);
      rail.style.transform = '';
      world.style.height = '';
      world.classList.remove('is-scroll-world');
    };

    const enable = () => {
      if (active || reducedMotionQuery.matches || !expandedPointer.matches) return;
      active = true;
      world.classList.add('is-scroll-world');
      rail.scrollLeft = 0;
      requestLayout();
    };

    const syncCapability = () => {
      if (reducedMotionQuery.matches || !expandedPointer.matches) {
        disable();
        return;
      }
      enable();
    };

    const onVisibilityChange = () => {
      if (document.hidden) {
        if (frame) window.cancelAnimationFrame(frame);
        frame = 0;
        return;
      }
      requestLayout();
      requestUpdate();
    };

    const onPageHide = () => {
      disable();
      resizeObserver?.disconnect();
    };

    const onPageShow = () => {
      resizeObserver?.observe(stage);
      resizeObserver?.observe(rail);
      syncCapability();
      requestLayout();
    };

    previous?.addEventListener('click', () => goToChapter(-1));
    next?.addEventListener('click', () => goToChapter(1));
    window.addEventListener('scroll', requestUpdate, { passive: true });
    window.addEventListener('resize', requestLayout, { passive: true });
    document.addEventListener('visibilitychange', onVisibilityChange, { passive: true });
    window.addEventListener('pagehide', onPageHide, { passive: true });
    window.addEventListener('pageshow', onPageShow, { passive: true });
    expandedPointer.addEventListener('change', syncCapability);
    reducedMotionQuery.addEventListener('change', syncCapability);

    if ('ResizeObserver' in window) {
      resizeObserver = new ResizeObserver(requestLayout);
      resizeObserver.observe(stage);
      resizeObserver.observe(rail);
    }

    syncCapability();
    return true;
  };

  const setupRail = (rail) => {
    const world = rail.closest('[data-horizontal-world]');
    const previous = world ? world.querySelector('[data-rail-prev]') : null;
    const next = world ? world.querySelector('[data-rail-next]') : null;
    const count = world ? world.querySelector('[data-rail-count]') : null;
    const progress = world ? world.querySelector('[data-rail-progress]') : null;
    const chapters = Array.from(rail.children);
    const storyProgress = rail.parentElement ? rail.parentElement.querySelector('.sr2-world-story__progress span') : null;

    if (world?.hasAttribute('data-scroll-world-pinned') && finePointer && !reducedMotion && window.matchMedia('(min-width: 1200px)').matches) {
      if (setupPinnedWorld(world, rail, chapters, previous, next, count, progress)) return;
    }

    const amount = () => {
      const first = chapters[0];
      return first ? first.getBoundingClientRect().width + 24 : rail.clientWidth * 0.8;
    };

    const updateRail = () => {
      const max = Math.max(1, rail.scrollWidth - rail.clientWidth);
      const ratio = Math.min(1, Math.max(0, rail.scrollLeft / max));
      if (progress) progress.style.transform = `scaleX(${1 + ratio * 3})`;
      if (storyProgress) storyProgress.style.transform = `scaleX(${ratio})`;

      if (count && chapters.length) {
        const center = rail.scrollLeft + rail.clientWidth / 2;
        let current = 0;
        chapters.forEach((chapter, index) => {
          if (chapter.offsetLeft <= center) current = index;
        });
        count.textContent = `${String(Math.min(current + 1, chapters.length)).padStart(2, '0')} / ${String(chapters.length).padStart(2, '0')}`;
      }
    };

    previous?.addEventListener('click', () => rail.scrollBy({ left: -amount(), behavior: reducedMotion ? 'auto' : 'smooth' }));
    next?.addEventListener('click', () => rail.scrollBy({ left: amount(), behavior: reducedMotion ? 'auto' : 'smooth' }));
    rail.addEventListener('scroll', () => window.requestAnimationFrame(updateRail), { passive: true });

    updateRail();
  };

  document.querySelectorAll('[data-horizontal-rail]').forEach(setupRail);



  /* Immediate card preview over the direct PDP link. The separate commerce
   * module refreshes server facts and imports the native purchase form on
   * intent; the PDP remains the complete progressive fallback. */
  const quickView = document.querySelector('[data-quick-view-dialog], #sr2-quick-view-dialog');
  if (quickView && typeof quickView.showModal === 'function') {
    const fields = {
      name: quickView.querySelector('[data-quick-view-name]'),
      collection: quickView.querySelector('[data-quick-view-collection]'),
      price: quickView.querySelector('[data-quick-view-price]'),
      availability: quickView.querySelector('[data-quick-view-availability]'),
      excerpt: quickView.querySelector('[data-quick-view-excerpt]'),
      image: quickView.querySelector('[data-quick-view-image]'),
      media: quickView.querySelector('[data-quick-view-media]'),
      url: quickView.querySelector('[data-quick-view-url]')
    };
    const closeQuickView = () => overlays.close();
    document.querySelectorAll('[data-quick-view]').forEach((button) => {
      button.addEventListener('click', (event) => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        Object.entries(fields).forEach(([key, field]) => {
          if (!field || key === 'media') return;
          const value = button.dataset[`quickView${key[0].toUpperCase()}${key.slice(1)}`] || '';
          if (key === 'image') {
            field.src = value;
            field.alt = button.dataset.quickViewName || '';
            if (fields.media) fields.media.hidden = !value;
          } else if (key === 'url') {
            field.href = value || '#';
          } else {
            field.textContent = value;
          }
        });
        if (overlays.openDialog(quickView, button)) event.preventDefault();
      });
    });
    quickView.querySelectorAll('[data-quick-view-dismiss]').forEach((button) => button.addEventListener('click', closeQuickView));
    quickView.addEventListener('click', (event) => { if (event.target === quickView) closeQuickView(); });
  }

  const sizeGuide = document.querySelector('#sr2-size-guide-dialog');
  if (sizeGuide && typeof sizeGuide.showModal === 'function') {
    document.querySelectorAll('[data-size-guide-open]').forEach((button) => {
      button.addEventListener('click', (event) => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        if (overlays.openDialog(sizeGuide, button)) event.preventDefault();
      });
    });
    sizeGuide.addEventListener('click', (event) => { if (event.target === sizeGuide) overlays.close(); });
  }

  /* Native links and GET search remain complete progressive fallbacks. The bag
     uses Woo-rendered fragments; no prices, totals or cart writes live here. */
  [
    ['#sr2-search-dialog', '[data-search-open]', '[data-search-input]'],
    ['#sr2-bag-dialog', '[data-bag-open]', '[data-bag-close]'],
  ].forEach(([selector, trigger, initialFocus]) => {
    const dialog = document.querySelector(selector);
    if (!dialog || typeof dialog.showModal !== 'function') return;
    document.querySelectorAll(trigger).forEach((button) => {
      button.addEventListener('click', (event) => {
        // Keep ordinary modified-link gestures and native route behavior.
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        if (!overlays.openDialog(dialog, button)) return;
        event.preventDefault();
        dialog.querySelector(initialFocus)?.focus({ preventScroll: true });
      });
    });
    dialog.querySelectorAll('[data-bag-close], [data-search-close]').forEach((button) => {
      button.addEventListener('click', () => overlays.close());
    });
    dialog.addEventListener('click', (event) => { if (event.target === dialog) overlays.close(); });
  });

  /* Woo's global live region is outside the modal accessibility tree. Relay
     only its own confirmed success message to a stable in-dialog status. */
  const bagDialog = document.querySelector('#sr2-bag-dialog');
  const bagStatus = bagDialog?.querySelector('[data-bag-status]');
  if (bagStatus && window.jQuery) {
    let pendingRemoval = null;
    bagDialog.addEventListener('click', (event) => {
      const control = event.target.closest?.('.remove_from_cart_button');
      if (!control || !bagDialog.contains(control)) return;
      pendingRemoval = control;
      bagStatus.textContent = '';
    });
    window.jQuery(body).on('removed_from_cart.sr2Bag', (_event, _fragments, _hash, button) => {
      if (!bagDialog.open || !pendingRemoval || button?.[0] !== pendingRemoval) return;
      const message = button.data('success_message');
      pendingRemoval = null;
      if (typeof message === 'string' && message.trim()) bagStatus.textContent = message;
    });
    bagDialog.addEventListener('close', () => { pendingRemoval = null; bagStatus.textContent = ''; });
  }

  if (finePointer && !reducedMotion) {

    document.querySelectorAll('[data-hero-depth]').forEach((hero) => {
      const media = hero.querySelector('img');
      if (!media) return;
      hero.addEventListener('pointermove', (event) => {
        const x = event.clientX / window.innerWidth - 0.5;
        const y = event.clientY / window.innerHeight - 0.5;
        media.style.transform = `scale(1.025) translate(${x * -8}px, ${y * -6}px)`;
      });
      hero.addEventListener('pointerleave', () => {
        media.style.transform = '';
      });
    });
  }


  /* WooCommerce owns variation resolution and cart writes. This adapter only
     reflects confirmed form events as V2 state/status; it never calculates
     price, stock, or a variation client-side. */
  const pdpStatus = document.querySelector('[data-sr2-pdp-status]');
  const setPdpStatus = (form, state, message = '') => {
    if (form) form.dataset.sr2VariationState = state;
    if (pdpStatus) {
      pdpStatus.dataset.state = state;
      pdpStatus.textContent = message;
    }
  };

  if (window.jQuery) {
    const $ = window.jQuery;
    $('.variations_form').each(function attachVariationState() {
      const form = this;
      setPdpStatus(form, 'incomplete', 'Select options to see the current piece availability.');
      $(form).on('show_variation', (_event, variation, purchasable) => {
        const nativeId = Number(form.querySelector('input[name="variation_id"]')?.value);
        if (!nativeId || nativeId !== Number(variation?.variation_id)) {
          setPdpStatus(form, 'resolving', 'Checking this selection.');
          return;
        }
        const available = purchasable !== false && variation?.is_in_stock !== false && variation?.is_purchasable !== false;
        setPdpStatus(
          form,
          available ? 'valid' : 'unavailable',
          available ? 'Selection confirmed. Current price and availability are shown above.' : 'This selection is unavailable. Choose another option.'
        );
      });
      $(form).on('hide_variation reset_data', () => {
        setPdpStatus(form, 'incomplete', 'Select options to see the current piece availability.');
      });
      $(form).on('woocommerce_variation_select_change woocommerce_variation_has_changed', () => {
        setPdpStatus(form, 'resolving', 'Checking this selection.');
      });
    });
  }

  document.querySelectorAll('.single_add_to_cart_button, form.cart button[type="submit"]').forEach((button) => {
    const form = button.closest('form.cart');
    if (!form) return;
    const restoreCartButton = () => {
      button.removeAttribute('aria-busy');
      if (button.dataset.sr2OriginalLabel) button.textContent = button.dataset.sr2OriginalLabel;
    };
    form.addEventListener('submit', (event) => {
      if (event.defaultPrevented) return;
      if (button.disabled || button.getAttribute('aria-busy') === 'true') {
        event.preventDefault();
        return;
      }
      if (form.matches('.variations_form') && (!Number(form.querySelector('input[name="variation_id"]')?.value) || button.classList.contains('disabled'))) {
        event.preventDefault();
        setPdpStatus(form, 'incomplete', 'Choose an available size before adding this piece.');
        return;
      }
      button.setAttribute('aria-busy', 'true');
      button.dataset.sr2OriginalLabel = button.textContent;
      button.textContent = 'Adding…';
    });
    window.addEventListener('pageshow', restoreCartButton);
    // WooCommerce emits its cart lifecycle through jQuery when that runtime is
    // present. Keep a native listener as a progressive fallback for a custom
    // cart integration, but never assume one event transport for both cases.
    if (window.jQuery) {
      window.jQuery(document.body).on('added_to_cart wc_fragments_refreshed', restoreCartButton);
    } else {
      document.body.addEventListener('added_to_cart', restoreCartButton);
      document.body.addEventListener('wc_fragments_refreshed', restoreCartButton);
    }
  });

  /* End native commerce adapter. */
})();
