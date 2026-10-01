# DevSkyy repository review guidance

DevSkyy is a Python, TypeScript/Next.js, and WordPress/WooCommerce monorepo.
Before reviewing a path, read the applicable `AGENTS.md` or local instructions
and the implementation, tests, and package configuration that own it. Do not
assume a root command or convention applies to every package.

## Review method

- Review the exact current commit and proposed diff. When a GitHub PR or CI run
  is in scope, use available GitHub MCP context read-only to confirm its head
  SHA, changed files, current checks, and existing review threads. Do not rely
  on stale PR text or results from an earlier head. State the reviewed head SHA
  and the checks considered in the review summary.
- When a finding depends on an external library/API contract, use the configured
  Context7 documentation tools for the exact library and relevant version when
  available. Prefer primary/official docs, and do not send secrets, customer
  payloads, or private source content to public documentation tools.
- Report only actionable defects introduced by the change or regressions it
  causes. Check current review threads and the latest diff first; do not repeat
  findings already fixed or addressed. Do not suppress a real bug because a
  similar issue was reported before.
- Lead with findings, highest impact first. Each finding must name the exact
  file and line, explain the trigger and user/system impact, and provide a
  concrete reproduction or evidence. Separate confirmed defects from questions
  or risks. If no actionable defect is supported, say so briefly.
- Ground conclusions in code, tests, configuration, or current CI output. Label
  checks as run, passing, failing, skipped, or unavailable; never infer a pass
  from the presence of a test, an HTTP 200, or a successful import.
- Review security, data integrity, authorization, failure handling, migrations,
  compatibility, and meaningful user-visible behavior where relevant. Avoid
  style-only comments unless a project rule or concrete defect is involved.

## SkyyRose authority

The editable product source of truth is
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`; read complete
records through `from skyyrose.core.product import get_product`. Corey is the
founder and maker. His latest explicit product specifications, artwork
identifications, and corrections are authoritative. Preserve their exact wording
and dimensions, and do not demand independent proof or downgrade their
authority. Do not create competing product facts in code, prompts, or generated
projections. Keep owner-ratified `docs/brand/constitution-v1/` text intact
unless the change itself is authorized to update it.

Review permissions are read-only. MCPs may provide context about code, PRs,
checks, or documentation when relevant; do not use them to post comments, edit
issues, merge, deploy, publish, migrate, or trigger paid/provider execution.
Review authority never grants those actions.
