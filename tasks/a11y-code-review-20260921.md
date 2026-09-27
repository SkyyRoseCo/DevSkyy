# Independent accessibility remediation code review — 2026-09-21

Scope: task-owned changes relative to `/tmp/skyyrose-a11y-fixes-20260921/baseline/`. The broader dirty worktree was excluded from attribution. Review covered escaping and internationalization, unique landmark names, Jetpack sharing semantics, all recorded Love Hurts small-text contrast nodes, footer token fallback behavior, comments landmark containment, homepage film group semantics, and regression risk.

## Resolved during review

**[HIGH] `assets/css/immersive.css:220` — Initial contrast patch covered only one of six recorded Love Hurts selectors**
Risk: The first supplied patch changed `.sr2-immersive__chapter-mark`, but retained axe evidence also identified the three chapter-navigation number spans and the prologue and portal eyebrows at 3.96:1. Shipping that version would have left visible serious contrast failures at both tested widths.
Fix: The current source scopes `#ef5269` to `.sr2-immersive--romantic-castle` and applies it to the chapter mark, both eyebrow labels, and chapter-navigation number spans. This now covers every selector recorded in `tasks/evidence/a11y-20260921/all-pages.json` while leaving other uses of the collection accent unchanged.

## Current-source verdict

No remaining actionable findings.

- `archive.php` omits the empty media link when no thumbnail exists and gives thumbnail links an escaped post-title accessible name.
- `template-parts/commerce/hero-composed-scene.php` adds the escaped scene label to each navigation landmark's referenced heading, making repeated “Shop this look” / “Pre-order this look” landmarks distinguishable.
- `template-parts/collections/scroll-world.php` adds the escaped collection name to the section's referenced heading, distinguishing collection story regions.
- `inc/launch-readiness.php` uses Jetpack's documented `jetpack_sharing_headline_html` three-argument contract, limits the replacement to the installed `sharing` and `likes` contexts, preserves the `sd-title` class used by Jetpack styling, and leaves final label escaping to Jetpack's verified post-filter `sprintf()` calls.
- `single.php` moves comments inside `main`, containing the reply heading and comment UI within the page's main landmark.
- `template-parts/home/editorial-hero.php` adds `role="group"`, making the existing translated `aria-label` valid group semantics.
- `assets/css/global-shell.css` keeps an unconditional 44px `min-height` before the custom-property expression. Missing or invalid `--sr2-target-size` invalidates only the later declaration; a valid value below 44px remains clamped by `max()`. The 24px inline minimum also preserves the WCAG target-size floor.

## Checks

- PHP syntax: PASS for all six changed PHP files.
- `npm audit --omit=dev --audit-level=high`: PASS, zero vulnerabilities.
- `php scripts/test-global-shell-contract.php`: PASS.
- `php scripts/test-page-service-template.php`: PASS.
- `php scripts/test-marketplace-registry.php`: PASS.
- Secret-pattern scan of changed PHP: no matches.
- `npm run verify`: not completed in this reviewer's default shell because `check-integrity.py` could not import Pillow (`ModuleNotFoundError: No module named 'PIL'`). This is an environment limitation, not a code failure. The root orchestrator is running the full verification separately with `/Users/theceo/DevSkyy/.venv/bin` on `PATH`; its result is outside this report until completed.

The initial `/tmp/skyyrose-a11y-fixes-20260921/owned-source.patch` observed during review predated the expanded contrast correction. The patch was refreshed at 16:55:58 local time and now includes the complete selector coverage present in current source.

> Review Summary: examined 8 task-owned source files, found 0 CRITICAL, 1 HIGH (resolved during review), 0 MEDIUM, 0 LOW findings. Top priority: confirm the root-owned full verification completes successfully. Merge recommendation: **APPROVE** after that verification passes.

## Follow-up: Jetpack sharing and Likes headings

The first staging retest exposed the same heading-order pattern on `/worlds/`, `/track-order/`, and `/wishlist/`: changing the sharing label to a paragraph revealed Jetpack's separate “Like this:” `h3`. The current callback now handles both installed module contexts:

```php
if ( ! in_array( $context, array( 'sharing', 'likes' ), true ) ) {
	return $headline_html;
}
return '<p class="sd-title">%s</p>';
```

This is the correct format contract for the installed Jetpack implementation. Both modules filter the headline format and then pass the result to `sprintf()` with an escaped label. Returning a format string preserves that sequencing, keeps percent characters in translated labels as data rather than format directives, retains the `sd-title` styling hook, and does not change either control set or its wrapper. Unknown contexts retain their original markup.

Installed implementation evidence: `/tmp/skyyrose-a11y-fixes-20260921/jetpack-hook-evidence.txt`, covering the Sharing call in `modules/sharedaddy/sharing-service.php` and the Likes call in the installed Likes module. The evidence records both `jetpack_sharing_headline_html` calls, their `sharing` / `likes` context arguments, the `%s` headline contract, and Jetpack's post-filter escaping.

Independent follow-up review found **0 new findings**. The source change resolves the headings initially exposed on all three affected pages. Root-owned focused coverage for escaped labels, percent-bearing labels, and unknown contexts passed all 7 cases. PHP syntax passed, and the refreshed runtime certification hash matches the current callback source.

The root-owned full suite was rerunning and the guarded staging follow-up was being applied when this review note was appended. Those outcomes remain separate from this source-review verdict until their final evidence is recorded.

## Follow-up: screen-reader label containment

The accessible scene label added inside `.sr2-hero-commerce__products h4` uses the global one-pixel, absolutely positioned `.screen-reader-text` utility. Without a positioned ancestor, that hidden span used a distant root containing block and expanded the document geometry at the 390px viewport (`scrollWidth` 510px, with the affected rail measuring 900px). The current source adds only `position: relative` to the existing heading rule in `assets/css/hero-commerce-scenes.css`.

Independent review found **0 new findings**. The heading is the narrowest stable containing block for its own hidden label. Establishing it as the containing block does not change the heading's visible flow, dimensions, typography, focus behavior, or accessible name. It also leaves the collection rail's intentional native overflow behavior intact instead of clipping the rail or applying a page-level overflow mask. The rebuilt `assets/css/hero-commerce-scenes.min.css` contains the same declaration, and the source/minified timestamps show the generated asset was rebuilt immediately after the source change.

Recorded browser evidence for the corrected state reports a 390px document width and `scrollX` 0 while preserving rail scrolling. The root-owned asset verification and full suite were still running when this follow-up review was appended; their final outcomes remain separate from this code-review result.
