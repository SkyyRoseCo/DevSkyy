/** One lazy, self-hosted Three core dependency; no mascot DOM or model loading. */
(function () {
  'use strict';
  if (window.skyyRoseThreeCore) return;
  const config = window.SKYYROSE_THREE_CORE || {};
  let dependency;
  function load(callback) {
    if (!dependency) {
      dependency = Promise.resolve().then(() => {
        const base = new URL(config.moduleBase, location.href);
        if (typeof config.moduleBase !== 'string' || base.origin !== location.origin || !/^https?:$/.test(base.protocol) || !base.pathname.endsWith('/assets/js/lib/three-r170/') || base.search || base.hash) {
          throw new Error('Three core must use the approved local module directory');
        }
        return new Promise((resolve, reject) => {
          const timer = setTimeout(() => reject(new Error('Three core timed out')), 8000);
          import(base.href + 'three.module.min.js').then(
            core => { clearTimeout(timer); resolve(core); },
            error => { clearTimeout(timer); reject(error); }
          );
        });
      }).then(core => {
        window.THREE = core;
        document.dispatchEvent(new Event('three-ready'));
        return [core];
      });
    }
    const result = dependency.then(loaded => {
      if (callback) callback(loaded[0]);
      return loaded;
    });
    result.catch(() => {});
    return result;
  }
  window.skyyRoseThreeCore = { load };
  if (typeof window.skyyRoseLoadThree !== 'function') window.skyyRoseLoadThree = load;
  window.addEventListener('skyyrose:request-three', () => { load(); });
})();
