# Staging acceptance for candidate 1acde81ed

The browser run in `run.cjs` targets the actual WordPress staging site. It
compares the served monument image bytes to the local committed asset, tests
homepage and Jersey gallery interactions, follows the first pre-order card to
its PDP, and takes BR-004 size M through cart and checkout. It saves desktop and
mobile screenshots and `artifacts/results.json`.

This run never clicks Place order, changes gateway settings, or implies that
blocked product fronts are approved. BR-001, BR-004, and BR-007 remain blocked
on current front-image fidelity; a lack of broken image requests does not mean
those product fronts are present or accurate. It also checks the deployed
minified hero/content CSS byte hashes and measures that mobile hero media begins
below the fixed header. Screenshots and results must be labeled with the
deployed candidate, and this script must run only after deployment completion
has been confirmed.

Run from the repository root with
`node tasks/v2-launch-20260928/staging-1acde81ed/run.cjs`. A passing result
means the specified public browsing and cart-to-checkout flow worked, not that a
payment, notification, or production launch was verified.
