# SkyyRose — stronger-output examples

These examples support [the skill audit](AUDIT.md). They are not replacement-campaign approval. Creative scenes are illustrative unless a specific observed result is stated. Verification date: 2026-09-12.

## 1. Prompt enhancement: a real failure and the correct response

**Context:** The user requested an audit and stronger examples. Higgsfield account access was verified, and two `--enhance-only` requests were authorized as non-rendering diagnostics. No image references were sent.

**Incorrect input, actually tested:**
> Make a cinematic luxury Black Rose train campaign with a male model, the Skyy mascot, dramatic lighting and a big reveal.

**Observed result:** The backend interpreted Black Rose as an oversized flower, invented a wool overcoat and a cobalt-blue mascot, and added French carriage wording. It produced detailed photography instructions, but failed the known product/identity/wordless constraints. Evidence: [exact response](enhancer-generic.json), classification **VERIFIED_LIVE**.

**Stronger user-intent input, actually tested:**
> Storyboard still for a wordless Black Rose encounter: the actual man from the supplied video has paused at an interior train door. On the other side, the exact supplied illustrated Skyy has reached for its handle to let him through. Capture the instant he notices her matching bomber. Keep both jacket fronts legible, her hand clear of the chest, and their attention on one another. A single practical window light defines the black satin and sherpa. No posing toward camera.

Separate brand/product context supplied the exact br-006 source authority, illustrated identity preservation, no invented signage and no floating roses/thrones. Evidence: [inputs](enhancer-inputs.json), [response](enhancer-directed.json).

**Observed improvement:** The backend retained the encounter, actor-source requirement, illustrated Skyy and bomber. **Remaining defects:** global “no cartoonish rendering” and “no doll eyes” contradict Skyy's illustrated appearance; assertions about garment features were not established by reference images. The more specific prompt still fails a production acceptance review.

Both requests returned 4:5 because the diagnostic omitted an aspect override. Production must explicitly carry the approved 9:16 film canvas; do not silently crop a default still to fit it.

**Correct action:** Reject both expanded prompts for production. Preserve the successful instruction details, resolve contradictions through the supported enhancement workflow, bind reference images, and inspect the actual final request before any render. An input filename mentioned in text is not an uploaded reference.

**Expected result, not yet observed:** A coherent expanded prompt that preserves all source roles and can be evaluated with an approved storyboard.

**Authentication:** VERIFIED_LIVE for CLI account access and two enhancement requests. MCP selected private Plus workspace `b9928f7d-3821-49a1-a40e-04c97f1bf6b8`; CLI account redacted as `i***@shopskyyrose.com`. Matching credit balances were observed, but the CLI's workspace ID was not separately inspected. Balance unchanged: 794.75.

**Limits/refresh:** Text compliance only; no image fidelity, acting or story-success test. Refresh after CLI/backend/skill changes. Do not reuse a regenerated prompt without inspecting it.

## 2. Same performer and garment: preserve authority

**Context:** Black Rose br-006; the user explicitly requires the actual man in the supplied video and allows product-readable excerpts without audio.

**Incorrect example, recorded failure context:** Choose a handsome male from an earlier generated campaign frame and call him “the same model.” A similar jacket does not make him the supplied performer. The user's casting correction and [actor-reference receipt](../identity-correction/black-rose-actor-references.json) establish the distinction.

**Correct output:**
- Cast authority: the supplied video and unchanged extracted source frames 731 and 1427.
- Garment authority: the actual br-006 bomber in that video, with canonical product references used for garment checks.
- Skyy identity: supplied image.png; archived collection outfits are wardrobe references, not alternate face designs.
- Original clips: choose source in/out frames, remove audio, retain their visual appearance. Edit new footage around those clips.
- Generated surrounding shots: reject changed face, head shape, body proportions, garment silhouette, closures or marks. A failed render stays in the rejection archive.

**Observed positive evidence:** Fresh source hashing matched the original video SHA256 `8b0953c5824f07f0a8f483aeac34305ec032d453c93da17a37cfa4ecd6918127` and Skyy image SHA256 `a8a32b8097f6885300f537e50c942c445c09012269807b072b6854c7019b9973`. [Source evidence](source-evidence.json), **REPRODUCED_LOCAL**.

The prior export report records original source intervals [695,767), [983,1031), [1391,1463), with 192 source frames in Black Rose and 144 in the main preservation master. This is **HISTORICAL_OBSERVED**, not a new all-frame check. [Historical final report](../identity-correction/output/final-report.json).

**Expected versus observed:** Source identity and historical preservation are evidenced. Future generated identity and a compelling film are not established.

**Authentication:** NOT_APPLICABLE to local hashing and receipt inspection. No new provider upload or media alteration.

**Limits/refresh:** Hashes prove bytes, not optical or narrative quality. Recheck all newly generated clips and newly assembled exports. Viewing compression and a source-preserving master are different deliverables.

## 3. Wordless story: replace adjectives with observable decisions

**Weak, illustrative:**
> They share an emotional moment. Slow push-in. Cinematic atmosphere.

**Stronger, illustrative 8-second beat:**
- 0–2 seconds: the connecting interior door is closing. The performer is already moving away when he sees Skyy through the glass.
- 2–5 seconds: he reverses two steps and holds the door; the reversal follows his eyeline.
- 5–8 seconds: she crosses, and only then does he continue. The next angle preserves their travel direction.

The action changes the situation: someone who would be left behind can pass. Body movement motivates garment visibility and the cut. This is **one acting example**, not a strong enough premise for the entire campaign. A full outline must establish why that passage matters.

**Better script record:** “What did they notice? What did they decide? What changed? What must we now see?” Each answer must point to something visible. “Mystery,” “power” and “emotion” alone are insufficient answers.

**Evidence:** video-script lines 150–154 require specific cues/timing but focus on spoken content. Founder rejection records the lack of convincing story; the recorded assistant critique identifies posed shots and camera motion without sufficient progression. [Rejection](../identity-correction/founder-rejection.json).

**Classification:** ILLUSTRATIVE_UNEXECUTED, informed by SOURCE_VERIFIED rules and HISTORICAL_OBSERVED rejection. **Authentication:** NOT_APPLICABLE.

**Expected versus observed:** The written beat contains causality. No viewer comprehension, performance or rendered blocking test has occurred. Refresh after the approved premise or shot timing changes.

## 4. A reveal: change what the audience understands

**Weak, illustrative:**
> The doors open on a huge Kids throne. Everyone smiles. Epic reveal.

This introduces scenery but does not specify a change in understanding.

**Stronger reveal mechanism, illustrative:**
> Early in the film, a close view of a canonical Kids cuff shows someone straightening it before stepping forward; framing withholds who is wearing it. At the payoff, repeat that action in a wider composition: the wearer is one of the actual Kids product-card models. The second Kids model joins, and the camera now gives both canonical fronts clear space as they move through the carriage. Skyy's earlier eyeline must connect to their arrival.

The exact models, outfits and source construction are fixed. No adult is transformed into a child, no garment changes scale, and no new design is invented. The earlier clue must be present in the edit; the wide shot cannot earn a payoff solely because its written description calls it one.

**Expected:** The audience revises an assumption about the wearer; the Kids products become identifiable. **Observed:** Only a written example exists. It is not a complete narrative and not founder-approved. It must be judged against the full story and may be rejected.

**Evidence:** founder requires a Kids reveal and canonical product fronts; [current rejection](../identity-correction/founder-rejection.json); viral-content-formula anti-pattern against clickbait without payoff, lines 193–199.

**Classification:** ILLUSTRATIVE_UNEXECUTED. **Authentication:** NOT_APPLICABLE. Refresh when setup, cast, garment or reveal order changes.

## 5. Collection identity: specify a source-derived visual choice

**Weak, illustrative:** “Black Rose is black; Love Hurts is red; Signature is gold; Kids is colorful.”

**Stronger direction record, illustrative:** Select the exact collection hero asset and name the feature used, its position, and how it supports the shot. For Black Rose, a source-confirmed bridge/metalwork form can inform the carriage view or framing while the bomber remains foreground. Record the hero as environment authority only. It cannot overwrite actor, garment or train continuity.

For every collection, attach a crop or locator from the actual hero and explain the adaptation. A new floating sculpture or palette alone is not proof of incorporating that hero.

**Evidence:** [source manifest](../../train-commercial/source-manifest.json) identifies hero_environment_only sources; br-004 records in that older manifest are superseded for the Black Rose product by current br-006 source records. Do not load an entire old manifest as undifferentiated authority.

**Classification:** SOURCE_VERIFIED authority separation; ILLUSTRATIVE_UNEXECUTED adaptation. **Authentication:** NOT_APPLICABLE. Source bytes for hero media were not freshly rehashed in this audit. Refresh before generation.

## 6. Stronger motion prompt: direct only what should move

**Weak, illustrative:** “Beautiful luxury, cinematic 8K, emotional, fluid, realistic, breathtaking reveal.”

**Stronger motion instruction, illustrative; assumes an already approved image:**
> The man first shifts his eyes toward Skyy's hand, then turns his head slightly. Skyy draws the interior handle toward herself while keeping her shoulders in place. The camera holds its position until the door begins to move. End before either character steps through.

This splits a complex interaction into a controllable shot. A separate next shot handles passage. Fixed faces, garments and composition belong in the approved frame/reference contract; a motion prompt is not a substitute for attaching them.

**Evidence:** [Runway image-to-video guide](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide) assigns visual appearance to the image and movement to the prompt. [Higgsfield Kling guide](https://higgsfield.ai/blog/Kling-3.0-is-on-Higgsfield-User-Guide-AI-Video-Generation) cautions against overloading shots and conflicting end frames. Verified 2026-09-12.

**Classification:** SOURCE_VERIFIED guidance; ILLUSTRATIVE_UNEXECUTED shot. **Authentication:** NOT_APPLICABLE to public documentation. No motion test occurred.

**Limit:** Provider-specific prompt handling still applies. Keeping actions simple does not guarantee hand anatomy, identity or physical correctness.

## 7. Do/don't examples for the supporting skills

| Skill | Correct application | Incorrect application and correction | Evidence/status |
|---|---|---|---|
| animate | Make player motion purposeful; provide deliberate Play/Pause and reduced-motion behavior for video as well as CSS. | Apply hover/particle/entrance effects to every film shot. Use the skill only for interface presentation; film direction is separate. | SOURCE_VERIFIED, animate 19–47 and 144–162; ILLUSTRATIVE_UNEXECUTED implementation. |
| premium-feature-system | Embed an approved film with its exact candidate, poster/fallback and measured delivery behavior. | Treat exported files as creative or conversion success. Require film acceptance and measured performance separately. | SOURCE_VERIFIED, skill 14–21, 56–61, 79–88; no embedding performed. |
| ln-1000 | Borrow fresh-state/checkpoint concepts into a distinct media ledger. Preserve rejected and paused states. | Run Kanban code coordinators, change permissions or push worktrees to “write a story.” Do not invoke the software pipeline for this film. | SOURCE_VERIFIED, skill 15–23, 169–170, 335–344, 416–424; runtime not tested. |
| viral-content-formula | Compare two understandable openings with the same remaining film and product. Record retention and product/story recognition if a test is authorized. | Promise virality because two triggers are present. Classify this as a hypothesis and avoid invented platform results. | SOURCE_VERIFIED source/overlay distinction; ILLUSTRATIVE_UNEXECUTED experiment. |
| Fashion Theme Team | Apply existing canon, product-fidelity and independent review controls; make story acceptance explicit. | Treat source hashes or a generated gap inventory as a complete creative audit. Inspect semantics and the actual visual sequence. | Both narrative source bindings REPRODUCED_LOCAL; rejection HISTORICAL_OBSERVED. |

Authentication for these supporting examples: NOT_APPLICABLE. Expected behavior is specified; no UI, software pipeline, live experiment or campaign launch occurred. Revalidate after affected skill/contract changes.

## Minimal film packet to fill the directing gap

For every shot record:
1. Shot ID, duration and place in the sequence.
2. What the audience already knows; what is withheld; payoff shot ID.
3. Character objective, visible action, response and consequence.
4. Camera start/end, reason for movement/cut, eyelines and screen direction.
5. Source-bound actor, Skyy identity, wardrobe/SKU and hero roles.
6. Product feature that must be legible and intended readable interval.
7. Original footage source frames, if present, and immutable visual constraints.
8. Exact user intent, enhanced prompt, submitted request and output candidate.
9. Independent story, identity, product, optical and editing review.
10. Founder acceptance recorded separately from provider completion.

A short silent animatic should let a fresh reviewer explain the action and identify the product without reading the treatment. This is a proposed qualitative test; no audience study has been run.

Useful existing sources:
- [Product fidelity](/Users/theceo/plugins/fashion-theme-team/skills/product-fidelity-image-edits/SKILL.md)
- [Video fidelity](/Users/theceo/plugins/fashion-theme-team/skills/product-fidelity-image-edits/references/video-fidelity.md)
- [Brand experience](/Users/theceo/plugins/fashion-theme-team/skills/fashion-brand-experience/SKILL.md)
- [Brand photography brief](/Users/theceo/.agents/skills/fashion-theme-team-global/package/vendor/branded-skills/social-media/brand-photography-brief/SKILL.md)
- [Product photography brief](/Users/theceo/.agents/skills/fashion-theme-team-global/package/vendor/branded-skills/social-media/product-photography-brief/SKILL.md)
- [Visual QA](/Users/theceo/plugins/fashion-theme-team/skills/fashion-visual-commerce-qa/SKILL.md)

This file is integrated into this audit through AUDIT.md and task-ledger.json. It has not been integrated into canonical skill/router sources; therefore it does not establish global skill-example compliance.
