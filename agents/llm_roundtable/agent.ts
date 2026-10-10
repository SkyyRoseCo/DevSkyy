/**
 * LLM Roundtable Agent
 *
 * Claude Agent SDK orchestrator that manages LLM competitions, technique A/B testing,
 * and auto-routing intelligence for the SkyyRose platform.
 *
 * Architecture:
 *   Lead Agent (Claude Opus) — orchestrates battles, analyzes patterns, optimizes routing
 *     ├── battle-analyst subagent — deep-dives into results and technique effectiveness
 *     ├── brand-judge subagent — evaluates outputs against SkyyRose brand standards
 *     └── MCP tools from engine.ts — run-battle, run-technique-battle, get-leaderboard, etc.
 *
 * Usage:
 *   npx tsx agents/llm_roundtable/agent.ts "Run a Content battle for BLACK ROSE hoodie copy"
 *   npx tsx agents/llm_roundtable/agent.ts --tournament "Full tournament across all categories"
 *   npx tsx agents/llm_roundtable/agent.ts --optimize "Find best technique per category"
 *   npx tsx agents/llm_roundtable/agent.ts --report "Generate performance report"
 *
 * @package DevSkyy
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { roundtableServer } from "./engine.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const PROJECT_ROOT = path.resolve(__dirname, "../..");

const CATEGORIES = [
  "Content", "SEO", "Social Media", "Email",
  "Analytics", "Support", "Code", "Creative", "Pricing",
];

const TECHNIQUES = [
  "chain_of_thought", "tree_of_thoughts", "react", "rag",
  "few_shot", "structured_output", "constitutional",
  "role_based", "self_consistency", "ensemble",
];

// ---------------------------------------------------------------------------
// System Prompt — Roundtable Orchestrator Identity
// ---------------------------------------------------------------------------
const SYSTEM_PROMPT = `You are the SkyyRose LLM Roundtable Orchestrator — an AI competition manager that optimizes model selection and prompt engineering for the entire DevSkyy platform.

## Your Mission
Run structured competitions between LLM providers, A/B test prompt techniques, and build an intelligence layer that auto-routes tasks to the best model + technique combination.

## Tools Available
- **run-battle**: Pit multiple models against each other on a task. Auto-selects prompt technique by category, or you can specify one. Returns winner + scores.
- **run-technique-battle**: Same model, different prompt techniques. Discovers which technique produces the best output for a task type.
- **get-leaderboard**: Current Elo rankings across all models.
- **get-battle-history**: Recent battles with winners, scores, techniques used.
- **get-technique-stats**: Performance data for each of the 10 prompt techniques by category.
- **list-techniques**: All 10 techniques with descriptions and category mappings.
- **Read/Glob/Grep**: Access codebase for context, product data, brand guidelines.

## The 10 Prompt Techniques
1. chain_of_thought — step-by-step reasoning
2. tree_of_thoughts — multi-branch exploration
3. react — reasoning + action loops
4. rag — retrieval-augmented generation
5. few_shot — exemplar-driven learning
6. structured_output — format-constrained responses
7. constitutional — principle-based self-critique
8. role_based — persona/expertise assignment
9. self_consistency — multi-path majority vote
10. ensemble — combined technique stacking

## Competition Formats
1. **Single Battle**: One task, all models compete, best wins
2. **Technique Battle**: One task, one model, multiple techniques — which prompt approach wins?
3. **Tournament**: Multiple battles across categories — builds comprehensive Elo rankings
4. **Optimization Run**: Technique battles across all categories — finds best technique per category

## Brand Context
SkyyRose — "" — Oakland luxury streetwear.
Collections: Black Rose (gothic/Oakland), Love Hurts (emotional/passionate), Signature (Bay Area/SF), Kids Capsule.
Brand colors: #B76E79 rose gold, #0A0A0A dark, #D4AF37 gold, #DC143C crimson.
Founder: Corey Foster.

## Rules
- Always specify category when running battles — it drives technique auto-selection
- Use SkyyRose-relevant tasks (product copy, collection pages, brand content)
- After battles, analyze WHY the winner won — technique effectiveness matters
- When optimizing, run technique battles for each major category
- Present results with actionable routing recommendations
- Ground all analysis in actual battle data, never fabricate scores or results`;

// ---------------------------------------------------------------------------
// Subagent Definitions
// ---------------------------------------------------------------------------
const SUBAGENTS = {
  "battle-analyst": {
    description: "Analyzes battle results, identifies patterns in model performance, and recommends routing optimizations. Reads battle history and technique stats to find which model + technique combinations excel at each task type.",
    prompt: `You analyze LLM competition results for SkyyRose. Given battle data:
1. Identify winning patterns per category (which models dominate where)
2. Evaluate technique effectiveness (which prompt techniques boost scores)
3. Detect performance trends (is a model improving or declining?)
4. Recommend routing rules (category X → model Y with technique Z)
Always cite specific battle IDs and scores. Never fabricate data.`,
    tools: ["Read", "Glob", "Grep"],
  },
  "brand-judge": {
    description: "Expert in SkyyRose brand standards. Reviews battle outputs against brand voice, tagline usage, collection accuracy, and luxury positioning. Flags any off-brand content.",
    prompt: `You are the SkyyRose brand guardian. Evaluate LLM battle outputs against:
- Tagline: "" (ONLY this tagline — never "Where Love Meets Luxury")
- Voice: elevated streetwear, Oakland roots, cultural depth, exclusive
- Collections: Black Rose (dark elegance), Love Hurts (emotional), Signature (foundation)
- Colors: #B76E79 rose gold, #0A0A0A obsidian, #D4AF37 gold, #DC143C crimson
- NEVER use generic luxury language — it must feel Oakland, not Milan
Read product data from memory before evaluating. Flag any factual errors (wrong SKUs, prices, collections).`,
    tools: ["Read", "Glob", "Grep"],
  },
};

// ---------------------------------------------------------------------------
// Preset Prompts
// ---------------------------------------------------------------------------
const TOURNAMENT_PROMPT = `Run a full tournament across these categories with SkyyRose-specific tasks:

1. Content: "Write product copy for the BLACK ROSE Heavyweight Hoodie — 280gsm cotton, double-stitched, limited to 200 units"
2. SEO: "Write meta descriptions for all 4 SkyyRose collection pages — Black Rose, Love Hurts, Signature, Kids Capsule"
3. Social Media: "Write 5 Instagram carousel captions for LOVE HURTS spring lookbook — emotional, Gen Z tone"
4. Email: "Write 3 abandoned cart email subject lines for Signature collection items"
5. Analytics: "Analyze why BLACK ROSE has 3x higher conversion than Signature — hypothesize top 3 factors"
6. Creative: "Write the homepage hero tagline and 2 supporting lines for a seasonal restock drop"
7. Code: "Write a WooCommerce filter that adds a 'PRE-ORDER' badge to products with pre-order status"

After all battles, show the full leaderboard and recommend which model handles each category.
Use the battle-analyst subagent to identify patterns.`;

const OPTIMIZE_PROMPT = `Run technique optimization across all major categories.

For each category, run a technique battle using claude-sonnet:
1. Content — test: role_based, constitutional, few_shot, ensemble
2. SEO — test: structured_output, few_shot, chain_of_thought
3. Social Media — test: few_shot, role_based, constitutional
4. Email — test: few_shot, role_based, structured_output
5. Analytics — test: chain_of_thought, tree_of_thoughts, react
6. Code — test: chain_of_thought, react, structured_output

Use real SkyyRose tasks for each. After all technique battles, compile a technique routing table:
  Category → Best Technique → Score → Runner-up

Then check get-technique-stats to validate against historical data.`;

const REPORT_PROMPT = `Generate a comprehensive performance report:

1. Get the current leaderboard (get-leaderboard)
2. Get the last 20 battles (get-battle-history with limit 20)
3. Get technique stats (get-technique-stats)
4. Use the battle-analyst subagent to identify:
   - Overall best model
   - Best model per category
   - Best technique per category
   - Cost efficiency rankings (score per dollar)
   - Any models that are underperforming relative to cost
5. Use the brand-judge subagent to review the top-scoring outputs from recent battles
6. Compile into a structured report with routing recommendations`;

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
SkyyRose LLM Roundtable Agent — Competition Orchestrator

Usage:
  npx tsx agents/llm_roundtable/agent.ts "<prompt>"
  npx tsx agents/llm_roundtable/agent.ts --tournament
  npx tsx agents/llm_roundtable/agent.ts --optimize
  npx tsx agents/llm_roundtable/agent.ts --report

Modes:
  <prompt>       Free-form instruction to the orchestrator
  --tournament   Full multi-category tournament with all models
  --optimize     A/B test techniques across categories to find optimal routing
  --report       Generate performance report from historical data

Examples:
  "Run a Content battle for BLACK ROSE hoodie copy"
  "Which model writes the best SEO meta descriptions?"
  "Compare chain_of_thought vs ensemble for analytics tasks"
  "Run 5 battles and tell me who should handle our email campaigns"

Models: claude-opus, claude-sonnet, claude-haiku, gpt-4o, gemini-2
Techniques: ${TECHNIQUES.join(", ")}
Categories: ${CATEGORIES.join(", ")}
`);
    return;
  }

  // Resolve prompt from flags or free-form input
  let finalPrompt: string;

  if (args[0] === "--tournament") {
    finalPrompt = TOURNAMENT_PROMPT;
  } else if (args[0] === "--optimize") {
    finalPrompt = OPTIMIZE_PROMPT;
  } else if (args[0] === "--report") {
    finalPrompt = REPORT_PROMPT;
  } else {
    finalPrompt = args.join(" ");
  }

  console.log("LLM Roundtable Agent starting...\n");

  for await (const message of query({
    prompt: finalPrompt,
    options: {
      cwd: PROJECT_ROOT,
      model: "claude-opus-4-6",
      allowedTools: ["Read", "Glob", "Grep", "Agent"],
      permissionMode: "acceptEdits",
      systemPrompt: SYSTEM_PROMPT,
      maxTurns: 80,
      agents: SUBAGENTS,
      mcpServers: { roundtable: roundtableServer },
    },
  })) {
    if ("result" in message) {
      console.log("\n" + message.result);
    }
  }
}

main().catch(console.error);
