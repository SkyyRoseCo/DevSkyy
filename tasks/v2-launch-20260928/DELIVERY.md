# V2 staging delivery

Staging runtime candidate: `1acde81ed`, deployed to
`https://staging-7e48-skyyrose.wpcomstaging.com/`. Nine authenticated SSH
source/asset hashes match the candidate. Desktop and mobile browser runs confirm
the glass monument, below-header mobile framing, eight product-linked Jersey
slides, 15 live pre-order cards, no mascot, and native size selection through
bag and checkout. Canonical URLs also passed after edge caches settled. See
`staging-1acde81ed/ACCEPTANCE.md` and its recorded results.

The first deployment attempt uploaded but did not swap because password-based
SSH failed. The ignored staging environment now points to the existing verified
key, and the official wrapper completed an atomic deployment. The worktree's
missing Husky hook files were restored. Credential values were never included in
the artifacts.

The full local theme verification suite passed, as did 42 product registry
tests, 54 unit tests, repository-wide mypy on 1,666 files, and custom-page
WooCommerce enqueue regression tests. CI exposed two real faults: card rendition
metadata entered a path-based source-image projection, and the isolated V2 test
lacked its own jsdom dependency. Those fixes passed 27/27 catalog checks, 16
focused tests and a theme-only isolated dependency install/test. The package
allowlist now classifies the new runtime files and excludes the superseded hero
and authoring test. Seventeen source-certification tests pass; the local
packager validates 583 runtime entries. A GitHub rerun is still required before
claiming green CI.

## Remaining work

Production is unchanged. BR-001, BR-004 and BR-007 still need correct front
imagery. BR-004's wearer-left hip patch content/size/application is unspecified
in the current founder record; that detail has been requested. All generated
background-replacement candidates remain outside the theme because they changed
garment artwork or lettering. A pixel-preserving masked compositing route is
ready locally, pending the user's requested-method decision. The checkout lists
no payment methods on staging; Stripe sandbox keys are absent, so no payment or
order was submitted. These are unresolved release requirements.

## Evidence examples

Correct, reproduced: the final browser harness waits until Woo variation state
is `valid`, then waits for the native add-to-cart confirmation before opening
the bag. Both viewports reach a one-line cart and checkout with the selected
size; the receipt records the measured results.

Incorrect, observed: treating a nonempty variation ID as purchase readiness
allowed a click while state was still `resolving`, yielding an empty cart.
Waiting for the actual ready state corrected the harness. Likewise, an HTTP 200
or unbroken image element alone never establishes garment fidelity: BR-004 is
explicitly unavailable, and rejected background outputs remain quarantined.

Authenticated deployment context: staging account
`staging-7e48-skyyrose.wordpress.com` on WordPress.com, scoped to
`/srv/htdocs/wp-content/themes/skyyrose-flagship-2`. Source hashes were read
through the verified existing SSH key. Browser acceptance was public and
required no account sign-in. Local build and image inspections require no
authentication. No production activation occurred.
