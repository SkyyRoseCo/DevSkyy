/**
 * SkyyRose Brand Mascot — Skyy Living Character
 *
 * State machine: dormant → walking-in → greeting → idle ↔ speaking → exiting
 *
 * Design rules (binding — see tasks/mascot-design-rulebook.md):
 * - NO pop-in: she always WALKS in (animated entrance), never materializes.
 *   First entrance of a session fires FIRST_ENTRY_DELAY_MS after load —
 *   host-greets-arrival semantics (founder directive 2026-07-08; idle-only
 *   gating meant actively-browsing visitors never saw her). Re-entries
 *   only after a randomized 10–30s idle window, reset by activity.
 * - Hard cap of MAX_PROACTIVE_APPEARANCES proactive appearances per session.
 * - A dismissal (minimize/ESC) is remembered for the rest of the session —
 *   Skyy never walks on again unsolicited after that; the recall pill stays
 *   available for the visitor to bring her back manually.
 * - The same scripted line never resurfaces twice in one session.
 * - Motion for the character image is opt-in via CSS
 *   (`prefers-reduced-motion: no-preference` in mascot.css/skyy-walk.css) —
 *   `prefersReducedMotion` below only affects JS-side *timing* (skipping
 *   artificial delays before showing already-final states), not whether
 *   CSS keyframes run.
 * - The minimize button (always visible + keyboard-reachable once idle or
 *   speaking) is the SC 2.2.2 pause/stop control for the looping idle
 *   breathing animation.
 * - Routine speech uses the non-modal speech bubble (role="status"). The
 *   "Ask Skyy" free-text lookup is the one deliberate, user-initiated panel
 *   interaction, and uses a native <dialog> + showModal() with focus
 *   restore (SC 2.1.2) instead of hijacking the bubble.
 *
 * Features:
 * - Contextual speech bubbles with typewriter text
 * - Choice chips drive conversation trees
 * - Tier 1 guide brain: matches free text against data/site-guide.json
 *   intents (deterministic keyword match, no external lib, no network call)
 * - Tier 2 (optional, Customizer-gated): falls back to the existing AJAX
 *   seam when the Tier 1 matcher finds nothing
 * - IntersectionObserver reacts to product grids entering view
 * - Product hover triggers excited reaction
 * - Minimize (walk off) + recall pill
 * - Keyboard accessible (Escape to dismiss/minimize)
 * - Respects prefers-reduced-motion
 *
 * @package SkyyRose_Flagship
 * @since   4.0.0
 */
(function () {
	'use strict';

	// -------------------------------------------------------------------------
	// Constants
	// -------------------------------------------------------------------------

	var IDLE_TRIGGER_MIN_MS      = 10000;
	var IDLE_TRIGGER_MAX_MS      = 30000;
	var ACTIVITY_THROTTLE_MS     = 250;
	/* First entrance of a session fires this long after load REGARDLESS of
	 * activity — she is the site host and greets arrivals. Only re-entries
	 * use the idle-trigger window above (an actively scrolling visitor never
	 * accumulates 10-30s of stillness, so idle-only gating means engaged
	 * visitors never meet her — the exact bug shipped in v1.9.2). */
	var FIRST_ENTRY_DELAY_MS     = 4500;
	var TYPEWRITER_SPEED         = 28;
	var BUBBLE_AUTO_HIDE         = 8000;
	var MAX_PROACTIVE_APPEARANCES = 3;

	var SESSION_KEY_GREETED   = 'skyy_greeted';
	var SESSION_KEY_DISMISSED = 'skyy_dismissed';
	var SESSION_KEY_APPEARANCES = 'skyy_appearances';
	var SESSION_KEY_SHOWN     = 'skyy_shown_prompts';

	// -------------------------------------------------------------------------
	// DOM References
	// -------------------------------------------------------------------------

	var mascotEl    = document.getElementById('skyyrose-mascot');
	if (!mascotEl) return;

	var triggerBtn   = document.getElementById('skyyrose-mascot-trigger');
	var minimizeBtn  = document.getElementById('skyyrose-mascot-minimize');
	var recallBtn    = document.getElementById('skyyrose-mascot-recall');
	var bubble       = document.getElementById('skyy-bubble');
	var bubbleText   = document.getElementById('skyy-bubble-text');
	var chipsEl      = document.getElementById('skyy-chips');
	var askTrigger   = document.getElementById('skyy-ask-trigger');
	var askDialog    = document.getElementById('skyy-ask-dialog');
	var askForm      = document.getElementById('skyy-ask-form');
	var askInput     = document.getElementById('skyy-ask-input');
	var askCancelBtn = document.getElementById('skyy-ask-cancel');

	if (!triggerBtn || !minimizeBtn || !recallBtn || !bubble || !bubbleText || !chipsEl) return;

	var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	var context = mascotEl.getAttribute('data-context') || 'default';

	var guideData = ( window.SKYY_GUIDE_DATA && window.SKYY_GUIDE_DATA.intents ) ? window.SKYY_GUIDE_DATA : { pages: {}, intents: [] };
	var guidePromise = null;
	var mascotConfig = window.SKYY_MASCOT_CONFIG || { pageTip: '', llmEnabled: false };

	// State: dormant | walking-in | greeting | idle | speaking | exiting
	var state = 'dormant';

	// Bridge to skyy-3d.js: every state transition (and gesture moment) is
	// broadcast as a `skyy:*` CustomEvent so the 3D loader can switch
	// animation clips. skyy-3d.js listens; nothing else needs these.
	function emitSkyy(name) {
		document.dispatchEvent(new CustomEvent('skyy:' + name));
	}

	// Pending greeting delay (wave-then-speak). Tracked so any user action
	// inside the gap — manual trigger, chip advance, minimize, ESC — cancels
	// the deferred greeting instead of letting it clobber the new state.
	var greetTimer = null;

	function clearGreetTimer() {
		if (greetTimer !== null) {
			clearTimeout(greetTimer);
			greetTimer = null;
		}
	}

	var typewriterTimer  = null;
	var autoDismissTimer = null;
	var idleTimer        = null;
	var lastActivityReset = 0;
	var askDialogOpener   = null;
	var pendingQuestion   = null;

	// -------------------------------------------------------------------------
	// Session Memory — appearances, dismissal, shown-prompt dedupe
	// -------------------------------------------------------------------------

	function getShownPrompts() {
		try {
			var raw = sessionStorage.getItem(SESSION_KEY_SHOWN);
			var parsed = raw ? JSON.parse(raw) : [];
			return Array.isArray(parsed) ? parsed : [];
		} catch (e) {
			return [];
		}
	}

	function markPromptShown(id) {
		if (!id) return;
		var shown = getShownPrompts();
		if (shown.indexOf(id) === -1) {
			shown.push(id);
			try {
				sessionStorage.setItem(SESSION_KEY_SHOWN, JSON.stringify(shown));
			} catch (e) { /* sessionStorage unavailable — degrade silently */ }
		}
	}

	function wasPromptShown(id) {
		return getShownPrompts().indexOf(id) !== -1;
	}

	function getAppearanceCount() {
		var raw = sessionStorage.getItem(SESSION_KEY_APPEARANCES);
		var n = raw ? parseInt(raw, 10) : 0;
		return isNaN(n) ? 0 : n;
	}

	function recordProactiveAppearance() {
		try {
			sessionStorage.setItem(SESSION_KEY_APPEARANCES, String(getAppearanceCount() + 1));
		} catch (e) { /* degrade silently */ }
	}

	function proactiveAppearancesExhausted() {
		return getAppearanceCount() >= MAX_PROACTIVE_APPEARANCES;
	}

	function isDismissedThisSession() {
		return sessionStorage.getItem(SESSION_KEY_DISMISSED) === '1';
	}

	function markDismissed() {
		try {
			sessionStorage.setItem(SESSION_KEY_DISMISSED, '1');
		} catch (e) { /* degrade silently */ }
	}

	// -------------------------------------------------------------------------
	// Conversation Scripts
	// -------------------------------------------------------------------------

	var SCRIPTS = {
		homepage: {
			greeting: {
				text: 'Hey! I’m Skyy 👋 Welcome to SkyyRose.',
				chips: [
					{ id: 'new_drops', label: 'What’s new?',    next: 'new_drops' },
					{ id: 'preorder',  label: 'Pre-order drops',     next: 'preorder'  },
					{ id: 'story',     label: 'Our story',           next: 'story'     }
				]
			},
			new_drops: {
				text: 'The Black Rose and Love Hurts collections are live.',
				chips: [
					{ id: 'shop', label: 'Shop now →', action: '/shop/', next: null },
					{ id: 'world', label: 'Enter the world', action: '/collections-world/', next: null }
				]
			},
			preorder: {
				text: 'Most of the collection is pre-order — made for you, no overstock. 🌹',
				chips: [{ id: 'preorder_page', label: 'See pre-orders', action: '/pre-order/', next: null }]
			},
			story: {
				text: 'SkyyRose was born in Oakland. Corey Foster built this from the concrete up. Real luxury, real roots.',
				chips: [{ id: 'about', label: 'Read our story', action: '/about/', next: null }]
			}
		},
		'black-rose': {
			greeting: {
				text: 'Oakland in your DNA? 🖤 Black Rose was made for the ones who built something from nothing.',
				chips: [
					{ id: 'jerseys', label: 'Show me the jerseys',  next: 'jerseys'                            },
					{ id: 'br_shop', label: 'Browse collection',    action: '/collections/black-rose/', next: null }
				]
			},
			jerseys: {
				text: 'SF inspired, Last Oakland, The Bay, The Rose — each its own story.',
				chips: [{ id: 'br_shop', label: 'Browse →', action: '/collections/black-rose/', next: null }]
			}
		},
		'love-hurts': {
			greeting: {
				text: 'Love Hurts is for the ones who feel everything deeply. ❤️',
				chips: [
					{ id: 'lh_fannie', label: 'What’s The Fannie?', next: 'fannie'                              },
					{ id: 'lh_browse', label: 'Browse collection',       action: '/collections/love-hurts/', next: null }
				]
			},
			fannie: {
				text: 'The Fannie is a statement piece — small, bold, SkyyRose. Love Hurts edition. 🌹',
				chips: [{ id: 'lh_shop', label: 'See it →', action: '/collections/love-hurts/', next: null }]
			}
		},
		signature: {
			greeting: {
				text: 'SF from the soul. 🌉 The Signature collection is Golden Gate, fog, and Bay Area energy.',
				chips: [
					{ id: 'sg_bridge', label: 'The Bay Bridge drops?', next: 'bridge'                               },
					{ id: 'sg_browse', label: 'Browse collection',      action: '/collections/signature/', next: null }
				]
			},
			bridge: {
				text: 'Bay Bridge Shorts + Shirt — the drop that defines the collection.',
				chips: [{ id: 'sg_shop', label: 'See it →', action: '/collections/signature/', next: null }]
			}
		},
		'kids-capsule': {
			greeting: {
				text: 'Little rebels need luxury too. 👑 Kids Capsule brings the SkyyRose story down a size.',
				chips: [{ id: 'kc_browse', label: 'Browse Kids Capsule', action: '/collections/kids-capsule/', next: null }]
			}
		},
		preorder: {
			greeting: {
				text: 'Pre-ordering means we make it for you — no overstock, no waste. Pure luxury.',
				chips: [{ id: 'po_browse', label: 'See all pre-orders', action: '/pre-order/', next: null }]
			}
		},
		'404': {
			greeting: {
				text: 'That page doesn’t exist — let me point you somewhere real. 🌹',
				chips: [
					{ id: '404_home', label: 'Take me home',      action: '/',      next: null },
					{ id: '404_shop', label: 'Shop collections',  action: '/shop/', next: null }
				]
			}
		},
		'default': {
			greeting: {
				text: 'Hey! I’m Skyy 👋 Need help finding something?',
				chips: [
					{ id: 'def_shop', label: 'Shop now',  action: '/shop/',     next: null },
					{ id: 'def_help', label: 'Get help',  action: '/contact/',  next: null }
				]
			}
		}
	};

	// -------------------------------------------------------------------------
	// Typewriter
	// -------------------------------------------------------------------------

	function typewrite(el, text, onDone) {
		clearInterval(typewriterTimer);
		el.textContent = '';
		if (prefersReducedMotion) {
			el.textContent = text;
			if (onDone) onDone();
			return;
		}
		var i = 0;
		typewriterTimer = setInterval(function () {
			el.textContent += text[i++];
			if (i >= text.length) {
				clearInterval(typewriterTimer);
				if (onDone) onDone();
			}
		}, TYPEWRITER_SPEED);
	}

	// -------------------------------------------------------------------------
	// Speech Bubble
	// -------------------------------------------------------------------------

	function speak(text, chips) {
		clearGreetTimer();
		clearTimeout(autoDismissTimer);
		state = 'speaking';
		emitSkyy('speaking');
		mascotEl.classList.add('skyy--speaking');
		triggerBtn.setAttribute('aria-expanded', 'true');

		// Clear previous chips
		chipsEl.replaceChildren();

		// Show bubble
		bubble.removeAttribute('hidden');
		// Force reflow so transition fires
		void bubble.offsetWidth;
		bubble.classList.add('skyy-bubble--visible');

		if (askTrigger) {
			askTrigger.hidden = false;
		}

		// Typewrite, then render chips
		typewrite(bubbleText, text, function () {
			if (chips && chips.length) {
				chips.forEach(function (chip) {
					var btn = document.createElement('button');
					btn.type = 'button';
					btn.className = 'skyy-chip';
					btn.textContent = chip.label;
					btn.dataset.chipId = chip.id;
					btn.dataset.action = chip.action || '';
					btn.dataset.next   = chip.next   || '';
					chipsEl.appendChild(btn);
				});
			} else {
				// No chips — auto-dismiss after delay
				autoDismissTimer = setTimeout(dismissBubble, BUBBLE_AUTO_HIDE);
			}
		});
	}

	function dismissBubble() {
		clearTimeout(autoDismissTimer);
		clearInterval(typewriterTimer);
		bubble.classList.remove('skyy-bubble--visible');
		mascotEl.classList.remove('skyy--speaking');
		triggerBtn.setAttribute('aria-expanded', 'false');
		setTimeout(function () {
			if (!bubble.classList.contains('skyy-bubble--visible')) {
				bubble.setAttribute('hidden', '');
				bubbleText.textContent = '';
				chipsEl.replaceChildren();
				if (askTrigger) {
					askTrigger.hidden = true;
				}
			}
			if (state === 'speaking') {
				state = 'idle';
				emitSkyy('idle');
			}
		}, 300);
	}

	// -------------------------------------------------------------------------
	// Chip Handling
	// -------------------------------------------------------------------------

	chipsEl.addEventListener('click', function (e) {
		var btn = e.target.closest('.skyy-chip');
		if (!btn) return;

		var action = btn.dataset.action;
		var next   = btn.dataset.next;

		// Visitor picked a destination — Skyy points the way.
		emitSkyy('point');

		if (action) {
			window.location.href = action;
			return;
		}

		if (next) {
			var script = SCRIPTS[context] || SCRIPTS['default'];
			var node   = script[next];
			if (node) {
				speak(node.text, node.chips || null);
			} else {
				dismissBubble();
			}
		}
	});

	// -------------------------------------------------------------------------
	// Tier 1 Guide Brain — matches free text against data/site-guide.json
	// -------------------------------------------------------------------------

	function normalizeQuery(text) {
		return text.toLowerCase().replace(/[^\w\s-]/g, ' ').replace(/\s+/g, ' ').trim();
	}

	function ensureGuideData() {
		if ( guideData.intents.length || ! mascotConfig.guideUrl ) {
			return Promise.resolve( guideData );
		}
		if ( guidePromise ) {
			return guidePromise;
		}
		guidePromise = fetch( mascotConfig.guideUrl, { credentials: 'same-origin' } )
			.then( function ( response ) {
				if ( ! response.ok ) {
					throw new Error( 'Guide unavailable' );
				}
				return response.json();
			} )
			.then( function ( data ) {
				if ( data && Array.isArray( data.intents ) ) {
					guideData = data;
				}
				return guideData;
			} )
			.catch( function () {
				return guideData;
			} );
		return guidePromise;
	}

	function matchIntent(rawQuery) {
		var query = normalizeQuery(rawQuery);
		if (!query || !guideData.intents.length) return null;

		var best = null;
		var bestScore = 0;

		guideData.intents.forEach(function (intent) {
			var patterns = intent.patterns || [];
			var score = 0;
			patterns.forEach(function (pattern) {
				var normalizedPattern = normalizeQuery(pattern);
				if (normalizedPattern && query.indexOf(normalizedPattern) !== -1) {
					// Longer, more specific patterns outrank single-word ones.
					score += normalizedPattern.split(' ').length;
				}
			});
			if (score > bestScore) {
				bestScore = score;
				best = intent;
			}
		});

		return best;
	}

	function speakIntentAnswer(intent) {
		var chips = null;
		if (intent.link) {
			chips = [{ id: 'guide-' + intent.id, label: 'Take me there →', action: intent.link, next: null }];
		}
		speak(intent.answer, chips);
	}

	function askTier2Fallback(rawQuery) {
		if (!mascotConfig.llmEnabled || !window.skyyRoseData || !window.skyyRoseData.ajaxUrl) {
			speakFallbackRedirect();
			return;
		}

		var body = new URLSearchParams();
		body.set('action', 'skyyrose_mascot_chat');
		body.set('nonce', window.skyyRoseData.nonce || '');
		body.set('message', rawQuery);

		fetch(window.skyyRoseData.ajaxUrl, {
			method: 'POST',
			credentials: 'same-origin',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: body.toString()
		})
			.then(function (response) { return response.json(); })
			.then(function (json) {
				var data   = json && json.data ? json.data : null;
				var answer = data && typeof data.answer === 'string' ? data.answer : '';
				if (answer) {
					var chips = data.link ? [{ id: 'tier2-link', label: 'Take me there →', action: data.link, next: null }] : null;
					speak(answer, chips);
				} else {
					speakFallbackRedirect();
				}
			})
			.catch(function () {
				speakFallbackRedirect();
			});
	}

	function speakFallbackRedirect() {
		speak('Ask me about finding things, sizing, or shipping — that’s what I know best. 🌹', null);
	}

	function handleAskSubmit(rawQuery) {
		if (!rawQuery || !rawQuery.trim()) return;
		ensureGuideData().then(function () {
			var intent = matchIntent(rawQuery);
			if (intent) {
				speakIntentAnswer(intent);
				return;
			}
			askTier2Fallback(rawQuery);
		});
	}

	// -------------------------------------------------------------------------
	// Ask Skyy Dialog — native <dialog> + showModal(), focus trapped + restored
	// -------------------------------------------------------------------------

	if (askTrigger && askDialog && askForm && askInput) {
		askTrigger.addEventListener('click', function () {
			askDialogOpener = document.activeElement;
			askInput.value = '';
			if (typeof askDialog.showModal === 'function') {
				askDialog.showModal();
				askInput.focus();
			}
		});

		askForm.addEventListener('submit', function () {
			// method="dialog" closes the dialog natively on submit; capture the
			// value now so the 'close' handler below can act on it afterward.
			pendingQuestion = askInput.value;
		});

		if (askCancelBtn) {
			askCancelBtn.addEventListener('click', function () {
				pendingQuestion = null;
				askDialog.close();
			});
		}

		askDialog.addEventListener('close', function () {
			if (askDialogOpener && typeof askDialogOpener.focus === 'function') {
				askDialogOpener.focus();
			}
			askDialogOpener = null;

			if (pendingQuestion) {
				var question = pendingQuestion;
				pendingQuestion = null;
				handleAskSubmit(question);
			}
		});
	}

	// -------------------------------------------------------------------------
	// Walk-On / Walk-Off
	// -------------------------------------------------------------------------

	function proactiveSpeak(promptId, text, chips) {
		if (wasPromptShown(promptId)) return false;
		markPromptShown(promptId);
		speak(text, chips);
		return true;
	}

	function walkOn(isProactive) {
		if (state === 'walking-in' || state === 'idle' || state === 'speaking') return;
		state = 'walking-in';
		emitSkyy('walking-in');
		mascotEl.setAttribute('aria-hidden', 'false');
		mascotEl.classList.remove('skyyrose-mascot--hidden', 'skyyrose-mascot--exiting');
		mascotEl.classList.add('skyyrose-mascot--entering');

		var walkDuration = prefersReducedMotion ? 0 : 1400;
		setTimeout(function () {
			mascotEl.classList.remove('skyyrose-mascot--entering');
			mascotEl.classList.add('skyyrose-mascot--idle');
			state = 'idle';
			emitSkyy('idle');

			// First visit = one contextual nudge, never a tour. Greet once
			// per session; never resurface the same greeting after that.
			// A founder-authored page tip (Customizer, empty by default)
			// takes the place of the generic greeting line when configured —
			// that IS the contextual nudge for this page.
			if (isProactive && !sessionStorage.getItem(SESSION_KEY_GREETED)) {
				try {
					sessionStorage.setItem(SESSION_KEY_GREETED, '1');
				} catch (e) { /* degrade silently */ }
				var script = SCRIPTS[context] || SCRIPTS['default'];
				var greetingText = mascotConfig.pageTip ? mascotConfig.pageTip : script.greeting.text;
				// Wave first, speak after — emitting both synchronously makes
				// the talk clip instantly override the wave in the 3D layer.
				emitSkyy('wave');
				greetTimer = setTimeout(function () {
					greetTimer = null;
					// User may have acted during the gap — only greet an
					// idle, undismissed character.
					if (state !== 'idle' || isDismissedThisSession()) return;
					proactiveSpeak('greeting:' + context, greetingText, script.greeting.chips);
				}, prefersReducedMotion ? 0 : 1400);
				recordProactiveAppearance();
			}
		}, walkDuration);
	}

	function walkOff(onDone) {
		clearGreetTimer();
		state = 'exiting';
		emitSkyy('exiting');
		dismissBubble();
		clearTimeout(idleTimer);
		mascotEl.classList.remove('skyyrose-mascot--idle', 'skyyrose-mascot--entering');
		mascotEl.classList.add('skyyrose-mascot--exiting');
		mascotEl.setAttribute('aria-hidden', 'true');

		var exitDuration = prefersReducedMotion ? 0 : 600;
		setTimeout(function () {
			mascotEl.classList.add('skyyrose-mascot--hidden');
			mascotEl.classList.remove('skyyrose-mascot--exiting');
			state = 'dormant';
			// The 3D canvas is a sibling of the mascot container — CSS state
			// classes can't reach it, so it must be told to stop and hide.
			emitSkyy('hidden');
			if (onDone) onDone();
		}, exitDuration);
	}

	// -------------------------------------------------------------------------
	// Entrance scheduling
	//
	// First appearance per session: fixed FIRST_ENTRY_DELAY_MS after load,
	// NOT reset by activity — she is the site host and greets arrivals.
	// Re-entries (after she has appeared at least once): only after the
	// visitor has gone quiet for a randomized 10–30s window, activity resets
	// that timer. Capped at MAX_PROACTIVE_APPEARANCES per session and skipped
	// entirely once the visitor has explicitly dismissed her this session.
	// -------------------------------------------------------------------------

	function scheduleIdleEntrance() {
		clearTimeout(idleTimer);
		if (isDismissedThisSession() || proactiveAppearancesExhausted()) {
			return;
		}
		// First appearance of the session: short fixed delay, host-greets-
		// arrival semantics. Re-entries: randomized idle window.
		var threshold = getAppearanceCount() === 0
			? FIRST_ENTRY_DELAY_MS
			: IDLE_TRIGGER_MIN_MS + Math.random() * (IDLE_TRIGGER_MAX_MS - IDLE_TRIGGER_MIN_MS);
		idleTimer = setTimeout(function () {
			if (state === 'dormant' && !isDismissedThisSession() && !proactiveAppearancesExhausted()) {
				walkOn(true);
			}
		}, threshold);
	}

	function onActivity() {
		var now = Date.now();
		if (now - lastActivityReset < ACTIVITY_THROTTLE_MS) return;
		lastActivityReset = now;
		// Re-arm only for idle-triggered RE-entries. The first-entrance timer
		// must survive scrolling/mouse movement — resetting it on activity
		// means engaged visitors never see her at all.
		if (state === 'dormant' && getAppearanceCount() > 0) {
			scheduleIdleEntrance();
		}
	}

	['scroll', 'pointerdown', 'pointermove', 'keydown', 'touchstart'].forEach(function (eventName) {
		window.addEventListener(eventName, onActivity, { passive: true });
	});

	// React when product grid enters viewport — a Skyy-initiated aside while
	// she's already present is not a new "proactive appearance."
	if ('IntersectionObserver' in window) {
		var productObserved = false;
		var productObs = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				if (entry.isIntersecting && state === 'idle' && !productObserved) {
					productObserved = true;
					mascotEl.classList.add('skyy--glancing');
					setTimeout(function () {
						mascotEl.classList.remove('skyy--glancing');
					}, 2000);
					if (proactiveSpeak('product-glance', 'These just landed. 👀', null)) {
						emitSkyy('excited');
					}
				}
			});
		}, { threshold: 0.3 });

		document.querySelectorAll('.products, .wc-block-grid, .collection-hero').forEach(function (el) {
			productObs.observe(el);
		});
	}

	// React when hovering product cards. Throttled separately from the CSS
	// class toggle below — rapid multi-card hovering must not thrash the 3D
	// layer's clip-switching (skyy-3d.js listens for skyy:excited).
	var HOVER_EXCITE_THROTTLE_MS = 2000;
	var lastHoverExciteAt = 0;
	document.addEventListener('mouseover', function (e) {
		if (state !== 'idle') return;
		if (e.target.closest('.product, .wc-block-grid__product')) {
			mascotEl.classList.add('skyy--excited');
			setTimeout(function () {
				mascotEl.classList.remove('skyy--excited');
			}, 1200);

			var now = Date.now();
			if (now - lastHoverExciteAt > HOVER_EXCITE_THROTTLE_MS) {
				lastHoverExciteAt = now;
				emitSkyy('excited');
			}
		}
	});

	// -------------------------------------------------------------------------
	// Minimize / Recall
	// -------------------------------------------------------------------------

	function minimize(isDismissal) {
		if (isDismissal) {
			markDismissed();
		}
		walkOff(function () {
			recallBtn.style.display = 'flex';
			recallBtn.setAttribute('aria-hidden', 'false');
			// Dismissal must not strand keyboard focus on <body> — the recall
			// pill is the continuation control.
			recallBtn.focus();
		});
	}

	function recall() {
		recallBtn.style.display = 'none';
		recallBtn.setAttribute('aria-hidden', 'true');
		// User-initiated — doesn't count against the proactive-appearance cap
		// and doesn't re-greet (greeting already marked shown this session).
		walkOn(false);
	}

	// -------------------------------------------------------------------------
	// Event Listeners
	// -------------------------------------------------------------------------

	triggerBtn.addEventListener('click', function (e) {
		e.stopPropagation();
		if (state === 'speaking') {
			dismissBubble();
		} else if (state === 'idle') {
			var script = SCRIPTS[context] || SCRIPTS['default'];
			speak(script.greeting.text, script.greeting.chips);
		}
	});

	minimizeBtn.addEventListener('click', function (e) {
		e.stopPropagation();
		minimize(true);
	});

	recallBtn.addEventListener('click', function (e) {
		e.stopPropagation();
		recall();
	});

	// Close bubble on outside click
	document.addEventListener('click', function (e) {
		if (state === 'speaking' && !mascotEl.contains(e.target) && !recallBtn.contains(e.target)) {
			dismissBubble();
		}
	});

	// Keyboard accessibility
	document.addEventListener('keydown', function (e) {
		if (e.key === 'Escape') {
			if (state === 'speaking') {
				dismissBubble();
				triggerBtn.focus();
			} else if (state === 'idle') {
				minimize(true);
			}
		}
	});

	// -------------------------------------------------------------------------
	// Initialize
	// -------------------------------------------------------------------------

	if (isDismissedThisSession()) {
		// Respect the earlier dismissal — surface only the recall pill, no
		// unsolicited walk-on for the rest of this session.
		recallBtn.style.display = 'flex';
		recallBtn.setAttribute('aria-hidden', 'false');
	} else {
		scheduleIdleEntrance();
	}
})();
