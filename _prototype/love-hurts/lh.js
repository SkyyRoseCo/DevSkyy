/* Shared helpers for the Love Hurts prototypes. DOM built with createElement only. */
(function () {
  'use strict';

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      var value = attrs[key];
      if (value === null || value === undefined || value === false) return;
      if (key === 'class') node.className = value;
      else if (key === 'text') node.textContent = value;
      else node.setAttribute(key, value === true ? '' : value);
    });
    (children || []).forEach(function (child) {
      if (child === null || child === undefined) return;
      node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    });
    return node;
  }

  function price(p) {
    return '$' + p.price;
  }

  function sizes(p) {
    var s = p.sizes || [];
    if (s.length === 1) return s[0];
    return s[0] + '–' + s[s.length - 1];
  }

  /* Registry descriptions carry internal SKU cross-references; keep them off the page. */
  function copy(p) {
    return p.description
      .replace(/\s*Mirror (black|white) colorway available as lh-\d+\.?/i, '')
      .replace(/^The mirror of lh-\d+ in (\w+)\./i, 'The mirror of the black pair, in $1.')
      .trim();
  }

  function alt(p, role) {
    var views = {
      front: 'worn, front view',
      back: 'back view',
      back_packshot: 'photographed flat, back view',
    };
    return p.name + ' — ' + (views[role] || role);
  }

  function img(p, role, extra) {
    var attrs = Object.assign(
      { src: p.images[role], alt: alt(p, role), loading: 'lazy', decoding: 'async' },
      extra || {}
    );
    return el('img', attrs);
  }

  /* The item for sale, cropped from the front image by its focus box.
     The wrapper takes the box's aspect ratio; the image is scaled and offset inside it. */
  function focus(p, extra) {
    var f = p.focus;
    var ratio = (f.w * f.width) / (f.h * f.height);
    var image = el('img', {
      src: p.images.front,
      alt: p.name + ' — the piece, close up',
      loading: 'lazy',
      decoding: 'async',
      style: 'width:' + 100 / f.w + '%;left:' + (-100 * f.x) / f.w + '%;top:' + (-100 * f.y) / f.h + '%',
    });
    /* Never upscale past 1.75x the crop's native pixels, never taller than --focus-vh. */
    var cap = Math.round(f.w * f.width * 1.75);
    var size =
      'aspect-ratio:' +
      ratio.toFixed(4) +
      ';width:min(100%, ' +
      cap +
      'px, calc(var(--focus-vh, 86svh) * ' +
      ratio.toFixed(4) +
      '))';
    return el('div', Object.assign({ class: 'lh-focus', style: size }, extra || {}), [image]);
  }

  /* The full styled frame, kept small as context beside the product crop. */
  function context(p) {
    return el('div', { class: 'lh-context' }, [
      el('img', { src: p.images.front, alt: p.name + ' — worn, full look', loading: 'lazy' }),
      el('span', { class: 'lh-caps lh-muted' }, ['In the room']),
    ]);
  }

  function viewLink(p) {
    return el('a', { class: 'lh-view', href: '#', 'aria-label': 'View ' + p.name + ', ' + price(p) }, [
      'View the piece',
    ]);
  }

  function reveal(root) {
    var nodes = (root || document).querySelectorAll('.lh-reveal');
    if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      nodes.forEach(function (n) {
        n.classList.add('is-in');
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('is-in');
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: '0px 0px -12% 0px' }
    );
    nodes.forEach(function (n) {
      io.observe(n);
    });
  }

  function protoNav(current) {
    var pages = [
      ['index.html', 'All five'],
      ['01-rose-under-glass.html', '01 Rose under glass'],
      ['02-lookbook.html', '02 Lookbook'],
      ['03-front-and-back.html', '03 Front & back'],
      ['04-makers-table.html', "04 Maker's table"],
      ['05-reel.html', '05 Reel'],
    ];
    return el(
      'nav',
      { class: 'lh-proto-nav', 'aria-label': 'Prototype variants' },
      pages.map(function (p) {
        return el('a', { href: p[0], 'aria-current': p[0] === current ? 'page' : null }, [p[1]]);
      })
    );
  }

  window.LHKit = {
    el: el,
    price: price,
    sizes: sizes,
    copy: copy,
    alt: alt,
    img: img,
    focus: focus,
    context: context,
    viewLink: viewLink,
    reveal: reveal,
    protoNav: protoNav,
  };
})();
