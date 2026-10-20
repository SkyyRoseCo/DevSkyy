"""Deterministic runtime allowlist packager. Call through npm run package:theme."""

import hashlib
import io
import json
import os
import platform
import re
import subprocess
import zipfile
import zlib
from pathlib import Path

from inputs import ROOT, all_skus, get_product
from PIL import Image, features

from skyyrose.core.media_usage import STAGING_TARGET, bound_document, validated_usage_roles
from skyyrose.core.production_media import (
    production_roles,
    validate_scope,
    TARGET as PRODUCTION_TARGET,
    SITE_ID as PRODUCTION_SITE_ID,
)

HERE = Path(__file__).resolve().parent
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Media-eligibility gate reused by skyyrose.core.product_registry for reviewed
# card fronts. Packaging (main) keeps the certified release boundary.
CANONICAL_MEDIA_SHA256 = "b4957a6f9210c6c906990a974e7f3f432cc4b2fe9d9ae94d09958e590c1a673e"


REQUIRED_ROLES_SHA256 = "6184c23a6a99f24e919fcdb9e37569d870865660bf9b5c9ccaeab3d26586b693"


CARD_ENCODING = {
    "builder_sha256": "5b9247ea80d593b87b1dd4bb15c02460fcb235d6dfc5d4fe8a1f8de8b98de791",
    "crop": False,
    "format": "WEBP",
    "libwebp_version": "1.6.0",
    "method": 6,
    "pillow_version": "12.3.0",
    "quality": 90,
    "resize": "LANCZOS",
    "upscale": False,
}


def eligible_derivative(relative, record, inventory):
    """Delivery inherits an eligible master; it cannot create visual approval."""
    skus = record.get("skus")
    if not isinstance(skus, list) or len(skus) != 1 or not isinstance(skus[0], str):
        return False
    sku = skus[0]
    width, height = record.get("width"), record.get("height")
    if (
        type(width) is not int
        or width < 1
        or type(height) is not int
        or height < 1
        or relative != f"assets/derived/card-fronts/{sku}-{width}w.webp"
        or not re.fullmatch(r"[a-z0-9-]+", sku)
        or record.get("kind") != "photograph"
        or record.get("origin") != "V2_ORIGINAL_20261002"
    ):
        return False
    source_path = record.get("source_path")
    if not isinstance(source_path, str) or source_path == relative:
        return False
    source = inventory.get("assets", {}).get(source_path, {})
    if (
        not isinstance(source, dict)
        or source.get("status") not in {"INDEPENDENT_VISUAL_PASS", "FOUNDER_ACCEPTED"}
        or source.get("kind") != "photograph"
        or source.get("sha256") != record.get("source_sha256")
        or not eligible_media(source_path, inventory)
    ):
        return False
    for binding in ("roles", "skus", "collections"):
        if record.get(binding) != source.get(binding):
            return False
    delivery = record.get("delivery_manifest")
    if (
        not isinstance(delivery, dict)
        or delivery.get("path") != "assets/derived/card-fronts/manifest.json"
    ):
        return False
    manifest_path = THEME / delivery["path"]
    if (
        manifest_path.is_symlink()
        or not manifest_path.is_file()
        or sha(manifest_path) != delivery.get("sha256")
    ):
        return False
    try:
        manifest_path.resolve().relative_to(THEME.resolve())
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict) or not isinstance(manifest.get("products"), dict):
            return False
        product = manifest["products"][sku]
        if not isinstance(product, dict):
            return False
        encoding = product.get("encoding")
        if not isinstance(encoding, dict) or set(encoding) != set(CARD_ENCODING):
            return False
        if any(type(encoding[key]) is not type(value) for key, value in CARD_ENCODING.items()):
            return False
        if (
            sha(ROOT / "tools/v2-runtime/build-card-renditions.py")
            != CARD_ENCODING["builder_sha256"]
        ):
            return False
        if (
            manifest.get("schema") != "skyyrose.card-renditions.v1"
            or product.get("source") != source_path
            or product.get("source_sha256") != source["sha256"]
            or product.get("source_review") != source.get("review")
            or product.get("encoding") != CARD_ENCODING
        ):
            return False
        if (
            Image.__version__ != CARD_ENCODING["pillow_version"]
            or features.version("webp") != CARD_ENCODING["libwebp_version"]
        ):
            return False
        for binding in ("roles", "skus", "collections"):
            if product.get(binding) != source.get(binding):
                return False
        expected = {"src": relative, "width": width, "height": height, "sha256": record["sha256"]}
        renditions = product.get("renditions")
        if not isinstance(renditions, list) or renditions.count(expected) != 1:
            return False
        with Image.open(THEME / source_path) as master, Image.open(THEME / relative) as child:
            if (
                child.format != "WEBP"
                or child.size != (width, height)
                or width > master.width
                or (width not in (160, 320, 480, 768, 1024, 1280, 1536) and width != master.width)
                or height != round(master.height * width / master.width)
            ):
                return False
            resized = master.resize((width, height), Image.Resampling.LANCZOS)
            stream = io.BytesIO()
            resized.save(stream, format="WEBP", quality=90, method=6)
            return stream.getvalue() == (THEME / relative).read_bytes()
    except (KeyError, TypeError, ValueError, OSError):
        return False


def house_art_restored(relative, record, digest):
    """Mirror of the PHP gate: the unchanged homepage hero and nothing else."""
    if (
        record.get("roles") != ["homepage_hero"]
        or record.get("skus") != []
        or record.get("collections") != []
    ):
        return False
    restore = bound_document(THEME, record.get("restoration_receipt"))
    return (
        restore is not None
        and restore.get("schema") == "skyyrose.v2.site-art-restoration.v1"
        and restore.get("scope") == "UNCHANGED_EXISTING_V2_HOMEPAGE_ART"
        and restore.get("source") == {"path": relative, "sha256": digest}
        and restore.get("user_request") == "wherr my homepage hero? my scenes?"
        and restore.get("target") == STAGING_TARGET
    )


def eligible_media_original(relative, inventory):
    """Packaging never promotes a candidate, old photograph or unbound derivative."""
    record = inventory.get("assets", {}).get(relative, {})
    path = THEME / relative
    if (
        not isinstance(record, dict)
        or not isinstance(record.get("roles"), list)
        or not record["roles"]
    ):
        return False
    if not record or path.is_symlink() or not path.is_file():
        return False
    try:
        path.resolve().relative_to(THEME.resolve())
    except ValueError:
        return False
    digest = sha(path)
    if record.get("sha256") != digest:
        return False
    if digest in inventory.get("disallowed_legacy_sha256", []):
        return False
    if record.get("kind") in {"housemark", "font", "icon", "house_art"}:
        authority = THEME / "data/v2-canonical-media.json"
        if (
            not authority.is_file()
            or authority.is_symlink()
            or sha(authority) != CANONICAL_MEDIA_SHA256
        ):
            return False
        canonical = json.loads(authority.read_text())
        if record.get("kind") == "house_art" and not house_art_restored(relative, record, digest):
            return False
        return canonical.get("assets", {}).get(relative) == record
    if record.get("status") == "DELIVERY_DERIVATIVE":
        return eligible_derivative(relative, record, inventory)
    review = record.get("review", {})
    if not isinstance(review, dict):
        return False
    receipt_path = review.get("path", "")
    if not re.fullmatch(r"data/v2-media-reviews/[A-Za-z0-9_.-]+\.json", receipt_path):
        return False
    receipt = THEME / receipt_path
    if not receipt.is_file() or receipt.is_symlink() or sha(receipt) != review.get("sha256"):
        return False
    try:
        receipt.resolve().relative_to(THEME.resolve())
        evidence = json.loads(receipt.read_text())
    except (ValueError, json.JSONDecodeError):
        return False
    if not isinstance(evidence, dict):
        return False
    for binding in ("roles", "skus", "collections"):
        values = record.get(binding)
        if (
            not isinstance(values, list)
            or not isinstance(evidence.get(binding), list)
            or values != evidence[binding]
            or any(not isinstance(value, str) or not value for value in values)
        ):
            return False
    for binding in ("production_id", "producer"):
        if (
            not isinstance(record.get(binding), str)
            or not record[binding]
            or record[binding] != evidence.get(binding)
        ):
            return False
    if record.get("status") == "FOUNDER_ACCEPTED":
        # Founder acceptance is its own evidence class, never a fabricated
        # independent visual PASS. It cannot broaden a card decision to PDP.
        return all(
            (
                record.get("kind") == "photograph",
                record.get("origin") == "V2_ORIGINAL_20261002",
                record.get("roles") == ["card_front"],
                len(record.get("skus", [])) == 1,
                len(record.get("collections", [])) == 1,
                evidence.get("schema") == "skyyrose.founder-card-acceptance.v1",
                review.get("verdict") == "ACCEPTED",
                review.get("reviewer") == "Corey",
                evidence.get("reviewer") == "Corey",
                evidence.get("verdict") == "ACCEPTED",
                evidence.get("authority") == "FOUNDER_CONFIRMED",
                evidence.get("asset_sha256") == digest,
                bool(evidence.get("decision_text")),
                evidence.get("placement_authorization")
                == "ALL 33 PRODUCTS. add them to their card NOW.",
                _founder_decision_bound(evidence),
            )
        )
    return all(
        (
            digest not in inventory.get("disallowed_legacy_sha256", []),
            record.get("kind") == "photograph",
            record.get("status") == "INDEPENDENT_VISUAL_PASS",
            record.get("origin") == "V2_ORIGINAL_20261002",
            bool(record.get("production_id")),
            bool(record.get("roles")),
            bool(record.get("producer")),
            bool(review.get("reviewer")),
            record.get("producer") != review.get("reviewer"),
            review.get("verdict") == "PASS",
            evidence.get("verdict") == "PASS",
            evidence.get("reviewer") == review.get("reviewer"),
            evidence.get("asset_sha256") == digest,
            evidence.get("v2_originality_pass") is True,
            evidence.get("product_fidelity_pass") is True,
        )
    )


def _founder_decision_bound(evidence):
    """Hash the preserved owner receipt as well as the selected image."""
    source = evidence.get("decision_source", {})
    relative = source.get("path", "")
    if not re.fullmatch(r"data/v2-media-reviews/owner-[A-Za-z0-9_.-]+\.json", relative):
        return False
    path = THEME / relative
    if not path.is_file() or path.is_symlink() or sha(path) != source.get("sha256"):
        return False
    try:
        document = json.loads(path.read_text())
        quote = document.get("decision_text") or document.get("decision_evidence", {}).get(
            "verbatim"
        )
        candidates = document.get("candidates", [document.get("candidate", {})])
        schema = document.get("schema")
        status = document.get("status")
        if schema == "skyyrose.creative.owner-decision.v1":
            accepted = status in {
                "FOUNDER_ACCEPTED_CANDIDATES_QUARANTINED",
                "FOUNDER_ACCEPTED_CANDIDATE_QUARANTINED",
            }
        elif schema == "skyyrose.founder-accepted-image-candidate.v2":
            accepted = (
                status == "FOUNDER_ACCEPTED_CANDIDATE"
                and document.get("decision_evidence", {}).get("authority") == "FOUNDER_CONFIRMED"
            )
        else:
            return False
        if not accepted:
            return False
        if not isinstance(candidates, list):
            return False
        return quote == evidence.get("decision_text") and any(
            isinstance(candidate, dict)
            and candidate.get("sha256") == evidence.get("asset_sha256")
            and (candidate.get("sku") or document.get("sku")) == evidence["skus"][0]
            and (
                (
                    isinstance(candidate.get("roles"), list)
                    and all(isinstance(role, str) and role for role in candidate["roles"])
                    and "card_front" in candidate["roles"]
                )
                or (
                    schema == "skyyrose.creative.owner-decision.v1"
                    and document.get("decision") == "ACCEPTED_FOR_PRODUCT_CARD_VISUAL_REVIEW"
                    and candidate.get("roles") is None
                    and status == "FOUNDER_ACCEPTED_CANDIDATE_QUARANTINED"
                )
            )
            for candidate in candidates
        )
    except (ValueError, TypeError, KeyError):
        return False


def eligible_media(relative, inventory):
    if not eligible_media_original(relative, inventory):
        return False
    record = inventory["assets"][relative]
    if record.get("kind") != "photograph" and record.get("status") != "DELIVERY_DERIVATIVE":
        return True
    roles = production_roles(relative, record, inventory, THEME)
    return roles is None or bool(roles)


def effective_media_roles(relative, inventory):
    """Preserve the original review roles and add only validated reuse grants."""
    if not eligible_media(relative, inventory):
        return []
    record = inventory["assets"][relative]
    approved = (
        production_roles(relative, record, inventory, THEME)
        if record.get("kind") == "photograph" or record.get("status") == "DELIVERY_DERIVATIVE"
        else None
    )
    if approved is not None:
        return approved
    if record.get("status") == "DELIVERY_DERIVATIVE":
        return effective_media_roles(record["source_path"], inventory)
    return list(
        dict.fromkeys(
            record.get("roles", [])
            + validated_usage_roles(relative, record, inventory.get("usage_adoptions", {}), THEME)
        )
    )


def missing_media_roles(inventory, selected):
    """A scalar COMPLETE label cannot replace a source-bound role census."""
    source = THEME / "data/v2-required-media-roles.json"
    if not source.is_file() or source.is_symlink() or sha(source) != REQUIRED_ROLES_SHA256:
        raise ValueError("Required V2 delivery role census changed without review")
    required = json.loads(source.read_text())["slots"]
    eligible = [
        (relative, record)
        for relative, record in inventory.get("assets", {}).items()
        if relative in selected
        and record.get("kind") == "photograph"
        and record.get("status") in {"INDEPENDENT_VISUAL_PASS", "FOUNDER_ACCEPTED"}
        and eligible_media(relative, inventory)
    ]
    roles_by_path = {
        relative: effective_media_roles(relative, inventory) for relative, _ in eligible
    }
    products = {sku: get_product(sku) for sku in all_skus()}
    preorder_skus_by_collection = {}
    for sku, product in products.items():
        catalog = product.get("catalog", {})
        collection = product.get("collection")
        if (
            catalog.get("published") == "1"
            and catalog.get("is_preorder") == "1"
            and isinstance(collection, str)
            and collection
        ):
            preorder_skus_by_collection.setdefault(collection, set()).add(sku)
    missing = []
    for slot in required:
        if slot["role"] in {"card_front", "pdp_on_model_front"}:
            collection = products.get(slot.get("sku"), {}).get("collection")
            matches = [
                record
                for relative, record in eligible
                if not relative.startswith("assets/derived/card-fronts/")
                and record.get("skus") == [slot.get("sku")]
                and collection
                and record.get("collections") == [collection]
                and slot["role"] in roles_by_path[relative]
            ]
            covered = len(matches) == 1
        elif slot["role"] == "merchandise_scene":
            collection = slot.get("collection")
            preorder_skus = preorder_skus_by_collection.get(collection, set())
            covered = any(
                slot["role"] in roles_by_path[relative]
                and record.get("collections") == [collection]
                and isinstance(record.get("skus"), list)
                and bool(record["skus"])
                and all(isinstance(sku, str) for sku in record["skus"])
                and set(record["skus"]).issubset(preorder_skus)
                for relative, record in eligible
            )
        else:
            covered = any(
                slot["role"] in roles_by_path[relative]
                and ("sku" not in slot or slot["sku"] in record.get("skus", []))
                and (
                    "collection" not in slot or slot["collection"] in record.get("collections", [])
                )
                for relative, record in eligible
            )
        if not covered:
            missing.append(slot)
    return missing


def validate_production_package(production_inventory, selected):
    """Refuse incomplete authority or provenance before creating a release ZIP."""
    production = validate_scope(production_inventory, THEME)
    approved_members = set(production["masters"])
    for entry in production["masters"].values():
        approved_members.update(item["path"] for item in entry["delivery_files"])
    for member in sorted(approved_members):
        if not eligible_media_original(member, production_inventory):
            raise ValueError("Original production member provenance refused: " + member)
    if not (approved_members | {"data/runtime-media.json"}) <= set(selected):
        raise ValueError("Approved production scope omitted from package")
    return production


def runtime_media_policy(inventory):
    """Use the delivered PHP source policy, including its approved film branch."""
    allowed = json.loads(subprocess.check_output([
        "/usr/bin/sandbox-exec", "-p", "(version 1)(allow default)(deny network*)",
        "/opt/homebrew/Cellar/php/8.5.6/bin/php", str(HERE / "compile-runtime-media.php"),
        str(THEME),
    ], text=True, timeout=120))
    fields = (
        "sha256", "kind", "status", "roles", "skus", "collections", "width", "height",
        "source_path", "source_sha256", "review",
    )
    assets = {}
    for relative, roles in sorted(allowed.items()):
        record = inventory["assets"][relative]
        assets[relative] = {k: record[k] for k in fields if k in record}
        assets[relative]["effective_roles"] = roles
    return {
        "schema": "skyyrose.v2.runtime-media.v1", "assets": assets,
        "usage_adoptions": inventory.get("usage_adoptions", {}),
    }


def main():
    boundary = json.loads((HERE / "package-boundary.json").read_text())["files"]
    expected = set(boundary)
    actual = {
        p.relative_to(THEME).as_posix()
        for p in THEME.rglob("*")
        if p.is_file()
        and not set(p.relative_to(THEME).parts) & {"node_modules", "dist", "__pycache__"}
        and p.name not in {".DS_Store", "package-lock.json"}
        # Gitignored runtime coordination locks written by the registry builders.
        and not p.name.endswith(".json.lock")
    }
    if actual != expected:
        raise ValueError(f"Unclassified or missing theme source: {sorted(actual ^ expected)}")
    out = THEME / "dist"
    out.mkdir(exist_ok=True)
    archive = out / "skyyrose-flagship-2.zip"
    selected = [p for p in sorted(boundary) if boundary[p]["release"]]
    production_inventory = json.loads((THEME / "data/v2-media-eligibility.json").read_text())
    production = validate_production_package(production_inventory, selected)
    policy_path = THEME / "data/runtime-media.json"
    if json.loads(policy_path.read_text()) != runtime_media_policy(production_inventory):
        raise ValueError("Runtime display policy differs from verified source decisions")
    gate = (THEME / "inc/v2-media-eligibility.php").read_text()
    if f"hash_equals( '{sha(policy_path)}', hash_file( 'sha256', $runtime ) )" not in gate:
        raise ValueError("Runtime display policy binding is stale")
    authority_binding = production_inventory["production_media_authority"]
    # Standard DEFLATE compresses code/data while retaining every original pixel.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for relative in selected:
            if any(
                part in {".DS_Store", "__MACOSX"} or part.startswith("._")
                for part in Path(relative).parts
            ):
                raise ValueError(f"Filesystem metadata is not a runtime asset: {relative}")
            path = THEME / relative
            if path.is_symlink():
                raise ValueError(f"Symlink not permitted: {relative}")
            path.resolve().relative_to(THEME.resolve())
            if any(x in Path(relative).parts for x in (".git", "node_modules", "qa", "scripts")):
                raise ValueError(f"Internal file in package: {relative}")
            content = path.read_bytes()
            if path.suffix in {".php", ".css", ".js", ".json", ".html"}:
                if re.search(rb"""(?:["'\s])/(?:Users|home)/""", content):
                    raise ValueError(f"Workstation path in package: {relative}")
            entry = zipfile.ZipInfo("skyyrose-flagship-2/" + relative, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, content)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None or len(bundle.namelist()) != len(selected):
            raise ValueError("ZIP integrity failed")
        for relative in selected:
            if hashlib.sha256(bundle.read("skyyrose-flagship-2/" + relative)).hexdigest() != sha(
                THEME / relative
            ):
                raise ValueError(f"ZIP content drift: {relative}")
    source_tree = os.environ.get("V2_SOURCE_TREE")
    if source_tree:
        if not re.fullmatch("[0-9a-f]{40}", source_tree):
            raise ValueError("V2_SOURCE_TREE must identify a Git tree export")
        commit, clean = None, None
    else:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True
        )
        clean = not bool(status.strip())
    inputs = json.loads((HERE / "build-inputs.json").read_text())
    release = {
        "schema": "skyyrose.v2.release-manifest.v1",
        "git_commit": commit,
        "source_tree": source_tree,
        "source_clean": clean,
        "deployment_authorized": False,
        "production_media": {
            "authority": authority_binding,
            "intended_target": PRODUCTION_TARGET,
            "expected_site_id": PRODUCTION_SITE_ID,
            "scope": production["scope"],
            "installed_identity_qualified": False,
        },
        "build_id": sha(HERE / "build-inputs.json"),
        "artifact_sha256": sha(archive),
        "theme_slug": "skyyrose-flagship-2",
        "theme_version": json.loads((THEME / "package.json").read_text())["version"],
        "toolchain": {
            "node": subprocess.check_output(["node", "--version"], text=True).strip(),
            "npm": subprocess.check_output(["npm", "--version"], text=True).strip(),
            "python": platform.python_version(),
            "zlib": zlib.ZLIB_VERSION,
            "zip_compression": "DEFLATED",
        },
        "historical_catalog_sha256": inputs["catalog_sha256"],
        "current_registry_sha256": inputs["current_registry_sha256"],
        "product_sot_scope": "historical_media_binding_only",
        "product_sot_sha256": inputs["product_sot_sha256"],
        "registry_sha256": sha(THEME / "data/product-presentation-registry.json"),
        "runtime_manifests": {p: sha(THEME / p) for p in selected if p.startswith("data/")},
        "files": {p: sha(THEME / p) for p in selected},
    }
    (out / "release-manifest.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
    print(f"Validated {len(selected)} runtime package entries; SHA-256 {sha(archive)}")


if __name__ == "__main__":
    main()
