# Kids Capsule — Designer Copy

> Source: docs/brand/collection-stories.md (canonical). Seed: "The Heir to the throne."

## Origin

The brand is named after her — Skyy Rose, Corey's daughter. She was on the way when he had nothing. No drive, no money, no support. She was the reason he built.

Verbatim from `collection-content.php`:

> "The whole brand is named after her — Skyy Rose. My daughter. She was on the way when I had nothing. No drive, no money, no support. But that baby coming changed everything. I needed to build something she'd be proud to carry."

The Kids Capsule is the brand completing its circle — the daughter who was the reason for all of it now wears the brand built in her name. Launched 2026 per the About page timeline: *"The fourth chapter. Same craftsmanship, smaller silhouettes. Passing the torch on the same terms that built the brand."*

Products: kids-001 Red/Black Hoodie Set ($65), kids-002 Purple/Black Hoodie Set ($65). Two SKUs. The capsule is tight by design — the same precision, smaller scale.

*Sources: `inc/collection-content.php`, `skyyrose.co/about/`, `skyyrose-catalog.csv`*

## Voice & Mood

Legacy. No sentimentality — this isn't nostalgia, it's inheritance. The same declarative voice as the rest of the brand, now aimed at the next generation.

Hero tagline (verbatim, live site): **"Luxury runs in the family."**

Hero subtitle, verbatim: *"Premium streetwear for the next generation — powerful, elevated, and born into legacy. Because legacy is not inherited. It is worn."*

Story label: "Her Name" / Story title: "Named After My Daughter"

Founder quote from `collection-content.php`:

> "I built SkyyRose so my daughter would never have to wonder if she was enough."

Founder's mandate for the product, verbatim:

> "No pastels. No cartoons. Skyy Rose doesn't wear that. She wears what her father built — premium, dark, elegant. Scaled down but never dumbed down."

Mood from `skyyrose.co/about/` description: *"Rose gold and soft pink. The fourth chapter, smaller silhouettes, same craftsmanship."*

## Story Tagline

**"Luxury runs in the family."**

*(Verbatim hero tagline, `collection-content.php`. Not invented.)*

---

## Moments of Delight — Campaign Elevation Layer

*Three award-caliber touches that make the Kids Capsule launch impossible to forget. Each is designed to be shared, felt, and remembered — not just seen.*

---

### 01 · The Digital Torch Pass

**What it is:** An interactive animation triggered on the Kids Capsule collection page. When a visitor lands or scrolls into the hero, a rose-gold flame materializes in the center of the screen — carried by the founder's silhouette — and the user can pass it forward by tapping or clicking. The flame lands in the hands of a child silhouette. The transition takes 1.2 seconds. No text needed.

**The mechanic:** Trigger on scroll-into-view (IntersectionObserver). Rose-gold particle flame (#B76E79), CSS/canvas animation, respects `prefers-reduced-motion`. On pass: the child silhouette lights up in rose-gold, a subtle haptic pulse fires on mobile, and the hero copy fades in: *"The torch is passed."*

**Why it wins:** The gesture is the story. Every visitor re-enacts the founding act — silently, in two seconds, without reading a word. The microinteraction is the campaign in motion.

**Execution scope:** `template-parts/kids-capsule/` JS + CSS, no external libs. Fires once per session (sessionStorage gate). Does NOT fire if `prefers-reduced-motion: reduce`. WCAG 2.2 AA compliant — keyboard-triggerable (Enter/Space on the hero CTA).

**Brand line for campaign use:** *"Some things you don't explain. You pass them on."*

---

### 02 · Hidden Rose Gold Thread — Packaging Detail

**What it is:** A single rose-gold thread stitched invisibly into the interior seam of every Kids Capsule polybag or hang-tag ribbon — visible only when the packaging is held to light. No callout. No label. Just the thread, there for the ones who look closely.

**Why it wins:** Discovery without announcement. The parent who notices it first will photograph it. The child who finds it years later understands something without being told. It is the physical equivalent of the brand's entire philosophy — luxury that doesn't need to explain itself.

**The reveal mechanic:** Printed inside the hang-tag in a 7pt font, bottom edge, in rose-gold ink on dark card:
> *Look at the seam.*

That's the full instruction. Nothing else.

**Production note:** Source rose-gold (#B76E79 / Pantone 7422 C) polyester thread. Single pass, interior seam of polybag gusset or ribbon loop. Cost per unit: negligible. Perceived value: disproportionate.

**Brand line for campaign use:** *"The detail no one asked for. The one they'll always remember."*

---

### 03 · The Oakland Soil Card — Kids Capsule Exclusive Insert

**What it is:** A 3.5" × 5" matte-black card, printed on 18pt stock, included in every Kids Capsule order. On one side: the brand tagline in Archivo Bold — *""* On the other side, a sealed clear-faced pocket containing a small amount of Oakland soil — sourced, dated, labeled.

**The text on the soil pocket label (Cinzel, 8pt, rose-gold ink):**

> Oakland, CA
> Collected [Month Year]
> The ground this was built on.

**Why it wins:** It is the most literal, most honest, most unanswerable statement the brand can make. The soil is not metaphorical. It is the proof. No campaign line, no influencer post, no ad spend delivers what a child holding a piece of Oakland in their hands delivers. The card will be kept. It will be shown. It will be photographed and posted without prompting.

**The ceremony copy (printed interior of shipper box, small type):**

> This collection was built for her — the daughter who was the reason for all of it. She was born into Oakland. So was this brand. So are you.
> *Keep the card.*

**Production note:** Source soil from a verified Oakland address meaningful to the founder. Seal in a 1.5" × 2" flat clear-faced ziplock with a circular Pantone-matched rose-gold label. Legal: soil is inert, unregulated for domestic shipment. Include a note on the card back: *Decorative soil. Not for consumption.*

**Brand line for campaign use:** *"She was born into Oakland. So was this brand. Now so are you."*

---

*These three moments operate on different timescales: the torch pass is felt in 2 seconds, the thread is found in 2 minutes, the soil card is kept for 20 years. Together, they turn a product purchase into a founding act.*
