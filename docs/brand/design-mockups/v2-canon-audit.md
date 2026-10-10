# v2.html Brand Canon Audit
**File**: `docs/brand/design-mockups/v2.html`
**Audit date**: 2026-05-25
**Auditor**: Brand Guardian
**Canon sources checked**: `docs/brand/visual-references.md`, `docs/brand/collection-stories.md`, `docs/brand/asset-hierarchy.md`, `docs/brand/corey-questions.md`, `docs/brand/canon-audit-2026-05-23.md`, `~/.claude/projects/-Users-theceo-DevSkyy/memory/feedback_collection_lockup_assets.md`, `~/.claude/projects/-Users-theceo-DevSkyy/memory/feedback_collection_canon_attribution.md`

---

## Summary

| ID | Severity | Section | Category | Finding |
|----|----------|---------|----------|---------|
| P0-A | P0 | `#br-cover` | Photo asset | `beauty-and-beast-*.webp` (Love Hurts env) on Black Rose surface |
| P0-B | P0 | `#home-hero` | Photo asset | `luxury-nighttime-*.webp` (Signature env) under `br-brand-script` (Black Rose lockup) |
| P1-A | P1 | `#home-cover` | Photo asset | `forbidden-midnight-*.webp` (Black Rose env) under brand-wide masthead and tagline |
| P1-B | P1 | `#br-cover` | Copy / voice | Invented tagline "Built for those who move through darkness like it's home." — no canon source |
| P1-C | P1 | `#br-cover`, `#br-voice` | Palette | BR accent uses `--sr-rose-gold` (#B76E79); canon = Silver `#C0C0C0` |
| P2-A | P2 | `#br-spread` | Asset scope | Tier 2 collection brand marks used as product tile photography |

---

## Audit by Category

### 1. Photo Assets

#### `#home-cover` (lines 532–570)
- Background: `forbidden-midnight-*.webp`
- `forbidden-midnight` = Black Rose hero env per `asset-hierarchy.md`
- Surface intent: brand-wide homepage cover (masthead "SKYY ROSE", tagline "", no collection attribution)
- **P1-A**: The Black Rose-exclusive photo env is used under brand-wide content. If this section represents the homepage cover (not BR collection page), the photo env should be brand-neutral or a homepage-specific asset. If intent is "homepage opens on the BR drop story", document that rationale explicitly and lock it. Currently ambiguous against the asset-hierarchy rule.

#### `#home-hero` (lines 571–612)
- Background: `luxury-nighttime-*.webp`
- Lockup overlay: `br-brand-script.png`
- `luxury-nighttime` = Signature hero env per `asset-hierarchy.md`
- `br-brand-script.png` = Black Rose Tier 2 collection mark
- **P0-B**: Signature photo env crossed with Black Rose lockup on the same surface. Two different collections' hero assets combined. Asset-hierarchy is explicit: `luxury-nighttime` is Signature-only. This frame must use `forbidden-midnight-*.webp` (or another BR-sanctioned asset) as its background.

#### `#br-cover` (lines 677–715)
- Background: `beauty-and-beast-*.webp`
- **P0-A (pre-identified)**: `beauty-and-beast` = Love Hurts hero env per `asset-hierarchy.md`. Confirmed violation. The Black Rose collection cover must use `forbidden-midnight-*.webp`.

#### `#br-hero` (lines 716–764)
- Background: `forbidden-midnight-*.webp`
- Lockup: `br-brand-script.png` delivered as `<picture>` with AVIF/WebP/PNG srcset
- **PASS**: Correct BR env, correct BR lockup, correct delivery format.

---

### 2. Collection Lockup Usage

#### `#home-cover`
- Masthead "SKYY ROSE" rendered in Cinzel 700 type
- **PASS**: "SKYY ROSE" is the brand masthead (not a collection name). Per `feedback_collection_lockup_assets.md`, the only permitted type-rendered hero-tier element is the brand masthead "SKYY ROSE" in Cinzel. This is correct.

#### `#home-hero`
- Lockup: `br-brand-script.png` as `<picture>` AVIF/WebP/PNG
- **PASS** (lockup format only): The lockup is delivered as an image, not type-rendered. Format is correct.
- **FAIL** (surface): See P0-B above — the background env is wrong for this surface.

#### `#br-hero`
- Lockup: `br-brand-script.png` as `<picture>` AVIF/WebP/PNG
- **PASS**: Correct lockup, correct format, correct surface.

#### `#home-spread` (lines 623–674)
- Tiles use: `black-rose-logo-hero.webp`, `love-hurts-logo-hero.webp`, `signature-logo-hero.webp`, `skyy-rose-collection-circular-patch.webp`
- These are Tier 2 collection marks per `asset-hierarchy.md`
- Labels: Collection 02 (BR), 03 (LH), 01 (SIG), 04 (KC)
- Collection numbering matches catalog: SIG=01, BR=02, LH=03, KC=04
- **PASS**: Correct marks, correct collection numbers, correct scope for a homepage spread featuring all collections.

---

### 3. Copy and Voice Attribution

#### `#home-cover`
- No brand slogan is authorized. — brand-wide canon ✓
- Byline: "By Corey Foster · Oakland · 2026" — founder voice, Oakland anchor ✓
- Meta: "VOL. IV / S/S 2026 / THE TOWN · DROP 01" — brand-wide civic identifier ✓
- **PASS**

#### `#home-hero`
- Kicker: "For The Town" — brand-wide civic line ✓
- **PASS** (copy only; photo violation is P0-B above)

#### `#home-voice`
- Quote: "Named after / a daughter. / Built by a father."
- Attribution: "Corey Foster · The Town"
- Brand-wide origin line per `feedback_collection_canon_attribution.md` ✓
- **PASS**

#### `#br-cover`
- Masthead: "BLACK ROSE" — collection name, correct surface ✓
- Tagline: "Built for those who move through / darkness like it's home."
- **P1-B**: This line does not appear in `collection-stories.md`, `corey-questions.md`, or any canon source. Verified BR verbatim canon lines are:
  - "You wear it because you already stood up."
  - "A black rose is a posture."
  - "Every piece in Black Rose is the concrete answering back."
  - "The beauty of the color black through the rose and high-end fashion design."
  - "You already stood up. Black Rose is the one that shows it."
  The cover tagline must be replaced with a verbatim canon line or founder-locked new copy. Do not use AI-drafted paraphrase.

#### `#br-hero`
- Kicker: "A black rose is a posture" — verbatim BR canon ✓
- Subtitle: "Vol. IV · Spring 2026 · The Town" — no collection mixing ✓
- **PASS**

#### `#br-voice`
- Quote: "You wear it / because you / already stood up."
- Attribution: "Black Rose · The Town · 2026"
- Verbatim BR canon per `collection-stories.md` ✓
- **PASS**

#### `#br-spread` product labels
- Products: br-001 ($180), br-004 ($240), br-005 ($320), br-008 ($260)
- All four SKUs exist in canonical catalog (`wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`)
- No LH, SIG, or KC copy on BR pages ✓
- **PASS**

---

### 4. Palette Per Surface

#### CSS token definitions (lines 17–62)
```css
--sr-rose-gold: #B76E79;
--sr-silver: #C0C0C0;
--sr-crimson: #DC143C;
--sr-gold: #D4AF37;
--sr-dark: #0A0A0A;
```
All brand palette tokens defined correctly.

#### `#br-cover` and `#br-voice` accent usage
- `.cover__tagline-accent` uses `--sr-rose-gold`
- `.voice__quote .line-2` uses `--sr-rose-gold`
- **P1-C**: Black Rose collection accent = Silver `#C0C0C0` per `collection-stories.md` ("Black Rose: Silver `#C0C0C0`"). Rose Gold is the brand-wide / Kids Capsule accent. No BR surface should use `--sr-rose-gold` for accent elements. Replace with `--sr-silver` on all BR-specific surfaces.

#### `#home-cover` and `#home-voice`
- Brand-wide surfaces using `--sr-rose-gold` as accent
- Rose Gold = brand-wide / Kids Capsule ✓
- **PASS**

---

### 5. Reference Set Check

#### Meta description (line 8)
- "Locked direction: Kith × Oaklandish × Culture Kings × Fear of God × Palm Angels. Not a production page."
- All five canonical references named ✓
- No locked-out brands named ✓

#### Markup and class names throughout
- No reference to Bottega Veneta, Numéro, Hedi Slimane, Rick Owens (visual), Acne FW24, Givenchy by Tisci, 032c, Off-White, Burberry Imagined, Khaite, Bode, or The Row in markup, comments, or asset names
- **PASS**

---

### 6. Founder Voice Register

#### Geographic anchors
- "Oakland", "The Town", "East Oakland" used throughout
- No "Bay Area" references (consistent with Oakland-anchor preference)
- **PASS**

#### Attribution format
- "By Corey Foster · Oakland · 2026" — staff-engineer register, direct ✓
- "Corey Foster · The Town" — same register ✓
- No urgency timers, no promotional superlatives ✓
- **PASS**

#### Brand sport patch context (`#br-hero`)
- NFL / NBA / MLB / Hockey patches used — founder-canon for Black Rose collection ✓
- **PASS**

---

## Asset Scope Concern

### `#br-spread` product tiles (P2-A)
- Tiles use: `black-rose-logo-hero.webp`, `black-rose-logo.webp`, `black-rose-monogram-sr.jpg`, `black-rose-logo-hero-transparent.png`
- Per `asset-hierarchy.md`, Tier 2 collection marks are scoped to "Collection page hero" use
- Product tiles require actual product photography (SKU-specific imagery from Elite Studio pipeline)
- Using brand marks as product photography conflates brand identity assets with product catalog assets
- **P2-A**: Flagged as placeholder content concern. For mockup purposes this is acceptable. Before any production use, replace with real product photography from the Elite Studio render pipeline (br-001, br-004, br-005, br-008 SKUs).

---

## Verdict by Section

| Section | Photo | Lockup | Copy | Palette | Result |
|---------|-------|--------|------|---------|--------|
| `#home-cover` | P1-A | PASS | PASS | PASS | Conditional pass |
| `#home-hero` | P0-B | PASS | PASS | PASS | Fail |
| `#home-voice` | N/A | N/A | PASS | PASS | Pass |
| `#home-spread` | N/A | PASS | PASS | PASS | Pass |
| `#br-cover` | P0-A | N/A | P1-B | P1-C | Fail |
| `#br-hero` | PASS | PASS | PASS | PASS | Pass |
| `#br-voice` | N/A | N/A | PASS | P1-C | Conditional pass |
| `#br-spread` | N/A | P2-A | PASS | PASS | Conditional pass |

---

## Required Fixes (by priority)

### P0 — Must fix before any production or stakeholder use

1. **P0-A**: Replace `#br-cover` background from `beauty-and-beast-*.webp` to `forbidden-midnight-*.webp`
   - `<source media="(min-width: 768px)" srcset="forbidden-midnight-landscape.avif 1x, forbidden-midnight-landscape@2x.avif 2x" type="image/avif">`
   - Match the `<picture>` pattern already used in `#br-hero`

2. **P0-B**: Replace `#home-hero` background from `luxury-nighttime-*.webp` to `forbidden-midnight-*.webp` (or a brand-wide hero env if one is created)
   - Alternatively, if the intent is a Signature collection feature on the homepage hero, replace the lockup from `br-brand-script.png` to `signature-logo-hero.webp` — but only if homepage positioning has been revisited with founder sign-off

### P1 — Fix before stakeholder review or founder sign-off pass

3. **P1-B**: Replace `#br-cover` tagline with verbatim canon line. Recommended: "Every piece in Black Rose is the concrete answering back." (from `collection-stories.md`). Alternatively, request a new founder-locked line — do not draft a paraphrase.

4. **P1-C**: Replace `--sr-rose-gold` accent on all BR surfaces (`#br-cover`, `#br-voice`) with `--sr-silver` (`#C0C0C0`)

5. **P1-A**: Clarify homepage cover photo intent with founder. If the homepage is always a BR drop-specific surface, lock `forbidden-midnight` as intentional. If homepage should be brand-neutral, create or designate a brand-wide hero env and update `asset-hierarchy.md` with the decision + date stamp.

### P2 — Fix before any production implementation

6. **P2-A**: Replace Tier 2 brand mark placeholders in `#br-spread` with actual product photography from Elite Studio pipeline (br-001, br-004, br-005, br-008)

---

## Canon Integrity Score

| Category | Pass | Conditional | Fail |
|----------|------|-------------|------|
| Photo assets | 2 | 1 | 2 |
| Lockup usage | 4 | 0 | 0 |
| Copy / voice | 6 | 0 | 1 |
| Palette | 5 | 1 | 1 |
| Reference set | 2 | 0 | 0 |
| Founder voice | 3 | 0 | 0 |

2 P0 violations, 3 P1 violations, 1 P2 concern. Core passes (voice, lockup format, reference set) are solid. Failures are concentrated in photo-env assignment and one invented copy line.
