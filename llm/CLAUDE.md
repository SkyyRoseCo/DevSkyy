# llm/

Scoped context for the multi-provider LLM layer. Core text providers: Anthropic, OpenAI, Google, Mistral, Cohere, Groq — plus DeepSeek and a LiteLLM gateway, and image-gen providers (Replicate, Stability, Vertex Imagen) all under `llm/providers/`. Don't cite a fixed provider count; it grows. Loads on top of root.

## Hard rules

- **`llm/model_ids.py` is the ONLY source of model strings.** Never hardcode `"claude-sonnet-4-6"`, `"gpt-4o"`, etc. anywhere — import the constant. A model roll-forward updates `model_ids.py` once and propagates everywhere.
- **Adding a provider = three files, all required:** (a) implement `BaseLLMClient.complete()` in `llm/providers/<name>.py` (extends `llm/base.py`); (b) add a `ProviderConfig` in `llm/router.py`; (c) register in `orchestration/llm_registry.py` `_providers` dict. Skip (c) and the provider is callable but invisible to `LLMRegistry.get_available_providers()`.
- **New machine decisions go through `llm/decisions/`, not free-text JSON.** Routing, gating and grading questions use typed `Choice` / `Score` / `Noul` with probabilities read from first-token logprobs (`LogprobBackend`), never a confidence number the model writes about itself. Every failure routes `SPLIT` (escalate). `SHARP` lets code take the cheap path; it never authorizes a paid, production or irreversible action. Default thresholds are placeholders: measure real ones with `scripts/decision_calibrate.py` (paid, refuses without `--yes`) before wiring a consumer.
