/**
 * DevSkyy Coding Architect Agent
 *
 * A full-featured coding architect agent specialized in TypeScript and Python development,
 * powered by Claude Agent SDK with 17 prompt engineering techniques.
 *
 * @example
 * ```typescript
 * import { createCodingArchitectAgent } from './index.js';
 *
 * const agent = createCodingArchitectAgent({
 *   workingDirectory: process.cwd(),
 *   verbose: true,
 * });
 *
 * const result = await agent.query("Review this TypeScript code for best practices");
 * console.log(result);
 * ```
 */

import { query, type SDKMessage } from "@anthropic-ai/claude-agent-sdk";
import { config } from "dotenv";

import SYSTEM_PROMPT, { TASK_PROMPTS, PROMPT_TECHNIQUES } from "./prompts/system-prompt.js";
import { typescriptToolsServer } from "./tools/typescript-tools.js";
import { pythonToolsServer } from "./tools/python-tools.js";
import type { AgentConfig, AgentResult, MessageHandler } from "./types/index.js";

// Load environment variables
config();

/**
 * Default configuration for the coding architect agent
 */
const DEFAULT_CONFIG: Required<AgentConfig> = {
  model: "claude-sonnet-4-5",
  workingDirectory: process.cwd(),
  maxBudgetUsd: 10.0,
  verbose: false,
};

/**
 * Create a coding architect agent instance
 */
export function createCodingArchitectAgent(userConfig: AgentConfig = {}) {
  const agentConfig: Required<AgentConfig> = {
    ...DEFAULT_CONFIG,
    ...userConfig,
  };

  /**
   * Execute a query with the coding architect agent
   */
  async function executeQuery(
    prompt: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const messages: SDKMessage[] = [];
    let sessionId = "";
    let result = "";
    let totalCostUsd = 0;
    let durationMs = 0;

    const startTime = Date.now();

    try {
      const response = query({
        prompt,
        options: {
          model: agentConfig.model,
          systemPrompt: SYSTEM_PROMPT,
          cwd: agentConfig.workingDirectory,
          maxBudgetUsd: agentConfig.maxBudgetUsd,
          permissionMode: "default",
          mcpServers: {
            "typescript-tools": typescriptToolsServer,
            "python-tools": pythonToolsServer,
          },
          allowedTools: [
            // Core tools
            "Read",
            "Write",
            "Edit",
            "Glob",
            "Grep",
            "Bash",
            // Custom MCP tools
            "mcp__typescript-tools__ts_type_check",
            "mcp__typescript-tools__ts_analyze_config",
            "mcp__typescript-tools__ts_dependency_audit",
            "mcp__typescript-tools__ts_analyze_complexity",
            "mcp__typescript-tools__ts_lint_check",
            "mcp__typescript-tools__ts_generate_types",
            "mcp__python-tools__py_type_check",
            "mcp__python-tools__py_lint",
            "mcp__python-tools__py_format",
            "mcp__python-tools__py_dependency_audit",
            "mcp__python-tools__py_venv_info",
            "mcp__python-tools__py_analyze_complexity",
            "mcp__python-tools__py_test_runner",
            "mcp__python-tools__py_generate_stubs",
          ],
        },
      });

      for await (const message of response) {
        messages.push(message);

        // Handle different message types
        switch (message.type) {
          case "system":
            if (message.subtype === "init") {
              sessionId = message.session_id;
              if (agentConfig.verbose) {
                console.log(`[Session] Started: ${sessionId}`);
                console.log(`[Model] ${message.model}`);
              }
            }
            break;

          case "assistant":
            if (agentConfig.verbose) {
              const text = message.message.content
                .flatMap((block) => (block.type === "text" ? [block.text] : []))
                .join("");
              if (text) {
                console.log(`[Assistant] ${text.slice(0, 100)}...`);
              }
            }
            break;

          case "result":
            if (message.subtype === "success") {
              result = message.result;
              totalCostUsd = message.total_cost_usd;
              durationMs = message.duration_ms;
            } else {
              console.error(`[Error] ${message.subtype}:`, message.errors);
            }
            break;
        }

        // Call custom message handler if provided
        if (onMessage) {
          await onMessage(message);
        }
      }
    } catch (error) {
      console.error("[Error] Query failed:", error);
      throw error;
    }

    durationMs = durationMs || Date.now() - startTime;

    return {
      sessionId,
      messages,
      result,
      totalCostUsd,
      durationMs,
    };
  }

  /**
   * Code review with Chain-of-Thought reasoning
   */
  async function reviewCode(
    filePath: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const prompt = `${TASK_PROMPTS.codeReview}

Please review the code in: ${filePath}`;
    return executeQuery(prompt, onMessage);
  }

  /**
   * Architecture design with Tree of Thoughts
   */
  async function designArchitecture(
    requirements: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const prompt = `${TASK_PROMPTS.architectureDesign}

Requirements: ${requirements}`;
    return executeQuery(prompt, onMessage);
  }

  /**
   * Debug an issue with ReAct pattern
   */
  async function debugIssue(
    issue: string,
    context?: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const prompt = `${TASK_PROMPTS.debugging}

Issue: ${issue}
${context ? `\nContext: ${context}` : ""}`;
    return executeQuery(prompt, onMessage);
  }

  /**
   * Refactor code with Constitutional AI principles
   */
  async function refactorCode(
    filePath: string,
    goals?: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const prompt = `${TASK_PROMPTS.refactoring}

File to refactor: ${filePath}
${goals ? `\nRefactoring goals: ${goals}` : ""}`;
    return executeQuery(prompt, onMessage);
  }

  /**
   * Analyze TypeScript code
   */
  async function analyzeTypeScript(
    target: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const prompt = `${TASK_PROMPTS.typeScriptAnalysis}

Target: ${target}`;
    return executeQuery(prompt, onMessage);
  }

  /**
   * Analyze Python code
   */
  async function analyzePython(
    target: string,
    onMessage?: MessageHandler
  ): Promise<AgentResult> {
    const prompt = `${TASK_PROMPTS.pythonAnalysis}

Target: ${target}`;
    return executeQuery(prompt, onMessage);
  }

  return {
    // Core query method
    query: executeQuery,

    // Specialized methods
    reviewCode,
    designArchitecture,
    debugIssue,
    refactorCode,
    analyzeTypeScript,
    analyzePython,

    // Configuration
    config: agentConfig,

    // Constants
    PROMPT_TECHNIQUES,
    TASK_PROMPTS,
  };
}

// Export types
export type { AgentConfig, AgentResult, MessageHandler };
export { SYSTEM_PROMPT, TASK_PROMPTS, PROMPT_TECHNIQUES };
export { typescriptToolsServer } from "./tools/typescript-tools.js";
export { pythonToolsServer } from "./tools/python-tools.js";

/**
 * Main entry point for CLI usage
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
╔══════════════════════════════════════════════════════════════════╗
║           DevSkyy Coding Architect Agent                         ║
║   Expert in TypeScript & Python with 17 Prompt Techniques        ║
╚══════════════════════════════════════════════════════════════════╝

Usage:
  npm start "<your prompt>"

Examples:
  npm start "Review the code in src/index.ts"
  npm start "Design an architecture for a REST API"
  npm start "Analyze the Python project in ./python"

Environment:
  ANTHROPIC_API_KEY  - Your Anthropic API key (required)
`);
    return;
  }

  const prompt = args.join(" ");
  console.log(`\n🤖 Coding Architect Agent\n`);
  console.log(`📝 Prompt: ${prompt}\n`);
  console.log("─".repeat(60));

  const agent = createCodingArchitectAgent({
    verbose: true,
    workingDirectory: process.cwd(),
  });

  try {
    const result = await agent.query(prompt, (message) => {
      if (message.type === "assistant") {
        // Stream assistant messages
        const content = message.message.content;
        if (typeof content === "string") {
          process.stdout.write(".");
        }
      }
    });

    console.log("\n" + "─".repeat(60));
    console.log("\n📊 Result:\n");
    console.log(result.result);
    console.log("\n" + "─".repeat(60));
    console.log(`💰 Cost: $${result.totalCostUsd.toFixed(4)}`);
    console.log(`⏱️  Duration: ${(result.durationMs / 1000).toFixed(2)}s`);
  } catch (error) {
    console.error("\n❌ Error:", error);
    process.exit(1);
  }
}

// Run main if this is the entry point
main().catch(console.error);
