"""Offline page-only projection from frozen presentation source and target preimages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
SOURCE = "299f694702ac2dcc61a0f30aa34e4b3ef12f9118"
ZIP_SHA = "47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16"
PATHS = (
    "collections",
    "collections/signature",
    "collections/black-rose",
    "collections/love-hurts",
    "collections/kids-capsule",
    "worlds",
    "worlds/signature",
    "worlds/black-rose",
    "worlds/love-hurts",
    "worlds/kids-capsule",
    "size-guide",
    "pre-order",
    "contact",
    "shipping-returns",
    "cart",
    "checkout",
)

NEW_PATHS = tuple(
    p
    for p in PATHS
    if p not in ("collections", "pre-order", "contact", "shipping-returns", "cart", "checkout")
)
WORLD_BODY = '<ul><li><a href="https://skyyrose.co/worlds/signature/">Signature — Full Scene</a></li><li><a href="https://skyyrose.co/worlds/black-rose/">Black Rose — Full Scene</a></li><li><a href="https://skyyrose.co/worlds/love-hurts/">Love Hurts — Full Scene</a></li><li><a href="https://skyyrose.co/worlds/kids-capsule/">Kids Capsule — Full Scene</a></li></ul>'
WORLD_SHA = "2a62b0f0f49633e63dd37c40d5075d9a54047b5c9c63c0c438e72cad194d5ab5"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen_file(relative: str) -> bytes:
    path = THEME / relative
    data = path.read_bytes()
    expected = subprocess.run(
        ["git", "show", f"{SOURCE}:wordpress-theme/skyyrose-flagship-2/{relative}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    if data != expected:
        raise ValueError("FROZEN_SOURCE_MISMATCH")
    return data


def definitions(presentation: bytes | None = None) -> dict:
    if presentation is None:
        presentation = frozen_file("inc/presentation-registry.php")
    code = (
        "define('ABSPATH', '/'); function __($s,$d=null){return $s;} "
        "function esc_html($s){return htmlspecialchars($s, ENT_QUOTES, 'UTF-8');} "
        "eval('?>' . stream_get_contents(STDIN)); echo json_encode(skyyrose2_marketplace_pages(), "
        "JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE);"
    )
    result = subprocess.run(
        ["php", "-r", code],
        input=presentation,
        capture_output=True,
        check=True,
    )
    return {row["path"]: row for row in json.loads(result.stdout).values()}


def validate_all_paths(inventory: dict, pages: dict) -> None:
    """Cross-check every status, including desired trashed and suffixed slugs."""
    rows = inventory.get("all_page_paths")
    if not isinstance(rows, list):
        raise ValueError("ALL_STATUS_INVENTORY_REQUIRED")
    seen_ids: set[int] = set()
    seen_paths: set[str] = set()
    resolved: dict[str, dict] = {}
    for row in rows:
        if (
            not isinstance(row, dict)
            or type(row.get("ID")) is not int
            or row["ID"] < 1
            or row["ID"] in seen_ids
            or not all(
                isinstance(row.get(k), str)
                for k in ("path", "post_name", "post_status", "trashed_slug")
            )
            or type(row.get("post_parent")) is not int
        ):
            raise ValueError("ALL_STATUS_ROW_INVALID")
        seen_ids.add(row["ID"])
        path = row["path"].strip("/")
        if path in PATHS:
            if path in seen_paths:
                raise ValueError("ALL_STATUS_DUPLICATE_PATH")
            seen_paths.add(path)
            resolved[path] = row
        if re.sub(r"-[0-9]+$", "", path) in PATHS and path not in PATHS:
            raise ValueError("ALL_STATUS_SUFFIX_COLLISION")
        parent = path.rpartition("/")[0]
        original_slug = row["trashed_slug"] or re.sub(
            r"__trashed(?:-[0-9]+)?$", "", row["post_name"]
        )
        original_path = (parent + "/" if parent else "") + original_slug
        if row["post_status"] == "trash" and (path in PATHS or original_path in PATHS):
            raise ValueError("ALL_STATUS_TRASH_COLLISION")
    for path, before in pages.items():
        row = resolved.get(path)
        if before is None:
            if row is not None:
                raise ValueError("ALL_STATUS_ABSENCE_CONFLICT")
        elif (
            row is None
            or row["ID"] != before.get("ID")
            or row["post_status"] != before.get("post_status")
        ):
            raise ValueError("ALL_STATUS_PREIMAGE_CONFLICT")


def make_plan(inventory: dict, operation: str) -> dict:
    if (
        inventory.get("home") != "https://skyyrose.co"
        or inventory.get("stylesheet") != "skyyrose-flagship"
    ):
        raise ValueError("TARGET_MISMATCH")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", operation):
        raise ValueError("OPERATION_INVALID")
    pages = inventory.get("pages", {})
    if set(pages) != set(PATHS):
        raise ValueError("EXPLICIT_PATH_INVENTORY_REQUIRED")
    validate_all_paths(inventory, pages)
    presentation = frozen_file("inc/presentation-registry.php")
    defs = definitions(presentation)
    ids: set[int] = set()
    changes = []
    template_hashes = {}
    for path in PATHS:
        row = defs.get(path, {"title": path.title(), "template": "default", "content": ""})
        before = pages[path]
        if before is not None:
            if (
                not isinstance(before, dict)
                or before.get("path") != path
                or before.get("post_type") != "page"
                or before.get("post_status") != "publish"
                or type(before.get("ID")) is not int
                or before["ID"] < 1
                or before["ID"] in ids
            ):
                raise ValueError("PAGE_PREIMAGE_INVALID")
            if not isinstance(before.get("snapshot_sha256"), str) or not re.fullmatch(
                r"[a-f0-9]{64}", before["snapshot_sha256"]
            ):
                raise ValueError("PAGE_SNAPSHOT_REQUIRED")
            if (
                not isinstance(before.get("template_values"), list)
                or len(before["template_values"]) > 1
                or not all(isinstance(v, str) for v in before["template_values"])
            ):
                raise ValueError("TEMPLATE_PREIMAGE_INVALID")
            ids.add(before["ID"])
        elif path in (
            "collections",
            "cart",
            "checkout",
            "pre-order",
            "contact",
            "shipping-returns",
        ):
            raise ValueError("REQUIRED_EXISTING_PAGE_ABSENT")
        if path not in NEW_PATHS:
            continue
        if before is not None:
            raise ValueError("NEW_PAGE_PATH_COLLISION")
        template = row["template"]
        file = "page.php" if template == "default" else template
        template_hashes[file] = digest(frozen_file(file))
        changes.append(
            {
                "path": path,
                "title": row["title"],
                "template": template,
                "content": WORLD_BODY if path == "worlds" else row["content"],
                "parent_path": path.rpartition("/")[0],
                "before": before,
            }
        )
    return {
        "schema": 1,
        "home": inventory["home"],
        "operation": operation,
        "source_sha": SOURCE,
        "zip_sha256": ZIP_SHA,
        "worlds_body_sha256": WORLD_SHA,
        "existing_guards": {p: pages[p] for p in PATHS if p not in NEW_PATHS},
        "source_hashes": {
            "inc/presentation-registry.php": digest(presentation),
            **template_hashes,
        },
        "changes": changes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--operation", required=True)
    args = parser.parse_args()
    plan = make_plan(json.loads(args.inventory.read_text(encoding="utf-8")), args.operation)
    # Exclusive output prevents accidental replacement of an already reviewed plan.
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "status": "PLAN_ONLY",
                "sha256": digest(args.output.read_bytes()),
                "count": len(plan["changes"]),
            }
        )
    )


if __name__ == "__main__":
    main()
