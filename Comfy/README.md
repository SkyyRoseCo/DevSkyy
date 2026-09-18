# SkyyRose local ComfyUI project

This project is the governed execution surface for SkyyRose scene candidates.
The canonical catalog and image sources remain in the DevSkyy repository; this
directory stores workflows, hash-bound scene contracts, OODA orchestration, and
append-only run evidence.

## Runtime contract

- Backend: Comfy Desktop local API (`http://127.0.0.1:8189` in the verified
  environment)
- Project default: `defaults.where: local` in `comfy.yaml`
- Provider/API spend: forbidden unless separately authorized and the scene
  contract has no execution blockers
- Generated images: candidate-only until product-fidelity, physical-integration,
  optical-realism, independent-review, and founder-approval gates pass
- Canonical product files are uploaded from their registered repository paths;
  generated outputs never become source authority

## Required local models

The retained source-bound workflow uses these official Comfy-Org model files:

- `models/diffusion_models/z_image_turbo_bf16.safetensors` loaded with
  `weight_dtype: default`
- `models/text_encoders/qwen_3_4b_fp8_mixed.safetensors`
- `models/vae/ae.safetensors`
- `models/background_removal/birefnet.safetensors` with SHA-256
  `9ab37426bf4de0567af6b5d21b16151357149139362e6e8992021b8ce356a154`

The shared model root is `/Users/theceo/ComfyUI-Shared/models`. Do not commit
model weights.

The full BF16 diffusion plus full text-encoder pair is intentionally not used:
together they forced this 16 GB unified-memory host into severe swap pressure
before sampling. The retained graph pairs the native BF16 diffusion model with
the smaller mixed-FP8 encoder because Apple MPS cannot execute Float8 diffusion
weights.

## Apple M5 16 GB compatibility verdict

The workflow is structurally valid and source-bound, but this Z-Image model
family is not a practical renderer on the current 16 GB Apple host:

- Native BF16 reaches KSampler but consumes about 19.4 GB of swap and remains at
  step zero.
- Loader-level Float8 is rejected because Apple MPS does not support
  `Float8_e4m3fn`.
- Int8 ConvRot reaches KSampler only with `PYTORCH_ENABLE_MPS_FALLBACK=1`; CPU
  fallback remains at step zero beyond the preview latency budget.

No candidate image was produced. The Int8 ConvRot weight and its reference
template were removed after diagnosis to recover 6.2 GB; they can be downloaded
again from the official template if the workflow moves to compatible hardware.
Execute this retained BF16 graph on a larger-memory compatible runner, or
authorize a separately budgeted provider route. Do not weaken the source
bindings or promotion gates to make a run complete.

## Launch the local server

```bash
comfy --workspace /Users/theceo/ComfyUI-Installs/ComfyUI/ComfyUI launch -- \
  --enable-manager \
  --extra-model-paths-config "/Users/theceo/Library/Application Support/Comfy Desktop/instance-model-paths/inst-1788304801153.yaml" \
  --input-directory /Users/theceo/ComfyUI-Shared/input \
  --output-directory /Users/theceo/ComfyUI-Shared/output
```

This launch path does not add a telemetry feature flag. CLI tracking must remain
disabled; verify it with `comfy --json env`.

## Verify before a run

```bash
comfy --json env
comfy --json project status
comfy --where local --json workflow validate --workflow workflows/lh-004-reference-pilot.api.json
comfy --where local --json run --workflow workflows/lh-004-reference-pilot.api.json --print-prompt
```

The validation receipt must report `spends_credits: false`, an empty
`partner_nodes` list, and no errors before submission.

## Run and recover

```bash
comfy --where local --json run --workflow workflows/lh-004-reference-pilot.api.json
comfy --where local --json jobs watch <prompt_id>
comfy --where local --json download <prompt_id>
```

Append the prompt ID to `job_ids.txt` at submission time and the submission/QC
decision to `LOG.md`. Source hashes and acceptance criteria live in
`scene-contracts/`.

## Provider routing inside the Comfy OODA

Provider selection follows the missing authority. FASHN creates a wearer
candidate only when exact on-model authority is missing. Runway creates
product-free environment plates only. Comfy owns source validation, input
upload, local segmentation, protected-pixel composition, receipts, rejection
routing, and review handoff. Higgsfield remains available only where an
individual scene contract explicitly permits it; rejected Higgsfield candidates
are evidence, never future source authority.

Fashion Theme Team governance is embedded through
`scene-contracts/scene-ooda-index.json` and the durable
`scene-contracts/scene-ooda-ledger.json`. See `FASHION-THEME-TEAM-OODA.md` for
role ownership and handoff boundaries. All five remaining mapped scenes have
individual contracts; blocked scenes remain mapped and validated without being
sent to paid generation.

The legacy `scene_ooda.py` commands remain available for existing Higgsfield
evidence packets such as `BR-COMMERCE-2`, but that scene now forbids another
full-scene Higgsfield attempt:

```bash
python3 Comfy/scripts/scene_ooda.py validate \
  --manifest Comfy/scene-contracts/br-commerce-2-higgsfield-comfy-ooda.json

python3 Comfy/scripts/scene_ooda.py enhance \
  --manifest Comfy/scene-contracts/br-commerce-2-higgsfield-comfy-ooda.json
```

Paid generation is fail-closed: it requires an explicit spend flag and a current
candidate-bound approval. The current Black Rose route recovers exact individual
foreground authorities, creates only an empty Runway environment, and integrates
the protected layers locally.

Environment-plate approvals bind the complete merge-gate state. After the gate
changes to `SATISFIED`, rerun the read-only `environment_plate_ooda.py preflight`
with an empty blocker list and a null approval receipt, then obtain a fresh
founder approval for that fingerprint. A pre-merge receipt cannot authorize the
post-merge request. Preflight never submits a paid generation.

If assertion rules change after a human/product-authority review, re-evaluate
the immutable enhancement receipt without another provider request:

```bash
python3 Comfy/scripts/scene_ooda.py review-enhance \
  --manifest Comfy/scene-contracts/br-commerce-2-higgsfield-comfy-ooda.json \
  --receipt /absolute/path/to/higgsfield-enhance-receipt.json
```

A generated result remains candidate-only and can be staged locally with:

```bash
python3 Comfy/scripts/scene_ooda.py stage \
  --manifest Comfy/scene-contracts/br-commerce-2-higgsfield-comfy-ooda.json \
  --candidate /absolute/path/to/candidate.png
```

Staging uploads the candidate to local ComfyUI and writes a receipt. It does not
promote, wire, deploy, or overwrite any SOT file.

## Specialized garment placement before scene generation

Scenes that lack an approved exact on-model product layer use a separate FASHN
candidate before any environment work. This stage receives one approved
full-body model image and one primary product image; the other physical product
views remain independent review authority because Try-On Max accepts only one
product image and cannot prove unseen construction.

Runtime readiness is read-only and never submits a paid request:

```bash
uv run --frozen python Comfy/scripts/runtime_readiness.py --minimum-fashn-credits 8
```

The FASHN developer API key is loaded from macOS Keychain service
`skyyrose-fashn-api` for the current account. If it is absent, add it through
the `security` command's hidden prompt; `-w` must remain the final option so the
secret is never a command-line argument:

```bash
/usr/bin/security add-generic-password -U -s skyyrose-fashn-api -a "$(id -un)" -w
```

Environment-variable fallback is restricted to CI and tests.

The first governed model plate is `LH-MODEL-01-FULL-BODY-A1`:

```bash
uv run --frozen python Comfy/scripts/model_plate_ooda.py preflight \
  --contract Comfy/scene-contracts/lh-model-01-full-body-a1.json
```

`preflight` verifies the approved identity manifest, identity approval, front
bust, rear-profile corroboration, exact four-credit request, output reservation,
live authentication, and balance. It returns `PASS_PENDING_APPROVAL` only when
the remaining gate is an exact fingerprint-bound spend approval. The separately
authorized execution command is:

```bash
uv run --frozen python Comfy/scripts/model_plate_ooda.py execute \
  --contract Comfy/scene-contracts/lh-model-01-full-body-a1.json \
  --allow-spend
```

The initial governed pilot is `LH-003-TRYON-MAX-PILOT-A1`:

```bash
uv run --frozen python Comfy/scripts/vto_ooda.py prepare \
  --contract Comfy/scene-contracts/lh-003-tryon-max-vto-ooda.json
```

`prepare` performs no paid `POST /run`. It returns `PASS_PENDING_APPROVAL` only
after the full-body model, product sources, authority receipts, request, output
reservation, authentication, and four-credit balance pass. Full `validate` and
`execute` remain blocked until all three gates exist:

1. a founder-approved full-body `LH-MODEL-01` source and authority receipt;
2. the hash-bound product pack and registered `tryon-max` capability; and
3. an approval receipt bound to the current execution fingerprint for one
   four-credit candidate.

Only after those gates pass can the separately authorized command run:

```bash
uv run --frozen python Comfy/scripts/vto_ooda.py execute \
  --contract Comfy/scene-contracts/lh-003-tryon-max-vto-ooda.json \
  --allow-spend
```

The runner sends local inputs as private data URIs, requests one lossless PNG
with a fixed seed, atomically consumes the candidate-bound approval in an
immutable attempt marker before the one-shot paid submission, refuses automatic
submission retry, and writes a contract/input/output/job/provider-credit receipt
from the exact submitted bytes. A successful front-facing response remains
quarantined and candidate-only until an independent reviewer verifies identity,
both visible side pockets and zippers, wearer-relative artwork, fit, and absence
of non-garment drift. The two rear zippered pockets remain source-verified but
must be marked `NOT_OBSERVABLE_IN_FRONT_CANDIDATE`; the candidate can never
claim rear-view or full-360 proof.

The independent receipt is checked separately and cannot be authored by the
candidate builder:

```bash
uv run --frozen python Comfy/scripts/vto_ooda.py review \
  --contract Comfy/scene-contracts/lh-003-tryon-max-vto-ooda.json \
  --candidate Comfy/quarantine/LH-003-VTO/LH-003-TRYON-MAX-PILOT-A1.png \
  --execution-receipt Comfy/receipts/lh-003-tryon-max-pilot-a1-execution.json \
  --review /absolute/path/to/lh-003-vto-independent-review.json
```

An independent `PASS` still reports `scene_input_authorized: false`; explicit
founder product approval must be bound before the candidate becomes an on-model
authority for `LH-COMMERCE-2`.

After that founder-bound foreground approval, BiRefNet extracts alpha without
changing interior RGB. A pixel-level receipt binds the source, alpha mask,
protected output, changed-pixel count, maximum channel delta, and diff hash;
composition refuses any receipt with a protected RGB change. Runway creates one
separately approved empty Fractured Chamber plate. Its Comfy workflow is sealed
to the live node schemas, expected output node, prompt-history entry, and an
immutable pre-submission attempt marker. Comfy then places the protected
customer/product and enchanted-rose layers on a `2048x1152` master. The tracked
API workflows are `workflows/lh-commerce-2-birefnet-segmentation-a1.api.json`
and `workflows/lh-commerce-2-runway-environment-a1.api.json`. No technical pass
authorizes scene promotion, storefront wiring, or deployment.
