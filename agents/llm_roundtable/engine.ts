/**
 * LLM Roundtable — Live Battle Engine
 *
 * Dispatches prompts to multiple LLM providers in parallel,
 * judges responses with Claude, updates Elo ratings, persists results.
 *
 * Integrates 10 prompt engineering techniques from the DevSkyy framework:
 *   1. Chain-of-Thought (CoT) — step-by-step reasoning
 *   2. Tree of Thoughts (ToT) — multi-branch exploration
 *   3. ReAct — reasoning + acting with tools
 *   4. RAG — retrieval-augmented generation
 *   5. Few-Shot — exemplar-driven learning
 *   6. Structured Output — format-constrained responses
 *   7. Constitutional AI — principle-based self-critique
 *   8. Role-Based — persona/expertise assignment
 *   9. Self-Consistency — multi-path majority vote
 *  10. Ensemble — combined technique stacking
 *
 * Uses Claude Agent SDK for orchestration + raw API calls for competing models.
 *
 * Usage:
 *   npx tsx agents/llm_roundtable/engine.ts "Write product copy for BLACK ROSE Hoodie"
 *   npx tsx agents/llm_roundtable/engine.ts --category "SEO" "Meta descriptions for 4 collections"
 *   npx tsx agents/llm_roundtable/engine.ts --technique "chain_of_thought" "Analyze pricing"
 *   npx tsx agents/llm_roundtable/engine.ts --technique-battle "Write brand copy" --category "Content"
 *
 * @package DevSkyy
 */

import Anthropic from "@anthropic-ai/sdk";
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import fs from "fs";
import path from "path";
import {
  recordLearning,
  updateRoutingWeights,
  getLearnedRoute,
  isModelDisabled,
  recordFailure,
  recordSuccess,
  getFallbackModel,
  withRetry,
  isAnomalousScore,
  isTechniqueUnderperforming,
  checkEloHealth,
  getHealthReport,
  getRecentCorrections,
} from "./adaptive.js";
import { loadJSON, saveJSON, DATA_DIR } from "./utils.js";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const BATTLES_FILE = path.join(DATA_DIR, "battles.json");
const ELO_FILE = path.join(DATA_DIR, "elo.json");
const TECHNIQUE_STATS_FILE = path.join(DATA_DIR, "technique_stats.json");

const K_FACTOR = 32; // Elo K-factor

// ---------------------------------------------------------------------------
// Prompt Techniques — ported from orchestration/prompt_engineering.py
// ---------------------------------------------------------------------------
type PromptTechnique =
  | "chain_of_thought"
  | "tree_of_thoughts"
  | "react"
  | "rag"
  | "few_shot"
  | "structured_output"
  | "constitutional"
  | "role_based"
  | "self_consistency"
  | "ensemble";

const ALL_TECHNIQUES: PromptTechnique[] = [
  "chain_of_thought",
  "tree_of_thoughts",
  "react",
  "rag",
  "few_shot",
  "structured_output",
  "constitutional",
  "role_based",
  "self_consistency",
  "ensemble",
];

// Maps battle categories to recommended techniques (mirrors base_super_agent.py TECHNIQUE_MAPPING)
const CATEGORY_TECHNIQUE_MAP: Record<string, PromptTechnique> = {
  Content: "role_based",
  SEO: "structured_output",
  "Social Media": "few_shot",
  Email: "few_shot",
  Analytics: "chain_of_thought",
  Support: "role_based",
  Code: "chain_of_thought",
  Reasoning: "chain_of_thought",
  Creative: "tree_of_thoughts",
  Classification: "few_shot",
  Extraction: "structured_output",
  Research: "rag",
  Planning: "tree_of_thoughts",
  Pricing: "chain_of_thought",
  Vision: "role_based",
  General: "role_based",
};

// SkyyRose brand context injected into role-based and RAG prompts
const SKYYROSE_BRAND_CONTEXT = `SkyyRose is an Oakland-based luxury streetwear brand.
Collections: BLACK ROSE (limited edition dark elegance), LOVE HURTS (emotional expression), SIGNATURE (foundation wardrobe essentials), Kids Capsule.
Brand colors: #B76E79 rose gold, #0A0A0A obsidian, #D4AF37 gold, #DC143C crimson.
Target: Discerning customers who appreciate elevated street style with cultural depth.
Founder: Corey Foster. Based in Oakland, CA.`;

// SkyyRose-specific few-shot examples by category
const SKYYROSE_FEW_SHOTS: Record<string, Array<{ input: string; output: string }>> = {
  Content: [
    {
      input: "Write copy for a premium hoodie, 280gsm cotton, limited to 200 units",
      output:
        "Built for those who move through darkness like it's home. 280gsm cotton that doesn't apologize for its weight. Double-stitched seams because shortcuts aren't in our vocabulary. Limited to 200 — when they're gone, they're gone forever.",
    },
    {
      input: "Write copy for rose gold varsity jacket, genuine leather sleeves",
      output:
        "Every thread tells the story of where we came from. Genuine leather sleeves that soften with every chapter you write. Rose gold hardware catching light the way confidence catches attention. This isn't a jacket — it's an arrival.",
    },
  ],
  SEO: [
    {
      input: "Meta description for BLACK ROSE collection page",
      output:
        "Shop BLACK ROSE — limited edition luxury streetwear from Oakland. Premium heavyweight cotton, rose gold hardware, gothic-inspired designs. Free shipping on orders $150+.",
    },
  ],
  "Social Media": [
    {
      input: "Instagram caption for new hoodie drop",
      output:
        "concrete taught us everything. ◆ BLACK ROSE Heavyweight Hoodie — 280gsm, double-stitched, limited to 200. link in bio before they're gone 🥀 #SkyyRose",
    },
  ],
  Email: [
    {
      input: "Subject line for abandoned cart — BLACK ROSE hoodie",
      output: "Your BLACK ROSE hoodie is still waiting. Only 47 left.",
    },
  ],
};

// ---------------------------------------------------------------------------
// Technique Implementations
// ---------------------------------------------------------------------------

function applyChainOfThought(task: string, context?: string): string {
  return `${context || "Please solve the following problem."}

Question: ${task}

Let's think through this step by step:
1. First, I'll identify what we're trying to solve.
2. Then, I'll break down the problem into smaller parts.
3. I'll work through each part systematically.
4. Finally, I'll combine the results for the answer.

Step-by-step reasoning:`;
}

function applyTreeOfThoughts(task: string, nBranches: number = 3): string {
  return `Problem: ${task}

Let's explore ${nBranches} different approaches to solve this:

Approach 1: [First direction]
- Initial thought:
- Development:
- Evaluation: [Rate 1-10]

Approach 2: [Second direction]
- Initial thought:
- Development:
- Evaluation: [Rate 1-10]

Approach 3: [Third direction]
- Initial thought:
- Development:
- Evaluation: [Rate 1-10]

After evaluating all approaches, the best path forward is:`;
}

function applyReAct(task: string, tools: string[] = []): string {
  const toolList = tools.length > 0 ? tools.join(", ") : "analysis, comparison, evaluation";
  return `Task: ${task}

Available tools: ${toolList}

Solve this task by alternating between:
- Thought: Your reasoning about what to do next
- Action: The tool to use and its input
- Observation: The result of the action

Begin:

Thought 1: I need to understand the current task and plan my approach.`;
}

function applyRAG(task: string, context: Array<{ text: string; source: string }> = []): string {
  const contextParts = context.length > 0
    ? context.map((c) => `[Source: ${c.source}]\n${c.text}`).join("\n\n")
    : `[Source: brand-context]\n${SKYYROSE_BRAND_CONTEXT}`;

  return `Use the following context to answer the question. If the context doesn't contain relevant information, say so.

Context:
${contextParts}

Question: ${task}

Answer based on the context above:`;
}

function applyFewShot(task: string, category: string): string {
  const examples = SKYYROSE_FEW_SHOTS[category] || SKYYROSE_FEW_SHOTS["Content"] || [];
  const exampleBlock = examples
    .map((ex, i) => `Example ${i + 1}:\nInput: ${ex.input}\nOutput: ${ex.output}`)
    .join("\n\n");

  return `Task: Complete the following for SkyyRose luxury streetwear brand.

${exampleBlock}

Now respond to:
Input: ${task}
Output:`;
}

function applyStructuredOutput(task: string, schema?: Record<string, string>): string {
  const defaultSchema = schema || {
    response: "string — the main response content",
    confidence: "number — confidence level 0-100",
    reasoning: "string — brief explanation of approach",
    brand_alignment: "number — alignment with SkyyRose brand voice 0-100",
  };
  return `${task}

Respond with a JSON object matching this schema:
\`\`\`json
${JSON.stringify(defaultSchema, null, 2)}
\`\`\`

Your response must be valid JSON only, no additional text.`;
}

function applyConstitutional(task: string, principles?: string[]): string {
  const defaultPrinciples = principles || [
    "Maintain SkyyRose luxury brand voice — never generic or mass-market",
    "Be culturally authentic — rooted in Oakland, not performative",
    "Respect exclusivity — never oversell or use desperate urgency tactics",
    "Be honest and accurate about product details",
    "Avoid clichés and overused marketing language",
    "Stay aspirational yet grounded",
  ];

  return `${task}

After drafting your response, evaluate it against these principles:
${defaultPrinciples.map((p) => `- ${p}`).join("\n")}

If any principle is violated, revise your response before submitting.
Provide your final, principle-aligned response:`;
}

function applyRoleBased(task: string, role?: string, background?: string): string {
  const finalRole = role || "a luxury streetwear brand strategist and fashion expert for SkyyRose";
  const finalBackground = background || SKYYROSE_BRAND_CONTEXT;

  return `You are ${finalRole}.

${finalBackground}

${task}`;
}

function applySelfConsistency(task: string, nVariants: number = 3): string[] {
  const prefixes = [
    "",
    "Let's approach this differently.\n\n",
    "Consider an alternative method.\n\n",
    "From another perspective,\n\n",
    "Using a different strategy,\n\n",
  ];
  return prefixes.slice(0, nVariants).map((p) => `${p}${task}`);
}

function applyEnsemble(task: string, category: string): string {
  // Stack role-based + chain-of-thought + constitutional for maximum quality
  const rolePart = applyRoleBased(task);
  const cotPart = applyChainOfThought(task);
  const constPart = applyConstitutional(task);

  return `[ENSEMBLE: Role-Based + Chain-of-Thought + Constitutional]

--- PERSONA ---
${rolePart}

--- REASONING ---
${cotPart}

--- PRINCIPLES ---
${constPart}

Synthesize the above approaches into a single, high-quality response:`;
}

/**
 * Apply a prompt technique to enhance the raw task before dispatching to models.
 *
 * Returns an array of prompts (usually 1, but self_consistency returns multiple).
 */
function applyTechnique(
  technique: PromptTechnique,
  task: string,
  category: string = "General",
  options: {
    context?: Array<{ text: string; source: string }>;
    tools?: string[];
    schema?: Record<string, string>;
    role?: string;
    background?: string;
    principles?: string[];
    nVariants?: number;
    nBranches?: number;
  } = {}
): string[] {
  switch (technique) {
    case "chain_of_thought":
      return [applyChainOfThought(task, options.context?.[0]?.text)];
    case "tree_of_thoughts":
      return [applyTreeOfThoughts(task, options.nBranches)];
    case "react":
      return [applyReAct(task, options.tools)];
    case "rag":
      return [applyRAG(task, options.context)];
    case "few_shot":
      return [applyFewShot(task, category)];
    case "structured_output":
      return [applyStructuredOutput(task, options.schema)];
    case "constitutional":
      return [applyConstitutional(task, options.principles)];
    case "role_based":
      return [applyRoleBased(task, options.role, options.background)];
    case "self_consistency":
      return applySelfConsistency(task, options.nVariants || 3);
    case "ensemble":
      return [applyEnsemble(task, category)];
  }
}

/**
 * Auto-select the best technique for a category.
 * Self-Learning: checks battle data first — if we have high-confidence learned
 * routing, use that. Otherwise falls back to the static CATEGORY_TECHNIQUE_MAP.
 */
function autoSelectTechnique(category: string): PromptTechnique {
  // Self-Learning: prefer learned routing when confidence > 50%
  const learned = getLearnedRoute(category);
  if (learned && learned.confidence > 50) {
    return learned.bestTechnique as PromptTechnique;
  }
  return CATEGORY_TECHNIQUE_MAP[category] || "role_based";
}

// ---------------------------------------------------------------------------
// Model Registry — real API configs
// ---------------------------------------------------------------------------
interface ModelConfig {
  id: string;
  name: string;
  provider: "anthropic" | "openai" | "google";
  modelId: string;
  tier: string;
  costPer1kInput: number;
  costPer1kOutput: number;
}

const MODEL_REGISTRY: ModelConfig[] = [
  { id: "claude-opus", name: "Claude Opus 4.6", provider: "anthropic", modelId: "claude-opus-4-6", tier: "frontier", costPer1kInput: 0.005, costPer1kOutput: 0.025 },
  { id: "claude-sonnet", name: "Claude Sonnet 4.6", provider: "anthropic", modelId: "claude-sonnet-4-6", tier: "performance", costPer1kInput: 0.003, costPer1kOutput: 0.015 },
  { id: "claude-haiku", name: "Claude Haiku 4.5", provider: "anthropic", modelId: "claude-haiku-4-5", tier: "speed", costPer1kInput: 0.001, costPer1kOutput: 0.005 },
  { id: "gpt-4o", name: "GPT-4o", provider: "openai", modelId: "gpt-4o", tier: "frontier", costPer1kInput: 0.005, costPer1kOutput: 0.015 },
  { id: "gemini-2", name: "Gemini 2.5 Pro", provider: "google", modelId: "gemini-2.5-pro", tier: "frontier", costPer1kInput: 0.00125, costPer1kOutput: 0.005 },
];

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface CompetitorResult {
  modelId: string;
  output: string;
  latencyMs: number;
  inputTokens: number;
  outputTokens: number;
  cost: number;
  error?: string;
}

interface JudgeScore {
  modelId: string;
  overall: number;
  criteria: Record<string, number>;
  reasoning: string;
}

interface Battle {
  id: string;
  task: string;
  category: string;
  technique: PromptTechnique;
  enhancedPrompt: string;
  timestamp: string;
  competitors: CompetitorResult[];
  scores: JudgeScore[];
  winner: string;
  criteria: string[];
}

interface TechniqueBattle {
  id: string;
  task: string;
  category: string;
  modelId: string;
  timestamp: string;
  techniques: Array<{
    technique: PromptTechnique;
    enhancedPrompt: string;
    result: CompetitorResult;
    score: number;
  }>;
  winner: PromptTechnique;
}

interface EloEntry {
  modelId: string;
  elo: number;
  wins: number;
  losses: number;
  draws: number;
  totalBattles: number;
}

interface TechniqueStats {
  technique: PromptTechnique;
  uses: number;
  avgScore: number;
  totalScore: number;
  categoryScores: Record<string, { uses: number; totalScore: number }>;
}

// ---------------------------------------------------------------------------
// LLM Callers — one per provider
// ---------------------------------------------------------------------------
async function callAnthropic(model: ModelConfig, prompt: string): Promise<CompetitorResult> {
  const client = new Anthropic();
  const start = Date.now();

  try {
    const response = await client.messages.create({
      model: model.modelId,
      max_tokens: 1024,
      messages: [{ role: "user", content: prompt }],
    });

    const text = response.content
      .filter((b): b is Anthropic.TextBlock => b.type === "text")
      .map((b) => b.text)
      .join("");

    return {
      modelId: model.id,
      output: text,
      latencyMs: Date.now() - start,
      inputTokens: response.usage.input_tokens,
      outputTokens: response.usage.output_tokens,
      cost:
        (response.usage.input_tokens / 1000) * model.costPer1kInput +
        (response.usage.output_tokens / 1000) * model.costPer1kOutput,
    };
  } catch (err: any) {
    return {
      modelId: model.id,
      output: "",
      latencyMs: Date.now() - start,
      inputTokens: 0,
      outputTokens: 0,
      cost: 0,
      error: err.message,
    };
  }
}

async function callOpenAI(model: ModelConfig, prompt: string): Promise<CompetitorResult> {
  const start = Date.now();
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return { modelId: model.id, output: "", latencyMs: 0, inputTokens: 0, outputTokens: 0, cost: 0, error: "OPENAI_API_KEY not set" };
  }

  try {
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ model: model.modelId, messages: [{ role: "user", content: prompt }], max_tokens: 1024 }),
    });
    const data = await res.json();
    return {
      modelId: model.id,
      output: data.choices?.[0]?.message?.content || "",
      latencyMs: Date.now() - start,
      inputTokens: data.usage?.prompt_tokens || 0,
      outputTokens: data.usage?.completion_tokens || 0,
      cost:
        ((data.usage?.prompt_tokens || 0) / 1000) * model.costPer1kInput +
        ((data.usage?.completion_tokens || 0) / 1000) * model.costPer1kOutput,
    };
  } catch (err: any) {
    return { modelId: model.id, output: "", latencyMs: Date.now() - start, inputTokens: 0, outputTokens: 0, cost: 0, error: err.message };
  }
}

async function callGoogle(model: ModelConfig, prompt: string): Promise<CompetitorResult> {
  const start = Date.now();
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    return { modelId: model.id, output: "", latencyMs: 0, inputTokens: 0, outputTokens: 0, cost: 0, error: "GOOGLE_API_KEY not set" };
  }

  try {
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model.modelId}:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: 1024 } }),
      }
    );
    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
    return {
      modelId: model.id,
      output: text,
      latencyMs: Date.now() - start,
      inputTokens: data.usageMetadata?.promptTokenCount || 0,
      outputTokens: data.usageMetadata?.candidatesTokenCount || 0,
      cost:
        ((data.usageMetadata?.promptTokenCount || 0) / 1000) * model.costPer1kInput +
        ((data.usageMetadata?.candidatesTokenCount || 0) / 1000) * model.costPer1kOutput,
    };
  } catch (err: any) {
    return { modelId: model.id, output: "", latencyMs: Date.now() - start, inputTokens: 0, outputTokens: 0, cost: 0, error: err.message };
  }
}

async function callModel(model: ModelConfig, prompt: string): Promise<CompetitorResult> {
  // Self-Healing: check circuit breaker before calling
  if (isModelDisabled(model.id)) {
    const fallbackId = getFallbackModel(model.id, MODEL_REGISTRY.map((m) => m.id));
    if (fallbackId) {
      const fallback = MODEL_REGISTRY.find((m) => m.id === fallbackId)!;
      console.log(`   ⚡ ${model.id} circuit breaker open — falling back to ${fallback.id}`);
      return callModel(fallback, prompt);
    }
    return {
      modelId: model.id,
      output: "",
      latencyMs: 0,
      inputTokens: 0,
      outputTokens: 0,
      cost: 0,
      error: `Circuit breaker open for ${model.id} — no fallback available`,
    };
  }

  // Self-Healing: retry with exponential backoff on transient errors
  try {
    const result = await withRetry(async () => {
      switch (model.provider) {
        case "anthropic": return callAnthropic(model, prompt);
        case "openai": return callOpenAI(model, prompt);
        case "google": return callGoogle(model, prompt);
      }
    }, 2, 1000);

    if (result.error) {
      recordFailure(model.id, result.error);
    } else {
      recordSuccess(model.id);
    }

    return result;
  } catch (err: any) {
    recordFailure(model.id, err.message);
    return {
      modelId: model.id,
      output: "",
      latencyMs: 0,
      inputTokens: 0,
      outputTokens: 0,
      cost: 0,
      error: `All retries failed: ${err.message}`,
    };
  }
}

// ---------------------------------------------------------------------------
// Judge — Claude Opus scores all responses
// ---------------------------------------------------------------------------
async function judgeResponses(
  task: string,
  category: string,
  criteria: string[],
  technique: PromptTechnique,
  results: CompetitorResult[]
): Promise<JudgeScore[]> {
  const client = new Anthropic();

  const competitorBlock = results
    .filter((r) => !r.error)
    .map((r) => `### Model: ${r.modelId}\n${r.output}`)
    .join("\n\n---\n\n");

  const response = await client.messages.create({
    model: "claude-opus-4-6",
    max_tokens: 4096,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    thinking: { type: "adaptive" } as any,
    messages: [
      {
        role: "user",
        content: `You are a blind judge in an LLM competition arena for SkyyRose luxury streetwear brand.

TASK: "${task}"
CATEGORY: ${category}
TECHNIQUE USED: ${technique} (${getTechniqueDescription(technique)})
CRITERIA: ${criteria.join(", ")}

Score each model's response on a 0-100 scale for each criterion, then give an overall score (weighted average).
Consider how well each model leveraged the ${technique} technique in its response.

RESPONSES:
${competitorBlock}

Respond in JSON format ONLY:
{
  "scores": [
    {
      "modelId": "model-id",
      "overall": 85,
      "criteria": { "criterion1": 90, "criterion2": 80 },
      "reasoning": "Brief explanation including technique effectiveness"
    }
  ]
}`,
      },
    ],
  });

  const text = response.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("");

  try {
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No JSON in judge response");
    const parsed = JSON.parse(jsonMatch[0]);
    return parsed.scores;
  } catch {
    return results.map((r) => ({
      modelId: r.modelId,
      overall: 75,
      criteria: Object.fromEntries(criteria.map((c) => [c, 75])),
      reasoning: "Judge parse failed — default scores assigned",
    }));
  }
}

function getTechniqueDescription(technique: PromptTechnique): string {
  const descriptions: Record<PromptTechnique, string> = {
    chain_of_thought: "step-by-step reasoning before final answer",
    tree_of_thoughts: "exploring multiple approaches, evaluating each",
    react: "alternating reasoning and action steps",
    rag: "grounded in retrieved context/knowledge",
    few_shot: "guided by exemplar input-output pairs",
    structured_output: "constrained to specific output format",
    constitutional: "self-critique against brand principles",
    role_based: "persona-driven with domain expertise",
    self_consistency: "multiple reasoning paths, best selected",
    ensemble: "combining multiple techniques for maximum quality",
  };
  return descriptions[technique];
}

// ---------------------------------------------------------------------------
// Elo Calculator
// ---------------------------------------------------------------------------
function updateElo(eloData: Record<string, EloEntry>, scores: JudgeScore[]): void {
  const sorted = [...scores].sort((a, b) => b.overall - a.overall);
  const winner = sorted[0];

  for (const score of scores) {
    if (!eloData[score.modelId]) {
      eloData[score.modelId] = { modelId: score.modelId, elo: 1500, wins: 0, losses: 0, draws: 0, totalBattles: 0 };
    }
  }

  for (let i = 1; i < sorted.length; i++) {
    const loser = sorted[i];
    const eloW = eloData[winner.modelId].elo;
    const eloL = eloData[loser.modelId].elo;

    const expectedW = 1 / (1 + Math.pow(10, (eloL - eloW) / 400));
    const expectedL = 1 - expectedW;

    if (winner.overall === loser.overall) {
      eloData[winner.modelId].elo += Math.round(K_FACTOR * (0.5 - expectedW));
      eloData[loser.modelId].elo += Math.round(K_FACTOR * (0.5 - expectedL));
      eloData[winner.modelId].draws++;
      eloData[loser.modelId].draws++;
    } else {
      eloData[winner.modelId].elo += Math.round(K_FACTOR * (1 - expectedW));
      eloData[loser.modelId].elo += Math.round(K_FACTOR * (0 - expectedL));
      eloData[winner.modelId].wins++;
      eloData[loser.modelId].losses++;
    }

    eloData[winner.modelId].totalBattles++;
    eloData[loser.modelId].totalBattles++;
  }
}

// ---------------------------------------------------------------------------
// Technique Stats Tracking
// ---------------------------------------------------------------------------
function updateTechniqueStats(
  technique: PromptTechnique,
  category: string,
  avgScore: number
): void {
  const stats = loadJSON<Record<string, TechniqueStats>>(TECHNIQUE_STATS_FILE, {});

  if (!stats[technique]) {
    stats[technique] = {
      technique,
      uses: 0,
      avgScore: 0,
      totalScore: 0,
      categoryScores: {},
    };
  }

  const entry = stats[technique];
  entry.uses++;
  entry.totalScore += avgScore;
  entry.avgScore = entry.totalScore / entry.uses;

  if (!entry.categoryScores[category]) {
    entry.categoryScores[category] = { uses: 0, totalScore: 0 };
  }
  entry.categoryScores[category].uses++;
  entry.categoryScores[category].totalScore += avgScore;

  saveJSON(TECHNIQUE_STATS_FILE, stats);
}

// ---------------------------------------------------------------------------
// Battle Orchestrator — now with technique integration
// ---------------------------------------------------------------------------
async function runBattle(
  task: string,
  category: string = "General",
  modelIds?: string[],
  technique?: PromptTechnique
): Promise<Battle> {
  const models = modelIds
    ? MODEL_REGISTRY.filter((m) => modelIds.includes(m.id))
    : MODEL_REGISTRY;

  // Auto-select technique if not provided
  const selectedTechnique = technique || autoSelectTechnique(category);
  const criteria = getCriteria(category);
  const battleId = `B-${Date.now().toString(36).toUpperCase()}`;

  // Apply technique to enhance the prompt
  const enhancedPrompts = applyTechnique(selectedTechnique, task, category);
  const primaryPrompt = enhancedPrompts[0];

  console.log(`\n⚔  Battle ${battleId}`);
  console.log(`   Task: ${task}`);
  console.log(`   Category: ${category}`);
  console.log(`   Technique: ${selectedTechnique} — ${getTechniqueDescription(selectedTechnique)}`);
  console.log(`   Competitors: ${models.map((m) => m.name).join(", ")}`);
  console.log(`   Criteria: ${criteria.join(", ")}\n`);

  // Phase 1: Dispatch enhanced prompt to all models in parallel
  console.log("   Dispatching technique-enhanced prompt...");
  const results = await Promise.all(models.map((m) => callModel(m, primaryPrompt)));

  for (const r of results) {
    const status = r.error ? `ERROR: ${r.error}` : `${r.outputTokens} tokens, ${r.latencyMs}ms, $${r.cost.toFixed(4)}`;
    console.log(`   ${r.modelId}: ${status}`);
  }

  // Self-Consistency: run additional variants and pick best per model
  if (selectedTechnique === "self_consistency" && enhancedPrompts.length > 1) {
    console.log(`\n   Running ${enhancedPrompts.length - 1} additional self-consistency variants...`);
    for (let v = 1; v < enhancedPrompts.length; v++) {
      const variantResults = await Promise.all(models.map((m) => callModel(m, enhancedPrompts[v])));
      // Merge: keep best output per model (longest non-error response as proxy)
      for (let j = 0; j < results.length; j++) {
        if (!results[j].error && !variantResults[j].error) {
          if (variantResults[j].output.length > results[j].output.length) {
            results[j] = variantResults[j];
          }
        }
      }
    }
  }

  // Phase 2: Judge
  console.log("\n   Judging responses...");
  const validResults = results.filter((r) => !r.error);
  const scores = await judgeResponses(task, category, criteria, selectedTechnique, validResults);

  const sorted = [...scores].sort((a, b) => b.overall - a.overall);
  const winnerId = sorted[0]?.modelId || "none";

  console.log("\n   Results:");
  for (const s of sorted) {
    const medal = s.modelId === winnerId ? "🏆" : "  ";
    console.log(`   ${medal} ${s.modelId}: ${s.overall}/100 — ${s.reasoning.substring(0, 80)}`);
  }

  // Phase 3: Update Elo
  const eloData = loadJSON<Record<string, EloEntry>>(ELO_FILE, {});
  updateElo(eloData, scores);
  saveJSON(ELO_FILE, eloData);

  // Phase 4: Update technique stats
  const avgScore = scores.reduce((sum, s) => sum + s.overall, 0) / scores.length;
  updateTechniqueStats(selectedTechnique, category, avgScore);

  // Phase 5: Persist battle
  const battles = loadJSON<Battle[]>(BATTLES_FILE, []);
  const battle: Battle = {
    id: battleId,
    task,
    category,
    technique: selectedTechnique,
    enhancedPrompt: primaryPrompt.substring(0, 500),
    timestamp: new Date().toISOString(),
    competitors: results,
    scores,
    winner: winnerId,
    criteria,
  };
  battles.unshift(battle);
  saveJSON(BATTLES_FILE, battles.slice(0, 500));

  // Phase 6: Self-Learning — record outcomes for adaptive routing
  for (const s of scores) {
    const competitor = results.find((r) => r.modelId === s.modelId);
    recordLearning({
      battleId,
      timestamp: new Date().toISOString(),
      category,
      technique: selectedTechnique,
      modelId: s.modelId,
      score: s.overall,
      won: s.modelId === winnerId,
      latencyMs: competitor?.latencyMs || 0,
      cost: competitor?.cost || 0,
      errorOccurred: !!competitor?.error,
    });
  }

  // Phase 7: Self-Correcting — detect anomalies
  for (const s of scores) {
    const anomaly = isAnomalousScore(s.overall, category);
    if (anomaly.anomalous) {
      console.log(`   ⚠  Anomalous score detected: ${s.modelId} ${s.overall} — ${anomaly.reason}`);
    }
  }

  const techCheck = isTechniqueUnderperforming(selectedTechnique, category);
  if (techCheck.underperforming) {
    console.log(`   ⚠  Technique alert: ${techCheck.recommendation}`);
  }

  for (const entry of Object.values(eloData)) {
    const health = checkEloHealth(entry.modelId, entry.elo);
    if (health.alert) {
      console.log(`   ⚠  Elo alert: ${health.message}`);
    }
  }

  // Phase 8: Self-Learning — update routing weights
  updateRoutingWeights();

  console.log(`\n   Winner: ${winnerId}`);
  console.log(`   Technique: ${selectedTechnique}`);
  console.log(`   Elo standings:`);
  Object.values(eloData)
    .sort((a, b) => b.elo - a.elo)
    .forEach((e, i) => console.log(`     #${i + 1} ${e.modelId}: ${e.elo} (${e.wins}W-${e.losses}L)`));

  // Show learned routing if available
  const learned = getLearnedRoute(category);
  if (learned) {
    console.log(`\n   Learned route for ${category}: ${learned.bestModel} + ${learned.bestTechnique} (${learned.confidence}% confidence, ${learned.sampleSize} samples)`);
  }

  return battle;
}

/**
 * Technique Battle: Same model, different techniques — which prompt approach wins?
 *
 * Dispatches the SAME task to the SAME model using different prompt techniques,
 * then judges which technique produced the best output.
 */
async function runTechniqueBattle(
  task: string,
  category: string = "General",
  modelId: string = "claude-sonnet",
  techniques?: PromptTechnique[]
): Promise<TechniqueBattle> {
  const model = MODEL_REGISTRY.find((m) => m.id === modelId) || MODEL_REGISTRY[1];
  const selectedTechniques = techniques || [
    autoSelectTechnique(category),
    "chain_of_thought",
    "role_based",
    "few_shot",
  ].filter((t, i, arr) => arr.indexOf(t) === i) as PromptTechnique[]; // dedupe

  const battleId = `TB-${Date.now().toString(36).toUpperCase()}`;

  console.log(`\n🔬 Technique Battle ${battleId}`);
  console.log(`   Task: ${task}`);
  console.log(`   Model: ${model.name}`);
  console.log(`   Techniques: ${selectedTechniques.join(", ")}\n`);

  // Dispatch same task with each technique to the same model
  const techniqueResults: TechniqueBattle["techniques"] = [];
  for (const tech of selectedTechniques) {
    const enhanced = applyTechnique(tech, task, category);
    console.log(`   Running ${tech}...`);
    const result = await callModel(model, enhanced[0]);
    techniqueResults.push({
      technique: tech,
      enhancedPrompt: enhanced[0].substring(0, 300),
      result,
      score: 0, // filled by judge
    });
  }

  // Judge the technique outputs
  const client = new Anthropic();
  const outputBlock = techniqueResults
    .filter((t) => !t.result.error)
    .map((t) => `### Technique: ${t.technique}\n${t.result.output}`)
    .join("\n\n---\n\n");

  const judgeResponse = await client.messages.create({
    model: "claude-opus-4-6",
    max_tokens: 2048,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    thinking: { type: "adaptive" } as any,
    messages: [
      {
        role: "user",
        content: `You are judging a prompt technique competition for SkyyRose luxury streetwear brand.

The SAME model (${model.name}) was given the SAME task using DIFFERENT prompt techniques.
Evaluate which technique produced the best output.

TASK: "${task}"
CATEGORY: ${category}

OUTPUTS BY TECHNIQUE:
${outputBlock}

Score each technique's output 0-100 on: Quality, Brand Alignment, Completeness, Technique Effectiveness.

Respond in JSON:
{
  "scores": [
    { "technique": "technique_name", "score": 85, "reasoning": "Why this score" }
  ]
}`,
      },
    ],
  });

  const judgeText = judgeResponse.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("");

  try {
    const jsonMatch = judgeText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      for (const s of parsed.scores) {
        const entry = techniqueResults.find((t) => t.technique === s.technique);
        if (entry) entry.score = s.score;
      }
    }
  } catch {
    // Default scores on parse failure
    techniqueResults.forEach((t) => (t.score = 75));
  }

  const winner = techniqueResults.reduce((best, t) => (t.score > best.score ? t : best), techniqueResults[0]);

  console.log("\n   Technique Rankings:");
  techniqueResults
    .sort((a, b) => b.score - a.score)
    .forEach((t, i) => {
      const medal = i === 0 ? "🏆" : "  ";
      console.log(`   ${medal} ${t.technique}: ${t.score}/100`);
    });

  const techniqueBattle: TechniqueBattle = {
    id: battleId,
    task,
    category,
    modelId: model.id,
    timestamp: new Date().toISOString(),
    techniques: techniqueResults,
    winner: winner.technique,
  };

  // Persist
  const battles = loadJSON<Battle[]>(BATTLES_FILE, []);
  battles.unshift(techniqueBattle as any);
  saveJSON(BATTLES_FILE, battles.slice(0, 500));

  // Update technique stats for each
  for (const t of techniqueResults) {
    updateTechniqueStats(t.technique, category, t.score);
  }

  return techniqueBattle;
}

function getCriteria(category: string): string[] {
  const map: Record<string, string[]> = {
    Content: ["Brand Voice", "Emotional Impact", "Conversion Potential", "Accuracy"],
    SEO: ["Keyword Relevance", "Click-Through Appeal", "Character Limits", "Brand Alignment"],
    "Social Media": ["Platform Fit", "Engagement Potential", "Brand Alignment", "CTA Strength"],
    Email: ["Subject Line Appeal", "Open Rate Potential", "Brand Voice", "Personalization"],
    Analytics: ["Analytical Depth", "Actionability", "Data Accuracy", "Clarity"],
    Support: ["Accuracy", "Empathy", "Resolution Speed", "Brand Voice"],
    Code: ["Correctness", "Readability", "Performance", "Best Practices"],
    Creative: ["Originality", "Brand Alignment", "Emotional Impact", "Technical Execution"],
    Pricing: ["Analytical Rigor", "Market Awareness", "Actionability", "Brand Fit"],
  };
  return map[category] || ["Quality", "Relevance", "Clarity", "Brand Alignment"];
}

// ---------------------------------------------------------------------------
// MCP Server — expose as tools for Agent SDK
// ---------------------------------------------------------------------------
const runBattleTool = tool(
  "run-battle",
  "Run a live LLM battle: dispatch task to multiple models with auto-selected prompt technique, judge responses, update Elo. Returns winner + scores + technique used.",
  {
    task: z.string().describe("The task/prompt for all models to compete on"),
    category: z.string().optional().describe("Category: Content, SEO, Social Media, Email, Analytics, Support, Code, Creative, Pricing"),
    models: z.string().optional().describe("Comma-separated model IDs to compete (default: all)"),
    technique: z.string().optional().describe("Prompt technique: chain_of_thought, tree_of_thoughts, react, rag, few_shot, structured_output, constitutional, role_based, self_consistency, ensemble (default: auto-select by category)"),
  },
  async ({ task, category, models, technique }) => {
    const modelIds = models?.split(",").map((s) => s.trim());
    const tech = technique as PromptTechnique | undefined;
    const battle = await runBattle(task, category || "General", modelIds, tech);
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            { id: battle.id, winner: battle.winner, technique: battle.technique, scores: battle.scores, category: battle.category },
            null,
            2
          ),
        },
      ],
    };
  }
);

const runTechniqueBattleTool = tool(
  "run-technique-battle",
  "Technique A/B test: same model, different prompt techniques. Reveals which technique produces the best output for a given task type. Useful for optimizing the auto-router.",
  {
    task: z.string().describe("The task/prompt to test across techniques"),
    category: z.string().optional().describe("Category for technique selection"),
    model: z.string().optional().describe("Model ID to use (default: claude-sonnet)"),
    techniques: z.string().optional().describe("Comma-separated techniques to compare (default: auto-select 4)"),
  },
  async ({ task, category, model, techniques }) => {
    const techs = techniques?.split(",").map((s) => s.trim()) as PromptTechnique[] | undefined;
    const result = await runTechniqueBattle(task, category || "General", model || "claude-sonnet", techs);
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              id: result.id,
              winner: result.winner,
              model: result.modelId,
              rankings: result.techniques.sort((a, b) => b.score - a.score).map((t) => ({
                technique: t.technique,
                score: t.score,
              })),
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

const getLeaderboardTool = tool(
  "get-leaderboard",
  "Get current Elo leaderboard with win/loss records",
  {},
  async () => {
    const eloData = loadJSON<Record<string, EloEntry>>(ELO_FILE, {});
    const sorted = Object.values(eloData).sort((a, b) => b.elo - a.elo);
    return { content: [{ type: "text" as const, text: JSON.stringify(sorted, null, 2) }] };
  }
);

const getBattleHistoryTool = tool(
  "get-battle-history",
  "Get recent battle history with winners, scores, and techniques used",
  { limit: z.number().optional().describe("Number of battles to return (default 10)") },
  async ({ limit }) => {
    const battles = loadJSON<Battle[]>(BATTLES_FILE, []);
    const recent = battles.slice(0, limit || 10).map((b) => ({
      id: b.id,
      task: b.task.substring(0, 80),
      category: b.category,
      technique: b.technique,
      winner: b.winner,
      topScore: b.scores?.sort((a: any, c: any) => c.overall - a.overall)[0]?.overall,
      timestamp: b.timestamp,
    }));
    return { content: [{ type: "text" as const, text: JSON.stringify(recent, null, 2) }] };
  }
);

const getTechniqueStatsTool = tool(
  "get-technique-stats",
  "Get performance statistics for each prompt technique across all battles. Shows which techniques produce the highest scores per category.",
  {},
  async () => {
    const stats = loadJSON<Record<string, TechniqueStats>>(TECHNIQUE_STATS_FILE, {});
    const sorted = Object.values(stats).sort((a, b) => b.avgScore - a.avgScore);
    return { content: [{ type: "text" as const, text: JSON.stringify(sorted, null, 2) }] };
  }
);

const listTechniquesTool = tool(
  "list-techniques",
  "List all 10 available prompt techniques with descriptions and category mappings",
  {},
  async () => {
    const techniqueInfo = ALL_TECHNIQUES.map((t) => ({
      technique: t,
      description: getTechniqueDescription(t),
      bestFor: Object.entries(CATEGORY_TECHNIQUE_MAP)
        .filter(([_, tech]) => tech === t)
        .map(([cat]) => cat),
    }));
    return { content: [{ type: "text" as const, text: JSON.stringify(techniqueInfo, null, 2) }] };
  }
);

const getHealthReportTool = tool(
  "get-health-report",
  "Get adaptive system health: routing weights, circuit breakers, recent corrections, learning record count",
  {},
  async () => {
    const report = getHealthReport();
    return { content: [{ type: "text" as const, text: JSON.stringify(report, null, 2) }] };
  }
);

const getCorrectionsTool = tool(
  "get-corrections",
  "Get recent self-corrections: anomalous scores, technique downgrades, Elo alerts, circuit breaks",
  { limit: z.number().optional().describe("Number of corrections to return (default 20)") },
  async ({ limit }) => {
    const corrections = getRecentCorrections(limit || 20);
    return { content: [{ type: "text" as const, text: JSON.stringify(corrections, null, 2) }] };
  }
);

export const roundtableServer = createSdkMcpServer({
  name: "llm-roundtable",
  tools: [
    runBattleTool,
    runTechniqueBattleTool,
    getLeaderboardTool,
    getBattleHistoryTool,
    getTechniqueStatsTool,
    listTechniquesTool,
    getHealthReportTool,
    getCorrectionsTool,
  ],
});

// ---------------------------------------------------------------------------
// CLI Entry Point
// ---------------------------------------------------------------------------
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
LLM Roundtable — Live Battle Engine with 10 Prompt Techniques

Usage:
  npx tsx agents/llm_roundtable/engine.ts "Task prompt here"
  npx tsx agents/llm_roundtable/engine.ts --category "SEO" "Write meta descriptions"
  npx tsx agents/llm_roundtable/engine.ts --technique "chain_of_thought" "Analyze pricing"
  npx tsx agents/llm_roundtable/engine.ts --technique-battle "Write brand copy" --category "Content"
  npx tsx agents/llm_roundtable/engine.ts --models "claude-opus,gpt-4o" "Task"
  npx tsx agents/llm_roundtable/engine.ts --leaderboard
  npx tsx agents/llm_roundtable/engine.ts --technique-stats
  npx tsx agents/llm_roundtable/engine.ts --agent "Run 3 battles for SkyyRose content"

Models: ${MODEL_REGISTRY.map((m) => m.id).join(", ")}
Categories: ${Object.keys(CATEGORY_TECHNIQUE_MAP).join(", ")}
Techniques: ${ALL_TECHNIQUES.join(", ")}
`);
    return;
  }

  if (args[0] === "--leaderboard") {
    const eloData = loadJSON<Record<string, EloEntry>>(ELO_FILE, {});
    const sorted = Object.values(eloData).sort((a, b) => b.elo - a.elo);
    console.log("\n  LLM Roundtable — Elo Leaderboard\n");
    sorted.forEach((e, i) => {
      const wr = e.totalBattles > 0 ? ((e.wins / e.totalBattles) * 100).toFixed(1) : "0.0";
      console.log(`  #${i + 1}  ${e.elo}  ${e.modelId}  (${e.wins}W-${e.losses}L-${e.draws}D, ${wr}% WR)`);
    });
    return;
  }

  if (args[0] === "--technique-stats") {
    const stats = loadJSON<Record<string, TechniqueStats>>(TECHNIQUE_STATS_FILE, {});
    const sorted = Object.values(stats).sort((a, b) => b.avgScore - a.avgScore);
    console.log("\n  Prompt Technique Performance\n");
    sorted.forEach((s, i) => {
      console.log(`  #${i + 1}  ${s.avgScore.toFixed(1)} avg  ${s.technique}  (${s.uses} uses)`);
      for (const [cat, data] of Object.entries(s.categoryScores)) {
        const catAvg = data.totalScore / data.uses;
        console.log(`       └─ ${cat}: ${catAvg.toFixed(1)} avg (${data.uses} uses)`);
      }
    });
    return;
  }

  // Parse flags
  let category = "General";
  let models: string[] | undefined;
  let technique: PromptTechnique | undefined;
  let agentMode = false;
  let techniqueBattleMode = false;
  const taskParts: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--category" && args[i + 1]) {
      category = args[++i];
    } else if (args[i] === "--models" && args[i + 1]) {
      models = args[++i].split(",").map((s) => s.trim());
    } else if (args[i] === "--technique" && args[i + 1]) {
      technique = args[++i] as PromptTechnique;
    } else if (args[i] === "--technique-battle") {
      techniqueBattleMode = true;
    } else if (args[i] === "--agent") {
      agentMode = true;
    } else {
      taskParts.push(args[i]);
    }
  }

  const task = taskParts.join(" ");

  if (techniqueBattleMode) {
    await runTechniqueBattle(task, category);
    return;
  }

  if (agentMode) {
    for await (const message of query({
      prompt: task,
      options: {
        cwd: path.resolve(__dirname, "../.."),
        model: "claude-opus-4-6",
        allowedTools: ["Read", "Glob", "Grep"],
        systemPrompt: `You are the LLM Roundtable Orchestrator for SkyyRose luxury streetwear.
You have tools to run battles between AI models, A/B test prompt techniques, check leaderboards, and view history.

PROMPT TECHNIQUES AVAILABLE:
${ALL_TECHNIQUES.map((t) => `- ${t}: ${getTechniqueDescription(t)}`).join("\n")}

Use run-battle for model-vs-model competitions (technique auto-selected by category).
Use run-technique-battle to A/B test which prompt technique works best for a task type.
Use list-techniques to see all techniques and their category mappings.
Use get-technique-stats to see which techniques perform best historically.

After battles, analyze results and recommend optimizations for the auto-router.

Brand: SkyyRose — Oakland luxury streetwear.
Collections: Black Rose, Love Hurts, Signature, Kids Capsule.`,
        mcpServers: { roundtable: roundtableServer },
      },
    })) {
      if ("result" in message) console.log(message.result);
    }
  } else {
    await runBattle(task, category, models, technique);
  }
}

main().catch(console.error);
