# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-08-30T15:58:11.751Z
> Files: 2294 tracked on main ∪ origin/main | Anatomy hits: 0 | Misses: 0

## ./

- `.claudeignore` — /*.png (~644 tok)
- `.dockerignore` — ALLOWLIST: ignore all, re-include first-party packages + canonical data; cuts context 1GB→43MB (~909 tok)
- `.eslintrc.cjs` — ESLint configuration (~954 tok)
- `.gitattributes` — Git attributes (~70 tok)
- `.gitignore` — Git ignore rules (~3315 tok)
- `.gitleaks.toml` — Gitleaks Configuration — DevSkyy (~1260 tok)
- `.gitleaksignore` (~7942 tok)
- `.impeccable.md` — Design Context (~1519 tok)
- `.markdownlint.json` (~57 tok)
- `.mcp.json` (~699 tok)
- `.nvmrc` (~3 tok)
- `.pre-commit-config.yaml` — Pre-commit Configuration - Optimized for Speed and Safety (~1909 tok)
- `.prettierrc.js` (~380 tok)
- `.vercelignore` — DevSkyy .vercelignore - Production Deployment (~853 tok)
- `AGENTS.md` — Repository Guidelines (~659 tok)
- `alembic.ini` — Alembic configuration for DevSkyy (~163 tok)
- `CHANGELOG.md` — Change log (~481 tok)
- `CLAUDE.md` — OpenWolf (~6734 tok)
- `conftest.py` — /*.py", (~2184 tok)
- `devskyy_mcp.py` (~1618 tok)
- `docker-compose.yml` — production stack: postgres/redis/app/worker/elite-worker + monitoring & proxy profiles; one devskyy:local image, fail-loud secrets (~2744 tok)
- `docker-entrypoint.sh` — startup script; generates JWT/ENC keys if unset, then dispatches a passed command (worker) or defaults to uvicorn (~1197 tok)
- `Dockerfile` — multi-stage Python image (builder + non-root runtime), `COPY . .` + allowlist .dockerignore, INSTALL_TARGET arg, tini PID1; one image for app+workers (~1593 tok)
- `Dockerfile.api` — Dockerfile.api — slim production image for the full FastAPI backend (~1193 tok)
- `Dockerfile.mcp` — Dockerfile.mcp — slim standalone MCP HTTP service (mcp_service:app). (~560 tok)
- `eslint.config.mjs` — ESLint flat configuration (~879 tok)
- `fastmcp.config.json` (~287 tok)
- `fly.backend.toml` — Fly config for devskyy-backend (main_enterprise API app); explicit CORS origins (no dead wildcard literal), DB_*/REDIS_* env names matching actual code consumers, /health+/ready checks (~1551 tok)
- `fly.toml` — fly.toml - DevSkyy Enterprise Platform (~1193 tok)
- `glb-models.html` — 33-SKU 3D GLB keep/delete QC sheet; model-viewer + meshopt/basis/draco decoders; serve over HTTP (`python3 -m http.server 8010`), file://-robust via CDN fallback + warning banner (~7078 tok)
- `IDEA.md` (~5 tok)
- `init.sql` — DevSkyy Database Initialization (~198 tok)
- `lint-staged.config.mjs` — Declares relPaths (~346 tok)
- `main_enterprise.py` — API router (~5854 tok)
  - fn `_parse_sentry_sample_rate` L39-52 (~130 tok)
  - fn `_resolve_cors_origin_regex` L53-78 (~327 tok)
  - fn `lifespan` L79-170 (~980 tok)
  - fn `_resolve_schema_url` L171-243 (~858 tok)
  - fn `correlation_id_middleware` L244-253 (~103 tok)
  - fn `timing_middleware` L254-268 (~114 tok)
  - fn `security_headers_middleware` L269-293 (~284 tok)
  - fn `rate_limit_middleware` L294-481 (~1905 tok)
  - fn `root` L482-493 (~82 tok)
  - fn `health_check` L494-515 (~165 tok)
  - fn `readiness_check` L516-520 (~27 tok)
  - fn `liveness_check` L521-530 (~78 tok)
  - fn `http_exception_handler` L531-545 (~140 tok)
  - fn `general_exception_handler` L546-581 (~316 tok)
- `Makefile` — Make build targets (~3850 tok)
- `mcp_service.py` — Standalone slim MCP HTTP service. (~676 tok)
  - fn `lifespan` L32-50 (~147 tok)
  - fn `health` L51-60 (~92 tok)
  - fn `ready` L61-70 (~111 tok)
- `mypy.ini` — Declares of (~538 tok)
- `nginx-app.devskyy.app.conf` — Nginx configuration for app.devskyy.app (self-hosted alternative) (~1497 tok)
- `nginx.conf` — Nginx configuration (~1630 tok)
- `opencode.json` (~56 tok)
- `package.json` — Node.js package manifest (~2924 tok)
- `prometheus.yml` — DevSkyy - Prometheus Configuration (~741 tok)
- `pyproject.toml` — Python project configuration (~5471 tok)
- `pyrightconfig.json` (~332 tok)
- `README.md` — Project documentation (~1693 tok)
- `render-review.html` — SkyyRose — ALL renders, every engine · ✓ keep / ✗ delete (~203235 tok)
- `requirements-imagery.txt` — Nano Banana 2 — SkyyRose AI Image Pipeline (~131 tok)
- `requirements-mcp.txt` — Slim MCP HTTP service dependencies (mcp_service.py / Dockerfile.mcp). (~122 tok)
- `requirements-trellis.txt` — TRELLIS clothing 3D pipeline dependencies (~327 tok)
- `skills-lock.json` (~3853 tok)
- `SOT.md` — Source of Truth (SOT) Registry (~5533 tok)
- `vercel.json` — /*.ts": { (~525 tok)

## .claude/

- `CLAUDE.md` — Recent Activity (~59 tok)
- `IMMEDIATE_REQUIREMENTS.md` — Immediate Requirements - READ THIS FIRST (~499 tok)
- `learn-elite-studio-progress.md` — Learn Codebase: Elite Studio — Progress (~12226 tok)
- `learn-wordpress-theme-progress.md` — Learn Codebase: WordPress Theme (skyyrose-flagship) — Progress (~21158 tok)
- `mcp-config.json` (~116 tok)
- `ralph-loop-iteration-2.md` — Ralph Loop Iteration 2 - MCP Server Loading Fix (~601 tok)
- `settings.json` — /.env)", (~2462 tok)

## .claude/agents/

- `architect.md` — Your Role (~1573 tok)
- `build-error-resolver.md` — Build Error Resolver (~936 tok)
- `code-reviewer.md` — Review Setup (~1763 tok)
- `database-reviewer.md` — Database Reviewer (~1079 tok)
- `deploy-and-verify.md` — Deploy & Verify Agent (~1555 tok)
- `doc-updater.md` — Documentation & Codemap Specialist (~831 tok)
- `e2e-runner.md` — E2E Test Runner (~1022 tok)
- `fashion-accessibility-content-engineer.md` — Fashion Accessibility and Content Engineer (~319 tok)
- `fashion-brand-systems-researcher.md` — Fashion Brand Systems Researcher (~296 tok)
- `fashion-component-commerce-engineer.md` — Fashion Component and Commerce Engineer (~322 tok)
- `fashion-design-system-engineer.md` — Fashion Design System Engineer (~3028 tok)
- `fashion-designops-governance-engineer.md` — Fashion DesignOps and Governance Engineer (~329 tok)
- `fashion-motion-responsive-engineer.md` — Fashion Motion and Responsive Engineer (~305 tok)
- `fashion-sot-watchdog.md` — Fashion SOT Watchdog (~284 tok)
- `fashion-theme-architect.md` — Award-winning end-to-end marketplace fashion-theme builder; full funnel, .min build, WCAG/CWV/i18n gate, STOP-AND-SHOW on deploy/paid (~4890 tok)
- `fashion-token-foundations-engineer.md` — Fashion Token Foundations Engineer (~287 tok)
- `fashion-typography-layout-director.md` — Fashion Typography and Layout Director (~292 tok)
- `fashion-visual-qa-red-team.md` — Fashion Visual QA Red Team (~344 tok)
- `fixer.md` — Role (~1100 tok)
- `frontend-developer.md` — Communication Protocol (~2766 tok)
- `loop-operator.md` — Mission (~1465 tok)
- `planner.md` — Your Role (~1763 tok)
- `pr-green-loop.md` — Inputs (~2075 tok)
- `python-reviewer.md` — Review Priorities (~843 tok)
- `refactor-cleaner.md` — Refactor & Dead Code Cleaner (~677 tok)
- `security-reviewer.md` — Security Reviewer (~1110 tok)
- `tdd-guide.md` — Your Role (~721 tok)
- `theme-heal-doctor.md` — Theme Heal Doctor (~2999 tok)
- `wp-code-simplifier.md` — WordPress Code Simplifier (~1348 tok)

## .claude/commands/

- `build-fix.md` — Build and Fix (~1110 tok)
- `checkpoint.md` — Checkpoint Command (~145 tok)
- `CLAUDE.md` — Recent Activity (~57 tok)
- `code-review.md` — Code Review (~247 tok)
- `deploy-wp.md` (~68 tok)
- `e2e.md` — E2E Command (~240 tok)
- `enhance.md` — /enhance — Prompt Enhancement (~1210 tok)
- `eval.md` — Eval Command (~167 tok)
- `execute-prp.md` — Execute BASE PRP (~317 tok)
- `fix-and-learn.md` (~101 tok)
- `generate-prp.md` — Create PRP (~660 tok)
- `generate-tests.md` — Generate Tests (~663 tok)
- `learn.md` — /learn - Extract Reusable Patterns (~164 tok)
- `orchestrate.md` — Orchestrate Command (~227 tok)
- `plan-exit-review.md` — Plan Review Mode (~2659 tok)
- `plan.md` — Plan Command (~234 tok)
- `pr-green.md` — Usage (~471 tok)
- `preflight.md` — What to do (~502 tok)
- `refactor-clean.md` — Refactor Clean (~180 tok)
- `ship-check.md` — Gate sequence (stop on first failure) (~585 tok)
- `sync-catalog.md` — sync-catalog (~668 tok)
- `tdd.md` — TDD Command (~266 tok)
- `test-coverage.md` — Test Coverage (~166 tok)
- `update-codemaps.md` — Update Codemaps (~176 tok)
- `update-docs.md` — Update Documentation (~184 tok)
- `verify.md` — Verification Command (~161 tok)
- `wp-simplify.md` (~46 tok)

## .claude/contexts/

- `dev.md` — Development Context (~105 tok)
- `research.md` — Research Context (~154 tok)
- `review.md` — Code Review Context (~132 tok)

## .claude/hooks/

- `canon-prefetch.sh` — UserPromptSubmit hook — structural enforcement of DevSkyy AP-16 (~1283 tok)
- `catalog-drift-guard.sh` — catalog-drift-guard.sh — PostToolUse hook: warn on drift after editing catalog/registry files. (~1778 tok)
- `context7-gate.sh` — DEPRECATED 2026-05-13. Replaced by context7-prefetch.sh (UserPromptSubmit (~876 tok)
- `context7-prefetch.sh` — UserPromptSubmit hook — auto-nudge Context7 docs lookup when the user's (~1770 tok)
- `context7-touched.sh` — PostToolUse companion to context7-prefetch.sh (and legacy context7-gate.sh). (~486 tok)
- `hooks.json` — Declares check (~3264 tok)
- `learning-reminder.sh` — Stop hook — structural reminder to update cerebrum / buglog / memory.md (~617 tok)
- `learning-tripwire.sh` — PostToolUse companion to learning-reminder.sh. (~454 tok)
- `paid-api-stopgate.sh` — PreToolUse hook — BLOCKING gate for paid / irreversible operations. (~2106 tok)
- `phpcs-on-write.sh` — PostToolUse hook — runs PHPCS WordPress standard on a single PHP file (~1002 tok)
- `prompt-eng-nudge.sh` — UserPromptSubmit hook — nudge to the prompt-engineering dataset when (~835 tok)
- `prompt-eng-tripwire.sh` — PreToolUse tripwire — fires when Claude is about to Edit/Write/MultiEdit (~695 tok)
- `python-format-on-write.sh` — PostToolUse hook — formats a single Python file immediately after (~718 tok)
- `stop-test-gate.sh` — /*.py" 2>/dev/null \ (~889 tok)

## .claude/hooks/claude-md-tracker/

- `session-summary.sh` — Stop Hook — Summarize CLAUDE.md staleness at session end (~539 tok)
- `test-hooks.sh` — Test harness for CLAUDE.md staleness tracking hooks (~3208 tok)
- `track-changes.sh` — PostToolUse Hook — Track structural changes for CLAUDE.md staleness detection (~1534 tok)

## .claude/hooks/image-optimizer/

- `optimize-image.sh` (~309 tok)

## .claude/hooks/lib/

- `common.sh` — Shared helpers for DevSkyy structural-enforcement hooks. (~856 tok)

## .claude/hooks/memory-persistence/

- `pre-compact.sh` — PreCompact Hook - Save state before context compaction (~312 tok)
- `session-end.sh` — Stop Hook (Session End) - Persist learnings when session ends (~409 tok)
- `session-start.sh` — SessionStart Hook - Load previous context on new session (~492 tok)

## .claude/hooks/router/

- `README.md` — Project documentation (~974 tok)
- `router.py` — DevSkyy task-aware resource router. (~1133 tok)
  - fn `_load_triggers` L41-49 (~68 tok)
  - fn `_read_prompt` L50-57 (~62 tok)
  - fn `_match_pattern` L58-70 (~99 tok)
  - fn `_format_context` L71-110 (~382 tok)
  - fn `main` L111-141 (~174 tok)
- `triggers.json` (~1242 tok)

## .claude/hooks/router/helpers/

- `backup-settings.sh` — Timestamped backup of both global and project Claude Code settings. (~121 tok)
- `enable-pack.sh` — Flip a Claude Code plugin's enabled state in ~/.claude/settings.json. (~601 tok)

## .claude/hooks/strategic-compact/

- `suggest-compact.sh` — Strategic Compact Suggester (~467 tok)

## .claude/rules/

- `agents.md` — Agent Orchestration (~406 tok)
- `prompt-techniques.md` — Prompt Technique Enhancement (Always Active) (~611 tok)
- `sequential-thinking.md` — Sequential Thinking (Auto-Trigger) (~329 tok)
- `testing.md` — Testing Requirements (~267 tok)
- `workflow-orchestration.md` — Workflow Orchestration (~1110 tok)

## .claude/state/

- `heal-knowledge.json` (~81 tok)
- `theme-health-baseline.json` (~1340 tok)

## .claude/system-prompts/

- `dashboard-gaps-3-6.html` — System Prompt: Dashboard Gaps — Priorities 3–6 (~5353 tok)
- `dashboard-gaps-3-6.md` — System Prompt: Dashboard Gaps — Priorities 3–6 (~3378 tok)

## .claude/workflows/

- `self-healing-theme-loop.js` — Exports meta (~9029 tok)
- `skyyrose-dev-team-context.html` — SkyyRose Dev Team — Charter & Context (~4649 tok)
- `skyyrose-dev-team.js` — Exports meta (~3257 tok)
  - fn `normalizeTask` L115-120 (~75 tok)
  - fn `agentFor` L121-125 (~48 tok)
  - fn `fileList` L126-245 (~1959 tok)
- `worktree-trio.js` — Exports meta (~7391 tok)
  - fn `planPrompt` L141-158 (~387 tok)
  - fn `execPrompt` L159-183 (~697 tok)
  - fn `fableReviewPrompt` L184-212 (~922 tok)
  - fn `integratePrompt` L213-341 (~2575 tok)

## .cursor/

- `mcp.json` (~31 tok)

## .design-sync/

- `config.json` (~108 tok)
- `NOTES.md` — design-sync Notes (~1119 tok)

## .design-sync/previews/

- `Button.tsx` — Solid (~125 tok)
- `CollectionHero.tsx` — Canonical brand-script lockup images from skyyrose.co theme assets (all verified 200). (~477 tok)
- `HoloCard.tsx` — Real product renders from skyyrose.co WooCommerce media library (all verified 200) (~400 tok)

## .fashion-theme/

- `candidate-manifest.json` (~358 tok)
- `catalog-binding.json` (~2636 tok)
- `codex-desktop-handoff.json` (~888 tok)
- `founder-rights-attestation-2026-08-26.json` (~326 tok)
- `gap-ledger.json` (~522 tok)
- `jersey-product-truth.json` (~3560 tok)
- `ownership-map.json` (~265 tok)
- `promotion-manifest.json` (~3485 tok)
- `shot-manifest.json` (~11689 tok)
- `v2-remodel-ledger.json` (~10376 tok)
- `woocommerce-runtime-capture-2026-08-26.json` (~3167 tok)
- `workspace-ledger.json` (~406 tok)

## .fashion-theme/review-assets/

- `generated-review-manifest.json` — Declares and (~2023 tok)
- `website-image-program.md` — Website image program — review only (~657 tok)

## .gemini/

- `settings.json` (~37 tok)

## .github/

- `BRANCH_PROTECTION.md` — Branch Protection Rules (~817 tok)
- `CODEOWNERS` — DevSkyy Code Owners (~619 tok)
- `copilot-instructions.md` — WordPress Development — Copilot Instructions (~1954 tok)
- `dependabot.yml` (~1069 tok)
- `PULL_REQUEST_TEMPLATE.md` — Description (~425 tok)

## .github/workflows/

- `asset-generation.yml` — CI: Asset Generation Pipeline (~1780 tok)
- `catalog-validate.yml` — CI: Catalog Consistency (~1726 tok)
- `ci.yml` — /*.py') }} (~10508 tok)
- `claude-code-review.yml` — /*.ts" (~435 tok)
- `claude.yml` — CI: Claude Code (~564 tok)
- `codeql.yml` — For most projects, this workflow file will not need changing; you simply need (~1449 tok)
- `dependabot-weekly-batch.yml` — CI: Dependabot Weekly Batch (~656 tok)
- `dossier-check.yml` — CI: Dossier Check (~830 tok)
- `pr-agent.yml` — PR Intelligence Agent — Auto-Trigger (~1116 tok)
- `pr-green-loop.yml` — CI: PR Green Loop (~1676 tok)
- `security-gate.yml` — DevSkyy Security Gate (~1704 tok)

## .husky/

- `post-checkout` (~24 tok)
- `post-commit` — post-commit hook: LFS + auto-regen of anatomy and Phase E manifest. (~709 tok)
- `post-merge` (~19 tok)
- `pre-commit` — Pre-commit: lint, type-check, syntax, and test gates (~486 tok)
- `pre-push` — git-lfs (managed by husky) — run if installed; don't short-circuit the rest. (~501 tok)

## .reports/

- `codemap-diff.txt` (~1154 tok)
- `deployment_summary.json` (~406 tok)

## .zap/

- `context.xml` (~509 tok)
- `QUICK_START.md` — DAST Quick Start Guide (~630 tok)
- `README.md` — Project documentation (~1690 tok)
- `rules.tsv` — ZAP Scan Rule Configuration for DevSkyy Platform (~1002 tok)
- `test-dast-local.sh` — Local DAST Testing Script for DevSkyy (~1740 tok)

## .zed/

- `settings.json` (~52 tok)

## PRPs/

- `.gitkeep` (~0 tok)

## PRPs/templates/

- `prp_base.md` — Purpose (~1518 tok)

## _prototype/homepage/

- `index.html` — SkyyRose homepage — section prototype (~2327 tok)
- `NOTES.md` — Homepage section prototype — THROWAWAY (~1376 tok)
- `tokens.css` — Styles: 10 rules, 85 vars, 1 media queries (~1677 tok)

## _prototype/homepage/assets/

- `home-hero-poster-720w.webp` (~4711 tok)

## _prototype/homepage/assets/branding/

- `black-rose-collection-text.webp` (~44003 tok)
- `black-rose-logo.webp` (~92240 tok)
- `love-hurts-logo.webp` (~45392 tok)
- `signature-logo.webp` (~56010 tok)
- `skyy-mascot.webp` (~9999 tok)
- `skyyrose-monogram.webp` (~52834 tok)
- `skyyrose-rose-icon.webp` (~128576 tok)
- `tsrc-lockup-static@2x.webp` (~1478 tok)

## _prototype/homepage/sections/

- `chooser.html` — Declares WITH (~12269 tok)
- `close.html` — Declares by (~11439 tok)
- `drop.html` — Declares that (~7256 tok)
- `hero.html` — Declares and (~9506 tok)
- `letter.html` — Declares asset (~9784 tok)
- `origin.html` — Declares asset (~8121 tok)
- `receipts.html` (~8507 tok)
- `ticker.html` (~4724 tok)

## _prototype/preorder/

- `index.html` — SkyyRose pre-order gateway — layout prototype (~1531 tok)
- `NOTES.md` — Pre-order gateway page prototype — THROWAWAY (~3153 tok)
- `tokens.css` — Styles: 17 rules, 85 vars, 3 media queries (~2236 tok)

## _prototype/preorder/assets/branding/

- `black-rose-logo.webp` (~92240 tok)
- `love-hurts-logo.webp` (~45392 tok)
- `signature-logo.webp` (~56010 tok)
- `skyyrose-monogram.webp` (~52834 tok)

## _prototype/preorder/assets/products/

- `br-006-onmodel.webp` (~60780 tok)
- `kids-001-onmodel.webp` (~48765 tok)
- `lh-004-onmodel.webp` (~75270 tok)
- `sg-009-onmodel.webp` (~56278 tok)

## _prototype/preorder/sections/

- `page.html` — Declares root (~8814 tok)

## agents/

- `__init__.py` (~3078 tok)
- `analytics_agent.py` — Declares AnalyticsAgent (~10317 tok)
  - class `AnalyticsAgent` L49-1001 (~10054 tok)
- `anigen_agent.py` — Pydantic: AniGenResult (40 fields) (~4442 tok)
  - class `AniGenConfig` L76-107 (~314 tok)
  - class `AniGenResult` L108-125 (~137 tok)
  - class `AniGenAgent` L126-464 (~3436 tok)
- `asset_tagging_agent.py` — VisionServiceError: tag_image (~2932 tok)
  - class `VisionServiceError` L28-33 (~26 tok)
  - class `AssetTaggingAgent` L34-295 (~2772 tok)
- `base_legacy.py` — for: has_capability, to_dict, is_ready, duration_seconds + 8 more (~5806 tok)
  - class `AgentCapability` L44-101 (~473 tok)
  - class `LLMCategory` L102-116 (~148 tok)
  - class `AgentStatus` L117-135 (~132 tok)
  - class `AgentConfig` L136-191 (~462 tok)
  - class `PlanStep` L192-235 (~330 tok)
  - class `RetrievalContext` L236-283 (~398 tok)
  - class `ExecutionResult` L284-322 (~259 tok)
  - class `ValidationResult` L323-368 (~376 tok)
  - class `SuperAgent` L369-722 (~2914 tok)
- `CLAUDE.md` — agents/ — SuperAgent layer (162 Python files) (~635 tok)
- `coding_doctor_agent.py` — HealthCheckType: to_dict, to_dict, success_rate, to_dict + 6 more (~15498 tok)
  - class `HealthCheckType` L71-83 (~77 tok)
  - class `SeverityLevel` L84-93 (~47 tok)
  - class `IssueCategory` L94-111 (~130 tok)
  - class `HealingAction` L112-130 (~154 tok)
  - class `CodeIssue` L131-160 (~259 tok)
  - class `HealingResult` L161-181 (~141 tok)
  - class `LearningEntry` L182-199 (~132 tok)
  - class `FileReview` L200-226 (~219 tok)
  - class `HealthReport` L227-276 (~554 tok)
  - class `SelfLearningEngine` L277-385 (~1109 tok)
  - class `SelfHealingEngine` L386-546 (~1706 tok)
  - class `BaseToolkit` L547-558 (~82 tok)
  - class `ECommerceToolkit` L559-652 (~1123 tok)
  - class `FinanceToolkit` L653-733 (~1056 tok)
  - class `SecurityToolkit` L734-834 (~1237 tok)
  - class `PerformanceToolkit` L835-922 (~1031 tok)
  - class `TestingToolkit` L923-989 (~787 tok)
  - class `CodingDoctorAgent` L990-1383 (~4220 tok)
  - fn `create_coding_doctor` L1384-1397 (~110 tok)
  - fn `main` L1398-1464 (~718 tok)
- `coding_doctor_toolkits.py` — from: to_dict, analyze (~30983 tok)
  - class `SeverityLevel` L29-36 (~38 tok)
  - class `IssueCategory` L37-48 (~67 tok)
  - class `CodeIssue` L49-80 (~273 tok)
  - class `ThreeJSToolkit` L81-460 (~4250 tok)
  - class `InteractiveWebToolkit` L461-805 (~3866 tok)
  - class `LLMBestPracticesKB` L806-1120 (~3614 tok)
  - class `FrontendToolkit` L1121-1231 (~1034 tok)
  - class `APIToolkit` L1232-1336 (~949 tok)
  - class `UIUXToolkit` L1337-1836 (~5110 tok)
  - class `OWASP2025Toolkit` L1837-2105 (~2779 tok)
  - class `PCIDSSToolkit` L2106-2226 (~1307 tok)
  - class `WordPressSecurityToolkit` L2227-2407 (~1836 tok)
  - class `PythonPerformanceToolkit` L2408-2576 (~1666 tok)
  - class `RenderAutomationToolkit` L2577-2771 (~1688 tok)
  - class `TexturePool` L2772-2822 (~375 tok)
  - class `SceneRecorder` L2823-3041 (~1922 tok)
- `collection_content_agent.py` — CollectionContentAgent: manage_collection, validate_collection_design, recover_collection_design, get_design_template + 2 more (~3269 tok)
  - class `CollectionContentAgent` L33-364 (~2942 tok)
  - fn `create_collection_content_agent` L365-376 (~85 tok)
- `commerce_agent.py` — Declares CommerceAgent (~10787 tok)
  - class `CommerceAgent` L58-1049 (~10452 tok)
- `creative_agent.py` — Declares import (~12692 tok)
  - class `VisualProvider` L53-62 (~64 tok)
  - class `VisualTaskType` L63-76 (~121 tok)
  - class `CreativeAgent` L77-1194 (~12177 tok)
- `errors.py` — ErrorCategory: to_dict, classify_exception, wrap_exception (~3988 tok)
  - class `ErrorCategory` L24-39 (~198 tok)
  - class `ErrorSeverity` L40-53 (~129 tok)
  - class `AgentError` L54-109 (~520 tok)
  - class `ConfigurationError` L110-132 (~159 tok)
  - class `AuthenticationError` L133-155 (~158 tok)
  - class `ValidationError` L156-181 (~190 tok)
  - class `ExecutionError` L182-207 (~194 tok)
  - class `TimeoutError` L208-231 (~177 tok)
  - class `ResourceError` L232-261 (~233 tok)
  - class `NetworkError` L262-285 (~163 tok)
  - class `DependencyError` L286-311 (~194 tok)
  - class `DataError` L312-337 (~190 tok)
  - class `PermissionError` L338-368 (~251 tok)
  - fn `classify_exception` L369-426 (~494 tok)
  - fn `wrap_exception` L427-508 (~596 tok)
- `fashn_agent.py` — Pydantic: FashnTask (53 fields) (~6374 tok)
  - class `GarmentCategory` L74-83 (~57 tok)
  - class `TryOnMode` L84-91 (~58 tok)
  - class `FashnTaskStatus` L92-102 (~58 tok)
  - class `FashnConfig` L103-147 (~455 tok)
  - class `FashnTask` L148-161 (~83 tok)
  - class `TryOnResult` L162-174 (~72 tok)
  - class `ModelGenerationResult` L175-189 (~111 tok)
  - class `FashnTryOnAgent` L190-697 (~5013 tok)
- `marketing_agent.py` — Declares MarketingAgent (~10260 tok)
  - class `MarketingAgent` L49-938 (~9997 tok)
- `meshy_agent.py` — Pydantic: MeshyTask (46 fields) (~12925 tok)
  - class `MeshyTaskStatus` L64-73 (~57 tok)
  - class `MeshyArtStyle` L74-81 (~41 tok)
  - class `MeshyTopology` L82-88 (~31 tok)
  - class `MeshyMode` L89-95 (~31 tok)
  - class `OutputFormat` L96-105 (~41 tok)
  - class `MeshyConfig` L106-187 (~1013 tok)
  - class `MeshyTask` L188-201 (~112 tok)
  - class `MeshyGenerationResult` L202-214 (~110 tok)
  - class `MeshyAssetValidation` L215-229 (~129 tok)
  - class `MeshyAgent` L230-1277 (~10686 tok)
  - fn `get_meshy_agent` L1278-1315 (~260 tok)
- `models.py` — SQLAlchemy ORM models for DevSkyy. (~4704 tok)
  - class `User` L34-78 (~521 tok)
  - class `Product` L79-119 (~464 tok)
  - class `Order` L120-161 (~472 tok)
  - class `LLMRoundTableResult` L162-200 (~443 tok)
  - class `AgentExecution` L201-240 (~427 tok)
  - class `ToolExecution` L241-290 (~539 tok)
  - class `RAGDocument` L291-332 (~500 tok)
  - class `BrandAsset` L333-395 (~680 tok)
  - class `BrandAssetIngestionJob` L396-436 (~442 tok)
- `multimodal_capabilities.py` — from: initialize, analyze_image, analyze_product_image (~4642 tok)
  - class `MultimodalProvider` L60-67 (~64 tok)
  - class `AnalysisType` L68-81 (~191 tok)
  - class `ImageAnalysisResult` L82-93 (~81 tok)
  - class `MultimodalCapabilities` L94-457 (~3588 tok)
  - fn `get_multimodal_capabilities` L458-474 (~143 tok)
- `operations_agent.py` — OperationsAgent: version (~9475 tok)
  - class `OperationsAgent` L49-912 (~9210 tok)
- `SECURITY_OPS_AGENT.md` — SecurityOpsAgent - Automated Vulnerability Management (~3211 tok)
- `security_ops_agent.py` — SecurityOpsAgent: scan_python_vulnerabilities, scan_javascript_vulnerabilities, get_dependabot_alerts, generate_security_report + 1 more (~3549 tok)
  - class `SecurityOpsAgent` L31-336 (~3363 tok)
- `skyyrose_content_agent.py` — SkyyRose Content Agent for DevSkyy Platform. (~10999 tok)
  - class `ContentType` L39-51 (~94 tok)
  - class `ContentStatus` L52-61 (~56 tok)
  - fn `_safe_collection_value` L62-101 (~360 tok)
  - class `BrandDNA` L102-228 (~1240 tok)
  - class `ContentRequest` L229-243 (~138 tok)
  - class `GeneratedContent` L244-270 (~261 tok)
  - class `SkyyRoseContentAgent` L271-1047 (~8522 tok)
- `skyyrose_imagery_agent.py` — SkyyRose Imagery Agent for DevSkyy Platform. (~6844 tok)
  - class `ImageryPurpose` L36-46 (~78 tok)
  - class `ModelPose` L47-57 (~60 tok)
  - class `ImageryRequest` L58-70 (~118 tok)
  - class `GeneratedImage` L71-86 (~106 tok)
  - class `ImageryBatch` L87-165 (~980 tok)
  - class `SkyyRoseImageryAgent` L166-637 (~5180 tok)
- `skyyrose_spaces_orchestrator.py` — SkyyRose HuggingFace Spaces Orchestrator. (~6634 tok)
  - class `ProductSpecs` L27-42 (~114 tok)
  - class `PipelineResult` L43-53 (~94 tok)
  - class `WordPressAPI` L54-190 (~1244 tok)
  - class `SkyyRoseSpacesOrchestrator` L191-651 (~4668 tok)
  - fn `deploy_product` L652-665 (~110 tok)
  - fn `main` L666-697 (~253 tok)
- `social_media_agent.py` — Declares import (~10528 tok)
  - class `Platform` L51-59 (~49 tok)
  - class `ContentType` L60-69 (~69 tok)
  - class `PostStatus` L70-283 (~2107 tok)
  - fn `_load_catalog` L284-348 (~752 tok)
  - class `SocialPost` L349-395 (~506 tok)
  - class `Campaign` L396-429 (~311 tok)
  - class `SocialMediaAgent` L430-1068 (~6276 tok)
- `support_agent.py` — Declares SupportAgent (~9197 tok)
  - class `SupportAgent` L49-841 (~8939 tok)
- `trellis_agent.py` — TRELLIS.2 subprocess wrapper for image-to-3D generation. (~3956 tok)
  - class `TrellisRunResult` L42-66 (~222 tok)
  - class `TrellisAgentError` L67-70 (~34 tok)
  - class `TrellisTimeoutError` L71-82 (~139 tok)
  - class `TrellisAgent` L83-381 (~3146 tok)
- `tripo_agent.py` — Pydantic: TripoTask (42 fields) (~15311 tok)
  - class `TripoTaskStatus` L74-83 (~53 tok)
  - class `ModelFormat` L84-94 (~81 tok)
  - class `ModelStyle` L95-104 (~50 tok)
  - class `TripoConfig` L105-198 (~1119 tok)
  - class `TripoTask` L199-215 (~111 tok)
  - class `GenerationResult` L216-231 (~101 tok)
  - class `AssetValidation` L232-246 (~130 tok)
  - class `TripoAssetAgent` L247-1404 (~13199 tok)
- `wordpress_asset_agent.py` — MediaType: from_env, execute, get_capabilities, upload_media + 3 more (~1920 tok)
  - class `MediaType` L15-21 (~29 tok)
  - class `WordPressAssetConfig` L22-40 (~161 tok)
  - class `MediaUploadResult` L41-48 (~41 tok)
  - class `ProductAssetResult` L49-56 (~53 tok)
  - class `GalleryResult` L57-64 (~49 tok)
  - class `Model3DUploadResult` L65-71 (~40 tok)
  - class `WordPressAssetAgent` L72-208 (~1450 tok)

## agents/base_super_agent/

- `__init__.py` — Declares for (~698 tok)
- `agent.py` — that: initialize (~14884 tok)
  - class `EnhancedSuperAgent` L65-1334 (~14375 tok)
- `learning_module.py` — SelfLearningModule: record_execution, get_best_technique, get_best_provider, score + 5 more (~5066 tok)
  - class `SelfLearningModule` L27-489 (~4871 tok)
- `ml_module.py` — SklearnModelWrapper: fit, predict, get_confidence, fit + 6 more (~4887 tok)
  - class `SklearnModelWrapper` L23-97 (~786 tok)
  - class `ProphetModelWrapper` L98-166 (~756 tok)
  - class `TrendExtrapolationWrapper` L167-251 (~697 tok)
  - class `MLCapabilitiesModule` L252-479 (~2501 tok)
- `prompt_module.py` — PromptEngineeringModule: auto_select_technique, apply_technique, apply_technique_with_tools, record_outcome + 1 more (~5802 tok)
  - class `PromptEngineeringModule` L38-323 (~3221 tok)
  - class `TaskCategoryAnalyzer` L324-527 (~2273 tok)
  - fn `get_task_analyzer` L528-538 (~67 tok)
- `round_table_module.py` — LLMRoundTableInterface: initialize, register_provider, set_judge, compete (~5979 tok)
  - class `LLMRoundTableInterface` L58-556 (~5484 tok)
- `types.py` — Declares import (~1772 tok)
  - class `SuperAgentType` L21-31 (~65 tok)
  - class `TaskCategory` L32-48 (~120 tok)
  - class `LLMProvider` L49-128 (~862 tok)
  - class `PromptTechniqueResult` L129-141 (~109 tok)
  - class `MLPrediction` L142-153 (~65 tok)
  - class `LearningRecord` L154-169 (~105 tok)
  - class `RoundTableEntry` L170-181 (~74 tok)
  - class `RoundTableResult` L182-211 (~207 tok)

## agents/claude_sdk/

- `__init__.py` (~1196 tok)
- `base.py` — SDKAgentConfig: run (~1341 tok)
  - class `SDKAgentConfig` L29-37 (~69 tok)
  - class `ClaudeSDKBaseAgent` L38-140 (~1107 tok)
- `dashboard.py` — Pydantic: DashboardAction (35 fields) (~5334 tok)
  - class `DashboardAction` L37-56 (~171 tok)
  - class `DashboardRequest` L57-71 (~108 tok)
  - class `ActionResult` L72-83 (~78 tok)
  - class `DashboardResult` L84-93 (~62 tok)
  - class `AgentHealthStatus` L94-103 (~55 tok)
  - class `DashboardHealthResponse` L104-119 (~115 tok)
  - class `AgentEntry` L120-129 (~53 tok)
  - class `DashboardAgentRegistry` L130-406 (~3004 tok)
  - class `DashboardOrchestrator` L407-544 (~1409 tok)
- `email_automation.py` — Pydantic: EmailTriageRequest (22 fields) (~2523 tok)
  - fn `_load_prompt` L33-41 (~75 tok)
  - class `EmailPriority` L42-49 (~37 tok)
  - class `EmailCategory` L50-59 (~62 tok)
  - class `EmailTriageRequest` L60-67 (~98 tok)
  - class `TriagedEmail` L68-81 (~87 tok)
  - class `EmailTriageResult` L82-94 (~93 tok)
  - class `IMAPClient` L95-179 (~820 tok)
  - class `EmailAutomationAgent` L180-279 (~1044 tok)
- `excel_handler.py` — Pydantic: ExcelRequest (16 fields) (~2000 tok)
  - class `ExcelOperation` L34-38 (~23 tok)
  - class `ExcelRequest` L39-58 (~177 tok)
  - class `ExcelResult` L59-75 (~142 tok)
  - fn `recalc_formulas` L76-109 (~302 tok)
  - class `ExcelHandlerAgent` L110-220 (~1136 tok)
- `hooks.py` — class: duration_s, to_dict, pre_tool_use, post_tool_use + 6 more (~3124 tok)
  - class `HookMetrics` L40-64 (~228 tok)
  - class `DevSkyyHookSystem` L65-328 (~2622 tok)
- `mixin.py` — MySubAgent: execute, to_dict (~3593 tok)
  - class `SDKExecutionResult` L49-70 (~162 tok)
  - class `SDKCapabilityMixin` L71-349 (~3060 tok)
- `research.py` — Pydantic: ResearchRequest (10 fields) (~1448 tok)
  - fn `_load_prompt` L26-35 (~88 tok)
  - class `ResearchRequest` L36-47 (~118 tok)
  - class `ResearchResult` L48-61 (~92 tok)
  - class `ResearchAgent` L62-149 (~988 tok)
- `sdk_sub_agent.py` — DeploySubAgent: execute, execute, execute_with_delegation, to_portal_node (~1834 tok)
  - class `SDKSubAgent` L46-201 (~1486 tok)
- `session.py` — Pydantic: SessionConfig (22 fields) (~1792 tok)
  - class `SessionConfig` L28-41 (~118 tok)
  - class `SessionCreateRequest` L42-51 (~78 tok)
  - class `SessionResumeRequest` L52-59 (~82 tok)
  - class `OneShotRequest` L60-66 (~65 tok)
  - class `SessionResponse` L67-79 (~93 tok)
  - class `SessionManager` L80-187 (~1154 tok)
- `tool_bridge.py` — MyAgent: for_domain, build_researcher_agent, build_analyst_agent, build_writer_agent + 2 more (~1917 tok)
  - class `ToolProfile` L32-161 (~755 tok)
  - fn `build_researcher_agent` L162-186 (~201 tok)
  - fn `build_analyst_agent` L187-203 (~166 tok)
  - fn `build_writer_agent` L204-225 (~194 tok)
  - fn `build_code_agent` L226-247 (~181 tok)
  - fn `build_domain_agents` L248-266 (~156 tok)

## agents/claude_sdk/domain_agents/

- `__init__.py` (~1184 tok)
- `analytics.py` — SDKDataAnalystAgent: execute (~1375 tok)
  - class `SDKDataAnalystAgent` L31-71 (~462 tok)
  - class `SDKReportGeneratorAgent` L72-136 (~687 tok)
- `brand_guardian.py` — Declares SDKBrandGuardianAgent (~1038 tok)
  - class `SDKBrandGuardianAgent` L25-93 (~858 tok)
- `commerce.py` — Declares SDKCatalogManagerAgent (~1306 tok)
  - class `SDKCatalogManagerAgent` L24-66 (~542 tok)
  - class `SDKPriceOptimizerAgent` L67-123 (~591 tok)
- `community.py` — Declares SDKCommunityLoyaltyAgent (~1006 tok)
  - class `SDKCommunityLoyaltyAgent` L25-91 (~823 tok)
- `content.py` — Declares SDKSeoWriterAgent (~1341 tok)
  - class `SDKSeoWriterAgent` L24-65 (~490 tok)
  - class `SDKCollectionPublisherAgent` L66-124 (~670 tok)
- `creative.py` — Declares SDKBrandAssetAgent (~1376 tok)
  - class `SDKBrandAssetAgent` L24-83 (~712 tok)
  - class `SDKDesignSystemAgent` L84-131 (~492 tok)
- `customer_intelligence.py` — Declares SDKCustomerIntelAgent (~972 tok)
  - class `SDKCustomerIntelAgent` L25-89 (~788 tok)
- `imagery.py` — Declares SDKVirtualTryOnAgent (~2039 tok)
  - class `SDKVirtualTryOnAgent` L25-86 (~799 tok)
  - class `SDKCompositorAgent` L87-131 (~525 tok)
  - class `SDKImageGenAgent` L132-181 (~520 tok)
- `immersive.py` — SDKGarment3DAgent: execute (~4741 tok)
  - class `SDKGarment3DAgent` L34-108 (~990 tok)
  - class `SDKSceneBuilderAgent` L109-243 (~1816 tok)
  - class `SDKAvatarStylistAgent` L244-376 (~1633 tok)
- `influencer.py` — SDKInfluencerAgent: execute (~1119 tok)
  - class `SDKInfluencerAgent` L23-107 (~952 tok)
- `marketing.py` — SDKCampaignAnalystAgent: execute (~1277 tok)
  - class `SDKCampaignAnalystAgent` L24-62 (~427 tok)
  - class `SDKCompetitiveIntelAgent` L63-130 (~672 tok)
- `operations.py` — SDKDeployRunnerAgent: execute (~1784 tok)
  - class `SDKDeployRunnerAgent` L25-88 (~668 tok)
  - class `SDKCodeDoctorAgent` L89-129 (~438 tok)
  - class `SDKSecurityScannerAgent` L130-175 (~478 tok)
- `seo_discovery.py` — SDKSEODiscoveryAgent: execute (~1282 tok)
  - class `SDKSEODiscoveryAgent` L27-118 (~1066 tok)
- `supply_chain.py` — Declares SDKSupplyChainAgent (~921 tok)
  - class `SDKSupplyChainAgent` L25-88 (~746 tok)
- `web_builder.py` — Declares SDKThemeDevAgent (~1348 tok)
  - class `SDKThemeDevAgent` L24-68 (~510 tok)
  - class `SDKTemplateBuilderAgent` L69-127 (~659 tok)

## agents/claude_sdk/prompts/

- `data_analyst.txt` (~429 tok)
- `email_triage.txt` (~452 tok)
- `report_writer.txt` (~448 tok)
- `research_lead.txt` (~837 tok)
- `researcher.txt` (~430 tok)

## agents/claude_sdk/utils/

- `__init__.py` — Utility modules for Claude SDK agents. (~13 tok)
- `recalc.py` — setup_libreoffice_macro, recalc, main (~1812 tok)
  - fn `setup_libreoffice_macro` L17-56 (~392 tok)
  - fn `recalc` L57-165 (~1113 tok)
  - fn `main` L166-187 (~234 tok)
- `tracker.py` — class: register_subagent_spawn, set_current_context, pre_tool_use_hook, post_tool_use_hook + 1 more (~1876 tok)
  - class `ToolCallRecord` L25-38 (~84 tok)
  - class `SubagentSession` L39-50 (~82 tok)
  - class `DevSkyySubagentTracker` L51-198 (~1564 tok)

## agents/core/

- `__init__.py` (~580 tok)
- `base.py` — CoreAgentType: categorize_failure, diagnose, heal (~7639 tok)
  - class `CoreAgentType` L51-64 (~96 tok)
  - class `FailureCategory` L65-75 (~78 tok)
  - class `CircuitBreakerState` L76-89 (~126 tok)
  - class `HealAttempt` L90-99 (~71 tok)
  - class `Diagnosis` L100-109 (~67 tok)
  - class `HealResult` L110-118 (~47 tok)
  - class `HealCycleResult` L119-128 (~69 tok)
  - class `HealthStatus` L129-168 (~431 tok)
  - fn `categorize_failure` L169-197 (~328 tok)
  - class `SelfHealingMixin` L198-514 (~3448 tok)
  - class `CoreAgent` L515-779 (~2490 tok)
- `factory.py` — create_orchestrator (~710 tok)
  - fn `create_orchestrator` L34-80 (~430 tok)
- `orchestrator.py` — Orchestrator: register_core_agent, get_core_agent, ai_bridge, set_budget_limit + 2 more (~4526 tok)
  - class `Orchestrator` L52-442 (~4042 tok)
- `sub_agent.py` — SocialMediaSubAgent: execute, execute, execute_safe, escalate_to_parent + 1 more (~2540 tok)
  - fn `_get_llm_client` L40-49 (~73 tok)
  - class `SubAgent` L50-276 (~2184 tok)
- `validation_scoring.py` — Validation scoring helpers shared across SuperAgents. (~668 tok)
  - fn `_normalize_fidelity` L26-37 (~107 tok)
  - fn `compute_validation_scores` L38-67 (~324 tok)

## agents/core/analytics/

- `__init__.py` — Analytics Core Agent — data, trends, conversion intelligence. (~67 tok)
- `agent.py` — AnalyticsCoreAgent: execute (~1769 tok)
  - class `AnalyticsCoreAgent` L21-154 (~1658 tok)

## agents/core/analytics/sub_agents/

- `__init__.py` — Analytics sub-agents: data analyst, trend predictor, conversion tracker. (~23 tok)
- `algorithm_agent.py` — class: execute, score_products, rank_content (~7126 tok)
  - class `ProductScore` L43-58 (~172 tok)
  - class `PriceRecommendation` L59-70 (~80 tok)
  - class `ContentRank` L71-82 (~98 tok)
  - class `ABTestResult` L83-104 (~182 tok)
  - class `AlgorithmSubAgent` L105-693 (~6225 tok)
- `analytics_ops.py` — AnalyticsOpsSubAgent: execute (~497 tok)
- `brand_intel_agent.py` — class: execute, profile_competitor, analyze_price_gaps (~8598 tok)
  - class `CompetitorProfile` L45-63 (~224 tok)
  - class `MarketGap` L64-75 (~102 tok)
  - class `PricePosition` L76-88 (~95 tok)
  - class `ThreatAssessment` L89-99 (~98 tok)
  - class `IntelBriefing` L100-118 (~213 tok)
  - class `BrandIntelAgent` L119-799 (~7469 tok)

## agents/core/commerce/

- `__init__.py` — Commerce Core Agent — all revenue-generating operations. (~65 tok)
- `agent.py` — CommerceCoreAgent: execute (~1557 tok)
  - class `CommerceCoreAgent` L24-145 (~1397 tok)

## agents/core/commerce/sub_agents/

- `__init__.py` — Commerce sub-agents: product, pricing, inventory, orders, WordPress bridge. (~24 tok)
- `product_ops.py` — ProductOpsSubAgent: execute (~563 tok)
  - class `ProductOpsSubAgent` L20-62 (~423 tok)
- `wordpress_assets.py` — WordPressAssetsSubAgent: execute (~369 tok)
- `wordpress_bridge.py` — WordPressBridgeSubAgent: execute (~396 tok)

## agents/core/content/

- `__init__.py` — Content Core Agent — pages, products, blogs, SEO copy. (~63 tok)
- `agent.py` — ContentCoreAgent: execute (~1356 tok)
  - class `ContentCoreAgent` L21-121 (~1243 tok)

## agents/core/content/sub_agents/

- `__init__.py` — Content sub-agents: collection content, SEO, copywriter. (~18 tok)
- `collection_content.py` — CollectionContentSubAgent: execute (~400 tok)
- `seo_copywriter.py` — SeoCopywriterSubAgent: execute (~488 tok)

## agents/core/creative/

- `__init__.py` — Creative Core Agent — visual identity, design system, brand enforcement. (~69 tok)
- `agent.py` — CreativeCoreAgent: execute (~1021 tok)
  - class `CreativeCoreAgent` L21-95 (~903 tok)

## agents/core/creative/sub_agents/

- `__init__.py` — Creative sub-agents: design system, brand guardian, asset generator, QA. (~23 tok)
- `brand_creative.py` — BrandCreativeSubAgent: execute (~585 tok)
  - class `BrandCreativeSubAgent` L20-62 (~449 tok)

## agents/core/imagery/

- `__init__.py` — Imagery & 3D Core Agent — photos, VTON, 3D model generation. (~65 tok)
- `agent.py` — ImageryCoreAgent: execute (~1597 tok)
  - class `ImageryCoreAgent` L21-138 (~1471 tok)

## agents/core/imagery/sub_agents/

- `__init__.py` — Imagery sub-agents: Gemini image, FASHN VTON, Tripo 3D, Meshy 3D, HF Spaces. (~24 tok)
- `fashn_vton.py` — FashnVtonSubAgent: execute (~517 tok)
  - class `FashnVtonSubAgent` L21-56 (~384 tok)
- `gemini_image.py` — GeminiImageSubAgent: execute (~395 tok)
- `hf_spaces.py` — HfSpacesSubAgent: execute (~376 tok)
- `meshy_3d.py` — Meshy3dSubAgent: execute (~334 tok)
- `tripo_3d.py` — Tripo3dSubAgent: execute (~347 tok)

## agents/core/marketing/

- `__init__.py` — Marketing Core Agent — campaigns, social, audience growth. (~66 tok)
- `agent.py` — MarketingCoreAgent: execute (~1181 tok)
  - class `MarketingCoreAgent` L21-111 (~1071 tok)

## agents/core/marketing/sub_agents/

- `__init__.py` — Marketing sub-agents: social media, campaign manager, A/B testing. (~21 tok)
- `campaign_ops.py` — CampaignOpsSubAgent: execute (~447 tok)
- `social_media.py` — SocialMediaSubAgent: execute (~5323 tok)
  - class `SocialMediaSubAgent` L25-527 (~5138 tok)

## agents/core/operations/

- `__init__.py` — Operations Core Agent — deploy, security, health, code quality. (~68 tok)
- `agent.py` — OperationsCoreAgent: execute (~1652 tok)
  - class `OperationsCoreAgent` L21-140 (~1535 tok)

## agents/core/operations/sub_agents/

- `__init__.py` — Operations sub-agents: deployment, security monitor, health checker, coding doctor. (~26 tok)
- `coding_doctor.py` — CodingDoctorSubAgent: execute (~370 tok)
- `deploy_health.py` — DeployHealthSubAgent: execute (~451 tok)
- `security_monitor.py` — SecurityMonitorSubAgent: execute (~385 tok)

## agents/core/shared/

- `__init__.py` — Shared capabilities available to all core agents. (~44 tok)
- `wp_ai_bridge.py` — WordPressAIBridge: generate_text, generate_image, provider_status, list_models + 4 more (~3806 tok)
  - class `WordPressAIBridge` L46-380 (~3445 tok)

## agents/core/web_builder/

- `__init__.py` — Web Builder Core Agent — theme generation, deployment, platform adapters. (~71 tok)
- `agent.py` — WebBuilderCoreAgent: execute (~1670 tok)
  - class `WebBuilderCoreAgent` L24-149 (~1505 tok)

## agents/core/web_builder/sub_agents/

- `__init__.py` — Web Builder sub-agents: frontend dev, backend dev, accessibility, performance, platform adapter. (~30 tok)
- `web_dev.py` — WebDevSubAgent: execute (~662 tok)
  - class `WebDevSubAgent` L20-74 (~513 tok)

## agents/devskyy-a2a/

- `.gitignore` — Git ignore rules (~712 tok)
- `CLAUDE.md` — agents/devskyy-a2a/ — Agent-to-Agent (A2A) framework placeholder (~871 tok)
- `Makefile` — Make build targets (~1584 tok)
- `pyproject.toml` — Python project configuration (~954 tok)
- `README.md` — Project documentation (~969 tok)

## agents/devskyy-a2a/agents/

- `__init__.py` — you may not use this file except in compliance with the License. (~177 tok)
- `agent.py` — DevSkyy A2A Coordinator (~6197 tok)
  - fn `_check_budget` L87-120 (~354 tok)
  - fn `_validate_sku` L121-143 (~205 tok)
  - fn `_skill_unavailable` L144-163 (~198 tok)
  - fn `list_products` L164-207 (~413 tok)
  - fn `semantic_search` L208-250 (~371 tok)
  - fn `product_description` L251-314 (~596 tok)
  - fn `brand_check` L315-375 (~580 tok)
  - fn `generate_3d_model` L376-424 (~402 tok)
  - fn `qa_render` L425-538 (~1015 tok)
  - fn `get_agent_card` L539-643 (~1167 tok)

## agents/devskyy-a2a/agents/app_utils/

- `telemetry.py` — you may not use this file except in compliance with the License. (~815 tok)
  - fn `setup_telemetry` L24-70 (~572 tok)
- `typing.py` — you may not use this file except in compliance with the License. (~299 tok)

## agents/devskyy-a2a/tests/eval/

- `eval_config.json` (~160 tok)

## agents/devskyy-a2a/tests/eval/evalsets/

- `basic.evalset.json` (~247 tok)
- `README.md` — Project documentation (~471 tok)
- `skill_routing.evalset.json` (~992 tok)

## agents/devskyy-a2a/tests/integration/

- `test_agent.py` — Smoke tests for the DevSkyy A2A coordinator. (~2088 tok)
  - fn `test_agent_constructs_with_expected_name` L29-33 (~51 tok)
  - fn `test_app_wraps_root_agent` L34-39 (~50 tok)
  - fn `test_agent_has_six_skills_registered` L40-53 (~133 tok)
  - fn `test_agent_card_is_valid_pydantic` L54-62 (~88 tok)
  - fn `test_agent_card_advertises_all_six_skills` L63-77 (~117 tok)
  - fn `test_agent_card_skills_are_well_formed` L78-88 (~139 tok)
  - fn `test_agent_card_url_overrides` L89-99 (~129 tok)
  - fn `test_paid_skill_rejects_missing_budget` L100-109 (~134 tok)
  - fn `generate_3d_model_below_budget` L110-122 (~166 tok)
  - fn `test_retired_sku_is_rejected` L123-130 (~91 tok)
  - fn `test_empty_sku_is_rejected` L131-142 (~141 tok)
  - fn `test_brand_check_flags_retired_tagline` L143-153 (~123 tok)
  - fn `test_brand_check_passes_clean_copy` L154-168 (~170 tok)
  - fn `test_qa_render_rejects_missing_file` L169-184 (~160 tok)
  - fn `test_list_products_allows_zero_budget` L185-193 (~117 tok)
  - fn `test_semantic_search_rejects_empty_query` L194-199 (~74 tok)

## agents/devskyy-a2a/tests/unit/

- `test_dummy.py` — you may not use this file except in compliance with the License. (~243 tok)

## agents/elite_web_builder/

- `__init__.py` (~63 tok)
- `conftest.py` — Root conftest for elite_web_builder — fully isolated from parent packages. (~328 tok)
- `director.py` — StoryStatus: from_config, add_stories, get_ready_stories, get_status_summary + 13 more (~7176 tok)
  - class `StoryStatus` L88-98 (~57 tok)
  - class `UserStory` L99-112 (~104 tok)
  - class `PRDBreakdown` L113-119 (~47 tok)
  - class `PlanningError` L120-128 (~84 tok)
  - class `ProjectReport` L129-147 (~146 tok)
  - class `DirectorConfig` L148-159 (~114 tok)
  - class `Director` L160-686 (~5381 tok)
  - fn `_load_default_routing` L687-718 (~462 tok)
- `prd.md` — Design Philosophy (MANDATORY — applies to ALL visual output) (~3630 tok)
- `pyproject.toml` — Python project configuration (~94 tok)
- `requirements.txt` — Python dependencies (~164 tok)
- `run.py` (~6337 tok)
  - fn `run` L301-436 (~1411 tok)
  - fn `main` L437-469 (~238 tok)
- `triggers.py` — Pipeline Triggers — route every pipeline build through the Elite team. (~4710 tok)
  - class `PipelineEvent` L58-68 (~72 tok)
  - class `PipelineReport` L69-114 (~388 tok)
  - fn `_resolve_agent` L115-124 (~85 tok)
  - fn `_confirm_paid_dispatch` L125-159 (~358 tok)
  - fn `_dispatch_imagery` L160-218 (~594 tok)
  - fn `_dispatch_social` L219-239 (~240 tok)
  - fn `_dispatch_theme` L240-275 (~456 tok)
  - fn `_stub_dispatch` L276-295 (~183 tok)
  - fn `_dispatch_photography` L296-313 (~186 tok)
  - fn `_dispatch_3d_garment` L314-330 (~178 tok)
  - fn `_dispatch_competitor_scout` L331-354 (~277 tok)
  - fn `_run_subprocess` L355-396 (~332 tok)
  - fn `_log_timestamp` L397-409 (~126 tok)
  - fn `_write_report` L410-432 (~241 tok)
  - fn `trigger_pipeline` L433-474 (~370 tok)

## agents/elite_web_builder/agents/

- `__init__.py` — Specialist agents for Elite Web Builder. (~792 tok)
- `accessibility.py` — Accessibility Agent — WCAG 2.2 AA/AAA, contrast, ARIA, keyboard nav. (~640 tok)
- `backend_dev.py` — Backend Dev Agent — PHP, Python, Node.js, databases, APIs, WooCommerce. (~860 tok)
- `base.py` — for: build_prompt (~610 tok)
  - class `AgentRole` L24-43 (~166 tok)
  - class `AgentCapability` L44-52 (~49 tok)
  - class `AgentOutput` L53-63 (~66 tok)
  - class `AgentSpec` L64-79 (~154 tok)
- `competitor_scout.py` — Competitor Scout Agent — Ad teardown + blueprint synthesis for SkyyRose. (~2043 tok)
- `design_system.py` — Design System Agent — color palettes, typography, spacing, design tokens. (~702 tok)
- `ecommerce_photography.py` — Ecommerce Photography Agent — Photography director for the SkyyRose brand. (~1861 tok)
- `frontend_dev.py` — Frontend Dev Agent — HTML/CSS/JS, React, Vue, block patterns, animations. (~742 tok)
- `garment_3d.py` — Garment 3D Agent — 3D rendering director for SkyyRose fashion pieces. (~2140 tok)
- `imagery.py` — Imagery Agent — Highest-level image generation for the SkyyRose brand. (~1584 tok)
- `performance.py` — Performance Agent — Core Web Vitals, asset optimization, caching. (~622 tok)
- `provider_adapters.py` — from: call, call, call, call + 2 more (~3499 tok)
  - fn `_make_httpx_client` L44-76 (~282 tok)
  - class `LLMMessage` L77-84 (~44 tok)
  - class `LLMResponse` L85-98 (~101 tok)
  - class `ProviderAdapter` L99-109 (~104 tok)
  - class `AnthropicAdapter` L110-177 (~678 tok)
  - class `GoogleAdapter` L178-272 (~961 tok)
  - class `OpenAIAdapter` L273-315 (~372 tok)
  - class `XAIAdapter` L316-368 (~436 tok)
  - fn `get_adapter` L369-385 (~144 tok)
- `qa.py` — QA Agent — E2E testing, cross-browser, visual regression, Lighthouse. (~688 tok)
- `runtime.py` — AgentRuntime: execute (~2600 tok)
  - class `AgentRuntime` L49-284 (~2098 tok)
- `seo_content.py` — SEO & Content Agent — meta tags, schema.org, copywriting, structured data. (~645 tok)
- `social_media.py` — Social Media Agent — High-level social content for the SkyyRose brand. (~1439 tok)
- `theme_builder.py` — Theme Builder Agent — Full-stack end-to-end WordPress theme ownership. (~2156 tok)

## agents/elite_web_builder/config/

- `learning_journal.json` (~60 tok)
- `provider_routing.json` (~264 tok)
- `quality_gates.json` (~520 tok)

## agents/elite_web_builder/core/

- `__init__.py` — Core infrastructure for Elite Web Builder. (~14 tok)
- `cost_tracker.py` — from: records, total_cost, total_input_tokens, total_output_tokens + 5 more (~1599 tok)
  - class `TokenRecord` L60-71 (~55 tok)
  - class `CostSummary` L72-88 (~123 tok)
  - class `CostTracker` L89-185 (~920 tok)
- `gate_checkers.py` — check_build, check_lint, check_security, check_diff (~5429 tok)
  - fn `check_build` L43-116 (~682 tok)
  - fn `_check_balanced` L117-144 (~249 tok)
  - fn `_try_php_lint` L145-186 (~521 tok)
  - fn `check_lint` L187-256 (~688 tok)
  - fn `check_security` L257-318 (~545 tok)
  - fn `check_diff` L319-414 (~799 tok)
  - fn `check_a11y` L415-483 (~646 tok)
  - fn `check_perf` L484-531 (~392 tok)
  - fn `build_gate_checkers` L532-593 (~527 tok)
- `ground_truth.py` — URL configuration (~5885 tok)
  - class `ClaimType` L40-53 (~109 tok)
  - class `ValidationSeverity` L54-62 (~48 tok)
  - class `ValidationResult` L63-91 (~258 tok)
  - fn `_is_valid_color` L92-137 (~437 tok)
  - fn `_has_spaces` L138-142 (~30 tok)
  - fn `_has_double_slashes_in_path` L143-166 (~237 tok)
  - class `GroundTruthValidator` L167-248 (~812 tok)
  - fn `_verify_file_exists` L249-278 (~270 tok)
  - fn `_verify_color_value` L279-297 (~178 tok)
  - fn `_verify_css_value` L298-337 (~368 tok)
  - fn `_verify_font_name` L338-391 (~520 tok)
  - fn `_verify_json_validity` L392-414 (~212 tok)
  - fn `_verify_api_endpoint` L415-473 (~494 tok)
  - fn `_verify_import_path` L474-509 (~384 tok)
  - fn `_verify_php_syntax` L510-570 (~538 tok)
  - fn `_verify_html_validity` L571-639 (~646 tok)
- `learning_journal.py` — from: to_dict, from_dict, to_dict, entries + 7 more (~2351 tok)
  - class `JournalEntry` L40-78 (~304 tok)
  - class `Instinct` L79-105 (~201 tok)
  - class `LearningJournal` L106-261 (~1506 tok)
- `model_router.py` — ProviderStatus: avg_latency, from_dict, from_json_file, get_health + 10 more (~3551 tok)
  - class `ProviderStatus` L40-48 (~49 tok)
  - class `ProviderConfig` L49-56 (~36 tok)
  - class `RouteResult` L57-65 (~47 tok)
  - class `ProviderHealth` L66-91 (~224 tok)
  - class `RoutingConfig` L92-125 (~358 tok)
  - class `ModelRouter` L126-363 (~2505 tok)
- `output_writer.py` — URL configuration (~3100 tok)
  - class `ExtractedFile` L94-102 (~42 tok)
  - class `WriteResult` L103-152 (~431 tok)
  - class `OutputWriter` L153-364 (~2022 tok)
- `ralph_integration.py` — from: to_dict, execute, execute_with_fallback (~1806 tok)
  - class `RalphConfig` L37-46 (~56 tok)
  - class `ExecutionResult` L47-70 (~193 tok)
  - class `RalphExecutor` L71-208 (~1271 tok)
- `self_healer.py` — FailureCategory: categorize, diagnose, heal (~2683 tok)
  - class `FailureCategory` L43-52 (~107 tok)
  - class `HealAttempt` L53-61 (~45 tok)
  - class `Diagnosis` L62-70 (~55 tok)
  - class `HealResult` L71-79 (~46 tok)
  - class `HealCycleResult` L80-127 (~517 tok)
  - class `SelfHealer` L128-283 (~1580 tok)
- `verification_loop.py` — Gate: passed, is_enabled, all_green, passed_count + 6 more (~2184 tok)
  - class `Gate` L40-52 (~66 tok)
  - class `GateStatus` L53-66 (~106 tok)
  - class `GateResult` L67-82 (~111 tok)
  - class `VerificationConfig` L83-100 (~166 tok)
  - class `VerificationReport` L101-152 (~449 tok)
  - class `VerificationLoop` L153-251 (~910 tok)

## agents/elite_web_builder/custom_instincts/

- `.gitkeep` (~0 tok)

## agents/elite_web_builder/evals/

- `wordpress_theme_colors.md` — Eval: WordPress Theme Colors (~242 tok)

## agents/elite_web_builder/instincts/

- `.gitkeep` (~0 tok)

## agents/elite_web_builder/knowledge/

- `canonical_catalog.md` — Canonical Catalog — Elite Web Builder Reference (~873 tok)
- `competitor_intel.md` — Competitor Intelligence — Knowledge Base (~2161 tok)
- `ecommerce_photography.md` — Ecommerce Photography — Knowledge Base (~2318 tok)
- `garment_3d.md` — 3D Fashion Garment Rendering — Knowledge Base (~2175 tok)
- `performance_budgets.md` — Performance Budgets (~550 tok)
- `photo_generation.md` — AI Photo Generation Pipeline — SkyyRose Elite Production Studio (~2567 tok)
- `security_checklist.md` — Security Checklist (OWASP Top 10 for Web Themes) (~756 tok)
- `shopify_themes.md` — Shopify Themes — Knowledge Base (~2331 tok)
- `social_media.md` — Social Media Agent — Knowledge Reference (~1300 tok)
- `wcag_checklist.md` — WCAG 2.2 AA Checklist (~722 tok)
- `wordpress_deployment.md` — WordPress Build Specification — SkyyRose Flagship Theme (~10677 tok)
- `wordpress.md` — WordPress Knowledge Base — SkyyRose Production (~2699 tok)

## agents/elite_web_builder/output/

- `last_report.json` (~2093 tok)

## agents/elite_web_builder/templates/shopify/

- `settings_schema_starter.json` (~288 tok)

## agents/elite_web_builder/templates/wordpress/

- `functions-starter.php` — Theme functions starter template. (~530 tok)
- `theme-json-starter.json` (~568 tok)

## agents/elite_web_builder/tests/

- `__init__.py` — Tests for Elite Web Builder. (~10 tok)
- `conftest.py` — Test configuration — completely isolate from parent packages. (~145 tok)
- `test_agent_runtime.py` — Tests for AgentRuntime — the bridge from AgentSpec to LLM execution. (~2954 tok)
  - fn `routing_config` L20-35 (~152 tok)
  - fn `router` L36-40 (~26 tok)
  - fn `validator` L41-45 (~20 tok)
  - fn `journal` L46-50 (~26 tok)
  - fn `runtime` L51-55 (~39 tok)
  - fn `frontend_spec` L56-72 (~133 tok)
  - fn `design_spec` L73-85 (~101 tok)
  - class `TestBuildMessages` L86-129 (~506 tok)
  - class `TestExecute` L130-250 (~1234 tok)
  - class `TestExtractFiles` L251-276 (~248 tok)
  - class `TestRuntimeRouterIntegration` L277-303 (~286 tok)
- `test_base_agents.py` — Tests for agents/base.py — AgentRole, AgentSpec, AgentOutput, AgentCapability. (~1630 tok)
  - class `TestAgentRole` L14-47 (~296 tok)
  - class `TestAgentCapability` L48-72 (~239 tok)
  - class `TestAgentOutput` L73-104 (~324 tok)
  - class `TestAgentSpec` L105-174 (~661 tok)
- `test_context7_bridge.py` — Tests for tools/context7_bridge.py — Context7 documentation lookup. (~4074 tok)
  - class `TestLibraryInfo` L25-59 (~283 tok)
  - class `TestDocSnippet` L60-89 (~268 tok)
  - class `TestBridgeConstruction` L90-108 (~186 tok)
  - class `TestResolveLibrary` L109-216 (~1175 tok)
  - class `TestQueryDocs` L217-324 (~1246 tok)
  - class `TestLookup` L325-361 (~365 tok)
  - class `TestErrorHandling` L362-390 (~380 tok)
- `test_cost_tracker.py` — Tests for core.cost_tracker — token usage and cost tracking. (~1314 tok)
  - class `TestComputeCost` L10-39 (~373 tok)
  - class `TestRecord` L40-69 (~380 tok)
  - class `TestSummary` L70-97 (~306 tok)
  - class `TestToDict` L98-110 (~110 tok)
  - class `TestReset` L111-119 (~92 tok)
- `test_director.py` — Tests for director.py — Director, UserStory, StoryStatus, PRDBreakdown. (~5894 tok)
  - class `TestStoryStatus` L25-39 (~136 tok)
  - class `TestUserStory` L40-80 (~407 tok)
  - class `TestPRDBreakdown` L81-110 (~274 tok)
  - class `TestDirectorCreation` L111-145 (~396 tok)
  - class `TestDirectorStoryManagement` L146-259 (~1109 tok)
  - class `TestDirectorExecution` L260-377 (~1140 tok)
  - class `TestDefaultRouting` L378-418 (~395 tok)
  - class `TestDirectorRuntimeIntegration` L419-593 (~1856 tok)
- `test_execute_prd.py` — Tests for execute_prd pipeline — PlanningError, ProjectReport, planning, execution. (~5990 tok)
  - fn `_valid_planning_json` L26-44 (~207 tok)
  - fn `_make_mock_adapter` L45-61 (~153 tok)
  - class `TestPlanningError` L62-84 (~225 tok)
  - class `TestProjectReport` L85-146 (~534 tok)
  - class `TestParsePlanningResponse` L147-181 (~436 tok)
  - class `TestBuildBreakdown` L182-274 (~910 tok)
  - class `TestPlanStories` L275-330 (~668 tok)
  - class `TestExecutePrd` L331-586 (~2480 tok)
  - class `TestDirectorConfigMaxStories` L587-605 (~204 tok)
- `test_gate_checkers.py` — Tests for core.gate_checkers — concrete gate checker implementations. (~3252 tok)
  - class `TestCheckBuild` L25-96 (~866 tok)
  - class `TestCheckLint` L97-142 (~572 tok)
  - class `TestCheckSecurity` L143-177 (~431 tok)
  - class `TestCheckDiff` L178-205 (~280 tok)
  - class `TestCheckA11y` L206-239 (~409 tok)
  - class `TestCheckPerf` L240-259 (~230 tok)
  - class `TestBuildGateCheckers` L260-282 (~311 tok)
- `test_ground_truth.py` — Tests for core/ground_truth.py — Anti-hallucination validator. (~9459 tok)
  - fn `validator` L29-33 (~27 tok)
  - fn `temp_dir` L34-103 (~626 tok)
  - class `TestClaimType` L104-125 (~179 tok)
  - class `TestValidationResult` L126-151 (~262 tok)
  - class `TestUnknownClaimType` L152-169 (~226 tok)
  - class `TestFileExists` L170-210 (~464 tok)
  - class `TestColorValue` L211-321 (~1542 tok)
  - class `TestCSSValue` L322-359 (~438 tok)
  - class `TestFontName` L360-409 (~603 tok)
  - class `TestJSONValidity` L410-448 (~449 tok)
  - class `TestAPIEndpoint` L449-515 (~852 tok)
  - class `TestImportPath` L516-581 (~770 tok)
  - class `TestPHPSyntax` L582-624 (~522 tok)
  - class `TestHTMLValidity` L625-694 (~910 tok)
  - class `TestInputSanitization` L695-725 (~374 tok)
  - class `TestVerifyAllOrFail` L726-752 (~282 tok)
  - class `TestBatchValidation` L753-785 (~361 tok)
  - class `TestValidationSummary` L786-814 (~366 tok)
- `test_integration.py` — Integration test — end-to-end run with a minimal test PRD. (~5511 tok)
  - fn `director` L45-49 (~23 tok)
  - fn `mini_prd_stories` L50-92 (~421 tok)
  - class `TestStoryLifecycle` L93-135 (~472 tok)
  - class `TestAgentExecutionPipeline` L136-251 (~1239 tok)
  - class `TestMultiProviderRouting` L252-273 (~251 tok)
  - class `TestGroundTruthIntegration` L274-310 (~416 tok)
  - class `TestLearningIntegration` L311-357 (~494 tok)
  - class `TestVerificationIntegration` L358-403 (~506 tok)
  - class `TestSelfHealIntegration` L404-439 (~350 tok)
  - class `TestRalphIntegration` L440-477 (~369 tok)
  - class `TestFullPipeline` L478-535 (~550 tok)
  - fn `_make_gate_result` L536-542 (~66 tok)
- `test_learning_journal.py` — Tests for core/learning_journal.py — Boris Cherny protocol + instinct extraction. (~2448 tok)
  - fn `journal` L18-22 (~33 tok)
  - fn `sample_entry` L23-37 (~128 tok)
  - class `TestJournalEntry` L38-72 (~390 tok)
  - class `TestJournalOperations` L73-150 (~698 tok)
  - class `TestPersistence` L151-177 (~297 tok)
  - class `TestInstinctExtraction` L178-229 (~581 tok)
  - class `TestContextGeneration` L230-248 (~209 tok)
- `test_lighthouse_runner.py` — Tests for tools/lighthouse_runner.py — Lighthouse performance measurement. (~5533 tok)
  - fn `_make_result` L86-123 (~325 tok)
  - class `TestLighthouseResult` L124-174 (~534 tok)
  - class `TestRunLighthouse` L175-340 (~2070 tok)
  - class `TestCheckPerformanceBudget` L341-451 (~1292 tok)
  - class `TestFormatReport` L452-513 (~607 tok)
- `test_model_router.py` — Tests for core/model_router.py — Multi-provider routing + fallback chain. (~2862 tok)
  - fn `routing_config` L20-42 (~357 tok)
  - fn `router` L43-51 (~84 tok)
  - class `TestProviderConfig` L52-68 (~186 tok)
  - class `TestRoutingResolution` L69-104 (~356 tok)
  - class `TestFallbackChain` L105-130 (~285 tok)
  - class `TestProviderHealth` L131-171 (~490 tok)
  - class `TestAsyncProviderCall` L172-245 (~754 tok)
  - class `TestConfigLoading` L246-269 (~229 tok)
- `test_new_specs.py` — Structural tests for the three new Elite Team specialists. (~2035 tok)
  - fn `_load_package_all_specs` L21-58 (~440 tok)
  - class `TestNewAgentRoles` L59-80 (~256 tok)
  - class `TestNewSpecsStructure` L81-131 (~668 tok)
  - class `TestAllSpecsTuple` L132-174 (~495 tok)
- `test_output_writer.py` — Tests for core.output_writer — filesystem output writer. (~2871 tok)
  - class `TestExtractedFile` L20-37 (~181 tok)
  - class `TestExtractFiles` L38-124 (~1008 tok)
  - class `TestValidatePath` L125-163 (~414 tok)
  - class `TestValidateContent` L164-177 (~135 tok)
  - class `TestWriteFile` L178-221 (~548 tok)
  - class `TestExtractAndWrite` L222-257 (~470 tok)
- `test_provider_adapters.py` — Tests for provider adapters — multi-provider LLM calling layer. (~2910 tok)
  - class `TestLLMMessage` L22-33 (~103 tok)
  - class `TestLLMResponse` L34-61 (~245 tok)
  - class `TestAnthropicAdapter` L62-147 (~928 tok)
  - class `TestGoogleAdapter` L148-197 (~480 tok)
  - class `TestOpenAIAdapter` L198-244 (~478 tok)
  - class `TestXAIAdapter` L245-280 (~359 tok)
  - class `TestGetAdapter` L281-301 (~181 tok)
- `test_ralph_integration.py` — Tests for core/ralph_integration.py — ADK agents to ralph-tui adapter. (~1719 tok)
  - fn `executor` L23-27 (~28 tok)
  - fn `custom_executor` L28-42 (~105 tok)
  - class `TestRalphConfig` L43-60 (~166 tok)
  - class `TestExecuteWithRetry` L61-114 (~518 tok)
  - class `TestExecuteWithFallback` L115-159 (~550 tok)
  - class `TestExecutionResult` L160-180 (~194 tok)
- `test_screenshot_diff.py` — Tests for tools/screenshot_diff.py — Visual regression testing tool. (~4792 tok)
  - fn `_save_solid_image` L29-39 (~79 tok)
  - fn `_save_half_red_half_blue` L40-55 (~164 tok)
  - class `TestDiffResult` L56-116 (~548 tok)
  - class `TestCompareIdentical` L117-149 (~398 tok)
  - class `TestCompareDifferent` L150-206 (~699 tok)
  - class `TestCompareSizeMismatch` L207-231 (~300 tok)
  - class `TestCompareErrors` L232-260 (~352 tok)
  - class `TestCaptureScreenshot` L261-320 (~689 tok)
  - class `TestRunVisualRegression` L321-450 (~1348 tok)
- `test_self_healer.py` — Tests for core/self_healer.py — Diagnose → categorize → route → retry loop. (~2878 tok)
  - fn `healer` L27-31 (~24 tok)
  - fn `failing_report` L32-62 (~353 tok)
  - class `TestFailureCategory` L63-74 (~116 tok)
  - class `TestDiagnosis` L75-110 (~404 tok)
  - class `TestHealCycle` L111-246 (~1357 tok)
  - class `TestCategoryRouting` L247-286 (~469 tok)
- `test_specialist_agents.py` — Tests for all 7 specialist agent specs — verify role, prompt, capabilities. (~2346 tok)
  - class `TestAllSpecs` L31-76 (~468 tok)
  - class `TestDesignSystem` L77-100 (~256 tok)
  - class `TestFrontendDev` L101-120 (~203 tok)
  - class `TestBackendDev` L121-141 (~223 tok)
  - class `TestAccessibility` L142-161 (~197 tok)
  - class `TestPerformance` L162-181 (~195 tok)
  - class `TestSeoContent` L182-201 (~195 tok)
  - class `TestQA` L202-225 (~226 tok)
  - class `TestLearningInjection` L226-234 (~120 tok)
- `test_template_scaffold.py` — Tests for tools/template_scaffold.py — WordPress, Shopify, and component scaffolding. (~4575 tok)
  - class `TestScaffoldFileImmutability` L26-42 (~193 tok)
  - class `TestScaffoldResultImmutability` L43-86 (~419 tok)
  - class `TestScaffoldWordPressTemplate` L87-167 (~1020 tok)
  - class `TestScaffoldShopifyTemplate` L168-233 (~816 tok)
  - class `TestScaffoldComponent` L234-314 (~1043 tok)
  - class `TestListTemplates` L315-362 (~496 tok)
  - class `TestEdgeCases` L363-394 (~400 tok)
- `test_tools.py` — Tests for tools/ — contrast checker, file validator, type scale, spacing scale. (~1546 tok)
  - class `TestHexToRgb` L27-37 (~88 tok)
  - class `TestRelativeLuminance` L38-45 (~75 tok)
  - class `TestCheckContrast` L46-79 (~318 tok)
  - class `TestFileValidator` L80-120 (~424 tok)
  - class `TestTypeScale` L121-147 (~228 tok)
  - class `TestSpacingScale` L148-169 (~228 tok)
- `test_triggers_dispatch.py` — Phase 3 tests for triggers.py dispatch routing. (~1315 tok)
  - class `TestAgentForKindMap` L27-50 (~295 tok)
  - class `TestNewDispatchers` L51-88 (~387 tok)
  - class `TestThemeDualPlatform` L89-121 (~347 tok)
  - class `TestInvalidKind` L122-126 (~59 tok)
- `test_verification_loop.py` — Tests for core/verification_loop.py — 8-gate quality check. (~2658 tok)
  - fn `default_config` L26-31 (~37 tok)
  - fn `loop` L32-40 (~87 tok)
  - class `TestGateEnum` L41-53 (~130 tok)
  - class `TestGateResult` L54-87 (~302 tok)
  - class `TestVerificationConfig` L88-111 (~291 tok)
  - class `TestRunGate` L112-159 (~514 tok)
  - class `TestFullRun` L160-229 (~680 tok)
  - class `TestVerificationReport` L230-263 (~453 tok)

## agents/elite_web_builder/tools/

- `__init__.py` — Verification and utility tools for Elite Web Builder. (~18 tok)
- `context7_bridge.py` — Context7 documentation bridge — anti-hallucination for library code. (~2108 tok)
  - class `Context7Error` L38-47 (~90 tok)
  - class `LibraryInfo` L48-58 (~56 tok)
  - class `DocSnippet` L59-73 (~95 tok)
  - class `Context7Bridge` L74-238 (~1564 tok)
- `contrast_checker.py` — ContrastResult: hex_to_rgb, relative_luminance, linearize, contrast_ratio + 2 more (~721 tok)
  - class `ContrastResult` L18-30 (~74 tok)
  - fn `hex_to_rgb` L31-38 (~80 tok)
  - fn `relative_luminance` L39-49 (~111 tok)
  - fn `contrast_ratio` L50-58 (~90 tok)
  - fn `wcag_level` L59-69 (~72 tok)
  - fn `check_contrast` L70-93 (~185 tok)
- `file_validator.py` — from: validate_file_exists, validate_json_file, validate_no_secrets (~711 tok)
  - class `FileValidationResult` L17-36 (~152 tok)
  - fn `validate_file_exists` L37-44 (~91 tok)
  - fn `validate_json_file` L45-61 (~167 tok)
  - fn `validate_no_secrets` L62-82 (~201 tok)
- `lighthouse_runner.py` — Lighthouse performance measurement tool for Elite Web Builder. (~2789 tok)
  - class `LighthouseError` L59-68 (~90 tok)
  - class `LighthouseResult` L69-86 (~135 tok)
  - fn `_get_timestamp` L87-91 (~38 tok)
  - fn `_build_command` L92-112 (~137 tok)
  - fn `_extract_score` L113-124 (~96 tok)
  - fn `_extract_metrics` L125-134 (~113 tok)
  - fn `_extract_failed_audits` L135-154 (~176 tok)
  - fn `_parse_report` L155-188 (~332 tok)
  - fn `run_lighthouse` L189-238 (~480 tok)
  - fn `check_performance_budget` L239-280 (~375 tok)
  - fn `format_report` L281-327 (~384 tok)
- `screenshot_diff.py` — from: capture_screenshot, compare_screenshots, run_visual_regression (~2720 tok)
  - class `DiffResult` L41-57 (~121 tok)
  - fn `_validate_file_exists` L58-65 (~74 tok)
  - fn `_validate_dir_exists` L66-73 (~75 tok)
  - fn `_url_to_filename` L74-88 (~161 tok)
  - fn `capture_screenshot` L89-141 (~424 tok)
  - fn `_load_and_normalize` L142-162 (~210 tok)
  - fn `_compute_pixel_diff` L163-198 (~316 tok)
  - fn `compare_screenshots` L199-248 (~490 tok)
  - fn `run_visual_regression` L249-299 (~504 tok)
- `spacing_scale.py` — generate_spacing_scale (~299 tok)
- `template_scaffold.py` — Template scaffolding tool — WordPress, Shopify, and frontend components. (~6256 tok)
  - class `ScaffoldError` L29-38 (~92 tok)
  - class `ScaffoldFile` L39-46 (~42 tok)
  - class `ScaffoldResult` L47-61 (~108 tok)
  - fn `_validate_name` L62-68 (~72 tok)
  - fn `_slugify` L69-97 (~236 tok)
  - fn `_wp_page` L98-133 (~371 tok)
  - fn `_wp_archive` L134-158 (~298 tok)
  - fn `_wp_single` L159-178 (~243 tok)
  - fn `_wp_template_part` L179-191 (~146 tok)
  - fn `_wp_block_pattern` L192-257 (~588 tok)
  - fn `_shopify_json_template` L258-274 (~127 tok)
  - fn `_shopify_page` L275-281 (~92 tok)
  - fn `_shopify_collection` L282-288 (~98 tok)
  - fn `_shopify_product` L289-295 (~95 tok)
  - fn `_shopify_section` L296-330 (~307 tok)
  - fn `_shopify_snippet` L331-362 (~285 tok)
  - fn `_component_react` L363-401 (~395 tok)
  - fn `_component_vue` L402-441 (~359 tok)
  - fn `_component_vanilla` L442-488 (~455 tok)
  - fn `scaffold_wordpress_template` L489-533 (~390 tok)
  - fn `scaffold_shopify_template` L534-578 (~392 tok)
  - fn `scaffold_component` L579-621 (~372 tok)
  - fn `list_templates` L622-653 (~462 tok)
- `type_scale.py` — generate_type_scale (~336 tok)

## agents/llm_roundtable/

- `.gitignore` — Git ignore rules (~14 tok)
- `adaptive.ts` — Adaptive Intelligence Module — Self-Healing, Self-Learning, Self-Correcting (~4687 tok)
  - section `LearningRecord` L45-58 (~87 tok)
  - section `RoutingWeight` L59-69 (~80 tok)
  - section `CircuitBreaker` L70-78 (~75 tok)
  - section `CorrectionRecord` L79-95 (~162 tok)
  - fn `recoverFile` L96-126 (~285 tok)
  - fn `recordLearning` L127-137 (~113 tok)
  - fn `updateRoutingWeights` L138-216 (~776 tok)
  - fn `getLearnedRoute` L217-230 (~154 tok)
  - fn `isModelDisabled` L231-252 (~189 tok)
  - fn `recordFailure` L253-290 (~318 tok)
  - fn `recordSuccess` L291-304 (~128 tok)
  - fn `getFallbackModel` L305-320 (~129 tok)
  - fn `withRetry` L321-348 (~242 tok)
  - fn `isAnomalousScore` L349-379 (~304 tok)
  - fn `isTechniqueUnderperforming` L380-441 (~606 tok)
  - fn `checkEloHealth` L442-464 (~228 tok)
  - fn `logCorrection` L465-473 (~77 tok)
  - fn `getRecentCorrections` L474-480 (~58 tok)
  - fn `getHealthReport` L481-494 (~128 tok)
- `agent.ts` — LLM Roundtable Agent (~3185 tok)
  - fn `main` L170-237 (~567 tok)
- `engine.ts` — LLM Roundtable — Live Battle Engine (~13440 tok)
  - fn `applyChainOfThought` L156-169 (~123 tok)
  - fn `applyTreeOfThoughts` L170-192 (~145 tok)
  - fn `applyReAct` L193-208 (~134 tok)
  - fn `applyRAG` L209-223 (~138 tok)
  - fn `applyFewShot` L224-238 (~122 tok)
  - fn `applyStructuredOutput` L239-255 (~159 tok)
  - fn `applyConstitutional` L256-274 (~225 tok)
  - fn `applyRoleBased` L275-285 (~90 tok)
  - fn `applySelfConsistency` L286-296 (~98 tok)
  - fn `applyEnsemble` L297-321 (~197 tok)
  - fn `applyTechnique` L322-365 (~412 tok)
  - fn `autoSelectTechnique` L366-377 (~153 tok)
  - section `ModelConfig` L378-398 (~346 tok)
  - section `CompetitorResult` L399-408 (~49 tok)
  - section `JudgeScore` L409-415 (~35 tok)
  - section `Battle` L416-428 (~71 tok)
  - section `TechniqueBattle` L429-443 (~82 tok)
  - section `EloEntry` L444-452 (~38 tok)
  - section `TechniqueStats` L453-463 (~109 tok)
  - fn `callAnthropic` L464-502 (~298 tok)
  - fn `callOpenAI` L503-531 (~360 tok)
  - fn `callGoogle` L532-564 (~398 tok)
  - fn `callModel` L565-618 (~484 tok)
  - fn `judgeResponses` L619-688 (~550 tok)
  - fn `getTechniqueDescription` L689-707 (~275 tok)
  - fn `updateElo` L708-745 (~416 tok)
  - fn `updateTechniqueStats` L746-779 (~274 tok)
  - fn `runBattle` L780-932 (~1598 tok)
  - fn `runTechniqueBattle` L933-1057 (~1081 tok)
  - fn `getCriteria` L1058-1346 (~3312 tok)
- `index.ts` — LLM Roundtable — Public API (~148 tok)
- `package.json` — Node.js package manifest (~158 tok)
- `schemas.ts` — LLM Roundtable — Input Validation Schemas (~513 tok)
- `tsconfig.json` — TypeScript configuration (~143 tok)
- `utils.ts` — LLM Roundtable — Shared Persistence Utilities (~446 tok)

## agents/llm_roundtable/ui/

- `LLMRoundtable.tsx` — @ts-nocheck (~12744 tok)
  - fn `getModel` L119-119 (~19 tok)
  - fn `cc` L120-120 (~28 tok)
  - fn `sc` L121-122 (~38 tok)
  - fn `Pulse` L123-126 (~74 tok)
  - fn `Bar` L127-132 (~77 tok)
  - fn `Tag` L133-144 (~136 tok)
  - fn `LLMRoundtable` L145-695 (~9620 tok)

## agents/render_pipeline/

- `__init__.py` — RenderPipeline ADK agent — generates validated product renders for SkyyRose SKUs. (~262 tok)
- `agent.py` — RenderPipeline ADK agent — root_agent definition. (~5549 tok)
  - class `InfraFailure` L97-110 (~142 tok)
  - class `RenderResult` L111-143 (~498 tok)
  - class `StopChecker` L144-411 (~3609 tok)
- `cli.py` — External CLI driver for the RenderPipeline ADK agent. (~3428 tok)
  - fn `_load_env_files` L45-73 (~310 tok)
  - fn `_make_state_shim` L74-84 (~126 tok)
  - fn `_preflight` L85-135 (~690 tok)
  - fn `_stop_and_show` L136-191 (~709 tok)
  - fn `_run_agent` L192-239 (~483 tok)
  - fn `main` L240-308 (~708 tok)
- `DESIGN.md` — RenderPipeline — Google ADK Agent (~3003 tok)
- `README.md` — Project documentation (~1056 tok)

## agents/render_pipeline/eval/

- `__init__.py` — ADK AgentEvaluator harness for the RenderPipeline agent. (~96 tok)
- `render_pipeline.evalset.json` (~523 tok)
- `test_config.json` (~27 tok)
- `test_render_pipeline.py` — Live integration eval — gated by EVAL_LIVE=1 environment variable. (~608 tok)
  - fn `test_render_pipeline_live_br001` L39-60 (~251 tok)

## agents/render_pipeline/learning/

- `__init__.py` — Continuous-improvement subsystem for the RenderPipeline agent. (~714 tok)
- `LOOP.md` — Learning Loop (~1242 tok)
- `proposals.py` — Propose catalog amendments from the learning loops' history. (~1693 tok)
  - fn `_read_jsonl` L22-27 (~51 tok)
  - fn `propose_engine_overrides` L28-75 (~531 tok)
  - fn `digest_failure_modes` L76-114 (~430 tok)
  - fn `write_proposals_markdown` L115-155 (~496 tok)
- `recorder.py` — Append-only structured recorders for the three learning loops. (~857 tok)
  - fn `_append_jsonl` L22-29 (~87 tok)
  - fn `record_engine_outcome` L30-54 (~196 tok)
  - fn `record_template_score` L55-72 (~152 tok)
  - fn `record_failure_mode` L73-98 (~237 tok)

## agents/render_pipeline/tests/

- `__init__.py` — Mock-based unit tests for the RenderPipeline tool functions. (~102 tok)
- `test_tools.py` — Mock-based unit tests for the 9 RenderPipeline tool functions. (~8610 tok)
  - fn `_make_ctx` L39-49 (~131 tok)
  - fn `test_load_dossier_fn_writes_state_and_returns_summary` L50-84 (~417 tok)
  - fn `test_load_dossier_fn_no_engine_override_when_blank` L85-106 (~213 tok)
  - fn `test_load_dossier_fn_propagates_dossier_missing` L107-123 (~178 tok)
  - fn `test_resolve_source_fn_writes_path_to_state` L124-147 (~244 tok)
  - fn `test_resolve_source_fn_returns_error_when_no_image_found` L148-165 (~160 tok)
  - fn `test_resolve_builds_candidates_under_wp_products_dir` L166-185 (~232 tok)
  - fn `test_route_engine_fn_uses_catalog_override_when_pinned` L186-201 (~187 tok)
  - fn `test_route_engine_fn_falls_through_to_vision_routing` L202-227 (~281 tok)
  - fn `test_route_engine_fn_returns_error_when_no_decisions` L228-246 (~214 tok)
  - fn `test_articulate_layer0_fn_uses_fallback_when_no_anthropic_key` L247-268 (~230 tok)
  - fn `test_articulate_layer0_fn_calls_sonnet_when_key_present` L269-302 (~358 tok)
  - fn `test_articulate_layer0_fn_falls_back_on_sonnet_error` L303-330 (~276 tok)
  - fn `test_build_prompt_fn_uses_sonnet_layer0_when_present` L331-361 (~378 tok)
  - fn `test_build_prompt_fn_falls_back_to_registry_when_no_sonnet_l0` L362-394 (~389 tok)
  - fn `test_generate_image_fn_returns_error_when_state_missing` L395-403 (~93 tok)
  - fn `test_generate_image_fn_unsupported_engine_returns_error` L404-412 (~114 tok)
  - fn `test_generate_image_fn_dispatches_gemini_pro_to_gen_function` L413-441 (~355 tok)
  - fn `test_qa_tournament_fn_records_to_learning_loops` L442-488 (~531 tok)
  - fn `test_qa_tournament_fn_records_failure_mode_on_low_score` L489-530 (~468 tok)
  - fn `test_qa_tournament_fn_surfaces_infra_failures` L531-574 (~496 tok)
  - fn `test_qa_tournament_fn_returns_error_on_missing_state` L575-587 (~134 tok)
  - fn `test_refine_image_fn_uses_kontext_first` L588-619 (~332 tok)
  - fn `test_refine_image_fn_falls_back_to_gemini_composite` L620-651 (~318 tok)
  - fn `test_refine_image_fn_returns_error_when_no_candidate` L652-659 (~82 tok)
  - fn `test_refine_image_fn_builds_synthesis_aware_prompt` L660-684 (~284 tok)
  - fn `test_vision_consensus_merge_unions_colors_and_graphics` L685-731 (~460 tok)
  - fn `test_vision_consensus_merge_handles_one_provider_failure` L732-750 (~157 tok)
  - fn `test_vision_consensus_fn_uses_disk_cache` L751-783 (~323 tok)
  - fn `test_fallback_layer0_engine_specific_styles` L784-798 (~192 tok)

## agents/render_pipeline/tools/

- `__init__.py` — ADK FunctionTool wrappers for the RenderPipeline 9-step workflow. (~624 tok)
- `_paths.py` — Shared sys.path setup for tool modules. (~261 tok)
- `articulate_layer0.py` — Tool 4a (NEW): Sonnet 4.6 articulates Layer 0 rendering directives. (~3002 tok)
  - fn `_build_articulation_prompt` L96-124 (~334 tok)
  - fn `_fallback_layer0` L125-160 (~559 tok)
  - fn `articulate_layer0_fn` L161-252 (~1029 tok)
- `build_prompt.py` — Tool 4: Compose Layer 0 + Layer 3 + Layer 2 final prompt. (~1011 tok)
  - fn `build_prompt_fn` L37-94 (~602 tok)
- `generate_image.py` — Tool 5: Generate image via routed engine. PAID API CALL. (~3507 tok)
  - fn `_is_text_bearing` L87-92 (~63 tok)
  - fn `_resolve_logo_image_path` L93-126 (~338 tok)
  - fn `_resolve_logo_extra_refs` L127-185 (~618 tok)
  - fn `_missing_state_error` L186-196 (~105 tok)
  - fn `_dispatch_engine` L197-235 (~374 tok)
  - fn `generate_image_fn` L236-330 (~1001 tok)
- `load_dossier.py` — Tool 1: Load the canonical dossier for a SKU. (~693 tok)
  - fn `load_dossier_fn` L26-69 (~478 tok)
- `qa_tournament.py` — Tool 6: 3-judge QA tournament + learning-loop recorder. PAID API CALLS. (~1794 tok)
  - fn `_build_tournament_clients` L41-74 (~267 tok)
  - fn `qa_tournament_fn` L75-181 (~1124 tok)
- `refine_image.py` — Tool 7: Refine the candidate using synthesis-aware corrections. PAID API CALL. (~1640 tok)
  - fn `_build_refine_prompt` L33-77 (~432 tok)
  - fn `refine_image_fn` L78-154 (~892 tok)
- `resolve_source.py` — Tool 2: Resolve source image path for a SKU. (~930 tok)
  - fn `_resolve` L31-61 (~354 tok)
  - fn `resolve_source_fn` L62-91 (~293 tok)
- `route_engine.py` — Tool 3: Route to the best image-gen engine. (~1088 tok)
  - fn `_model_id_for` L37-49 (~148 tok)
  - fn `route_engine_fn` L50-104 (~578 tok)
- `vision_consensus.py` — Tool 3a (NEW): Dual-vision consensus describe — Gemini + OpenAI in parallel. (~3417 tok)
  - fn `_gemini_describe` L104-141 (~386 tok)
  - fn `_openai_describe` L142-192 (~471 tok)
  - fn `_merge_consensus` L193-257 (~734 tok)
  - fn `vision_consensus_fn` L258-325 (~800 tok)

## agents/visual_generation/

- `__init__.py` — Visual Generation Agents Module. (~281 tok)
- `conversation_editor.py` — class: add_message, get_history, is_expired, start_session + 8 more (~3441 tok)
  - class `GeneratedImage` L44-60 (~120 tok)
  - class `ChatSessionError` L61-72 (~90 tok)
  - class `ChatSessionExpiredError` L73-80 (~72 tok)
  - class `ChatSessionNotFoundError` L81-95 (~106 tok)
  - class `ChatMessage` L96-103 (~50 tok)
  - class `ChatSession` L104-178 (~701 tok)
  - class `ConversationEditor` L179-412 (~1999 tok)
- `gemini_native.py` — GeminiNativeError: to_dict, save, show, connect + 2 more (~6289 tok)
  - class `GeminiNativeError` L45-68 (~193 tok)
  - class `GeminiAuthenticationError` L69-74 (~32 tok)
  - class `GeminiRateLimitError` L75-87 (~90 tok)
  - class `GeminiQuotaExceededError` L88-93 (~31 tok)
  - class `GeminiInvalidRequestError` L94-99 (~30 tok)
  - class `GeminiModelNotFoundError` L100-105 (~34 tok)
  - class `GeminiContentFilterError` L106-111 (~36 tok)
  - class `GeminiTimeoutError` L112-117 (~28 tok)
  - class `GeminiServiceUnavailableError` L118-123 (~36 tok)
  - class `ChatSessionExpiredError` L124-134 (~91 tok)
  - class `AspectRatio` L135-149 (~131 tok)
  - class `ImageSize` L150-158 (~56 tok)
  - class `ImageGenerationConfig` L159-169 (~102 tok)
  - class `GeneratedImage` L170-195 (~180 tok)
  - class `GeminiNativeImageClient` L196-493 (~2960 tok)
  - class `GeminiFlashImageClient` L494-570 (~703 tok)
  - class `GeminiProImageClient` L571-700 (~1219 tok)
- `prompt_optimizer.py` — VisualUseCase: create_prompt, get_base_negatives, get_collection_negatives, build_negative_prompt (~7002 tok)
  - class `VisualUseCase` L35-45 (~102 tok)
  - class `CameraAngle` L46-56 (~100 tok)
  - class `LightingSetup` L57-72 (~192 tok)
  - class `GeminiTreeOfThoughtsVisual` L73-175 (~1301 tok)
  - class `GeminiNegativePromptEngine` L176-268 (~989 tok)
  - class `CollectionPromptBuilder` L269-382 (~1582 tok)
  - class `ThinkingModeConstructor` L383-456 (~702 tok)
  - class `GoogleSearchGroundingOptimizer` L457-523 (~613 tok)
  - class `GeminiPromptOptimizer` L524-637 (~1080 tok)
- `reference_manager.py` — ReferenceType: to_dict, from_dict, validate_references, create_subject_references + 3 more (~5170 tok)
  - class `ReferenceType` L57-70 (~130 tok)
  - class `ReferenceValidationError` L71-76 (~32 tok)
  - class `ThoughtSignatureError` L77-88 (~84 tok)
  - class `ReferenceImage` L89-113 (~198 tok)
  - class `ThoughtSignature` L114-163 (~504 tok)
  - class `ReferenceImageManager` L164-406 (~2270 tok)
  - class `ThoughtSignatureManager` L407-576 (~1481 tok)
- `visual_generation.py` — VisualProvider: generate, generate (~10400 tok)
  - class `VisualProvider` L44-55 (~103 tok)
  - class `GenerationType` L56-67 (~106 tok)
  - class `AspectRatio` L68-77 (~48 tok)
  - class `ImageQuality` L78-92 (~96 tok)
  - class `GenerationRequest` L93-117 (~245 tok)
  - class `GenerationResult` L118-189 (~574 tok)
  - class `GoogleImagenClient` L190-323 (~1358 tok)
  - class `GoogleVeoClient` L324-447 (~1261 tok)
  - class `HuggingFaceFluxClient` L448-551 (~1070 tok)
  - class `ReplicateLoRAClient` L552-750 (~2196 tok)
  - class `VisualGenerationRouter` L751-1040 (~2878 tok)
  - fn `create_visual_router` L1041-1069 (~182 tok)

## agents/wordpress_bridge/

- `__init__.py` — WordPress Bridge Agent — connects dashboard pipelines to WordPress/WooCommerce. (~274 tok)
- `agent.py` — WordPress Bridge Agent — Claude Agent SDK entry point. (~1271 tok)
  - class `WordPressBridgeAgent` L24-79 (~562 tok)
  - fn `run_agent` L80-121 (~544 tok)
- `mcp_server.py` — WordPress Bridge Agent — MCP tool definitions for WordPress/WooCommerce operations. (~8887 tok)
  - fn `_safe_error` L48-64 (~188 tok)
  - fn `_get_wp_client` L65-102 (~414 tok)
  - fn `_get_product_sync` L103-148 (~494 tok)
  - fn `wp_health_check` L149-170 (~184 tok)
  - fn `wp_get_products` L171-204 (~290 tok)
  - fn `wp_get_orders` L205-238 (~271 tok)
  - fn `wp_update_order` L239-270 (~296 tok)
  - fn `wp_sync_product` L271-319 (~432 tok)
  - fn `wp_sync_collection` L320-389 (~631 tok)
  - fn `wp_create_page` L390-434 (~412 tok)
  - fn `wp_upload_media` L435-476 (~397 tok)
  - fn `_slugify` L477-489 (~129 tok)
  - fn `wp_publish_round_table` L490-556 (~685 tok)
  - fn `wp_attach_3d_model` L557-599 (~431 tok)
  - fn `wp_upload_product_image` L600-651 (~532 tok)
  - fn `wp_publish_social_campaign` L652-707 (~549 tok)
  - fn `wp_update_conversion_data` L708-758 (~514 tok)
  - fn `get_pipeline_status` L759-832 (~673 tok)
  - fn `get_product_catalog` L833-890 (~591 tok)
  - fn `create_wordpress_tools` L891-916 (~220 tok)
- `prompts.py` — System prompt and per-pipeline prompt templates for the WordPress Bridge Agent. (~1216 tok)

## agents/wordpress_theme_builder/

- `agent.ts` — WordPress Theme Builder Agent (~3269 tok)
  - fn `main` L207-271 (~632 tok)

## ai_3d/

- `__init__.py` — ai_3d/__init__.py (~257 tok)
- `generation_pipeline.py` — ai_3d/generation_pipeline.py (~6261 tok)
  - class `ThreeDProvider` L47-56 (~80 tok)
  - class `ModelFormat` L57-67 (~48 tok)
  - class `GenerationQuality` L68-76 (~74 tok)
  - class `GenerationConfig` L77-133 (~481 tok)
  - class `GenerationResult` L134-162 (~310 tok)
  - class `ThreeDGenerationPipeline` L163-629 (~4944 tok)
- `model_generator.py` — Pydantic: GenerationConfig (55 fields) (~8458 tok)
  - class `ModelGenerationError` L42-66 (~201 tok)
  - class `ModelFidelityError` L67-94 (~200 tok)
  - class `GeneratedModel` L95-136 (~384 tok)
  - class `GenerationConfig` L137-166 (~312 tok)
  - class `AI3DModelGenerator` L167-863 (~7103 tok)
- `quality_enhancer.py` — ai_3d/quality_enhancer.py (~3875 tok)
  - class `EnhancementConfig` L42-94 (~389 tok)
  - class `EnhancementResult` L95-106 (~82 tok)
  - class `ModelQualityEnhancer` L107-427 (~3160 tok)
- `resilience.py` — from: record_success, record_failure, call, get_state + 3 more (~3962 tok)
  - class `CircuitState` L23-31 (~65 tok)
  - class `RetryConfig` L32-42 (~82 tok)
  - class `CircuitBreakerConfig` L43-52 (~103 tok)
  - class `CircuitBreakerState` L53-62 (~69 tok)
  - class `CircuitBreakerError` L63-71 (~91 tok)
  - class `MaxRetriesExceededError` L72-80 (~90 tok)
  - class `CircuitBreaker` L81-175 (~1080 tok)
  - class `RetryStrategy` L176-255 (~743 tok)
  - class `FallbackConfig` L256-264 (~66 tok)
  - class `GracefulDegradation` L265-348 (~820 tok)
  - class `ResilientAPIClient` L349-415 (~629 tok)
- `virtual_photoshoot.py` — ScenePreset: to_dict, to_dict, generate_photoshoot (~6243 tok)
  - class `ScenePreset` L33-53 (~164 tok)
  - class `PhotoshootScene` L54-76 (~217 tok)
  - class `GeneratedPhotoshoot` L77-185 (~1109 tok)
  - class `VirtualPhotoshootGenerator` L186-654 (~4583 tok)

## ai_3d/providers/

- `__init__.py` — ai_3d/providers/__init__.py (~174 tok)
- `huggingface.py` — ai_3d/providers/huggingface.py (~4081 tok)
  - class `HuggingFace3DClient` L36-416 (~3856 tok)
- `meshy.py` — ai_3d/providers/meshy.py (~6543 tok)
  - class `MeshyTaskStatus` L46-55 (~58 tok)
  - class `MeshyArtStyle` L56-62 (~36 tok)
  - class `MeshyTopology` L63-70 (~34 tok)
  - class `MeshyTask` L71-97 (~254 tok)
  - class `MeshyClient` L98-692 (~5894 tok)
- `tripo.py` — ai_3d/providers/tripo.py (~4882 tok)
  - class `ImageGenerationRequest` L39-98 (~588 tok)
  - class `TextGenerationRequest` L99-119 (~178 tok)
  - class `TripoAPIResponse` L120-139 (~168 tok)
  - class `TripoTaskStatus` L140-149 (~70 tok)
  - class `TripoClient` L150-537 (~3616 tok)

## alembic/

- `env.py` — Alembic environment configuration with async support. (~789 tok)
  - fn `run_migrations_offline` L52-65 (~105 tok)
  - fn `do_run_migrations` L66-73 (~71 tok)
  - fn `run_async_migrations` L74-87 (~119 tok)
  - fn `run_migrations_online` L88-97 (~62 tok)
- `script.py.mako` (~170 tok)

## alembic/versions/

- `001_baseline_schema.py` — baseline schema (~2899 tok)
  - fn `upgrade` L23-240 (~2649 tok)
  - fn `downgrade` L241-253 (~137 tok)
- `002_add_brand_assets.py` — Add brand assets tables for US-013. (~1390 tok)
  - fn `upgrade` L24-130 (~1112 tok)
  - fn `downgrade` L131-146 (~154 tok)
- `003_add_analytics_tables.py` — Add analytics tables for US-001: Analytics Database Schema. (~3800 tok)
  - fn `upgrade` L26-301 (~3108 tok)
  - fn `downgrade` L302-342 (~527 tok)

## aos/

- `__init__.py` — AOS — Agentic Operating System. (~60 tok)

## aos/adapters/

- `__init__.py` — AOS Adapters — wrap existing agents (SuperAgent, ClaudeSDK) for kernel management. (~26 tok)
- `superagent_adapter.py` — SuperAgentAdapter — non-invasive wrapper around the existing EnhancedSuperAgent. (~1726 tok)
  - class `HealJournalEntry` L25-36 (~84 tok)
  - class `AdapterRun` L37-51 (~125 tok)
  - class `SuperAgentAdapter` L52-137 (~972 tok)
  - fn `_read_error` L138-150 (~103 tok)
  - fn `_read_circuit_state` L151-157 (~54 tok)
  - fn `_extract_metadata` L158-170 (~160 tok)

## aos/cognition/

- `__init__.py` — AOS Cognitive Layer — goal decomposition, planning, and reflection. (~22 tok)
- `goal_decomposer.py` — GoalDecomposer — rule-based goal-to-TaskGraph decomposer. (~1319 tok)
  - class `GoalDecomposer` L18-53 (~377 tok)
  - fn `_product_template` L54-75 (~204 tok)
  - fn `_marketing_template` L76-103 (~273 tok)
  - fn `_analytics_template` L104-125 (~209 tok)
  - fn `_default_template` L126-134 (~57 tok)
- `planner.py` — Planner — converts a TaskGraph into an ordered DecomposedPlan. (~254 tok)
- `reflector.py` — Reflector — converts ExecutionOutcome + LearningTrace into a quality-scored Reflection. (~1224 tok)
  - class `FailureCategory` L33-66 (~444 tok)
  - class `Reflection` L67-80 (~102 tok)
  - class `Reflector` L81-104 (~247 tok)
  - fn `classify_failure` L105-112 (~69 tok)
  - fn `_compute_quality` L113-124 (~129 tok)
- `types.py` — Cognition types — task graph, plan steps, and decomposed plans. (~876 tok)
  - class `TaskNode` L14-27 (~122 tok)
  - class `TaskGraph` L28-76 (~526 tok)
  - class `PlanStep` L77-85 (~58 tok)
  - class `DecomposedPlan` L86-98 (~98 tok)

## aos/governance/

- `__init__.py` — AOS Governance — audit trail, budget control, and policy enforcement. (~22 tok)
- `approval.py` — ApprovalGate — STOP-AND-SHOW enforcement for irreversible/paid actions. (~1906 tok)
  - class `ApprovalStatus` L19-27 (~50 tok)
  - class `RiskLevel` L28-36 (~43 tok)
  - class `ApprovalRequest` L37-52 (~144 tok)
  - class `ApprovalDecision` L53-69 (~133 tok)
  - class `ApprovalGate` L70-191 (~1394 tok)
- `audit.py` — AuditTrail — immutable append-only audit log backed by SQLite. (~1786 tok)
  - class `AuditTrail` L37-164 (~1348 tok)
  - fn `_row_to_entry` L165-177 (~140 tok)
- `budget.py` — BudgetController — per-process and system-wide spend tracking + guards. (~1126 tok)
  - class `BudgetVerdict` L11-18 (~36 tok)
  - class `BudgetDecision` L19-29 (~60 tok)
  - class `BudgetController` L30-120 (~977 tok)
- `policy.py` — PolicyEngine — declarative ALLOW/DENY/REQUIRE_APPROVAL rules for kernel actions. (~947 tok)
  - class `PolicyVerdict` L17-31 (~84 tok)
  - class `PolicyRule` L32-46 (~145 tok)
  - class `PolicyDecision` L47-56 (~58 tok)
  - class `PolicyEngine` L57-109 (~523 tok)
- `types.py` — Governance types — audit entries and policy decisions. (~713 tok)
  - class `AuditEventType` L13-50 (~392 tok)
  - class `AuditEntry` L51-77 (~255 tok)

## aos/healing/

- `__init__.py` — AOS self-healing layer — retry policy, circuit breaker, healing director. (~143 tok)
- `circuit_breaker.py` — Kernel-side circuit breaker — prevents cascading failures per agent_type. (~570 tok)
  - class `CircuitState` L11-17 (~32 tok)
  - class `CircuitBreaker` L18-62 (~472 tok)
- `director.py` — HealingDirector — maps FailureCategory + attempt number to a HealDecision. (~521 tok)
  - class `HealingDirector` L10-47 (~440 tok)
- `policy.py` — Per-FailureCategory retry policies for the AOS healing layer. (~341 tok)
- `types.py` — AOS healing types — action enum, retry config, and healing decision. (~144 tok)

## aos/init/

- `__init__.py` — AOS Init — boot sequence and service initialization. (~17 tok)

## aos/ipc/

- `__init__.py` — AOS IPC — inter-process communication via typed message bus. (~20 tok)
- `message_bus.py` — MessageBus — typed async pub/sub + request/reply. (~1831 tok)
  - class `RequestTimeoutError` L17-20 (~34 tok)
  - class `SubscriptionClosedError` L21-24 (~30 tok)
  - class `MessageBus` L25-167 (~1634 tok)
- `types.py` — IPC message types for the AOS message bus. (~674 tok)
  - class `MessageType` L16-25 (~55 tok)
  - class `SignalType` L26-35 (~64 tok)
  - class `Message` L36-79 (~405 tok)
  - class `Subscription` L80-88 (~66 tok)

## aos/kernel/

- `__init__.py` — AOS Kernel — process lifecycle, scheduling, and the main event loop. (~22 tok)
- `kernel.py` — Kernel — wires ProcessManager + MessageBus + AuditTrail into a single coordinator. (~8527 tok)
  - class `PolicyDeniedError` L45-48 (~33 tok)
  - class `ApprovalRejectedError` L49-52 (~33 tok)
  - class `BudgetDeniedError` L53-56 (~27 tok)
  - class `Kernel` L57-738 (~7551 tok)
  - fn `_resolve_event_type` L739-763 (~241 tok)
  - fn `_empty_adapter_run` L764-778 (~130 tok)
- `process_manager.py` — ProcessManager — lifecycle controller for agent processes. (~1657 tok)
  - class `ProcessNotFoundError` L20-23 (~28 tok)
  - class `ProcessManager` L24-159 (~1517 tok)
- `types.py` — Shared domain types for the AOS kernel. (~1404 tok)
  - class `ProcessStatus` L16-37 (~139 tok)
  - class `ProcessPriority` L38-67 (~291 tok)
  - fn `is_terminal` L68-72 (~63 tok)
  - fn `can_transition` L73-77 (~58 tok)
  - class `AgentProcess` L78-136 (~672 tok)
  - class `SpawnRequest` L137-148 (~94 tok)

## aos/memory/

- `__init__.py` — AOS Memory — namespaced key/value store with TTL and tag-based query index. (~105 tok)
- `index.py` — AOS MemoryIndex — tag-based filter index over a MemoryStore. (~765 tok)
  - class `MemoryIndex` L11-84 (~708 tok)
- `store.py` — AOS MemoryStore — namespaced key/value store with TTL expiry. (~1434 tok)
  - class `MemoryStore` L11-139 (~1371 tok)
- `types.py` — AOS Memory — entry type and exceptions. (~382 tok)

## aos/modules/

- `__init__.py` — AOS Modules — pluggable capability registration for agent types and tools. (~136 tok)
- `loader.py` — Dynamic module loader — importlib-based loader for AOS module packages. (~409 tok)
- `registry.py` — ModuleRegistry — pluggable agent-factory store for the AOS kernel. (~1028 tok)
  - class `DuplicateModuleError` L8-11 (~29 tok)
  - class `ModuleNotFoundError` L12-15 (~27 tok)
  - class `ModuleRegistry` L16-90 (~923 tok)
- `types.py` — AOS module types — manifest and factory type alias. (~211 tok)

## aos/observability/

- `__init__.py` — AOS Observability — metrics, tracing, and health monitoring. (~108 tok)
- `finetune_buffer.py` — FineTuneBuffer — quality-gated accumulator for OpenAI fine-tuning traces. (~942 tok)
  - class `FineTuneRecord` L25-33 (~67 tok)
  - class `FineTuneBuffer` L34-81 (~465 tok)
  - fn `_build_record` L82-101 (~220 tok)
- `health.py` — AOS HealthCheck — snapshot aggregator for kernel subsystem state. (~1310 tok)
  - class `HealthStatus` L11-17 (~32 tok)
  - class `SubsystemHealth` L18-24 (~33 tok)
  - class `HealthSnapshot` L25-30 (~34 tok)
  - class `_KernelHealthSource` L31-50 (~103 tok)
  - class `HealthCheck` L51-151 (~1046 tok)
- `learning_hook.py` — LearningHook — batched per-agent-type trace flusher. (~1289 tok)
  - class `LearningTrace` L17-33 (~137 tok)
  - class `LearningHook` L34-101 (~705 tok)
  - fn `_ingest_one` L102-134 (~330 tok)
- `metrics.py` — AOS MetricsCollector — lightweight in-process counters and gauges. (~996 tok)
  - class `MetricSample` L11-19 (~54 tok)
  - class `MetricsCollector` L20-109 (~886 tok)

## aos/runtime/

- `__init__.py` — AOS Runtime — execution sandboxing, resource limits, and container management. (~25 tok)
- `container.py` — AgentContainer — wraps agent coroutines with resource enforcement. (~1255 tok)
  - class `AgentContainer` L18-111 (~960 tok)
  - class `ResourceLimitExceeded` L112-115 (~31 tok)
  - fn `_measure_output` L116-130 (~135 tok)
- `executor.py` — Executor — kernel.execute() end-to-end runner. (~326 tok)
- `types.py` — Runtime types — resource limits and usage tracking. (~479 tok)

## aos/shell/

- `__init__.py` — AOS Shell — interactive REPL over the live Kernel API. (~68 tok)
- `commands.py` — AOS Shell command dispatch — pure async, zero I/O. (~1548 tok)
  - class `CommandResult` L20-39 (~164 tok)
  - fn `execute_command` L40-62 (~236 tok)
  - fn `_cmd_help` L63-66 (~34 tok)
  - fn `_cmd_exit` L67-70 (~38 tok)
  - fn `_cmd_ps` L71-80 (~132 tok)
  - fn `_cmd_kill` L81-92 (~136 tok)
  - fn `_cmd_spawn` L93-102 (~126 tok)
  - fn `_cmd_budget` L103-109 (~93 tok)
  - fn `_cmd_modules` L110-123 (~165 tok)
  - fn `_cmd_audit` L124-154 (~281 tok)
- `repl.py` — AOS Shell REPL — thin stdin/stdout loop over execute_command. (~675 tok)
  - class `AosShell` L21-76 (~519 tok)

## api/

- `__init__.py` (~843 tok)
- `admin_dashboard.py` — Pydantic: Asset3D (78 fields) (~6382 tok)
  - class `AssetType` L42-50 (~49 tok)
  - class `AssetStatus` L51-60 (~59 tok)
  - class `PipelineType` L61-69 (~58 tok)
  - class `PipelineStatus` L70-79 (~56 tok)
  - class `SyncChannel` L80-87 (~43 tok)
  - class `SyncStatus` L88-101 (~104 tok)
  - class `Asset3D` L102-118 (~162 tok)
  - class `FidelityReport` L119-135 (~170 tok)
  - class `PipelineInfo` L136-149 (~114 tok)
  - class `DashboardMetrics` L150-167 (~140 tok)
  - class `AdminAssetStore` L168-261 (~993 tok)
  - class `DashboardStats` L262-274 (~88 tok)
  - class `ProductSummary` L275-286 (~65 tok)
  - class `SyncJobSummary` L287-297 (~63 tok)
  - class `SalesDataPoint` L298-305 (~35 tok)
  - class `SalesAnalytics` L306-319 (~120 tok)
  - class `AdminDataStore` L320-415 (~932 tok)
  - fn `get_dashboard_stats` L416-435 (~194 tok)
  - fn `get_products` L436-474 (~373 tok)
  - fn `get_sync_jobs` L475-519 (~423 tok)
  - fn `trigger_full_sync` L520-549 (~244 tok)
  - fn `get_sales_analytics` L550-583 (~266 tok)
  - fn `create_product` L584-608 (~214 tok)
  - fn `get_product` L609-635 (~269 tok)
  - class `ProductListResponse` L636-644 (~62 tok)
  - class `SyncJobListResponse` L645-656 (~108 tok)
  - class `AIProviderStatus` L657-665 (~62 tok)
  - class `AIBridgeStatus` L666-675 (~84 tok)
  - fn `get_ai_provider_status` L676-741 (~521 tok)
- `agents.py` — Pydantic: AgentTask (75 fields) (~10250 tok)
  - class `AgentCategory` L36-52 (~115 tok)
  - class `TaskStatus` L53-62 (~53 tok)
  - class `Priority` L63-76 (~88 tok)
  - class `AgentTask` L77-108 (~335 tok)
  - class `AgentTaskResponse` L109-120 (~67 tok)
  - class `AgentInfo` L121-136 (~113 tok)
  - class `ModelFormat` L137-145 (~38 tok)
  - class `GenerateFromDescriptionRequest` L146-156 (~144 tok)
  - class `GenerateFromImageRequest` L157-164 (~104 tok)
  - class `ThreeDGenerationResult` L165-183 (~291 tok)
  - class `SocialPlatform` L184-192 (~54 tok)
  - class `SocialPostRequest` L193-203 (~82 tok)
  - class `SocialAnalyticsRequest` L204-216 (~111 tok)
  - class `EmailRequest` L217-227 (~67 tok)
  - class `SMSRequest` L228-235 (~45 tok)
  - class `CampaignRequest` L236-250 (~116 tok)
  - class `TicketPriority` L251-257 (~32 tok)
  - class `SupportTicketRequest` L258-267 (~62 tok)
  - class `ChatbotRequest` L268-280 (~95 tok)
  - class `ContentType` L281-289 (~60 tok)
  - class `ContentRequest` L290-300 (~71 tok)
  - class `SEOOptimizeRequest` L301-314 (~108 tok)
  - class `AgentService` L315-679 (~4249 tok)
  - fn `list_agents` L680-694 (~125 tok)
  - fn `execute_agent_task` L695-706 (~118 tok)
  - fn `get_task_status` L707-718 (~97 tok)
  - fn `create_social_post` L719-735 (~154 tok)
  - fn `get_social_analytics` L736-751 (~122 tok)
  - fn `send_email` L752-762 (~100 tok)
  - fn `send_sms` L763-1070 (~2799 tok)
- `ai_3d_endpoints.py` — View: create, get, update (~3952 tok)
  - class `GenerateModelRequest` L40-47 (~80 tok)
  - class `GenerateModelResponse` L48-60 (~99 tok)
  - class `RegenerateRequest` L61-67 (~62 tok)
  - class `ModelInfoResponse` L68-82 (~118 tok)
  - class `PipelineStatusResponse` L83-98 (~133 tok)
  - class `JobStore` L99-172 (~712 tok)
  - fn `run_model_generation` L173-232 (~555 tok)
  - fn `get_pipeline_status` L233-255 (~205 tok)
  - fn `list_jobs` L256-261 (~57 tok)
  - fn `get_job` L262-270 (~86 tok)
  - fn `generate_model` L271-347 (~665 tok)
  - fn `regenerate_model` L348-398 (~434 tok)
  - fn `get_model_info` L399-452 (~465 tok)
- `ar_sessions.py` — Pydantic: CreateSessionRequest (53 fields) (~5093 tok)
  - class `ARMode` L64-71 (~54 tok)
  - class `CollectionType` L72-80 (~55 tok)
  - class `SessionStatus` L81-94 (~93 tok)
  - class `CreateSessionRequest` L95-105 (~154 tok)
  - class `ARSession` L106-120 (~94 tok)
  - class `ARProduct` L121-134 (~84 tok)
  - class `SessionAnalytics` L135-145 (~74 tok)
  - class `TryOnEvent` L146-160 (~131 tok)
  - class `ARSessionStore` L161-275 (~1169 tok)
  - fn `_collection_type_from_slug` L276-288 (~121 tok)
  - fn `_garment_category_from_row` L289-300 (~118 tok)
  - fn `_csv_flag` L301-312 (~144 tok)
  - fn `_ar_product_from_row` L313-362 (~494 tok)
  - fn `get_ar_products_from_catalog` L363-382 (~217 tok)
  - fn `create_ar_session` L383-392 (~94 tok)
  - fn `get_ar_session` L393-401 (~99 tok)
  - fn `update_ar_session` L402-414 (~138 tok)
  - fn `record_tryon` L415-433 (~181 tok)
  - fn `get_ar_products` L434-447 (~129 tok)
  - fn `get_all_ar_products` L448-459 (~120 tok)
  - fn `get_ar_analytics` L460-465 (~53 tok)
  - fn `get_ar_capabilities` L466-485 (~203 tok)
  - fn `ar_websocket` L486-541 (~557 tok)
- `brand.py` — ColorInfo: get_brand, get_brand_summary, get_brand_colors, list_collections + 3 more (~2248 tok)
  - class `ColorInfo` L30-37 (~29 tok)
  - class `ToneInfo` L38-45 (~37 tok)
  - class `TypographyInfo` L46-53 (~34 tok)
  - class `AudienceInfo` L54-62 (~46 tok)
  - class `CollectionInfo` L63-74 (~51 tok)
  - class `BrandResponse` L75-90 (~103 tok)
  - class `BrandSummary` L91-106 (~114 tok)
  - fn `get_brand` L107-175 (~656 tok)
  - fn `get_brand_summary` L176-190 (~157 tok)
  - fn `get_brand_colors` L191-203 (~126 tok)
  - fn `list_collections` L204-222 (~202 tok)
  - fn `get_collection` L223-252 (~298 tok)
  - fn `get_brand_tone` L253-263 (~104 tok)
  - fn `get_brand_typography` L264-272 (~96 tok)
- `CLAUDE.md` — api/ — FastAPI endpoint layer (78 Python files) (~362 tok)
- `dashboard.py` — Pydantic: ToolParameter (34 fields) (~13474 tok)
  - class `ToolParameter` L50-57 (~36 tok)
  - class `ToolInfo` L58-64 (~42 tok)
  - class `AgentStats` L65-72 (~51 tok)
  - class `AgentInfo` L73-84 (~77 tok)
  - class `ExecuteRequest` L85-90 (~41 tok)
  - class `ExecuteResponse` L91-333 (~2184 tok)
  - class `AgentRegistry` L334-479 (~1619 tok)
  - fn `health` L480-490 (~97 tok)
  - fn `list_agents` L491-496 (~50 tok)
  - fn `get_agent` L497-505 (~99 tok)
  - fn `get_agent_stats` L506-514 (~103 tok)
  - fn `get_agent_tools` L515-523 (~93 tok)
  - fn `start_agent` L524-538 (~182 tok)
  - fn `stop_agent` L539-549 (~117 tok)
  - fn `trigger_learning` L550-573 (~316 tok)
  - fn `execute_agent_task` L574-641 (~721 tok)
  - fn `list_tools` L642-654 (~134 tok)
  - fn `get_tools_by_category` L655-667 (~142 tok)
  - fn `test_tool` L668-688 (~225 tok)
  - class `ARDashboardOverview` L689-700 (~108 tok)
  - fn `get_ar_overview` L701-754 (~548 tok)
  - fn `get_ar_metrics` L755-785 (~300 tok)
  - class `WordPressDashboardOverview` L786-803 (~165 tok)
  - fn `get_wordpress_overview` L804-870 (~730 tok)
  - fn `get_wordpress_products` L871-905 (~384 tok)
  - fn `get_wordpress_orders` L906-945 (~434 tok)
  - class `HuggingFaceDashboardOverview` L946-963 (~161 tok)
  - fn `get_huggingface_overview` L964-1040 (~768 tok)
  - fn `get_huggingface_spaces` L1041-1071 (~303 tok)
  - fn `get_huggingface_training` L1072-1371 (~2880 tok)
- `elementor_3d.py` — Elementor 3D Integration API. (~896 tok)
  - class `ElementorWidgetConfig` L18-27 (~134 tok)
  - class `ElementorWidgetResponse` L28-36 (~61 tok)
  - fn `list_widgets` L37-52 (~129 tok)
  - fn `create_widget` L53-79 (~244 tok)
  - fn `get_widget` L80-96 (~134 tok)
  - fn `delete_widget` L97-104 (~57 tok)
- `gateway.py` — CircuitState: state, is_open, failure_rate, record_success + 6 more (~5357 tok)
  - class `CircuitState` L70-78 (~80 tok)
  - class `CircuitBreaker` L79-161 (~945 tok)
  - class `RateLimiter` L162-243 (~886 tok)
  - class `RouteConfig` L244-258 (~150 tok)
  - class `APIGateway` L259-519 (~2655 tok)
- `gdpr.py` — Pydantic: GDPRExportRequest (62 fields) (~10515 tok)
  - class `DataCategory` L40-49 (~103 tok)
  - class `LegalBasis` L50-60 (~87 tok)
  - class `RequestType` L61-71 (~84 tok)
  - class `RequestStatus` L72-81 (~56 tok)
  - class `ExportFormat` L82-90 (~40 tok)
  - class `GDPRExportRequest` L91-115 (~214 tok)
  - class `GDPRExportResponse` L116-127 (~68 tok)
  - class `GDPRDeleteRequest` L128-161 (~355 tok)
  - class `GDPRDeleteResponse` L162-173 (~86 tok)
  - class `RetentionPolicy` L174-183 (~58 tok)
  - class `RetentionPolicyResponse` L184-192 (~60 tok)
  - class `GDPRRequestRecord` L193-206 (~92 tok)
  - class `ConsentRecord` L207-223 (~109 tok)
  - class `GDPRService` L224-931 (~7868 tok)
  - fn `export_personal_data` L932-953 (~186 tok)
  - fn `delete_personal_data` L954-974 (~200 tok)
  - fn `get_retention_policies` L975-989 (~124 tok)
  - fn `get_gdpr_requests` L990-1003 (~136 tok)
  - fn `record_consent` L1004-1012 (~113 tok)
  - fn `get_my_consents` L1013-1036 (~179 tok)
- `graphql_server.py` (~441 tok)
- `index.py` — API: GET (5 endpoints) (~1186 tok)
  - fn `root` L75-93 (~138 tok)
  - fn `health` L94-104 (~68 tok)
  - fn `ready` L105-110 (~35 tok)
  - fn `live` L111-123 (~105 tok)
  - fn `dashboard_metrics` L124-147 (~243 tok)
- `requirements.txt` — Python dependencies (~110 tok)
- `round_table.py` — Pydantic: ProviderInfo (48 fields) (~3374 tok)
  - fn `get_round_table` L29-41 (~118 tok)
  - class `ProviderInfo` L42-52 (~63 tok)
  - class `CompetitionRequest` L53-63 (~99 tok)
  - class `EntryScore` L64-74 (~67 tok)
  - class `CompetitionEntry` L75-85 (~60 tok)
  - class `CompetitionResponse` L86-101 (~112 tok)
  - class `HistoryEntry` L102-112 (~63 tok)
  - class `ProviderStats` L113-130 (~138 tok)
  - fn `list_providers` L131-154 (~240 tok)
  - fn `list_competitions` L155-206 (~560 tok)
  - fn `get_latest_competition` L207-219 (~111 tok)
  - fn `get_competition` L220-256 (~448 tok)
  - fn `run_competition` L257-273 (~162 tok)
  - fn `get_provider_stats` L274-297 (~231 tok)
  - fn `_result_to_response` L298-359 (~728 tok)
- `sync_endpoints.py` — View: create, get, update (~3224 tok)
  - class `ProductSyncRequest` L38-51 (~150 tok)
  - class `BulkSyncRequest` L52-58 (~55 tok)
  - class `SyncJobResponse` L59-75 (~131 tok)
  - class `SyncStatusResponse` L76-86 (~81 tok)
  - class `BulkSyncResponse` L87-101 (~125 tok)
  - class `SyncJobStore` L102-168 (~628 tok)
  - fn `run_product_sync` L169-223 (~490 tok)
  - fn `sync_single_product` L224-264 (~334 tok)
  - fn `sync_bulk_products` L265-306 (~335 tok)
  - fn `get_sync_status` L307-341 (~345 tok)
  - fn `list_sync_jobs` L342-355 (~109 tok)
  - fn `get_sync_job` L356-364 (~84 tok)
  - fn `trigger_full_sync` L365-378 (~105 tok)
- `tasks.py` — View: create, get, update (~2949 tok)
  - class `TaskMetrics` L40-49 (~77 tok)
  - class `TaskRequest` L50-59 (~86 tok)
  - class `TaskResponse` L60-75 (~139 tok)
  - class `TaskStore` L76-150 (~646 tok)
  - fn `execute_task_background` L151-270 (~1147 tok)
  - fn `list_tasks` L271-280 (~106 tok)
  - fn `get_task` L281-289 (~82 tok)
  - fn `submit_task` L290-307 (~141 tok)
  - fn `cancel_task` L308-330 (~227 tok)
- `three_d.py` — View: create, get, update (~8445 tok)
  - class `ModelProvider` L54-72 (~167 tok)
  - class `JobStatus` L73-81 (~47 tok)
  - class `GenerateTextRequest` L82-92 (~119 tok)
  - class `GenerateImageRequest` L93-101 (~88 tok)
  - class `JobResponse` L102-118 (~121 tok)
  - class `PipelineStatus` L119-129 (~67 tok)
  - class `ProviderInfo` L130-146 (~117 tok)
  - class `JobStore` L147-257 (~990 tok)
  - fn `run_trellis_generation` L258-325 (~634 tok)
  - fn `run_tripo_generation` L326-378 (~451 tok)
  - fn `run_huggingface_text_generation` L379-432 (~503 tok)
  - fn `run_huggingface_image_generation` L433-487 (~518 tok)
  - fn `run_round_table_generation` L488-579 (~964 tok)
  - fn `get_pipeline_status` L580-610 (~269 tok)
  - fn `list_providers` L611-684 (~770 tok)
  - fn `list_jobs` L685-690 (~59 tok)
  - fn `get_job` L691-699 (~85 tok)
  - fn `generate_from_text` L700-772 (~656 tok)
  - fn `generate_from_image_url` L773-851 (~685 tok)
  - fn `generate_from_upload` L852-930 (~705 tok)
- `tools.py` — Pydantic: ToolInfo (16 fields) (~1770 tok)
  - class `ToolInfo` L31-41 (~64 tok)
  - class `ToolTestRequest` L42-48 (~43 tok)
  - class `ToolTestResponse` L49-76 (~308 tok)
  - fn `list_tools` L77-121 (~478 tok)
  - fn `list_tools_by_category` L122-130 (~92 tok)
  - fn `test_tool` L131-181 (~571 tok)
  - fn `list_categories` L182-185 (~34 tok)
- `versioning.py` — URL configuration (~5174 tok)
  - class `VersionConfig` L46-74 (~260 tok)
  - class `VersionStatus` L75-88 (~129 tok)
  - class `APIVersion` L89-99 (~70 tok)
  - class `VersionInfo` L100-113 (~112 tok)
  - class `VersionExtractor` L114-180 (~618 tok)
  - class `VersionMiddleware` L181-262 (~882 tok)
  - class `VersionedAPIRouter` L263-314 (~465 tok)
  - fn `get_api_version` L315-329 (~114 tok)
  - class `RequireVersion` L330-371 (~458 tok)
  - fn `versioned` L372-410 (~392 tok)
  - fn `get_api_versions` L411-441 (~293 tok)
  - fn `get_current_version` L442-451 (~107 tok)
  - fn `setup_api_versioning` L452-483 (~276 tok)
  - class `APIVersionFactory` L484-571 (~642 tok)
- `virtual_tryon.py` — Pydantic: TryOnRequest (73 fields) (~16930 tok)
  - fn `is_private_ip` L81-98 (~133 tok)
  - fn `validate_url_for_ssrf` L99-147 (~459 tok)
  - fn `validate_file_extension` L148-178 (~236 tok)
  - class `TryOnProvider` L179-186 (~70 tok)
  - class `GarmentCategory` L187-196 (~56 tok)
  - class `TryOnMode` L197-204 (~66 tok)
  - class `JobStatus` L205-213 (~47 tok)
  - class `ModelGender` L214-226 (~93 tok)
  - class `TryOnRequest` L227-266 (~344 tok)
  - class `BatchTryOnRequest` L267-292 (~248 tok)
  - class `GenerateModelRequest` L293-310 (~144 tok)
  - class `JobResponse` L311-327 (~117 tok)
  - class `BatchJobResponse` L328-340 (~78 tok)
  - class `ModelGenerationResponse` L341-354 (~90 tok)
  - class `PipelineStatus` L355-367 (~81 tok)
  - class `ProviderInfo` L368-385 (~125 tok)
  - class `TryOnJobStore` L386-730 (~3772 tok)
  - fn `run_fashn_tryon` L731-803 (~812 tok)
  - fn `run_idm_vton_tryon` L804-906 (~1216 tok)
  - fn `run_round_table_tryon` L907-992 (~1038 tok)
  - fn `run_fashn_model_generation` L993-1047 (~562 tok)
  - fn `download_image` L1048-1134 (~984 tok)
  - fn `get_pipeline_status` L1135-1171 (~440 tok)
  - fn `list_providers` L1172-1210 (~472 tok)
  - fn `list_categories` L1211-1228 (~242 tok)
  - fn `list_jobs` L1229-1246 (~143 tok)
  - fn `get_job` L1247-1263 (~144 tok)
  - fn `generate_tryon` L1264-1331 (~893 tok)
  - fn `generate_tryon_upload` L1332-1436 (~1339 tok)
  - fn `batch_tryon` L1437-1596 (~1810 tok)
- `visual.py` — View: create, get, update (~6917 tok)
  - class `VisualProvider` L42-49 (~53 tok)
  - class `ImageStyle` L50-59 (~95 tok)
  - class `JobStatus` L60-66 (~37 tok)
  - class `ProductPhotoRequest` L67-78 (~172 tok)
  - class `BatchPhotoRequest` L79-88 (~98 tok)
  - class `VisualJobResponse` L89-104 (~110 tok)
  - class `BatchJobResponse` L105-117 (~91 tok)
  - class `VisualJobStore` L118-185 (~617 tok)
  - fn `run_product_photo_generation` L186-228 (~383 tok)
  - fn `_style_to_description` L229-246 (~288 tok)
  - fn `list_providers` L247-277 (~327 tok)
  - fn `list_styles` L278-314 (~360 tok)
  - fn `list_jobs` L315-320 (~60 tok)
  - fn `get_job` L321-329 (~84 tok)
  - fn `generate_product_photo` L330-366 (~279 tok)
  - fn `generate_batch_photos` L367-414 (~378 tok)
  - class `EnhancementType` L415-424 (~98 tok)
  - class `EnhanceRequest` L425-437 (~186 tok)
  - class `EnhanceUploadRequest` L438-447 (~58 tok)
  - fn `run_image_enhancement` L448-498 (~538 tok)
  - fn `_upscale_image` L499-533 (~381 tok)
  - fn `_enhance_background` L534-559 (~238 tok)
  - fn `_full_enhancement` L560-586 (~234 tok)
  - fn `enhance_from_url` L587-638 (~460 tok)
  - fn `enhance_from_upload` L639-693 (~507 tok)
  - fn `batch_enhance` L694-748 (~497 tok)
- `webhooks.py` — Pydantic: WebhookEndpoint (72 fields) (~7972 tok)
  - class `WebhookConfig` L53-77 (~185 tok)
  - class `WebhookEventType` L78-116 (~303 tok)
  - class `DeliveryStatus` L117-131 (~107 tok)
  - class `WebhookEndpoint` L132-157 (~261 tok)
  - class `WebhookEvent` L158-168 (~92 tok)
  - class `WebhookDelivery` L169-195 (~199 tok)
  - class `WebhookEndpointCreate` L196-204 (~64 tok)
  - class `WebhookEndpointResponse` L205-221 (~138 tok)
  - class `WebhookSigner` L222-307 (~735 tok)
  - class `WebhookManager` L308-677 (~3770 tok)
  - fn `create_webhook_endpoint` L678-702 (~218 tok)
  - fn `list_webhook_endpoints` L703-720 (~152 tok)
  - fn `get_webhook_endpoint` L721-737 (~156 tok)
  - fn `delete_webhook_endpoint` L738-746 (~100 tok)
  - fn `rotate_webhook_secret` L747-756 (~114 tok)
  - fn `list_webhook_deliveries` L757-767 (~106 tok)
  - fn `list_dead_letters` L768-773 (~56 tok)
  - fn `retry_dead_letter` L774-783 (~111 tok)
  - fn `test_webhook_endpoint` L784-805 (~211 tok)
  - class `WebhookReceiver` L806-872 (~534 tok)
- `websocket_integration.py` — WebSocket Integration Layer for Agent Execution. (~4305 tok)
  - class `WebSocketIntegration` L37-400 (~3432 tok)
  - fn `wrap_agent_execution` L401-473 (~623 tok)
- `websocket.py` — WebSocket server for real-time dashboard updates. (~3542 tok)
  - class `ConnectionManager` L31-160 (~1300 tok)
  - fn `websocket_handler` L161-223 (~685 tok)
  - fn `websocket_agents` L224-229 (~60 tok)
  - fn `websocket_round_table` L230-235 (~64 tok)
  - fn `websocket_tasks` L236-241 (~60 tok)
  - fn `websocket_3d_pipeline` L242-247 (~64 tok)
  - fn `websocket_metrics` L248-254 (~73 tok)
  - fn `websocket_endpoint` L255-272 (~173 tok)
  - fn `broadcast_agent_update` L273-291 (~143 tok)
  - fn `broadcast_round_table_update` L292-312 (~165 tok)
  - fn `broadcast_task_update` L313-336 (~166 tok)
  - fn `broadcast_3d_pipeline_update` L337-360 (~193 tok)
  - fn `broadcast_metrics_update` L361-373 (~87 tok)
  - fn `broadcast_error` L374-388 (~123 tok)

## api/graphql/

- `__init__.py` (~36 tok)
- `schema.py` — Query: product, products (~648 tok)
  - class `Query` L27-77 (~464 tok)
- `types.py` — ProductType: from_db (~430 tok)

## api/graphql/dataloaders/

- `__init__.py` (~71 tok)
- `product_loader.py` — ProductDataLoader: get_db_session (~673 tok)
  - class `ProductDataLoader` L25-72 (~460 tok)
  - fn `get_db_session` L73-77 (~42 tok)

## api/graphql/resolvers/

- `__init__.py` — GraphQL resolvers (~7 tok)
- `product_resolver.py` — get_products_from_db (~342 tok)

## api/image-processing/

- `luxury-enhance.ts` — Enhance product image with luxury aesthetic (~2593 tok)
  - section `LuxuryEnhanceOptions` L5-14 (~66 tok)
  - section `EnhancedImage` L15-25 (~48 tok)
  - class `LuxuryImageProcessor` L26-334 (~2446 tok)

## api/v1/

- `__init__.py` — API v1 Package. (~806 tok)
- `approval.py` — Approval queue API endpoints. (~3846 tok)
  - class `ActionRequest` L61-70 (~84 tok)
  - class `BatchActionRequest` L71-78 (~45 tok)
  - class `RevisionCompleteRequest` L79-84 (~32 tok)
  - class `SyncTriggerRequest` L85-91 (~69 tok)
  - class `QueueSummary` L92-104 (~98 tok)
  - fn `get_manager` L105-109 (~34 tok)
  - fn `get_sync` L110-120 (~102 tok)
  - fn `list_approval_queue` L121-153 (~302 tok)
  - fn `get_approval_item` L154-173 (~176 tok)
  - fn `process_approval_action` L174-219 (~420 tok)
  - fn `batch_process_approvals` L220-248 (~255 tok)
  - fn `list_revision_queue` L249-271 (~218 tok)
  - fn `complete_revision` L272-302 (~298 tok)
  - fn `get_queue_stats` L303-315 (~107 tok)
  - fn `get_queue_summary` L316-338 (~196 tok)
  - fn `trigger_wordpress_sync` L339-402 (~620 tok)
  - fn `expire_old_items` L403-422 (~196 tok)
  - fn `create_approval_item` L423-435 (~123 tok)
- `assets.py` — Asset Processing API Endpoints. (~11886 tok)
  - class `JobStatus` L75-84 (~55 tok)
  - class `ProcessingProfile` L85-93 (~52 tok)
  - class `ImageSource` L94-101 (~40 tok)
  - class `IngestRequest` L102-128 (~256 tok)
  - class `IngestResponse` L129-139 (~56 tok)
  - class `StageInfo` L140-150 (~70 tok)
  - class `JobResponse` L151-170 (~124 tok)
  - class `JobListResponse` L171-180 (~50 tok)
  - class `JobWebhookPayload` L181-205 (~230 tok)
  - fn `ingest_image` L206-337 (~1198 tok)
  - fn `get_job_status` L338-403 (~630 tok)
  - fn `list_jobs` L404-499 (~944 tok)
  - fn `cancel_job` L500-541 (~344 tok)
  - fn `retry_job` L542-618 (~653 tok)
  - fn `get_version_manager` L619-633 (~141 tok)
  - class `VersionRevertRequest` L634-643 (~101 tok)
  - class `RetentionUpdateRequest` L644-655 (~120 tok)
  - fn `list_asset_versions` L656-704 (~440 tok)
  - fn `get_asset_version` L705-763 (~494 tok)
  - fn `revert_asset_version` L764-841 (~710 tok)
  - fn `update_asset_retention` L842-927 (~788 tok)
  - fn `delete_asset_version` L928-1001 (~652 tok)
  - class `AssetMetadata` L1002-1010 (~63 tok)
  - class `AssetResponse` L1011-1025 (~96 tok)
  - class `AssetListResponse` L1026-1035 (~50 tok)
  - class `AssetUploadResponse` L1036-1041 (~26 tok)
  - class `SkuImageCountsResponse` L1042-1049 (~101 tok)
  - class `HfDatasetInfo` L1050-1061 (~66 tok)
  - class `HfDatasetsResponse` L1062-1082 (~148 tok)
  - fn `list_assets` L1083-1358 (~2652 tok)
- `autonomous.py` — API: GET, POST (4 endpoints) (~1814 tok)
  - class `AutonomousOperation` L54-63 (~65 tok)
  - class `AutonomousHistoryEntry` L64-72 (~52 tok)
  - class `AutonomousOperationsResponse` L73-77 (~30 tok)
  - fn `_load_history` L78-91 (~133 tok)
  - fn `_persist_history` L92-99 (~75 tok)
  - fn `_log_event` L100-113 (~134 tok)
  - fn `_build_operation` L114-131 (~172 tok)
  - fn `list_operations` L132-144 (~119 tok)
  - fn `start_operation` L145-167 (~214 tok)
  - fn `stop_operation` L168-190 (~216 tok)
  - fn `get_operation_history` L191-203 (~152 tok)
- `brand_assets.py` — Brand asset ingestion API for training data preparation. (~9193 tok)
  - fn `_get_r2_client` L49-70 (~191 tok)
  - class `BrandAssetCategory` L71-81 (~70 tok)
  - class `AssetApprovalStatus` L82-89 (~46 tok)
  - class `IngestionJobStatus` L90-99 (~59 tok)
  - class `TrainingReadinessStatus` L100-112 (~98 tok)
  - class `BrandAssetMetadata` L113-124 (~93 tok)
  - class `BrandAssetUpload` L125-146 (~290 tok)
  - class `BulkIngestionRequest` L147-165 (~200 tok)
  - class `ColorPalette` L166-173 (~86 tok)
  - class `CompositionAnalysis` L174-181 (~91 tok)
  - class `LightingProfile` L182-189 (~86 tok)
  - class `VisualFeatures` L190-199 (~96 tok)
  - class `BrandAsset` L200-217 (~184 tok)
  - class `IngestionJobResult` L218-226 (~52 tok)
  - class `BulkIngestionJob` L227-241 (~142 tok)
  - class `BrandAssetsListResponse` L242-251 (~52 tok)
  - class `CategoryStats` L252-261 (~50 tok)
  - class `TrainingReadinessResponse` L262-278 (~162 tok)
  - fn `_asset_to_row` L279-299 (~204 tok)
  - fn `_row_to_asset` L300-322 (~212 tok)
  - fn `_job_to_row` L323-338 (~150 tok)
  - fn `_row_to_job` L339-359 (~201 tok)
  - fn `extract_visual_features` L360-437 (~822 tok)
  - fn `upload_to_r2` L438-524 (~791 tok)
  - fn `process_bulk_ingestion` L525-644 (~1202 tok)
  - fn `bulk_ingest_brand_assets` L645-685 (~329 tok)
  - fn `get_ingestion_job` L686-710 (~228 tok)
  - fn `list_brand_assets` L711-757 (~435 tok)
  - fn `get_brand_asset` L758-777 (~172 tok)
  - fn `approve_brand_asset` L778-980 (~1980 tok)
- `catalog.py` — Catalog Search API — semantic retrieval over the SkyyRose canonical catalog. (~7153 tok)
  - fn `_get_retriever` L63-84 (~298 tok)
  - class `AnswerCache` L85-155 (~722 tok)
  - fn `_get_answer_cache` L156-174 (~188 tok)
  - class `CatalogMatchResponse` L175-196 (~178 tok)
  - class `SearchResponse` L197-206 (~79 tok)
  - class `CatalogHealthResponse` L207-221 (~124 tok)
  - fn `search_catalog` L222-265 (~509 tok)
  - fn `collection_featured` L266-307 (~452 tok)
  - class `DossierResponse` L308-318 (~81 tok)
  - class `ProductDetailResponse` L319-334 (~131 tok)
  - fn `_coerce_bool` L335-339 (~52 tok)
  - fn `get_product` L340-406 (~786 tok)
  - class `SimilarResponse` L407-416 (~89 tok)
  - fn `get_similar_products` L417-467 (~586 tok)
  - class `AnswerResponse` L468-504 (~344 tok)
  - fn `answer_question` L505-567 (~712 tok)
  - fn `_sse` L568-573 (~55 tok)
  - fn `answer_question_stream` L574-622 (~552 tok)
  - class `CacheStatsResponse` L623-634 (~71 tok)
  - fn `cache_stats` L635-640 (~60 tok)
  - fn `cache_clear` L641-650 (~114 tok)
  - fn `catalog_health` L651-668 (~203 tok)
- `claude_sdk.py` — API: POST, GET (8 endpoints) (~3785 tok)
  - fn `trigger_research` L39-80 (~389 tok)
  - fn `triage_email` L81-125 (~396 tok)
  - fn `handle_excel` L126-180 (~506 tok)
  - fn `manage_session` L181-257 (~756 tok)
  - fn `execute_dashboard_actions` L258-303 (~455 tok)
  - fn `get_dashboard_health` L304-326 (~224 tok)
  - fn `list_dashboard_agents` L327-370 (~402 tok)
  - fn `find_agents_by_capability` L371-403 (~278 tok)
- `code.py` — Code Analysis and Fixing API Endpoints. (~3204 tok)
  - class `CodeScanRequest` L36-55 (~153 tok)
  - class `ScanIssue` L56-68 (~98 tok)
  - class `CodeScanResponse` L69-81 (~71 tok)
  - class `CodeFixRequest` L82-104 (~221 tok)
  - class `CodeFix` L105-115 (~47 tok)
  - class `CodeFixResponse` L116-138 (~204 tok)
  - fn `_do_scan` L139-159 (~260 tok)
  - fn `_finding_to_issue` L160-174 (~178 tok)
  - fn `_build_summary` L175-191 (~192 tok)
  - fn `scan_code` L192-265 (~792 tok)
  - fn `fix_code` L266-321 (~719 tok)
- `commerce.py` — Commerce API Endpoints (Bulk Products & Dynamic Pricing). (~6478 tok)
  - class `BulkProductRequest` L36-47 (~124 tok)
  - class `ProductResult` L48-56 (~64 tok)
  - class `BulkProductResponse` L57-69 (~75 tok)
  - class `DynamicPricingRequest` L70-87 (~171 tok)
  - class `PriceOptimization` L88-99 (~82 tok)
  - class `DynamicPricingResponse` L100-116 (~133 tok)
  - fn `_dispatch_product_op` L117-235 (~1485 tok)
  - fn `_process_bulk_products_background` L236-344 (~1031 tok)
  - class `BulkTaskStatusResponse` L345-365 (~169 tok)
  - fn `bulk_product_operations` L366-475 (~1068 tok)
  - fn `get_bulk_operation_status` L476-522 (~451 tok)
  - fn `_coerce_price` L523-533 (~92 tok)
  - fn `_catalog_price_map` L534-548 (~129 tok)
  - fn `optimize_pricing` L549-657 (~1112 tok)
- `competitors.py` — API endpoints for competitor analysis. (~3101 tok)
  - fn `get_analysis_service` L47-51 (~63 tok)
  - fn `check_competitor_access` L52-73 (~238 tok)
  - fn `get_style_analytics` L74-93 (~194 tok)
  - fn `get_analytics_summary` L94-139 (~457 tok)
  - fn `upload_competitor_asset` L140-168 (~338 tok)
  - fn `list_competitor_assets` L169-201 (~358 tok)
  - fn `get_competitor_asset` L202-217 (~149 tok)
  - fn `update_competitor_asset` L218-234 (~157 tok)
  - fn `delete_competitor_asset` L235-255 (~209 tok)
  - fn `create_competitor` L256-275 (~192 tok)
  - fn `list_competitors` L276-287 (~110 tok)
  - fn `get_competitor` L288-303 (~145 tok)
  - fn `delete_competitor` L304-317 (~154 tok)
- `context_dev.py` — Authenticated Context.dev structured web extraction API. (~1713 tok)
  - class `ContextDevExtractionRequest` L38-80 (~471 tok)
  - class `ContextDevExtractionResponse` L81-92 (~91 tok)
  - fn `create_extraction` L93-155 (~786 tok)
- `descriptions.py` — API endpoints for image-to-description pipeline. (~3726 tok)
  - fn `get_vision_client` L45-49 (~33 tok)
  - fn `get_pipeline` L50-61 (~116 tok)
  - class `QuickDescriptionRequest` L62-78 (~139 tok)
  - class `BatchStatusResponse` L79-91 (~112 tok)
  - fn `generate_description` L92-126 (~336 tok)
  - fn `generate_quick_description` L127-149 (~259 tok)
  - fn `generate_batch_descriptions` L150-190 (~398 tok)
  - fn `extract_features` L191-216 (~254 tok)
  - fn `list_models` L217-281 (~687 tok)
  - fn `list_styles` L282-324 (~487 tok)
  - fn `health_check` L325-362 (~432 tok)
  - fn `_send_webhook` L363-381 (~155 tok)
- `elite_studio_webhooks.py` — WebhookManager: register, fire (~2352 tok)
  - class `WebhookManager` L72-203 (~1321 tok)
  - fn `_fire_all` L204-211 (~88 tok)
  - fn `_deliver` L212-248 (~361 tok)
  - fn `_sign` L249-252 (~53 tok)
- `elite_studio.py` — API: POST, GET, DELETE (8 endpoints) (~4722 tok)
  - fn `_get_api_key_dependency` L47-83 (~401 tok)
  - class `ProduceRequest` L84-109 (~199 tok)
  - class `BatchProduceRequest` L110-127 (~140 tok)
  - class `ProduceResponse` L128-136 (~46 tok)
  - class `BatchProduceResponse` L137-144 (~46 tok)
  - class `JobStatusResponse` L145-153 (~53 tok)
  - class `JobListResponse` L154-162 (~47 tok)
  - class `HealthResponse` L163-176 (~107 tok)
  - fn `_get_redis` L177-189 (~110 tok)
  - fn `_require_redis` L190-199 (~71 tok)
  - fn `_fetch_result` L200-223 (~224 tok)
  - fn `produce` L224-256 (~295 tok)
  - fn `produce_batch` L257-284 (~243 tok)
  - fn `get_job_status` L285-309 (~190 tok)
  - fn `get_job_result` L310-329 (~150 tok)
  - fn `cancel_job` L330-354 (~231 tok)
  - fn `list_jobs` L355-404 (~425 tok)
  - fn `list_skus` L405-438 (~244 tok)
  - fn `health` L439-475 (~303 tok)
  - class `CreateRequest` L476-501 (~214 tok)
  - class `CreateResponse` L502-517 (~106 tok)
  - fn `create_operation` L518-557 (~366 tok)
  - fn `_register_job_webhook` L558-568 (~114 tok)
- `feature_flags.py` — API: GET, PUT, POST, DELETE (4 endpoints) (~1152 tok)
  - class `FlagCreateRequest` L26-33 (~88 tok)
  - class `FlagResponse` L34-42 (~54 tok)
  - class `RolloutRequest` L43-47 (~38 tok)
  - fn `list_flags` L48-66 (~181 tok)
  - fn `upsert_flag` L67-94 (~261 tok)
  - fn `update_rollout` L95-121 (~238 tok)
  - fn `delete_flag` L122-136 (~131 tok)
- `hf_spaces.py` — Pydantic: HFSpaceInfo (27 fields) (~3939 tok)
  - class `HFSpaceInfo` L74-87 (~182 tok)
  - class `HFSpacesStatus` L88-138 (~556 tok)
  - fn `check_space_status` L139-194 (~611 tok)
  - fn `get_spaces_status` L195-253 (~596 tok)
  - fn `get_space_info` L254-303 (~456 tok)
  - fn `refresh_space` L304-362 (~599 tok)
  - fn `health_check` L363-407 (~371 tok)
- `lora.py` — LoRA Training API Router (api/v1/lora.py). (~2692 tok)
  - class `TrainLoRARequest` L40-53 (~150 tok)
  - class `TrainLoRAResponse` L54-60 (~32 tok)
  - class `SampleProduct` L61-68 (~36 tok)
  - class `DatasetPreviewResponse` L69-76 (~55 tok)
  - class `ProductContributionOut` L77-84 (~42 tok)
  - class `LoRAVersionOut` L85-96 (~78 tok)
  - class `ProductHistoryResponse` L97-106 (~74 tok)
  - fn `_version_to_out` L107-129 (~202 tok)
  - fn `_make_tracker` L130-138 (~94 tok)
  - fn `_run_training` L139-168 (~274 tok)
  - fn `start_lora_training` L169-197 (~284 tok)
  - fn `preview_dataset` L198-251 (~533 tok)
  - fn `get_version_info` L252-273 (~234 tok)
  - fn `get_product_training_history` L274-294 (~216 tok)
- `marketing.py` — Marketing Campaign API Endpoints. (~1809 tok)
  - class `MarketingCampaignRequest` L34-63 (~278 tok)
  - class `MarketingCampaignResponse` L64-85 (~154 tok)
  - fn `_channels_for_campaign` L86-90 (~63 tok)
  - fn `_build_campaign_brief` L91-117 (~283 tok)
  - fn `create_campaign` L118-196 (~784 tok)
- `media.py` — Media Generation API Endpoints (3D Models). (~4306 tok)
  - class `ThreeDGenerationFromTextRequest` L40-69 (~273 tok)
  - class `ThreeDGenerationFromImageRequest` L70-97 (~230 tok)
  - class `ThreeDAssetMetadata` L98-108 (~68 tok)
  - class `ThreeDGenerationResponse` L109-128 (~162 tok)
  - fn `_resolve_image_to_tempfile` L129-174 (~488 tok)
  - fn `_run_3d_generation_background` L175-254 (~907 tok)
  - fn `generate_3d_from_text` L255-337 (~753 tok)
  - fn `generate_3d_from_image` L338-417 (~707 tok)
  - fn `get_3d_generation_status` L418-457 (~396 tok)
- `ml.py` — Machine Learning Prediction API Endpoints. (~4070 tok)
  - class `MLModelType` L37-61 (~322 tok)
  - class `MLPredictionRequest` L62-76 (~136 tok)
  - class `MLPrediction` L77-85 (~49 tok)
  - class `MLPredictionResponse` L86-102 (~127 tok)
  - fn `_run_ml_prediction_background` L103-180 (~739 tok)
  - fn `_reshape_agent_result` L181-209 (~340 tok)
  - fn `_compute_prediction` L210-247 (~443 tok)
  - class `MLTaskStatusResponse` L248-262 (~153 tok)
  - fn `predict` L263-352 (~932 tok)
  - fn `get_prediction_status` L353-405 (~505 tok)
- `monitoring.py` — System Monitoring and Health API Endpoints. (~5825 tok)
  - class `MetricDataPoint` L80-87 (~44 tok)
  - class `MetricSeries` L88-96 (~53 tok)
  - class `MonitoringMetricsResponse` L97-105 (~56 tok)
  - class `ServiceHealthStatus` L106-116 (~84 tok)
  - class `SystemStats` L117-127 (~60 tok)
  - class `HealthEvent` L128-137 (~55 tok)
  - class `MonitoringHealthResponse` L138-146 (~58 tok)
  - class `AgentInfo` L147-158 (~77 tok)
  - class `AgentListResponse` L159-173 (~112 tok)
  - fn `track_request` L174-178 (~61 tok)
  - fn `_check_http_service` L179-232 (~509 tok)
  - fn `_check_db_service` L233-280 (~434 tok)
  - fn `_compute_system_stats` L281-299 (~221 tok)
  - fn `_compute_latency_p95` L300-317 (~257 tok)
  - fn `_compute_requests_per_second` L318-330 (~133 tok)
  - fn `get_health` L331-391 (~606 tok)
  - fn `get_metrics` L392-529 (~1261 tok)
  - fn `_scan_agents_directory` L530-577 (~547 tok)
  - fn `_get_agents_snapshot` L578-596 (~199 tok)
  - fn `list_agents` L597-632 (~372 tok)
- `orchestration.py` — Multi-Agent Orchestration API Endpoints. (~2046 tok)
  - class `WorkflowExecutionRequest` L33-50 (~185 tok)
  - class `AgentTaskResult` L51-61 (~75 tok)
  - class `WorkflowExecutionResponse` L62-85 (~180 tok)
  - fn `execute_workflow` L86-219 (~1370 tok)
- `pipeline.py` — 3D Generation Pipeline API. (~3185 tok)
  - class `JobStatus` L26-35 (~58 tok)
  - class `QualityTier` L36-43 (~39 tok)
  - class `Provider` L44-51 (~41 tok)
  - class `BatchGenerateRequest` L52-66 (~153 tok)
  - class `BatchGenerateResponse` L67-82 (~94 tok)
  - class `GenerateSingleRequest` L83-91 (~84 tok)
  - class `GenerateSingleResponse` L92-105 (~97 tok)
  - class `JobListResponse` L106-114 (~46 tok)
  - class `FidelityBreakdown` L115-123 (~48 tok)
  - class `FidelityResponse` L124-134 (~62 tok)
  - class `ProviderInfo` L135-145 (~62 tok)
  - class `ProvidersResponse` L146-151 (~32 tok)
  - class `ProviderStatus` L152-160 (~44 tok)
  - class `CostEstimateRequest` L161-168 (~43 tok)
  - class `CostEstimateResponse` L169-197 (~233 tok)
  - fn `start_batch_generation` L198-232 (~308 tok)
  - fn `get_job_status` L233-251 (~132 tok)
  - fn `list_jobs` L252-282 (~248 tok)
  - fn `generate_single_model` L283-308 (~235 tok)
  - fn `get_fidelity_score` L309-334 (~218 tok)
  - fn `approve_fidelity` L335-347 (~94 tok)
  - fn `reject_fidelity` L348-360 (~94 tok)
  - fn `list_providers` L361-391 (~249 tok)
  - fn `get_provider_status` L392-410 (~125 tok)
  - fn `estimate_cost` L411-426 (~138 tok)
- `rag_anything.py` — API: POST, GET, DELETE (4 endpoints) (~2041 tok)
  - class `IngestResponse` L42-50 (~48 tok)
  - class `QueryRequest` L51-63 (~154 tok)
  - class `QueryResponse` L64-72 (~51 tok)
  - class `CollectionInfo` L73-85 (~93 tok)
  - fn `_metering` L86-89 (~18 tok)
  - fn `_checker` L90-93 (~38 tok)
  - fn `_service` L94-114 (~207 tok)
  - fn `ingest_document` L115-161 (~500 tok)
  - fn `query_collection` L162-191 (~274 tok)
  - fn `list_collections` L192-212 (~225 tok)
  - fn `delete_collection` L213-219 (~59 tok)
- `social_media.py` — API: POST, GET (4 endpoints) (~4789 tok)
  - class `GeneratePostRequest` L44-73 (~271 tok)
  - class `GenerateCampaignRequest` L74-104 (~257 tok)
  - class `SchedulePostRequest` L105-129 (~199 tok)
  - class `PublishPostRequest` L130-145 (~110 tok)
  - class `SocialPostResponse` L146-165 (~158 tok)
  - class `CampaignResponse` L166-176 (~56 tok)
  - class `PlatformAnalyticsResponse` L177-189 (~87 tok)
  - class `AnalyticsResponse` L190-198 (~56 tok)
  - class `QueueResponse` L199-205 (~38 tok)
  - class `SuccessResponse` L206-218 (~107 tok)
  - fn `_get_agent` L219-245 (~259 tok)
  - fn `generate_post` L246-318 (~698 tok)
  - fn `generate_campaign` L319-371 (~486 tok)
  - fn `get_queue` L372-407 (~309 tok)
  - fn `get_analytics` L408-440 (~288 tok)
  - fn `schedule_post` L441-506 (~551 tok)
  - fn `publish_post` L507-566 (~484 tok)
- `sync.py` — Pydantic: TriggerSyncRequest (8 fields) (~2272 tok)
  - class `TriggerSyncRequest` L66-88 (~237 tok)
  - fn `get_sync_status` L89-111 (~226 tok)
  - fn `trigger_sync` L112-174 (~595 tok)
  - fn `sync_round_table_to_hf` L175-203 (~307 tok)
  - fn `sync_health_check` L204-240 (~356 tok)
- `training_status.py` — Pydantic: TrainingProgressResponse (60 fields) (~7873 tok)
  - class `TrainingProgressResponse` L94-142 (~761 tok)
  - class `TrainingJobInfo` L143-161 (~288 tok)
  - class `TrainingJobsListResponse` L162-172 (~139 tok)
  - class `ExportRequest` L173-208 (~356 tok)
  - class `ExportResponse` L209-224 (~202 tok)
  - fn `_validate_job_id` L225-246 (~169 tok)
  - fn `_safe_path_resolve` L247-276 (~296 tok)
  - fn `_load_progress_file` L277-294 (~213 tok)
  - fn `_load_status_file` L295-312 (~207 tok)
  - fn `_find_training_versions` L313-331 (~177 tok)
  - fn `_load_round_table_results` L332-352 (~219 tok)
  - fn `get_training_status` L353-406 (~563 tok)
  - fn `list_training_jobs` L407-485 (~788 tok)
  - fn `get_training_job` L486-524 (~370 tok)
  - fn `export_round_table_to_hf` L525-699 (~1969 tok)
  - fn `training_health_check` L700-733 (~329 tok)
- `woocommerce_webhooks.py` — WooCommerce Webhooks API. (~562 tok)
  - fn `handle_order_webhook` L20-42 (~214 tok)
  - fn `handle_product_webhook` L43-63 (~191 tok)
- `wordpress_agent.py` — WordPress Bridge Agent API — SSE streaming endpoint + webhook dispatch. (~1682 tok)
  - class `AgentExecuteRequest` L32-42 (~122 tok)
  - class `WebhookDispatchRequest` L43-57 (~151 tok)
  - fn `execute_agent` L58-103 (~464 tok)
  - fn `dispatch_webhook` L104-162 (~674 tok)
- `wordpress_integration.py` — WordPress Integration API Endpoints. (~3408 tok)
  - class `WordPressSettings` L32-55 (~289 tok)
  - fn `get_settings` L56-71 (~151 tok)
  - fn `verify_webhook_signature` L72-100 (~233 tok)
  - fn `verify_webhook` L101-135 (~282 tok)
  - fn `sync_product` L136-163 (~255 tok)
  - fn `sync_collection` L164-212 (~525 tok)
  - fn `order_created_webhook` L213-243 (~260 tok)
  - fn `order_updated_webhook` L244-275 (~287 tok)
  - fn `product_updated_webhook` L276-326 (~531 tok)
  - fn `wordpress_health` L327-361 (~353 tok)
- `wordpress_theme.py` — WordPress Theme Management API. (~1284 tok)
  - class `ThemeConfig` L27-36 (~58 tok)
  - class `ThemeDeployRequest` L37-44 (~67 tok)
  - fn `get_theme_config` L45-58 (~107 tok)
  - fn `deploy_theme` L59-131 (~847 tok)
- `wordpress.py` — WordPress Integration API. (~910 tok)
  - class `WordPressSyncRequest` L21-29 (~50 tok)
  - class `WordPressSyncResponse` L30-38 (~55 tok)
  - fn `_get_wp_creds` L39-52 (~176 tok)
  - fn `sync_to_wordpress` L53-79 (~268 tok)
  - fn `get_wordpress_status` L80-100 (~212 tok)

## api/v1/analytics/

- `__init__.py` — Analytics API module for DevSkyy admin dashboard. (~187 tok)
- `alert_configs.py` — Alert Configuration API Endpoints for Admin Dashboard. (~7266 tok)
  - class `ConditionType` L42-49 (~39 tok)
  - class `ConditionOperator` L50-60 (~48 tok)
  - class `SeverityLevel` L61-68 (~38 tok)
  - class `NotificationChannel` L69-82 (~98 tok)
  - class `AlertConfigBase` L83-116 (~498 tok)
  - class `AlertConfigCreate` L117-122 (~31 tok)
  - class `AlertConfigUpdate` L123-142 (~259 tok)
  - class `AlertConfigResponse` L143-167 (~187 tok)
  - class `AlertConfigListResponse` L168-178 (~62 tok)
  - class `AlertConfigCreateResponse` L179-186 (~46 tok)
  - class `AlertConfigUpdateResponse` L187-194 (~46 tok)
  - class `AlertConfigDeleteResponse` L195-207 (~94 tok)
  - fn `parse_notification_channels` L208-216 (~74 tok)
  - fn `parse_json_field` L217-225 (~55 tok)
  - fn `row_to_response` L226-263 (~493 tok)
  - fn `list_alert_configs` L264-373 (~1146 tok)
  - fn `create_alert_config` L374-476 (~1094 tok)
  - fn `get_alert_config` L477-538 (~541 tok)
  - fn `update_alert_config` L539-691 (~1574 tok)
  - fn `delete_alert_config` L692-746 (~496 tok)
- `alerts.py` — Alert History and Acknowledgment API Endpoints for Admin Dashboard. (~8514 tok)
  - class `AlertStatus` L39-46 (~42 tok)
  - class `AlertSeverity` L47-59 (~92 tok)
  - class `NotificationRecord` L60-69 (~68 tok)
  - class `AlertMetadata` L70-82 (~129 tok)
  - class `AlertHistoryItem` L83-100 (~128 tok)
  - class `AlertHistoryResponse` L101-111 (~60 tok)
  - class `ActiveAlertsResponse` L112-123 (~68 tok)
  - class `AcknowledgeRequest` L124-129 (~54 tok)
  - class `AcknowledgeResponse` L130-139 (~59 tok)
  - class `ResolveRequest` L140-147 (~58 tok)
  - class `ResolveResponse` L148-157 (~54 tok)
  - class `BulkAcknowledgeRequest` L158-168 (~97 tok)
  - class `BulkAcknowledgeResult` L169-176 (~47 tok)
  - class `BulkAcknowledgeResponse` L177-192 (~123 tok)
  - fn `parse_json_field` L193-202 (~70 tok)
  - fn `build_alert_metadata` L203-252 (~544 tok)
  - fn `get_alert_history` L253-433 (~2036 tok)
  - fn `get_active_alerts` L434-574 (~1421 tok)
  - fn `acknowledge_alert` L575-674 (~898 tok)
  - fn `resolve_alert` L675-785 (~994 tok)
  - fn `bulk_acknowledge_alerts` L786-900 (~1142 tok)
- `business.py` — Business Metrics API Endpoints for SkyyRose Admin Dashboard. (~8201 tok)
  - class `TimeGranularity` L38-46 (~49 tok)
  - class `ComparisonPeriod` L47-58 (~105 tok)
  - class `MetricValue` L59-67 (~70 tok)
  - class `BusinessOverview` L68-79 (~83 tok)
  - class `BusinessOverviewResponse` L80-88 (~52 tok)
  - class `TimeseriesDataPoint` L89-96 (~49 tok)
  - class `SalesBreakdown` L97-104 (~57 tok)
  - class `SalesTimeseriesResponse` L105-118 (~98 tok)
  - class `ProductPerformance` L119-134 (~100 tok)
  - class `ProductPerformanceResponse` L135-146 (~80 tok)
  - class `CollectionMetrics` L147-158 (~74 tok)
  - class `CollectionMetricsResponse` L159-168 (~62 tok)
  - class `FunnelStage` L169-178 (~62 tok)
  - class `ConversionFunnelResponse` L179-194 (~126 tok)
  - fn `calculate_change` L195-210 (~130 tok)
  - fn `get_period_metrics` L211-248 (~330 tok)
  - fn `get_business_overview` L249-347 (~1140 tok)
  - fn `get_sales_timeseries` L348-472 (~1279 tok)
  - fn `get_product_performance` L473-606 (~1424 tok)
  - fn `get_collection_metrics` L607-719 (~1180 tok)
  - fn `get_conversion_funnel` L720-838 (~1347 tok)
- `dashboard.py` — Dashboard Summary API for DevSkyy Admin Dashboard. (~6079 tok)
  - class `DashboardSection` L43-51 (~46 tok)
  - class `AlertSeverity` L52-59 (~38 tok)
  - class `PipelineStatus` L60-73 (~100 tok)
  - class `ServiceHealth` L74-82 (~60 tok)
  - class `SystemHealthSection` L83-94 (~101 tok)
  - class `MLPipelineInfo` L95-106 (~83 tok)
  - class `MLPipelinesSection` L107-118 (~68 tok)
  - class `BusinessMetric` L119-126 (~56 tok)
  - class `BusinessSection` L127-138 (~92 tok)
  - class `AlertInfo` L139-150 (~62 tok)
  - class `AlertsSection` L151-161 (~58 tok)
  - class `DashboardSummaryResponse` L162-180 (~166 tok)
  - class `DashboardCache` L181-261 (~782 tok)
  - fn `fetch_system_health` L262-315 (~434 tok)
  - fn `fetch_ml_pipelines` L316-360 (~441 tok)
  - fn `fetch_business_metrics` L361-446 (~972 tok)
  - fn `fetch_active_alerts` L447-490 (~428 tok)
  - fn `get_allowed_sections` L491-523 (~305 tok)
  - fn `get_dashboard_summary` L524-665 (~1455 tok)
- `health.py` — System Health Metrics API Endpoints for DevSkyy Admin Dashboard. (~7634 tok)
  - class `TimeRange` L48-56 (~50 tok)
  - class `SystemStatus` L57-69 (~96 tok)
  - class `LatencyMetrics` L70-78 (~98 tok)
  - class `ErrorMetrics` L79-86 (~84 tok)
  - class `HealthOverview` L87-99 (~166 tok)
  - class `HealthOverviewResponse` L100-107 (~48 tok)
  - class `EndpointPerformance` L108-118 (~123 tok)
  - class `APIPerformanceResponse` L119-132 (~102 tok)
  - class `ConnectionPoolMetrics` L133-142 (~128 tok)
  - class `QueryLatencyMetrics` L143-151 (~112 tok)
  - class `DatabaseHealthResponse` L152-163 (~114 tok)
  - class `HealthTimeseriesDataPoint` L164-173 (~65 tok)
  - class `HealthTimeseriesResponse` L174-189 (~126 tok)
  - fn `format_uptime` L190-203 (~110 tok)
  - fn `get_time_range_seconds` L204-214 (~90 tok)
  - fn `get_granularity` L215-225 (~93 tok)
  - fn `extract_histogram_percentiles` L226-263 (~401 tok)
  - fn `extract_counter_value` L264-281 (~227 tok)
  - fn `extract_gauge_value` L282-294 (~165 tok)
  - fn `determine_system_status` L295-318 (~272 tok)
  - fn `get_health_overview` L319-405 (~881 tok)
  - fn `get_api_performance` L406-524 (~1349 tok)
  - fn `get_database_health` L525-648 (~1313 tok)
  - fn `get_health_timeseries` L649-743 (~1064 tok)
- `ml_pipelines.py` — api/v1/analytics/ml_pipelines.py (~4848 tok)
  - class `TimeRange` L41-50 (~51 tok)
  - class `MLProvider` L51-60 (~53 tok)
  - class `PipelineType` L61-70 (~71 tok)
  - class `JobStatus` L71-85 (~104 tok)
  - class `LatencyPercentiles` L86-93 (~85 tok)
  - class `PipelineMetrics` L94-106 (~166 tok)
  - class `ProviderMetrics` L107-122 (~130 tok)
  - class `ThreeDMetrics` L123-136 (~135 tok)
  - class `DescriptionMetrics` L137-149 (~100 tok)
  - class `AssetMetrics` L150-161 (~86 tok)
  - class `MLOverviewResponse` L162-175 (~122 tok)
  - class `ThreeDAnalyticsResponse` L176-184 (~87 tok)
  - class `DescriptionAnalyticsResponse` L185-193 (~91 tok)
  - class `AssetAnalyticsResponse` L194-201 (~64 tok)
  - class `ProviderAnalyticsResponse` L202-215 (~128 tok)
  - fn `get_time_range_start` L216-231 (~168 tok)
  - fn `generate_mock_latency` L232-243 (~84 tok)
  - fn `generate_mock_pipeline_metrics` L244-266 (~212 tok)
  - fn `generate_mock_provider_metrics` L267-304 (~363 tok)
  - fn `get_ml_overview` L305-356 (~508 tok)
  - fn `get_3d_analytics` L357-421 (~593 tok)
  - fn `get_description_analytics` L422-485 (~577 tok)
  - fn `get_asset_analytics` L486-525 (~350 tok)
  - fn `get_provider_analytics` L526-555 (~232 tok)

## api/v1/clothing_3d/

- `__init__.py` — FastAPI surface for the clothing 3D pipeline. (~95 tok)
- `router.py` — FastAPI router for the clothing 3D pipeline. (~3222 tok)
  - fn `get_pipeline` L78-86 (~92 tok)
  - fn `get_queue` L87-93 (~35 tok)
  - fn `get_store` L94-100 (~36 tok)
  - fn `get_idempotency` L101-117 (~133 tok)
  - fn `generate_endpoint` L118-155 (~393 tok)
  - fn `generate_async_endpoint` L156-203 (~453 tok)
  - fn `get_job_endpoint` L204-225 (~201 tok)
  - fn `list_jobs_endpoint` L226-252 (~214 tok)
  - fn `health_endpoint` L253-280 (~304 tok)
  - fn `ready_endpoint` L281-312 (~282 tok)
  - fn `info_endpoint` L313-346 (~303 tok)
  - fn `metrics_endpoint` L347-353 (~65 tok)
- `schemas.py` — API schemas — thin Pydantic wrappers over the pipeline models. (~396 tok)

## api/v1/portal/

- `__init__.py` (~230 tok)
- `billing.py` — API: GET, POST (2 endpoints) (~1657 tok)
  - fn `_stripe` L34-42 (~70 tok)
  - class `InvoiceItem` L43-55 (~92 tok)
  - class `InvoiceListResponse` L56-63 (~39 tok)
  - class `PortalSessionRequest` L64-76 (~104 tok)
  - class `PortalSessionResponse` L77-93 (~116 tok)
  - fn `list_invoices` L94-144 (~452 tok)
  - fn `create_portal_session` L145-189 (~414 tok)
  - fn `_resolve_customer_id` L190-196 (~116 tok)
- `subscriptions.py` — API: POST, GET, PATCH, DELETE (4 endpoints) (~2669 tok)
  - fn `_stripe` L39-42 (~17 tok)
  - fn `_metering` L43-51 (~80 tok)
  - class `SubscribeRequest` L52-66 (~145 tok)
  - class `UpgradeRequest` L67-81 (~138 tok)
  - class `SubscriptionStatusResponse` L82-94 (~95 tok)
  - class `SubscribeResponse` L95-116 (~163 tok)
  - fn `subscribe` L117-183 (~603 tok)
  - fn `get_current_subscription` L184-220 (~340 tok)
  - fn `update_subscription` L221-277 (~532 tok)
  - fn `cancel_subscription` L278-300 (~233 tok)
- `team.py` — API: GET, POST, DELETE, PATCH (4 endpoints) (~2448 tok)
  - class `TeamMember` L40-47 (~35 tok)
  - class `TeamListResponse` L48-56 (~48 tok)
  - class `InviteRequest` L57-70 (~129 tok)
  - class `InviteResponse` L71-80 (~48 tok)
  - class `RoleUpdateRequest` L81-101 (~195 tok)
  - fn `_get_members` L102-105 (~26 tok)
  - fn `_find_member` L106-112 (~50 tok)
  - fn `_require_tenant` L113-123 (~118 tok)
  - fn `_require_admin` L124-145 (~214 tok)
  - fn `list_team_members` L146-176 (~221 tok)
  - fn `invite_member` L177-222 (~354 tok)
  - fn `remove_member` L223-266 (~336 tok)
  - fn `update_member_role` L267-309 (~344 tok)
- `usage.py` — API: GET (2 endpoints) (~1688 tok)
  - fn `_metering` L36-44 (~78 tok)
  - class `IntentUsageSummary` L45-53 (~51 tok)
  - class `UsageSummaryResponse` L54-63 (~54 tok)
  - class `MonthlyUsageRecord` L64-71 (~42 tok)
  - class `UsageHistoryResponse` L72-90 (~129 tok)
  - fn `get_current_usage` L91-147 (~477 tok)
  - fn `get_usage_history` L148-184 (~332 tok)
  - fn `_current_period` L185-188 (~23 tok)
  - fn `_last_n_periods` L189-202 (~127 tok)
  - fn `_intent_to_quota_field` L203-214 (~127 tok)

## api/v2/

- `__init__.py` (~149 tok)
- `assets.py` — API: GET, DELETE (3 endpoints) (~2756 tok)
  - fn `_get_api_key_dependency` L42-71 (~313 tok)
  - class `AssetResponse` L72-81 (~68 tok)
  - class `AssetListResponse` L82-93 (~84 tok)
  - fn `_get_redis` L94-106 (~108 tok)
  - fn `_require_redis` L107-116 (~71 tok)
  - fn `_fetch_asset` L117-128 (~102 tok)
  - fn `_file_size` L129-136 (~55 tok)
  - fn `_collect_assets_from_results` L137-185 (~420 tok)
  - fn `_infer_asset_type` L186-209 (~217 tok)
  - fn `list_assets` L210-278 (~606 tok)
  - fn `get_asset` L279-301 (~162 tok)
  - fn `delete_asset` L302-323 (~204 tok)
- `characters.py` — API: POST, GET, PATCH (5 endpoints) (~3320 tok)
  - fn `_get_api_key_dependency` L47-76 (~313 tok)
  - class `CreateCharacterRequest` L77-95 (~161 tok)
  - class `UpdateCharacterRequest` L96-105 (~80 tok)
  - class `CharacterResponse` L106-115 (~56 tok)
  - class `CharacterListResponse` L116-127 (~87 tok)
  - fn `_get_redis` L128-140 (~109 tok)
  - fn `_require_redis` L141-150 (~71 tok)
  - fn `_store_character` L151-158 (~90 tok)
  - fn `_fetch_character` L159-175 (~170 tok)
  - fn `_build_character_response` L176-221 (~407 tok)
  - fn `create_character` L222-247 (~194 tok)
  - fn `get_rosie` L248-292 (~357 tok)
  - fn `get_character` L293-312 (~150 tok)
  - fn `list_characters` L313-355 (~342 tok)
  - fn `update_character` L356-386 (~322 tok)
- `creative.py` — API: POST, GET (3 endpoints) (~4040 tok)
  - fn `_get_redis` L50-75 (~229 tok)
  - fn `_get_api_key_dependency` L76-105 (~313 tok)
  - class `CreateOperationRequest` L106-131 (~216 tok)
  - class `OperationResponse` L132-143 (~92 tok)
  - class `OperationListResponse` L144-155 (~87 tok)
  - fn `_require_redis` L156-165 (~71 tok)
  - fn `_store_operation` L166-180 (~166 tok)
  - fn `_fetch_operation` L181-211 (~344 tok)
  - fn `_register_webhook_for_op` L212-222 (~120 tok)
  - fn `_cancel_queued_op` L223-239 (~160 tok)
  - fn `create_operation` L240-320 (~768 tok)
  - fn `get_operation` L321-344 (~189 tok)
  - fn `list_operations` L345-404 (~556 tok)
  - fn `cancel_operation` L405-434 (~260 tok)
- `health.py` — API: GET (2 endpoints) (~1993 tok)
  - fn `_get_api_key_dependency` L34-57 (~215 tok)
  - class `ServiceStatus` L58-63 (~47 tok)
  - class `HealthResponse` L64-69 (~40 tok)
  - class `UsageSummaryResponse` L70-83 (~96 tok)
  - fn `_get_redis` L84-96 (~108 tok)
  - fn `_check_graph` L97-117 (~180 tok)
  - fn `health` L118-159 (~328 tok)
  - fn `usage_summary` L160-239 (~749 tok)
- `webhooks.py` — API: POST, GET, DELETE (5 endpoints) (~2941 tok)
  - fn `_get_api_key_dependency` L38-70 (~334 tok)
  - class `RegisterWebhookRequest` L71-94 (~211 tok)
  - class `WebhookResponse` L95-103 (~44 tok)
  - class `WebhookListResponse` L104-108 (~26 tok)
  - class `TestWebhookResponse` L109-120 (~101 tok)
  - fn `_get_redis` L121-124 (~19 tok)
  - fn `_require_redis` L125-134 (~71 tok)
  - fn `_fetch_webhook_record` L135-145 (~101 tok)
  - fn `_list_webhook_records` L146-159 (~116 tok)
  - fn `_raw_to_response` L160-176 (~162 tok)
  - fn `_delete_webhook_record` L177-187 (~102 tok)
  - fn `_store_extra_fields` L188-207 (~218 tok)
  - fn `register_webhook` L208-250 (~343 tok)
  - fn `list_webhooks` L251-266 (~133 tok)
  - fn `get_webhook` L267-286 (~149 tok)
  - fn `delete_webhook` L287-307 (~161 tok)
  - fn `test_webhook` L308-350 (~369 tok)

## assets/

- `INVENTORY.json` (~74 tok)

## assets/2d-25d-assets/

- `master_manifest.json` (~1840 tok)
- `product_image_mappings.json` (~5064 tok)

## assets/3d-models/signature/

- `5b4b4dbd-3f7c-49ce-a158-336d8d535b00.html` — Declares shouldSkipAnalytics (~1318 tok)
- `5b4b4dbd-3f7c-49ce-a158-336d8d535b00(1).html` — Declares shouldSkipAnalytics (~1318 tok)
- `SIGNATURE_SPEC.md` — SKYYROSE SIGNATURE COLLECTION PAGE SPECIFICATION (~3287 tok)

## assets/3d-models/signature/_Signature Collection_/

- `5b4b4dbd-3f7c-49ce-a158-336d8d535b00.html` — Declares shouldSkipAnalytics (~1318 tok)
- `5b4b4dbd-3f7c-49ce-a158-336d8d535b00(1).html` — Declares shouldSkipAnalytics (~1318 tok)

## assets/brand/

- `brand.yaml` — /*.{php,py} or frontend/**/*.{ts,tsx,js,jsx} file. (~2673 tok)

## assets/hub/

  - fn `faceof` L56-62 (~51 tok)
  - fn `engine` L63-80 (~129 tok)
  - fn `fileurl` L81-84 (~20 tok)
  - fn `_index_images` L85-99 (~95 tok)
  - fn `candidates_for` L100-116 (~175 tok)
  - fn `cell` L117-264 (~2551 tok)
  - fn `engine_of` L55-66 (~84 tok)
  - fn `provenance` L67-91 (~211 tok)
  - fn `review_slug_for` L92-99 (~70 tok)
  - fn `first_existing` L100-118 (~168 tok)
  - fn `add_product` L119-142 (~219 tok)
  - fn `add_pending` L143-238 (~1011 tok)
  - fn `scope_from_name` L239-306 (~723 tok)
  - fn `fileurl` L25-28 (~17 tok)
  - fn `faceof` L29-32 (~29 tok)
  - fn `cell` L33-114 (~1626 tok)
  - fn `_kv` L50-76 (~291 tok)
  - fn `is_ref` L77-84 (~86 tok)
  - fn `is_gen_source` L85-89 (~57 tok)
  - fn `engine_of` L90-103 (~100 tok)
  - fn `provenance` L104-116 (~107 tok)
  - fn `copy_master` L117-192 (~821 tok)
  - fn `fmt_pick` L193-226 (~396 tok)
  - fn `_plan_add` L227-360 (~1111 tok)
- `manifest.json` (~15606 tok)

## assets/marketing-keepers/

- `README.md` — Project documentation (~573 tok)

## assets/products/

- `manifest.json` (~11929 tok)

## assets/products/masters/

- `README.md` — Project documentation (~772 tok)

## assets/products/references/

- `beanie-3-colorways-techflat.avif` (~1650 tok)
- `beanie-3-colorways-techflat.webp` (~1666 tok)
- `black-rose-logo-reference.avif` (~7603 tok)
- `black-rose-logo-reference.webp` (~10817 tok)
- `BLACK-Rose-slide-sample.avif` (~19787 tok)
- `leather-rose-patch-closeup.avif` (~6831 tok)
- `leather-rose-patch-closeup.webp` (~10176 tok)
- `love-hurts-heart-logo.avif` (~25723 tok)
- `love-hurts-heart-logo.webp` (~35959 tok)
- `love-hurts-logo-reference.avif` (~9493 tok)
- `love-hurts-logo-reference.webp` (~12610 tok)
- `love-hurts-rose-logo.avif` (~4844 tok)
- `love-hurts-rose-logo.webp` (~4489 tok)
- `LoveHurts-Slides Sample.avif` (~60092 tok)
- `Mint-Lavender-hoodie-promo-1.avif` (~43706 tok)
- `mint-set-back-source.avif` (~1025 tok)
- `mint-set-back-source.webp` (~1000 tok)
- `mint-set-front-source.avif` (~1295 tok)
- `mint-set-front-source.webp` (~1319 tok)
- `mint-set-techflat.avif` (~1629 tok)
- `mint-set-techflat.webp` (~1721 tok)
- `patch-hockey.avif` (~9944 tok)
- `patch-hockey.webp` (~13652 tok)
- `patch-nba-basketball.avif` (~7414 tok)
- `patch-nba-basketball.webp` (~11502 tok)
- `patch-nfl-football.avif` (~18519 tok)
- `patch-nfl-football.webp` (~26473 tok)
- `Signature-T.avif` (~23528 tok)
- `signature-tee-beanie-joggers-flatlay.avif` (~10844 tok)
- `signature-tee-beanie-joggers-flatlay.webp` (~14012 tok)
- `Stay-Golden-T-Shirt.avif` (~3541 tok)
- `winter-collection-flatlay.avif` (~2576 tok)
- `winter-collection-flatlay.webp` (~3189 tok)

## assets/products/source-photos/

- `CLAUDE.md` — assets/products/source-photos/ (~291 tok)
- `HANDOFF.md` — Source Products Catalog — Handoff (~2048 tok)
- `manifest.json` (~7156 tok)

## assets/products/source-photos/black-rose/

- `br-012-last-oakland-baseball-back.webp` (~8657 tok)
- `br-012-last-oakland-baseball-front.webp` (~9392 tok)
- `br-014-baseball-classic-giants.webp` (~3250 tok)
- `br-015-baseball-classic-white.webp` (~3250 tok)
- `CLAUDE.md` (~11 tok)

## assets/products/source-photos/brand-assets/

- `CLAUDE.md` (~11 tok)

## assets/products/source-photos/kids/

- `CLAUDE.md` (~11 tok)

## assets/products/source-photos/love-hurts/

- `CLAUDE.md` (~11 tok)

## assets/products/source-photos/pre-order/

- `CLAUDE.md` (~11 tok)

## assets/products/source-photos/signature/

- `CLAUDE.md` (~11 tok)
- `sg-015-windbreaker-set.webp` (~8200 tok)

## assets/prompts/

- `registry.yaml` — SkyyRose Prompt Library — SINGLE SOURCE OF TRUTH for prompts with production impact (~1402 tok)

## assets/specifications/

- `BLACK_ROSE_SPEC.md` — SKYYROSE BLACK ROSE COLLECTION PAGE SPECIFICATION (~6467 tok)
- `GLOBAL_CONFIG.md` — SKYYROSE GLOBAL CONFIGURATION & COMPONENT LIBRARY (~5085 tok)
- `HOMEPAGE_SPEC.md` — SKYYROSE HOMEPAGE SPECIFICATION (~10079 tok)
- `LOVE_HURTS_SPEC.md` — SKYYROSE LOVE HURTS COLLECTION PAGE SPECIFICATION (~6385 tok)
- `PRODUCT_PAGE_SPEC.md` — SKYYROSE PRODUCT PAGE (PDP) SPECIFICATION (~4578 tok)
- `SHOP_ARCHIVE_SPEC.md` — SKYYROSE SHOP ARCHIVE PAGE SPECIFICATION (~3901 tok)
- `SIGNATURE_SPEC.md` — SKYYROSE SIGNATURE COLLECTION PAGE SPECIFICATION (~3287 tok)
- `SPINNING_LOGO_SPEC.md` — SKYYROSE UPDATED DESIGN TOKENS & SPINNING LOGO (~4184 tok)

## billing/

- `__init__.py` (~307 tok)
- `entitlements.py` — EntitlementResult: check, get_upgrade_message (~1530 tok)
  - class `EntitlementResult` L54-79 (~232 tok)
  - class `EntitlementChecker` L80-172 (~890 tok)
- `metering.py` — UsageMetering: record, get_usage, get_all_usage, check_quota + 1 more (~2327 tok)
  - fn `_current_period` L32-36 (~40 tok)
  - fn `_key` L37-40 (~34 tok)
  - class `UsageMetering` L41-230 (~2014 tok)
- `middleware.py` — billing_middleware (~1700 tok)
  - fn `_get_checker` L47-58 (~106 tok)
  - fn `billing_middleware` L59-151 (~978 tok)
  - fn `_record_usage_async` L152-170 (~185 tok)
  - fn `_is_creative_endpoint` L171-174 (~55 tok)
- `plans.py` — TierLimits: get_limits, intent_allowed, quota_remaining (~1686 tok)
  - class `TierLimits` L33-145 (~1012 tok)
  - fn `get_limits` L146-158 (~88 tok)
  - fn `intent_allowed` L159-177 (~148 tok)
  - fn `quota_remaining` L178-199 (~182 tok)
- `stripe_client.py` — StripeClient: create_customer, create_subscription, cancel_subscription, get_subscription + 3 more (~2275 tok)
  - class `StripeClient` L29-238 (~2088 tok)
- `webhooks.py` — handle_stripe_webhook (~2106 tok)
  - fn `handle_stripe_webhook` L54-113 (~696 tok)
  - fn `_dispatch` L114-127 (~141 tok)
  - fn `_handle_subscription_change` L128-159 (~330 tok)
  - fn `_handle_invoice_paid` L160-172 (~118 tok)
  - fn `_handle_invoice_payment_failed` L173-188 (~144 tok)
  - fn `_tier_from_status_and_items` L189-207 (~206 tok)
  - fn `_load_stripe` L208-216 (~62 tok)

## ci-env/

- `.gitignore` — Git ignore rules (~24 tok)
- `README.md` — Project documentation (~1316 tok)
- `setup.sh` — ci-env/setup.sh — Build the isolated Python toolchain that scripts/ci-local.sh (~922 tok)

## cli/

- `__init__.py` — DevSkyy CLI tools. (~34 tok)
- `prompt_enhance.py` — TaskMode: load_config, get_config, to_dict, main (~10847 tok)
  - fn `load_config` L55-79 (~220 tok)
  - fn `get_config` L80-92 (~101 tok)
  - class `TaskMode` L93-104 (~66 tok)
  - class `OutputFormat` L105-112 (~39 tok)
  - class `PromptTechnique` L113-131 (~163 tok)
  - class `PromptAnalysis` L132-143 (~87 tok)
  - class `TechniqueSelection` L144-152 (~48 tok)
  - class `EnhancedPrompt` L153-279 (~1020 tok)
  - fn `main` L280-380 (~845 tok)
  - class `EnhancementError` L381-500 (~740 tok)
  - class `PromptAnalyzer` L501-620 (~1168 tok)
  - class `TechniqueSelector` L621-683 (~758 tok)
  - class `ContextScanner` L684-779 (~1015 tok)
  - class `PromptEnhancer` L780-952 (~2180 tok)
  - fn `_enhance_prompt` L953-1014 (~488 tok)
  - fn `_output_result` L1015-1078 (~607 tok)
  - fn `_show_stats` L1079-1125 (~440 tok)
  - fn `_init_config` L1126-1165 (~302 tok)
  - fn `_log_enhancement` L1166-1184 (~158 tok)
  - fn `cli` L1185-1192 (~32 tok)

## config/

- `__init__.py` (~465 tok)
- `ARCHITECTURE_DIAGRAM.md` — Security Monitoring & Alerting Architecture (~2696 tok)
- `asset_tagging.yaml` — Asset Tagging Configuration (~283 tok)
- `asset_taxonomy.yaml` — Asset taxonomy definition for style, mood, and color tags (~216 tok)
- `autotrain_config.yaml` (~131 tok)
- `collections.py` — Canonical collection registry for SkyyRose. (~1293 tok)
  - class `Collection` L18-27 (~86 tok)
  - class `CollectionMeta` L28-88 (~696 tok)
  - fn `get_collection` L89-103 (~145 tok)
  - fn `get_meta` L104-108 (~43 tok)
  - fn `get_aesthetic` L109-113 (~48 tok)
  - fn `get_intro` L114-118 (~49 tok)
  - fn `get_copy_voice` L119-133 (~93 tok)
- `load_env.py` — load_project_env (~506 tok)
  - fn `_find_project_root` L20-30 (~116 tok)
  - fn `load_project_env` L31-66 (~283 tok)
- `load-env.js` — Universal environment loader for DevSkyy (Node.js). (~366 tok)
- `MONITORING_QUICKSTART.md` — Security Monitoring Quick Start Guide (~2142 tok)
- `settings.py` — DevSkyySettings: get_hf_token, get_fashn_key, validate_required_keys, get_settings + 1 more (~3015 tok)
  - class `DevSkyySettings` L45-159 (~1657 tok)
  - fn `get_settings` L160-213 (~502 tok)
  - fn `print_config_status` L214-261 (~462 tok)
- `skyyrose_3d_config.yaml` — SkyyRose 3D Asset Generation Configuration (~706 tok)

## config/alertmanager/

- `alertmanager.yml` (~468 tok)

## config/claude/

- `desktop.example.json` (~900 tok)

## config/grafana/

- `README.md` — Project documentation (~1949 tok)

## config/grafana/dashboards/

- `security-dashboard.json` (~4016 tok)

## config/grafana/provisioning/dashboards/

- `dashboard.yml` (~77 tok)

## config/grafana/provisioning/datasources/

- `prometheus.yml` (~63 tok)

## config/nginx/

- `nginx.conf` — Nginx configuration (~1416 tok)

## config/prometheus/

- `prometheus.yml` — Prometheus Configuration for DevSkyy Security Monitoring (~472 tok)

## config/prometheus/alerts/

- `security_alerts.yml` (~1967 tok)
- `security.yml` — Security Alert Rules for DevSkyy (~2041 tok)

## config/testing/

- `vitest.config.ts` — Vitest test configuration (~746 tok)

## config/typescript/

- `tsconfig.json` — TypeScript configuration (~540 tok)

## config/vite/

- `demo.config.ts` — Vite Configuration for SkyyRose Collection 3D Experience Demos (~236 tok)

## config/zero_trust/

- `zero_trust_config.yaml` — Zero Trust Architecture Configuration (~1468 tok)

## core/

- `__init__.py` (~384 tok)
- `performance.py` — View: get (~4602 tok)
  - class `CacheMetrics` L45-82 (~337 tok)
  - fn `get_cache_metrics` L83-92 (~89 tok)
  - fn `timed_lru_cache` L93-130 (~333 tok)
  - fn `async_lru_cache` L131-184 (~505 tok)
  - fn `instructor_cache` L185-276 (~923 tok)
  - class `HierarchicalCache` L277-381 (~912 tok)
  - class `AsyncConnectionPool` L382-431 (~462 tok)
  - class `LazyImport` L432-471 (~317 tok)
  - class `cached_property` L472-514 (~403 tok)
- `product_spec.py` — Unified product specification — single source of truth for all pipelines. (~1639 tok)
  - class `ProductSpec` L21-98 (~992 tok)
  - fn `from_concept` L99-115 (~160 tok)
  - fn `from_design_specs` L116-137 (~283 tok)
- `redis_cache.py` — RedisConfig: connect, disconnect, get_llm_response, set_llm_response + 1 more (~2134 tok)
  - class `RedisConfig` L42-63 (~246 tok)
  - class `RedisCache` L64-221 (~1598 tok)
- `structured_logging.py` — add_context_vars, bind_contextvars, unbind_contextvars, clear_contextvars + 2 more (~1831 tok)
  - fn `add_context_vars` L47-63 (~136 tok)
  - fn `bind_contextvars` L64-83 (~182 tok)
  - fn `unbind_contextvars` L84-101 (~141 tok)
  - fn `clear_contextvars` L102-106 (~41 tok)
  - fn `configure_logging` L107-191 (~807 tok)
  - fn `get_logger` L192-206 (~114 tok)
- `task_status_store.py` — API: GET (1 endpoints) (~3026 tok)
  - class `TaskStatusStore` L31-316 (~2590 tok)
  - fn `get_task_status_store` L317-328 (~90 tok)
  - fn `get_initialized_task_status_store` L329-346 (~158 tok)
- `token_tracker.py` — TaskType: calculate_cost, record, get_total_cost, get_total_tokens + 5 more (~4532 tok)
  - class `TaskType` L28-73 (~498 tok)
  - class `TokenUsage` L74-105 (~279 tok)
  - class `TokenTracker` L106-318 (~2009 tok)
  - fn `get_token_tracker` L319-334 (~166 tok)
  - fn `record_llm_usage` L335-373 (~381 tok)
  - fn `record_embedding_usage` L374-415 (~440 tok)
  - fn `record_gate_score` L416-455 (~412 tok)
  - fn `gate_scores` L456-470 (~176 tok)

## core/agents/

- `__init__.py` — Core agent interfaces. (~47 tok)
- `interfaces.py` — IAgent: execute, initialize, get_capabilities, execute_auto + 5 more (~981 tok)
  - class `IAgent` L26-60 (~240 tok)
  - class `ISuperAgent` L61-95 (~245 tok)
  - class `IAgentOrchestrator` L96-152 (~343 tok)

## core/auth/

- `__init__.py` (~542 tok)
- `interfaces.py` — ITokenValidator: validate_token, validate_token, is_token_revoked, authenticate + 15 more (~2126 tok)
  - class `ITokenValidator` L26-74 (~338 tok)
  - class `IAuthProvider` L75-162 (~608 tok)
  - class `ITokenBlacklist` L163-217 (~336 tok)
  - class `IRateLimiter` L218-274 (~335 tok)
  - class `IPasswordHasher` L275-321 (~310 tok)
- `models.py` — Pydantic: AuthCredentials (43 fields) (~1793 tok)
  - class `AuthCredentials` L20-40 (~124 tok)
  - class `TokenRequest` L41-47 (~34 tok)
  - class `TokenResponse` L48-62 (~186 tok)
  - class `TokenPair` L63-76 (~77 tok)
  - class `AuthResult` L77-97 (~155 tok)
  - class `UserBase` L98-122 (~186 tok)
  - class `UserCreate` L123-164 (~356 tok)
  - class `UserInDB` L165-213 (~542 tok)
- `role_hierarchy.py` — get_role_level, is_role_at_least, has_required_role, get_minimum_required_level + 2 more (~1149 tok)
  - fn `get_role_level` L26-42 (~90 tok)
  - fn `is_role_at_least` L43-64 (~178 tok)
  - fn `has_required_role` L65-84 (~168 tok)
  - fn `get_minimum_required_level` L85-103 (~151 tok)
  - fn `get_roles_at_or_above` L104-121 (~148 tok)
  - fn `get_highest_role_from_list` L122-151 (~214 tok)
- `token_payload.py` — representing: has_role, has_any_role, has_all_roles, get_highest_role + 2 more (~1188 tok)
  - class `TokenPayload` L22-145 (~1070 tok)
- `types.py` — Declares import (~1362 tok)
  - class `UserRole` L19-50 (~260 tok)
  - class `TokenType` L51-79 (~232 tok)
  - class `AuthStatus` L80-99 (~133 tok)
  - class `AuthErrorCode` L100-123 (~201 tok)
  - class `Permission` L124-168 (~335 tok)
  - class `SubscriptionTier` L169-183 (~93 tok)

## core/caching/

- `__init__.py` (~65 tok)
- `multi_tier_cache.py` — View: get (~2849 tok)
  - class `MultiTierCache` L39-233 (~1866 tok)
  - fn `get_cache` L234-241 (~63 tok)
  - fn `cached` L242-302 (~660 tok)

## core/cqrs/

- `__init__.py` (~110 tok)
- `command_bus.py` — class: register_handler, execute, create_product_handler (~1704 tok)
  - class `Command` L51-67 (~140 tok)
  - class `CommandBus` L68-124 (~558 tok)
  - fn `create_product_handler` L125-191 (~639 tok)
- `query_bus.py` — class: register_handler, execute (~659 tok)
  - class `Query` L33-45 (~94 tok)
  - class `QueryBus` L46-78 (~317 tok)

## core/errors/

- `__init__.py` — core/errors/__init__.py (~536 tok)
- `production_errors.py` — errors/production_errors.py (~8015 tok)
  - class `DevSkyErrorSeverity` L31-40 (~97 tok)
  - class `DevSkyErrorCode` L41-102 (~563 tok)
  - class `DevSkyError` L103-177 (~718 tok)
  - class `ValidationError` L178-204 (~201 tok)
  - class `AuthenticationError` L205-216 (~103 tok)
  - class `AuthorizationError` L217-240 (~186 tok)
  - class `RateLimitError` L241-269 (~213 tok)
  - class `ExternalServiceError` L270-298 (~261 tok)
  - class `DatabaseError` L299-321 (~170 tok)
  - class `ConfigurationError` L322-345 (~165 tok)
  - class `ResourceNotFoundError` L346-372 (~213 tok)
  - class `ResourceConflictError` L373-396 (~169 tok)
  - class `ThreeDGenerationError` L397-422 (~207 tok)
  - class `ImageProcessingError` L423-443 (~156 tok)
  - class `ModelFidelityError` L444-477 (~298 tok)
  - class `WordPressIntegrationError` L478-506 (~214 tok)
  - class `MCPServerError` L507-530 (~183 tok)
  - class `LLMProviderError` L531-557 (~204 tok)
  - class `ToolExecutionError` L558-581 (~182 tok)
  - class `AgentExecutionError` L582-605 (~185 tok)
  - class `PipelineError` L606-635 (~227 tok)
  - class `SyncError` L636-661 (~193 tok)
  - class `AssetNotFoundError` L662-685 (~161 tok)
  - fn `create_correlation_id` L686-695 (~85 tok)
  - fn `format_error_response` L696-736 (~292 tok)
  - class `SecurityError` L737-757 (~162 tok)
  - class `EncryptionError` L758-788 (~206 tok)
  - fn `error_handler` L789-900 (~1141 tok)
  - fn `classify_error` L901-944 (~370 tok)
  - class `ErrorResponse` L945-969 (~270 tok)

## core/events/

- `__init__.py` (~85 tok)
- `event_bus.py` — EventBus: subscribe, publish, get_dead_letters, clear_dead_letters (~745 tok)
  - class `EventBus` L21-80 (~624 tok)
- `event_handlers.py` — ProductEventHandler: handle, subscribe (~2366 tok)
  - class `ProductEventHandler` L30-218 (~2148 tok)
- `event_store.py` — Event: apply_event, append, get_events, replay (~2557 tok)
  - class `Event` L45-118 (~783 tok)
  - fn `apply_event` L119-132 (~150 tok)
  - class `EventStore` L133-257 (~1289 tok)

## core/feature_flags/

- `__init__.py` (~41 tok)
- `flag_manager.py` — class: create_flag, set_flag, get_flag, get_all_flags + 8 more (~4559 tok)
  - class `FeatureFlag` L55-89 (~400 tok)
  - class `FlagManager` L90-311 (~2359 tok)
  - class `RedisFlagManager` L312-425 (~1344 tok)

## core/llm/

- `__init__.py` (~442 tok)

## core/llm/domain/

- `__init__.py` — LLM Domain Layer. (~245 tok)
- `models.py` — Pydantic: LLMCapabilities (31 fields) (~1016 tok)
  - class `LLMCapabilities` L52-64 (~93 tok)
  - class `LLMRequest` L65-98 (~284 tok)
  - class `LLMResponse` L99-143 (~338 tok)
- `ports.py` — ILLMProvider: complete, stream, connect, close + 5 more (~1156 tok)
  - class `ILLMProvider` L42-94 (~381 tok)
  - class `ILLMRouter` L95-134 (~273 tok)
  - class `IProviderFactory` L135-177 (~265 tok)

## core/llm/infrastructure/

- `__init__.py` (~109 tok)
- `provider_factory.py` — ProviderFactory: create_provider, get_or_create_provider, get_capabilities, list_providers + 2 more (~2222 tok)
  - class `ProviderFactory` L103-265 (~1398 tok)

## core/llm/providers/

- `__init__.py` (~247 tok)

## core/llm/services/

- `__init__.py` (~206 tok)

## core/middleware/

- `__init__.py` (~52 tok)
- `tenant.py` — tenant_middleware (~1287 tok)
  - fn `tenant_middleware` L37-64 (~249 tok)
  - fn `_resolve_tenant` L65-91 (~300 tok)
  - fn `_internal_service_token_valid` L92-100 (~109 tok)
  - fn `_extract_jwt_claims` L101-139 (~357 tok)

## core/registry/

- `__init__.py` (~161 tok)
- `registrations.py` — View: get, delete (~1786 tok)
  - fn `register_core_services` L23-54 (~260 tok)
  - fn `register_ml_services` L55-77 (~189 tok)
  - fn `register_rag_services` L78-100 (~195 tok)
  - fn `register_llm_services` L101-123 (~170 tok)
  - fn `register_repositories` L124-140 (~134 tok)
  - fn `register_external_clients` L141-167 (~233 tok)
  - fn `register_all_services` L168-187 (~158 tok)
  - class `InMemoryCache` L188-206 (~129 tok)
  - class `MockMLPipeline` L207-216 (~78 tok)
  - class `MockRAGManager` L217-225 (~100 tok)
- `service_registry.py` — View: get, get (~1961 tok)
  - class `ServiceNotFoundError` L30-37 (~72 tok)
  - class `ServiceEntry` L38-93 (~469 tok)
  - class `ServiceRegistry` L94-227 (~1104 tok)
  - fn `register_service` L228-241 (~102 tok)
  - fn `get_service` L242-249 (~54 tok)

## core/repositories/

- `__init__.py` — Core repository interfaces. (~78 tok)
- `interfaces.py` — IRepository: get_by_id, create, update, delete + 7 more (~957 tok)
  - class `IRepository` L19-103 (~549 tok)
  - class `IUserRepository` L104-117 (~102 tok)
  - class `IProductRepository` L118-131 (~103 tok)
  - class `IOrderRepository` L132-144 (~110 tok)

## core/runtime/

- `__init__.py` (~368 tok)
- `code_execution_tool.py` (~784 tok)
- `input_validator.py` — ToolInputValidationError: validate (~3347 tok)
  - class `ToolInputValidationError` L33-42 (~101 tok)
  - class `ToolInputValidator` L43-336 (~3057 tok)
- `tool_registry.py` — Pydantic: ToolParameter (68 fields) (~20657 tok)
  - class `ToolCategory` L46-60 (~94 tok)
  - class `ToolSeverity` L61-74 (~138 tok)
  - class `ParameterType` L75-85 (~59 tok)
  - class `ExecutionStatus` L86-102 (~119 tok)
  - class `ToolCallContext` L103-186 (~793 tok)
  - class `ToolParameter` L187-234 (~438 tok)
  - class `ToolSpec` L235-382 (~1386 tok)
  - class `ToolExecutionResult` L383-420 (~224 tok)
  - class `ToolRegistry` L421-944 (~5440 tok)
  - fn `get_tool_registry` L945-959 (~149 tok)
  - class `ToolDefinition` L960-2159 (~11468 tok)

## core/services/

- `__init__.py` — Core service interfaces. (~49 tok)
- `interfaces.py` — View: get, delete (~800 tok)
  - class `IRAGManager` L17-51 (~248 tok)
  - class `IMLPipeline` L52-80 (~176 tok)
  - class `ICacheProvider` L81-131 (~298 tok)

## core/telemetry/

- `__init__.py` (~26 tok)
- `tracer.py` — _NoOpSpan: my_function, init_telemetry, get_tracer, set_attribute + 4 more (~1246 tok)
  - fn `init_telemetry` L34-104 (~757 tok)
  - fn `get_tracer` L105-118 (~84 tok)
  - class `_NoOpSpan` L119-137 (~106 tok)
  - class `_NoOpTracer` L138-149 (~90 tok)

## database/

- `__init__.py` — API: GET (1 endpoints) (~301 tok)
- `CLAUDE.md` — database/ — Async SQLAlchemy 2.0 Layer (~237 tok)
- `db.py` — SQLAlchemy: DatabaseConfig (users) (~7728 tok)
  - class `DatabaseConfig` L55-65 (~132 tok)
  - fn `_normalize_async_url` L66-108 (~488 tok)
  - class `Base` L109-114 (~22 tok)
  - class `TimestampMixin` L115-132 (~158 tok)
  - class `User` L133-155 (~316 tok)
  - class `Product` L156-184 (~388 tok)
  - class `Order` L185-212 (~366 tok)
  - class `OrderItem` L213-230 (~219 tok)
  - class `AuditLog` L231-249 (~239 tok)
  - class `AgentTask` L250-269 (~296 tok)
  - class `EventRecord` L270-302 (~380 tok)
  - class `DatabaseManager` L303-466 (~1668 tok)
  - class `BaseRepository` L467-533 (~582 tok)
  - class `UserRepository` L534-557 (~252 tok)
  - class `ProductRepository` L558-608 (~521 tok)
  - class `OrderRepository` L609-670 (~614 tok)
  - class `AuditLogRepository` L671-730 (~538 tok)
  - fn `get_db` L731-763 (~202 tok)
- `indexes.sql` — Performance Indexes for DevSkyy (~643 tok)
- `models_brand_assets.py` — SQLAlchemy models backing the brand-assets store (US-013). (~801 tok)
  - class `BrandAssetRecord` L21-44 (~347 tok)
  - class `IngestionJobRecord` L45-62 (~260 tok)
- `models_competitors.py` — SQLAlchemy models backing the competitor-analysis store (US-034). (~746 tok)
  - class `CompetitorRecord` L19-35 (~224 tok)
  - class `CompetitorAssetRecord` L36-58 (~365 tok)
- `query_optimizer.py` — QueryOptimizer: optimize_product_query, explain_query, detect_n_plus_one_risk, get_index_recommendations (~1690 tok)
  - class `QueryOptimizer` L34-180 (~1475 tok)
- `seed_admin.py` — Seed an admin user into the DevSkyy database. (~1168 tok)
  - class `OwnerConfig` L27-34 (~45 tok)
  - fn `load_owner_config` L35-72 (~385 tok)
  - fn `prompt_owner_password` L73-84 (~141 tok)
  - fn `seed_admin` L85-123 (~396 tok)
- `seed_catalog.py` — Seed the DevSkyy database with SkyyRose product catalog. (~1185 tok)
  - fn `_to_float` L18-28 (~81 tok)
  - fn `_to_int` L29-39 (~79 tok)
  - fn `_infer_category` L40-64 (~173 tok)
  - fn `_load_products` L65-95 (~324 tok)
  - fn `seed` L96-142 (~426 tok)

## database/models/

- `__init__.py` (~59 tok)
- `tenant_user.py` — SQLAlchemy: TenantUser (tenant_users) (~452 tok)
- `tenant.py` — SQLAlchemy: Tenant (tenants) (~671 tok)
  - class `Tenant` L21-73 (~555 tok)

## datasets/

- `product_inventory.json` (~38 tok)

## datasets/skyyrose_lora_v1/

- `dataset_manifest.json` (~38 tok)
- `metadata.jsonl` (~35 tok)
- `training_config.json` (~37 tok)

## datasets/training/

- `skyyrose_lora_training.ipynb` — Declares SkyyRoseDataset (~4138 tok)

## deploy/clothing_3d/

- `docker-compose.yml` — Docker Compose services (~669 tok)
- `Dockerfile` — Docker container definition (~528 tok)
- `k8s.yaml` — Clothing 3D pipeline — Kubernetes manifests. (~1324 tok)

## design-system/skyyrose-storefront/

- `.gitignore` — Git ignore rules (~6 tok)
- `package-lock.json` — npm lock file (~41358 tok)
- `package.json` — @skyyrose/storefront-ds v0.1.0; npm scripts build/test/sync/sync:check; peer react>=18 (~314 tok)
- `tsconfig.json` — ES2020, bundler moduleResolution, react-jsx, strict, noEmit, vitest/globals + jest-dom types (~123 tok)
- `vite.config.ts` — library mode: es format, skyyrose-ds.es.js, cssFileName skyyrose-ds, dts({ include: ['src'], insertTypesEntry: true }), externals react/react-dom (~154 tok)
- `vitest.config.ts` — globals:true, jsdom, setupFiles vitest.setup.ts, css:false (~74 tok)
- `vitest.setup.ts` — imports @testing-library/jest-dom/vitest (~12 tok)

## design-system/skyyrose-storefront/scripts/

- `sync-theme-assets.mjs` — scripts/sync-theme-assets.mjs (~1970 tok)
  - fn `ensure` L47-69 (~274 tok)
  - fn `buildFontsCss` L70-159 (~1182 tok)

## design-system/skyyrose-storefront/src/

- `index.ts` — re-exports Collection from ./types; placeholder for component exports (~220 tok)
- `types.ts` — exports Collection type ('signature'|'black-rose'|'love-hurts'|'kids-capsule') (~24 tok)

## design-system/skyyrose-storefront/src/components/Button/

- `button.css` — Styles: 6 rules (~244 tok)
- `Button.tsx` — Button.tsx (~394 tok)
- `index.ts` (~23 tok)

## design-system/skyyrose-storefront/src/components/CollectionHero/

- `collection-hero.css` — Styles: 5 rules (~254 tok)
- `CollectionHero.tsx` — CollectionHero.tsx — lockup-image hero (no Three.js, no type-rendered title). (~307 tok)
- `index.ts` (~32 tok)

## design-system/skyyrose-storefront/src/components/HoloCard/

- `holo-card.css` — Holo Product Card — Impeccable Luxury Refinement (~1411 tok)
- `HoloCard.tsx` — HoloCard.tsx — faithful React port of template-parts/product-card-holo.php (~1299 tok)
  - section `HoloCardProps` L8-25 (~120 tok)
  - fn `HoloCard` L26-130 (~1080 tok)
- `index.ts` (~25 tok)

## design-system/skyyrose-storefront/src/fonts/

- `fonts.css` — Styles: 10 rules (~424 tok)

## design-system/skyyrose-storefront/src/styles/

- `commercial-polish.css` — SkyyRose Commercial Polish — premium presentation layer. (~3436 tok)

## design-system/skyyrose-storefront/src/tokens/

- `tokens.css` — SkyyRose Design Tokens (~3724 tok)

## design-system/skyyrose-storefront/test/

- `Button.test.tsx` — btn (~625 tok)
- `CollectionHero.test.tsx` — base (~408 tok)
- `HoloCard.test.tsx` — base (~653 tok)
- `parity.test.ts` — test/parity.test.ts (~388 tok)
- `smoke.test.ts` — verifies module loads (1 test) (~66 tok)
- `sync.test.ts` — Declares PKG (~510 tok)

## dev/

- `.gitignore` — Git ignore rules (~166 tok)
- `package.json` — Node.js package manifest (~222 tok)
- `README.md` — Project documentation (~1205 tok)
- `tsconfig.json` — TypeScript configuration (~201 tok)

## dev/python/

- `main.py` — from: query, review_code, design_architecture, debug_issue + 6 more (~2377 tok)
  - class `AgentConfig` L39-48 (~62 tok)
  - class `AgentResult` L49-58 (~51 tok)
  - class `CodingArchitectAgent` L59-226 (~1597 tok)
  - fn `print_banner` L227-236 (~100 tok)
  - fn `print_usage` L237-252 (~104 tok)
  - fn `main` L253-289 (~219 tok)

## dev/python/prompts/

- `__init__.py` — Prompts module for the Coding Architect Agent. (~120 tok)
- `system_prompt.py` — Declares from (~3819 tok)
  - class `PromptTechnique` L12-203 (~2025 tok)
  - class `TaskPrompt` L204-394 (~1462 tok)
  - class `DatabaseConfig` L395-402 (~35 tok)
  - fn `get_db_connection` L403-421 (~108 tok)
  - fn `get_system_prompt` L422-426 (~28 tok)
  - fn `get_task_prompt` L427-431 (~42 tok)
  - fn `get_few_shot_examples` L432-435 (~45 tok)

## dev/python/tools/

- `__init__.py` — Tools module for the Coding Architect Agent. (~52 tok)
- `python_tools.py` — from: type_check, lint, format_code, dependency_audit + 3 more (~4042 tok)
  - class `ToolResult` L13-19 (~30 tok)
  - class `PythonTools` L20-445 (~3943 tok)
- `typescript_tools.py` — from: type_check, analyze_config, dependency_audit, analyze_complexity + 2 more (~2909 tok)
  - class `ToolResult` L13-19 (~30 tok)
  - class `TypeScriptTools` L20-312 (~2807 tok)

## dev/src/

- `index.ts` — DevSkyy Coding Architect Agent (~2523 tok)
  - fn `createCodingArchitectAgent` L45-270 (~1681 tok)
  - fn `main` L271-330 (~481 tok)

## dev/src/prompts/

- `system-prompt.ts` — DevSkyy Coding Architect Agent - System Prompt (~3619 tok)
  - fn `safeParseJSON` L342-381 (~290 tok)
  - class `DatabaseConfig` L382-417 (~219 tok)

## dev/src/tools/

- `python-tools.ts` — Python Analysis Tools for Coding Architect Agent (TypeScript SDK) (~5099 tok)
- `typescript-tools.ts` — TypeScript Analysis Tools for Coding Architect Agent (~3800 tok)

## dev/src/types/

- `index.ts` — Type definitions for the Coding Architect Agent (~1193 tok)
  - section `AgentConfig` L10-23 (~92 tok)
  - section `AgentResult` L24-78 (~297 tok)
  - section `CodeAnalysisResult` L79-94 (~108 tok)
  - section `CodeIssue` L95-112 (~104 tok)
  - section `CodeMetrics` L113-130 (~120 tok)
  - section `ArchitectureRecommendation` L131-148 (~116 tok)
  - section `ToolResult` L149-176 (~142 tok)
  - section `FewShotExample` L177-188 (~61 tok)
  - section `PromptTemplate` L189-203 (~106 tok)

## devskyy-sdk-app/

- `.gitignore` — Git ignore rules (~35 tok)
- `catalog.py` — Sample SkyyRose product catalog for the Agent SDK starter. (~1780 tok)
  - class `CollectionMeta` L19-57 (~513 tok)
  - fn `collection_meta` L58-67 (~103 tok)
  - class `Product` L68-151 (~731 tok)
  - fn `find_products` L152-168 (~157 tok)
  - fn `products_in_collection` L169-173 (~78 tok)
- `main.py` — SkyyRose commerce agent — entry point. (~2513 tok)
  - fn `build_options` L98-131 (~509 tok)
  - fn `ask` L132-156 (~396 tok)
  - fn `main` L157-189 (~295 tok)
- `pyproject.toml` — Python project configuration (~222 tok)
- `README.md` — Project documentation (~1069 tok)
- `test_tools.py` — Offline checks for the catalog tools and agent wiring. (~1094 tok)
  - fn `_text` L25-29 (~55 tok)
  - fn `_checks` L30-81 (~771 tok)
- `tools.py` — In-process MCP tools for the SkyyRose commerce agent. (~1528 tok)
  - fn `_format_product` L32-48 (~189 tok)
  - fn `lookup_product` L49-79 (~352 tok)
  - fn `list_collection` L80-114 (~400 tok)
  - fn `collection_canon` L115-142 (~313 tok)

## devskyy_workflows/

- `__init__.py` (~187 tok)
- `__main__.py` (~62 tok)
- `ci_workflow.py` — CIWorkflowState: execute (~3576 tok)
  - class `CIWorkflowState` L17-26 (~72 tok)
  - class `CIWorkflow` L27-358 (~3423 tok)
- `cli.py` — setup_runner, run_workflow, run_all_workflows, list_workflows + 2 more (~1635 tok)
  - fn `setup_runner` L37-51 (~124 tok)
  - fn `run_workflow` L52-83 (~254 tok)
  - fn `run_all_workflows` L84-107 (~187 tok)
  - fn `list_workflows` L108-129 (~212 tok)
  - fn `show_status` L130-154 (~183 tok)
  - fn `main` L155-204 (~393 tok)
- `config.py` — get_workflow_config (~840 tok)
  - fn `get_workflow_config` L114-123 (~109 tok)
- `deployment_workflow.py` — DeploymentWorkflowState: execute (~6644 tok)
  - class `DeploymentWorkflowState` L18-27 (~88 tok)
  - class `DeploymentWorkflow` L28-581 (~6470 tok)
- `docker_workflow.py` — DockerWorkflowState: execute (~2226 tok)
  - class `DockerWorkflowState` L17-24 (~57 tok)
  - class `DockerWorkflow` L25-233 (~2093 tok)
- `mcp_workflow.py` — MCPWorkflowState: execute (~2311 tok)
  - class `MCPWorkflowState` L17-24 (~49 tok)
  - class `MCPWorkflow` L25-249 (~2186 tok)
- `ml_workflow.py` — MLWorkflowState: execute (~2635 tok)
  - class `MLWorkflowState` L17-24 (~49 tok)
  - class `MLWorkflow` L25-291 (~2514 tok)
- `quality_workflow.py` — QualityWorkflowState: execute (~2782 tok)
  - class `QualityWorkflowState` L17-24 (~54 tok)
  - class `QualityWorkflow` L25-280 (~2650 tok)
- `QUICKSTART.md` — Quick Start Guide: Code-Based Workflows (~1600 tok)
- `README.md` — Project documentation (~2005 tok)
- `workflow_runner.py` — WorkflowConfig: register, run, run_multiple, get_results (~1255 tok)
  - class `WorkflowConfig` L20-30 (~66 tok)
  - class `WorkflowResult` L31-43 (~84 tok)
  - class `WorkflowRunner` L44-152 (~1008 tok)

## docs/

- `3D_GENERATION_FILES.md` — 3D Generation - Files Created & Updated (~1527 tok)
- `3D_GENERATION_PIPELINE.md` — SkyyRose 3D Generation Pipeline (~3449 tok)
- `3D_PIPELINE_HARDENING.md` — 3D Pipeline Security & Resilience Hardening (~3363 tok)
- `AGENT_CHAT_IMPLEMENTATION.md` — Agent Chat Interface Implementation (~2367 tok)
- `AGENT_REFACTORING.md` — Agent Refactoring Summary (~1997 tok)
- `AGENTS.md` — DevSkyy Agent Orchestration (~2369 tok)
- `AI_TOOLS_CHECKLIST.md` — AI Tools Implementation Checklist ✅ (~1738 tok)
- `AI_TOOLS_IMPLEMENTATION.md` — AI Tools & HuggingFace Spaces Implementation (~2355 tok)
- `AR_SHOPPING_MISSION.md` — AR Shopping Experience Mission (~1036 tok)
- `AR_STACK_CONFIGURATION.md` — AR Stack Configuration Mission (~1401 tok)
- `ARCHITECTURE.md` — Architecture Reference (~4430 tok)
- `ASSET_EXTRACTION_REPORT.md` — SkyyRose Asset Extraction & Organization Report (~3869 tok)
- `CATALOG_SYNC.md` — Catalog Consistency & Auto-Sync (~1473 tok)
- `CLAUDE.md` — DevSkyy docs/ — Canonical Index for AI Agents (~1152 tok)
- `CLOTHING_3D_PIPELINE.md` — Clothing 3D Pipeline (~2696 tok)
- `CLOTHING_3D_PRODUCTION.md` — Clothing 3D — Production Deployment Guide (~2484 tok)
- `COLAB_TRAINING_GUIDE.md` — ✅ Google Colab LoRA Training Guide (FREE) (~1014 tok)
- `collection-hub-wiring-spec.md` — Collection Hub Wiring Spec (~4070 tok)
- `CONSOLIDATED_VALIDATION_ISSUES.md` — DevSkyy Consolidated Validation Issues Report (~3918 tok)
- `CONTEXT.md` — DevSkyy (~1629 tok)
- `CONTRIBUTING.md` — DevSkyy Contributor Guide, renamed from CONTRIB.md 2026-07-06 (~5714 tok)
- `CRITICAL_FUCHSIA_APE_QUICKSTART.md` — Critical Fuchsia Ape - Quick Start Guide (~1234 tok)
- `CRITICAL_FUCHSIA_APE_SETUP.md` — DevSkyy MCP - Critical Fuchsia Ape Backend Setup (~1857 tok)
- `CRITICAL_FUCHSIA_APE_SUMMARY.md` — DevSkyy MCP - Critical Fuchsia Ape Setup Summary (~1957 tok)
- `CRITICAL_ISSUES_SUMMARY.md` — DevSkyy - CRITICAL ISSUES SUMMARY (~1193 tok)
- `DASHBOARD_BACKEND_IMPLEMENTATION.md` — Dashboard Backend Implementation (~5189 tok)
- `DATABASE_INTEGRATION_VALIDATION_REPORT.md` — Database Integration Validation Report (~6891 tok)
- `DEBUG_3D_GENERATION_ISSUES.md` — 3D Model Generation - Debugging Results (~1225 tok)
- `DEPENDENCIES.md` — Dependencies Reference (~2331 tok)
- `dependency-env-audit.md` — Dependency + Environment Audit (~285 tok)
- `DEPLOY_HF_SPACES_QUICKSTART.md` — HuggingFace Spaces Deployment - Quick Start (~797 tok)
- `DEPLOY_NOW.md` — 🚀 Deploy DevSkyy to Vercel - Quick Reference Card (~725 tok)
- `DEPLOYMENT_ARCHITECTURE.md` — DevSkyy Production Deployment Architecture (~4452 tok)
- `DEPLOYMENT.md` — Collection Pages Deployment Guide (~2963 tok)
- `DESIGN.md` — Design System Inspired by Claude (Anthropic) (~5031 tok)
- `DEVSKYY_MCP_COMPLETE_SETUP.md` — DevSkyy MCP - Complete Setup Guide (~2579 tok)
- `DEVSKYY_MCP_SECURITY_FIXES.md` — DevSkyy MCP Server - Security Fixes Completed (~3030 tok)
- `DOCKER.md` — Docker — DevSkyy Production Stack (~1205 tok)
- `ELEMENTOR_CUSTOMIZATION_GUIDE.md` — SkyyRose Elementor Page Customization Guide (~3852 tok)
- `engineering-learnings.md` — Engineering Learnings (~9253 tok)
- `ENTERPRISE_INTELLIGENCE_DEPLOYMENT.md` — Enterprise Intelligence Deployment Guide (~2782 tok)
- `ENTERPRISE_INTELLIGENCE_IMPLEMENTATION.md` — Enterprise Intelligence Implementation Complete (~4384 tok)
- `ENV_VARS_MANIFEST.md` — DevSkyy Environment Variables Manifest (~2841 tok)
- `ENV_VARS_REFERENCE.md` — Environment Variables Reference (~5420 tok)
- `FASTMCP_DEPLOYMENT.md` — FastMCP Deployment Guide (~2016 tok)
- `FINE_TUNING_GUIDE.md` — SkyyRose Fine-Tuning Guide (~1246 tok)
- `GoogleImagery.md` — Image generation (text-to-image) (~40393 tok)
- `HF_SPACES_DEPLOYMENT.md` — HuggingFace Spaces Deployment Guide (~1377 tok)
- `HF_SPACES_SETUP.md` — HuggingFace Spaces Configuration Summary (~2020 tok)
- `homepage-rebuild-spec.md` — HOMEPAGE REBUILD — Direction Spec (skyyrose.co front page) (~5331 tok)
- `HUGGINGFACE_3D_INTEGRATION.md` — HuggingFace 3D Integration Implementation (~3225 tok)
- `HUGGINGFACE_AUTH_GUIDE.md` — HuggingFace Authentication Guide (~681 tok)
- `HUGGINGFACE_SPACES.md` — HuggingFace Spaces Integration Guide (~3295 tok)
- `IMPLEMENTATION_PLAN.md` — DevSkyy Production Hardening - Implementation Plan (~2706 tok)
- `INSTALLATION_REQUIREMENTS.md` — SkyyRose Installation & Dependency Requirements (~1739 tok)
- `javascript-typescript-sdk.md` — DevSkyy JavaScript/TypeScript SDK (~2258 tok)
- `LLAMAINDEX_MULTIMODAL.md` — LlamaIndex Multimodal Integration (~2662 tok)
- `LLM_CLIENTS_QUICK_START.md` — LLM Clients Quick Start Guide (~1800 tok)
- `LLM_LAYER_VALIDATION_REPORT.md` — LLM Layer Production Validation Report (~9521 tok)
- `LORA_DEPLOYMENT_STATUS.md` — SkyyRose LoRA Training - Deployment Status (~1280 tok)
- `MANAGED_AGENTS.md` — Managed Agents — Claude Agent SDK Integration (~3958 tok)
- `MCP_ARCHITECTURE.md` — DevSkyy MCP Architecture (~3245 tok)
- `MCP_CONFIGURATION_GUIDE.md` — DevSkyy MCP Server Configuration Guide (~4291 tok)
- `MCP_CONFIGURATION.md` — DevSkyy MCP Server Configuration Guide (~2409 tok)
- `MCP_QUICK_REFERENCE.md` — DevSkyy MCP Quick Reference (~1181 tok)
- `MCP_TOOLS.md` — MCP Tools Reference (~1464 tok)
- `mcp-config-reference.json` — Declares calls (~2812 tok)
- `mcp-http-architecture.md` — MCP over HTTP — Architecture (~3302 tok)
- `memory-architecture.html` — DevSkyy Memory Architecture (~2294 tok)
- `MFA_TESTING.md` — MFA Module Testing Documentation (~3571 tok)
- `model-routing.md` — Model Routing Policy (~657 tok)
- `NANO_BANANA.md` — Nano Banana 2 — SkyyRose AI Image Pipeline (~1750 tok)
- `ORCHESTRATION_CONFIGURATION_AUDIT.md` — DevSkyy Orchestration Layer - Configuration Audit & Refactor Report (~3215 tok)
- `PIPELINE-ARCHITECTURE.md` — Pipeline Architecture (~1246 tok)
- `PLAN_INDEX.md` — Skyyrose V2 — Plan Index (Cross-Reference) (~1943 tok)
- `POST_MORTEM_TEMPLATE.md` — Post-Mortem Template (~3955 tok)
- `PRODUCTION_ENVIRONMENT_SETUP.md` — Production Environment Setup Guide (~3926 tok)
- `PRODUCTION_LAUNCH_CHECKLIST.md` — Production Launch Checklist - DevSkyy (~1795 tok)
- `PRODUCTION_LAUNCH_PLAN.md` — DevSkyy Production Launch Plan (~2422 tok)
- `PTC_COMPLETE_SUMMARY.md` — Anthropic Programmatic Tool Calling (PTC) - Complete Implementation Summary (~6074 tok)
- `PTC_IMPLEMENTATION_PLAN.md` — Programmatic Tool Calling (PTC) Implementation Plan (~4895 tok)
- `RAG_INTEGRATION.md` — RAG Pipeline Integration (~2044 tok)
- `README.md` — Project documentation (~1185 tok)
- `REMEDIATION_MAP.md` — SkyyRose Structural Remediation — Phase 0 Map (~3092 tok)
- `RENDER_DEPLOYMENT_CHECKLIST.md` — Render Backend Deployment Checklist (~3579 tok)
- `ROUND_TABLE_STATE_OF_ART.md` — LLM Round Table - State-of-the-Art Configuration (~4569 tok)
- `RUNBOOK.md` — DevSkyy Production Runbook (~3783 tok)
- `SECRETS_MIGRATION.md` — Secrets Management Migration Guide (~4622 tok)
- `SECURITY_HARDENING.md` — DevSkyy Security Hardening Guide (~476 tok)
- `SECURITY.md` — Security Policy (~155 tok)
- `SETUP_INSTRUCTIONS.md` — DevSkyy - Production Environment Setup Instructions (~1172 tok)
- `skill-audit.html` — DevSkyy Skill Audit — 2026-06-13 (~2227 tok)
- `skill-authoring-standard.md` — Skill Authoring Standard (~1560 tok)
- `skill-cleanup-changelog-2026-06-13.md` — Skill Cleanup Changelog — Phase 1 (2026-06-13) (~2695 tok)
- `skill-quality-audit-2026-06-13.md` — SkyyRose Suite — Skill Content-Quality Audit (~1905 tok)
- `SKIPPED_TESTS_ANALYSIS.md` — Skipped Tests Analysis (~1434 tok)
- `SKYYROSE_V2_MASTER_PLAN.md` — SKYYROSE V2 — MASTER EXECUTION PLAN (~10314 tok)
- `SKYYROSE_WORDPRESS_PLAN.md` — SKYYROSE WORDPRESS PLAN — skyyrose.co (~14418 tok)
- `skyyrose-plugin-suite.html` — SkyyRose Plugin Suite — 4-Plugin Architecture (~2160 tok)
- `SQLALCHEMY_ORM_IMPLEMENTATION.md` — SQLAlchemy ORM Models and Alembic Integration (~3509 tok)
- `TEST_SUITE_ANALYSIS.md` — DevSkyy Test Suite Analysis (~3225 tok)
- `theme-team-charter.md` — SkyyRose Theme Team Charter (~7366 tok)
- `TODOS.md` — TODOS (~2424 tok)
- `TOOL_REGISTRY_IMPLEMENTATION.md` — Tool Registry Implementation Summary (~3736 tok)
- `TRACK_B_PHASE_4_COMPLETION.md` — Track B Phase 4: Domain Verification - Completion Report (~2199 tok)
- `UNIFIED_LLM_CLIENT.md` — Unified LLM Client - Usage Guide (~2783 tok)
- `VALIDATION_REPORT_INDEX.md` — DevSkyy Validation Report Index (~2473 tok)
- `VERCEL_DOMAIN_SETUP.md` — Vercel Domain Setup Guide for app.devskyy.app (~2043 tok)
- `VERCEL_ROUTING_FIX.md` — Vercel Routing Issue - Required Manual Fix (~1727 tok)
- `VERIFICATION_REPORTS_INDEX.md` — DevSkyy Domain Verification Reports - Index (~1865 tok)
- `WEBSOCKET_API.md` — WebSocket API Documentation (~2742 tok)
- `WORDPRESS_API_FIX.md` — WordPress REST API Authentication Fix (~3719 tok)
- `WORDPRESS_CONFIGURATION_STATUS.md` — SkyyRose WordPress Configuration Status (~2969 tok)
- `WORDPRESS_EMBED.md` — WordPress Embed Snippets (~1701 tok)
- `WORDPRESS_INTEGRATION.md` — WordPress.com Integration Guide (~226 tok)
- `WORDPRESS_SHOPTIMIZER_BUILD_GUIDE.md` — Complete WordPress/Shoptimizer/Elementor Bundle Build Guide (~3385 tok)
- `WORDPRESS_UPLOAD_SUCCESS.md` — WordPress Media Upload - SUCCESS ✅ (~2694 tok)
- `WORKER_ARCHITECTURE.md` — DevSkyy Worker Architecture (~3193 tok)
- `WORKER_QUICK_START.md` — Worker Quick Start Guide (~1878 tok)
- `ZERO_TRUST_ARCHITECTURE.md` — Zero Trust Architecture (~5617 tok)

## docs/CODEMAPS/

- `architecture.md` — Architecture Codemap (~811 tok)
- `backend.md` — Backend Codemap (~1338 tok)
- `data.md` — Data Codemap (~722 tok)
- `dependencies.md` — Dependencies Codemap (~838 tok)
- `frontend.md` — Frontend Codemap (~857 tok)
- `INDEX.md` — DevSkyy Codemaps Index (~644 tok)
- `wordpress.md` — WordPress Theme Codemap (~941 tok)

## docs/adr/

- `0001-compositor-is-agent-inside-langgraph-node.md` — Compositor is an agent inside a LangGraph node, not a procedural script (~532 tok)
- `0002-brand-centroid-global-pending-data.md` — Brand centroid is global pending false-pass measurement data (~540 tok)

## docs/agents/

- `AGENTS.md` — DevSkyy Platform - Core Agent Documentation (~3598 tok)
- `README.md` — Project documentation (~1239 tok)

## docs/api/

- `ECOMMERCE_API.md` — E-Commerce API Documentation (~3505 tok)
- `NEW_MCP_ENDPOINTS.md` — New MCP-Integrated API Endpoints (~4109 tok)

## docs/architecture/

- `AUTHENTICATED_IMPLEMENTATIONS.md` — Authenticated Industry Implementations Reference (~3240 tok)
- `COMPONENTS.md` — DevSkyy Components Documentation (~7557 tok)
- `DATA_FLOW.md` — DevSkyy Data Flow Documentation (~3539 tok)
- `DEVSKYY_MASTER_PLAN.md` — ðŸš€ DevSkyy Autonomous Commerce Master Plan (~9829 tok)
- `flux-synthesis.md` — FLUX Synthesis Pipeline — Architecture Document (~6737 tok)
- `lifecycle-redesign-2026-06-21.html` — DevSkyy — Lifecycle Architecture Redesign (~8279 tok)
- `mockup-first-100pct-replica-system-plan.md` — 100% Replica System Plan — Mockup First, Scenes Second (~5225 tok)
- `README.md` — Project documentation (~1993 tok)
- `render-fidelity-industry-standard-2026-06-15.html` — AI Product-Render Fidelity — Industry Standard & SkyyRose Reconciliation (2026-06-15) (~4363 tok)
- `SYSTEM_ARCHITECTURE.md` — DevSkyy System Architecture (~3118 tok)

## docs/audits/

- `catalog-imagery-audit-2026-06-19.html` — Catalog Imagery Audit — 2026-06-19 (~2118 tok)
- `pretest-failures-2026-05-26.md` — Pre-Existing Test Failures — 2026-05-26 Audit (~1487 tok)

## docs/brand/

- `asset-hierarchy.md` — SkyyRose Brand Asset Hierarchy (~2105 tok)
- `blog-black-rose.md` — Blog copy: "Black Rose Is Not a Theme. It's Armor." (~745 tok)
- `blog-kids-capsule.md` — Blog copy: "Luxury Runs in the Family." (~722 tok)
- `blog-love-hurts.md` — Blog copy: "They Called Him Beast. They Were Right." (~717 tok)
- `blog-luxury-grows-from-concrete.md` — Blog copy: "Luxury Grows from Concrete" (~842 tok)
- `blog-signature.md` — Blog copy: "Not Basics. Blueprints." (~722 tok)
- `canon-audit-2026-05-23.md` — SkyyRose Canon Audit — 2026-05-23 (~5363 tok)
- `collection-design-proposals.md` — SkyyRose Collection Design Proposals (~8132 tok)
- `collection-stories.md` — SkyyRose Collection Stories (~4415 tok)
- `collection-ux-architecture.md` — SkyyRose Collection UX Architecture — Proposal (~3464 tok)
- `corey-questions.md` — Two Questions for Corey (~996 tok)
- `immersive-hero-prompts.md` — Immersive Hub — Dedicated Hero Master Prompts (Midjourney) · v2 (~1872 tok)
- `sot-imagery-policy.md` — SOT-Only Product Imagery — Policy & Enforcement (~1162 tok)
- `visual-audit-2026-05-23.md` — SkyyRose.co Visual Audit — 2026-05-23 (~3860 tok)
- `visual-references.md` — SkyyRose Visual Reference Set — Canonical (~1130 tok)

## docs/brand/design-mockups/

- `collection-designs.html` — SkyyRose — Collection Design Mockups (2026-05-24) (~11152 tok)
- `README.md` — Project documentation (~346 tok)
- `v2-asset-audit.md` — v2.html Image Asset Audit — Transparency / Background Removal (~2619 tok)
- `v2-canon-audit.md` — v2.html Brand Canon Audit (~2925 tok)
- `v2-fix-manifest.md` — v2.html Fix Manifest — Synthesized from 4 audit reports (~3900 tok)
- `v2-polish-mix.md` — v2 Polish Mix-In Specification (~7739 tok)
- `v2-visual-fixes.md` — v2.html Visual Fix Spec (~5062 tok)

## docs/campaigns/

- `2026-kids-capsule-report.html` — SkyyRose | Inheritance of Elegance Campaign Report (~1140 tok)
- `sot-lookbook.html` — SkyyRose Lookbook (wordpress-theme/skyyrose-flagship / lookbook · 4 collections) (~4514 tok)

## docs/database/

- `MIGRATION_GUIDE.md` — SQLAlchemy ORM Migration Guide (~4760 tok)
- `ORM_MODELS.md` — SQLAlchemy ORM Models Documentation (~4536 tok)
- `QUICK_START.md` — Database ORM Quick Start Guide (~3182 tok)
- `README.md` — Project documentation (~3249 tok)

## docs/deployment/

- `DEPLOYMENT_GUIDE.md` — DevSkyy Platform - Deployment Implementation Guide (~18051 tok)
- `DEPLOYMENT_SUMMARY.md` — DevSkyy Frontend Deployment - Summary Report (~3635 tok)
- `Production_Grade_WordPress_Elementor_Automation_Guide.md` — Production-Grade WordPress/Elementor Automation Reference (~2846 tok)
- `PUSH_INSTRUCTIONS.md` — Push Instructions for DevSkyy Platform (~342 tok)
- `README.md` — Project documentation (~1745 tok)
- `RENDER_ARCHITECTURE.md` — DevSkyy on Render - Architecture Diagram (~4609 tok)
- `RENDER_DEPLOYMENT_GUIDE.md` — DevSkyy Backend - Render Deployment Guide (~6689 tok)
- `RENDER_QUICKSTART.md` — DevSkyy Render Deployment - Quick Start (~1535 tok)
- `VERCEL_DEPLOYMENT_GUIDE.md` — DevSkyy Frontend Vercel Deployment Guide (~4188 tok)
- `VERCEL_QUICK_START.md` — DevSkyy Vercel Quick Start Guide (~1323 tok)
- `WORDPRESS_SETUP.md` — WordPress API Configuration for DevSkyy (~1245 tok)

## docs/design-mockups/

- `black-rose-oakland-after-dark.html` — Black Rose · Tier 2 — Oakland After Dark (embedded scene) (~45510 tok)
- `black-rose-preorder-horizontal.html` — Black Rose · Pre-Order — Oakland After Dark (horizontal) (~4909 tok)
- `br-012-cutout.webp` (~16342 tok)
- `oakland-horizon.webp` (~21813 tok)

## docs/design/

- `fashion-design-system-team.md` — Fashion Design System Team (~1895 tok)
- `visual-pattern-shortlist.md` — SkyyRose Visual Pattern Shortlist (~2786 tok)

## docs/design/v2-remodel/

- `CODEX-DESKTOP-MANIFEST.json` — Declares as (~1626 tok)
- `collection-imagery-lookbook.html` — SkyyRose V2 · Collection Imagery Lookbook (~3703 tok)

## docs/design/v2-remodel/design-system/

- `contract.json` (~1434 tok)
- `evidence.json` (~672 tok)
- `preview.html` — SkyyRose V2 Commerce System Preview (~1520 tok)

## docs/design/v2-remodel/house-of-roses/

- `bart-film-storyboard.md` — Superseded: transit-specific Jersey Series film contract (~5923 tok)
- `component-contract.json` (~918 tok)
- `evidence.json` (~656 tok)
- `skyyrose-tour-film-storyboard.md` — Skyy Rose Tour Around the Bay — Jersey Series previsualization (~567 tok)

## docs/design/v2-remodel/kids-capsule-reveal/

- `contract.json` (~1301 tok)
- `evidence.json` — Declares renders (~1888 tok)
- `plan.md` — Kids Capsule Chapter 04 — Royal Procession (~1423 tok)

## docs/design/v2-remodel/reports/

- `catalog-media-binding-audit.md` — V2 catalog, media, and Scroll World binding audit (~4759 tok)
- `cinematic-motion-responsive-contract.md` — V2 cinematic motion and responsive contract (~6149 tok)
- `commerce-journey-gap-map.md` — V1 → V2 commerce journey gap map (~6168 tok)
- `design-system-census.md` — SkyyRose Flagship V2 remodel — design-system census (~4320 tok)
- `handoff-reconciliation-2026-08-15.md` — V2 handoff reconciliation — 2026-08-15 (~2125 tok)
- `scroll-world-archive-intake.md` — SkyyRose Scroll World archive intake (~717 tok)
- `typography-open-source-contract.md` — V2 typography and artwork provenance contract (~1483 tok)
- `v1-authority-benchmark.md` — V1 authority benchmark for the V2 remodel (~4102 tok)

## docs/design/v2-remodel/review-assets/lookbook-wave-01/

- `manifest.json` (~739 tok)

## docs/design/v2-remodel/review-assets/lookbook-wave-02/

- `manifest.json` (~688 tok)

## docs/elite-studio/

- `LAYER_2_PIPELINE_STAGES.md` — Elite Studio Layer 2 — Pipeline Stages (~1455 tok)
- `LAYER_6_VIRTUAL_TRYON.md` — Layer 6 — Virtual Try-On (~877 tok)
- `render-readiness-audit-2026-05-27.html` — Elite Studio — Render Readiness Audit (2026-05-27) (~7001 tok)

## docs/elite-web-builder-package/collection-pages/

- `black-rose.html` — BLACK ROSE — SkyyRose Collection 01 (~110062 tok)
- `love-hurts.html` — LOVE HURTS — SkyyRose Collection 02 (~92449 tok)
- `signature.html` — SIGNATURE — SkyyRose Collection 03 (~108626 tok)

## docs/elite-web-builder-package/homepage/

- `about.html` — Our Story — SkyyRose | Luxury Grows from Concrete (~34379 tok)
- `index.html` — The Skyy Rose Collection — Oakland Luxury Streetwear (~17938 tok)
- `skyyrose-homepage-v2.html` — SkyyRose — Luxury Grows from Concrete | Oakland Streetwear (~228350 tok)

## docs/elite-web-builder-package/product-pages/

- `product-black-rose.html` — Midnight Bomber — BLACK ROSE | SkyyRose (~44609 tok)
- `product-love-hurts.html` — Tears Jacket — LOVE HURTS | SkyyRose (~39364 tok)
- `product-signature.html` — Foundation Blazer — SIGNATURE | SkyyRose (~83177 tok)

## docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/

- `functions.php` — SkyyRose Flagship Theme Functions (~1048 tok)
- `style.css` (~170 tok)

## docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/assets/css/

- `main.css` — SkyyRose Flagship — Global Styles (~341 tok)
- `single-product.css` — SkyyRose Single Product Page Styles (~5830 tok)

## docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/assets/js/

- `single-product.js` — SkyyRose Single Product Page JS (~1928 tok)

## docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/inc/

- `wc-product-functions.php` — SkyyRose WooCommerce Product Functions (~3056 tok)

## docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/woocommerce/

- `single-product.php` — SkyyRose Single Product Page (~4653 tok)

## docs/guides/

- `ADVANCED_TOOL_USE_DEVSKYY.md` — Advanced Tool Use Integration Guide for DevSkyy (~6270 tok)
- `AUTOTRAIN_SETUP_GUIDE.md` — HuggingFace AutoTrain Setup Guide (~782 tok)
- `clean-coding-agents.md` — Clean Coding Compliance Agents (~6244 tok)
- `compliance-architecture.txt` — Declares checking (~3613 tok)
- `DEVELOPER_QUICKREF.md` — DevSkyy Developer Quick Reference (~1390 tok)
- `developer-quickref.md` — Developer Quick Reference - Clean Coding Compliance (~1776 tok)
- `DevSky_Enterprise_Platform_Development_Guide.md` — DevSkyy Enterprise Platform Development Guide (~5140 tok)
- `Enterprise_FastAPI_Platform_Implementation_Guide.md` — Enterprise FastAPI Platform Implementation Guide (~11232 tok)
- `env-setup-guide.md` — Environment Variables Setup Guide (~1575 tok)
- `implementation-summary.md` — DevSkyy Clean Coding Compliance - Implementation Summary (~3503 tok)
- `MAINTENANCE_BEST_PRACTICES.md` — DevSkyy Platform Maintenance Best Practices (~5335 tok)
- `QUICKSTART.md` — Quick Start Guide: OpenAI MCP Server (~1651 tok)
- `RAG_QUERY_REWRITING.md` — Advanced Query Rewriting for DevSkyy RAG (~2200 tok)
- `README.md` — Project documentation (~1219 tok)
- `repository-files.md` — DevSkyy Repository - Complete File Inventory (~3322 tok)
- `SERVER_README.md` — DevSkyy OpenAI MCP Server (~1401 tok)
- `server-readme.md` — OpenAI MCP Server for DevSkyy (~2216 tok)

## docs/handoff/

- `01-DEVELOPER_SETUP.md` — DevSkyy Dashboard — Developer Setup (~793 tok)
- `02-FRONTEND_ARCHITECTURE.md` — DevSkyy Dashboard — Frontend Architecture (~1949 tok)
- `03-API_CONTRACT.md` — DevSkyy Dashboard — API Contract (~2059 tok)
- `04-DESIGN_SYSTEM.md` — DevSkyy Dashboard — Design System (~1974 tok)

## docs/integrations/

- `openai-feed-compliance-report.md` — OpenAI ChatGPT Product Feed — Compliance Report (~5225 tok)
- `openai-product-feed-spec.md` — OpenAI ChatGPT Product Feed — Specification Reference (~2493 tok)

## docs/legal/

- `_live-backup-2026-06-05.md` — Live page content backup — pre-publish rollback (2026-06-05) (~1398 tok)
- `_SCAFFOLD.html` — {{TITLE}} — SkyyRose (~691 tok)
- `_SHARED-BRIEF.md` — SkyyRose Store Policies — Shared Source of Truth (~1344 tok)
- `accessibility-statement.html` — Accessibility Statement — SkyyRose (~2932 tok)
- `cookie-policy.html` — Cookie Policy — SkyyRose (~5059 tok)
- `index.html` — SkyyRose Store Policies — Draft Set (~1607 tok)
- `privacy-policy.html` — Privacy Policy — SkyyRose (~7925 tok)
- `refund-return-policy.html` — Refund &amp; Return Policy — SkyyRose (~4620 tok)
- `shipping-policy.html` — Shipping Policy — SkyyRose (~3884 tok)
- `terms-of-service.html` — Terms of Service — SkyyRose (~7919 tok)

## docs/plans/

- `2026-02-26-wordpress-bridge-agent-design.md` — WordPress Bridge Agent — Design Document (~2452 tok)
- `2026-02-26-wordpress-bridge-agent-plan.md` — WordPress Bridge Agent — Implementation Plan (~9195 tok)
- `2026-02-28-ai-cli-plan.md` — AI CLI Implementation Plan (~10314 tok)
- `2026-03-03-agent-hierarchy-redesign.md` — DevSkyy Agent Hierarchy Redesign — Phase 2 Design Document (~4392 tok)
- `2026-03-05-ai-providers-design.md` — Full-Stack AI Provider Wiring — Design Doc (~415 tok)
- `2026-03-06-immersive-scene-generation.md` — Immersive Scene Generation — RALPH Task (~2237 tok)
- `2026-03-07-interactive-product-cards-design.md` — Interactive Product Cards — Implementation Plan (~6238 tok)
- `2026-03-07-interactive-product-cards-plan.md` — Interactive Product Cards — Implementation Plan (~4313 tok)

## docs/reports/

- `COMPLETE_LLM_SETUP_GUIDE.md` — Complete LLM Provider Setup Guide (~1967 tok)
- `DAST_IMPLEMENTATION_SUMMARY.md` — DAST Implementation Summary - Phase 2 Task 4 (~2746 tok)
- `DOMAIN_VERIFICATION_REPORT.md` — Track B Phase 4: Domain Verification Report (~3896 tok)
- `DOMAIN_VERIFICATION_SUMMARY.txt` (~2379 tok)
- `EXECUTIVE_SUMMARY.md` — DevSkyy Platform Analysis - Executive Summary (~2527 tok)
- `FINAL_CHECKLIST.md` — Phase 2 Task 5 Part B - Final Checklist (~2118 tok)
- `FULL_CATALOG_UPLOAD_COMPLETE.md` — Full Product Catalog Upload - COMPLETE ✅ (~3712 tok)
- `GAP_ANALYSIS.md` — DevSkyy Gap Analysis: Discussed vs Implemented Features (~725 tok)
- `GRAFANA_ALERTING_IMPLEMENTATION.md` — Phase 2 Task 5 Part B: Grafana Dashboards & Slack Integration (~3119 tok)
- `IMAGE_OPTIMIZATION_WORKFLOW_SUMMARY.md` — SkyyRose Image Optimization - Full Test & WordPress Integration (~3496 tok)
- `LAUNCH_BLOCKERS.md` — 🚨 DevSkyy Launch Blockers (~2989 tok)
- `LLM_CLIENTS_INTEGRATION_REPORT.md` — DevSkyy LLM Clients Integration Report (~1819 tok)
- `MCP_SETUP_CHECKLIST.md` — DevSkyy MCP Setup Checklist (~1478 tok)
- `MCP_SETUP_SUMMARY.md` — DevSkyy MCP Configuration Summary (~1450 tok)
- `MISSING_FILES_ANALYSIS.md` — DevSkyy Missing Files & Import Analysis (~2954 tok)
- `OPENAI_SETUP_GUIDE.md` — OpenAI API Key Setup Guide (~1190 tok)
- `PHASE2_TASK5B_COMPLETE.md` — Phase 2 Task 5 Part B - COMPLETE ✅ (~3105 tok)
- `PRODUCTION_READINESS_REPORT.md` — DevSkyy Production Readiness Report (~3312 tok)
- `README.md` — Project documentation (~1438 tok)
- `SDK_UPGRADE_ANALYSIS.md` — SDK/ADK Upgrade Analysis for DevSkyy (~1786 tok)
- `SECURITY_ALERT_API_KEY_EXPOSED.md` — 🚨 SECURITY ALERT - API KEY EXPOSED (~1293 tok)
- `SECURITY_ASSESSMENT.md` — DevSkyy Security Assessment Report (~4316 tok)
- `SECURITY_HARDENING_SUMMARY.md` — Security Hardening Summary - Phase 1 Complete (~3036 tok)
- `SECURITY_IMPLEMENTATION_REPORT.md` — DevSkyy Enterprise Platform - Security Implementation Report (~3342 tok)
- `STAGING_TEST_SUITE_SUMMARY.md` — Staging Test Suite - Implementation Summary (~2503 tok)
- `UPGRADE_PLAN.md` — DevSkyy SDK/ADK Upgrade Plan (~1522 tok)
- `ZERO_TRUST_IMPLEMENTATION_REPORT.md` — Zero Trust Architecture Foundation - Implementation Report (~4982 tok)

## docs/runbooks/

- `api-key-leak.md` — API Key Leak Response (~5183 tok)
- `authentication-bypass.md` — Authentication Bypass Response (~1723 tok)
- `brute-force-attack.md` — Brute Force Attack Response (~3983 tok)
- `data-breach.md` — Data Breach Response (~5268 tok)
- `ddos-attack.md` — DDoS Attack Response (~5040 tok)
- `ransomware-attack.md` — Ransomware Attack Response (~4795 tok)
- `security-incident-response.md` — Security Incident Response - Master Procedure (~2519 tok)
- `sql-injection.md` — SQL Injection Attack Response (~5417 tok)
- `xss-attack.md` — XSS (Cross-Site Scripting) Attack Response (~3491 tok)
- `zero-day-vulnerability.md` — Zero-Day Vulnerability Response (~4246 tok)

## docs/security/

- `CLEAN_CODING_AGENTS.md` — DevSkyy Clean Coding Compliance System (~2103 tok)
- `KEY_ROTATION.md` — Key Rotation Guide (~2271 tok)
- `README.md` — Project documentation (~1564 tok)
- `vulnerability_report.md` — DevSkyy Security Vulnerability Report (~68 tok)

## docs/setup/

- `BACKEND_QUICKSTART.md` — Backend Quick Start Guide (~1507 tok)

## docs/superpowers/plans/

- `2026-04-20-ghost-mannequin-pipeline.md` — Ghost-Mannequin Imagery Pipeline (Phase B2) Implementation Plan (~16427 tok)
- `2026-04-29-bugfix-gltfloader-brand-colors-renders.md` — Post-Image-Taste Bugfix Sprint Implementation Plan (~3805 tok)
- `2026-05-25-v2-mockup-design.md` — SkyyRose v2 Mockup Implementation Plan (~12836 tok)
- `2026-05-28-replica-foundry.md` — Replica Foundry Implementation Plan (~21121 tok)
- `2026-05-29-catalog-dossier-steward.md` — Catalog & Dossier Steward Implementation Plan (~21358 tok)
- `2026-06-02-pipeline3d-phase1.md` — Unified 3D Pipeline Orchestrator — Phase 1 Implementation Plan (~17896 tok)
- `2026-06-13-skyyrose-plugin-suite.md` — SkyyRose Plugin Suite — Implementation Plan (~6575 tok)
- `2026-06-13-skyyrose-suite-phase2-playbook.md` — SkyyRose Suite — Phase 2/3 Execution Playbook (filesystem-verified) (~2144 tok)
- `2026-06-14-collection-identity-sot.md` — Collection Identity SOT — Implementation Plan (~14527 tok)
- `2026-06-16-evaluator-agent.md` — Evaluator / Critic Agent — Implementation Plan (~11431 tok)
- `2026-06-16-observability-agent.md` — Metrics Foundation + Observability Agent — Implementation Plan (~16143 tok)
- `2026-06-16-render-fidelity-evaluator.md` — Render Fidelity Evaluator — Implementation Plan (Phase 0 core + Phase 1 imagery) (~12464 tok)
- `2026-06-22-embeddings-phase0-no-break-anchor.md` — Embeddings Reframe — Phase 0 (No-Break Anchor) Implementation Plan (~4889 tok)
- `2026-06-22-embeddings-phase1-pipeline-integrity.md` — Embeddings Reframe — Phase 1 (Pipeline Integrity) Implementation Plan (~6027 tok)
- `2026-06-22-skyyrose-react-ds.md` — SkyyRose Storefront React DS (v1) Implementation Plan (~11958 tok)

## docs/superpowers/specs/

- `2026-05-25-footer-logo-swap.md` — Footer Logo Swap to Brand-Primary Monogram (~1323 tok)
- `2026-05-25-v2-mockup-design.md` — SkyyRose v2 Mockup — Visual Direction Lock (~4387 tok)
- `2026-05-27-compositor-production-hardening-design.md` — Compositor Production Hardening — Four Enhancement Patterns (~6102 tok)
- `2026-05-27-elite-team-creative-cloud-strategic-spec.md` — Elite Team — Strategic Spec (~5711 tok)
- `2026-05-27-mockup-stage-d-and-cost-ceiling-design.md` — Mockup-First Stage D Landing + IC-Light Cost Gate (~3637 tok)
- `2026-05-28-immersive-scene-intro-design.md` — Immersive Scene Intro + Premium Motion — Design Spec (~3063 tok)
- `2026-05-28-replica-foundry-design.md` — Replica Foundry — Multi-Tenant SaaS Imagery Pipeline (Design Spec) (~5392 tok)
- `2026-05-29-catalog-dossier-steward-design.md` — Catalog & Dossier Steward — Design Spec (~2820 tok)
- `2026-05-29-replica-foundry-roadmap.md` — Replica Foundry — Milestone Roadmap (~1389 tok)
- `2026-05-31-elite-team-build-evidence.md` — Elite Team Build — Reproducible Evidence Bundle (~4600 tok)
- `2026-05-31-pipeline-completion-rollout.md` — Pipeline Completion Rollout — Every DevSkyy Pipeline, Evidence-Verified (~2742 tok)
- `2026-06-01-orchestration-mode-design.html` — Orchestration Mode — Design Spec (2026-06-01) (~6876 tok)
- `2026-06-02-pipeline3d-orchestrator-design.html` — Unified 3D Pipeline Orchestrator — Design Spec (~4627 tok)
- `2026-06-05-skyyrose-elite-plugin-design.md` — SkyyRose Elite Plugin — Design Spec (~1181 tok)
- `2026-06-13-skyyrose-plugin-suite-design.md` — SkyyRose Plugin Suite — Design Spec (~3419 tok)
- `2026-06-14-collection-identity-sot-design.md` — Collection Identity SOT — Design Spec (~4771 tok)
- `2026-06-16-evaluation-system-two-domains-design.html` — Evaluation System (Two Domains) — Design Spec (~4821 tok)
- `2026-06-16-evaluator-observability-agents-design.html` — Evaluator + Observability Agents — Design Spec (~7751 tok)
- `2026-06-16-evaluator-observability-research.md` — Evaluator + Observability Agents — Research Report (~5407 tok)
- `2026-06-22-embeddings-reframe-design.md` — Embeddings Reframe — Design Spec (~6831 tok)
- `2026-06-22-skyyrose-react-ds-design.md` — SkyyRose Storefront React Design System → claude.ai/design (WordPress-compatible) (~3121 tok)
- `2026-07-12-collection-scene-hero-design.md` — Collection Scene Hero — Design Spec (~3088 tok)
- `2026-07-12-programmatic-tool-calling-integration-design.md` — Programmatic Tool Calling (PTC) — Full-Platform Integration Spec (~2587 tok)
- `elite-theme-platform.html` — Elite Theme Platform — Provider-Agnostic Autonomous Commercial Theme Agents (~2764 tok)
- `self-healing-theme-loop.html` — Self-Healing + Self-Improving + Learning Theme Loop — Contract (~11373 tok)
- `skyyrose-suite-selfheal-audit-handoff.html` — Skyyrose Suite — Self-Heal &amp; Learning Audit Handoff (~5725 tok)

## docs/testing/

- `COVERAGE_MATRIX.md` — DevSkyy Test Coverage Matrix (~4347 tok)
- `README.md` — Project documentation (~1879 tok)

## elite-theme-platform/adapters/nextjs/

- `component-kit.md` — Next.js Adapter — Cockpit Component Vocabulary (~3413 tok)
- `contract.ts` — Elite Theme Platform — Next.js Adapter Contract (~3679 tok)
  - section `BrandBrief` L22-34 (~131 tok)
  - section `DashboardSection` L35-43 (~74 tok)
  - section `DashboardTokenOverrides` L44-62 (~141 tok)
  - section `ScaffoldOutput` L63-86 (~259 tok)
  - section `DesignSystem` L87-95 (~97 tok)
  - section `DashboardTokenSet` L96-103 (~62 tok)
  - section `BuildOutput` L104-127 (~251 tok)
  - section `DeployConfig` L128-143 (~149 tok)
  - section `DeployResult` L144-165 (~191 tok)
  - class `DeployKeyholeError` L166-178 (~127 tok)
  - section `MonitorConfig` L179-189 (~113 tok)
  - section `RouteCheck` L190-196 (~50 tok)
  - section `RSCCheck` L197-202 (~39 tok)
  - section `CanonCheck` L203-209 (~42 tok)
  - section `MonitorResult` L210-240 (~365 tok)
  - section `CommerceBindConfig` L241-253 (~134 tok)
  - section `CommerceCredentials` L254-260 (~70 tok)
  - section `CommerceBindResult` L261-287 (~307 tok)
  - section `Regression` L288-298 (~102 tok)
  - section `HealResult` L299-355 (~628 tok)
  - section `NextjsThemeAdapter` L356-368 (~78 tok)
- `README.md` — Project documentation (~1744 tok)
- `tokens.ts` — Elite Theme Platform — Next.js Adapter Design Tokens (~2945 tok)

## eval/

- `agent-skill-inventory.md` — Agent & Skill Inventory Audit (~4683 tok)
- `AGENTS.md` — AGENTS.md — `eval/` (evaluation truth-doc layer) (~1396 tok)
- `banned-elements.md` — Banned-by-Default Elements (~1931 tok)
- `blocking-prerequisites.md` — Blocking Prerequisites — Phase 0.5 (~647 tok)
- `brand-story.md` — Skyyrose — Brand Story Canon (~1578 tok)
- `brand.md` — Brand Voice & Visual Adherence (~1390 tok)
- `commercial-protocols.md` — Commercial Protocols Matrix (~3090 tok)
- `cost-cap-policy.md` — Cost-Cap Policy (Skyyrose V2 Build) (~2579 tok)
- `design-system.json` — Declares families (~1686 tok)
- `integrations.md` — Per-Integration Eval Rubric (~1216 tok)
- `luxury-references.md` — Three Luxury Reference Brands (~2225 tok)
- `marketplace.md` — Marketplace Readiness Checklist (~1741 tok)
- `measurement-access-requests.md` — Measurement Access Requests — Single Sitting (~4126 tok)
- `page-flow.md` — Page Flow / IA Eval Rubric (~714 tok)
- `premium-feel.md` — Premium-Feel Sitewide Checklist (~1371 tok)
- `shocking.md` — Shocking-Not-Impressive Criteria (~1191 tok)
- `silent-disable-audit.md` — Silent-Disable Pattern Audit (~3596 tok)
- `templates.md` — Per-Template Eval Rubric (~902 tok)

## eval/critique/

- `current-site-audit.md` — SkyyRose Current-Site Critique Audit — v1 (Phase 0) (~11205 tok)

## evaluation/

- `__init__.py` — Package init; re-exports RenderFidelityEvaluator, Verdict (~22 tok)
- `adapter.py` — DomainAdapter Protocol: deterministic_checks / build_judge_request / parse_verdict / revise (~288 tok)
- `agents.py` — RenderFidelityEvaluator job-title agent: thin wrapper over EvaluationCore + ImageryAdapter (~782 tok)
  - class `RenderFidelityEvaluator` L21-36 (~164 tok)
  - class `CopyEvaluator` L37-72 (~406 tok)
- `budget.py` — Cost budget + STOP-AND-SHOW ceiling for evaluation judge calls. (~571 tok)
  - class `CostCapExceeded` L26-30 (~38 tok)
  - class `EvalBudget` L31-52 (~216 tok)
- `calibration.py` — CalibrationHarness: runs adapter over ground-truth labels, computes Cohen's kappa (~234 tok)
- `contracts.py` — Normalized Verdict dataclass (frozen), Severity enum, EvalDomain literal (~454 tok)
- `core.py` — EvaluationCore: score() det-gate→judge→verdict; gate() revise loop with cap (~1297 tok)
  - class `EvaluationCore` L27-105 (~1020 tok)
- `judge.py` — ClaudeJudge: Anthropic vision judge via forced tool-use; image_block helper; configurable model (~979 tok)
  - fn `anthropic_cost_usd` L29-35 (~96 tok)
  - fn `make_client` L36-49 (~147 tok)
  - fn `image_block` L50-58 (~96 tok)
  - class `ClaudeJudge` L59-87 (~369 tok)
- `observer.py` — EvaluationObserver: structured JSON event logging for every verdict (~631 tok)
  - class `Observer` L13-53 (~408 tok)
  - fn `judge_human_agreement` L54-61 (~129 tok)

## evaluation/domains/

- `__init__.py` — Evaluation domain adapters. (~10 tok)
- `copy.py` — Brand Copy Evaluator — copy/content domain adapter. (~3280 tok)
  - class `CopyBrief` L148-157 (~73 tok)
  - fn `_clamp_score` L158-166 (~84 tok)
  - fn `_uses_sku_as_handle` L167-178 (~133 tok)
  - class `CopyAdapter` L179-275 (~1088 tok)
- `imagery.py` — Render Fidelity Evaluator — imagery domain adapter. (~1440 tok)
  - class `ImageryAdapter` L56-118 (~868 tok)

## examples/

- `aos_demo.py` — Live demo of the AOS kernel — Phase 1 + 2. (~1752 tok)
  - fn `banner` L32-35 (~23 tok)
  - fn `kv` L36-39 (~28 tok)
  - fn `main` L40-179 (~1451 tok)
- `autonomous_agent_demo.py` — Autonomous coding agent demo for DevSkyy. (~6052 tok)
  - fn `parse_args` L112-219 (~1065 tok)
  - fn `resolve_task` L220-237 (~170 tok)
  - fn `prepare_project_dir` L238-247 (~119 tok)
  - fn `check_auth` L248-265 (~207 tok)
  - fn `_session_path` L266-269 (~25 tok)
  - fn `load_saved_session` L270-280 (~104 tok)
  - fn `save_session` L281-289 (~121 tok)
  - fn `resolve_session` L290-314 (~252 tok)
  - fn `load_mcp_servers` L315-336 (~228 tok)
  - fn `build_builtin_server` L337-378 (~627 tok)
  - fn `build_sandbox` L379-390 (~163 tok)
  - fn `build_options` L391-428 (~416 tok)
  - fn `_format_tool_use` L429-444 (~189 tok)
  - fn `print_assistant` L445-459 (~166 tok)
  - fn `print_tool_results` L460-471 (~152 tok)
  - fn `print_summary` L472-486 (~181 tok)
  - fn `run_agent` L487-508 (~283 tok)
  - fn `_describe_extras` L509-523 (~152 tok)
  - fn `main` L524-562 (~408 tok)
- `basic_query.py` — basic_example, single_agent_example, main (~616 tok)
  - fn `basic_example` L17-44 (~259 tok)
  - fn `single_agent_example` L45-67 (~177 tok)
  - fn `main` L68-87 (~116 tok)
- `basic-usage.ts` — DevSkyy Basic Usage Examples (~2019 tok)
  - fn `basicInitialization` L16-33 (~132 tok)
  - fn `agentManagement` L34-75 (~315 tok)
  - fn `openaiIntegration` L76-120 (~374 tok)
  - fn `threejsVisualization` L121-187 (~519 tok)
  - fn `agentMonitoring` L188-208 (~149 tok)
  - fn `errorHandlingExample` L209-238 (~209 tok)
  - fn `runExamples` L239-276 (~244 tok)
- `claude_agent_sdk_demo.py` — basic_query_demo, code_execution_demo, main (~472 tok)
- `continuous_conversation.py` — interactive_conversation, multi_turn_analysis, collaborative_workflow, main (~2236 tok)
  - fn `interactive_conversation` L23-88 (~730 tok)
  - fn `multi_turn_analysis` L89-143 (~587 tok)
  - fn `collaborative_workflow` L144-200 (~585 tok)
  - fn `main` L201-228 (~213 tok)
- `llamaindex_multimodal_demo.py` — demo_multimodal_capabilities, quick_test (~1710 tok)
  - fn `demo_multimodal_capabilities` L30-132 (~1038 tok)
  - fn `quick_test` L133-188 (~501 tok)
- `luxury-product-showcase.tsx` — LuxuryProductShowcase — uses useEffect (~2395 tok)
  - section `Product` L16-25 (~44 tok)
  - fn `LuxuryProductShowcase` L26-247 (~2250 tok)
- `multi_agent_workflow.py` — product_launch_workflow, campaign_optimization_workflow, customer_support_workflow, main (~1309 tok)
  - fn `product_launch_workflow` L17-68 (~461 tok)
  - fn `campaign_optimization_workflow` L69-103 (~286 tok)
  - fn `customer_support_workflow` L104-143 (~323 tok)
  - fn `main` L144-169 (~170 tok)
- `security_alerting_demo.py` — demo_basic_slack_alert, demo_multi_channel_alerting, demo_manual_channel_selection, demo_alert_deduplication + 3 more (~2283 tok)
  - fn `demo_basic_slack_alert` L20-46 (~287 tok)
  - fn `demo_multi_channel_alerting` L47-102 (~569 tok)
  - fn `demo_manual_channel_selection` L103-127 (~234 tok)
  - fn `demo_alert_deduplication` L128-155 (~246 tok)
  - fn `demo_severity_based_routing` L156-194 (~363 tok)
  - fn `demo_slack_color_coding` L195-209 (~133 tok)
  - fn `main` L210-246 (~319 tok)
- `tool_registry_example.py` — main (~1669 tok)
  - fn `main` L28-168 (~1501 tok)
- `webhook_integration_example.py` — API: POST (2 endpoints) (~2124 tok)
  - fn `process_new_order` L29-33 (~52 tok)
  - fn `process_completed_order` L34-38 (~57 tok)
  - fn `process_cancelled_order` L39-43 (~57 tok)
  - fn `send_critical_alert` L44-48 (~44 tok)
  - fn `log_security_event` L49-58 (~107 tok)
  - fn `register_webhook_endpoints` L59-115 (~586 tok)
  - fn `handle_order_webhook` L116-151 (~326 tok)
  - fn `handle_security_webhook` L152-187 (~311 tok)
  - fn `send_security_events_example` L188-222 (~381 tok)

## examples/collection-demo/

- `index.html` — SkyyRose Collection 3D Experience Demo (~923 tok)
- `main.ts` — SkyyRose Collection 3D Experience Demo Entry Point (~1474 tok)
  - fn `initExperience` L52-154 (~912 tok)

## frontend/

- `.gitignore` — Git ignore rules (~68 tok)
- `AGENTS.md` — AGENTS.md — `frontend/` (Vercel — Next.js dashboard + API routes) (~872 tok)
- `CLAUDE.md` — frontend/ — DevSkyy dashboard (Next.js 16, React 19) (~1234 tok)
- `components.json` (~133 tok)
- `DASHBOARD_STATUS.md` — Dashboard Status - All Components Working ✅ (~1845 tok)
- `DEPLOYMENT.md` — DevSkyy Deployment Guide (~3281 tok)
- `eslint.config.mjs` — ESLint flat configuration (~964 tok)
- `IMPLEMENTATION_SUMMARY.md` — Implementation Summary - Vercel & WordPress Integration (~3966 tok)
- `next-env.d.ts` — / <reference types="next" /> (~71 tok)
- `next.config.ts` — Next.js configuration (~406 tok)
- `package-lock.json` — npm lock file (~162645 tok)
- `package.json` — Node.js package manifest (~1344 tok)
- `playwright.config.ts` — Playwright test configuration (~236 tok)
- `postcss.config.js` — PostCSS configuration (~24 tok)
- `tailwind.config.ts` — Tailwind CSS configuration (~770 tok)
- `tsconfig.json` — TypeScript configuration (~200 tok)
- `VERCEL_PROJECT_CONFIG.md` — Vercel Project Configuration (~1510 tok)
- `vercel.json` — /*.ts": { (~492 tok)
- `vitest.config.ts` — vitest config scoped to lib/wp/**/*.test.ts (server-only-free WP wiring modules) — WS7 (~374 tok)

## frontend/app/

- `AGENTS.md` — Next.js App Routes — Agent Guide (~1740 tok)
- `globals.css` — Styles: 6 rules, 65 vars, 4 animations, 3 layers (~1826 tok)
- `layout.tsx` — inter (~429 tok)
- `page.tsx` — metadata (~306 tok)

## frontend/app/(storefront)/

- `HomePage.tsx` — RotatingLogoFallback — uses useState, useEffect (~6562 tok)
  - section `Particle` L14-21 (~35 tok)
  - section `HomePageProps` L22-25 (~18 tok)
  - fn `HomePage` L26-553 (~6379 tok)

## frontend/app/admin/

- `console.css` — Styles: 9 rules, 4 vars, 3 animations (~345 tok)
- `layout.tsx` — AdminLayout (~252 tok)
- `page.tsx` — fetchDashboardData — renders chart — uses useQuery (~3130 tok)
  - fn `safeOrders` L26-38 (~136 tok)
  - fn `safeAdminProducts` L39-46 (~41 tok)
  - fn `OverviewPage` L47-240 (~2580 tok)
  - fn `danger` L241-243 (~23 tok)
  - fn `warning` L244-246 (~24 tok)
  - fn `idle` L247-250 (~23 tok)
- `SessionProviderClient.tsx` — SessionProvider (~133 tok)

## frontend/app/admin/3d-pipeline/

- `page.tsx` — Pipeline3DPage — uses useState, useEffect (~5839 tok)
  - section `MeshyStatus` L30-36 (~35 tok)
  - fn `Pipeline3DPage` L37-361 (~3670 tok)
  - fn `StatusBadge` L362-380 (~196 tok)
  - fn `GradientStatCard` L381-409 (~250 tok)
  - fn `JobCard` L410-458 (~584 tok)
  - fn `MeshyBadge` L459-485 (~202 tok)
  - fn `MeshyProviderCard` L486-541 (~562 tok)
  - fn `Pipeline3DSkeleton` L542-555 (~110 tok)

## frontend/app/admin/agents/

- `page.tsx` — CATEGORY_ICONS — uses useState (~969 tok)
  - fn `AgentsPage` L14-79 (~791 tok)

## frontend/app/admin/assets/

- `page.tsx` — COLLECTIONS — uses useState, useEffect (~9625 tok)
  - fn `AssetsPage` L66-831 (~8874 tok)
  - fn `AssetsSkeleton` L832-850 (~158 tok)

## frontend/app/admin/autonomous/

- `page.tsx` — StatusBadge — uses useState, useCallback, useEffect (~4371 tok)
  - fn `StatusBadge` L29-39 (~138 tok)
  - fn `StatusIcon` L40-50 (~118 tok)
  - fn `HistoryActionBadge` L51-61 (~138 tok)
  - fn `AutonomousAgentsPage` L62-339 (~3781 tok)

## frontend/app/admin/catalog-search/

- `page.tsx` — /admin/catalog-search — Semantic catalog search + "You might also like" surface. (~6357 tok)
  - fn `collectionLabel` L43-50 (~90 tok)
  - fn `ScoreBadge` L51-68 (~189 tok)
  - section `MatchCardProps` L69-74 (~38 tok)
  - fn `MatchCard` L75-117 (~532 tok)
  - section `SimilarPanelProps` L118-124 (~40 tok)
  - fn `SimilarPanel` L125-197 (~950 tok)
  - section `FeaturedPanelState` L198-203 (~34 tok)
  - fn `FeaturedPanel` L204-315 (~1419 tok)
  - fn `CatalogSearchPage` L316-522 (~2648 tok)

## frontend/app/admin/catalog/

- `page.tsx` — /admin/catalog — Product / SKU editor against the canonical catalog CSV. (~6254 tok)
  - section `SotImageSet` L42-47 (~24 tok)
  - section `CatalogProduct` L48-67 (~110 tok)
  - section `DraftFields` L68-88 (~125 tok)
  - fn `collectionLabel` L89-92 (~27 tok)
  - fn `toDraft` L93-106 (~91 tok)
  - fn `parseSizes` L107-114 (~59 tok)
  - fn `buildPatch` L115-138 (~287 tok)
  - fn `CatalogPage` L139-535 (~4537 tok)
  - fn `SotImagery` L536-566 (~322 tok)
  - fn `ImagePreview` L567-592 (~254 tok)

## frontend/app/admin/collections/

- `page.tsx` — safeOrders (~1114 tok)
  - fn `safeOrders` L13-22 (~77 tok)
  - fn `haloFor` L23-29 (~60 tok)
  - fn `CollectionsPage` L30-86 (~684 tok)
  - fn `Stat` L87-97 (~104 tok)

## frontend/app/admin/competitors/

- `page.tsx` — CATEGORY_OPTIONS — renders form, modal — uses useQuery, useState (~6061 tok)
  - fn `CompetitorsPage` L72-483 (~5424 tok)

## frontend/app/admin/conversion/

- `page.tsx` — COLLECTION_CONFIG — renders chart — uses useState, useEffect, useCallback (~20110 tok)
  - section `FunnelStage` L47-53 (~37 tok)
  - section `ProductHeat` L54-63 (~79 tok)
  - section `ABVariant` L64-71 (~51 tok)
  - section `ControlsState` L72-116 (~398 tok)
  - section `ApiProductRow` L117-122 (~24 tok)
  - fn `hashSku` L123-131 (~89 tok)
  - fn `isKnownCollection` L132-135 (~37 tok)
  - fn `deriveHeatData` L136-187 (~426 tok)
  - section `LiveMetrics` L188-218 (~212 tok)
  - fn `ConversionIntelligencePage` L219-423 (~2106 tok)
  - fn `FunnelVisualization` L424-500 (~819 tok)
  - fn `OverviewTab` L501-685 (~2013 tok)
  - fn `ABTestsTab` L686-766 (~754 tok)
  - fn `VariantCard` L767-839 (~662 tok)
  - fn `ProductHeatTab` L840-853 (~86 tok)
  - fn `ProductHeatCard` L854-980 (~1485 tok)
  - fn `VelocityAnalyticsTab` L981-1238 (~3250 tok)
  - fn `ControlsTab` L1239-1505 (~2649 tok)
  - fn `MomentumCommerceTab` L1506-1811 (~4229 tok)
  - fn `ConversionSkeleton` L1812-1840 (~245 tok)
  - fn `formatNumber` L1841-1846 (~59 tok)
  - fn `getHeatColor` L1847-1863 (~121 tok)

## frontend/app/admin/customers/

- `page.tsx` — Real WC customer records don't carry order-count/spend on the customer (~1235 tok)
  - fn `safeCustomers` L9-16 (~42 tok)
  - fn `safeOrders` L17-27 (~107 tok)
  - fn `tierFor` L28-33 (~74 tok)
  - fn `CustomersPage` L34-98 (~878 tok)

## frontend/app/admin/elite-studio/

- `layout.tsx` — ELITE_NAV (~692 tok)
  - fn `EliteStudioNav` L22-52 (~265 tok)
  - fn `EliteStudioLayout` L53-77 (~253 tok)
- `page.tsx` — QUICK_ACTIONS — uses useQuery (~3675 tok)
  - fn `EliteStudioPage` L91-336 (~2870 tok)

## frontend/app/admin/elite-studio/characters/

- `page.tsx` — containerVariants — uses useQuery (~2843 tok)
  - fn `CharacterCard` L28-108 (~878 tok)
  - fn `CharactersPage` L109-259 (~1748 tok)

## frontend/app/admin/elite-studio/design/

- `page.tsx` — PROMPT_SUGGESTIONS (~6792 tok)
  - section `Message` L31-38 (~40 tok)
  - section `DesignResult` L39-63 (~288 tok)
  - fn `DesignResultDisplay` L64-171 (~1154 tok)
  - fn `ChatBubble` L172-206 (~344 tok)
  - fn `DesignCoPilotPage` L207-603 (~4676 tok)
  - fn `extractConceptName` L604-607 (~31 tok)

## frontend/app/admin/elite-studio/operations/

- `page.tsx` — INTENTS — renders table (~3456 tok)
  - fn `formatAgo` L54-61 (~47 tok)
  - fn `OperationsListSkeleton` L62-79 (~157 tok)
  - fn `OperationsListPage` L80-87 (~48 tok)
  - fn `OperationsListContent` L88-338 (~2792 tok)

## frontend/app/admin/elite-studio/operations/[id]/

- `page.tsx` — ResultPanel — uses useState, useQuery (~3816 tok)
  - section `Props` L37-40 (~16 tok)
  - fn `ResultPanel` L41-125 (~936 tok)
  - fn `OperationDetailSkeleton` L126-135 (~75 tok)
  - fn `OperationDetailPage` L136-143 (~58 tok)
  - fn `OperationDetailContent` L144-369 (~2440 tok)

## frontend/app/admin/experience/

- `page.tsx` — dailyEvents — renders chart — uses useState (~6594 tok)
  - section `Module` L77-143 (~521 tok)
  - section `Directive` L144-179 (~222 tok)
  - fn `ExperiencePage` L180-590 (~5280 tok)

## frontend/app/admin/hub/

- `page.tsx` — timeAgo — uses useQuery (~4702 tok)
  - fn `timeAgo` L14-23 (~93 tok)
  - fn `taskStatusColor` L24-30 (~65 tok)
  - fn `HubPage` L31-300 (~4115 tok)
  - fn `HeroStat` L301-311 (~113 tok)
  - fn `PipelineHeader` L312-322 (~114 tok)
  - fn `EmptyRow` L323-326 (~39 tok)

## frontend/app/admin/huggingface/

- `page.tsx` — SIMULATED_STATS — uses useState, useCallback, useEffect (~16090 tok)
  - section `HFSpace` L45-56 (~68 tok)
  - section `HFModel` L57-66 (~44 tok)
  - section `HFEndpoint` L67-78 (~70 tok)
  - section `HFStats` L79-229 (~1116 tok)
  - fn `HuggingFacePage` L230-1028 (~9927 tok)
  - fn `GradientStatCard` L1029-1059 (~257 tok)
  - fn `SpaceCard` L1060-1210 (~1480 tok)
  - fn `ModelCard` L1211-1263 (~599 tok)
  - fn `EndpointCard` L1264-1418 (~1599 tok)
  - fn `HuggingFaceSkeleton` L1419-1437 (~156 tok)
  - fn `TrainingStatusBadge` L1438-1466 (~404 tok)
  - fn `formatNumber` L1467-1472 (~57 tok)

## frontend/app/admin/imagery/

- `page.tsx` — PROVIDER_GRADIENTS — uses useState, useEffect (~8159 tok)
  - section `ImageProvider` L37-49 (~70 tok)
  - section `GeneratedImage` L50-63 (~84 tok)
  - section `PipelineStats` L64-117 (~660 tok)
  - fn `ImageryPipelinePage` L118-487 (~3938 tok)
  - fn `GradientStatCard` L488-518 (~257 tok)
  - fn `ProviderCard` L519-581 (~666 tok)
  - fn `GalleryCard` L582-760 (~1958 tok)
  - fn `ImageryPipelineSkeleton` L761-784 (~215 tok)

## frontend/app/admin/jobs/

- `page.tsx` — QUEUE_META — uses useQuery (~2149 tok)
  - section `QueueStats` L25-58 (~176 tok)
  - fn `fetchQueueStats` L59-65 (~70 tok)
  - fn `JobsPage` L66-231 (~1788 tok)

## frontend/app/admin/journey-analytics/

- `page.tsx` — Fetch live metrics from the Conversion Analytics API and merge with (~9403 tok)
  - section `CollectionData` L24-35 (~69 tok)
  - section `RoomData` L36-44 (~45 tok)
  - section `FunnelStep` L45-50 (~23 tok)
  - section `StatsData` L51-57 (~38 tok)
  - section `RealTimeData` L58-64 (~38 tok)
  - section `WeeklyTrend` L65-159 (~1140 tok)
  - section `LiveMetrics` L160-195 (~261 tok)
  - fn `fetchLiveMetrics` L196-280 (~944 tok)
  - fn `JourneyAnalyticsPage` L281-431 (~1530 tok)
  - fn `GradientStatCard` L432-462 (~257 tok)
  - fn `CollectionBreakdownCard` L463-533 (~880 tok)
  - fn `ConversionFunnelCard` L534-588 (~666 tok)
  - fn `RoomHeatmapTable` L589-678 (~1150 tok)
  - fn `RealTimePanel` L679-749 (~848 tok)
  - fn `HistoricalPanel` L750-828 (~994 tok)
  - fn `JourneyAnalyticsSkeleton` L829-853 (~238 tok)
  - fn `formatNumber` L854-859 (~57 tok)
  - fn `formatTime` L860-865 (~45 tok)

## frontend/app/admin/launch-desk/

- `LaunchDeskClient.tsx` — EMPTY_FORM — renders form — uses useState, useRef, useMemo (~4736 tok)
  - section `LaunchForm` L18-27 (~57 tok)
  - section `ProgressItem` L28-33 (~24 tok)
  - section `LaunchStreamEvent` L34-57 (~173 tok)
  - fn `parseEvent` L58-69 (~80 tok)
  - fn `setProgress` L70-80 (~108 tok)
  - fn `LaunchDeskClient` L81-387 (~4047 tok)
  - fn `Field` L388-413 (~179 tok)
- `loading.tsx` — LaunchDeskLoading (~158 tok)
- `page.tsx` — metadata (~128 tok)
- `README.md` — Project documentation (~1071 tok)

## frontend/app/admin/mascot/

- `page.tsx` — POSE_OPTIONS — uses useState, useCallback, useEffect (~7220 tok)
  - section `MascotJob` L41-53 (~74 tok)
  - section `MascotStats` L54-115 (~692 tok)
  - fn `MascotPage` L116-469 (~4262 tok)
  - fn `GradientStatCard` L470-498 (~250 tok)
  - fn `MascotCard` L499-623 (~1416 tok)
  - fn `MascotSkeleton` L624-646 (~213 tok)

## frontend/app/admin/mcp/

- `page.tsx` — McpConsolePage — uses useEffect, useCallback (~1416 tok)
  - section `McpTool` L5-9 (~18 tok)
  - section `ToolResultContent` L10-14 (~19 tok)
  - fn `McpConsolePage` L15-147 (~1358 tok)

## frontend/app/admin/monitoring/

- `page.tsx` — formatTimestamp (~3641 tok)
  - fn `formatTimestamp` L22-29 (~95 tok)
  - fn `ServiceStatusIcon` L30-35 (~92 tok)
  - fn `ServiceStatusBadge` L36-44 (~119 tok)
  - fn `CircuitBreakerBadge` L45-55 (~146 tok)
  - fn `ActivityIcon` L56-61 (~86 tok)
  - fn `ServiceCardSkeleton` L62-76 (~138 tok)
  - fn `MonitoringPage` L77-296 (~2815 tok)

## frontend/app/admin/orders/

- `page.tsx` — safeOrders (~1396 tok)
  - fn `safeOrders` L17-24 (~40 tok)
  - fn `OrdersPage` L25-115 (~1191 tok)

## frontend/app/admin/pipeline/

- `page.tsx` — PipelinePage — uses useState, useEffect, useCallback (~3190 tok)
  - section `QueueStats` L30-37 (~38 tok)
  - fn `PipelinePage` L38-315 (~2722 tok)
  - fn `PipelineSkeleton` L316-330 (~123 tok)

## frontend/app/admin/pricing/

- `page.tsx` — STRATEGY_OPTIONS — renders form, table — uses useState (~3210 tok)
  - fn `parseSkus` L39-49 (~52 tok)
  - fn `PricingPage` L50-276 (~2710 tok)

## frontend/app/admin/products/

- `page.tsx` — safeAdminProducts (~1219 tok)
  - fn `safeAdminProducts` L10-17 (~41 tok)
  - fn `stockView` L18-24 (~126 tok)
  - fn `ProductsPage` L25-95 (~921 tok)

## frontend/app/admin/qa/

- `page.tsx` — QAPage — uses useState, useCallback, useEffect (~2476 tok)
  - fn `QAPage` L23-258 (~2278 tok)

## frontend/app/admin/round-table/

- `page.tsx` — RoundTablePage — uses useQuery, useState, useEffect (~4301 tok)
  - fn `RoundTablePage` L26-335 (~3806 tok)
  - fn `RoundTableSkeleton` L336-366 (~269 tok)

## frontend/app/admin/settings/

- `page.tsx` — SettingsPage — uses useState, useEffect (~1836 tok)
  - section `IntegrationItem` L7-13 (~29 tok)
  - section `IntegrationGroup` L14-18 (~22 tok)
  - fn `statusColor` L19-24 (~49 tok)
  - fn `envStatus` L25-30 (~52 tok)
  - fn `SettingsPage` L31-133 (~1615 tok)

## frontend/app/admin/social-media/

- `page.tsx` — PLATFORM_CONFIG — renders chart — uses useState, useCallback, useEffect (~9428 tok)
  - section `ProductOption` L78-90 (~113 tok)
  - fn `SocialMediaPage` L91-657 (~6199 tok)
  - fn `PlatformStatCard` L658-703 (~400 tok)
  - fn `GradientStatCard` L704-734 (~257 tok)
  - fn `QueueItem` L735-784 (~606 tok)
  - fn `CampaignCard` L785-835 (~524 tok)
  - fn `AnalyticsCard` L836-896 (~534 tok)
  - fn `SocialMediaSkeleton` L897-919 (~209 tok)
  - fn `formatNumber` L920-925 (~57 tok)

## frontend/app/admin/tasks/

- `page.tsx` — TasksPage — uses useState (~1126 tok)
  - fn `TasksPage` L10-123 (~1021 tok)

## frontend/app/admin/vercel/

- `page.tsx` — VercelAdminPage — uses useState, useEffect (~3824 tok)
  - fn `VercelAdminPage` L24-374 (~3660 tok)

## frontend/app/admin/web-extraction/

- `page.tsx` — DEFAULT_SCHEMA — renders form — uses useState (~3483 tok)
  - fn `errorMessage` L44-59 (~184 tok)
  - fn `WebExtractionPage` L60-258 (~2928 tok)

## frontend/app/admin/wordpress/

- `page.tsx` — WordPressAdminPage — uses useState, useCallback, useEffect (~11525 tok)
  - section `CreateFormState` L60-70 (~87 tok)
  - fn `WordPressAdminPage` L71-925 (~10980 tok)

## frontend/app/api/auth/[...nextauth]/

- `route.ts` — NextAuth.js v4 API Route Handler (~82 tok)

## frontend/app/api/catalog/

- `route.ts` — Admin Catalog API — RAW catalog read for the /admin/catalog editor. (~461 tok)

## frontend/app/api/catalog/[sku]/

- `route.ts` — Admin Catalog API — single-SKU UPDATE. (~1241 tok)
  - fn `toCsvPatch` L33-48 (~286 tok)
  - fn `putHandler` L49-109 (~602 tok)

## frontend/app/api/catalog/summary/

- `route.ts` — Live WooCommerce catalog counts vs canonical CSV, by collection — WS7 (~598 tok)
  - fn `getHandler` L18-57 (~409 tok)

## frontend/app/api/checkout/

- `route.ts` — Stripe is initialized lazily to avoid errors when STRIPE_SECRET_KEY is not set (~622 tok)
  - fn `getStripe` L4-13 (~80 tok)
  - section `CheckoutItem` L14-21 (~34 tok)
  - fn `POST` L22-78 (~472 tok)

## frontend/app/api/console/orders-count/

- `route.ts` — Orders-count for the Operator Console's nav badge (ConsoleShell fetches (~266 tok)

## frontend/app/api/conversion/

- `route.ts` — Conversion Analytics API — Unified Event Collection (~3316 tok)
  - section `ConversionEvent` L23-30 (~39 tok)
  - section `AggregatedMetrics` L31-85 (~399 tok)
  - fn `addEvents` L86-104 (~150 tok)
  - fn `aggregateMetrics` L105-295 (~1630 tok)
  - fn `corsHeaders` L296-310 (~183 tok)
  - fn `optionsHandler` L311-316 (~54 tok)
  - fn `postHandler` L317-375 (~542 tok)
  - fn `getHandler` L376-392 (~121 tok)

## frontend/app/api/health/

- `route.ts` — WP↔dashboard wiring health check: public/authed-wc/authed-wp probes — WS7 (~515 tok)
  - fn `getHandler` L18-59 (~349 tok)

## frontend/app/api/huggingface/

- `route.ts` — HuggingFace Hub API Proxy Route (~3179 tok)
  - section `HFSpace` L31-39 (~35 tok)
  - section `HFModel` L40-48 (~40 tok)
  - section `HFActionRequestBody` L49-53 (~22 tok)
  - section `SimulatedSpace` L54-62 (~36 tok)
  - section `SimulatedModel` L63-74 (~84 tok)
  - fn `getToken` L75-78 (~23 tok)
  - fn `makeAuthHeaders` L79-89 (~79 tok)
  - fn `getSimulatedSpaces` L90-121 (~232 tok)
  - fn `getSimulatedModels` L122-144 (~179 tok)
  - fn `fetchSpaces` L145-161 (~146 tok)
  - fn `fetchModels` L162-178 (~146 tok)
  - fn `fetchWhoAmI` L179-190 (~113 tok)
  - fn `performSpaceAction` L191-231 (~410 tok)
  - fn `getHandler` L232-314 (~703 tok)
  - fn `postHandler` L315-393 (~623 tok)

## frontend/app/api/imagery/

- `route.ts` — Imagery API Route Handler (~3412 tok)
  - section `GenerationRequest` L19-26 (~74 tok)
  - section `GenerationRecord` L27-51 (~190 tok)
  - fn `addRecord` L52-65 (~125 tok)
  - section `ProviderConfig` L66-109 (~364 tok)
  - fn `getProviderStatus` L110-115 (~61 tok)
  - fn `selectProvider` L116-130 (~168 tok)
  - fn `generateWithGemini` L131-155 (~260 tok)
  - fn `generateWithImagen` L156-178 (~214 tok)
  - fn `generateWithFlux` L179-198 (~186 tok)
  - fn `generateWithReplicate` L199-231 (~302 tok)
  - fn `generateImage` L232-256 (~266 tok)
  - fn `postHandler` L257-330 (~763 tok)
  - fn `getHandler` L331-361 (~279 tok)

## frontend/app/api/jobs/

- `route.ts` — Next.js API route: POST, GET (~448 tok)

## frontend/app/api/launch-desk/

- `route.ts` — Next.js API route (~1200 tok)
  - section `StreamEvent` L17-21 (~32 tok)
  - fn `sse` L22-25 (~35 tok)
  - fn `handleLaunchDesk` L26-130 (~1009 tok)

## frontend/app/api/launch-desk/_lib/

- `agent.ts` — Exports createLaunchDeskAgent, formatLaunchPrompt (~758 tok)
  - fn `createLaunchDeskAgent` L45-55 (~72 tok)
  - fn `formatLaunchPrompt` L56-82 (~211 tok)
- `tools.ts` — Exports extractLaunchTasks, assessLaunchReadiness, buildOwnerChecklists, draftLaunchCopy (~1410 tok)
  - fn `includesAny` L9-13 (~47 tok)
  - fn `extractLaunchTasks` L14-68 (~527 tok)
  - fn `assessLaunchReadiness` L69-111 (~486 tok)
  - fn `buildOwnerChecklists` L112-121 (~109 tok)
  - fn `draftLaunchCopy` L122-146 (~209 tok)
- `types.ts` — Zod schemas: launchBriefSchema (~258 tok)

## frontend/app/api/mascot/

- `route.ts` — Brand Mascot API Route (~2528 tok)
  - section `MascotJob` L28-40 (~76 tok)
  - section `MascotGenerateRequest` L41-99 (~741 tok)
  - fn `addJob` L100-168 (~601 tok)
  - fn `getHandler` L169-194 (~225 tok)
  - fn `postHandler` L195-268 (~600 tok)

## frontend/app/api/mcp/

- `route.ts` — Route handlers run on the Node runtime by default (the MCP SDK needs Node APIs). (~1290 tok)
  - section `McpRequestBody` L17-24 (~71 tok)
  - class `McpTimeoutError` L25-31 (~36 tok)
  - fn `withClient` L32-66 (~472 tok)
  - fn `postHandler` L67-108 (~478 tok)

## frontend/app/api/monitoring/health/

- `route.ts` — Health Check Endpoint - Next.js Route Handler (~334 tok)

## frontend/app/api/monitoring/metrics/

- `route.ts` — Prometheus Metrics Endpoint - Next.js Route Handler (~475 tok)

## frontend/app/api/pipeline-status/

- `route.ts` — Pipeline Status Dashboard - API Route (~474 tok)

## frontend/app/api/pipeline/meshy/

- `route.ts` — Meshy API Route Handler (~1324 tok)
  - fn `postHandler` L20-105 (~682 tok)
  - fn `getHandler` L106-160 (~435 tok)

## frontend/app/api/pipeline/tripo/

- `route.ts` — Tripo 3D API Route Handler (~1256 tok)
  - fn `postHandler` L20-107 (~711 tok)
  - fn `getHandler` L108-149 (~335 tok)

## frontend/app/api/products/

- `route.ts` — Products API Route (~970 tok)
  - section `Product` L22-41 (~121 tok)
  - fn `deriveStatus` L42-49 (~75 tok)
  - fn `deriveShortDescription` L50-54 (~57 tok)
  - fn `deriveSeoMeta` L55-58 (~39 tok)
  - fn `shape` L59-78 (~186 tok)
  - fn `getHandler` L79-118 (~310 tok)

## frontend/app/api/settings/

- `route.ts` — Next.js API route: GET, POST (~962 tok)
  - fn `getSettings` L10-58 (~527 tok)
  - fn `isAuthenticated` L59-63 (~39 tok)
  - fn `getHandler` L64-74 (~86 tok)
  - fn `postHandler` L75-100 (~219 tok)

## frontend/app/api/social-media/

- `route.ts` — Social Media Pipeline - Main Status Route (~562 tok)
  - fn `getHandler` L14-59 (~446 tok)

## frontend/app/api/social-media/analytics/

- `route.ts` — Social Media Pipeline - Analytics Route (~3210 tok)
  - section `PlatformAnalytics` L21-31 (~54 tok)
  - section `AnalyticsResponse` L32-45 (~129 tok)
  - fn `getSimulatedAnalytics` L46-85 (~244 tok)
  - fn `fetchInstagramAnalytics` L86-141 (~519 tok)
  - fn `fetchTiktokAnalytics` L142-197 (~390 tok)
  - fn `fetchTwitterAnalytics` L198-279 (~660 tok)
  - fn `fetchFacebookAnalytics` L280-346 (~559 tok)
  - fn `getHandler` L347-399 (~437 tok)

## frontend/app/api/social-media/generate/

- `route.ts` — Social Media Pipeline - Post Generation Route (~3535 tok)
  - section `GenerateRequest` L22-27 (~40 tok)
  - section `SocialPost` L28-74 (~656 tok)
  - fn `generateFromTemplate` L75-125 (~1033 tok)
  - fn `generateWithLlm` L126-190 (~720 tok)
  - fn `postHandler` L191-288 (~815 tok)
  - fn `generateId` L289-294 (~50 tok)

## frontend/app/api/social-media/publish/

- `route.ts` — Social Media Pipeline - Publish Route (~3588 tok)
  - section `PublishRequest` L21-27 (~34 tok)
  - section `PublishResult` L28-41 (~107 tok)
  - fn `publishToInstagram` L42-148 (~849 tok)
  - fn `publishToTiktok` L149-227 (~566 tok)
  - fn `publishToTwitter` L228-307 (~630 tok)
  - fn `publishToFacebook` L308-403 (~769 tok)
  - fn `postHandler` L404-451 (~403 tok)

## frontend/app/api/social-media/schedule/

- `route.ts` — Social Media Pipeline - Schedule Route (~1140 tok)
  - section `ScheduledEntry` L18-28 (~86 tok)
  - fn `addScheduledEntry` L29-43 (~146 tok)
  - fn `postHandler` L44-116 (~598 tok)
  - fn `getHandler` L117-137 (~142 tok)

## frontend/app/api/v1/3d/generate/image/

- `route.ts` — Next.js API route: POST (~468 tok)

## frontend/app/api/v1/3d/generate/text/

- `route.ts` — Next.js API route: POST (~409 tok)

## frontend/app/api/v1/3d/jobs/

- `route.ts` — In-memory job store (replaced by database in production) (~208 tok)

## frontend/app/api/v1/3d/providers/

- `route.ts` — Next.js API route: GET (~260 tok)

## frontend/app/api/v1/3d/status/

- `route.ts` — Next.js API route: GET (~180 tok)

## frontend/app/api/webhooks/woocommerce/

- `route.ts` — WooCommerce webhook receiver, HMAC-verified + tag revalidation — WS7 (~502 tok)
  - fn `POST` L15-46 (~356 tok)

## frontend/app/api/wordpress/proxy/

- `route.ts` — WordPress API Proxy — Server-Side Credential Injection (~1038 tok)
  - fn `postHandler` L25-111 (~810 tok)

## frontend/app/api/wordpress/proxy/upload/

- `route.ts` — WordPress Media Upload Proxy — Server-Side Credential Injection (~534 tok)
  - fn `postHandler` L19-65 (~376 tok)

## frontend/app/checkout/

- `page.tsx` — CheckoutPage — uses useState (~2408 tok)
  - fn `CheckoutPage` L17-241 (~2326 tok)

## frontend/app/collections/

- `CollectionsLanding.tsx` — RotatingLogoFallback — uses useState (~2517 tok)
  - fn `CollectionsLanding` L15-192 (~2124 tok)
  - fn `CollectionCardImage` L193-235 (~263 tok)
- `layout.tsx` — metadata (~254 tok)
- `page.tsx` — metadata (~190 tok)

## frontend/app/collections/[slug]/

- `CollectionExperience.tsx` — CollectionScene — uses useState, useEffect, useCallback (~1984 tok)
  - section `CollectionExperienceProps` L18-21 (~21 tok)
  - fn `CollectionExperience` L22-212 (~1764 tok)
- `page.tsx` — generateStaticParams (~688 tok)
  - section `PageProps` L7-10 (~18 tok)
  - fn `generateStaticParams` L11-14 (~32 tok)
  - fn `generateMetadata` L15-40 (~210 tok)
  - fn `CollectionPage` L41-94 (~354 tok)

## frontend/app/login/

- `page.tsx` — API_URL — renders form — uses useRouter, useState, useEffect, useCallback (~4189 tok)
  - fn `API_URL` L17-64 (~448 tok)
  - fn `generateNonce` L65-70 (~54 tok)
  - fn `setSecureCookie` L71-76 (~86 tok)
  - fn `clearAuthData` L77-88 (~102 tok)
  - fn `checkRateLimit` L89-104 (~121 tok)
  - fn `recordLoginAttempt` L105-124 (~146 tok)
  - fn `LoginPage` L125-413 (~3032 tok)

## frontend/app/pre-order/

- `page.tsx` — metadata (~266 tok)
- `PreOrderPage.tsx` — PreOrderPage — renders form — uses useState (~5536 tok)
  - section `PreOrderPageProps` L21-24 (~20 tok)
  - fn `PreOrderPage` L25-328 (~3668 tok)
  - fn `CollectionSection` L329-405 (~646 tok)
  - fn `ProductPreOrderCard` L406-531 (~1086 tok)

## frontend/components/

- `AGENTS.md` — Next.js Components — Agent Guide (~1661 tok)
- `error-boundary.tsx` — generateErrorId — uses useCallback (~2644 tok)
  - section `ErrorBoundaryProps` L12-18 (~47 tok)
  - section `ErrorBoundaryState` L19-29 (~91 tok)
  - fn `generateErrorId` L30-33 (~33 tok)
  - fn `sanitizeErrorMessage` L34-43 (~127 tok)
  - fn `sanitizeStackTrace` L44-55 (~113 tok)
  - class `ErrorBoundary` L56-208 (~1521 tok)
  - section `UseErrorHandlerOptions` L209-213 (~29 tok)
  - fn `useErrorHandler` L214-239 (~218 tok)
  - section `AsyncBoundaryProps` L240-245 (~34 tok)
  - fn `AsyncBoundary` L246-266 (~180 tok)
  - fn `RouteErrorBoundary` L267-282 (~119 tok)
- `three-viewer.tsx` — COLLECTION_LIGHTING — renders chart — uses useEffect, useCallback, useState (~3941 tok)
  - section `ThreeViewerProps` L71-83 (~89 tok)
  - fn `Loader` L84-108 (~238 tok)
  - fn `Model` L109-146 (~258 tok)
  - fn `CollectionLighting` L147-184 (~294 tok)
  - fn `CameraController` L185-226 (~238 tok)
  - fn `ScreenshotCapture` L227-247 (~135 tok)
  - fn `ThreeViewer` L248-451 (~1800 tok)
  - fn `ModelViewerFallback` L452-507 (~418 tok)
  - fn `preloadModel` L508-511 (~20 tok)

## frontend/components/3d/

- `LuxuryProductViewer.tsx` — Model — renders chart — uses useState (~1884 tok)
  - section `LuxuryProductViewerProps` L22-30 (~79 tok)
  - fn `Model` L31-52 (~177 tok)
  - fn `LuxuryShadows` L53-77 (~131 tok)
  - fn `LuxuryEnvironment` L78-118 (~273 tok)
  - fn `LuxuryProductViewer` L119-244 (~1070 tok)
  - fn `preloadModel` L245-248 (~20 tok)
- `RotatingCollectionLogo.tsx` — LogoMesh — renders chart (~557 tok)
  - section `LogoMeshProps` L8-13 (~23 tok)
  - fn `LogoMesh` L14-50 (~258 tok)
  - section `RotatingCollectionLogoProps` L51-56 (~28 tok)
  - fn `RotatingCollectionLogo` L57-78 (~186 tok)
- `RotatingLogoFallback.tsx` — RotatingLogoFallback (~234 tok)

## frontend/components/admin/

- `WordPressSyncPanel.tsx` — WordPressSyncPanel — uses useState (~1474 tok)
  - section `WordPressSyncPanelProps` L10-14 (~28 tok)
  - fn `WordPressSyncPanel` L15-159 (~1332 tok)
- `wp-error-boundary.tsx` — Exports WPErrorBoundary (~574 tok)
  - section `Props` L5-9 (~20 tok)
  - section `State` L10-14 (~18 tok)
  - class `WPErrorBoundary` L15-64 (~514 tok)
- `wp-skeleton.tsx` — shimmer (~552 tok)
  - fn `Row` L3-12 (~70 tok)
  - fn `PostsSkeleton` L13-22 (~65 tok)
  - fn `PagesSkeleton` L23-32 (~65 tok)
  - fn `MediaSkeleton` L33-42 (~66 tok)
  - fn `CategoriesSkeleton` L43-52 (~64 tok)
  - fn `TagsSkeleton` L53-62 (~79 tok)
  - fn `UsersSkeleton` L63-76 (~130 tok)

## frontend/components/admin/assets/

- `AssetCard.tsx` — AssetCard (~472 tok)
- `AssetEditModal.tsx` — AssetEditModal — uses useState (~530 tok)
  - section `AssetEditModalProps` L6-11 (~38 tok)
  - fn `AssetEditModal` L12-62 (~466 tok)
- `AssetPreviewModal.tsx` — AssetPreviewModal (~486 tok)
- `AssetRow.tsx` — AssetRow (~486 tok)
- `BatchGenerationModal.tsx` — QUALITY_OPTIONS — uses useState (~845 tok)
  - section `BatchGenerationModalProps` L5-16 (~140 tok)
  - fn `BatchGenerationModal` L17-84 (~691 tok)
- `UploadZone.tsx` — UploadZone (~302 tok)

## frontend/components/admin/pipeline/

- `BatchJobCard.tsx` — BatchJobCard (~895 tok)
  - section `BatchJobCardProps` L6-9 (~16 tok)
  - fn `BatchJobCard` L10-74 (~816 tok)
- `JobCard.tsx` — JobCard (~768 tok)
  - section `JobCardProps` L5-10 (~27 tok)
  - fn `JobCard` L11-69 (~690 tok)
- `JobDetailModal.tsx` — JobDetailModal (~1569 tok)
  - section `JobDetailModalProps` L8-12 (~22 tok)
  - fn `JobDetailModal` L13-120 (~1442 tok)
- `ProviderCard.tsx` — ProviderCard (~852 tok)
  - section `ProviderCardProps` L6-12 (~38 tok)
  - fn `ProviderCard` L13-79 (~754 tok)
- `QueueStatCard.tsx` — QueueStatCard (~438 tok)

## frontend/components/admin/qa/

- `QASkeleton.tsx` — QASkeleton (~186 tok)
- `ReviewDetail.tsx` — FIDELITY_THRESHOLD (~3565 tok)
  - section `ReviewDetailProps` L36-46 (~81 tok)
  - fn `ReviewDetail` L47-267 (~3136 tok)
- `ReviewListItem.tsx` — FIDELITY_THRESHOLD (~732 tok)
  - section `ReviewListItemProps` L7-12 (~31 tok)
  - fn `ReviewListItem` L13-68 (~653 tok)
- `StatCard.tsx` — StatCard (~444 tok)

## frontend/components/collections/

- `CollectionHero.tsx` — CollectionHero — uses useState, useEffect, useCallback (~2528 tok)
  - section `CollectionHeroProps` L8-13 (~39 tok)
  - fn `CollectionHero` L14-254 (~2422 tok)
- `CollectionScene.tsx` — ENVIRONMENT_MAP — renders chart — uses useRef, useState, useCallback (~1578 tok)
  - fn `Loader` L22-35 (~114 tok)
  - fn `FloatingParticles` L36-77 (~267 tok)
  - fn `LuxuryPedestal` L78-102 (~189 tok)
  - section `CollectionSceneProps` L103-107 (~26 tok)
  - fn `CollectionScene` L108-217 (~842 tok)
- `CollectionTabBar.tsx` — CollectionTabBar (~926 tok)
  - fn `CollectionTabBar` L9-16 (~42 tok)
  - fn `CollectionTabBarContent` L17-100 (~815 tok)
- `ProductCard.tsx` — ProductCard — uses useState (~1436 tok)
  - section `ProductCardProps` L7-13 (~44 tok)
  - fn `ProductCard` L14-141 (~1335 tok)
- `ProductGrid.tsx` — ProductGrid — uses useMemo (~842 tok)
  - section `ProductGridProps` L8-13 (~42 tok)
  - fn `ProductGrid` L14-98 (~741 tok)
- `ProductQuickView.tsx` — ProductQuickView — uses useState, useEffect, useCallback (~2662 tok)
  - section `ProductQuickViewProps` L9-14 (~34 tok)
  - fn `ProductQuickView` L15-240 (~2545 tok)

## frontend/components/console/

- `Card.tsx` — The console's `.dsh-card` primitive: bg #111, border #2A2A2A, radius 8, hover lift. (~219 tok)
- `ConsoleShell.tsx` — fetchOrderCount — uses useRouter, useEffect, useQuery (~1487 tok)
  - section `ConsoleShellProps` L13-16 (~18 tok)
  - fn `fetchOrderCount` L17-23 (~61 tok)
  - fn `ConsoleShell` L24-129 (~1288 tok)
- `GrainOverlay.tsx` — Same feTurbulence technique already used in HomePage.tsx / CollectionHero.tsx, (~168 tok)
- `nav-config.ts` — Exports ConsoleNavItem, CONSOLE_NAV_ITEMS (~209 tok)
- `RevenueChart.tsx` — Matches the handoff's `viewBox 0 0 600 200` revenue chart: 3 gridlines, a (~706 tok)
  - section `RevenueChartProps` L1-7 (~33 tok)
  - fn `toPath` L8-24 (~188 tok)
  - fn `RevenueChart` L25-65 (~486 tok)
- `RoundtableDiagram.tsx` — Cycles through the REAL agent roster (not the mockup's fixed 6 fictional (~1603 tok)
  - section `RoundtableDiagramProps` L7-22 (~167 tok)
  - fn `RoundtableDiagram` L23-132 (~1381 tok)
- `Sparkline.tsx` — Matches the handoff's `viewBox 0 0 120 32` KPI-card sparkline exactly. (~273 tok)
- `StatusPill.tsx` — StatusPill (~250 tok)
- `TopBar.tsx` — TopBar — uses useMemo (~618 tok)
  - section `TopBarProps` L7-10 (~13 tok)
  - fn `TopBar` L11-63 (~567 tok)

## frontend/components/console/screens/

- `AgentsListCard.tsx` — Overview's "DevSkyy Agents" card — real `/api/v1/agents` data. The mockup's (~662 tok)
  - fn `AgentsListCard` L12-55 (~521 tok)
- `OverviewKpis.tsx` — TIMEFRAME_DAYS — uses useMemo (~1346 tok)
  - fn `periodDelta` L12-18 (~65 tok)
  - section `OverviewKpisProps` L19-25 (~62 tok)
  - fn `OverviewKpis` L26-97 (~965 tok)
  - fn `KpiHead` L98-107 (~126 tok)

## frontend/components/dashboard/

- `analytics-charts.tsx` — BRAND_COLORS — renders chart — uses useMemo (~3468 tok)
  - section `ProviderPerformanceChartProps` L50-53 (~20 tok)
  - fn `ProviderPerformanceChart` L54-144 (~897 tok)
  - section `CompetitionTrendChartProps` L145-152 (~38 tok)
  - fn `CompetitionTrendChart` L153-217 (~742 tok)
  - section `AgentStatusChartProps` L218-223 (~26 tok)
  - fn `AgentStatusChart` L224-295 (~784 tok)
  - section `PipelineMetricsChartProps` L296-302 (~38 tok)
  - fn `PipelineMetricsChart` L303-357 (~594 tok)
  - fn `generateSampleTrendData` L358-366 (~77 tok)
- `app-sidebar.tsx` — mainNavItems (~2288 tok)
  - fn `AppSidebar` L182-317 (~1485 tok)
- `aurora-analytics.tsx` — BRAND — uses useState, useEffect (~3830 tok)
  - fn `useAnimatedCounter` L32-54 (~234 tok)
  - section `AuroraData` L55-75 (~144 tok)
  - fn `useAuroraData` L76-135 (~674 tok)
  - fn `AuroraAnalytics` L136-354 (~2436 tok)
  - fn `AuroraMetric` L355-385 (~207 tok)
- `conversion-pulse.tsx` — BRAND — renders chart — uses useState, useRef, useEffect, useCallback (~5854 tok)
  - section `Collection` L34-39 (~21 tok)
  - section `ConversionEvent` L40-48 (~42 tok)
  - section `SparkPoint` L49-53 (~19 tok)
  - section `LiveMetrics` L54-103 (~504 tok)
  - fn `formatTime` L104-112 (~52 tok)
  - fn `randomBetween` L113-116 (~35 tok)
  - fn `generateEvent` L117-143 (~195 tok)
  - fn `Sparkline` L144-209 (~474 tok)
  - fn `useAnimatedCounter` L210-238 (~286 tok)
  - fn `MetricChip` L239-287 (~392 tok)
  - fn `EventRow` L288-365 (~721 tok)
  - fn `ConversionPulse` L366-671 (~2911 tok)
- `DashboardSkeleton.tsx` — Loading skeleton for the dashboard page. (~646 tok)
  - fn `DashboardSkeleton` L10-70 (~576 tok)
- `index.ts` — Dashboard components for the admin interface. (~176 tok)
- `personalization-analytics.tsx` — BRAND — uses useCallback, useEffect (~4303 tok)
  - section `IntentSegment` L37-44 (~36 tok)
  - section `PersonalizationMetrics` L45-55 (~75 tok)
  - section `FunnelStage` L56-61 (~23 tok)
  - section `TopProduct` L62-70 (~52 tok)
  - fn `randomInt` L71-74 (~34 tok)
  - fn `generateMetrics` L75-89 (~141 tok)
  - fn `generateIntentSegments` L90-118 (~200 tok)
  - fn `generateFunnel` L119-134 (~240 tok)
  - fn `generateTopProducts` L135-148 (~133 tok)
  - fn `PersonalizationAnalytics` L149-401 (~2845 tok)
  - fn `MetricCard` L402-430 (~229 tok)
  - fn `MiniStat` L431-439 (~76 tok)
- `pulse-analytics.tsx` — PulseAnalytics - Dashboard widget for "The Pulse" social proof engine. (~5627 tok)
  - fn `useAnimatedCounter` L34-63 (~254 tok)
  - section `LiveData` L64-83 (~110 tok)
  - fn `useSimulatedLiveData` L84-168 (~887 tok)
  - fn `PulseAnalytics` L169-494 (~3640 tok)
  - fn `MetricCard` L495-527 (~206 tok)
  - fn `FunnelStep` L528-580 (~380 tok)
- `StatsCard.tsx` — Card title (~702 tok)
  - section `StatsCardProps` L7-26 (~146 tok)
  - fn `StatsCard` L27-84 (~499 tok)

## frontend/components/elite-studio/

- `IntentBadge.tsx` — INTENT_MAP (~566 tok)
  - section `IntentBadgeProps` L6-10 (~21 tok)
  - section `IntentConfig` L11-60 (~356 tok)
  - fn `IntentBadge` L61-76 (~148 tok)
- `OperationCard.tsx` — OperationCard (~1044 tok)
  - section `OperationCardProps` L13-17 (~25 tok)
  - fn `OperationCard` L18-100 (~882 tok)
- `OperationStatusBadge.tsx` — STATUS_CONFIG (~432 tok)
- `StageProgress.tsx` — STAGE_ORDER (~1049 tok)
  - section `StageProgressProps` L5-20 (~101 tok)
  - fn `formatStageName` L21-27 (~44 tok)
  - fn `formatMs` L28-32 (~37 tok)
  - fn `StageProgress` L33-113 (~852 tok)
- `UsageMeter.tsx` — CircleMeter — uses useQuery (~921 tok)
  - section `UsageMeterProps` L8-11 (~15 tok)
  - fn `CircleMeter` L12-69 (~460 tok)
  - fn `UsageMeter` L70-123 (~382 tok)

## frontend/components/marketing/

- `IncentivePopup.tsx` — POPUP_DISMISSED_KEY — renders form — uses useState, useEffect (~2174 tok)
  - fn `IncentivePopup` L11-184 (~2090 tok)

## frontend/components/mascot/

- `MascotBubble.tsx` — COLLECTION_GREETINGS — uses useState, useCallback, useEffect (~3509 tok)
  - section `ChatMessage` L14-61 (~405 tok)
  - fn `getCollectionFromPath` L62-75 (~300 tok)
  - fn `getMascotReply` L76-87 (~157 tok)
  - fn `MascotBubble` L88-315 (~2514 tok)

## frontend/components/navigation/

- `SiteNav.tsx` — NAV_LINKS — uses useState, useEffect (~1085 tok)
  - fn `SiteNav` L14-109 (~988 tok)

## frontend/components/shared/

- `EmptyState.tsx` — Icon component (~456 tok)
- `ErrorState.tsx` — Error title (~437 tok)
- `index.ts` — Shared UI components for consistent loading, error, and empty states. (~89 tok)
- `LoadingState.tsx` — Loading message (~304 tok)

## frontend/components/ui/

- `alert.tsx` — alertVariants (~457 tok)
- `badge.tsx` — badgeVariants (~326 tok)
- `button.tsx` — buttonVariants (~544 tok)
  - section `ButtonProps` L37-58 (~156 tok)
- `card.tsx` — Card (~523 tok)
- `chart.tsx` — THEMES — renders chart — uses useContext, useMemo (~3213 tok)
  - fn `useChart` L27-69 (~486 tok)
  - fn `ChartStyle` L70-334 (~2271 tok)
  - fn `getPayloadConfigFromPayload` L335-381 (~292 tok)
- `dialog.tsx` — Dialog — renders modal (~1100 tok)
- `input.tsx` — Input (~220 tok)
- `label.tsx` — labelVariants (~208 tok)
- `select.tsx` — Select (~1613 tok)
- `separator.tsx` — Separator (~220 tok)
- `sheet.tsx` — Sheet (~1223 tok)
  - section `SheetContentProps` L52-141 (~708 tok)
- `sidebar.tsx` — SIDEBAR_COOKIE_NAME — uses useContext, useState, useCallback, useEffect (~6739 tok)
  - fn `useSidebar` L47-774 (~6385 tok)
- `skeleton.tsx` — Skeleton (~76 tok)
- `switch.tsx` — Switch (~332 tok)
- `table.tsx` — Table — renders table (~822 tok)
- `tabs.tsx` — Tabs (~541 tok)
- `textarea.tsx` — Textarea (~213 tok)
- `tooltip.tsx` — TooltipProvider (~362 tok)

## frontend/components/wordpress/

- `sync-status-toast.tsx` — SyncStatusToast — uses useEffect (~895 tok)
  - section `Toast` L8-14 (~28 tok)
  - fn `SyncStatusToast` L15-91 (~801 tok)

## frontend/contexts/

- `AuthContext.tsx` — initialState — uses useReducer, useEffect, useCallback, useContext (~1205 tok)
  - section `User` L14-20 (~30 tok)
  - section `AuthState` L21-34 (~94 tok)
  - section `AuthContextValue` L35-52 (~99 tok)
  - fn `authReducer` L53-85 (~227 tok)
  - fn `AuthProvider` L86-161 (~645 tok)
  - fn `useAuth` L162-171 (~66 tok)

## frontend/docs/

- `CONTRIB.md` — Contributing to DevSkyy Dashboard (~3034 tok)
- `RUNBOOK.md` — DevSkyy Dashboard Operations Runbook (~3129 tok)

## frontend/e2e/

- `auth.setup.ts` — Authentication Setup (~1383 tok)
- `login-dashboard.spec.ts` — Login & Dashboard E2E Tests (~5330 tok)
  - class `LoginPage` L35-78 (~342 tok)
  - class `DashboardPage` L79-143 (~445 tok)
  - fn `getAuthToken` L144-609 (~4292 tok)

## frontend/e2e/pages/

- `index.ts` — Page Object Models (~3062 tok)
  - class `LoginPage` L15-86 (~652 tok)
  - class `DashboardPage` L87-179 (~755 tok)
  - class `AgentsPage` L180-225 (~363 tok)
  - class `AgentDetailPage` L226-299 (~568 tok)
  - class `ProductsPage` L300-377 (~599 tok)

## frontend/hooks/

- `index.ts` — Custom React hooks for DevSkyy frontend. (~184 tok)
- `use-mobile.tsx` — MOBILE_BREAKPOINT — uses useEffect (~162 tok)
- `useAgents.ts` — Exports useAgents (~326 tok)
- `useAssets.ts` — Exports Collection, AssetType, ViewMode, useAssets, useBatchJob (~3013 tok)
  - section `UseAssetsState` L17-29 (~76 tok)
  - section `UseAssetsReturn` L30-62 (~275 tok)
  - fn `useAssets` L63-317 (~1913 tok)
  - fn `useBatchJob` L318-408 (~635 tok)
- `useAutonomous.ts` — Exports useAutonomous (~864 tok)
  - section `UseAutonomousState` L7-14 (~50 tok)
  - fn `useAutonomous` L15-95 (~747 tok)
- `useDebounce.ts` — Debounces a value by delaying updates until after a specified delay. (~225 tok)
- `useMonitoring.ts` — Exports useMonitoring (~556 tok)
  - section `UseMonitoringState` L7-13 (~49 tok)
  - fn `useMonitoring` L14-55 (~437 tok)
- `useQuery.ts` — Callback on successful fetch (~744 tok)
  - section `UseQueryOptions` L5-19 (~124 tok)
  - section `UseQueryResult` L20-37 (~108 tok)
  - fn `useQuery` L38-102 (~488 tok)
- `useToggle.ts` — Simple toggle hook for boolean state. (~181 tok)
- `useWebSocket.ts` — Zod schemas: WebSocketMessageSchema, RoundTableEventSchema, Pipeline3DEventSchema (~2782 tok)
  - fn `WS_URL` L10-66 (~533 tok)
  - section `WebSocketMessage` L67-75 (~68 tok)
  - section `WebSocketError` L76-85 (~80 tok)
  - fn `validateChannel` L86-90 (~44 tok)
  - fn `sanitizeToken` L91-97 (~78 tok)
  - fn `parseMessage` L98-136 (~339 tok)
  - fn `useWebSocket` L137-322 (~1482 tok)
  - fn `useRoundTableWS` L323-328 (~39 tok)
  - fn `use3DPipelineWS` L329-334 (~39 tok)

## frontend/lib/

- `AGENTS.md` — Next.js Lib — Agent Guide (~1612 tok)
- `api-auth.ts` — Route-handler authentication gate for the DevSkyy dashboard API. (~655 tok)
  - fn `withAuth` L43-54 (~100 tok)
- `api-public-routes.ts` — Dashboard API routes deliberately reachable without a session. (~510 tok)
- `api.ts` — TypeScript resolves `@/lib/api` to this file before the `api/` directory. (~62 tok)
- `auth.d.ts` — NextAuth.js type augmentations for custom JWT fields (~146 tok)
- `auth.ts` — NextAuth.js v4 Configuration (~798 tok)
- `catalog-csv.ts` — Pure CSV transforms for the canonical SkyyRose catalog. (~2228 tok)
  - fn `splitCsvRow` L38-62 (~163 tok)
  - fn `escapeCsvCell` L63-69 (~44 tok)
  - fn `serializeCsvRow` L70-79 (~117 tok)
  - fn `collapseNewlines` L80-83 (~30 tok)
  - section `ApplyPatchResult` L84-102 (~234 tok)
  - fn `applyPatch` L103-197 (~892 tok)
  - fn `parseDataRows` L198-255 (~342 tok)
- `catalog-server.ts` — Exports getEnrichedCollection, getAllEnrichedCollections (~401 tok)
- `catalog-write.ts` — Canonical catalog WRITE path (server-only). (~828 tok)
  - section `UpdateResult` L26-35 (~75 tok)
  - fn `updateProductRow` L36-76 (~427 tok)
- `catalog.ts` — Canonical product catalog reader (server-only). Exposes resolveRepoFile/resolveCsvPath/resetCatalogCache; reuses splitCsvRow from catalog-csv.ts. (~1494 tok)
  - section `CatalogProduct` L17-53 (~312 tok)
  - fn `resolveRepoFile` L54-67 (~119 tok)
  - fn `resolveCsvPath` L68-77 (~82 tok)
  - fn `parseCsv` L78-116 (~371 tok)
  - section `CacheEntry` L117-125 (~78 tok)
  - fn `resetCatalogCache` L126-129 (~18 tok)
  - fn `loadFresh` L130-140 (~116 tok)
  - fn `getCatalog` L141-145 (~42 tok)
  - fn `getProduct` L146-150 (~64 tok)
  - fn `getCollectionProducts` L151-155 (~55 tok)
  - fn `getCollectionSlugs` L156-159 (~34 tok)
- `collections.ts` — Exports CollectionSlug, CollectionProduct, CollectionScene, CollectionConfig + 4 more (~1475 tok)
  - section `CollectionProduct` L3-12 (~48 tok)
  - section `CollectionScene` L13-26 (~128 tok)
  - section `CollectionConfig` L27-157 (~1176 tok)
  - fn `getCollection` L158-161 (~36 tok)
  - fn `getAllCollections` L162-165 (~28 tok)
  - fn `getAllCollectionSlugs` L166-169 (~34 tok)
- `elite-studio-client.ts` — ENVIRONMENT (~2467 tok)
  - fn `API_URL` L8-74 (~571 tok)
  - section `CreateOperationRequest` L75-80 (~33 tok)
  - section `ListOperationsFilters` L81-91 (~105 tok)
  - fn `getAuthToken` L92-96 (~40 tok)
  - fn `getAuthHeaders` L97-108 (~85 tok)
  - fn `fetchWithTimeout` L109-123 (~113 tok)
  - fn `handleResponse` L124-137 (~161 tok)
  - fn `handleVoid` L138-255 (~1292 tok)
- `fonts.ts` — Exports playfair, cormorant, spaceMono (~311 tok)
- `renders-pure.ts` — PURE render-review helpers — no `node:fs`, no `server-only`, no `@/` aliases. (~1878 tok)
  - section `ReviewEntry` L17-25 (~48 tok)
  - section `RenderVerdict` L26-31 (~26 tok)
  - section `VerdictRecord` L32-42 (~115 tok)
  - fn `isSafeSegment` L43-56 (~192 tok)
  - fn `stableStringify` L57-60 (~25 tok)
  - fn `pyDump` L61-83 (~274 tok)
  - fn `pyEscapeString` L84-118 (~347 tok)
  - fn `parseVerdicts` L119-185 (~711 tok)
- `renders.ts` — OAI render review data layer (server-only). (~2116 tok)
  - section `RenderRecord` L42-52 (~85 tok)
  - section `RenderQueue` L53-63 (~54 tok)
  - fn `rendersDir` L64-67 (~23 tok)
  - fn `reviewStatePath` L68-72 (~54 tok)
  - fn `resolveRenderImage` L73-108 (~361 tok)
  - fn `loadReviewState` L109-128 (~191 tok)
  - fn `saveReviewEntry` L129-156 (~241 tok)
  - fn `loadVerdicts` L157-178 (~174 tok)
  - fn `listRenderFiles` L179-203 (~196 tok)
  - fn `getRenderQueue` L204-241 (~310 tok)
- `require-admin-session.ts` — Server-side session read for /admin/* Server Component pages. (~464 tok)
- `sot-images.ts` — Read-only SOT (source-of-truth) product-imagery reader (server-only). (~513 tok)
  - section `SotImageSet` L17-24 (~42 tok)
  - section `SotCache` L25-31 (~37 tok)
  - fn `load` L32-57 (~232 tok)
  - fn `getSotImagesForSku` L58-61 (~32 tok)
- `utils.ts` — Exports cn (~48 tok)

## frontend/lib/animations/

- `luxury-transitions.ts` — SkyyRose Luxury Animation Library (~2052 tok)
  - fn `parallaxScroll` L195-392 (~962 tok)
  - fn `createSpring` L393-404 (~59 tok)
  - fn `createEase` L405-414 (~50 tok)

## frontend/lib/api/

- `client.ts` — Exports getAuthToken, getAuthHeaders, fetchWithTimeout, handleResponse, handleArrayResponse (~713 tok)
  - fn `getAuthToken` L6-10 (~44 tok)
  - fn `getAuthHeaders` L11-22 (~94 tok)
  - fn `fetchWithTimeout` L23-41 (~133 tok)
  - fn `handleResponse` L42-67 (~196 tok)
  - fn `handleArrayResponse` L68-96 (~216 tok)
- `config.ts` — Exports API_URL (~81 tok)
- `errors.ts` — Exports ApiError (~266 tok)
- `index.ts` — Exports api (~386 tok)
- `schemas.ts` — Provider Schemas (~6127 tok)
- `types.ts` — Inferred Types (~2416 tok)
  - section `CompetitionRequest` L37-42 (~35 tok)
  - section `TextTo3DRequest` L43-48 (~36 tok)
  - section `ImageTo3DRequest` L49-54 (~37 tok)
  - section `AssetFilters` L55-62 (~67 tok)
  - section `AssetUpdateRequest` L63-70 (~41 tok)
  - section `BatchGenerationRequest` L71-76 (~40 tok)
  - section `QAReviewRequest` L77-81 (~27 tok)
  - section `RegenerateRequest` L82-107 (~357 tok)
  - section `CatalogSearchRequest` L108-113 (~30 tok)
  - section `ContextDevExtractionRequest` L114-135 (~315 tok)
  - section `BrandAssetUploadInput` L136-148 (~80 tok)
  - section `BulkIngestionRequest` L149-155 (~48 tok)
  - section `BrandAssetListFilters` L156-168 (~151 tok)
  - section `AssetIngestOptions` L169-187 (~310 tok)
  - section `CompetitorCreateRequest` L188-195 (~52 tok)
  - section `CompetitorAssetListFilters` L196-207 (~115 tok)
  - section `DynamicPricingRequest` L208-213 (~55 tok)

## frontend/lib/api/endpoints/

- `agents.ts` — Exports agents (~148 tok)
- `assets.ts` — Exports assets (~1679 tok)
- `autonomous.ts` — Exports autonomous (~487 tok)
- `batch.ts` — Exports batch (~812 tok)
- `brand-assets.ts` — GET /brand-assets/training-readiness — status, category breakdown, recommendations. (~1234 tok)
- `catalog.ts` — Semantic search across all catalog SKUs. (~930 tok)
- `competitors.ts` — GET /competitors — list all tracked competitor brands. Restricted to strategy/marketing/admin roles. (~1153 tok)
  - fn `assertValidId` L23-96 (~976 tok)
- `context-dev.ts` — POST /context-dev/extractions — authenticated, fact-checked web extraction. (~298 tok)
- `health.ts` — Exports health (~222 tok)
- `monitoring.ts` — Exports monitoring (~430 tok)
- `pipeline.ts` — Exports pipeline3d (~936 tok)
- `pricing.ts` — POST /commerce/pricing/optimize — ML + market-intelligence price optimization for a set of SKUs. (~241 tok)
- `qa.ts` — Exports qa (~606 tok)
- `round-table.ts` — Exports roundTable (~662 tok)
- `settings.ts` — Settings API client for the dashboard. (~251 tok)
- `social-media.ts` — Social Media Pipeline API Endpoints (~1423 tok)
  - section `SocialPost` L12-26 (~114 tok)
  - section `PlatformAnalytics` L27-37 (~56 tok)
  - section `SocialAnalytics` L38-44 (~46 tok)
  - section `Campaign` L45-56 (~65 tok)
  - fn `generatePost` L57-88 (~237 tok)
  - fn `schedulePost` L89-115 (~181 tok)
  - fn `getPostQueue` L116-130 (~109 tok)
  - fn `getAnalytics` L131-145 (~116 tok)
  - fn `generateCampaign` L146-175 (~217 tok)
  - fn `publishPost` L176-205 (~202 tok)
- `tasks.ts` — Tasks API client for the dashboard. (~553 tok)
  - fn `fetchTasks` L11-23 (~170 tok)
  - fn `fetchTask` L24-31 (~77 tok)
  - fn `submitTask` L32-45 (~128 tok)
  - fn `cancelTask` L46-54 (~90 tok)
- `training.ts` — Exports training (~404 tok)

## frontend/lib/autonomous/

- `round-table-auto-trigger.ts` — Autonomous Round Table Auto-Trigger System (~1434 tok)
  - section `TaskRequest` L10-15 (~46 tok)
  - section `TaskResult` L16-23 (~44 tok)
  - class `RoundTableAutoTrigger` L24-162 (~1259 tok)
- `self-healing-service.ts` — Self-Healing Service (~1828 tok)
  - section `HealthCheck` L9-15 (~32 tok)
  - section `CircuitBreaker` L16-21 (~24 tok)
  - class `SelfHealingService` L22-247 (~1710 tok)

## frontend/lib/console/

- `agents.ts` — Real-agent display helpers for the Hub/Agents/Overview screens. (~553 tok)
  - fn `agentStatusColor` L13-19 (~80 tok)
  - fn `agentInitials` L20-36 (~191 tok)
  - fn `agentGradient` L37-42 (~60 tok)
  - fn `activeAgentCount` L43-46 (~43 tok)
- `brand.ts` — Operator Console brand tokens — collection accents and status colors. (~364 tok)
- `format.ts` — "$1.24M" style — used where the mockup's KPI values are compact. (~233 tok)
- `orders.ts` — Order aggregation for the Operator Console — derives every revenue/status (~2566 tok)
  - section `OrderStatusView` L13-19 (~45 tok)
  - fn `mapOrderStatus` L20-42 (~269 tok)
  - fn `orderTotal` L43-47 (~50 tok)
  - fn `orderCustomerName` L48-56 (~118 tok)
  - section `OrderLineItem` L57-63 (~32 tok)
  - fn `orderLineItems` L64-68 (~70 tok)
  - fn `orderPieceSummary` L69-78 (~128 tok)
  - fn `orderCollection` L79-87 (~88 tok)
  - fn `buildSkuToCollectionMap` L88-91 (~45 tok)
  - section `RevenueKpis` L92-97 (~27 tok)
  - fn `computeKpis` L98-105 (~115 tok)
  - section `CollectionRevenue` L106-112 (~48 tok)
  - fn `revenueByCollection` L113-129 (~259 tok)
  - section `CustomerAggregate` L130-134 (~23 tok)
  - fn `orderDate` L135-148 (~165 tok)
  - fn `filterByTimeframe` L149-159 (~140 tok)
  - fn `dailySeries` L160-176 (~201 tok)
  - fn `latestOrderDate` L177-187 (~149 tok)
  - fn `weeklyRevenueSeries` L188-210 (~256 tok)
  - fn `aggregateByCustomer` L211-222 (~174 tok)

## frontend/lib/meshy/

- `client.ts` — Meshy API Client (~2218 tok)
  - section `MeshyTextTo3DRequest` L18-34 (~94 tok)
  - section `MeshyImageTo3DRequest` L35-48 (~73 tok)
  - section `MeshyModelUrls` L49-55 (~29 tok)
  - section `MeshyTaskResponse` L56-77 (~172 tok)
  - fn `mockTaskId` L78-81 (~33 tok)
  - fn `createMockTask` L82-96 (~86 tok)
  - fn `createMockCompletedTask` L97-122 (~217 tok)
  - fn `meshyFetch` L123-268 (~1151 tok)
  - fn `toJob3D` L269-298 (~216 tok)
- `config.ts` — Meshy API Configuration (~469 tok)

## frontend/lib/pipeline-config/

- `index.ts` — Unified Pipeline Configuration - Master Aggregator (~855 tok)
  - section `PipelineModule` L27-46 (~111 tok)
  - fn `buildResponse` L47-74 (~216 tok)
  - fn `getAllPipelineStatuses` L75-82 (~76 tok)
  - fn `getAllPipelineStatusesDryRun` L83-91 (~90 tok)
  - fn `getPipelineStatus` L92-96 (~63 tok)
- `types.ts` — Shared types for the unified pipeline configuration system. (~292 tok)
- `validators.ts` — Environment variable validators for pipeline configuration. (~619 tok)
  - fn `validateEnvVars` L14-55 (~294 tok)
  - fn `validateApiKey` L56-72 (~104 tok)
  - fn `getKnownPrefix` L73-79 (~51 tok)
  - fn `validateUrl` L80-91 (~59 tok)

## frontend/lib/pipeline-config/pipelines/

- `huggingface.ts` — HuggingFace Pipeline Configuration (~429 tok)
- `imagery.ts` — Imagery Pipeline Configuration (~708 tok)
  - fn `getServiceStatus` L21-32 (~95 tok)
  - fn `getConnectionStatus` L33-67 (~303 tok)
  - fn `getDryRunData` L68-82 (~131 tok)
- `llm-round-table.ts` — LLM Round Table Pipeline Configuration (~637 tok)
  - section `LlmProviderDef` L11-33 (~191 tok)
  - fn `providerStatus` L34-45 (~98 tok)
  - fn `getConnectionStatus` L46-62 (~153 tok)
  - fn `getDryRunData` L63-78 (~101 tok)
- `payments.ts` — Payments Pipeline Configuration (~602 tok)
  - fn `getConnectionStatus` L22-55 (~318 tok)
  - fn `getDryRunData` L56-69 (~114 tok)
- `social-media.ts` — Social Media Pipeline Configuration (~569 tok)
  - section `PlatformDef` L11-35 (~165 tok)
  - fn `platformStatus` L36-46 (~84 tok)
  - fn `getConnectionStatus` L47-63 (~142 tok)
  - fn `getDryRunData` L64-79 (~97 tok)
- `three-d.ts` — 3D Pipeline Configuration (~590 tok)
  - fn `getServiceStatus` L19-30 (~95 tok)
  - fn `getConnectionStatus` L31-52 (~187 tok)
  - fn `getDryRunData` L53-67 (~129 tok)
- `virtual-tryon.ts` — Virtual Try-On Pipeline Configuration (~390 tok)
- `wordpress.ts` — WordPress / WooCommerce Pipeline Configuration (~782 tok)
  - fn `getConnectionStatus` L20-69 (~447 tok)
  - fn `getDryRunData` L70-83 (~114 tok)

## frontend/lib/providers/

- `query-provider.tsx` — QueryProvider — uses useState (~165 tok)

## frontend/lib/queue/

- `queues.ts` — BullMQ Queue Definitions (~984 tok)
  - fn `parseRedisUrl` L12-33 (~153 tok)
  - section `JobData` L34-101 (~474 tok)
  - fn `addJob` L102-118 (~99 tok)
  - fn `getQueueStats` L119-131 (~106 tok)
  - fn `getAllQueueStats` L132-139 (~71 tok)
- `worker.ts` — BullMQ Worker Process (~1460 tok)
  - fn `parseRedisUrl` L15-37 (~238 tok)
  - fn `handleGenerate3D` L38-58 (~191 tok)
  - fn `handleProcessImage` L59-77 (~183 tok)
  - fn `handleSyncWordPress` L78-99 (~199 tok)
  - fn `handleSendEmail` L100-126 (~245 tok)
  - fn `startWorkers` L127-167 (~308 tok)

## frontend/lib/social-media/

- `config.ts` — Social Media Platform Configuration (~957 tok)
  - section `PlatformConnection` L11-19 (~49 tok)
  - section `PlatformEnvConfig` L20-55 (~237 tok)
  - fn `hasLlmKey` L56-62 (~43 tok)
  - fn `checkPlatform` L63-97 (~270 tok)
  - fn `getPlatformConnections` L98-104 (~49 tok)
  - fn `getPlatformConnection` L105-122 (~133 tok)
  - fn `getPlatformToken` L123-132 (~91 tok)

## frontend/lib/stores/

- `cart-store.ts` — Exports CartItem, useCartStore (~619 tok)
  - section `CartItem` L4-12 (~43 tok)
  - section `CartState` L13-82 (~553 tok)

## frontend/lib/tripo/

- `client.ts` — Tripo 3D API Client (~2481 tok)
  - section `TripoTextTo3DRequest` L18-22 (~25 tok)
  - section `TripoImageTo3DRequest` L23-35 (~60 tok)
  - section `TripoTaskOutput` L36-40 (~24 tok)
  - section `TripoTaskData` L41-49 (~51 tok)
  - section `TripoApiResponse` L50-54 (~24 tok)
  - section `TripoUploadData` L55-62 (~70 tok)
  - fn `mockTaskId` L63-66 (~33 tok)
  - fn `createMockTaskData` L67-80 (~98 tok)
  - fn `createMockCompletedTaskData` L81-102 (~198 tok)
  - fn `tripoFetch` L103-146 (~311 tok)
  - fn `tripoUpload` L147-299 (~1222 tok)
  - fn `toJob3D` L300-327 (~207 tok)
- `config.ts` — Tripo 3D API Configuration (~473 tok)

## frontend/lib/vercel/

- `deployment-manager.ts` — Vercel Deployment Manager (~4402 tok)
  - section `VercelConfig` L6-11 (~24 tok)
  - section `Deployment` L12-28 (~101 tok)
  - section `DeploymentEvent` L29-37 (~33 tok)
  - section `Project` L38-57 (~100 tok)
  - section `EnvironmentVariable` L58-65 (~50 tok)
  - class `VercelDeploymentManager` L66-535 (~3954 tok)
  - fn `getVercelDeploymentManager` L536-552 (~110 tok)

## frontend/lib/wordpress/

- `agent-client.ts` — Exports AgentMessage, AgentStatus, useWordPressAgent (~785 tok)
  - section `AgentMessage` L5-15 (~88 tok)
  - fn `useWordPressAgent` L16-99 (~677 tok)
- `menu-manager.ts` — WordPress Menu Manager (~1565 tok)
  - section `MenuItem` L8-23 (~99 tok)
  - section `Menu` L24-32 (~35 tok)
  - class `WordPressMenuManager` L33-202 (~1344 tok)
  - fn `getWordPressMenuManager` L203-208 (~46 tok)
- `operations-manager.ts` — WordPress Operations Manager (~4989 tok)
  - section `WordPressManagerConfig` L8-16 (~89 tok)
  - section `WordPressPost` L17-37 (~189 tok)
  - section `WordPressPage` L38-50 (~96 tok)
  - section `WordPressCategory` L51-59 (~42 tok)
  - section `WordPressTag` L60-67 (~36 tok)
  - section `WordPressMedia` L68-77 (~45 tok)
  - section `WordPressUser` L78-90 (~64 tok)
  - section `WordPressComment` L91-103 (~86 tok)
  - section `WordPressSettings` L104-126 (~173 tok)
  - class `WordPressOperationsManager` L127-592 (~4080 tok)
  - fn `getWordPressOperationsManager` L593-598 (~52 tok)
- `proxy-client.ts` — WordPress Proxy Client (~197 tok)
- `sync-service.ts` — WordPress Sync Service (~1751 tok)
  - section `RoundTableResult` L8-43 (~206 tok)
  - section `WordPressPost` L44-52 (~48 tok)
  - class `WordPressSyncService` L53-200 (~1429 tok)
  - fn `getWordPressSyncService` L201-204 (~30 tok)
- `types.ts` — WordPress REST API Response Types (~511 tok)
  - section `WPRenderedField` L8-12 (~21 tok)
  - section `WPPostResponse` L13-28 (~99 tok)
  - section `WPPageResponse` L29-41 (~75 tok)
  - section `WPCategoryResponse` L42-50 (~40 tok)
  - section `WPTagResponse` L51-58 (~34 tok)
  - section `WPMediaResponse` L59-68 (~65 tok)
  - section `WPUserResponse` L69-78 (~50 tok)
  - section `WPMenuResponse` L79-86 (~34 tok)
  - section `WPConnectionStatus` L87-96 (~44 tok)

## frontend/lib/wp/

- `auth-policy.ts` — resolveAuthTier(path): 'public'\|'wc'\|'wp-app', throws on unmatched path (~366 tok)
- `client.ts` — server-only typed client: wpRequest/wpRequestRaw + 13 typed methods (~3025 tok)
  - fn `requireEnv` L32-39 (~50 tok)
  - fn `buildUrl` L40-45 (~58 tok)
  - fn `authHeader` L46-59 (~157 tok)
  - class `WpRequestError` L60-77 (~186 tok)
  - fn `wpRequestRaw` L78-107 (~297 tok)
  - fn `wpRequest` L108-118 (~117 tok)
  - section `WcCategoryRef` L119-124 (~24 tok)
  - section `WcStoreProduct` L125-132 (~40 tok)
  - section `WcOrder` L133-138 (~25 tok)
  - section `WcCustomer` L139-148 (~68 tok)
  - section `SkyyRoseCollection` L149-157 (~52 tok)
  - section `GetProductsResult` L158-162 (~25 tok)
  - section `BatchProductOps` L163-170 (~61 tok)
  - fn `getCollections` L171-175 (~66 tok)
  - fn `getProducts` L176-189 (~204 tok)
  - section `WcAdminProduct` L190-205 (~159 tok)
  - fn `getAdminProducts` L206-210 (~89 tok)
  - fn `getStock` L211-214 (~39 tok)
  - fn `get3DProducts` L215-218 (~49 tok)
  - fn `getOrders` L219-228 (~144 tok)
  - fn `getCustomers` L229-238 (~103 tok)
  - fn `updateOrder` L239-248 (~137 tok)
  - fn `updateProduct` L249-255 (~73 tok)
  - fn `batchProducts` L256-259 (~50 tok)
  - fn `getSettings` L260-263 (~38 tok)
  - fn `updateSettings` L264-267 (~61 tok)
  - fn `pushNarrative` L268-271 (~57 tok)
  - fn `getAnalyticsSummary` L272-275 (~35 tok)
  - fn `agentsOpenState` L276-280 (~84 tok)
- `path-safety.ts` — Framework-free path guards for the WP client. Kept out of client.ts (which is (~355 tok)
- `signature.ts` — computeWebhookSignature/verifyWebhookSignature, HMAC-SHA256 via node:crypto (~314 tok)
- `throttle.ts` — RequestThrottle: 2 req/s pacing + Retry-After-aware backoff (~363 tok)

## frontend/lib/wp/__tests__/

- `auth-policy.test.ts` — vitest: tier routing per prefix + throw-on-unknown (~423 tok)
- `path-safety.test.ts` (~420 tok)
- `signature.test.ts` — vitest: accept-on-match, reject on tampered body/secret/null/malformed (~360 tok)
- `throttle.test.ts` — vitest: fake-timer pacing delay + Retry-After/backoff math (~397 tok)

## frontend/public/models/

- `.gitkeep` — 3D Models Directory (~26 tok)

## frontend/scripts/

- `deploy.ts` — Automated Vercel Deployment Script (~2446 tok)
  - section `DeploymentOptions` L14-22 (~45 tok)
  - class `VercelDeployer` L23-305 (~2114 tok)
  - fn `main` L306-336 (~208 tok)
- `link-vercel-project.sh` — Link Vercel Project to "devskyy" (~361 tok)

## frontend/tests/

- `api-auth-coverage.test.ts` — Fail-closed coverage gate for dashboard API authentication. (~1289 tok)
  - fn `findRouteFiles` L27-40 (~122 tok)
  - fn `routePath` L41-50 (~118 tok)
  - fn `stripComments` L51-55 (~58 tok)
  - fn `exportedHandlers` L56-121 (~672 tok)
- `context-dev-api.test.ts` — Declares fetchMock (~450 tok)
- `launch-desk-tools.test.ts` — Declares completeBrief (~572 tok)

## frontend/tests/e2e/

- `settings-page.spec.ts` — Declares saveButton (~2338 tok)
- `smoke.spec.ts` — API routes: GET (1 endpoints) (~507 tok)

## frontend/types/

- `model-viewer.d.ts` — Type declarations for @google/model-viewer web component (~310 tok)

## grpc_server/

- `__init__.py` (~0 tok)
- `product_service.py` — ProductServicer: GetProduct, ListProducts, CreateProduct, UpdateProductPrice + 1 more (~3740 tok)
  - class `ProductServicer` L56-269 (~2306 tok)
  - class `_SimpleRequest` L270-282 (~112 tok)
  - fn `serve` L283-352 (~799 tok)

## grpc_server/generated/

- `__init__.py` (~0 tok)

## grpc_server/proto/

- `product.proto` — Proto: messages: ProductResponse, GetProductRequest, ListProductsRequest, services: access, calls, ProductService (~391 tok)

## hf-spaces/virtual-tryon/

- `app.py` — SQLAlchemy model (~2946 tok)
  - fn `encode_image_to_base64` L50-59 (~82 tok)
  - fn `fashn_api_request` L60-95 (~313 tok)
  - fn `poll_prediction` L96-115 (~169 tok)
  - fn `virtual_tryon_async` L116-176 (~514 tok)
  - fn `virtual_tryon` L177-212 (~296 tok)
  - fn `create_app` L213-328 (~1176 tok)
- `README.md` — Project documentation (~224 tok)
- `requirements.txt` — Python dependencies (~109 tok)

## imagery/

- `__init__.py` — DevSkyy Imagery Module. (~882 tok)
  - fn `get_sdxl_pipeline` L54-60 (~65 tok)
  - fn `get_luxury_photography` L61-67 (~70 tok)
  - fn `get_lora_trainer` L68-74 (~64 tok)
  - fn `get_premium_3d_pipeline` L75-122 (~344 tok)
- `headless_renderer.py` — Headless 3D Model Renderer. (~5129 tok)
  - fn `_configure_opengl_platform` L28-76 (~438 tok)
  - class `LightingPreset` L77-85 (~51 tok)
  - class `CameraAngle` L86-110 (~183 tok)
  - class `RenderConfig` L111-123 (~131 tok)
  - class `RenderResult` L124-132 (~62 tok)
  - class `HeadlessRenderer` L133-517 (~3835 tok)
  - fn `render_glb_to_images` L518-554 (~276 tok)
- `image_processor.py` — imagery/image_processor.py (~4333 tok)
  - class `ImageFormat` L44-53 (~42 tok)
  - class `ImageMetadata` L54-65 (~61 tok)
  - class `ImageProcessor` L66-326 (~2286 tok)
  - class `ImagePreprocessor` L327-399 (~607 tok)
  - class `BackgroundRemover` L400-522 (~1087 tok)
- `lora_trainer.py` — SkyyRose LoRA Trainer. (~9362 tok)
  - class `TrainingConfig` L24-52 (~227 tok)
  - class `TrainingImage` L53-63 (~53 tok)
  - class `TrainingDataset` L64-96 (~302 tok)
  - class `SkyyRoseLoRATrainer` L97-939 (~8648 tok)
- `lora_version_tracker.py` — class: create_version_database, initialize, create_version, get_version + 1 more (~5161 tok)
  - class `ProductContribution` L47-63 (~110 tok)
  - class `LoRAVersion` L64-82 (~160 tok)
  - class `VersionDiff` L83-148 (~624 tok)
  - fn `create_version_database` L149-171 (~184 tok)
  - class `LoRAVersionTracker` L172-559 (~3794 tok)
- `luxury_photography.py` — Luxury Product Photography Generation. (~5463 tok)
  - class `ShotType` L24-38 (~106 tok)
  - class `LightingPreset` L39-50 (~97 tok)
  - class `ColorGrade` L51-60 (~62 tok)
  - class `GarmentSpecs` L61-72 (~74 tok)
  - class `PhotoSuite` L73-103 (~319 tok)
  - class `LuxuryProductPhotography` L104-509 (~4664 tok)
- `model_fidelity.py` — imagery/model_fidelity.py (~7638 tok)
  - class `FidelityCategory` L75-83 (~69 tok)
  - class `FidelityGrade` L84-94 (~72 tok)
  - class `FidelityMetrics` L95-151 (~537 tok)
  - class `GeometryMetrics` L152-162 (~76 tok)
  - class `TextureMetrics` L163-171 (~62 tok)
  - class `MaterialMetrics` L172-179 (~52 tok)
  - class `FidelityReport` L180-223 (~402 tok)
  - class `ModelFidelityValidator` L224-741 (~5562 tok)
  - fn `validate_model_fidelity` L742-772 (~273 tok)
- `premium_3d_pipeline.py` — Premium 3D Asset Pipeline. (~7099 tok)
  - class `FabricType` L30-44 (~86 tok)
  - class `TextureMap` L45-57 (~73 tok)
  - class `MeshQuality` L58-67 (~57 tok)
  - class `MaterialSet` L68-81 (~104 tok)
  - class `LODLevel` L82-91 (~47 tok)
  - class `FinalModel` L92-103 (~94 tok)
  - class `Wonder3DReconstructor` L104-205 (~926 tok)
  - class `BlenderProcessor` L206-473 (~2543 tok)
  - class `FabricMaterialGenerator` L474-613 (~1532 tok)
  - class `Premium3DAssetPipeline` L614-767 (~1458 tok)
- `product_training_dataset.py` — class: fetch_products_from_woocommerce, download_product_images, evaluate_image_quality, filter_by_quality (~4663 tok)
  - class `ProductTrainingSource` L48-66 (~158 tok)
  - class `ProductTrainingDataset` L67-84 (~180 tok)
  - fn `fetch_products_from_woocommerce` L85-206 (~1097 tok)
  - fn `_extract_collection` L207-233 (~224 tok)
  - fn `_extract_garment_type` L234-268 (~295 tok)
  - fn `download_product_images` L269-338 (~731 tok)
  - fn `evaluate_image_quality` L339-376 (~315 tok)
  - fn `filter_by_quality` L377-425 (~453 tok)
  - fn `prepare_training_dataset` L426-493 (~600 tok)
  - fn `_generate_product_caption` L494-527 (~275 tok)
- `prompt_guard.py` — Prompt guard — grounds every SDXL/FLUX prompt in verified product specs. (~2500 tok)
  - class `SpecsValidator` L63-92 (~352 tok)
  - class `GroundedPromptBuilder` L93-216 (~1570 tok)
- `quality_gate.py` — Asset Quality Gate. (~4275 tok)
  - class `GateStatus` L23-32 (~53 tok)
  - class `QualityGateResult` L33-52 (~222 tok)
  - class `AssetFidelityError` L53-68 (~116 tok)
  - class `AssetQualityGate` L69-400 (~3441 tok)
  - fn `validate_before_upload` L401-440 (~320 tok)
- `sdxl_pipeline.py` — SDXL Image Generation Pipeline. (~5686 tok)
  - class `ControlNetMode` L27-34 (~38 tok)
  - class `GenerationQuality` L35-44 (~75 tok)
  - class `GenerationConfig` L45-69 (~218 tok)
  - class `GenerationResult` L70-81 (~92 tok)
  - class `SDXLPipeline` L82-459 (~4066 tok)
  - class `SkyyRosePromptBuilder` L460-552 (~1041 tok)
- `skyyrose_lora_generator.py` — SkyyRose LoRA Image Generator. (~5271 tok)
  - class `SkyyRoseCollection` L31-38 (~47 tok)
  - class `GarmentType` L39-55 (~94 tok)
  - class `LoRAGenerationConfig` L56-72 (~134 tok)
  - class `LoRAGenerationResult` L73-123 (~636 tok)
  - class `SkyyRoseLoRAGenerator` L124-494 (~3824 tok)
  - fn `generate_skyyrose_image` L495-543 (~350 tok)
- `training_progress_reporter.py` — class: to_dict, from_dict, start, update + 3 more (~3824 tok)
  - class `TrainingProgress` L42-95 (~362 tok)
  - class `TrainingStatus` L96-119 (~176 tok)
  - class `ProgressReporter` L120-398 (~2843 tok)
  - fn `create_progress_reporter` L399-422 (~179 tok)
- `virtual_photoshoot.py` — imagery/virtual_photoshoot.py (~5766 tok)
  - class `LightingPreset` L40-51 (~126 tok)
  - class `BackgroundPreset` L52-63 (~127 tok)
  - class `CameraAngle` L64-78 (~88 tok)
  - class `CameraConfig` L79-89 (~93 tok)
  - class `LightConfig` L90-99 (~68 tok)
  - class `PhotoshootConfig` L100-151 (~510 tok)
  - class `PhotoshootResult` L152-168 (~146 tok)
  - class `VirtualPhotoshootPipeline` L169-641 (~4377 tok)
- `visual_comparison.py` — Visual Comparison Engine for Asset Fidelity. (~5709 tok)
  - class `ComparisonConfidence` L64-71 (~42 tok)
  - class `ComparisonResult` L72-106 (~423 tok)
  - class `ComparisonWeights` L107-130 (~242 tok)
  - class `VisualComparisonEngine` L131-528 (~4280 tok)
  - fn `compare_images` L529-562 (~269 tok)

## integrations/

- `__init__.py` — SkyyRose Integration Modules (~189 tok)
- `cloudflare_r2_manager.py` — cloudflare_r2_manager.py (~3558 tok)
  - class `CloudflareR2Manager` L12-355 (~3090 tok)
  - fn `setup_r2_bucket` L356-405 (~411 tok)
- `context_dev.py` — Server-side Context.dev structured web extraction. (~881 tok)
  - class `ContextDevConfigurationError` L18-21 (~38 tok)
  - fn `extract_structured_data` L22-83 (~711 tok)
- `openai_agents_api.py` — Raw-httpx client for OpenAI Agents API beta (/v1/agents/sessions, OpenAI-Beta: agents=v1); dry-run-by-default paid create_session + STOP-AND-SHOW manifest, SSE terminal-state classifier, free check_access probe (~4288 tok)
- `wordpress_client.py` — Pydantic: ProductData (50 fields) (~6631 tok)
  - class `APIType` L40-46 (~56 tok)
  - class `SkyyRoseCollection` L47-99 (~444 tok)
  - class `ProductData` L100-120 (~163 tok)
  - class `VariationData` L121-130 (~63 tok)
  - class `VariableProductData` L131-139 (~100 tok)
  - class `MediaUploadResult` L140-149 (~46 tok)
  - class `WebhookPayload` L150-160 (~68 tok)
  - class `WordPressClient` L161-724 (~5370 tok)
- `wordpress_com_client.py` — WordPress.com REST API Client. (~3594 tok)
  - class `WordPressConfig` L16-38 (~290 tok)
  - class `WooCommerceConfig` L39-46 (~92 tok)
  - class `WordPressProduct` L47-69 (~161 tok)
  - class `WordPressComClient` L70-360 (~2602 tok)
  - fn `create_wordpress_client` L361-400 (~356 tok)
- `wordpress_product_sync.py` — WordPress Product Sync for SkyyRose Collections. (~1959 tok)
  - class `SkyyRoseProduct` L18-35 (~269 tok)
  - class `ProductSyncResult` L36-44 (~52 tok)
  - class `WordPressProductSync` L45-213 (~1550 tok)

## knowledge-base/

- `README.md` — Project documentation (~2572 tok)

## knowledge-base/decisions/

- `0001-v2-locked-decisions.md` — V2 Locked Decisions — Page-Level and Architectural (~1783 tok)
- `0002-cost-cap-hybrid-policy.md` — Cost-Cap Hybrid Policy (~1762 tok)
- `0003-imagery-as-launch-blocker.md` — ADR 0003 — Imagery as Launch Blocker (~1615 tok)

## knowledge-base/lessons/

- `anti-patterns.md` — Anti-Patterns: Confirmed Failure Modes (~5719 tok)

## knowledge-base/prompts/

- `INDEX.yaml` — model: { default: gemini-3 } (~3380 tok)
- `README.md` — Project documentation (~1393 tok)

## knowledge-base/prompts/eval/

- `.gitkeep` — Per-prompt eval datasets land here as <id>.jsonl. (~23 tok)

## knowledge-base/prompts/templates/

- `structured-output-schema.md` — Template: Structured-Output Schema Block (~478 tok)

## knowledge-base/references/

- `trusted-set.md` — Trusted Reference Set — Canonical Sources for V2 Development (~2699 tok)

## knowledge-base/seed/

- `from-claude-mem.md` — Seed Index: claude-mem Observations (`~/.claude-mem/claude-mem.db`) (~2991 tok)
- `from-gsd.md` — Seed Index: GSD Artifacts (`.planning/`) (~2520 tok)
- `from-interview.md` — Interview Capture — Corey, 2026-05-03 (~3014 tok)
- `from-openwolf.md` — Seed Index: OpenWolf System (`.wolf/`) (~2328 tok)
- `from-serena.md` — Seed Index: Serena Memories (`.serena/memories/`) (~2633 tok)
- `press-features.md` — Press Features — SkyyRose Collection (~2252 tok)
- `timeline.md` — SkyyRose Timeline — Brand Canon (~1040 tok)

## llm/

- `__init__.py` — Declares calling (~1098 tok)
- `ab_testing.py` — ExperimentStatus: mean, conversion_rate, variance, std_error + 7 more (~7956 tok)
  - class `ExperimentStatus` L37-46 (~58 tok)
  - class `MetricType` L47-56 (~89 tok)
  - class `WinnerStatus` L57-73 (~123 tok)
  - class `Variant` L74-85 (~74 tok)
  - class `MetricResult` L86-127 (~338 tok)
  - class `StatisticalResult` L128-147 (~144 tok)
  - class `Experiment` L148-184 (~344 tok)
  - class `ExperimentResult` L185-201 (~173 tok)
  - class `StatisticalCalculator` L202-307 (~938 tok)
  - class `ABTestingEngine` L308-828 (~5227 tok)
  - fn `create_ab_engine` L829-857 (~205 tok)
- `adaptive_learning.py` — Adaptive learning for provider profiling and optimization. (~4389 tok)
  - class `PerformanceTrend` L24-33 (~64 tok)
  - class `ProviderProfile` L34-129 (~985 tok)
  - class `RecommendationResult` L130-145 (~136 tok)
  - class `AdaptiveLearningEngine` L146-435 (~3017 tok)
- `base.py` — Pydantic: CallerInfo (67 fields) (~4439 tok)
  - class `MessageRole` L46-54 (~46 tok)
  - class `ModelProvider` L55-67 (~73 tok)
  - class `CallerType` L68-84 (~151 tok)
  - class `CallerInfo` L85-115 (~305 tok)
  - class `ContainerInfo` L116-153 (~320 tok)
  - class `Message` L154-193 (~332 tok)
  - class `ToolCall` L194-245 (~427 tok)
  - class `CompletionResponse` L246-301 (~476 tok)
  - class `StreamChunk` L302-320 (~139 tok)
  - class `BaseLLMClient` L321-533 (~1914 tok)
- `classification.py` — Pydantic: ClassificationExample (58 fields) (~5825 tok)
  - class `ClassificationType` L42-51 (~58 tok)
  - class `SentimentLabel` L52-65 (~99 tok)
  - class `ClassificationExample` L66-75 (~98 tok)
  - class `ClassificationResult` L76-97 (~229 tok)
  - class `ClassificationConfig` L98-125 (~252 tok)
  - class `ClassificationPrompts` L126-187 (~485 tok)
  - class `GroqFastClassifier` L188-599 (~3855 tok)
  - fn `get_classifier` L600-607 (~69 tok)
  - fn `classify_intent` L608-616 (~83 tok)
  - fn `classify_category` L617-625 (~87 tok)
  - fn `analyze_sentiment` L626-630 (~53 tok)
  - fn `detect_language` L631-659 (~214 tok)
- `CLAUDE.md` — llm/ — Unified LLM Client Library (~231 tok)
- `creative_judge.py` — Pydantic: CriterionEval (34 fields) (~11616 tok)
  - class `CriterionEval` L43-61 (~233 tok)
  - class `PillarEval` L62-70 (~84 tok)
  - class `JudgeOutput` L71-153 (~990 tok)
  - class `Verdict` L154-164 (~114 tok)
  - class `CriterionScore` L165-196 (~325 tok)
  - class `PillarScore` L197-221 (~230 tok)
  - class `JudgeVerdict` L222-520 (~3414 tok)
  - class `CreativeJudge` L521-1064 (~5414 tok)
  - fn `judge_creative_output` L1065-1090 (~221 tok)
  - fn `compare_creative_outputs` L1091-1120 (~269 tok)
- `evaluation_metrics.py` — Advanced ML-based evaluation metrics for LLM Round Table. (~3472 tok)
  - class `AdvancedMetrics` L26-377 (~3282 tok)
- `exceptions.py` — LLMError: to_dict (~836 tok)
  - class `LLMError` L11-37 (~215 tok)
  - class `AuthenticationError` L38-43 (~28 tok)
  - class `RateLimitError` L44-56 (~85 tok)
  - class `QuotaExceededError` L57-62 (~27 tok)
  - class `InvalidRequestError` L63-68 (~26 tok)
  - class `ModelNotFoundError` L69-74 (~30 tok)
  - class `ContentFilterError` L75-80 (~31 tok)
  - class `ContextLengthError` L81-95 (~115 tok)
  - class `TimeoutError` L96-101 (~24 tok)
  - class `ServiceUnavailableError` L102-107 (~32 tok)
  - class `StreamError` L108-113 (~23 tok)
  - class `ToolCallError` L114-141 (~170 tok)
- `model_ids.py` — Canonical LLM model IDs — single source of truth for model strings. (~2419 tok)
- `round_table_metrics.py` — Prometheus metrics for Round Table monitoring. (~3154 tok)
  - fn `record_competition` L230-248 (~154 tok)
  - fn `record_provider_result` L249-276 (~241 tok)
  - fn `record_scoring_components` L277-287 (~108 tok)
  - fn `record_ml_scoring` L288-301 (~133 tok)
  - fn `record_tool_call` L302-319 (~142 tok)
  - fn `record_ab_test` L320-345 (~223 tok)
  - fn `record_tokens` L346-357 (~119 tok)
  - fn `record_database_operation` L358-368 (~111 tok)
  - fn `set_system_info` L369-384 (~129 tok)
- `round_table.py` — LLMProvider: total, total_score, to_dict, initialize + 3 more (~17655 tok)
  - class `LLMProvider` L54-64 (~61 tok)
  - class `CompetitionStatus` L65-81 (~126 tok)
  - class `LLMResponse` L82-95 (~96 tok)
  - class `ResponseScores` L96-132 (~398 tok)
  - class `RoundTableEntry` L133-146 (~88 tok)
  - class `ABTestResult` L147-165 (~157 tok)
  - class `RoundTableResult` L166-215 (~566 tok)
  - class `RoundTableDatabase` L216-441 (~2396 tok)
  - class `ResponseScorer` L442-917 (~4554 tok)
  - class `LRUHistory` L918-999 (~705 tok)
  - class `LLMRoundTable` L1000-1566 (~6204 tok)
  - fn `create_round_table` L1567-1577 (~98 tok)
  - fn `_auto_register_providers` L1578-1601 (~303 tok)
  - fn `_create_provider_generator` L1602-1719 (~1263 tok)
  - fn `_estimate_cost` L1720-1749 (~262 tok)
- `router.py` — class: is_available, record_success, record_failure, get_status + 2 more (~6038 tok)
  - class `ProviderConfig` L48-137 (~774 tok)
  - class `RoutingStrategy` L138-152 (~144 tok)
  - class `CircuitBreaker` L153-268 (~1242 tok)
  - class `LLMRouter` L269-605 (~3400 tok)
  - fn `get_router` L606-613 (~56 tok)
  - fn `complete` L614-632 (~122 tok)
- `statistics.py` — Statistical analysis for Round Table competitions. (~3297 tok)
  - class `ABTestResult` L25-60 (~369 tok)
  - class `StatisticalAnalyzer` L61-344 (~2759 tok)
- `task_classifier.py` — Pydantic: TaskClassificationResult (28 fields) (~4860 tok)
  - class `TaskCategory` L39-58 (~150 tok)
  - class `PromptTechnique` L59-121 (~782 tok)
  - class `TaskClassificationResult` L122-140 (~225 tok)
  - class `TaskClassifierConfig` L141-193 (~630 tok)
  - class `TaskClassifier` L194-430 (~2426 tok)
  - fn `get_classifier` L431-438 (~68 tok)
  - fn `classify_task` L439-446 (~76 tok)
  - fn `classify_messages` L447-476 (~225 tok)
- `tournament.py` — ResponseScore: score_coherence, score_task_completion, score_brand_alignment, score_accuracy_with_judge + 2 more (~4320 tok)
  - class `ResponseScore` L40-67 (~195 tok)
  - class `TournamentResult` L68-78 (~92 tok)
  - class `ResponseScorer` L79-260 (~1688 tok)
  - class `LLMTournament` L261-481 (~2083 tok)
- `unified_llm_client.py` — Pydantic: LLMRequest (50 fields) (~6038 tok)
  - class `ExecutionMode` L77-89 (~128 tok)
  - class `LLMRequest` L90-137 (~479 tok)
  - class `LLMResponse` L138-174 (~411 tok)
  - class `UnifiedLLMClient` L175-544 (~4076 tok)
  - fn `get_client` L545-552 (~65 tok)
  - fn `complete` L553-585 (~231 tok)
- `verification.py` — Pydantic: VerificationConfig (30 fields) (~3543 tok)
  - class `VerificationDecision` L35-42 (~78 tok)
  - class `IssueLevel` L43-51 (~75 tok)
  - class `CodeIssue` L52-62 (~83 tok)
  - class `VerificationResult` L63-73 (~92 tok)
  - class `VerificationConfig` L74-134 (~570 tok)
  - class `LLMVerificationEngine` L135-345 (~2411 tok)

## llm/providers/

- `__init__.py` (~260 tok)
- `anthropic.py` — AnthropicClient: complete, stream (~2925 tok)
  - class `AnthropicClient` L40-313 (~2726 tok)
- `cohere.py` — CohereClient: complete, stream (~1824 tok)
  - class `CohereClient` L30-211 (~1656 tok)
- `deepseek.py` — DeepSeekClient: complete, stream, get_model_info (~2436 tok)
  - class `DeepSeekClient` L27-256 (~2264 tok)
- `google.py` — GoogleClient: complete, stream (~1861 tok)
  - class `GoogleClient` L30-210 (~1690 tok)
- `groq.py` — GroqClient: complete, stream (~1448 tok)
  - class `GroqClient` L30-173 (~1281 tok)
- `litellm_provider.py` — LiteLLMClient: get_model_string, complete, stream (~2487 tok)
  - class `LiteLLMClient` L50-269 (~2102 tok)
- `mistral.py` — MistralClient: complete, stream (~1413 tok)
  - class `MistralClient` L30-169 (~1250 tok)
- `openai.py` — OpenAIClient: complete, stream (~1534 tok)
  - class `OpenAIClient` L30-179 (~1362 tok)
- `replicate.py` — ReplicateClient: generate_image, upscale_image, remove_background, caption_image + 3 more (~5434 tok)
  - fn `_validate_remote_url` L50-83 (~322 tok)
  - class `ConfirmationRequired` L84-103 (~201 tok)
  - class `ReplicateClient` L104-551 (~4557 tok)
- `stability.py` — StabilityClient: generate, image_to_image, inpaint (~5314 tok)
  - class `StabilityClient` L38-630 (~5050 tok)
- `vertex_imagen.py` — VertexImagenClient: generate, generate_fast, edit, upscale + 1 more (~4680 tok)
  - class `VertexImagenClient` L47-501 (~4286 tok)

## mcp_tools/

- `__init__.py` — DevSkyy MCP Tools Package. (~91 tok)
- `api_client.py` — Shared API client utilities: _make_api_request, _handle_api_error, _format_response. (~2289 tok)
  - fn `_make_api_request` L22-171 (~1360 tok)
  - fn `_handle_api_error` L172-194 (~269 tok)
  - fn `_format_response` L195-239 (~503 tok)
- `http_mount.py` — Mount the DevSkyy MCP server as an authenticated HTTP endpoint on the FastAPI app. (~1895 tok)
  - class `BearerAuthMiddleware` L50-108 (~638 tok)
  - fn `_allowed_hosts` L109-126 (~175 tok)
  - fn `build_mcp_app` L127-149 (~306 tok)
  - fn `mcp_session_manager` L150-157 (~65 tok)
  - fn `tool_count` L158-168 (~144 tok)
- `security.py` — secure_tool() decorator for MCP tool handlers. (~1765 tok)
  - fn `secure_tool` L23-163 (~1579 tok)
- `server.py` — FastMCP server instance, configuration constants, and logger. (~646 tok)
- `types.py` — Shared enums and base input model for all MCP tools. (~355 tok)

## mcp_tools/external_clients/

- `__init__.py` (~332 tok)
- `context7.py` — Context7Client: resolve_library, get_docs, search_docs, get_code_examples (~1627 tok)
  - class `Context7Client` L27-203 (~1458 tok)
- `playwright.py` — PlaywrightMCPClient: navigate, screenshot, click, fill + 6 more (~3037 tok)
  - class `PlaywrightMCPClient` L29-383 (~2855 tok)
- `serena.py` — SerenaClient: analyze_file, analyze_directory, find_issues, suggest_refactoring + 5 more (~2261 tok)
  - class `SerenaClient` L28-294 (~2090 tok)
- `server_manager.py` — Pydantic: MCPToolResult (34 fields) (~3052 tok)
  - class `MCPServerStatus` L30-39 (~57 tok)
  - class `MCPServerConfig` L40-51 (~81 tok)
  - class `MCPToolResult` L52-60 (~113 tok)
  - class `MCPServerManager` L61-315 (~2589 tok)

## mcp_tools/tools/

- `__init__.py` — Side-effect imports: each module registers its tools via @mcp.tool(). (~989 tok)
  - fn `_resolve_modules` L65-97 (~344 tok)
- `advanced.py` — Advanced tools: multi-agent workflow orchestration. (~1329 tok)
  - class `MultiAgentWorkflowInput` L13-66 (~549 tok)
  - fn `multi_agent_workflow` L67-138 (~694 tok)
- `claude_sdk.py` — Claude Agent SDK MCP tools: research, email triage, spreadsheet ops, dashboard. (~3154 tok)
  - class `ResearchInput` L15-42 (~228 tok)
  - fn `research_topic` L43-82 (~370 tok)
  - class `EmailTriageInput` L83-102 (~180 tok)
  - fn `email_triage` L103-139 (~348 tok)
  - class `GenerateSpreadsheetInput` L140-165 (~210 tok)
  - fn `generate_spreadsheet` L166-196 (~292 tok)
  - class `AnalyzeSpreadsheetInput` L197-220 (~192 tok)
  - fn `analyze_spreadsheet` L221-251 (~269 tok)
  - class `DashboardActionInput` L252-284 (~280 tok)
  - fn `dashboard_action` L285-321 (~324 tok)
  - class `DashboardHealthInput` L322-342 (~146 tok)
  - fn `dashboard_health` L343-360 (~185 tok)
- `cli_anything.py` — CLI-Anything harness tools: agent-native Blender and GIMP control. (~2244 tok)
  - fn `_run_cli` L23-68 (~398 tok)
  - class `BlenderEditInput` L69-112 (~462 tok)
  - fn `blender_edit` L113-146 (~394 tok)
  - class `GimpEditInput` L147-191 (~449 tok)
  - fn `gimp_edit` L192-219 (~359 tok)
- `ecommerce.py` — E-commerce tools: manage_products, dynamic_pricing. (~2077 tok)
  - class `ProductManagementInput` L13-33 (~181 tok)
  - class `DynamicPricingInput` L34-86 (~483 tok)
  - fn `manage_products` L87-168 (~792 tok)
  - fn `dynamic_pricing` L169-224 (~529 tok)
- `elite_studio.py` — Elite Studio MCP tools — thin surface over skyyrose/elite_studio/cli.py. (~5834 tok)
  - fn `_is_sku_complete` L73-89 (~196 tok)
  - class `RenderInput` L90-108 (~210 tok)
  - class `BatchInput` L109-122 (~146 tok)
  - class `ValidateDossierInput` L123-126 (~29 tok)
  - class `CostEstimateInput` L127-146 (~171 tok)
  - class `StatusInput` L147-162 (~147 tok)
  - fn `_resolve_skus` L163-197 (~350 tok)
  - fn `es_render` L198-298 (~1188 tok)
  - fn `es_batch` L299-403 (~1041 tok)
  - fn `es_validate_dossier` L404-458 (~639 tok)
  - fn `es_cost_estimate` L459-505 (~485 tok)
  - fn `es_status` L506-547 (~496 tok)
- `external_mcp.py` — context7_resolve_library, context7_get_docs, context7_search_docs, context7_get_code_examples + 7 more (~5338 tok)
  - fn `_ok` L32-39 (~79 tok)
  - fn `_err` L40-59 (~167 tok)
  - fn `context7_resolve_library` L60-94 (~333 tok)
  - fn `context7_get_docs` L95-129 (~313 tok)
  - fn `context7_search_docs` L130-162 (~284 tok)
  - fn `context7_get_code_examples` L163-202 (~369 tok)
  - fn `playwright_navigate` L203-232 (~241 tok)
  - fn `playwright_screenshot` L233-274 (~390 tok)
  - fn `playwright_click` L275-301 (~211 tok)
  - fn `playwright_fill` L302-329 (~229 tok)
  - fn `playwright_evaluate` L330-358 (~248 tok)
  - fn `playwright_get_page_content` L359-383 (~214 tok)
  - fn `playwright_test_3d_viewer` L384-417 (~350 tok)
  - fn `playwright_test_wordpress_page` L418-452 (~318 tok)
  - fn `serena_analyze_file` L453-482 (~245 tok)
  - fn `serena_find_issues` L483-514 (~249 tok)
  - fn `serena_validate_security` L515-544 (~264 tok)
  - fn `serena_full_project_audit` L545-577 (~320 tok)
  - fn `serena_check_code_style` L578-599 (~195 tok)
- `infrastructure.py` — Infrastructure & system tools: scan_code, fix_code, self_healing. (~2995 tok)
  - class `ScanCodeInput` L24-43 (~182 tok)
  - class `FixCodeInput` L44-62 (~200 tok)
  - class `SelfHealingInput` L63-98 (~320 tok)
  - fn `scan_code` L99-199 (~881 tok)
  - fn `fix_code` L200-293 (~868 tok)
  - fn `self_healing` L294-331 (~376 tok)
- `lora_generation.py` — LoRA product image generation tools: generate, pose transfer, upscale, background removal, caption. (~7527 tok)
  - class `LoRAProductGenerationInput` L24-82 (~470 tok)
  - class `LoRAPoseTransferInput` L83-112 (~268 tok)
  - class `LoRAUpscaleInput` L113-140 (~231 tok)
  - class `LoRABackgroundRemovalInput` L141-169 (~264 tok)
  - class `ProductCaptionInput` L170-237 (~716 tok)
  - fn `_get_lora_generator` L238-281 (~397 tok)
  - fn `lora_generate` L282-396 (~1076 tok)
  - fn `lora_pose_transfer` L397-496 (~963 tok)
  - fn `lora_upscale` L497-597 (~940 tok)
  - fn `lora_clean_background` L598-709 (~990 tok)
  - fn `product_caption` L710-801 (~963 tok)
- `lora_training.py` — LoRA training tools: train, dataset preview, version info, product history. (~2238 tok)
  - class `TrainLoRAInput` L15-41 (~222 tok)
  - class `LoRADatasetPreviewInput` L42-57 (~125 tok)
  - class `LoRAVersionInfoInput` L58-68 (~73 tok)
  - class `LoRAProductHistoryInput` L69-97 (~200 tok)
  - fn `train_lora_from_products` L98-149 (~506 tok)
  - fn `lora_dataset_preview` L150-192 (~377 tok)
  - fn `lora_version_info` L193-226 (~334 tok)
  - fn `lora_product_history` L227-256 (~295 tok)
- `marketing.py` — Marketing campaign tool. (~1160 tok)
  - class `MarketingCampaignInput` L13-61 (~484 tok)
  - fn `marketing_campaign` L62-119 (~595 tok)
- `ml.py` — Machine learning prediction tool. (~1123 tok)
  - class `MLPredictionInput` L13-60 (~472 tok)
  - fn `ml_prediction` L61-113 (~564 tok)
- `monitoring.py` — System monitoring tool. (~785 tok)
  - class `MonitoringInput` L11-38 (~241 tok)
  - fn `system_monitoring` L39-97 (~474 tok)
- `oai_render.py` — OAI gpt-image-2 product-render tools — plan (free) + generate (paid, gated). (~2400 tok)
  - class `OAIRenderPlanInput` L25-58 (~376 tok)
  - class `OAIRenderGenerateInput` L59-68 (~109 tok)
  - fn `_validate_styles` L69-77 (~111 tok)
  - fn `_plan` L78-126 (~411 tok)
  - fn `oai_render_plan` L127-159 (~354 tok)
  - fn `oai_render_generate` L160-224 (~784 tok)
- `orchestration.py` — Orchestration MCP tools — ported from mcp_servers/agent_bridge_server.py. (~3946 tok)
  - class `_ResponseFormat` L31-35 (~22 tok)
  - fn `_fmt` L36-88 (~475 tok)
  - fn `_err` L89-100 (~104 tok)
  - class `_BaseInput` L101-108 (~81 tok)
  - class `_RoundTableInput` L109-114 (~84 tok)
  - class `_RouterSelectInput` L115-120 (~90 tok)
  - class `_LearningReportInput` L121-130 (~120 tok)
  - class `_OperationsDeployInput` L131-146 (~169 tok)
  - fn `orchestration_round_table` L147-203 (~572 tok)
  - fn `orchestration_router_select` L204-265 (~658 tok)
  - fn `orchestration_learning_report` L266-341 (~742 tok)
  - fn `operations_deploy` L342-393 (~526 tok)
- `rag.py` — RAG (Retrieval-Augmented Generation) MCP tools. (~5226 tok)
  - class `RAGQueryInput` L46-53 (~104 tok)
  - class `RAGIngestInput` L54-64 (~104 tok)
  - class `RAGContextInput` L65-74 (~125 tok)
  - class `RAGQueryRewriteInput` L75-92 (~194 tok)
  - fn `_error_json` L93-97 (~52 tok)
  - fn `_fmt` L98-157 (~684 tok)
  - fn `_get_pipeline` L158-199 (~399 tok)
  - fn `_get_rewriter` L200-233 (~265 tok)
  - fn `rag_query` L234-286 (~495 tok)
  - fn `rag_ingest` L287-343 (~573 tok)
  - fn `rag_get_context` L344-387 (~431 tok)
  - fn `rag_query_rewrite` L388-451 (~693 tok)
  - fn `rag_list_sources` L452-487 (~328 tok)
  - fn `rag_stats` L488-515 (~280 tok)
- `resources.py` — Resource tools: list_agents, health_check. (~4513 tok)
  - fn `list_agents` L27-70 (~490 tok)
  - fn `health_check` L71-180 (~1061 tok)
  - fn `fleet_health` L181-213 (~336 tok)
  - fn `fraud_assess` L214-270 (~676 tok)
  - fn `retention_assess` L271-328 (~635 tok)
  - fn `demand_forecast` L329-376 (~540 tok)
  - fn `recommend` L377-421 (~552 tok)
- `threed.py` — 3D asset generation tools: text-to-3D, image-to-3D. (~2678 tok)
  - class `ThreeDGenerationInput` L16-45 (~272 tok)
  - class `ThreeDImageInput` L46-134 (~932 tok)
  - fn `generate_3d_from_description` L135-229 (~968 tok)
  - fn `generate_3d_from_image` L230-259 (~373 tok)
- `virtual_tryon.py` — Virtual try-on tools: single, batch, AI model generation, status. (~4368 tok)
  - fn `_resolve_garment_url` L23-37 (~154 tok)
  - class `VirtualTryOnInput` L38-94 (~674 tok)
  - class `BatchVirtualTryOnInput` L95-139 (~492 tok)
  - class `AIModelGenerationInput` L140-204 (~612 tok)
  - fn `virtual_tryon` L205-286 (~970 tok)
  - fn `batch_virtual_tryon` L287-347 (~672 tok)
  - fn `generate_ai_model` L348-387 (~382 tok)
  - fn `virtual_tryon_status` L388-403 (~178 tok)
- `wc_client.py` — WooCommerce MCP tools — 429-safe client exposed as 5 tools. (~9488 tok)
  - fn `_extract_error` L28-56 (~302 tok)
  - class `GetProductsInput` L57-63 (~81 tok)
  - class `GetProductInput` L64-67 (~23 tok)
  - class `GetOrdersInput` L68-75 (~80 tok)
  - class `UpdateProductInput` L76-84 (~94 tok)
  - class `SmoketestInput` L85-93 (~79 tok)
  - class `UpdateStockInput` L94-108 (~181 tok)
  - class `UpdateOrderStatusInput` L109-124 (~170 tok)
  - class `SearchCustomersInput` L125-133 (~104 tok)
  - class `ValidateCouponInput` L134-142 (~96 tok)
  - class `GetStoreSettingsInput` L143-146 (~27 tok)
  - class `ListOrdersInput` L147-181 (~349 tok)
  - fn `wc_get_products` L182-240 (~509 tok)
  - fn `wc_get_product` L241-274 (~338 tok)
  - fn `wc_get_orders` L275-324 (~447 tok)
  - fn `wc_update_product` L325-373 (~464 tok)
  - fn `wc_smoketest` L374-436 (~657 tok)
  - fn `wc_update_stock` L437-527 (~891 tok)
  - fn `wc_update_order_status` L528-620 (~884 tok)
  - fn `wc_search_customers` L621-696 (~687 tok)
  - fn `wc_validate_coupon` L697-842 (~1454 tok)
  - fn `wc_get_store_settings` L843-903 (~549 tok)
  - fn `wc_list_orders` L904-981 (~770 tok)
- `wordpress.py` — WordPress theme generation tool. (~1252 tok)
  - class `WordPressThemeInput` L13-77 (~616 tok)
  - fn `generate_wordpress_theme` L78-128 (~554 tok)
- `wp_deploy.py` — WordPress theme deploy MCP tools — atomic release ritual exposed as 4 tools. (~7195 tok)
  - fn `_redact_secrets` L66-109 (~526 tok)
  - fn `_read_current_versions` L110-123 (~140 tok)
  - fn `_bump_semver` L124-138 (~167 tok)
  - fn `_write_version` L139-154 (~187 tok)
  - fn `_git_dirty` L155-166 (~84 tok)
  - fn `_run_subprocess` L167-201 (~294 tok)
  - class `BumpVersionInput` L202-212 (~103 tok)
  - class `VerifyLiveInput` L213-243 (~338 tok)
  - class `ReleaseInput` L244-268 (~243 tok)
  - class `BackfillNextgenInput` L269-301 (~253 tok)
  - fn `wp_bump_version` L302-390 (~1114 tok)
  - fn `_verify_live_impl` L391-445 (~482 tok)
  - fn `wp_verify_live` L446-483 (~384 tok)
  - fn `wp_release` L484-613 (~1643 tok)
  - fn `wp_backfill_nextgen` L614-653 (~450 tok)

## models/

- `skyyrose-lora-v3-info.json` (~413 tok)
- `skyyrose-lora-v4-info.json` (~410 tok)
- `skyyrose-lora-v4-trigger-map.json` (~1384 tok)

## models/skyyrose-lora-v3-tests/

- `blackrose_sherpa.webp` (~4343 tok)
- `lovehurts_windbreaker.webp` (~9775 tok)
- `signature_beanie.webp` (~13683 tok)

## models/training-runs/phase2-exact-replica/

- `progress.json` (~275 tok)
- `status.json` (~275 tok)
- `training_config.json` (~462 tok)

## monitoring/

- `__init__.py` — monitoring package (~6 tok)
- `ab_comparison.py` — from: record, report (~1963 tok)
  - class `ProviderStats` L35-48 (~93 tok)
  - class `ABReport` L49-60 (~100 tok)
  - class `ABComparisonTracker` L61-166 (~1152 tok)
  - fn `_compute_stats` L167-194 (~229 tok)
  - fn `_percentile` L195-209 (~140 tok)
- `elite_studio_metrics.py` — record_job_completed, record_stage_duration, record_cost, record_qc_score + 3 more (~1544 tok)
  - fn `_make_counter` L31-42 (~99 tok)
  - fn `_make_histogram` L43-56 (~117 tok)
  - fn `_make_gauge` L57-119 (~538 tok)
  - fn `record_job_completed` L120-127 (~84 tok)
  - fn `record_stage_duration` L128-135 (~92 tok)
  - fn `record_cost` L136-143 (~92 tok)
  - fn `record_qc_score` L144-151 (~72 tok)
  - fn `set_active_jobs` L152-159 (~71 tok)
  - fn `set_queue_depth` L160-167 (~71 tok)
  - fn `record_retry` L168-174 (~79 tok)
- `embedding_observer.py` — Embedding-gate observability + PSI drift — ALERT-ONLY, pure-read. (~2333 tok)
  - fn `_bucket_index` L36-52 (~165 tok)
  - fn `_proportions` L53-63 (~110 tok)
  - class `PSIReference` L64-85 (~263 tok)
  - fn `psi` L86-102 (~188 tok)
  - class `GateAlert` L103-111 (~40 tok)
  - class `GateReport` L112-118 (~68 tok)
  - class `EmbeddingObserver` L119-191 (~782 tok)
  - fn `format_gate_report` L192-224 (~323 tok)
- `fleet_observer.py` — Fleet-health observability consumer. (~2464 tok)
  - class `AlertSeverity` L25-33 (~53 tok)
  - class `FleetAlert` L34-43 (~54 tok)
  - class `HealthReport` L44-52 (~54 tok)
  - fn `_p95` L53-59 (~70 tok)
  - fn `_max_consecutive_failures` L60-71 (~108 tok)
  - class `FleetObserver` L72-215 (~1526 tok)
  - fn `format_health_report` L216-245 (~314 tok)
- `metrics_server.py` — MetricsHandler: do_GET, serve_metrics, serve_health, serve_status + 3 more (~2398 tok)
  - class `MetricsHandler` L48-208 (~1663 tok)
  - fn `start_metrics_server` L209-232 (~224 tok)
  - fn `start_metrics_server_background` L233-254 (~154 tok)
- `prometheus_metrics.py` — record_tool_call, record_error, record_rate_limit_hit, record_llm_tokens + 12 more (~3550 tok)
  - fn `record_tool_call` L195-224 (~242 tok)
  - fn `record_error` L225-246 (~161 tok)
  - fn `record_rate_limit_hit` L247-257 (~98 tok)
  - fn `record_llm_tokens` L258-279 (~186 tok)
  - fn `record_3d_generation` L280-289 (~65 tok)
  - fn `record_security_event` L290-299 (~73 tok)
  - fn `record_validation_failure` L300-313 (~106 tok)
  - fn `set_tool_availability` L314-324 (~86 tok)
  - fn `update_queue_depth` L325-335 (~72 tok)
  - fn `set_server_info` L336-353 (~120 tok)
  - fn `update_server_uptime` L354-363 (~60 tok)
  - fn `get_metrics_text` L364-378 (~113 tok)
  - fn `monitored_tool` L379-403 (~175 tok)
  - fn `initialize_metrics` L404-460 (~476 tok)
- `README.md` — Project documentation (~2858 tok)
- `stream_processor.py` — class: to_dict, start, stop, process_event (~4800 tok)
  - class `AnalyticsState` L55-87 (~366 tok)
  - class `StreamProcessor` L88-430 (~3942 tok)

## monitoring/grafana/

- `devskyy_dashboard.json` (~3824 tok)
- `elite_studio_dashboard.json` (~2027 tok)

## orchestration/

- `__init__.py` (~2400 tok)
  - fn `__getattr__` L135-153 (~239 tok)
- `agent_counter.py` — count_active_agents, attempt_count, count_active_agents_sync (~1961 tok)
  - fn `count_active_agents` L39-144 (~1097 tok)
  - fn `count_active_agents_sync` L145-208 (~572 tok)
- `asset_pipeline.py` — Pydantic: ProgressEvent (75 fields) (~21780 tok)
  - class `ProductCategory` L133-140 (~74 tok)
  - class `PipelineStage` L141-151 (~78 tok)
  - class `Primary3DGenerator` L152-160 (~87 tok)
  - class `PipelineConfig` L161-263 (~1429 tok)
  - class `ProgressEventType` L264-277 (~118 tok)
  - class `ProgressEvent` L278-295 (~146 tok)
  - class `RetryQueueItem` L296-313 (~134 tok)
  - class `BatchResult` L314-333 (~188 tok)
  - class `Asset3DResult` L334-345 (~84 tok)
  - class `TryOnAssetResult` L346-356 (~70 tok)
  - class `WordPressAssetResult` L357-365 (~58 tok)
  - class `AssetPipelineResult` L366-393 (~262 tok)
  - class `ProductAssetPipeline` L394-2002 (~17858 tok)
- `auto_ingestion.py` — AutoDocumentIngestion: ingest_all, auto_ingest_documents (~2930 tok)
  - class `AutoDocumentIngestion` L36-298 (~2443 tok)
  - fn `auto_ingest_documents` L299-332 (~245 tok)
- `brand_context.py` — Collection: get_system_prompt, get_compact_prompt, inject, get_product_context + 1 more (~6955 tok)
  - class `Collection` L42-177 (~1397 tok)
  - class `BrandContextInjector` L178-409 (~2293 tok)
  - class `CatalogSummary` L410-423 (~101 tok)
  - class `CatalogContext` L424-454 (~335 tok)
  - fn `_canonical_catalog_path` L455-480 (~225 tok)
  - fn `_catalog_mtime_ns` L481-488 (~63 tok)
  - fn `load_catalog_context` L489-548 (~609 tok)
  - fn `_read_rows` L549-562 (~146 tok)
  - fn `_format_summary` L563-592 (~397 tok)
  - fn `_cached_catalog_context` L593-598 (~54 tok)
  - fn `_cached_digest` L599-619 (~278 tok)
  - fn `compile_catalog_digest` L620-629 (~121 tok)
  - fn `get_brand_context` L630-665 (~389 tok)
  - fn `get_brand_system_prompt` L666-670 (~53 tok)
  - fn `inject_brand_context` L671-696 (~198 tok)
- `brand_integration.py` — API router (~2684 tok)
  - fn `wire_brand_learning` L38-95 (~496 tok)
  - fn `_import_feedback_tracker_signals` L96-167 (~685 tok)
  - fn `get_brand_context_with_learning` L168-247 (~790 tok)
  - fn `_medium_confidence` L248-259 (~104 tok)
  - fn `on_startup` L260-279 (~156 tok)
  - fn `on_cycle_check` L280-304 (~184 tok)
- `brand_learning.py` — SignalType: store_signal, get_signals, count_signals, store_insight (~15518 tok)
  - class `SignalType` L47-60 (~131 tok)
  - class `InsightCategory` L61-73 (~114 tok)
  - class `InsightConfidence` L74-82 (~86 tok)
  - class `LoopPhase` L83-99 (~119 tok)
  - class `BrandSignal` L100-117 (~159 tok)
  - class `BrandInsight` L118-134 (~189 tok)
  - class `BrandAdaptation` L135-147 (~126 tok)
  - class `LoopState` L148-165 (~148 tok)
  - class `BrandMemory` L166-537 (~3912 tok)
  - class `PatternExtractor` L538-787 (~3222 tok)
  - class `BrandAdaptor` L788-948 (~1652 tok)
  - class `BrandLearningLoop` L949-1379 (~4889 tok)
  - fn `create_brand_learning_loop` L1380-1434 (~407 tok)
- `catalog_retriever.py` — CatalogRetriever — semantic retrieval over the SkyyRose canonical catalog. (~7607 tok)
  - class `CatalogMatch` L52-63 (~66 tok)
  - class `CatalogAnswer` L64-87 (~270 tok)
  - fn `_extract_citations` L88-103 (~158 tok)
  - class `CatalogRetriever` L104-672 (~6657 tok)
- `docs_context.py` — Lazy RAG context provider for the devskyy_docs vector collection. (~826 tok)
  - fn `_lock` L28-34 (~41 tok)
  - fn `_ensure_ready` L35-61 (~302 tok)
  - fn `get_docs_context` L62-87 (~245 tok)
- `document_ingestion.py` — ", "**/.git/**"] (~4999 tok)
  - class `DocumentType` L50-59 (~47 tok)
  - class `ChunkMetadata` L60-83 (~206 tok)
  - class `IngestionConfig` L84-104 (~196 tok)
  - class `IngestionResult` L105-131 (~252 tok)
  - class `TextChunker` L132-231 (~976 tok)
  - class `DocumentLoader` L232-280 (~462 tok)
  - class `DocumentIngestionPipeline` L281-526 (~2444 tok)
  - fn `ingest_docs_directory` L527-532 (~76 tok)
- `embedding_engine.py` — View: get, put (~7345 tok)
  - class `EmbeddingCache` L37-120 (~767 tok)
  - fn `get_embedding_cache` L121-135 (~165 tok)
  - class `EmbeddingProvider` L136-144 (~56 tok)
  - class `EmbeddingConfig` L145-183 (~434 tok)
  - class `BaseEmbeddingEngine` L184-230 (~398 tok)
  - class `SentenceTransformerEngine` L231-312 (~846 tok)
  - class `OpenAIEmbeddingEngine` L313-430 (~1200 tok)
  - class `CohereEmbeddingEngine` L431-566 (~1379 tok)
  - class `VoyageEmbeddingEngine` L567-712 (~1592 tok)
  - fn `create_embedding_engine` L713-740 (~280 tok)
- `enterprise_index.py` — Pydantic: EnterpriseIndexConfig (39 fields) (~6929 tok)
  - class `IndexProvider` L41-49 (~59 tok)
  - class `SearchLanguage` L50-62 (~67 tok)
  - class `CodeSearchResult` L63-76 (~71 tok)
  - class `RepositoryContext` L77-89 (~64 tok)
  - class `EnterpriseIndexConfig` L90-121 (~319 tok)
  - class `BaseIndexProvider` L122-173 (~537 tok)
  - class `GitHubEnterpriseProvider` L174-278 (~1130 tok)
  - class `GitLabProvider` L279-380 (~1049 tok)
  - class `SourcegraphProvider` L381-486 (~1013 tok)
  - class `BitbucketProvider` L487-554 (~698 tok)
  - class `EnterpriseIndex` L555-687 (~1298 tok)
  - fn `create_enterprise_index` L688-719 (~356 tok)
- `feedback_tracker.py` — class: record (~1584 tok)
  - class `ResponseMetric` L39-56 (~159 tok)
  - class `ProviderStats` L57-78 (~172 tok)
  - class `FeedbackTracker` L79-188 (~1021 tok)
- `huggingface_3d_client.py` — Pydantic: HF3DResult (66 fields) (~12549 tok)
  - class `HF3DModel` L75-100 (~256 tok)
  - class `HF3DFormat` L101-112 (~107 tok)
  - class `HF3DQuality` L113-122 (~76 tok)
  - class `HuggingFace3DConfig` L123-188 (~794 tok)
  - class `HF3DResult` L189-221 (~269 tok)
  - class `HF3DOptimizationHints` L222-232 (~98 tok)
  - class `HuggingFace3DClient` L233-1253 (~10393 tok)
- `huggingface_asset_enhancer.py` — Pydantic: BrandValidationResult (29 fields) (~15334 tok)
  - class `BrandValidationResult` L171-185 (~152 tok)
  - class `SkyyRoseBrandValidator` L186-402 (~2201 tok)
  - class `EnhancementStrategy` L403-410 (~87 tok)
  - class `TextureQuality` L411-419 (~56 tok)
  - class `PreprocessingMode` L420-429 (~72 tok)
  - class `EnhancerConfig` L430-488 (~611 tok)
  - class `ImagePreprocessResult` L489-500 (~99 tok)
  - class `Model3DResult` L501-515 (~110 tok)
  - class `EnhancementResult` L516-549 (~270 tok)
  - class `CollectionEnhancementResult` L550-567 (~172 tok)
  - class `ImagePreprocessor` L568-723 (~1597 tok)
  - class `HuggingFaceAssetEnhancer` L724-1206 (~5104 tok)
  - class `TextureEnhancementResult` L1207-1219 (~107 tok)
  - class `TextureEnhancer` L1220-1462 (~2395 tok)
  - class `HuggingFaceAssetEnhancerWithTextures` L1463-1549 (~796 tok)
- `langgraph_integration.py` — Pydantic: WorkflowState (26 fields) (~1887 tok)
  - class `NodeType` L51-61 (~57 tok)
  - class `EdgeType` L62-69 (~40 tok)
  - class `WorkflowStatus` L70-85 (~115 tok)
  - class `WorkflowState` L86-185 (~921 tok)
  - class `WorkflowEdge` L186-203 (~146 tok)
  - class `ConditionalEdge` L204-226 (~156 tok)
- `llm_clients.py` — MessageRole: close, complete, stream, complete + 2 more (~8796 tok)
  - class `MessageRole` L76-84 (~40 tok)
  - class `Message` L85-94 (~56 tok)
  - class `ToolCall` L95-102 (~36 tok)
  - class `CompletionResponse` L103-123 (~107 tok)
  - class `StreamChunk` L124-136 (~93 tok)
  - class `BaseLLMClient` L137-209 (~555 tok)
  - class `OpenAIClient` L210-339 (~1153 tok)
  - class `AnthropicClient` L340-498 (~1416 tok)
  - class `GoogleClient` L499-649 (~1448 tok)
  - class `MistralClient` L650-762 (~1047 tok)
  - class `CohereClient` L763-886 (~1199 tok)
  - class `GroqClient` L887-1001 (~1053 tok)
- `llm_registry.py` — Declares import (~8009 tok)
  - class `ModelProvider` L36-46 (~55 tok)
  - class `ModelTier` L47-55 (~73 tok)
  - class `ModelCapability` L56-95 (~289 tok)
  - class `ModelDefinition` L96-131 (~252 tok)
  - class `ProviderConfig` L132-586 (~3804 tok)
  - class `LLMRegistry` L587-908 (~3279 tok)
- `model_config.py` — get_model_id, get_all_model_ids, log_model_configuration, get_claude_sonnet + 3 more (~1958 tok)
  - fn `get_model_id` L121-166 (~414 tok)
  - fn `get_all_model_ids` L167-182 (~115 tok)
  - fn `log_model_configuration` L183-208 (~256 tok)
  - fn `get_claude_sonnet` L209-213 (~38 tok)
  - fn `get_gpt4o` L214-218 (~32 tok)
  - fn `get_gemini_2_flash` L219-223 (~40 tok)
  - fn `get_llama_3_3_70b` L224-227 (~38 tok)
- `orchestration_mode_tools.py` — Local tool layer for orchestration mode. (~3247 tok)
  - fn `normalize_subtasks` L125-141 (~180 tok)
  - fn `run_bash` L142-174 (~345 tok)
  - fn `handle_bash_block` L175-189 (~169 tok)
  - fn `run_subagent` L190-244 (~682 tok)
  - fn `run_workflow` L245-286 (~495 tok)
- `orchestration_mode.py` — Orchestration mode — a session-level standing-consent fan-out loop. (~2869 tok)
  - class `ReminderTransport` L70-77 (~80 tok)
  - class `ModeConfig` L78-98 (~216 tok)
  - class `ModeAgent` L99-236 (~1786 tok)
- `prompt_engineering.py` — PromptTechnique: render, validate_variables, get_step, create_prompt + 9 more (~7324 tok)
  - class `PromptTechnique` L51-72 (~192 tok)
  - class `OutputFormat` L73-87 (~94 tok)
  - class `PromptTemplate` L88-111 (~222 tok)
  - class `PromptChain` L112-131 (~163 tok)
  - class `ChainOfThought` L132-194 (~505 tok)
  - class `FewShotLearning` L195-267 (~716 tok)
  - class `SelfConsistency` L268-333 (~543 tok)
  - class `TreeOfThoughts` L334-401 (~402 tok)
  - class `ReActPrompting` L402-458 (~435 tok)
  - class `RAGPrompting` L459-533 (~554 tok)
  - class `StructuredOutput` L534-613 (~537 tok)
  - class `ConstitutionalAI` L614-681 (~475 tok)
  - class `NegativePrompting` L682-715 (~207 tok)
  - class `RoleBasedPrompting` L716-771 (~446 tok)
  - class `PromptEngineer` L772-914 (~1454 tok)
- `protocols.py` — kwargs` to remain decoupled from (~660 tok)
  - class `AssetWorkflowAgent` L21-39 (~171 tok)
  - class `WordPressUploadAgent` L40-58 (~207 tok)
  - class `PreviewGateAgent` L59-70 (~88 tok)
- `query_rewriter_integration.py` — EnhancedSuperAgent: example_basic_rewriting, example_rag_pipeline_integration, example_super_agent_integration, use_technique + 4 more (~3584 tok)
  - fn `example_basic_rewriting` L40-78 (~365 tok)
  - fn `example_rag_pipeline_integration` L79-156 (~704 tok)
  - fn `example_super_agent_integration` L157-204 (~496 tok)
  - fn `example_batch_rewriting` L205-240 (~328 tok)
  - fn `example_complete_rag_flow` L241-308 (~620 tok)
  - fn `example_strategy_guide` L309-355 (~511 tok)
  - fn `main` L356-385 (~251 tok)
- `query_rewriter.py` — Pydantic: RewrittenQuery (27 fields) (~5155 tok)
  - class `QueryRewriteStrategy` L41-50 (~62 tok)
  - class `RewrittenQuery` L51-60 (~122 tok)
  - class `QueryRewriterConfig` L61-75 (~125 tok)
  - class `AdvancedQueryRewriter` L76-438 (~3736 tok)
  - class `RAGPipelineWithRewriting` L439-524 (~768 tok)
- `rag_context_manager.py` — Pydantic: RAGContextConfig (50 fields) (~5880 tok)
  - class `RAGContextConfig` L55-92 (~417 tok)
  - class `RAGDocument` L93-103 (~65 tok)
  - class `RAGContext` L104-172 (~624 tok)
  - class `RAGContextManager` L173-501 (~3533 tok)
  - fn `create_rag_context_manager` L502-590 (~892 tok)
- `reranker.py` — Pydantic: RerankerConfig (44 fields) (~5126 tok)
  - class `RerankingCache` L36-140 (~1039 tok)
  - fn `get_reranking_cache` L141-155 (~168 tok)
  - class `RerankerProvider` L156-162 (~34 tok)
  - class `RerankerConfig` L163-183 (~183 tok)
  - class `RankedResult` L184-197 (~93 tok)
  - class `BaseReranker` L198-252 (~434 tok)
  - class `CohereReranker` L253-400 (~1344 tok)
  - class `VoyageReranker` L401-544 (~1361 tok)
  - fn `create_reranker` L545-570 (~242 tok)
- `scout_harvester.py` — Scout Harvester — input layer for the COMPETITOR_SCOUT agent. (~1660 tok)
  - class `HarvestSource` L37-45 (~69 tok)
  - class `HarvestResult` L46-56 (~75 tok)
  - fn `_fixtures_dir` L57-62 (~58 tok)
  - fn `_load_fixture` L63-80 (~175 tok)
  - fn `load_fixtures` L81-91 (~140 tok)
  - fn `_load_fixtures_uncached` L92-104 (~141 tok)
  - fn `_load_fixtures_cached` L105-108 (~30 tok)
  - fn `is_live_mode` L109-113 (~43 tok)
  - fn `harvest` L114-169 (~593 tok)
- `semantic_analyzer.py` — CodePatternType: analyze_file (~5132 tok)
  - class `CodePatternType` L39-63 (~172 tok)
  - class `CodeSymbol` L64-81 (~156 tok)
  - class `CodePattern` L82-94 (~85 tok)
  - class `SemanticAnalysis` L95-110 (~163 tok)
  - class `SemanticCodeAnalyzer` L111-497 (~4211 tok)
  - fn `get_semantic_analyzer` L498-504 (~72 tok)
- `sync_pipeline.py` — Pydantic: SystemStatus (42 fields) (~5833 tok)
  - fn `_safe_load_json` L66-96 (~275 tok)
  - fn `_sanitize_text` L97-110 (~151 tok)
  - class `SyncDirection` L111-119 (~63 tok)
  - class `SyncStatus` L120-130 (~58 tok)
  - class `SyncRecord` L131-144 (~93 tok)
  - class `SystemStatus` L145-154 (~124 tok)
  - class `SyncPipelineStatus` L155-165 (~159 tok)
  - class `SyncTriggerResponse` L166-179 (~153 tok)
  - class `AssetSyncPipeline` L180-575 (~4020 tok)
  - fn `get_sync_pipeline` L576-596 (~165 tok)
- `tasks.py` — Pydantic: ThreeDGenerationInput (45 fields) (~6161 tok)
  - class `ThreeDGenerationInput` L48-59 (~202 tok)
  - class `MarketingCampaignInput` L60-70 (~176 tok)
  - class `MLTrainingInput` L71-82 (~145 tok)
  - class `MLPredictionInput` L83-97 (~148 tok)
  - fn `process_3d_asset_generation` L98-177 (~784 tok)
  - fn `execute_marketing_campaign` L178-252 (~723 tok)
  - fn `train_ml_model` L253-325 (~722 tok)
  - fn `run_ml_prediction` L326-397 (~738 tok)
  - fn `_execute_email_campaign` L398-430 (~256 tok)
  - fn `_execute_social_campaign` L431-459 (~222 tok)
  - fn `_execute_seo_campaign` L460-488 (~215 tok)
  - fn `_train_sentiment_model` L489-517 (~217 tok)
  - fn `_train_trend_model` L518-545 (~207 tok)
  - fn `_train_segmentation_model` L546-575 (~219 tok)
  - fn `_run_sentiment_prediction` L576-613 (~297 tok)
  - fn `_run_trend_prediction` L614-642 (~191 tok)
  - fn `_run_segmentation_prediction` L643-688 (~377 tok)
- `threed_round_table.py` — CircuitState: should_allow_request, record_success, record_failure, get_delay + 3 more (~18721 tok)
  - fn `_extract_sku_parts` L75-92 (~181 tok)
  - fn `_sku_tokens_consistent` L93-119 (~337 tok)
  - class `CircuitState` L120-128 (~62 tok)
  - class `CircuitBreakerConfig` L129-138 (~94 tok)
  - class `CircuitBreakerState` L139-194 (~641 tok)
  - class `RetryConfig` L195-225 (~273 tok)
  - class `QualityEnhancementConfig` L226-261 (~351 tok)
  - class `ProviderHealth` L262-299 (~343 tok)
  - class `ThreeDProvider` L300-322 (~134 tok)
  - class `CompetitionStatus` L323-335 (~93 tok)
  - class `GenerationType` L336-348 (~98 tok)
  - class `ThreeDQualityScores` L349-400 (~610 tok)
  - class `ThreeDResponse` L401-427 (~249 tok)
  - class `RoundTableEntry` L428-442 (~104 tok)
  - class `ABTestResult` L443-456 (~112 tok)
  - class `RoundTableResult` L457-515 (~692 tok)
  - class `ProviderQuality` L516-547 (~424 tok)
  - class `ThreeDRoundTable` L548-1713 (~12945 tok)
  - fn `quick_text_to_3d` L1714-1725 (~102 tok)
  - fn `quick_image_to_3d` L1726-1756 (~219 tok)
- `vector_store.py` — Pydantic: VectorStoreConfig (41 fields) (~8339 tok)
  - class `VectorSearchCache` L40-139 (~1036 tok)
  - fn `get_vector_search_cache` L140-158 (~200 tok)
  - class `VectorDBType` L159-165 (~36 tok)
  - class `DocumentStatus` L166-175 (~50 tok)
  - class `Document` L176-199 (~211 tok)
  - class `SearchResult` L200-215 (~105 tok)
  - class `VectorStoreConfig` L216-251 (~379 tok)
  - class `BaseVectorStore` L252-318 (~568 tok)
  - class `ChromaVectorStore` L319-587 (~3078 tok)
  - class `PineconeVectorStore` L588-791 (~2241 tok)
  - fn `create_vector_store` L792-814 (~191 tok)

## pipelines/

- `__init__.py` — Cross-service orchestration pipelines. (~106 tok)

## pipelines/clothing_3d/

- `__init__.py` — Clothing 3D pipeline. (~766 tok)
- `cli.py` — CLI entry point for the clothing 3D pipeline. (~2414 tok)
  - fn `build_parser` L53-109 (~702 tok)
  - fn `cmd_generate` L110-135 (~246 tok)
  - fn `cmd_batch` L136-168 (~318 tok)
  - fn `cmd_health` L169-185 (~151 tok)
  - fn `_build_config` L186-195 (~99 tok)
  - fn `_build_provider` L196-202 (~76 tok)
  - fn `_load_jsonl` L203-218 (~183 tok)
  - fn `_emit_result` L219-231 (~118 tok)
  - fn `main` L232-252 (~151 tok)
- `events.py` — Pipeline event bus. (~1334 tok)
  - class `PipelineEvent` L29-43 (~120 tok)
  - class `PipelineEventBus` L44-102 (~511 tok)
  - fn `log_event_subscriber` L103-118 (~140 tok)
  - fn `webhook_subscriber` L119-158 (~322 tok)
- `job_store.py` — Persistent job state for the clothing 3D pipeline. (~3081 tok)
  - class `JobRecord` L38-115 (~907 tok)
  - class `JobStore` L116-134 (~159 tok)
  - class `InMemoryJobStore` L135-183 (~512 tok)
  - class `RedisJobStore` L184-287 (~1047 tok)
  - fn `build_job_store` L288-309 (~171 tok)
- `models.py` — Pydantic models for the clothing 3D pipeline. (~1264 tok)
  - class `PipelineStage` L17-27 (~66 tok)
  - class `PipelineStatus` L28-42 (~123 tok)
  - class `PipelineRequest` L43-92 (~487 tok)
  - class `StageReport` L93-105 (~101 tok)
  - class `PipelineQualityReport` L106-116 (~83 tok)
  - class `PipelineResult` L117-153 (~270 tok)
- `observability.py` — Observability — structured logging + Prometheus metrics. (~2824 tok)
  - class `_JsonFormatter` L38-87 (~402 tok)
  - fn `configure_logging` L88-123 (~343 tok)
  - class `_NoopMetric` L124-139 (~104 tok)
  - class `PipelineMetrics` L140-241 (~1015 tok)
  - fn `get_metrics` L242-249 (~76 tok)
  - fn `render_metrics` L250-258 (~76 tok)
  - fn `metrics_event_subscriber` L259-303 (~468 tok)
- `pipeline.py` — End-to-end clothing 3D pipeline orchestrator. (~3224 tok)
  - class `ClothingPipeline` L39-308 (~2828 tok)
  - fn `run_clothing_pipeline` L309-323 (~121 tok)
- `queue.py` — Queue abstraction for the clothing 3D worker. (~3058 tok)
  - class `QueueMessage` L38-59 (~163 tok)
  - class `JobQueue` L60-80 (~184 tok)
  - class `InMemoryQueue` L81-131 (~490 tok)
  - class `RedisStreamsQueue` L132-301 (~1735 tok)
  - fn `build_queue` L302-323 (~163 tok)
- `reliability.py` — Reliability primitives: retries, idempotency, cost quotas. (~3602 tok)
  - class `RetryPolicy` L48-123 (~790 tok)
  - fn `request_fingerprint` L124-166 (~408 tok)
  - class `IdempotencyEntry` L167-175 (~49 tok)
  - class `IdempotencyStore` L176-187 (~117 tok)
  - class `InMemoryIdempotencyStore` L188-210 (~246 tok)
  - class `IdempotencyCache` L211-272 (~597 tok)
  - class `BackendCost` L273-289 (~130 tok)
  - class `QuotaExceededError` L290-294 (~35 tok)
  - class `_QuotaWindow` L295-299 (~36 tok)
  - class `CostQuota` L300-376 (~739 tok)
- `stages.py` — Individual pipeline stages. (~3833 tok)
  - class `PipelineContext` L43-69 (~279 tok)
  - fn `_start_report` L70-73 (~32 tok)
  - fn `_finish_report` L74-100 (~208 tok)
  - fn `stage_ingest` L101-155 (~499 tok)
  - fn `_safe_image_size` L156-180 (~238 tok)
  - fn `stage_generate` L181-248 (~596 tok)
  - class `QCThresholds` L249-258 (~64 tok)
  - fn `stage_qc` L259-332 (~738 tok)
  - fn `stage_store` L333-405 (~589 tok)
  - fn `default_thresholds_for` L406-430 (~197 tok)
- `storage.py` — Artifact storage for the clothing 3D pipeline. (~2473 tok)
  - class `ArtifactBundle` L34-45 (~87 tok)
  - class `StoredArtifact` L46-65 (~168 tok)
  - class `ArtifactStore` L66-76 (~94 tok)
  - class `LocalArtifactStore` L77-154 (~805 tok)
  - class `S3ArtifactStore` L155-258 (~1018 tok)
- `worker.py` — Background worker for the clothing 3D pipeline. (~3820 tok)
  - class `PipelineWorker` L63-301 (~2814 tok)
  - fn `_build_worker_id` L302-311 (~85 tok)
  - fn `_run_worker` L312-334 (~195 tok)
  - fn `main` L335-353 (~170 tok)

## plugins/fashion-theme-team/

- `.editorconfig` — Editor configuration (~75 tok)
- `.gitignore` — Git ignore rules (~38 tok)
- `.prettierignore` — # Generated branded-skill projections and their evidence snapshots. (~157 tok)
- `.prettierrc.json` — Prettier configuration (~69 tok)
- `formatting.toml` — Fashion Theme Team formatting matrix. (~924 tok)
- `pyproject.toml` — Python project configuration (~89 tok)
- `requirements-formatting.txt` — Locked Python tooling for the full formatting lane. (~45 tok)

## plugins/fashion-theme-team/.codex-plugin/

- `plugin.json` (~821 tok)

## plugins/fashion-theme-team/agents/

- `accessibility-performance-reviewer.md` — Accessibility and Performance Reviewer (~345 tok)
- `brand-experience-architect.md` — Brand Experience Architect (~451 tok)
- `catalog-sot-integrator.md` — Catalog Source-of-Truth Integrator (~391 tok)
- `ecommerce-growth-analytics-engineer.md` — Ecommerce Growth and Analytics Engineer (~310 tok)
- `fashion-accessibility-content-engineer.md` — Fashion Accessibility and Content Engineer (~205 tok)
- `fashion-brand-systems-researcher.md` — Fashion Brand Systems Researcher (~187 tok)
- `fashion-commerce-strategist.md` — Fashion Commerce Strategist (~308 tok)
- `fashion-component-commerce-engineer.md` — Fashion Component and Commerce Engineer (~203 tok)
- `fashion-design-system-engineer.md` — Fashion Design System Architect (~1185 tok)
- `fashion-designops-governance-engineer.md` — Fashion DesignOps and Governance Engineer (~228 tok)
- `fashion-frontend-engineer.md` — Fashion Frontend Engineer (~430 tok)
- `fashion-knowledge-curator.md` — Fashion Knowledge Curator (~315 tok)
- `fashion-merchandising-conversion-architect.md` — Fashion Merchandising and Conversion Architect (~320 tok)
- `fashion-motion-responsive-engineer.md` — Fashion Motion and Responsive Engineer (~201 tok)
- `fashion-product-fit-returns-specialist.md` — Fashion Product, Fit, and Returns Specialist (~300 tok)
- `fashion-theme-lead.md` — Fashion Theme Lead (~638 tok)
- `fashion-token-foundations-engineer.md` — Fashion Token Foundations Engineer (~196 tok)
- `fashion-typography-layout-director.md` — Fashion Typography and Layout Director (~195 tok)
- `fashion-visual-qa-red-team.md` — Fashion Visual QA Red Team (~240 tok)
- `theme-release-engineer.md` — Theme Release Engineer (~401 tok)
- `visual-commerce-qa.md` — Visual Commerce QA (~345 tok)
- `woocommerce-theme-engineer.md` — WooCommerce Theme Engineer (~500 tok)

## plugins/fashion-theme-team/hooks/

- `hooks.json` (~93 tok)
- `session-start.sh` — shellcheck disable=SC2016 (~153 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/

- `__init__.py` (~63 tok)
- `conftest.py` — Root conftest for elite_web_builder — fully isolated from parent packages. (~328 tok)
- `director.py` — ruff: noqa: E402 (~7226 tok)
  - class `StoryStatus` L89-99 (~57 tok)
  - class `UserStory` L100-113 (~104 tok)
  - class `PRDBreakdown` L114-120 (~47 tok)
  - class `PlanningError` L121-129 (~84 tok)
  - class `ProjectReport` L130-148 (~146 tok)
  - class `DirectorConfig` L149-160 (~114 tok)
  - class `Director` L161-691 (~5425 tok)
  - fn `_load_default_routing` L692-723 (~462 tok)
- `INTEGRATION.md` — Fashion Theme Team Integration Overlay (~258 tok)
- `prd.md` — No Built-In Production PRD (~143 tok)
- `pyproject.toml` — Python project configuration (~94 tok)
- `requirements.txt` — Python dependencies (~164 tok)
- `run.py` — Safe, lazy entry point for the optional Elite Web Builder runtime. (~1134 tok)
  - fn `_load_json` L22-31 (~101 tok)
  - fn `_read_prd` L32-41 (~82 tok)
  - fn `_required_keys` L42-55 (~146 tok)
  - fn `_execute` L56-75 (~207 tok)
  - fn `build_parser` L76-94 (~204 tok)
  - fn `main` L95-121 (~255 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/agents/

- `__init__.py` — Specialist agents for Elite Web Builder. (~531 tok)
- `accessibility.py` — Accessibility Agent — WCAG 2.2 AA/AAA, contrast, ARIA, keyboard nav. (~640 tok)
- `backend_dev.py` — Backend Dev Agent — PHP, Python, Node.js, databases, APIs, WooCommerce. (~860 tok)
- `base.py` — for: build_prompt (~540 tok)
  - class `AgentRole` L24-37 (~95 tok)
  - class `AgentCapability` L38-46 (~49 tok)
  - class `AgentOutput` L47-57 (~66 tok)
  - class `AgentSpec` L58-73 (~154 tok)
- `design_system.py` — Design System Agent — color palettes, typography, spacing, design tokens. (~702 tok)
- `frontend_dev.py` — Frontend Dev Agent — HTML/CSS/JS, React, Vue, block patterns, animations. (~742 tok)
- `performance.py` — Performance Agent — Core Web Vitals, asset optimization, caching. (~622 tok)
- `provider_adapters.py` — from: call, call, call, call + 2 more (~3507 tok)
  - fn `_make_httpx_client` L44-76 (~282 tok)
  - class `LLMMessage` L77-84 (~44 tok)
  - class `LLMResponse` L85-98 (~101 tok)
  - class `ProviderAdapter` L99-109 (~104 tok)
  - class `AnthropicAdapter` L110-177 (~678 tok)
  - class `GoogleAdapter` L178-272 (~961 tok)
  - class `OpenAIAdapter` L273-315 (~372 tok)
  - class `XAIAdapter` L316-368 (~436 tok)
  - fn `get_adapter` L369-387 (~152 tok)
- `qa.py` — QA Agent — E2E testing, cross-browser, visual regression, Lighthouse. (~688 tok)
- `runtime.py` — AgentRuntime: execute (~2305 tok)
  - class `AgentRuntime` L39-265 (~1956 tok)
- `seo_content.py` — SEO & Content Agent — meta tags, schema.org, copywriting, structured data. (~645 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/config/

- `provider_routing.json` (~264 tok)
- `quality_gates.json` (~520 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/core/

- `__init__.py` — Core infrastructure for Elite Web Builder. (~14 tok)
- `cost_tracker.py` — from: records, total_cost, total_input_tokens, total_output_tokens + 5 more (~1599 tok)
  - class `TokenRecord` L60-71 (~55 tok)
  - class `CostSummary` L72-88 (~123 tok)
  - class `CostTracker` L89-185 (~920 tok)
- `gate_checkers.py` — check_build, check_lint, check_security, check_diff (~5470 tok)
  - fn `check_build` L43-116 (~682 tok)
  - fn `_check_balanced` L117-144 (~249 tok)
  - fn `_try_php_lint` L145-194 (~539 tok)
  - fn `check_lint` L195-268 (~698 tok)
  - fn `check_security` L269-330 (~545 tok)
  - fn `check_diff` L331-431 (~811 tok)
  - fn `check_a11y` L432-500 (~646 tok)
  - fn `check_perf` L501-548 (~392 tok)
  - fn `build_gate_checkers` L549-610 (~527 tok)
- `ground_truth.py` — URL configuration (~5885 tok)
  - class `ClaimType` L40-53 (~109 tok)
  - class `ValidationSeverity` L54-62 (~48 tok)
  - class `ValidationResult` L63-91 (~258 tok)
  - fn `_is_valid_color` L92-137 (~437 tok)
  - fn `_has_spaces` L138-142 (~30 tok)
  - fn `_has_double_slashes_in_path` L143-166 (~237 tok)
  - class `GroundTruthValidator` L167-248 (~812 tok)
  - fn `_verify_file_exists` L249-278 (~270 tok)
  - fn `_verify_color_value` L279-297 (~178 tok)
  - fn `_verify_css_value` L298-337 (~368 tok)
  - fn `_verify_font_name` L338-391 (~520 tok)
  - fn `_verify_json_validity` L392-414 (~212 tok)
  - fn `_verify_api_endpoint` L415-473 (~494 tok)
  - fn `_verify_import_path` L474-509 (~384 tok)
  - fn `_verify_php_syntax` L510-570 (~538 tok)
  - fn `_verify_html_validity` L571-639 (~646 tok)
- `learning_journal.py` — from: to_dict, from_dict, to_dict, entries + 7 more (~2351 tok)
  - class `JournalEntry` L40-78 (~304 tok)
  - class `Instinct` L79-105 (~201 tok)
  - class `LearningJournal` L106-261 (~1505 tok)
- `model_router.py` — ProviderStatus: avg_latency, from_dict, from_json_file, get_health + 10 more (~3538 tok)
  - class `ProviderStatus` L38-46 (~49 tok)
  - class `ProviderConfig` L47-54 (~36 tok)
  - class `RouteResult` L55-63 (~47 tok)
  - class `ProviderHealth` L64-89 (~224 tok)
  - class `RoutingConfig` L90-123 (~358 tok)
  - class `ModelRouter` L124-361 (~2506 tok)
- `output_writer.py` — URL configuration (~3100 tok)
  - class `ExtractedFile` L94-102 (~42 tok)
  - class `WriteResult` L103-152 (~431 tok)
  - class `OutputWriter` L153-364 (~2022 tok)
- `ralph_integration.py` — from: to_dict, execute, execute_with_fallback (~1806 tok)
  - class `RalphConfig` L37-46 (~56 tok)
  - class `ExecutionResult` L47-70 (~193 tok)
  - class `RalphExecutor` L71-208 (~1271 tok)
- `self_healer.py` — FailureCategory: categorize, diagnose, heal (~2683 tok)
  - class `FailureCategory` L43-52 (~107 tok)
  - class `HealAttempt` L53-61 (~45 tok)
  - class `Diagnosis` L62-70 (~55 tok)
  - class `HealResult` L71-79 (~46 tok)
  - class `HealCycleResult` L80-127 (~517 tok)
  - class `SelfHealer` L128-283 (~1580 tok)
- `verification_loop.py` — Gate: passed, is_enabled, all_green, passed_count + 6 more (~2210 tok)
  - class `Gate` L40-52 (~66 tok)
  - class `GateStatus` L53-66 (~106 tok)
  - class `GateResult` L67-82 (~108 tok)
  - class `VerificationConfig` L83-100 (~166 tok)
  - class `VerificationReport` L101-153 (~478 tok)
  - class `VerificationLoop` L154-252 (~910 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/evals/

- `wordpress_theme_colors.md` — Eval: WordPress Theme Colors (~242 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/knowledge/

- `performance_budgets.md` — Performance Budgets (~534 tok)
- `photo_generation.md` — AI Photo Generation Pipeline — SkyyRose Elite Production Studio (~2745 tok)
- `security_checklist.md` — Security Checklist (OWASP Top 10 for Web Themes) (~756 tok)
- `wcag_checklist.md` — WCAG 2.2 AA Checklist (~722 tok)
- `wordpress_deployment.md` — WordPress Build Specification — SkyyRose Flagship Theme (~10678 tok)
- `wordpress.md` — WordPress Knowledge Base — SkyyRose Production (~2482 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/templates/shopify/

- `settings_schema_starter.json` (~292 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/templates/wordpress/

- `functions-starter.php` — Theme functions starter template. (~530 tok)
- `theme-json-starter.json` (~568 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/tests/

- `__init__.py` — Tests for Elite Web Builder. (~10 tok)
- `conftest.py` — Test configuration — completely isolate from parent packages. (~145 tok)
- `test_agent_runtime.py` — Tests for AgentRuntime — the bridge from AgentSpec to LLM execution. (~2971 tok)
  - fn `routing_config` L20-38 (~169 tok)
  - fn `router` L39-43 (~26 tok)
  - fn `validator` L44-48 (~20 tok)
  - fn `journal` L49-53 (~26 tok)
  - fn `runtime` L54-58 (~39 tok)
  - fn `frontend_spec` L59-75 (~133 tok)
  - fn `design_spec` L76-88 (~101 tok)
  - class `TestBuildMessages` L89-132 (~506 tok)
  - class `TestExecute` L133-253 (~1234 tok)
  - class `TestExtractFiles` L254-279 (~248 tok)
  - class `TestRuntimeRouterIntegration` L280-306 (~286 tok)
- `test_base_agents.py` — Tests for agents/base.py — AgentRole, AgentSpec, AgentOutput, AgentCapability. (~1563 tok)
  - class `TestAgentRole` L14-37 (~229 tok)
  - class `TestAgentCapability` L38-62 (~239 tok)
  - class `TestAgentOutput` L63-94 (~324 tok)
  - class `TestAgentSpec` L95-164 (~661 tok)
- `test_context7_bridge.py` — Tests for tools/context7_bridge.py — Context7 documentation lookup. (~4074 tok)
  - class `TestLibraryInfo` L25-59 (~283 tok)
  - class `TestDocSnippet` L60-89 (~268 tok)
  - class `TestBridgeConstruction` L90-108 (~186 tok)
  - class `TestResolveLibrary` L109-216 (~1175 tok)
  - class `TestQueryDocs` L217-324 (~1246 tok)
  - class `TestLookup` L325-361 (~365 tok)
  - class `TestErrorHandling` L362-390 (~380 tok)
- `test_cost_tracker.py` — Tests for core.cost_tracker — token usage and cost tracking. (~1314 tok)
  - class `TestComputeCost` L10-39 (~373 tok)
  - class `TestRecord` L40-69 (~380 tok)
  - class `TestSummary` L70-97 (~306 tok)
  - class `TestToDict` L98-110 (~110 tok)
  - class `TestReset` L111-119 (~92 tok)
- `test_director.py` — Tests for director.py — Director, UserStory, StoryStatus, PRDBreakdown. (~5894 tok)
  - class `TestStoryStatus` L25-39 (~136 tok)
  - class `TestUserStory` L40-80 (~407 tok)
  - class `TestPRDBreakdown` L81-110 (~274 tok)
  - class `TestDirectorCreation` L111-145 (~396 tok)
  - class `TestDirectorStoryManagement` L146-259 (~1109 tok)
  - class `TestDirectorExecution` L260-377 (~1140 tok)
  - class `TestDefaultRouting` L378-418 (~395 tok)
  - class `TestDirectorRuntimeIntegration` L419-593 (~1856 tok)
- `test_execute_prd.py` — Tests for execute_prd pipeline — PlanningError, ProjectReport, planning, execution. (~5990 tok)
  - fn `_valid_planning_json` L26-44 (~207 tok)
  - fn `_make_mock_adapter` L45-61 (~153 tok)
  - class `TestPlanningError` L62-84 (~225 tok)
  - class `TestProjectReport` L85-146 (~534 tok)
  - class `TestParsePlanningResponse` L147-181 (~436 tok)
  - class `TestBuildBreakdown` L182-274 (~910 tok)
  - class `TestPlanStories` L275-330 (~668 tok)
  - class `TestExecutePrd` L331-586 (~2480 tok)
  - class `TestDirectorConfigMaxStories` L587-605 (~204 tok)
- `test_gate_checkers.py` — Tests for core.gate_checkers — concrete gate checker implementations. (~3252 tok)
  - class `TestCheckBuild` L25-96 (~866 tok)
  - class `TestCheckLint` L97-142 (~572 tok)
  - class `TestCheckSecurity` L143-177 (~431 tok)
  - class `TestCheckDiff` L178-205 (~280 tok)
  - class `TestCheckA11y` L206-239 (~409 tok)
  - class `TestCheckPerf` L240-259 (~230 tok)
  - class `TestBuildGateCheckers` L260-282 (~311 tok)
- `test_ground_truth.py` — Tests for core/ground_truth.py — Anti-hallucination validator. (~9473 tok)
  - fn `validator` L29-33 (~27 tok)
  - fn `temp_dir` L34-103 (~626 tok)
  - class `TestClaimType` L104-125 (~179 tok)
  - class `TestValidationResult` L126-151 (~262 tok)
  - class `TestUnknownClaimType` L152-169 (~226 tok)
  - class `TestFileExists` L170-210 (~464 tok)
  - class `TestColorValue` L211-321 (~1542 tok)
  - class `TestCSSValue` L322-359 (~438 tok)
  - class `TestFontName` L360-409 (~603 tok)
  - class `TestJSONValidity` L410-448 (~449 tok)
  - class `TestAPIEndpoint` L449-515 (~852 tok)
  - class `TestImportPath` L516-581 (~770 tok)
  - class `TestPHPSyntax` L582-624 (~522 tok)
  - class `TestHTMLValidity` L625-694 (~910 tok)
  - class `TestInputSanitization` L695-725 (~374 tok)
  - class `TestVerifyAllOrFail` L726-752 (~282 tok)
  - class `TestBatchValidation` L753-785 (~361 tok)
  - class `TestValidationSummary` L786-817 (~380 tok)
- `test_integration.py` — Integration test — end-to-end run with a minimal test PRD. (~5486 tok)
  - fn `director` L45-49 (~23 tok)
  - fn `mini_prd_stories` L50-92 (~421 tok)
  - class `TestStoryLifecycle` L93-135 (~472 tok)
  - class `TestAgentExecutionPipeline` L136-251 (~1239 tok)
  - class `TestMultiProviderRouting` L252-273 (~251 tok)
  - class `TestGroundTruthIntegration` L274-310 (~416 tok)
  - class `TestLearningIntegration` L311-357 (~494 tok)
  - class `TestVerificationIntegration` L358-403 (~506 tok)
  - class `TestSelfHealIntegration` L404-436 (~325 tok)
  - class `TestRalphIntegration` L437-474 (~369 tok)
  - class `TestFullPipeline` L475-532 (~550 tok)
  - fn `_make_gate_result` L533-539 (~66 tok)
- `test_learning_journal.py` — Tests for core/learning_journal.py — Boris Cherny protocol + instinct extraction. (~2448 tok)
  - fn `journal` L18-22 (~33 tok)
  - fn `sample_entry` L23-37 (~128 tok)
  - class `TestJournalEntry` L38-72 (~390 tok)
  - class `TestJournalOperations` L73-150 (~698 tok)
  - class `TestPersistence` L151-177 (~297 tok)
  - class `TestInstinctExtraction` L178-229 (~581 tok)
  - class `TestContextGeneration` L230-248 (~209 tok)
- `test_lighthouse_runner.py` — Tests for tools/lighthouse_runner.py — Lighthouse performance measurement. (~5551 tok)
  - fn `_make_result` L86-127 (~343 tok)
  - class `TestLighthouseResult` L128-178 (~534 tok)
  - class `TestRunLighthouse` L179-344 (~2070 tok)
  - class `TestCheckPerformanceBudget` L345-455 (~1292 tok)
  - class `TestFormatReport` L456-517 (~607 tok)
- `test_model_router.py` — Tests for core/model_router.py — Multi-provider routing + fallback chain. (~2862 tok)
  - fn `routing_config` L20-42 (~357 tok)
  - fn `router` L43-51 (~84 tok)
  - class `TestProviderConfig` L52-68 (~186 tok)
  - class `TestRoutingResolution` L69-104 (~356 tok)
  - class `TestFallbackChain` L105-130 (~285 tok)
  - class `TestProviderHealth` L131-171 (~490 tok)
  - class `TestAsyncProviderCall` L172-245 (~754 tok)
  - class `TestConfigLoading` L246-269 (~229 tok)
- `test_output_writer.py` — Tests for core.output_writer — filesystem output writer. (~2886 tok)
  - class `TestExtractedFile` L20-37 (~181 tok)
  - class `TestExtractFiles` L38-126 (~1016 tok)
  - class `TestValidatePath` L127-165 (~414 tok)
  - class `TestValidateContent` L166-179 (~135 tok)
  - class `TestWriteFile` L180-223 (~548 tok)
  - class `TestExtractAndWrite` L224-261 (~478 tok)
- `test_provider_adapters.py` — Tests for provider adapters — multi-provider LLM calling layer. (~2932 tok)
  - class `TestLLMMessage` L22-33 (~103 tok)
  - class `TestLLMResponse` L34-61 (~245 tok)
  - class `TestAnthropicAdapter` L62-147 (~928 tok)
  - class `TestGoogleAdapter` L148-203 (~501 tok)
  - class `TestOpenAIAdapter` L204-250 (~478 tok)
  - class `TestXAIAdapter` L251-286 (~359 tok)
  - class `TestGetAdapter` L287-307 (~181 tok)
- `test_ralph_integration.py` — Tests for core/ralph_integration.py — ADK agents to ralph-tui adapter. (~1719 tok)
  - fn `executor` L23-27 (~28 tok)
  - fn `custom_executor` L28-42 (~105 tok)
  - class `TestRalphConfig` L43-60 (~166 tok)
  - class `TestExecuteWithRetry` L61-114 (~518 tok)
  - class `TestExecuteWithFallback` L115-159 (~550 tok)
  - class `TestExecutionResult` L160-180 (~194 tok)
- `test_screenshot_diff.py` — Tests for tools/screenshot_diff.py — Visual regression testing tool. (~4792 tok)
  - fn `_save_solid_image` L29-39 (~79 tok)
  - fn `_save_half_red_half_blue` L40-55 (~164 tok)
  - class `TestDiffResult` L56-116 (~548 tok)
  - class `TestCompareIdentical` L117-149 (~398 tok)
  - class `TestCompareDifferent` L150-206 (~699 tok)
  - class `TestCompareSizeMismatch` L207-231 (~300 tok)
  - class `TestCompareErrors` L232-260 (~352 tok)
  - class `TestCaptureScreenshot` L261-320 (~689 tok)
  - class `TestRunVisualRegression` L321-450 (~1348 tok)
- `test_self_healer.py` — Tests for core/self_healer.py — Diagnose → categorize → route → retry loop. (~2903 tok)
  - fn `healer` L27-31 (~24 tok)
  - fn `failing_report` L32-62 (~353 tok)
  - class `TestFailureCategory` L63-74 (~116 tok)
  - class `TestDiagnosis` L75-110 (~404 tok)
  - class `TestHealCycle` L111-250 (~1383 tok)
  - class `TestCategoryRouting` L251-290 (~469 tok)
- `test_specialist_agents.py` — Tests for all 7 specialist agent specs — verify role, prompt, capabilities. (~2346 tok)
  - class `TestAllSpecs` L31-76 (~468 tok)
  - class `TestDesignSystem` L77-100 (~256 tok)
  - class `TestFrontendDev` L101-120 (~203 tok)
  - class `TestBackendDev` L121-141 (~223 tok)
  - class `TestAccessibility` L142-161 (~197 tok)
  - class `TestPerformance` L162-181 (~195 tok)
  - class `TestSeoContent` L182-201 (~195 tok)
  - class `TestQA` L202-225 (~226 tok)
  - class `TestLearningInjection` L226-234 (~120 tok)
- `test_template_scaffold.py` — Tests for tools/template_scaffold.py — WordPress, Shopify, and component scaffolding. (~4575 tok)
  - class `TestScaffoldFileImmutability` L26-42 (~193 tok)
  - class `TestScaffoldResultImmutability` L43-86 (~419 tok)
  - class `TestScaffoldWordPressTemplate` L87-167 (~1020 tok)
  - class `TestScaffoldShopifyTemplate` L168-233 (~816 tok)
  - class `TestScaffoldComponent` L234-314 (~1043 tok)
  - class `TestListTemplates` L315-362 (~496 tok)
  - class `TestEdgeCases` L363-394 (~400 tok)
- `test_tools.py` — Tests for tools/ — contrast checker, file validator, type scale, spacing scale. (~1546 tok)
  - class `TestHexToRgb` L27-37 (~88 tok)
  - class `TestRelativeLuminance` L38-45 (~75 tok)
  - class `TestCheckContrast` L46-79 (~318 tok)
  - class `TestFileValidator` L80-120 (~424 tok)
  - class `TestTypeScale` L121-147 (~228 tok)
  - class `TestSpacingScale` L148-169 (~228 tok)
- `test_verification_loop.py` — Tests for core/verification_loop.py — 8-gate quality check. (~2692 tok)
  - fn `default_config` L26-31 (~37 tok)
  - fn `loop` L32-40 (~87 tok)
  - class `TestGateEnum` L41-62 (~160 tok)
  - class `TestGateResult` L63-96 (~305 tok)
  - class `TestVerificationConfig` L97-120 (~291 tok)
  - class `TestRunGate` L121-168 (~514 tok)
  - class `TestFullRun` L169-238 (~680 tok)
  - class `TestVerificationReport` L239-272 (~453 tok)

## plugins/fashion-theme-team/runtime/elite_web_builder/tools/

- `__init__.py` — Verification and utility tools for Elite Web Builder. (~18 tok)
- `context7_bridge.py` — Context7 documentation bridge — anti-hallucination for library code. (~2108 tok)
  - class `Context7Error` L38-47 (~90 tok)
  - class `LibraryInfo` L48-58 (~56 tok)
  - class `DocSnippet` L59-73 (~95 tok)
  - class `Context7Bridge` L74-238 (~1564 tok)
- `contrast_checker.py` — ContrastResult: hex_to_rgb, relative_luminance, linearize, contrast_ratio + 2 more (~721 tok)
  - class `ContrastResult` L18-30 (~74 tok)
  - fn `hex_to_rgb` L31-38 (~80 tok)
  - fn `relative_luminance` L39-49 (~111 tok)
  - fn `contrast_ratio` L50-58 (~90 tok)
  - fn `wcag_level` L59-69 (~72 tok)
  - fn `check_contrast` L70-93 (~185 tok)
- `file_validator.py` — from: validate_file_exists, validate_json_file, validate_no_secrets (~711 tok)
  - class `FileValidationResult` L17-36 (~152 tok)
  - fn `validate_file_exists` L37-44 (~91 tok)
  - fn `validate_json_file` L45-61 (~167 tok)
  - fn `validate_no_secrets` L62-82 (~201 tok)
- `lighthouse_runner.py` — Lighthouse performance measurement tool for Elite Web Builder. (~2792 tok)
  - class `LighthouseError` L59-68 (~90 tok)
  - class `LighthouseResult` L69-86 (~135 tok)
  - fn `_get_timestamp` L87-91 (~38 tok)
  - fn `_build_command` L92-112 (~137 tok)
  - fn `_extract_score` L113-124 (~96 tok)
  - fn `_extract_metrics` L125-134 (~113 tok)
  - fn `_extract_failed_audits` L135-154 (~176 tok)
  - fn `_parse_report` L155-188 (~332 tok)
  - fn `run_lighthouse` L189-238 (~482 tok)
  - fn `check_performance_budget` L239-280 (~375 tok)
  - fn `format_report` L281-327 (~385 tok)
- `screenshot_diff.py` — from: capture_screenshot, compare_screenshots, run_visual_regression (~2720 tok)
  - class `DiffResult` L41-57 (~121 tok)
  - fn `_validate_file_exists` L58-65 (~74 tok)
  - fn `_validate_dir_exists` L66-73 (~75 tok)
  - fn `_url_to_filename` L74-88 (~161 tok)
  - fn `capture_screenshot` L89-141 (~424 tok)
  - fn `_load_and_normalize` L142-162 (~210 tok)
  - fn `_compute_pixel_diff` L163-198 (~316 tok)
  - fn `compare_screenshots` L199-248 (~490 tok)
  - fn `run_visual_regression` L249-299 (~504 tok)
- `spacing_scale.py` — generate_spacing_scale (~299 tok)
- `template_scaffold.py` — Template scaffolding tool — WordPress, Shopify, and frontend components. (~6339 tok)
  - class `ScaffoldError` L29-38 (~92 tok)
  - class `ScaffoldFile` L39-46 (~42 tok)
  - class `ScaffoldResult` L47-61 (~108 tok)
  - fn `_validate_name` L62-68 (~72 tok)
  - fn `_slugify` L69-97 (~236 tok)
  - fn `_wp_page` L98-133 (~371 tok)
  - fn `_wp_archive` L134-157 (~287 tok)
  - fn `_wp_single` L158-177 (~243 tok)
  - fn `_wp_template_part` L178-189 (~132 tok)
  - fn `_wp_block_pattern` L190-255 (~588 tok)
  - fn `_shopify_json_template` L256-272 (~127 tok)
  - fn `_shopify_page` L273-279 (~92 tok)
  - fn `_shopify_collection` L280-286 (~98 tok)
  - fn `_shopify_product` L287-293 (~95 tok)
  - fn `_shopify_section` L294-328 (~307 tok)
  - fn `_shopify_snippet` L329-360 (~285 tok)
  - fn `_component_react` L361-399 (~397 tok)
  - fn `_component_vue` L400-439 (~361 tok)
  - fn `_component_vanilla` L440-486 (~457 tok)
  - fn `scaffold_wordpress_template` L487-531 (~392 tok)
  - fn `scaffold_shopify_template` L532-577 (~397 tok)
  - fn `scaffold_component` L578-620 (~374 tok)
  - fn `list_templates` L621-673 (~556 tok)
- `type_scale.py` — generate_type_scale (~336 tok)

## plugins/fashion-theme-team/scripts/

- `capture-branded-authorities.py` — Capture TLS-authenticated primary-authority metadata for branded skills. (~2423 tok)
  - fn `authenticated_capture` L59-87 (~394 tok)
  - fn `main` L88-210 (~1486 tok)
- `check-formatting.py` — Run the Fashion Theme Team's deterministic, source-aware format matrix. (~5821 tok)
  - class `MatrixError` L32-35 (~30 tok)
  - class `_HTMLProbe` L36-42 (~67 tok)
  - fn `load_config` L43-53 (~118 tok)
  - fn `run_git` L54-67 (~138 tok)
  - fn `has_git_worktree` L68-83 (~136 tok)
  - fn `decode_nul_list` L84-87 (~44 tok)
  - fn `changed_files` L88-104 (~118 tok)
  - fn `candidate_files` L105-134 (~322 tok)
  - fn `matches_exclude` L135-139 (~45 tok)
  - fn `is_excluded` L140-143 (~43 tok)
  - fn `extension` L144-147 (~21 tok)
  - fn `language_for` L148-159 (~126 tok)
  - fn `classify_files` L160-179 (~191 tok)
  - fn `read_text` L180-187 (~73 tok)
  - fn `text_policy_errors` L188-207 (~250 tok)
  - fn `normalize_text` L208-222 (~177 tok)
  - fn `resolve_tool` L223-238 (~152 tok)
  - fn `tool_version` L239-253 (~166 tok)
  - fn `enforce_pinned_version` L254-278 (~261 tok)
  - fn `run_command` L279-288 (~105 tok)
  - fn `run_black` L289-308 (~269 tok)
  - fn `run_python_quality_checks` L309-358 (~574 tok)
  - fn `optional_formatter_command` L359-377 (~224 tok)
  - fn `run_optional_formatter` L378-399 (~233 tok)
  - fn `validate_syntax` L400-452 (~586 tok)
  - fn `format_group` L453-490 (~397 tok)
  - fn `build_parser` L491-506 (~185 tok)
  - fn `main` L507-555 (~517 tok)
- `check-formatting.sh` (~48 tok)
- `generate-branded-skill-enhancements.py` — Generate deterministic SkyyRose enhancement manifests for branded skills. (~8508 tok)
  - fn `sha256_bytes` L145-148 (~24 tok)
  - fn `parse_frontmatter` L149-161 (~136 tok)
  - fn `capability_profile` L162-219 (~617 tok)
  - fn `gap_records` L220-337 (~1716 tok)
  - fn `canonical_contract_sha` L338-349 (~109 tok)
  - fn `record_for` L350-619 (~3129 tok)
  - fn `generate` L620-678 (~789 tok)
  - fn `compare_trees` L679-692 (~169 tok)
  - fn `main` L693-747 (~623 tok)
- `preflight.sh` — Declares f (~561 tok)
- `report.sh` — shellcheck disable=SC2016 (~570 tok)
- `sync-branded-skill-sources.py` — Vendor the approved branded-skill source set as an immutable plugin input. (~670 tok)
  - fn `copy_sources` L13-20 (~91 tok)
  - fn `main` L21-63 (~513 tok)
- `sync-team-distributions.py` — Check or mirror the canonical Fashion Theme Team package to one local target. (~1786 tok)
  - class `Difference` L39-48 (~63 tok)
  - fn `is_local_path` L49-56 (~73 tok)
  - fn `package_files` L57-69 (~131 tok)
  - fn `sha256` L70-77 (~65 tok)
  - fn `validate_package` L78-87 (~140 tok)
  - fn `compare` L88-102 (~149 tok)
  - fn `print_difference` L103-118 (~128 tok)
  - fn `remove_empty_parent_directories` L119-128 (~72 tok)
  - fn `apply` L129-144 (~196 tok)
  - fn `parse_args` L145-171 (~234 tok)
  - fn `main` L172-198 (~268 tok)
- `test_check_formatting.py` — Regression tests for the source-aware formatting matrix. (~1422 tok)
  - class `ChangedFileScopeTests` L21-116 (~1235 tok)
- `test_sync_team_distributions.py` — Regression tests for Fashion Theme Team distribution boundaries. (~702 tok)
  - class `PackageBoundaryTests` L21-64 (~512 tok)
- `validate-branded-evidence.py` — Validate candidate-bound evidence beyond JSON Schema expressiveness. (~1166 tok)
  - fn `sha256` L16-19 (~22 tok)
  - fn `contract_sha` L20-27 (~86 tok)
  - fn `candidate_sha` L28-35 (~72 tok)
  - fn `main` L36-100 (~902 tok)
- `verify-portable-package.sh` (~314 tok)
- `verify.sh` — Declares f (~10063 tok)

## plugins/fashion-theme-team/tasks/

- `branded-skills-enhancement-ledger.json` (~996 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-architecture/

- `SKILL.md` — Brand Architecture (~1559 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-audit/

- `SKILL.md` — Brand Audit (~1488 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-identity-guide/

- `SKILL.md` — Brand Identity Guide (~1384 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-positioning-statement/

- `SKILL.md` — Brand Positioning Statement (~1508 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-refresh/

- `SKILL.md` — Brand Refresh (~4331 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-tagline/

- `SKILL.md` — Brand Tagline (~1592 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/brand-voice-guide/

- `SKILL.md` — Brand Voice Guide (~6509 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/color-palette-generator/

- `SKILL.md` — Color Palette Generator (~1401 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/executive-resume/

- `SKILL.md` — Executive Resume (~2316 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/expert-positioning/

- `SKILL.md` — Expert Positioning (~1775 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/icon-set-brief/

- `SKILL.md` — Icon Set Brief (~1407 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/merch-design-brief/

- `SKILL.md` — Merch Design Brief (~1501 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/mission-statement/

- `SKILL.md` — Mission Statement (~1848 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/naming-workshop/

- `SKILL.md` — Naming Workshop (~1548 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/packaging-brief/

- `SKILL.md` — Packaging Brief (~1553 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/portfolio-page/

- `SKILL.md` — Portfolio Page (~1596 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/presentation-template-guide/

- `SKILL.md` — Presentation Template Guide (~1462 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/rebrand-plan/

- `SKILL.md` — Rebrand Plan (~1535 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/signage-brief/

- `SKILL.md` — Signage Brief (~1432 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/signature-talk/

- `SKILL.md` — Signature Talk (~1794 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/speaking-one-sheet/

- `SKILL.md` — Speaking One-Sheet (~2079 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/style-tile/

- `SKILL.md` — Style Tile (~1568 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/unboxing-experience/

- `SKILL.md` — Unboxing Experience (~1555 tok)

## plugins/fashion-theme-team/vendor/branded-skills/branding-design/visual-identity-brief/

- `SKILL.md` — Visual Identity Brief (~1542 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/about-page/

- `SKILL.md` — About Page (~5622 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/article-rewriter/

- `SKILL.md` — Article Rewriter (~1752 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/authority-content-strategy/

- `SKILL.md` — Authority Content Strategy (~2404 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/blog-post/

- `SKILL.md` — Blog Post (~3778 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/book-outline/

- `SKILL.md` — Book Outline Builder (~1661 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/book-proposal/

- `SKILL.md` — Book Proposal (~2248 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/brand-story/

- `SKILL.md` — Brand Story Builder (~1838 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/caption-writer/

- `SKILL.md` — Caption Writer (~1407 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/case-study/

- `SKILL.md` — Case Study (~4611 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/collection-page-copy/

- `SKILL.md` — Collection Page Copy (~1642 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/comparison-article/

- `SKILL.md` — Comparison Article (~1830 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-audit/

- `SKILL.md` — Content Audit (~1791 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-brief/

- `SKILL.md` — Content Brief Builder (~1838 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-calendar/

- `SKILL.md` — Content Calendar (~5214 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-cluster-plan/

- `SKILL.md` — Content Cluster Plan (~1572 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-gap-finder/

- `SKILL.md` — Content Gap Finder (~1789 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-pillar-strategy/

- `SKILL.md` — Content Pillar Strategy (~1868 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-repurpose/

- `SKILL.md` — Content Repurpose (~1543 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/content-style-guide/

- `SKILL.md` — Content Style Guide (~2042 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/donation-page-copy/

- `SKILL.md` — Donation Page Copy (~1788 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/ebook-outline/

- `SKILL.md` — Ebook Outline (~1856 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/expert-roundup-pitch/

- `SKILL.md` — Expert Roundup Pitch (~1527 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/faq-generator/

- `SKILL.md` — FAQ Generator (~6419 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/feature-announcement/

- `SKILL.md` — Feature Announcement (~1580 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/ghostwriter-brief/

- `SKILL.md` — Ghostwriter Brief (~1981 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/headline-generator/

- `SKILL.md` — Headline Generator (~1772 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/help-center-article/

- `SKILL.md` — Help Center Article (~1670 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/hook-generator/

- `SKILL.md` — Hook Generator (~1638 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/landing-page-copy/

- `SKILL.md` — Landing Page Copy (~1993 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/linkedin-article/

- `SKILL.md` — LinkedIn Article (~1773 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/listicle-generator/

- `SKILL.md` — Listicle Generator (~1713 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/microcopy-writer/

- `SKILL.md` — Microcopy Writer (~1837 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/newsletter-builder/

- `SKILL.md` — Newsletter Builder (~3410 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/newsletter-strategy/

- `SKILL.md` — Newsletter Strategy (~2016 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/pillar-page/

- `SKILL.md` — Pillar Page (~1879 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/podcast-one-sheet/

- `SKILL.md` — Podcast One-Sheet (~1701 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/podcast-show-notes/

- `SKILL.md` — Podcast Show Notes (~2572 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/press-kit/

- `SKILL.md` — Press Kit (~1657 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/press-release/

- `SKILL.md` — Press Release (~6123 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/pricing-page-copy/

- `SKILL.md` — Pricing Page Copy (~1693 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/product-changelog/

- `SKILL.md` — Product Changelog (~1717 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/product-description/

- `SKILL.md` — Product Description (~4253 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/product-faq/

- `SKILL.md` — Product FAQ (~1571 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/professional-bio/

- `SKILL.md` — Professional Bio (~2211 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/recipe-card/

- `SKILL.md` — Recipe Card (~2151 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/release-notes/

- `SKILL.md` — Release Notes (~1843 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/script-to-blog/

- `SKILL.md` — Script to Blog (~1849 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/seo-content-brief/

- `SKILL.md` — SEO Content Brief (~1518 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/speech-writer/

- `SKILL.md` — Speech Writer (~1746 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/thought-leader-content-plan/

- `SKILL.md` — Thought Leader Content Plan (~2008 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/thought-leadership/

- `SKILL.md` — Thought Leadership (~1877 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/tutorial-writer/

- `SKILL.md` — Tutorial Writer (~2944 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/video-script/

- `SKILL.md` — Video Script (~4177 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/viral-content-formula/

- `SKILL.md` — Viral Content Formula (~2224 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/white-paper/

- `SKILL.md` — White Paper (~2129 tok)

## plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/youtube-thumbnail/

- `SKILL.md` — YouTube Thumbnail Generator (~4280 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/cross-border-selling/

- `SKILL.md` — Cross-Border Selling (~1752 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/dropshipping-supplier-brief/

- `SKILL.md` — Dropshipping Supplier Brief (~1593 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/exchange-policy/

- `SKILL.md` — Exchange Policy (~1703 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/food-delivery-strategy/

- `SKILL.md` — Food Delivery Strategy (~2124 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/food-truck-business-plan/

- `SKILL.md` — Food Truck Business Plan (~2094 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/gift-guide/

- `SKILL.md` — Gift Guide (~1415 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/investment-property-analysis/

- `SKILL.md` — Investment Property Analysis (~1635 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/lease-agreement-checklist/

- `SKILL.md` — Lease Agreement Checklist (~1700 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/marketplace-listing/

- `SKILL.md` — Marketplace Listing (~1685 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/neighborhood-guide/

- `SKILL.md` — Neighborhood Guide (~1809 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/open-house-plan/

- `SKILL.md` — Open House Plan (~1719 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/product-recall-plan/

- `SKILL.md` — Product Recall Plan (~1761 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/product-sourcing-brief/

- `SKILL.md` — Product Sourcing Brief (~1662 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/property-listing/

- `SKILL.md` — Property Listing (~1608 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/property-management-sop/

- `SKILL.md` — Property Management SOP (~2048 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/real-estate-crm-setup/

- `SKILL.md` — Real Estate CRM Setup (~1940 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/real-estate-newsletter/

- `SKILL.md` — Real Estate Newsletter (~1738 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/rental-listing/

- `SKILL.md` — Rental Listing (~1636 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/seasonal-inventory-plan/

- `SKILL.md` — Seasonal Inventory Plan (~1641 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/seller-onboarding/

- `SKILL.md` — Seller Onboarding (~2040 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/size-guide/

- `SKILL.md` — Size Guide (~1442 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/store-launch-plan/

- `SKILL.md` — Store Launch Plan (~1625 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/subscription-box-plan/

- `SKILL.md` — Subscription Box Plan (~1770 tok)

## plugins/fashion-theme-team/vendor/branded-skills/e-commerce-products/wholesale-catalog/

- `SKILL.md` — Wholesale Catalog (~1460 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/abandoned-cart-email/

- `SKILL.md` — Abandoned Cart Email (~2231 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/ambassador-program/

- `SKILL.md` — Ambassador Program (~2343 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/black-friday-emails/

- `SKILL.md` — Black Friday Emails (~1390 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/cart-recovery-sms/

- `SKILL.md` — Cart Recovery SMS (~1376 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/cause-marketing-campaign/

- `SKILL.md` — Cause Marketing Campaign (~1827 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/cold-outreach/

- `SKILL.md` — Cold Outreach (~3853 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/customer-review-strategy/

- `SKILL.md` — Customer Review Strategy (~1652 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/downsell-sequence/

- `SKILL.md` — Downsell Sequence (~1668 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/drip-campaign/

- `SKILL.md` — Drip Campaign (~1744 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-ab-test-plan/

- `SKILL.md` — Email A/B Test Plan (~1558 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-deliverability-audit/

- `SKILL.md` — Email Deliverability Audit (~2728 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-design-system/

- `SKILL.md` — Email Design System (~1540 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-list-cleanup/

- `SKILL.md` — Email List Cleanup (~1514 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-newsletter-template/

- `SKILL.md` — Email Newsletter Template (~2186 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-preference-center/

- `SKILL.md` — Email Preference Center (~1383 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-sequence/

- `SKILL.md` — Email Sequence (~5002 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/email-subject-line-tester/

- `SKILL.md` — Email Subject Line Tester (~1478 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/engagement-playbook/

- `SKILL.md` — Engagement Playbook (~2259 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/flash-sale-campaign/

- `SKILL.md` — Flash Sale Campaign (~1380 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/launch-email-sequence/

- `SKILL.md` — Launch Email Sequence (~1430 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/loyalty-program/

- `SKILL.md` — Loyalty Program Designer (~1759 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/milestone-email/

- `SKILL.md` — Milestone Email (~1439 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/order-bump-copy/

- `SKILL.md` — Order Bump Copy (~1577 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/payment-plan-offer/

- `SKILL.md` — Payment Plan Offer (~1504 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/price-increase-notice/

- `SKILL.md` — Price Increase Notice (~1622 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/product-launch-email/

- `SKILL.md` — Product Launch Email (~2039 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/re-engagement-email/

- `SKILL.md` — Re-Engagement Email (~2188 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/referral-program/

- `SKILL.md` — Referral Program Designer (~1699 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/renewal-campaign/

- `SKILL.md` — Renewal Campaign (~1514 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/seasonal-campaign/

- `SKILL.md` — Seasonal Campaign (~3134 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/social-proof-collector/

- `SKILL.md` — Social Proof Collector (~2333 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/testimonial-collector/

- `SKILL.md` — Testimonial Collector (~2031 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/thank-you-campaign/

- `SKILL.md` — Thank-You Campaign (~2521 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/transactional-email/

- `SKILL.md` — Transactional Email (~2192 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/trial-to-paid-email/

- `SKILL.md` — Trial-to-Paid Email Sequence (~1916 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/two-sided-email-strategy/

- `SKILL.md` — Two-Sided Email Strategy (~2097 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/upsell-sequence/

- `SKILL.md` — Upsell Sequence (~5388 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/user-generated-content/

- `SKILL.md` — User-Generated Content (~1979 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/waitlist-builder/

- `SKILL.md` — Waitlist Builder (~1569 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/webinar-email-sequence/

- `SKILL.md` — Webinar Email Sequence (~1348 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/welcome-sequence/

- `SKILL.md` — Welcome Sequence Builder (~1864 tok)

## plugins/fashion-theme-team/vendor/branded-skills/email-marketing-automation/win-back-campaign/

- `SKILL.md` — Win-Back Campaign (~5039 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/business-plan/

- `SKILL.md` — Business Plan Writer (~1728 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/coaching-framework/

- `SKILL.md` — Coaching Framework (~3100 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/collaboration-agreement/

- `SKILL.md` — Collaboration Agreement (~2045 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/competitor-analysis/

- `SKILL.md` — Competitor Analysis (~6825 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/customer-journey-map/

- `SKILL.md` — Customer Journey Map (~3209 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/customer-persona/

- `SKILL.md` — Customer Persona (~1679 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/customer-segmentation/

- `SKILL.md` — Customer Segmentation (~1933 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/discovery-call-script/

- `SKILL.md` — Discovery Call Script (~1930 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/joint-venture-proposal/

- `SKILL.md` — Joint Venture Proposal (~1841 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/lead-magnet/

- `SKILL.md` — Lead Magnet (~5092 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/market-research/

- `SKILL.md` — Market Research (~1732 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/market-sizing/

- `SKILL.md` — Market Sizing (~1457 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/membership-site-plan/

- `SKILL.md` — Membership Site Plan (~3357 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/objection-handler/

- `SKILL.md` — Objection Handler Playbook (~1926 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/partnership-proposal/

- `SKILL.md` — Partnership Proposal (~2471 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/pitch-deck/

- `SKILL.md` — Pitch Deck (~3802 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/product-comparison/

- `SKILL.md` — Product Comparison (~2977 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/product-roadmap/

- `SKILL.md` — Product Roadmap (~4362 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/proposal-writer/

- `SKILL.md` — Proposal Writer (~5255 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/revenue-model/

- `SKILL.md` — Revenue Model (~1452 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/sales-battlecard/

- `SKILL.md` — Sales Battlecard (~1585 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/sales-deck/

- `SKILL.md` — Sales Deck (~1602 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/sales-email-template/

- `SKILL.md` — Sales Email Template (~1588 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/sales-funnel-builder/

- `SKILL.md` — Sales Funnel Builder (~1610 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/sales-script/

- `SKILL.md` — Sales Script Builder (~1767 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/strategic-alliance-plan/

- `SKILL.md` — Strategic Alliance Plan (~1846 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/swot-analysis/

- `SKILL.md` — SWOT Analysis (~7119 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/value-proposition-canvas/

- `SKILL.md` — Value Proposition Canvas (~1546 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/webinar-sales-script/

- `SKILL.md` — Webinar Sales Script (~1626 tok)

## plugins/fashion-theme-team/vendor/branded-skills/sales-funnels/win-loss-analysis/

- `SKILL.md` — Win/Loss Analysis (~1599 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/checkout-optimizer/

- `SKILL.md` — Checkout Optimizer (~2443 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/featured-snippet-optimizer/

- `SKILL.md` — Featured Snippet Optimizer (~1675 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/google-business-profile/

- `SKILL.md` — Google Business Profile (~1859 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/keyword-research/

- `SKILL.md` — Keyword Research (~1573 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/landing-page-audit/

- `SKILL.md` — Landing Page Audit (~1668 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/link-building-plan/

- `SKILL.md` — Link Building Plan (~1649 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/local-seo-plan/

- `SKILL.md` — Local SEO Plan (~1674 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/marketplace-seo/

- `SKILL.md` — Marketplace SEO (~2136 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/meta-tag-optimizer/

- `SKILL.md` — Meta Tag Optimizer (~1568 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/platform-migration/

- `SKILL.md` — Platform Migration (~2164 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/product-listing-optimizer/

- `SKILL.md` — Product Listing Optimizer (~1677 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/schema-markup-guide/

- `SKILL.md` — Schema Markup Guide (~1626 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/seo-audit/

- `SKILL.md` — SEO Audit (~1697 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/seo-competitor-analysis/

- `SKILL.md` — SEO Competitor Analysis (~1630 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/seo-migration-plan/

- `SKILL.md` — SEO Migration Plan (~1751 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/seo-reporting-template/

- `SKILL.md` — SEO Reporting Template (~1646 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/site-architecture-plan/

- `SKILL.md` — Site Architecture Plan (~1657 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/store-page-audit/

- `SKILL.md` — Store Page Audit (~1648 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/technical-seo-checklist/

- `SKILL.md` — Technical SEO Checklist (~1800 tok)

## plugins/fashion-theme-team/vendor/branded-skills/seo-search/youtube-seo/

- `SKILL.md` — YouTube SEO (~1679 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/author-platform-plan/

- `SKILL.md` — Author Platform Plan (~2050 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/brand-photography-brief/

- `SKILL.md` — Brand Photography Brief (~3008 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/co-marketing-plan/

- `SKILL.md` — Co-Marketing Plan (~1927 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/community-launch/

- `SKILL.md` — Community Launch (~2106 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/community-moderation/

- `SKILL.md` — Community Moderation (~2406 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/crisis-comms/

- `SKILL.md` — Crisis Communications Planner (~1683 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/facebook-group-plan/

- `SKILL.md` — Facebook Group Plan (~2307 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/food-photography-brief/

- `SKILL.md` — Food Photography Brief (~2148 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/guest-post-pitch/

- `SKILL.md` — Guest Post Pitch (~2005 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/hashtag-strategy/

- `SKILL.md` — Hashtag Strategy (~3184 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/influencer-campaign-brief/

- `SKILL.md` — Influencer Campaign Brief (~1726 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/influencer-outreach/

- `SKILL.md` — Influencer Outreach (~2148 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/instagram-carousel/

- `SKILL.md` — Instagram Carousel (~1789 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/linkedin-profile-optimizer/

- `SKILL.md` — LinkedIn Profile Optimizer (~2233 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/linkedin-strategy/

- `SKILL.md` — LinkedIn Strategy (~2120 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/media-kit/

- `SKILL.md` — Media Kit Builder (~1287 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/meme-content-brief/

- `SKILL.md` — Meme Content Brief (~1680 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/menu-design-brief/

- `SKILL.md` — Menu Design Brief (~2134 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/networking-strategy/

- `SKILL.md` — Networking Strategy (~1861 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/personal-brand-strategy/

- `SKILL.md` — Personal Brand Strategy (~1952 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/pinterest-strategy/

- `SKILL.md` — Pinterest Strategy (~2051 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/platform-community-guidelines/

- `SKILL.md` — Platform Community Guidelines (~2101 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/podcast-guest-pitch/

- `SKILL.md` — Podcast Guest Pitch (~2040 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/pr-pitch/

- `SKILL.md` — PR Pitch Writer (~1388 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/product-photography-brief/

- `SKILL.md` — Product Photography Brief (~3531 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/reddit-strategy/

- `SKILL.md` — Reddit Strategy (~2024 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/short-form-video-plan/

- `SKILL.md` — Short-Form Video Plan (~1911 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/social-listening-plan/

- `SKILL.md` — Social Listening Plan (~2101 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/social-media-audit/

- `SKILL.md` — Social Media Audit (~6858 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/social-media-calendar/

- `SKILL.md` — Social Media Calendar (~2041 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/social-media-graphics/

- `SKILL.md` — Social Media Graphics (~4494 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/social-media-policy/

- `SKILL.md` — Social Media Policy (~2201 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/social-media-strategy/

- `SKILL.md` — Social Media Strategy (~1985 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/sponsor-pitch/

- `SKILL.md` — Sponsor Pitch (~1587 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/thread-hook-writer/

- `SKILL.md` — Thread Hook Writer (~1942 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/tiktok-script/

- `SKILL.md` — TikTok Script (~1848 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/twitter-thread/

- `SKILL.md` — Twitter Thread (~1748 tok)

## plugins/fashion-theme-team/vendor/branded-skills/social-media/youtube-strategy/

- `SKILL.md` — YouTube Strategy (~2135 tok)

## prompts/

- `__init__.py` (~299 tok)
- `agent_prompts.py` — Declares from (~7546 tok)
  - class `AgentPromptConfig` L40-52 (~104 tok)
  - class `AgentPromptLibrary` L53-679 (~6990 tok)
  - fn `create_prompt_library` L680-684 (~40 tok)
  - fn `get_agent_prompt` L685-710 (~187 tok)
- `base_system_prompt.py` — from: to_prompt_section, to_prompt_line, generate (~6052 tok)
  - class `AgentCategory` L25-37 (~93 tok)
  - class `OutputStandard` L38-46 (~76 tok)
  - class `AgentIdentity` L47-68 (~171 tok)
  - class `BehavioralDirective` L69-81 (~142 tok)
  - class `BaseAgentSystemPrompt` L82-617 (~5038 tok)
  - fn `create_base_prompt_generator` L618-622 (~44 tok)
  - fn `generate_agent_system_prompt` L623-667 (~329 tok)
- `chain_orchestrator.py` — ChainStepType: to_dict, to_dict, to_dict, create_workflow (~7192 tok)
  - class `ChainStepType` L29-38 (~56 tok)
  - class `ChainStatus` L39-49 (~58 tok)
  - class `ChainStep` L50-79 (~274 tok)
  - class `ChainResult` L80-104 (~203 tok)
  - class `WorkflowDefinition` L105-126 (~193 tok)
  - class `PromptChainOrchestrator` L127-738 (~5813 tok)
  - fn `create_chain_orchestrator` L739-743 (~46 tok)
  - fn `create_sequential_workflow` L744-791 (~350 tok)
- `meta_prompts.py` — from: to_prompt_section, create (~7433 tok)
  - class `MetaPromptType` L23-36 (~115 tok)
  - class `SubAgent` L37-53 (~123 tok)
  - class `MetaPromptFactory` L54-460 (~3189 tok)
  - fn `sample_data` L461-466 (~27 tok)
  - fn `mock_dependencies` L467-476 (~89 tok)
  - class `TestFunctionName` L477-825 (~2499 tok)
  - fn `create_` L826-949 (~1247 tok)
- `rag_mcp_hybrid.py` — View: get, put (~13430 tok)
  - class `DocumentType` L82-92 (~54 tok)
  - class `RetrievalStrategy` L93-107 (~144 tok)
  - class `MCPPrimitive` L108-123 (~88 tok)
  - class `Document` L124-152 (~257 tok)
  - class `RetrievalResult` L153-162 (~49 tok)
  - class `RAGResponse` L163-180 (~161 tok)
  - class `QueryCache` L181-247 (~649 tok)
  - class `TextChunker` L248-352 (~1039 tok)
  - class `EmbeddingEngine` L353-437 (~888 tok)
  - class `VectorStore` L438-708 (~2874 tok)
  - class `RAGEngine` L709-874 (~1575 tok)
  - class `MCPRAGServer` L875-1041 (~1638 tok)
  - class `RAGMCPHybridSystem` L1042-1197 (~1509 tok)
  - fn `create_rag_router` L1198-1348 (~1667 tok)
- `task_templates.py` — TaskCategory: to_dict, create_ecommerce_task (~6833 tok)
  - class `TaskCategory` L27-38 (~76 tok)
  - class `TaskPriority` L39-48 (~44 tok)
  - class `TaskContext` L49-74 (~245 tok)
  - class `TaskTemplateFactory` L75-936 (~6049 tok)
  - fn `create_task_factory` L937-941 (~41 tok)
  - fn `create_task_context` L942-974 (~220 tok)
- `technique_engine.py` — from: to_prompt, to_prompt, to_prompt, to_prompt + 4 more (~9083 tok)
  - class `PromptTechnique` L26-41 (~140 tok)
  - class `TaskComplexity` L42-51 (~91 tok)
  - class `RoleDefinition` L52-78 (~246 tok)
  - class `Constraint` L79-97 (~150 tok)
  - class `OutputFormat` L98-128 (~268 tok)
  - class `FewShotExample` L129-147 (~143 tok)
  - class `ThoughtBranch` L148-169 (~184 tok)
  - class `ReActStep` L170-187 (~146 tok)
  - class `PromptTechniqueEngine` L188-857 (~7010 tok)
  - fn `create_agent_prompt` L858-914 (~467 tok)

## public/draco/

- `draco_decoder.js` — isVersionSupported: locateFile, logExceptionOnExit, instantiate + 3 more (~205546 tok)
- `draco_encoder.js` — isVersionSupported: shell_read, readBinary, shell_read + 24 more (~265348 tok)
- `draco_wasm_wrapper.js` — n: l, f, v + 13 more (~16790 tok)
- `README.md` — Project documentation (~327 tok)

## public/experiences/

- `black-rose.html` — BLACK ROSE Collection | SkyyRose Virtual Garden (~9020 tok)
- `love-hurts.html` — LOVE HURTS Collection | SkyyRose Virtual Castle (~10271 tok)
- `signature.html` — SIGNATURE Collection | SkyyRose Virtual Runway (~10217 tok)

## screenshots/root-audit/

- `blackrose-grid-snapshot.yml` (~11362 tok)
- `blackrose-grid-snapshot2.yml` (~11349 tok)
- `blackrose-hero-snapshot.yml` (~11233 tok)
- `blackrose-hero-snapshot2.yml` (~11394 tok)
- `home-cards-snapshot.yml` (~11304 tok)
- `home-top-nav.yml` (~11562 tok)
- `mobile-nav-fresh.yml` (~11579 tok)
- `preorder-reserve-snapshot.yml` (~10531 tok)

## scripts/

- `__init__.py` (~0 tok)
- `3D_GENERATION_STATUS.md` — 3D Generation Status - READY (API Key Required) (~1003 tok)
- `add_love_hurts_and_logos_to_lora.py` — luxury_post_process, upscale_with_lanczos, detect_garment_type, generate_training_caption + 2 more (~4004 tok)
  - fn `luxury_post_process` L75-94 (~178 tok)
  - fn `upscale_with_lanczos` L95-115 (~224 tok)
  - fn `detect_garment_type` L116-182 (~738 tok)
  - fn `generate_training_caption` L183-233 (~448 tok)
  - fn `enhance_and_add_to_dataset` L234-275 (~354 tok)
  - fn `main` L276-398 (~1346 tok)
- `add_requirements_txt.py` (~540 tok)
- `ai_config.py` — AI CLI configuration and constants. (~447 tok)
- `ai_providers.py` — Training providers for AI CLI — HuggingFace and Replicate. (~1125 tok)
  - class `TrainingProvider` L35-50 (~128 tok)
  - class `ReplicateProvider` L51-85 (~378 tok)
  - class `HuggingFaceProvider` L86-124 (~341 tok)
- `ai_templates.py` — Embedded HF Space templates for AI CLI. (~1475 tok)
  - fn `install_dependencies` L13-25 (~100 tok)
  - fn `train_lora` L26-139 (~1126 tok)
  - fn `render_trainer_app` L140-155 (~155 tok)
  - fn `render_requirements` L156-159 (~35 tok)
- `ai.py` — Unified AI CLI for SkyyRose — training, datasets, Spaces, models. (~2640 tok)
  - fn `spaces_list` L28-47 (~168 tok)
  - fn `spaces_status` L48-62 (~163 tok)
  - fn `spaces_restart` L63-71 (~92 tok)
  - fn `spaces_hardware` L72-80 (~103 tok)
  - fn `spaces_deploy` L81-118 (~343 tok)
  - fn `train_run` L119-142 (~260 tok)
  - fn `train_status` L143-164 (~220 tok)
  - fn `train_logs` L165-185 (~187 tok)
  - fn `dataset_info` L186-197 (~118 tok)
  - fn `dataset_push` L198-228 (~301 tok)
  - fn `model_list` L229-248 (~174 tok)
  - fn `model_info` L249-263 (~152 tok)
  - fn `model_download` L264-279 (~159 tok)
- `anatomy_filter_main.py` — Filter .wolf/anatomy.md to entries tracked on git main. (~1127 tok)
  - fn `_git_ls_tree` L29-41 (~100 tok)
  - fn `canonical_files` L42-56 (~127 tok)
  - fn `_section_dir` L57-64 (~55 tok)
  - fn `filter_anatomy` L65-111 (~390 tok)
  - fn `update_header_files_count` L112-121 (~87 tok)
  - fn `main` L122-138 (~148 tok)
- `approve_ghost.py` — approve-ghost {sku} — move reviewed image to approved/ and update CSV. (~553 tok)
  - fn `build_parser` L26-43 (~174 tok)
  - fn `main` L44-64 (~183 tok)
- `audit_dossier_coverage.py` — Audit dossier completeness across every active SKU in the canonical CSV. (~1722 tok)
  - fn `main` L39-102 (~568 tok)
  - fn `_summarize` L103-127 (~240 tok)
  - fn `_render_markdown` L128-168 (~474 tok)
  - fn `_render_summary_text` L169-181 (~113 tok)
- `audit_golden_coverage.py` — Audit golden-reference coverage across every active SKU. (~1557 tok)
  - fn `main` L36-115 (~796 tok)
  - fn `_render_markdown` L116-160 (~479 tok)
- `audit_prompts.py` — Audit nano-banana prompts against real product images. (~2365 tok)
  - fn `_find_image_for_sku` L41-54 (~116 tok)
  - fn `_minimal_prompt` L55-64 (~136 tok)
  - fn `main` L65-216 (~1776 tok)
- `audit_source_photos.py` — Audit source product photography coverage and emit a structured manifest. (~5479 tok)
  - fn `_infer_garment_type` L153-161 (~110 tok)
  - fn `_normalize_garment_type` L162-172 (~110 tok)
  - fn `_required_angles` L173-177 (~45 tok)
  - class `SkuPhotoCoverage` L178-190 (~124 tok)
  - class `PhotoCollisionError` L191-195 (~42 tok)
  - class `_PhotoCandidate` L196-200 (~22 tok)
  - fn `_normalize_angle` L201-210 (~77 tok)
  - fn `_asset_kind_priority` L211-227 (~129 tok)
  - fn `_select_candidate` L228-248 (~263 tok)
  - fn `_scan_files` L249-308 (~654 tok)
  - fn `_build_coverage_for` L309-366 (~585 tok)
  - fn `_summarize` L367-382 (~178 tok)
  - fn `_render_audit_md` L383-420 (~467 tok)
  - fn `_render_shoot_list_md` L421-467 (~562 tok)
  - fn `build_manifest` L468-484 (~212 tok)
  - fn `main` L485-515 (~355 tok)
- `batch_3d_generation.py` — URL configuration (~7092 tok)
  - class `AssetInfo` L100-120 (~145 tok)
  - class `GenerationResult` L121-135 (~124 tok)
  - class `BatchProgress` L136-213 (~785 tok)
  - fn `discover_assets` L214-263 (~472 tok)
  - class `BatchGenerator` L264-498 (~2431 tok)
  - fn `populate_qa_queue` L499-539 (~440 tok)
  - fn `generate_report` L540-653 (~1017 tok)
  - fn `main` L654-720 (~538 tok)
  - fn `parse_args` L721-776 (~397 tok)
- `batch_enhance_clothing.py` — enhance_all_images (~813 tok)
  - fn `enhance_all_images` L22-94 (~678 tok)
- `batch_flux_collections.py` — Batch FLUX synthesis pipeline — Love Hurts + Signature collections. (~2490 tok)
  - fn `_load_manifest` L61-92 (~364 tok)
  - fn `_print_plan` L93-103 (~118 tok)
  - fn `_run_view` L104-143 (~314 tok)
  - fn `main` L144-258 (~1107 tok)
- `batch_product_processor_original_colors.sh` — Batch Product Image Processor (ORIGINAL COLORS PRESERVED) (~1319 tok)
- `batch_product_processor.sh` — ############################################################################## (~1579 tok)
- `batch_upload_mcp.py` — extract_collection, clean_title, main (~810 tok)
  - fn `extract_collection` L18-28 (~89 tok)
  - fn `clean_title` L29-39 (~113 tok)
  - fn `main` L40-96 (~483 tok)
- `benchmark_performance.py` — class: calculate_percentile, create_result, benchmark_embedding_cache, benchmark_reranking_cache + 8 more (~3718 tok)
  - class `BenchmarkResult` L37-64 (~205 tok)
  - fn `calculate_percentile` L65-73 (~86 tok)
  - fn `create_result` L74-89 (~186 tok)
  - fn `benchmark_embedding_cache` L90-139 (~434 tok)
  - fn `benchmark_reranking_cache` L140-194 (~476 tok)
  - fn `benchmark_vector_search_cache` L195-243 (~444 tok)
  - fn `benchmark_parallel_processing` L244-289 (~404 tok)
  - fn `benchmark_semaphore_limiting` L290-348 (~580 tok)
  - fn `print_summary` L349-384 (~399 tok)
  - fn `main` L385-412 (~291 tok)
- `bug322_sig_commerce_audit.py` — bug-322 follow-up: git-only sha256 audit of 21 stale SIG-COMMERCE contract bindings vs codex/final-scenes-e2e-20260830; --deep hashes every blob in .git (all refs/reflogs/unreachable) with provenance; gated (--fire, manifest, y) Agents API 3-subagent delegation (~6517 tok)
- `build_asset_manifest.py` — Generate ``assets/products/manifest.json`` — the content-hashed SKU→asset map. (~2066 tok)
  - fn `_catalog_rows` L49-61 (~130 tok)
  - fn `_record` L62-68 (~82 tok)
  - fn `_directional_source_records` L69-85 (~188 tok)
  - fn `build` L86-130 (~498 tok)
  - fn `report` L131-160 (~332 tok)
  - fn `main` L161-194 (~336 tok)
- `build_brand_centroid.py` — Build the SkyyRose brand-style centroid from approved hero shots. (~675 tok)
  - fn `main` L28-75 (~485 tok)
- `build_complete_luxury_pages.py` — Build COMPLETE Luxury Experience Pages for SkyyRose. (~5341 tok)
  - fn `get_wordpress_media_assets` L120-175 (~639 tok)
  - fn `generate_custom_css` L176-346 (~1066 tok)
  - fn `generate_product_gallery_html` L347-385 (~424 tok)
  - fn `generate_hf_spaces_html` L386-457 (~767 tok)
  - fn `generate_complete_page_html` L458-495 (~328 tok)
  - fn `update_experience_page` L496-552 (~587 tok)
  - fn `main` L553-594 (~421 tok)
- `build_lora_v4_dataset.py` — copy_and_prepare_image (~5180 tok)
  - fn `copy_and_prepare_image` L260-288 (~337 tok)
  - fn `write_caption` L289-297 (~98 tok)
  - fn `main` L298-417 (~1330 tok)
- `build_lora_v5_dataset.py` — sku_to_trigger, read_catalog (~6081 tok)
  - fn `sku_to_trigger` L44-48 (~34 tok)
  - fn `read_catalog` L49-320 (~3692 tok)
  - fn `copy_and_prepare_image` L321-338 (~232 tok)
  - fn `write_caption` L339-342 (~40 tok)
  - fn `build_caption` L343-348 (~72 tok)
  - fn `main` L349-508 (~1601 tok)
- `build_product_similarities.py` — Pre-compute the top-N visually-similar SKUs for the [skyyrose_visual_similar] widget. (~988 tok)
  - fn `main` L45-108 (~646 tok)
- `build_v7_cards.py` — build_v7_cards.py — Generate the V7 lookbook card store as a DERIVED VIEW. (~2216 tok)
  - fn `_shots_for` L80-100 (~261 tok)
  - fn `build_cards` L101-130 (~347 tok)
  - fn `build_document` L131-141 (~90 tok)
  - fn `serialize` L142-148 (~56 tok)
  - fn `main` L149-193 (~414 tok)
- `build-lookbook-from-sot.py` — Generate a lightweight editorial lookbook from a single SOT document. (~2677 tok)
  - fn `esc` L26-29 (~29 tok)
  - fn `resolve_asset` L30-35 (~44 tok)
  - fn `product_cover` L36-50 (~139 tok)
  - fn `render_collection` L51-122 (~769 tok)
  - fn `build_html` L123-168 (~672 tok)
  - fn `parse_args` L169-188 (~171 tok)
  - fn `normalize_collection_entries` L189-217 (~324 tok)
  - fn `build_title` L218-227 (~110 tok)
  - fn `build_lookbook_html` L228-237 (~120 tok)
  - fn `main` L238-252 (~116 tok)
- `build-lookbook-mask.py` — Build a garment-preserving mask for a gpt-image-2 masked edit (FREE, local). (~2207 tok)
  - fn `crop_to_aspect` L56-68 (~146 tok)
  - fn `clean_alpha` L69-92 (~262 tok)
  - fn `segment_by_boxes` L93-112 (~218 tok)
  - fn `build_mask` L113-145 (~330 tok)
  - fn `main` L146-196 (~592 tok)
- `build-lookbook-sot.py` — Build a single aggregated lookbook SOT from per-collection SOT files. (~2049 tok)
  - fn `parse_args` L32-63 (~276 tok)
  - fn `load_manifest_sources` L64-110 (~546 tok)
  - fn `load_collections_from_manifest` L111-117 (~64 tok)
  - fn `load_collections_from_dir` L118-135 (~203 tok)
  - fn `build_lookbook_payload` L136-161 (~262 tok)
  - fn `serialize` L162-166 (~48 tok)
  - fn `main` L167-210 (~401 tok)
- `build-site-guide.py` — build-site-guide.py — generate data/site-guide.json for the Skyy mascot guide brain. (~3057 tok)
  - fn `slugify` L60-66 (~63 tok)
  - fn `title_case_slug` L67-71 (~46 tok)
  - fn `extract_menu_items` L72-84 (~137 tok)
  - fn `extract_page_registry` L85-93 (~105 tok)
  - fn `extract_footer_legal_links` L94-105 (~108 tok)
  - fn `extract_collections` L106-115 (~110 tok)
  - fn `build_pages` L116-166 (~529 tok)
  - fn `build_intents` L167-228 (~594 tok)
  - fn `generate` L229-273 (~539 tok)
  - fn `main` L274-288 (~133 tok)
- `capture_goldens.py` — Curate golden reference images for visual-regression scoring. (~1330 tok)
  - fn `_validate_image` L39-61 (~238 tok)
  - fn `_confirm` L62-67 (~50 tok)
  - fn `_capture_one` L68-86 (~187 tok)
  - fn `main` L87-139 (~558 tok)
- `capture_v2_woocommerce_authority.py` — Create a local, read-only WooCommerce authority receipt for the V2 catalog. (~1487 tok)
  - fn `sha256` L29-32 (~26 tok)
  - fn `git_head` L33-36 (~36 tok)
  - fn `configuration` L37-49 (~167 tok)
  - fn `catalog` L50-54 (~52 tok)
  - fn `product_record` L55-71 (~176 tok)
  - fn `main` L72-139 (~802 tok)
- `catalog_ml_audit.py` — ML audit on the canonical catalog CSV. (~4255 tok)
  - fn `_load_embeddings_matrix` L58-65 (~96 tok)
  - fn `_attach_catalog` L66-79 (~147 tok)
  - fn `cluster_vs_collections` L80-125 (~520 tok)
  - fn `per_collection_outliers` L126-160 (~385 tok)
  - fn `name_image_alignment` L161-190 (~296 tok)
  - fn `top_n_similar` L191-215 (~239 tok)
  - fn `cross_collection_anomalies` L216-242 (~305 tok)
  - fn `emit_markdown` L243-333 (~1112 tok)
  - fn `main` L334-383 (~604 tok)
- `check_catalog_duplicates.py` — Detect near-duplicate SKUs by CLIP embedding similarity. (~430 tok)
- `check_dossier_coverage.py` — Confirm every active SKU has a per-product design dossier. (~884 tok)
  - fn `slugify` L32-38 (~44 tok)
  - fn `resolve_slug` L39-48 (~99 tok)
  - fn `main` L49-104 (~486 tok)
- `check_gitignore_health.py` — check_gitignore_health.py — Read-only .gitignore redundancy/duplication linter. (~1797 tok)
  - class `ContentLine` L41-47 (~60 tok)
  - fn `_content_lines` L48-58 (~108 tok)
  - fn `_normalize` L59-63 (~50 tok)
  - fn `find_duplicate_lines` L64-71 (~101 tok)
  - fn `find_redundant_recursive_patterns` L72-105 (~436 tok)
  - fn `build_report` L106-138 (~404 tok)
  - fn `main` L139-162 (~196 tok)
- `ci-local.sh` — scripts/ci-local.sh -- Offline mirror of ci.yml's six gating jobs (lint/python-tests/security/frontend/threejs/wordpress-theme); CI_LOCAL_ROOT overridable (~3887 tok)
- `ci-sim.sh` — scripts/ci-sim.sh -- Simulated CI clone: fetches a PR's merge preview (refs/pull/N/merge) or any ref into a disposable worktree and runs ci-local.sh there; PASS/FAIL verdict (~1850 tok)
- `claude-mem-settings.sh` — claude-mem-settings.sh — Interactive settings manager for ~/.claude-mem/settings.json (~3638 tok)
- `cleanup_phase2_ralph.py` — CleanupError: delete_file_safe, attempt_delete, archive_file_safe, attempt_archive + 6 more (~3003 tok)
  - class `CleanupError` L34-39 (~25 tok)
  - fn `delete_file_safe` L40-79 (~333 tok)
  - fn `archive_file_safe` L80-125 (~427 tok)
  - fn `delete_directory_safe` L126-165 (~349 tok)
  - fn `move_file_safe` L166-212 (~402 tok)
  - fn `cleanup_phase_2` L213-308 (~1166 tok)
  - fn `main` L309-321 (~86 tok)
- `composite_products.py` — encode_image_base64, call_fal_product_shot, poll_fal_result, download_image + 2 more (~3867 tok)
  - fn `encode_image_base64` L144-147 (~31 tok)
  - fn `call_fal_product_shot` L148-203 (~587 tok)
  - fn `poll_fal_result` L204-236 (~395 tok)
  - fn `download_image` L237-243 (~48 tok)
  - fn `process_scene` L244-318 (~771 tok)
  - fn `main` L319-363 (~444 tok)
- `consolidate_branches_ralph.py` — GitConsolidationError: run_git_command, merge_branch_squash, attempt_merge, consolidate_branches + 1 more (~2616 tok)
  - class `GitConsolidationError` L33-38 (~29 tok)
  - fn `run_git_command` L39-91 (~426 tok)
  - fn `merge_branch_squash` L92-201 (~1116 tok)
  - fn `consolidate_branches` L202-272 (~739 tok)
  - fn `main` L273-285 (~88 tok)
- `create_cpu_space_then_upgrade.py` — show_instructions (~1223 tok)
  - fn `show_instructions` L89-193 (~672 tok)
- `create_luxury_experience_pages.py` — Create Luxury Experience Pages for SkyyRose Collections. (~4854 tok)
  - fn `generate_signature_content` L45-137 (~1030 tok)
  - fn `generate_black_rose_content` L138-230 (~1222 tok)
  - fn `generate_love_hurts_content` L231-349 (~1282 tok)
  - fn `update_experience_page` L350-416 (~720 tok)
  - fn `main` L417-445 (~266 tok)
- `create_virtual_tryon_space.py` — Create virtual-tryon HuggingFace Space and push code with ralph-loop retry. (~1045 tok)
  - fn `main` L36-118 (~815 tok)
- `curate_centroid_test_set.py` — Curate the labeled good/bad render fixtures the centroid harness needs. (~2796 tok)
  - class `Candidate` L58-64 (~51 tok)
  - class `CurationResult` L65-69 (~39 tok)
  - fn `_discover_good` L70-84 (~183 tok)
  - fn `_discover_bad` L85-116 (~298 tok)
  - fn `_unique_target_name` L117-127 (~118 tok)
  - fn `_materialize` L128-149 (~236 tok)
  - fn `_wipe` L150-157 (~58 tok)
  - fn `_write_manifest` L158-171 (~142 tok)
  - fn `_write_readme` L172-215 (~465 tok)
  - fn `main` L216-270 (~507 tok)
- `demo_image_generation.py` — demo_replicate, demo_stability, compare_providers, main + 1 more (~3045 tok)
  - fn `demo_replicate` L23-121 (~905 tok)
  - fn `demo_stability` L122-243 (~1110 tok)
  - fn `compare_providers` L244-291 (~635 tok)
  - fn `main` L292-330 (~256 tok)
- `dependabot-batch-pr.sh` — Weekly Dependabot triage + batch-PR routine. (~1978 tok)
- `dependency_matrix.py` — Generate a domain-oriented dependency inventory and gap report. (~4395 tok)
  - fn `normalize_package_name` L58-74 (~115 tok)
  - fn `classify_domain` L75-118 (~362 tok)
  - fn `parse_package_json` L119-130 (~150 tok)
  - fn `parse_lockfile` L131-141 (~112 tok)
  - fn `parse_pyproject` L142-159 (~178 tok)
  - fn `parse_requirements` L160-173 (~122 tok)
  - fn `is_unpinned` L174-178 (~40 tok)
  - fn `is_manifest` L179-184 (~53 tok)
  - fn `collect_manifests` L185-205 (~201 tok)
  - fn `build_matrix` L206-335 (~1426 tok)
  - fn `render_markdown` L336-395 (~793 tok)
  - fn `main` L396-434 (~476 tok)
- `deploy_elementor_templates.py` — ElementorDeployer: get_page_by_slug, deploy_template, deploy_all, main (~1786 tok)
  - class `ElementorDeployer` L14-147 (~1362 tok)
  - fn `main` L148-189 (~373 tok)
- `deploy_hf_spaces.sh` — HuggingFace Spaces Deployment Script (~1377 tok)
- `deploy_skyyrose_site.py` — Pydantic: DeploymentConfig (57 fields) (~6703 tok)
  - class `DeploymentConfig` L46-100 (~564 tok)
  - class `DeploymentPhase` L101-119 (~198 tok)
  - class `DeploymentSummary` L120-150 (~292 tok)
  - class `SkyyRoseDeploymentOrchestrator` L151-581 (~4664 tok)
  - fn `main` L582-661 (~638 tok)
- `deploy_to_fastmcp.sh` — Deploy DevSkyy MCP to FastMCP (critical-fuchsia-ape) (~2462 tok)
- `deploy_to_skyyrose.py` — WordPressDeployer: deploy_pages, upload_3d_models, create_woocommerce_products, deploy_elementor_templates + 2 more (~3979 tok)
  - class `WordPressDeployer` L33-339 (~3456 tok)
  - fn `main` L340-379 (~333 tok)
- `deploy-holo-cards.sh` — scripts/deploy-holo-cards.sh -- Deploy Holo product card rollout to production (~3234 tok)
- `deploy-mu-plugin.sh` — scripts/deploy-mu-plugin.sh -- SCP one MU-plugin (MU_SRC param, dest=basename) to wp-content/mu-plugins/ + nonce-endpoint verify; STOPSHOW_ACK-gated (~1048 tok)
- `deploy-pipeline.sh` — scripts/deploy-pipeline.sh -- Single-command deploy pipeline for SkyyRose WordPress theme (~1847 tok)
- `deploy-theme.sh` — scripts/deploy-theme.sh -- Production deploy script for SkyyRose WordPress theme (~13969 tok)
- `designqc-playwright.mjs` — Captures desktop and mobile visual-QA evidence without OpenWolf's (~644 tok)
- `diagnose_cli_raw.py` — Build the exact CLI command the SDK would use and run it via subprocess (~507 tok)
- `diagnose_orchestrator.py` — Test ClaudeSDKClient (async context manager) with MCP server. (~665 tok)
  - fn `stderr_callback` L24-27 (~33 tok)
  - fn `main` L28-79 (~477 tok)
- `diagnose_sdk.py` — Diagnostic: capture exact claude CLI stderr when SDK fails. (~554 tok)
  - fn `stderr_callback` L25-29 (~53 tok)
  - fn `main` L30-66 (~329 tok)
- `diagnose_tripo_api.py` — test_api_connection, test_task_polling, test_image_to_3d, main (~3042 tok)
  - fn `test_api_connection` L24-151 (~1385 tok)
  - fn `test_task_polling` L152-200 (~567 tok)
  - fn `test_image_to_3d` L201-280 (~761 tok)
  - fn `main` L281-309 (~220 tok)
- `docker-secrets.sh` — Generate .env.docker from .env.docker.example with strong random secrets. (~578 tok)
- `docs_scraper.py` — Bright Data SERP API — Documentation Scraper (~8295 tok)
  - class `SERPResult` L246-254 (~37 tok)
  - class `DocPage` L255-270 (~88 tok)
  - class `DocCollection` L271-286 (~122 tok)
  - class `BrightDataSERPClient` L287-431 (~1565 tok)
  - class `OfficialDocsFilter` L432-484 (~534 tok)
  - fn `parse_serp_response` L485-549 (~702 tok)
  - fn `_html_to_text` L550-599 (~595 tok)
  - fn `slugify` L600-605 (~58 tok)
  - fn `_build_doc_query` L606-615 (~120 tok)
  - class `DocsScraper` L616-772 (~1600 tok)
  - fn `_parse_args` L773-830 (~525 tok)
  - fn `main` L831-907 (~796 tok)
- `download_and_test_lora.py` — check_training_complete, download_lora_model, test_lora_inference, main (~1904 tok)
  - fn `check_training_complete` L31-49 (~133 tok)
  - fn `download_lora_model` L50-86 (~351 tok)
  - fn `test_lora_inference` L87-188 (~906 tok)
  - fn `main` L189-229 (~342 tok)
- `download_models.sh` — Download SDXL and related models for local image generation (~641 tok)
- `ecommerce_image_pro.py` — EcomSize: upscale_image, remove_background, create_white_background, resize_contain + 2 more (~5691 tok)
  - class `EcomSize` L71-101 (~261 tok)
  - class `ProcessingResult` L102-114 (~92 tok)
  - class `EcommerceImageProcessor` L115-444 (~3402 tok)
  - fn `main` L445-582 (~1442 tok)
- `enhance_assets_huggingface.py` — setup_logging, print_banner, print_result_summary, enhance_single + 2 more (~6366 tok)
  - fn `setup_logging` L56-78 (~228 tok)
  - fn `print_banner` L79-97 (~306 tok)
  - fn `print_result_summary` L98-149 (~586 tok)
  - fn `enhance_single` L150-202 (~475 tok)
  - fn `enhance_collection` L203-264 (~534 tok)
  - fn `enhance_all_collections` L265-354 (~876 tok)
  - fn `list_models` L355-386 (~310 tok)
  - fn `check_environment` L387-508 (~1319 tok)
  - fn `create_parser` L509-612 (~1058 tok)
  - fn `main` L613-645 (~201 tok)
- `enhance_brand_image.py` — Enhance a brand-asset or product-reference image to canonical quality. (~1617 tok)
  - fn `enhance` L38-86 (~536 tok)
  - fn `save` L87-102 (~172 tok)
  - fn `main` L103-148 (~509 tok)
- `enhance_captions_exact_replica.py` — extract_product_name, detect_collection, create_exact_replica_caption, enhance_dataset_captions + 2 more (~2382 tok)
  - fn `extract_product_name` L58-72 (~126 tok)
  - fn `detect_collection` L73-85 (~110 tok)
  - fn `create_exact_replica_caption` L86-112 (~248 tok)
  - fn `enhance_dataset_captions` L113-177 (~599 tok)
  - fn `validate_captions` L178-229 (~496 tok)
  - fn `main` L230-267 (~297 tok)
- `enhance_colors_for_3d.py` — enhance_for_3d, process_collection, main (~1331 tok)
  - fn `enhance_for_3d` L14-72 (~498 tok)
  - fn `process_collection` L73-106 (~305 tok)
  - fn `main` L107-156 (~454 tok)
- `enhance_product_images.py` — ExportSize: ensure_dependencies, production, fast, find_images + 3 more (~9114 tok)
  - fn `ensure_dependencies` L61-113 (~392 tok)
  - class `ExportSize` L114-134 (~131 tok)
  - class `EnhancementConfig` L135-182 (~380 tok)
  - class `EnhancementResult` L183-195 (~100 tok)
  - class `ImageEnhancementPipeline` L196-847 (~6678 tok)
  - fn `print_banner` L848-867 (~227 tok)
  - fn `main` L868-961 (~727 tok)
- `enhance_real_products.py` — detect_collection, luxury_post_process, upscale_with_realesrgan, upscale_with_lanczos + 2 more (~2429 tok)
  - fn `detect_collection` L28-38 (~108 tok)
  - fn `luxury_post_process` L39-58 (~178 tok)
  - fn `upscale_with_realesrgan` L59-97 (~340 tok)
  - fn `upscale_with_lanczos` L98-103 (~69 tok)
  - fn `enhance_product_photo` L104-161 (~512 tok)
  - fn `main` L162-257 (~1032 tok)
- `enhance_with_ai_pipeline.py` — class: connect, close, generate_with_flux, generate_with_sdxl + 2 more (~10483 tok)
  - class `EnhancementResult` L174-193 (~175 tok)
  - class `HuggingFaceTopModels` L194-456 (~2622 tok)
  - class `GeminiNanaBananaPro` L457-559 (~1062 tok)
  - class `LoRATrainingPipeline` L560-673 (~1162 tok)
  - class `AIEnhancementPipeline` L674-950 (~3125 tok)
  - fn `print_banner` L951-970 (~343 tok)
  - fn `print_results` L971-989 (~204 tok)
  - fn `main` L990-1030 (~417 tok)
- `enhance-product-images.ts` — Non-Destructive Product Image Enhancement (~1188 tok)
  - fn `applyLuxuryGrading` L36-57 (~214 tok)
  - fn `main` L58-130 (~608 tok)
- `evaluate_product_photos.py` — Product Photo Evaluation Script. (~6142 tok)
  - class `PhotoQuality` L45-55 (~90 tok)
  - class `PhotoMetrics` L56-88 (~219 tok)
  - class `CollectionSummary` L89-102 (~79 tok)
  - class `PhotoEvaluator` L103-340 (~2512 tok)
  - class `PhotoEvaluationReport` L341-546 (~2126 tok)
  - fn `main` L547-632 (~801 tok)
- `expand_brand_voice_dataset.py` — generate_response, expand_dataset (~4612 tok)
  - fn `generate_response` L225-250 (~263 tok)
  - fn `expand_dataset` L251-389 (~1604 tok)
- `export_luxury_templates.py` — export_templates (~1323 tok)
  - fn `export_templates` L37-122 (~1006 tok)
- `export_round_table_to_hf.py` — validate_dataset_name, validate_collections, load_round_table_results, transform_to_hf_dataset + 3 more (~3455 tok)
  - fn `validate_dataset_name` L58-67 (~96 tok)
  - fn `validate_collections` L68-96 (~306 tok)
  - fn `load_round_table_results` L97-119 (~236 tok)
  - fn `transform_to_hf_dataset` L120-191 (~706 tok)
  - fn `save_local_export` L192-229 (~339 tok)
  - fn `upload_to_huggingface` L230-276 (~375 tok)
  - fn `main` L277-374 (~918 tok)
- `extract_all_collections.py` — Extract all product collection ZIP files from Desktop. (~703 tok)
  - fn `extract_zip` L14-50 (~309 tok)
  - fn `main` L51-91 (~315 tok)
- `extract_and_deploy_skyyrose.py` — SkyyRoseDeploymentOrchestrator: phase_1_5_generate_3d_models, phase_2_generate_templates, phase_3_deploy_pages, run + 1 more (~3035 tok)
  - class `SkyyRoseDeploymentOrchestrator` L46-261 (~2585 tok)
  - fn `main` L262-278 (~116 tok)
- `extract_higgsfield_context.py` — Manually extract grounded Higgsfield context for internal pipeline research. (~1736 tok)
  - fn `parse_args` L132-141 (~165 tok)
  - fn `main` L142-163 (~173 tok)
- `extract_skyyrose_assets.py` — AssetExtractor: extract_zip, create_directory_structure, categorize_file, organize_files + 5 more (~3104 tok)
  - class `AssetExtractor` L70-302 (~2430 tok)
  - fn `main` L303-333 (~195 tok)
- `fix_and_redeploy_spaces.py` — Fix and redeploy all HuggingFace Spaces with correct dependencies (ralph-loop retry). (~1086 tok)
  - fn `upload_space_with_retry` L53-90 (~350 tok)
  - fn `main` L91-128 (~382 tok)
- `fix_elementor_spinning_logo.py` — get_spinning_logo_html, make_request, update_elementor_widget, update_recursive + 4 more (~2617 tok)
  - fn `get_spinning_logo_html` L33-74 (~623 tok)
  - fn `make_request` L75-91 (~180 tok)
  - fn `update_elementor_widget` L92-113 (~221 tok)
  - fn `detect_variant_from_shortcode` L114-121 (~70 tok)
  - fn `process_page` L122-226 (~1096 tok)
  - fn `main` L227-256 (~212 tok)
- `fix_spinning_logo_shortcode.py` — make_request, replace_shortcode, replacement, get_elementor_data + 3 more (~3326 tok)
  - fn `make_request` L128-144 (~180 tok)
  - fn `replace_shortcode` L145-159 (~153 tok)
  - fn `get_elementor_data` L160-176 (~161 tok)
  - fn `update_page_content` L177-192 (~174 tok)
  - fn `process_page` L193-239 (~482 tok)
  - fn `main` L240-269 (~207 tok)
- `format_staged.sh` — scripts/format_staged.sh — Pre-format every git-staged file by type. (~2994 tok)
- `freshness-guard.sh` — scripts/freshness-guard.sh — keep derived files in sync with their sources. (~3248 tok)
- `gemini_lookbook.py` — load_image_bytes, generate_lookbook (~4552 tok)
  - fn `load_image_bytes` L189-210 (~209 tok)
  - fn `generate_lookbook` L211-335 (~1492 tok)
  - fn `main` L336-373 (~343 tok)
- `gemini_scene_gen.py` — build_prompt (~6602 tok)
  - fn `build_prompt` L225-255 (~314 tok)
  - fn `get_client` L256-266 (~88 tok)
  - fn `generate_scene` L267-312 (~434 tok)
  - fn `convert_to_webp` L313-338 (~218 tok)
  - fn `process_scene` L339-391 (~583 tok)
  - fn `main` L392-505 (~1161 tok)
- `gen_signature_emblem.py` — One-off: generate Signature collection emblem candidates via gpt-image-2. (~791 tok)
  - fn `main` L42-74 (~274 tok)
- `gen_v7_avif.py` — Generate AVIF siblings for every V7 product-card shot (webp/png/jpg → .avif). (~663 tok)
  - fn `_current` L34-38 (~59 tok)
  - fn `main` L39-67 (~259 tok)
- `gen-hero-previews.py` — Immersive Hub hero-scene PREVIEW generator (OpenAI + open-model FLUX). (~4572 tok)
  - class `Scene` L58-175 (~1962 tok)
  - fn `gen_openai` L176-200 (~248 tok)
  - fn `gen_replicate` L201-220 (~176 tok)
  - fn `_read_replicate_output` L221-247 (~322 tok)
  - fn `build_manifest` L248-288 (~434 tok)
  - fn `run` L289-325 (~530 tok)
  - fn `main` L326-363 (~328 tok)
- `gen-lookbook-remake.py` — Lookbook remake via gpt-image-2 EDIT (garment-preserving). (~2805 tok)
  - fn `_as_upload` L96-105 (~123 tok)
  - fn `gen_edit` L106-128 (~221 tok)
  - fn `build_manifest` L129-161 (~388 tok)
  - fn `run` L162-207 (~579 tok)
  - fn `main` L208-249 (~401 tok)
- `gen3d_simple.py` — generate_3d_model, main (~1922 tok)
  - fn `generate_3d_model` L17-135 (~1257 tok)
  - fn `main` L136-207 (~577 tok)
- `generate_2d_25d_assets.py` — generate_angle_views, generate_360_spin_frames, generate_depth_layers, generate_product_2d_25d_assets + 1 more (~3000 tok)
  - fn `generate_angle_views` L71-126 (~499 tok)
  - fn `generate_360_spin_frames` L127-183 (~505 tok)
  - fn `generate_depth_layers` L184-234 (~421 tok)
  - fn `generate_product_2d_25d_assets` L235-282 (~412 tok)
  - fn `main` L283-330 (~498 tok)
- `generate_2d_25d_visualizations.py` — create_drop_shadow, create_depth_effect, create_parallax_layers, create_enhanced_detail + 3 more (~3548 tok)
  - fn `create_drop_shadow` L57-109 (~454 tok)
  - fn `create_depth_effect` L110-150 (~373 tok)
  - fn `create_parallax_layers` L151-210 (~551 tok)
  - fn `create_enhanced_detail` L211-240 (~233 tok)
  - fn `generate_all_variations` L241-305 (~650 tok)
  - fn `main` L306-394 (~856 tok)
- `generate_3d_color_accurate.py` — Tripo3DClient: upload_image, create_task, get_task_status, download_model + 3 more (~2889 tok)
  - class `Tripo3DClient` L24-77 (~531 tok)
  - fn `generate_3d_model` L78-170 (~965 tok)
  - fn `discover_products` L171-197 (~232 tok)
  - fn `main` L198-304 (~1032 tok)
- `generate_3d_direct.py` — generate_exact_replica, main (~1703 tok)
  - fn `generate_exact_replica` L27-108 (~767 tok)
  - fn `main` L109-192 (~771 tok)
- `generate_3d_http.py` — Tripo3DClient: upload_image, create_task, get_task_status, download_model + 2 more (~2448 tok)
  - class `Tripo3DClient` L16-70 (~548 tok)
  - fn `generate_3d_model` L71-171 (~1040 tok)
  - fn `main` L172-267 (~791 tok)
- `generate_3d_models_from_assets.py` — Pydantic: CollectionMetadata (31 fields) (~4137 tok)
  - class `CollectionMetadata` L38-50 (~179 tok)
  - class `ModelGenerationPipeline` L51-356 (~3232 tok)
  - fn `main` L357-420 (~477 tok)
- `generate_3d_models_official_sdk.py` — get_image_files, generate_3d_model, batch_generate_models, main (~3392 tok)
  - fn `get_image_files` L44-75 (~260 tok)
  - fn `generate_3d_model` L76-147 (~754 tok)
  - fn `batch_generate_models` L148-242 (~966 tok)
  - fn `main` L243-344 (~1115 tok)
- `generate_3d_models.py` — upload_image, create_3d_task, wait_for_task, download_model + 2 more (~1753 tok)
  - fn `upload_image` L50-76 (~259 tok)
  - fn `create_3d_task` L77-97 (~200 tok)
  - fn `wait_for_task` L98-122 (~246 tok)
  - fn `download_model` L123-130 (~86 tok)
  - fn `generate_model` L131-161 (~270 tok)
  - fn `main` L162-195 (~302 tok)
- `generate_3d_trellis.py` — is_clothing_item, find_clothing_images, generate_3d_trellis, main (~2459 tok)
  - fn `is_clothing_item` L56-61 (~60 tok)
  - fn `find_clothing_images` L62-77 (~172 tok)
  - fn `generate_3d_trellis` L78-137 (~558 tok)
  - fn `main` L138-280 (~1371 tok)
- `generate_ai_models_with_products.py` — detect_collection, extract_product_name, setup_pipeline, generate_model_with_product + 1 more (~2600 tok)
  - fn `detect_collection` L68-79 (~118 tok)
  - fn `extract_product_name` L80-88 (~88 tok)
  - fn `setup_pipeline` L89-130 (~483 tok)
  - fn `generate_model_with_product` L131-176 (~403 tok)
  - fn `main` L177-265 (~840 tok)

## scripts/_lib/

- `script-utils.js` — scripts/_lib/script-utils.js — shared utilities for the per-edit toolchain. (~543 tok)
  - fn `utcTimestamp` L24-33 (~120 tok)
  - fn `pathToSlug` L34-44 (~71 tok)
  - fn `deriveTaskId` L45-52 (~74 tok)
  - fn `run` L53-61 (~80 tok)

## scripts/clustering/

- `__init__.py` (~108 tok)
- `gallery_builder.py` — from: to_dict, build_galleries_from_clusters, save_galleries, generate_woocommerce_import + 1 more (~2089 tok)
  - class `ProductGallery` L24-52 (~266 tok)
  - class `GalleryBuilder` L53-232 (~1686 tok)
- `similarity_matcher.py` — from: compute_similarity_matrix, find_duplicates, find_variants, cluster_products + 1 more (~2862 tok)
  - class `SimilarityMatch` L21-43 (~232 tok)
  - class `ProductCluster` L44-56 (~93 tok)
  - class `SimilarityMatcher` L57-296 (~2406 tok)

## scripts/devworkflows/

- `review.sh` — Parallel lint review of changed files — ruff | tsc | phpcs (~1293 tok)
- `security.sh` — Parallel security gate on changed files — bandit | secret scan | npm audit (~1806 tok)
- `ship.sh` — Ship gate — composite pre-push gate. Fail-fast: cheap stages first. (~1112 tok)
- `tdd.sh` — TDD gate — RED / GREEN / coverage enforcement via pytest (~1096 tok)

## scripts/flux_lora/

- `__init__.py` — Declares FluxLoraError (~367 tok)
- `cli.py` — cmd_dataset_info, cmd_train, cmd_generate, cmd_status + 4 more (~4834 tok)
  - fn `_confirm` L70-83 (~134 tok)
  - fn `cmd_dataset_info` L84-104 (~212 tok)
  - fn `cmd_train` L105-184 (~772 tok)
  - fn `cmd_generate` L185-243 (~551 tok)
  - fn `cmd_status` L244-257 (~127 tok)
  - fn `cmd_build_dataset` L258-305 (~510 tok)
  - fn `cmd_upload_dataset` L306-345 (~326 tok)
  - fn `cmd_list` L346-368 (~216 tok)
  - fn `build_parser` L369-484 (~1256 tok)
  - fn `main` L485-500 (~109 tok)
- `config.py` — get_api_key, api_key_present, is_https_url (~1108 tok)
  - fn `get_api_key` L76-83 (~82 tok)
  - fn `api_key_present` L84-88 (~46 tok)
  - fn `is_https_url` L89-97 (~92 tok)
- `dataset_builder.py` — build_dataset (~1478 tok)
  - fn `_compose_caption` L32-67 (~323 tok)
  - fn `build_dataset` L68-156 (~843 tok)
- `dataset.py` — load_dataset, validate_dataset, pack_zip, dataset_summary (~1644 tok)
  - fn `_image_files` L25-33 (~108 tok)
  - fn `load_dataset` L34-77 (~388 tok)
  - fn `validate_dataset` L78-124 (~455 tok)
  - fn `pack_zip` L125-156 (~263 tok)
  - fn `dataset_summary` L157-185 (~235 tok)
- `inference.py` — load_latest_lora, generate (~2475 tok)
  - fn `load_latest_lora` L54-75 (~204 tok)
  - fn `_show_inference_stopandshow` L76-95 (~168 tok)
  - fn `_extract_output_urls` L96-108 (~128 tok)
  - fn `_poll_prediction` L109-135 (~324 tok)
  - fn `generate` L136-235 (~1110 tok)
- `status.py` — get_status, list_runs, format_status (~920 tok)
  - fn `get_status` L25-52 (~250 tok)
  - fn `list_runs` L53-72 (~169 tok)
  - fn `format_status` L73-107 (~314 tok)
- `trainer.py` — build_manifest, show_stopandshow, start_training, save_run_record (~3070 tok)
  - fn `build_manifest` L56-134 (~880 tok)
  - fn `show_stopandshow` L135-171 (~416 tok)
  - fn `_build_training_url` L172-192 (~249 tok)
  - fn `start_training` L193-270 (~772 tok)
  - fn `save_run_record` L271-304 (~328 tok)
- `upload.py` — show_upload_stopandshow, upload_zip (~1466 tok)
  - fn `_get_hf_token` L36-63 (~240 tok)
  - fn `show_upload_stopandshow` L64-100 (~305 tok)
  - fn `upload_zip` L101-183 (~614 tok)

## pipelines/blender_render/

Headless-Blender render worker (2026-09-17). Consumes the `blender_render` Redis
stream fed by `/api/v1/render-jobs`; two job types — `render_stills` (Cycles CPU
turntable PNGs) and `optimize_web` (sheen patch + gltfpack + web gate). Fails
CLOSED on every path.

- `models.py` — Pydantic v2 job models; key/SKU validation, `count·resolution²·samples ≤ 2e9` budget. (~1798 tok)
- `worker.py` — queue consumer: get→execute→update→ack wrapped, infra errors NACK×3 then ACK, `reclaim_pending` janitor, child kill on cancel, `check_still` opaque-RGB uniformity gate. (~5248 tok)
- `render_stills.py` — runs INSIDE Blender (bpy only): import glTF, frame camera to bbox, 3-light rig, transparent film, N stills. (~2560 tok)
- `artifacts.py` — keyed artifact store (Local + S3-compatible), atomic tmp+rename put, delete for rollback. (~1783 tok)
- `store.py` — job store; RedisJobStore subclass overriding only get/list. (~876 tok)
- `oneshot.py` — in-process single-job runner used for local E2E without Redis. (~1003 tok)

## api/v1/render_jobs/

- `router.py` — `/render-jobs` POST 202 + GET {job_id}/list/health. Mounted in `main_enterprise.py` (lazy `_IncludedRouter` — verify with TestClient, NOT `app.routes`; bug-330). 503 fail-closed when the artifact store is unconfigured. (~1850 tok)
- `schemas.py` — request/response envelopes matching the clothing_3d convention. (~248 tok)

## skyyrose/elite_studio/pipeline3d/ — web-GLB modules (2026-09-17)

- `glb_container.py` — lossless GLB I/O: rewrites ONLY the JSON chunk, walks every chunk and fails closed on BIN overrun / trailing junk / unpadded length / duplicate BIN / NaN literals. (~1246 tok)
- `glb_materials.py` — fabric classifier over founder prose (negation-stripping, exterior-shell precedence) + sheen presets per class; anisotropy opt-in only (AI atlases have no grain). (~2881 tok)
- `glb_optimize.py` — gltfpack `-cc -tc` wrapper + web gate (≤3MB, meshopt in extensionsRequired AND on a real bufferView, basisu, sheen VALUES valid, KTX2-only images). (~1790 tok)
- `webgl_qc.py` — renders a web GLB in the PRODUCTION three.js viewer (Playwright + loopback server over a temp serve root) and pixel-diffs variants; VIEWER_PARITY is parity-gated against product-3d-viewer.js; VOID (maxΔ=0) is distinct from "no visible difference". (~3900 tok)
- `templates/webgl_qc_harness.html` — the deterministic render page; PARITY/ANGLES are injected at serve time, un-injected it refuses to render. (~1700 tok)
