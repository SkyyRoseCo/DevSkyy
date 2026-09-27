# Engineering Reference Library

Load when: a phase needs WordPress theme mechanics, WooCommerce PDP correctness,
CSS craft, or three.js/immersive implementation detail.

These are on-demand references, not listed skills. Read this index, then load
only the single file the active phase needs, and record it in the phase ledger
under `../tool-budget-and-loading.md`. Never load a whole folder.

## Routing

| Need                                                    | Load                                                                  | Primary owners                                             |
| ------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| Theme build, `.min` parity, templates, quality gates    | `wordpress-woocommerce/skyyrose-wp-platform/overview.md`, then one reference | `woocommerce-theme-engineer`, `fashion-frontend-engineer`  |
| WooCommerce data flow, REST, webhooks, catalog binding  | `wordpress-woocommerce/skyyrose-wp-platform/woocommerce-integration.md` | `woocommerce-theme-engineer`, `catalog-sot-integrator`     |
| PDP add-to-cart, variations, stock, cart fragments      | `wordpress-woocommerce/wc-pdp-correctness.md`                         | `woocommerce-theme-engineer`, `visual-commerce-qa`         |
| Cascade, layout, responsive, theming, CSS audit         | `css/index.md`, then `css/css-expert/overview.md` and one member      | `fashion-token-foundations-engineer`, `fashion-frontend-engineer` |
| three.js scenes, materials, shaders, GLB product viewer | `threejs-immersive/index.md`, then one file                            | `fashion-motion-responsive-engineer`, `fashion-frontend-engineer` |

## Placeholders

- `<repo-root>`: the host repository root.
- `<theme-workspace>`: the directory holding the theme's `package.json` build.
  DevSkyy: `wordpress-theme/`.
- `<theme-root>`: the theme directory. DevSkyy: `wordpress-theme/skyyrose-flagship`.
- `<theme-dir>`: the theme directory name. DevSkyy: `skyyrose-flagship`.

## Rules that outrank these references

- Product facts and image bindings come only from `logo-registry.json`; read
  [../product-registry-authority.md](../product-registry-authority.md). Founder
  corrections are `FOUNDER_CONFIRMED` and land in the registry first.
- Brand decisions follow [../skyyrose-design-canon.md](../skyyrose-design-canon.md).
- The Fashion Theme Team builds and reviews candidates only. Production deploys,
  live WooCommerce or media writes, uploads, and paid calls belong to the host
  repository's approval process.
- Lines marked "Host repo (DevSkyy)" name tools or files that exist only in that
  repository; confirm them read-only before relying on them elsewhere.
- Current official documentation and executable repository evidence outrank any
  version-specific claim in these files.

## Provenance and licenses

Each folder's `index.md` records the source path, source SHA-256, license, and
every adaptation. The three.js family is third-party (CloudAI-X/threejs-skills,
MIT per its README); keep its attribution with any distribution.
