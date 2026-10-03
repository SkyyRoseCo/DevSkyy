# Bounded merchant recovery

Specific authority: Corey, 2 October 2026 23:03 UTC, “Fix those gaps.” This authorizes the two existing approved Kids image assignments. The prepared LH006 conversion was rejected by automatic approval review pending exact existing-cart consequence approval and remains NOT RUN; no activation, publication, paid payment, generated images, credentials or new inventory policy.

Every dispatch has a fresh full native preimage, exact runner SHA, operation UUID, exclusive mode0600 journal with fsynced intent/after records, and independent readback. The file journal is copied outside the server. No operation is retried after ambiguous transport or commit; first reconcile the journal, parent, child and attachment states read-only. Filesystem power-loss durability is not qualified.

Image recovery is a separate reviewed invocation of `sr_restore(..., 'image')` with exact original/current snapshots and the operation-owned attachment marker. It restores only the original featured-image ID via native Woo. It refuses foreign drift; the imported attachment remains for review. Failed or uncertain imports never authorize blind cleanup.

LH006 recovery uses `sr_restore(..., 'variable', child_states)` with the commit-intent's exact parent and complete child snapshots. It refuses changed parent/children, foreign ownership or any new order-item reference to the created children. It removes only operation-owned children and restores the native simple parent, original Size attributes, defaults and native price/inventory under verified InnoDB transaction. Historical parent-order references remain untouched. Product caches are invalidated after commit. Native restoration checks permit only the naturally changed modification timestamp.

A future live restore must independently confirm target https://skyyrose.co, active V1, fresh exact state, all required InnoDB tables, the same product-only webhook/HTTP isolation, exclusive recovery journal and explicit recovery authority. These library functions are qualified on a copied loopback WP7.1.2/Woo11.1.2 SQLite fixture; no live restore ran. The transaction dialect's production InnoDB preconditions are independently inspected, not simulated as SQLite evidence.

Migration consequence: existing native simple-cart LH006 entries are removed by WooCommerce with a modification notice; customers must reselect a size. Historical orders are unchanged. This is demonstrated in the native fixture, not a claim that all live carts were inspected.

Broader theme/page recovery remains a separate unqualified release gate. These merchant procedures cannot restore theme files/options, publish pages, or qualify a paid payment.
