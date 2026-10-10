/** Core collection scene → native commerce arrival. No scroll or history ownership. */
(function () {
	'use strict';
	var section = document.querySelector('.sr2-collection-world [data-scene-handoff]');
	if (!section || section.dataset.handoffInitialized) return;
	section.dataset.handoffInitialized = 'true';
	var preference = window.matchMedia('(prefers-reduced-motion: reduce)');
	var connection = navigator.connection;
	var observer = null;
	var animations = [];
	var arrived = false;
	var visible = false;
	var suspended = false;

	function cancel() {
		animations.forEach(function (animation) { animation.cancel(); });
		animations = [];
	}

	function disconnect() {
		if (observer) observer.disconnect();
		observer = null;
		cancel();
	}

	function staticMode() {
		return preference.matches || (connection && connection.saveData) || !window.IntersectionObserver;
	}

	function enter() {
		section.dataset.handoffState = 'active';
		if (arrived) return;
		arrived = true;
		var style = getComputedStyle(section);
		var time = style.getPropertyValue('--sr2-handoff-duration').trim();
		var duration = parseFloat(time) * (time.endsWith('ms') ? 1 : 1000);
		var easing = style.getPropertyValue('--sr2-handoff-easing').trim();
		var distance = style.getPropertyValue('--sr2-handoff-distance').trim();
		var staggerToken = style.getPropertyValue('--sr2-handoff-stagger').trim();
		var stagger = parseFloat(staggerToken) * (staggerToken.endsWith('ms') ? 1 : 1000);
		if (!Number.isFinite(stagger)) stagger = 0;
		if (!Number.isFinite(duration) || duration <= 1 || !distance || !easing) return;
		var targets = section.querySelectorAll('.sr2-world-section-head, .sr2-world-products');
		targets.forEach(function (target, index) {
			if (!target.animate) return;
			try {
				animations.push(target.animate([
					{ opacity: 0.84, transform: 'translateY(' + distance + ')' },
					{ opacity: 1, transform: 'translateY(0)' }
				], { duration: duration, delay: index * stagger, easing: easing, fill: 'backwards' }));
			} catch (error) { /* Unsupported token values retain the fully visible base. */ }
		});
		if (!animations.length) return;
		section.dataset.handoffState = 'enter';
		Promise.all(animations.map(function (animation) {
			return animation.finished.catch(function () {});
		})).then(function () {
			if (!suspended && !staticMode()) section.dataset.handoffState = visible ? 'active' : 'exit';
		});
	}

	function connect() {
		disconnect();
		if (suspended) return;
		if (staticMode()) {
			arrived = true;
			section.dataset.handoffState = 'static';
			return;
		}
		section.dataset.handoffState = 'idle';
		observer = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				visible = entry.isIntersecting;
				if (visible) enter();
				else {
					cancel();
					section.dataset.handoffState = arrived ? 'exit' : 'idle';
				}
			});
		}, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
		observer.observe(section);
	}

	window.addEventListener('pagehide', function () {
		suspended = true;
		disconnect();
		section.dataset.handoffState = 'suspended';
	});
	window.addEventListener('pageshow', function (event) {
		if (!event.persisted) return;
		suspended = false;
		connect();
	});
	if (preference.addEventListener) preference.addEventListener('change', connect);
	if (connection && connection.addEventListener) connection.addEventListener('change', connect);
	connect();
})();
