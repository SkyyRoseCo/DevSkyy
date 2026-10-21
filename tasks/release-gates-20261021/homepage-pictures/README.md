# Homepage pictures restored

All four homepage collection panels now display their existing verified pictures on https://skyyrose.co/. Published October 21, 2026 at 06:50:49 PDT. Current source: `7cf587133bdb061fadf1138f42b1a183a5fd5300`.

The homepage used obsolete still references and a legacy motion resolver. The output filter removed those references, leaving four empty picture elements and a Kids motion button with no playable source. The fix adopts the collection pages' existing governed cinema resolver and the current Kids static product fallback. No image admission policy, product fact, source artwork or media binary was changed.

Only `template-parts/home/editorial-collection.php` changed in production, from SHA256 `248f2a752611cf463b8a0e2cc52d23ce8cd587a9313904475dcd2e51fdee11c2` to `59b77560f14e90b58dd63f961aecd56e41f4dbe382fc7d53157ee7889fe8a4cf`. The other 731 expected release members rehashed unchanged before and after replacement. The original file was retained under the existing protected 0700 rollback parent, with backup file mode0600; the full previous theme and both dist artifacts remain preserved. Replacement used the established authenticated SSH route, exact prior-file guard, PHP parse check, exclusive release lock and atomic same-directory rename. No generic rollback, cleanup or retry followed an uncertain outcome.

Verification:

- PHP syntax passed. Two offline rendered component tests passed, including missing motion, missing Kids still and tampered inventory cases; 20 motion validator regressions passed. These use the real gate/resolvers with request APIs stubbed and are not full native WordPress qualification. The previously rejected full loopback WordPress fixture action was not repeated or bypassed.
- Fresh installed WordPress.com site238510894 rendering, with the actual output filter explicitly applied, reproduced zero pictures before and four surviving pictures after. WordPress CLI bootstrap is not claimed inherently read-only; no explicit order/product/payment mutation was invoked.
- Supported cache flush succeeded. The first normal HTTP response still served STALE markup; later normal HTTP and browser requests served the corrected page as HIT. Early missing-browser and zero-image browser failures remain retained. No second publication was made to mask those failures.
- Final anonymous normal-URL browser checks decoded all four pictures at390/768/1440px: 12 unique cases. Visible dimensions and nonzero natural dimensions were asserted, and screenshots retained. Kids has no dead film/control. Reduced motion was used; these checks do not claim new live motion, physical-device, payment, consent/privacy or full-plugin qualification. Browser requests were GET/HEAD only with a bounded theme-image CDN allowance. No consent selection, cart add, form submission, live order or payment occurred. All owned browser process groups retired.
- Final standalone read-only snapshot retained the same213-byte history SHAe20d90615a3b4d15b447b406ec6d6d3ff015f0024790e9c5d5e079b1b0405484, one legacy fingerprint, one shop order and zero marked orders. Commerce source remained unchanged; the prior72native commerce checks were not rerun.
- All seven unrelated dirty canonical Kids/projection files match their pre-task hashes. Required registry projection check passed.

A standard 732-member successor theme ZIP is retained at `.artifacts/picture-restoration-20261021/skyyrose-flagship-2-2.5.6-home-pictures.zip`, SHA256 `a637754718e9e74535ae7e60d85a41ea2efb8077fbda68cbbf6bbd5f82a20471`. It differs from the prior e332 package in the single published PHP member; the earlier package remains historical evidence. No provider archive acquisition or new creative generation occurred.

Raw evidence and screenshots: `.artifacts/picture-restoration-20261021/`. See `reference-pins.json` for retained result bindings.
