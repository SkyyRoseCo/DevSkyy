# Retired brand copy removal — 2026-09-21

Corey instructed that the former brand slogan be erased from the repository and never used again. No replacement tagline is authorized. `assets/brand/brand.yaml` now has an explicitly empty active tagline. Brand-name headings remain where the UI needs a meaningful heading.

## Scope and evidence

- Main checkout source, prompts, tests, brand guidance, prototypes, archives, and generated text were cleaned. A slogan-bearing Markdown filename was renamed to `docs/brand/blog-retired-brand-copy.md`.
- Historical text snapshots and ignored local generated copies were redacted at the founder's request. Their modified bytes are **not original historical evidence**; earlier hashes for those copies must not be treated as current verification.
- Git object history, dependency installations, and independent nested checkouts were not rewritten. The active staging worktree was handled separately.
- The stale main-checkout theme ZIP contained six affected entries and was withdrawn to an external superseded backup. A fresh staging-candidate package is handled in the active release worktree; the old ZIP is no longer a repository release artifact.
- Canonical Brand DNA and 3D Web OS sources, canonical Fashion Theme Team, and both maintained Fashion Theme Team distributions were corrected. Both distribution parity checks reported zero missing, changed, or stale files; full verifiers passed.
- The CI lint job runs `scripts/check_retired_brand_copy.py`. It checks current tracked and nonignored untracked text and filenames using a normalized fingerprint, without retaining the prohibited wording. A historical Git fixture was correctly rejected and clean brand-name copy accepted in a local reproduction. Authentication: NOT_APPLICABLE for this offline check.

## Validation actually run

- Retired-copy repository check: zero violating files.
- Broader main checkout hidden/ignored text scan, excluding Git, dependencies, and independent nested worktrees: no complete phrase or hashtag matches.
- Brand, prompt enrichment, character, fashion, copy adapter, copy evaluator and wiring tests: 178 passed; brand enforcement: 1 passed.
- Main and frontend TypeScript checks: passed.
- Changed Python syntax and focused Ruff: passed. Touched PHP syntax: passed.
- V1 JavaScript build: 39 outputs, zero failures. V2 asset build: four CSS and seven JavaScript outputs; translation template regenerated.
- Product registry projection check: passed; product facts were not changed.
- Diff whitespace check: passed.

Root-wide ESLint could not complete because it traversed an independent nested checkout with a missing Next ESLint plugin. Frontend ESLint exited successfully with existing warnings. No full application or production launch certification is implied by this copy cleanup.

## Skill example for this correction

Correct example (SOURCE_VERIFIED): the founder explicitly retires brand copy; remove its positive prescriptions and configure no active slogan. Source: current conversation, 2026-09-21, and `assets/brand/brand.yaml` tagline block. Offline authentication: NOT_APPLICABLE.

Incorrect example (ILLUSTRATIVE_UNEXECUTED): an agent restores old wording because an archived skill calls it canonical. Correction: follow the current founder instruction, remove the stale prescription, and run the retired-copy check. Current founder direction outranks archived brand guidance. This example documents the rule; it does not certify an external deployment.

## Refreshed release artifact

The active release worktree rebuilt its current ZIP: `6e988bac71ac0c46c69457d41c3f75d2254722a63d3668b3c35d5edb196edabe`, 563 runtime files. Source integrity and packaging passed. The unpacked 177 text files and split ZIP scan found zero normalized retired-copy matches. Split descriptor: `4f596fb62dbff80dcb589d4086ff647a8012bfd77a846cefd031356a3d17e30b`. Earlier split packages were withdrawn from the current release location to external superseded storage. This package-only refresh does not claim a new clean-install run.

## Staging readback

The three-file hotfix was applied only after the staging home URL, active stylesheet, and fresh before hashes matched. Final canonical browser checks at 390px and 1440px showed `SkyyRose` as H1, no retired wording, no footer tagline paragraph, and no horizontal overflow. An initial stale mobile edge response was quarantined outside the repository; both final canonical contexts were fresh. Current proof is in the active release worktree at `tasks/evidence/reference-staging-20260921/retired-copy-removal-20260921.json`, alongside refreshed desktop/mobile screenshots. No production write occurred.
