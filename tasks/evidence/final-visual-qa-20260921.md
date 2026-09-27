# Final Staging Visual QA — 2026-09-21

Environment: `https://staging-7e48-skyyrose.wpcomstaging.com/`

Candidate cache token: `qa=launch_final_20260921b`. Root release evidence
confirmed the deployed theme hashes (including the new page-service part) before
this browser pass. These are browser observations, not checkout/payment proof.

## Measured home layout

| Viewport | Result |
|---|---|
| Desktop 1440px | `scrollWidth` 1440px. Hero title was centered at x=509.7, width=420.5; intro x=537.2, width=365.6; CTA rail used `justify-content:center`. Screenshot captured. |
| Mobile 390px | `scrollWidth` 390px. Centered title x=77.0, width=235.9; intro x=42.7, width=304.6; CTAs x=20, width=350, height=48. Mascot was visible at 44×46. Screenshot captured. |
| Mobile 320px | `scrollWidth` 320px. Centered title x=51.5, width=216.9; intro x=20, width=280; wrapped CTA rail x=20, width=280, height=108, with both actions reachable. Mascot remained 44×46. |

The live Pause motion control changed its accessible label to Play motion and
then back to Pause motion after a second activation. The menu, shop, account,
mascot, bag, and hero actions were exposed in the accessibility tree.

## Commerce and service routes

| Route / viewport | Result |
|---|---|
| Shop, 390px | `scrollWidth` 390px; product grid rendered one 326px column at x=32; collection rail used `justify-content:center`; H1 was centered. |
| BR-003 PDP, 1440px | `scrollWidth` 1440px; product eyebrow and H1 both used `text-align:center` in their 514.7px summary rail. Primary on-model image rendered at 754.1×640 in the desktop slot and had `currentSrc` `assets/card-scenes/br-003-onmodel.webp` (natural 426×640). Screenshot captured. |
| FAQ | Fresh candidate contained the three canonical FAQ questions and five client-service links. Generic heading centered and client-service links used `justify-content:center`. Screenshot captured. |
| My Account, 390px | `scrollWidth` 390px; centered H1. Native Woo login form present at x=33, width=324; service navigation absent. Screenshot captured. |
| BR-002 variation | Initial front was `assets/approved-card-fronts/br-002-onmodel.webp`. Selecting M and resetting to the empty value left that approved front, its alt text, derivative `srcset`, and `sizes` intact. `sizes` was `(max-width: 47.99rem) clamp(214px, 34.6667svh, 320px), clamp(299px, 42.6667svh, 470px)`, the expected aspect-ratio scaling of the 52svh mobile and 64svh desktop constraints. This confirms DOM/image state, not transfer bytes. |

## Outcome and limits

No horizontal overflow, centered-hierarchy regression, hidden control, or
approved-front reset regression was observed in the listed final paths. A
single broad six-route sweep timed out and reset the browser automation kernel;
the remaining routes were then checked sequentially rather than counted as
passed from that timed-out run.

## Sequential page-alignment follow-up

At 390px, the collections index, Signature collection world, About, Journal,
Contact, and Shipping & Returns all retained visible centered H1/hero hierarchy
without a visual horizontal clipping defect. The collection index retained its
world controls; the Signature world retained its Pause motion control and
chapter actions. Contact retained all native form controls and its service-link
group. Shipping & Returns retained its dense policy/table content with the
page title centered and the long-form body kept left aligned for readability.

Desktop visual capture of the collections index confirmed its centered hero
heading, deck, and world controls. Mobile screenshots were captured for the
collections index, Signature world, About, Journal, Contact, and Shipping &
Returns. No corrective CSS was warranted from this pass.
