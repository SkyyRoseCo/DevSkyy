# pipeline3d — Unified 3D Pipeline Orchestrator (Phase 1)

Provider-agnostic staged 3D pipeline cloning the Tripo3D/Meshy workflow shape:
`image-to-3D → texture → remesh → export-GLB`. Phase 1 ships the Tripo vertical
slice driven by a CLI.

## Quick start

```bash
# Dry run (estimate only, no dispatch):
python -m skyyrose.elite_studio.pipeline3d --sku br-001 \
  --stages image-to-3d,texture,remesh,export

# Paid dispatch (STOP-AND-SHOW gate; needs TRIPO_API_KEY):
python -m skyyrose.elite_studio.pipeline3d --sku br-001 \
  --stages image-to-3d,texture,remesh,export --go
```

## Architecture

| Module                  | Role                                                                                   |
| ----------------------- | -------------------------------------------------------------------------------------- |
| `models`                | immutable data types; `Artifact` is the chaining handle (task_id + path)               |
| `router`                | picks an adapter per stage by capability/priority/availability + fallback              |
| `executor`              | runs stages in order; budget gate; telemetry; idempotent resume; chaining              |
| `estimator`             | one whole-job cost estimate, shown before dispatch                                     |
| `store`                 | file-based stage-level idempotency (resume skips completed stages)                     |
| `adapters/tripo`        | image-to-3D / texture / remesh via the tripo3d SDK                                     |
| `adapters/local_export` | EXPORT stage — copies final GLB to `<output>/<sku>.glb`                                |
| `preflight`             | resolves the canonical source image + guards against missing source                    |
| `glb_container`         | lossless GLB I/O — rewrites only the JSON chunk, fails closed on a malformed container |
| `glb_materials`         | fabric class from the founder's prose → `KHR_materials_sheen` (anisotropy opt-in)      |
| `glb_optimize`          | `gltfpack -cc -tc` + the ≤3 MB web delivery gate                                       |
| `webgl_qc`              | renders a web GLB in the **production** three.js viewer and pixel-diffs variants       |

### Web delivery + QC

`glb_materials → glb_optimize → webgl_qc` is the path a garment takes from a raw
provider GLB to something the PDP serves. `webgl_qc` exists because a material
change can only be judged in the engine that will ship it: it mirrors
`product-3d-viewer.js` (a parity test fails when that viewer drifts), renders at
a camera derived from the bounding box so two variants differ only by their GLB,
and reports VOID — distinct from "no visible difference" — when a change
produced no pixels at all. CLI: `scripts/glb_qc_render.py`.

Execution spine: **synchronous-within-stage** (the adapter polls to completion).
Cross-provider chaining: same provider → pass `task_id`; different provider →
hand off the downloadable `model_url`/path.

## Roadmap

- **Phase 2:** Meshy + TRELLIS adapters, router fallback across providers,
  batch.
- **Phase 3:** REST API + Redis async worker, inbound webhook + HMAC, outbound
  events.

See `docs/superpowers/specs/2026-06-02-pipeline3d-orchestrator-design.html`.
