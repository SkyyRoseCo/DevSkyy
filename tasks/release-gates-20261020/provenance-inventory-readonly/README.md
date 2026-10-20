# Existing-order provenance inventory — read-only result

The authorized bounded server-local inventory completed without application bootstrap or live writes. One HPOS shop order with one line item met the strict standalone legacy-candidate checks. There were zero generation-marked, variable-only, incomplete or malformed orders. The size-history option remains absent.

The proposed state is **213 bytes**, SHA-256 `e20d90615a3b4d15b447b406ec6d6d3ff015f0024790e9c5d5e079b1b0405484`. Only classification counts, state length and digest left the server. No order/item/product identifiers, raw keys, fingerprint map, customer fields or proposed state body were exported or saved. No initialization was performed.

## Scope clarification

The trusted parent clarified that the existing verification request already permits this necessary server-local read, provided it performs no external writes and exports only aggregate results. This supersedes the earlier statement in [the readiness plan](../theme-only-readiness/README.md) that another permission was needed merely to perform the bounded read. It does not authorize initialization, identifier/map export, rollback or provider archive acquisition, live mutations, deployment or a broader verification task. Integration remains the sole implementation writer; no new agents were started.

## Route actually established

Static PHP token inspection found no literal database definitions in the site configuration. It identified a literal table prefix and the normal `ABSPATH . 'wp-settings.php'` bootstrap include, which was never executed. Four exact-named database connection values were already available in the hosting process environment. Their values were used only in server memory and never printed, logged by this program or transferred. No credential or persistent hosting configuration was changed. Transaction and character-set settings applied only to this temporary client session.

A standalone PHP/mysqli reader verified the previously pinned installed theme anchor, then opened a session-local **read-only, repeatable-read transaction with a consistent snapshot**. It checked the expected home, active theme, HPOS-enabled/sync-disabled state and transactional table engines. It executed SELECT queries only after starting the snapshot and rolled back before closing. WordPress, regular plugins, MU plugins and configuration code were not bootstrapped or evaluated.

The initial counts-only preflight passed. The final inventory used fixed bounded SELECT joins, keeping order/item identifiers out of SQL statements and bound parameters as well as output. Reads were bounded to 1,000 HPOS records, 10,000 line items, 40,000 relevant metadata rows and 20,000 referenced post types. Oversized or noncanonical metadata, bad dates, missing keys, duplicate metadata, invalid product/variation types, generation-marked and incomplete orders would withhold the proposed digest. No such anomaly was observed in this snapshot. The original per-ID inventory reader was reviewed but never executed; its successor alone performed the inventory.

The final reader contains the exact candidate `skyyrose2_simple_size_order_lines` and `skyyrose2_simple_size_legacy_fingerprint` functions. Strict SQL-backed facades supply canonical integer metadata and UTC creation dates. Three new, small offline reader probes checked a sorted golden fingerprint, zero-quantity refusal and empty-key refusal. These are synthetic reader checks; none of the accepted native suites were rerun. The existing architect accepted the counts preflight and the final reader before their respective executions.

## Qualification and next boundary

This is a **snapshot proposal**, not trusted initialized state or installed commerce qualification. The standalone adapter does not execute the effective installed quantity filters or native object-loading hooks. It therefore does not establish installed-runtime fingerprint parity. The real size-history option is still absent, so deploying the current theme alone would still disable simple-product purchasing.

Before a later live release, qualify the affected installed profile and fingerprint interpretation, establish the expressly approved exact-theme rollback, then use an approved checkout/order-writer boundary to recompute provenance and create the absent-only history state with validated readback before activation. Stop on drift; do not install this snapshot digest as if it were a cutover inventory. Initialization and every live write remain held. No order, payment, stock, product, persistent site-setting, storage-mode, credential, provider archive, rollback capture, conversion or deployment mutation occurred here.

Frozen runtime source `4bed5b6595aa0a024d5077f13170307eef2a57bb`, theme tree `02026eda8676ede43111f102ae97601cdd7141d5`, and ZIP `52c1e4a1953a821357e9cf7ab4f43ca2d23373bc97ae027fc864a6baa5a1ee94` are unchanged. Historical synthetic parent 1290/child 1292 ownership remains unresolved and is separate from this actual-site aggregate inventory. No additional cleanup or package rebuild was performed.

See [summary.json](summary.json) and [evidence-index.json](evidence-index.json) for the redacted result and exact reader/evidence bindings. These documents add evidence to the prior frozen packets without rewriting them.
