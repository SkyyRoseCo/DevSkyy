#!/usr/bin/env python3
"""Read-only evidence refresh; never executes providers, approvals or deployments."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import ipaddress
import json
import os
import re
import subprocess
import tempfile
import tomllib
import uuid
from pathlib import Path
from urllib import error, parse, request

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

MAX_JSON = 4 * 1024 * 1024
MAX_FILE = 128 * 1024 * 1024
SITE_HOSTS = {"skyyrose.co", "skyyrose.wpcomstaging.com", "staging-7e48-skyyrose.wpcomstaging.com"}
INTEGRITY_LIMIT = "Local corruption detection only; not an independently anchored audit or Governor economic ledger."


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def load_json(path: Path, limit: int = MAX_JSON) -> dict:
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit:
        raise ValueError("JSON artifact exceeds size limit")
    value = json.loads(
        body, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON"))
    )
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object")
    return value


def fields(value: dict, allowed: set[str], required: set[str] = frozenset()) -> None:
    if not isinstance(value, dict) or set(value) - allowed or required - set(value):
        raise ValueError("Unexpected or missing input fields")


def text(value: object, limit: int = 2000) -> str:
    if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError("Invalid text field")
    if re.search(
        r"(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]{16,}|\bsk-[A-Za-z0-9_-]{16,}|(?:api[_ -]?key|application password|authorization)\s*[:=]",
        value,
        re.I,
    ):
        raise ValueError("Credential-shaped text is forbidden")
    return value


def enum(value: object) -> str:
    value = text(value, 100)
    if not re.fullmatch(r"[A-Za-z0-9_ -]+", value):
        raise ValueError("Invalid status or evidence label")
    return value


def timestamp(value: object) -> str:
    value = text(value, 40)
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Evidence timestamps require timezone")
    return value


def public_url(value: object) -> str:
    value = text(value)
    parts = parse.urlsplit(value)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
    ):
        raise ValueError("Expected HTTPS URL without credentials or query")
    try:
        ip = ipaddress.ip_address(parts.hostname)
    except ValueError:
        ip = None
    if parts.hostname in {"localhost", "localhost.localdomain"} or (ip and not ip.is_global):
        raise ValueError("Private network URL forbidden")
    return value


def absolute_path(value: object) -> Path:
    path = Path(text(value))
    if not path.is_absolute():
        raise ValueError("Source paths must be absolute")
    return path


def source_path(value: object) -> str:
    """Resolve portable source bindings; reject relative paths escaping the checkout."""
    path = Path(text(value))
    if path.is_absolute():
        return str(path)
    resolved = (REPOSITORY_ROOT / path).resolve()
    if not resolved.is_relative_to(REPOSITORY_ROOT.resolve()):
        raise ValueError("Relative source path escapes repository")
    return str(resolved)


def config_read(path: Path) -> dict:
    cfg = load_json(path)
    fields(
        cfg,
        {
            "schema_version",
            "components",
            "repositories",
            "manifest_path",
            "e2e_state_path",
            "connector_observations_path",
            "website_observations_path",
            "integration_evidence_path",
            "live_targets",
        },
        {"schema_version", "components", "repositories"},
    )
    if cfg["schema_version"] != 1:
        raise ValueError("Unsupported schema")
    for component in cfg["components"]:
        fields(
            component,
            {
                "id",
                "category",
                "name",
                "status",
                "evidence_class",
                "summary",
                "source_paths",
                "next_action",
                "owner",
            },
            {
                "id",
                "category",
                "name",
                "status",
                "evidence_class",
                "summary",
                "source_paths",
                "next_action",
                "owner",
            },
        )
        for key, value in component.items():
            if key == "source_paths":
                component[key] = [source_path(entry) for entry in value]
            elif key in {"status", "evidence_class", "id", "category"}:
                enum(value)
            else:
                text(value)
    cfg["repositories"] = [source_path(entry) for entry in cfg["repositories"]]
    for key in (
        "manifest_path",
        "e2e_state_path",
        "connector_observations_path",
        "website_observations_path",
        "integration_evidence_path",
    ):
        if cfg.get(key):
            cfg[key] = source_path(cfg[key])
    for target in cfg.get("live_targets", []):
        fields(target, {"id", "url", "kind"}, {"id", "url", "kind"})
        enum(target["id"])
        public_url(target["url"])
        if target["kind"] not in {"website", "service"}:
            raise ValueError("Invalid live target kind")
    return cfg


def file_state(path: Path) -> dict:
    exists = path.exists()
    kind = (
        "file"
        if path.is_file()
        else "directory" if path.is_dir() else "other" if exists else "missing"
    )
    result = {
        "path": str(path),
        "exists": exists,
        "kind": kind,
        "bytes": None,
        "modified_at": None,
        "sha256": None,
    }
    if result["exists"]:
        stat = path.stat()
        result["modified_at"] = dt.datetime.fromtimestamp(stat.st_mtime, dt.UTC).isoformat()
        if kind == "file":
            result["bytes"] = stat.st_size
        if kind == "file" and stat.st_size <= MAX_FILE:
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    digest.update(chunk)
            result["sha256"] = digest.hexdigest()
    return result


def repository_state(path: Path) -> dict:
    result = {
        "path": str(path),
        "head": None,
        "branch": None,
        "staged_count": None,
        "dirty_count": None,
        "untracked_count": None,
    }
    try:

        def git(*args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(path), *args],
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            ).stdout.rstrip("\n")

        result["head"] = git("rev-parse", "HEAD")
        result["branch"] = git("rev-parse", "--abbrev-ref", "HEAD")
        statuses = git("status", "--porcelain=v1", "-z").split("\0")
        codes, skip = [], False
        for entry in statuses:
            if skip:
                skip = False
                continue
            if entry:
                codes.append(entry[:2])
                skip = "R" in entry[:2] or "C" in entry[:2]
        result.update(
            staged_count=sum(c[0] not in " ?" for c in codes),
            dirty_count=sum(c[1] not in " ?" for c in codes),
            untracked_count=codes.count("??"),
        )
    except (OSError, subprocess.SubprocessError):
        result["error"] = "Repository metadata unavailable"
    return result


def mcp_inventory(path: Path) -> list[dict]:
    if not path.exists():
        return []
    if path.stat().st_size > MAX_JSON:
        raise ValueError("MCP config exceeds size limit")
    with path.open("rb") as handle:
        servers = tomllib.load(handle).get("mcp_servers", {})
    output = []
    for name, entry in servers.items():
        name = enum(name)
        if not isinstance(entry, dict):
            raise ValueError("Invalid MCP server entry")
        url = entry.get("url")
        safe_url = None
        if url:
            parts = parse.urlsplit(text(url))
            if parts.scheme not in {"http", "https"} or not parts.hostname:
                raise ValueError("Invalid configured MCP URL")
            host = parts.hostname
            if ":" in host:
                host = f"[{host}]"
            safe_url = parse.urlunsplit(
                (parts.scheme, host + (f":{parts.port}" if parts.port else ""), "", "", "")
            )
        output.append(
            {
                "name": name,
                "url": safe_url,
                "url_scope": "configured_origin",
                "enabled": entry.get("enabled", True) is True,
                "transport": "streamable_http" if url else "stdio",
            }
        )
    return output


def manifest_integrity(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "checked": 0, "mismatches": []}
    source = load_json(path)
    root = absolute_path(source["candidate_root"]).resolve()
    entries = source.get("files")
    if (
        not isinstance(entries, list)
        or not entries
        or any(not isinstance(entry, dict) for entry in entries)
    ):
        raise ValueError("Manifest requires nonempty file entries")
    if "candidate_file_count_excluding_manifest" in source and source[
        "candidate_file_count_excluding_manifest"
    ] != len(entries):
        raise ValueError("Manifest file count mismatch")
    mismatches, seen = [], set()
    for entry in source["files"]:
        relative = Path(text(entry["path"]))
        target = (root / relative).resolve()
        if relative.is_absolute() or not target.is_relative_to(root):
            raise ValueError("Manifest path escapes candidate root")
        if target in seen:
            raise ValueError("Duplicate normalized manifest path")
        seen.add(target)
        current = file_state(target)
        expected = entry.get("candidate_sha256")
        if not re.fullmatch(r"[a-f0-9]{64}", expected or ""):
            raise ValueError("Invalid manifest digest")
        if current["sha256"] != expected:
            mismatches.append(str(relative))
    return {
        "status": "MATCH" if not mismatches else "DRIFT",
        "checked": len(source["files"]),
        "mismatches": mismatches,
        "source_reported_readiness": enum(source.get("readiness", "UNKNOWN")),
        "evidence_class": "local_file_integrity_only",
    }


def e2e_gates(path: Path) -> dict:
    if not path.exists():
        return {"overall_status": "UNKNOWN", "gates": {}, "evidence_class": "unknown"}
    source = load_json(path)
    gates = {}
    for name, gate in source.get("gates", {}).items():
        projected = {"status": enum(gate["status"])}
        if gate.get("report") is not None:
            projected["report"] = text(gate["report"])
        if "required_for_os_e2e" in gate:
            if not isinstance(gate["required_for_os_e2e"], bool):
                raise ValueError("Invalid gate flag")
            projected["required_for_os_e2e"] = gate["required_for_os_e2e"]
        gates[enum(name)] = projected
    return {
        "overall_status": enum(source.get("overall_status", "UNKNOWN")),
        "source_date": text(source.get("date", "unknown")),
        "gates": gates,
        "evidence_class": "source_reported_historical",
    }


def manual_observations(path: Path, kind: str) -> dict:
    if not path.exists():
        return (
            {"captured_at": None, "evidence_class": "unknown", "connectors": []}
            if kind == "connectors"
            else {
                "captured_at": None,
                "evidence_class": "unknown",
                "sites": [],
                "funnel": dict.fromkeys(
                    ("page_view", "view_item", "add_to_cart", "begin_checkout", "purchase")
                ),
                "limitations": ["No captured website observations"],
            }
        )
    source = load_json(path)
    base = {
        "captured_at": timestamp(source["captured_at"]),
        "evidence_class": enum(source["evidence_class"]),
    }
    allowed = (
        {"captured_at", "evidence_class", "connectors"}
        if kind == "connectors"
        else {"captured_at", "evidence_class", "sites", "funnel", "limitations"}
    )
    fields(source, allowed, allowed)
    if kind == "connectors":
        base["connectors"] = []
        for item in source["connectors"]:
            fields(
                item,
                {
                    "id",
                    "name",
                    "status",
                    "tool_count",
                    "site_connected",
                    "summary",
                    "next_action",
                    "observed_at",
                    "scope",
                },
            )
            projected = {
                k: (
                    enum(v)
                    if k in {"id", "status"}
                    else timestamp(v) if k == "observed_at" else text(v)
                )
                for k, v in item.items()
                if k not in {"tool_count", "site_connected"}
            }
            for key in ("tool_count", "site_connected"):
                value = item.get(key)
                if value is not None and (
                    (key == "tool_count" and (type(value) is not int or value < 0))
                    or (key == "site_connected" and type(value) is not bool)
                ):
                    raise ValueError("Invalid connector metric")
                projected[key] = value
            base["connectors"].append(projected)
    else:
        base["sites"] = []
        for item in source["sites"]:
            fields(
                item,
                {
                    "site_id",
                    "url",
                    "primary_domain",
                    "environment",
                    "theme",
                    "monthly_views",
                    "window_definition",
                },
            )
            projected = {
                k: public_url(v) if k == "url" else text(v)
                for k, v in item.items()
                if k not in {"monthly_views", "site_id"}
            }
            site_id = item.get("site_id")
            if not (type(site_id) is int and site_id > 0) and not (
                isinstance(site_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", site_id)
            ):
                raise ValueError("Invalid site identifier")
            projected["site_id"] = site_id
            value = item.get("monthly_views")
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("Invalid monthly views")
            projected["monthly_views"] = value
            base["sites"].append(projected)
        fields(
            source["funnel"],
            {"page_view", "view_item", "add_to_cart", "begin_checkout", "purchase"},
        )
        for value in source["funnel"].values():
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("Invalid funnel measurement")
        base.update(
            funnel={
                k: source["funnel"].get(k)
                for k in ("page_view", "view_item", "add_to_cart", "begin_checkout", "purchase")
            },
            limitations=[text(v) for v in source["limitations"]],
        )
    return base


def integration_evidence(path: Path) -> dict | None:
    """Import a bounded local replay record without upgrading economic authority."""
    if not path.is_file():
        return None
    source = load_json(path)
    allowed = {
        "schema_version",
        "captured_at",
        "evidence_class",
        "authentication",
        "checks",
        "creative",
        "governor",
        "website",
        "limitations",
    }
    fields(source, allowed, allowed)
    if (
        type(source["schema_version"]) is not int
        or source["schema_version"] != 1
        or source["evidence_class"] != "REPRODUCED_LOCAL_FIXTURES"
        or source["authentication"] != "SYNTHETIC_LOCAL"
    ):
        raise ValueError("Local replay evidence cannot claim live authentication")
    timestamp(source["captured_at"])
    checks = source["checks"]
    if not isinstance(checks, list) or not 1 <= len(checks) <= 32:
        raise ValueError("Bounded integration checks required")
    for check in checks:
        fields(check, {"name", "status", "detail"}, {"name", "status", "detail"})
        text(check["name"], 100)
        text(check["detail"])
        if check["status"] not in {"PASS", "FAIL", "BLOCKED"}:
            raise ValueError("Invalid integration check status")
    creative = source["creative"]
    creative_fields = {
        "job_id",
        "contract_id",
        "evidence_mode",
        "receipt_state",
        "artifact_count",
        "technical_passes",
        "owner_acceptance",
        "publication_authorized",
        "spend_authorized",
        "actual_spend",
        "current_provider_execution",
    }
    fields(creative, creative_fields, creative_fields)
    governor = source["governor"]
    governor_fields = {
        "job_id",
        "grant_id",
        "evidence_mode",
        "head_sequence",
        "ledger_authenticated",
        "resources",
        "operations_count",
        "owner_acceptance",
        "actual_spend",
        "current_provider_execution",
    }
    fields(governor, governor_fields, governor_fields)
    if (
        creative["job_id"] != governor["job_id"]
        or creative["evidence_mode"] != "SIMULATED"
        or governor["evidence_mode"] != "SIMULATED"
        or creative["owner_acceptance"] != "BLOCKED"
        or governor["owner_acceptance"] != "UNVERIFIED"
        or creative["publication_authorized"] is not False
        or creative["spend_authorized"] is not False
        or creative["actual_spend"] is not None
        or governor["actual_spend"] is not None
        or creative["current_provider_execution"] is not None
        or governor["current_provider_execution"] is not None
    ):
        raise ValueError("Fixture lineage or authority boundary violated")
    for record, names in (
        (creative, ("job_id", "receipt_state")),
        (governor, ("job_id", "grant_id")),
    ):
        for name in names:
            enum(record[name])
    if not isinstance(creative["contract_id"], str) or not re.fullmatch(
        r"[a-f0-9]{64}", creative["contract_id"]
    ):
        raise ValueError("Invalid replay contract digest")
    for record, names in (
        (creative, ("artifact_count", "technical_passes")),
        (governor, ("head_sequence", "operations_count")),
    ):
        for name in names:
            if type(record[name]) is not int or not 0 <= record[name] <= 100_000:
                raise ValueError("Invalid replay counter")
    if creative["technical_passes"] > creative["artifact_count"]:
        raise ValueError("Impossible artifact verification count")
    if type(governor["ledger_authenticated"]) is not bool:
        raise ValueError("Invalid local ledger verification flag")
    resources = governor["resources"]
    resource_fields = {"authorized", "consumed", "held", "available", "unspent_authorization"}
    fields(resources, resource_fields, resource_fields)
    for amounts in resources.values():
        if not isinstance(amounts, dict) or len(amounts) > 16:
            raise ValueError("Bounded resource totals required")
        for unit, amount in amounts.items():
            enum(unit)
            if not isinstance(amount, str) or not re.fullmatch(r"\d{1,24}(?:\.\d{1,18})?", amount):
                raise ValueError("Exact bounded resource amount required")
    website = source["website"]
    fields(
        website,
        {"site_id", "environment", "events", "paid_orders", "purchase_attribution"},
        {"site_id", "environment", "events", "paid_orders", "purchase_attribution"},
    )
    enum(website["site_id"])
    if website["environment"] != "test" or website["purchase_attribution"] is not None:
        raise ValueError("Fixture website data cannot become production attribution")
    for name in ("events", "paid_orders"):
        if type(website[name]) is not int or not 0 <= website[name] <= 100_000:
            raise ValueError("Invalid fixture event counter")
    if not isinstance(source["limitations"], list) or len(source["limitations"]) > 32:
        raise ValueError("Bounded evidence limitations required")
    for limitation in source["limitations"]:
        text(limitation)
    return source


def redirect_allowed(original: str, destination: str) -> bool:
    try:
        public_url(destination)
        old, new = parse.urlsplit(original), parse.urlsplit(destination)
        return old.netloc == new.netloc or (
            old.hostname in SITE_HOSTS
            and new.hostname in SITE_HOSTS
            and old.port in {None, 443}
            and new.port in {None, 443}
        )
    except ValueError:
        return False


def observe_http(target: dict) -> dict:
    class Boundary(request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if not redirect_allowed(target["url"], newurl):
                raise ValueError("Redirect crossed allowed origin boundary")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    result = {
        "id": target["id"],
        "url": target["url"],
        "kind": target["kind"],
        "captured_at": dt.datetime.now(dt.UTC).isoformat(),
        "http_status": None,
        "evidence_class": "live_public_http_only",
    }
    try:
        opener = request.build_opener(request.ProxyHandler({}), Boundary())
        with opener.open(
            request.Request(target["url"], headers={"User-Agent": "SkyyRose-Evidence-Tracker/1.0"}),
            timeout=12,
        ) as response:
            result.update(http_status=response.status, final_url=public_url(response.url))
            body = response.read(1024 * 1024 + 1)
        if len(body) > 1024 * 1024:
            raise ValueError("Response exceeded bounded read")
        if target["kind"] == "service":
            health = json.loads(body)
            if not isinstance(health, dict):
                raise ValueError("Health response must be an object")
            result["health"] = {
                k: text(health[k], 100)
                for k in ("status", "service", "version")
                if k in health and isinstance(health[k], str)
            }
            result["health"].update(
                {
                    k: health[k]
                    for k in ("dry_run_enabled", "provider_execution_enabled")
                    if type(health.get(k)) is bool
                }
            )
        else:
            html = body.decode("utf-8", errors="replace")
            result["ga4_ids"] = sorted(set(re.findall(r"\bG-[A-Z0-9]{6,}\b", html)))
            result["analytics_markers"] = {
                k: token in html.lower()
                for k, token in {
                    "google_tag_manager": "googletagmanager.com",
                    "google_analytics": "google-analytics.com",
                    "woocommerce": "woocommerce",
                    "consent_script": "consent",
                }.items()
            }
    except error.HTTPError as exc:
        result["http_status"] = exc.code
    except (OSError, ValueError, error.URLError):
        result["error"] = "HTTP observation unavailable or boundary rejected"
    return result


def safe_script_json(value: object) -> str:
    return (
        canonical(value)
        .decode()
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def atomic_write(path: Path, body: bytes) -> None:
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".tracking-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def append_events(
    directory: Path, observations: list[tuple[str, str, str, dict]], captured_at: str
) -> dict:
    log = directory / "observed-events.jsonl"
    checkpoint = directory / ".observed-events.checkpoint.json"
    with (directory / ".tracking.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        body = b""
        if log.exists():
            with log.open("rb") as handle:
                body = handle.read(32 * 1024 * 1024 + 1)
        if len(body) > 32 * 1024 * 1024 or (body and not body.endswith(b"\n")):
            raise ValueError("Observation history is oversized or truncated")
        count, previous = 0, "0" * 64
        for line in body.splitlines():
            event = json.loads(line)
            fields(
                event,
                {
                    "observation_id",
                    "captured_at",
                    "kind",
                    "component_id",
                    "evidence_class",
                    "data",
                    "prev_hash",
                    "hash",
                },
                {"hash", "prev_hash", "data"},
            )
            saved = event.pop("hash")
            if (
                event["prev_hash"] != previous
                or hashlib.sha256(canonical(event)).hexdigest() != saved
            ):
                raise ValueError("Observation history hash chain mismatch")
            previous, count = saved, count + 1
        expected = {"event_count": count, "last_hash": previous}
        if checkpoint.exists():
            if load_json(checkpoint) != expected:
                raise ValueError("Observation history differs from checkpoint; refusing reset")
        elif count:
            raise ValueError("Existing history has no checkpoint; refusing adoption")
        lines = []
        for kind, component_id, evidence_class, data in observations:
            event = {
                "observation_id": str(uuid.uuid4()),
                "captured_at": captured_at,
                "kind": kind,
                "component_id": component_id,
                "evidence_class": evidence_class,
                "data": data,
                "prev_hash": previous,
            }
            previous = hashlib.sha256(canonical(event)).hexdigest()
            event["hash"] = previous
            lines.append(canonical(event) + b"\n")
            count += 1
        with log.open("ab") as handle:
            handle.write(b"".join(lines))
            handle.flush()
            os.fsync(handle.fileno())
        atomic_write(checkpoint, canonical({"event_count": count, "last_hash": previous}) + b"\n")
        return {
            "path": str(log.resolve()),
            "event_count": count,
            "last_hash": previous,
            "chain_verified": True,
            "integrity_limitation": INTEGRITY_LIMIT,
        }


def refresh(config: Path, output: Path, live: bool = False, mcp_config: Path | None = None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".refresh.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _refresh(config, output, live, mcp_config)


def _refresh(config: Path, output: Path, live: bool, mcp_config: Path | None) -> dict:
    config_before = file_state(config)
    cfg = config_read(config)
    template = config.parent / "dashboard-template.html"
    if not template.is_file() or template.stat().st_size > MAX_JSON:
        raise ValueError("Dashboard template missing or exceeds size limit")
    template_before = file_state(template)
    template_body = template.read_text()
    if template_body.count("__TRACKING_DATA__") != 1:
        raise ValueError("Dashboard must have exactly one data marker")
    now = dt.datetime.now(dt.UTC).isoformat()
    output.mkdir(parents=True, exist_ok=True)
    connector_path = Path(
        cfg.get("connector_observations_path") or config.parent / "connector-observations.json"
    )
    website_path = Path(
        cfg.get("website_observations_path") or config.parent / "website-observations.json"
    )
    files = {p for c in cfg["components"] for p in c["source_paths"]}
    files.update(
        str(p.resolve()) for p in (config, Path(__file__), template, connector_path, website_path)
    )
    files.update(
        cfg[k]
        for k in ("manifest_path", "e2e_state_path", "integration_evidence_path")
        if cfg.get(k)
    )
    snapshot = {
        "schema_version": 1,
        "captured_at": now,
        "mode": "live" if live else "offline",
        "components": cfg["components"],
        "source_files": [file_state(Path(p)) for p in sorted(files)],
        "config_sha256": config_before["sha256"],
        "collector_sha256": file_state(Path(__file__))["sha256"],
        "repository_state": [repository_state(Path(p)) for p in cfg["repositories"]],
        "mcp_inventory": mcp_inventory(mcp_config or Path.home() / ".codex/config.toml"),
        "live_observations": [],
    }
    snapshot["manifest_integrity"] = (
        manifest_integrity(Path(cfg["manifest_path"]))
        if cfg.get("manifest_path")
        else {"status": "UNKNOWN"}
    )
    snapshot["e2e_gates"] = (
        e2e_gates(Path(cfg["e2e_state_path"]))
        if cfg.get("e2e_state_path")
        else {"overall_status": "UNKNOWN", "gates": {}}
    )
    connectors = manual_observations(connector_path, "connectors")
    snapshot["connectors"], snapshot["connector_capture"] = connectors["connectors"], {
        k: connectors[k] for k in ("captured_at", "evidence_class")
    }
    snapshot["website"] = manual_observations(website_path, "website")
    snapshot["integration"] = (
        integration_evidence(Path(cfg["integration_evidence_path"]))
        if cfg.get("integration_evidence_path")
        else None
    )
    if live:
        snapshot["live_observations"] = [observe_http(t) for t in cfg.get("live_targets", [])]
    for before in [config_before, template_before, *snapshot["source_files"]]:
        if file_state(Path(before["path"])) != before:
            raise ValueError(
                "Tracking source changed during refresh; refusing mismatched provenance"
            )
    events = [
        (
            "config_inventory",
            "mcp",
            "local_configuration_only",
            {"servers": snapshot["mcp_inventory"]},
        ),
        (
            "repository_state",
            "repositories",
            "local_observation",
            {"repositories": snapshot["repository_state"]},
        ),
        (
            "manifest_integrity",
            "candidate",
            "local_file_integrity_only",
            snapshot["manifest_integrity"],
        ),
        (
            "website_aggregate_snapshot",
            "website",
            snapshot["website"]["evidence_class"],
            snapshot["website"],
        ),
        ("connector_snapshot", "connectors", connectors["evidence_class"], connectors),
        (
            "source_tracking",
            "components",
            "curated_source_reported",
            {
                "components": snapshot["components"],
                "files": snapshot["source_files"],
                "e2e_gates": snapshot["e2e_gates"],
            },
        ),
    ]
    events += [
        ("public_http_observation", t["id"], t["evidence_class"], t)
        for t in snapshot["live_observations"]
    ]
    if snapshot["integration"] is not None:
        events.append(
            (
                "local_e2e_validation_snapshot",
                "local-integration",
                "REPRODUCED_LOCAL_FIXTURES",
                snapshot["integration"],
            )
        )
    snapshot["history"] = append_events(output, events, now)
    atomic_write(
        output / "snapshot.json",
        json.dumps(snapshot, indent=2, ensure_ascii=False, allow_nan=False).encode() + b"\n",
    )
    rows = [
        "# Production, Creative and Website Tracking",
        "",
        f"Refreshed: {now} ({snapshot['mode']}). Historical evidence dates retain their original scope.",
        "",
        "| Component | Status | Evidence | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for component in snapshot["components"]:
        rows.append(
            "| "
            + " | ".join(
                component[k].replace("|", "\\|")
                for k in ("name", "status", "evidence_class", "next_action")
            )
            + " |"
        )
    rows.extend(
        [
            "",
            "Unmeasured funnel metrics remain null. HTTP health does not authorize paid transactions or releases.",
            "",
            INTEGRITY_LIMIT,
            "",
        ]
    )
    atomic_write(output / "STATUS.md", "\n".join(rows).encode())
    atomic_write(
        output / "dashboard.html",
        template_body.replace("__TRACKING_DATA__", safe_script_json(snapshot)).encode(),
    )
    return snapshot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("sources.json"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    try:
        result = refresh(
            args.config.resolve(), (args.output_dir or args.config.parent).resolve(), args.live
        )
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise SystemExit(
            f"Tracking refresh refused ({type(exc).__name__}); validate schema and history. No secret values printed."
        ) from None
    print(
        f"Refreshed {len(result['components'])} components; {result['history']['event_count']} observation events. Mode: {result['mode']}."
    )
