# PRD: Prompt Enhancer CLI

## Overview
A standalone CLI tool that transforms natural language prompts into optimized, executive-level prompts for Claude. The enhancer analyzes input, auto-detects task type, selects appropriate prompt engineering techniques, and injects relevant context from the codebase—all configurable with override flags.

## Goals
- Transform casual prompts into high-quality, structured prompts
- Automatically select optimal prompt engineering techniques based on task type
- Inject relevant codebase context to improve Claude's responses
- Track enhancement analytics to learn which techniques work best
- Provide pipe-friendly CLI interface with multiple output formats

## Quality Gates

These commands must pass for every user story:
- `pytest -v` - All tests passing
- `isort .` - Import sorting
- `ruff check --fix` - Linting
- `black .` - Code formatting

## User Stories

### US-001: Basic CLI Structure
**Description:** As a developer, I want a CLI entry point so that I can enhance prompts from my terminal.

**Acceptance Criteria:**
- [ ] Create `cli/prompt_enhance.py` with click CLI framework
- [ ] Support `prompt-enhance "my prompt"` invocation
- [ ] Support piped input: `echo "my prompt" | prompt-enhance`
- [ ] Add `--help` with clear usage examples
- [ ] Register as console script in `pyproject.toml`

### US-002: Prompt Analysis Engine
**Description:** As a user, I want my prompt analyzed for intent, complexity, and task type so that the right enhancement strategy is selected.

**Acceptance Criteria:**
- [ ] Create `PromptAnalyzer` class in `cli/prompt_enhance.py`
- [ ] Detect task type: code, writing, analysis, creative, debugging, refactoring
- [ ] Assess prompt clarity score (0-100)
- [ ] Identify missing elements (context, constraints, examples, output format)
- [ ] Return structured `PromptAnalysis` dataclass

### US-003: Technique Selection Engine
**Description:** As a user, I want the enhancer to automatically select the best prompt engineering techniques for my task type.

**Acceptance Criteria:**
- [ ] Create `TechniqueSelector` class
- [ ] Implement technique registry with: chain-of-thought, tree-of-thoughts, few-shot, role-assignment, self-consistency, metacognition, step-by-step, constraints-first
- [ ] Map task types to recommended techniques
- [ ] Support technique combinations (e.g., role + chain-of-thought + constraints)
- [ ] Return `TechniqueSelection` with reasoning

### US-004: Context Injection System
**Description:** As a user, I want relevant codebase context auto-injected into my prompt so Claude has the information it needs.

**Acceptance Criteria:**
- [ ] Implement `ContextScanner` class
- [ ] Auto-scan current directory for relevant files based on prompt keywords
- [ ] Support `--context file1.py,file2.py` for explicit context
- [ ] Support `--no-context` to disable auto-scanning
- [ ] Limit context to configurable token budget (default 2000 tokens)
- [ ] Prioritize most relevant snippets using keyword matching

### US-005: Prompt Enhancement Core
**Description:** As a user, I want my prompt transformed into an optimized version using Claude API.

**Acceptance Criteria:**
- [ ] Create `PromptEnhancer` class that orchestrates analysis → technique → context → generation
- [ ] Call Claude API with meta-prompt for enhancement
- [ ] Include selected techniques in enhancement instructions
- [ ] Preserve user's core intent while adding structure
- [ ] Return `EnhancedPrompt` with original, enhanced, and metadata

### US-006: Mode Detection and Override
**Description:** As a user, I want the tool to auto-detect my task mode with the option to override.

**Acceptance Criteria:**
- [ ] Implement auto-detection based on keywords and patterns
- [ ] Support `--mode code|writing|analysis|creative|debug|refactor`
- [ ] Mode affects technique selection and enhancement style
- [ ] Show detected mode in verbose output

### US-007: Preview and Auto Modes
**Description:** As a user, I want to preview enhanced prompts before use, or auto-send them.

**Acceptance Criteria:**
- [ ] Default behavior: show enhanced prompt and exit
- [ ] `--preview` flag: show side-by-side comparison (original vs enhanced)
- [ ] `--auto` flag: output only the enhanced prompt (for piping)
- [ ] `--copy` flag: copy enhanced prompt to clipboard

### US-008: Configurable Output Formats
**Description:** As a user, I want to choose output format based on my workflow needs.

**Acceptance Criteria:**
- [ ] `--format plain` (default): clean text output
- [ ] `--format md`: markdown with technique annotations
- [ ] `--format json`: full metadata including analysis, techniques, confidence
- [ ] JSON schema documented in help text

### US-009: Analytics and History Tracking
**Description:** As a user, I want enhancement history tracked so I can learn which techniques work best.

**Acceptance Criteria:**
- [ ] Create `~/.prompt-enhance/` directory on first run
- [ ] Log each enhancement to `history.jsonl` with timestamp, original, enhanced, techniques, mode
- [ ] Implement `prompt-enhance --stats` to show technique usage analytics
- [ ] Track success patterns (which techniques for which task types)
- [ ] Support `--no-log` to disable tracking

### US-010: Configuration File Support
**Description:** As a user, I want to configure defaults so I don't repeat flags.

**Acceptance Criteria:**
- [ ] Support `~/.prompt-enhance/config.yaml` for defaults
- [ ] Configurable: default mode, output format, context budget, API settings
- [ ] CLI flags override config file
- [ ] `prompt-enhance --init` creates default config

### US-011: Unit Tests with Mocks
**Description:** As a developer, I want comprehensive unit tests with mocked API calls.

**Acceptance Criteria:**
- [ ] Test `PromptAnalyzer` with various prompt types
- [ ] Test `TechniqueSelector` technique mapping logic
- [ ] Test `ContextScanner` file discovery
- [ ] Test `PromptEnhancer` with mocked Claude responses
- [ ] Test CLI argument parsing
- [ ] Achieve >90% code coverage

### US-012: Integration Tests with Real API
**Description:** As a developer, I want integration tests that verify real Claude API enhancement.

**Acceptance Criteria:**
- [ ] Create `tests/cli/test_prompt_enhance_integration.py`
- [ ] Mark with `@pytest.mark.integration`
- [ ] Test end-to-end enhancement flow
- [ ] Verify enhanced prompts are structurally valid
- [ ] Skip in CI if `ANTHROPIC_API_KEY` not set

## Functional Requirements

- FR-1: The tool must accept prompts via argument or stdin pipe
- FR-2: The tool must analyze prompts and detect task type within 100ms (local analysis)
- FR-3: The tool must call Claude API for enhancement (typically 1-3 seconds)
- FR-4: The tool must respect `ANTHROPIC_API_KEY` environment variable
- FR-5: The tool must gracefully handle API errors with helpful messages
- FR-6: The tool must limit context injection to token budget to avoid bloat
- FR-7: The tool must preserve the user's core intent in all enhancements
- FR-8: The tool must work offline for `--stats` and `--help` commands

## Non-Goals

- GUI or web interface (CLI only for v1)
- Support for non-Claude LLMs (Claude-only for v1)
- Real-time prompt streaming during enhancement
- Prompt template library/marketplace
- Team/shared analytics

## Technical Considerations

- Use `click` for CLI framework (consistent with existing DevSkyy CLI tools)
- Use `anthropic` Python SDK for API calls
- Store history in JSONL for easy append and streaming reads
- Consider async for API calls if adding batch mode later
- Meta-prompt for enhancement should itself be well-engineered

### Meta-Prompt Strategy
The enhancer uses a carefully crafted meta-prompt to instruct Claude on enhancement:
```
You are an elite prompt engineer. Transform the following prompt into an optimized version.

Task Type: {detected_mode}
Selected Techniques: {techniques}
Context Available: {context_summary}

Original Prompt:
{user_prompt}

Enhancement Guidelines:
1. Preserve the user's core intent
2. Add clear structure and formatting
3. Apply {techniques} appropriately
4. Include relevant constraints
5. Specify desired output format
6. Add examples if beneficial

Output only the enhanced prompt, no explanations.
```

## Success Metrics

- Enhancement latency < 5 seconds average
- User intent preservation rate > 95% (manual review)
- Analytics show technique effectiveness patterns within 50 uses
- Zero crashes on malformed input

## Open Questions

- Should we add a `--interactive` mode for iterative refinement?
- Should enhanced prompts include a "meta" section explaining the techniques used?
- Consider adding `--cost` flag to show estimated API cost before enhancement?
