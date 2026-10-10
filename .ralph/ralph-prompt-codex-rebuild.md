# Phase 2 Full Rebuild — Codex Agent

You are Ralph, an autonomous builder. You work in `/Users/theceo/DevSkyy`.
Branch: `phase2-codex-rebuild`. Commit and push after EVERY task.

## Git Protocol

After completing each task:
```bash
cd /Users/theceo/DevSkyy && git add -A && git commit -m "<type>: <description>" && git push origin phase2-codex-rebuild
```

## Credentials (pre-loaded in .env files)

- `.env` — GOOGLE_AI_API_KEY, ANTHROPIC_API_KEY, REPLICATE_API_TOKEN
- `.env.hf` — OPENAI_API_KEY, FAL_KEY, MESHY_API_KEY, TOGETHER_API_KEY
- `.env.wordpress` — SSH credentials (see .env.wordpress, never inline passwords here)
- Theme on server: `/htdocs/wp-content/themes/skyyrose-flagship`

Load keys in Python:
```python
from pathlib import Path
for f in [Path(".env"), Path(".env.hf")]:
    for line in f.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
```

## Brand Constants

- Colors: Rose Gold `#B76E79`, Dark `#0A0A0A`, Silver `#C0C0C0`, Crimson `#DC143C`, Gold `#D4AF37`
- No brand slogan is authorized. (NEVER "Where Love Meets Luxury")
- WordPress API: `index.php?rest_route=` (NOT `/wp-json/`)
- Only theme: `skyyrose-flagship`

---

## TASKS — Execute in order. One commit per task.

### Task 1: Create `template-collections.php`

The `/collections/` page returns 404. Create the missing template.

**Reference**: `template-collection-black-rose.php`, `template-collection-love-hurts.php`, `template-collection-signature.php`, `template-collection-kids-capsule.php` already exist as individual collection pages.

**Requirements**:
- WordPress Template Name: `Collections`
- Display all 4 collections as a grid of cards
- Each card: collection image, name, product count (via `wc_get_products`), link to individual template
- Collections: Black Rose, Love Hurts, Signature, Kids Capsule
- Use existing CSS patterns from `assets/css/collections.css`
- Enqueue in `inc/enqueue.php` if needed
- Mobile responsive (1 col mobile, 2 col tablet, 4 col desktop)

**Commit**: `feat: create template-collections.php with collection grid`

### Task 2: Deduplicate `homepage.css` & `collection-v4.css`

**Files**:
- `assets/css/homepage.css` and `assets/css/homepage-v2.css`
- `assets/css/collection-v4.css` and `assets/css/collections.css`

**Requirements**:
- Diff `homepage.css` vs `homepage-v2.css` — identify shared rules
- Diff `collection-v4.css` vs `collections.css` — identify shared rules
- Extract shared rules into the primary file, remove duplicates from the secondary
- If `homepage.css` is entirely superseded by `homepage-v2.css`, mark it deprecated with a comment at top and remove its enqueue
- Regenerate `.min.css` for any changed files using `csso` or `cleancss` (check which is in node_modules)
- Do NOT delete files — only deduplicate and deprecate

**Commit**: `refactor: deduplicate homepage and collection CSS files`

### Task 3: Fix mobile nav two-tap dropdown

**Files**: `header.php`, `assets/js/navigation.js`

**Problem**: On mobile, dropdown menu items require two taps — first tap opens the dropdown, second tap follows the link. Should be: tap opens dropdown with sub-items visible, tap on sub-item follows that link. Parent items that have children should toggle the dropdown only (not navigate).

**Requirements**:
- Read `header.php` to understand the `wp_nav_menu` structure
- Read `assets/js/navigation.js` for the current mobile menu JS
- Fix: parent menu items with children → tap toggles submenu, does NOT navigate
- Fix: child menu items (leaves) → tap navigates immediately
- Add `aria-expanded` toggle for accessibility
- Test: ensure desktop hover behavior is NOT affected (CSS `:hover` still works)
- Regenerate `navigation.min.js`

**Commit**: `fix: mobile nav dropdown two-tap behavior`

### Task 4: Build product compositing script — `scripts/composite_products.py`

Composite actual product photos INTO the immersive scene backgrounds using FAL AI Bria Product Shot API.

**API**: `fal-ai/bria/product-shot`
- Endpoint: `https://queue.fal.run/fal-ai/bria/product-shot`
- Auth: `FAL_KEY` from `.env.hf` (format: `key_id:key_secret`)
- Cost: ~$0.04/image
- Input: product image URL or base64 + scene description OR reference scene image
- Output: composited image URL

**Install fal-client first**:
```bash
source .venv-imagery/bin/activate && pip install fal-client
```

**Product-to-Scene Mapping** (use `-front-model.webp` images as product source):

BLACK ROSE scenes (`assets/scenes/black-rose/`):
- `black-rose-rooftop-garden-v2.png` background:
  - `br-006-front-model.webp` → "draped over arm of black lounge chair, left side"
  - `br-001-front-model.webp` → "folded on seat of low-profile couch, center-left"
  - `br-002-front-model.webp` → "folded on side table next to planter, center-right"
  - `br-004-front-model.webp` → "hanging from matte black clothing rack, right side"

LOVE HURTS scenes (`assets/scenes/love-hurts/`):
- `love-hurts-cathedral-rose-chamber-v2.png` background:
  - `lh-005-front-model.webp` → "draped beside enchanted rose glass dome, center-left"
  - `lh-001-front-model.webp` → "hung from gothic candelabra stand, right"
  - `lh-003-front-model.webp` → "displayed on stone ledge in stained glass alcove, center"

SIGNATURE scenes (`assets/scenes/signature/`):
- `signature-golden-gate-showroom-v2.png` background:
  - `sg-012-front-model.webp` → "hanging on wall-mounted clothing rack, left"
  - `sg-005-front-model.webp` → "featured on center marble display table"
  - `sg-007-front-model.webp` → "on marble pedestal, left-center"
  - `sg-011-front-model.webp` → "hanging on wall-mounted clothing rack, right"

**Script requirements**:
```python
# scripts/composite_products.py
# Usage:
#   source .venv-imagery/bin/activate
#   python scripts/composite_products.py --scene black-rose-rooftop-garden
#   python scripts/composite_products.py --all
#   python scripts/composite_products.py --list
```
- Load FAL_KEY from `.env.hf`
- For EACH product in a scene:
  1. Read the product image from disk
  2. Read the scene background from disk
  3. Call `fal-ai/bria/product-shot` with the product image and a scene description referencing the background
  4. Save the composited result to `assets/scenes/{collection}/{scene}-{product-sku}.webp`
- After ALL products for a scene are composited individually, create a FINAL composite:
  - Use the scene background
  - Overlay all individual product composites at their described positions
  - Save as `assets/scenes/{collection}/{scene}-final.webp` and `.png`
- Add `--dry-run` flag to preview without API calls
- Add retry logic (3 attempts, 8s delay)
- Log costs per image and total

**Commit**: `feat: add product compositing script using FAL AI Bria`

### Task 5: Run the compositing script

```bash
source .venv-imagery/bin/activate
python scripts/composite_products.py --all
```

- Verify output images exist and are >50KB each
- Open and visually verify (mention in commit what you see)

**Commit**: `feat: generate composited product scenes for all 3 collections`

### Task 6: Update immersive templates with composited scenes

Update the 3 immersive templates to use the new composited scene images as backgrounds instead of the plain scenes.

**Files**:
- `template-immersive-black-rose.php`
- `template-immersive-love-hurts.php`
- `template-immersive-signature.php`

**Requirements**:
- Change room background `image` URLs to point to the `-final.webp` composited versions
- Keep the hotspot beacon overlay system — beacons should still appear at product positions
- When a beacon is clicked, show the product detail modal with the actual product photos (front-model, back-model, branding views)
- Verify the `skyyrose_immersive_product()` function references match actual product SKUs on disk
- Add `loading="lazy"` and `decoding="async"` to scene background images

**Commit**: `feat: update immersive templates with composited product scenes`

### Task 7: Deploy to WordPress.com via SFTP

Upload all changed theme files to the live server.

```bash
# Use lftp for reliable SFTP upload
lftp -u "$SFTP_USER","$SFTP_PASS" sftp://"$SFTP_HOST" -e "
  mirror --reverse --verbose --only-newer \
    wordpress-theme/skyyrose-flagship/ \
    /htdocs/wp-content/themes/skyyrose-flagship/;
  quit"
```

If `lftp` is not installed: `brew install lftp` or use `scp -r`.

**Verify**: `curl -sI https://skyyrose.co | head -5` should return 200.

**Commit**: `chore: deploy phase 2 rebuild to production`

### Task 8: Verify live site

```bash
# Check pages respond
curl -sI "https://skyyrose.co" | head -1
curl -sI "https://skyyrose.co/?page_id=0&preview=true" | head -1
curl -sI "https://skyyrose.co/index.php?rest_route=/wp/v2/pages" | head -1

# Check scene images load
curl -sI "https://skyyrose.co/wp-content/themes/skyyrose-flagship/assets/scenes/black-rose/black-rose-rooftop-garden-v2-final.webp" | head -1
```

**Commit**: `chore: verify live deployment — all pages responding`

---

## DONE

When ALL 8 tasks are complete, output: <promise>COMPLETE</promise>
