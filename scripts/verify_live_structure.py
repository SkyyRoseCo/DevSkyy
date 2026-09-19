#!/usr/bin/env python3
"""Structural deploy verification for a SkyyRose WordPress site.

Called by scripts/deploy-theme.sh::verify_live() AFTER the curl-based
HTTP / size / PHP-error checks pass. Uses Scrapling to fetch live pages
and assert that template-specific DOM markers exist - catches regressions
where WordPress returns HTTP 200 but a template fell back to a default
page or stripped a critical section.

The target URL and the theme folder (slug) come from the caller or the
environment - there is no literal production default. The page registry is
selected by the LIVE theme's Text Domain (read from
/wp-content/themes/<slug>/style.css): "skyyrose" -> the V1 registry,
"skyyrose-flagship-2" -> the V2 registry. Anything else fails closed.

Usage:
  verify_live_structure.py --url URL --theme-slug SLUG            # homepage only
  verify_live_structure.py --url URL --theme-slug SLUG --page black-rose
  verify_live_structure.py --url URL --theme-slug SLUG --all
  verify_live_structure.py --list [--text-domain skyyrose-flagship-2]
  PUBLIC_URL=https://... WP_THEME_PATH=/.../skyyrose-flagship-2 verify_live_structure.py --all

Exit codes:
  0 - all assertions passed for every page checked
  2 - one or more assertions failed (real regression) OR usage error
      (missing/unknown URL, slug, page or text domain)
  3 - environment problem (scrapling missing, total network failure)
      Bash deploy script logs as warning; does NOT trigger rollback.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin

# The page registries live beside this script; make them importable whether it
# runs as `python scripts/verify_live_structure.py` or is loaded by path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
# E402: must follow the sys.path insert. F401: theme_css_assertion is re-exported.
from verify_live_registries import (  # noqa: E402,F401
    KNOWN_TEXT_DOMAINS,
    Assertion,
    Page,
    PricingCheck,
    Registry,
    parse_text_domain,
    select_registry,
    theme_css_assertion,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 25

# Cache-bust query param appended to every fetched URL unless --no-cache-bust.
# Bypasses Jetpack Boost page cache so we observe a fresh render.
CACHE_BUST_PARAM = "deploy_verify"

# Number of fetch attempts per page (initial + retries). Set to 1 to disable
# retries. Connection-level errors trigger backoff; HTTP errors do not retry
# (a 500 won't fix itself in 1.5s, but a TLS handshake hiccup might).
FETCH_RETRY_ATTEMPTS = 2
FETCH_RETRY_BACKOFF_SECONDS = 1.5


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


class FetchError(Exception):
    """Transport-layer fetch failure (connection, TLS, timeout)."""


@dataclass(frozen=True)
class CheckResult:
    assertion: Assertion
    actual: int

    @property
    def passed(self) -> bool:
        if self.actual < self.assertion.min_count:
            return False
        return self.assertion.max_count is None or self.actual <= self.assertion.max_count


@dataclass
class PageReport:
    page: Page
    url: str
    http_status: int
    fetched: bool
    fetch_error: str | None = None
    results: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.fetched and self.http_status == 200 and all(r.passed for r in self.results)


# ---------------------------------------------------------------------------
# Target resolution -- fail CLOSED, no literal production default
# ---------------------------------------------------------------------------


def resolve_base_url(cli_value: str | None, env: dict[str, str] | None = None) -> str | None:
    env = os.environ if env is None else env
    value = cli_value or env.get("PUBLIC_URL") or env.get("WORDPRESS_URL") or ""
    value = value.split("?", 1)[0].rstrip("/")
    return value or None


def resolve_theme_slug(cli_value: str | None, env: dict[str, str] | None = None) -> str | None:
    env = os.environ if env is None else env
    value = cli_value or env.get("THEME_SLUG") or ""
    if not value and env.get("WP_THEME_PATH"):
        value = os.path.basename(env["WP_THEME_PATH"].rstrip("/"))
    return value or None


# ---------------------------------------------------------------------------
# Fetch + evaluate
# ---------------------------------------------------------------------------


def _import_fetcher():
    """Import-late so missing scrapling triggers exit 3, not crash on argparse."""
    try:
        from scrapling.fetchers import Fetcher  # noqa: PLC0415
    except ImportError as exc:
        print(f"[SKIP] Scrapling not available: {exc}", file=sys.stderr)
        print(
            "[SKIP] Install via: source .venv/bin/activate && pip install 'scrapling[all]'",
            file=sys.stderr,
        )
        sys.exit(3)
    return Fetcher


def _fetch_once(fetcher, url: str, timeout: int):
    """Single fetch attempt — wraps any exception into a FetchError."""
    try:
        return fetcher.get(url, timeout=timeout)
    except (OSError, TimeoutError) as exc:
        raise FetchError(f"{type(exc).__name__}: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 — last-resort wrapper for SDK errors
        raise FetchError(f"{type(exc).__name__}: {exc}") from exc


def fetch_page(fetcher, url: str, timeout: int) -> tuple[object | None, str | None]:
    """Fetch with one retry on transport errors. Returns (response, error_str)."""
    last_error: str | None = None
    for attempt in range(FETCH_RETRY_ATTEMPTS):
        try:
            return _fetch_once(fetcher, url, timeout), None
        except FetchError as exc:
            last_error = str(exc)
            is_last = attempt + 1 >= FETCH_RETRY_ATTEMPTS
            if not is_last:
                time.sleep(FETCH_RETRY_BACKOFF_SECONDS * (attempt + 1))
    return None, last_error


def _response_text(response) -> str:
    """Decode a Scrapling Response body (bytes per the v0.4+ contract)."""
    body = getattr(response, "body", b"")
    if isinstance(body, bytes):
        return body.decode(getattr(response, "encoding", None) or "utf-8", errors="replace")
    return str(body)


def fetch_live_text_domain(
    fetcher, base_url: str, theme_slug: str, timeout: int, cache_bust: bool
) -> tuple[str | None, str | None]:
    """Read the live theme's Text Domain. Returns (text_domain, error).

    Both None-with-error outcomes (fetch failure, non-200, unparseable) are
    reported to the caller, which fails closed -- guessing a registry would
    turn a wrong-theme deploy into a green structural check.
    """
    url = _build_url(base_url, f"/wp-content/themes/{theme_slug}/style.css", cache_bust)
    response, err = fetch_page(fetcher, url, timeout)
    if response is None:
        return None, f"style.css fetch failed: {err}"
    status = getattr(response, "status", None)
    if status != 200:
        return None, f"style.css returned HTTP {status} at {url}"
    domain = parse_text_domain(_response_text(response))
    if not domain:
        return None, f"style.css at {url} has no parseable Text Domain header"
    return domain, None


def evaluate_assertions(response, assertions: tuple[Assertion, ...]) -> list[CheckResult]:
    """Run every selector against `response` and produce CheckResult per assertion.

    A selector that raises is treated as `count=0` plus a stderr warning —
    the assertion fails (since min_count >= 1 in nearly all cases) but the
    rest of the page's checks still run, so the operator gets a complete
    picture in one pass.
    """
    results: list[CheckResult] = []
    for assertion in assertions:
        try:
            matches = response.css(assertion.selector)
            count = len(matches) if matches is not None else 0
        except (AttributeError, TypeError, ValueError, RuntimeError) as exc:
            print(
                f"  [WARN] Selector {assertion.selector!r} raised {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            count = 0
        results.append(CheckResult(assertion, count))
    return results


def check_no_forbidden_text(response, checks: tuple[PricingCheck, ...]) -> list[CheckResult]:
    """
    Assert that no matched element contains a forbidden text string.

    Returns one synthetic CheckResult per PricingCheck where:
    - actual=0  → no forbidden text found (PASS, min_count=0, max_count=0)
    - actual=N  → N elements with forbidden text (FAIL)
    """
    results: list[CheckResult] = []
    for check in checks:
        synthetic = Assertion(
            selector=check.selector,
            min_count=0,
            label=check.label,
            max_count=0,
        )
        try:
            elements = response.css(check.selector) or []
            hit_count = sum(
                1
                for el in elements
                if any(forbidden in (el.text or "") for forbidden in check.forbidden_texts)
            )
        except (AttributeError, TypeError, ValueError, RuntimeError) as exc:
            print(
                f"  [WARN] PricingCheck selector {check.selector!r} raised "
                f"{type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            hit_count = 0
        results.append(CheckResult(synthetic, hit_count))
    return results


def _build_url(base_url: str, path: str, cache_bust: bool) -> str:
    url = urljoin(base_url + "/", path.lstrip("/"))
    if cache_bust:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{CACHE_BUST_PARAM}={int(time.time())}"
    return url


def check_page(
    fetcher, page: Page, registry: Registry, base_url: str, timeout: int, cache_bust: bool
) -> PageReport:
    url = _build_url(base_url, page.path, cache_bust)

    response, err = fetch_page(fetcher, url, timeout)
    if response is None:
        return PageReport(page=page, url=url, http_status=0, fetched=False, fetch_error=err)

    # Defensive: a malformed response object without `status` shouldn't be
    # silently treated as HTTP 0 — it's a transport-layer mismatch worth
    # flagging as a fetch error so the operator knows the contract broke.
    if not hasattr(response, "status"):
        return PageReport(
            page=page,
            url=url,
            http_status=0,
            fetched=False,
            fetch_error="response object missing 'status' attribute",
        )

    status = response.status
    if status != 200:
        return PageReport(page=page, url=url, http_status=status, fetched=True)

    results = evaluate_assertions(response, registry.global_assertions + page.assertions)
    results += check_no_forbidden_text(response, registry.pricing_checks)
    return PageReport(page=page, url=url, http_status=status, fetched=True, results=results)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _format_check_line(result: CheckResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    a = result.assertion
    return (
        f"  [{status}] {a.label}  "
        f"(selector={a.selector!r}, found={result.actual}, {a.bounds_str()})"
    )


def print_page_report(report: PageReport) -> None:
    print(f"=== {report.page.name}  ({report.url}) ===")
    if not report.fetched:
        print(f"  [FAIL] Fetch error: {report.fetch_error}")
        return
    if report.http_status != 200:
        print(f"  [FAIL] HTTP {report.http_status} (expected 200)")
        return
    for r in report.results:
        print(_format_check_line(r))


def _summary_detail(report: PageReport) -> str:
    if not report.fetched:
        return "fetch error"
    if report.http_status != 200:
        return f"HTTP {report.http_status}"
    passed_n = sum(1 for r in report.results if r.passed)
    return f"{passed_n}/{len(report.results)} assertions"


def print_summary(reports: list[PageReport]) -> None:
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in reports:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.page.name:<30} {_summary_detail(r)}")
    failed = [r for r in reports if not r.passed]
    print(f"\nResult: {len(reports) - len(failed)}/{len(reports)} pages passed")
    if failed:
        print(f"Failed pages: {', '.join(r.page.name for r in failed)}")


def list_registry(registry: Registry) -> None:
    print(f"Registry for text domain: {registry.text_domain}")
    print("Global assertions (run on every page):")
    for a in registry.global_assertions:
        print(f"  - {a.label}  ({a.bounds_str()})")
    print()
    print(f"Registered pages ({len(registry.pages)}):\n")
    for key, page in registry.pages.items():
        print(f"  {key:<22} -> {page.path}")
        print(f"  {'':<22}    {page.name}")
        for a in page.assertions:
            print(f"  {'':<22}    - {a.label}  ({a.bounds_str()})")
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _resolve_pages(args: argparse.Namespace, registry: Registry) -> list[Page]:
    """Translate --all / --page args into the actual page list to verify.

    Raises SystemExit(2) with a useful message on unknown --page values
    so the operator sees the available registry without re-running --list.
    """
    if args.all:
        return list(registry.pages.values())
    if args.page not in registry.pages:
        known = ", ".join(sorted(registry.pages))
        print(
            f"Unknown page: {args.page!r} for text domain {registry.text_domain}\n"
            f"Known pages: {known}\nRun with --list for full assertion details.",
            file=sys.stderr,
        )
        sys.exit(2)
    return [registry.pages[args.page]]


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--url", default=None, help="Base URL (else $PUBLIC_URL, else $WORDPRESS_URL; required)"
    )
    parser.add_argument(
        "--theme-slug",
        default=None,
        help="Live theme folder (else $THEME_SLUG, else basename of $WP_THEME_PATH; required)",
    )
    parser.add_argument(
        "--text-domain",
        default=None,
        choices=KNOWN_TEXT_DOMAINS,
        help="Skip the live style.css read and use this registry (tests / --list)",
    )
    parser.add_argument(
        "--page", default="home", help="Page name from registry (default: home). See --list."
    )
    parser.add_argument(
        "--all", action="store_true", help="Verify every registered page (overrides --page)"
    )
    parser.add_argument("--list", action="store_true", help="Print page registry and exit")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Fetch timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--no-cache-bust",
        action="store_true",
        help=f"Skip ?{CACHE_BUST_PARAM}=<ts> query string",
    )
    return parser


def _list_registries(args: argparse.Namespace) -> int:
    slug = resolve_theme_slug(args.theme_slug) or "<theme-slug>"
    domains = (args.text_domain,) if args.text_domain else KNOWN_TEXT_DOMAINS
    for domain in domains:
        list_registry(select_registry(domain, slug))
    return 0


def _resolve_target(args: argparse.Namespace) -> tuple[str, str] | None:
    """(base_url, theme_slug) from CLI/env, or None after printing why not."""
    base_url = resolve_base_url(args.url)
    if not base_url:
        print("No target URL: pass --url or set PUBLIC_URL / WORDPRESS_URL", file=sys.stderr)
        return None
    theme_slug = resolve_theme_slug(args.theme_slug)
    if not theme_slug:
        print("No theme slug: pass --theme-slug or set THEME_SLUG / WP_THEME_PATH", file=sys.stderr)
        return None
    return base_url, theme_slug


def _live_registry(
    args: argparse.Namespace, fetcher, base_url: str, theme_slug: str, cache_bust: bool
) -> Registry | int:
    """The registry for the live theme, or the exit code when it cannot be established."""
    text_domain = args.text_domain
    if text_domain is None:
        text_domain, err = fetch_live_text_domain(
            fetcher, base_url, theme_slug, args.timeout, cache_bust
        )
        if text_domain is None:
            print(f"Cannot establish live theme identity: {err}", file=sys.stderr)
            return 3 if err and "fetch failed" in err else 2
    try:
        registry = select_registry(text_domain, theme_slug)
    except ValueError as exc:
        print(f"Refusing to guess a registry: {exc}", file=sys.stderr)
        return 2
    print(f"Live theme: {theme_slug} (text domain {text_domain}) at {base_url}\n")
    return registry


def main() -> int:
    args = _build_arg_parser().parse_args()
    cache_bust = not args.no_cache_bust
    if args.list:
        return _list_registries(args)

    target = _resolve_target(args)
    if target is None:
        return 2
    base_url, theme_slug = target
    fetcher = _import_fetcher()
    registry = _live_registry(args, fetcher, base_url, theme_slug, cache_bust)
    if isinstance(registry, int):
        return registry

    pages = _resolve_pages(args, registry)
    reports: list[PageReport] = []
    for page in pages:
        report = check_page(fetcher, page, registry, base_url, args.timeout, cache_bust)
        print_page_report(report)
        reports.append(report)
        print()

    print_summary(reports)

    # Exit 3 if every page failed to fetch (env/network problem),
    # otherwise exit 2 on any structural failure, else 0.
    if not any(r.fetched for r in reports):
        return 3
    return 2 if any(not r.passed for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
