/**
 * Cinematic chapters runtime: Story Thread memory, Prologue panel activation,
 * single-alive card hover engine, Konami → Chapter IV title screen.
 * No innerHTML. Every path degrades to plain links; nothing here gates shopping.
 */
(function () {
  'use strict';

  var STORE_KEY = 'sr2.chapters.seen';
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function readSeen() {
    try {
      var parsed = JSON.parse(window.localStorage.getItem(STORE_KEY) || '[]');
      return Array.isArray(parsed) ? parsed.filter(function (s) { return typeof s === 'string'; }) : [];
    } catch (e) {
      return [];
    }
  }

  function writeSeen(list) {
    try {
      window.localStorage.setItem(STORE_KEY, JSON.stringify(list));
    } catch (e) { /* storage blocked: thread simply doesn't remember */ }
  }

  /* Story Thread: remember visited chapters between visits. */
  function initThread() {
    var thread = document.querySelector('[data-story-thread]');
    if (!thread) { return; }
    var seen = readSeen();

    function paint() {
      thread.querySelectorAll('[data-chapter]').forEach(function (item) {
        if (seen.indexOf(item.getAttribute('data-chapter')) !== -1) {
          item.setAttribute('data-seen', '');
        }
      });
    }

    thread.addEventListener('click', function (event) {
      var item = event.target.closest('[data-chapter]');
      if (!item) { return; }
      var slug = item.getAttribute('data-chapter');
      if (seen.indexOf(slug) === -1) {
        seen = seen.concat(slug);
        writeSeen(seen);
      }
    });
    paint();
  }

  /* Prologue: hover/focus handled by CSS; touch + keyboard get [data-active]. */
  function initPrologue() {
    var panels = Array.prototype.slice.call(document.querySelectorAll('[data-panel]'));
    if (!panels.length) { return; }

    function activate(target) {
      panels.forEach(function (panel) {
        if (panel === target) { panel.setAttribute('data-active', ''); }
        else { panel.removeAttribute('data-active'); }
      });
    }

    if (!finePointer) {
      /* Touch: first tap previews (widens), second tap follows the link. */
      panels.forEach(function (panel) {
        panel.addEventListener('click', function (event) {
          if (!panel.hasAttribute('data-active')) {
            event.preventDefault();
            activate(panel);
          }
        });
      });
      if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting && entry.intersectionRatio > 0.6) { activate(entry.target); }
          });
        }, { threshold: [0.6] });
        panels.forEach(function (panel) { observer.observe(panel); });
      }
    }
  }

  /* Card hover engine: REST → INTENT (100ms) → ALIVE → EXIT. One alive at a time. */
  function initCards() {
    var cards = document.querySelectorAll('[data-alive-card]');
    if (!cards.length || reduced) { return; }
    var INTENT_MS = 100;
    var timer = 0;
    var current = null;

    function setState(card, state) { card.setAttribute('data-state', state); }

    function release(card) {
      window.clearTimeout(timer);
      if (!card) { return; }
      setState(card, 'exit');
      window.setTimeout(function () {
        if (card !== current) { card.removeAttribute('data-state'); }
      }, 400);
      var grid = card.closest('[data-alive-grid]');
      if (grid && card === current) { grid.removeAttribute('data-has-alive'); }
      if (card === current) { current = null; }
    }

    function engage(card) {
      if (current && current !== card) { release(current); }
      window.clearTimeout(timer);
      setState(card, 'intent');
      current = card;
      timer = window.setTimeout(function () {
        if (current !== card) { return; }
        setState(card, 'alive');
        var grid = card.closest('[data-alive-grid]');
        if (grid) { grid.setAttribute('data-has-alive', ''); }
      }, INTENT_MS);
    }

    cards.forEach(function (card) {
      if (finePointer) {
        card.addEventListener('pointerenter', function () { engage(card); });
        card.addEventListener('pointerleave', function () { release(card); });
      }
      card.addEventListener('focusin', function () { engage(card); });
      card.addEventListener('focusout', function () { release(card); });
    });
  }

  /* Konami code, anywhere → Chapter IV title screen (its Press Start link). */
  function initKonami() {
    var code = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    var index = 0;
    document.addEventListener('keydown', function (event) {
      var target = event.target;
      if (target && /^(input|textarea|select)$/i.test(target.tagName || '')) { return; }
      var key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
      index = key === code[index] ? index + 1 : (key === code[0] ? 1 : 0);
      if (index === code.length) {
        index = 0;
        var start = document.querySelector('[data-chapter-link][href*="kids-capsule"], [data-panel][data-verb="play"]');
        if (start && start.href) { window.location.assign(start.href); }
      }
    });
  }

  function init() {
    initThread();
    initPrologue();
    initCards();
    initKonami();
  }

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); }
  else { init(); }
})();
