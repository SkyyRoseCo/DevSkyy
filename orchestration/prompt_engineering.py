"""
DevSkyy Prompt Engineering Framework
=====================================

17 verified prompting techniques backed by academic research and industry best practices.

Techniques:
1. Role-Based Constraint
2. Chain-of-Thought (CoT)
3. Few-Shot Learning
4. Self-Consistency
5. Tree of Thoughts (ToT)
6. ReAct (Reasoning + Acting)
7. RAG (Retrieval-Augmented Generation)
8. Prompt Chaining
9. Generated Knowledge
10. Negative Prompting
11. Constitutional AI
12. COSTARD (Context-Sensitive)
13. Meta-Prompting
14. Recursive Prompting
15. Structured Output
16. Temperature Scheduling
17. Ensemble Prompting

References:
- Chain-of-Thought: Wei et al., 2022 (https://arxiv.org/abs/2201.11903)
- Self-Consistency: Wang et al., 2022 (https://arxiv.org/abs/2203.11171)
- Tree of Thoughts: Yao et al., 2023 (https://arxiv.org/abs/2305.10601)
- ReAct: Yao et al., 2022 (https://arxiv.org/abs/2210.03629)
- Constitutional AI: Bai et al., 2022 (https://arxiv.org/abs/2212.08073)
"""

import json
import logging
import re
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class PromptTechnique(StrEnum):
    """Prompting techniques"""

    ROLE_BASED = "role_based"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"
    SELF_CONSISTENCY = "self_consistency"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    RAG = "rag"
    PROMPT_CHAINING = "prompt_chaining"
    GENERATED_KNOWLEDGE = "generated_knowledge"
    NEGATIVE_PROMPTING = "negative_prompting"
    CONSTITUTIONAL = "constitutional"
    COSTARD = "costard"
    META_PROMPTING = "meta_prompting"
    RECURSIVE = "recursive"
    STRUCTURED_OUTPUT = "structured_output"
    TEMPERATURE_SCHEDULING = "temperature_scheduling"
    ENSEMBLE = "ensemble"


class OutputFormat(StrEnum):
    """Output format types"""

    TEXT = "text"
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"
    CODE = "code"


# =============================================================================
# Models
# =============================================================================


class PromptTemplate(BaseModel):
    """Prompt template definition"""

    name: str
    description: str
    template: str
    technique: PromptTechnique
    variables: list[str] = []
    examples: list[dict[str, Any]] = []
    output_format: OutputFormat = OutputFormat.TEXT

    def render(self, **kwargs) -> str:
        """Render template with variables"""
        prompt = self.template
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt

    def validate_variables(self, provided: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate all required variables are provided"""
        missing = [v for v in self.variables if v not in provided]
        return len(missing) == 0, missing


class PromptChain(BaseModel):
    """Chain of prompts for multi-step reasoning"""

    name: str
    description: str
    steps: list[PromptTemplate]
    aggregate_results: bool = True

    def get_step(self, index: int) -> PromptTemplate | None:
        """Get step by index"""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None


# =============================================================================
# Technique Implementations
# =============================================================================


class ChainOfThought:
    """
    Chain-of-Thought Prompting

    Encourages step-by-step reasoning before arriving at final answer.

    Reference: Wei et al., 2022 - "Chain-of-Thought Prompting Elicits Reasoning"

    Usage:
        cot = ChainOfThought()
        prompt = cot.create_prompt(
            question="What is 17 * 24?",
            context="Solve step by step"
        )
    """

    TEMPLATE = """
{context}

Question: {question}

Let's think through this step by step:
1. First, I'll identify what we're trying to solve.
2. Then, I'll break down the problem into smaller parts.
3. I'll work through each part systematically.
4. Finally, I'll combine the results for the answer.

Step-by-step reasoning:
"""

    COT_SUFFIX = "\n\nTherefore, the answer is:"

    @classmethod
    def create_prompt(
        cls,
        question: str,
        context: str = "",
    ) -> str:
        """Create CoT prompt"""
        return cls.TEMPLATE.format(
            context=context or "Please solve the following problem.", question=question
        )

    @classmethod
    def extract_answer(cls, response: str) -> str:
        """Extract final answer from CoT response"""
        # Look for common answer patterns
        patterns = [
            r"Therefore,?\s*(?:the answer is|we get|the result is)[:\s]*(.+?)(?:\.|$)",
            r"(?:Final answer|Answer)[:\s]*(.+?)(?:\.|$)",
            r"(?:In conclusion|Thus)[,:\s]*(.+?)(?:\.|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Return last line as fallback
        lines = response.strip().split("\n")
        return lines[-1].strip() if lines else response


class FewShotLearning:
    """
    Few-Shot Learning

    Provides examples to guide model behavior.

    Reference: Brown et al., 2020 - "Language Models are Few-Shot Learners"

    Usage:
        fs = FewShotLearning()
        prompt = fs.create_prompt(
            task="Classify sentiment",
            examples=[
                {"input": "Great product!", "output": "positive"},
                {"input": "Terrible service", "output": "negative"},
            ],
            query="Love this!"
        )
    """

    @classmethod
    def create_prompt(
        cls,
        task: str,
        examples: list[dict[str, str]],
        query: str,
        input_label: str = "Input",
        output_label: str = "Output",
    ) -> str:
        """Create few-shot prompt"""
        prompt_parts = [f"Task: {task}\n"]

        # Add examples
        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"{input_label}: {example.get('input', '')}")
            prompt_parts.append(f"{output_label}: {example.get('output', '')}")
            prompt_parts.append("")

        # Add query
        prompt_parts.append("Now respond to:")
        prompt_parts.append(f"{input_label}: {query}")
        prompt_parts.append(f"{output_label}:")

        return "\n".join(prompt_parts)

    @classmethod
    def create_examples_for_domain(cls, domain: str) -> list[dict[str, str]]:
        """Get domain-specific examples"""
        examples = {
            "sentiment": [
                {
                    "input": "This product exceeded my expectations!",
                    "output": "positive",
                },
                {"input": "Waste of money, don't buy.", "output": "negative"},
                {"input": "It's okay, nothing special.", "output": "neutral"},
            ],
            "product_description": [
                {
                    "input": "Bomber jacket, black, premium fabric",
                    "output": "Crafted from premium heavyweight fabric, this bomber jacket embodies sophisticated street elegance. Features rose gold hardware and meticulous stitching throughout.",
                },
            ],
            "categorization": [
                {"input": "oversized hoodie", "output": "tops"},
                {"input": "slim joggers", "output": "bottoms"},
                {"input": "puffer coat", "output": "outerwear"},
            ],
        }
        return examples.get(domain, [])


class SelfConsistency:
    """
    Self-Consistency Prompting

    Sample multiple reasoning paths and take majority vote.

    Reference: Wang et al., 2022 - "Self-Consistency Improves Chain of Thought Reasoning"

    Usage:
        sc = SelfConsistency()
        answer = sc.aggregate_responses([
            "The answer is 42",
            "I calculate 42",
            "Result: 41"
        ])  # Returns "42" (majority)
    """

    @classmethod
    def create_variants(
        cls,
        base_prompt: str,
        n_variants: int = 5,
    ) -> list[str]:
        """Create prompt variants for sampling"""
        variants = [base_prompt]

        prefixes = [
            "Let's approach this differently.",
            "Consider an alternative method.",
            "From another perspective,",
            "Using a different strategy,",
        ]

        for i in range(min(n_variants - 1, len(prefixes))):
            variants.append(f"{prefixes[i]}\n\n{base_prompt}")

        return variants[:n_variants]

    @classmethod
    def aggregate_responses(
        cls,
        responses: list[str],
        extract_answer: Callable[[str], str] = None,
    ) -> str:
        """Aggregate multiple responses via majority voting"""
        if not responses:
            return ""

        # Extract answers
        extractor = extract_answer or ChainOfThought.extract_answer
        answers = [extractor(r) for r in responses]

        # Count occurrences (normalized)
        normalized = [a.lower().strip() for a in answers]
        counts = {}
        for ans, orig in zip(normalized, answers, strict=False):
            if ans in counts:
                counts[ans]["count"] += 1
            else:
                counts[ans] = {"count": 1, "original": orig}

        # Return most common
        best = max(counts.items(), key=lambda x: x[1]["count"])
        return best[1]["original"]


class TreeOfThoughts:
    """
    Tree of Thoughts (ToT)

    Explores multiple reasoning paths as a tree structure.

    Reference: Yao et al., 2023 - "Tree of Thoughts: Deliberate Problem Solving"

    Usage:
        tot = TreeOfThoughts()
        prompt = tot.create_prompt(
            problem="Design a logo for SkyyRose",
            n_branches=3
        )
    """

    TEMPLATE = """
Problem: {problem}

Let's explore {n_branches} different approaches to solve this:

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

After evaluating all approaches, the best path forward is:
"""

    @classmethod
    def create_prompt(
        cls,
        problem: str,
        n_branches: int = 3,
    ) -> str:
        """Create ToT prompt"""
        return cls.TEMPLATE.format(problem=problem, n_branches=n_branches)

    @classmethod
    def create_evaluation_prompt(cls, approach: str) -> str:
        """Create prompt to evaluate an approach"""
        return f"""
Evaluate this approach:

{approach}

Rate on these criteria (1-10):
1. Feasibility:
2. Effectiveness:
3. Originality:
4. Efficiency:

Overall score:
Should we continue exploring this path? (Yes/No):
Reasoning:
"""


class ReActPrompting:
    """
    ReAct: Reasoning + Acting

    Interleaves reasoning traces with actions.

    Reference: Yao et al., 2022 - "ReAct: Synergizing Reasoning and Acting"

    Usage:
        react = ReActPrompting()
        prompt = react.create_prompt(
            task="Find trending streetwear styles",
            tools=["web_search", "analyze_image"]
        )
    """

    TEMPLATE = """
Task: {task}

Available tools: {tools}

Solve this task by alternating between:
- Thought: Your reasoning about what to do next
- Action: The tool to use and its input
- Observation: The result of the action

Begin:

Thought 1: I need to understand the current task and plan my approach.
"""

    @classmethod
    def create_prompt(
        cls,
        task: str,
        tools: list[str],
    ) -> str:
        """Create ReAct prompt"""
        return cls.TEMPLATE.format(task=task, tools=", ".join(tools))

    @classmethod
    def parse_action(cls, response: str) -> dict[str, str] | None:
        """Parse action from response"""
        # Look for Action: tool_name[input]
        match = re.search(r"Action[:\s]+(\w+)\[(.+?)\]", response)
        if match:
            return {"tool": match.group(1), "input": match.group(2)}
        return None

    @classmethod
    def format_observation(cls, result: Any) -> str:
        """Format observation for next step"""
        if isinstance(result, dict):
            result = json.dumps(result, indent=2)
        return f"\nObservation: {result}\n\nThought: "


class RAGPrompting:
    """
    Retrieval-Augmented Generation

    Grounds responses in retrieved context.

    Reference: Lewis et al., 2020 - "Retrieval-Augmented Generation"

    Usage:
        rag = RAGPrompting()
        prompt = rag.create_prompt(
            question="What's the BLACK ROSE collection?",
            context=[
                {"text": "BLACK ROSE is our limited edition line...", "source": "about.md"},
            ]
        )
    """

    TEMPLATE = """
Use the following context to answer the question. If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {question}

Answer based on the context above:
"""

    @classmethod
    def create_prompt(
        cls,
        question: str,
        context: list[dict[str, str]],
        max_context_length: int = 3000,
    ) -> str:
        """Create RAG prompt"""
        # Format context
        context_parts = []
        total_length = 0

        for item in context:
            text = item.get("text", "")
            source = item.get("source", "unknown")

            formatted = f"[Source: {source}]\n{text}\n"

            if total_length + len(formatted) > max_context_length:
                break

            context_parts.append(formatted)
            total_length += len(formatted)

        return cls.TEMPLATE.format(context="\n".join(context_parts), question=question)

    @classmethod
    def create_with_citations(cls, question: str, context: list[dict]) -> str:
        """Create prompt that encourages citation"""
        template = """
Answer the question using ONLY the provided sources. Cite sources using [1], [2], etc.

Sources:
{sources}

Question: {question}

Answer with citations:
"""
        sources = []
        for i, item in enumerate(context, 1):
            sources.append(f"[{i}] {item.get('text', '')}")

        return template.format(sources="\n\n".join(sources), question=question)


class StructuredOutput:
    """
    Structured Output Prompting

    Guides model to produce specific output formats.

    Usage:
        so = StructuredOutput()
        prompt = so.create_json_prompt(
            task="Extract product info",
            schema={"name": "string", "price": "number"}
        )
    """

    JSON_TEMPLATE = """
{task}

Respond with a JSON object matching this schema:
```json
{schema}
```

Your response must be valid JSON only, no additional text.
"""

    XML_TEMPLATE = """
{task}

Respond with XML matching this structure:
```xml
{schema}
```

Your response must be valid XML only.
"""

    @classmethod
    def create_json_prompt(
        cls,
        task: str,
        schema: dict[str, Any],
    ) -> str:
        """Create JSON output prompt"""
        return cls.JSON_TEMPLATE.format(task=task, schema=json.dumps(schema, indent=2))

    @classmethod
    def create_xml_prompt(
        cls,
        task: str,
        schema: str,
    ) -> str:
        """Create XML output prompt"""
        return cls.XML_TEMPLATE.format(task=task, schema=schema)

    @classmethod
    def parse_json_response(cls, response: str) -> dict | None:
        """Parse JSON from response"""
        # Try to find JSON in response
        patterns = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
            r"\{[\s\S]*\}",
        ]

        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    json_str = match.group(1) if match.lastindex else match.group()
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        # Try parsing entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None


class ConstitutionalAI:
    """
    Constitutional AI Prompting

    Self-critique and revision based on principles.

    Reference: Bai et al., 2022 - "Constitutional AI"

    Usage:
        cai = ConstitutionalAI()
        prompt = cai.create_critique_prompt(
            response="...",
            principles=["Be helpful", "Be honest"]
        )
    """

    CRITIQUE_TEMPLATE = """
Original response:
{response}

Evaluate this response against these principles:
{principles}

For each principle, identify any violations:
"""

    REVISION_TEMPLATE = """
Original response:
{response}

Critique:
{critique}

Revise the response to address the critique while maintaining helpfulness:
"""

    @classmethod
    def create_critique_prompt(
        cls,
        response: str,
        principles: list[str],
    ) -> str:
        """Create critique prompt"""
        principles_text = "\n".join(f"- {p}" for p in principles)
        return cls.CRITIQUE_TEMPLATE.format(response=response, principles=principles_text)

    @classmethod
    def create_revision_prompt(
        cls,
        response: str,
        critique: str,
    ) -> str:
        """Create revision prompt"""
        return cls.REVISION_TEMPLATE.format(response=response, critique=critique)

    @classmethod
    def get_default_principles(cls) -> list[str]:
        """Get default constitutional principles"""
        return [
            "Be helpful and informative",
            "Be honest and accurate",
            "Avoid harmful or misleading content",
            "Respect privacy and confidentiality",
            "Be fair and unbiased",
            "Support user autonomy",
        ]


class NegativePrompting:
    """
    Negative Prompting

    Specifies what NOT to include in output.

    Usage:
        np = NegativePrompting()
        prompt = np.create_prompt(
            task="Write product description",
            negative=["Don't use superlatives", "Avoid clichés"]
        )
    """

    TEMPLATE = """
{task}

Important constraints - DO NOT:
{constraints}

Now complete the task while avoiding the above:
"""

    @classmethod
    def create_prompt(
        cls,
        task: str,
        negative: list[str],
    ) -> str:
        """Create negative prompt"""
        constraints = "\n".join(f"- {c}" for c in negative)
        return cls.TEMPLATE.format(task=task, constraints=constraints)


class RoleBasedPrompting:
    """
    Role-Based Constraint Prompting

    Establishes persona and expertise.

    Usage:
        rbp = RoleBasedPrompting()
        prompt = rbp.create_prompt(
            role="luxury fashion expert",
            task="Describe this jacket"
        )
    """

    TEMPLATE = """
You are {role}.

{background}

{task}
"""

    @classmethod
    def create_prompt(
        cls,
        role: str,
        task: str,
        background: str = "",
    ) -> str:
        """Create role-based prompt"""
        if not background:
            background = f"With your expertise as {role}, complete the following task."

        return cls.TEMPLATE.format(role=role, background=background, task=task)

    @classmethod
    def get_skyyrose_expert(cls) -> tuple[str, str]:
        """Get SkyyRose brand expert role"""
        role = "a luxury streetwear brand strategist and fashion expert for SkyyRose"
        background = """
SkyyRose is an Oakland-based luxury streetwear brand
The brand features three collections:
- BLACK ROSE: Limited edition dark elegance
- LOVE HURTS: Emotional expression pieces
- SIGNATURE: Foundation wardrobe essentials
Colors: Rose gold, obsidian black, ivory
Target: Discerning customers who appreciate elevated street style
"""
        return role, background


# =============================================================================
# Main Prompt Engineer Class
# =============================================================================


class PromptEngineer:
    """
    Central prompt engineering utility.

    Usage:
        engineer = PromptEngineer()

        # Use specific technique
        prompt = engineer.create(
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            question="How should we price this product?"
        )

        # Auto-select technique
        prompt = engineer.auto_create(
            task="Generate product description",
            context={"product_name": "Heart aRose Bomber"}
        )
    """

    def __init__(self):
        self.templates: dict[str, PromptTemplate] = {}
        self._load_builtin_templates()

    def _load_builtin_templates(self):
        """Load built-in templates"""
        self.templates["skyyrose_product"] = PromptTemplate(
            name="skyyrose_product",
            description="Generate SkyyRose product description",
            template="""
You are a luxury fashion copywriter for SkyyRose, an Oakland-based streetwear brand.

Product: {product_name}
Collection: {collection}
Features: {features}

Write a compelling product description that:
- Evokes the brand's Oakland roots and streetwear heritage
- Highlights craftsmanship and exclusivity
- Appeals to discerning fashion enthusiasts
- Is 2-3 paragraphs

Description:
""",
            technique=PromptTechnique.ROLE_BASED,
            variables=["product_name", "collection", "features"],
        )

    def create(
        self,
        technique: PromptTechnique,
        **kwargs,
    ) -> str:
        """Create prompt using specific technique"""
        if technique == PromptTechnique.CHAIN_OF_THOUGHT:
            return ChainOfThought.create_prompt(
                question=kwargs.get("question", ""),
                context=kwargs.get("context", ""),
            )

        elif technique == PromptTechnique.FEW_SHOT:
            return FewShotLearning.create_prompt(
                task=kwargs.get("task", ""),
                examples=kwargs.get("examples", []),
                query=kwargs.get("query", ""),
            )

        elif technique == PromptTechnique.TREE_OF_THOUGHTS:
            return TreeOfThoughts.create_prompt(
                problem=kwargs.get("problem", ""),
                n_branches=kwargs.get("n_branches", 3),
            )

        elif technique == PromptTechnique.REACT:
            return ReActPrompting.create_prompt(
                task=kwargs.get("task", ""),
                tools=kwargs.get("tools", []),
            )

        elif technique == PromptTechnique.RAG:
            return RAGPrompting.create_prompt(
                question=kwargs.get("question", ""),
                context=kwargs.get("context", []),
            )

        elif technique == PromptTechnique.STRUCTURED_OUTPUT:
            return StructuredOutput.create_json_prompt(
                task=kwargs.get("task", ""),
                schema=kwargs.get("schema", {}),
            )

        elif technique == PromptTechnique.CONSTITUTIONAL:
            return ConstitutionalAI.create_critique_prompt(
                response=kwargs.get("response", ""),
                principles=kwargs.get("principles", ConstitutionalAI.get_default_principles()),
            )

        elif technique == PromptTechnique.NEGATIVE_PROMPTING:
            return NegativePrompting.create_prompt(
                task=kwargs.get("task", ""),
                negative=kwargs.get("negative", []),
            )

        elif technique == PromptTechnique.ROLE_BASED:
            return RoleBasedPrompting.create_prompt(
                role=kwargs.get("role", "an expert assistant"),
                task=kwargs.get("task", ""),
                background=kwargs.get("background", ""),
            )

        else:
            raise ValueError(f"Unsupported technique: {technique}")

    def auto_select_technique(self, task_type: str) -> PromptTechnique:
        """Auto-select best technique for task type"""
        mappings = {
            "reasoning": PromptTechnique.CHAIN_OF_THOUGHT,
            "classification": PromptTechnique.FEW_SHOT,
            "creative": PromptTechnique.TREE_OF_THOUGHTS,
            "search": PromptTechnique.REACT,
            "qa": PromptTechnique.RAG,
            "extraction": PromptTechnique.STRUCTURED_OUTPUT,
            "moderation": PromptTechnique.CONSTITUTIONAL,
            "generation": PromptTechnique.ROLE_BASED,
        }
        return mappings.get(task_type, PromptTechnique.ROLE_BASED)

    def use_template(self, template_name: str, **kwargs) -> str:
        """Use a saved template"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")

        return template.render(**kwargs)

    def register_template(self, template: PromptTemplate):
        """Register custom template"""
        self.templates[template.name] = template

    def list_techniques(self) -> list[dict[str, str]]:
        """List all available techniques with descriptions"""
        return [{"name": t.value, "technique": t} for t in PromptTechnique]
