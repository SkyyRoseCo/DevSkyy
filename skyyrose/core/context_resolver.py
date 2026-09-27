"""Read-only, content-addressed SkyyRose context resolution; never release approval.

CLI: python -m skyyrose.core.context_resolver request.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from skyyrose.core.content_intent import (
    TAXONOMY,
    ContentIntent,
    missing_planning_fields,
    verification_requirements,
)
from skyyrose.core.execution_policy import STAGES, LifecycleStatus, select_rules
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT
from skyyrose.core.product import get_product, provenance
from skyyrose.core.product_truth import project_product

PACKAGE = REPO_ROOT / "docs/brand/constitution-v1"
Mode = Literal["EXACT_PRODUCT", "PRODUCT_CONCEPT", "BRAND_ABSTRACT"]
Stage = Literal["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]
PaletteDomain = Literal[
    "PRODUCT",
    "PROTECTED_ASSET",
    "INTERFACE",
    "ENVIRONMENT",
    "PHOTOGRAPHIC",
    "CAMPAIGN",
    "LIGHTING",
    "NATURAL_LOCATION",
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceReference(Contract):
    """Local, digest-bound evidence. Its presence does not confer owner approval."""

    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ProductRequirement(Contract):
    sku: str = Field(min_length=1)
    required_views: list[Literal["front", "back", "packshot", "back_packshot"]]
    required_details: list[str]


class PaletteIntent(Contract):
    domain: PaletteDomain
    purpose: str = Field(min_length=1)
    proposed_colors: list[str] = Field(default_factory=list)
    alters_product: bool = False
    alters_protected_asset: bool = False


class ResolutionRequest(Contract):
    job_id: str = Field(min_length=1)
    brand: Literal["skyyrose"]
    objective: str = Field(min_length=1)
    collection_context: str | None
    campaign_brief: SourceReference | None
    lifecycle_stage: Stage
    channel: str | None = None
    content_intent: ContentIntent
    production_method: str | None = None
    campaign_authority_required: bool = False
    major_initiative: bool = False
    place_relevant: bool = False
    intended_use: Literal["INTERNAL", "CUSTOMER_FACING", "CONCEPT", "PAID", "ECOMMERCE", "RESEARCH"]
    audience: str = Field(min_length=1)
    representation_mode: Mode
    products: list[ProductRequirement]
    decisions: list[SourceReference]
    constraints: list[str]
    palette_intents: list[PaletteIntent] = Field(default_factory=list)
    absence_reasons: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def explicit_absence(self) -> ResolutionRequest:
        for field in self.absence_reasons:
            if field not in ("collection_context", "campaign_brief"):
                raise ValueError(f"Unsupported absence reason: {field}")
            if getattr(self, field) is not None:
                raise ValueError(f"{field}: present field cannot have absence reason")
        for field in ("lifecycle_stage", "intended_use", "audience", "representation_mode"):
            if getattr(self, field) != getattr(self.content_intent, field):
                raise ValueError(f"content_intent.{field} contradicts request.{field}")
        if self.channel is not None and self.content_intent.distribution_channels != [self.channel]:
            raise ValueError(
                "Legacy channel must equal the explicit distribution channel; film is a medium/production type"
            )
        for field in ("collection_context", "campaign_brief"):
            if getattr(self, field) is None and not self.absence_reasons.get(field, "").strip():
                raise ValueError(f"{field}: null requires an absence_reasons entry")
        if len({p.sku for p in self.products}) != len(self.products):
            raise ValueError("duplicate SKU requirements")
        return self


class Gap(Contract):
    field: str
    source: str
    reason: str
    blocking: bool
    affected_stage: Stage


class ResolvedContext(Contract):
    resolution_id: str
    request_digest: str
    constitution_version: str
    constitution_digest: str
    selected_rule_ids: list[str]
    applicable_context: list[str]
    source_manifest: list[dict[str, Any]]
    field_authority: dict[str, str]
    protected_constraints: list[dict[str, Any]]
    creative_freedoms: list[dict[str, Any]]
    applicable_rules: list[dict[str, Any]]
    request_snapshot: dict[str, Any]
    typography: dict[str, Any]
    conflicts: list[Gap]
    gaps: list[Gap]
    status: LifecycleStatus
    resolution_status: Literal["READY", "READY_WITH_NONBLOCKING_GAPS", "BLOCKED"]
    execution_products: list[dict[str, Any]]
    product_conflicts: list[dict[str, Any]]
    execution_rule_ids: list[str]
    rule_explanations: list[dict[str, Any]]
    verification_requirements: dict[str, list[str]]
    missing_context: list[str]
    decision_lineage: list[str]
    products: list[dict[str, Any]]
    palette_policies: list[dict[str, Any]]
    resolved_at: str
    release_ready: Literal[False] = False
    action_authorized: Literal[False] = False


class SourceIntegrityError(ValueError):
    """Source is missing, unratified, inconsistent or changed during resolution."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _within(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise SourceIntegrityError("reference escapes its source root")
    return path


def _detail(record: dict[str, Any], key: str) -> Any:
    value: Any = record
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def resolve_context(request: ResolutionRequest, *, package: Path = PACKAGE) -> ResolvedContext:
    """Resolve fresh sources without mutation, cached success, media generation or live commerce.

    READY means sufficient context for the declared request, not verified output.
    Free-text objectives/constraints are carried as briefs, never parsed as authority.
    """
    sources: dict[Path, str] = {}

    def read(path: Path, expected: str | None = None) -> bytes:
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise SourceIntegrityError(f"unreadable source: {path}") from exc
        digest = _digest(data)
        if expected is not None and digest != expected:
            raise SourceIntegrityError(f"source digest mismatch: {path}")
        if path in sources and sources[path] != digest:
            raise SourceIntegrityError(f"source changed during resolution: {path}")
        sources[path] = digest
        return data

    read(Path(__file__).resolve())
    for module in ("content_intent.py", "product_truth.py", "execution_policy.py"):
        read(Path(__file__).with_name(module))
    typography = json.loads(read(THEME_ROOT / "data/brand/typography.json"))
    constitution_bytes = read(package / "constitution.json")
    constitution = json.loads(constitution_bytes)
    manifest = json.loads(read(package / "context-manifest.json"))
    decisions = json.loads(read(package / "owner-decisions.json"))
    if constitution["status"] != "FULLY_RATIFIED" or decisions["status"] != "FULLY_RATIFIED":
        raise SourceIntegrityError("Constitution is not fully ratified")
    if manifest["constitution"]["sha256"] != _digest(constitution_bytes):
        raise SourceIntegrityError("manifest Constitution digest mismatch")
    rules = constitution["rules"]
    ids = {r["id"] for r in rules}
    if len(ids) != len(rules) or ids != set(decisions["ratified_rule_ids"]):
        raise SourceIntegrityError("canonical rule/decision mismatch")
    if ids != {r["id"] for r in manifest["records"]}:
        raise SourceIntegrityError("canonical rule/manifest mismatch")
    events = {e["event_id"]: e for e in decisions["events"]}
    for rule in rules:
        if (
            rule["status"] != "OWNER_RATIFIED"
            or rule["decision_event"] not in events
            or events[rule["decision_event"]]["status"] not in ("APPROVED", "APPROVED_SCOPED")
        ):
            raise SourceIntegrityError("rule lacks owner ratification lineage")
        wording = events[rule["decision_event"]].get("approved_wording")
        if isinstance(wording, dict) and wording.get(rule["id"]) != rule["rule"]:
            raise SourceIntegrityError("rule differs from approved decision wording")
        if isinstance(wording, str):
            if rule["id"] in ("D.origin", "D.legacy"):
                clauses = wording.split(";")
                if len(clauses) != 2:
                    raise SourceIntegrityError("invalid legacy split approval")
                expected = clauses[0 if rule["id"] == "D.origin" else 1]
                matches = (
                    rule["rule"].strip().rstrip(".").casefold()
                    == expected.strip().rstrip(".").casefold()
                )
            else:
                matches = rule["rule"] == wording
            if not matches:
                raise SourceIntegrityError("rule differs from approved decision wording")
        if not isinstance(wording, (str, dict)):
            raise SourceIntegrityError("decision has no approved wording")
    manifest_records = {r["id"]: r for r in manifest["records"]}
    for rule in rules:
        record = manifest_records[rule["id"]]
        if (
            record["status"] != "OWNER_RATIFIED"
            or record["decision_event"] != rule["decision_event"]
        ):
            raise SourceIntegrityError("manifest decision lineage mismatch")
    for key in ("source_handoff", "final_ratification_source"):
        ref = constitution[key]
        read(_within(package, ref["path"]), ref["sha256"])
    for ref in ([request.campaign_brief] if request.campaign_brief else []) + request.decisions:
        read(_within(REPO_ROOT, ref.path), ref.sha256)

    gaps: list[Gap] = []
    conflicts: list[Gap] = []

    def gap(
        field: str, source: str, reason: str, *, blocking: bool = True, conflict: bool = False
    ) -> None:
        (conflicts if conflict else gaps).append(
            Gap(
                field=field,
                source=source,
                reason=reason,
                blocking=blocking,
                affected_stage=request.lifecycle_stage,
            )
        )

    if request.representation_mode != "EXACT_PRODUCT" and request.products:
        gap("representation_mode", "F1", "Real SKU bindings require EXACT_PRODUCT", conflict=True)
    if request.representation_mode == "EXACT_PRODUCT" and not request.products:
        gap("products", "F1", "EXACT_PRODUCT requires at least one SKU")
    if request.decisions:
        gap(
            "decisions",
            "owner-decisions.json",
            "Additional decision documents require canonical ratification before overriding rules",
        )

    late_stage = request.lifecycle_stage in ("M5", "M6", "M7")
    needs_campaign = (
        request.campaign_authority_required
        or TAXONOMY.family("content_role", request.content_intent.content_role)
        in ("campaign", "film", "advertising")
        or TAXONOMY.family("production_type", request.content_intent.production_type)
        in ("campaign", "film", "advertising")
        or request.intended_use in ("CUSTOMER_FACING", "PAID", "ECOMMERCE")
    )
    if late_stage and needs_campaign and request.campaign_brief is None:
        gap("campaign_brief", "lifecycle", "Campaign authority required for production/release")
    missing_context = missing_planning_fields(request.content_intent)
    for field in missing_context:
        gap(
            f"content_intent.{field}",
            "intent",
            "Required intent planning context missing",
            blocking=late_stage,
        )
    if (
        late_stage
        and request.intended_use in ("CUSTOMER_FACING", "PAID", "ECOMMERCE")
        and not request.content_intent.distribution_channels
    ):
        gap(
            "distribution_channels",
            "intent",
            "Customer-facing production requires distribution context",
        )
    if (
        request.representation_mode == "EXACT_PRODUCT"
        and request.lifecycle_stage != "M1"
        and not request.production_method
    ):
        gap("production_method", "M-002", "Declare a fidelity-preserving production path")
    if request.production_method not in (
        None,
        "SOURCE_PHOTOGRAPHY",
        "SOURCE_COMPOSITE",
        "VALIDATED_3D",
        "PRODUCT_SCAN",
        "CONTROLLED_RENDER",
        "VERIFIED_WORKFLOW",
        "ABSTRACT",
    ):
        gap("production_method", "M-002", "Unknown or unresolved production path")
    if request.representation_mode == "EXACT_PRODUCT" and request.production_method == "ABSTRACT":
        gap("production_method", "F1", "Abstract production cannot depict a real SKU")
    required_by_sku = {p.sku: p for p in request.products}
    for shot in request.content_intent.shots:
        for sku in shot.product_skus:
            if sku not in required_by_sku:
                gap(
                    f"shots.{shot.shot_id}.{sku}",
                    "intent",
                    "Shot SKU lacks resolved product requirements",
                )
    shot_bindings = [(shot.shot_role, shot.product_skus) for shot in request.content_intent.shots]
    if request.content_intent.shot_role:
        shot_bindings.append((request.content_intent.shot_role, list(required_by_sku)))
    for role, skus in shot_bindings:
        for sku in skus:
            requirement = required_by_sku.get(sku)
            if requirement is None:
                continue
            expected_views = {"FRONT": {"front", "packshot"}, "BACK": {"back", "back_packshot"}}
            if role in expected_views and not expected_views[role].intersection(
                requirement.required_views
            ):
                gap(
                    f"shots.{sku}.{role}",
                    "F1",
                    "Shot function requires corresponding authoritative product view",
                )
            if role == "SIDE":
                gap(
                    f"shots.{sku}.SIDE",
                    "F1",
                    "No authoritative side-view adapter; never invent side evidence",
                )
            if (
                role in ("DETAIL", "MATERIAL", "GRAPHIC", "FIT")
                and not requirement.required_details
            ):
                gap(
                    f"shots.{sku}.{role}",
                    "F1",
                    "Detail/fit shot requires explicit authoritative detail requirements",
                )
    products: list[dict[str, Any]] = []
    execution_products = []
    product_conflicts = []
    contexts = {request.collection_context} if request.collection_context else set()
    for requirement in request.products:
        try:
            for ref in provenance()["sources"].values():
                read(_within(REPO_ROOT, ref["path"]))
            product = get_product(requirement.sku)
        except (KeyError, FileNotFoundError, ValueError) as exc:
            gap(f"products.{requirement.sku}", "get_product", type(exc).__name__)
            continue
        # Independently hash bytes: never trust the reader's mtime-based stamp alone.
        for ref in product["provenance"]["sources"].values():
            data = read(_within(REPO_ROOT, ref["path"]))
            if not _digest(data).startswith(ref["sha256"]):
                raise SourceIntegrityError("product reader/source snapshot mismatch")
        if product.get("collection"):
            contexts.add(product["collection"])
            if request.collection_context and request.collection_context != product["collection"]:
                gap(
                    "collection_context",
                    requirement.sku,
                    "Requested collection contradicts canonical SKU collection",
                    conflict=True,
                )
        if not requirement.required_views:
            gap(
                f"products.{requirement.sku}.required_views", "F1", "Declare required product views"
            )
        for role in requirement.required_views:
            image = product["images"].get(role)
            field = f"products.{requirement.sku}.images.{role}"
            if not image or not image.get("role_asset"):
                gap(
                    field,
                    "get_product",
                    "Insufficient authoritative view; fallback is not that role",
                )
                continue
            path = _within(THEME_ROOT, image["path"])
            if not path.is_file():
                gap(field, "get_product", "Authoritative reference binary missing")
            else:
                read(path)
        # Irrelevant product gaps remain visible but cannot block a requested available view.
        for missing in product.get("gaps", []):
            gap(
                f"products.{requirement.sku}.{missing}",
                "get_product",
                "Reader-reported gap; applicability governed by explicit requirements",
                blocking=False,
            )
        product = {
            **product,
            "provenance": {k: v for k, v in product["provenance"].items() if k != "generated"},
        }
        projection = project_product(
            json.loads(json.dumps(product)),
            requirement.required_views,
            requirement.required_details,
        )
        for problem in projection["execution"]["unresolved_required_gaps"]:
            gap(
                f"products.{requirement.sku}.{problem['field']}",
                "product authority",
                problem["reason"],
            )
        for conflict in projection["conflicts"]:
            product_conflicts.append({"sku": requirement.sku, **conflict})
            if conflict["status"] == "CONFLICTED" and request.production_method in (
                "VALIDATED_3D",
                "PRODUCT_SCAN",
                "CONTROLLED_RENDER",
                "VERIFIED_WORKFLOW",
            ):
                gap(
                    f"products.{requirement.sku}.{conflict['field']}",
                    "product authority",
                    "Reconstructive production requires resolution of conflicting dimensions",
                )
        execution_products.append(projection["execution"])
        registry_ref = product["provenance"]["sources"].get("registry")
        if registry_ref:
            registry_snapshot = json.loads(read(_within(REPO_ROOT, registry_ref["path"])))
            product["audit_registry_record"] = registry_snapshot.get("products", {}).get(
                requirement.sku
            )
            product["audit_registry_placements"] = registry_snapshot.get("sku_logos", {}).get(
                requirement.sku
            )
        product["audit_authority_conflicts"] = projection["conflicts"]
        product["audit_editorial_exclusions"] = projection["excluded_editorial"]
        products.append(product)

    kids = any("kids" in context.lower() for context in contexts)
    selected = [r for r in rules if not r["id"].startswith("K") or kids]
    palette_policies = []
    domain_keys = {"PROTECTED_ASSET": "protected_assets", "NATURAL_LOCATION": "natural_location"}
    for intent in request.palette_intents:
        refs = manifest["palette_domains"][domain_keys.get(intent.domain, intent.domain.lower())]
        palette_policies.append(
            {
                **intent.model_dump(),
                "rule_ids": refs,
                "permission": "SCOPED_POLICY_ONLY_NOT_OUTPUT_VERIFICATION",
            }
        )
        if intent.alters_product and request.representation_mode == "EXACT_PRODUCT":
            gap("palette_intents", "P2-001", "Palette cannot recolor a real product", conflict=True)
        if intent.alters_protected_asset:
            gap(
                "palette_intents",
                "P3-001",
                "Protected asset treatment requires governed permission",
                conflict=True,
            )

    # Recheck every source, including required image bytes, before returning a coherent snapshot.
    for path, digest in list(sources.items()):
        read(path, digest)
    execution_rule_ids, rule_explanations = select_rules(
        rules,
        exact=request.representation_mode == "EXACT_PRODUCT",
        kids=kids,
        major=request.major_initiative,
        place=request.place_relevant,
        medium=request.content_intent.medium,
        palette_ids={rule for p in palette_policies for rule in p["rule_ids"]},
    )
    for product in execution_products:
        for reference in product["references"].values():
            if reference:
                path = str((THEME_ROOT / reference["path"]).resolve())
                reference["sha256"] = sources.get(Path(path))
    request_digest = _digest(_canonical(request.model_dump()))
    source_manifest = [
        {"path": str(path), "sha256": digest} for path, digest in sorted(sources.items())
    ]
    resolution_id = _digest(
        _canonical(
            {
                "request": request_digest,
                "sources": source_manifest,
                "products": products,
                "execution_products": execution_products,
                "taxonomy": TAXONOMY.snapshot(),
                "execution_rule_ids": execution_rule_ids,
                "selected_rules": selected,
                "palette_policies": palette_policies,
            }
        )
    )
    blocking = any(g.blocking for g in gaps + conflicts)
    return ResolvedContext(
        resolution_id=resolution_id,
        request_digest=request_digest,
        constitution_version=constitution["version"],
        constitution_digest=_digest(constitution_bytes),
        selected_rule_ids=[r["id"] for r in selected],
        applicable_context=sorted(contexts),
        source_manifest=source_manifest,
        field_authority={
            "constitutional": "Owner-ratified constitution.json and decision history",
            "product": "get_product(sku); unified registry; founder facts authoritative",
            "live_commerce": "WooCommerce fresh session/variation state; NOT_RESOLVED here",
            "typography": "typography.json governs existing storefront",
            "palette": "P1-001–P8-001; domain permissions never transfer automatically",
            "brief": "Digest-bound context; cannot silently override constitutional/product truth",
        },
        protected_constraints=[
            r
            for r in selected
            if r["level"] in ("L1", "HARD_REQUIREMENT", "GOVERNANCE")
            or r["id"] in ("F2", "F3", "F4")
        ],
        creative_freedoms=[
            r
            for r in selected
            if r["id"]
            in {
                "F5",
                "F6",
                "F7",
                "F8",
                "F9",
                "F10",
                "F11",
                "F12",
                "F13",
                "F14",
                "P4-001",
                "P5-001",
                "P6-001",
                "P7-001",
                "K2-001",
                "K3-001",
            }
        ],
        applicable_rules=selected,
        request_snapshot=request.model_dump(),
        typography=typography,
        conflicts=conflicts,
        gaps=gaps,
        status="BLOCKED" if blocking else STAGES[request.lifecycle_stage],
        resolution_status=(
            "BLOCKED" if blocking else ("READY_WITH_NONBLOCKING_GAPS" if gaps else "READY")
        ),
        execution_products=execution_products,
        product_conflicts=product_conflicts,
        execution_rule_ids=execution_rule_ids,
        rule_explanations=rule_explanations,
        verification_requirements=verification_requirements(request.content_intent),
        missing_context=missing_context,
        decision_lineage=sorted({r["decision_event"] for r in selected}),
        products=products,
        palette_policies=palette_policies,
        resolved_at=datetime.now(UTC).isoformat(),
    )


def execution_context(context: ResolvedContext) -> dict[str, Any]:
    """Compact CLI/default consumer representation; full model is audit-only."""
    return {
        "schema_version": "1.0",
        "bundle_type": "EXECUTION_CONTEXT",
        "job_id": context.request_snapshot["job_id"],
        "objective": context.request_snapshot["objective"],
        "production_method": context.request_snapshot["production_method"],
        "resolved_collection_context": context.applicable_context,
        "resolution_id": context.resolution_id,
        "status": context.status,
        "resolution_status": context.resolution_status,
        "intent": context.request_snapshot["content_intent"],
        "constitution": {
            "version": context.constitution_version,
            "sha256": context.constitution_digest,
            "source": "docs/brand/constitution-v1/constitution.json",
        },
        "rule_ids": context.execution_rule_ids,
        "rule_reasons": {r["id"]: r["reason"] for r in context.rule_explanations if r["included"]},
        "products": context.execution_products,
        "palette_policies": context.palette_policies,
        "verification_requirements": context.verification_requirements,
        "constraints": context.request_snapshot["constraints"],
        "gaps": [g.model_dump() for g in context.gaps if g.blocking],
        "conflicts": [g.model_dump() for g in context.conflicts],
        "missing_context": context.missing_context,
        "explicit_absences": {
            k: v
            for k, v in context.request_snapshot["absence_reasons"].items()
            if not (k == "collection_context" and context.applicable_context)
        },
        "audit_reference": {
            "resolution_id": context.resolution_id,
            "source_manifest_digest": _digest(_canonical(context.source_manifest)),
        },
        "release_ready": False,
        "action_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Print full raw evidence instead of compact execution context",
    )
    args = parser.parse_args()
    try:
        request = ResolutionRequest.model_validate_json(args.request.read_bytes())
        result = resolve_context(request)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}), file=sys.stderr)
        return 2
    print(
        result.model_dump_json(indent=2)
        if args.audit
        else json.dumps(execution_context(result), indent=2, ensure_ascii=False)
    )
    return 1 if result.status == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
