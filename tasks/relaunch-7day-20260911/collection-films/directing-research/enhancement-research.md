# Prompt enhancement for source-faithful cinematic fashion

## Findings

The strongest workflow separates a director’s brief, a still-image specification, a motion instruction and an editing instruction. Enhancement should translate approved decisions into a supported model interface; it should not invent casting, garment construction or the plot. This is a recommended operating design, not a measured claim that a longer prompt produces better films.

Higgsfield currently documents two materially different photoshoot routes. The official CLI skill v0.12.0 uses a backend enhancer and GPT Image 2. The installed OpenAI plugin skill assembles structured prompts for Nano Banana Pro. Their model mandates and assembly mechanisms conflict; they are alternative routes, not interchangeable steps. The official CLI skill’s claim that bypassing enhancement produces worse output has no comparative benchmark attached and should not establish model superiority.[1][2]

Read-only local CLI help on September 12, 2026 explicitly exposes `--enhance-only`, `--brand_context`, `--product_context`, repeatable `--image`, and `--aspect_ratio`. It describes enhancement-only as returning prompts without submitting generation jobs. This check required no authentication; no enhancement, upload or render was executed for this research. Neither this help nor the public CLI skill exposes a reviewed-prompt token or an option that submits a previously returned expansion unchanged. Consequently, exact expanded-prompt freezing through the photoshoot route remains unproven.[1][3]

## Cinema Studio capabilities and boundaries

Higgsfield’s account of Cinema Studio describes controls for camera, lens and focal length, later aperture, reusable references, genre and projects. It explicitly explains that lens character is amplified rather than physically equivalent to real optics. Its newer multishot workflow can proceed directly to video. Therefore, still-first is a deliberate fidelity checkpoint for this campaign, not a universal prerequisite imposed by the product.[4]

The official camera guide recommends defined beginning and ending framing, movement speed and an explicit distinction between a dolly and a zoom. It describes camera, lighting and lens settings as controls separate from movement wording. Treat its reproducibility language as vendor guidance: it does not demonstrate deterministic identity, physical optics or repeatable pixels for SkyyRose.[5]

The current public CLI model reference documents `cinematic_studio_video_3_5` with camera style, lighting scheme, color grading, image/start/end references and multishot fields. `style_prompt` is mutually exclusive with the inline camera/lighting/grading axes. By comparison, its 3.0 entry exposes genre, speed ramp, references and multishot controls. These are source-verified schemas; fresh account availability and actual behavior of 3.5 were not tested. Do not infer a mapping from every Cinema 4.0 browser control to a 3.0 CLI request.[6]

## Recorded enhancer failure

Two historical local receipts contain enhancement-only requests and returned text. Neither request attached images, so mentions of filenames in their prompts were not actual media bindings.[7][8]

| Input | Recorded output | Production implication |
|---|---|---|
| Generic luxury train/mascot intent | Invented flower-led product, overcoat, cobalt mascot and decorative lettering | Mood adjectives did not constrain brand identity or product selection |
| Directed Black Rose door encounter | Retained the encounter and split photographic/illustrated styling, but appended bans on cartoon rendering and doll eyes; asserted garment details without attached references | Better action description still required contradiction and source review |
| Both requests | Returned 4:5 | Set the campaign’s 9:16 format explicitly |

These are observations about returned prompt text, not rendered visual failures or a controlled model comparison. The directed result also introduces camera/lighting specificity that sounds authoritative without proving a workable set: apparent precision must be checked against the actual floor plan and required simultaneous focus.

## Recommended enhancement compiler

1. **Capture source authority.** Record actor, mascot identity, garment and environment references independently. Bind actual files/media IDs in the request; a filename in prose is insufficient. Record which reference governs which property, and which generated candidates are merely proposals.
2. **Write the shot’s function.** State the visible action, what changes, the audience’s question, and the required product view. A deliberate inspection shot may serve product recognition without adding another plot event.
3. **Resolve staging.** Identify body positions, eyelines, movement direction, depth and light path. Reject mutually exclusive requirements such as a complete orbit while both jacket fronts remain continuously visible.
4. **Prepare still intent.** Specify the decisive instant, source roles, composition, product visibility and render registers. Add detail only when it resolves ambiguity. Use backend context fields where supported; do not substitute a hand-written final expansion while claiming the mandated photoshoot route.
5. **Inspect enhancement.** Compare additions and deletions against the brief. Flag new wardrobe features, identity substitutions, stylistic conflicts, added writing and incompatible framing. Do not silently edit returned text and assume the next backend call will use that edited expansion.
6. **Confirm a supported handoff.** Establish how the chosen interface submits the reviewed intent and its references. If enhancement is recomputed, review its new output when exposed and retain the actual submission receipt. Where the exact submitted expansion is unavailable, disclose that limitation and inspect resulting pixels before accepting the shot.
7. **Compile motion separately.** Start from the accepted image/state. Describe subject action, environmental movement, camera path and end state. Set supported duration, aspect, audio and style parameters explicitly. Avoid repeating a full still-photography essay when the reference already defines appearance. Runway likewise advises concentrating image-to-video text on movement rather than redescribing the input image.[9]
8. **Evaluate the result.** Examine face/hair/proportions, exact garment details, hands, contact, eyelines, temporal stability and product-readable intervals. A successful job status establishes completion, not continuity or narrative effectiveness. Keep original source-video editing outside generative transformation: select silent excerpts and preserve their visuals.

## Illustrative examples

**Example 1 — still enhancement.** Incorrect illustrative input: “Epic luxury, gorgeous model, magical mascot, photorealistic everything, no cartoons, massive reveal.” It leaves casting unspecified and directly conflicts with the illustrated mascot. Historical receipts support that this class of omission/conflict requires review; this exact sentence was not tested.

Improved intent, with separately attached verified references: “A 9:16 storyboard still at the instant the actual Black Rose performer notices Skyy through the open carriage doorway. The performer stays photographic. Skyy keeps the supplied illustrated face, curls, eye shape and proportions. Outfit references govern only each br-006 bomber. Their attention is on each other; hands remain clear of the garment fronts. Show the established carriage geometry and window light. Preserve authentic garment marks; add no wording.”

This is a constrained shot example, not a complete story, approved scene or successful generation. The next check is source correspondence and staging, followed by scrutiny of any enhancer additions. The correct principle is separation of identity, outfit and rendering register, rather than a blanket realism demand.[7][8]

**Example 2 — motion enhancement.** Incorrect illustrative input: “Orbit 360 degrees quickly while both jacket fronts remain visible, then reveal every collection and the Kids line in five seconds.” Its coverage requirement is geometrically incompatible with the camera path and its event load obscures a readable progression.

Improved motion instruction for an already accepted matching keyframe: “Skyy releases the door handle and steps half a pace aside. The man’s gaze shifts from her jacket to her face. Camera makes a short lateral move toward the doorway and settles with both fronts unobstructed. End before he crosses the threshold.”

Use a separate subsequent shot for a collection reveal. Do not invent universal word limits: concise means one comprehensible action progression, not omitting necessary direction. This example is unrendered; actual blocking, timing and comprehension remain to be tested.[5][9]

## Sources

1. Higgsfield AI. [Product Photoshoot skill v0.12.0](https://raw.githubusercontent.com/higgsfield-ai/skills/main/higgsfield-product-photoshoot/SKILL.md). Undated; accessed September 12, 2026. Local matching route: `/Users/theceo/.agents/skills/higgsfield-product-photoshoot/SKILL.md`.
2. Higgsfield OpenAI plugin. Product Photoshoot, installed distribution 2.0.0. Local source `/Users/theceo/.codex/plugins/cache/openai-curated-remote/app-6a3293e129088191abf0875820e839da/2.0.0/skills/product-photoshoot/SKILL.md`; accessed September 12, 2026. Private filesystem source; no public equivalent asserted.
3. Higgsfield CLI. Local `product-photoshoot create --help`, executed September 12, 2026 at `/Users/theceo/.npm-global/bin/higgsfield`; authentication not applicable. Public [CLI repository](https://github.com/higgsfield-ai/cli).
4. Higgsfield. [Inside Higgsfield #1: How We Built Cinema Studio](https://higgsfield.ai/blog/how-we-built-cinema-studio). Publication date not established; accessed September 12, 2026.
5. Higgsfield. [How to Control Camera Movement, Angles, and Lens in AI Video](https://higgsfield.ai/blog/ai-video-camera-control). July 24, 2026; accessed September 12, 2026.
6. Higgsfield AI. [CLI Model Reference](https://raw.githubusercontent.com/higgsfield-ai/cli/main/MODELS.md), Cinematic Studio 3.0 and 3.5 sections. Undated, mutable main branch; accessed September 12, 2026.
7. SkyyRose. `collection-films/skill-audit/enhancer-generic.json`, recorded enhancement-only response, September 12, 2026. Local historical execution evidence; no new authenticated execution here.
8. SkyyRose. `collection-films/skill-audit/enhancer-directed.json`, recorded enhancement-only response, September 12, 2026. Same scope as source 7.
9. Runway. [Image to Video Prompting Guide](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide). Undated; accessed September 12, 2026. Prompting guidance, not proof of Higgsfield implementation.
