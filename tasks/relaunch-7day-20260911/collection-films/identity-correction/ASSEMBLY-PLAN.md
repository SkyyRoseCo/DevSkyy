Execution note: the main Signature reveal uses SGB frames144–239 to retain the completed large-rose ending. See STORY-AS-BUILT.md and final-timeline-preview.json.

# Town Line identity correction: assembly plan

Status: executable edit specification; corrected motion and revised exports are not yet complete. This task created this document only. It made no paid calls, uploaded nothing, and did not alter the original footage, historical edits, or assembly script. Temporary decoded contact sheets were used to verify reuse boundaries.

## Recommended production count

**Eight fresh motion jobs, requesting 75 seconds total, can deliver all five films without repeating motion frames inside a standalone.** Use seven 10-second requests and one 5-second request. This requires the precise recut below; it is not a drop-in replacement for every old clip.

The minimum assumes the requested 5/10-second production choices, two distinct collection encounters/reveals, no frozen or looped filler, and retention of both red and purple Kids outfits. Signature and Love Hurts each require two clips to fill 20 seconds. Black Rose needs two clips for its 12 seconds of new footage. Kids needs two clips after excluding the old character footage. The main commercial reuses selected portions of these same new clips, requiring no additional motion job.

The current callable Runway `generate_video` description lists Kling O3 Pro durations 5, 10, and 15 seconds. This plan deliberately uses the assigned 5/10-second choices. Availability or input acceptance is not established by the schema: the root task is resolving the recorded mascot/child moderation failure. Do not describe adult-only replacements as completing the required shared scenes, change providers to evade a rejection, or count failed/rejected pilots as usable production footage.

| New clip ID | Request | Frames available to the edit at 24 fps | Required story content |
| --- | ---: | ---: | --- |
| `SGA_R2` | 10 s | 240 | Signature model plus exact Skyy; first encounter; fronts visible |
| `SGB_R2` | 10 s | 240 | Same cast and clothes; Golden Gate/rose-monument reveal |
| `BRA_R2` | 10 s | 240; use 168 | Actual source performer plus exact Skyy; black carriage; no invented trouser mark or copied source overlay |
| `BRB_R2` | 5 s | 120 | Same cast; Bay Bridge/silver-edged black rose-star reveal already readable during the usable five seconds |
| `LHA_R2` | 10 s | 240 | Canonical Love Hurts model plus exact Skyy; matching bomber fronts |
| `LHB_R2` | 10 s | 240 | Same cast; invitation/rose-arch reveal |
| `KR_R2` | 10 s | 240 | Red Kids model and exact Skyy: doors open/recognition during seconds 0–6, restrained low invitation during seconds 6–10 |
| `KP_R2` | 10 s | 240; use 228 | Purple Kids model and exact Skyy; coherent train/throne reveal; fronts visible throughout |

These frame budgets require probing the actual returned files. A 5-second provider label alone does not prove 120 usable frames. Historical Higgsfield clips had `24/1` fps and one extra terminal frame; the recorded Runway adult pilot lasted 5.041 seconds, but its actual frame count must not be inferred from that duration. Probe each new download and record its hash, dimensions, pixel format, frame count, rational frame rate, time base, and audio streams before editing.

All Skyy-containing image and motion calls must retain the founder master specified by [STATUS.md](STATUS.md). Black Rose also retains both actual-performer reference frames. The rejected adult pilot `14616b11-3f52-44e0-889a-945f1227ffaa` and prior character-bearing generation outputs are excluded.

## Safe reuse, verified during this planning task

Fresh downloads matched the SHA-256 values in [the existing edit manifest](../build/edit-manifest.json). Every frame in the proposed train reuse range and the door contact sheets was inspected at contact-sheet resolution. These are explicit reuse boundaries, not new character-identity approval.

| Existing asset | Reuse | Evidence and exclusion |
| --- | --- | --- |
| Corrected `TRAIN` | `[0,48)`; 48 frames / 2.002 s | All 48 frames show the train/platform without people or added wording at review resolution. SHA-256 `95a736ed1550944b038040641d4247b07ab33d7bf3041965535e77ac67b20b02`. Use corrected job `47c02d76-7571-410b-a19c-fb5e191711f2`, not the rejected lettered arrival. |
| `DOOR` | **Only `[0,12)`**; 12 frames / 0.5005 s | First 12 frames show closed opaque doors with no people visible. Subsequent frames open onto the rejected cast; do not reuse `[12,72)` in the corrected edit. SHA-256 `f071c24131d3fd4329bb1766fbf47656ca7299f382bc71c33a1f4bacabc51efe`. |
| `SOURCE` | Existing selections unchanged | Verified 192-frame source reel, 720×1280, 24000/1001 fps, silent. SHA-256 `beeb0045d74edf3f7933422aca1ea9df6eed0832fc2d5217a42f88f78b5b3608`. |

The door prefix can precede the corrected red shot, which must begin with a matching doorway opening. If that visual join is poor, remove the prefix and extend the first red range by 12 frames; no extra paid job is needed. Do not slow or loop the old closed doors to restore the old three-second opening.

Temporary evidence from this run: `/var/folders/bz/k0nc044d1fz2rs3kz_gyv99m0000gn/T/town-line-reuse-review-yoyyccc0/{door-0-36.jpg,door-36-72.jpg,train-0-48.jpg}`. These temporary paths are not durable deliverables. The exact asset hashes and frame boundaries above make the inspection reproducible; the implementing task can retain fresh sheets in its evidence directory.

## Exact recommended timeline

All ranges are zero-based, end-exclusive decoded frame indices. Preserve these film IDs and totals. Final time is `frame_count × 1001 / 24000`, yielding 480 frames = **20.020 seconds** and 960 frames = **40.040 seconds**.

```json
{
  "signature": [
    ["SGA_R2", 0, 240],
    ["SGB_R2", 0, 240]
  ],
  "black-rose": [
    ["SOURCE", 0, 48],
    ["BRA_R2", 0, 72],
    ["SOURCE", 48, 72],
    ["SOURCE", 72, 120],
    ["BRA_R2", 72, 168],
    ["SOURCE", 120, 192],
    ["BRB_R2", 0, 120]
  ],
  "love-hurts": [
    ["LHA_R2", 0, 240],
    ["LHB_R2", 0, 240]
  ],
  "kids-capsule": [
    ["DOOR", 0, 12],
    ["KR_R2", 0, 144],
    ["KP_R2", 0, 228],
    ["KR_R2", 144, 240]
  ],
  "town-line-main": [
    ["TRAIN", 0, 48],
    ["SGA_R2", 144, 192],
    ["SGB_R2", 24, 120],
    ["SOURCE", 0, 24],
    ["BRA_R2", 24, 72],
    ["SOURCE", 24, 48],
    ["SOURCE", 72, 120],
    ["SOURCE", 120, 168],
    ["BRB_R2", 24, 120],
    ["LHA_R2", 144, 240],
    ["LHB_R2", 144, 240],
    ["DOOR", 0, 12],
    ["KR_R2", 0, 120],
    ["KP_R2", 24, 120],
    ["KR_R2", 180, 240]
  ]
}
```

Arithmetic and equality of all ordered `SOURCE` ranges to the historical manifest were reproduced locally. Black Rose retains exactly 192 original frames / 8.008 seconds. The main retains exactly 144 original frames / 6.006 seconds. Their positions can shift when adjacent generated shots change, but their source indices and order cannot.

Kids retains a red ending: the first and last red sections are disjoint parts of one new continuous take, separated by the new purple scene. The main likewise uses disjoint red ranges. Generation must deliver the invitation in the final portion; do not claim a gesture exists merely because it was prompted. If the old door prefix is dropped, change Kids' first red range to `[0,156)` and its final red range to `[156,240)` while expanding purple to `[0,240)`; this alternative still totals 480. For the main, remove `DOOR` and extend its first red range to `[0,132)`, retaining the other ranges for 960 total frames.

## Alternative: retain every original shot slot

If creative review requires the original 10/10 Signature, 6/6 new Black Rose, 10/10 Love Hurts, and 3/8/5/4 Kids timing, generate **10 fresh jobs / 85 requested seconds**:

| Existing slot | New request | Retained frames |
| --- | ---: | ---: |
| `SGA`, `SGB`, `LHA`, `LHB` | 10 s each | 240 each |
| `BRA`, `BRB` | 10 s each | 144 each |
| `KR` | 10 s | 192 |
| `KP` | 5 s | 120 |
| `KRI` | 5 s | 96 |
| `DOOR` with corrected cast behind it | 5 s | 72 |

The nine character slots alone total 80 requested seconds, but leaving the original three-second door clip intact would reintroduce rejected people. The fresh five-second door request is therefore required for the unchanged slot layout. The corrected train remains reusable. Extra pilots or rejected attempts are not included in either production count, and these second totals are not credit quotations or retry authority.

## Practical local assembly using the existing implementation

Local tools were verified: Python 3.14.6, FFmpeg/FFprobe 8.0.1 with `libx264`, and curl. No dependency installation is needed. The old script hardcodes `/home/user/town-line-build` and executes at import time, so it is not ready to run unchanged on this Mac. Create a task-local adapter/copy under `identity-correction/` and preserve [the historical assembly script](../build/assemble.py).

1. **Isolate inputs and output.** Use separate `identity-correction/inputs/` and `identity-correction/exports-r2/` directories. Download each accepted new clip once; retain the provider response privately, SHA-256, task ID, and review disposition. Fetch the existing SOURCE/TRAIN/DOOR by the exact manifest URLs and assert the hashes above. Do not overwrite the original input video or historical exports.
2. **Make the output root configurable.** Replace the Linux constant in the new adapter with an explicit output-directory argument. Keep downloaded inputs separate from this root so `urlretrieve` cannot overwrite the same `file://` source it is reading. Either extend input loading to accept a local `path` with an explicit copy or supply local file URIs pointing to the separate input directory.
3. **Separate private download data from deliverable metadata.** Runway asset URLs can contain `_jwt=` authorization tokens. The old script writes `CONFIG` verbatim into the ZIP; do not feed fresh authenticated URLs into that archive path. Keep network URLs in a private download manifest outside the output/ZIP, and archive only relative filenames, job IDs, content hashes, frame metadata, source ranges, and editorial notes. Exclude tokens, upload destinations, cookies, and full provider responses. Also exclude machine-specific absolute file URIs from the public manifest. Error messages should identify a clip ID or filename without its URL.
4. **Preflight actual files.** Use FFprobe decoded frame counts where available, confirm every range is within `usable_frames`, and reject duplicate IDs or unknown references. All accepted generated inputs must be 24/1 fps for the existing algorithm. If a new provider output differs, add a documented generated-only normalization stage and review its result; never route SOURCE through it. Require silence. If audio appears on a generated clip despite the request, make a separate video-stream-copy mute and record both hashes before assembly.
5. **Retain the proven source path.** Preserve `trim=start_frame: end_frame`, rational `settb=1/24000`, frame timestamp spacing `N*1001`, H.264 CRF0 lossless cuts, `-fps_mode passthrough`, and stream-copy concatenation. SOURCE already has this cadence: timestamp rebasing for each cut must not change its spacing, reorder frames, duplicate/drop frames, or transform pixels. Apply fit/pad/SAR changes only to generated inputs. Never crop, grade, resize, mirror, stabilize, overlay, interpolate, or regenerate SOURCE.
6. **Validate final timing and pixels.** Retain per-cut length checks, final 480/960 frame counts, 720×1280, zero audio, final duration checks, and every selected source-frame MD5 comparison at its concatenated offset. Check decoded frame count as well as container metadata. The new 12-frame door prefix introduces half-millisecond segment durations; inspect final frame timestamps and segment boundaries for duplicate, missing, or discontinuous cadence. If MP4 concat duration rounding introduces a gap, use exact packet durations/time bases or a lossless frame-concat path and rerun all source MD5 checks, rather than accepting merely the total duration.
7. **Keep delivery compression separate.** Export five CRF0 lossless MP4 masters and five H.264 High-profile CRF16 viewing copies. Verify the latter independently for dimensions, frame count, cadence, duration, and silence. Source pixel identity applies to masters; delivery compression is explicitly disclosed. Generate contact sheets including the actual final frame (`count - 1`) and review all joins in playback.
8. **Package locally first.** Supply an empty upload list `[]` to the adapted script for local-only export. Keep the existing ZIP file whitelist and CRC test, and include the sanitized edit manifest, verification report, adapter, and original-source receipt. Compute the final ZIP SHA-256 externally; its own hash cannot be embedded inside itself. The old script's archive/upload results are added after its inner `verification.json` is written, so retain a companion `final-report.json` outside the ZIP for archive hash and any later upload receipts. Upload only through the root task's authorized delivery step, preserving sanitized failure reporting.

The original source receipt links the 192-frame reel to the original supplied video. Keep its original-source hash and intervals 695–767, 983–1031, and 1391–1463 alongside the new verification. An MD5 match against the reel alone does not recreate that provenance without the receipt.

## Evidence and limits

- [Existing edit manifest](../build/edit-manifest.json), SHA-256 `88f46cc10437c6dfce45ed06a55cf3ec144e4ed24646632a512cca45dc4110e0` at inspection.
- [Existing assembler](../build/assemble.py), SHA-256 `95303f7806dfd25e6fb77880c17547f0d76b200f4a9d7a236705be2a14e656fa` at inspection.
- [Source selection receipt](../product-selects-receipt.json), SHA-256 `d2f5bfd65e62730d78129bd28290591d2e6a9291a9f3448dc67a355e3f139146`.
- [Historical completed export metadata](../build/final-report.json) establishes prior technical behavior, not acceptance of rejected character continuity.
- [Current adult-shot rejection](kling-adult-shot-review.json) and [correction status](STATUS.md) control exclusions.
- Current Runway connector `generate_video` description was inspected without calling generation. Account authorization/modeled availability is recorded by the root task; this subtask made no authenticated provider calls. Public hash-matched media retrieval and local decoding required no authentication.

Correct, reproduced example: sum the recommended Black Rose ranges to 480 frames and compare its ordered SOURCE ranges against the historical manifest; both checks passed, with 192 source frames retained.

Incorrect, observed example: classify the full DOOR clip as a reusable empty-carriage transition. The decoded frames visibly reveal the old cast. Correction: retain only verified `[0,12)` and cut to a new accepted red scene, or replace the door shot with new corrected footage.

No new cast frame, motion clip, final assembly, browser playback, or upload has passed review merely because this plan is complete.
