(() => {
  'use strict';

  /* Kids Capsule Royal Procession: native scrolling remains the transport;
     this controller only synchronizes controls and chapter state. */

  const section = document.querySelector('[data-house-royal-procession]');
  if (!section) return;

  const viewport = section.querySelector('[data-procession-viewport]');
  const chapters = Array.from(section.querySelectorAll('[data-procession-chapter]'));
  const previous = section.querySelector('[data-procession-previous]');
  const next = section.querySelector('[data-procession-next]');
  const current = section.querySelector('[data-procession-current]');
  const label = section.querySelector('[data-procession-label]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const verticalLayout = window.matchMedia('(max-width: 40em)');
  const saveData = Boolean(navigator.connection?.saveData);
  const controller = new AbortController();
  const { signal } = controller;
  const chapterLabels = ['The Invitation', 'The Guardians', 'The Heir'];
  let activeIndex = 0;
  let observer;

  if (!viewport || chapters.length !== 3) return;

  const setActive = index => {
    activeIndex = Math.max(0, Math.min(chapters.length - 1, index));
    section.dataset.activeChapter = chapters[activeIndex].dataset.processionChapter;
    chapters.forEach((chapter, chapterIndex) => {
      chapter.toggleAttribute('data-active', chapterIndex === activeIndex);
      chapter.setAttribute('aria-current', chapterIndex === activeIndex ? 'step' : 'false');
    });
    if (current) current.textContent = String(activeIndex + 1);
    if (label) label.textContent = chapterLabels[activeIndex];
    if (previous) previous.disabled = activeIndex === 0;
    if (next) next.disabled = activeIndex === chapters.length - 1;
  };

  const moveTo = index => {
    const target = chapters[Math.max(0, Math.min(chapters.length - 1, index))];
    if (!target) return;
    const behavior = reducedMotion.matches || saveData ? 'auto' : 'smooth';
    if (verticalLayout.matches) {
      target.scrollIntoView({ behavior, block: 'start' });
    } else {
      viewport.scrollTo({ left: target.offsetLeft - viewport.offsetLeft, behavior });
    }
    setActive(chapters.indexOf(target));
  };

  const handleNavigationKeys = event => {
    if (event.target !== viewport) {
      return;
    }

    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
      event.preventDefault();
      moveTo(activeIndex - 1);
      return;
    }

    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
      event.preventDefault();
      moveTo(activeIndex + 1);
    }
  };

  const connectObserver = () => {
    observer?.disconnect();
    if (!('IntersectionObserver' in window)) return;
    observer = new IntersectionObserver(
      entries => {
        const visible = entries
          .filter(entry => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(chapters.indexOf(visible.target));
      },
      {
        root: verticalLayout.matches ? null : viewport,
        threshold: [0.42, 0.62, 0.82],
      }
    );
    chapters.forEach(chapter => observer.observe(chapter));
  };

  previous?.addEventListener('click', () => moveTo(activeIndex - 1), { signal });
  next?.addEventListener('click', () => moveTo(activeIndex + 1), { signal });
  viewport.addEventListener('keydown', handleNavigationKeys, { signal });
  verticalLayout.addEventListener?.('change', connectObserver, { signal });
  reducedMotion.addEventListener?.(
    'change',
    () => (section.dataset.motion = reducedMotion.matches || saveData ? 'reduced' : 'full'),
    { signal }
  );
  document.addEventListener(
    'visibilitychange',
    () => {
      if (!document.hidden) setActive(activeIndex);
    },
    { signal }
  );
  section.querySelectorAll('img').forEach(image => {
    image.addEventListener(
      'error',
      () =>
        image
          .closest('.sr-kids-procession__scene, .sr-kids-procession__guardian, .sr-kids-procession__proof-media')
          ?.classList.add('is-media-missing'),
      { signal, once: true }
    );
  });
  window.addEventListener(
    'pagehide',
    () => {
      observer?.disconnect();
      controller.abort();
    },
    { signal, once: true }
  );

  section.dataset.enhanced = 'true';
  section.dataset.motion = reducedMotion.matches || saveData ? 'reduced' : 'full';
  setActive(0);
  connectObserver();
})();
