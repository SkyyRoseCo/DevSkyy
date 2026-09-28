/* Homepage collection films and manual Jersey Series reveal. */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  document.querySelectorAll('[data-home-motion]').forEach(function (root) {
    var video = root.querySelector('video');
    var button = root.querySelector('[data-home-motion-toggle]');
    if (!video || !button) return;
    var visible = false;
    var choice = null;
    var failed = false;
    var pending = false;
    var allowed = function () {
      return !reduced.matches && !(connection && connection.saveData);
    };
    var wanted = function () {
      return visible && !document.hidden && !failed && (choice === true || (choice === null && allowed()));
    };
    var update = function () {
      button.textContent = video.paused ? 'Play motion' : 'Pause motion';
      button.setAttribute('aria-label', button.textContent);
    };
    var sync = function () {
      if (!wanted()) {
        video.pause();
        update();
        return;
      }
      if (pending || !video.paused) return;
      if (!video.dataset.loaded) {
        video.querySelectorAll('source[data-src]').forEach(function (source) {
          source.src = source.dataset.src;
        });
        video.dataset.loaded = 'true';
        video.load();
      }
      pending = true;
      var attempt = video.play();
      Promise.resolve(attempt)
        .then(function () {
          pending = false;
          if (!wanted()) video.pause();
          update();
        })
        .catch(function () {
          pending = false;
          root.classList.remove('is-playing');
          update();
        });
    };
    button.hidden = false;
    button.addEventListener('click', function () {
      choice = video.paused;
      visible = true;
      sync();
    });
    video.addEventListener('playing', function () {
      if (!wanted()) {
        video.pause();
        return;
      }
      root.classList.add('is-playing');
      update();
    });
    video.addEventListener('pause', function () {
      root.classList.remove('is-playing');
      update();
    });
    video.addEventListener('error', function () {
      failed = true;
      root.classList.remove('is-playing');
      button.textContent = 'Film unavailable';
      button.disabled = true;
      button.removeAttribute('aria-label');
    });
    document.addEventListener('visibilitychange', sync);
    var preferenceChanged = function () {
      choice = null;
      sync();
    };
    if (reduced.addEventListener) reduced.addEventListener('change', preferenceChanged);
    if (connection && connection.addEventListener) connection.addEventListener('change', preferenceChanged);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(
        function (entries) {
          visible = entries[0].isIntersecting;
          sync();
        },
        { threshold: 0.2 }
      ).observe(root);
    }
    // Without an observer, leave the still visible until explicit playback.
  });
  document.querySelectorAll('[data-jersey-gallery]').forEach(function (root) {
    var rail = root.querySelector('[data-jersey-rail]');
    var slides = rail ? Array.from(rail.children) : [];
    var controls = root.querySelector('[data-jersey-controls]');
    if (!rail || !controls || slides.length < 2) return;
    var previous = controls.querySelector('[data-jersey-prev]');
    var next = controls.querySelector('[data-jersey-next]');
    var position = controls.querySelector('[data-jersey-position]');
    var current = 0;
    var update = function () {
      current = Math.max(0, Math.min(slides.length - 1, Math.round(rail.scrollLeft / rail.clientWidth)));
      position.textContent = current + 1 + ' / ' + slides.length;
      previous.disabled = current === 0;
      next.disabled = current === slides.length - 1;
    };
    var move = function (delta) {
      var index = Math.max(0, Math.min(slides.length - 1, current + delta));
      rail.scrollTo({ left: index * rail.clientWidth, behavior: reduced.matches ? 'auto' : 'smooth' });
    };
    previous.addEventListener('click', function () {
      move(-1);
    });
    next.addEventListener('click', function () {
      move(1);
    });
    rail.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    controls.hidden = false;
    update();
  });
})();
