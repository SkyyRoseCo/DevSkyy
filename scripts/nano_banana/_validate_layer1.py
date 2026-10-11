"""Layer 1 closed-loop validation — manual, paid-call validator.

NOT FOR CI. Run manually when validating the refinement-feedback wiring
end-to-end. Costs ~$0.65-$1.65 per run (2 tournaments + 1 Kontext
refinement). Leading-underscore filename signals "internal validator,
not a library script."

Hypothesis: the synthesis-aware refinement prompt should move the
br-001 candidate's score from ~45 (baseline with hallucination_veto)
toward 70+ on the post-refine tournament.

Result of the 2026-05-04 run: 45 → 90 (+45 pts, hallucination_veto
cleared). Full results JSON at tasks/layer1-validation-1777935127.json.

Flow:
1. Load per-judge env files + FAL_KEY
2. Run baseline tournament against the existing br-001 candidate
3. Build refinement prompt via _build_refinement_prompt() — Layer 1
4. Call refine_with_kontext (FAL Kontext) with that prompt
5. Save refined image to /tmp/br-001-refined.png
6. Run post-refine tournament against the refined image
7. Print before/after delta + per-axis breakdown

Real paid call. ~$0.65-$1.65 total ($0.30-$0.80 × 2 tournaments + ~$0.05
refinement).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))


def _load(p: Path) -> None:
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _build_clients() -> dict:
    """Build the three judge clients."""
    clients: dict = {}
    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI

        clients["openai"] = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    if os.environ.get("ANTHROPIC_API_KEY"):
        from anthropic import Anthropic

        clients["anthropic"] = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        from google import genai

        gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ["GEMINI_API_KEY"]
        clients["gemini"] = genai.Client(api_key=gemini_key)
    return clients


def _summarize(label: str, result) -> None:
    print(f"\n=== {label} ===")
    print(f"  aggregate_score:    {result.aggregate_score:.1f}/100")
    print(f"  vision_pair_mean:   {result.vision_pair_mean:.1f}/100")
    if result.synthesis_overall is not None:
        print(f"  synthesis_overall:  {result.synthesis_overall:.1f}/100")
    print(f"  passed_98:          {result.passed_98}")
    synth = result.synthesis_judge
    if synth:
        print(f"  hallucination_veto: {synth.hallucination_veto}")
        print(f"  vision_consensus:   {synth.vision_consensus}")
    for j in result.judges:
        print(
            f"    {j.judge:<32} overall={j.overall:>3}  "
            f"color={j.color_accuracy:>3}  logo={j.logo_accuracy:>3}  "
            f"hallucinations={j.no_hallucinations:>3}"
        )


def main() -> int:
    # Load env files
    for envf in (
        ".env.judge-gpt-vision",
        ".env.judge-gemini-vision",
        ".env.judge-opus-thinking",
        ".env.hf",  # FAL_KEY lives here
    ):
        _load(REPO / envf)

    needed = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "FAL_KEY"]
    missing = [k for k in needed if not os.environ.get(k)]
    if missing:
        print(f"ERROR: missing keys: {missing}", file=sys.stderr)
        return 1
    print("All required keys loaded.\n")

    # Load files
    from skyyrose.core.paths import WP_PRODUCTS_DIR

    products = WP_PRODUCTS_DIR
    source_path = products / "black-rose-crewneck-techflat-v4.jpg"
    candidate_path = products / "br-001-crewneck.png"
    refined_path = Path(
        "/tmp/br-001-refined.png"
    )  # nosec B108 — validation script, ephemeral output

    for label, p in (("source", source_path), ("baseline candidate", candidate_path)):
        if not p.exists():
            print(f"ERROR: {label} missing: {p}", file=sys.stderr)
            return 1
        print(f"  {label}: {p.name} ({p.stat().st_size:,} bytes)")
    print()

    # Load from canonical dossier — ad-hoc DNA omits per-element trim
    # color and the negative list, which judges need to score correctly.
    from nano_banana.spec_builder import build_dna_from_sku

    dna = build_dna_from_sku("br-001")
    print(f"Spec source: canonical dossier ({len(dna['spec']):,}c spec text)")
    print(f"  product: {dna.get('name')} ({dna.get('sku')})\n")

    # Build clients
    clients = _build_clients()
    print(f"Configured judges: {sorted(clients.keys())}\n")

    from nano_banana.engine_fal import refine_with_kontext
    from nano_banana.pipeline import _build_refinement_prompt
    from nano_banana.tournament import run_tournament

    # ── Stage 1: BASELINE tournament ─────────────────────────────────────
    print("=" * 70)
    print("STAGE 1: Baseline tournament against existing br-001-crewneck.png")
    print("=" * 70)
    t0 = time.monotonic()
    baseline = run_tournament(clients, source_path, candidate_path, dna)
    print(f"  elapsed: {time.monotonic() - t0:.1f}s")
    _summarize("BASELINE", baseline)

    # ── Stage 2: Build the synthesis-aware refinement prompt ─────────────
    print("\n" + "=" * 70)
    print("STAGE 2: Synthesis-aware refinement prompt (Layer 1)")
    print("=" * 70)
    refine_prompt = _build_refinement_prompt("Black Rose Crewneck", "br-001", baseline)
    print(refine_prompt)

    # ── Stage 3: Refine via FAL Kontext ──────────────────────────────────
    print("\n" + "=" * 70)
    print("STAGE 3: FAL Kontext refinement")
    print("=" * 70)
    t1 = time.monotonic()
    refined_bytes = refine_with_kontext(candidate_path, refine_prompt)
    print(f"  elapsed: {time.monotonic() - t1:.1f}s")
    if not refined_bytes:
        print("ERROR: Kontext returned no bytes. Aborting.", file=sys.stderr)
        return 2
    refined_path.write_bytes(refined_bytes)
    print(f"  refined image: {refined_path} ({len(refined_bytes):,} bytes)")

    # ── Stage 4: POST-REFINE tournament ──────────────────────────────────
    print("\n" + "=" * 70)
    print("STAGE 4: Post-refine tournament against refined image")
    print("=" * 70)
    t2 = time.monotonic()
    post_refine = run_tournament(clients, source_path, refined_path, dna)
    print(f"  elapsed: {time.monotonic() - t2:.1f}s")
    _summarize("POST-REFINE", post_refine)

    # ── Stage 5: Delta ───────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("STAGE 5: Layer 1 validation — delta")
    print("=" * 70)

    delta = post_refine.aggregate_score - baseline.aggregate_score
    sign = "+" if delta >= 0 else ""
    print(
        f"  Aggregate score:   {baseline.aggregate_score:>5.1f} → {post_refine.aggregate_score:>5.1f}   ({sign}{delta:.1f})"
    )
    print(
        f"  Vision-pair mean:  {baseline.vision_pair_mean:>5.1f} → {post_refine.vision_pair_mean:>5.1f}"
    )
    if baseline.synthesis_overall is not None and post_refine.synthesis_overall is not None:
        s_delta = post_refine.synthesis_overall - baseline.synthesis_overall
        s_sign = "+" if s_delta >= 0 else ""
        print(
            f"  Synthesis overall: {baseline.synthesis_overall:>5.1f} → {post_refine.synthesis_overall:>5.1f}   ({s_sign}{s_delta:.1f})"
        )

    base_synth = baseline.synthesis_judge
    post_synth = post_refine.synthesis_judge
    if base_synth and post_synth:
        veto_changed = base_synth.hallucination_veto != post_synth.hallucination_veto
        print(
            f"  Hallucination veto: {base_synth.hallucination_veto} → "
            f"{post_synth.hallucination_veto}"
            f"   {'(CLEARED)' if (base_synth.hallucination_veto and not post_synth.hallucination_veto) else '(unchanged)' if not veto_changed else '(WORSE)'}"
        )

    print()
    print(f"VERDICT: {'PASS' if delta >= 20 else 'PARTIAL' if delta >= 5 else 'NO LIFT'}")
    print(f"  Layer 1 hypothesis: 30-60 pt lift on first refine. Observed: {delta:+.1f} pts.")

    # Save full results JSON for post-mortem
    out = REPO / "tasks" / f"layer1-validation-{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "baseline": baseline.to_dict(),
                "refine_prompt": refine_prompt,
                "post_refine": post_refine.to_dict(),
                "delta_aggregate": delta,
            },
            indent=2,
        )
    )
    print(f"\n  Full results saved: {out.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
