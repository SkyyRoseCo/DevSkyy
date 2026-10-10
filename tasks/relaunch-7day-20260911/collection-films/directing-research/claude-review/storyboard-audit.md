# Review of Claude's storyboard research snapshot

Review date: 2026-09-12. Scope: full `snapshot/research-storyboard.md`, including all 94 listed URL rows and gaps. Snapshot SHA-256: `b5d2d42e2bddc551c33a46d1d3a9c4aa03231dab805ad8d3b154ecb8d49ef49e`.

This is a review of a research document, not a review of newly rendered footage or a production approval. Public primary documentation was checked for the Runway reference workflow, Motion Brush, Google Shorts specifications, and TikTok's cited research. No provider account was accessed and no media was uploaded or generated. Authentication: not applicable to these public-source checks. Claude's files and terminal were not changed.

## Assessment

Useful discovery report with honest labels for many single-source, truncated, and unverified findings. Its strongest practical material is the SKU-aware shot list (lines11–14), planning different outputs before production (line19), and explicit garment-fidelity rejection criteria (line28). Those ideas are suitable inputs to our existing directing workflow.

It is not yet a dependable executable production recipe. The report combines ordinary photography templates, vendor advice, platform advertising recommendations, and model capabilities without consistently distinguishing their applicability to our protected footage and wordless stories. One model capability is contradicted by official documentation. The number of links is breadth, not the number of independently verified claims.

## Findings and concrete corrections

### 1. Correct the Gen-4 Motion Brush claim before any workflow adopts it

**Evidence:** snapshot line27 describes a March2026 Runway Gen-4 case study using Motion Brush. Runway's official [Gen-2 Deprecation](https://help.runwayml.com/hc/en-us/articles/41072248471187-Gen-2-Deprecation) explicitly places Motion Brush in Gen-2 and says it is unavailable on newer models; the page dates complete Gen-2 deprecation to May11,2025.

**Implication:** the unnamed third-party case study cannot substantiate that capability as written. A production plan using it would name a control unavailable on the stated model.

**Correction:** mark the case study technically inconsistent and exclude its tool instructions until the author explains the actual generation pipeline. Use documented controls for the selected model and interface. Do not substitute an unverified modern tool name into the anecdote.

### 2. Separate still references from video inputs and account-specific tools

**Evidence:** line25 bundles Gen-4 `@ref`, Kling Elements, Veo Ingredients, and other mechanisms as one technique stack; line186 admits that no official Runway/Kling/Veo documentation was fetched. Official [Gen-4 Image References](https://help.runwayml.com/hc/en-us/articles/40042718905875-Creating-with-Gen-4-Image-References) documents named references for **image generation**, with up to three active references per generation. That does not establish the same interface for a video request or a connector.

**Correction:** write a separate record per intended route: provider, exact model/version, still or video stage, UI/API/connector, supported input roles, documented limits, and whether this account's route has been exercised. A broad 2–7-image research set can exist without implying all seven images can enter the generation.

**Correct example — primary-document supported, no authenticated run claimed:** select the necessary identity/wardrobe/composition references for a Gen-4 Image still; inspect the resulting image; pass an accepted composition into the separately documented video stage.

**Illustrative incorrect example:** send `@Skyy @male @bomber` as plain text to an arbitrary video connector and call the identities locked. Correct by using actual supported reference fields and reviewing the resulting people and garments; names in prompt text alone do not prove binding.

### 3. Add an explicit exception for protected Black Rose footage

**Evidence:** lines27,31–32 recommend a common LUT/grade; line27 reports hiding identity drift with quick cuts and grading. Line46 describes a universal vertical-master workflow. None is reconciled with our current task's instruction to preserve original Black Rose visuals and the actual performer, with source audio excluded.

**Correction:** distinguish generated train coverage from protected source inserts. Match new footage to the source where appropriate; keep source excerpts visually unchanged. Preserve source geometry through a deliberate edit layout rather than automatically cropping it to a vertical master. Audio removal and authorized excerpt selection are separate from image alteration.

**Task-specific correct example — user-instruction grounded:** cut to a readable original bomber excerpt, retain its actual performer and original visual treatment, omit the source audio, then return to accepted generated coverage.

**Illustrative incorrect example:** grade the source video and shorten mismatching face shots until the generated man appears consistent. Correct by rejecting the wrong identity and retaining the real source performer. An edit that conceals a failure does not resolve it.

### 4. Convert quantitative prescriptions into scoped hypotheses

**Evidence:** the report proposes 10–15 shots per30seconds (line15), 15–20 shots per30seconds (line24), but also 3–5 hard cuts in15–30seconds (line45). Lines23–26 include 40–80 reference frames, 48-hour turnaround, stills at3% of render cost, and75–85% rejection, largely from individual operators. Line42 calls early-hook advice industry consensus and adds fixed success/failure rates without common measurement definitions.

**Correction:** these are different operators' recipes, examples, or reported outcomes, not a universal pacing or cost standard. Label each with source type, sample/denominator if supplied, model/pricing conditions, and applicability. Do not force the24-second Kids board into a new shot count. Time the reveal, recognition, response, and garment read according to comprehension tests; generation duration and edited shot duration are different quantities.

**Primary-source clarification:** TikTok's [Creative Codes article](https://ads.tiktok.com/business/en-US/blog/creative-best-practices-top-performing-ads) does report the first-six-seconds recall figure and product/CTA effects. Its footnotes point to studies from2020–2022. This is historical platform research, not a2026 SkyyRose sales benchmark. Its support for additive brand cues also does not justify the blanket instruction in line42 to postpone brand identity until the end.

### 5. Add a project-specific silent-story test; templates do not establish drama

**Evidence:** lines14–16 cover panel fields, camera information and treatment structure. Lines40–46 emphasize hooks, overlays, CTA and advertising rhythm. Those provide structure but do not test whether a viewer understands an eyeline, a decision, spatial cause, or a character's change without explanatory text.

**Correction:** each board needs observable state before the action, the action itself, the response, the changed state, garment visibility, screen direction, and the viewer inference we expect. Use notes-hidden review. Ask what happened, what caused the next action, who initiated, and what clothing the viewer remembers. Technical completeness and silent causal clarity need separate results.

**Task-specific example, proposed test not a new observed result:** in Kids RouteA, test whether viewers recover red initiates → Skyy initiates → purple initiates, rather than merely reporting three characters posing. If the third initiation is missed, change gaze/hold/coverage before adding production polish. No extra rendered train spectacle will repair an unreadable exchange by itself.

Keep added captions, voiceover and CTA endcards out of the film unless the user changes that requirement; placement copy/CTA can be planned separately. Document any platform or disclosure requirement independently rather than silently turning vendor advice into creative instructions.

### 6. Keep source identity, wardrobe and world references in separate roles

**Evidence:** line25 recommends a single consistency stack and last-frame chaining; line32 describes a generated brand model saved as FINAL. The report does not yet account for Skyy's supplied identity versus archive wardrobe references, the actual Black Rose performer, or the two Kids colorways.

**Correction:** add explicit identity source, wardrobe/SKU source, environment/hero reference, and generated candidate status per shot. Generated angle extensions do not become canonical because a file is named FINAL. Use frame chaining only when its continuity is intended and the handoff frame passes source comparison; re-anchor against canonical sources so errors do not propagate.

**Illustrative incorrect example:** use whichever archived mascot outfit photo is closest to a shot as both face and garment authority. Correct by retaining the supplied Skyy identity reference while separately binding the collection wardrobe. Preserve one Skyy outfit within each continuous scene and explain changes across chapters.

### 7. Tighten evidence accounting and quarantine legal/policy claims from production rules

**Evidence:** line3 claims96URLs; the explicit ledger at lines84–177 contains94unique URL rows. The yes/no column is unlabeled; line141 says yes for a headline-only fetch. Lines75/78/189 disclose truncation and use of search highlights. Line186 correctly admits missing primary model documentation. Legal/platform claims in lines50–58 often rely on commercial blogs and law-firm interpretations; not all have a primary legal or platform reference attached.

**Correction:** report94listed ledger rows or enumerate the missing two. Replace yes/no with discovery-only, partial fetch, full fetch, and claim verified, with the exact passage and access date for consequential claims. Retain the candid gap section and attach uncertainty to the relevant finding, not only at the end.

This review does not verify the legal conclusions. Do not operationalize the specific jurisdictional effective dates, fines, geographic scope or platform label requirements from this snapshot alone. Review those against the applicable official texts and selected placement before release; this research limitation does not create a new prohibition on authorized offline story development.

## Primary checks that held

Google's [Shorts asset specifications](https://support.google.com/google-ads/answer/16041697?hl=en) support line38's distinction between a permitted video up to3minutes and the initial60seconds played in the Shorts feed, plus the10–30-second action-oriented recommendation. Those are placement-specific recommendations/limits, not a requirement that every collection story last30seconds.

TikTok's official Creative Codes page supports line40's hook/body/close account. The corrections needed concern study age, interpretation, and applying a wordless brand brief—not whether the quoted figures appear on the page.

## What to carry into our next work package

1. Keep the current roughboard comparison; improve causal clarity before final imagery.
2. Expand each shot packet with source roles, immutable source-insert status, garment rejection criteria, and a notes-hidden viewer question.
3. Qualify the exact still-to-motion route with current primary specifications before calling reference consistency solved.
4. Test one complete exchange and readable product sequence, then scale accepted footage into collection and commercial edits.
5. Treat format, performance and disclosure guidance as separate placement decisions; do not inherit a vendor's fixed shot count, template story, cost ratio or 48-hour promise.

No campaign launch, film approval, authenticated rendering success, or legal clearance is implied by this review.
