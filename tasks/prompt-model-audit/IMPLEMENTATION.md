# Prompt/model audit implementation — first four priorities

Implemented against `/Users/theceo/.codex/worktrees/58cc/DevSkyy`, starting from
clean detached HEAD `8a13099798c6b50d3f65bca93baba060b0a82a35`. The original
audit chat was idle when work began. Delivery branch:
`codex/prompt-model-contracts`. Source, regression tests, verification evidence
and this documentation are included in the local commit series. Use
`git log --oneline 8a13099798c6b50d3f65bca93baba060b0a82a35..HEAD` to inspect
the resulting commits. No publishing, deployment, model migration, credential
setup, purchase or authorized live model evaluation is part of this work.

## Product grounding

`PromptChain.enhance` now separates product constraints, bound references,
creative direction, required views, missing facts and brief status. Existing
SKUs resolve exclusively through `skyyrose.core.product.get_product`.
Registry-owned garment facts, dossier text, logos, correction provenance and
authority are preserved without adding category fabric or construction
assumptions. Unknown SKUs raise; absent facts/views produce an incomplete brief.
Optional creative context cannot become product authority.

The registry remains `logo-registry.json` →
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`. No product facts or
projections were edited. Corey remains the founder/maker authority; his exact
specifications and corrections are preserved. Our tests check execution against
the supplied record, not independent proof of his facts.

Category defaults require explicit `new_design=True` with
`intent="design-ideation"`, and their output is labeled as proposed design, not
existing product facts. Real-SKU briefs bypass semantic caching so a similar
SKU, negated instruction or earlier registry state cannot supply stale
constraints. Existing result fields remain; `brief_status` and `gaps` are
additional fields.

The required creative reference is
[imagery-prompting.md](/Users/theceo/.codex/creative-standards/imagery-prompting.md),
read before prompt changes and cited by generated briefs and the QA prompt. It
governs natural scene integration, protected garment detail and review. Seed and
separate negative-prompt controls are marked not applicable without a selected
provider. This implementation does not approve a new creative direction or
resume the generation hold.

## Real image inputs

`OpenAIService.analyzeImage` sends typed `text` and `image_url` content blocks
to Chat Completions. Existing string messages and the public call signature
still work. The current `gpt-4o` model and 1,000-token vision budget are
unchanged. Transport tests assert the serialized multimodal body, not just
prompt keywords. This follows
[OpenAI image input documentation](https://developers.openai.com/api/docs/guides/images-vision).

## Model settings and request execution

A dependency-light shared contract lives in `skyyrose/core/openai_settings.py`
and is consumed by the raw HTTP OpenAI provider, orchestration SDK provider and
web-builder OpenAI adapter. It validates registered Chat Completions
capabilities, forwards supported structured output and generation settings, and
rejects unknown settings/model capabilities before I/O. Rejection of an
unregistered model is an adapter coverage limit, not a claim that the model does
not exist.

GPT-4o and mini retain their defaults and reject reasoning/verbosity settings.
GPT-6 reasoning, sampling and tool compatibility follow current official
guidance: Astra Chat Completions cannot use tools or reasoning `none`; Sol/Luna
Chat Completions tools require reasoning `none`. Reasoning budgets serialize as
`max_completion_tokens`. No model defaults were upgraded. Sources:
[current model guidance](https://developers.openai.com/api/docs/guides/latest-model),
[reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning),
and
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

Budgets are explicit: 1,600 tokens for ghost QA, 2,400 for scene QA, and the
existing 1,000 for TypeScript vision. The web-builder adapter now accepts an
explicit caller budget; its previous 16,384 default remains for unconstrained
existing callers rather than guessing task requirements from prose.

The web-builder's blocking OpenAI request and client lifecycle run in a worker
thread; its SDK retries are disabled because its runtime owns provider fallback.
The orchestration OpenAI client keeps SDK retries and removes the outer
three-attempt Tenacity layer. Tests verify one SDK retry means exactly two HTTP
attempts. Structured Gemini QA and OpenAI QA each make one transport attempt.
Other providers' retry policies are outside this change.

The installed Mistral 2.4.5 package lacks the older top-level `Mistral` export.
Its import is now deferred to that provider's initializer, so unrelated OpenAI
imports work without test stubs. Repairing the Mistral adapter itself remains
out of scope.

## QA evidence and acceptance

Both judges receive labeled image A (registry-bound reference for the explicit
front/back view) and image B (candidate). The reference must match the SKU/view
binding; absent assets, missing view or a substituted reference block before
dispatch. Reference and candidate SHA-256 values and registry provenance
accompany the decision.

Identity has six independent findings: silhouette, construction, artwork,
lettering, color and placement. Each must be `match`, `mismatch` or
`not_visible`, with nonblank visible evidence. Missing/hidden detail cannot be
counted as a match. Physical dimensions or fiber composition must not be
inferred from pixels.

Scene integration is separate. Existing lighting/edge/shadow weights are
retained at 35%/30%/35%, with explicit scale, perspective and occlusion
findings. A pasted-on lighting failure does not mean the garment identity is
wrong. A zero integration score or nonmatching scale/perspective/occlusion
blocks acceptance.

For ghost QA, the existing 30% identity / 40% fidelity / 30% branding weighting
remains. Identity and branding scores are calculated from validated findings.
Both judges must independently pass all identity visibility/match conditions and
reach at least 80. Providers cannot supply an overriding total or approval flag.
Malformed, out-of-range, refused and truncated responses fail closed; invalid
responses and provider errors are distinct states.

The text-only ADK request was removed from the visual gate. Classifier
confidence can reject early but cannot approve. Coordinator and graph completion
paths retain failed candidates but cannot report them as approved production or
send them to downstream compositing merely because a file exists. Public QA
calls without new SKU/view evidence remain callable and return a blocked result.

Gemini serialization uses labeled inline images and `responseJsonSchema`; local
Pydantic validation remains mandatory. Source:
[Gemini generation configuration](https://ai.google.dev/api/generate-content#v1beta.GenerationConfig).

## Verification evidence

Run `bash tasks/prompt-model-audit/verify.sh` from this checkout.
[verification.txt](verification.txt) records the successful final run.

- 274 focused Python tests passed: prompt/enhancer/resolver integration,
  settings serialization, retry budgets, QA schemas and dual-judge acceptance,
  graph/coordinator failure propagation, and Gemini transport behavior.
- 34 web-builder adapter/runtime tests passed, including an event-loop progress
  check while a mocked synchronous request waits in its worker thread.
- 27 TypeScript service/SDK compatibility tests passed.
- Root TypeScript type-check passed.
- Changed TypeScript ESLint and Prettier checks passed.
- Changed Python Ruff, Black and isort checks passed.
- `python scripts/sync_product_registry.py --check` passed: CSV and all product
  dossiers match the registry.
- `git diff --check` passed.

The guarded Python run blocks real `requests`/`httpx` HTTP while allowing
explicit `httpx.MockTransport`. Authentication is not applicable to the
synthetic transport/fixture results. No model quality, cost or latency
improvement is claimed from these tests.

Initial failures were resolved: prior tests expected invented material defaults
or classifier-only approval; they now check the intended safe behavior. Gemini's
old tests mocked key selection but left the frozen key list empty; fixtures now
provide an offline key list. The web-builder combined suite requires its owning
package's `importlib` collection mode. Baseline and candidate source snapshots
independently passed 31 and 34 tests respectively; their logs are included.

## Review and boundaries

[implementation.patch](implementation.patch) includes changed source, tests and
the offline verification helper, including new files. The patch excludes
generated evidence/report files. The patch is the pre-commit implementation
snapshot; Git history is authoritative for the committed source and subsequent
documentation. See [PRODUCT-TRUTH-SCOPE.md](PRODUCT-TRUTH-SCOPE.md) for the
independent scope review.

Live model behavior, account access and actual visual judgment quality remain
unmeasured. These changes establish request and acceptance contracts, not proof
that either judge catches every visual defect. The complete repository test
suite was not run. Other provider rewrites, broad SEO/agent rewrites, Round
Table redesign, model migration and the paid comparison remain follow-up scope.
Node tests reused the local dependency tree through an ignored `node_modules`
symlink; no dependency manifests or lockfiles were changed.

Commit verification note: the configured `.husky/_` hook launcher is absent in
this checkout, so Git did not execute the pre-commit hook. The bounded
verification script and changed-Python style checks were run explicitly and
passed before documentation handoff; whole-project mypy and the hook-only
fast-unit suite were not run. No hook configuration was changed.
