# V2 consent and durable analytics

This is a standalone V2 theme integration. It does not load V1 files at runtime.
The live theme was observed as V2 2.3.1; this checkout is V2 2.5.0. Passing
these local fixtures does not establish deployed collection or live provider
execution.

Configure these server-side constants or environment variables before collection
can receive a durable acknowledgement:

- `SKYYROSE_ANALYTICS_API_URL`: explicit backend base URL, HTTPS except local
  fixtures.
- `SKYYROSE_ANALYTICS_SITE_ID`: backend-bound site identifier.
- `SKYYROSE_ANALYTICS_ENVIRONMENT`: `production`, `staging`, or `test`, matching
  the backend.
- `SKYYROSE_ANALYTICS_SECRET`: matching backend HMAC secret, at least 32
  characters.

The backend host must also pass the shared allowlist and address checks.
Extending `skyyrose2_analytics_allowed_backend_hosts` is a server-side
integration decision. No secret is localized into browser code. Missing
configuration fails closed. The public page token is distinct from the HMAC
secret.

Collection begins only with matching accepted browser storage and consent
cookie. The footer Cookie settings link reopens the accessible dialog.
Decline/revoke clears the session and in-memory queue. Card views and clicks are
engagement only; a native buy click is never a purchase. Paid-order truth
remains the backend WooCommerce webhook's responsibility. No legacy visitor
counter is installed.

`../../scripts/sync-analytics.py` generates/checks explicit projections of the
V1 validator, bounded HMAC relay, consent UI, and collector. The checked
transforms adapt only the V2 prefix, text domain, card selectors, and omission
of the V1 legacy counter projection/personalization module. Edit the V1
maintained sources for shared behavior, then regenerate; V2 bootstrap/card
rendering remain local. The script also projects regression fixtures to exercise
the same protocol gates.

From the repository root:

```sh
python3 wordpress-theme/skyyrose-flagship-2/scripts/sync-analytics.py --check
node --test wordpress-theme/skyyrose-flagship-2/tests/analytics/consent.test.cjs
php wordpress-theme/skyyrose-flagship-2/tests/analytics/relay.php
php wordpress-theme/skyyrose-flagship-2/tests/analytics/bootstrap.php
node --test wordpress-theme/skyyrose-flagship-2/tests/analytics/browser-consent.test.cjs
```

Offline fixtures use synthetic records; authentication is not applicable. The
card fixture executes the actual V2 PHP partial. Browser tests at 1280px/375px
exercise its rendered banner, storage, clicks, and revocation; the fixture
prevents native anchor navigation so it can continue asserting the dialog state.
That does not establish a live WooCommerce transaction.
