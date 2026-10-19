# ComfyUI Setup Hardening Report

Generated: 2026-09-15 · Hardware: Apple M5 16 GB unified memory · ComfyUI 0.36.0

---

## 1. Environment & Hardware Health

| Check | Result |
|---|---|
| Server reachable at `127.0.0.1:8188` | ✅ PASS |
| ComfyUI version | 0.36.0 |
| PyTorch version | 2.12.1 |
| MPS device present | ✅ Apple M5 |
| RAM total | 16 GB |
| RAM free at audit time | 5 GB |
| CLI `tracking_enabled` | ✅ `false` |

### ⚠️ Telemetry flag injected by Desktop

The running server contains `--feature-flag enable_telemetry=true` in its `argv`.
This is injected by the **ComfyUI Desktop app** and is separate from the CLI
`tracking_enabled: false` config. **Always launch from the terminal**, not the Desktop
UI, to avoid this. Documented in `README.md`.

Verification command:

```bash
curl -s http://127.0.0.1:8188/system_stats | python3 -c \
  "import json,sys; print([a for a in json.load(sys.stdin)['system']['argv'] if 'telemetry' in a])"
# Expected: []
```

---

## 2. Model Compatibility

| Model | Size | Dtypes | MPS Status |
|---|---|---|---|
| `background_removal/birefnet.safetensors` | 0.4 GB | I64, F16 | ✅ SAFE |
| `diffusion_models/z_image_turbo_bf16.safetensors` | 12.3 GB | BF16 | ⚠️ DTYPE_SAFE / MEMORY_RISK |
| `text_encoders/qwen_3_4b.safetensors` | 8.0 GB | BF16 | ⚠️ DTYPE_SAFE / MEMORY_RISK |
| `text_encoders/qwen_3_4b_fp8_mixed.safetensors` | 5.6 GB | **F8_E4M3**, BF16, F32, U8 | ❌ MPS_INCOMPATIBLE |
| `vae/ae.safetensors` | 0.3 GB | F32 | ✅ SAFE |

### Memory pressure analysis

| Scenario | Weight GB | Peak GB | Safe? |
|---|---|---|---|
| z_image + qwen_3_4b_full + vae + birefnet | 21.0 GB | ~27 GB | ❌ Severe swap |
| BiRefNet only (compositing pipeline) | 0.4 GB | ~0.5 GB | ✅ Safe |
| SD 1.5 fp16 + birefnet (recommended) | 2.4 GB | ~3.0 GB | ✅ Safe |

**Action:** `qwen_3_4b_fp8_mixed.safetensors` must not be loaded on MPS. Use the
MPS guard before any model-loading workflow:

```bash
python3 Comfy/scripts/mps_model_guard.py --check --budget-gb 12
```

---

## 3. OODA Governance Validation

| Contract | Schema | Source Ready | Blockers | Status |
|---|---|---|---|---|
| `br-commerce-2-higgsfield-comfy-ooda.json` | ✅ | ❌ | 6 | BLOCKED |
| `lh-commerce-2-higgsfield-comfy-ooda.json` | ✅ | ❌ | 4 | BLOCKED |
| `sig-commerce-1-higgsfield-comfy-ooda.json` | ✅ | ❌ (3 missing) | 2 | BLOCKED |
| `sig-commerce-2-higgsfield-comfy-ooda.json` | ✅ | ❌ (3 missing) | 3 | BLOCKED |
| `sig-commerce-3-higgsfield-comfy-ooda.json` | ✅ | ❌ (5 missing) | 4 | BLOCKED |
| `cinematic-urban-grit-ooda-task.json` | ❌ wrong schema | — | — | SCHEMA_ERROR |
| `lh-003-model-casting-higgsfield-ooda.json` | ❌ wrong schema | — | — | SCHEMA_ERROR |
| `lh-003-tryon-max-vto-ooda.json` | ❌ wrong schema | — | — | SCHEMA_ERROR |
| `scene-ooda-index.json` | ❌ (index, not scene) | — | — | NOT_A_SCENE |
| `scene-ooda-ledger.json` | ❌ (ledger, not scene) | — | — | NOT_A_SCENE |

Non-scene JSONs in `scene-contracts/` are correctly rejected by `load_manifest()`
(wrong schema). All 5 real OODA contracts are blocked by missing source files or
consumed paid attempts — no contract is ready for execution. This is **expected
and correct** — all blockers are documented in the contracts themselves.

---

## 4. Workflow Integrity

| Check | Result |
|---|---|
| `build_birefnet_segmentation_workflow` builds correctly | ✅ PASS |
| Empty filename guard raises `ValueError` | ✅ PASS |
| `build_lh_native_composite_workflow` rejects bad receipt | ✅ PASS (raises) |
| `analyze_birefnet_mask` normal mask | ✅ PASS |
| `analyze_birefnet_mask` degenerate (all zero) | ✅ PASS (BLOCKED) |
| `analyze_birefnet_mask` degenerate (all opaque) | ✅ PASS (BLOCKED) |
| `analyze_birefnet_mask` invalid SHA-256 | ✅ PASS (raises) |
| `analyze_birefnet_mask` empty bytes | ✅ PASS (raises) |
| `protected_rgb_modified` always False | ✅ PASS |
| `generative_use_allowed` always False | ✅ PASS |

**Test suite:** 66/66 passing (`.venv/bin/python -m pytest Comfy/tests/ -v`)

### Bug fixed

`test_paid_execution_needs_receipts_even_if_text_blockers_are_removed` was
failing because it loaded the real BR-COMMERCE-2 contract whose source files do
not exist on every machine, causing `source_ready: False` to cascade into
`configuration_ready: False`. Fixed by patching `verify_file` with
`monkeypatch` so the test stays focused on receipt-gate behaviour.

---

## 5. Architectural Gaps & Remediation

| Gap | Severity | Status |
|---|---|---|
| `qwen_3_4b_fp8_mixed` in model directory — MPS incompatible | 🔴 Critical | ⚠️ Documented — do not load |
| No working diffusion model for local correction passes | 🔴 Critical | Pending — download SD 1.5 fp16 |
| No upscale models | 🟠 High | Pending — download Real-ESRGAN 4x |
| Telemetry injected by Desktop launcher | 🟡 Medium | ✅ Documented in README + HARDENING |
| `CLIPSeg`, `ImageColorMatch+`, `ImageApplyLUT+` nodes unused | 🟡 Medium | Pending — wire into compositing workflow |
| No pytest in system Python — tests only run via `.venv` | 🟡 Medium | ✅ Documented — use `.venv/bin/python -m pytest` |
| `native_scene_workflows.py` imports fail under system Python | 🟡 Medium | ✅ Documented — use `.venv/bin/python` |
| Non-scene JSONs in `scene-contracts/` cause noisy validation | 🟢 Low | By design — schema check rejects them cleanly |

---

## Test runner reference

```bash
# All Comfy tests (correct interpreter)
.venv/bin/python -m pytest Comfy/tests/ -v

# MPS model guard
.venv/bin/python Comfy/scripts/mps_model_guard.py --check --budget-gb 12

# OODA validation (one contract)
python3 Comfy/scripts/scene_ooda.py validate \
  --manifest Comfy/scene-contracts/lh-commerce-2-higgsfield-comfy-ooda.json

# Telemetry check
curl -s http://127.0.0.1:8188/system_stats | python3 -c \
  "import json,sys; print([a for a in json.load(sys.stdin)['system']['argv'] if 'telemetry' in a])"
```
