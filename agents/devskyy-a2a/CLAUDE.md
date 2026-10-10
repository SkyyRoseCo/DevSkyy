# Coding Agent Guide

## Reference Documentation

If you have ADK skills available, use those instead of fetching the URLs below.

Otherwise, fetch these resources as needed:

- **ADK Cheatsheet**:
  https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/agent_starter_pack/resources/docs/adk-cheatsheet.md
  — Agent definitions, tools, callbacks, orchestration
- **Evaluation Guide**:
  https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/agent_starter_pack/resources/docs/adk-eval-guide.md
  — Eval config, metrics, gotchas
- **Deployment Guide**:
  https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/agent_starter_pack/resources/docs/adk-deploy-guide.md
  — Infrastructure, CI/CD, testing deployed agents
- **Development Guide**:
  https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/docs/guide/development-guide.md
  — Full development workflow
- **ADK Docs**: https://google.github.io/adk-docs/llms.txt

---

## Deploy gate

**Deploy to dev requires explicit human approval.** Run `make deploy` only after
the user confirms (see the **Deployment Guide**). `make deploy` only exists
after `uvx agent-starter-pack enhance` (or equivalent) adds a deployment target.
For production, ask the user: Option A (simple single-project) or Option B (full
CI/CD pipeline with `uvx agent-starter-pack setup-cicd`) —
[deployment docs](https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/docs/guide/deployment.md).

Other commands (`playground`, `test`, `eval`, `eval-all`, `lint`,
`setup-dev-env`) are Makefile targets.

---

## Operational Guidelines for Coding Agents

- **Code preservation**: Only modify code directly targeted by the user's
  request. Preserve all surrounding code, config values (e.g., `model`),
  comments, and formatting.
- **NEVER change the model** unless explicitly asked. Use
  `gemini-3-flash-preview` or `gemini-3.1-pro-preview` for new agents.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (e.g., `global` instead of
  `us-east1`), not the model name.
- **ADK tool imports**: Import the tool instance, not the module:
  `from google.adk.tools.load_web_page import load_web_page`
- **Run Python with `uv`**: `uv run python script.py`. Run `make install` first.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root
  cause instead of retrying.
- **Terraform conflicts** (Error 409): Use `terraform import` instead of
  retrying creation.
