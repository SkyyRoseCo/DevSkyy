# Current release-gate handoff

Local fixes and bounded fallback/readiness qualification are complete. Release remains **HOLD**.
No production conversion, order/payment, synchronization, deployment, publication,
provider call or renewed live browser checkpoint was performed.

The source candidate is `887b6bfe0405d9601dd1b743542ba75e1cc5d6e2`
on `codex/release-gates-20261019`, based on current-main comparison
`cebe98935a5fd22169b58d3504783eef00016e66`. Later evidence-only commits do not
change its runtime bytes. See `adoption-manifest.json` for final package identity.

| Gate | Current disposition | Evidence |
| --- | --- | --- |
| Combined candidate/package | Full owning build and verification passed; clean-export reproducibility is bound in the final manifest | `evidence/owning-package-r5.txt`, `evidence/clean-owning-package.txt`, `evidence/package-reproducibility.json` |
| Ten logical destinations | 40/40 local desktop/mobile × full/reduced-motion cases; 12/12 browser faults; all 22 unique linked native product destinations pass | `evidence/browser-ten-routes/results.json`, `evidence/browser-faults/results.json`, `evidence/browser-destinations/results.json` |
| V1/global privacy | Offline controls pass; consumed live checkpoint remains FAIL, original collector/full packet unavailable, eight unsupported rows remain UNKNOWN | `evidence/v1-inert-local.txt`, `evidence/v1-offline-successor/results.json`, `offline-v1/provenance.json` |
| Size migration | Four native storage modes × 148 assertions, two synchronization controls, process/connection-loss recovery, stale-writer and orphan controls pass locally | `evidence/migration-subset.json` |
| Installed baseline/recovery | Authenticated installed code/runtime/content metadata read; complete recoverable backup and disposable restore remain unproved | `evidence/authenticated-installed-baseline.json`, `evidence/authenticated-native-storage.json`, `evidence/authenticated-backup-metadata.json` |

The native fixture uses WordPress 7.1.3 and WooCommerce 11.2.1. Its PHP 8.5.6,
MariaDB 13.0.2 and Woo-only plugin stack differ from installed PHP 8.4.26,
database 11.8.9 and 33 active plugins. The tests establish the stated local
boundary, not equivalence of those environments. All product availability and
orders in the fixture are synthetic. Product facts come from `get_product`;
the registry and accepted imagery/grants were not changed.

The final browser fixture follows the authenticated published route choices:
four `/collections/{collection}/`, `/experiences/`, four
`/experience-{collection}/` and `/size-guide/`. Production `/worlds/` and its
children are drafts. Local route results do not establish deployed-byte parity
or Corey's acceptance of the full immersive experience.

The 16 immersive primary cases exercised reduced-motion or unavailable-WebGL
paths. All 52 chapter instances used fallback imagery; positive original-scene
hotspot placement is source-reviewed, not browser-proven by that matrix. Heroes
were decoded explicitly; every lazy chapter was not. Destination checks tap one
link per unique SKU on mobile/reduced motion and select one native child where
applicable; they do not cover every link or cart/checkout. History checks prove
paths, not full scene reinitialization. These bounds remain open where required
by the full experience gate.

The additional native software-WebGL probe reached `three-timeout` on all four
worlds with no page errors. It did not establish successful Three rendering.
The current upstream theme hard-disables the mascot in `functions.php:15–16`;
its Three dependency loader is enqueued inside that mascot gate, and
`skyy-3d.js` returns when mascot nodes are absent. The full world-rendering
dependency therefore remains a concrete integration gap. This packet does not
enable the mascot or claim that decorative atmosphere meets the full immersive
requirement. See `evidence/three-positive-control.json`.

Scene fallback now preserves collection/role authority and separates related
products from depicted products. A different fallback SKU cannot inherit the
original scene's coordinates or “Piece in this scene” wording. Cached and late
image failures demote those links while retaining exact canonical native URLs.
Sixteen recorded different-SKU fallback observations support this boundary.

The migration writes its durable guard before product mutation, excludes another
writer, disables reconnect/replay while fenced, and requires exact fresh
reconciliation for recovery. Orphan child creation remains unavailable for
manual repair; no automatic child deletion or destructive rollback is offered.
Historical v1 and v2 order identities and monetary values remain unchanged.
In-flight commerce must be drained before any future authorized conversion.

Fresh native production reads confirm HPOS authority and its actual datastore,
with `orders_pending_sync=true`. Pending synchronization blocks a claim of safe
authority switching or synchronized-store equivalence. It does **not**, by
itself, prove that current checkout/order behavior is broken. No live sync or
storage option was changed.

The offline privacy successor persists structural network/error projections and
inert HTML. A real synthetic raw trace contained a private marker despite clean
returned HTML; the retained projected trace/log/HTML omit it. The unsafe raw
control was removed. This is not a repaired original collector, a general HTML
sanitizer qualification or a renewed live-checkpoint authorization.

Independent bounded source reviews passed for migration and immersive recovery;
JS/CSS minified bytes independently matched owning build options. The final
execution packet is separately reviewable. Details are in
`evidence/independent-reviews.json`. Review does not grant creative acceptance,
production media usage, publication or release authority.

See `remaining-gates.json` for the smallest outstanding evidence/actions and
owners. Raw local browser pixels/traces are excluded from Git and indexed by
hash in `evidence/local-browser-artifact-index.json`; they are not certified as
privacy-safe export artifacts. Historical failed runs remain retained.
