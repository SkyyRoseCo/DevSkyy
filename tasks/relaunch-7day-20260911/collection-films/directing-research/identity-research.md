# Identity continuity and reference-driven film production

## Research judgment

Use verified source images to establish appearance, reviewed scene frames to establish staging, and motion prompts to describe actions through time. A model name, repeated character description or “100% identical” instruction cannot establish exact likeness or garment fidelity. The available official guidance supports a reference-conditioned workflow; it does not establish a best model for this particular mixture of a real performer, an illustrated mascot and exact fashion products.

Scope: public documentation reviewed September 12, 2026. Authentication is not applicable to this document review. No account capability, generation result, paid execution or campaign approval is demonstrated here. Prompt examples below are illustrative proposals, not executed results.

## What the official documentation supports

| Route | Source-verified capability | Application and limitation |
|---|---|---|
| Runway Gen-4 Image References | Up to three active image references; saved reference names; individual character/scene iteration; references can include stylized subjects. [1] | Useful for candidate scene frames. Its documented wardrobe variation example demonstrates why a generated result must be checked. This is a still-image feature, not proof that a video connector accepts three identity references. |
| Runway image-to-video, guide optimized for Gen-4.5 | The input image supplies appearance and composition; text primarily directs subject, environment and camera motion. Sequential instructions and rough timestamps are supported guidance. [2] | Approve the mixed live-action/Skyy frame first. Motion instructions should identify each subject unambiguously. Do not use motion text to repair the wrong actor in the input. |
| Runway longer-film workflow | Treatment, storyboards, neutral character plates, environment references and editorial assembly. [3] | Useful production sequence. For this project, use original actor angles when available; generated new angles remain candidates, not new canonical identity evidence. |
| Kling VIDEO 3.0, native guide | Multi-shot, start/end-frame generation and start-frame-plus-Element reference; flexible 3–15-second video. [4] | Applicable capability family. Native guide does not establish identical controls on Higgsfield CLI, MCP or Runway's connector. |
| Kling Element Library | Native 3.0 supports up to three bound Elements in start-frame/start-end-frame generation; guide also describes broader reference modes and multi-angle assets. [5] | Do not collapse route-specific limits into a universal “seven references.” Separate the man, Skyy and product roles; determine actual slots from the executing route. |
| Kling VIDEO 3.0 Omni | Image/video/Element inputs; video-created character Elements; multi-shot and up to 15 seconds. [6] | Distinct from standard 3.0. Promotional consistency claims are not independent tests. A video-derived Element is generative conditioning, not preserved original footage. |
| Higgsfield Kling 3.0 UI | Guide specifies up to five shots, custom shot durations, audio on/off and start/end controls. Same Element is tagged wherever it reappears. [7] | Custom shot mode can represent an approved scene plan. Automatic shot splitting is better treated as a draft. UI syntax and capacities must be checked against the actual connector before execution. |

**Documentation tension:** Higgsfield's guide describes end-frame-only operation and broad frame controls, while its practical connector may expose a stricter schema. Kling's native Element guide differentiates reference modes. These are surface-specific descriptions, not interchangeable API contracts. The supported request schema must decide valid combinations; documentation alone does not certify successful submission.

## Recommended production sequence

1. **Keep four reference roles explicit:** performer identity; Skyy identity; collection garment; environment/hero architecture. The original Black Rose man remains the performer. A product-card model cannot silently replace him. Skyy's face, curls and proportions remain fixed while approved collection wardrobe changes.
2. **Plan the required angles.** Obtain matching existing source views for the expected camera travel. A full orbit exposes unseen garment surfaces and identity angles; lacking sources is a coverage gap. Prefer a different shot or seek additional approved evidence instead of inventing the hidden construction.
3. **Build and review each scene frame.** Check both faces, scale relationship, wardrobe, contact shadows, eyelines and product visibility before motion. Use a source manifest; a pleasant generated frame is not a replacement for original references.
4. **Compile route-specific motion.** Describe one readable action or short causal sequence. Keep camera movement and available duration physically compatible. Give the garment a deliberate front-facing hold where the story allows it.
5. **Review motion at the beginning, intermediate frames and end.** Check identity, garment markings, closure/panels, material, anatomy, occlusion recovery and screen direction. Sample more densely around turns, hand contact and cuts.
6. **Assemble the protected footage separately.** The supplied video may contribute silent, product-readable excerpts. Generated reference conditioning does not preserve those original pixels; use the actual source selections in the edit.

These are production recommendations derived from the source guidance and project constraints, not a tested quality benchmark.

## Prompt enhancement rules

Enhancement should remove ambiguity and add playable action, useful camera direction and source roles. It should not add a different person, substitute wardrobe, invent embroidery or remove Skyy's illustrated characteristics. Use positive visual description in Gen-4 Image prompts; its official guide warns that negative prompting is unsupported. [8]

Maintain separate records for a still prompt, a motion prompt and editorial requirements. Audio-off and canvas size belong in supported generation settings as well as the production brief. A prompt sentence alone is not proof those settings were applied.

Runway also publishes a versioned Product Ad Recipe that analyzes product images, builds a storyboard and renders video in one request. Its listed public version is `2026-07`. This is an execution workflow, not a harmless prompt enhancer. It can be investigated for generic product-ad coverage, but its combined generation step is a poor default when an approved storyboard and protected original footage must control the edit. [9]

## Two illustrative improvements

**A. Candidate scene-frame prompt; references already verified and attached.**

Incorrect: “A handsome male model and cute realistic girl on a luxury train, matching black designer jackets, cinematic masterpiece.”

Correction: “The adult man in the performer reference stands on the left of the train aisle. Skyy from the character reference stands on the right, retaining her illustrated face, full curls and compact proportions. Each wears the approved Black Rose sherpa bomber shown in their respective wardrobe references. They look toward the same doorway beyond the camera. Waist-up two-shot, both jacket fronts visible, soft window light across the garment texture, deeper carriage shadows behind. Live-action environment and adult performer, with Skyy's established illustrated rendering integrated through matching light and contact shadows.”

Why: explicit identity/style roles prevent “realistic girl” from redefining Skyy; staging gives both subjects a shared focus. This does not by itself establish a complete story. If the selected route has three slots and the verified inputs exceed that budget, use reviewed intermediate scene/wardrobe references or another supported route; do not silently omit sources. [1,8]

**B. Motion prompt from an approved starting frame; six-second continuous shot.**

Incorrect: “Massive cinematic reveal, both jacket fronts visible throughout a fast 360-degree orbit, perfect faces, dramatic emotion.”

Correction: “Skyy takes one step toward the doorway, then stops and looks back at the man. He notices her pause, shifts his gaze toward the doorway and follows one step. The camera tracks backward a short distance along the aisle, maintaining their relative positions. They settle side by side for the final two seconds, their jacket fronts facing the camera. Continuous shot, restrained natural movement.”

Why: action, response and final framing are achievable within a short clip; the camera no longer contradicts the product view. Actual facial/garment fidelity still needs review. An expansive reveal would be a separately planned shot with its own setup, reference and timing. [2,7]

## Sources

1. Runway, [Creating with Gen-4 Image References](https://help.runwayml.com/hc/en-us/articles/40042718905875-Creating-with-Gen-4-Image-References). Publication date not displayed; accessed September 12, 2026. Sections: character recommendations, multi-reference prompts, advanced iteration.
2. Runway, [Image to Video Prompting Guide](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide). Publication date not displayed; accessed September 12, 2026. Explicitly optimized for Gen-4.5; core elements, sequential prompting and unwanted cuts.
3. Runway, [How to create longer videos and films](https://help.runwayml.com/hc/en-us/articles/26871350018835-How-to-create-longer-videos-and-films). Publication date not displayed; accessed September 12, 2026. Story planning, character plates and assembly.
4. Kling AI, [Kling VIDEO 3.0 Model User Guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide). February 6, 2026. Capability matrix and model highlights.
5. Kling AI, [Kling Element Library User Guide](https://kling.ai/quickstart/klingai-element-library-3-user-guide). February 5, 2026. Route-specific binding limits and character Elements.
6. Kling AI, [Kling VIDEO 3.0 Omni Model User Guide](https://kling.ai/quickstart/klingai-video-3-omni-model-user-guide). February 6, 2026. Page body title; search metadata misleadingly labels it a color-prompts guide.
7. Higgsfield, [Kling 3.0 on Higgsfield: A Guide to the Next Era of AI Video Generation](https://higgsfield.ai/blog/Kling-3.0-is-on-Higgsfield-User-Guide-AI-Video-Generation). February 12, 2026; page reports “last updated: 2w ago” at access. UI multi-shot, Elements and frame controls.
8. Runway, [Gen-4 Image Prompting Guide](https://help.runwayml.com/hc/en-us/articles/35694045317139-Gen-4-Image-Prompting-Guide). Publication date not displayed; accessed September 12, 2026. Positive descriptive language.
9. Runway Dev, [Product Ad](https://docs.dev.runwayml.com/recipes/product-ad/). Publication date not displayed; current listed recipe version `2026-07`; accessed September 12, 2026. Inputs and execution sequence.
