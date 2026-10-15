# Copilot review context and MCP setup

## Repository instructions

Copilot review guidance lives in:

- `.github/copilot-instructions.md` for monorepo-wide review expectations.
- `.github/instructions/wordpress.instructions.md` for WordPress/WooCommerce.
- `.github/instructions/creative-analytics.instructions.md` for Creative OS,
  context resolution, and analytics.
- `.github/instructions/frontend.instructions.md` for the Next.js frontend.

GitHub reads repository-wide and path-specific custom instructions from the PR
head branch, so a review of a change to these files can use the new version in
that same PR. Check the active PR head before relying on review results.

## Context7 configuration

The repository contains
[`.github/copilot-mcp.json`](../../.github/copilot-mcp.json) with a remote
Context7 endpoint and an explicit allowlist of two documentation tools:
`resolve-library-id` and `query-docs`. This file is configuration input; it does
**not** automatically install or activate the server for GitHub Copilot. The
configuration was saved through the authenticated GitHub repository settings on
2026-09-30. The MCP settings page confirmed success; Copilot code review's
MCP-tools and custom-instructions settings were already enabled, and were left
unchanged. No credentials were configured or needed for this public
documentation endpoint.

Context7 is for public library/API documentation lookups. Use it only when a
review needs an external contract, resolve the specific library and version, and
query public docs without sending repository secrets or customer data. The
configured allowlist grants no repository, production, or provider access.

GitHub's built-in MCP server and Playwright MCP server remain enabled by
default. GitHub documents its built-in server as read-only for the current
repository. The repository-specific MCP server list is restricted to the two
Context7 tools above; no production connectors are configured here.

## Validation and evidence limits

The checked-in JSON parses locally. A live unauthenticated Context7 MCP
`initialize` and `tools/list` probe returned HTTP 200 and exposed both allowed
tools with `readOnlyHint: true`. The authenticated repository settings save and
review toggles were also confirmed. These checks verify configuration and
endpoint metadata; no Copilot review session has yet been shown to invoke
Context7. Do not claim MCP context was used for a particular review unless its
review-comment attribution or linked session logs show the server/tool call.

GitHub's documented setup and verification paths are
[Configure MCP servers for your repository](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers)
and
[Using GitHub Copilot code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review).
The latter describes repository-wide and path-specific instruction files,
head-branch instruction loading, relevant MCP use, and review-session
attribution. Recheck the documentation when changing configuration because
Copilot's supported MCP behavior can change.
