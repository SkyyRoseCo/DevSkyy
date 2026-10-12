/* Unfiltered Shop cinema bands: rail controls, film playback, and scroll phases.
 * Progressive enhancement only: without this file every band, card and link is visible
 * and the rails remain native horizontal snap scrollers. */
(function () {
  'use strict';

  var root = document.querySelector('[data-sr2bv2]');
  if (!root || !('querySelectorAll' in root)) return;

  var media = function (query) {
    return window.matchMedia ? window.matchMedia(query) : { matches: false };
  };
  var reduced = media('(prefers-reduced-motion: reduce)');
  var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection || null;
  var hasObserver = 'IntersectionObserver' in window;
  var supportsTimeline = Boolean(window.CSS && CSS.supports && CSS.supports('animation-timeline: view()'));

  var motionAllowed = function () {
    return !reduced.matches && !(connection && connection.saveData);
  };
  var listen = function (target, type, handler) {
    if (target && target.addEventListener) target.addEventListener(type, handler);
  };
  var pad = function (value) {
    return (value < 10 ? '0' : '') + value;
  };

  function initRail(band) {
    var rail = band.querySelector('[data-sr2bv2-rail]');
    var controls = band.querySelector('[data-sr2bv2-controls]');
    if (!rail || !controls) return;
    var cards = Array.prototype.filter.call(rail.children, function (child) {
      return child.tagName === 'LI';
    });
    var previous = controls.querySelector('[data-sr2bv2-prev]');
    var next = controls.querySelector('[data-sr2bv2-next]');
    var position = controls.querySelector('[data-sr2bv2-position]');
    if (!cards.length || !previous || !next || !position) return;

    var visible = new Set();
    var current = 0;
    var frame = 0;

    var setDisabled = function (button, disabled) {
      button.setAttribute('aria-disabled', disabled ? 'true' : 'false');
    };
    var scrollable = function () {
      return rail.scrollWidth - rail.clientWidth > 1;
    };
    var render = function () {
      frame = 0;
      var indexes = Array.from(visible).sort(function (a, b) {
        return a - b;
      });
      var canScroll = scrollable();
      if (indexes.length) current = indexes[0];
      // Scroll position covers the frame before the first observer report.
      var left = rail.scrollLeft;
      var atStart = !canScroll || left <= 1 || visible.has(0);
      // The rail's trailing room lets the last piece reach the snap slot, so "end" means the
      // last piece is the focused one (or the rail cannot scroll any further).
      var atEnd = !canScroll || left + rail.clientWidth >= rail.scrollWidth - 1 || current === cards.length - 1;
      // Focused piece for the no-scroll-timeline path (CSS reads it only under data-sr2bv2-observe).
      cards.forEach(function (card, index) {
        if (index === current) card.setAttribute('data-sr2bv2-focus', 'true');
        else if (card.hasAttribute('data-sr2bv2-focus')) card.removeAttribute('data-sr2bv2-focus');
      });
      setDisabled(previous, atStart);
      setDisabled(next, atEnd);
      var text = pad(current + 1) + ' / ' + pad(cards.length);
      if (position.textContent !== text) position.textContent = text;
      // The signature moment: once the final piece has snapped in, the film dims and hands off.
      band.setAttribute('data-sr2bv2-complete', canScroll && atEnd ? 'true' : 'false');
    };
    var schedule = function () {
      if (!frame) frame = window.requestAnimationFrame(render);
    };
    var focusCard = function (index) {
      var link = cards[index].querySelector('.sr2-c-editorial-card__title a') || cards[index].querySelector('a[href]');
      if (link) link.focus({ preventScroll: true });
    };
    var slotLeft = function (index) {
      return cards[index].offsetLeft - cards[0].offsetLeft;
    };
    var go = function (index, moveFocus) {
      var target = Math.max(0, Math.min(cards.length - 1, index));
      rail.scrollTo({
        left: slotLeft(target),
        behavior: reduced.matches ? 'auto' : 'smooth',
      });
      if (moveFocus) focusCard(target);
    };
    // Keyboard focus that lands in a piece (Tab, Shift+Tab, a screen reader) brings that piece
    // into the snap slot, on the same path as Prev/Next. A pointer press already places the
    // piece where the user wants it, so focus that follows a press is left alone.
    var pointerActive = false;
    var pointerTimer = 0;
    listen(rail, 'pointerdown', function () {
      pointerActive = true;
      window.clearTimeout(pointerTimer);
    });
    var pointerDone = function () {
      window.clearTimeout(pointerTimer);
      pointerTimer = window.setTimeout(function () {
        pointerActive = false;
      }, 400);
    };
    listen(rail, 'pointerup', pointerDone);
    listen(rail, 'pointercancel', pointerDone);
    listen(rail, 'focusin', function (event) {
      if (pointerActive) return;
      var index = cards.findIndex(function (card) {
        return card.contains(event.target);
      });
      if (index === -1) return;
      // Next frame: WebKit runs its own focus scroll after focusin, which cancels a smooth
      // scroll started inside the handler.
      window.requestAnimationFrame(function () {
        var left = Math.min(slotLeft(index), rail.scrollWidth - rail.clientWidth);
        if (cards[index].contains(document.activeElement) && Math.abs(rail.scrollLeft - left) > 1) go(index, false);
      });
    });

    listen(previous, 'click', function () {
      if (previous.getAttribute('aria-disabled') !== 'true') go(current - 1, false);
    });
    listen(next, 'click', function () {
      if (next.getAttribute('aria-disabled') !== 'true') go(current + 1, false);
    });
    listen(rail, 'keydown', function (event) {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      var from = cards.findIndex(function (card) {
        return card.contains(document.activeElement);
      });
      var base = from === -1 ? current : from;
      var map = { ArrowRight: base + 1, ArrowLeft: base - 1, Home: 0, End: cards.length - 1 };
      if (!(event.key in map)) return;
      event.preventDefault();
      go(map[event.key], true);
    });

    if (hasObserver) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            var index = cards.indexOf(entry.target);
            if (entry.intersectionRatio >= 0.9) visible.add(index);
            else visible.delete(index);
          });
          schedule();
        },
        { root: rail, threshold: [0, 0.9, 1] }
      );
      cards.forEach(function (card) {
        observer.observe(card);
      });
    } else {
      // Without an observer, derive the first piece from scroll position, once per frame.
      var fallback = function () {
        visible.clear();
        var left = rail.scrollLeft;
        var width = rail.clientWidth;
        cards.forEach(function (card, index) {
          var start = card.offsetLeft - cards[0].offsetLeft;
          if (start >= left - 1 && start + card.offsetWidth <= left + width + 1) visible.add(index);
        });
        render();
      };
      rail.addEventListener(
        'scroll',
        function () {
          if (!frame) frame = window.requestAnimationFrame(fallback);
        },
        { passive: true }
      );
      fallback();
    }
    if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(rail);
    controls.hidden = false;
    schedule();
  }

  function initFilm(band) {
    var poster = band.querySelector('[data-sr2bv2-poster]');
    if (poster) {
      var posterFailed = function () {
        // A poster that fails to decode falls back to the designed type-led header.
        band.setAttribute('data-poster', 'failed');
        band.setAttribute('data-film', 'type');
      };
      if (poster.complete && poster.naturalWidth === 0 && poster.currentSrc) posterFailed();
      listen(poster, 'error', posterFailed);
    }

    var video = band.querySelector('[data-sr2bv2-video]');
    var button = band.querySelector('[data-sr2bv2-motion]');
    if (!video || !button || typeof video.play !== 'function') return;

    var inView = false;
    var choice = null;
    var failed = false;
    var pending = false;

    // Motion never runs without its visible pause control (WCAG 2.2.2).
    var wanted = function () {
      return (
        inView && !document.hidden && !failed && motionAllowed() && choice !== false && !button.closest('[hidden]')
      );
    };
    var label = function () {
      if (failed) {
        button.textContent = button.getAttribute('data-label-failed') || button.textContent;
        button.disabled = true;
        button.setAttribute('aria-pressed', 'false');
        return;
      }
      var playing = !video.paused;
      button.textContent = button.getAttribute(playing ? 'data-label-pause' : 'data-label-play') || button.textContent;
      button.setAttribute('aria-pressed', playing ? 'true' : 'false');
    };
    var sync = function () {
      button.hidden = !motionAllowed() && !failed;
      if (!wanted()) {
        if (!video.paused) video.pause();
        label();
        return;
      }
      if (pending || !video.paused) return;
      if (!video.getAttribute('data-sr2bv2-loaded')) {
        Array.prototype.forEach.call(video.querySelectorAll('source[data-src]'), function (source) {
          source.src = source.getAttribute('data-src');
        });
        video.setAttribute('data-sr2bv2-loaded', 'true');
        video.load();
      }
      pending = true;
      Promise.resolve(video.play())
        .then(function () {
          pending = false;
          if (!wanted()) video.pause();
          label();
        })
        .catch(function () {
          // Autoplay rejected: the poster remains the film; the user can still press play.
          pending = false;
          band.classList.remove('is-playing');
          choice = false;
          label();
        });
    };

    listen(button, 'click', function () {
      choice = video.paused;
      if (choice) inView = true;
      sync();
    });
    listen(video, 'playing', function () {
      if (!wanted()) {
        video.pause();
        return;
      }
      band.classList.add('is-playing');
      label();
    });
    listen(video, 'pause', function () {
      band.classList.remove('is-playing');
      label();
    });
    listen(video, 'error', function () {
      failed = true;
      band.classList.remove('is-playing');
      label();
    });
    Array.prototype.forEach.call(video.querySelectorAll('source'), function (source, index, all) {
      // Only the last candidate's failure means no source can play. Resource selection also
      // fires error at a source that has no src yet (data-src only), which is not a failure.
      if (index === all.length - 1) {
        listen(source, 'error', function () {
          if (!source.getAttribute('src')) return;
          failed = true;
          band.classList.remove('is-playing');
          label();
        });
      }
    });
    listen(document, 'visibilitychange', sync);
    var preferenceChanged = function () {
      choice = null;
      sync();
    };
    listen(reduced, 'change', preferenceChanged);
    listen(connection, 'change', preferenceChanged);

    if (hasObserver) {
      // Bands are taller than the viewport, so measure coverage of the viewport's middle band,
      // not the band's own intersection ratio (which can never reach a fixed threshold).
      new IntersectionObserver(
        function (entries) {
          inView = entries[entries.length - 1].isIntersecting;
          sync();
        },
        { rootMargin: '-35% 0px -35% 0px', threshold: 0 }
      ).observe(band);
    }
    // Without an observer the poster stays; playback starts only from the toggle.
    label();
    button.hidden = !motionAllowed();
  }

  function initPhases(bands) {
    if (supportsTimeline || !hasObserver) return;
    root.setAttribute('data-sr2bv2-observe', 'true');
    var steps = [];
    for (var step = 0; step <= 20; step += 1) steps.push(step / 20);
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var rect = entry.boundingClientRect;
          var height = entry.rootBounds ? entry.rootBounds.height : window.innerHeight;
          var phase = 'active';
          if (!entry.isIntersecting) phase = rect.top > 0 ? 'before' : 'after';
          else if (rect.top > height * 0.35) phase = 'enter';
          else if (rect.bottom < height * 0.7) phase = 'exit';
          entry.target.setAttribute('data-sr2bv2-phase', phase);
        });
      },
      { threshold: steps }
    );
    bands.forEach(function (band) {
      observer.observe(band);
    });
  }

  var bands = Array.prototype.slice.call(root.querySelectorAll('[data-sr2bv2-band]'));
  bands.forEach(function (band) {
    try {
      initFilm(band);
      initRail(band);
    } catch (error) {
      // One band failing must not strand the others; its native rail stays usable.
      band.removeAttribute('data-sr2bv2-complete');
    }
  });
  initPhases(bands);
  root.setAttribute('data-sr2bv2-ready', 'true');
})();
