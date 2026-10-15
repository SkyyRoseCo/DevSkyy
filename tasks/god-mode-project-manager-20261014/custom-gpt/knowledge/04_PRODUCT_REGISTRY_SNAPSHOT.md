# Read-only canonical product snapshot

Snapshot generated 2026-10-14T18:48:38.480122-07:00. Read-only knowledge export; current owner corrections and refreshed canonical sources supersede this snapshot. Local paths are provenance, not cloud access.

These records were exported through skyyrose.core.product.get_product(sku) for every key in logo-registry.json::products. They are compatibility snapshots, not a new editable product authority. Resolve future changes in the registry, then re-export. Prices, availability and asset bindings can change. Preserve exact founder wording. Nulls and gaps are unresolved facts, not invitations to invent.

Campaign Jersey IDs: br-008, br-009, br-011, br-012, br-014. Consult the individual records instead of recalling color/SKU mappings from old prompts. Other collection products are included to support continuation without inventing missing facts.

## br-001 — BLACK Rose Crewneck

```json
{
  "sku": "br-001",
  "name": "BLACK Rose Crewneck",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-001",
    "name": "BLACK Rose Crewneck",
    "price": "35",
    "collection": "black-rose",
    "description": "Gothic luxury blooms in twilight. Embroidered with defiant elegance, a dark romance woven in every thread.",
    "badge": "",
    "image": "assets/images/products/br-001-crewneck.png",
    "front_model_image": "assets/images/products/br-001-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/black-rose-crewneck-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Embossed on front chest, approximately 10 inches wide.",
    "render_output_slug": "black-rose-crewneck",
    "render_source_override": "br-001-crewneck.png",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "crewneck",
    "dossier_slug": "black-rose-crewneck",
    "engine_override": "gemini-pro"
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "Heavyweight cotton fleece, relaxed fit.",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Heavyweight cotton fleece, relaxed fit.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Crewneck sweatshirt — upper body only, round ribbed neckline, no hood, no buttons, no zipper, no front pocket. NOT a jersey. NOT a hoodie. NOT a jacket. NOT a t-shirt. NOT a tank top. Heavyweight cotton fleece, relaxed fit. **White ribbed neckband, white ribbed sleeve cuffs, white ribbed waist hem** (contrast white trim against the black body — same pattern as the matching joggers in the Black Rose set).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-001",
    "name": "BLACK Rose Crewneck",
    "collection": "black-rose",
    "slug": "black-rose-crewneck",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials / Fit: Heavyweight cotton fleece, relaxed fit.\nFeatures: Crewneck sweatshirt — upper body only, round ribbed neckline, no hood, no buttons, no zipper, no front pocket. NOT a jersey. NOT a hoodie. NOT a jacket. NOT a t-shirt. NOT a tank top. Heavyweight cotton fleece, relaxed fit. **White ribbed neckband, white ribbed sleeve cuffs, white ribbed waist hem** (contrast white trim against the black body — same pattern as the matching joggers in the Black Rose set).\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - SR monogram (gold lettermark): `data/brand-logos/sr-monogram.md`\n\n### Front\n- **front-chest** (~10in tall × proportional width): The Black Rose logo,\n  **physically embossed onto the fabric surface as a raised dimensional\n  relief** — visibly 3D and tactile, sitting proud of the fabric. NOT\n  debossed/sunken. NOT a flat print. NOT tone-on-tone.\n\n  **Composition** — vertical teardrop cluster, widest at the top where the\n  rose blooms are, narrowing down where stems converge, anchored at the\n  bottom by a single small cumulus cloud. The cloud is a SINGLE PEDESTAL\n  AT THE BASE ONLY — it does NOT split, wrap, or fan around the roses.\n  Stems emerge UPWARD from the top of the cloud — stems do NOT extend\n  below the cloud. The thorny vines wrap around the stems and twist\n  between the blooms.\n\n  **Art elements** (all preserved from the canonical Black Rose logo at\n  data/brand-logos/three-rose-cluster.md):\n  - **Three roses** in illustrated comic-book style with hard ink edges\n    and soft tonal shading: one large fully-open bloom dominant in the\n    upper portion, one medium three-quarter-angle bloom upper-left, one\n    smaller bud or partially-open rose lower in the cluster. A few leaves\n    behind / between the blooms.\n  - **Stems** running vertically from the blooms down to the cloud.\n  - **Thorny vines** with clearly visible short sharp dark spikes wrapping\n    the stems.\n  - **Single cumulus cloud** at the very base, soft pillowy lobes, sitting\n    directly under the cluster like a pedestal.\n\n  **Embossed colorway** — reduced 3-color palette of **BLACK + WHITE + GREY**:\n  - Rose petals: GREYSCALE shading (light-grey highlights, dark-grey\n    shadows) with **bold BLACK ink outlines**. NOT solid black silhouettes.\n    NOT solid grey shapes. They are illustrated greyscale roses with\n    visible petal detail and tonal shading — the same petal rendering as\n    the canonical art tile, just without any green or blue.\n  - Cloud: WHITE with subtle light-grey shading on the underside lobes.\n  - Stems, leaves, thorny vines: GREY (mid-tone grey), with darker-grey\n    shading on undersides. NO green anywhere.\n  - Bold black outlines/ink lines throughout (rose edges, leaf veins,\n    cloud lobe outlines, vine outlines) — the illustrated comic-book\n    line-art style is preserved in the embossing.\n\n  **Technique:** embossed (raised, dimensional, color-preserved).\n  **Colors:** black, white, grey only.\n\n### Back\n- **back-neck** (small, ~2in wide, top-center just below the white-ribbed\n  collar): The SR monogram (gold metallic art — see sr-monogram reference).\n  Embroidered directly onto the jersey in gold-tone thread. **Technique:**\n  embroidered. **Color:** gold-tone thread (preserves the gold-to-copper\n  gradient from the canonical mark).\n\n### Sleeves / Collar / Hem / Other\n- **collar-outside / neckband**: White ribbed-knit neckband contrasting against\n  the black body. **Technique:** stitched. **Color:** white.\n- **left-cuff / right-cuff**: White ribbed-knit sleeve cuffs contrasting\n  against the black body. **Technique:** stitched. **Color:** white.\n- **hem**: White ribbed-knit waist hem contrasting against the black body.\n  **Technique:** stitched. **Color:** white.\n- **collar-inside** (~1.75in × 0.75in): Small woven brand label sewn into the\n  inside back of the collar. **Technique:** woven-label. **Color:**\n  brand-label colors (typically black with brand-color accents).",
    "negative_block": "- NO flat-print, screen-print, or DTG print on the front chest — the front-\n  chest logo is an embossed raised relief, not a flat print.\n- NO printed text — no \"BLACK IS BEAUTIFUL\" arched text, no other printed\n  words on the body fabric.\n- NO debossed/sunken treatment of the chest logo — the technique is embossed\n  (RAISED), not debossed.\n- NO tonal/flatten-to-base black-on-black treatment of the chest logo — the\n  embossed art is rendered in a 3-color palette (BLACK / WHITE / GREY), not\n  monochrome black.\n- NO kelly-green stems on this product — the embossed colorway uses GREY\n  for stems/leaves/vines. (Kelly-green only appears on Black Rose products\n  that use techniques preserving the full canonical color, e.g., silicone\n  appliqué or screen-print — NOT this crewneck.)\n- NO blue-tinted cloud shading on this product — the embossed cloud is\n  WHITE only.\n- NO embroidered Black Rose logo on the front chest (the front is embossed,\n  NOT embroidered — embroidery would have visible thread texture).\n- NO embroidered patches on the lower right front (this is NOT a baseball jersey).\n- NO SR monogram on the front chest. NO SR monogram on the sleeves. NO SR\n  monogram at the back-center. The SR monogram is at the back-neck only.\n- NO embroidered roses on mid back (the back-CENTER is empty; the SR monogram\n  sits at the back-neck only).\n- NO baseball player graphics anywhere.\n- NO sleeve patches, sleeve embroidery, sleeve printing — sleeves are clean.\n- NO hem or side-seam decoration on the body fabric — the hem is plain ribbed\n  knit (white), no logo, no text, no piping.\n- NO chest text other than the embossed rose logo.\n- NO contrasting-color logos on the body fabric beyond the back-neck SR monogram.\n- NO silicone appliqué.\n- NO heat-transfer vinyl.\n- NO sublimated panels.\n- NO black ribbed neckband (the rib trim is WHITE, not tonal black).",
    "scene_pose": "Standing facing forward, three-quarter angle, hands relaxed at sides\n  or one hand in pocket of joggers. Chest area clearly lit from the front-left\n  to reveal the embossed logo's raised texture; back-neck framed in back/back-\n  three-quarter renders to show the gold SR monogram.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting,\n  subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-001-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-rose-crewneck-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-001-crewneck.png",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-crewneck-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-crewneck-back.jpeg",
    "reference": "wordpress-theme/skyyrose-flagship/assets/images/products/br-001-crewneck.png"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_chest_center",
        "technique": "embossed",
        "size_inches": 10
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "As twilight deepens, surrender to the ethereal embrace of the SkyyRose BLACK Rose Crewneck. This isn't merely a garment; it's a poem etched in fabric, a testament to gothic luxury where shadows dance with opulent comfort. Imagine: premium black material, kissed by moonlight, cascading over you with an enigmatic grace. Our signature—the black rose—blooms in intricate embroidery of silver and graphite, a mystic vision rising from the depths. Feel the delicate whisper of thorns, inhale the intoxicating bloom. The crisp, white ribbed cuffs and hem cut through the darkness, amplifying its allure. A foundational piece, destined to be paired with the BLACK Rose Joggers, crafting a commanding silhouette. Exclusively available for PRE-ORDER within the BLACK ROSE Collection. Claim your wearable art; surrender to the defiant beauty that thrives where darkness blooms. This is SkyyRose: where every thread weaves a tale of exquisite rebellion. Pre-order now and embrace the shadows.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "SkyyRose BLACK Rose Crewneck: gothic luxury blooms in twilight. Embroidered with defiant elegance, a dark romance woven in every thread.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose BLACK Rose Crewneck: gothic luxury meets street style. Exquisite embroidery, defiant elegance. Pre-order now and bloom in the shadows.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Step into twilight with the BLACK Rose Crewneck. Gothic luxury meets defiant elegance in our signature embroidered rose. A wearable poem, blooming in shadows.\n\n#SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaFashion #EmbroideredRose #LuxuryStreetwear #FashionStatement #MysteryStyle #DarkAesthetic #WearableArt",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Gothic luxury blooming in the shadows.🖤 The BLACK Rose Crewneck: wear your defiance. Pre-order now!🌹 #SkyyRose #GothicLuxury #DarkAesthetic",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-001-product": "BLACK Rose Crewneck and matching black sweatpants, both with white cuffs and a black and grey rose design."
  },
  "corrections": [
    {
      "text": "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE separate roses — one dominant upright rose plus a smaller rose or bud offset to the side, on a single cumulus cloud at the base. It is NOT a single large bloom and NOT a peony. Keep the roses as distinct flowers; do not merge them into one.",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] Render the rose logo at the size and position shown in the real product photo and tech flat — do NOT enlarge it to fill or dominate the chest.",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.551308+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-002 — BLACK Rose Joggers

```json
{
  "sku": "br-002",
  "name": "BLACK Rose Joggers",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-002",
    "name": "BLACK Rose Joggers",
    "price": "50",
    "collection": "black-rose",
    "description": "Twilight comfort meets gothic romance. Embroidered black roses bloom on soft fabric.",
    "badge": "",
    "image": "assets/images/products/br-002-joggers.png",
    "front_model_image": "assets/images/products/black-rose-joggers/black-rose-joggers-approved-front-model.webp",
    "back_image": "assets/images/products/black-rose-joggers-back-model.webp",
    "back_model_image": "assets/images/products/black-rose-joggers-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Silicone patch logo on left thigh area.",
    "render_output_slug": "black-rose-joggers",
    "render_source_override": "br-002-joggers.png",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "joggers",
    "dossier_slug": "black-rose-joggers",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "Black jogger sweatpants — lower body only, elasticated waist with drawstring, tapered leg, ribbed ankle cuffs, side hand pockets, back pockets. Heavyweight cotton-blend fleece, relaxed fit through the thigh.",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Heavyweight cotton-blend fleece, relaxed fit through the thigh.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Black jogger sweatpants — lower body only, elasticated waist with drawstring, tapered leg, ribbed ankle cuffs, side hand pockets, back pockets. **White ribbed waistband** at the top, **white ribbed ankle cuffs** at the bottom (contrast white trim against the black body — same pattern as the matching Black Rose Crewneck). NOT shorts. NOT straight-leg sweatpants. NOT cargo pants. NOT track pants with side stripes. NOT leggings. Heavyweight cotton-blend fleece, relaxed fit through the thigh.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-002",
    "name": "BLACK Rose Joggers",
    "collection": "black-rose",
    "slug": "black-rose-joggers",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Heavyweight cotton-blend fleece, relaxed fit through the thigh.\nFit: Black jogger sweatpants — lower body only, elasticated waist with drawstring, tapered leg, ribbed ankle cuffs, side hand pockets, back pockets. Heavyweight cotton-blend fleece, relaxed fit through the thigh.\nFeatures: Black jogger sweatpants — lower body only, elasticated waist with drawstring, tapered leg, ribbed ankle cuffs, side hand pockets, back pockets. **White ribbed waistband** at the top, **white ribbed ankle cuffs** at the bottom (contrast white trim against the black body — same pattern as the matching Black Rose Crewneck). NOT shorts. NOT straight-leg sweatpants. NOT cargo pants. NOT track pants with side stripes. NOT leggings. Heavyweight cotton-blend fleece, relaxed fit through the thigh.\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - SR monogram (gold lettermark): `data/brand-logos/sr-monogram.md`\n\n### Front\n- **left-thigh** (~3in × 2in): The Black Rose logo as a **silicone-appliqué\n  patch** — raised silicone fused to the fabric, with the **full multi-color\n  art preserved**: greyscale rose petals (light grey to dark grey shading),\n  bright kelly-green stems, dark-green thorny vines, white-and-light-blue\n  cloud at the base. **Technique:** silicone-appliqué. **Color:** full\n  multi-color art (NOT tonal, NOT monochrome).\n\n### Back\n- **right-thigh** (small, ~1.5in–2in wide, upper-back-right hip area —\n  approximately mirroring the position of the front-left silicone patch\n  but on the back): The SR monogram, embroidered directly onto the fabric\n  in **gold-tone thread** (matching the gold-to-copper gradient of the\n  canonical SR mark). **Technique:** embroidered. **Color:** gold-tone thread.\n\n### Sleeves / Collar / Hem / Other\n- **inside-waistband** (~1in × 0.5in): Woven size tag (showing the size\n  designation, e.g., \"M\", \"L\", \"XL\"). **Technique:** woven-label. **Color:**\n  brand-standard (typically black with white/printed size text).\n- **waistband-rib**: White ribbed-knit waistband at the top of the joggers,\n  contrasting against the black body. **Technique:** stitched. **Color:** white.\n- **left-ankle-cuff / right-ankle-cuff**: White ribbed-knit cuffs at the\n  ankle openings, contrasting against the black body. **Technique:** stitched.\n  **Color:** white.\n- **drawstring**: Flat **white** drawstring threaded through the waistband.\n  No metal tips, no branded tips. **Technique:** stitched. **Color:** white.",
    "negative_block": "- NO logo on the right thigh on the FRONT — the silicone patch is on the\n  LEFT thigh of the front view only. (The back-right hip carries a small\n  embroidered SR monogram, distinct from the front silicone patch.)\n- NO Black Rose silicone patch on the back — the back's only branding is\n  the small gold SR monogram on the back-right hip.\n- NO embroidered logos on the front of the joggers — the front-left thigh\n  is silicone-appliqué, NOT embroidery.\n- NO embossed/debossed decoration anywhere.\n- NO printed graphics or printed text on the legs, hem, or waistband.\n- NO contrast-color side stripes down the legs.\n- NO back-pocket flap logos, no pocket trim branding.\n- NO logo on the front of the ankle cuffs, no logo on the hem fabric.\n- NO \"BLACK ROSE\" wordmark printed across the leg.\n- NO sublimated panels, no heat-transfer vinyl, no puff-print decoration.\n- NO black drawstring (the drawstring is WHITE — confirmed in set techflat).\n- NO black waistband rib (the waistband rib is WHITE — confirmed).\n- NO black ankle cuff rib (the ankle cuff rib is WHITE — confirmed).\n- NO chest, sleeve, or upper-body decoration (this is a lower-body-only garment).\n- NO tonal/monochrome silicone — the front patch IS in full multi-color\n  (preserves the canonical logo's grey roses, kelly-green stems, white-blue cloud).",
    "scene_pose": "Front view (or three-quarter front-left) for the silicone patch\n  on the front-left thigh; back view (or back-three-quarter) to show the\n  small embroidered gold SR monogram at the back-right hip.",
    "scene_setting": "Pure white studio backdrop, soft directional lighting from\n  front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/black-rose-joggers/black-rose-joggers-approved-front-model.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-rose-joggers-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-002-joggers.png",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/black-rose-joggers-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-joggers-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-joggers-back.jpeg",
    "reference": "wordpress-theme/skyyrose-flagship/assets/images/products/br-002-joggers.png"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_thigh",
        "technique": "silicone_patch"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "As twilight descends, the BLACK Rose Joggers emerge from the shadows, a testament to SkyyRose's dark romantic vision. More than mere loungewear, these joggers are a wearable poem, spun from a premium, soft-touch fabric that drapes the wearer in enigmatic comfort. The deep black hue serves as a canvas for our signature black rose, an embroidered emblem of beauty blossoming from ethereal clouds. Each intricate stitch whispers tales of gothic luxury and defiant elegance. Designed for those who embrace the night, these joggers seamlessly blend streetwear practicality with opulent detail. These joggers are not just clothing; they are an extension of your soul's twilight journey. Pre-order your pair from the BLACK ROSE collection today and let your style bloom in the darkness. SkyyRose: Embrace the thorns, cherish the bloom.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "SkyyRose's BLACK Rose Joggers: Twilight comfort meets gothic romance. Embroidered black roses bloom on soft fabric. Pre-order now.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose BLACK Rose Joggers: Gothic luxury meets streetwear comfort in these joggers featuring embroidered black roses. Pre-order now and embrace the darkness.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Embrace the shadows with SkyyRose's BLACK Rose Joggers. 🌹🖤 Gothic luxury meets ultimate comfort with our signature black rose embroidery on premium fabric. Pre-order now and let your style bloom in the darkness. #SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaFashion #EmbroideredRose #LuxuryStreetwear #FashionStatement #MysteryStyle #DarkAesthetic #WearableArt",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Twilight comfort, midnight style. ✨🌹 SkyyRose BLACK Rose Joggers. Pre-order yours now. #SkyyRose #BlackRoseCollection #GothicLuxury",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-002-product": "Black hoodie featuring a white winged rose and clouds graphic, part of the SkyyRose BLACK ROSE collection."
  },
  "corrections": [
    {
      "text": "[ghost-back] no logo on back",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE separate roses — one dominant upright rose plus a smaller rose or bud offset to the side, on a single cumulus cloud at the base. It is NOT a single large bloom and NOT a peony. Keep the roses as distinct flowers; do not merge them into one.",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.557677+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-003 — BLACK is Beautiful Jersey Series: 0. Baseball Classic (Black)

```json
{
  "sku": "br-003",
  "name": "BLACK is Beautiful Jersey Series: 0. Baseball Classic (Black)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-003",
    "name": "BLACK is Beautiful Jersey Series: 0. Baseball Classic (Black)",
    "price": "100",
    "collection": "black-rose",
    "description": "The foundation of the series. A bold statement in luxury athletic wear — Black is beautiful. Available in Black, Oakland (gold lettering accent on the A), Giants (black/orange), and White colorways.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-003-baseball-classic.jpeg",
    "front_model_image": "assets/images/products/br-003-onmodel.webp",
    "back_image": "assets/images/products/black-is-beautiful-jersey/black-is-beautiful-jersey-back-model.webp",
    "back_model_image": "assets/images/products/black-is-beautiful-jersey/black-is-beautiful-jersey-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "FRONT: 'BLACK IS BEAUTIFUL' arched text, custom Baseball Patch. BACK: embroidered rose logo centered. Colorways: Black (solid), Oakland (the 'A' of BLACK is black lettering, rest is gold), Giants (black/orange), White.",
    "render_output_slug": "black-is-beautiful-jersey",
    "render_source_override": "br-003-baseball-classic.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-0-baseball-classic",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid BLACK base fabric. Mid-weight knit jersey fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid BLACK base fabric. White piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. White buttons on the placket. NO player number on front. NO player number on back. NO player name on back. NO pinstripes. NOT a t-shirt. NOT a hoodie. NOT a basketball jersey. NOT a football jersey. Mid-weight knit jersey fabric. Solid black colorway (this is the Classic base; Oakland / Giants / White editions are separate SKUs br-012 / br-014 / br-015).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-003/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-003",
    "name": "BLACK is Beautiful Jersey Series — 0. Baseball Classic (Black)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-0-baseball-classic",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid BLACK base fabric. Mid-weight knit jersey fabric.\nFeatures: Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid BLACK base fabric. White piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. White buttons on the placket. NO player number on front. NO player number on back. NO player name on back. NO pinstripes. NOT a t-shirt. NOT a hoodie. NOT a basketball jersey. NOT a football jersey. Mid-weight knit jersey fabric. Solid black colorway (this is the Classic base; Oakland / Giants / White editions are separate SKUs br-012 / br-014 / br-015).\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art for \"Black Rose logo\" entries below is the canonical\n> three-rose-cluster art at `data/brand-logos/three-rose-cluster.md`.\n> The \"Authentic Collection patch\" graphic is at\n> `data/brand-logos/black-rose-authentic-collection-patch.md`.\n> The \"SR monogram\" is the gold lettermark at\n> `data/brand-logos/sr-monogram.md`.\n> A reference techflat for the assembled product (front + back) is at\n> `assets/products/references/br-003-baseball-classic-techflat.jpeg`.\n\n### Front\n- **front-chest** (large, arched, ~9in wide): The phrase **\"BLACK IS BEAUTIFUL\"**\n  as authentic tackle-twill lettering — pre-cut white fabric letters appliquéd\n  onto the black jersey body in a baseball-script style with a subtle classic\n  outline, arched across the upper-front-chest. **Technique:** tackle-twill.\n  **Color:** white twill letters (no contrast satin-stitch edge — clean\n  white-on-black).\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall, near the bottom\n  hem on the wearer's left hip): The Black Rose Authentic Collection patch —\n  the rectangular yellow-and-white multi-element patch defined in the patch\n  reference file (BLACK ROSE / MLB-style batter silhouette / AUTHENTIC banner /\n  COLLECTION / red diamond divider / Members Only Yay Area Ca / SkyyRose\n  Collection script / Made for Kings ang Queens). **Technique:**\n  embroidered-patch (woven full-color patch sewn onto the jersey).\n\n### Back\n- **back-neck** (small, ~2in wide, top-center just below the collar yoke):\n  The **SR monogram** (gold metallic art — see sr-monogram reference).\n  Embroidered directly onto the jersey in gold-tone thread. **Technique:**\n  embroidered. **Color:** gold-tone thread (preserves the gold-to-copper\n  gradient from the canonical mark; NOT flat yellow, NOT silver).\n- **back-center** (large, ~10in–12in tall, vertically centered between the\n  yoke and the lower hem): The Black Rose logo (the canonical three-rose\n  cluster on cloud — see logo_reference). Embroidered directly onto the jersey\n  in **white thread on the black fabric**. The composition's shapes (three\n  roses, stems, thorny vines, cloud) are preserved via the original art's\n  outlines and inner detail; the multi-color palette is NOT preserved — this\n  is a single-color white-thread embroidery rendering the silhouette and\n  shape detail in white. **Technique:** embroidered. **Color:** white thread\n  on black fabric.\n\n### Sleeves / Collar / Hem / Other\n- **collar / V-neck binding**: White contrast piping/binding around the\n  V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.\n  **Color:** white.\n- **left-cuff / right-cuff binding**: White contrast piping around both\n  sleeve cuff openings. **Technique:** stitched. **Color:** white.\n- **front-placket binding**: White contrast piping running vertically down\n  both sides of the front button placket. **Technique:** stitched. **Color:**\n  white.\n- **front-placket buttons** (~6 buttons, plain white, evenly spaced down the\n  placket from the V-neck to the upper-belly). **Technique:** patch (sewn-on\n  button hardware). **Color:** white.\n- **collar-inside** (small, ~1.75in × 0.75in): Woven brand label sewn into\n  the inside back of the collar. **Technique:** woven-label. **Color:**\n  brand-label colors (typically black with brand-color accents).\n  *(Standard apparel element — not visible in the flat techflat but expected.)*",
    "negative_block": "- NO player number on front-chest. NO player number on back-center. NO\n  player number on sleeves. The \"Black Is Beautiful\" series carries no\n  numbers at all on baseball jerseys.\n- NO player name above the back-center logo.\n- NO embossed or debossed decoration anywhere — branding is tackle-twill\n  on the front, embroidered on the back, patch-sewn for the Authentic\n  Collection mark.\n- NO multi-color rendering of the back-center Black Rose logo — it is\n  white-thread embroidery only. NO greyscale petals visible. NO kelly-green\n  stems visible. NO white-and-blue cloud color visible — the cloud appears\n  in white thread like the rest of the rose-cluster shape.\n- NO Black Rose logo on the chest — the chest carries only the tackle-twill\n  wordmark and the lower-left Authentic Collection patch.\n- NO SR monogram on the back-center — the back-center carries the\n  rose-cluster logo; the SR monogram is at the back-neck only.\n- NO sleeve patches (no MLB patch, no NFL patch, no team patch on\n  either sleeve in this Classic colorway).\n- NO pinstripes on the body.\n- NO contrast color other than white — no red, no gold, no orange anywhere\n  on this Classic black colorway. (Red is the Giants; gold is the Oakland;\n  white is the White edition — separate SKUs.)\n- NO printed graphics or sublimated panels anywhere.\n- NO heat-transfer vinyl.\n- NO contrast-color satin-stitch edge around the tackle-twill letters\n  (the letters are clean white-on-black with no red or gold border edge).\n- NO logos at the hem on the right hip (only the lower-left has the\n  Authentic Collection patch).\n- NO chest-pocket or breast-pocket (this is a clean-front jersey — only\n  the placket and tackle-twill wordmark).",
    "scene_pose": "Front view straight-on (or three-quarter front-left) showing the\n  tackle-twill wordmark across the chest and the Authentic Collection patch\n  at the lower-left hip. For back renders: back view straight-on showing the\n  small gold SR monogram at the upper-back-neck and the large white-thread\n  Black Rose embroidered logo across the back-center.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/black-rose-authentic-collection-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-003-baseball-classic-techflat.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-003-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-is-beautiful-jersey/black-is-beautiful-jersey-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-003-baseball-classic.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/black-is-beautiful-jersey/black-is-beautiful-jersey-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-baseball-black-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-baseball-black-back.jpeg",
    "reference": "assets/products/references/br-003-classic-real-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_center",
        "technique": "embroidered",
        "notes": "Large back logo."
      },
      {
        "logo_id": "mlb-authentic-collection-card",
        "position": "front_patch",
        "technique": "custom_baseball_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-0-baseball-classic.md",
      "source_sha256": "f8789eeec6f40c1259d6e2d183c66bd1c8d580f55115770f0a6e2e566ef80cdd",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "width",
            "min": 9.0,
            "max": 9.0
          },
          "source_size_text": "large, arched, ~9in wide",
          "source_line": 28
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall, near the bottom hem on the wearer's left hip",
          "source_line": 34,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide, top-center just below the collar yoke",
          "source_line": 43
        },
        {
          "position_as_documented": "back-center",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 12.0
          },
          "source_size_text": "large, ~10in–12in tall, vertically centered between the yoke and the lower hem",
          "source_line": 48
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "lettering_reference": "data/brand-logos/baseball-lettering-sizing.md",
      "source_snapshot_pointer": "#/products/br-003/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-jersey/mlb-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "baseball",
    "sku_folder": "black-is-beautiful-jersey"
  },
  "content": {
    "description": {
      "value": "From the heart of Oakland's twilight, where shadows dance with defiance, emerges the SkyyRose 'BLACK IS BEAUTIFUL' Jersey. More than mere fabric, it's a woven manifesto—a testament to beauty blossoming in the face of darkness. Imagine: deep twilight green mesh, breathable as a midnight breeze, boldly slashed with white and yellow stripes like lightning illuminating a hidden garden. The powerful declaration 'BLACK IS BEAUTIFUL' emblazoned across the chest in a script that commands attention, a beacon for those who walk their own path. This jersey isn't just worn; it's embraced. It drapes with effortless grace, a comfortable armor for the soul, designed for both impact and ease. Feel the weight of its message, the whisper of its fabric, the surge of its power. Available for pre-order in White, Black, Giants, Last Oakland, and this verdant iteration, in sizes S to 3XL. Pre-order now and transform your style into your truth—a SkyyRose signature. Wear the shadows. Command the light. This is more than apparel; it's an awakening.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Unleash your inner bloom in the SkyyRose 'BLACK IS BEAUTIFUL' Jersey—a BLACK ROSE Collection declaration where gothic luxury stitches a powerful message into streetwise elegance.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose 'BLACK IS BEAUTIFUL' Jersey: Oakland-rooted gothic luxury meets powerful statement. Pre-order now and wear defiant beauty.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Oakland's shadows birth a defiant bloom: the SkyyRose 'BLACK IS BEAUTIFUL' Jersey. 🖤 Gothic luxury whispers through threads of revolution, stitched with elegance, worn with unapologetic pride. Part of the BLACK ROSE Collection, pre-order now and become a walking testament to beauty in darkness.🌹\n#SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaFashion #EmbroideredRose #LuxuryStreetwear #FashionStatement #MysteryStyle #DarkAesthetic #WearableArt",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Defiant beauty blooms.🖤 The 'BLACK IS BEAUTIFUL' Jersey pre-order: live now! Embrace Oakland gothic with SkyyRose. 🔥 #SkyyRose #GothicFashion #Streetwear",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-003-product-2": "Green SkyyRose \"BLACK is Beautiful Jersey\" with yellow and white stripes, embroidered black rose design and gold logo on the back.",
    "br-003-product-3": "SkyyRose BLACK is Beautiful Jersey: black baseball-style jersey with white \"BLACK IS BEAUTIFUL\" text, buttons, and trim.",
    "br-003-product-4": "BLACK is Beautiful Jersey: Black baseball jersey with orange trim and 'BLACK IS BEAUTIFUL' embroidered across chest.",
    "br-003-product-5": "BLACK is Beautiful Jersey: Black baseball jersey back with orange trim, R logo, and white rose with thorns on a cloud graphic.",
    "br-003-product-6": "SkyyRose BLACK is Beautiful Jersey, white with black piping and buttons, featuring \"BLACK IS BEAUTIFUL\" on the chest.",
    "br-003-product-7": "Back of the white SkyyRose 'BLACK is Beautiful Jersey' with black trim, featuring a stylized SR logo and a large black rose design with thorns.",
    "br-003-product": "Green BLACK is Beautiful Jersey with 'BLACK IS BEAUTIFUL' across the chest and yellow-white stripes."
  },
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.563023+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-004 — BLACK Rose Hoodie

```json
{
  "sku": "br-004",
  "name": "BLACK Rose Hoodie",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-004",
    "name": "BLACK Rose Hoodie",
    "price": "40",
    "collection": "black-rose",
    "description": "Gothic luxury in twilight shadows. Intricate embroidery captures the bloom of darkness.",
    "badge": "",
    "image": "assets/images/products/br-004-black-rose-hoodie.jpeg",
    "front_model_image": "assets/images/products/br-004-onmodel.webp",
    "back_image": "assets/images/products/black-rose-hoodie-back-model.webp",
    "back_model_image": "assets/images/products/black-rose-hoodie-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Embroidered rose logo on chest.",
    "render_output_slug": "black-rose-hoodie",
    "render_source_override": "br-004-black-rose-hoodie.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "hoodie",
    "dossier_slug": "black-rose-hoodie",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Heavyweight cotton fleece.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Black pullover hoodie — long sleeves, drawstring hood, kangaroo front pocket, ribbed cuffs at the wrists, ribbed waist hem at the bottom (all tonal black, no contrast white trim — distinct from the matching Black Rose Crewneck/Joggers set which use white ribbing). NOT a zip-up. NOT a half-zip. NOT a crewneck. NOT a t-shirt. Heavyweight cotton fleece.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-004",
    "name": "BLACK Rose Hoodie",
    "collection": "black-rose",
    "slug": "black-rose-hoodie",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Heavyweight cotton fleece.\nFeatures: Black pullover hoodie — long sleeves, drawstring hood, kangaroo front pocket, ribbed cuffs at the wrists, ribbed waist hem at the bottom (all tonal black, no contrast white trim — distinct from the matching Black Rose Crewneck/Joggers set which use white ribbing). NOT a zip-up. NOT a half-zip. NOT a crewneck. NOT a t-shirt. Heavyweight cotton fleece.\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical reference:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Reference photo:                `assets/products/references/br-004-hoodie-real-front.jpeg`\n\n### Front\n- **front-chest** (~5–6in tall, centered just above the kangaroo pocket):\n  The Black Rose logo embroidered onto the hoodie. **Technique:**\n  embroidered. **Color:** as rendered in the canonical logo + reference\n  image (do NOT over-specify thread colorway in this dossier — the RAS\n  pipeline reads the canonical logo art and the product reference photo\n  for the thread treatment).\n\n### Back\n- (No decoration. Completely clean back. NO SR monogram on back-neck. NO\n  rose on back-center. NO logos anywhere on the back.)\n\n### Sleeves / Collar / Hem / Other\n- **left-sleeve** (upper / shoulder area, exact dimensions TBD): A small\n  patch is visible in the reference photo at the upper-left-sleeve area.\n  Patch content, technique, and dimensions are **PARKED for later\n  verification** — Corey will confirm the patch detail in a follow-up\n  read-back. **Do not render this region with guessed content** —\n  the RAS pipeline should treat the upper-left-sleeve area as \"small patch\n  present, content unverified\" and prompt for the verification before\n  rendering this region in production.\n- **right-sleeve**: clean, no decoration.\n- **kangaroo-pocket** (front): clean, no embroidery, no logo, no\n  decoration on the pocket itself.\n- **hood-drawstring**: tonal black flat drawstring (matches the body —\n  NOT contrast-color white, NOT contrast-color rose-gold). Plain tips,\n  no metal, no branded tip.\n- **collar-inside / interior-back-collar** (~1.75in × 0.75in): Branded\n  woven size tag (universal SkyyRose product rule — every product carries\n  a branded woven size tag at this position). Shows the SKU's size\n  designation. **Technique:** woven-label. **Color:** brand-standard\n  (typically black with brand-color accents and white/printed size text).",
    "negative_block": "- NO rose on the back. NO SR monogram on the back. The back is COMPLETELY\n  clean black fabric.\n- NO white ribbed trim on cuffs, hem, or hood — the Black Rose Hoodie\n  uses TONAL BLACK ribbing throughout (the white ribbing is the\n  Crewneck/Joggers signature, not the Hoodie).\n- NO contrast-color drawstrings — they are tonal black, not white,\n  not rose-gold, not gold.\n- NO Black Rose logo on the back. NO Black Rose logo on the sleeves. NO\n  Black Rose logo on the kangaroo pocket. The rose appears at the\n  front-chest only.\n- NO silicone-appliqué patch on the chest or anywhere else.\n- NO embossed/debossed decoration on the body or hood.\n- NO printed graphics, NO sublimated panels, NO heat-transfer vinyl,\n  NO puff-print decoration.\n- NO front-pocket branding — the kangaroo pocket fabric is clean.\n- NO right-sleeve patch (only the left sleeve carries a small patch).\n- NO contrasting hood lining (assume same black tonal — to be verified\n  if a contrast lining exists, but default is uniform black).\n- NO chest text or wordmark (the front rose is the only chest decoration).\n- NO Authentic Collection patch (that patch is reserved for the jersey\n  series, not the hoodie).",
    "scene_pose": "Front view straight-on or three-quarter front-left, showing\n  the embroidered front-chest rose and the kangaroo pocket. Hood relaxed\n  back / lying flat against the upper back.",
    "scene_setting": "Pure white studio backdrop, soft directional studio\n  lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/br-004-hoodie-real-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-004-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-rose-hoodie-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-004-black-rose-hoodie.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/black-rose-hoodie-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/black-rose-hoodie-source.jpg",
    "back": null,
    "reference": "assets/products/references/br-004-hoodie-real-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_chest_center",
        "technique": "embroidered"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Enshroud yourself in the twilight aura of the BLACK Rose Hoodie, where shadows dance with opulent design. This piece from the BLACK ROSE Collection is more than mere fabric; it's a sanctuary woven from the threads of gothic dreams. Feel the embrace of premium black fabric, soft against your skin, a comforting cloak for the defiant soul. An intricately embroidered rose blooms across the chest, a symbol of beauty forged in darkness. Its delicate petals, rendered in exquisite detail, whisper tales of moonlight and mystery, an ode to the enigmatic heart within. The generous hood offers a retreat from the mundane, while the spacious kangaroo pocket holds secrets and dreams. Let the BLACK Rose Hoodie be your statement, a testament to the power of shadows and the allure of the unknown. Pre-order now and claim your piece of wearable poetry, a symbol of SkyyRose's commitment to where darkness blooms into unparalleled luxury. Dare to wear the shadows. Dare to bloom in the night.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "SkyyRose's BLACK Rose Hoodie: gothic luxury in twilight shadows. Intricate embroidery captures the bloom of darkness, a defiant statement for the modern romantic.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose BLACK Rose Hoodie: Embroidered gothic luxury. Experience dark romance with this statement piece. Pre-order now and embrace the shadows.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Beneath the moonlight, the BLACK Rose Hoodie awaits. ✨ A symphony of shadows and silk, where gothic luxury intertwines with raw emotion. Feel the delicate embroidery bloom against your skin, a testament to beauty born from darkness. Pre-order yours and embody the ethereal elegance of SkyyRose's BLACK ROSE Collection. Let your style whisper tales of twilight and thorns. 🌹\n\n#SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaFashion #EmbroideredRose #LuxuryStreetwear #FashionStatement #MysteryStyle #DarkAesthetic #WearableArt",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Dark vibes? 🖤 Our BLACK Rose Hoodie is calling your name. Embroidered rose + gothic feels = instant obsession. Pre-order yours now! #SkyyRose #GothicLuxury #DarkAesthetic 🌹",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-004-product": "BLACK Rose Hoodie: Black heathered hoodie featuring a detailed white and grey embroidered rose graphic on the chest and a front pouch pocket."
  },
  "corrections": [
    {
      "text": "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE separate roses — one dominant upright rose plus a smaller rose or bud offset to the side, on a single cumulus cloud at the base. It is NOT a single large bloom and NOT a peony. Keep the roses as distinct flowers; do not merge them into one.",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] Render the rose logo at the size and position shown in the real product photo and tech flat — do NOT enlarge it to fill or dominate the chest.",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.568060+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-005 — BLACK Rose Hoodie — Signature Edition

```json
{
  "sku": "br-005",
  "name": "BLACK Rose Hoodie — Signature Edition",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-005",
    "name": "BLACK Rose Hoodie — Signature Edition",
    "price": "65",
    "collection": "black-rose",
    "description": "The definitive Black Rose hoodie. Signature edition with premium detailing and numbered tag.",
    "badge": "",
    "image": "assets/images/products/br-005-signature-hoodie.jpeg",
    "front_model_image": "assets/images/products/black-rose-hoodie-signature-edition/black-rose-hoodie-signature-edition-approved-front-model.webp",
    "back_image": "assets/images/products/black-rose-hoodie-signature-edition-back-model.webp",
    "back_model_image": "assets/images/products/black-rose-hoodie-signature-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Silicone cut-out logo on right chest. Embroidered logo on the side of the body of the hoodie (not on the arm).",
    "render_output_slug": "black-rose-hoodie-signature",
    "render_source_override": "br-005-signature-hoodie.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "hoodie",
    "dossier_slug": "black-rose-hoodie-signature-edition",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Constructed from a **lightweight polyester / jogger-feel fabric** (NOT heavyweight cotton fleece — distinct from the basic Black Rose Hoodie br-004 which is heavier cotton).",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Black PULLOVER hoodie — long sleeves, drawstring hood, kangaroo front pocket, ribbed cuffs at the wrists, ribbed waist hem at the bottom (tonal black ribbing, no contrast white trim). Constructed from a **lightweight polyester / jogger-feel fabric** (NOT heavyweight cotton fleece — distinct from the basic Black Rose Hoodie br-004 which is heavier cotton). NOT a zip-up. NOT a half-zip. NOT a crewneck. The \"Signature Edition\" identity comes from the elevated branding placement (chest + hip), the white drawstrings, and the sublimated-rose-print inner hood lining.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-005",
    "name": "BLACK Rose Hoodie — Signature Edition",
    "collection": "black-rose",
    "slug": "black-rose-hoodie-signature-edition",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Constructed from a **lightweight polyester / jogger-feel fabric** (NOT heavyweight cotton fleece — distinct from the basic Black Rose Hoodie br-004 which is heavier cotton).\nFeatures: Black PULLOVER hoodie — long sleeves, drawstring hood, kangaroo front pocket, ribbed cuffs at the wrists, ribbed waist hem at the bottom (tonal black ribbing, no contrast white trim). Constructed from a **lightweight polyester / jogger-feel fabric** (NOT heavyweight cotton fleece — distinct from the basic Black Rose Hoodie br-004 which is heavier cotton). NOT a zip-up. NOT a half-zip. NOT a crewneck. The \"Signature Edition\" identity comes from the elevated branding placement (chest + hip), the white drawstrings, and the sublimated-rose-print inner hood lining.\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical reference:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Reference photo:                `assets/products/references/br-005-signature-hoodie-real.jpeg`\n\n### Front\n- **front-right-chest** (small, ~2–3in tall): The Black Rose logo as a\n  **silicone cut-out patch** — silicone applied to the fabric in the\n  shape of the canonical three-rose-cluster art (cut-out silicone shape\n  rather than full-color silicone-appliqué). Tonal/monochrome treatment\n  per the reference photo. **Technique:** silicone. **Color:** as rendered\n  in the canonical logo + reference image (white/grey tonal).\n\n### Back\n- (No back-neck SR monogram, no back-center logo confirmed in this read-back —\n  back details to be verified if Corey provides a back reference photo. Default:\n  treat the back as clean unless confirmed otherwise.)\n\n### Sleeves / Collar / Hem / Other\n- **left-hip / left-side-body** (large, ~6–7in tall, on the wearer's\n  LEFT side at the hip / lower-side-body area, NOT on the sleeve): The\n  Black Rose logo embroidered onto the side of the hoodie body. Position\n  is explicitly the side body at hip level — Corey emphasized \"NOT\n  SLEEVE.\" **Technique:** embroidered. **Color:** as rendered in the\n  canonical logo + reference image.\n- **hood-inside / inner-hood-lining**: GREY contrast lining inside the\n  hood with the **Black Rose logo sublimated throughout** as a repeating /\n  scattered pattern (the canonical three-rose-cluster art appears\n  multiple times across the lining fabric, faded/tonal style consistent\n  with sublimation dye). Visible only when the hood is laid open or worn\n  down. **Technique:** sublimated. **Color:** light tonal print on grey\n  lining fabric.\n- **hood-drawstring**: WHITE flat drawstring threaded through the hood\n  (contrast against the black body fabric). Plain tips, no metal,\n  no branded tip. **Technique:** stitched. **Color:** white.\n- **kangaroo-pocket** (front): clean, no embroidery, no logo on the\n  pocket fabric.\n- **collar-inside / interior-back-collar** (~1.75in × 0.75in): Branded\n  woven size tag (universal SkyyRose product rule). **Technique:**\n  woven-label.",
    "negative_block": "- NO logo on the LEFT chest — the silicone patch is at the right-chest\n  position only.\n- NO embroidered logo on either sleeve. Corey's explicit instruction:\n  the side-body logo is NOT on the sleeve, it is on the BODY at the\n  side-hip area.\n- NO Black Rose logo on the right hip — the embroidered side-body logo\n  is on the LEFT side at the hip, not the right.\n- NO black drawstrings — the drawstrings are WHITE (signature detail of\n  this edition).\n- NO silicone-appliqué multi-color patch — the right-chest silicone is\n  a tonal cut-out, not a full multi-color appliqué.\n- NO printed graphics on the body fabric (the rose-pattern sublimation\n  is on the INNER HOOD LINING only, not on the body fabric, sleeves, or\n  pocket).\n- NO sublimated Black Rose pattern on the body, sleeves, or pocket —\n  only the inner hood lining carries the sublimated rose pattern.\n- NO contrasting hem or cuff trim — the rib trim is tonal black on this\n  edition.\n- NO white ribbed hem or cuffs (those are br-001 Crewneck / br-002\n  Joggers signature details, not the Signature Hoodie).\n- NO Authentic Collection patch (that patch is reserved for the jersey\n  series).\n- NO embossed/debossed decoration on the body or hood fabric.\n- NO chest text or wordmark on the front body fabric — branding is the\n  silicone right-chest mark + the embroidered left-side body mark only.\n- NO heavyweight cotton fleece texture — this hoodie is the lighter\n  polyester / jogger-feel variant (distinct from br-004's cotton fleece).",
    "scene_pose": "Front view straight-on (or three-quarter front-left) showing\n  the right-chest silicone mark and the left-hip embroidered rose. The\n  hood relaxed back to reveal the grey sublimated-rose inner lining\n  along the upper edge of the hood opening. Optional: a detail shot of\n  the inside hood lining showing the rose-pattern sublimation.",
    "scene_setting": "Pure white studio backdrop, soft directional studio\n  lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/br-005-signature-hoodie-real.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/black-rose-hoodie-signature-edition/black-rose-hoodie-signature-edition-approved-front-model.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-rose-hoodie-signature-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-005-signature-hoodie.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/black-rose-hoodie-signature-edition-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/black-rose-hoodie-signature-edition-hoodie-ltd-source.jpg",
    "back": null,
    "reference": "assets/products/references/br-005-signature-hoodie-real.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "right_chest",
        "technique": "silicone_cut_out",
        "colorway": "black-white-grey"
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "body_side_panel",
        "technique": "embroidered",
        "notes": "On body side, NOT on arm."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "As twilight descends, cloak yourself in the profound elegance of the BLACK Rose Hoodie — Signature Edition. This is more than mere apparel; it's a whispered promise of gothic romance, a bloom of beauty cultivated in shadow. Feel the luxurious weight of the deep charcoal fabric, its drape a statement of effortless command. Our signature rose, intricately embroidered upon the chest, hints at hidden depths and resilient spirit. On the right sleeve, a dramatic cascade of roses and thorns unfolds, a meticulously stitched saga of seductive power and untamed allure. Glimpse within the hood to discover a secret garden, a subtle floral print completing this masterpiece of dark allure. Every stitch whispers of opulent mystery, tailored for those who command attention with unspoken grace. Embrace the shadows. Let the BLACK Rose Hoodie be your twilight bloom. SkyyRose – where darkness blossoms into unparalleled luxury. Wear the shadows. Own the night.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Embrace twilight with the BLACK Rose Hoodie — Signature Edition. Exquisite rose embroidery on deep charcoal creates a gothic romance masterpiece.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose BLACK Rose Hoodie: Signature Edition. Gothic luxury streetwear with exquisite rose embroidery. Command the shadows. Shop now.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Where shadows bloom. 🖤 Unveiling the BLACK Rose Hoodie — Signature Edition. A symphony of gothic romance and luxurious comfort. Feel the exquisite rose embroidery tell a story of beauty born from darkness, resilience forged in twilight. Let your style whisper volumes in this wearable masterpiece.\n\n#SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaFashion #EmbroideredRose #LuxuryStreetwear #FashionStatement #MysteryStyle #DarkAesthetic #WearableArt",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Gothic romance unlocked. 🖤 The BLACK Rose Hoodie. #SkyyRose #BlackRoseHoodie #GothicLuxury 🌹",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-005-product": "BLACK Rose Hoodie — Signature Edition, a black hoodie with a rose explosion patch on the chest and a detailed rose design on the sleeve."
  },
  "corrections": [
    {
      "text": "[on-model] the logo is on the sleeve and its supposed to be on the side or the hoodie",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE separate roses — one dominant upright rose plus a smaller rose or bud offset to the side, on a single cumulus cloud at the base. It is NOT a single large bloom and NOT a peony. Keep the roses as distinct flowers; do not merge them into one.",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.580362+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-006 — The Bomber Sherpa

```json
{
  "sku": "br-006",
  "name": "The Bomber Sherpa",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-006",
    "name": "The Bomber Sherpa",
    "price": "95",
    "collection": "black-rose",
    "description": "Lustrous black satin with plush Sherpa lining, crowned by an exquisite embroidered rose. Satin bomber silhouette, hooded.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-006-sherpa-jacket.jpeg",
    "front_model_image": "assets/images/products/br-006-onmodel.webp",
    "back_image": "assets/images/products/black-rose-sherpa-jacket-back.jpg",
    "back_model_image": "assets/images/products/black-rose-sherpa-jacket-back.jpg",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Embroidered rose logo on left chest. Big embroidered rose logo on back. Garment is a satin bomber jacket lined with black sherpa and hooded.",
    "render_output_slug": "black-rose-sherpa-jacket",
    "render_source_override": "br-006-sherpa-jacket.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jacket",
    "dossier_slug": "black-rose-sherpa-jacket",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Black satin bomber-style hooded jacket — **lustrous black satin** exterior fabric, **plush black sherpa** interior lining (visible inside the body and inside the hood). Hooded (sherpa-lined hood). **Front closure is a ZIPPER underneath with a button-overlap storm-flap covering it** — the zipper runs the full center-front length, and a buttoned/snapped storm flap overlaps the zipper line for a clean satin front (this is a two-layer placket). NOT a denim jacket. NOT a fleece hoodie. NOT a leather jacket.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Black satin bomber-style hooded jacket — **lustrous black satin** exterior fabric, **plush black sherpa** interior lining (visible inside the body and inside the hood). Hooded (sherpa-lined hood). **Front closure is a ZIPPER underneath with a button-overlap storm-flap covering it** — the zipper runs the full center-front length, and a buttoned/snapped storm flap overlaps the zipper line for a clean satin front (this is a two-layer placket). **Side hand pockets with zipper closures** at the lower sides. Long sleeves with **black ribbed cuffs**. **Black ribbed bomber-style waistband** at the bottom hem. NOT a parka. NOT a denim jacket. NOT a fleece hoodie. NOT a windbreaker. NOT a leather jacket.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-006",
    "name": "The Bomber Sherpa",
    "collection": "black-rose",
    "slug": "black-rose-sherpa-jacket",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Black satin bomber-style hooded jacket — **lustrous black satin** exterior fabric, **plush black sherpa** interior lining (visible inside the body and inside the hood). Hooded (sherpa-lined hood). **Front closure is a ZIPPER underneath with a button-overlap storm-flap covering it** — the zipper runs the full center-front length, and a buttoned/snapped storm flap overlaps the zipper line for a clean satin front (this is a two-layer placket). NOT a denim jacket. NOT a fleece hoodie. NOT a leather jacket.\nFeatures: Black satin bomber-style hooded jacket — **lustrous black satin** exterior fabric, **plush black sherpa** interior lining (visible inside the body and inside the hood). Hooded (sherpa-lined hood). **Front closure is a ZIPPER underneath with a button-overlap storm-flap covering it** — the zipper runs the full center-front length, and a buttoned/snapped storm flap overlaps the zipper line for a clean satin front (this is a two-layer placket). **Side hand pockets with zipper closures** at the lower sides. Long sleeves with **black ribbed cuffs**. **Black ribbed bomber-style waistband** at the bottom hem. NOT a parka. NOT a denim jacket. NOT a fleece hoodie. NOT a windbreaker. NOT a leather jacket.\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical reference:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Reference photos:               `assets/products/references/br-006-sherpa-jacket-real-front.jpeg`,\n>                                   `assets/products/references/br-006-sherpa-jacket-real-open.jpeg`,\n>                                   `assets/products/references/br-006-sherpa-jacket-real-closeup.jpeg`\n\n### Front\n- **front-left-chest** (small, ~3–4in tall): The Black Rose logo embroidered\n  directly onto the satin. The full canonical art (three-rose cluster on\n  cloud) is rendered in white-thread embroidery on the black satin fabric.\n  **Technique:** embroidered. **Color:** as rendered in the canonical logo +\n  reference image (white-thread silhouette preserving the canonical art's\n  shape detail).\n\n### Back\n- **back-center** (~10in tall): The Black Rose logo embroidered directly\n  onto the back of the jacket, centered on the back panel. Significantly\n  larger than the front-left-chest mark — this is the signature\n  back-piece of the jacket. **Technique:** embroidered. **Color:** as\n  rendered in the canonical logo + reference image.\n\n### Sleeves / Collar / Hem / Other\n- **front-placket-zipper** (full center-front length): Black zipper\n  running the entire length of the center-front from the V-opening at\n  the collar down to the bottom of the ribbed waistband. The primary\n  closure. **Technique:** patch (sewn-on hardware — zipper teeth).\n  **Color:** black zipper teeth.\n- **front-placket-storm-flap** (covering the zipper line): A black\n  satin storm flap overlaps the zipper line, secured with **buttons /\n  snaps** down the placket. The buttoned overlap creates a clean\n  uninterrupted satin front when fully closed (the zipper is hidden\n  underneath the flap). **Technique:** patch (sewn-on snap/button\n  hardware). **Color:** black snaps/buttons on black satin.\n- **front-placket-drawstring**: A flat black drawstring threaded down\n  the inside of the placket area, hanging visibly from inside the hood\n  toward the chest. **Technique:** stitched. **Color:** black.\n- **side-hand-pockets** (left and right, lower-side): Slash-style hand\n  pockets with **zipper closures** at the openings. **Technique:**\n  patch (sewn-on hardware — zipper teeth). **Color:** black zipper teeth.\n- **left-cuff / right-cuff**: Black ribbed-knit cuffs at the wrists\n  (tonal black, contrasting with the satin sleeves). **Technique:**\n  stitched. **Color:** black.\n- **hem / waistband**: Black ribbed-knit bomber-style waistband at the\n  bottom of the jacket. **Technique:** stitched. **Color:** black.\n- **hood-inside / inner-hood-lining**: Black sherpa lining inside the\n  hood (plush textured fabric, distinct from the satin exterior).\n  **Technique:** stitched. **Color:** black sherpa.\n- **body-inside / inner-body-lining**: Black sherpa lining inside the\n  body of the jacket (visible when the front placket is open).\n  **Technique:** stitched. **Color:** black sherpa.\n- **collar-inside / interior-back-collar** (small woven label): Branded\n  woven size tag (universal SkyyRose product rule). Visible as a small\n  white-and-brand-color tag in the reference photos. **Technique:**\n  woven-label.",
    "negative_block": "- NO Black Rose logo on the front-RIGHT chest — the chest mark is on\n  the wearer's LEFT only (per CSV: \"Embroidered rose logo on left chest\").\n- NO Black Rose logo on the sleeves.\n- NO snap-only front closure — the front IS a zipper underneath, with\n  a buttoned/snapped storm flap overlapping it (NOT a snap-only design;\n  NOT a zipper-only exposed-teeth design — the zipper is hidden under\n  the snap-buttoned satin storm flap).\n- NO SR monogram on the back-neck — there is NO back-neck logo of any\n  kind on this jacket (distinct from the crewneck / jerseys which carry\n  a back-neck SR monogram).\n- NO logos on the back-yoke or upper back — the rose is centered on\n  the mid-back panel only.\n- NO contrast-color piping on the sleeves, body, or hood.\n- NO white drawstrings — the placket-area drawstring is BLACK.\n- NO white ribbed trim at cuffs or waistband — they are tonal black.\n- NO fleece, NO cotton-fleece body fabric — this jacket is black SATIN\n  with a sherpa interior, NOT cotton fleece.\n- NO hood without sherpa lining — the hood interior IS sherpa-lined.\n- NO Black Rose logo on the back-neck region between the hood and the\n  back panel — the back rose is at back-center (mid-back), not at the\n  back-neck.\n- NO multi-color rendering of either rose — the canonical art is\n  rendered in white-thread embroidery on the black satin.\n- NO Authentic Collection patch (that patch is reserved for the jersey series).\n- NO embossed/debossed decoration anywhere.\n- NO printed graphics, NO sublimated panels (the inner hood lining is\n  PLAIN black sherpa for this jacket — distinct from br-005's grey\n  sublimated-rose inner hood).",
    "scene_pose": "Front view straight-on or three-quarter front-left to display\n  the front-left chest rose, the buttoned storm-flap placket (zipper\n  hidden underneath), the side zip pockets, and the satin sheen of the\n  body. For the back: straight-on back view to show the large centered\n  back rose embroidery.",
    "scene_setting": "Pure white studio backdrop, soft directional studio\n  lighting from front-left (the satin fabric will catch light dynamically\n  — angle the lighting to enhance the satin sheen without blowing it\n  out). Subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/br-006-sherpa-jacket-real-front.jpeg",
    "extra_references": [
      "assets/products/references/br-006-sherpa-jacket-real-open.jpeg",
      "assets/products/references/br-006-sherpa-jacket-real-closeup.jpeg"
    ]
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-006-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-rose-sherpa-jacket-back.jpg",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-006-sherpa-jacket.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/black-rose-sherpa-jacket-back.jpg",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/black-rose-sherpa-jacket-sherpa-product.jpg",
    "back": "wordpress-theme/skyyrose-flagship/assets/images/products/black-rose-sherpa-jacket-back.jpg",
    "reference": "assets/products/references/br-006-sherpa-jacket-real-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_chest",
        "technique": "embroidered",
        "size_inches": 4
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_center",
        "technique": "embroidered",
        "size_inches": 10,
        "notes": "Large back version."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Embrace the shadows with a whisper of rebellion. The SkyyRose BLACK Rose Sherpa Jacket is a testament to raw elegance, a piece forged in the heart of dark romance. Crafted for those who find beauty in the unconventional, its lustrous black exterior shimmers with a mysterious allure, hinting at stories untold beneath the moonlight. The sleek, satin-like shell is contrasted with a lavish Sherpa lining, enveloping you in an embrace of warmth and comfort, a soft secret against the skin.\n\nAdorning the chest, an intricately embroidered black rose blooms, entwined with thorns, a stark symbol of enduring beauty born from pain. This jacket isn't just an garment; it's an extension of your spirit, a confident statement that challenges the mundane. With its integrated hood and classic bomber silhouette, it offers both street-ready style and an undeniable edge. Step into the night, empowered by the darkness and grace that is uniquely SkyyRose. This is more than fashion; this is art you wear.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Unveil your dark allure. The BLACK Rose Sherpa Jacket combines lustrous black satin with plush Sherpa lining, crowned by an exquisite embroidered rose that speaks volumes of gothic luxury.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "Shop the SkyyRose BLACK Rose Sherpa Jacket. Featuring a luxurious satin-look exterior, warm Sherpa lining, and intricate embroidered black roses. Pre-order now.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "When shadows whisper secrets and roses bloom in monochrome. 🖤 Our BLACK Rose Sherpa Jacket marries luxurious darkness with an undeniable edge, its sleek exterior hiding a soft, warm embrace. Each embroidered rose tells a tale of fierce beauty and resilient spirit, making it a powerful statement for those who dare to stand apart. Pre-order this coveted piece and let your style unfurl with a gothic elegance only SkyyRose can deliver. Embrace the beautiful pain. 🌹\n\n#SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaStyle #LuxuryStreetwear #EmbroideredRoses #SherpaJacket #PreOrder #FashionStatement #Mystery",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "This ain't just a jacket, it's a mood. 🖤 The BLACK Rose Sherpa Jacket drops, bringing gothic luxury to your street style. Pre-order the vibe. 🌹 #SkyyRose #BlackRose #Streetwear #NewDrop",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-006-product-2": "Black hooded BLACK Rose Sherpa Jacket with a white embroidered rose and cloud design on the back.",
    "br-006-product": "BLACK Rose jacket: black satin hooded bomber with an embroidered rose emblem."
  },
  "corrections": [
    {
      "text": "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE separate roses — one dominant upright rose plus a smaller rose or bud offset to the side, on a single cumulus cloud at the base. It is NOT a single large bloom and NOT a peony. Keep the roses as distinct flowers; do not merge them into one.",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] Render the rose logo at the size and position shown in the real product photo and tech flat — do NOT enlarge it to fill or dominate the chest.",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.594941+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-007 — BLACK Rose x Love Hurts Basketball Shorts

```json
{
  "sku": "br-007",
  "name": "BLACK Rose x Love Hurts Basketball Shorts",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-007",
    "name": "BLACK Rose x Love Hurts Basketball Shorts",
    "price": "65",
    "collection": "black-rose",
    "description": "Two worlds collide. A cross-collection collaboration merging Black Rose darkness with Love Hurts fire.",
    "badge": "",
    "image": "assets/images/products/br-007.jpg",
    "front_model_image": "assets/images/products/ghost/br-007-ghost-front.webp",
    "back_image": "assets/images/products/br-007-real-back.jpg",
    "back_model_image": "assets/images/products/black-rose-love-hurts-basketball-shorts/black-rose-love-hurts-basketball-shorts-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Tackle twill cut-out letters stitched on the front spelling 'Oakland'. Sublimated rose logo throughout the shorts. Big sublimated 'Love Hurts' logo on the left side. Additional 'Love Hurts' and rose logos stitched on the mesh sides of the shorts.",
    "render_output_slug": "black-rose-love-hurts-bb-shorts",
    "render_source_override": "br-007.jpg",
    "render_back_source_override": "br-007-real-back.jpg",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shorts",
    "dossier_slug": "black-rose-x-love-hurts-basketball-shorts",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Knee-length (or just-above-knee) athletic basketball shorts — black mesh main body with white mesh side panels, white elasticated waistband with white drawstring, **two side hand pockets** (left and right — both with zipper closures) and **one back pocket** (also with zipper closure) — three zip pockets total.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Knee-length (or just-above-knee) athletic basketball shorts — black mesh main body with white mesh side panels, white elasticated waistband with white drawstring, **two side hand pockets** (left and right — both with zipper closures) and **one back pocket** (also with zipper closure) — three zip pockets total. Black ribbed-binding hem with white contrast piping. Cross-collection collab combining Black Rose and Love Hurts visual systems on a single garment. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-007",
    "name": "BLACK Rose x Love Hurts Basketball Shorts",
    "collection": "black-rose",
    "slug": "black-rose-x-love-hurts-basketball-shorts",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Knee-length (or just-above-knee) athletic basketball shorts — black mesh main body with white mesh side panels, white elasticated waistband with white drawstring, **two side hand pockets** (left and right — both with zipper closures) and **one back pocket** (also with zipper closure) — three zip pockets total.\nFeatures: Knee-length (or just-above-knee) athletic basketball shorts — black mesh main body with white mesh side panels, white elasticated waistband with white drawstring, **two side hand pockets** (left and right — both with zipper closures) and **one back pocket** (also with zipper closure) — three zip pockets total. Black ribbed-binding hem with white contrast piping. Cross-collection collab combining Black Rose and Love Hurts visual systems on a single garment. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short.\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Love Hurts (wordmark + broken-heart-and-thorns lockup): `data/brand-logos/love-hurts-logo.md`\n> - Physical source photos: `assets/products/source-photos/black-rose/br-007-shorts-front.jpeg`,\n>                           `assets/products/source-photos/black-rose/br-007-shorts-back-hanger.jpeg`,\n>                           `assets/products/source-photos/black-rose/br-007-shorts-wearer-left.jpeg`,\n>                           `assets/products/source-photos/black-rose/br-007-shorts-wearer-right.jpeg`\n> - Techflat context: `assets/products/source-photos/black-rose/br-007-techflat-shorts.jpeg`\n>\n> ### COLORWAY OVERRIDE — read this BEFORE rendering\n>\n> The black body print, OAKLAND tackle-twill, and Love Hurts wordmarks use the\n> shorts' black, grey, white, and cream/peach tonal palette. The embroidered\n> Black Rose cluster on the **wearer-right white mesh side panel is the physical\n> exception**: black rose, green stem/leaves, and pale blue/white cloud. Preserve\n> the physical source colors and placement; do not mirror this panel.\n>\n> Tonal palette for this product:\n> - Body fabric: black mesh\n> - Side panels: white mesh\n> - Sublimated patterns: tonal grey on black\n> - Wearer-left side embroidery: tonal grey / cream / dark grey on white mesh\n> - Wearer-right Black Rose embroidery: black rose, green stem/leaves,\n>   pale blue/white cloud on white mesh\n> - Tackle-twill: white face with dark satin-stitch edge\n> - Wordmark colors: cream / peach / light-pink (NOT red)\n\n### Front\n- **front-body** (entire black mesh field): The Black Rose three-rose-cluster\n  art **sublimated as a small repeating pattern across the entire black mesh\n  body fabric** — small tonal grey rose silhouettes scattered across the\n  mesh like an all-over print. Subtle (almost camo-like) on black ground,\n  visible in close-up but reads as textured field at distance. **Technique:**\n  sublimated. **Color:** tonal grey on black mesh.\n- **front-thigh-center** (large, arched, ~6–7in wide): The wordmark\n  **\"OAKLAND\"** as authentic tackle-twill — pre-cut white twill letters\n  appliquéd onto the body in classic baseball-script style with a contrast\n  satin-stitch edge. **Technique:** tackle-twill. **Color:** white twill\n  letter face with a dark satin-stitch edge.\n- **front-right-thigh** (cursive script overlapping the OAKLAND wordmark):\n  The \"Love Hurts\" wordmark in cursive script, rendered as a large\n  sublimated/printed wordmark in **cream/peach/pink tonal color** on the\n  black mesh. Spans the right thigh area, reading top-to-bottom as the\n  cursive lettering descends. **Technique:** sublimated. **Color:**\n  cream/peach/light-pink tonal.\n- **wearer-left-mesh-side-panel** (small, on the white mesh side panel):\n  The \"Love Hurts\" wordmark (cursive script only — no broken heart in\n  this position) stitched onto the white mesh. **Technique:** embroidered.\n  **Color:** dark/contrast thread on white mesh.\n- **wearer-right-mesh-side-panel** (small, on the white mesh side panel):\n  The Black Rose cluster stitched onto the white mesh: black rose bloom,\n  green stem/leaves, and pale blue/white cloud. **Technique:** embroidered.\n  **Color:** physical source colors; do not tonalize, mirror, or move it.\n\n### Back\n- **back-body** (entire black mesh field): Same sublimated tonal grey\n  rose-cluster pattern as the front-body (continuous across the garment).\n  **Technique:** sublimated. **Color:** tonal grey on black mesh.\n- **back-upper / back-yoke** (large cursive across the upper back):\n  The \"Love Hurts\" wordmark in cursive script, rendered larger than the\n  front-right version, in **cream/peach/light-pink tonal color** sublimated\n  onto the back mesh. **Technique:** sublimated. **Color:** cream/peach/\n  light-pink tonal.\n- **back-side continuity:** The white mesh inserts remain on the two outer side\n  panels. There is no white center-back pentagon. The wearer-left panel carries\n  Love Hurts; the wearer-right panel carries the Black Rose cluster.\n\n### Sleeves / Collar / Hem / Other\n- **waistband-rib**: White elasticated waistband at the top.\n  **Technique:** stitched. **Color:** white.\n- **drawstring**: White flat drawstring threaded through the waistband.\n  **Technique:** stitched. **Color:** white.\n- **left-side-pocket / right-side-pocket** (front-side hand pockets):\n  Vertical hand pockets at both sides, **with zipper closures**.\n  **Technique:** patch (sewn-on zipper hardware). **Color:** black\n  zipper teeth (with white piping at the pocket edge).\n- **back-pocket** (single, centered upper-back, with zipper):\n  One zippered back pocket — visible as a horizontal welt opening\n  with white piping at the welt edges. **Technique:** patch (sewn-on\n  zipper hardware). **Color:** black zipper teeth (with white piping\n  at the welt edges).\n- **hem / leg-binding**: Black ribbed-knit binding at the leg openings\n  with a thin white contrast piping accent. **Technique:** stitched.\n  **Color:** black with white piping.\n- **inside-waistband** (~1in × 0.5in): Branded woven size tag (universal\n  SkyyRose product rule). **Technique:** woven-label.",
    "negative_block": "- **NO canonical red Love Hurts treatment on this garment.** The Love Hurts\n  wordmarks remain in the shorts' tonal palette\n  (black/grey/white/cream/peach). Specifically:\n  - NO red roses anywhere — the body sublimation is the Black Rose\n    three-rose-cluster in tonal grey-on-black, NOT the canonical\n    multi-color or Love Hurts red-roses variant.\n  - NO bright red Love Hurts wordmark — the cursive script is rendered\n    in cream/peach/light-pink tonal, NOT the canonical saturated red.\n- NO Black Rose cluster on the wearer-left mesh side panel — wearer-left\n  carries the Love Hurts wordmark only.\n- NO Love Hurts wordmark on the wearer-right mesh side panel — wearer-right\n  carries the physical-color Black Rose cluster only.\n- NO center-back white pentagon or center-back Love Hurts patch.\n- NO multi-color rendering of the body sublimated rose pattern — it is\n  tonal grey-on-black, NOT the full multi-color art.\n- NO Black Rose logo at front-thigh-center — the front center carries\n  the OAKLAND tackle-twill wordmark, not a rose.\n- NO solid-color body — the body fabric carries the sublimated rose\n  pattern (NOT a plain black field).\n- NO front pockets visible from outside — the visible pockets are on\n  the BACK only; the front is uninterrupted by pocket openings.\n- NO black drawstrings — the drawstring is white.\n- NO black waistband — the waistband is white.\n- NO contrast satin-stitch edge other than dark on the OAKLAND letters.\n- NO numbers anywhere — no player number, no jersey-style numerals.\n- NO sleeve elements (this is a shorts garment, lower-body only — no\n  upper-body decoration of any kind).\n- NO Authentic Collection patch (that is reserved for the jersey series).\n- NO sublimated pattern on the white mesh side panels — the side panels\n  are clean white mesh with only the embroidered cluster (left) and\n  wordmark (right) on top.",
    "scene_pose": "Front view straight-on (or three-quarter front-left) showing\n  the OAKLAND wordmark, the wearer-left Love Hurts script/side panel, and the\n  wearer-right physical-color Black Rose cluster. For back: back view\n  straight-on showing the upper-back Love Hurts cursive script and both outer\n  side panels, with no invented center-back panel.",
    "scene_setting": "Pure white studio backdrop, soft directional studio\n  lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/love-hurts-logo.md"
    ],
    "reference_image": "assets/products/source-photos/black-rose/br-007-shorts-front.jpeg",
    "extra_references": [
      "assets/products/source-photos/black-rose/br-007-shorts-back-hanger.jpeg",
      "assets/products/source-photos/black-rose/br-007-shorts-wearer-left.jpeg",
      "assets/products/source-photos/black-rose/br-007-shorts-wearer-right.jpeg",
      "assets/products/source-photos/black-rose/br-007-techflat-shorts.jpeg"
    ]
  },
  "images": {
    "front": {
      "path": "assets/images/products/hub/br-007-front.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/hub/br-007-back.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-007.jpg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/br-007-real-back.jpg",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/references/br-007-shorts-real-front.jpeg",
    "back": "wordpress-theme/skyyrose-flagship/assets/images/products/br-007-real-back.jpg",
    "reference": "assets/products/references/br-007-shorts-real-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "all_over",
        "technique": "sublimated"
      },
      {
        "logo_id": "love-hurts-full-lettering",
        "position": "left_side",
        "technique": "sublimated",
        "size_inches": 12,
        "notes": "Large sublimated element."
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "mesh_side_panels",
        "technique": "stitched"
      },
      {
        "logo_id": "love-hurts-full-lettering",
        "position": "mesh_side_panels",
        "technique": "stitched",
        "notes": "Smaller Love Hurts + Rose logos stitched on mesh side panels."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Twilight descends on the court, where shadows dance with every move. The BLACK Rose × Love Hurts Basketball Shorts are a gothic poem etched in mesh, a symphony of darkness and defiance. Born from Oakland's soul, these shorts whisper tales of resilience and romance. Imagine the ethereal touch of premium black mesh against your skin, adorned with shadowed roses and enigmatic clouds, a silent ballet of beauty blooming from pain. \"OAKLAND\" stands bold, a testament to roots, while bespoke white side panels showcase embroidered black roses rising from mystic blue clouds — a luxurious rebellion in every thread. These shorts aren't just clothing; they're a statement, a wearable canvas of confidence and evocative self-expression. Embrace the duality, where athletic comfort meets gothic allure, and let your style bloom in the shadows. Available in sizes S/M/L/XL/2XL/3XL. At SkyyRose, we craft luxury that dares to embrace the darkness, finding power in every delicate thorn. Dare to bloom.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "SkyyRose BLACK Rose: Where twilight meets the streets. Embroidered roses bloom on black mesh, a gothic love letter to Oakland's soul.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose BLACK Rose × Love Hurts Basketball Shorts: Gothic luxury meets Oakland grit. Shop dark romance apparel with embroidered rose details. Dare to bloom.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "From Oakland's heart, a gothic romance unfolds. The BLACK Rose × Love Hurts Basketball Shorts are where shadows bloom, a testament to the beauty found in darkness. Feel the ethereal mesh against your skin, a whisper of luxury echoing through the streets.\n\n#SkyyRose #BlackRoseCollection #GothicLuxury #DarkRomance #StreetwearFashion #BayAreaFashion #EmbroideredRose #LuxuryStreetwear #FashionStatement #MysteryStyle #DarkAesthetic #WearableArt",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Darkness blooms in Oakland.🖤🌹 SkyyRose BLACK Rose shorts: Gothic luxury forged in Bay Area grit. #SkyyRose #BlackRoseCollection #GothicLuxury #BayAreaFashion",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-007-product-2": "Black Rose x Love Hurts Basketball Shorts, black with white details, grey rose/cloud patterns, and \"Love Hurts\" text/heart graphic.",
    "br-007-product": "BLACK Rose × Love Hurts Basketball Shorts. Black with white \"OAKLAND,\" rose & cloud patterns, and white mesh trim."
  },
  "corrections": [
    {
      "text": "[ghost-back] Love Hurts is only on the side not across the back",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] oakland needs to be centered and slightly bigger",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE separate roses — one dominant upright rose plus a smaller rose or bud offset to the side, on a single cumulus cloud at the base. It is NOT a single large bloom and NOT a peony. Keep the roses as distinct flowers; do not merge them into one.",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.608576+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-008 — BLACK is Beautiful Jersey Series: 1. SF Inspired (Football)

```json
{
  "sku": "br-008",
  "name": "BLACK is Beautiful Jersey Series: 1. SF Inspired (Football)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-008",
    "name": "BLACK is Beautiful Jersey Series: 1. SF Inspired (Football)",
    "price": "115",
    "collection": "black-rose",
    "description": "Red #80 football jersey. SF 49ers inspired, alternating rose fill on numbers. Exclusive edition — 80 pieces.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-008-sf-inspired.jpg",
    "front_model_image": "assets/images/products/br-008-onmodel.webp",
    "back_image": "",
    "back_model_image": "",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Red",
    "edition_size": "80",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Jersey-style stitched numbers (80) on front and back. FRONT: the '8' contains the rose logo, the '0' is plain white. Custom Football Patch in bottom-left corner. BACK: reversed — the '8' is plain white, the '0' contains the rose.",
    "render_output_slug": "jersey-sf-inspired-football",
    "render_source_override": "br-008-sf-inspired.jpg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-1-sf-inspired-football",
    "engine_override": ""
  },
  "garment": {
    "color": "Red",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid **bright red** base fabric (San Francisco red colorway). Mid-weight\nknit jersey fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style football jersey — V-neck collar opening\nwith **black-and-white horizontal striped neckband**, short sleeves with a\n**white triple-stripe band (three thin horizontal white stripes)** at each\ncuff, straight even hem (no drop-tail), no laces, no shoulder-armor seam.\nSolid **bright red** base fabric (San Francisco red colorway). Mid-weight\nknit jersey fabric. Pullover construction — NO buttons, NO front placket. NOT\na t-shirt. NOT a hoodie. NOT a basketball tank. NOT a baseball jersey.\n**PRE-ORDER product** — design renderings only; no real-product photography\nexists yet.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-008/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-008",
    "name": "BLACK is Beautiful Jersey Series — 1. SF Inspired (Football)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-1-sf-inspired-football",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid **bright red** base fabric (San Francisco red colorway). Mid-weight\nknit jersey fabric.\nFeatures: Authentic-style football jersey — V-neck collar opening\nwith **black-and-white horizontal striped neckband**, short sleeves with a\n**white triple-stripe band (three thin horizontal white stripes)** at each\ncuff, straight even hem (no drop-tail), no laces, no shoulder-armor seam.\nSolid **bright red** base fabric (San Francisco red colorway). Mid-weight\nknit jersey fabric. Pullover construction — NO buttons, NO front placket. NOT\na t-shirt. NOT a hoodie. NOT a basketball tank. NOT a baseball jersey.\n**PRE-ORDER product** — design renderings only; no real-product photography\nexists yet.\nColor: Red\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - NFL Authentic Collection patch: `data/brand-logos/nfl-authentic-collection-patch.md`\n> - Product design render:          `assets/products/references/br-008-design-front.jpeg`\n>\n> ### COLORWAY OVERRIDE — read this BEFORE rendering\n>\n> The number-fill rose-cluster art is rendered in **tonal greyscale only**\n> (black + white + grey shading + black ink outlines), NOT canonical\n> multi-color. The cluster is recognizable by composition (three roses,\n> thorny vines, cloud at base) but renders in greyscale-on-red so it reads\n> cleanly inside the white-outlined number forms. NO red roses, NO kelly-green\n> stems, NO white-and-blue clouds.\n\n### Front\n- **front-chest** (large, ~10in tall, vertically centered between the\n  neckband and the lower belly): The number **\"80\"** rendered as\n  large athletic-block digits — each digit has a **white outline edge** with\n  the canonical Black Rose three-rose-cluster art (in tonal greyscale)\n  filling the interior of both the \"8\" and the \"0\". The rose composition is\n  preserved (three roses + thorny vines + cloud at base) but rendered in\n  black/white/grey only. **Technique:** sublimated. **Color:** white outline\n  + greyscale rose-cluster fill on red ground.\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall, near the bottom\n  hem on the wearer's left hip): The NFL Authentic Collection patch (yellow\n  field + navy \"BLACK ROSE / COLLECTION\" + NFL shield + white \"AUTHENTIC\"\n  banner + red diamond divider + greyscale rose-cluster + \"Property Of /\n  Black Is Beautiful Series / Skyy Rose Co\" footer — see patch reference).\n  Sewn onto the lower-left hip. **Technique:** embroidered-patch.\n\n### Back\n- **back-yoke / upper-back** (across the upper-back, arched, ~9–10in wide):\n  The phrase **\"BLACK IS BEAUTIFUL\"** as authentic tackle-twill lettering,\n  baseball-script style with subtle outlines, arched across the upper-back.\n  Rendered in **black twill** on the red body. **Technique:** tackle-twill.\n  **Color:** black twill letters on red ground (no contrast satin-stitch edge).\n- **back-center** (large, ~12in tall, vertically centered between the\n  upper-back wordmark and the lower hem): The number **\"80\"** rendered\n  identically to the front — white outline + greyscale rose-cluster fill.\n  **Technique:** sublimated. **Color:** white outline + greyscale\n  rose-cluster fill.\n\n### Sleeves / Collar / Hem / Other\n- **collar / V-neck binding**: Black-and-white horizontal striped neckband\n  (a ribbed band with alternating black and white stripes, ~1in wide). The V\n  opening is shaped within this striped band. **Technique:** stitched.\n  **Color:** alternating black + white.\n- **left-cuff / right-cuff binding**: White triple-stripe (three thin\n  horizontal white stripes spaced evenly) on each short sleeve cuff against\n  the red body fabric. **Technique:** stitched. **Color:** white stripes on\n  red.\n- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal\n  SkyyRose product rule). **Technique:** woven-label.",
    "negative_block": "- NO player NAME on back. NO last name. NO first name. NO nameplate above\n  the back-center number — the upper back carries ONLY the \"BLACK IS\n  BEAUTIFUL\" wordmark.\n- NO numbers on sleeves — the sleeves are clean (only the white triple-stripe\n  cuff treatment, no shoulder digit, no sleeve number).\n- NO multi-color rendering of the rose-cluster fill inside the \"80\" — it is\n  greyscale only. NO red roses, NO kelly-green stems, NO white-and-blue\n  cloud color.\n- NO solid-color \"80\" digits — the digits are NOT solid white; they have\n  a white outline edge with rose-cluster art FILLING the interior.\n- NO contrast satin-stitch edge around the \"BLACK IS BEAUTIFUL\" wordmark —\n  it is clean black-twill-on-red.\n- NO buttons, NO placket, NO V-neck contrast piping other than the striped\n  neckband — this is a pullover construction.\n- NO MLB Authentic Collection patch (that's the baseball series). NO NBA\n  Authentic Collection patch. NO Hockey Championship patch — football only.\n- NO embossed/debossed decoration anywhere.\n- NO heat-transfer vinyl on the body.\n- NO SR monogram on the back-neck — this colorway has no separate back-neck\n  embroidered mark.\n- NO standalone Black Rose rose-cluster on the back-center other than as\n  digit fill — the rose-cluster appears ONLY inside the \"80\" digits, not as\n  a separate composition.\n- NO sleeve patches (no shoulder NFL patch, no league patch on the\n  shoulders).\n- NO sublimated panels other than the rose-fill inside the digits and the\n  cuff stripes.\n- NO pinstripes anywhere on the body.\n- NO snap-front, NO zipper-front (this is a pullover).",
    "scene_pose": "Front view straight-on (or three-quarter front-left) showing the\n  large rose-fill \"80\" front-chest, the striped neckband, the white-stripe\n  cuffs, and the lower-left NFL patch. For back: back view straight-on\n  showing the \"BLACK IS BEAUTIFUL\" tackle-twill arch and the matching\n  rose-fill \"80\".",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/nfl-authentic-collection-patch.md"
    ],
    "reference_image": "assets/products/references/br-008-design-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-008-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": null,
    "packshot": {
      "path": "assets/images/products/br-008-sf-inspired.jpg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-football-sf-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-football-sf-back.jpeg",
    "reference": "assets/products/references/br-008-design-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_number_8",
        "technique": "stitched",
        "colorway": "rose_gold",
        "notes": "Rose cluster fills the '8' digit in jersey number 80 on the front; '0' remains plain white."
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_number_0",
        "technique": "stitched",
        "colorway": "rose_gold",
        "notes": "Reversed on back — '8' is plain, '0' has the rose cluster fill."
      },
      {
        "logo_id": "nfl-authentic-collection-card",
        "position": "bottom_left_corner",
        "technique": "custom_football_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-1-sf-inspired-football.md",
      "source_sha256": "30616c5c83341a4827c3b28b55a7eb8c812b0233d6bf03a3a7071b8c99fe64ce",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "number",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 10.0
          },
          "source_size_text": "large, ~10in tall, vertically centered between the neckband and the lower belly",
          "source_line": 41
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall, near the bottom hem on the wearer's left hip",
          "source_line": 49,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-yoke / upper-back",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "width",
            "min": 9.0,
            "max": 10.0
          },
          "source_size_text": "across the upper-back, arched, ~9–10in wide",
          "source_line": 57
        },
        {
          "position_as_documented": "back-center",
          "kind": "number",
          "dimension_inches": {
            "axis": "height",
            "min": 12.0,
            "max": 12.0
          },
          "source_size_text": "large, ~12in tall, vertically centered between the upper-back wordmark and the lower hem",
          "source_line": 62
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "source_snapshot_pointer": "#/products/br-008/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-football-jersey-red/nfl-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "football",
    "sku_folder": "black-is-beautiful-football-jersey-red"
  },
  "content": {
    "description": {
      "value": "The first in the exclusive BLACK is Beautiful Jersey Series. SF-inspired luxury athletic wear that makes a bold statement. Limited to 80 pieces worldwide.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "BLACK is Beautiful Jersey Series: SF inspired. Exclusive luxury athletic wear, limited to 80 pieces.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose BLACK is Beautiful Jersey Series: SF inspired. Exclusive limited-edition luxury streetwear. Pre-order now.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "SF inspired. Exclusive. 80 pieces worldwide. The BLACK is Beautiful Jersey Series drops soon. Pre-order now.\n\n#SkyyRose #BlackRoseCollection #GothicLuxury #LuxuryStreetwear #BayAreaFashion #ExclusiveDrop",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "80 pieces. SF inspired. BLACK is Beautiful Jersey Series. Pre-order now. #SkyyRose #ExclusiveDrop #BayArea",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "br-008-product": "BLACK is Beautiful Jersey Series: 1. SF inspired — exclusive luxury athletic jersey with Bay Area detailing."
  },
  "corrections": [
    {
      "text": "[ghost-back] rose logo only goes in the 0 in back",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] rose only goes in the 8 in front",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[on-model] fix logo inside numbers",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back",
    "images.back_packshot"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.616143+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-009 — BLACK is Beautiful Jersey Series: 2. Last Oakland (Football)

```json
{
  "sku": "br-009",
  "name": "BLACK is Beautiful Jersey Series: 2. Last Oakland (Football)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-009",
    "name": "BLACK is Beautiful Jersey Series: 2. Last Oakland (Football)",
    "price": "115",
    "collection": "black-rose",
    "description": "White #32 football jersey. White numbers with black border, alternating rose fill. The Last Oakland edition — 80 pieces.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-009-last-oakland-football.jpg",
    "front_model_image": "assets/images/products/br-009-onmodel.webp",
    "back_image": "",
    "back_model_image": "",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "80",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Jersey-style stitched numbers (32) on front and back. FRONT: the '3' contains the rose logo, the '2' is plain white. Custom Football Patch in bottom-left corner. BACK: reversed — the '3' is plain white, the '2' contains the rose.",
    "render_output_slug": "jersey-last-oakland-football",
    "render_source_override": "br-009-last-oakland-football.jpg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-2-last-oakland-football",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid **white** base fabric (Last Oakland Raiders-inspired road/away\ncolorway). Mid-weight knit jersey fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style football jersey — V-neck collar opening\nwith **solid black neckband** (contrast against the white body), short sleeves\nwith a **black-and-white horizontal striped cuff band** at each cuff, straight\neven hem. Solid **white** base fabric (Last Oakland Raiders-inspired road/away\ncolorway). Mid-weight knit jersey fabric. Pullover construction — NO buttons,\nNO front placket. NOT a t-shirt. NOT a hoodie. NOT a basketball tank. NOT a\nbaseball jersey. **PRE-ORDER product** — design renderings only.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-009/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-009",
    "name": "BLACK is Beautiful Jersey Series — 2. Last Oakland (Football)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-2-last-oakland-football",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid **white** base fabric (Last Oakland Raiders-inspired road/away\ncolorway). Mid-weight knit jersey fabric.\nFeatures: Authentic-style football jersey — V-neck collar opening\nwith **solid black neckband** (contrast against the white body), short sleeves\nwith a **black-and-white horizontal striped cuff band** at each cuff, straight\neven hem. Solid **white** base fabric (Last Oakland Raiders-inspired road/away\ncolorway). Mid-weight knit jersey fabric. Pullover construction — NO buttons,\nNO front placket. NOT a t-shirt. NOT a hoodie. NOT a basketball tank. NOT a\nbaseball jersey. **PRE-ORDER product** — design renderings only.\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - NFL Authentic Collection patch: `data/brand-logos/nfl-authentic-collection-patch.md`\n> - SR monogram (back-neck):       `data/brand-logos/sr-monogram.md`\n> - Product design render:          `assets/products/references/br-009-design-front.jpeg`\n>\n> ### COLORWAY OVERRIDE — read this BEFORE rendering\n>\n> The number-fill rose-cluster art is rendered in **tonal greyscale only**\n> (black + white + grey shading + black ink outlines), NOT canonical\n> multi-color. The SR monogram is rendered in **black thread** on this\n> colorway (NOT canonical gold) — black-on-white reads cleanly where\n> gold-on-white would not. NO red roses, NO kelly-green stems, NO\n> white-and-blue cloud color.\n\n### Front\n- **front-chest** (large, ~10in tall, vertically centered): The number\n  **\"32\"** rendered as athletic-block digits with a **black outline edge**\n  and Black Rose three-rose-cluster art filling the **3 only**; the **2\n  remains plain white**. The legacy color/technique fields below remain unresolved. **Technique:** sublimated. **Color:** black outline +\n  greyscale rose-cluster fill on white ground.\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall): The NFL\n  Authentic Collection patch sewn onto the lower-left hip. **Technique:**\n  embroidered-patch.\n\n### Back\n- **back-neck** (small, ~2in wide, top-center just below the collar yoke):\n  The SR monogram embroidered directly onto the jersey in **black thread**\n  (instead of canonical gold — black-on-white for this colorway).\n  **Technique:** embroidered. **Color:** black thread.\n- **back-yoke / upper-back** (arched, ~9in wide): The phrase **\"BLACK IS\n  BEAUTIFUL\"** in tackle-twill lettering, baseball-script style. Rendered in\n  **black twill** on the white body. **Technique:** tackle-twill. **Color:**\n  black twill letters on white ground.\n- **back-center** (large, ~12in tall, vertically centered): The number\n  **\"32\"** with the rose fill in the **2 only** and the **3 plain white**,\n  reversing the front fill assignment. **Technique:** unresolved legacy claim: sublimated.\n  **Color:** black outline + greyscale rose-cluster fill.\n\n### Sleeves\n- **left-shoulder / right-shoulder** (small, ~3–4in tall, on each shoulder):\n  A smaller version of the same \"32\" digit composition (greyscale rose-cluster\n  fill with black outline) on each shoulder/sleeve area. **Technique:**\n  sublimated. **Color:** black outline + greyscale rose-cluster fill.\n\n### Collar / Hem / Other\n- **collar / V-neck binding**: Solid black neckband (~1in wide). **Technique:**\n  stitched. **Color:** black.\n- **left-cuff / right-cuff binding**: Black-and-white horizontal striped band\n  at each short sleeve cuff (alternating black and white stripes, ~1in tall\n  total). **Technique:** stitched. **Color:** alternating black + white.\n- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal\n  SkyyRose product rule). **Technique:** woven-label.",
    "negative_block": "- NO player NAME on back. NO nameplate above the back number.\n- NO multi-color rendering of the rose-cluster fill — greyscale only.\n- NO red anywhere on this colorway (this is the Last Oakland white away —\n  NO 49ers red, NO Giants orange).\n- NO rose fill in both digits. Front: rose in 3, plain white 2. Back: plain white 3, rose in 2. Preserve the black outline; technique/color remain held above.\n- NO MLB Authentic Collection patch (baseball series only).\n- NO Hockey Championship patch.\n- NO NBA Authentic Collection patch.\n- NO embossed/debossed decoration.\n- NO buttons, NO placket — pullover construction.\n- NO standalone Black Rose three-rose-cluster art on the back-center other\n  than as digit fill — the rose appears ONLY inside the digit fills.\n- NO gold thread on the SR monogram — black thread for this colorway.\n- NO sleeve PATCHES — the sleeves carry duplicate \"32\" numerals, not woven\n  patches.\n- NO printed graphics other than the rose-fill inside digits and the sleeve\n  number duplicates.\n- NO pinstripes.\n- NO snap-front or zipper-front closure.",
    "scene_pose": "Front view straight-on showing the front-chest \"32\" with rose\n  fill, the black neckband, the striped cuffs, and the lower-left NFL patch.\n  Three-quarter view shows the sleeve \"32\" detail. Back view shows the\n  upper-back \"BLACK IS BEAUTIFUL\" tackle-twill, the small black SR monogram\n  at back-neck, and the matching back-center \"32\".",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/nfl-authentic-collection-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-009-design-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-009-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": null,
    "packshot": {
      "path": "assets/images/products/br-009-last-oakland-football.jpg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-football-oakland-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-football-oakland-back.jpeg",
    "reference": "assets/products/references/br-009-design-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_number_3",
        "technique": "stitched",
        "colorway": "rose_gold",
        "notes": "Rose cluster fills the '3' digit in jersey number 32 on the front; '2' remains plain white."
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_number_2",
        "technique": "stitched",
        "colorway": "rose_gold",
        "notes": "Reversed on back — '3' is plain, '2' has the rose cluster fill."
      },
      {
        "logo_id": "nfl-authentic-collection-card",
        "position": "bottom_left_corner",
        "technique": "custom_football_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-2-last-oakland-football.md",
      "source_sha256": "c24f2568a0031b7d3c59fcf9aa1a9a2883d3418848ae10dad6928c33479f2daa",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "number",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 10.0
          },
          "source_size_text": "large, ~10in tall, vertically centered",
          "source_line": 47
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall",
          "source_line": 52,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide, top-center just below the collar yoke",
          "source_line": 57
        },
        {
          "position_as_documented": "back-yoke / upper-back",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "width",
            "min": 9.0,
            "max": 9.0
          },
          "source_size_text": "arched, ~9in wide",
          "source_line": 61
        },
        {
          "position_as_documented": "back-center",
          "kind": "number",
          "dimension_inches": {
            "axis": "height",
            "min": 12.0,
            "max": 12.0
          },
          "source_size_text": "large, ~12in tall, vertically centered",
          "source_line": 65
        },
        {
          "position_as_documented": "left-shoulder / right-shoulder",
          "kind": "number",
          "dimension_inches": {
            "axis": "height",
            "min": 3.0,
            "max": 4.0
          },
          "source_size_text": "small, ~3–4in tall, on each shoulder",
          "source_line": 71
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "source_snapshot_pointer": "#/products/br-009/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-football-jersey-white/nfl-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "football",
    "sku_folder": "black-is-beautiful-football-jersey-white"
  },
  "content": {
    "description": {
      "value": "White #32 football jersey. White numbers with black border, alternating rose fill. The Last Oakland edition — 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "White #32 football jersey. White numbers with black border, alternating rose fill. The Last Oakland edition — 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [
    {
      "text": "[ghost-back] rose logo only goes in the 2 in back",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] rose logo only goes in the 3 infront",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[on-model] fix rose logo only goes in the 3",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back",
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.624675+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-010 — BLACK is Beautiful Jersey Series: 3. The Bay (Basketball)

```json
{
  "sku": "br-010",
  "name": "BLACK is Beautiful Jersey Series: 3. The Bay (Basketball)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-010",
    "name": "BLACK is Beautiful Jersey Series: 3. The Bay (Basketball)",
    "price": "100",
    "collection": "black-rose",
    "description": "Basketball tank with \"THE BAY\" gold text. Rose circle graphic, grey/silver rose fade. Bay Area edition — 80 pieces.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-010-the-bay-basketball.jpeg",
    "front_model_image": "assets/images/products/br-010-onmodel.webp",
    "back_image": "",
    "back_model_image": "",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White/Gold",
    "edition_size": "80",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Use the existing successful render as reference — vision pipeline produced a good first render of this SKU. Preserve the established composition.",
    "render_output_slug": "jersey-the-bay-basketball",
    "render_source_override": "br-010-the-bay-basketball.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "1",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-3-the-bay-basketball",
    "engine_override": ""
  },
  "garment": {
    "color": "White/Gold",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "**White base body fabric with a sublimated all-over\nrose-cluster pattern fading from clean white at the upper-chest into greyscale\nsilhouettes at the lower hem** — the bottom third of the jersey is a layered\ngrey-on-white rose-cluster pattern that wraps front and back continuously.",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "**White base body fabric with a sublimated all-over\nrose-cluster pattern fading from clean white at the upper-chest into greyscale\nsilhouettes at the lower hem** — the bottom third of the jersey is a layered\ngrey-on-white rose-cluster pattern that wraps front and back continuously. Mid-weight tank fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style basketball tank — sleeveless, round\nneck with thin contrast binding, deep armhole openings (basketball-cut),\nstraight even hem. **White base body fabric with a sublimated all-over\nrose-cluster pattern fading from clean white at the upper-chest into greyscale\nsilhouettes at the lower hem** — the bottom third of the jersey is a layered\ngrey-on-white rose-cluster pattern that wraps front and back continuously.\nMid-weight tank fabric. NO sleeves. NO numbers anywhere. NOT a t-shirt. NOT\na football jersey. NOT a baseball jersey. **PRE-ORDER product** — design\nrenderings only.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-010/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-010",
    "name": "BLACK is Beautiful Jersey Series — 3. The Bay (Basketball)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-3-the-bay-basketball",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: **White base body fabric with a sublimated all-over\nrose-cluster pattern fading from clean white at the upper-chest into greyscale\nsilhouettes at the lower hem** — the bottom third of the jersey is a layered\ngrey-on-white rose-cluster pattern that wraps front and back continuously. Mid-weight tank fabric.\nFit: **White base body fabric with a sublimated all-over\nrose-cluster pattern fading from clean white at the upper-chest into greyscale\nsilhouettes at the lower hem** — the bottom third of the jersey is a layered\ngrey-on-white rose-cluster pattern that wraps front and back continuously.\nFeatures: Authentic-style basketball tank — sleeveless, round\nneck with thin contrast binding, deep armhole openings (basketball-cut),\nstraight even hem. **White base body fabric with a sublimated all-over\nrose-cluster pattern fading from clean white at the upper-chest into greyscale\nsilhouettes at the lower hem** — the bottom third of the jersey is a layered\ngrey-on-white rose-cluster pattern that wraps front and back continuously.\nMid-weight tank fabric. NO sleeves. NO numbers anywhere. NOT a t-shirt. NOT\na football jersey. NOT a baseball jersey. **PRE-ORDER product** — design\nrenderings only.\nColor: White/Gold\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - NBA Authentic Collection patch: `data/brand-logos/nba-authentic-collection-patch.md`\n> - SR monogram (back-neck):       `data/brand-logos/sr-monogram.md`\n> - Product design render:          `assets/products/references/br-010-design-front.jpeg`\n>\n> ### COLORWAY OVERRIDE — read this BEFORE rendering\n>\n> The fading rose-pattern at the lower body is rendered in **tonal grey on\n> white** (NOT canonical multi-color). The center medallion's rose-cluster\n> is also greyscale. Wordmarks (\"THE BAY\", \"BLACK IS BEAUTIFUL\") are\n> rendered in **gold/yellow** color. The SR monogram renders in black\n> thread on the white body for visibility (NOT canonical gold).\n\n### Front\n- **front-body sublimated pattern** (lower half / hem area): An all-over\n  layered rose-cluster silhouette pattern (canonical roses + thorny vines +\n  cloud composition repeated at large scale) that fades from clean white at\n  the upper-chest into tonal greyscale silhouettes at the bottom hem. The\n  pattern wraps continuously to the back. **Technique:** sublimated.\n  **Color:** tonal grey rose-cluster silhouettes on white.\n- **front-chest** (large, ~6–7in diameter, vertically centered on the upper\n  chest): A circular medallion with a thin dark-grey ring border, **\"THE BAY\"**\n  in gold/yellow serif lettering arched across the top of the ring, and the\n  canonical Black Rose three-rose-cluster (greyscale) centered inside the\n  circle. **Technique:** sublimated. **Color:** dark grey ring + gold \"THE\n  BAY\" text + greyscale rose-cluster.\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall, against the\n  fading rose pattern): The NBA Authentic Collection patch sewn onto the\n  lower-left hip. **Technique:** embroidered-patch.\n\n### Back\n- **back-neck** (small, ~2in wide): The SR monogram embroidered directly\n  onto the jersey in **black thread** (NOT canonical gold — black-on-white\n  for visibility). **Technique:** embroidered. **Color:** black thread.\n- **back-upper-center** (stacked vertically on three lines, ~6in tall total):\n  The phrase **\"BLACK / IS / BEAUTIFUL\"** stacked across three lines in\n  gold/yellow serif lettering, centered on the upper back below the back-neck.\n  **Technique:** sublimated. **Color:** gold/yellow.\n- **back-body sublimated pattern**: The same fading rose-cluster silhouette\n  pattern as the front, continuing from front to back, fading from clean white\n  at the upper-back into tonal greyscale at the bottom hem. **Technique:**\n  sublimated. **Color:** tonal grey on white.\n\n### Collar / Hem / Other\n- **collar / round-neck binding**: Thin contrast binding (~1/4in) around the\n  round neck opening. **Technique:** stitched. **Color:** dark grey / black.\n- **armhole binding**: Thin matching binding around each armhole opening.\n  **Technique:** stitched. **Color:** dark grey / black.\n- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal\n  SkyyRose product rule). **Technique:** woven-label.",
    "negative_block": "- NO sleeves (this is a basketball tank — sleeveless).\n- NO numbers anywhere — front, back, or shoulders.\n- NO player name on back.\n- NO multi-color rendering of the rose-pattern — greyscale on white only.\n- NO red roses, NO kelly-green stems, NO blue clouds in the pattern (the\n  rose-cluster is remapped to greyscale silhouettes).\n- NO MLB Authentic Collection patch. NO NFL Authentic Collection patch. NO\n  Hockey Championship patch — only the NBA patch on this jersey.\n- NO solid-color base — the body has the sublimated fading pattern, not a\n  plain white field.\n- NO embossed/debossed decoration.\n- NO tackle-twill anywhere — wordmarks are sublimated, not appliquéd.\n- NO standalone embroidered Black Rose rose-cluster on the back-center —\n  the rose-cluster appears as part of the sublimated all-over pattern + the\n  front medallion only, not as a separate embroidered logo on the back.\n- NO buttons, NO placket, NO zipper.\n- NO sleeve patches (there are no sleeves to patch).\n- NO heat-transfer vinyl other than the sublimated medallion + sublimated\n  pattern.",
    "scene_pose": "Front view straight-on showing the round medallion + \"THE BAY\"\n  + lower NBA patch + the fading rose pattern at the hem. Three-quarter view\n  catches the armhole binding and the side wrap of the rose pattern. Back\n  view shows the small black SR monogram, the stacked gold \"BLACK / IS /\n  BEAUTIFUL\" lettering, and the matching fading hem pattern.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/nba-authentic-collection-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-010-design-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-010-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": null,
    "packshot": {
      "path": "assets/images/products/br-010-the-bay-basketball.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-basketball-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-basketball-back.jpeg",
    "reference": "assets/products/references/br-010-design-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "nba-authentic-collection-card",
        "position": "front_patch",
        "technique": "custom_basketball_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-3-the-bay-basketball.md",
      "source_sha256": "a70d8554ca5cc1d081d5e54b96b31d20c229590036e0a7890b9dfed44796eeb4",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "diameter",
            "min": 6.0,
            "max": 7.0
          },
          "source_size_text": "large, ~6–7in diameter, vertically centered on the upper chest",
          "source_line": 48,
          "scope_note": "6–7 inch diameter applies to the complete medallion including THE BAY, not the lettering height."
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall, against the fading rose pattern",
          "source_line": 54,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide",
          "source_line": 59
        },
        {
          "position_as_documented": "back-upper-center",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "height",
            "min": 6.0,
            "max": 6.0
          },
          "source_size_text": "stacked vertically on three lines, ~6in tall total",
          "source_line": 62,
          "scope_note": "6 inch height applies to the complete three-line stack, not each line."
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "source_snapshot_pointer": "#/products/br-010/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-basketball-jersey/nba-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "basketball",
    "sku_folder": "black-is-beautiful-basketball-jersey"
  },
  "content": {
    "description": {
      "value": "Basketball tank with \"THE BAY\" gold text. Rose circle graphic, grey/silver rose fade. Bay Area edition — 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Basketball tank with \"THE BAY\" gold text. Rose circle graphic, grey/silver rose fade. Bay Area edition — 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back",
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.630449+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-011 — BLACK is Beautiful Jersey Series: 4. The Rose (Hockey)

```json
{
  "sku": "br-011",
  "name": "BLACK is Beautiful Jersey Series: 4. The Rose (Hockey)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-011",
    "name": "BLACK is Beautiful Jersey Series: 4. The Rose (Hockey)",
    "price": "115",
    "collection": "black-rose",
    "description": "Hooded hockey jersey in black and teal. San Jose Sharks inspired, rose crest on front. Exclusive edition — 80 pieces.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-011-the-rose-hockey.png",
    "front_model_image": "assets/images/products/br-011-onmodel.webp",
    "back_image": "assets/images/products/black-is-beautiful-hockey-jersey-back-model.webp",
    "back_model_image": "assets/images/products/black-is-beautiful-hockey-jersey-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black/Teal",
    "edition_size": "80",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Use the existing successful render as reference — vision pipeline produced a good first render of this SKU. Preserve the established composition.",
    "render_output_slug": "jersey-the-rose-hockey",
    "render_source_override": "br-011-the-rose-hockey.png",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "hoodie",
    "dossier_slug": "black-is-beautiful-jersey-series-4-the-rose-hockey",
    "engine_override": "gemini-pro"
  },
  "garment": {
    "color": "Black/Teal",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid **black** base body fabric with **teal/turquoise (cyan)** accent\ncolorway. Mid-weight knit fabric, hockey-jersey-weight. NOT a sherpa jacket\n(distinct from br-006 which is a separate satin bomber).",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Hockey-style pullover hoodie with long sleeves and a\nhood — round-neck pullover construction, hood with **bright teal/turquoise\ninner lining** against a black hood exterior, long sleeves ending in a\nlayered striped cuff band, straight hem with a matching layered striped hem\nband. Solid **black** base body fabric with **teal/turquoise (cyan)** accent\ncolorway. Mid-weight knit fabric, hockey-jersey-weight. NOT a basketball\ntank. NOT a baseball jersey. NOT a football jersey. NOT a sherpa jacket\n(distinct from br-006 which is a separate satin bomber). **PRE-ORDER product**\n— design renderings only.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-011/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-011",
    "name": "BLACK is Beautiful Jersey Series — 4. The Rose (Hockey)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-4-the-rose-hockey",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid **black** base body fabric with **teal/turquoise (cyan)** accent\ncolorway. Mid-weight knit fabric, hockey-jersey-weight. NOT a sherpa jacket\n(distinct from br-006 which is a separate satin bomber).\nFeatures: Hockey-style pullover hoodie with long sleeves and a\nhood — round-neck pullover construction, hood with **bright teal/turquoise\ninner lining** against a black hood exterior, long sleeves ending in a\nlayered striped cuff band, straight hem with a matching layered striped hem\nband. Solid **black** base body fabric with **teal/turquoise (cyan)** accent\ncolorway. Mid-weight knit fabric, hockey-jersey-weight. NOT a basketball\ntank. NOT a baseball jersey. NOT a football jersey. NOT a sherpa jacket\n(distinct from br-006 which is a separate satin bomber). **PRE-ORDER product**\n— design renderings only.\nColor: Black/Teal\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Hockey Championship patch:     `data/brand-logos/hockey-championship-patch.md`\n> - SR monogram (back-neck):       `data/brand-logos/sr-monogram.md`\n> - Product design render:          `assets/products/references/br-011-design-front.jpeg`\n>\n> ### COLORWAY OVERRIDE — read this BEFORE rendering\n>\n> All decoration on this jersey is rendered in the **teal/turquoise + black +\n> white** colorway, NOT canonical multi-color. The Black Rose three-rose-cluster\n> medallion uses **teal/cyan roses** (instead of greyscale or red), with\n> black ink outlines and white highlights — a unique colorway treatment for\n> this product. The number \"0\" follows the same teal-on-black palette. The\n> SR monogram is rendered in **teal/cyan thread** (NOT canonical gold).\n\n### Front\n- **front-chest** (large, ~6–7in diameter, vertically centered on the upper\n  chest): A circular medallion with a teal/cyan + white double-ring border,\n  containing the canonical Black Rose three-rose-cluster art rendered in\n  **teal/cyan** (with black ink outlines and white highlights). The roses,\n  vines, and cloud are all preserved in shape but recolored to the cyan\n  palette. **Technique:** sublimated. **Color:** teal/cyan rose-cluster +\n  black + white on black ground.\n- **front-shoulder-left / front-shoulder-right** (small, ~2in tall, on each\n  shoulder): A small white-thread embroidered emblem of the rose-cluster\n  silhouette outline (simplified single-color version). **Technique:**\n  embroidered. **Color:** white thread on black.\n- **front-collar-area / upper-center-collar** (small, ~1in wide, just below\n  the hood opening at the V): A small black-and-white hockey-style league\n  emblem (a stylized shield with hockey stick + puck details, woven flat).\n  **Technique:** woven-label. **Color:** black + white.\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall, against the\n  striped hem band): The Hockey Championship patch (greyscale/silver palette\n  patch — see hockey-championship-patch reference). Sewn onto the lower-left\n  hip. **Technique:** embroidered-patch.\n\n### Back\n- **back-neck** (small, ~2in wide): The SR monogram embroidered directly\n  onto the jersey in **teal/cyan thread** (matches the colorway palette).\n  **Technique:** embroidered. **Color:** teal/cyan thread on black.\n- **back-yoke / upper-back** (arched, ~9in wide): The phrase **\"BLACK IS\n  BEAUTIFUL\"** in tackle-twill lettering, baseball-script style, arched across\n  the upper back. Rendered in **teal/cyan twill** on the black body.\n  **Technique:** tackle-twill. **Color:** teal/cyan twill letters on black\n  ground.\n- **back-center** (large, ~10in tall, vertically centered): The number\n  **\"0\"** rendered with a **teal/cyan outline edge** and a teal-and-black\n  rose-cluster art fill inside the digit form. **Technique:** sublimated.\n  **Color:** teal/cyan outline + teal-and-black rose-cluster fill.\n\n### Sleeves / Hood / Hem / Other\n- **hood-exterior**: Black to match the body. **Technique:** stitched.\n  **Color:** black.\n- **hood-interior / hood-lining**: Bright teal/turquoise lining inside the\n  hood (visible when the hood is laid back or worn down). **Technique:**\n  stitched. **Color:** teal/turquoise.\n- **left-cuff / right-cuff striped band**: Each long-sleeve cuff ends in a\n  layered striped band — solid black at the top, then a teal stripe, then\n  white, then a series of thin teal stripes / parallel teal lines descending\n  toward the cuff edge. **Technique:** sublimated. **Color:** layered black\n  + teal/cyan + white.\n- **hem / waistband striped band**: The bottom hem of the body has the\n  matching striped band — solid black above, teal stripe, white, then thin\n  teal stripes wrapping front and back. **Technique:** sublimated. **Color:**\n  layered black + teal + white.\n- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal\n  SkyyRose product rule). **Technique:** woven-label.",
    "negative_block": "- NO red anywhere — this is the teal/cyan colorway, NOT a red colorway.\n- NO yellow / gold anywhere on this jersey (the colorway is black + teal +\n  white only).\n- NO multi-color canonical rose-cluster — the rose-cluster is recolored to\n  teal/cyan + black + white. NO red roses. NO kelly-green stems. NO\n  white-and-blue cloud color.\n- NO solid-color \"0\" digit — the digit has teal outline + rose-cluster fill.\n- NO MLB Authentic Collection patch. NO NFL Authentic Collection patch. NO\n  NBA Authentic Collection patch — only the Hockey Championship patch.\n- NO NHL logos, no barcode labels, no real sports league trademarks. The\n  collar emblem is a GENERIC black-and-white hockey-style woven league\n  label — NOT the NHL shield mark, NOT any real-league trademark. The\n  hem patch is the greyscale Hockey Championship patch — NOT a retail\n  barcode/UPC label, NOT a price tag, NOT a hangtag.\n- NO embossed/debossed decoration.\n- NO buttons, NO placket, NO zipper — pullover construction.\n- NO laces at the V-neck (this is a fashion hoodie, not a tied-collar hockey\n  jersey).\n- NO standalone embroidered Black Rose rose-cluster on the back-center other\n  than as digit fill — the rose-cluster appears as fill inside the \"0\" digit\n  + the front medallion + the small white shoulder emblems, NOT as a separate\n  back-center embroidered logo.\n- NO gold thread anywhere — the SR monogram and lettering are teal, not gold.\n- NO solid teal hood exterior — the hood EXTERIOR is BLACK; only the\n  INTERIOR LINING is teal.\n- NO sublimated all-over body pattern — the body is solid black with the\n  noted decorations only (distinct from br-010 which has the all-over fading\n  rose pattern).\n- NO pinstripes.",
    "scene_pose": "Front view straight-on showing the teal rose medallion + small\n  shoulder emblems + small collar league mark + lower-left Hockey Championship\n  patch + striped cuff and hem bands. Three-quarter view catches the teal hood\n  lining peeking inside. Back view shows the teal-twill \"BLACK IS BEAUTIFUL\"\n  arch + the small teal SR monogram + the back-center \"0\" + the matching\n  striped hem.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/hockey-championship-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-011-design-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-011-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/br-011-the-rose-hockey-back.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-011-the-rose-hockey.png",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/black-is-beautiful-hockey-jersey-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-hockey-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-hockey-back.jpeg",
    "reference": "assets/products/references/br-011-design-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "hockey-championship-card",
        "position": "front_patch",
        "technique": "custom_hockey_patch",
        "notes": "Hockey Championship card — different visual style from NBA/NFL cards (gray ground, shield with sticks+puck, minimalist)."
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-4-the-rose-hockey.md",
      "source_sha256": "007e6d73174f8b4c8ddaa0a0d618ccfb9af8ce0aa9e2091377501eb7879506c0",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "diameter",
            "min": 6.0,
            "max": 7.0
          },
          "source_size_text": "large, ~6–7in diameter, vertically centered on the upper chest",
          "source_line": 43
        },
        {
          "position_as_documented": "front-shoulder-left / front-shoulder-right",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "height",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in tall, on each shoulder",
          "source_line": 50
        },
        {
          "position_as_documented": "front-collar-area / upper-center-collar",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 1.0,
            "max": 1.0
          },
          "source_size_text": "small, ~1in wide, just below the hood opening at the V",
          "source_line": 54
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall, against the striped hem band",
          "source_line": 58,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide",
          "source_line": 64
        },
        {
          "position_as_documented": "back-yoke / upper-back",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "width",
            "min": 9.0,
            "max": 9.0
          },
          "source_size_text": "arched, ~9in wide",
          "source_line": 67
        },
        {
          "position_as_documented": "back-center",
          "kind": "number",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 10.0
          },
          "source_size_text": "large, ~10in tall, vertically centered",
          "source_line": 72
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "source_snapshot_pointer": "#/products/br-011/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-hockey-jersey/hockey-championship-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "hockey",
    "sku_folder": "black-is-beautiful-hockey-jersey"
  },
  "content": {
    "description": {
      "value": "Hooded hockey jersey in black and teal. San Jose Sharks inspired, rose crest on front. Exclusive edition — 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Hooded hockey jersey in black and teal. San Jose Sharks inspired, rose crest on front. Exclusive edition — 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [
    {
      "text": "[ghost-back] adjust hood",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] adjust hood",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.636055+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-012 — BLACK is Beautiful Jersey Series: 5. Baseball Classic (Last Oakland)

```json
{
  "sku": "br-012",
  "name": "BLACK is Beautiful Jersey Series: 5. Baseball Classic (Last Oakland)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-012",
    "name": "BLACK is Beautiful Jersey Series: 5. Baseball Classic (Last Oakland)",
    "price": "100",
    "collection": "black-rose",
    "description": "Green button-front baseball jersey with \"BLACK IS BEAUTIFUL\" arched in gold. Rose crest on back. Limited to 80 pieces.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-012-last-oakland-baseball-front.jpeg",
    "front_model_image": "assets/images/products/jersey-last-oakland-baseball-front-model.webp",
    "back_image": "assets/images/products/br-012-last-oakland-baseball-back.jpeg",
    "back_model_image": "assets/images/products/br-012-last-oakland-baseball-back.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Green/Gold",
    "edition_size": "80",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Green button-front baseball jersey. FRONT: 'BLACK IS BEAUTIFUL' arched across approximately 72% of visible torso width matching the physical flatlay; white letter faces except black A, gold satin-stitch edge. Preserve gold/yellow piping, sleeves and placket. MLB Authentic Collection patch at wearer-left lower hem, 3 inches wide x 4 inches tall. BACK: large embroidered black rose rising from gold clouds, monogram 'SR' at upper neck in gold.",
    "render_output_slug": "jersey-last-oakland-baseball",
    "render_source_override": "br-012-last-oakland-baseball-front.jpeg",
    "render_back_source_override": "br-012-last-oakland-baseball-back.jpeg",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-5-last-oakland-baseball",
    "engine_override": ""
  },
  "garment": {
    "color": "Green/Gold",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid **dark forest green** base fabric. Mid-weight knit jersey.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style baseball jersey — V-neck collar opening with gold/yellow piping, button-front placket with gold/yellow piping, short sleeves with gold/yellow cuff piping, straight even hem (no drop-tail). Solid **dark forest green** base fabric. Mid-weight knit jersey. NOT a t-shirt, NOT a hoodie, NOT a basketball tank, NOT a football jersey. **PRE-ORDER product**.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-012/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-012",
    "name": "BLACK is Beautiful Jersey Series — 5. Baseball Classic (Last Oakland)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-5-last-oakland-baseball",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid **dark forest green** base fabric. Mid-weight knit jersey.\nFeatures: Authentic-style baseball jersey — V-neck collar opening with gold/yellow piping, button-front placket with gold/yellow piping, short sleeves with gold/yellow cuff piping, straight even hem (no drop-tail). Solid **dark forest green** base fabric. Mid-weight knit jersey. NOT a t-shirt, NOT a hoodie, NOT a basketball tank, NOT a football jersey. **PRE-ORDER product**.\nColor: Green/Gold\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`\n> - SR monogram:                   `data/brand-logos/sr-monogram.md`\n\n### Front\n- **front-chest** (large, arched, approximately 72% of visible torso width, matching the physical flatlay): The phrase **\"BLACK IS BEAUTIFUL\"**\n  as authentic tackle-twill lettering with a **gold satin-stitch edge**\n  surrounding the letter faces. The contrast satin-stitch edge is integral\n  to this colorway's look (vs. the Classic black which has no contrast edge).\n  - **Letter faces — WHITE twill**, EXCEPT…\n  - **The \"A\" in \"BLACK\" — BLACK twill** (the only black letter face, a\n    deliberate stylistic accent that calls back to the Oakland Athletics'\n    team-A identity).\n  - **Satin-stitch edge — gold** around every letter (including the black A).\n  - **Technique:** tackle-twill. **Color:** white twill faces (with one black\n    \"A\") + gold satin-stitch edge.\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall): The Black Rose\n  MLB Authentic Collection patch (yellow field, navy \"BLACK ROSE / COLLECTION\",\n  MLB-style batter silhouette, white \"AUTHENTIC\" banner, red diamond divider,\n  \"Members Only / Yay Area, Ca\", SkyyRose script logo, \"Made for Kings ang\n  Queens\"). Sewn onto the lower-left hip. **Technique:** embroidered-patch.\n\n### Back\n- **back-neck** (small, ~2in wide): The SR monogram, embroidered directly\n  onto the jersey in **gold-tone thread** (matching the colorway theme — the\n  SR mark renders in gold to match the gold satin-stitch edge and the gold\n  piping). **Technique:** embroidered. **Color:** gold-tone thread.\n- **back-center** (~10in–12in tall): The Black Rose logo embroidered directly\n  onto the jersey. The roses, stems, and thorny vines are rendered in\n  **white thread**; the cloud at the base of the cluster is rendered in\n  **yellow/gold thread** (a colorway-specific accent — the cloud picks up\n  the Oakland yellow palette while the rose-cluster stays white-thread).\n  **Technique:** embroidered. **Color:** white thread on the rose-cluster +\n  yellow/gold thread on the cloud at the base.\n\n### Sleeves / Collar / Hem / Other\n- **collar / V-neck binding**: Gold/yellow contrast piping/binding around the\n  V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.\n  **Color:** gold/yellow.\n- **left-cuff / right-cuff binding**: Gold/yellow piping around both sleeve\n  cuff openings. **Technique:** stitched. **Color:** gold/yellow.\n- **front-placket binding**: Gold/yellow piping running vertically down both\n  sides of the front button placket. **Technique:** stitched. **Color:**\n  gold/yellow.\n- **front-placket buttons** (~5–6 buttons, evenly spaced down the placket).\n  **Technique:** patch (sewn-on hardware). **Color:** body-matching\n  (green/yellow tone — blends with the placket).\n- **collar-inside** (~1.75in × 0.75in): Woven brand label sewn into the\n  inside back of the collar. **Technique:** woven-label.",
    "negative_block": "- NO player number, NO player name on front, back, or sleeves.\n- NO white piping (this colorway uses GOLD/YELLOW piping — not white).\n- NO orange piping (that's the Giants colorway).\n- NO black piping (that's the White edition).\n- NO solid-yellow tackle-twill letters — letter FACES are WHITE (with one\n  black \"A\"); only the satin-stitch EDGE is gold.\n- NO uniform letter color — the \"A\" in \"BLACK\" is BLACK while every other\n  letter is white. This is the colorway's signature detail.\n- NO contrast satin edge OTHER than gold (no white edge, no red edge).\n- NO gold thread on the rose-cluster — only the cloud is yellow/gold thread;\n  the roses and stems are WHITE thread.\n- NO multi-color rendering of the rose-cluster (kelly-green stems, etc.) —\n  the cluster is white thread; the cloud is the only colorway accent in gold.\n- NO orange or red anywhere on this colorway.\n- NO Black Rose logo on the chest — the chest carries only the tackle-twill\n  wordmark and the lower-left Authentic Collection patch.\n- NO SR monogram on the back-center — that region is the rose-cluster only.\n- NO sleeve patches anywhere on this jersey.\n- NO pinstripes, NO embossed/debossed, NO sublimated panels, NO heat-transfer\n  vinyl, NO printed graphics on the body.\n- NO chest-pocket or breast-pocket.",
    "scene_pose": "Front view straight-on or three-quarter front-left to display\n  the gold-edged tackle-twill wordmark with the black \"A\" accent; back view\n  straight-on for the embroidered logos.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/black-rose-authentic-collection-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-012-techflat.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/jersey-last-oakland-baseball-front-model.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/br-012-last-oakland-baseball-back.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-012-last-oakland-baseball-front.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/br-012-last-oakland-baseball-back.jpeg",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/last-oakland-baseball-jersey-front.jpeg",
    "back": "wordpress-theme/skyyrose-flagship/assets/images/products/br-012-last-oakland-baseball-back.jpeg",
    "reference": "assets/products/references/br-012-techflat.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_center",
        "technique": "embroidered"
      },
      {
        "logo_id": "mlb-authentic-collection-card",
        "position": "front_patch",
        "technique": "custom_baseball_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-5-last-oakland-baseball.md",
      "source_sha256": "d9356bba1e8a310664d3dd0138bf127d2e3fac02441825bcc0ec9350f8c53fe0",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "lettering",
          "source_size_text": "large, arched, approximately 72% of visible torso width, matching the physical flatlay",
          "source_line": 28,
          "relative_dimension": {
            "axis": "width",
            "ratio": 0.72,
            "reference": "visible_garment_torso_width_excluding_sleeves",
            "method": "RECOVERED_FLATLAY_DERIVED_TARGET"
          },
          "authority_reference": "data/brand-logos/baseball-lettering-sizing.md"
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall",
          "source_line": 39,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide",
          "source_line": 46
        },
        {
          "position_as_documented": "back-center",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 12.0
          },
          "source_size_text": "~10in–12in tall",
          "source_line": 50
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "lettering_reference": "data/brand-logos/baseball-lettering-sizing.md",
      "source_snapshot_pointer": "#/products/br-012/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/jersey-last-oakland-baseball/mlb-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "baseball",
    "sku_folder": "jersey-last-oakland-baseball"
  },
  "content": {
    "description": {
      "value": "Green button-front baseball jersey with \"BLACK IS BEAUTIFUL\" arched in gold. Rose crest on back. Limited to 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Green button-front baseball jersey with \"BLACK IS BEAUTIFUL\" arched in gold. Rose crest on back. Limited to 80 pieces.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.744626+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-014 — BLACK is Beautiful Jersey Series: 0. Baseball Classic (Giants)

```json
{
  "sku": "br-014",
  "name": "BLACK is Beautiful Jersey Series: 0. Baseball Classic (Giants)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-014",
    "name": "BLACK is Beautiful Jersey Series: 0. Baseball Classic (Giants)",
    "price": "100",
    "collection": "black-rose",
    "description": "Special edition Giants colorway with black and orange accents.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-014-baseball-classic-giants.jpeg",
    "front_model_image": "assets/images/products/br-014-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/br-014-giants-back.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black/Orange",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Giants colorway: Black and Orange theme.",
    "render_output_slug": "black-is-beautiful-jersey-giants",
    "render_source_override": "br-014-baseball-classic-giants.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-0-baseball-classic-giants",
    "engine_override": ""
  },
  "garment": {
    "color": "Black/Orange",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid BLACK base fabric with **bright orange** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Mid-weight knit jersey.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid BLACK base fabric with **bright orange** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. **Black** buttons on the placket (matching the body, no contrast). NO player number on front. NO player number on back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the GIANTS colorway (separate SKU from the Classic black-with-white-piping br-003).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-014/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-014",
    "name": "BLACK is Beautiful Jersey Series — 0. Baseball Classic (Giants)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-0-baseball-classic-giants",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid BLACK base fabric with **bright orange** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Mid-weight knit jersey.\nFeatures: Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid BLACK base fabric with **bright orange** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. **Black** buttons on the placket (matching the body, no contrast). NO player number on front. NO player number on back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the GIANTS colorway (separate SKU from the Classic black-with-white-piping br-003).\nColor: Black/Orange\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`\n> - SR monogram:                   `data/brand-logos/sr-monogram.md`\n> - Product techflat:              `assets/products/references/br-014-techflat.jpeg`\n> - Real product photos:           `assets/products/references/br-014-real-front.jpeg`,\n>                                  `assets/products/references/br-014-real-back.jpeg`\n\n### Front\n- **front-chest** (large, arched, ~9in wide): The phrase **\"BLACK IS BEAUTIFUL\"**\n  as authentic tackle-twill lettering — pre-cut **bright orange** fabric letters\n  appliquéd onto the black jersey body in a baseball-script style, arched across\n  the upper-front-chest. **Technique:** tackle-twill. **Color:** bright orange\n  twill (NO contrast satin-stitch edge — clean orange-on-black).\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall): The Black Rose\n  Authentic Collection patch (full multi-color: yellow field, navy text,\n  white banner, red diamond divider, etc. — see patch reference). Sewn onto\n  the lower-left hip. **Technique:** embroidered-patch.\n\n### Back\n- **back-neck** (small, ~2in wide): The SR monogram, embroidered directly\n  onto the jersey in **orange-tone thread** (matching the colorway theme — the\n  techflat and real product photo confirm an orange-toned rendering, distinct\n  from the Classic's gold-tone). **Technique:** embroidered. **Color:** bright\n  orange thread.\n- **back-center** (~10in–12in tall): The Black Rose logo embroidered directly\n  onto the jersey in **white thread on the black fabric** (same treatment as\n  the Classic black colorway — single-color white-thread silhouette\n  preserving the canonical art's shapes). **Technique:** embroidered.\n  **Color:** white thread.\n\n### Sleeves / Collar / Hem / Other\n- **collar / V-neck binding**: Bright orange contrast piping/binding around\n  the V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.\n  **Color:** bright orange.\n- **left-cuff / right-cuff binding**: Bright orange piping around both sleeve\n  cuff openings. **Technique:** stitched. **Color:** bright orange.\n- **front-placket binding**: Bright orange piping running vertically down both\n  sides of the front button placket. **Technique:** stitched. **Color:**\n  bright orange.\n- **front-placket buttons** (~5–6 buttons, plain BLACK, evenly spaced):\n  **Technique:** patch (sewn-on hardware). **Color:** black (NOT white).\n- **collar-inside** (~1.75in × 0.75in): Woven brand label sewn into the\n  inside back of the collar. **Technique:** woven-label.",
    "negative_block": "- NO player number, NO player name on front or back or sleeves.\n- NO white piping (this colorway uses ORANGE piping — not white).\n- NO white tackle-twill letters (the BIB wordmark is ORANGE — not white,\n  not gold, not yellow).\n- NO white buttons (this colorway uses BLACK buttons).\n- NO gold-tone SR monogram (this colorway's monogram is in ORANGE thread —\n  the gold version is on the Classic black br-003).\n- NO multi-color back-rose embroidery — the back-center rose is white-thread\n  silhouette only (NOT the canonical multi-color art).\n- NO Black Rose logo on the chest — the chest carries only the tackle-twill\n  wordmark and lower-left Authentic Collection patch.\n- NO SR monogram on the back-center — back-center is the rose-cluster only.\n- NO sleeve patches anywhere.\n- NO pinstripes, NO embossed/debossed, NO sublimated panels, NO heat-transfer\n  vinyl, NO printed graphics on the body.\n- NO contrast colors other than orange — no green, no yellow, no red elsewhere.\n- NO contrast satin-stitch edge around the tackle-twill letters.",
    "scene_pose": "Front view straight-on or three-quarter front-left for the chest\n  wordmark; back view straight-on for the embroidered logos.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting,\n  subtle natural drop shadow.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/black-rose-authentic-collection-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-014-techflat.jpeg",
    "extra_references": [
      "assets/products/references/br-014-real-front.jpeg",
      "assets/products/references/br-014-real-back.jpeg"
    ]
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-014-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/br-014-giants-back.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-014-baseball-classic-giants.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-baseball-giants-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-baseball-giants-back.jpeg",
    "reference": "assets/products/references/br-014-real-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_center",
        "technique": "embroidered",
        "notes": "Large back logo (matches br-003 baseline)."
      },
      {
        "logo_id": "mlb-authentic-collection-card",
        "position": "front_patch",
        "technique": "custom_baseball_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-0-baseball-classic-giants.md",
      "source_sha256": "6918b34916f69ad64a3553109bf128e839658686be048efd442b2e0e47145da5",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "width",
            "min": 9.0,
            "max": 9.0
          },
          "source_size_text": "large, arched, ~9in wide",
          "source_line": 31
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall",
          "source_line": 36,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide",
          "source_line": 42
        },
        {
          "position_as_documented": "back-center",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 12.0
          },
          "source_size_text": "~10in–12in tall",
          "source_line": 47
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "lettering_reference": "data/brand-logos/baseball-lettering-sizing.md",
      "source_snapshot_pointer": "#/products/br-014/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-jersey-giants/mlb-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "baseball",
    "sku_folder": "black-is-beautiful-jersey-giants"
  },
  "content": {
    "description": {
      "value": "Special edition Giants colorway with black and orange accents.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Special edition Giants colorway with black and orange accents.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.776563+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## br-015 — BLACK is Beautiful Jersey Series: 0. Baseball Classic (White)

```json
{
  "sku": "br-015",
  "name": "BLACK is Beautiful Jersey Series: 0. Baseball Classic (White)",
  "collection": "black-rose",
  "catalog": {
    "sku": "br-015",
    "name": "BLACK is Beautiful Jersey Series: 0. Baseball Classic (White)",
    "price": "100",
    "collection": "black-rose",
    "description": "Special edition White colorway of the Baseball Classic jersey.",
    "badge": "Pre-Order",
    "image": "assets/images/products/br-015-baseball-classic-white.jpeg",
    "front_model_image": "assets/images/products/br-015-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/black-is-beautiful-jersey-white/black-is-beautiful-jersey-white-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "White colorway with black accents.",
    "render_output_slug": "black-is-beautiful-jersey-white",
    "render_source_override": "br-015-baseball-classic-white.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jersey",
    "dossier_slug": "black-is-beautiful-jersey-series-0-baseball-classic-white",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Solid **white** base fabric with **black** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Mid-weight knit jersey.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid **white** base fabric with **black** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Black buttons on the placket. NO player number on front or back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the WHITE colorway (separate SKU from Classic black br-003 / Giants br-014 / Oakland br-012).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": "#/sku_logos/br-015/decoration_sizing",
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "br-015",
    "name": "BLACK is Beautiful Jersey Series — 0. Baseball Classic (White)",
    "collection": "black-rose",
    "slug": "black-is-beautiful-jersey-series-0-baseball-classic-white",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Solid **white** base fabric with **black** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Mid-weight knit jersey.\nFeatures: Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid **white** base fabric with **black** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Black buttons on the placket. NO player number on front or back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the WHITE colorway (separate SKU from Classic black br-003 / Giants br-014 / Oakland br-012).\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`\n> - SR monogram:                   `data/brand-logos/sr-monogram.md`\n> - Product techflat:              `assets/products/references/br-015-techflat.jpeg`\n\n### Front\n- **front-chest** (large, arched, ~9in wide): The phrase **\"BLACK IS BEAUTIFUL\"**\n  as authentic tackle-twill lettering — pre-cut **black** fabric letters\n  appliquéd onto the white jersey body in a baseball-script style, arched\n  across the upper-front-chest. **Technique:** tackle-twill. **Color:** black\n  twill letters (the inverse colorway treatment of the Classic black; clean\n  black-on-white with no contrast satin-stitch edge).\n- **front-left-hem / front-belly-lower-left** (3in wide × 4in tall): The Black Rose\n  Authentic Collection patch (full multi-color — yellow field, navy text,\n  white banner, red diamond divider, etc.). Sewn onto the lower-left hip.\n  **Technique:** embroidered-patch.\n\n### Back\n- **back-neck** (small, ~2in wide): The SR monogram, embroidered directly\n  onto the jersey in **black or dark-tone thread** (the gold-on-white would\n  read poorly; the colorway uses black thread to maintain the high-contrast\n  reading). **Technique:** embroidered. **Color:** black thread.\n- **back-center** (~10in–12in tall): The Black Rose logo embroidered directly\n  onto the jersey in **black thread on the white fabric** (the inverse\n  treatment of the Classic black colorway's white-on-black). The composition's\n  shapes (three roses, stems, thorny vines, cloud) are preserved via the\n  original art's outlines and inner shading; on white background, the\n  embroidered art may show greyscale shading more naturally — petals can\n  carry darker fills, cloud renders lighter (grey-thread or stitch-density\n  variation). **Technique:** embroidered. **Color:** primarily black thread\n  with optional grey-thread shading on the cloud and lighter rose details.\n\n### Sleeves / Collar / Hem / Other\n- **collar / V-neck binding**: Black contrast piping/binding around the\n  V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.\n  **Color:** black.\n- **left-cuff / right-cuff binding**: Black piping around both sleeve cuff\n  openings. **Technique:** stitched. **Color:** black.\n- **front-placket binding**: Black piping running vertically down both sides\n  of the front button placket. **Technique:** stitched. **Color:** black.\n- **front-placket buttons** (~5–6 buttons, plain BLACK or dark-tone, evenly\n  spaced). **Technique:** patch (sewn-on hardware). **Color:** black.\n- **collar-inside** (~1.75in × 0.75in): Woven brand label sewn into the\n  inside back of the collar. **Technique:** woven-label.",
    "negative_block": "- NO player number, NO player name on front, back, or sleeves.\n- NO white piping (this colorway uses BLACK piping — not white).\n- NO orange piping (that's the Giants colorway).\n- NO gold/yellow piping (that's the Oakland colorway).\n- NO white tackle-twill letters (the BIB wordmark is BLACK on white — the\n  inverse of the Classic colorway).\n- NO white buttons (this colorway uses black buttons).\n- NO gold-tone SR monogram (this colorway's monogram is in BLACK thread).\n- NO Black Rose logo on the chest — the chest carries only the tackle-twill\n  wordmark and the lower-left Authentic Collection patch.\n- NO SR monogram on the back-center — back-center is the rose-cluster only.\n- NO sleeve patches anywhere.\n- NO contrast colors other than black on this colorway — no orange, no\n  yellow, no red elsewhere on the body fabric.\n- NO multi-color (kelly-green / blue / yellow) rendering of the back rose;\n  this is a black-thread embroidery (with optional grey shading).\n- NO contrast satin-stitch edge around the tackle-twill letters.\n- NO pinstripes, NO embossed/debossed, NO sublimated panels, NO heat-transfer\n  vinyl, NO printed graphics on the body.\n- NO special \"A\" treatment (the colorway-specific black-A is Oakland's\n  signature; on the White edition every letter is uniformly black).",
    "scene_pose": "Front view straight-on or three-quarter front-left to display\n  the high-contrast black tackle-twill wordmark on the white body; back view\n  for the embroidered black-thread Black Rose logo.",
    "scene_setting": "Pure white studio backdrop with subtle directional lighting\n  to define the white-on-white silhouette and avoid blowing out the body\n  fabric. Soft natural drop shadow.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/black-rose-authentic-collection-patch.md",
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/br-015-techflat.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/br-015-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/black-is-beautiful-jersey-white/black-is-beautiful-jersey-white-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/br-015-baseball-classic-white.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/black-rose/br-jersey-baseball-white-front.jpeg",
    "back": "assets/products/techflats/split/black-rose/br-jersey-baseball-white-back.jpeg",
    "reference": "assets/products/references/br-015-techflat.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_center",
        "technique": "embroidered",
        "notes": "Large back logo (matches br-003 baseline)."
      },
      {
        "logo_id": "mlb-authentic-collection-card",
        "position": "front_patch",
        "technique": "custom_baseball_patch"
      }
    ],
    "decoration_sizing": {
      "status": "FOUNDER_CONFIRMED",
      "source": "data/dossiers/black-is-beautiful-jersey-series-0-baseball-classic-white.md",
      "source_sha256": "c5fff8e858d510ce68edb2ac28892d9535ad427be949f85e9acd225cd0c41798",
      "units": "inches",
      "measurement_scope": "Overall physical decoration dimensions in inches. Preserve the founder-documented values and ranges; these are not typographic point sizes.",
      "font_file": null,
      "items": [
        {
          "position_as_documented": "front-chest",
          "kind": "lettering",
          "dimension_inches": {
            "axis": "width",
            "min": 9.0,
            "max": 9.0
          },
          "source_size_text": "large, arched, ~9in wide",
          "source_line": 26
        },
        {
          "position_as_documented": "front-left-hem / front-belly-lower-left",
          "kind": "patch",
          "dimension_inches": {
            "width": 3,
            "height": 4,
            "orientation": "portrait"
          },
          "source_size_text": "3in wide × 4in tall",
          "source_line": 32,
          "scope_note": "Founder-confirmed complete patch: 3 inches wide × 4 inches tall. Preserve the registered patch artwork and internal lettering proportions.",
          "authority_reference": "data/brand-logos/jersey-patch-sizing.md"
        },
        {
          "position_as_documented": "back-neck",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "width",
            "min": 2.0,
            "max": 2.0
          },
          "source_size_text": "small, ~2in wide",
          "source_line": 38
        },
        {
          "position_as_documented": "back-center",
          "kind": "graphic",
          "dimension_inches": {
            "axis": "height",
            "min": 10.0,
            "max": 12.0
          },
          "source_size_text": "~10in–12in tall",
          "source_line": 42
        }
      ],
      "authority": {
        "role": "Founder and maker of the items",
        "confirmation": "i made the items thats the only verification you need",
        "scope": "Jersey decoration dimensions recorded from founder-authored dossiers; no additional manufacturing verification required."
      },
      "lettering_reference": "data/brand-logos/baseball-lettering-sizing.md",
      "source_snapshot_pointer": "#/products/br-015/dossier/content",
      "source_snapshot_note": "source_sha256 and source_line identify the founder specification preserved at this internal pointer. The external dossier is a generated compatibility projection."
    },
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/products/black-is-beautiful-jersey-white/mlb-authentic-collection-card.jpeg",
    "reference_kind": "patch",
    "patch_sport": "baseball",
    "sku_folder": "black-is-beautiful-jersey-white"
  },
  "content": {
    "description": {
      "value": "Special edition White colorway of the Baseball Classic jersey.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Special edition White colorway of the Baseball Classic jersey.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.792426+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## kids-001 — Kids Colorblock Hoodie Set — Red/Black

```json
{
  "sku": "kids-001",
  "name": "Kids Colorblock Hoodie Set — Red/Black",
  "collection": "kids-capsule",
  "catalog": {
    "sku": "kids-001",
    "name": "Kids Colorblock Hoodie Set — Red/Black",
    "price": "65",
    "collection": "kids-capsule",
    "description": "Bold red and black V-chevron colorblock hoodie and jogger set. Designed for young ones who wear luxury from the start.",
    "badge": "",
    "image": "assets/images/products/kids-001-red-set.jpeg",
    "front_model_image": "assets/images/products/kids-001-onmodel-v2.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/kids-red-set-back-model.webp",
    "sizes": "2T|3T|4T|5|6|7",
    "color": "Red/Black/White",
    "edition_size": "150",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Black rose embroidered logo on the left chest and the left thigh. Right arm features a circular patch logo: white background, black lettering, black rose in center. Patch text: 'Skyy Rose' arched on top, 'Collection' arched on bottom.",
    "render_output_slug": "kids-red-set",
    "render_source_override": "kids-001-red-set.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "hoodie",
    "dossier_slug": "kids-colorblock-hoodie-set-red-black",
    "engine_override": ""
  },
  "garment": {
    "color": "Red/Black/White",
    "available_sizes": [
      "2T",
      "3T",
      "4T",
      "5",
      "6",
      "7"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Mid-weight cotton-fleece fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Two-piece kids hoodie set — (1) pullover hoodie with kangaroo front pocket, drawstring hood, ribbed cuffs and hem, **angular geometric color-block construction** (red hood + diagonal black-and-white upper-body panels + red lower body), and (2) matching sweatpants in solid black with drawstring waist. NOT a zip-up jacket. NOT a single-piece garment. NOT an adult-sized SKU. Mid-weight cotton-fleece fabric. **Two-piece sold together as one SKU.**",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "kids-001",
    "name": "Kids Colorblock Hoodie Set — Red/Black",
    "collection": "kids-capsule",
    "slug": "kids-colorblock-hoodie-set-red-black",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Mid-weight cotton-fleece fabric.\nFeatures: Two-piece kids hoodie set — (1) pullover hoodie with kangaroo front pocket, drawstring hood, ribbed cuffs and hem, **angular geometric color-block construction** (red hood + diagonal black-and-white upper-body panels + red lower body), and (2) matching sweatpants in solid black with drawstring waist. NOT a zip-up jacket. NOT a single-piece garment. NOT an adult-sized SKU. Mid-weight cotton-fleece fabric. **Two-piece sold together as one SKU.**\nColor: Red/Black/White\nAvailable sizes: 2T | 3T | 4T | 5 | 6 | 7",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Product techflat:              `assets/products/references/kids-001-techflat.jpeg`\n> - Real product photo:            `assets/products/references/kids-001-real-photo.jpeg`\n\n### Hoodie — Front\n- **front-body color-block** (entire front body): Angular geometric color-block construction — the body is divided into three colorway panels by diagonal seams. **Upper-left panel** (from top-left descending diagonally toward center): solid **black**. **Upper-right panel** (from top-right descending diagonally toward center): solid **white**. **Lower body** (from the diagonal meeting points down to the hem, including the kangaroo pocket area): solid **red**. The diagonals create an angular chevron pointing down toward the kangaroo pocket. **Technique:** stitched. **Color:** black + white + red.\n- **front-chest cluster** (ONLY mark on the hoodie front body; small, ~2in tall, on the CHEST — see the real product photo for exact position): The Black Rose three-rose-cluster, rendered in greyscale (NOT canonical multi-color). **Technique:** embroidered. **Color:** white + black + grey thread. NOTE: there is NO patch on the chest and NO logo on the stomach / lower body (above the kangaroo pocket) — the front body carries this single chest cluster and nothing else.\n\n### Hoodie — Back\n- **back-body color-block**: Mirrors the front color-block construction — the back has the same angular black/white upper panels and red lower body, with the diagonals continuing from the front around to the back. **Technique:** stitched. **Color:** black + white + red.\n\n### Hoodie — Sleeves / Hood / Hem / Other\n- **left-sleeve**: Solid **black** to match the front-upper-left panel. **Technique:** stitched. **Color:** black.\n- **right-sleeve**: Solid **white** to match the front-upper-right panel. **Technique:** stitched. **Color:** white.\n- **sleeve patch** (ONE only, ~2in diameter, on the upper sleeve / shoulder — see the real product photo for which sleeve): A small circular rose-cluster patch — Black Rose three-rose-cluster art rendered in greyscale on a circular patch backing with a contrast border ring. **Technique:** embroidered-patch. Only ONE sleeve carries a patch; the other sleeve is plain.\n- **hood**: Solid **red** (full hood, matching the red lower body). **Technique:** stitched. **Color:** red.\n- **hood-drawstring**: White flat drawstring threaded through the hood. **Technique:** stitched. **Color:** white.\n- **kangaroo-pocket**: Red front kangaroo pocket integrated into the lower-body red panel. No decoration on the pocket fabric.\n- **left-cuff / right-cuff**: Ribbed-knit cuffs at the wrists, color-matching their respective sleeve. **Technique:** stitched. **Color:** body-tone.\n- **hem / waistband**: Ribbed-knit waistband at the bottom, red to match the lower-body panel. **Technique:** stitched. **Color:** red.\n- **collar-inside / size-tag** (~1.25in × 0.5in): Branded woven size tag (universal SkyyRose product rule, scaled for kids). **Technique:** woven-label.\n\n### Sweatpants — Front\n- **pants-body**: Solid **black** sweatpants. **Technique:** stitched. **Color:** black.\n- **pants cluster** (ONE only, small, ~2in tall, on the pants — see the real product photo for exact position): A small Black Rose three-rose-cluster (greyscale). **Technique:** embroidered. **Color:** white + black + grey thread on black. Only ONE cluster on the pants.\n\n### Sweatpants — Other\n- **waistband-drawstring**: White flat drawstring at the waistband. **Technique:** stitched. **Color:** white.\n- **left-pocket / right-pocket**: Slash-style hand pockets at both sides. **Technique:** stitched.\n- **pants-cuffs**: Ribbed-knit ankle cuffs (or straight-leg open hem). **Technique:** stitched. **Color:** black.\n- **pants-inside / waistband-tag**: Branded woven size tag. **Technique:** woven-label.",
    "negative_block": "- NO zip-up front (the hoodie is a pullover with a kangaroo pocket).\n- NO solid red body — the body is angular color-block with black/white upper panels and a red lower body, NOT a solid red field.\n- NO horizontal stripe blocking — the color-block panels are DIAGONAL, creating angular chevrons.\n- NO matching sleeves — the LEFT sleeve is black, the RIGHT sleeve is white (mirror continuation from the body panels).\n- NO colored drawstrings — drawstrings are WHITE on the hoodie + WHITE on the pants.\n- NO decoration on the back-body — the back is a clean color-block panel with no logo placement.\n- NO logos on the kangaroo pocket fabric — the pocket is clean red.\n- NO Love Hurts logo on this product — this is a Black Rose / Kids Capsule product, NOT Love Hurts.\n- THE ONLY MARKS ON THIS SET: (1) ONE rose-cluster on the hoodie CHEST, (2) ONE round patch on ONE sleeve, (3) ONE rose-cluster on the pants. Nothing else.\n- NO multi-color (canonical) rose-cluster — the rose-cluster is greyscale.\n- NO patch on the CHEST — the chest carries ONLY the rose-cluster. NO MLB/NFL/NBA/Hockey \"Authentic Collection\" batter patch on the chest or body. (The single round SLEEVE patch is the only patch; render its art per the real product photo.)\n- NO logo on the stomach / lower body above the kangaroo pocket. NO second sleeve patch (one sleeve only; the other is plain). NO second pants cluster.\n- NO chest text or wordmark on the front body fabric — only the single chest rose-cluster.\n- NO pinstripes anywhere.\n- NO embossed/debossed decoration.\n- NO color-block on the sweatpants — the pants are SOLID BLACK (color-block construction is on the HOODIE only).\n- NO white or red pants for this colorway — pants are black.",
    "scene_pose": "Front view straight-on showing the kids hoodie color-block + the single chest rose-cluster + the single sleeve patch, with the matching black sweatpants (one rose-cluster) laid below the hoodie. Three-quarter view catches the diagonal panel seam-lines.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/kids-001-techflat.jpeg",
    "extra_references": [
      "assets/products/references/kids-001-real-photo.jpeg"
    ]
  },
  "images": {
    "front": {
      "path": "assets/images/products/kids-001-onmodel-v2.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/kids-red-set-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/kids-001-red-set.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/kids-capsule/kids-red-hoodie-front.jpeg",
    "back": "assets/products/techflats/split/kids-capsule/kids-red-hoodie-back.jpeg",
    "reference": "assets/products/references/kids-001-real-photo.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_chest",
        "technique": "embroidered",
        "colorway": "black"
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_thigh",
        "technique": "embroidered",
        "colorway": "black"
      },
      {
        "logo_id": "skyy-rose-collection-circular-patch",
        "position": "right_arm",
        "technique": "circular_patch"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Bold red and black V-chevron colorblock hoodie and jogger set. Designed for young ones who wear luxury from the start.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Bold red and black V-chevron colorblock hoodie and jogger set. Designed for young ones who wear luxury from the start.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [
    {
      "text": "[ghost-back] not rendered to look 3d extra logos were added",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] not rendered to look 3d extra logos were added",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.889276+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## kids-002 — Kids Colorblock Hoodie Set — Purple/Black

```json
{
  "sku": "kids-002",
  "name": "Kids Colorblock Hoodie Set — Purple/Black",
  "collection": "kids-capsule",
  "catalog": {
    "sku": "kids-002",
    "name": "Kids Colorblock Hoodie Set — Purple/Black",
    "price": "65",
    "collection": "kids-capsule",
    "description": "Rich purple and black V-chevron colorblock hoodie and jogger set. Little ones deserve luxury too.",
    "badge": "",
    "image": "assets/images/products/kids-002-purple-set.jpeg",
    "front_model_image": "assets/images/products/kids-purple-set/kids-purple-set-approved-front-model.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/kids-purple-set/kids-purple-set-back-model.webp",
    "sizes": "2T|3T|4T|5|6|7",
    "color": "Lavender/Purple",
    "edition_size": "150",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Black rose embroidered logo on the left chest and the left thigh. Right arm features a circular patch logo: white background, black lettering, black rose in center. Patch text: 'Skyy Rose' arched on top, 'Collection' arched on bottom.",
    "render_output_slug": "kids-purple-set",
    "render_source_override": "kids-002-purple-set.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "hoodie",
    "dossier_slug": "kids-colorblock-hoodie-set-purple-black",
    "engine_override": ""
  },
  "garment": {
    "color": "Lavender/Purple",
    "available_sizes": [
      "2T",
      "3T",
      "4T",
      "5",
      "6",
      "7"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Mid-weight cotton-fleece fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Two-piece kids hoodie set — (1) pullover hoodie with kangaroo front pocket, drawstring hood, ribbed cuffs and hem, **angular geometric color-block construction** (lavender/light-pink hood + diagonal lavender-and-medium-purple upper-body panels + deep purple lower body), and (2) matching sweatpants in solid deep purple with drawstring waist. NOT a zip-up jacket. NOT a single-piece garment. NOT an adult-sized SKU. Mid-weight cotton-fleece fabric. **Two-piece sold together as one SKU.** Same construction as the Red/Black colorway (kids-001) but in a purple-monochrome palette.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "kids-002",
    "name": "Kids Colorblock Hoodie Set — Purple/Black",
    "collection": "kids-capsule",
    "slug": "kids-colorblock-hoodie-set-purple-black",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Mid-weight cotton-fleece fabric.\nFeatures: Two-piece kids hoodie set — (1) pullover hoodie with kangaroo front pocket, drawstring hood, ribbed cuffs and hem, **angular geometric color-block construction** (lavender/light-pink hood + diagonal lavender-and-medium-purple upper-body panels + deep purple lower body), and (2) matching sweatpants in solid deep purple with drawstring waist. NOT a zip-up jacket. NOT a single-piece garment. NOT an adult-sized SKU. Mid-weight cotton-fleece fabric. **Two-piece sold together as one SKU.** Same construction as the Red/Black colorway (kids-001) but in a purple-monochrome palette.\nColor: Lavender/Purple\nAvailable sizes: 2T | 3T | 4T | 5 | 6 | 7",
    "branding_block": "> Logo art canonical references:\n> - Black Rose three-rose-cluster: `data/brand-logos/three-rose-cluster.md`\n> - Product techflat:              `assets/products/references/kids-002-techflat.jpeg`\n> - Real product photo:            `assets/products/references/kids-002-real-photo.jpeg`\n\n### Hoodie — Front\n- **front-body color-block** (entire front body): Angular geometric color-block construction with diagonal seams. **Upper-left panel** (descending from top-left toward center): **lavender / light pink-purple**. **Upper-right panel** (descending from top-right toward center): **medium purple**. **Lower body** (from the diagonal meeting points down to the hem, including the kangaroo pocket area): **deep / dark purple**. **Technique:** stitched. **Color:** lavender + medium purple + deep purple.\n- **front-chest cluster** (ONLY mark on the hoodie front body; small, ~2in tall, on the CHEST — see the real product photo for exact position): The Black Rose three-rose-cluster, rendered in greyscale (NOT canonical multi-color). **Technique:** embroidered. **Color:** white + black + grey thread. NOTE: there is NO patch on the chest and NO logo on the stomach / lower body (above the kangaroo pocket) — the front body carries this single chest cluster and nothing else.\n\n### Hoodie — Back\n- **back-body color-block**: Mirrors the front — the back has the same angular lavender/medium-purple upper panels and deep-purple lower body. **Technique:** stitched. **Color:** lavender + medium purple + deep purple.\n\n### Hoodie — Sleeves / Hood / Hem / Other\n- **left-sleeve**: Solid **lavender / light pink-purple** to match the front-upper-left panel. **Technique:** stitched. **Color:** lavender.\n- **right-sleeve**: Solid **medium purple** to match the front-upper-right panel. **Technique:** stitched. **Color:** medium purple.\n- **sleeve patch** (ONE only, ~2in diameter, on the upper sleeve / shoulder — see the real product photo for which sleeve and its exact artwork): A small round embroidered patch. **Technique:** embroidered-patch. Only ONE sleeve carries a patch; the other sleeve is plain.\n- **hood**: Solid **lavender / light pink-purple** (matching the upper-left panel). **Technique:** stitched. **Color:** lavender.\n- **hood-drawstring**: White flat drawstring threaded through the hood. **Technique:** stitched. **Color:** white.\n- **kangaroo-pocket**: Deep purple front kangaroo pocket integrated into the lower-body panel.\n- **left-cuff / right-cuff**: Ribbed-knit cuffs, color-matching their sleeves. **Technique:** stitched.\n- **hem / waistband**: Ribbed-knit waistband, deep purple to match the lower-body panel. **Technique:** stitched. **Color:** deep purple.\n- **collar-inside / size-tag** (~1.25in × 0.5in): Branded woven size tag. **Technique:** woven-label.\n\n### Sweatpants — Front\n- **pants-body**: Solid **deep / dark purple** sweatpants (NOT black — see catalog-name note above). **Technique:** stitched. **Color:** deep purple.\n- **pants cluster** (ONE only, small, ~2in tall, on the pants — see the real product photo for exact position): A small Black Rose three-rose-cluster (greyscale). **Technique:** embroidered. **Color:** white + black + grey thread on deep purple. Only ONE cluster on the pants.\n\n### Sweatpants — Other\n- **waistband-drawstring**: White flat drawstring. **Technique:** stitched. **Color:** white.\n- **left-pocket / right-pocket**: Slash-style hand pockets. **Technique:** stitched.\n- **pants-cuffs**: Ribbed-knit ankle cuffs (or straight-leg open hem). **Technique:** stitched. **Color:** deep purple.\n- **pants-inside / waistband-tag**: Branded woven size tag. **Technique:** woven-label.",
    "negative_block": "- NO BLACK pants — pants are DEEP PURPLE despite the catalog name \"Purple/Black\" (the techflat and real photo both confirm purple, not black).\n- NO red anywhere on this colorway — this is the all-purple sister set to kids-001 (Red/Black). NO red roses, NO red body panel, NO red kangaroo pocket.\n- NO solid-color hoodie body — body is angular color-block, NOT a solid lavender or solid purple field.\n- NO horizontal stripe blocking — color-block panels are DIAGONAL.\n- NO matching sleeves — LEFT sleeve is lavender (light), RIGHT sleeve is medium purple.\n- NO colored drawstrings — drawstrings are WHITE on hoodie + WHITE on pants.\n- NO decoration on the back-body — back is a clean color-block panel.\n- NO logos on the kangaroo pocket fabric.\n- NO Love Hurts logo on this product.\n- THE ONLY MARKS ON THIS SET: (1) ONE rose-cluster on the hoodie CHEST, (2) ONE round patch on ONE sleeve, (3) ONE rose-cluster on the pants. Nothing else.\n- NO multi-color (canonical) rose-cluster — greyscale only.\n- NO patch on the CHEST — the chest carries ONLY the rose-cluster. NO MLB/NFL/NBA/Hockey \"Authentic Collection\" batter patch on the chest or body. (The single round SLEEVE patch is the only patch; render its art per the real product photo.)\n- NO logo on the stomach / lower body above the kangaroo pocket. NO second sleeve patch (one sleeve only; the other is plain). NO second pants cluster.\n- NO chest text or wordmark on the front body fabric — only the single chest rose-cluster.\n- NO pinstripes.\n- NO embossed/debossed decoration.\n- NO color-block on the sweatpants — pants are SOLID deep purple.",
    "scene_pose": "Front view straight-on showing the lavender/purple color-block hoodie + the single chest rose-cluster + the single sleeve patch, with the matching deep-purple sweatpants (one rose-cluster) laid below the hoodie.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/kids-002-techflat.jpeg",
    "extra_references": [
      "assets/products/references/kids-002-real-photo.jpeg"
    ]
  },
  "images": {
    "front": {
      "path": "assets/images/products/kids-purple-set/kids-purple-set-approved-front-model.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/kids-purple-set/kids-purple-set-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/kids-002-purple-set.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/kids-capsule/kids-purple-hoodie-front.jpeg",
    "back": "assets/products/techflats/split/kids-capsule/kids-purple-hoodie-back.jpeg",
    "reference": "assets/products/references/kids-002-real-photo.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_chest",
        "technique": "embroidered",
        "colorway": "black"
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_thigh",
        "technique": "embroidered",
        "colorway": "black"
      },
      {
        "logo_id": "skyy-rose-collection-circular-patch",
        "position": "right_arm",
        "technique": "circular_patch",
        "notes": "Same placement pattern as kids-001."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Rich purple and black V-chevron colorblock hoodie and jogger set. Little ones deserve luxury too.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Rich purple and black V-chevron colorblock hoodie and jogger set. Little ones deserve luxury too.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [
    {
      "text": "[ghost-back] not rendered to look 3d extra logos were added",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] not rendered to look 3d extra logos were added",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.900488+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## lh-002 — Love Hurts Joggers (Black)

```json
{
  "sku": "lh-002",
  "name": "Love Hurts Joggers (Black)",
  "collection": "love-hurts",
  "catalog": {
    "sku": "lh-002",
    "name": "Love Hurts Joggers (Black)",
    "price": "95",
    "collection": "love-hurts",
    "description": "Oakland grit meets luxury. Solid black body with white contrast side-panels running vertically from waist to ankle. White flat drawstring. The Love Hurts heart-rose-composite embroidered on the left thigh — the heart-and-thorns lockup with roses emerging from the top, rendered in red, green, and crimson on the black fabric. Mid-weight cotton-fleece, athletic-fit through the leg, ribbed ankle cuffs. Mirror white colorway available as lh-006.",
    "badge": "",
    "image": "assets/images/products/lh-002-joggers.jpeg",
    "front_model_image": "assets/images/products/lh-002-onmodel.webp",
    "back_image": "assets/images/products/love-hurts-joggers-back-model.webp",
    "back_model_image": "assets/images/products/love-hurts-joggers-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Heart-rose-composite (Love Hurts heart-and-thorns lockup) embroidered on the left thigh. White contrast side-panel running vertically on both side seams. White drawstring.",
    "render_output_slug": "love-hurts-joggers",
    "render_source_override": "lh-002-joggers.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "joggers",
    "dossier_slug": "love-hurts-joggers",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs).",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Mid-weight cotton-fleece fabric. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs). Mid-weight cotton-fleece fabric. **BLACK body** with **WHITE contrast side-panel running vertically down each side leg** (waistband to ankle on both left and right side seams). White flat drawstring. NOT pants. NOT shorts. NOT a track short. NOT a basketball jogger. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique. The white-base mirror colorway is a separate SKU (`lh-006`).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "lh-002",
    "name": "Love Hurts Joggers (Black)",
    "collection": "love-hurts",
    "slug": "love-hurts-joggers",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Mid-weight cotton-fleece fabric. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique.\nFit: Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs).\nFeatures: Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs). Mid-weight cotton-fleece fabric. **BLACK body** with **WHITE contrast side-panel running vertically down each side leg** (waistband to ankle on both left and right side seams). White flat drawstring. NOT pants. NOT shorts. NOT a track short. NOT a basketball jogger. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique. The white-base mirror colorway is a separate SKU (`lh-006`).\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Heart-rose composite (Love Hurts heart-and-thorns lockup): `data/brand-logos/heart-rose-composite.md`\n> - Love Hurts wordmark (NOT on this product, listed for canonical reference): `data/brand-logos/love-hurts-logo.md`\n> - Product techflat: `assets/products/references/lh-002-techflat-front.jpeg`\n\n### Front\n- **front-body** (entire front body — solid black field): Solid black, cotton-fleece. **Technique:** stitched. **Color:** black.\n- **front-left-pocket** (vertical slash pocket at the left side of the upper hip): Slash-style hand pocket at the front left side, with vertical welt opening. **Technique:** stitched (sewn-on welt edges). **Color:** body-matching black.\n- **front-right-pocket** (vertical slash pocket at the right side of the upper hip): Slash-style hand pocket at the front right side, with vertical welt opening. **Technique:** stitched (sewn-on welt edges). **Color:** body-matching black.\n- **left-thigh** (centered on the wearer's left thigh, just below the hip): **Heart-rose-composite logo** — the Love Hurts heart-and-thorns lockup with roses emerging from the top, rendered embroidered on the black body fabric. **Technique:** embroidered. **Color:** red roses + green thorns + crimson heart, on black body.\n\n### Back\n- (No back-body decoration. The back is a clean panel with no embroidered logo or graphic — the contrast side-panel wraps cleanly from front to back through the side seam.)\n\n### Sleeves / Collar / Hem / Other\n- **left-side-panel** (vertical contrast strip running from waistband to ankle on the left side seam): A WHITE contrast-fabric panel inserted along the left side seam. The panel is approximately 1.5in–2in wide and runs continuously from the waistband down to the ankle hem. **Technique:** stitched (contrast fabric panel sewn into the side seam). **Color:** white.\n- **right-side-panel** (vertical contrast strip running from waistband to ankle on the right side seam): A WHITE contrast-fabric panel inserted along the right side seam. The panel is approximately 1.5in–2in wide and runs continuously from the waistband down to the ankle hem. **Technique:** stitched. **Color:** white.\n- **waistband**: Black elasticated waistband with **white flat drawstring**. **Technique:** stitched. **Color:** black waistband + white drawstring.\n- **drawstring**: White flat drawstring. **Technique:** stitched. **Color:** white.\n- **left-ankle-cuff** (ribbed-knit band at the left ankle hem): Ribbed-knit cuff at the left ankle in black (some variants may use a banded-elastic cuff instead of rib-knit). **Technique:** stitched. **Color:** black.\n- **right-ankle-cuff** (ribbed-knit band at the right ankle hem): Ribbed-knit cuff at the right ankle in black (some variants may use a banded-elastic cuff instead of rib-knit). **Technique:** stitched. **Color:** black.\n- **inside-waistband** (~1.25in × 0.5in, sewn into the inside front waistband): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** white label, black lettering.",
    "negative_block": "- NO Love Hurts wordmark across the leg or thigh — the only Love-Hurts-coded mark on this product is the heart-rose-composite on the left thigh.\n- NO red roses cloud cluster on the joggers — that motif is on lh-003 (basketball shorts) and lh-004 (bomber inside-hood), NOT here.\n- NO sublimated all-over rose pattern on the body — the black body is SOLID black fabric (not sublimated).\n- NO mirror colorway in this SKU — the white-base / black-panel mirror is a separate SKU (`lh-006 Love Hurts Joggers (White)`).\n- NO contrast piping at the waistband or cuffs — only the side-seam panel is contrast.\n- NO black drawstring — the drawstring is WHITE.\n- NO horizontal stripe blocking — the contrast panel runs VERTICALLY along the side seam, top to bottom.\n- NO decoration on the right thigh — the heart-rose-composite sits on the LEFT thigh only.\n- NO embossed/debossed decoration anywhere.\n- NO printed all-over graphic on the body — body is solid black.\n- NO Black Rose three-rose-cluster on this product — this is a Love Hurts collection product. Black Rose marks (gothic greyscale) do NOT appear here.\n- NO contrast satin-stitch on any decoration.\n- NO zipper closures on the pockets — slash pockets are open-welt, not zippered.\n- NO patch applications on the joggers — branding is embroidered, not patch-sewn.\n- NO ankle taper that hits above the cuff — joggers terminate cleanly at the ribbed/banded cuff at ankle level.",
    "scene_pose": "Front view straight-on (laid flat or on a model) showing the black body + the vertical white contrast side-panel + the heart-rose-composite on the left thigh + the white drawstring. For the back: clean back panel showing the contrast side-panel continuing.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/love-hurts-logo.md",
    "extra_logos": [
      "data/brand-logos/heart-rose-composite.md"
    ],
    "reference_image": "assets/products/references/lh-002-techflat-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/lh-002-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/love-hurts-joggers-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/lh-002-joggers.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/love-hurts-joggers-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/techflats/split/love-hurts/lh-joggers-front.jpeg",
    "back": null,
    "reference": "assets/products/references/lh-002-techflat-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "heart-rose-composite",
        "position": "left_thigh",
        "technique": "embroidered"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/heart-rose-composite.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "More than just joggers, they're a testament to the fire in your heart, forged in the concrete of Oakland. Feel the pulse of the streets with the SkyyRose Love Hurts Joggers—where raw emotion meets undeniable luxury. These joggers are for those who wear their scars like badges of honor, who understand that true beauty is born from pain. The deep black fabric is slashed with crisp white stripes, mirroring the stark contrasts of the city, leading down to zippered ankles ready to grind, ready to move. But the heart of these joggers lies in the embroidered rose, a symbol of passion and resilience, its thorns a reminder that love leaves its mark. Wear them as a declaration: you're not afraid to feel, to bleed, to rise. SkyyRose: Luxury born from the streets, where every thread tells a story of love, loss, and the unyielding spirit of Oakland. Own your story.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "SkyyRose Love Hurts Joggers: Where Oakland grit meets luxury. Feel the fire with the embroidered rose, a symbol of passion forged in the streets.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Love Hurts Joggers: Oakland-forged luxury streetwear. Embroidered rose, raw passion. Own the streets.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "From the heart of Oakland, where passion ignites the streets. 🔥 The SkyyRose Love Hurts Joggers embody the grit and grace of the Bay. Feel the fire in every thread, the resilience in the embroidered rose. Wear your story. This is Oakland luxury.\n\n#SkyyRose #LoveHurts #OaklandFashion #BayAreaStyle #StreetwearFashion #GritAndGrace #RealStyle #UrbanLuxury #Authentic #BayArea #OaklandProud #RoseAndThorns",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Oakland fire 🔥 Love Hurts Joggers: where passion meets the pavement. Show your soul. #SkyyRose #LoveHurts #Oakland",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "lh-002-product": "SkyyRose Love Hurts Joggers: Black with white side stripes, red rose and barbed wire embroidery, and zippered ankles."
  },
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.919087+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## lh-003 — Love Hurts Basketball Shorts

```json
{
  "sku": "lh-003",
  "name": "Love Hurts Basketball Shorts",
  "collection": "love-hurts",
  "catalog": {
    "sku": "lh-003",
    "name": "Love Hurts Basketball Shorts",
    "price": "75",
    "collection": "love-hurts",
    "description": "Oakland-inspired luxury streetwear. Defiant rose design on breathable mesh.",
    "badge": "",
    "image": "assets/images/products/lh-003-shorts.jpeg",
    "front_model_image": "assets/images/products/ghost/lh-003-ghost-front.webp",
    "back_image": "assets/images/products/lh-003-real-back.jpg",
    "back_model_image": "assets/images/products/love-hurts-basketball-shorts-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Sublimated rose logo throughout the shorts. Big sublimated 'Love Hurts' logo on the left side. Additional 'Love Hurts' and rose logos stitched on the mesh sides of the shorts.",
    "render_output_slug": "love-hurts-basketball-shorts",
    "render_source_override": "lh-003-shorts.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shorts",
    "dossier_slug": "love-hurts-basketball-shorts",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Knee-length athletic basketball shorts — **white mesh\nbody fabric** with **all-over sublimated red-roses-cluster pattern** repeating\nacross the entire body, **black ribbed elasticated waistband** with **white flat\ndrawstring**, **exactly four zippered pockets** (**two side hand pockets + two\nrear pockets**), **black ribbed-binding hem with red contrast piping** along the\nleg openings.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Knee-length athletic basketball shorts — **white mesh\nbody fabric** with **all-over sublimated red-roses-cluster pattern** repeating\nacross the entire body, **black ribbed elasticated waistband** with **white flat\ndrawstring**, **exactly four zippered pockets** (**two side hand pockets + two\nrear pockets**), **black ribbed-binding hem with red contrast piping** along the\nleg openings. Every pocket has a zipper closure. Knee-length cut. NOT pants. NOT\njoggers. NOT short-shorts. NOT a swim trunk. NOT a track short.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "lh-003",
    "name": "Love Hurts Basketball Shorts",
    "collection": "love-hurts",
    "slug": "love-hurts-basketball-shorts",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Knee-length athletic basketball shorts — **white mesh\nbody fabric** with **all-over sublimated red-roses-cluster pattern** repeating\nacross the entire body, **black ribbed elasticated waistband** with **white flat\ndrawstring**, **exactly four zippered pockets** (**two side hand pockets + two\nrear pockets**), **black ribbed-binding hem with red contrast piping** along the\nleg openings.\nFeatures: Knee-length athletic basketball shorts — **white mesh\nbody fabric** with **all-over sublimated red-roses-cluster pattern** repeating\nacross the entire body, **black ribbed elasticated waistband** with **white flat\ndrawstring**, **exactly four zippered pockets** (**two side hand pockets + two\nrear pockets**), **black ribbed-binding hem with red contrast piping** along the\nleg openings. Every pocket has a zipper closure. Knee-length cut. NOT pants. NOT\njoggers. NOT short-shorts. NOT a swim trunk. NOT a track short.\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n>\n> - Love Hurts logo (wordmark + heart-and-thorns):\n>   `data/brand-logos/love-hurts-logo.md`\n> - Red Roses Cloud Cluster (the LH variant of the rose-cluster — red roses +\n>   green stems + white-and-blue cloud):\n>   `data/brand-logos/red-roses-cloud-cluster.md`\n> - Physical front:\n>   `assets/products/source-photos/love-hurts/lh-003-shorts-front.jpeg`\n> - Physical back:\n>   `assets/products/source-photos/love-hurts/lh-003-shorts-back.jpeg`\n> - Physical wearer-left side:\n>   `assets/products/source-photos/love-hurts/lh-003-shorts-wearer-left.jpg`\n> - Physical wearer-right side:\n>   `assets/products/source-photos/love-hurts/lh-003-shorts-wearer-right.jpg`\n> - Product techflat fallback:\n>   `assets/products/references/lh-003-techflat-front.jpeg`\n\n### Front\n\n- **front-body** (entire white mesh field, front and back continuous): The\n  canonical Red Roses Cloud Cluster art (three red roses + thorny green vines +\n  white-and-blue cloud at base) sublimated as a small repeating pattern across\n  the entire white mesh body, scattered evenly with the cloud pointing down.\n  Each rose-cluster is rendered in canonical full color (saturated red roses,\n  kelly-green stems, white-and-blue cloud) on the white ground. **Technique:**\n  sublimated. **Color:** canonical multi-color red green white blue on white\n  mesh.\n- **wearer-left front/side body** (large, diagonal): The \"Love Hurts\" wordmark\n  in red cursive script spans the white mesh toward the left side seam. The\n  adjacent black mesh inset carries a smaller red Love Hurts emblem with\n  rose/heart artwork. **Technique:** large treatment sublimated; small inset\n  mark embroidered. **Color:** canonical Love Hurts red with black artwork and\n  green/red rose detail.\n- **wearer-right side inset** (black mesh panel): A red rose bouquet with green\n  stems above a white-and-blue cloud is embroidered on the black mesh inset.\n  **Technique:** embroidered. **Color:** red, green, white, and blue on black\n  mesh.\n\n### Back\n\n- **back-body** (white mesh field, continues from front): Same all-over Red\n  Roses Cloud Cluster pattern as the front, continuing across the rear.\n  **Technique:** sublimated. **Color:** canonical multi-color on white mesh.\n- **back-wearer-left** (large upper-side treatment): A large red-and-black\n  broken-heart/paint treatment with descending red Love Hurts script crosses the\n  upper wearer-left rear and continues toward the left side seam. Preserve its\n  scale, direction, and relationship to the repeating rose field. **Technique:**\n  sublimated. **Color:** canonical red and black.\n- **rear pockets** (exactly two, below waistband): Two\n  horizontal-to-slightly-angled zippered rear pockets finished with black\n  perforated trim and black zipper closures. Both rear pockets contain zippers.\n  **Technique:** stitched zipper pocket. **Color:** black.\n\n### Sleeves / Collar / Hem / Other\n\n- **waistband** (~1.5in tall, top of shorts): Black ribbed-knit elasticated\n  waistband. **Technique:** stitched. **Color:** black.\n- **drawstring** (waistband-thread, ~24in long): White flat drawstring threaded\n  through the waistband. **Technique:** stitched. **Color:** white.\n- **left-pocket** (upper wearer-left side): Angled zippered hand pocket\n  immediately below the waistband, finished with black perforated trim and a\n  black zipper closure. **Technique:** stitched zipper pocket. **Color:** black.\n- **right-pocket** (upper wearer-right side): Angled zippered hand pocket\n  immediately below the waistband, finished with black perforated trim and a\n  black zipper closure. **Technique:** stitched zipper pocket. **Color:** black.\n- **leg-binding** (each leg opening, ~1in wide): Black perforated binding with\n  parallel red and white contrast stripes tracing the angular basketball-short\n  hem. **Technique:** stitched. **Color:** black, red, and white.\n- **inside-waistband** (~1.5in × 0.5in, interior tag): Branded woven size tag.\n  **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO solid-color body — the entire body has the sublimated all-over rose-cluster\n  pattern, NOT a plain white mesh field.\n- NO greyscale rendering of the rose-cluster — this is the LOVE HURTS variant in\n  **canonical full color** (red roses + green stems + white-and-blue cloud), NOT\n  the Black Rose greyscale variant.\n- NO Black Rose three-rose-cluster on this product — this is a Love Hurts\n  product, the cluster is the **red-roses** variant only.\n- NO black mesh body — body is WHITE mesh (distinct from br-007 BR×LH shorts\n  which has black mesh).\n- NO contrast color side-panels — body is uniform white mesh with the sublimated\n  pattern; no white-mesh-vs-black-mesh side panel distinction (that's br-007).\n- NO OAKLAND tackle-twill wordmark — that's br-007. This product has only the\n  Love Hurts cursive wordmark.\n- NO COLORWAY OVERRIDE — colors render in canonical Love Hurts palette, NOT\n  remapped to greyscale or tonal.\n- NO black drawstring — drawstring is WHITE.\n- NO white waistband — waistband is BLACK ribbed.\n- NO open, zipperless, patch, or cargo pockets — the product has exactly four\n  pockets, and all four have zipper closures: two side pockets and two rear\n  pockets.\n- NO plain back — the physical back includes two black zippered rear pockets and\n  the large red-and-black wearer-left Love Hurts treatment.\n- NO sublimated pattern in greyscale — the all-over rose pattern is canonical\n  multi-color.\n- NO mirrored side branding — the large red Love Hurts treatment belongs on\n  wearer-left; the rose-bouquet/cloud inset belongs on wearer-right.\n- NO embossed/debossed decoration anywhere.\n- NO sleeve elements (this is a shorts garment, lower-body only).\n- NO numbers anywhere — no jersey numerals.\n- NO Authentic Collection patch — that patch is reserved for the Black Rose\n  jersey series.",
    "scene_pose": "Front view straight-on (laid flat or on an approved model) showing\n  the all-over rose pattern, wearer-left red Love Hurts treatment, wearer-right\n  rose-bouquet/cloud inset, black waistband, both zippered side pockets when the\n  angle exposes them, and black/red/white angular leg binding. For the back:\n  show the continuous rose pattern, both black zippered rear pockets, and the\n  large wearer-left red-and-black rear treatment. Across all views, preserve\n  exactly two side pockets and two rear pockets, with a zipper closure on every\n  pocket. Use the matching directional side source whenever a side panel is\n  visible; never mirror it.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from\n  front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/love-hurts-logo.md",
    "extra_logos": [
      "data/brand-logos/red-roses-cloud-cluster.md"
    ],
    "reference_image": "assets/products/source-photos/love-hurts/lh-003-shorts-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/hub/lh-003-front.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/love-hurts-basketball-shorts-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/lh-003-shorts.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/lh-003-real-back.jpg",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/lh-003-real-front.jpg",
    "back": "wordpress-theme/skyyrose-flagship/assets/images/products/lh-003-real-back.jpg",
    "reference": "assets/products/references/lh-003-techflat-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "red-roses-cloud-cluster",
        "position": "all_over",
        "technique": "sublimated",
        "notes": "Re-corrected 2026-05-27 per founder: red-roses-cloud-cluster IS used on Love Hurts (the 2026-05-25 misclassification correction was itself wrong). Heart-rose-composite is reserved for lh-004 back-center, lh-005 Fannie (i-dot), and the LH joggers left thigh only."
      },
      {
        "logo_id": "love-hurts-full-lettering",
        "position": "left_side",
        "technique": "sublimated",
        "size_inches": 12
      },
      {
        "logo_id": "red-roses-cloud-cluster",
        "position": "mesh_side_panels",
        "technique": "stitched",
        "notes": "Re-corrected 2026-05-27 per founder: was incorrectly switched to heart-rose-composite on 2026-05-25."
      },
      {
        "logo_id": "love-hurts-full-lettering",
        "position": "mesh_side_panels",
        "technique": "stitched",
        "notes": "Smaller Love Hurts + heart-rose logos stitched on mesh side panels."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/red-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "SkyyRose Love Hurts Basketball Shorts are a declaration, not just a garment. Imagine twilight descending on an Oakland basketball court, the air thick with untold stories. That's the feeling woven into every fiber of these shorts. Crafted from breathable, high-performance white mesh, they move with the rhythm of the streets. Defiant orange roses bloom across the fabric, their thorny stems entwined in delicate clouds – a symbol of beauty rising from struggle. A stark black panel showcases crimson roses, framed by red and white stripes, a tribute to Oakland grit. The elastic waistband keeps you grounded. SkyyRose melds Bay Area soul with luxury, transforming emotion into wearable art. Feel the fire. Own the streets. Dare to wear your heart.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "SkyyRose Love Hurts: Where street passion meets luxury. Rock these mesh basketball shorts with a defiant rose design, born from Oakland grit.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Love Hurts Basketball Shorts: Oakland-inspired luxury streetwear. Defiant rose design on breathable mesh. Shop now for passion, pain, and undeniable style.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Straight fire from the streets of Oakland. 🔥 The SkyyRose Love Hurts Basketball Shorts are a testament to turning pain into power. With that defiant rose-on-cloud design and the deep crimson bouquet on the back, these shorts are pure flames. 🌹 Representing Bay Area luxury streetwear at its finest, we turn raw emotion into untouchable style. You feel this?\n#SkyyRose #LoveHurts #OaklandFashion #StreetwearFashion #LuxuryStreetwear #BayAreaStyle #RoseDesign #GritAndGrace #FashionKilla #StreetStyle #RealStyle #NewDrop",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Love Hurts just dropped! 💔 SkyyRose shorts: rose on cloud vibe + Oakland soul. 🔥 Flex your fire. #SkyyRose #LoveHurts #Streetwear #BayArea 🌹",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "lh-003-product-2": "White mesh Love Hurts Basketball Shorts with red \"Love Hurts\" text, a bleeding heart, orange roses, and black trim.",
    "lh-003-product-3": "Love Hurts Basketball Shorts: White mesh with orange roses on clouds, black striped sides, and red logo.",
    "lh-003-product": "Love Hurts Basketball Shorts: White with orange roses on clouds, black waistband, and red-trimmed black pentagon with a red rose."
  },
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.930788+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## lh-004 — Love Hurts Bomber Jacket

```json
{
  "sku": "lh-004",
  "name": "Love Hurts Bomber Jacket",
  "collection": "love-hurts",
  "catalog": {
    "sku": "lh-004",
    "name": "Love Hurts Bomber Jacket",
    "price": "265",
    "collection": "love-hurts",
    "description": "Oakland street couture. Satin bomber with bold fire-red script and a hidden rose garden in the hood.",
    "badge": "",
    "image": "assets/images/products/lh-004-bomber.png",
    "front_model_image": "assets/images/products/lh-004-onmodel.webp",
    "back_image": "assets/images/products/lh-004-bomber-back.png",
    "back_model_image": "assets/images/products/lh-004-bomber-back.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White/Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "'Love Hurts' logo lettering across the front. Inside of the hood features a sublimated rose logo. BACK: large 'Heart and Rose' Love Hurts logo centered.",
    "render_output_slug": "love-hurts-bomber",
    "render_source_override": "lh-004-bomber.png",
    "render_back_source_override": "lh-004-bomber-back.png",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "bomber jacket",
    "dossier_slug": "love-hurts-bomber-jacket",
    "engine_override": ""
  },
  "garment": {
    "color": "White/Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "The hood lining shows a small white-and-red rose-silhouette mini-pattern (visible when the hood is laid open or worn down).",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Hooded varsity-bomber hybrid jacket — **white body fabric** with **black contrast raglan sleeves** (sleeves are a different color from the body, joining at a diagonal raglan seam from underarm to neck), **black hood**, **button-front placket** (snap or button-front closure running the full length of the center-front), **vertical slash hand pockets** at the lower sides with welt openings, **ribbed-knit cuffs and waistband with red+white+black striped accent banding**. Satin appearance is required by the later founder review; fiber composition is not established here. NOT a sherpa jacket.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Hooded varsity-bomber hybrid jacket — **white body fabric** with **black contrast raglan sleeves** (sleeves are a different color from the body, joining at a diagonal raglan seam from underarm to neck), **black hood**, **button-front placket** (snap or button-front closure running the full length of the center-front), **vertical slash hand pockets** at the lower sides with welt openings, **ribbed-knit cuffs and waistband with red+white+black striped accent banding**. The hood lining shows a small white-and-red rose-silhouette mini-pattern (visible when the hood is laid open or worn down). Satin appearance is required by the later founder review; fiber composition is not established here. NOT a sherpa jacket. NOT a windbreaker. NOT a hoodie (it has button-front closure, not pullover construction).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "lh-004",
    "name": "Love Hurts Bomber Jacket",
    "collection": "love-hurts",
    "slug": "love-hurts-bomber-jacket",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Hooded varsity-bomber hybrid jacket — **white body fabric** with **black contrast raglan sleeves** (sleeves are a different color from the body, joining at a diagonal raglan seam from underarm to neck), **black hood**, **button-front placket** (snap or button-front closure running the full length of the center-front), **vertical slash hand pockets** at the lower sides with welt openings, **ribbed-knit cuffs and waistband with red+white+black striped accent banding**. Satin appearance is required by the later founder review; fiber composition is not established here. NOT a sherpa jacket.\nFit: The hood lining shows a small white-and-red rose-silhouette mini-pattern (visible when the hood is laid open or worn down).\nFeatures: Hooded varsity-bomber hybrid jacket — **white body fabric** with **black contrast raglan sleeves** (sleeves are a different color from the body, joining at a diagonal raglan seam from underarm to neck), **black hood**, **button-front placket** (snap or button-front closure running the full length of the center-front), **vertical slash hand pockets** at the lower sides with welt openings, **ribbed-knit cuffs and waistband with red+white+black striped accent banding**. The hood lining shows a small white-and-red rose-silhouette mini-pattern (visible when the hood is laid open or worn down). Satin appearance is required by the later founder review; fiber composition is not established here. NOT a sherpa jacket. NOT a windbreaker. NOT a hoodie (it has button-front closure, not pullover construction).\nColor: White/Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Love Hurts logo (wordmark + heart-and-thorns): `data/brand-logos/love-hurts-logo.md`\n> - Red Roses Cloud Cluster (LH variant): `data/brand-logos/red-roses-cloud-cluster.md`\n> - Product techflat: `assets/products/references/lh-004-techflat-front.jpeg`\n\n### Front\n- **front-body** (entire white field, between the raglan sleeve seams and excluding the placket): Solid **white** fabric. **Technique:** stitched. **Color:** white.\n- **front-left-chest** (~3–4in tall, upper left chest panel — \"Love\" half of the wordmark): The **\"Love\"** portion of the canonical \"Love Hurts\" cursive script wordmark — wearer's LEFT chest, placket separates it from \"Hurts\" on the right. Hand-drawn graffiti-cursive style (see logo reference). **Technique:** embroidered. **Color:** canonical Love Hurts red.\n- **front-right-chest** (~3–4in tall, upper right chest panel — \"Hurts\" half of the wordmark): The **\"Hurts\"** portion of the canonical \"Love Hurts\" cursive script wordmark — wearer's RIGHT chest, placket separates it from \"Love\" on the left. Hand-drawn graffiti-cursive style (see logo reference). **Technique:** embroidered. **Color:** canonical Love Hurts red.\n- **front-placket** (vertical center-front closure, full length): Button or snap front placket running from the V-opening at the collar to the bottom of the ribbed waistband. **Technique:** patch (sewn-on snap/button hardware). **Color:** body-tone snaps/buttons on white.\n- **front-left-pocket** (vertical slash welt opening at the lower-left side of the body, just above the waistband): Slash hand pocket with vertical welt opening. **Technique:** stitched (welt-edge construction). **Color:** white body with subtle welt.\n- **front-right-pocket** (vertical slash welt opening at the lower-right side of the body, just above the waistband): Slash hand pocket with vertical welt opening. **Technique:** stitched (welt-edge construction). **Color:** white body with subtle welt.\n\n### Back\n- **back-body** (large, ~10–12in tall, vertically centered on the back): The **canonical Love Hurts heart-and-thorns + roses lockup** — a bright red broken-heart-and-thorns illustration with **canonical red-roses-cluster art** wrapping around / accenting it. The composition fills most of the back upper-mid area. Rendered in canonical Love Hurts multi-color (red heart with dark cracks, brown/dark thorny vines, red rose petals, kelly-green stems). **Technique:** embroidered. **Color:** canonical Love Hurts multi-color (red + green + brown + black ink outlines).\n\n### Sleeves / Hood / Hem / Other\n- **left-sleeve** (solid black raglan, diagonal seam from underarm to neck on the left): Solid **black** fabric, different color from the white body. **Technique:** stitched. **Color:** black.\n- **right-sleeve** (solid black raglan, diagonal seam from underarm to neck on the right): Solid **black** fabric, different color from the white body. **Technique:** stitched. **Color:** black.\n- **left-cuff** (ribbed-knit striped band at the left sleeve cuff, ~3–4 stripes): Ribbed-knit band with alternating white + red + black stripes. **Technique:** stitched (striped rib-knit). **Color:** alternating white + red + black.\n- **right-cuff** (ribbed-knit striped band at the right sleeve cuff, ~3–4 stripes): Ribbed-knit band with alternating white + red + black stripes. **Technique:** stitched (striped rib-knit). **Color:** alternating white + red + black.\n- **waistband** (ribbed-knit striped band at the bottom hem, ~3–4 stripes, matching the cuff accent): The bottom hem of the body has a **ribbed-knit waistband with the same white + red + black striped accent** as the cuffs. **Technique:** stitched. **Color:** alternating white + red + black.\n- **hood**: Solid **black** hood (matches the black raglan sleeves). **Technique:** stitched. **Color:** black.\n- **hood-lining** (inner hood lining, visible when hood is laid back or worn down): A **white-and-red rose-silhouette pattern** sublimated inside the hood lining — small red rose silhouettes scattered across the white inner-lining fabric. **Technique:** sublimated. **Color:** small red rose silhouettes on white inner-lining.\n- **collar-tag** (~1.75in × 0.75in, sewn at the interior back collar): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** white label, black lettering.",
    "negative_block": "- NO Black Rose three-rose-cluster on this product — this is a Love Hurts product. The back graphic is the Love Hurts heart-and-thorns + canonical red roses, NOT the Black Rose greyscale cluster.\n- NO greyscale rose rendering anywhere — all rose imagery is canonical Love Hurts multi-color (red + green + brown).\n- NO single-color body — the body is WHITE with BLACK raglan sleeves and BLACK hood (three-color contrast: white body + black sleeves + black hood).\n- NO non-raglan sleeve seam — the sleeves are RAGLAN cut (diagonal seam from underarm to neck), NOT set-in.\n- NO sherpa fabric. Preserve the satin appearance requested in the later founder review; do not infer cotton-blend or any fiber composition.\n- NO zipper-front closure — the front is BUTTON or SNAP placket, NOT a zipper.\n- NO solid-color cuffs/hem — the rib-knit cuffs and waistband have a STRIPED accent pattern (white + red + black), NOT solid black or solid white.\n- NO sublimated all-over body pattern — the body is solid white, NOT sublimated.\n- NO Love Hurts wordmark on the back — the back has the heart-and-thorns + roses graphic; the wordmark is on the front-chest only.\n- NO heart-and-thorns on the front — the front has the cursive \"Love\" + \"Hurts\" wordmark only; the heart graphic is on the back.\n- NO red drawstrings — there is no drawstring on this jacket (it's a button-front bomber, not a pullover hoodie).\n- NO white sleeves — sleeves are black.\n- NO contrast piping on the body or pockets.\n- NO Authentic Collection patch — that patch is reserved for the Black Rose jersey series.\n- NO embossed/debossed decoration anywhere.\n- NO printed graphics on the body fabric — branding is embroidered.\n- NO numbers anywhere.",
    "scene_pose": "Front view straight-on showing the white body + black raglan sleeves + black hood + cursive \"Love\" / \"Hurts\" chest wordmark + striped cuff and hem bands + button-front placket. Three-quarter view catches the raglan seam diagonal and the side wrap of the striped bands. For the back: back view straight-on showing the large heart-and-thorns + roses graphic and the matching striped hem.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/love-hurts-logo.md",
    "extra_logos": [
      "data/brand-logos/red-roses-cloud-cluster.md"
    ],
    "reference_image": "assets/products/references/lh-004-techflat-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/lh-004-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/lh-004-bomber-back.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/lh-004-bomber.png",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/lh-004-bomber-back.png",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/techflats/split/love-hurts/lh-bomber-front.jpeg",
    "back": "assets/products/techflats/split/love-hurts/lh-bomber-back.jpeg",
    "reference": "assets/products/references/lh-004-techflat-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "love-hurts-full-lettering",
        "position": "front_across",
        "technique": "embroidered_or_applique",
        "size_inches": 12,
        "notes": "User-confirmed 2026-04-20: Love Hurts graffiti lettering goes on the front."
      },
      {
        "logo_id": "red-roses-cloud-cluster",
        "position": "inside_hood",
        "technique": "sublimated",
        "notes": "Re-corrected 2026-05-27 per founder: red-roses-cloud-cluster is the correct LH inside-hood pattern. The 2026-05-25 switch to heart-rose-composite was incorrect."
      },
      {
        "logo_id": "heart-rose-composite",
        "position": "back_center",
        "technique": "embroidered_or_printed",
        "size_inches": 10,
        "notes": "User-confirmed 2026-04-20: heart-and-rose composite centered on back."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/love-hurts-full-lettering.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Oakland bleeds into every stitch of the Love Hurts Varsity Jacket. It's a testament to surviving heartbreak and turning pain into power. The iconic 'Love Hurts' script, emblazoned in fire-engine red, screams louder than any broken promise. Peek inside – a secret garden of roses blooms within the hood, a reminder that beauty can rise from the ashes. This is street couture, SkyyRose style. We've injected a dose of raw, unfiltered emotion into the classic varsity silhouette. Wear it to rep your scars, your resilience, your story. This jacket is a pre-order, built for those who know that love leaves a mark. Embrace the burn. SkyyRose: Luxury forged in the fire of the streets.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Oakland grit meets broken hearts in the Love Hurts Varsity Jacket. Black satin, fire-red script, secret rose garden. Pre-order your battle armor.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Love Hurts Varsity Jacket: Oakland street couture for the heartbroken. Satin, bold script, hidden roses. Pre-order your pain-proof statement.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Wear your heart on your sleeve, even when it's broken. The SkyyRose Love Hurts Varsity Jacket is a raw anthem of resilience, crafted from sleek black satin with a fire-red declaration. A secret rose garden blooms inside the hood, a reminder that even pain births beauty. This is Oakland street luxury, unfiltered.\n\nPre-order and wear your scars with pride. 💔\n\n#SkyyRose #LoveHurts #OaklandFashion #StreetwearFashion #BayAreaStyle #GritAndGrace #UrbanLuxury #Authentic #VarsityJacket #RoseDetails #StreetCouture",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Love Hurts? Turn pain into power. 🔥 Varsity jacket with satin vibes & rose-lined hood. Pre-order now! 💔 #SkyyRose #LoveHurts #Oakland",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "lh-004-product": "Love Hurts Varsity Jacket: black & white satin, red \"Love Hurts\" text on chest, striped cuffs & hem, floral hood."
  },
  "corrections": [
    {
      "text": "[ghost-back] doesn't look satin",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] doesn't look satin",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.942165+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## lh-005 — The Fannie

```json
{
  "sku": "lh-005",
  "name": "The Fannie",
  "collection": "love-hurts",
  "catalog": {
    "sku": "lh-005",
    "name": "The Fannie",
    "price": "45",
    "collection": "love-hurts",
    "description": "Oakland luxury meets everyday utility. The essential Love Hurts fanny pack with premium embroidery.",
    "badge": "Pre-Order",
    "image": "assets/images/products/lh-005-fannie.jpeg",
    "front_model_image": "assets/images/products/lh-005-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/the-fannie-back-model.webp",
    "sizes": "One Size",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "High-end leather fanny pack construction. The heart-and-rose logo positioned where the dot of the 'I' in 'FANNIE' would go.",
    "render_output_slug": "the-fannie",
    "render_source_override": "lh-005-fannie.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "1",
    "garment_type_lock": "",
    "dossier_slug": "the-fannie",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "One Size"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "A **black PU/faux-leather fanny pack (waist-belt bag / cross-body sling)** — small rectangular bag body in pebbled-textured black faux-leather, single front-pocket with a horizontal zipper closure, **adjustable black nylon webbing strap** with a **plastic quick-release buckle** (clip-on/clip-off side-release buckle), worn at the waist or across the chest. NOT a leather handbag.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "A **black PU/faux-leather fanny pack (waist-belt bag / cross-body sling)** — small rectangular bag body in pebbled-textured black faux-leather, single front-pocket with a horizontal zipper closure, **adjustable black nylon webbing strap** with a **plastic quick-release buckle** (clip-on/clip-off side-release buckle), worn at the waist or across the chest. NOT a backpack. NOT a tote bag. NOT a duffel. NOT a wristlet. NOT a leather handbag. **A small accessory product** — distinct from the apparel pieces in the Love Hurts collection.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "lh-005",
    "name": "The Fannie",
    "collection": "love-hurts",
    "slug": "the-fannie",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: A **black PU/faux-leather fanny pack (waist-belt bag / cross-body sling)** — small rectangular bag body in pebbled-textured black faux-leather, single front-pocket with a horizontal zipper closure, **adjustable black nylon webbing strap** with a **plastic quick-release buckle** (clip-on/clip-off side-release buckle), worn at the waist or across the chest. NOT a leather handbag.\nFeatures: A **black PU/faux-leather fanny pack (waist-belt bag / cross-body sling)** — small rectangular bag body in pebbled-textured black faux-leather, single front-pocket with a horizontal zipper closure, **adjustable black nylon webbing strap** with a **plastic quick-release buckle** (clip-on/clip-off side-release buckle), worn at the waist or across the chest. NOT a backpack. NOT a tote bag. NOT a duffel. NOT a wristlet. NOT a leather handbag. **A small accessory product** — distinct from the apparel pieces in the Love Hurts collection.\nColor: Black\nAvailable sizes: One Size",
    "branding_block": "> Logo art canonical references:\n> - Love Hurts logo (cursive script):  `data/brand-logos/love-hurts-logo.md` (only the cursive lettering style is referenced here — the full lockup with broken-heart is NOT on this bag)\n> - Product real photo:                 `assets/products/references/lh-005-fannie-photo.jpeg`\n> - Product mockup:                     `assets/products/references/lh-005-fannie-mockup.jpeg`\n\n### Front\n- **front-body** (the front face of the bag, ~6–8in wide): Solid **black pebbled faux-leather** fabric. **Technique:** stitched. **Color:** black.\n- **front-pocket-zipper** (horizontal, across the front face below the bag's top edge): A black metal/plastic zipper running horizontally across the front face providing access to the front pocket. **Technique:** patch (sewn-on zipper hardware). **Color:** black zipper teeth and pull.\n- **front-center-bottom** (~3–4in wide, centered on the lower front face below the zipper): The wordmark **\"FANNIE\"** in stylized white cursive script lettering, with a small **canonical Love Hurts red rose graphic** decoration to the immediate right of the wordmark (a single small red rose accent — similar in style to the small standalone rose accent used on lh-002 joggers). **Technique:** embroidered (wordmark in white thread + small red rose embroidered detail). **Color:** white \"FANNIE\" + small red rose accent.\n\n### Back\n- **back-body** (the panel against the wearer's body): Solid **black pebbled faux-leather**, no decoration. **Technique:** stitched. **Color:** black.\n- **strap-attachment-points** (D-rings or stitched belt-loops at the upper-left and upper-right corners of the bag): Two D-rings or stitched belt-loops where the nylon strap attaches. **Technique:** patch (sewn-on hardware). **Color:** black.\n\n### Strap / Hardware / Other\n- **adjustable-strap**: Black nylon webbing strap, adjustable length via slider, with a **plastic quick-release side-release buckle** at one point so the strap can clip on and off. **Technique:** patch (sewn-on plastic buckle hardware) + stitched (webbing). **Color:** black webbing + black plastic buckle.\n- **strap-buckle**: Plastic side-release clip buckle. **Technique:** patch (sewn-on plastic hardware). **Color:** black.\n- **interior-tag** (~1in × 0.5in, sewn into the interior of the front pocket): Branded woven size tag (universal SkyyRose product rule, scaled for accessory). **Technique:** woven-label. **Color:** white label, black lettering.",
    "negative_block": "- NO Love Hurts full lockup (wordmark + broken-heart-and-thorns) on the bag — only the \"FANNIE\" wordmark + a single small red rose accent appear. The full Love Hurts lockup is for jackets / shorts / shirts, NOT this small accessory.\n- NO Black Rose three-rose-cluster on this product — this is a Love Hurts collection product.\n- NO multi-color rose-cluster composition — the rose accent is a single small red rose graphic, NOT the full canonical multi-rose-on-cloud composition.\n- NO patches on this bag — the wordmark + rose are EMBROIDERED directly into the front face, NOT sewn-on patches.\n- NO Authentic Collection patch.\n- NO greyscale wordmark — the \"FANNIE\" lettering is WHITE on the black faux-leather.\n- NO red wordmark — the \"FANNIE\" letters are WHITE; the only red element is the small rose graphic accent next to the wordmark.\n- NO additional pockets visible from outside other than the single front zipper-pocket. No back pocket. No side pockets.\n- NO hardware in metal-gold or rose-gold finish — all hardware (buckle, zipper) is BLACK.\n- NO contrast piping along any edge — the bag is uniformly black faux-leather with no contrast piping or trim.\n- NO drawstring closure — closure is the front zipper only.\n- NO embossed or debossed branding — the FANNIE wordmark is embroidered, NOT embossed into the faux-leather surface.\n- NO real leather (this is **faux-leather / PU pebbled-finish**, not genuine leather).\n- NO printed graphics — branding is embroidered.\n- NO Skyy Rose Co script logo on this bag — the only branding is \"FANNIE\" + the small red rose accent.",
    "scene_pose": "Front view straight-on showing the bag worn flat (or laid flat), with the strap visible curving above and connecting to the bag corners — show the buckle clip and the FANNIE wordmark + red rose accent on the lower-front face. Optional alternate view: bag worn cross-body or at the waist on a model to show scale.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/love-hurts-logo.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/lh-005-fannie-photo.jpeg",
    "extra_references": [
      "assets/products/references/lh-005-fannie-mockup.jpeg"
    ]
  },
  "images": {
    "front": {
      "path": "assets/images/products/lh-005-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/the-fannie-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/lh-005-fannie.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/the-fannie-pack-photo.jpg",
    "back": null,
    "reference": "assets/products/references/lh-005-fannie-mockup.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "heart-rose-composite",
        "position": "dot_of_i_in_fannie_text",
        "technique": "leather_emboss_or_patch",
        "notes": "Heart and rose logo positioned where the dot of the 'i' in 'Fannie' would go."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/heart-rose-composite.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Oakland luxury meets everyday utility. The essential Love Hurts fanny pack with premium embroidery.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Oakland luxury meets everyday utility. The essential Love Hurts fanny pack with premium embroidery.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [
    {
      "text": "[ghost] logo is supposed the be the dot of the I",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[on-model] logo is supposed the be the dot of the I",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.953611+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## lh-006 — Love Hurts Joggers (White)

```json
{
  "sku": "lh-006",
  "name": "Love Hurts Joggers (White)",
  "collection": "love-hurts",
  "catalog": {
    "sku": "lh-006",
    "name": "Love Hurts Joggers (White)",
    "price": "95",
    "collection": "love-hurts",
    "description": "The mirror of lh-002 in white. Solid white body with black contrast side-panels running vertically from waist to ankle. White flat drawstring. The Love Hurts heart-rose-composite embroidered on the left thigh — the heart-and-thorns lockup with roses emerging from the top, rendered in red, green, and crimson on the white fabric. Mid-weight cotton-fleece, athletic-fit through the leg, ribbed ankle cuffs. Mirror black colorway available as lh-002.",
    "badge": "",
    "image": "assets/images/products/lh-006-joggers-white.jpeg",
    "front_model_image": "assets/images/products/lh-006-onmodel.webp",
    "back_image": "assets/images/products/love-hurts-joggers-white-back-model.webp",
    "back_model_image": "assets/images/products/love-hurts-joggers-white-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Heart-rose-composite (Love Hurts heart-and-thorns lockup) embroidered on the left thigh. Black contrast side-panel running vertically on both side seams. White drawstring.",
    "render_output_slug": "love-hurts-joggers-white",
    "render_source_override": "lh-006-joggers-white.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "joggers",
    "dossier_slug": "love-hurts-joggers-white",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs).",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Mid-weight cotton-fleece fabric. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs). Mid-weight cotton-fleece fabric. **WHITE body** with **BLACK contrast side-panel running vertically down each side leg** (waistband to ankle on both left and right side seams). White flat drawstring. NOT pants. NOT shorts. NOT a track short. NOT a basketball jogger. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique. The black-base mirror colorway is a separate SKU (`lh-002`).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "lh-006",
    "name": "Love Hurts Joggers (White)",
    "collection": "love-hurts",
    "slug": "love-hurts-joggers-white",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Mid-weight cotton-fleece fabric. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique.\nFit: Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs).\nFeatures: Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs). Mid-weight cotton-fleece fabric. **WHITE body** with **BLACK contrast side-panel running vertically down each side leg** (waistband to ankle on both left and right side seams). White flat drawstring. NOT pants. NOT shorts. NOT a track short. NOT a basketball jogger. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique. The black-base mirror colorway is a separate SKU (`lh-002`).\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Heart-rose composite (Love Hurts heart-and-thorns lockup): `data/brand-logos/heart-rose-composite.md`\n> - Love Hurts wordmark (NOT on this product, listed for canonical reference): `data/brand-logos/love-hurts-logo.md`\n> - Product techflat (shared with lh-002): `assets/products/references/lh-006-techflat-front.jpeg`\n\n### Front\n- **front-body** (entire front body — solid white field): Solid white, cotton-fleece. **Technique:** stitched. **Color:** white.\n- **front-left-pocket** (vertical slash pocket at the left side of the upper hip): Slash-style hand pocket at the front left side, with vertical welt opening. **Technique:** stitched (sewn-on welt edges). **Color:** body-matching white.\n- **front-right-pocket** (vertical slash pocket at the right side of the upper hip): Slash-style hand pocket at the front right side, with vertical welt opening. **Technique:** stitched (sewn-on welt edges). **Color:** body-matching white.\n- **left-thigh** (centered on the wearer's left thigh, just below the hip): **Heart-rose-composite logo** — the Love Hurts heart-and-thorns lockup with roses emerging from the top, rendered embroidered on the white body fabric. **Technique:** embroidered. **Color:** red roses + green thorns + crimson heart, on white body.\n\n### Back\n- (No back-body decoration. The back is a clean panel with no embroidered logo or graphic — the contrast side-panel wraps cleanly from front to back through the side seam.)\n\n### Sleeves / Collar / Hem / Other\n- **left-side-panel** (vertical contrast strip running from waistband to ankle on the left side seam): A BLACK contrast-fabric panel inserted along the left side seam. The panel is approximately 1.5in–2in wide and runs continuously from the waistband down to the ankle hem. **Technique:** stitched (contrast fabric panel sewn into the side seam). **Color:** black.\n- **right-side-panel** (vertical contrast strip running from waistband to ankle on the right side seam): A BLACK contrast-fabric panel inserted along the right side seam. The panel is approximately 1.5in–2in wide and runs continuously from the waistband down to the ankle hem. **Technique:** stitched. **Color:** black.\n- **waistband**: White elasticated waistband with **white flat drawstring**. **Technique:** stitched. **Color:** white.\n- **drawstring**: White flat drawstring. **Technique:** stitched. **Color:** white.\n- **left-ankle-cuff** (ribbed-knit band at the left ankle hem): Ribbed-knit cuff at the left ankle in white (some variants may use a banded-elastic cuff instead of rib-knit). **Technique:** stitched. **Color:** white.\n- **right-ankle-cuff** (ribbed-knit band at the right ankle hem): Ribbed-knit cuff at the right ankle in white (some variants may use a banded-elastic cuff instead of rib-knit). **Technique:** stitched. **Color:** white.\n- **inside-waistband** (~1.25in × 0.5in, sewn into the inside front waistband): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** white label, black lettering.",
    "negative_block": "- NO Love Hurts wordmark across the leg or thigh — the only Love-Hurts-coded mark on this product is the heart-rose-composite on the left thigh.\n- NO red roses cloud cluster on the joggers — that motif is on lh-003 (basketball shorts) and lh-004 (bomber inside-hood), NOT here.\n- NO sublimated all-over rose pattern on the body — the white body is SOLID white fabric (not sublimated).\n- NO mirror colorway in this SKU — the black-base / white-panel mirror is a separate SKU (`lh-002 Love Hurts Joggers (Black)`).\n- NO contrast piping at the waistband or cuffs — only the side-seam panel is contrast.\n- NO horizontal stripe blocking — the contrast panel runs VERTICALLY along the side seam, top to bottom.\n- NO decoration on the right thigh — the heart-rose-composite sits on the LEFT thigh only.\n- NO embossed/debossed decoration anywhere.\n- NO printed all-over graphic on the body — body is solid white.\n- NO Black Rose three-rose-cluster on this product — this is a Love Hurts collection product. Black Rose marks (gothic greyscale) do NOT appear here.\n- NO contrast satin-stitch on any decoration.\n- NO zipper closures on the pockets — slash pockets are open-welt, not zippered.\n- NO patch applications on the joggers — branding is embroidered, not patch-sewn.\n- NO ankle taper that hits above the cuff — joggers terminate cleanly at the ribbed/banded cuff at ankle level.",
    "scene_pose": "Front view straight-on (laid flat or on a model) showing the white body + the vertical black contrast side-panel + the heart-rose-composite on the left thigh + the white drawstring. For the back: clean back panel showing the contrast side-panel continuing.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/love-hurts-logo.md",
    "extra_logos": [
      "data/brand-logos/heart-rose-composite.md"
    ],
    "reference_image": "assets/products/references/lh-006-techflat-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/lh-006-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/love-hurts-joggers-white-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/lh-006-joggers-white.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/love-hurts-joggers-white-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/lh-006-joggers-white.jpeg",
    "back": null,
    "reference": "assets/products/references/lh-006-techflat-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "heart-rose-composite",
        "position": "left_thigh",
        "technique": "embroidered"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/heart-rose-composite.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Beneath the Oakland sky, where concrete kisses the soul, there's a fire burning. The Fannie isn't just a bag; it's a piece of that fire, forged in love and loss. From 'LOVE HURTS', this fanny pack embodies the grit and grace of the streets. Sleek black material, tough as the streets, adorned with a defiant embroidered rose. A symbol of Oakland authenticity, luxury born from concrete.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "From the SkyyRose 'LOVE HURTS' collection, The Fannie is a luxury fanny pack embodying Oakland grit, passion, and the defiant bloom of a street rose.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose The Fannie: luxury fanny pack from the LOVE HURTS collection. Oakland-inspired streetwear with rose embroidery. Pre-order now.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Oakland heart, luxury soul. The Fannie from 'LOVE HURTS': street grit meets style. Carry your story, blooming with a rose. Pre-order now.\n\n#SkyyRose #LoveHurts #OaklandFashion #BayAreaStyle #StreetwearFashion #GritAndGrace #UrbanLuxury",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Oakland fire, luxury desire! The Fannie from SkyyRose's 'LOVE HURTS' collection. Pre-order now! #SkyyRose #LoveHurts #Oakland",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "lh-006-product": "The Fannie: black SkyyRose fanny pack featuring white script embroidery and a red rose graphic."
  },
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.964372+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-001 — The Bridge Series 'The Bay Bridge' Shorts

```json
{
  "sku": "sg-001",
  "name": "The Bridge Series 'The Bay Bridge' Shorts",
  "collection": "signature",
  "catalog": {
    "sku": "sg-001",
    "name": "The Bridge Series 'The Bay Bridge' Shorts",
    "price": "65",
    "collection": "signature",
    "description": "Embody West Coast luxury. Athletic shorts wrapped in a sublimated Bay Bridge skyline with the iconic embroidered rose.",
    "badge": "Pre-Order",
    "image": "assets/images/products/sg-001-bay-bridge-shorts.jpeg",
    "front_model_image": "assets/images/products/bridge-bay-bridge-shorts-front-model.webp",
    "back_image": "assets/images/products/the-bay-set-back-model.webp",
    "back_model_image": "assets/images/products/bridge-bay-bridge-shorts-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Blue",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Bay Bridge daytime all-over photographic print; blue embroidered rose at wearer-left lower leg, blue waistband, white drawstring.",
    "render_output_slug": "bridge-bay-bridge-shorts",
    "render_source_override": "sg-001-bay-bridge-shorts.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shorts",
    "dossier_slug": "the-bridge-series-the-bay-bridge-shorts",
    "engine_override": ""
  },
  "garment": {
    "color": "Blue",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Bay Bridge (San Francisco-Oakland Bay Bridge) in daytime / clear-blue-sky lighting**.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Bay Bridge (San Francisco-Oakland Bay Bridge) in daytime / clear-blue-sky lighting**. The photo print shows the steel-cabled Bay Bridge crossing the water with the SF skyline visible in the background, blue sky overhead, and water reflections at the bottom hem. Standard basketball-shorts construction: blue elasticated waistband at the top with **white drawstring**, vertical slash side hand pockets, knee-length cut, no leg-binding contrast piping. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short. NOT a basketball jersey. NOT the Stay Golden Shorts (that's sg-003 — Golden Gate Bridge night palette, separate SKU).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-001",
    "name": "The Bridge Series 'The Bay Bridge' Shorts",
    "collection": "signature",
    "slug": "the-bridge-series-the-bay-bridge-shorts",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Bay Bridge (San Francisco-Oakland Bay Bridge) in daytime / clear-blue-sky lighting**.\nFeatures: Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Bay Bridge (San Francisco-Oakland Bay Bridge) in daytime / clear-blue-sky lighting**. The photo print shows the steel-cabled Bay Bridge crossing the water with the SF skyline visible in the background, blue sky overhead, and water reflections at the bottom hem. Standard basketball-shorts construction: blue elasticated waistband at the top with **white drawstring**, vertical slash side hand pockets, knee-length cut, no leg-binding contrast piping. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short. NOT a basketball jersey. NOT the Stay Golden Shorts (that's sg-003 — Golden Gate Bridge night palette, separate SKU).\nColor: Blue\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "Exact SKU artwork and front placement are bound in `logo-registry.json::sku_logos::sg-001::render_reference` to `assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png`. The existing physical-authority record and its current file hash agree. Use the complete garment pixels for artwork, position and relative scale; no generic cluster recoloring.\n\n### Front\n- **front-body** (entire body — front and back continuous): All-over sublimated photographic print of the **San Francisco-Oakland Bay Bridge in daytime daylight** — clear blue sky filling the upper third, the steel-truss Bay Bridge spanning across the middle (center-aligned, with the cantilever section visible), the SF skyline (downtown buildings) visible behind/beside the bridge, and water at the lower portion with reflections of the bridge. Photographic, hyper-realistic, NOT illustrated. The print wraps continuously front-to-back. **Technique:** sublimated. **Color:** photographic full-color (blue sky + grey-and-white bridge steel + tan/grey building skyline + blue water with reflections).\n\n- **front-wearer-left-lower-leg** (~3in tall, wearer-left lower-leg panel (viewer-right in front view), layered on top of the sublimated bridge print): Embroidered **blue** rose-cluster — the daytime variant carries a BLUE rose (the night Stay Golden variant carries a purple rose, see sg-003). **Technique:** embroidered. **Color:** blue thread. Catalog branding_spec (canonical): \"Embroidered rose on the bottom-left.\"\n\n### Back\n- **back-body** (entire field, continuation of front): Same Bay Bridge daytime photographic print continuing seamlessly from the front around to the back. **Technique:** sublimated. **Color:** photographic full-color, continuous wrap.\n\n### Sleeves / Collar / Hem / Other\n- **waistband** (~1.5in tall, top of shorts): Blue elasticated waistband at the top. **Technique:** stitched. **Color:** blue.\n- **drawstring** (~24in long, threaded through waistband): White flat drawstring threaded through the waistband, hanging from the front center. **Technique:** stitched. **Color:** white.\n- **left-pocket** (front-side hand pocket on wearer's left): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching (mesh shows the underlying photo print).\n- **right-pocket** (front-side hand pocket on wearer's right): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching.\n- **leg-hem** (each leg opening, clean hem): Plain finished hem at each leg opening — no contrast piping, no contrast binding, no rib-knit band. **Technique:** stitched. **Color:** body-matching.\n- **inside-waistband** (~1.5in × 0.5in interior tag): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO Golden Gate Bridge in the print — this is the BAY BRIDGE (a steel-truss/cantilever bridge with the SF skyline behind it), NOT the Golden Gate (the orange suspension bridge between SF and Marin). The Golden Gate appears on sg-003 Stay Golden Shorts.\n- NO sunset / twilight / orange palette — this is the DAYTIME Bay Bridge with blue sky. The night palette belongs to sg-003.\n- NO night-time Bay Bridge with city lights — this is the clear-day variant. (A night-Bay-Bridge alternate render exists in older asset directories but is NOT a current SKU.)\n- NO illustrated / cartoon-rendered bridge — the print is a hyper-realistic photographic sublimation, not a stylized illustration.\n- The ONLY layered mark is the embroidered BLUE rose-cluster at the bottom-left leg (see Front) — daytime Bay Bridge variant = BLUE rose. NO rose graphics anywhere else on the body.\n- NO purple rose on this SKU — purple is the night variant (sg-003 Stay Golden). The daytime Bay Bridge carries the BLUE rose.\n- NO Love Hurts canonical roses, NO SR monogram, NO Authentic Collection patch on these shorts. Branding = the bridge photograph + the single bottom-left blue rose.\n- NO black mesh body — body is WHITE mesh with the sublimated print on top (the print supplies all visible color).\n- NO contrast color side-panels — body is uniform front-to-back.\n- NO black drawstring — drawstring is WHITE.\n- NO white waistband — waistband is BLUE.\n- NO zipper closures on the pockets — open welt.\n- NO additional pockets on the back — only two front side hand pockets.\n- NO embossed/debossed decoration anywhere.\n- NO rib-knit leg-binding — the leg opening is a clean stitched hem.\n- NO numbers, NO wordmark, NO chest text — bridge photo print is the only graphic.\n- NO sleeves (this is a shorts garment, lower-body only).",
    "scene_pose": "Front view straight-on (laid flat or on a model) showing the full daytime Bay Bridge sublimated print, the blue waistband, white drawstring, and clean leg hem. Three-quarter view shows the side wrap of the photo print and the slash pocket openings. For the back: back view straight-on showing the continuous bridge print.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png",
    "extra_logos": [],
    "reference_image": "assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-001-bay-bridge-shorts.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/bridge-bay-bridge-shorts-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-001-bay-bridge-shorts.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/the-bay-set-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png",
    "back": null,
    "reference": "assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "wearer_left_lower_leg",
        "technique": "embroidered",
        "colorway": "blue",
        "notes": "Exact blue embroidered rose and pale cloud on wearer-left lower leg, viewer-right in the front source. Copy artwork and placement from this SKU's physical garment."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png",
    "reference_kind": "garment",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Immerse yourself in the sun-drenched opulence of the West Coast with The Bay Set, a definitive statement piece from the SkyyRose SIGNATURE Collection. This exclusive ensemble is meticulously crafted for those who embody the spirit and ambition of the Bay Area. The crisp white tee showcases our iconic SkyyRose, rendered in a striking blue and silver, a testament to enduring beauty rising from the heart of Oakland's vibrant streets. This emblem mirrors the grace and relentless drive that defines our beloved home. Accompanying the tee are the exquisitely designed shorts, offering unparalleled comfort and a vivid display of artistry. A breathtaking panorama of the Bay's majestic skyline and iconic bridges adorns these shorts, a wearable masterpiece infused with subtle hints of our signature blue rose. This subtle nod pays homage to the vibrant energy and unparalleled beauty of our origin. More than mere streetwear, The Bay Set is a declaration of prestige, a confident stride into a legacy of impeccable style. Secure your place in this exclusive narrative. The Bay Set is available for pre-order, a limited opportunity to claim your piece of West Coast luxury. Elevate your wardrobe, elevate your legacy – this is SkyyRose.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "The Bay Set: embody West Coast luxury with this SIGNATURE collection ensemble. Featuring the iconic blue rose and a vibrant Bay Area skyline, it's a testament to refined style.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose The Bay Set: luxury streetwear embodying West Coast prestige. Features signature blue rose & Bay Area skyline. Pre-order now for exclusive style.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Step into West Coast opulence with The Bay Set ✨. This SIGNATURE collection piece embodies the golden spirit of the Bay Area, showcasing our iconic blue rose and a breathtaking skyline. It's more than streetwear; it's a statement of refined style and unwavering pride. Elevate your legacy. Pre-order now and wear the Bay.\n\n#SkyyRose #SignatureCollection #LuxuryFashion #BayAreaLuxury #WestCoastStyle #CoutureStreetwear #BlueRose #ExclusiveFashion #TheBaySet #PrestigeWear #BayAreaProud #FashionForward",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Bay Area drip just dropped! 💎 The Bay Set = ultimate luxury meets West Coast pride. Pre-order yours now! #SkyyRose #BaySet #Luxury",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-001-product-2": "The Bay Set: White t-shirt with blue rose and cloud graphic, and blue mesh shorts with cityscape and bridge.",
    "sg-001-product": "The Bay Set features a white t-shirt with a blue rose design and blue-green cityscape shorts."
  },
  "corrections": [
    {
      "text": "[ghost-back] looks more like a tech flat",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] missing logo and not rendered looks more like a tech flat",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:38.973047+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-002 — The Bridge Series 'Stay Golden' Shirt

```json
{
  "sku": "sg-002",
  "name": "The Bridge Series 'Stay Golden' Shirt",
  "collection": "signature",
  "catalog": {
    "sku": "sg-002",
    "name": "The Bridge Series 'Stay Golden' Shirt",
    "price": "65",
    "collection": "signature",
    "description": "Embrace West Coast prestige. Luxurious statement of Bay Area style featuring signature rose.",
    "badge": "Pre-Order",
    "image": "assets/images/products/sg-002-stay-golden-shirt.jpeg",
    "front_model_image": "assets/images/products/sg-002-stay-golden-shirt.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/stay-golden-tee-back-model.webp",
    "sizes": "XS|S|M|L|XL|2XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Embroidered purple rose on front chest center with Golden Gate Bridge at night imagery stitched inside the rose petals. Preserve exact artwork and relative scale from the bound physical garment. SR monogram at back collar per existing specification.",
    "render_output_slug": "bridge-stay-golden-shirt",
    "render_source_override": "sg-002-stay-golden-shirt.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shirt",
    "dossier_slug": "the-bridge-series-stay-golden-shirt",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "XS",
      "S",
      "M",
      "L",
      "XL",
      "2XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem. Pairs in The Bridge Series with the Stay Golden Shorts (sg-003 Golden Gate night palette). NOT a tank. NOT a long-sleeve tee. NOT a hoodie. NOT a polo. NOT the Bay Bridge Shirt (that's sg-005 — blue rose-cluster decoration, separate SKU). **The Stay Golden colorway uses a PURPLE/VIOLET rose-cluster on the chest** (matching the purple-and-orange Golden Gate night palette).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-002",
    "name": "The Bridge Series 'Stay Golden' Shirt",
    "collection": "signature",
    "slug": "the-bridge-series-stay-golden-shirt",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem.\nFeatures: Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem. Pairs in The Bridge Series with the Stay Golden Shorts (sg-003 Golden Gate night palette). NOT a tank. NOT a long-sleeve tee. NOT a hoodie. NOT a polo. NOT the Bay Bridge Shirt (that's sg-005 — blue rose-cluster decoration, separate SKU). **The Stay Golden colorway uses a PURPLE/VIOLET rose-cluster on the chest** (matching the purple-and-orange Golden Gate night palette).\nColor: White\nAvailable sizes: XS | S | M | L | XL | 2XL",
    "branding_block": "Exact SKU artwork and front placement are bound in `logo-registry.json::sku_logos::sg-002::render_reference` to `assets/products/source-photos/signature/sg-002-stay-golden-shirt-front-authentic.jpg`. The existing physical-authority record and its current file hash agree. Use the complete garment pixels for artwork, position and relative scale; no generic cluster recoloring.\n\n### Front\n- **front-chest-center** (position and relative dimensions exactly as shown on the bound physical garment): Embroidered purple rose composition containing photographic Golden Gate Bridge at night imagery inside its petals, with silver/grey stems and vines and a dark charcoal/black cloud. Preserve the complete composition, including bridge detail within the blooms; this is not a plain recolored rose. **Technique:** embroidered. **Color:** exact purple bridge-filled artwork on white.\n\n### Back\n- **back-neck** (small, ~1.5in wide, top-center just below the collar): The SR monogram embroidered onto the jersey in **dark grey / black thread** (NOT canonical gold — black-on-white reads cleanly where gold-on-white would not on a casual tee). Rendered as the canonical SR cursive script. **Technique:** embroidered. **Color:** dark grey / black thread on white.\n\n### Sleeves / Collar / Hem / Other\n- **collar** (~0.5in wide ribbed crew neck): Standard ribbed crew-neck collar. **Technique:** stitched. **Color:** white.\n- **left-sleeve** (short sleeve, plain hem): Short set-in sleeve, plain stitched hem at the cuff. **Technique:** stitched. **Color:** white.\n- **right-sleeve** (short sleeve, plain hem): Mirror of left-sleeve. **Technique:** stitched. **Color:** white.\n- **hem** (straight even bottom hem): Plain stitched bottom hem. **Technique:** stitched. **Color:** white.\n- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO blue rose-cluster on the chest — this is the PURPLE/VIOLET Stay Golden colorway. Blue rose-cluster belongs to sg-005 Bay Bridge Shirt.\n- NO canonical multi-color rose-cluster (red roses + green stems + white-and-blue cloud) — the exact Golden Gate-filled composition is bound to this SKU.\n- NO generic greyscale rose-cluster; use the exact registered Golden Gate-filled rose.\n- NO all-over bridge print on the shirt. Photographic bridge imagery IS required inside the registered rose petals; the surrounding shirt body remains solid white.\n- NO chest text or wordmark on the front body fabric — only the registered bridge-filled chest rose decoration.\n- NO logo or graphic on the back body — only the small back-neck SR monogram.\n- NO Authentic Collection patch — that patch is reserved for the Black Rose jersey series.\n- NO Love Hurts branding — this is a Signature collection product.\n- NO sublimated all-over body pattern — body is solid white.\n- NO contrast color sleeve cuffs or hem.\n- NO embossed/debossed decoration.\n- NO V-neck or henley placket — this is a crew-neck tee with no front opening.",
    "scene_pose": "Front view straight-on showing the center-chest Golden Gate-filled rose composition on the white tee, the crew neck, and the short sleeves. For the back: back view straight-on showing the small SR monogram at the back-neck.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "assets/products/source-photos/signature/sg-002-stay-golden-shirt-front-authentic.jpg",
    "extra_logos": [
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/source-photos/signature/sg-002-stay-golden-shirt-front-authentic.jpg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-002-stay-golden-shirt.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/stay-golden-tee-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-002-stay-golden-shirt.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/source-photos/signature/sg-002-stay-golden-shirt-front-authentic.jpg",
    "back": null,
    "reference": "assets/products/source-photos/signature/sg-002-stay-golden-shirt-front-authentic.jpg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_chest_center",
        "technique": "embroidered",
        "colorway": "purple",
        "notes": "Exact Golden Gate Bridge at night photographic imagery is stitched inside the rose petals. Match the purple palette, stems, cloud and center-chest proportions in the bound physical garment source. No generic recoloring or small left-chest substitution."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/source-photos/signature/sg-002-stay-golden-shirt-front-authentic.jpg",
    "reference_kind": "garment",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Bathed in the perpetual glow of California sunshine, the SkyyRose SIGNATURE 'Stay Golden' Set is more than apparel—it's a wearable embodiment of West Coast aspiration. Imagine strolling through sun-drenched streets, the embodiment of success and effortless style. This set isn't just seen; it's felt, radiating confidence and a golden aura. The crisp white tee features a mesmerizing, multi-hued rose graphic, blossoming from ethereal clouds with intricate detail. This vibrant design, a symbol of growth and enduring beauty, serves as a captivating focal point, perfectly balanced by the premium fabric's clean lines and soft touch. Complementing this, the luxuriously textured mesh shorts showcase a vibrant, abstract cityscape interwoven with iconic Bay Area landmarks. A harmonizing rose emblem subtly adorns the shorts, unifying the set's visual narrative with a touch of SkyyRose heritage. Experience a symphony of comfort and unparalleled style that speaks volumes, allowing you to carry the golden essence of the Bay wherever your journey takes you. Pre-order this exclusive set now and secure your piece of SkyyRose legacy—truly Stay Golden.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Embrace West Coast prestige with the SkyyRose SIGNATURE Stay Golden Set—a luxurious statement of Bay Area style featuring our signature rose and cityscape.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Stay Golden Set: Luxurious Bay Area streetwear. Own a piece of West Coast prestige with this exclusive pre-order. Shop now!",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Shine like California gold in the SkyyRose SIGNATURE Stay Golden Set ✨. This exclusive pre-order captures the essence of Bay Area luxury, blending our signature rose with a vibrant cityscape. Elevate your legacy and Stay Golden 💛.\n\n#SkyyRose #SignatureCollection #StayGolden #LuxuryStreetwear #BayAreaFashion #CoutureStyle #WestCoastVibes #GoldenHour #LimitedEdition #PrestigeFashion #SkyyRoseCollection #StreetwearCouture",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Golden vibes only in the SkyyRose Stay Golden Set! ✨ Bay Area luxury meets iconic streetwear. Pre-order yours now! 💛 #StayGolden #SkyyRose #BayArea",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-002-product": "Stay Golden Set: White tee with vibrant rose graphic from clouds, and mesh shorts with a colorful cityscape."
  },
  "corrections": [
    {
      "text": "[ghost] needs to be slightly bigger and look embroidered for the logo",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.979007+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-003 — The Bridge Series 'Stay Golden' Shorts

```json
{
  "sku": "sg-003",
  "name": "The Bridge Series 'Stay Golden' Shorts",
  "collection": "signature",
  "catalog": {
    "sku": "sg-003",
    "name": "The Bridge Series 'Stay Golden' Shorts",
    "price": "65",
    "collection": "signature",
    "description": "From the Bridge Series. Athletic shorts in Stay Golden colorway celebrating Bay Area luxury.",
    "badge": "Pre-Order",
    "image": "assets/images/products/sg-003-stay-golden-shorts.jpeg",
    "front_model_image": "assets/images/products/bridge-stay-golden-shorts-front-model.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/bridge-stay-golden-shorts-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Golden Gate Bridge at night all-over photographic print; purple embroidered rose at wearer-left lower leg, purple waistband, white drawstring.",
    "render_output_slug": "bridge-stay-golden-shorts",
    "render_source_override": "sg-003-stay-golden-shorts.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shorts",
    "dossier_slug": "the-bridge-series-stay-golden-shorts",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Golden Gate Bridge at night**.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Golden Gate Bridge at night**. The photo print shows the iconic Golden Gate Bridge illuminated against a deep purple-violet/navy night sky, with golden city-light reflections rippling vertically across the dark water at the lower portion. Standard basketball-shorts construction: purple elasticated waistband at the top with **white drawstring**, vertical slash side hand pockets, knee-length cut, no leg-binding contrast piping. \"Stay Golden\" refers to the **Golden Gate Bridge lit gold against the night sky** (this is the NIGHT variant — carries a purple rose; the daytime Bay Bridge variant sg-001 carries a blue rose). NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short. NOT the Bay Bridge Shorts (that's sg-001 — daytime SF-Oakland Bay Bridge, separate SKU).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-003",
    "name": "The Bridge Series 'Stay Golden' Shorts",
    "collection": "signature",
    "slug": "the-bridge-series-stay-golden-shorts",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Golden Gate Bridge at night**.\nFeatures: Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Golden Gate Bridge at night**. The photo print shows the iconic Golden Gate Bridge illuminated against a deep purple-violet/navy night sky, with golden city-light reflections rippling vertically across the dark water at the lower portion. Standard basketball-shorts construction: purple elasticated waistband at the top with **white drawstring**, vertical slash side hand pockets, knee-length cut, no leg-binding contrast piping. \"Stay Golden\" refers to the **Golden Gate Bridge lit gold against the night sky** (this is the NIGHT variant — carries a purple rose; the daytime Bay Bridge variant sg-001 carries a blue rose). NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short. NOT the Bay Bridge Shorts (that's sg-001 — daytime SF-Oakland Bay Bridge, separate SKU).\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "Exact SKU artwork and front placement are bound in `logo-registry.json::sku_logos::sg-003::render_reference` to `assets/products/source-photos/signature/sg-003-stay-golden-shorts-front-authentic.png`. The existing physical-authority record and its current file hash agree. Use the complete garment pixels for artwork, position and relative scale; no generic cluster recoloring.\n\n### Front\n- **front-body** (entire body — front and back continuous): All-over sublimated photographic print of the **Golden Gate Bridge at night** — deep purple-violet/navy night sky filling the upper third, the iconic **Golden Gate Bridge illuminated** across the middle (the bridge reads warm orange-gold from its lighting against the dark sky), and rippling dark water at the lower portion with **vertical golden city-light reflections** (gold + yellow + pink + white streaks running vertically downward) reflecting the lit bridge and city against the water. Photographic, hyper-realistic, NOT illustrated. The print wraps continuously front-to-back. **Technique:** sublimated. **Color:** photographic full-color (deep purple-violet/navy sky + warm gold lit bridge + golden/yellow/pink reflections on dark water).\n- **front-wearer-left-lower-leg** (~3in tall, wearer-left lower-leg panel (viewer-right in front view), layered on top of the sublimated bridge print): Embroidered **purple** rose-cluster — the night Stay Golden variant carries a PURPLE rose (the daytime Bay Bridge variant sg-001 carries a blue rose). **Technique:** embroidered. **Color:** purple thread. Catalog branding_spec (canonical): \"Purple embroidered rose on the bottom-left.\"\n\n### Back\n- **back-body** (entire field, continuation of front): Same Golden Gate night photographic print continuing seamlessly from the front around to the back. **Technique:** sublimated. **Color:** photographic full-color night, continuous wrap.\n\n### Sleeves / Collar / Hem / Other\n- **waistband** (~1.5in tall, top of shorts): Purple elasticated waistband at the top (same construction as sg-001, with this SKU’s purple colorway). **Technique:** stitched. **Color:** purple.\n- **drawstring** (~24in long, threaded through waistband): White flat drawstring threaded through the waistband, hanging from the front center. **Technique:** stitched. **Color:** white.\n- **left-pocket** (front-side hand pocket on wearer's left): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching.\n- **right-pocket** (front-side hand pocket on wearer's right): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching.\n- **leg-hem** (each leg opening, clean hem): Plain finished hem — no contrast piping, no rib-knit band. **Technique:** stitched. **Color:** body-matching.\n- **inside-waistband** (~1.5in × 0.5in interior tag): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO Bay Bridge in the print — this is the GOLDEN GATE (orange-red suspension bridge between SF and Marin), NOT the Bay Bridge (steel-truss bridge between SF and Oakland with downtown skyline). The Bay Bridge appears on sg-001.\n- NO daytime / clear-blue-sky palette — this is the NIGHT variant with a deep purple-violet/navy sky and golden city lights. Daytime palette belongs to sg-001.\n- NO illustrated / cartoon-rendered bridge — the print is a hyper-realistic photographic sublimation.\n- NO SF skyline in the photo — the Golden Gate bridge spans water + Marin headlands, NOT downtown skyline. (The Bay Bridge image has the skyline; this one does not.)\n- The ONLY layered mark is the embroidered PURPLE rose-cluster at the bottom-left leg (see Front) — night Stay Golden variant = PURPLE rose. NO rose graphics anywhere else on the body.\n- NO blue rose on this SKU — blue is the daytime variant (sg-001 Bay Bridge). The night Stay Golden carries the PURPLE rose.\n- NO Love Hurts canonical roses, NO SR monogram, NO Authentic Collection patch. Branding = the bridge photograph + the single bottom-left purple rose.\n- NO black mesh body — body is WHITE mesh with the sublimated night print on top.\n- NO contrast color side-panels.\n- NO black drawstring — drawstring is WHITE.\n- NO white waistband — waistband is PURPLE.\n- NO zipper closures on the pockets.\n- NO additional back pockets.\n- NO embossed/debossed decoration.\n- NO rib-knit leg-binding — clean stitched hem.\n- NO numbers, NO wordmark, NO chest text on the body.\n- NO sleeves.",
    "scene_pose": "Front view straight-on showing the full night Golden Gate sublimated print, the purple waistband, white drawstring, and clean leg hem. Three-quarter view shows the side wrap of the night gradient and the orange-red bridge silhouette wrapping side-to-side. For the back: back view straight-on showing the continuous night bridge print.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "assets/products/source-photos/signature/sg-003-stay-golden-shorts-front-authentic.png",
    "extra_logos": [],
    "reference_image": "assets/products/source-photos/signature/sg-003-stay-golden-shorts-front-authentic.png",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/hub/sg-003-front.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/bridge-stay-golden-shorts-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-003-stay-golden-shorts.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/source-photos/signature/sg-003-stay-golden-shorts-front-authentic.png",
    "back": null,
    "reference": "assets/products/source-photos/signature/sg-003-stay-golden-shorts-front-authentic.png"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "wearer_left_lower_leg",
        "technique": "embroidered",
        "colorway": "purple",
        "notes": "Exact purple embroidered rose and pale cloud on wearer-left lower leg, viewer-right in the front source. Copy artwork and placement from this SKU's physical garment."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/source-photos/signature/sg-003-stay-golden-shorts-front-authentic.png",
    "reference_kind": "garment",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Indulge in the understated opulence of The Signature Tee in Orchid, a testament to SkyyRose's commitment to elevated everyday wear. Imagine the cool caress of premium fabric against your skin, a whisper of luxury that accompanies every move. This is more than a t-shirt; it's a foundation piece, meticulously crafted to integrate seamlessly into your curated wardrobe. The subtle orchid hue evokes the tranquil beauty of a Bay Area sunset, while the iconic gold 'SkyyRose' neck label and sleeve emblem quietly assert your discerning taste. The refined silhouette offers unparalleled versatility, effortlessly complementing both tailored ensembles and relaxed weekend attire. This piece doesn't just complete an outfit; it elevates it. Experience the prestige of bespoke design, reimagined for the modern era. Command attention without uttering a word. Wear the legacy. SkyyRose: Defining the future of California couture, one exquisite detail at a time.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "The Signature Tee in Orchid: embody elevated style with this premium staple, showcasing SkyyRose's commitment to couture-level everyday luxury.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Signature Tee in Orchid: Experience refined luxury with this premium Bay Area essential. Elevate your signature style today.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Step into a realm of quiet confidence with The Signature Tee in Orchid. This piece whispers of prestige, from its luxuriously soft fabric to the subtle gleam of the gold SkyyRose emblem. It's not just a tee; it's a statement of refined taste.\n\nElevate your everyday. Define your legacy. #SkyyRose #SignatureCollection #LuxuryFashion #Couture #ElevatedStyle #BayAreaLuxury #FashionForward #SignatureStyle #ExclusiveFashion #Prestige #OrchidTee #GoldStandard",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Signature style unlocked! ✨ The Orchid Tee: luxe comfort meets Bay Area cool. Level up your look. #SkyyRose #SignatureCollection #LuxuryFashion",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-003-product-2": "The Signature Tee in mauve, featuring a black SkyyRose neck label and branded sleeve tag.",
    "sg-003-product": "The Signature Tee in purple, featuring a SkyyRose neck label and sleeve logo."
  },
  "corrections": [
    {
      "text": "[ghost-back] looks more like a tech flat",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[ghost] missing logo and not rendered looks more like a tech flat",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.986958+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-005 — The Bridge Series 'The Bay Bridge' Shirt

```json
{
  "sku": "sg-005",
  "name": "The Bridge Series 'The Bay Bridge' Shirt",
  "collection": "signature",
  "catalog": {
    "sku": "sg-005",
    "name": "The Bridge Series 'The Bay Bridge' Shirt",
    "price": "25",
    "collection": "signature",
    "description": "From the Bridge Series. White tee with blue rose and Bay Bridge emblem celebrating the iconic crossing.",
    "badge": "Pre-Order",
    "image": "assets/images/products/sg-005-bay-bridge-shirt.jpeg",
    "front_model_image": "assets/images/products/sg-005-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/bridge-bay-bridge-shirt-back-model.webp",
    "sizes": "S|M|L|XL|2XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Embroidered blue rose on front chest center with Bay Bridge daytime imagery stitched inside the rose petals. Preserve exact artwork and relative scale from the bound physical garment. SR monogram at back collar per existing specification.",
    "render_output_slug": "bridge-bay-bridge-shirt",
    "render_source_override": "sg-005-bay-bridge-shirt.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shirt",
    "dossier_slug": "the-bridge-series-the-bay-bridge-shirt",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem. Pairs in The Bridge Series with the Bay Bridge Shorts (sg-001 daytime SF-Oakland Bay Bridge palette). NOT a tank. NOT a long-sleeve tee. NOT a hoodie. NOT a polo. NOT the Stay Golden Shirt (that's sg-002 — purple rose-cluster decoration, separate SKU). **The Bay Bridge colorway uses a BLUE/CYAN rose-cluster on the chest** (matching the daytime-blue Bay Bridge palette).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-005",
    "name": "The Bridge Series 'The Bay Bridge' Shirt",
    "collection": "signature",
    "slug": "the-bridge-series-the-bay-bridge-shirt",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem.\nFeatures: Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem. Pairs in The Bridge Series with the Bay Bridge Shorts (sg-001 daytime SF-Oakland Bay Bridge palette). NOT a tank. NOT a long-sleeve tee. NOT a hoodie. NOT a polo. NOT the Stay Golden Shirt (that's sg-002 — purple rose-cluster decoration, separate SKU). **The Bay Bridge colorway uses a BLUE/CYAN rose-cluster on the chest** (matching the daytime-blue Bay Bridge palette).\nColor: White\nAvailable sizes: S | M | L | XL | 2XL",
    "branding_block": "Exact SKU artwork and front placement are bound in `logo-registry.json::sku_logos::sg-005::render_reference` to `assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg`. The existing physical-authority record and its current file hash agree. Use the complete garment pixels for artwork, position and relative scale; no generic cluster recoloring.\n\n### Front\n- **front-chest-center** (position and relative dimensions exactly as shown on the bound physical garment): Embroidered blue rose composition containing photographic Bay Bridge daytime imagery inside its petals, with silver/grey stems and vines and a blue/cyan cloud with dark lower lobes. Preserve the complete composition, including bridge detail within the blooms; this is not a plain recolored rose. **Technique:** embroidered. **Color:** exact blue bridge-filled artwork on white.\n\n### Back\n- **back-neck** (small, ~1.5in wide, top-center just below the collar): The SR monogram embroidered onto the jersey in **dark grey / black thread** (NOT canonical gold). **Technique:** embroidered. **Color:** dark grey / black thread on white.\n\n### Sleeves / Collar / Hem / Other\n- **collar** (~0.5in wide ribbed crew neck): Standard ribbed crew-neck collar. **Technique:** stitched. **Color:** white.\n- **left-sleeve** (short sleeve, plain hem): Short set-in sleeve. **Technique:** stitched. **Color:** white.\n- **right-sleeve** (short sleeve, plain hem): Mirror of left. **Technique:** stitched. **Color:** white.\n- **hem** (straight even bottom hem): Plain stitched bottom hem. **Technique:** stitched. **Color:** white.\n- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO purple rose-cluster on the chest — this is the BLUE/CYAN Bay Bridge colorway. Purple rose-cluster belongs to sg-002 Stay Golden Shirt.\n- NO canonical multi-color rose-cluster — the exact Bay Bridge-filled composition is bound to this SKU.\n- NO canonical greyscale rose-cluster — recolored to blue.\n- NO all-over bridge print on the shirt. Photographic bridge imagery IS required inside the registered rose petals; the surrounding shirt body remains solid white.\n- NO chest text or wordmark on the front body fabric — only the chest rose.\n- NO logo on the back body — only the small back-neck SR monogram.\n- NO Authentic Collection patch.\n- NO Love Hurts branding.\n- NO sublimated all-over body pattern — body is solid white.\n- NO contrast color sleeve cuffs or hem.\n- NO embossed/debossed decoration.\n- NO V-neck or henley placket.",
    "scene_pose": "Front view straight-on showing the center-chest Bay Bridge-filled rose composition on the white tee, the crew neck, and the short sleeves. For the back: back view straight-on showing the small SR monogram at the back-neck.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg",
    "extra_logos": [
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-005-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/bridge-bay-bridge-shirt-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-005-bay-bridge-shirt.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg",
    "back": null,
    "reference": "assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_chest_center",
        "technique": "embroidered",
        "colorway": "blue_cyan",
        "notes": "Exact Bay Bridge daytime photographic imagery is stitched inside the rose petals. Match the blue palette, stems, cloud and center-chest proportions in the bound physical garment source. No generic recoloring or small left-chest substitution."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg",
    "reference_kind": "garment",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Indulge in the radiant prestige of the Stay Golden Tee, a wearable emblem of West Coast ambition. Imagine the golden light of a San Francisco sunset, the energy of Oakland pulsing beneath your feet—this tee captures that essence. At its heart, a meticulously crafted rose bursts forth, a vibrant testament to resilience and artistry. Its intricate petals, painted with rich hues and bold patterns, rise from darkness, symbolizing the journey from aspiration to achievement. More than design, it's a narrative etched in thread, reflecting authenticity and ambition. Woven from fine, soft cotton, this tee offers unparalleled comfort and drape. The Stay Golden Tee: a symbol of confidence and drive that defines the SkyyRose legacy. Embrace the golden standard; embrace your legacy.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Signature Collection: The Stay Golden Tee embodies West Coast ambition, featuring an opulent rose design symbolizing resilience and the pursuit of excellence.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Stay Golden Tee: Luxury streetwear embodying West Coast ambition and success. Featuring an iconic rose design. Shop the Signature Collection now.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Step into your golden era with the SkyyRose Stay Golden Tee. ✨ It's more than apparel; it's a symbol of unwavering ambition, resilience, and the radiant spirit of the West Coast. Our signature rose, meticulously crafted and bursting with color, embodies your journey, rooted in the Bay and reaching for the sky. Wear your legacy, feel the prestige, and Stay Golden. 💛\n\n#SkyyRose #SignatureCollection #LuxuryFashion #Couture #ElevatedStyle #BayAreaLuxury #FashionForward #SignatureStyle #ExclusiveFashion #Prestige #WestCoastVibes",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Golden hour glow up! ✨ The Stay Golden Tee: where Oakland grit meets couture prestige. Stay golden, SkyyRose fam! 🌹 #SkyyRose #SignatureCollection #BayAreaLuxury #StayGolden",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-005-product": "White SkyyRose Stay Golden Tee featuring a vibrant rose graphic with a thorny stem and dark cloud base."
  },
  "corrections": [
    {
      "text": "[ghost] doesn't look like my logo and logo needs to be centered with the bay bridge imagery embroidered into the rose",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:38.994698+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-006 — Mint & Lavender Hoodie

```json
{
  "sku": "sg-006",
  "name": "Mint & Lavender Hoodie",
  "collection": "signature",
  "catalog": {
    "sku": "sg-006",
    "name": "Mint & Lavender Hoodie",
    "price": "45",
    "collection": "signature",
    "description": "Sweet pastel vibes meet streetwear luxury. Mint and lavender colorblock with signature rose detail.",
    "badge": "",
    "image": "assets/images/products/sg-006-mint-lavender-hoodie.png",
    "front_model_image": "assets/images/products/sg-006-onmodel.webp",
    "back_image": "assets/images/products/mint-lavender-hoodie-back-model.webp",
    "back_model_image": "assets/images/products/mint-lavender-hoodie-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Mint/Lavender",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Lavender rose logo centered on the front.",
    "render_output_slug": "mint-lavender-hoodie",
    "render_source_override": "sg-006-mint-lavender-hoodie.png",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "hoodie",
    "dossier_slug": "mint-lavender-hoodie",
    "engine_override": ""
  },
  "garment": {
    "color": "Mint/Lavender",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Mid-weight cotton-fleece fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "PULLOVER hoodie (kangaroo pouch pocket, NO zipper of any\nkind) — solid **mint green** body, hood, and sleeves, all one mint color.\n**Lavender/purple drawstrings** at the hood opening (the only contrast hardware).\nLarge lavender rose-cluster graphic centered on the chest. Ribbed cuffs and\nbottom hem in self-color mint. Mid-weight cotton-fleece fabric. Pairs with the\nMint & Lavender Sweatpants (sg-014) as a matching set. **Sold as the hoodie SKU\nonly — the matching sweatpants are sg-014, separate SKU.** NOT a zip-up. NOT a\ncrewneck (that's sg-013 Mint & Lavender Crewneck — separate SKU). NOT a\nwindbreaker (the white-body rainbow-chevron zip-up set is sg-015 — a completely\ndifferent product).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-006",
    "name": "Mint & Lavender Hoodie",
    "collection": "signature",
    "slug": "mint-lavender-hoodie",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Mid-weight cotton-fleece fabric.\nFeatures: PULLOVER hoodie (kangaroo pouch pocket, NO zipper of any\nkind) — solid **mint green** body, hood, and sleeves, all one mint color.\n**Lavender/purple drawstrings** at the hood opening (the only contrast hardware).\nLarge lavender rose-cluster graphic centered on the chest. Ribbed cuffs and\nbottom hem in self-color mint. Mid-weight cotton-fleece fabric. Pairs with the\nMint & Lavender Sweatpants (sg-014) as a matching set. **Sold as the hoodie SKU\nonly — the matching sweatpants are sg-014, separate SKU.** NOT a zip-up. NOT a\ncrewneck (that's sg-013 Mint & Lavender Crewneck — separate SKU). NOT a\nwindbreaker (the white-body rainbow-chevron zip-up set is sg-015 — a completely\ndifferent product).\nColor: Mint/Lavender\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical reference:\n> - Rose-cluster composition (three roses, thorny vines, cloud at base):\n>   `data/brand-logos/three-rose-cluster.md` — rendered here in the\n>   **lavender colorway**: lavender/purple rose blooms with white highlights,\n>   grey-green thorny stems and leaves, grey-and-white cloud at the base.\n> - Product techflat (front):\n>   `assets/products/techflats/split/signature/sg-mint-lav-hoodie-front.jpeg`\n>\n> ### COLORWAY — Mint & Lavender\n>\n> \"Mint & Lavender\" means exactly what the techflat shows: a solid **mint\n> green** garment body with the **lavender** rose-cluster as the chest art.\n> No stripes, no chevrons, no color-blocking — the colorway lives in the\n> mint body + lavender artwork pairing.\n\n### Front\n- **front-center-chest** (large, ~10in tall, centered on the chest between the hood opening and the kangaroo pocket): The canonical rose-cluster composition in the lavender colorway — lavender/purple roses with white petal highlights, grey-green thorny stems and leaves, rising from a grey-and-white cloud at the base. **Technique:** printed. **Color:** lavender + white + grey-green + grey on mint.\n- **front-body** (everything outside the chest art): Solid **mint green** cotton-fleece. **Technique:** stitched. **Color:** mint green.\n- **front-kangaroo-pocket** (lower front, full-width pouch pocket): Standard kangaroo pouch, self-color mint, no decoration. **Technique:** stitched. **Color:** mint green.\n- **hood-drawstrings** (two cords at the hood opening): **Lavender/purple** drawstrings with metal or self-tipped ends. **Technique:** stitched. **Color:** lavender/purple.\n\n### Back\n- **back-body** (entire back field, hood seam to hem): Solid **mint green**, no decoration of any kind. **Technique:** stitched. **Color:** mint green.\n\n### Sleeves / Hood / Hem / Other\n- **hood**: Solid mint green inside and out, matching the body. **Technique:** stitched. **Color:** mint green.\n- **left-sleeve / right-sleeve** (long sleeves): Solid mint green, no decoration. **Technique:** stitched. **Color:** mint green.\n- **cuffs** (ribbed, at each wrist): Self-color mint ribbing. **Technique:** stitched. **Color:** mint green.\n- **hem** (ribbed bottom band): Self-color mint ribbing. **Technique:** stitched. **Color:** mint green.\n- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO zipper anywhere — this is a PULLOVER with a kangaroo pocket. NOT a zip-up.\n- NO white body — the body is SOLID MINT GREEN.\n- NO rainbow chevron, NO multi-color stripe bands, NO color-block panels — that\n  is the sg-015 windbreaker set, a different product.\n- NO pink hood — hood is mint, same as the body.\n- NO slash hand pockets, NO pink piping — single kangaroo pouch only.\n- NO decoration on the back — back is blank mint (no SR monogram, no art).\n- NO decoration on the sleeves, cuffs, hood, or hem.\n- NO red Love Hurts roses — the rose-cluster here is LAVENDER (Signature collection).\n- NO greyscale Black Rose treatment — roses are lavender/purple, not silver/grey.\n- NO Authentic Collection patch.\n- NO Bridge Series photo print.\n- NO chest text or wordmark — the chest carries artwork only.\n- NO embossed/debossed decoration.",
    "scene_pose": "Front view straight-on showing the solid mint body, lavender\n  drawstrings, centered lavender rose-cluster chest art, and kangaroo pocket.\n  Three-quarter view shows the clean mint sleeves. For the back: back view\n  straight-on showing the blank mint back panel and hood.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/techflats/split/signature/sg-mint-lav-hoodie-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-006-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/mint-lavender-hoodie-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-006-mint-lavender-hoodie.png",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/mint-lavender-hoodie-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "assets/products/techflats/split/signature/sg-mint-lav-hoodie-front.jpeg",
    "back": null,
    "reference": "wordpress-theme/skyyrose-flagship/assets/images/products/sg-006-mint-lavender-hoodie.png"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_center",
        "technique": "embroidered",
        "colorway": "lavender"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/logos/three-rose-cluster-lavender.png",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Envelop yourself in the effortless luxury that defines West Coast prestige. The Mint & Lavender Hoodie, a standout piece from the SkyyRose SIGNATURE Collection, redefines comfort with an unmistakable air of Bay Area sophistication. Imagine a serene California morning – that's the feeling embodied in the hoodie's refreshing mint hue. An exquisite lavender floral graphic, a dynamic burst of purple artfully set atop a subtle, ethereal cloud, adds an artistic touch that speaks volumes.\n\nMeticulously crafted from a premium, incredibly soft-touch fabric, every detail is considered. Note the perfectly structured hood, the adjustable drawstrings, the cozy kangaroo pocket, and the meticulously ribbed cuffs and hem – all designed for an elevated fit and enduring style. A discreet, signature detail on the cuff subtly marks this garment as an authentic SkyyRose creation.\n\nMore than just a hoodie, this is a statement of discerning taste, a piece of wearable art that embodies the golden soul of the Bay Area. Elevate your everyday.\n\nAvailable in sizes S, M, L, XL, 2XL, and 3XL. Claim your piece of the SkyyRose legacy.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Experience elevated comfort with the Mint & Lavender Hoodie from the SkyyRose SIGNATURE Collection, where a refreshing mint base meets opulent lavender artistry.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Mint & Lavender Hoodie: Experience Bay Area luxury with this SIGNATURE piece. Premium comfort meets lavender floral artistry. Elevate your wardrobe today.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Step into unparalleled comfort and style. ✨ The Mint & Lavender Hoodie, a standout from our SIGNATURE Collection, embodies elevated Bay Area luxury. Crafted with meticulous detail, its refreshing mint hue and captivating lavender floral art define West Coast premium design. Feel the legacy; wear the confidence. This piece is pure gold. 💫 Own your signature style today.\n\n#SkyyRose #SignatureCollection #LuxuryFashion #Couture #ElevatedStyle #BayAreaLuxury #FashionForward #SignatureStyle #ExclusiveFashion #Prestige #MintAndLavender #HoodieSeason",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "West Coast chill meets couture thrill! ☁️ The Mint & Lavender Hoodie from SkyyRose's Signature Collection. Your new everyday flex. 😉 #SkyyRose #LuxuryFashion #BayArea",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-006-product-2": "Mint green crewneck and sweatpants set with a lavender floral explosion graphic on chest and pocket. Product: Mint & Lavender Hoodie.",
    "sg-006-product-3": "SkyyRose \"Mint & Lavender Hoodie\" set: mint green sweatshirt and matching sweatpants with a lavender graphic.",
    "sg-006-product": "SkyyRose Mint & Lavender Hoodie, SIGNATURE Collection, featuring a lavender floral design and a ladybug cuff tag."
  },
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:39.000103+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-007 — The Signature Beanie

```json
{
  "sku": "sg-007",
  "name": "The Signature Beanie",
  "collection": "signature",
  "catalog": {
    "sku": "sg-007",
    "name": "The Signature Beanie",
    "price": "25",
    "collection": "signature",
    "description": "Classic fitted beanie with embroidered signature rose. West Coast luxury meets everyday warmth. Rose-logo color variants: red, grey, black, purple.",
    "badge": "",
    "image": "assets/images/products/sg-007-signature-beanie.png",
    "front_model_image": "assets/images/products/sg-007-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/signature-beanie-back-model.webp",
    "sizes": "One Size",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Small silicone patch logo positioned slightly off-center to the left. Logo rose color variants: red, grey, black, purple.",
    "render_output_slug": "signature-beanie",
    "render_source_override": "sg-007-signature-beanie.png",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "1",
    "garment_type_lock": "",
    "dossier_slug": "the-signature-beanie",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "One Size"
    ],
    "fit": {
      "specification": "Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit.",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit. Mid-weight knit fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit. NOT a hat with a brim. NOT a baseball cap. NOT a pom-pom beanie. NOT a slouchy beanie. NOT a fitted-cap. **Sold across 4 decoration / colorway variants** that share the same base beanie but differ in the small rose graphic embroidered on the front face of the cuff. Mid-weight knit fabric.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-007",
    "name": "The Signature Beanie",
    "collection": "signature",
    "slug": "the-signature-beanie",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit. Mid-weight knit fabric.\nFit: Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit.\nFeatures: Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit. NOT a hat with a brim. NOT a baseball cap. NOT a pom-pom beanie. NOT a slouchy beanie. NOT a fitted-cap. **Sold across 4 decoration / colorway variants** that share the same base beanie but differ in the small rose graphic embroidered on the front face of the cuff. Mid-weight knit fabric.\nColor: Black\nAvailable sizes: One Size",
    "branding_block": "Source reconciliation pending: see `logo-registry.json::gaps::signature-beanie-variant-binding`. Preserve the specific product/variant artwork; the existing text below must not be treated as proof that conflicting references have been resolved.\n\n> Logo art canonical references:\n> - Black Rose three-rose-cluster (greyscale): `data/brand-logos/three-rose-cluster.md`\n> - Red Roses Cloud Cluster (LH multi-color):  `data/brand-logos/red-roses-cloud-cluster.md`\n> - Product techflat (4 variants visible):     `assets/products/references/sg-007-techflat.jpeg`\n>\n> ### COLORWAY / DECORATION VARIANTS\n>\n> All 4 variants share the same **black ribbed knit beanie** base. The only\n> difference is the rose graphic embroidered on the front face of the cuff:\n>\n> - **Variant 1 — Purple/Violet rose-cluster** (small, ~1.5in tall): a\n>   tonal purple-and-violet rendering of the canonical rose-cluster (three\n>   roses + cloud at base + thorny vines), recolored to a purple-on-black\n>   palette. **Color:** purple-violet on black.\n> - **Variant 2 — White-outline rose-cluster** (small, ~1.5in tall): a\n>   line-art white-thread version of the canonical rose-cluster — outlines\n>   only, no fill. **Color:** white thread on black.\n> - **Variant 3 — Small single red rose with cloud** (small, ~1in tall):\n>   a single canonical red rose bloom (with thorny green stem and a small\n>   white-and-blue cloud at the base) — minimal scale. **Color:**\n>   canonical Love Hurts red + green + white-and-blue.\n> - **Variant 4 — Red rose-cluster with cloud** (medium, ~2in tall):\n>   the full canonical Red Roses Cloud Cluster (multiple red roses + thorny\n>   green vines + white-and-blue cloud) — the larger Love Hurts canonical\n>   composition. **Color:** canonical multi-color (red + green + white +\n>   blue).\n>\n> Render the requested variant ONLY — do not place all four roses on a\n> single beanie.\n\n### Front\n- **front-cuff** (small, ~1.5–2in tall, centered on the front face of the cuff fold): The selected variant's rose decoration (Variant 1, 2, 3, or 4 per the COLORWAY/DECORATION VARIANTS block above) embroidered into the cuff face. **Technique:** embroidered. **Color:** per selected variant.\n\n### Back\n- (Clean back — no decoration on the rear-cuff face or rear-crown.)\n\n### Sleeves / Hood / Hem / Other\n- **cuff** (~2.5–3in tall folded): Standard ribbed-knit cuff, folded up once. **Technique:** stitched. **Color:** black.\n- **crown**: Rounded knit crown, no decoration. **Technique:** stitched. **Color:** black.\n- **inside-cuff** (~1in × 0.5in interior tag): Branded woven size tag (universal SkyyRose product rule, scaled for accessory). **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO embroidery on the back / rear-cuff — the rose decoration is on the FRONT cuff face only.\n- NO multi-color rose on Variants 1 or 2 — Variant 1 is purple-monochrome, Variant 2 is white-outline-only.\n- NO mixing of variants — render only ONE rose decoration (the selected variant).\n- NO contrast color on the beanie body — the body is solid black across all 4 variants.\n- NO pom-pom on the crown.\n- NO brim (this is a beanie, not a fitted cap or trucker hat).\n- NO slouchy / oversize crown — the beanie is a snug fitted-knit silhouette.\n- NO Authentic Collection patch on a beanie.\n- NO SR monogram on the beanie (the SR mark is a back-neck embroidery on jerseys, not on accessories).\n- NO printed graphics — branding is embroidered, not printed.\n- NO contrast piping along the cuff edge.\n- NO tag visible on the exterior (interior size-tag only).",
    "scene_pose": "Front view straight-on showing the cuff with the selected variant's rose decoration. Optional: 3/4 view showing the snug knit fit and the cuff fold-line.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [
      "data/brand-logos/red-roses-cloud-cluster.md"
    ],
    "reference_image": "assets/products/references/sg-007-techflat.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-007-signature-beanie.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/signature-beanie-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-007-signature-beanie.png",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/signature/sg-beanie-purple.jpeg",
    "back": null,
    "reference": "assets/products/references/sg-007-techflat.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "slightly_off_left",
        "technique": "silicone_patch",
        "notes": "Small silicone patch. Rose cluster colorway follows the beanie variant color."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/logos/three-rose-cluster-greyscale.png",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Indulge in the refined embrace of the SkyyRose Signature Beanie, where unparalleled warmth meets the commanding essence of couture. More than a mere shield against the chill, this beanie is a statement of discerning taste, an echo of the West Coast's opulent spirit. Imagine yourself amidst the vibrant pulse of the Bay Area, or ascending to the heights of global influence – this piece effortlessly complements every facet of your journey. Woven from the finest, cloud-soft yarns, it offers a bespoke fit designed for supreme comfort and enduring style. The iconic SkyyRose emblem, meticulously embroidered, serves as a distinguished hallmark of our legacy and a vibrant tribute to California's golden energy. Elevate your everyday ensemble with a touch of prestige streetwear, a testament to enduring quality and unparalleled craftsmanship. Available in rich Red, regal Purple, and timeless Black, each colorway is carefully curated to resonate with your individual expression. The Signature Beanie is more than an accessory; it is a symbol of elevated style, a whisper of luxury, and a bold declaration of your SkyyRose allegiance. Command attention. Radiate confidence. Embrace the signature. Where California dreaming meets unparalleled craftsmanship.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Elevate your everyday with the SkyyRose Signature Beanie: a luxurious knit, bespoke comfort, and a bold statement of West Coast prestige.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Signature Beanie: Experience elevated style with this luxury knit beanie. Featuring the iconic rose emblem. Available in Red, Purple, and Black. Shop now.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Command attention with the SkyyRose Signature Beanie. More than just a knit, it's a statement of refined taste and West Coast prestige. Adorned with our iconic rose emblem and crafted for unparalleled comfort, this beanie elevates your everyday style.\n\n#SkyyRose #SignatureCollection #LuxuryFashion #Couture #ElevatedStyle #BayAreaLuxury #FashionForward #SignatureStyle #ExclusiveFashion #Prestige #Beanie #Knitwear",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "Cali cool meets couture comfort! 😎 The SkyyRose Signature Beanie is that luxe layer you need. #SkyyRose #SignatureCollection #BayAreaLuxury #Beanie",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-007-product-2": "The Signature Beanie, a dark gray knit beanie, features a patch with purple roses, green leaves, and white clouds.",
    "sg-007-product-3": "The Signature Beanie: Black knit beanie with a light blue patch featuring a cherub holding a rose.",
    "sg-007-product": "SkyyRose Signature Beanie: Dark green knit beanie with a prominent red rose patch on the folded brim."
  },
  "corrections": [
    {
      "text": "[ghost] logo Is a patch not directly on beanie",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[on-model] logo Is a patch not directly on beanie",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:39.005420+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-009 — The Sherpa Jacket

```json
{
  "sku": "sg-009",
  "name": "The Sherpa Jacket",
  "collection": "signature",
  "catalog": {
    "sku": "sg-009",
    "name": "The Sherpa Jacket",
    "price": "80",
    "collection": "signature",
    "description": "Plush sherpa warmth in the SkyyRose signature colorway. Luxury outerwear for the West Coast. Body lined with white sherpa.",
    "badge": "",
    "image": "assets/images/products/sg-009-sherpa-jacket.jpeg",
    "front_model_image": "assets/images/products/sg-009-onmodel.webp",
    "back_image": "assets/images/products/the-sherpa-jacket-back-model.webp",
    "back_model_image": "assets/images/products/signature-sherpa-jacket-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Black",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Red rose logo on the front. Body lined with white sherpa.",
    "render_output_slug": "signature-sherpa-jacket",
    "render_source_override": "sg-009-sherpa-jacket.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "jacket",
    "dossier_slug": "the-sherpa-jacket",
    "engine_override": ""
  },
  "garment": {
    "color": "Black",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Sherpa-lined zip-front jacket — solid **black** nylon-windbreaker-style exterior shell with full-length center-front zipper closure and a **white / cream sherpa fleece interior lining** that wraps the entire interior body, sleeves, and stand-up collar. Visible white-sherpa contrast at the front placket, sleeve cuffs, hem, and stand-up collar opening when the jacket is worn open. NOT a sherpa-exterior coat (the sherpa is the INTERIOR lining; the exterior is smooth black nylon-style fabric).",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Sherpa-lined zip-front jacket — solid **black** nylon-windbreaker-style exterior shell with full-length center-front zipper closure and a **white / cream sherpa fleece interior lining** that wraps the entire interior body, sleeves, and stand-up collar. Visible white-sherpa contrast at the front placket, sleeve cuffs, hem, and stand-up collar opening when the jacket is worn open. Two patch hand pockets at the lower body. Stand-up funnel-neck collar (NOT a hood). Small interior brand woven label at the back-neck. Mid-weight to outerwear weight. NOT a pullover. NOT a hoodie (no hood). NOT a sherpa-exterior coat (the sherpa is the INTERIOR lining; the exterior is smooth black nylon-style fabric). NOT a fully-reversible jacket (the rose-cluster embroidery is exterior-only, so it cannot be worn inside-out as a finished look). NOT a windbreaker set (this is the jacket alone, no matching pants).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-009",
    "name": "The Sherpa Jacket",
    "collection": "signature",
    "slug": "the-sherpa-jacket",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Sherpa-lined zip-front jacket — solid **black** nylon-windbreaker-style exterior shell with full-length center-front zipper closure and a **white / cream sherpa fleece interior lining** that wraps the entire interior body, sleeves, and stand-up collar. Visible white-sherpa contrast at the front placket, sleeve cuffs, hem, and stand-up collar opening when the jacket is worn open. NOT a sherpa-exterior coat (the sherpa is the INTERIOR lining; the exterior is smooth black nylon-style fabric).\nFeatures: Sherpa-lined zip-front jacket — solid **black** nylon-windbreaker-style exterior shell with full-length center-front zipper closure and a **white / cream sherpa fleece interior lining** that wraps the entire interior body, sleeves, and stand-up collar. Visible white-sherpa contrast at the front placket, sleeve cuffs, hem, and stand-up collar opening when the jacket is worn open. Two patch hand pockets at the lower body. Stand-up funnel-neck collar (NOT a hood). Small interior brand woven label at the back-neck. Mid-weight to outerwear weight. NOT a pullover. NOT a hoodie (no hood). NOT a sherpa-exterior coat (the sherpa is the INTERIOR lining; the exterior is smooth black nylon-style fabric). NOT a fully-reversible jacket (the rose-cluster embroidery is exterior-only, so it cannot be worn inside-out as a finished look). NOT a windbreaker set (this is the jacket alone, no matching pants).\nColor: Black\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Red Roses Cloud Cluster (left-chest exterior embroidery): `data/brand-logos/red-roses-cloud-cluster.md`\n> - SR monogram / brand woven label (interior back-neck): `data/brand-logos/sr-monogram.md`\n> - Product reference exterior front (rose-cluster placement visible):\n>   `assets/products/references/sg-009-sherpa-front.jpeg`\n> - Product reference interior detail (sherpa lining + brand label visible):\n>   `assets/products/references/sg-009-sherpa-interior.jpeg`\n\n### Front\n- **front-body** (entire black exterior field, between the stand-up collar and the bottom hem): Solid **black** nylon-style smooth shell fabric. **Technique:** stitched. **Color:** black.\n- **front-left-chest** (~3in tall, on wearer's left chest, just right of the center-front zipper, ~4in below the stand-up collar): Canonical **Red Roses Cloud Cluster** logo embroidered onto the black exterior — three red roses with kelly-green stems and thorny vines, wrapping a small white-and-light-blue cumulus cloud at the base. Full-color thread embroidery. **Technique:** embroidered. **Color:** red petals + dark-red shading + kelly-green stems + white cloud + pale-blue cloud-shading thread on black.\n- **front-zipper** (vertical center-front, full body length from stand-up collar opening to bottom hem): Standard center-front zipper running the full length of the body. **Technique:** patch. **Color:** body-tone hardware (black or near-black teeth).\n- **front-left-pocket** (patch hand pocket at the lower-left body, ~6in × 5in, sewn-on patch construction with horizontal welt opening): Patch hand pocket. **Technique:** stitched. **Color:** black, matching the body.\n- **front-right-pocket** (patch hand pocket at the lower-right body, mirror of left): Patch hand pocket. **Technique:** stitched. **Color:** black, matching the body.\n\n### Back\n- **back-body** (entire black exterior back field, between the stand-up collar seam and the bottom hem): Solid **black** nylon-style shell, no decoration. **Technique:** stitched. **Color:** black.\n- **back-collar-inside** (small, ~1.5in × 0.5in interior tag at the back-neck, visible only when the collar is folded open): Branded **SR monogram** woven label — small rectangular woven brand label carrying the canonical SR cursive monogram. **Technique:** woven-label. **Color:** brand-label palette (black ground with white SR script, or matching brand label specification).\n\n### Sleeves / Collar / Hem / Other\n- **left-sleeve** (long sleeve, ~24in from shoulder seam to cuff): Solid **black** nylon-style shell exterior with white sherpa fleece interior lining. **Technique:** stitched. **Color:** black exterior with white-sherpa interior.\n- **right-sleeve** (mirror of left): Solid black exterior with white sherpa interior lining. **Technique:** stitched. **Color:** black exterior with white-sherpa interior.\n- **left-cuff** (~2in cuff at wrist, finished black-exterior cuff with the white sherpa lining peeking at the cuff opening): Black ribbed or finished cuff. **Technique:** stitched. **Color:** black with white-sherpa interior peek.\n- **right-cuff** (mirror of left-cuff): Black finished cuff. **Technique:** stitched. **Color:** black with white-sherpa interior peek.\n- **collar** (~2.5in tall stand-up funnel-neck collar around the entire neck opening): Black nylon-style exterior with white sherpa interior lining. **Technique:** stitched. **Color:** black exterior with white-sherpa interior.\n- **hem** (~1in finished bottom hem along the entire bottom edge of the body): Clean finished hem on the black exterior with the white sherpa interior visible from below when the jacket is open. **Technique:** stitched. **Color:** black with white-sherpa interior.\n- **interior-lining** (full-body interior lining covering the entire inside surface of the body and sleeves): Plush **white / cream sherpa fleece** lining throughout the interior. **Technique:** stitched. **Color:** white / cream sherpa fleece.",
    "negative_block": "- NO hood — this is a STAND-UP COLLAR jacket, not a hoodie. There is no hood, no drawstring, no hood-lining seam.\n- NO contrast-color exterior panels — the exterior is **entirely black** front, back, and sleeves. No white panels, no color-blocking, no rainbow chevron, no sublimated print.\n- NO decoration on the back — the back exterior is plain solid black. The only back element is the small interior brand woven label at the back-neck.\n- NO sherpa visible on the exterior — the sherpa is **interior lining only**. The exterior is smooth black nylon-style fabric. Do NOT render a sherpa-exterior coat.\n- NO chevron stripes, no rainbow color-block, no V-shape stripe panels.\n- NO Bridge Series photo print on the body.\n- NO Authentic Collection patch (no NFL / NBA / Hockey patch).\n- NO Black Rose greyscale rose-cluster — the chest rose is the canonical RED Roses Cloud Cluster (full-color red), not the greyscale variant.\n- NO chest text or wordmark — the only chest decoration is the embroidered rose-cluster.\n- NO additional pockets on the back, sleeves, or chest — only the two front patch hand pockets.\n- NO decorative buttons — closure is the center-front zipper only.\n- NO half-zip placket — the zipper runs the FULL body length from stand-up collar opening to bottom hem.\n- NO drawstring or cordlock at the hem or collar.\n- NO embossed or debossed decoration anywhere.\n- NO printed graphics — all decoration is embroidered or woven.\n- NO contrast piping anywhere (no pink piping, no colored piping).",
    "scene_pose": "Front view straight-on with the jacket worn closed showing the all-black exterior + stand-up collar + center-zipper + left-chest red-rose embroidery + two patch pockets. A second three-quarter angle worn open shows the white sherpa interior lining peeking at the front placket, cuffs, collar, and hem. Optional flat-lay laid open showing both the black exterior and the white sherpa interior side-by-side (matching the reference image).",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/red-roses-cloud-cluster.md",
    "extra_logos": [
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/sg-009-sherpa-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-009-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/signature-sherpa-jacket-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-009-sherpa-jacket.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/the-sherpa-jacket-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/sherpa-jacket-front.jpg",
    "back": null,
    "reference": "assets/products/references/sg-009-sherpa-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "red-roses-cloud-cluster",
        "position": "front_chest",
        "technique": "embroidered_or_applique",
        "notes": "Signature LOGO. Pairs with rose-gold-rose system-wide as the Signature mark set."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/red-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Envelop yourself in the commanding presence of the SkyyRose Signature Sherpa Jacket — where West Coast luxury meets unparalleled comfort. More than mere outerwear, this is a wearable monument to Bay Area prestige, meticulously crafted for those who move through the world with unwavering confidence. Imagine the jacket's sleek, premium black exterior as a canvas, showcasing our signature rose embroidery — a symbol of beauty, resilience, and the very essence of the SkyyRose legacy. The plush Sherpa interior cradles you in luxurious warmth, an indulgence perfect for navigating the Golden State's ever-changing seasons with effortless style. Each detail whispers of heritage, a seamless blend of timeless elegance and urban sophistication. The SkyyRose Signature Sherpa Jacket transcends its function; it becomes an extension of your most audacious self, a tangible piece of our legacy designed to elevate yours. Claim your piece of Bay Area gold today. Pre-order now and wear your legacy with unmistakable pride.",
      "source": "product-content.json",
      "enriched": true
    },
    "short_description": {
      "value": "Command attention in the SkyyRose Signature Sherpa Jacket, an opulent statement of West Coast luxury, defined by our signature rose embroidery. Pre-order your legacy.",
      "source": "product-content.json",
      "enriched": true
    },
    "seo_meta": {
      "value": "SkyyRose Signature Sherpa Jacket: Opulent West Coast outerwear featuring signature rose embroidery. Experience unparalleled Bay Area luxury. Pre-order your legacy today.",
      "source": "product-content.json",
      "enriched": true
    },
    "instagram": {
      "value": "Embrace the prestige. ✨ The SkyyRose Signature Sherpa Jacket isn't just outerwear; it's a declaration of West Coast luxury, meticulously crafted for those who command attention. Our signature rose embroidery blooms against the plush Sherpa, a symbol of beauty and undeniable Bay Area style. Pre-order your legacy today and wear your aspiration with pride. 🌹\n\n#SkyyRose #SignatureCollection #LuxuryFashion #Couture #ElevatedStyle #BayAreaLuxury #FashionForward #SignatureStyle #ExclusiveFashion #Prestige #SherpaJacket #WestCoastStyle",
      "source": "product-content.json",
      "enriched": true
    },
    "tiktok": {
      "value": "SkyyRose Signature Sherpa Jacket: Drop Alert! 🌹 West Coast luxury meets iconic rose embroidery. Elevate your style. Pre-order now! ✨ #SkyyRose #SignatureCollection #BayArea",
      "source": "product-content.json",
      "enriched": true
    }
  },
  "alt_text": {
    "sg-009-product-2": "The Sherpa Jacket, black with a cozy white sherpa lining and an embroidered red rose design.",
    "sg-009-product": "The Sherpa Jacket in black, featuring an embroidered design of two red roses on clouds."
  },
  "corrections": [
    {
      "text": "[ghost] sherpa lining doesn't show on bottom",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[on-model] sherpa lining doesn't show on bottom",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [],
  "provenance": {
    "generated": "2026-10-15T01:48:39.011071+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-011 — Original Label Tee (White)

```json
{
  "sku": "sg-011",
  "name": "Original Label Tee (White)",
  "collection": "signature",
  "catalog": {
    "sku": "sg-011",
    "name": "Original Label Tee (White)",
    "price": "30",
    "collection": "signature",
    "description": "The original SkyyRose label tee in clean white. Minimal design with signature branding.",
    "badge": "",
    "image": "assets/images/products/sg-011-original-label-tee-white.jpeg",
    "front_model_image": "assets/images/products/sg-011-onmodel.webp",
    "back_image": "assets/images/products/original-label-tee-white-back-model.webp",
    "back_model_image": "assets/images/products/original-label-tee-white-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Original SkyyRose label tee — minimal design with signature branding. Detailed placement spec TBD.",
    "render_output_slug": "original-label-tee-white",
    "render_source_override": "sg-011-original-label-tee-white.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shirt",
    "dossier_slug": "original-label-tee-white",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "White 100% cotton construction.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Classic crew-neck T-shirt, upper body only. NOT a crewneck sweatshirt, NOT a hoodie, NOT a jersey, NOT a long-sleeve. Short sleeves, ribbed crew neckline, no buttons, no hood, no kangaroo pocket. White 100% cotton construction.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-011",
    "name": "Original Label Tee (White)",
    "collection": "signature",
    "slug": "original-label-tee-white",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: White 100% cotton construction.\nFeatures: Classic crew-neck T-shirt, upper body only. NOT a crewneck sweatshirt, NOT a hoodie, NOT a jersey, NOT a long-sleeve. Short sleeves, ribbed crew neckline, no buttons, no hood, no kangaroo pocket. White 100% cotton construction.\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> **Founder-confirmed (2026-06-16): there are NO logos at all on the Original Label Tees.** No SR monogram, no chest mark, no sleeve badge, no print, no embroidery. The garment is a BLANK white tee whose only branding is the interior woven neck label (the \"original label\" the product is named for). A prior dossier revision invented a front-left-chest SR monogram — that mark does NOT exist on the product and must never be rendered.\n\n### Front\n- **front-body**: Completely blank white fabric. No monogram, no graphic, no print, no embroidery. Clean tee front.\n\n### Sleeves / Collar / Hem / Other\n- **collar-inside** (back neck, ~1.5in wide × ~0.5in tall): SkyyRose woven brand neck label, interior only — not visible from outside when worn. **Technique:** woven-label. **Color/Colorway:** white/silver label with woven brand text on white ground.\n- **sleeves**: Plain short sleeves — no badge, no patch, no print.",
    "negative_block": "- NO front-chest SR monogram — a prior dossier invented this; it does NOT exist. The front is BLANK.\n- NO sleeve badge, woven patch, or sewn logo of any kind — the source photo's apparent \"sleeve badge\" was a retail HANG TAG, not garment branding.\n- NO logo, graphic, monogram, or mark anywhere on the exterior — front, back, sleeves all blank white.\n- No back graphics of any kind — back is completely plain white fabric.\n- No sleeve printing, embroidery, or decoration of any kind.\n- No graphic fills, no printed rose illustrations, no screen-printed text anywhere on the body.\n- No embossed/debossed relief, no puff-print, heat-transfer, or vinyl decoration.\n- No visible label on the outside of the garment — only the inside back-collar woven neck label.\n- No hang tags rendered as garment branding.",
    "scene_pose": "Standing facing forward, slight three-quarter angle, relaxed arms at sides.",
    "scene_setting": "Clean white studio backdrop, soft diffused lighting on a pure blank white tee. Minimal shadow. No logo to highlight — the garment reads as a minimal blank white tee.",
    "logo_reference": "",
    "extra_logos": [],
    "reference_image": "",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-011-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/hub/sg-011-back.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-011-original-label-tee-white.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/original-label-tee-white-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/original-label-tee-white-front.webp",
    "back": null,
    "reference": "wordpress-theme/skyyrose-flagship/assets/images/products/sg-011-onmodel.webp"
  },
  "logos": {
    "placements": [],
    "decoration_sizing": {},
    "primary_reference": null,
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "The original SkyyRose label tee in clean white. Minimal design with signature branding.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "The original SkyyRose label tee in clean white. Minimal design with signature branding.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:39.015941+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-012 — Original Label Tee (Orchid)

```json
{
  "sku": "sg-012",
  "name": "Original Label Tee (Orchid)",
  "collection": "signature",
  "catalog": {
    "sku": "sg-012",
    "name": "Original Label Tee (Orchid)",
    "price": "30",
    "collection": "signature",
    "description": "The original SkyyRose label tee in rich orchid. Minimal design with signature branding.",
    "badge": "",
    "image": "assets/images/products/sg-012-original-label-tee-orchid.jpeg",
    "front_model_image": "assets/images/products/sg-012-onmodel.webp",
    "back_image": "assets/images/products/original-label-tee-orchid-back-model.webp",
    "back_model_image": "assets/images/products/original-label-tee-orchid-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Orchid",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Original SkyyRose label tee — minimal design with signature branding. Detailed placement spec TBD.",
    "render_output_slug": "original-label-tee-orchid",
    "render_source_override": "sg-012-original-label-tee-orchid.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "shirt",
    "dossier_slug": "original-label-tee-orchid",
    "engine_override": ""
  },
  "garment": {
    "color": "Orchid",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Orchid (soft purple-pink) 100% cotton construction.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Classic crew-neck T-shirt, upper body only. NOT a crewneck sweatshirt, NOT a hoodie, NOT a jersey, NOT a long-sleeve. Short sleeves, ribbed crew neckline, no buttons, no hood, no kangaroo pocket. Orchid (soft purple-pink) 100% cotton construction.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-012",
    "name": "Original Label Tee (Orchid)",
    "collection": "signature",
    "slug": "original-label-tee-orchid",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Orchid (soft purple-pink) 100% cotton construction.\nFeatures: Classic crew-neck T-shirt, upper body only. NOT a crewneck sweatshirt, NOT a hoodie, NOT a jersey, NOT a long-sleeve. Short sleeves, ribbed crew neckline, no buttons, no hood, no kangaroo pocket. Orchid (soft purple-pink) 100% cotton construction.\nColor: Orchid\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> **Founder-confirmed (2026-06-16): there are NO logos at all on the Original Label Tees.** No SR monogram, no chest mark, no sleeve badge, no print, no embroidery. The garment is a BLANK orchid tee whose only branding is the interior woven neck label (the \"original label\" the product is named for). A prior dossier revision invented a front-left-chest rose-gold SR monogram — that mark does NOT exist on the product and must never be rendered.\n\n### Front\n- **front-body**: Completely blank orchid fabric. No monogram, no graphic, no print, no embroidery. Clean tee front.\n\n### Sleeves / Collar / Hem / Other\n- **collar-inside** (back neck, ~1.5in wide × ~0.5in tall): SkyyRose woven brand neck label, interior only — not visible from outside when worn. **Technique:** woven-label. **Color/Colorway:** white/rose-gold label with woven brand text on orchid-compatible ground.\n- **sleeves**: Plain short sleeves — no badge, no patch, no print.",
    "negative_block": "- NO front-chest SR monogram — a prior dossier invented this (in rose-gold thread); it does NOT exist. The front is BLANK.\n- NO sleeve badge, woven patch, or sewn logo of any kind — the source photo's apparent \"sleeve badge\" was a retail HANG TAG, not garment branding.\n- NO logo, graphic, monogram, or mark anywhere on the exterior — front, back, sleeves all blank orchid.\n- No back graphics of any kind — back is completely plain orchid fabric.\n- No sleeve printing, embroidery, or decoration of any kind.\n- No graphic fills, no printed rose illustrations, no screen-printed text anywhere on the body.\n- No embossed/debossed relief, no puff-print, heat-transfer, or vinyl decoration.\n- No visible label on the outside of the garment — only the inside back-collar woven neck label.\n- No hang tags rendered as garment branding.",
    "scene_pose": "Standing facing forward, slight three-quarter angle, relaxed arms at sides.",
    "scene_setting": "Clean light studio backdrop, soft warm directional lighting on a pure blank orchid tee. Subtle gradient shadow at base. No logo to highlight — the garment reads as a minimal blank orchid tee.",
    "logo_reference": "",
    "extra_logos": [],
    "reference_image": "",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-012-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/original-label-tee-orchid-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-012-original-label-tee-orchid.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": {
      "path": "assets/images/products/original-label-tee-orchid-back-model.webp",
      "source_key": "back_image",
      "role_asset": true
    }
  },
  "render_sources": {
    "front": "wordpress-theme/skyyrose-flagship/assets/images/products/sg-012-original-label-tee-orchid.webp",
    "back": null,
    "reference": "wordpress-theme/skyyrose-flagship/assets/images/products/sg-012-onmodel.webp"
  },
  "logos": {
    "placements": [],
    "decoration_sizing": {},
    "primary_reference": null,
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "The original SkyyRose label tee in rich orchid. Minimal design with signature branding.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "The original SkyyRose label tee in rich orchid. Minimal design with signature branding.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [
    {
      "text": "[ghost] ADDED A LOGO",
      "authority": "FOUNDER_VERBATIM"
    },
    {
      "text": "[on-model] ADDED A LOGO",
      "authority": "FOUNDER_VERBATIM"
    }
  ],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:39.021018+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-013 — Mint & Lavender Crewneck

```json
{
  "sku": "sg-013",
  "name": "Mint & Lavender Crewneck",
  "collection": "signature",
  "catalog": {
    "sku": "sg-013",
    "name": "Mint & Lavender Crewneck",
    "price": "40",
    "collection": "signature",
    "description": "Pastel luxury in crewneck form. Mint and lavender colorblock with signature rose embroidery.",
    "badge": "",
    "image": "assets/images/products/sg-013-mint-lavender-crewneck.jpeg",
    "front_model_image": "assets/images/products/sg-013-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/mint-lavender-crewneck-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Mint/Lavender",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Lavender rose embroidered logo centered on the front. Small embroidered logo at the back of the neck.",
    "render_output_slug": "mint-lavender-crewneck",
    "render_source_override": "sg-013-mint-lavender-crewneck.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "crewneck",
    "dossier_slug": "mint-lavender-crewneck",
    "engine_override": ""
  },
  "garment": {
    "color": "Mint/Lavender",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Crew-neck pullover sweatshirt — solid **mint green / seafoam-green** body fabric throughout (front, back, sleeves) with **NO hood, NO zipper, NO color-blocking, NO chevron stripes, NO contrast panels**. Mid-weight cotton-fleece fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Crew-neck pullover sweatshirt — solid **mint green / seafoam-green** body fabric throughout (front, back, sleeves) with **NO hood, NO zipper, NO color-blocking, NO chevron stripes, NO contrast panels**. Long sleeves, ribbed crew-neck, ribbed cuffs at wrists, ribbed waistband at hem (all in matching mint). Mid-weight cotton-fleece fabric. NOT a hoodie (no hood — this is the no-hood sibling of the Mint & Lavender Hoodie sg-006). NOT a zip-up (pullover construction, no zipper). NOT a chevron-rainbow garment (the sg-006 hoodie has rainbow chevron stripes; this crewneck does NOT — it is a clean solid-mint body with embroidered rose decoration only). NOT a tee (this is a heavier sweatshirt with ribbed cuffs/waistband). The matching mint sweatpants visible in the techflat are sold as a separate companion piece — this dossier covers ONLY the crewneck top.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-013",
    "name": "Mint & Lavender Crewneck",
    "collection": "signature",
    "slug": "mint-lavender-crewneck",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Crew-neck pullover sweatshirt — solid **mint green / seafoam-green** body fabric throughout (front, back, sleeves) with **NO hood, NO zipper, NO color-blocking, NO chevron stripes, NO contrast panels**. Mid-weight cotton-fleece fabric.\nFeatures: Crew-neck pullover sweatshirt — solid **mint green / seafoam-green** body fabric throughout (front, back, sleeves) with **NO hood, NO zipper, NO color-blocking, NO chevron stripes, NO contrast panels**. Long sleeves, ribbed crew-neck, ribbed cuffs at wrists, ribbed waistband at hem (all in matching mint). Mid-weight cotton-fleece fabric. NOT a hoodie (no hood — this is the no-hood sibling of the Mint & Lavender Hoodie sg-006). NOT a zip-up (pullover construction, no zipper). NOT a chevron-rainbow garment (the sg-006 hoodie has rainbow chevron stripes; this crewneck does NOT — it is a clean solid-mint body with embroidered rose decoration only). NOT a tee (this is a heavier sweatshirt with ribbed cuffs/waistband). The matching mint sweatpants visible in the techflat are sold as a separate companion piece — this dossier covers ONLY the crewneck top.\nColor: Mint/Lavender\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical references:\n> - Canonical rose-cluster art (recolored to lavender / purple per COLORWAY OVERRIDE): `data/brand-logos/three-rose-cluster.md`\n> - Product reference techflat (crewneck top + matching pants visible together):\n>   `assets/products/references/sg-013-techflat-front.jpeg`\n>\n> ### COLORWAY OVERRIDE — Lavender / Purple rose-cluster on mint ground\n>\n> The rose-cluster on the front chest and back-yoke uses the **canonical\n> rose-cluster composition** (three roses, stems, thorny vines, cloud at\n> base) but RECOLORED to a **LAVENDER / PURPLE** palette:\n> - **Petals:** lavender / medium-purple / deep-purple gradient (NOT red,\n>   NOT greyscale).\n> - **Stems and leaves:** silver-grey or cool grey-purple (NOT kelly green).\n> - **Cloud at base:** white-and-light-grey (matching the canonical cloud).\n> - **Outlines:** dark purple-grey or black ink outlines.\n>\n> The catalog name \"Mint & Lavender\" describes BODY = mint green +\n> ROSE-CLUSTER ART = lavender. The body is solid mint; the lavender accent\n> is carried entirely by the rose-cluster embroidery on chest and back.\n\n### Front\n- **front-body** (entire mint field, between the crew-neck collar and the waistband): Solid **mint green / seafoam green** cotton-fleece body fabric. **Technique:** stitched. **Color:** mint green.\n- **front-center-chest** (~5–6in tall, ~4in wide, centered on the chest just below the crew-neck opening): Large **lavender / purple rose-cluster embroidery** — canonical three-rose-cluster composition recolored to a lavender / purple palette per the COLORWAY OVERRIDE above (lavender petals + silver-grey stems and leaves + white-and-light-grey cloud at base + dark purple-grey outlines). Significant chest-emblem scale, the visual focal point of the front. **Technique:** embroidered. **Color:** lavender + medium-purple + deep-purple thread + silver-grey stem thread + white cloud thread on mint ground.\n\n### Back\n- **back-yoke** (~2in tall, ~1.5in wide, top-center back just below the crew-neck collar seam): Small lavender / purple rose-cluster embroidery — same canonical composition as the front-center-chest emblem but at miniature scale (single small accent emblem). **Technique:** embroidered. **Color:** lavender + medium-purple + silver-grey + white thread on mint ground.\n- **back-body** (entire back field, between the crew-neck collar seam and the waistband): Solid **mint green**, no other decoration. **Technique:** stitched. **Color:** mint green.\n\n### Sleeves / Collar / Hem / Other\n- **left-sleeve** (long sleeve, ~24in from shoulder seam to cuff): Solid **mint green** cotton-fleece, no decoration. **Technique:** stitched. **Color:** mint green.\n- **right-sleeve** (mirror of left): Solid mint green, no decoration. **Technique:** stitched. **Color:** mint green.\n- **left-cuff** (~2in tall ribbed cuff at wrist): Solid mint-green ribbed cuff. **Technique:** stitched. **Color:** mint green.\n- **right-cuff** (mirror of left-cuff): Solid mint-green ribbed cuff. **Technique:** stitched. **Color:** mint green.\n- **collar** (~1in tall ribbed crew-neck collar around the entire neck opening): Solid mint-green ribbed crew-neck. **Technique:** stitched. **Color:** mint green.\n- **waistband** (~2in tall ribbed waistband at the bottom hem): Solid mint-green ribbed waistband wrapping front-and-back. **Technique:** stitched. **Color:** mint green.\n- **collar-inside** (~1.5in × 0.5in interior tag at the back-neck below the crew-neck seam): Branded woven size / composition label. **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO hood — this is a CREWNECK, not a hoodie. The Mint & Lavender Hoodie (sg-006) is the hooded sibling; this is the no-hood variant.\n- NO zipper — pullover construction, no closure.\n- NO chevron rainbow stripes — the rainbow-chevron garment is the sg-015 Windbreaker Set, a different product; this crewneck (and the sg-006 hoodie sibling) is solid mint. The body is solid mint front and back.\n- NO multi-color stripe band on cuffs, collar, or waistband — those are SOLID MINT to match the body (same self-color ribbing as the sg-006 hoodie).\n- NO white body — the body is solid MINT green (the sg-006 hoodie is solid mint too; the white-body garment is the sg-015 windbreaker set).\n- NO solid lavender body — body is MINT; lavender is the rose-cluster accent only.\n- NO red rose-cluster — the rose-cluster is RECOLORED LAVENDER / PURPLE, not the canonical red.\n- NO greyscale rose-cluster — the rose-cluster is RECOLORED LAVENDER / PURPLE, not the canonical Black Rose greyscale.\n- NO Black Rose three-rose-cluster as a chest emblem (in greyscale) — the chest rose is the lavender-recolored canonical.\n- NO Authentic Collection patch (no NFL / NBA / Hockey patch).\n- NO Bridge Series photo print on the body.\n- NO chest text or wordmark — the only chest decoration is the embroidered rose-cluster.\n- NO embossed or debossed decoration.\n- NO printed graphics — all decoration is embroidered.\n- NO additional pockets — this is a clean pullover crewneck with no pockets.\n- NO contrast piping anywhere.\n- NO sleeve-stripe tape or contrast sleeve seam.",
    "scene_pose": "Front view straight-on showing the mint body + large lavender rose-cluster on center chest + ribbed crew-neck collar + ribbed cuffs + ribbed waistband. Back view straight-on shows the small lavender rose-cluster at back-yoke and the otherwise plain mint back. Three-quarter view shows the clean side seams and silhouette.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/references/sg-013-techflat-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/sg-013-onmodel.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/mint-lavender-crewneck-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-013-mint-lavender-crewneck.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/signature/sg-mint-lav-crewneck-front.jpeg",
    "back": "assets/products/techflats/split/signature/sg-mint-lav-crewneck-back.jpeg",
    "reference": "assets/products/references/sg-013-techflat-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "front_center",
        "technique": "embroidered",
        "colorway": "lavender"
      },
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "back_of_neck",
        "technique": "embroidered",
        "colorway": "lavender",
        "size_inches": 1.5,
        "notes": "Small neck back embroidery."
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/black-roses-cloud-cluster.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Pastel luxury in crewneck form. Mint and lavender colorblock with signature rose embroidery.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Pastel luxury in crewneck form. Mint and lavender colorblock with signature rose embroidery.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:39.026581+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-014 — Mint & Lavender Sweatpants

```json
{
  "sku": "sg-014",
  "name": "Mint & Lavender Sweatpants",
  "collection": "signature",
  "catalog": {
    "sku": "sg-014",
    "name": "Mint & Lavender Sweatpants",
    "price": "45",
    "collection": "signature",
    "description": "Pastel luxury meets streetwear comfort. Mint and lavender sweatpants with signature rose detail.",
    "badge": "",
    "image": "assets/images/products/sg-014-mint-lavender-sweatpants.jpeg",
    "front_model_image": "assets/images/products/ghost/sg-014-ghost-front.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/mint-lavender-sweatpants-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "Mint/Lavender",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "0",
    "branding_spec": "Embroidered rose logo on the left thigh.",
    "render_output_slug": "mint-lavender-sweatpants",
    "render_source_override": "sg-014-mint-lavender-sweatpants.jpeg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "sweatpants",
    "dossier_slug": "mint-lavender-sweatpants",
    "engine_override": ""
  },
  "garment": {
    "color": "Mint/Lavender",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": "Athletic-cut sweatpants with a tapered jogger leg and\nribbed ankle cuffs — solid **mint green** body, front and back, all one mint\ncolor.",
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Mid-weight cotton-fleece fabric.",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Athletic-cut sweatpants with a tapered jogger leg and\nribbed ankle cuffs — solid **mint green** body, front and back, all one mint\ncolor. Small lavender rose-cluster logo on the **wearer's left thigh** (upper\nthigh, below the hip). Elasticated drawstring waistband, side-seam hand\npockets. Mid-weight cotton-fleece fabric. Pairs with the Mint & Lavender\nHoodie (sg-006) as a matching set. **Sold as the sweatpants SKU only — the\nmatching hoodie is sg-006, separate SKU.** NOT shorts. NOT track pants. NOT\nthe white chevron windbreaker-set pants (that's sg-015 — a completely\ndifferent product).",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-014",
    "name": "Mint & Lavender Sweatpants",
    "collection": "signature",
    "slug": "mint-lavender-sweatpants",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Mid-weight cotton-fleece fabric.\nFit: Athletic-cut sweatpants with a tapered jogger leg and\nribbed ankle cuffs — solid **mint green** body, front and back, all one mint\ncolor.\nFeatures: Athletic-cut sweatpants with a tapered jogger leg and\nribbed ankle cuffs — solid **mint green** body, front and back, all one mint\ncolor. Small lavender rose-cluster logo on the **wearer's left thigh** (upper\nthigh, below the hip). Elasticated drawstring waistband, side-seam hand\npockets. Mid-weight cotton-fleece fabric. Pairs with the Mint & Lavender\nHoodie (sg-006) as a matching set. **Sold as the sweatpants SKU only — the\nmatching hoodie is sg-006, separate SKU.** NOT shorts. NOT track pants. NOT\nthe white chevron windbreaker-set pants (that's sg-015 — a completely\ndifferent product).\nColor: Mint/Lavender\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "> Logo art canonical reference:\n> - Rose-cluster composition (three roses, thorny vines, cloud at base):\n>   `data/brand-logos/three-rose-cluster.md` — rendered here small, in the\n>   **lavender colorway**: lavender/purple blooms, grey-green stems and\n>   leaves, grey-and-white cloud at the base.\n> - Product techflats (front + back):\n>   `assets/products/techflats/split/signature/sg-mint-lav-sweats-front.jpeg`\n>   `assets/products/techflats/split/signature/sg-mint-lav-sweats-back.jpeg`\n>\n> ### COLORWAY — Mint & Lavender\n>\n> Same pairing as the sg-006 hoodie: solid **mint green** garment body with\n> the **lavender** rose-cluster as the only decoration. No stripes, no\n> chevrons, no color-blocking.\n\n### Front\n- **front-left-thigh** (small, ~3in tall, upper thigh on the wearer's LEFT leg, below the hip): The canonical rose-cluster composition in the lavender colorway, rendered small. Per the catalog: \"Embroidered rose logo on the left thigh.\" **Technique:** embroidered. **Color:** lavender + grey-green + grey thread on mint.\n- **front-body** (everything else, waistband to ankle cuffs, both legs): Solid **mint green** cotton-fleece. **Technique:** stitched. **Color:** mint green.\n- **waistband** (elasticated, with drawstring): Self-color mint elasticated waistband with a drawstring. **Technique:** stitched. **Color:** mint green.\n- **side-pockets** (one at each side seam): Side-seam hand pockets, self-color, no contrast piping. **Technique:** stitched. **Color:** mint green.\n\n### Back\n- **back-body** (entire back field, waistband to ankle cuffs): Solid **mint green**, no decoration of any kind — no pockets, no art, no labels. **Technique:** stitched. **Color:** mint green.\n\n### Sleeves / Hood / Hem / Other\n- **left-ankle-cuff / right-ankle-cuff** (ribbed, at each ankle): Self-color mint ribbing, tapered jogger finish. **Technique:** stitched. **Color:** mint green.\n- **inside-waistband** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO white body — the body is SOLID MINT GREEN, front and back.\n- NO rainbow chevron, NO multi-color stripe bands, NO color-block thigh panels —\n  that is the sg-015 windbreaker set, a different product.\n- NO rose at the center-front waistband — the rose-cluster sits on the\n  wearer's LEFT THIGH only, and nowhere else.\n- NO logo on the right thigh — left thigh only.\n- NO pink piping on the pockets — pockets are plain self-color side-seam pockets.\n- NO decoration on the back — back is blank mint.\n- NO back pockets.\n- NO red Love Hurts roses — the rose-cluster here is LAVENDER (Signature collection).\n- NO greyscale Black Rose treatment.\n- NO Authentic Collection patch.\n- NO Bridge Series photo print.\n- NO text or wordmark anywhere.\n- NO embossed/debossed decoration.\n- NO multi-color cuffs or waistband — all ribbing and elastication is self-color mint.",
    "scene_pose": "Front view straight-on showing the solid mint legs, drawstring\n  waistband, side-seam pockets, small lavender rose-cluster on the wearer's\n  left thigh, and ribbed ankle cuffs. For the back: back view straight-on\n  showing the clean blank mint back panels and ankle cuffs.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting\n  from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/three-rose-cluster.md",
    "extra_logos": [],
    "reference_image": "assets/products/techflats/split/signature/sg-mint-lav-sweats-front.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/hub/sg-014-front.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/mint-lavender-sweatpants-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-014-mint-lavender-sweatpants.jpeg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "front": "assets/products/techflats/split/signature/sg-mint-lav-sweats-front.jpeg",
    "back": "assets/products/techflats/split/signature/sg-mint-lav-sweats-back.jpeg",
    "reference": "assets/products/references/sg-014-techflat-front.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "black-roses-cloud-cluster",
        "position": "left_thigh",
        "technique": "embroidered",
        "colorway": "lavender"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "assets/products/logos/three-rose-cluster-lavender.png",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Pastel luxury meets streetwear comfort. Mint and lavender sweatpants with signature rose detail.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Pastel luxury meets streetwear comfort. Mint and lavender sweatpants with signature rose detail.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:39.031706+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```

## sg-015 — The Windbreaker Set

```json
{
  "sku": "sg-015",
  "name": "The Windbreaker Set",
  "collection": "signature",
  "catalog": {
    "sku": "sg-015",
    "name": "The Windbreaker Set",
    "price": "85",
    "collection": "signature",
    "description": "Signature luxury meets West Coast weather. A premium windbreaker set built for those who move through fog.",
    "badge": "Pre-Order",
    "image": "assets/images/products/sg-015-windbreaker-set.jpg",
    "front_model_image": "assets/images/products/sg-015-onmodel.webp",
    "back_image": "",
    "back_model_image": "assets/images/products/signature-windbreaker-set-back-model.webp",
    "sizes": "S|M|L|XL|2XL|3XL",
    "color": "White",
    "edition_size": "250",
    "published": "1",
    "is_preorder": "1",
    "branding_spec": "Premium windbreaker set (jacket + matching bottom). Signature first rose on wearer-left jacket chest and pants thigh; separate small rear SR below hood. See dossier and logo-registry.json for artwork and placement authority.",
    "render_output_slug": "signature-windbreaker-set",
    "render_source_override": "sg-015-windbreaker-set.jpg",
    "render_back_source_override": "",
    "render_is_tech_flat": "0",
    "render_is_accessory": "0",
    "garment_type_lock": "set",
    "dossier_slug": "the-windbreaker-set",
    "engine_override": ""
  },
  "garment": {
    "color": "White",
    "available_sizes": [
      "S",
      "M",
      "L",
      "XL",
      "2XL",
      "3XL"
    ],
    "fit": {
      "specification": null,
      "source": "founder product dossier"
    },
    "materials": {
      "specification": "Two-piece matching set sold as a single SKU — **lightweight nylon zip-front hooded windbreaker JACKET + matching nylon track-style PANTS**. Both pieces are constructed from smooth lightweight **nylon windbreaker fabric** (NOT cotton-fleece — this is the lighter water-resistant sibling of the Mint & Lavender Hoodie set). NOT cotton-fleece (this is the windbreaker variant, not the cousin sg-006 fleece hoodie + sg-014 fleece pants). NOT a fleece hoodie (different fabric, different weight, different construction).",
      "source": "founder product dossier"
    },
    "features": {
      "specification": "Two-piece matching set sold as a single SKU — **lightweight nylon zip-front hooded windbreaker JACKET + matching nylon track-style PANTS**. Both pieces are constructed from smooth lightweight **nylon windbreaker fabric** (NOT cotton-fleece — this is the lighter water-resistant sibling of the Mint & Lavender Hoodie set). Solid **white** body on both pieces with a **multi-color V-shape rainbow chevron color-block detail** at the upper chest (jacket) and at each upper-thigh (pants), **PINK contrast hood** on the jacket, **multi-color rainbow stripe bands** at the jacket cuffs / hem and the pants waistband / ankle cuffs. The jacket has a full-length center-front zipper. The pants have a white drawstring waistband and slash hand pockets. NOT cotton-fleece (this is the windbreaker variant, not the cousin sg-006 fleece hoodie + sg-014 fleece pants). NOT a single-piece SKU — this is sold as the matching JACKET + PANTS set together. NOT a fleece hoodie (different fabric, different weight, different construction). NOT solid black — both the current catalog and tech flat specify a WHITE body; preserve the pink hood and rainbow chevrons shown in the reference.",
      "source": "founder product dossier"
    },
    "sizing_references": {
      "decoration_sizing_pointer": null,
      "garment_size_chart": null,
      "source_rule": "Use founder specifications and actual product flatlays; no inferred garment measurements."
    }
  },
  "dossier": {
    "sku": "sg-015",
    "name": "The Windbreaker Set",
    "collection": "signature",
    "slug": "the-windbreaker-set",
    "garment_type_lock": "FOUNDER_CONFIRMED structured specifications (take precedence over legacy dossier prose):\nMaterials: Two-piece matching set sold as a single SKU — **lightweight nylon zip-front hooded windbreaker JACKET + matching nylon track-style PANTS**. Both pieces are constructed from smooth lightweight **nylon windbreaker fabric** (NOT cotton-fleece — this is the lighter water-resistant sibling of the Mint & Lavender Hoodie set). NOT cotton-fleece (this is the windbreaker variant, not the cousin sg-006 fleece hoodie + sg-014 fleece pants). NOT a fleece hoodie (different fabric, different weight, different construction).\nFeatures: Two-piece matching set sold as a single SKU — **lightweight nylon zip-front hooded windbreaker JACKET + matching nylon track-style PANTS**. Both pieces are constructed from smooth lightweight **nylon windbreaker fabric** (NOT cotton-fleece — this is the lighter water-resistant sibling of the Mint & Lavender Hoodie set). Solid **white** body on both pieces with a **multi-color V-shape rainbow chevron color-block detail** at the upper chest (jacket) and at each upper-thigh (pants), **PINK contrast hood** on the jacket, **multi-color rainbow stripe bands** at the jacket cuffs / hem and the pants waistband / ankle cuffs. The jacket has a full-length center-front zipper. The pants have a white drawstring waistband and slash hand pockets. NOT cotton-fleece (this is the windbreaker variant, not the cousin sg-006 fleece hoodie + sg-014 fleece pants). NOT a single-piece SKU — this is sold as the matching JACKET + PANTS set together. NOT a fleece hoodie (different fabric, different weight, different construction). NOT solid black — both the current catalog and tech flat specify a WHITE body; preserve the pink hood and rainbow chevrons shown in the reference.\nColor: White\nAvailable sizes: S | M | L | XL | 2XL | 3XL",
    "branding_block": "The first rose is the Signature collection lead, not a Windbreaker-only mark.\nThe founder confirmed this logo on the set and its relationship to the Signature\nfont. See [the shared identity reference](../brand-logos/rose-gold-rose.md).\nThis supersedes the earlier pink rose-cloud-cluster identification in this dossier.\n\n> Logo art canonical references:\n> - First rose: `data/brand-logos/rose-gold-rose.md`.\n> - Separate small rear SR: `data/brand-logos/sr-monogram.md`; the tech flat\n>   controls this garment's scale and dark appearance, not generic metallic styling.\n> - Product placement reference: `assets/products/references/sg-015-windbreaker-set-techflat.jpeg`.\n> - The drawing was visually inspected September 13, 2026. It shows the first\n>   rose on the wearer-left chest and wearer-left thigh, and a small SR centered\n>   below the hood at the back. It does not establish physical dimensions or\n>   manufacturing technique. Existing embroidery specifications are retained;\n>   they are not newly confirmed by the founder's logo statement.\n>\n> The white body, pink hood and rainbow panels are garment colors. They do not\n> authorize recoloring the first rose or substituting a pink rose cluster.\n> The catalog's current color is White; the former Black-color warning was stale.\n\n### Front\n- **front-body-jacket** (entire white jacket field, between the hood seam and the bottom hem): Solid **white** nylon windbreaker shell fabric. **Technique:** stitched. **Color:** white.\n- **front-chevron-jacket** (large V-shape, ~10in wide, fanning from the upper chest outward toward both shoulders and up to the hood opening): Multi-color **rainbow chevron stripe color-block panel** — alternating pink + green + lavender + yellow stripes (~5–8 stripes, each ~0.5–1in wide) arranged in a V/chevron formation that meets at the center-front upper-chest and fans up-and-out toward each shoulder. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow on white ground.\n- **front-left-chest-jacket** (wearer-left chest on the chevron panel, as shown in the tech flat): Canonical **first rose / rose-gold-rose** with stem and leaves. Preserve the registered artwork, orientation and relative scale. **Technique:** embroidered (existing registry specification; physical execution not established by the drawing). **Color:** rose gold.\n- **front-zipper-jacket** (vertical center-front, full body length from hood opening to waistband hem): Standard center-front zipper running the full length of the jacket body. **Technique:** patch. **Color:** body-tone hardware (white or near-white teeth).\n- **front-left-pocket-jacket** (vertical slash hand pocket at the lower-left jacket body, with **pink contrast piping** along the welt edge): Slash hand pocket. **Technique:** stitched. **Color:** white body with pink piping accent.\n- **front-right-pocket-jacket** (vertical slash hand pocket at the lower-right jacket body, mirror of left): Slash hand pocket with pink contrast piping. **Technique:** stitched. **Color:** white body with pink piping.\n- **front-body-pants** (entire white pants field, between the waistband and ankle cuffs): Solid **white** nylon windbreaker fabric. **Technique:** stitched. **Color:** white.\n- **front-thigh-chevron-pants** (V-shape, ~6–7in wide, on each upper-thigh / hip area, mirroring across the center-front): Multi-color V-shape **rainbow chevron stripe color-block panel** on each upper thigh — alternating pink + green + lavender + yellow stripes arranged in V/chevron pattern. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow on white ground.\n- **front-left-thigh-logo-pants** (wearer-left thigh over the chevron, as shown in the tech flat): Canonical **first rose / rose-gold-rose**, same identity as the chest mark. **Technique:** embroidered (existing registry specification). **Color:** rose gold. Preserve source-relative scale; no cloud-cluster substitution.\n- **front-left-pocket-pants** (vertical slash hand pocket on wearer's left thigh, with **pink contrast piping** along the welt edge): Slash hand pocket. **Technique:** stitched. **Color:** white body with pink piping.\n- **front-right-pocket-pants** (vertical slash hand pocket on wearer's right thigh, mirror of left): Slash hand pocket with pink contrast piping. **Technique:** stitched. **Color:** white body with pink piping.\n- **drawstring-pants** (~24in long, threaded through the pants waistband): White flat drawstring. **Technique:** stitched. **Color:** white.\n\n### Back\n- **back-neck-jacket** (centered immediately below the hood seam): Small **SR monogram**, scaled to the tech flat. Do not use the former unsupported 5–6in oversized specification. **Technique:** embroidered (retained specification). **Color:** dark appearance in the tech flat; do not infer metallic thread from the shared logo reference.\n- **back-body-jacket** (entire white back field, below the SR monogram and above the waistband): Solid **white**, no other decoration. **Technique:** stitched. **Color:** white.\n- **back-body-pants** (entire white pants back field, between waistband and ankle cuffs): Solid **white**, no decoration. **Technique:** stitched. **Color:** white.\n\n### Sleeves / Hood / Hem / Other\n- **hood-jacket** (full hood with drawstring, ~10in tall when laid flat): Solid **pink / light pink** contrast hood. **Technique:** stitched. **Color:** pink / light pink.\n- **hood-drawstring-jacket** (white flat drawstring threaded through the hood opening): White drawstring. **Technique:** stitched. **Color:** white.\n- **left-sleeve-jacket** (long nylon sleeve): Solid white nylon body with a small V-shape rainbow chevron stripe panel at the upper-cuff / forearm area mirroring the front-chevron color story. **Technique:** sublimated. **Color:** white body with chevron accent.\n- **right-sleeve-jacket** (mirror of left-sleeve): Solid white with chevron accent at the upper-cuff. **Technique:** sublimated. **Color:** white body with chevron accent.\n- **left-cuff-jacket** (~1.5in tall ribbed cuff at wrist): Multi-color rainbow stripe band (alternating pink + green + lavender + yellow stripes wrapping the cuff). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.\n- **right-cuff-jacket** (mirror of left-cuff-jacket): Multi-color rainbow stripe band. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.\n- **waistband-jacket** (~2in tall ribbed band at the jacket bottom hem): Multi-color rainbow stripe band wrapping the jacket front-and-back at the hem. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.\n- **waistband-pants** (~2in tall ribbed band at the pants top): Multi-color rainbow stripe band matching the jacket waistband (alternating pink + green + lavender + yellow stripes wrapping front-and-back). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.\n- **left-ankle-cuff-pants** (~1.5in tall ribbed band at the left ankle): Multi-color rainbow stripe band matching the jacket cuff treatment. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.\n- **right-ankle-cuff-pants** (mirror of left-ankle-cuff-pants): Multi-color rainbow stripe band. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.\n- **collar-inside-jacket** (~1.5in × 0.5in interior tag at the back-neck of the jacket): Branded woven size / composition label. **Technique:** woven-label. **Color:** brand-label palette.\n- **inside-waistband-pants** (~1.5in × 0.5in interior tag at the back-waistband of the pants): Branded woven size / composition label. **Technique:** woven-label. **Color:** brand-label palette.",
    "negative_block": "- NO cotton-fleece — this is **NYLON WINDBREAKER fabric** (lightweight, smooth, water-resistant). The sg-006 hoodie + sg-014 sweatpants set is the cotton-fleece cousin; this set is the NYLON WINDBREAKER variant.\n- NO solid black exterior — retain the White catalog color and the source tech flat’s white body, rainbow chevrons and pink hood.\n- NO solid hood matching body — the hood is **PINK** contrast against the white body.\n- NO single-color drawstring matching the hood — drawstring is WHITE on the pink hood.\n- NO solid-color cuffs or waistbands — cuffs and waistbands carry the multi-color rainbow stripe band on BOTH the jacket and the pants.\n- NO contrast piping on the cuffs or waistband — those areas have the rainbow stripe band; only the slash pockets carry pink piping.\n- NO chevron on the back of the jacket or back of the pants — chevron decorations are on the FRONT only (front-chest jacket, front-thighs pants, sleeve forearm panels).\n- NO three-rose cloud-cluster substitution: this garment carries the standalone first rose, not the Black Rose cluster or a pink variant of the red cluster.\n- NO recoloring the first rose to match the pink hood or rainbow panels.\n- NO Authentic Collection patch (no NFL / NBA / Hockey patch).\n- NO Bridge Series photo print on either piece.\n- NO embossed or debossed decoration.\n- NO invented chest lettering: the founder confirms a relationship to Signature font, but its exact lettering artwork and garment application must be source-bound before adding any text.\n- NO printed graphics other than the sublimated chevron stripes and stripe bands.\n- NO half-zip placket on the jacket — the zipper runs the FULL body length.\n- NO additional pockets on the back of the jacket, pants, or sleeves — only the two front slash hand pockets per piece.\n- NO sherpa lining (this is a windbreaker, not a sherpa-lined jacket — sg-009 is the sherpa-lined sibling).\n- NO oversized SR across the back yoke — retain the small separate rear SR below the hood shown in the tech flat.",
    "scene_pose": "Front view showing the closed jacket, white body, pink hood, rainbow chevrons, wearer-left first rose, full zipper and pink-piped pockets. Include the matching pants with their wearer-left first rose. Back coverage preserves the small SR immediately below the hood. Show relative logo sizes and placements from the tech flat; do not invent dimensions.",
    "scene_setting": "Pure white studio backdrop, soft directional studio lighting from front-left, subtle natural drop shadow on the floor.",
    "logo_reference": "data/brand-logos/rose-gold-rose.md",
    "extra_logos": [
      "data/brand-logos/sr-monogram.md"
    ],
    "reference_image": "assets/products/references/sg-015-windbreaker-set-techflat.jpeg",
    "extra_references": []
  },
  "images": {
    "front": {
      "path": "assets/images/products/hub/sg-015-front.webp",
      "source_key": "front_model_image",
      "role_asset": true
    },
    "back": {
      "path": "assets/images/products/signature-windbreaker-set-back-model.webp",
      "source_key": "back_model_image",
      "role_asset": true
    },
    "packshot": {
      "path": "assets/images/products/sg-015-windbreaker-set.jpg",
      "source_key": "image",
      "role_asset": true
    },
    "back_packshot": null
  },
  "render_sources": {
    "reference": "assets/products/references/sg-015-windbreaker-set-techflat.jpeg"
  },
  "logos": {
    "placements": [
      {
        "logo_id": "rose-gold-rose",
        "position": "jacket_left_chest",
        "technique": "embroidered",
        "colorway": "rose_gold"
      },
      {
        "logo_id": "rose-gold-rose",
        "position": "pants_left_thigh",
        "technique": "embroidered",
        "colorway": "rose_gold"
      }
    ],
    "decoration_sizing": {},
    "primary_reference": "wordpress-theme/skyyrose-flagship/assets/images/logos/rose-gold-rose.jpeg",
    "reference_kind": "logo",
    "patch_sport": null,
    "sku_folder": null
  },
  "content": {
    "description": {
      "value": "Signature luxury meets West Coast weather. A premium windbreaker set built for those who move through fog.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "short_description": {
      "value": "Signature luxury meets West Coast weather. A premium windbreaker set built for those who move through fog.",
      "source": "registry.catalog.description",
      "enriched": false
    },
    "seo_meta": null,
    "instagram": null,
    "tiktok": null
  },
  "alt_text": {},
  "corrections": [],
  "authority": "FOUNDER_PRODUCT_SPECIFICATIONS",
  "gaps": [
    "images.back_packshot",
    "content.description.enriched",
    "content.short_description.enriched",
    "content.seo_meta",
    "content.instagram",
    "content.tiktok",
    "content.alt_text"
  ],
  "provenance": {
    "generated": "2026-10-15T01:48:39.037159+00:00",
    "entry_point": "skyyrose.core.product.get_product",
    "sources": {
      "registry": {
        "path": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "sha256": "c27f1a3809208542",
        "modified": "2026-09-21T20:37:39.396356+00:00",
        "bytes": 438102
      },
      "content": {
        "path": "skyyrose/assets/data/product-content.json",
        "sha256": "689141e194852372",
        "modified": "2026-03-13T01:22:14.372198+00:00",
        "bytes": 38125
      },
      "alt_text": {
        "path": "skyyrose/assets/data/alt-text.json",
        "sha256": "27ad11393da6d975",
        "modified": "2026-03-13T01:22:14.370343+00:00",
        "bytes": 5302
      },
      "corrections": {
        "path": "wordpress-theme/skyyrose-flagship/data/render-corrections.json",
        "sha256": "9b63514da5e7b793",
        "modified": "2026-06-25T02:21:26.163061+00:00",
        "bytes": 5538
      }
    }
  }
}
```