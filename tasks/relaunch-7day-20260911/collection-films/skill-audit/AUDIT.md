# SkyyRose — cinematic skill audit and production shortlist

Audit date: 2026-09-12. Scope: six user-selected skills, their relevant Fashion Theme Team overlays, and a narrow shortlist of installed alternatives. This is an audit and proposed workflow improvement, not an approved replacement treatment or rendered film.

## Decision

We already have capable generation, product-fidelity and editing tools. The highest-value change is to join them through a wordless directing contract and enforce it before rendering. More detail in a prompt is useful only when it preserves the right subject and describes a meaningful action.

The previous completed package remains rejected. Its technical evidence is retained as historical evidence; it does not prove creative success. The proposed last-train-home story remains unapproved.

## What the live prompt comparison proved

Two text-only `higgsfield product-photoshoot create --enhance-only` requests completed successfully using CLI 1.1.23. Both returned GPT Image 2 / 2K prompt records. Neither submitted an image/video job or uploaded reference images. The observed Higgsfield balance remained 794.75 credits.

| Input | Observed backend output | Audit conclusion |
|---|---|---|
| Vague cinematic Black Rose train brief | Invented an oversized black rose as the product, a floor-length wool overcoat, a cobalt-blue mascot, a European station and French carriage lettering. | The enhancer can amplify ambiguity into detailed brand errors. This was an isolated diagnostic, not proof that these exact instructions caused the historical films. |
| Specific action plus brand and br-006 constraints | Retained the encounter, the source-performer requirement, illustrated Skyy and matching bomber. Also appended “no cartoonish rendering,” “no doll eyes,” and unverified garment construction/lettering assertions. | Better instruction coverage, but still unsuitable for rendering without correction. Prompt compliance is not image fidelity or story effectiveness. |

Evidence: [inputs](enhancer-inputs.json), [generic response](enhancer-generic.json), [directed response](enhancer-directed.json), [account scope](provider-scope.json), [capability checks](plugin-capabilities.json). The comparison deliberately used no images to isolate how textual intent was expanded. An actual production call must bind the correct images.

Both diagnostics also returned the mode's 4:5 default because no aspect override was supplied. The existing films use a 9:16 canvas. A production adapter must carry the approved aspect ratio explicitly instead of inheriting a still-photo default. This is an integration omission in the diagnostic, not a claim that the backend ignored a requested ratio.

The local photoshoot skill forbids manually replacing the backend's final prompt. Therefore correction should happen through revised intent/context and another inspected enhancement, or an explicitly selected alternate workflow. Do not silently hand-edit its output and claim the same workflow was followed. Inspect whether an approved enhanced prompt can be submitted without being regenerated; that exact handoff was not tested here.

## Audit of the selected skills

| Selected skill | Keep | Gap or conflict | Disposition |
|---|---|---|---|
| [higgsfield-product-photoshoot](/Users/theceo/.agents/skills/higgsfield-product-photoshoot/SKILL.md) | Backend enhancement, exact reference inputs, GPT Image 2 and 2K stills. | No campaign-specific acceptance step between enhancement and rendering; no documented enhance-only example despite live CLI support. Local instructions conflict with installed plugin photoshoot instructions, which prescribe Nano Banana Pro and manual prompt assembly. | Use the explicitly selected local route for approved stills. Add enhancement review and reference-role checks. |
| [video-script](/Users/theceo/plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/video-script/SKILL.md) | Brief, opening hook, timed outline, specific shot list. | Its examples, dialogue rules and word-count timing target narrated creator content. Missing wordless causality, acting beats, reveal logic and editorial continuity. | Add a wordless narrative branch. Existing confirmed brief facts do not need repeated intake questions. New story examples remain proposals. |
| [viral-content-formula](/Users/theceo/plugins/fashion-theme-team/vendor/branded-skills/content-copywriting/viral-content-formula/SKILL.md) | Curiosity, identity, emotional relevance and a payoff that earns attention. | Deterministic virality language and unsupported platform tactics; checklist can pass a film that has no intelligible story. | Use for hypotheses and hook comparison. No reach guarantee, forced controversy or in-film sharing CTA. |
| [animate](/Users/theceo/.agents/skills/animate/SKILL.md) | Purposeful motion and restrained presentation; player controls/reduced-motion behavior later. | UI animation skill, not actor or camera direction. It recommends height transitions at line 73 but forbids height animation at 157. | Keep outside the film-generation chain. Repair the documentation conflict separately. |
| [fashion-premium-feature-system](/Users/theceo/plugins/fashion-theme-team/skills/fashion-premium-feature-system/SKILL.md) | SOT, exact candidate evidence, fallback, independent review and founder acceptance separation. | Governs 44 storefront features, not screenwriting or cinematic performance. | Use when approved films are embedded on the website. No storefront work initiated by this audit. |
| [ln-1000-pipeline-orchestrator](/Users/theceo/.agents/skills/ln-1000-pipeline-orchestrator/SKILL.md) | Durable checkpoints, fresh state and bounded rework ideas. | Its Story is a Kanban issue. Setup assumes permission changes and software worktrees; cleanup stages/pushes/removes worktrees. Non-DONE cleanup attempts DONE and missing state defaults to DONE, conflicting with PAUSED as a valid terminal state. | Do not run it for this film. Use a separate media ledger. Runtime guards were not tested; completion issue is source-level. |

## Existing Fashion overlays: what is already covered

The [branded skill router](/Users/theceo/plugins/fashion-theme-team/skills/fashion-branded-skills/SKILL.md) loads maintained overlays for video-script and viral-content-formula. They already add canon/SOT, source and candidate hashes, independent review, rights and current-claim controls. Both source hashes matched their overlay bindings in a fresh local check. We should use those controls, not duplicate them.

A confirmed audit false positive exists in the video-script overlay: it claims a missing explicit input contract because the generator's heading matcher omits “Brief.” The source actually enumerates seven brief inputs. Correct the finding to missing **film-specific** inputs; change the generator to distinguish unmatched headings from absent content. Evidence: [source binding check](source-contract-check.json), generator lines 162–172 and 274–281, selected video overlay lines 124–128.

The overlays still lack campaign-specific correct/incorrect example pairs with observed-versus-expected outcomes. This audit's linked [examples](EXAMPLES.md) provide that evidence for this task, but they are not installed into global skill entrypoints. Library-wide verification is not claimed.

## Best available stack for this campaign

Ranked by fit to the actual failure, not an unperformed image-quality benchmark.

| Capability we have | Why it belongs | Verification and limit |
|---|---|---|
| **Fashion Theme Team: product-fidelity-image-edits** | Highest-priority addition to the active workflow. Separates casting, garment construction and optical integration; includes temporal identity, first-frame locks, per-frame review and rejected-reference quarantine. | Installed source and linked video-fidelity contract inspected. References do not guarantee unchanged product pixels through time. |
| **Fashion Theme Team: fashion-brand-experience** | Keeps Oakland, the actual products and distinct collection roles central; provides anti-generic exclusions and logo-off recognition. | Installed source inspected. Creative direction, not a renderer or founder approval. |
| **Fashion Theme Team: brand-photography-brief + product-photography-brief** | Turns “cinematic” into framing, material response, lighting and a specific buyer-visible product detail. | Installed sources inspected. Adapt still-photo guidance; do not import their generic catalog shot count or props into the film. |
| **video-script + the proposed wordless directing additions** | Provides timed structure; the additions require a visible objective, action, response and consequence, plus an earned ending. | Source audited. A proposed improvement, not yet a tested complete film-directing skill. |
| **Higgsfield: Product Photoshoot + reusable Elements** | Creates source-led storyboard frames and makes the same mascot/garment references reusable. A completed “Skyy Founder Master Sep11” Element already exists; its description identifies the supplied image hash and distinguishes identity from wardrobe. | Authenticated account and Element metadata read live. Remote bytes and per-shot injection not reverified. For Kling 3.0, the tool contract requires an explicit start image for Element use. |
| **Higgsfield: Cinema Studio** | Worth auditioning for deliberate shot design: the live CLI contract exposes reference media, start/end images, custom multishot structure, genre and timing controls. The product UI also documents camera/optics controls. | Cinematic Studio 3.0 CLI contract verified; no new render test. MCP search missed it, so search absence was not treated as unavailability. Do not assume every UI control is exposed by the CLI. |
| **Runway with Kling O3 Pro** | Strong documented fit for the paired human/Skyy shots: reference images and start/end constraints can carry approved casting and blocking into motion. Keep one or two principal subjects per shot where possible. | Runway authentication and model availability verified live. Prior films were creatively rejected; no new comparison proves it produces a better film than Cinema Studio. |
| **Existing local FFmpeg assembly workflow** | Strongest evidenced option here for protecting the supplied source footage. The correction package's assembler records exact source-frame selection, silent output and pixel comparisons in preservation masters. | Historical implementation/verification, not a plugin. New edits require fresh frame comparisons. It guarantees neither a compelling cut nor creative acceptance. |
| **Higgsfield video-editing / Higgsedit** | An installed option for explicit cuts, trims, source-time placement and editable composition. It can support new scenes edited around protected footage. | Installed skill inspected. The correction package's cited pixel proof belongs to the local FFmpeg assembler, not Higgsedit. Exact runtime and new export preservation must be tested before relying on this route. It is not a generative motion model. |
| **Fashion Theme Team: fashion-visual-commerce-qa, selected media checks** | Independent review of anatomy, garment fidelity, optical integration and repetitive collection storytelling. | Installed source inspected. Add film comprehension and continuity criteria; do not claim a complete storefront/checkout audit. |
| **Descript — optional editorial review** | Useful for an editable scene timeline and comparing cut order/pacing with a human. | Connected read request succeeded and returned no matching owned projects. No edit/export test or project created. Automatic layouts/transitions need explicit control. Exact source-pixel preservation is not established. |

Additional relevant contract: [Prompt Engineering, Chaining, and Caching](/Users/theceo/plugins/fashion-theme-team/skills/fashion-theme-team/brain/prompts/prompt-orchestration.md) keeps source roles, founder decisions and rejected examples in versioned packets. It is a linked Fashion Brain contract, not a standalone skill.

The most relevant local paths are in [the examples and source notes](EXAMPLES.md). Provider evidence is in [plugin-capabilities.json](plugin-capabilities.json).

## What needs to be filled before another full film batch

1. **Wordless directing:** objective, obstacle, decision, consequence, setup/payoff. A kind gesture or held door is one beat; it cannot carry the whole campaign by itself.
2. **Shot continuity handoff:** cast ID, wardrobe ID, entry/exit positions, eyelines, screen direction, light direction, intended next cut. Integrate the already-installed video-fidelity contract.
3. **Prompt review before generation:** separate user intent, backend-expanded prompt and actual submitted request. Check the final prompt for contradictory style instructions, invented garment facts, extra cast, words, irrelevant symbols and unbound references.
4. **Protected-footage editing:** use the exact source performer; cut approved excerpts; remove audio; preserve source pixels in the preservation master. No regenerated replacement, crop, grade or retiming of original video.
5. **Creative testing:** review a short silent sequence without its written explanation. The reviewer must describe what the character wants, what changes, which garment is featured, and how the reveal answers the setup. Separate technical QA, creative review and founder acceptance.
6. **Evidence-backed examples:** attach real positive/negative cases with source, date, authentication, expected/observed outcomes and limits. Fix the confirmed documentation contradictions through canonical source maintenance, not disposable caches.

Recommended sequence: source/cast packet → wordless outline → story and source review → enhanced still prompt review → approved storyboard frame → one short motion proof → silent sequence review → full production and edit → independent QA → founder review.

## Scope and evidence limits

Two independent agents reviewed separate source areas. Neither rendered anything. Live provider work consisted of account/catalog/Element reads and two text-only prompt enhancements. No campaigns were activated, no media or skill source files were modified, and no global permissions changed.

Original source video and supplied Skyy image hashes still match their recorded identities. Source hashing establishes byte identity, not creative quality. [Source evidence](source-evidence.json).

Current primary references checked on 2026-09-12:
- [Runway image-to-video prompting](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide): use the image for visual appearance and the prompt for motion; input artifacts can intensify.
- [Higgsfield Kling control guide](https://higgsfield.ai/blog/Kling-3.0-is-on-Higgsfield-User-Guide-AI-Video-Generation): start/end frames and restrained action design. Product-page claims do not override the actual tool schema.
- [Higgsfield Cinema Studio design](https://higgsfield.ai/blog/how-we-built-cinema-studio): camera/optics interface and project continuity; no claim that current UI versions equal this CLI's model ID.
- [Descript timeline](https://help.descript.com/hc/en-us/articles/10249307946893-Media-layers-scenes-and-the-script-in-the-Timeline), [transitions](https://help.descript.com/hc/en-us/articles/10255989387661-Transitions-overview): editable scenes/clips and explicit removal of automatic transitions.

Coverage verdict: **PARTIAL** for campaign skill adoption. Audit findings and source bindings are supported; improved creative examples remain unrendered and unapproved. The highest-quality output remains to be demonstrated on the same approved scene and references.
