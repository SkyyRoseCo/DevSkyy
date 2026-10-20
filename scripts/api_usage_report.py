#!/usr/bin/env python3
"""Per-API-key usage and cost report for one UTC day (Anthropic + OpenAI).

Read-only and free: it calls only the providers' admin reporting endpoints,
which bill nothing. It needs ADMIN keys, not inference keys:

    ANTHROPIC_ADMIN_KEY  sk-ant-admin...  Claude Console -> Settings -> Admin keys
    OPENAI_ADMIN_KEY     sk-admin-...     platform.openai.com -> Settings -> Admin keys

Keys are read from the shell, then .env / .env.local, and are never printed.

Usage:
    python scripts/api_usage_report.py                       # today (UTC), both providers
    python scripts/api_usage_report.py --date 2026-10-17
    python scripts/api_usage_report.py --provider openai --json

Notes:
- A day is the provider's UTC day bucket; data lags the API by ~5 minutes.
- Anthropic's cost API cannot split cost by key. Per-key Anthropic dollars are an
  estimate: each (model, token type) cost for the day is allocated to keys in
  proportion to their tokens. Costs with no token match (web search, code
  execution) are listed as unallocated. OpenAI reports cost per key directly.
- Console / playground usage carries no key and is shown under NO_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import UTC, date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILES = (".env", ".env.local")
ANTHROPIC_BASE = "https://api.anthropic.com/v1/organizations"
OPENAI_BASE = "https://api.openai.com/v1/organization"
ANTHROPIC_VERSION = "2023-06-01"
USER_AGENT = "DevSkyy-api-usage-report/1.0"
ADMIN_KEYS = {
    "anthropic": ("ANTHROPIC_ADMIN_KEY", "sk-ant-admin"),
    "openai": ("OPENAI_ADMIN_KEY", "sk-admin-"),
}
MAX_PAGES = 100
NO_KEY = "(no key: console / playground)"
CENTS = Decimal(100)
ANTHROPIC_TOKEN_TYPES = (
    "uncached_input_tokens",
    "cache_creation.ephemeral_5m_input_tokens",
    "cache_creation.ephemeral_1h_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


class ReportError(RuntimeError):
    """A provider call failed or returned data this script cannot trust."""


# --------------------------------------------------------------------------- keys / http


def load_admin_key(provider: str) -> str | None:
    """Return the provider's admin key from the shell or repo env files, or None."""
    name, prefix = ADMIN_KEYS[provider]
    value = os.environ.get(name, "").strip()
    for env_file in ENV_FILES:
        if value:
            break
        path = REPO_ROOT / env_file
        if path.is_file():
            value = (dotenv_values(path, interpolate=False).get(name) or "").strip()
    if not value:
        return None
    if not value.startswith(prefix):
        raise ReportError(f"{name} is not an admin key (expected prefix {prefix}...)")
    return value


def make_client(
    provider: str, key: str, transport: httpx.BaseTransport | None = None
) -> httpx.Client:
    if provider == "anthropic":
        headers = {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}
    else:
        headers = {"Authorization": f"Bearer {key}"}
    return httpx.Client(
        headers={**headers, "User-Agent": USER_AGENT},
        timeout=httpx.Timeout(30.0),
        transport=transport,
    )


def get_json(client: httpx.Client, url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = client.get(url, params=params)
    if response.status_code != 200:
        raise ReportError(f"GET {url} -> HTTP {response.status_code}: {_error_text(response)}")
    return response.json()


def _error_text(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:300]
    error = body.get("error", body) if isinstance(body, dict) else body
    if isinstance(error, dict):
        error = error.get("message") or error
    return str(error)[:300]


def day_results(payload: dict[str, Any], day_start: datetime) -> list[dict[str, Any]]:
    """Return the results of the bucket for ``day_start``; fail on any other bucket."""
    data = payload.get("data")
    if not isinstance(data, list):
        raise ReportError("response has no 'data' list")
    if not data:
        return []
    bucket = data[0]
    if "starting_at" in bucket:
        start = datetime.fromisoformat(str(bucket["starting_at"]).replace("Z", "+00:00"))
    else:
        start = datetime.fromtimestamp(int(bucket["start_time"]), UTC)
    if start != day_start:
        raise ReportError(
            f"provider returned bucket {start.isoformat()}, expected {day_start.isoformat()}"
        )
    return list(bucket.get("results") or [])


def usd(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.0001'))}"


# --------------------------------------------------------------------------- anthropic


def fetch_anthropic(client: httpx.Client, day_start: datetime) -> dict[str, Any]:
    base = {
        "starting_at": day_start.isoformat().replace("+00:00", "Z"),
        "bucket_width": "1d",
        "limit": 1,
    }
    usage_page = get_json(
        client,
        f"{ANTHROPIC_BASE}/usage_report/messages",
        {**base, "group_by[]": ["api_key_id", "model"]},
    )
    cost_page = get_json(
        client, f"{ANTHROPIC_BASE}/cost_report", {**base, "group_by[]": ["description"]}
    )
    usage = day_results(usage_page, day_start)
    costs = day_results(cost_page, day_start)
    return build_anthropic_report(usage, costs, anthropic_key_names(client))


def anthropic_key_names(client: httpx.Client) -> dict[str, str]:
    names: dict[str, str] = {}
    params: dict[str, Any] = {"limit": 1000}
    for _ in range(MAX_PAGES):
        page = get_json(client, f"{ANTHROPIC_BASE}/api_keys", params)
        for key in page.get("data") or []:
            hint = key.get("partial_key_hint")
            names[key["id"]] = (key.get("name") or key["id"]) + (f" [{hint}]" if hint else "")
        if not page.get("has_more"):
            return names
        params = {**params, "after_id": page["last_id"]}
    raise ReportError("Anthropic api_keys listing exceeded MAX_PAGES")


def anthropic_tokens(result: dict[str, Any]) -> dict[str, int]:
    cache = result.get("cache_creation") or {}
    return {
        "uncached_input_tokens": int(result.get("uncached_input_tokens") or 0),
        "cache_creation.ephemeral_5m_input_tokens": int(
            cache.get("ephemeral_5m_input_tokens") or 0
        ),
        "cache_creation.ephemeral_1h_input_tokens": int(
            cache.get("ephemeral_1h_input_tokens") or 0
        ),
        "cache_read_input_tokens": int(result.get("cache_read_input_tokens") or 0),
        "output_tokens": int(result.get("output_tokens") or 0),
    }


def _anthropic_cost_pools(
    costs: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], Decimal], list[dict[str, str]], Decimal]:
    """Split cost lines into per-(model, token type) pools and everything else."""
    pools: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    lines: list[dict[str, str]] = []
    total = Decimal(0)
    for line in costs:
        amount = Decimal(str(line.get("amount") or "0")) / CENTS
        total += amount
        lines.append({"description": line.get("description") or "(total)", "cost_usd": usd(amount)})
        if line.get("cost_type") == "tokens" and line.get("model") and line.get("token_type"):
            pools[(line["model"], line["token_type"])] += amount
    return pools, lines, total


def build_anthropic_report(
    usage: list[dict[str, Any]], costs: list[dict[str, Any]], names: dict[str, str]
) -> dict[str, Any]:
    pools, cost_lines, total = _anthropic_cost_pools(costs)
    pool_tokens: dict[tuple[str, str], int] = defaultdict(int)
    rows = []
    for result in usage:
        model = result.get("model") or "(unknown model)"
        tokens = anthropic_tokens(result)
        for token_type, count in tokens.items():
            pool_tokens[(model, token_type)] += count
        rows.append((result.get("api_key_id"), model, tokens, result))

    keys: dict[str | None, dict[str, Any]] = {}
    allocated = Decimal(0)
    for key_id, model, tokens, result in rows:
        cost = sum(
            (
                pools[(model, tt)] * count / pool_tokens[(model, tt)]
                for tt, count in tokens.items()
                if count and pool_tokens[(model, tt)]
            ),
            Decimal(0),
        )
        allocated += cost
        entry = keys.setdefault(key_id, {"cost": Decimal(0), "models": []})
        entry["cost"] += cost
        web = int((result.get("server_tool_use") or {}).get("web_search_requests") or 0)
        entry["models"].append(
            {
                "model": model,
                "tokens": tokens,
                "web_search_requests": web,
                "est_cost_usd": usd(cost),
            }
        )
    return {
        "provider": "anthropic",
        "total_cost_usd": usd(total),
        "unallocated_cost_usd": usd(total - allocated),
        "cost_is_estimate_per_key": True,
        "keys": _key_rows(keys, names, cost_field="est_cost_usd"),
        "cost_lines": cost_lines,
    }


def _key_rows(
    keys: dict[str | None, dict[str, Any]], names: dict[str, str], cost_field: str
) -> list[dict]:
    rows = [
        {
            "key_id": key_id,
            "name": names.get(key_id, key_id) if key_id else NO_KEY,
            cost_field: usd(entry["cost"]),
            **{k: v for k, v in entry.items() if k != "cost"},
        }
        for key_id, entry in keys.items()
    ]
    return sorted(rows, key=lambda row: Decimal(row[cost_field]), reverse=True)


# --------------------------------------------------------------------------- openai


def fetch_openai(client: httpx.Client, day_start: datetime) -> dict[str, Any]:
    base = {"start_time": int(day_start.timestamp()), "bucket_width": "1d", "limit": 1}
    by_key_model = {**base, "group_by": ["api_key_id", "model"]}
    costs = day_results(
        get_json(client, f"{OPENAI_BASE}/costs", {**base, "group_by": ["api_key_id", "line_item"]}),
        day_start,
    )
    completions = day_results(
        get_json(client, f"{OPENAI_BASE}/usage/completions", by_key_model), day_start
    )
    images = day_results(get_json(client, f"{OPENAI_BASE}/usage/images", by_key_model), day_start)
    return build_openai_report(costs, completions, images, openai_key_names(client))


def _paginate_openai(
    client: httpx.Client, url: str, params: dict[str, Any]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for _ in range(MAX_PAGES):
        page = get_json(client, url, params)
        items.extend(page.get("data") or [])
        if not page.get("has_more"):
            return items
        params = {**params, "after": page["last_id"]}
    raise ReportError(f"{url} listing exceeded MAX_PAGES")


def openai_key_names(client: httpx.Client) -> dict[str, str]:
    names: dict[str, str] = {}
    projects = _paginate_openai(
        client, f"{OPENAI_BASE}/projects", {"limit": 100, "include_archived": "true"}
    )
    for project in projects:
        keys = _paginate_openai(
            client,
            f"{OPENAI_BASE}/projects/{project['id']}/api_keys",
            {"limit": 100, "owner_project_access": "any"},
        )
        for key in keys:
            label = key.get("name") or key["id"]
            hint = key.get("redacted_value")
            names[key["id"]] = (
                f"{label} [{hint}] ({project.get('name') or project['id']})" if hint else label
            )
    return names


def _openai_entry(keys: dict[str | None, dict[str, Any]], key_id: str | None) -> dict[str, Any]:
    return keys.setdefault(key_id, {"cost": Decimal(0), "line_items": [], "models": {}})


def build_openai_report(
    costs: list[dict[str, Any]],
    completions: list[dict[str, Any]],
    images: list[dict[str, Any]],
    names: dict[str, str],
) -> dict[str, Any]:
    keys: dict[str | None, dict[str, Any]] = {}
    total = Decimal(0)
    for line in costs:
        amount = Decimal(str((line.get("amount") or {}).get("value") or 0))
        total += amount
        entry = _openai_entry(keys, line.get("api_key_id"))
        entry["cost"] += amount
        entry["line_items"].append(
            {"line_item": line.get("line_item") or "(total)", "cost_usd": usd(amount)}
        )
    for result in completions:
        model = _openai_entry(keys, result.get("api_key_id"))["models"].setdefault(
            result.get("model") or "(unknown model)", _empty_openai_model()
        )
        model["requests"] += int(result.get("num_model_requests") or 0)
        model["input_tokens"] += int(result.get("input_tokens") or 0)
        model["cached_input_tokens"] += int(result.get("input_cached_tokens") or 0)
        model["output_tokens"] += int(result.get("output_tokens") or 0)
    for result in images:
        model = _openai_entry(keys, result.get("api_key_id"))["models"].setdefault(
            result.get("model") or "(unknown model)", _empty_openai_model()
        )
        model["requests"] += int(result.get("num_model_requests") or 0)
        model["images"] += int(result.get("images") or 0)
    for entry in keys.values():
        entry["models"] = [{"model": name, **stats} for name, stats in entry["models"].items()]
    return {
        "provider": "openai",
        "total_cost_usd": usd(total),
        "cost_is_estimate_per_key": False,
        "keys": _key_rows(keys, names, cost_field="cost_usd"),
    }


def _empty_openai_model() -> dict[str, int]:
    return {
        "requests": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "images": 0,
    }


# --------------------------------------------------------------------------- output / cli


def render_text(report: dict[str, Any]) -> str:
    estimate = report["cost_is_estimate_per_key"]
    cost_field = "est_cost_usd" if estimate else "cost_usd"
    out = [f"== {report['provider'].upper()}  total ${report['total_cost_usd']}"]
    if estimate:
        out.append(
            f"   per-key $ is a token-proportional estimate; unallocated ${report['unallocated_cost_usd']}"
        )
    if not report["keys"]:
        out.append("   no usage recorded for this day")
    for key in report["keys"]:
        out.append(f"-- {key['name']}  ${key[cost_field]}")
        for model in key["models"]:
            stats = model.get("tokens", model)
            detail = ", ".join(
                f"{k}={v:,}" for k, v in stats.items() if isinstance(v, int) and v and k != "model"
            )
            extra = (
                f", web_search={model['web_search_requests']:,}"
                if model.get("web_search_requests")
                else ""
            )
            cost = f"  ${model['est_cost_usd']}" if "est_cost_usd" in model else ""
            out.append(f"     {model['model']}{cost}: {detail or 'no tokens'}{extra}")
        for line in key.get("line_items", []):
            out.append(f"     $ {line['line_item']}: ${line['cost_usd']}")
    for line in report.get("cost_lines", []):
        out.append(f"   $ {line['description']}: ${line['cost_usd']}")
    return "\n".join(out)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--date", type=date.fromisoformat, default=datetime.now(UTC).date(), help="UTC day"
    )
    parser.add_argument("--provider", choices=("all", "anthropic", "openai"), default="all")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    return parser.parse_args(argv)


FETCHERS = {"anthropic": fetch_anthropic, "openai": fetch_openai}


def main(argv: list[str] | None = None, transport: httpx.BaseTransport | None = None) -> int:
    args = parse_args(argv)
    day_start = datetime.combine(args.date, time.min, tzinfo=UTC)
    providers = list(FETCHERS) if args.provider == "all" else [args.provider]
    reports, skipped = [], []
    try:
        for provider in providers:
            key = load_admin_key(provider)
            if key is None:
                skipped.append(
                    f"{provider}: {ADMIN_KEYS[provider][0]} not set (shell, {', '.join(ENV_FILES)})"
                )
                continue
            with make_client(provider, key, transport) as client:
                reports.append(FETCHERS[provider](client, day_start))
    except (ReportError, httpx.HTTPError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    for line in skipped:
        print(f"SKIP  {line}", file=sys.stderr)
    if not reports:
        print("FAIL  no provider could be queried: set an admin key", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"date": args.date.isoformat(), "reports": reports}, indent=2))
    else:
        print(f"API usage for {args.date.isoformat()} (UTC)\n")
        print("\n\n".join(render_text(report) for report in reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
