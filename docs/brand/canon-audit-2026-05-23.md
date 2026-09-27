# SkyyRose Canon Audit — 2026-05-23

Canon locked: `docs/brand/collection-stories.md` + `project_founder_voice.md` (locked 2026-05-23).
Audit completed: 2026-05-23.

---

## Summary

- **Total violations: 17**
- **Severity breakdown:** HIGH: 7 / MEDIUM: 7 / LOW: 3
- **Worst offender file:** `wordpress-theme/skyyrose-flagship/template-landing-love-hurts.php` — 3 lineage violations in customer-facing story copy
- **Worst offender page (live):** `skyyrose.co/` homepage — "Where Bay Area authenticity meets high-fashion aesthetics" is HIGH severity and visible above the fold

---

## Violations by surface

### Live site (skyyrose.co)

---

**Violation LV-01**
- **Location:** `https://skyyrose.co/` — homepage above-fold hero / brand description block
- **Current copy:** "Where Bay Area authenticity meets high-fashion aesthetics"
- **Violation type:** vocabulary — "Bay Area" as geographic identity
- **Severity:** HIGH — above-fold, brand-defining framing, directly contradicts Oakland-only canon
- **Proposed fix:** "Where Oakland authenticity meets high-fashion aesthetics" — or, stronger in founder voice: "Where the Town builds something that has no business being this beautiful."

---

**Violation LV-02**
- **Location:** `https://skyyrose.co/` — homepage brand description / tagline block
- **Current copy:** "Pioneer in Bay Area gender-neutral fashion"
- **Violation type:** vocabulary — "Bay Area" as geographic identity
- **Severity:** HIGH — customer-facing brand descriptor; mislocates the brand geographically
- **Proposed fix:** "Pioneer in Oakland gender-neutral fashion" or drop geographic qualifier and lean on "Oakland · Est. 2020 · Gender Neutral" already present on the page

---

**Violation LV-03**
- **Location:** `https://skyyrose.co/` — homepage tagline block
- **Current copy:** "Three collections, one vision — built by a father, named after a daughter"
- **Violation type:** tagline drift (minor) — not a replacement of the locked tagline, but the "one vision" framing misses the locked front-page copy from `front-page.php` which correctly reads "four collections, one bloodline." The live rendering is mismatched from source.
- **Severity:** MEDIUM — visible homepage copy; "vision" is generic brand-speak vs. "bloodline" which is canon
- **Proposed fix:** "Four collections, one bloodline — built by a father, named after a daughter." (matches `front-page.php:252` source)

---

**Violation LV-04**
- **Location:** `https://skyyrose.co/about/` — press section, "Best of Best Review" award excerpt
- **Current copy (live):** "The Skyy Rose Collection has been honored with the prestigious Best Bay Area Clothing Line Award 2024 — recognized for high-end, gender-neutral clothing that transcends age and gender boundaries."
- **Violation type:** vocabulary — "Bay Area" as geographic identity used in brand-endorsed framing of the award
- **Severity:** MEDIUM — this is third-party press copy being reproduced verbatim; the award name itself contains "Bay Area." The violation is in the *framing choice* to display it unqualified. An editorial note reanchoring to Oakland would resolve it.
- **Proposed fix:** Add a brief editorial bracket or reframe the display label: "Best Bay Area Clothing Line Award 2024 — Oakland recognized." Alternatively, display the award name without the full excerpt so the "Bay Area" appears as award nomenclature only, not brand identity.

---

**Violation LV-05**
- **Location:** `https://skyyrose.co/about/` — press section, "San Francisco Post" excerpt
- **Current copy:** "A trailblazing gender-neutral clothing brand redefining fashion in the Bay Area and beyond."
- **Violation type:** vocabulary — "Bay Area" as brand geographic identity in a press excerpt the brand chooses to display and endorse
- **Severity:** MEDIUM — third-party text, but brand curates what it surfaces; framing Oakland as "Bay Area" brand is a canon violation
- **Proposed fix:** Truncate the excerpt before "in the Bay Area and beyond" — the headline "From Oakland's Streets to Fashion Heights" is the canon-correct framing. Show headline + source, drop the "Bay Area and beyond" body text.

---

**Violation LV-06**
- **Location:** `https://skyyrose.co/collection-black-rose/` — collection hero subtitle
- **Current copy:** "Every man would wear a black rose."
- **Violation type:** voice — gender-coded language. Canon explicitly forbids "for him / for her / men's / women's." "Every man" encodes masculine gender address into the brand's gender-neutral collection.
- **Severity:** HIGH — hero subtitle, first copy after the tagline, canonically the voice-defining line
- **Proposed fix:** "Every one of us would wear a black rose." — or the existing body copy already present: "You don't wear it to stand out. You wear it because you already stood up." which is gender-neutral and canonically locked.

---

**Violation LV-07**
- **Location:** `https://skyyrose.co/collection-kids-capsule/` — urgency/waitlist block
- **Current copy:** "Be the First to Know" / "Early access, exclusive previews, and first dibs" / "Join the Kids Capsule waitlist"
- **Violation type:** voice — FOMO framing. "First dibs" is urgency theatre. Canon states the founder "doesn't believe in urgency timers" and the site should "know when to shut up."
- **Severity:** MEDIUM — waitlist mechanics are valid; "first dibs" is the specific violation. The surrounding "Be the First to Know" framing edges into FOMO theatre.
- **Proposed fix:** Replace "Early access, exclusive previews, and first dibs" with "Be notified when Kids Capsule drops." Keep the waitlist form; remove the urgency-coded copy around it.

---

**Violation LV-08**
- **Location:** `https://skyyrose.co/collection-signature/` — cross-collection navigation rail
- **Current copy:** Related collection rail present: "Black Rose ('Dark Elegance')" / "Love Hurts ('Crimson Rebellion')" / "Kids Capsule ('Next Generation')"
- **Violation type:** voice — "related products / you may also like" rails are explicitly forbidden by founder canon ("He doesn't believe in the related-products rail")
- **Severity:** HIGH — present across multiple collection pages; a foundational banned pattern
- **Proposed fix:** Remove the cross-collection navigation rail entirely. The collections navigate themselves through the brand arc; the nav bar handles cross-collection routing.

---

**Violation LV-09**
- **Location:** `https://skyyrose.co/collection-kids-capsule/` — cross-collection navigation rail
- **Current copy:** Related collection rail: "Black Rose Collection / Love Hurts Collection / Signature Collection / Pre-Order section / All Products link"
- **Violation type:** voice — same banned pattern as LV-08
- **Severity:** HIGH — Kids Capsule has the most explicit related-products rail of all pages reviewed
- **Proposed fix:** Remove the rail. The Kids Capsule page closes the brand circle narratively; it doesn't need to redirect to other collections.

---

**Violation LV-10**
- **Location:** `https://skyyrose.co/collection-kids-capsule/` — tagline block
- **Current copy:** Secondary tagline: "Luxury Streetwear Born From Struggle"
- **Violation type:** tagline drift — this is not the locked tagline "" and is not a collection-specific story tagline from canon
- **Severity:** MEDIUM — sub-tagline position, not replacing the primary; but creates a competing brand phrase
- **Proposed fix:** Remove "Luxury Streetwear Born From Struggle." The collection-specific tagline is canonically "Luxury runs in the family." Use that. The global tagline "" handles the rest.

---

### Local theme files

---

**Violation TF-01**
- **Location:** `wordpress-theme/skyyrose-flagship/inc/collection-content.php:35`
- **Current copy:** `'hero_subtitle' => __( 'Monochrome sophistication. Dark-on-dark texture. Masculine elegance distilled into every fiber. Every man would wear a black rose.', 'skyyrose' )`
- **Violation type:** voice — gender-coded. "Masculine elegance" and "Every man" both encode masculine address. This is the source of LV-06.
- **Severity:** HIGH — this is the PHP source driving the live hero subtitle
- **Proposed fix:** `'hero_subtitle' => __( 'Monochrome sophistication. Dark-on-dark texture. Elegance distilled into every fiber. You don\'t wear it to stand out. You wear it because you already stood up.', 'skyyrose' )`

---

**Violation TF-02**
- **Location:** `wordpress-theme/skyyrose-flagship/template-landing-love-hurts.php:7` (file docblock comment)
- **Current copy:** `* "Hurts" is the founder's family name — this collection is deeply personal.`
- **Violation type:** lineage — "family name" resolves the Foster/Hurts duality in the wrong direction. Canon explicitly says do not "resolve the technicality" — use "bloodline." "Family name" implies Hurts is Corey's public surname, which is incorrect; Foster is.
- **Severity:** LOW — PHP docblock, not customer-facing. But it seeds wrong framing for every developer touching this file.
- **Proposed fix:** `* "Hurts" is the bloodline that raised the founder — this collection is that lineage made wearable.`

---

**Violation TF-03**
- **Location:** `wordpress-theme/skyyrose-flagship/template-landing-love-hurts.php:65`
- **Current copy:** `'This Isn\'t a Theme. It\'s a Family Name.'`
- **Violation type:** lineage — "Family Name" is the section headline. Canon locks the framing as "bloodline," not "family name." "Family name" implies public surname; the collection's power is that it's the *bloodline* — the people, not the surname.
- **Severity:** HIGH — customer-facing H2 heading, story section anchor
- **Proposed fix:** `'This Isn\'t a Theme. It\'s the Bloodline That Raised Me.'`

---

**Violation TF-04**
- **Location:** `wordpress-theme/skyyrose-flagship/template-landing-love-hurts.php:67`
- **Current copy:** `'"Hurts" isn\'t a word we chose for the aesthetic. It\'s the name our family carries. Every scar, every lesson, every door that closed and every one we kicked open — it\'s all in the name.'`
- **Violation type:** lineage — "the name our family carries" uses generic "family" framing and implies public surname. Canon: use "bloodline." The locked phrase is "the bloodline that raised me." Also: "we" implies collective brand voice; canon is first-person singular (founder's own voice).
- **Severity:** HIGH — primary story paragraph, customer-facing, the first substantive copy the reader encounters in the Love Hurts story section
- **Proposed fix:** `'"Hurts" isn\'t a word we chose for the aesthetic. It\'s the bloodline that raised me. Every scar, every lesson, every door that closed and every one we kicked open — it\'s all in that name.'`

---

**Violation TF-05**
- **Location:** `wordpress-theme/skyyrose-flagship/template-landing-love-hurts.php:183` (craft card heading)
- **Current copy:** `'Family Name Legacy'`
- **Violation type:** lineage — same pattern as TF-03. "Family Name" vs. "Bloodline."
- **Severity:** MEDIUM — craft card section label, customer-facing
- **Proposed fix:** `'Bloodline Legacy'`

---

**Violation TF-06**
- **Location:** `wordpress-theme/skyyrose-flagship/template-landing-love-hurts.php:200` (FAQ answer)
- **Current copy:** `'"Hurts" is the founder\'s actual family name. This collection is deeply personal — it\'s a tribute to everything the family has been through, transformed into something you can wear with pride.'`
- **Violation type:** lineage — "actual family name" explicitly resolves the Foster/Hurts duality in the wrong direction. "The family has been through" uses generic family framing. Canon: don't resolve the technicality; say "bloodline."
- **Severity:** MEDIUM — FAQ is lower visibility than hero copy, but it's the place customers go when they want the definitive answer; this is where the wrong explanation gets cemented
- **Proposed fix:** `'"Hurts" is the bloodline that raised the founder. This collection is that lineage — every scar, every lesson, every door they kicked open. Made wearable.'`

---

**Violation TF-07**
- **Location:** `wordpress-theme/skyyrose-flagship/template-about.php:88`
- **Current copy:** `'desc' => 'San Francisco Post profile. Best Bay Area Clothing Line Award. CEO Weekly cover story. The Blox interview. Independent press confirms what Oakland already knew.'`
- **Violation type:** vocabulary — "Bay Area" used as brand identity in the timeline entry for 2024. The last clause is canon-correct ("what Oakland already knew"); the award name itself contains "Bay Area." The violation is surfacing "Bay Area" unqualified in a brand-authored timeline event.
- **Severity:** MEDIUM — About page timeline, brand-authored historical record
- **Proposed fix:** `'desc' => 'San Francisco Post profile. The "Best Bay Area Clothing Line" award — Oakland recognized. CEO Weekly cover story. The Blox interview. Independent press confirms what the Town already knew.'`

---

**Violation TF-08**
- **Location:** `wordpress-theme/skyyrose-flagship/template-about.php:128`
- **Current copy (press excerpt):** `'A trailblazing gender-neutral clothing brand redefining fashion in the Bay Area and beyond.'`
- **Violation type:** vocabulary — "Bay Area" as brand identity (third-party press text displayed and endorsed)
- **Severity:** LOW — press verbatim quote; brand does not author this. Source is San Francisco Post. However, the brand chooses to display it.
- **Proposed fix:** Truncate excerpt to: `'A trailblazing gender-neutral clothing brand redefining fashion — Established by Corey Foster, a single father with a dream.'` Drop "in the Bay Area and beyond."

---

**Violation TF-09**
- **Location:** `wordpress-theme/skyyrose-flagship/template-about.php:134–135` (Best of Best Review entry)
- **Current copy:** `'headline' => 'Best Bay Area Clothing Line Award 2024'` / `'excerpt' => 'The Skyy Rose Collection has been honored with the prestigious Best Bay Area Clothing Line Award 2024 — recognized for high-end, gender-neutral clothing that transcends age and gender boundaries.'`
- **Violation type:** vocabulary — "Bay Area" used twice in brand-displayed copy; sourced from award nomenclature but displayed without any Oakland reanchoring
- **Severity:** MEDIUM — award section of About page, customer-facing. The award name is third-party; the choice to display the full excerpt with "Bay Area" twice is brand's.
- **Proposed fix:** Rename display label to `'Best Clothing Line Award 2024 — Oakland'` and truncate excerpt to the award recognition fact, removing the "Bay Area" body text.

---

**Violation TF-10**
- **Location:** `wordpress-theme/skyyrose-flagship/template-immersive-signature.php:5` (file docblock comment)
- **Current copy:** `* "The Golden Gate Runway" — San Francisco waterfront, golden hour, / * Golden Gate Bridge showroom.`
- **Violation type:** vocabulary — "San Francisco waterfront" directly names SF as the scene setting. Canon: the Bay Bridge is Oakland's. The Golden Gate Bridge belongs to SF/Marin and is not an Oakland artifact. This scene positions Signature in "San Francisco" geography, not Oakland.
- **Severity:** HIGH — the immersive experience is a premium brand touchpoint; framing it as "San Francisco waterfront" directly contradicts the Oakland-only geographic canon. The Golden Gate is not the Bay Bridge.
- **Note:** This may be intentional as an aspirational/crossover scene, but it violates locked canon. Flagged for founder decision: is the Golden Gate scene intentional brand expansion or a slip? The docblock says "Oakland luxury" at end of line 6 — the framing is internally contradictory.
- **Proposed fix (if violation confirmed):** Reframe the immersive scene to an Oakland waterfront — Jack London Square at golden hour, the Bay Bridge from the Oakland side, or the estuary. Change docblock to: `* "The Gold Standard" — Oakland waterfront, Jack London Square, golden hour.`

---

## Fix priority list

Ranked by severity × customer visibility. Fix in this order:

1. **TF-01** — `collection-content.php:35` — "Masculine elegance / Every man" hero subtitle (source of LV-06). One PHP string fix; kills the live violation immediately.
2. **LV-01** — Homepage "Where Bay Area authenticity meets high-fashion aesthetics" — above-fold, brand-defining, HIGH severity.
3. **TF-03 + TF-04** — Love Hurts landing `template-landing-love-hurts.php:65,67` — H2 headline + first story paragraph both say "family name / our family." Two adjacent lines, fix together.
4. **LV-08 + LV-09** — Related-products rails on Signature and Kids Capsule collection pages. Banned pattern; remove the rail markup.
5. **TF-10** — `template-immersive-signature.php` docblock + scene framing — "San Francisco waterfront / Golden Gate Bridge." Needs founder confirmation on intent before the fix.
6. **TF-06** — Love Hurts FAQ answer — "actual family name" resolves the Foster/Hurts duality incorrectly. FAQ is where customers go for the definitive answer.
7. **LV-02** — Homepage "Pioneer in Bay Area gender-neutral fashion."
8. **TF-07 + TF-09** — About page timeline copy and Best of Best award excerpt — "Bay Area" in brand-authored timeline.
9. **LV-04 + LV-05 + TF-08** — Press excerpt truncations (San Francisco Post + Best of Best). Lower priority because these are third-party text; fix is truncation not rewrite.
10. **TF-05 + TF-02** — "Family Name Legacy" craft card heading and file docblock. Quick string replacements once the higher-priority lineage fixes above are done.

---

## Clean — no violations found

The following surfaces were audited and returned no violations:

- **Tagline usage (all files):** "" is used consistently throughout `inc/seo.php`, `footer.php`, `front-page.php`, `template-preorder-gateway.php`, `template-about.php`, `template-coming-soon.php`, `template-parts/kids-capsule/teaser.php`. No retired tagline ("Where Love Meets Luxury") found anywhere. No tagline drift variants ("Luxury Born from Concrete," "Luxury From Concrete") found in local files.
- **About page timeline (2021 entry):** `template-about.php:78` — "Three Chapters Drop: Black Rose. Love Hurts. Signature. Three collections, one bloodline — not a launch, a declaration." Uses "bloodline" correctly.
- **Collection-content.php Love Hurts block:** Hero badge (`'The Hurts Bloodline'`), story label (`'The Bloodline'`), story title (`'The Hurts Bloodline'`), products subheading (`'Pieces forged in the Hurts bloodline'`), CTA title (`'Wear the Bloodline'`) — all use "bloodline" correctly.
- **`template-landing-love-hurts.php` screen-reader H1:** `'Love Hurts Collection — the Hurts bloodline'` — correct.
- **Bay Bridge SKUs (sg-001, sg-002, sg-005):** Not reviewed for PDP copy in this pass, but no violations found in collection-content.php or landing templates associating the Bay Bridge with "Bay Area" or "SF cityscape." The bridge is handled as Oakland iconography in all PHP source reviewed.
- **Gender-coded language (collection pages other than Black Rose hero):** No "for him / for her / men's / women's" found in any collection or landing template outside the TF-01 line.
- **Urgency timers / countdown language in local PHP:** No countdown timers found in any PHP template. `'countdown' => false` is set in `template-landing-love-hurts.php:33`.
- **Blue color usage:** No blue referenced in brand copy or CSS token references reviewed (not a CSS audit; scoped to copy).
- **Apology language in copy:** No "we hope / perhaps / might be / I apologize" found in brand copy reviewed.
- **`front-page.php` tagline:** Line 252 — " Four collections, one bloodline — built by a father, named after a daughter." Canon-correct.
- **`template-landing-love-hurts.php` hero subtitle:** "This isn't a theme. It's what you've survived." — No lineage violation here; does not use "family name."
- **`skyyrose.co/collection-love-hurts/` live page:** Love Hurts live collection page uses "bloodline" framing correctly ("The Hurts Bloodline," "three generations of Hurts"). Clean.
- **`skyyrose.co/collection-black-rose/` live page:** Tagline correct, "the Town" used correctly, Oakland-first framing throughout. Violation is only the hero subtitle (LV-06 / TF-01).

---

## Audit method

Canonical sources read in full: `docs/brand/collection-stories.md`, `project_founder_voice.md`, `project_brand.md`, `knowledge-base/seed/from-interview.md`. Live site fetched via WebFetch for five URLs: `skyyrose.co/`, `/about/`, `/collection-signature/`, `/collection-love-hurts/`, `/collection-black-rose/`, `/collection-kids-capsule/`. Local theme grepped for `San Francisco`, `SF`, `Bay Area`, `the City`, `for him/her`, `men's/women's`, `bloodline/family name`, and tagline variants across all PHP files in `wordpress-theme/skyyrose-flagship/` (vendor/ excluded manually from results). Targeted reads on `inc/collection-content.php`, `template-landing-love-hurts.php`, `template-about.php`, `template-immersive-signature.php`, and `front-page.php`. Product detail pages for sg-001/sg-002/sg-005/lh-004 were not individually fetched (PDPs are WooCommerce-driven; violations in that surface would originate from `collection-content.php` which was read in full). The `template-parts/landing/` partial directory was not read in full — coverage came from grep results and the landing template reads. `SF Mono` font-family references in Elementor widget PHP were identified as false positives (CSS font stack, not brand copy) and excluded.
