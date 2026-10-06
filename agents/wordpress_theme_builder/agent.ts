/**
 * WordPress Theme Builder Agent
 *
 * Full-stack agent that builds and deploys WordPress themes end-to-end.
 * Uses Claude Agent SDK with built-in tools + custom MCP tools for:
 *   1. Theme scaffolding (templates, parts, CSS, JS)
 *   2. WooCommerce integration
 *   3. Build pipeline (minify, lint, verify)
 *   4. Marketplace evaluation (wp.org / ThemeForest scoring)
 *   5. Production deployment + verification
 *
 * Usage:
 *   npx tsx agents/wordpress_theme_builder/agent.ts "Build a new collection page for Summer Drop"
 *   npx tsx agents/wordpress_theme_builder/agent.ts --deploy "Deploy current theme to production"
 *   npx tsx agents/wordpress_theme_builder/agent.ts --evaluate "Evaluate theme for ThemeForest"
 *
 * @package DevSkyy
 */

import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { execSync } from "child_process";
import path from "path";

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const THEME_DIR = path.join(PROJECT_ROOT, "wordpress-theme/skyyrose-flagship");
const SCRIPTS_DIR = path.join(PROJECT_ROOT, "scripts");

// ---------------------------------------------------------------------------
// Custom MCP Tools — WordPress Theme Operations
// ---------------------------------------------------------------------------

const themeBuild = tool(
  "theme-build",
  "Run the full theme build pipeline: CSS minification, JS webpack, PHP lint, verification, asset manifest. Modes: --css, --js, --lint, --verify, --production, --clean",
  { mode: z.string().optional().describe("Build mode: full, css, js, lint, verify, clean, production") },
  async ({ mode }) => {
    const flag = mode && mode !== "full" ? `--${mode}` : "";
    try {
      const output = execSync(`bash ${SCRIPTS_DIR}/theme-build.sh ${flag}`, {
        cwd: PROJECT_ROOT,
        timeout: 120_000,
        encoding: "utf-8",
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (err: any) {
      return { content: [{ type: "text" as const, text: `Build failed:\n${err.stdout || err.message}` }] };
    }
  }
);

const themeEnhance = tool(
  "theme-enhance",
  "Analyze and optimize theme: asset sizes, image compression, unused CSS/JS detection, accessibility audit, WooCommerce health, performance scoring. Modes: --analyze, --images, --assets, --unused, --a11y, --perf, --wc-health",
  { mode: z.string().optional().describe("Enhance mode: full, analyze, images, assets, unused, a11y, perf, wc-health") },
  async ({ mode }) => {
    const flag = mode && mode !== "full" ? `--${mode}` : "--analyze";
    try {
      const output = execSync(`bash ${SCRIPTS_DIR}/theme-enhance.sh ${flag}`, {
        cwd: PROJECT_ROOT,
        timeout: 120_000,
        encoding: "utf-8",
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (err: any) {
      return { content: [{ type: "text" as const, text: `Enhancement analysis failed:\n${err.stdout || err.message}` }] };
    }
  }
);

const marketplaceEval = tool(
  "marketplace-eval",
  "Evaluate theme against WordPress.org and ThemeForest marketplace standards. Returns scored report with pass/fail on 50+ criteria. Modes: --wporg, --themeforest, --security, --score",
  { mode: z.string().optional().describe("Eval mode: full, wporg, themeforest, security, score") },
  async ({ mode }) => {
    const flag = mode && mode !== "full" ? `--${mode}` : "";
    try {
      const output = execSync(`bash ${SCRIPTS_DIR}/theme-marketplace-eval.sh ${flag}`, {
        cwd: PROJECT_ROOT,
        timeout: 60_000,
        encoding: "utf-8",
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (err: any) {
      return { content: [{ type: "text" as const, text: err.stdout || err.message }] };
    }
  }
);

const themeDev = tool(
  "theme-dev",
  "Developer toolkit: scaffold templates/parts/css/js, run tests, check status, bump version, create package ZIP, diff vs live site. Commands: new-template, new-part, new-css, new-js, test, status, version, package, diff-live",
  {
    command: z.string().describe("Command: new-template, new-part, new-css, new-js, test, test-php, status, version, package, diff-live"),
    args: z.string().optional().describe("Arguments for the command (e.g., template name, version number)"),
  },
  async ({ command, args }) => {
    try {
      const output = execSync(`bash ${SCRIPTS_DIR}/theme-dev.sh ${command} ${args || ""}`, {
        cwd: PROJECT_ROOT,
        timeout: 120_000,
        encoding: "utf-8",
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (err: any) {
      return { content: [{ type: "text" as const, text: err.stdout || err.message }] };
    }
  }
);

const deployTheme = tool(
  "deploy-theme",
  "Deploy the WordPress theme to production. Runs the full deploy pipeline: build → maintenance mode → rsync → cache flush → verify. Use --dry-run to preview.",
  { dryRun: z.boolean().optional().describe("Preview only, no server contact") },
  async ({ dryRun }) => {
    const flag = dryRun ? "--dry-run" : "";
    try {
      const output = execSync(`bash ${SCRIPTS_DIR}/deploy-pipeline.sh ${flag}`, {
        cwd: PROJECT_ROOT,
        timeout: 300_000,
        encoding: "utf-8",
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (err: any) {
      return { content: [{ type: "text" as const, text: `Deploy failed:\n${err.stdout || err.message}` }] };
    }
  }
);

const verifyDeploy = tool(
  "verify-deploy",
  "Post-deploy verification: checks HTTP 200 + content markers on all critical pages (homepage, collections, shop, about, contact).",
  {},
  async () => {
    try {
      const output = execSync(`bash ${SCRIPTS_DIR}/verify-deploy.sh`, {
        cwd: PROJECT_ROOT,
        timeout: 60_000,
        encoding: "utf-8",
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (err: any) {
      return { content: [{ type: "text" as const, text: err.stdout || err.message }] };
    }
  }
);

// ---------------------------------------------------------------------------
// MCP Server with all WordPress tools
// ---------------------------------------------------------------------------
const wpToolsServer = createSdkMcpServer({
  name: "wordpress-theme-tools",
  tools: [themeBuild, themeEnhance, marketplaceEval, themeDev, deployTheme, verifyDeploy],
});

// ---------------------------------------------------------------------------
// System Prompt — WordPress Theme Builder Identity
// ---------------------------------------------------------------------------
const SYSTEM_PROMPT = `You are the SkyyRose WordPress Theme Builder Agent — a full-stack theme development AI.

## Your Capabilities
You build, enhance, evaluate, and deploy WordPress themes end-to-end. You have:
- **File tools**: Read, Write, Edit, Glob, Grep — for writing PHP, CSS, JS
- **Bash**: Run commands, git operations, npm scripts
- **theme-build**: Full build pipeline (CSS/JS minification, PHP lint, verification)
- **theme-enhance**: Performance analysis (asset budgets, a11y, unused detection)
- **marketplace-eval**: Marketplace readiness scoring (WordPress.org / ThemeForest)
- **theme-dev**: Scaffolding (new templates, parts, CSS, JS), versioning, packaging
- **deploy-theme**: Production deployment with maintenance mode + cache flush
- **verify-deploy**: Post-deploy verification on all live pages

## Theme Architecture (SkyyRose Flagship)
- Theme directory: ${THEME_DIR}
- functions.php bootstraps inc/ modules (enqueue, security, woocommerce, SEO, etc.)
- 4 collection templates: Black Rose, Love Hurts, Signature, Kids Capsule
- 3 immersive 3D templates (Three.js via CDN)
- WooCommerce overrides in woocommerce/ (holo product cards)
- 112 CSS files, 88 JS files, all with .min counterparts
- Brand: #B76E79 rose gold, #0A0A0A dark, #D4AF37 gold, #DC143C crimson

## Workflow
1. **Understand** the request — read existing code before modifying
2. **Scaffold** if needed (theme-dev new-template/new-part/new-css/new-js)
3. **Implement** with proper WordPress patterns (escaping, i18n, ABSPATH guards)
4. **Build** (theme-build) — minify CSS/JS, lint PHP, verify output
5. **Evaluate** (marketplace-eval) — check marketplace readiness
6. **Deploy** (deploy-theme --dry-run first, then live)
7. **Verify** (verify-deploy) — confirm all pages render correctly

## Rules
- Always escape output: esc_html(), esc_attr(), esc_url()
- Always use text domain 'skyyrose-flagship' for i18n
- Always add ABSPATH guards to PHP files
- Use get_template_part() for reusable components
- Prefix all functions with skyyrose_
- CSS/JS budget: 30KB per CSS file, 50KB per JS file
- Run theme-build after every code change
- Never deploy without --dry-run first`;

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
SkyyRose WordPress Theme Builder Agent

Usage:
  npx tsx agents/wordpress_theme_builder/agent.ts "<prompt>"

Examples:
  "Build a new Sustainability page with hero, story section, and product grid"
  "Add a newsletter signup form to the footer template"
  "Run marketplace evaluation and fix all critical issues"
  "Deploy current theme to production"
  "Create a new Summer Drop collection template"
  "Optimize all images and reduce total asset weight"
  "Check WooCommerce template compatibility"

Options:
  --deploy     Deploy to production (runs full pipeline)
  --evaluate   Run marketplace evaluation
  --build      Run build pipeline only
  --status     Show theme status
  --help       Show this help
`);
    return;
  }

  // Quick shortcuts
  const prompt = args.join(" ");
  let finalPrompt = prompt;

  if (args[0] === "--deploy") {
    finalPrompt = "Deploy the current theme to production. First do a --dry-run, show me the results, then proceed with the actual deploy. Verify all pages after deployment.";
  } else if (args[0] === "--evaluate") {
    finalPrompt = "Run a full marketplace evaluation of the SkyyRose Flagship theme. Report the score and list all critical and high-priority issues that need fixing.";
  } else if (args[0] === "--build") {
    finalPrompt = "Run the full theme build pipeline. Show me the results including any errors or warnings.";
  } else if (args[0] === "--status") {
    finalPrompt = "Show me the current theme status: file counts, build state, PHP health, and git status.";
  }

  console.log("WordPress Theme Builder Agent starting...\n");

  for await (const message of query({
    prompt: finalPrompt,
    options: {
      cwd: THEME_DIR,
      model: "claude-opus-4-6",
      allowedTools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent"],
      permissionMode: "acceptEdits",
      systemPrompt: SYSTEM_PROMPT,
      maxTurns: 50,
      mcpServers: { "wp-tools": wpToolsServer },
    },
  })) {
    if ("result" in message) {
      console.log("\n" + message.result);
    }
  }
}

main().catch(console.error);
