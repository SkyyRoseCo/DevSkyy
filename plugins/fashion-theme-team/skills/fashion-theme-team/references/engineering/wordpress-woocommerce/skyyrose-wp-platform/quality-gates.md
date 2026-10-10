# The Gates That Keep This a Luxury Storefront, Not Just a WordPress Site

Load when: the task touches accessibility, SEO/schema, Core Web Vitals, CSS cascade discipline, or CSP/nonce security on the SkyyRose storefront (routed from `overview.md`).

Provenance: embedded from the DevSkyy skill `skyyrose-wp-platform` (`reference/quality-gates.md`); source hash, license, and every adaptation are recorded in [`../index.md`](../index.md).

A generic accessibility/SEO/performance/security checklist doesn't know what's actually at
stake here: a visitor who can't navigate the Black Rose immersive world because of a missing
skip link is being locked out of the brand experience, not just failing a WCAG rule; a
Core Web Vitals regression on a page carrying nine self-hosted brand fonts and a walk-on
mascot is a different problem than a slow blog post. Every gate below is framed around what
it's actually protecting on THIS storefront.

## Accessibility — a known, tracked gap, not a fresh audit target

Skip-links are a confirmed open gap, tracked as **HG-5**. If a pass turns this up again, it is
not a new finding — check whether a fix is already in flight before starting one from scratch.
Beyond that specific gap: every custom component this theme ships (product-card-holo's
magnetic-tilt cards, the four immersive-world hotspots, the mascot's walk-on presence) is
bespoke, meaning it has no framework default to fall back on for focus order or ARIA roles —
these have to be authored deliberately, the same way the visual design was.

## SEO — discoverability for four distinct collections, not one generic catalog

JSON-LD structured data and OG-tag work has already shipped. The thing worth protecting here
isn't "SEO" in the abstract — it's that Signature, Black Rose, Love Hurts, and Kids Capsule
each need to surface as what they distinctly are, not as four variations of one generic
product-category template. Before adding new schema markup, check what's live first —
cache-busted `curl` (never `WebFetch`, which strips `<script>` tags and would hide exactly the
JSON-LD you're trying to verify).

## Performance — nine brand fonts and a walk-on mascot is not a lightweight page

`inc/performance.php` handles Google Fonts removal — all nine brand font families (Archivo for
display and headings, Hanken Grotesk for body/UI copy, Anton for UI caps and accent, Cinzel as
the engraved-caps accent, Inter for system fallback, plus the four per-collection script faces)
are self-hosted via the WordPress Font Library declared in `theme.json` — zero external Google
Fonts CDN calls, by design, not by omission. That design choice only pays off if the `.min`
build pipeline is actually rebuilt after every source change (see `build-and-templates.md`) —
an un-rebuilt `.min` means the browser silently serves a larger bundle than the font-hosting
work was meant to prevent.

## CSS cascade discipline — one brand, four collections, one set of tokens

This is a 24+-template theme (4 collection pages, 3 landing pages, 4 immersive pages,
pre-order, about, WooCommerce templates, search, 404, header/footer chrome) built on five
brand tokens: Rose Gold `#B76E79` (global accent, Kids Capsule), Dark `#0A0A0A` (background),
Silver `#C0C0C0` (Black Rose), Crimson `#DC143C` (Love Hurts), Gold `#D4AF37` (Signature). The
recurring risk is a per-collection override accidentally bleeding into another collection's
pages through specificity — prefer scoping new rules to a template-specific class over
winning a cascade fight with higher specificity, and check `product-card-holo.css` and
`immersive.css` for the existing pattern before introducing a new one. A Black Rose page
rendering with Signature gold, or vice versa, is a brand-canon violation, not just a CSS bug.

## Security (CSP, nonces) — protecting real customer orders and the founder's own words

`inc/security.php` owns CSP headers, rate limiting, and ABSPATH guards. Any new script/style
source (a CDN, a new inline script) needs a corresponding CSP allowance here — see
`threejs-immersive.md` for the `script-src` vs `connect-src` distinction that has caused real
bugs (jsdelivr allowed for scripts, not for the Draco decoder's runtime fetch). This isn't
abstract OWASP hygiene: what's behind these gates is live WooCommerce order data and
founder-authored product dossiers, not placeholder content.

## Domain-specific verification

- **A11y**: an actual accessibility-tree read (Playwright/Chrome DevTools MCP) or `axe-core`
  run against the live or staged page — not a manual visual scan, which reliably misses
  focus-order and ARIA issues on bespoke components that have no framework default to lean on.
- **SEO/schema**: cache-busted `curl` of the served HTML, checked for the actual `<script
  type="application/ld+json">` block content per collection page — not `WebFetch`, and not
  "the plugin says it's enabled."
- **Performance**: a real Lighthouse/WebPageTest run or Core Web Vitals field data, measured
  before and after — not an assumption that self-hosting fonts or shipping AVIF automatically
  improved the metric.
- **CSP**: cache-busted `curl -sI ... | grep -i content-security-policy` against the live
  response plus a browser console check for CSP violation errors — a header existing in
  `inc/security.php` source doesn't prove it's the header actually being served after a
  deploy (cache layers can serve stale headers too).
- **Brand-token/canon compliance**: a Playwright screenshot of the specific collection page
  being touched, read against its own token (Black Rose = silver/Black Rose Script lockup/gothic, Love Hurts =
  crimson/castle, Signature = gold/city, Kids Capsule = rose gold) — not a diff against a
  generic design-system baseline that doesn't know the four collections apart.
