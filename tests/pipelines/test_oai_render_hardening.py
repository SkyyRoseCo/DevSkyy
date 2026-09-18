"""Unit tests for the oai_render hallucination-hardening layer.

Covers: injected-text sanitization, anti-collage prompt guardrails,
deterministic QC checks (decode / dimensions / collage bands), runtime
spend tracking, and the judged retry / quarantine loop in render_sku.
No network calls — the OpenAI client and QC judge are faked.
"""

from __future__ import annotations

import hashlib
import io
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from scripts.oai_render import config
from scripts.oai_render import pipeline as pipeline_mod
from scripts.oai_render import prompt as prompt_mod
from scripts.oai_render import qc
from scripts.oai_render.client import ImageCallResult
from scripts.oai_render.cost import SpendTracker
from scripts.oai_render.pipeline import SkuPlan, render_sku
from scripts.oai_render.prompt import (
    NEGATIVE_GUARDRAILS,
    PAIR_NEGATIVE_GUARDRAILS,
    build_pair_prompt,
    build_prompt,
    read_dossier,
    sanitize_injected_text,
    sanitize_name,
)
from scripts.oai_render.references import ReferenceImage
from scripts.oai_render.runlog import RunLog, load_events

# ── Sanitizer ────────────────────────────────────────────────────────────────


def test_sanitizer_drops_view_enumeration_lines():
    text = (
        "## Construction\n"
        "Heavyweight 400gsm cotton fleece, ribbed cuffs.\n"
        "Front view shows the chest rose; back view shows the script.\n"
        "Double-needle stitching throughout."
    )
    out = sanitize_injected_text(text, source="test")
    assert "Front view" not in out
    assert "back view" not in out
    assert "Heavyweight 400gsm" in out
    assert "Double-needle" in out
    assert "## Construction" in out  # headings survive


def test_sanitizer_keeps_single_view_mention_and_colorway_facts():
    # Placement spec with ONE view mention and colorway construction facts are
    # legitimate dossier fidelity content — they must survive sanitization.
    text = (
        "Rose graphic sits on the LEFT thigh of the front view only.\n"
        "Embossed colorway — reduced 3-color palette of BLACK + WHITE + GREY.\n"
        "Front view shows the rose; back view shows the script; side view plain."
    )
    out = sanitize_injected_text(text, source="test")
    assert "LEFT thigh of the front view only" in out
    assert "Embossed colorway" in out
    assert "side view plain" not in out  # enumeration line (3 view mentions) dropped


def test_sanitizer_drops_availability_and_styling_lines():
    text = "Also available in crimson.\nPairs well when styled with the joggers.\nSilk lining."
    out = sanitize_injected_text(text, source="test")
    assert out == "Silk lining."


def test_sanitize_name_strips_triggers_and_flattens():
    assert sanitize_name("Black  Rose\nHoodie") == "Black Rose Hoodie"
    cleaned = sanitize_name("Bay Tee — available in white")
    assert "available in" not in cleaned
    assert cleaned.startswith("Bay Tee")


def test_read_dossier_sanitizes_and_caps(tmp_path: Path):
    dossier = tmp_path / "br-001.md"
    dossier.write_text(
        "---\nsku: br-001\n---\n"
        "## Construction\nFleece crewneck, embroidered rose.\n"
        "## Scene direction\nfront view, back view, three-quarter angles.\n"
        "## Materials\nShown from multiple angles in the lookbook.\nCotton-poly blend.\n",
        encoding="utf-8",
    )
    body = read_dossier(dossier)
    assert body is not None
    assert "Scene direction" not in body  # section strip
    assert "multiple angles" not in body  # line sanitizer
    assert "Fleece crewneck" in body
    assert "Cotton-poly blend" in body


# ── Prompt guardrails ────────────────────────────────────────────────────────


def test_guardrails_carry_anti_collage_enforcement():
    for block in (NEGATIVE_GUARDRAILS, PAIR_NEGATIVE_GUARDRAILS):
        assert "single full-bleed photograph" in block
        assert "No collage" in block


def test_build_prompt_sanitizes_name_and_indexes_references():
    p = build_prompt(
        name="Rose Tee — available in white",
        sku="sg-001",
        collection="signature",
        reference_labels=["REFERENCE IMAGE 1 — GARMENT TECH FLAT"],
        dossier_text=None,
        is_patch=False,
        style="ghost",
        view="front",
    )
    assert "available in" not in p.split("\n")[2]  # PRODUCT line is clean
    assert '"image 1" is the first' in p


def test_pair_prompt_assigns_body_zones_and_requires_both():
    p = build_pair_prompt(
        pair_label="br-001 + br-002",
        collection="black-rose",
        garments=[
            {
                "name": "Crewneck",
                "sku": "br-001",
                "reference_labels": [],
                "dossier_text": None,
                "is_patch": False,
            },
            {
                "name": "Joggers",
                "sku": "br-002",
                "reference_labels": [],
                "dossier_text": None,
                "is_patch": False,
            },
        ],
    )
    assert "upper body/torso" in p
    assert "lower body/legs" in p
    assert "BOTH garments MUST be visible" in p


# ── Deterministic QC checks ──────────────────────────────────────────────────


def _png_bytes(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


def _noise_render() -> np.ndarray:
    """A 'good' render: textured content crossing the central band everywhere."""
    w, h = config.EXPECTED_RENDER_SIZE
    rng = np.random.default_rng(7)
    return rng.integers(0, 255, size=(h, w, 3), dtype=np.uint8)


def test_deterministic_pass_on_clean_render():
    assert qc.deterministic_checks(_png_bytes(_noise_render())) == []


def test_deterministic_flags_invalid_bytes():
    assert qc.deterministic_checks(b"not a png") == ["invalid_image"]


def test_deterministic_flags_wrong_dimensions():
    arr = np.random.default_rng(7).integers(0, 255, size=(512, 512, 3), dtype=np.uint8)
    assert "wrong_dimensions" in qc.deterministic_checks(_png_bytes(arr))


def test_deterministic_flags_horizontal_collage_gutter():
    arr = _noise_render()
    mid = arr.shape[0] // 2
    arr[mid - 3 : mid + 3, :, :] = 255  # uniform full-width band through the center
    assert "collage_panels" in qc.deterministic_checks(_png_bytes(arr))


def test_deterministic_flags_vertical_collage_gutter():
    arr = _noise_render()
    mid = arr.shape[1] // 2
    arr[:, mid - 3 : mid + 3, :] = 250
    assert "collage_panels" in qc.deterministic_checks(_png_bytes(arr))


# ── Spend tracker ────────────────────────────────────────────────────────────


def test_spend_tracker_enforces_cap():
    t = SpendTracker(cap_usd=1.0)
    assert t.can_afford(0.40)
    t.add(0.40)
    t.add(0.40)
    assert not t.can_afford(0.40)
    assert t.remaining_usd == pytest.approx(0.20)


# ── render_sku judged retry loop ─────────────────────────────────────────────


class _FakeClient:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.calls = 0
        self.prompts: list[str] = []

    def edit_with_metadata(
        self,
        *,
        prompt: str,
        image_paths: list[Path],
        expected_input_sha256s: tuple[str, ...] | None = None,
    ) -> ImageCallResult:
        self.calls += 1
        self.prompts.append(prompt)
        input_hashes = expected_input_sha256s or tuple(
            hashlib.sha256(str(path).encode("utf-8")).hexdigest() for path in image_paths
        )
        prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        parameters: dict[str, object] = {
            "model": "gpt-image-2-2026-04-21",
            "quality": "high",
            "size": "1024x1536",
            "output_format": "png",
            "background": "auto",
            "n": 1,
        }
        contract: dict[str, object] = {
            "contract_id": "skyyrose-product-image-candidate-v1",
            "authority_state": "CANDIDATE_ONLY",
            "operation": "product_image_candidate",
            "provider": "openai",
            "api_surface": "images",
            "endpoint": "/v1/images/edits",
            "requested_model": "gpt-image-2-2026-04-21",
            "prompt_sha256": prompt_sha256,
            "request_image_sha256s": list(input_hashes),
            "mask_sha256": None,
            "request_parameters": parameters,
            "release_authority": False,
        }
        contract_sha256 = hashlib.sha256(
            json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return ImageCallResult(
            data=self.payload,
            request_id=f"req_fake_{self.calls}",
            requested_model="gpt-image-2-2026-04-21",
            sdk_version="test",
            endpoint="/v1/images/edits",
            request_parameters=parameters,
            ordered_input_sha256s=input_hashes,
            mask_sha256=None,
            prompt_sha256=prompt_sha256,
            job_contract=contract,
            contract_sha256=contract_sha256,
        )


class _ScriptedGate:
    """QC gate double whose verdicts (and optional per-attempt failure tags) are scripted."""

    def __init__(self, verdicts: list[bool], tags: list[tuple[str, ...]] | None = None):
        self._verdicts = verdicts
        self._tags = tags
        self.calls = 0

    def check(self, data: bytes, exp) -> qc.QCVerdict:
        passed = self._verdicts[min(self.calls, len(self._verdicts) - 1)]
        tag = ("collage_panels",)
        if self._tags is not None:
            tag = self._tags[min(self.calls, len(self._tags) - 1)]
        self.calls += 1
        if passed:
            return qc.QCVerdict(passed=True, reason="pass")
        return qc.QCVerdict(passed=False, failure_tags=tag, reason="scripted fail")


@pytest.fixture()
def _tmp_output(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path / "oai")
    monkeypatch.setattr(config, "REJECTED_DIR", tmp_path / "oai" / "_rejected")
    return tmp_path


def _plan() -> SkuPlan:
    return SkuPlan(
        sku="br-001",
        name="Black Rose Crewneck",
        collection="black-rose",
        output_slug="black-rose-crewneck",
        references=[ReferenceImage(label="ref 1", path=Path(__file__), kind="garment")],
        prompt="prompt",
    )


def test_render_sku_accepts_on_retry_after_qc_fail(_tmp_output):
    client = _FakeClient(b"png-bytes")
    gate = _ScriptedGate([False, True])
    result = render_sku(_plan(), client, gate=gate, spend=SpendTracker())
    assert result.status == "rendered"
    assert client.calls == 2
    rejected = list((config.REJECTED_DIR / "black-rose-crewneck").glob("*.png"))
    assert len(rejected) == 1  # first attempt quarantined


def test_render_sku_quarantines_after_exhausting_retries(_tmp_output):
    client = _FakeClient(b"png-bytes")
    # DISTINCT failure each attempt → no early-abort → genuinely exhausts every retry.
    gate = _ScriptedGate([False], tags=[("collage_panels",), ("wrong_view",), ("flat_render",)])
    result = render_sku(_plan(), client, gate=gate, spend=SpendTracker())
    assert result.status == "qc_failed"
    assert client.calls == 1 + config.QC_MAX_RENDER_RETRIES
    qdir = config.REJECTED_DIR / "black-rose-crewneck"
    assert len(list(qdir.glob("*.png"))) == client.calls
    meta = json.loads(sorted(qdir.glob("*.json"))[0].read_text())
    assert meta["failure_tags"] == ["collage_panels"]
    # accepted output was never written
    assert not (config.OUTPUT_DIR / "black-rose-crewneck" / "ghost.png").exists()


def test_render_sku_early_aborts_on_repeated_identical_failure(_tmp_output):
    """Same QC failure twice running → abort before burning the final retry (saves spend)."""
    client = _FakeClient(b"png-bytes")
    gate = _ScriptedGate([False])  # identical tag (collage_panels) every attempt
    result = render_sku(_plan(), client, gate=gate, spend=SpendTracker())
    assert result.status == "qc_failed"
    # 2 renders, NOT 1 + QC_MAX_RENDER_RETRIES — the 3rd identical-failure render is saved.
    assert client.calls == 2


def test_render_sku_feeds_qc_reason_into_retry(_tmp_output):
    """The retry prompt carries the prior rejection's reason — not a blind replay."""
    client = _FakeClient(b"png-bytes")
    gate = _ScriptedGate([False, True])
    result = render_sku(_plan(), client, gate=gate, spend=SpendTracker())
    assert result.status == "rendered"
    assert client.calls == 2
    assert client.prompts[0] == "prompt"  # first attempt = unmodified plan prompt
    assert "PREVIOUS ATTEMPT REJECTED" in client.prompts[1]
    assert "scripted fail" in client.prompts[1]  # the judge's reason fed back in


def test_render_sku_stops_when_budget_exhausted(_tmp_output):
    client = _FakeClient(b"png-bytes")
    spend = SpendTracker(cap_usd=0.10)  # cannot afford even one render
    result = render_sku(_plan(), client, gate=None, spend=spend)
    assert result.status == "error"
    assert "budget" in result.reason
    assert client.calls == 0


def test_render_sku_no_gate_accepts_first_render(_tmp_output):
    client = _FakeClient(b"png-bytes")
    result = render_sku(_plan(), client, gate=None, spend=SpendTracker())
    assert result.status == "rendered"
    assert client.calls == 1
    assert result.output_path is not None and result.output_path.exists()


def test_render_sku_writes_hash_bound_candidate_receipt(_tmp_output, tmp_path: Path):
    ref = tmp_path / "reference.png"
    ref.write_bytes(b"physical-source-bytes")
    plan = _plan()
    plan.references = [ReferenceImage(label="physical front", path=ref, kind="garment")]

    class _MetadataClient:
        def edit_with_metadata(
            self,
            *,
            prompt: str,
            image_paths: list[Path],
            expected_input_sha256s: tuple[str, ...] | None = None,
        ):
            prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            input_hashes = expected_input_sha256s or (
                "0f42fe3ccdc71744b95003efaf209de0fa1b3982aded905d04d42e418290c0e2",
            )
            parameters: dict[str, object] = {
                "model": "gpt-image-2-2026-04-21",
                "quality": "high",
                "size": "1024x1536",
                "output_format": "png",
                "background": "auto",
                "n": 1,
            }
            contract: dict[str, object] = {
                "contract_id": "skyyrose-product-image-candidate-v1",
                "authority_state": "CANDIDATE_ONLY",
                "operation": "product_image_candidate",
                "provider": "openai",
                "api_surface": "images",
                "endpoint": "/v1/images/edits",
                "requested_model": "gpt-image-2-2026-04-21",
                "release_authority": False,
                "prompt_sha256": prompt_sha256,
                "request_image_sha256s": list(input_hashes),
                "mask_sha256": None,
                "request_parameters": parameters,
            }
            return ImageCallResult(
                data=b"generated-candidate",
                request_id="req_receipt_123",
                requested_model="gpt-image-2-2026-04-21",
                sdk_version="2.23.0",
                endpoint="/v1/images/edits",
                request_parameters=parameters,
                ordered_input_sha256s=input_hashes,
                mask_sha256=None,
                prompt_sha256=prompt_sha256,
                job_contract=contract,
                contract_sha256=hashlib.sha256(
                    json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
            )

    result = render_sku(plan, _MetadataClient(), gate=None, spend=SpendTracker())

    assert result.status == "rendered"
    assert result.receipt_path is not None and result.receipt_path.exists()
    receipt = json.loads(result.receipt_path.read_text(encoding="utf-8"))
    assert receipt["authority_state"] == "CANDIDATE_ONLY"
    assert receipt["contract"]["release_authority"] is False
    assert receipt["contract_sha256"]
    assert receipt["x_request_id"] == "req_receipt_123"
    assert receipt["requested_model"] == "gpt-image-2-2026-04-21"
    assert receipt["ordered_inputs"][0]["sha256"] == (
        "0f42fe3ccdc71744b95003efaf209de0fa1b3982aded905d04d42e418290c0e2"
    )
    assert receipt["output"]["sha256"] == (
        "859b51b2664361deeb1beb449774d587932af5c8ca27ae74134f38b1fbac9da1"
    )
    assert receipt["output_sha256"] == receipt["output"]["sha256"]
    assert receipt["request_image_sha256s"] == [receipt["input_sha256"]]
    assert receipt["mask_path"] is None
    assert receipt["mask_sha256"] is None
    serialized = json.dumps(receipt)
    assert "OPENAI_API_KEY" not in serialized
    assert "sk-proj" not in serialized


def test_render_sku_rejects_legacy_client_before_call(_tmp_output):
    class _LegacyClient:
        calls = 0

        def edit(self, *, prompt: str, image_paths: list[Path]):
            self.calls += 1
            return b"unreceipted"

    client = _LegacyClient()
    result = render_sku(_plan(), client, gate=None, spend=SpendTracker())

    assert result.status == "error"
    assert "evidence_required" in result.reason
    assert client.calls == 0


def test_render_sku_reruns_publish_request_unique_candidates(_tmp_output):
    client = _FakeClient(b"candidate")

    first = render_sku(_plan(), client, gate=None, spend=SpendTracker())
    second = render_sku(_plan(), client, gate=None, spend=SpendTracker())

    assert first.status == second.status == "rendered"
    assert first.output_path != second.output_path
    assert first.output_path is not None and first.output_path.exists()
    assert second.output_path is not None and second.output_path.exists()
    assert ".candidate.req_fake_" in first.output_path.name


@pytest.mark.parametrize(
    "tamper",
    ["model", "endpoint", "parameters", "release_authority", "input_hashes", "mask"],
)
def test_receipt_rejects_self_consistent_contract_contradictions(_tmp_output, tamper):
    base = _FakeClient(b"candidate")

    class _TamperedClient:
        def edit_with_metadata(
            self,
            *,
            prompt: str,
            image_paths: list[Path],
            expected_input_sha256s: tuple[str, ...] | None = None,
        ):
            result = base.edit_with_metadata(
                prompt=prompt,
                image_paths=image_paths,
                expected_input_sha256s=expected_input_sha256s,
            )
            changes = {}
            contract = dict(result.job_contract)
            if tamper == "model":
                changes["requested_model"] = "gpt-image-2"
                contract["requested_model"] = "gpt-image-2"
            elif tamper == "endpoint":
                changes["endpoint"] = "/v1/responses"
                contract["endpoint"] = "/v1/responses"
            elif tamper == "parameters":
                parameters = {**result.request_parameters, "quality": "low"}
                changes["request_parameters"] = parameters
                contract["request_parameters"] = parameters
            elif tamper == "release_authority":
                contract["release_authority"] = True
            elif tamper == "input_hashes":
                hashes = ("0" * 64,)
                changes["ordered_input_sha256s"] = hashes
                contract["request_image_sha256s"] = list(hashes)
            else:
                changes["mask_sha256"] = "f" * 64
                contract["mask_sha256"] = "f" * 64
            changes["job_contract"] = contract
            changes["contract_sha256"] = hashlib.sha256(
                json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            return replace(result, **changes)

    result = render_sku(_plan(), _TamperedClient(), gate=None, spend=SpendTracker())

    assert result.status == "error"
    assert any(term in result.reason for term in ("provider", "contract", "mask"))


def test_rejected_attempt_persistence_failure_stops_paid_retries(
    _tmp_output, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    client = _FakeClient(b"candidate")
    gate = _ScriptedGate([False])
    runlog = RunLog(path=tmp_path / "failure.jsonl")

    def _fail(*_args, **_kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(pipeline_mod, "_write_generation_receipt", _fail)
    result = render_sku(_plan(), client, gate=gate, spend=SpendTracker(), runlog=runlog)

    assert result.status == "error"
    assert client.calls == 1
    events = load_events(runlog.path)
    assert "evidence_error" in [event["event"] for event in events]
    assert "quarantined" not in [event["event"] for event in events]


# ── Q-unavail: judge-infra failure → mandatory human review, never auto-ship ──


class _UnavailableGate:
    """QC gate double reporting the judge was unavailable (Q-unavail)."""

    def __init__(self) -> None:
        self.calls = 0

    def check(self, data: bytes, exp) -> qc.QCVerdict:
        self.calls += 1
        return qc.QCVerdict(
            passed=False,
            needs_review=True,
            failure_tags=("judge_unavailable",),
            reason="judge error: TimeoutError: backend down",
        )


def test_qc_check_judge_unavailable_routes_to_review(monkeypatch):
    """A judge exception during check() must yield a needs_review verdict (NOT pass)."""
    monkeypatch.setattr(config, "QC_ENABLED", True)

    def _boom(_req):
        raise TimeoutError("judge backend down")

    gate = qc.QCGate(judge_fn=_boom)
    exp = qc.RenderExpectation(
        sku="br-001",
        name="Black Rose Crewneck",
        style="ghost",
        view="front",
        is_pair=False,
        is_patch=False,
    )
    verdict = gate.check(_png_bytes(_noise_render()), exp)
    assert verdict.needs_review is True
    assert verdict.passed is False
    assert "judge_unavailable" in verdict.failure_tags


@pytest.mark.parametrize(
    "malformed",
    [
        {},
        {"garment_matches_reference": "false"},
        {
            "visual_analysis": "looks wrong",
            "is_single_photograph": True,
            "garment_matches_reference": True,
            "view_correct": True,
            "branding_legible_and_correct": True,
            "photorealistic_not_flat": True,
            "all_garments_present": True,
            "authority_consistent": True,
            "reason": "pass",
            "unexpected": True,
        },
    ],
)
def test_qc_malformed_judge_verdict_fails_closed(malformed):
    gate = qc.QCGate(judge_fn=lambda _req: (malformed, 0.01))
    verdict = gate.check(
        _png_bytes(_noise_render()),
        qc.RenderExpectation(
            sku="br-001",
            name="Black Rose Crewneck",
            style="ghost",
            view="front",
            is_pair=False,
            is_patch=False,
        ),
    )

    assert verdict.passed is False
    assert verdict.needs_review is True
    assert verdict.failure_tags == ("malformed_judge_verdict",)


def test_qc_authority_conflict_routes_to_review_without_retry():
    raw = {
        "visual_analysis": "dossier says white drawstring; real garment photo shows black",
        "is_single_photograph": True,
        "garment_matches_reference": True,
        "view_correct": True,
        "branding_legible_and_correct": True,
        "photorealistic_not_flat": True,
        "all_garments_present": True,
        "authority_consistent": False,
        "reason": "dossier and photo conflict on drawstring color",
    }
    gate = qc.QCGate(judge_fn=lambda _req: (raw, 0.01))
    verdict = gate.check(
        _png_bytes(_noise_render()),
        qc.RenderExpectation(
            sku="br-002",
            name="BLACK Rose Joggers",
            style="ghost",
            view="front",
            is_pair=False,
            is_patch=True,
            dossier_spec="The drawstring is WHITE.",
        ),
    )

    assert verdict.passed is False
    assert verdict.needs_review is True
    assert verdict.failure_tags == ("authority_conflict",)


def test_judge_api_retries_one_transient_failure(monkeypatch: pytest.MonkeyPatch):
    gate = qc.QCGate(use_judge=False)
    calls = 0

    class _TransientError(Exception):
        status_code = 429

    def _send():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise _TransientError("rate limited")
        return "ok"

    monkeypatch.setattr(qc.time, "sleep", lambda _delay: None)

    assert gate._call_judge_api(_send) == "ok"
    assert calls == 2
    assert gate._last_judge_attempts == 2


def test_judge_api_does_not_retry_non_transient_failure(monkeypatch: pytest.MonkeyPatch):
    gate = qc.QCGate(use_judge=False)
    calls = 0

    class _InvalidRequestError(Exception):
        status_code = 400

    def _send():
        nonlocal calls
        calls += 1
        raise _InvalidRequestError("invalid schema")

    monkeypatch.setattr(qc.time, "sleep", lambda _delay: None)

    with pytest.raises(_InvalidRequestError):
        gate._call_judge_api(_send)
    assert calls == 1
    assert gate._last_judge_attempts == 1


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_judge_clients_disable_hidden_sdk_retries(provider: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "QC_JUDGE_PROVIDER", provider)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-abc")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-abc")

    gate = qc.QCGate()

    assert gate._client.max_retries == 0


def test_render_sku_needs_review_quarantines_without_retry(_tmp_output):
    """judge_unavailable: quarantine for human sign-off, no paid retry, never shipped."""
    client = _FakeClient(b"png-bytes")
    gate = _UnavailableGate()
    result = render_sku(_plan(), client, gate=gate, spend=SpendTracker())

    assert result.status == "needs_review"
    assert client.calls == 1  # judge being down can't be fixed by re-rendering — no retry
    assert gate.calls == 1

    qdir = config.REJECTED_DIR / "black-rose-crewneck"
    pngs = list(qdir.glob("*.png"))
    assert len(pngs) == 1  # the render bytes are held for mandatory human review
    meta = json.loads(sorted(qdir.glob("*.json"))[0].read_text())
    assert meta["failure_tags"] == ["judge_unavailable"]

    # never accepted/shipped to the output tree
    assert not (config.OUTPUT_DIR / "black-rose-crewneck" / "ghost.png").exists()


# ── Founder review corrections (registry products[sku].corrections) ─────────
def _write_corrections(tmp_path: Path, monkeypatch, corrections: dict) -> None:
    registry = {
        "products": {
            sku: {
                "catalog": {"sku": sku},
                "corrections": [
                    {"text": line, "authority": "FOUNDER_VERBATIM", "captured": "2026-06-09"}
                    for line in lines
                ],
            }
            for sku, lines in corrections.items()
        }
    }
    path = tmp_path / "logo-registry.json"
    path.write_text(json.dumps(registry))
    monkeypatch.setattr("skyyrose.core.product_registry.PRODUCT_REGISTRY", path)


def test_founder_corrections_injected_verbatim(tmp_path: Path, monkeypatch):
    _write_corrections(
        tmp_path, monkeypatch, {"sg-007": ["[ghost] logo Is a patch not directly on beanie"]}
    )
    p = build_prompt(
        name="The Signature Beanie",
        sku="sg-007",
        collection="signature",
        reference_labels=[],
        dossier_text=None,
        is_patch=False,
        style="ghost",
        view="front",
    )
    assert "FOUNDER CORRECTIONS" in p
    assert "logo Is a patch not directly on beanie" in p


def test_no_corrections_block_when_sku_has_none(tmp_path: Path, monkeypatch):
    _write_corrections(tmp_path, monkeypatch, {"sg-007": ["[ghost] note"]})
    p = build_prompt(
        name="Other Product",
        sku="br-001",
        collection="black-rose",
        reference_labels=[],
        dossier_text=None,
        is_patch=False,
        style="ghost",
        view="front",
    )
    assert "FOUNDER CORRECTIONS" not in p


def test_agent_added_corrections_never_appear_as_founder_words(tmp_path: Path, monkeypatch):
    # Only the founder's own review comments may sit under the FOUNDER CORRECTIONS
    # header, which tells the model the founder wrote them and that they override
    # the spec. Agent-added lines go in their own section, subordinate to the spec.
    registry = {
        "products": {
            "br-004": {
                "catalog": {"sku": "br-004"},
                "corrections": [
                    {
                        "text": "[ghost] founder line",
                        "authority": "FOUNDER_VERBATIM",
                        "captured": "2026-06-09",
                    },
                    {
                        "text": "[ghost] agent line",
                        "authority": "AGENT_ADDED",
                        "captured": "2026-06-12",
                    },
                ],
            }
        }
    }
    path = tmp_path / "logo-registry.json"
    path.write_text(json.dumps(registry))
    monkeypatch.setattr("skyyrose.core.product_registry.PRODUCT_REGISTRY", path)
    p = build_prompt(
        name="BLACK Rose Hoodie",
        sku="br-004",
        collection="black-rose",
        reference_labels=[],
        dossier_text=None,
        is_patch=False,
        style="ghost",
        view="front",
    )
    founder_at = p.index("FOUNDER CORRECTIONS")
    agent_at = p.index("AGENT-ADDED RENDER CONSTRAINTS")
    founder_block = p[founder_at:agent_at] if founder_at < agent_at else p[founder_at:]
    agent_block = p[agent_at:founder_at] if agent_at < founder_at else p[agent_at:]
    assert "founder line" in founder_block and "agent line" not in founder_block
    assert "agent line" in agent_block and "founder line" not in agent_block


def test_live_br004_agent_lines_are_not_labelled_founder():
    p = build_prompt(
        name="BLACK Rose Hoodie",
        sku="br-004",
        collection="black-rose",
        reference_labels=[],
        dossier_text=None,
        is_patch=False,
        style="ghost",
        view="front",
    )
    # br-004's only two corrections were added by an agent on 2026-06-12.
    assert "FOUNDER CORRECTIONS" not in p
    assert "AGENT-ADDED RENDER CONSTRAINTS" in p
    assert "rose-cluster logo is a cluster of MULTIPLE" in p


def test_corrections_missing_registry_fails_closed(tmp_path: Path, monkeypatch):
    # Rendering without the product's corrections would repeat a render the
    # founder already rejected, so an absent registry must stop the prompt build.
    monkeypatch.setattr("skyyrose.core.product_registry.PRODUCT_REGISTRY", tmp_path / "absent.json")
    with pytest.raises(FileNotFoundError):
        prompt_mod.corrections_for("sg-007")


def test_live_registry_corrections_reach_the_prompt():
    # br-004's two lines live only in the registry now; they must still arrive
    # verbatim, in order, exactly as the retired render-corrections.json held them.
    lines = prompt_mod.corrections_for("br-004")
    assert [line["authority"] for line in lines] == ["AGENT_ADDED", "AGENT_ADDED"]
    assert lines[0]["text"].startswith(
        "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE"
    )
    assert lines[1]["text"].startswith(
        "[ghost] Render the rose logo at the size and position shown"
    )
    assert prompt_mod.corrections_for("br-003") == []


def test_base_procedure_carries_material_and_photorealism_directives():
    p = build_prompt(
        name="Love Hurts Bomber",
        sku="lh-004",
        collection="love-hurts",
        reference_labels=[],
        dossier_text=None,
        is_patch=False,
        style="ghost",
        view="front",
    )
    assert "MATERIAL:" in p and "satin" in p
    assert "PHOTOREALISM:" in p and "tech flats" in p
    assert "BRANDING IS EXHAUSTIVE" in p


def test_qc_schema_gates_flat_renders():
    props = qc._JUDGE_SCHEMA["schema"]["properties"]
    assert "photorealistic_not_flat" in props
    assert qc._GATE_TAGS["photorealistic_not_flat"] == "flat_render"
    assert "photorealistic_not_flat" in qc._JUDGE_SCHEMA["schema"]["required"]


def test_mint_lavender_skus_render_again_with_clean_dossiers():
    # bug-119 regression guard: the contamination was cleared 2026-06-10 by
    # re-authoring both dossiers from the real mint garments. These SKUs must
    # stay renderable, and their dossiers must never drift back to the
    # windbreaker-set design (white body + rainbow chevron zip-up).
    assert "sg-006" not in config.EXCLUDED_SKUS
    assert "sg-014" not in config.EXCLUDED_SKUS
    for slug, garment in (
        ("mint-lavender-hoodie", "PULLOVER"),
        ("mint-lavender-sweatpants", "sweatpants"),
    ):
        text = (config.DOSSIER_DIR / f"{slug}.md").read_text(encoding="utf-8")
        lock = text.split("**Garment type lock:**", 1)[1].split("##", 1)[0]
        assert garment in lock
        assert "mint green" in lock
        # exact phrasing the contaminated dossiers used for the wrong garment
        assert "solid **white**" not in lock
        assert "rainbow chevron color-block" not in lock
        assert "zip-up hoodie" not in lock.lower()


def test_extract_view_branding_returns_per_view_sections():
    from scripts.oai_render.prompt import extract_view_branding

    dossier = (
        "# X\n## Branding\n### Front\n- **front-chest**: rose art. Color: red.\n"
        "### Back\n- **back-body**: Solid, no decoration.\n"
        "## Negative\n- NO stripes\n"
    )
    front = extract_view_branding(dossier, "front")
    back = extract_view_branding(dossier, "back")
    assert "front-chest" in front and "back-body" not in front
    assert "no decoration" in back and "rose art" not in back
    assert "NO stripes" not in back  # stops at the next ## section
    assert extract_view_branding(None, "front") == ""
    assert extract_view_branding(dossier, "sideways") == ""


def test_qc_judge_receives_dossier_branding_ground_truth():
    # bug: blank-back garments were failed for "missing branding" because the
    # judge only saw front/logo references. The judge must receive the
    # dossier's per-view spec and be told blank panels are correct.
    from scripts.oai_render import pipeline, references
    from scripts.oai_render.qc import _judge_instructions

    catalog = references.load_catalog()
    dossiers = references.build_dossier_index()
    plan = pipeline.plan_sku("sg-006", catalog, dossiers, style="ghost", view="front")
    exp = pipeline.expectation_for(plan)
    assert exp.branding_spec  # flowed from the dossier
    text = _judge_instructions(exp)
    # Behavior (not exact wording): the dossier's per-view spec reaches the judge,
    # and blank panels are explicitly NOT failed for "missing branding".
    assert exp.branding_spec in text
    assert "blank" in text.lower() and "absence" in text.lower()


def test_qc_judge_rejects_obvious_trim_and_construction_mismatches():
    from scripts.oai_render.qc import RenderExpectation, _judge_instructions

    text = _judge_instructions(
        RenderExpectation(
            sku="br-002",
            name="BLACK Rose Joggers",
            style="ghost",
            view="front",
            is_pair=False,
            is_patch=True,
        )
    ).lower()

    assert "wrong drawstring color" in text
    assert "wrong zipper/closure" in text
    assert "product facts, not cosmetic micro-deviations" in text


def test_founder_keeper_assets_skip_their_plan(tmp_path, monkeypatch):
    # tasks/mockup-render-inventory.md keep pass: a checked keeper drops its
    # exact (sku, style, view) plan from the batch — direct cost savings.

    from scripts.oai_render import pipeline, references

    # A keeper must name an asset that exists on disk to be honored (else it
    # would silently block the re-render of a product whose "kept" image is gone).
    keeper_asset = tmp_path / "sg-009-keeper.webp"
    keeper_asset.write_bytes(b"fake-image")
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        pipeline,
        "_registry_keepers",
        lambda: [
            {
                "sku": "sg-009",
                "style": "on-model",
                "view": "front",
                "asset": "sg-009-keeper.webp",
                "founder_note": "good render, save it",
            }
        ],
    )
    catalog = references.load_catalog()
    dossiers = references.build_dossier_index()
    result = pipeline.run(["sg-009"], catalog, dossiers, styles=["ghost", "on-model"], dry_run=True)
    combos = {(p.sku, p.style, p.view) for p in result["plans"]}
    assert ("sg-009", "on-model", "front") not in combos
    assert ("sg-009", "ghost", "front") in combos  # only the keeper plan drops


def test_live_registry_keepers_are_the_founder_decisions():
    # The two keep decisions moved from render-keepers.json into the registry's
    # render_policy sections, with their founder notes intact.
    from scripts.oai_render import pipeline

    keepers = {(k["sku"], k["style"], k["view"]): k for k in pipeline._registry_keepers()}
    assert set(keepers) == {("br-006", "on-model", "front"), ("sg-009", "on-model", "front")}
    assert keepers[("br-006", "on-model", "front")]["founder_note"] == (
        "real product \u2014 approved 2026-06-10"
    )
    assert keepers[("sg-009", "on-model", "front")]["asset"].endswith(
        "signature-sherpa-jacket-front-model.webp"
    )


def test_pair_with_excluded_member_falls_back_to_solo(monkeypatch):
    from scripts.oai_render import pipeline, references

    monkeypatch.setitem(config.EXCLUDED_SKUS, "sg-014", "test: contaminated dossier")
    catalog = references.load_catalog()
    dossiers = references.build_dossier_index()
    result = pipeline.run(["sg-013"], catalog, dossiers, styles=["on-model"], dry_run=True)
    plans = [p for p in result["plans"] if p.error is None]
    assert len(plans) == 1
    assert plans[0].style == "on-model"
    assert not plans[0].output_slug.startswith("pair__")


def test_br009_founder_specified_garment_is_batch_plannable():
    # br-009's technique, colour, digit placement and 3in x 4in patch are all
    # founder-specified in the registry dossier, so nothing holds it out of batch
    # planning. (A "generation hold" written into the dossier by an agent was
    # removed as an imposed verification requirement.) Paid generation stays
    # gated separately: `generate` needs --yes and a founder y.
    from scripts.oai_render import pipeline, references

    assert "br-009" not in config.EXCLUDED_SKUS
    catalog = references.load_catalog()
    assert "br-009" in pipeline.resolve_targets(catalog, collection="black-rose")
    assert "br-009" in pipeline.resolve_targets(catalog, all_skus=True)
    assert pipeline.resolve_targets(catalog, sku="br-009") == ["br-009"]
