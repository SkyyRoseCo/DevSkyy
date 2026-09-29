# Tech-flat mapping and split receipt

The SSOT is `wordpress-theme/skyyrose-flagship/data/logo-registry.json` (root symlink `logo-registry.json`). Agents, pipelines, and workflows read `get_product(sku)["render_sources"]`. This document is evidence, not a second product map.

- `techflat_sheet`: original design sheet.
- `techflat_front` / `techflat_back`: visually identified design views, including lossless crops where existing splits were incomplete or wrong.
- `front` / `back`: effective render inputs. Authoritative photo fronts are preserved. Missing views can now use identified technical views. Kids inputs now include both pieces of each set.
- Technical drawings preserve their original pixels; they do not override later founder corrections or resolve outstanding exact artwork/variant issues by themselves.

Search covered root product assets, source-photo and reference folders, V1 assets including ignored files, and the Black Rose archive listing. Inspected 26 central sheets and 72 unique JPEG/PNG V1 candidates. V1 has misleading filenames: jogger-labelled files containing bomber drawings, hoodie-labelled files containing shorts, and front/back files that are halves of a single front image. These were not reused as valid views.

27 SKUs have a mapped sheet. 20 have both technical views. 18 new lossless PNG crops preserve exact decoded source pixels, including complete Kids/Windbreaker sets and corrected crewneck/jogger/shirt crops. Remaining valid existing splits are reused. No generative enhancement, recoloring, sharpening, or resolution invention. Original files retained.

Six matching drawings not located: br-004, br-005, br-006, sg-009, sg-011, sg-012. Photos and mismatched order sheets are not relabelled as the missing drawing. This is a search result, not a claim that these sheets do not exist elsewhere.

Single-view sheets remain single-view: br-007, lh-002, lh-003, lh-005, lh-006, sg-006. sg-007 has a four-front-variant sheet, not front/back views; no arbitrary variant is promoted. The remaining render-view gaps are 10. The beanie variant and secondary SR artwork issues remain recorded in the registry.

Validation: exact decoded-pixel equality for all 18 crops; all mapped paths exist and effective render references pass the canonical validator; 64 schema/product tests and all 27 catalog consistency checks. Catalog fields, storefront images, garment specifications, founder dossiers, and corrections are unchanged by this tech-flat pass.

See techflat-crops.json for original file hashes, output hashes, and reproducible integer crop rectangles. Old audit inventories describe their earlier snapshots and are not lookup sources.
