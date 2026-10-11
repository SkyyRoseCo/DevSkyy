(() => {
  'use strict';
  const house = document.querySelector('[data-house-motion]');
  const toggle = house?.querySelector('[data-house-motion-toggle]');
  if (!house || !toggle) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = reduce.matches || Boolean(navigator.connection?.saveData);
  let visible = true;
  const sync = () => {
    house.dataset.motion = !paused && visible && !document.hidden ? 'playing' : 'paused';
    toggle.textContent = paused ? 'Play atmosphere' : 'Pause atmosphere';
    toggle.setAttribute('aria-pressed', String(paused));
  };
  toggle.hidden = false;
  toggle.addEventListener('click', () => { paused = !paused; sync(); });
  reduce.addEventListener('change', () => { paused = reduce.matches; sync(); });
  document.addEventListener('visibilitychange', sync);
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }).observe(house);
  sync();
})();
