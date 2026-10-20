# Draft provider question — not sent

Contact permission is pending. This draft requests guidance only and authorizes no operation. Disclose only site identity and the technical question; attach no customer/order records or identifiers, fingerprint maps, keys, credentials, configuration values, source files or private capture material.

## Exact question

For WordPress.com site **238510894**, **https://skyyrose.co**, what supported procedure can establish a temporary global writer pause, drain existing writers, and retain/replay incoming events across checkout, Store API/REST, payment webhooks, admin writes, schedulers/queues, CLI and background processes during a theme replacement? How can we safely inspect effective order-loading behavior and the `woocommerce_stock_amount` callback chain to verify order-line fingerprint interpretation without uncontrolled application writes or other side effects?

Please identify the supported controls and provide an authenticated, site-specific way to prove: coverage of every writer and completion of the drain; durable event retention and ordered/idempotent replay, including retries or expiry limits; the exact inspection context, callback order and effective quantity/order-item behavior with documented side effects; host-supported theme replacement and rollback semantics, permissions, filesystem/rename guarantees and recovery after an uncertain result; and explicit criteria for safe reopening and verification that queued events have resumed. Please identify any uncovered path or unsupported guarantee. We seek guidance only: do not pause traffic, run inspection, change files/settings/state, restore, deploy or reopen anything on this request.

## Evidence boundary

A generic maintenance-mode description, quiet traffic counter, source-only callback search or successful command exit does not establish these guarantees. Before any future separately authorized execution, retain redacted proof of the authenticated account/site/environment, exact supported control/procedure and permitted scope, observed pause/drain and event disposition, inspection results and limitations, replacement/rollback identity checks, and explicit reopening acknowledgement. Provider guidance is not execution authorization.

The reviewed static capture packet remains frozen at commit `54afd9d35`; this question adds no installed-runtime qualification. Integration retains exclusive implementation ownership. Initialization, archive jobs, live privacy changes, conversion and deployment remain held.
