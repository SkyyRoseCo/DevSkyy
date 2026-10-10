/** Progressive interview playback. The original source link works without JS. */
(function () {
  'use strict';
  function videoId(href) {
    try {
      var url = new URL(href, window.location.href);
      if (url.protocol !== 'https:') return null;
      var id = null;
      if (url.hostname === 'youtu.be') id = url.pathname.slice(1);
      if (url.hostname === 'www.youtube.com' || url.hostname === 'youtube.com') {
        if (url.pathname === '/watch') id = url.searchParams.get('v');
      }
      return id && /^[A-Za-z0-9_-]{11}$/.test(id) ? id : null;
    } catch (error) { return null; }
  }
  document.querySelectorAll('.sr2-about-archive .sr2-about-film').forEach(function (film) {
    var link = film.querySelector('a.sr2-about-play, .sr2-about-play a');
    if (!link || !videoId(link.href)) return;
    var player = null;
    var poster = film.querySelector('.wp-block-image');
    var posterImage = poster && poster.querySelector('img');
    var posterSlot = null;
    if (posterImage) {
      posterSlot = document.createElement('div');
      posterSlot.className = 'sr2-about-film-slot';
      posterImage.parentNode.insertBefore(posterSlot, posterImage);
      posterSlot.appendChild(posterImage);
    }
    link.addEventListener('click', function (event) {
      // Preserve deliberate new-tab/window gestures and invalid destination links.
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      var id = videoId(link.href);
      if (!id) return;
      if (player) {
        event.preventDefault();
        player.focus();
        return;
      }
      var frame = document.createElement('iframe');
      var box = document.createElement('div');
      var status = document.createElement('p');
      var title = film.querySelector('h2, h3');
      box.className = 'sr2-about-player';
      status.className = 'sr2-about-player-status';
      status.setAttribute('role', 'status');
      status.textContent = 'Loading interview. The original source link remains available.';
      frame.title = title ? title.textContent.trim() : 'SkyyRose interview';
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.tabIndex = 0;
      // No provider connections occur until this explicit user action.
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id + '?rel=0&autoplay=1';
      var timer = window.setTimeout(function () {
        status.textContent = 'If the player has not appeared, watch using the original source link.';
      }, 12000);
      frame.addEventListener('load', function () {
        window.clearTimeout(timer);
        // An iframe load is not proof of successful cross-origin playback.
        status.textContent = 'Player opened. If playback is unavailable, use the original source link.';
      });
      frame.addEventListener('error', function () {
        window.clearTimeout(timer);
        status.textContent = 'The player could not load. Use the original source link to watch the interview.';
      });
      box.appendChild(frame);
      if (posterSlot) {
        posterSlot.appendChild(box);
      } else {
        film.appendChild(box);
      }
      film.appendChild(status);
      player = frame;
      event.preventDefault();
      frame.focus();
    });
  });
}());
