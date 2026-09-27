---
name: Banned-by-Default Elements (WP §1.3)
specified_by: [wp: §1.3]
phase: 0
test_command: node scripts/measurement/check-banned-elements.js
pass_threshold: Zero banned-element instances on customer-facing surfaces; or 100-word justification per exception
last_updated: 2026-05-03
last_updated_by: eval-harness (Phase 0)
---

# Banned-by-Default Elements

These are not banned because they don't work. They are banned because **they are how every Shopify store on Earth looks**. Premium means earning the visual moves. If the move is going to look like everyone else's, justify it (in a 100-word writeup that survives the §1.1 critique pass) or replace it.

This list is **enforced** — Phase 0 critique and Phase 6.8 brand consistency sweep both check for these. Any instance found = FAIL until either removed or justified.

---

## The 17 banned defaults

| # | Banned element | Why it's banned | The premium replacement |
|---|---------------|-----------------|-------------------------|
| 1 | Centered hero with full-width photo + headline + "Shop Now" button | Generic Shopify default; says nothing about the brand | Scroll-driven editorial hero with one image + one sentence (no CTA in hero per WP §6.1) |
| 2 | 4-column equal-spaced product grid with white background | Generic e-commerce default; no editorial voice | Editorial collection narrative with products inside the story (per WP §6.4) |
| 3 | Generic stock-photo style imagery | Reads as inauthentic immediately | Authored photography with named context; Oakland references named not gestured |
| 4 | Stock badge animations (pulsing dots, generic carousel arrows) | Cliché motion that doesn't compound | Slow, intentional motion (400ms default per WP §5.3) — or no motion |
| 5 | "Lorem ipsum" anywhere, ever | Tells the customer the page isn't done | Real, brand-voiced copy from Phase 4+ work |
| 6 | Default WooCommerce styling on any customer-facing surface | Looks like every other WC store | Phase 5.1 fully styles WC blocks; Phase 5.10 wires payments cleanly |
| 7 | Trust badge clusters at the bottom of pages (Visa/MC/Amex logos in a row) | Generic; tells the customer the page is generic | Editorial single-line trust statement near CTA (WP §6.3) |
| 8 | "Limited Time Offer!" countdown timers as a homepage element | Pressure, not premium | Drop countdown (Phase 5.4) is contextual to a real drop, not always-on pressure |
| 9 | Stock testimonial layouts (avatar circle + name + quote in a card) | Looks like a SaaS landing page | Pulled-quote editorial treatment integrated into product story (WP §4.7) |
| 10 | Free shipping bars at the top of the page in a color that fights the design | Visual noise | Free shipping threshold shown as quiet progress indicator near cart CTA, not a top bar |
| 11 | Cookie banners that take more than 3 seconds to dismiss | Friction; brand-cheapening | Tasteful GDPR consent banner with Accept / Reject / Customize, dismissible in <3s |
| 12 | **Blue, in any shade.** No navy, no denim-blue, no powder, no slate-blue, no electric-blue. Banned site-wide. | Breaks brand palette canon (rose gold / dark / gold / crimson / silver). Blue reads "tech startup", not "Oakland luxury". | Use the 5-color palette only. Substitute crimson for "warm accent", silver for "cool accent", dark for any backdrop. |
| 13 | **Luxury clichés.** Gold filigree, marble countertops, champagne flutes, chandeliers, "iconic", "curated for you", "elevated essentials", any Versailles-grade decoration | Says "I think luxury looks like this" when real luxury is restraint. Tells the customer the brand is performing, not living. | Restraint. Editorial silence. Concrete textures (literal — ""). Oakland canon as backdrop. |
| 14 | **Dry product reveals.** CSS slide-in / fade-in animations on product cards with no narrative beat. | Motion without meaning is decoration; decoration is the opposite of premium. | Reveals tied to a story moment — scroll triggers a narrative beat, then the product enters as part of the beat (per WP §5.3 motion rules). |
| 15 | **Lackluster anything.** Safe colors, expected layouts, brand-checklist defaults, "industry standard" UX patterns chosen because they're industry-standard. | The brand's job is bold. Safe is the enemy. | Bold default. If the choice is "what would every Shopify store do" — invert it. Justify safety in writing if you choose it. |
| 16 | **Dated visual language.** 2015-2022 e-commerce template tropes — card-grid scroll-and-buy, homepage hero-with-CTA-stack, "Featured / Best Sellers / New In" sectional homepage, sidebar filter panels with checkbox lists. | The site reads as a Shopify clone from a previous era. | Editorial-magazine information architecture (i-D / Document / SSENSE editorial). Story → atmosphere → product as a beat. |
| 17 | **Gendered framing in copy.** "For him", "for her", "men's", "women's", "boyfriend gift", "she'll love it". | The brand is gender-neutral, designed for everyone. Gendered framing breaks canon. | Sized garments without gender labels. Copy speaks to *the person who wears it*, not their assigned-at-birth shopping aisle. |

---

## The justification protocol

If a surface genuinely needs one of the above (rare — by design), the agent must write a 100-word justification in `eval/banned-elements-exceptions/<surface>-<element>.md`:

```yaml
---
surface: <page slug>
element_used: <which banned element from the list above>
date: <YYYY-MM-DD>
agent: <which agent claims this exception>
---

<100 words explaining why the brand-coherent alternative doesn't work for this specific case, what was tried first, and what makes this instance not look like a generic Shopify store>
```

The justification must survive the §1.1 critique pass (especially pass 3 — adversarial critique). If it doesn't survive — the element is removed.

---

## Banned element check

```bash
node scripts/measurement/check-banned-elements.js
```

Greps the rendered output of every page (via Chrome MCP) for the visual signatures of these elements. Exits 0 if none found OR all instances are documented exceptions; exits 1 on any unjustified instance.

---

## Adjacent-banned (lower bar but flagged)

These aren't banned outright but get flagged for review:

| Element | Reason for flag |
|---------|-----------------|
| Gradient backgrounds | Almost always reads as 2014; usually replaceable with a single color or photograph |
| Drop-shadow stacks | Premium = restrained shadows; multiple shadows usually = trying to fake depth |
| All-caps text larger than 16px outside the type system | Type system specifies all-caps cases (Anton UI); arbitrary all-caps reads as shouting |
| Ghost buttons with thin borders on photographs | Low contrast + low brand presence |
| Box-shadows on buttons | Premium buttons don't have shadows (per WP §5.3 #6) |
| Hover states that scale + shadow + color flip | Mash of three effects; usually one is right (per WP §5.3 #5) |
| Default browser spinners on loading | Loading states are designed (per WP §5.3 #7) |
| Blank empty states (empty cart, no search results, 404) | Empty states have personality (per WP §5.3 #8) |
| Toast-only form errors | Errors should be inline + specific (per WP §5.3 #9) |

These are surfaced in the `audit` skill's P2/P3 issues. Not blocking, but noted.

---

## How this enforces

- Phase 0 §3 critique audit (running now via UX Researcher subagent) flags any of these on the current live site
- Phase 4 per-template work runs `eval/brand.md` rubric which includes a banned-elements check
- Phase 6.8 brand consistency sub-phase via `Brand Guardian` agent does sitewide audit
- Phase 7 ship-check re-runs the full check; any unjustified instance fails the gate
