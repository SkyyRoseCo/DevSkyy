# GSAP ScrollTrigger Patterns — Immersive Interactive Architect Reference

Load when: GSAP 3.12 + ScrollTrigger cinematic drop pages, landing reveals, and scroll-driven Three.js camera moves.

Provenance: embedded copy of `host repo (DevSkyy) .claude/skills/immersive-interactive-architect/references/gsap-scroll-patterns.md`; verbatim except the adaptations recorded in [index.md](../index.md).

Production patterns for GSAP 3.12 + ScrollTrigger in the SkyyRose context: cinematic
collection drop pages, landing page reveals, and scroll-driven 3D camera moves.

---

## 1. GSAP + ScrollTrigger Setup

### CDN (WordPress / standalone HTML)

```html
<!-- Load order matters: GSAP core before plugins -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js" defer></script>
<!-- ⚠️  SplitText is a Club GSAP plugin (paid/registered) — it is NOT on cdnjs and any
     cdnjs URL for it will 404. To use SplitText you must either:
       • npm install gsap  (with a Club GSAP license) and import as shown below, OR
       • self-host the Club file you downloaded from gsap.com/members.
     Free alternative: split-type (MIT) — https://github.com/lukePeavey/SplitType -->

<script>
document.addEventListener('DOMContentLoaded', () => {
  gsap.registerPlugin(ScrollTrigger);
  // gsap.registerPlugin(SplitText);  // only after self-hosting the Club file
});
</script>
```

### NPM / Next.js

```javascript
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
// SplitText requires a Club GSAP license — install via npm only with a valid membership:
import { SplitText } from 'gsap/SplitText';  // Club GSAP — license required

gsap.registerPlugin(ScrollTrigger, SplitText);
```

---

## 2. Prefers-Reduced-Motion Guard

**Always implement this first** — it wraps all animation initialization.

```javascript
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function initAnimations() {
  if (prefersReduced) {
    // Make everything immediately visible — no motion
    gsap.set('.rv-clip-up, .rv-blur, .col-reveal, .lp-rv', { opacity: 1, y: 0, clipPath: 'none' });
    return;
  }
  // Safe to run motion-heavy code below
  initScrollTimelines();
  initSplitText();
}

// Also respond to live preference changes (accessibility setting change mid-session)
window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
  if (e.matches) {
    gsap.globalTimeline.pause();
    ScrollTrigger.getAll().forEach(t => t.disable());
  } else {
    gsap.globalTimeline.resume();
    ScrollTrigger.getAll().forEach(t => t.enable());
  }
});

document.addEventListener('DOMContentLoaded', initAnimations);
```

---

## 3. Core ScrollTrigger Configuration Pattern

```javascript
// Best practice: define defaults once, override per trigger
ScrollTrigger.defaults({
  toggleActions: 'play none none reverse',
  ease: 'power2.out',
});

// Refresh on font load — prevents position miscalculation
document.fonts.ready.then(() => ScrollTrigger.refresh());
```

---

## 4. Cinematic Hero Reveal (Collection Drop)

Mimics a movie credit sequence — product emerges from darkness on scroll entry.

```javascript
const heroTl = gsap.timeline({
  scrollTrigger: {
    trigger: '#hero',
    start:   'top top',
    end:     '+=100%',
    scrub:   1.5,          // scrub = scroll-synced, value = lag in seconds
    pin:     true,         // pin hero while scrolling through it
    anticipatePin: 1,
  },
});

heroTl
  .from('.hero-product', {
    scale: 0.5, opacity: 0, filter: 'blur(20px)',
    duration: 1, ease: 'power3.out',
  })
  .from('.collection-wordmark img', {
    y: 60, opacity: 0, duration: 0.8,
  }, '-=0.5')
  .from('.hero-tagline', {
    y: 40, opacity: 0, duration: 0.6,
  }, '-=0.3')
  .from('.hero-cta', {
    scale: 0.8, opacity: 0, duration: 0.5,
  }, '-=0.2');
```

---

## 5. Product Card Stagger Reveal

```javascript
// ScrollTrigger on the grid container, stagger children automatically
gsap.from('.product-card', {
  scrollTrigger: {
    trigger:      '.product-grid',
    start:        'top 80%',
    toggleActions: 'play none none reverse',
  },
  y:        80,
  opacity:  0,
  stagger:  { each: 0.12, from: 'start', ease: 'none' },
  ease:     'power3.out',
  duration: 0.9,
});
```

---

## 6. Scroll-Scrubbed Three.js Camera Move

Sync a Three.js camera path to scroll position without a render loop conflict.

```javascript
// Position keyframes along a path
const cameraPath = {
  start: new THREE.Vector3(0, 1, 6),
  mid:   new THREE.Vector3(2, 0.5, 3),
  end:   new THREE.Vector3(0, 0, 2),
};

const proxy = { progress: 0 };

ScrollTrigger.create({
  trigger: '#experience-section',
  start:   'top top',
  end:     '+=300%',
  scrub:   true,
  pin:     true,
  onUpdate: (self) => {
    const p = self.progress;
    // Lerp between keyframes based on scroll progress
    if (p < 0.5) {
      camera.position.lerpVectors(cameraPath.start, cameraPath.mid, p * 2);
    } else {
      camera.position.lerpVectors(cameraPath.mid, cameraPath.end, (p - 0.5) * 2);
    }
    camera.lookAt(0, 0, 0);
  },
});
```

---

## 7. SplitText Word / Character Reveals

```javascript
// Word-by-word reveal — SkyyRose brand voice: deliberate, weighted
function initSplitText() {
  const headings = document.querySelectorAll('.collection-heading, .brand-statement');

  headings.forEach((el) => {
    const split = new SplitText(el, { type: 'words,chars' });

    gsap.from(split.words, {
      scrollTrigger: {
        trigger:       el,
        start:         'top 85%',
        toggleActions: 'play none none reverse',
      },
      y:        '110%',         // slide up from below (clip-path alternative)
      opacity:  0,
      duration: 0.7,
      stagger:  0.06,
      ease:     'power3.out',
      onComplete: () => split.revert(), // clean up after animation
    });
  });
}

// Character-by-character for short hero words
function revealChars(selector) {
  const split = new SplitText(selector, { type: 'chars' });
  gsap.from(split.chars, {
    scrollTrigger: { trigger: selector, start: 'top 80%' },
    opacity:  0,
    y:        30,
    rotateX:  -90,
    stagger:  0.03,
    duration: 0.5,
    ease:     'back.out(1.7)',
  });
}
```

---

## 8. Lottie Integration — Scroll-Scrubbed

```javascript
// Assumes lottie-web loaded via CDN
import lottie from 'lottie-web'; // or use CDN: window.lottie

const anim = lottie.loadAnimation({
  container:  document.getElementById('lottie-player'),
  renderer:   'svg',       // svg = sharpest; canvas = fastest; html = most compatible
  loop:       false,
  autoplay:   false,
  path:       '/wp-content/themes/skyyrose-flagship/assets/js/animations/drop-reveal.json',
});

// Wait for Lottie to load before wiring ScrollTrigger
anim.addEventListener('DOMLoaded', () => {
  ScrollTrigger.create({
    trigger:  '#lottie-section',
    start:    'top center',
    end:      'bottom center',
    scrub:    1,
    onUpdate: (self) => {
      // Drive Lottie frame from scroll position — no autoplay needed
      const frame = Math.round(self.progress * (anim.totalFrames - 1));
      anim.goToAndStop(frame, true);
    },
  });
});
```

---

## 9. Horizontal Scroll Section (Collection Gallery)

```javascript
// Pin a container while its inner track scrolls horizontally
const track = document.querySelector('.gallery-track');
const cards  = gsap.utils.toArray('.gallery-card');

gsap.to(track, {
  x:    () => -(track.scrollWidth - window.innerWidth),
  ease: 'none',
  scrollTrigger: {
    trigger:          '#gallery-section',
    start:            'top top',
    end:              () => `+=${track.scrollWidth - window.innerWidth}`,
    pin:              true,
    scrub:            1,
    invalidateOnRefresh: true, // recalculate on resize
  },
});

// Capture the horizontal scroll tween so it can be passed to containerAnimation
const horizontalTween = gsap.to(track, {
  x:    () => -(track.scrollWidth - innerWidth),
  ease: 'none',
  scrollTrigger: {
    trigger:          wrapper,
    pin:              true,
    scrub:            1,
    end:              () => '+=' + track.scrollWidth,
    invalidateOnRefresh: true,
  },
});

// Add parallax depth to cards while they scroll horizontally
cards.forEach((card, i) => {
  const depth = (i % 2 === 0) ? -30 : 30; // alternate up/down
  gsap.to(card, {
    y:    depth,
    ease: 'none',
    scrollTrigger: {
      trigger:            card,
      containerAnimation: horizontalTween, // pass the tween directly — never gsap.core.globals()
      start:              'left right',
      end:                'right left',
      scrub:              true,
    },
  });
});
```

---

## 10. Pin / Snap — Full-Section Snap Scrolling

```javascript
// Snap to section boundaries — creates intentional chapter-by-chapter feeling
const sections = gsap.utils.toArray('.experience-chapter');

sections.forEach((section, i) => {
  ScrollTrigger.create({
    trigger:  section,
    start:    'top top',
    pin:      true,
    pinSpacing: false,   // stacking sections (parallax stack)
    snap: {
      snapTo:       1 / (sections.length - 1),
      duration:     { min: 0.3, max: 0.8 },
      delay:        0.05,
      ease:         'power2.inOut',
    },
  });
});
```

---

## 11. ScrollTrigger Cleanup (React + WordPress SPA)

Leaking ScrollTrigger instances causes compounding animation bugs and memory leaks.

```javascript
// React: cleanup in useEffect return
useEffect(() => {
  const ctx = gsap.context(() => {
    // All GSAP/ScrollTrigger code inside here is scoped
    gsap.from('.hero-product', { opacity: 0, y: 60, duration: 1 });
    ScrollTrigger.create({ trigger: '.section', start: 'top 80%', /* ... */ });
  }, containerRef); // scope to component DOM node

  return () => ctx.revert(); // kills all animations AND ScrollTriggers in scope
}, []);

// WordPress: kill all triggers on Barba.js / custom SPA nav
document.addEventListener('skyyrose:page-leave', () => {
  ScrollTrigger.getAll().forEach(t => t.kill());
  gsap.globalTimeline.clear();
});
```

---

## 12. Performance Notes

- **`scrub: true`** (boolean) = instant sync; `scrub: 1.5` = 1.5s lag — smoother, heavier.
- **`invalidateOnRefresh: true`** is required on any trigger that uses a function-based `end` calculation — prevents stale pixel values after resize.
- **Batch static reveals**: use `ScrollTrigger.batch()` for large lists of reveal elements instead of individual `ScrollTrigger.create()` calls — reduces observer count dramatically.

```javascript
ScrollTrigger.batch('.product-card', {
  onEnter: (elements) => {
    gsap.from(elements, { opacity: 0, y: 60, stagger: 0.1, duration: 0.8 });
  },
  onLeaveBack: (elements) => {
    gsap.to(elements, { opacity: 0, y: -40, stagger: 0.05 });
  },
  start: 'top 85%',
  once:  false,
});
```
