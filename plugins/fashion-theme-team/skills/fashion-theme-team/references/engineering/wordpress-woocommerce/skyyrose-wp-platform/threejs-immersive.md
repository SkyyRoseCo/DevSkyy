# The Mascot and the Four Immersive Worlds (WordPress-side)

Load when: the task touches the mascot, the four immersive worlds, `assets/js/skyy-3d.js`, or anything under `assets/scenes/` in the SkyyRose theme (routed from `overview.md`).

Provenance: embedded from the DevSkyy skill `skyyrose-wp-platform` (`reference/threejs-immersive.md`); source hash, license, and every adaptation are recorded in [`../index.md`](../index.md).

The mascot is the face of the brand, not a decorative widget, and the four immersive worlds
(Black Rose's gothic cathedral, Love Hurts' romantic castle, Signature's city tour, Kids
Capsule) are top-of-funnel storytelling, not shopping pages. This file covers how _this
theme specifically_ loads and wires vanilla three.js to carry that -- it replaces what
`immersive-interactive-architect` and the generic `threejs-*` framing addressed as abstract
3D mechanics. For general three.js API (AnimationMixer, morph targets, materials, shaders),
read the plugin's Three.js reference at
[`../../threejs-immersive/index.md`](../../threejs-immersive/index.md) (Host repo (DevSkyy):
the `threejs-animation` skill and its siblings) — this file only covers the WordPress-specific
loading, CSP, and template wiring that those references don't know about.

## How three.js actually loads in this theme

`assets/js/skyy-3d.js`'s `loadThree()` function:

- Loads `three@0.170.0` from jsdelivr CDN via `/+esm` endpoints (rewrites bare `from 'three'`
  specifiers to jsdelivr's own ESM URL for the same version — one shared instance, no
  importmap needed; a _late_ importmap is rejected once the page has already executed any
  module script, which the homepage does, so this loading order is load-bearing, not
  incidental).
- Self-hosts the Draco decoder binaries (`DRACO_DECODER_PATH`) even though the three.js/loader
  scripts themselves come from jsdelivr — because the decoder's runtime fetch falls under CSP
  `connect-src`, which does not allow jsdelivr, while the script tags themselves fall under
  `script-src`, which does. Getting this distinction wrong is the single most common way a
  "it works locally but the mascot is invisible on skyyrose.co" bug happens.
- Sets `window.THREE`, `window.THREE_GLTFLoader`, `window.THREE_DRACOLoader` and dispatches a
  `three-ready` event — other scripts should listen for that event, not assume THREE is
  already global.

**This is a different three.js instance and version than `frontend/`'s npm-installed
`three@^0.172.0` (via `@react-three/fiber`).** A fix verified against one is not automatically
true of the other — check which one you're actually touching before generalizing a finding.

## Where the immersive scenes live

- `template-immersive-{signature,black-rose,love-hurts,kids-capsule}.php`
- `assets/js/immersive.js`, `assets/css/immersive.css`, `assets/scenes/`
- These are top-of-funnel storytelling pages (Black Rose gothic cathedral, Love Hurts romantic
  castle, Signature city tour, Kids Capsule) — not shopping pages. Don't route product-grid
  or catalog work into these templates. The one sanctioned crossover is
  `immersive-wc-bridge.js` (hotspot → real product link).
- Host repo (DevSkyy): `wp-immersive` is the agent that owns this surface
  (`.claude/agents/wp-immersive.md`, user-scope). New/modified scene patterns should draw
  from the pre-screened set in `docs/design/visual-pattern-shortlist.md` (Priority tier +
  Chapter 1-3/7 entries tagged "Immersive Worlds scene work") and must still pass
  `fashion-theme-architect.md`'s §5.2 Motion QA (reduced-motion fallback, cut-font grep,
  brand-token hex grep, mobile WebGL fallback, no autoplay audio) even though wp-immersive is
  the builder — that gate isn't agent-specific. Inside this plugin, the same Motion QA
  checklist applies regardless of which agent builds the scene.

## Mascot-specific spec (current production baseline)

- GLB textures: 1024×1024, JPEG, re-encoded via `npx @gltf-transform/cli` (confirmed this is
  the correct invocation this session — a bare `gltf-transform` binary resolves to a different,
  nonexistent npm package and fails; the CLI must be invoked via the scoped `@gltf-transform/cli`
  package) (`resize` → `jpeg --formats
  png --quality 85` → `draco`). Note `--formats` defaults to only reprocessing _already-jpeg_
  textures — passing `--formats png` explicitly is required to convert PNG source textures.
- Corrective shape keys (not weight-painting, not a helper bone) fix LBS collapse at extreme
  joint flexion — see the Corrective Shape Keys material in
  [`../../threejs-immersive/index.md`](../../threejs-immersive/index.md) (Host repo (DevSkyy):
  `threejs-animation`'s Corrective Shape Keys section and the `3d-rigging-pipeline` skill for
  the Blender-side authoring).
- A shape key's rest/default weight must be verified as exactly 0.0 by parsing the exported
  GLB JSON directly — not inferred from runtime playback, which cannot detect a leaking rest
  weight (bug-214 class).

## Domain-specific verification

- **CSP is actually satisfied, not just "should be"** — cache-busted
  `curl -sI "https://skyyrose.co/PATH?cb=$(date +%s)" | grep -i content-security-policy`
  against the live response, then check the browser console for CSP violation errors via
  Playwright/Chrome DevTools MCP — a curl 200 does not prove the CSP header is what you think
  it is after a deploy.
- **The mascot/scene is actually visible, not a white cutout or invisible** — Playwright
  screenshot with the pre-decode pattern: `browser_evaluate` running `img.decode()` (or the
  scene's equivalent readiness signal) on the relevant images/canvas _before_ taking the
  screenshot, with a 5-second budget — a screenshot taken before assets finish decoding
  reports false negatives.
- **Draco/GLTFLoader wiring survived a deploy** — the four known root-causes on this project
  (Draco decoder path wiring, `/+esm` bare-specifier resolution, `ver=` query-string cache
  edge caching, a body-transform breaking the scene) are each independently checkable: decoder
  path via a network request read, bare-specifier resolution via the console for module
  load errors, cache via the cache-busted curl above, body-transform via a direct DOM read of
  the mascot container's computed transform.
