"""Reject retired brand copy without storing the removed wording in the repository.

The guard blocks NEW occurrences. Occurrences that already exist are listed in
ALLOWLIST with a reason; a pinned entry fails if its file gains another one.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

# Fingerprint of the founder-retired wording, normalized to ASCII letters.
# A digest keeps the prohibited copy itself out of source, tests, and logs.
RETIRED_DIGEST = "19a498e50c9f1ddeb3557f71df88ffd86160dc1c2c7f23ab98c729edf97a515f"
RETIRED_LENGTH = 23

# Binary formats are skipped by extension. Any OTHER file that is not valid
# UTF-8 fails the check: an unreadable file is not a clean file.
BINARY_EXTENSIONS = frozenset(
    {
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.ico', '.bmp', '.tif',
        '.tiff', '.heic', '.psd', '.woff', '.woff2', '.ttf', '.otf', '.eot',
        '.glb', '.gltf', '.bin', '.usdz', '.fbx', '.obj', '.blend', '.mp4', '.mov',
        '.webm', '.mp3', '.wav', '.ogg', '.pdf', '.zip', '.gz', '.tar', '.tgz',
        '.7z', '.wasm', '.npz', '.npy', '.pyc', '.so', '.dylib', '.parquet', '.sqlite', '.db',
    }
)  # fmt: skip


@dataclass(frozen=True)
class AllowEntry:
    """A path glob permitted to carry retired copy, and why.

    ``max_count`` pins the number of occurrences allowed in each matching file
    (a file name that carries the phrase counts as one). ``None`` leaves the
    entry unpinned; use that only for append-only records and captures.
    """

    pattern: str
    reason: str
    max_count: int | None = None


_KEPT = "PR #1011 kept-on-purpose: founder-verbatim story quote"
_KIDS = "PR #1011 kept-on-purpose: Kids Capsule insert-card copy (open founder call)"
_GUARD = "retired-phrase guard list or assertion that the phrase is rejected"
_RECORD = "dated audit/plan/task record of the retirement or of earlier copy"
_TRIAGE = (
    "UNRESOLVED, not covered by a PR #1011 keep: pinned so it cannot grow; "
    "remove the copy, then delete this entry"
)

ALLOWLIST: tuple[AllowEntry, ...] = (
    # Founder-verbatim quote kept by PR #1011.
    AllowEntry('wordpress-theme/skyyrose-flagship/inc/collection-content.php', _KEPT, 2),
    AllowEntry('wordpress-theme/skyyrose-flagship/languages/skyyrose.pot', _KEPT + ' (2 msgids)', 2),
    AllowEntry('wordpress-theme/skyyrose-flagship/data/collections/signature/copy.md', _KEPT, 1),
    AllowEntry('wordpress-theme/skyyrose-flagship/data/collections/signature/index.html', _KEPT, 1),
    AllowEntry('docs/brand/collection-stories.md', 'Corey\'s verbatim Signature quote, canon source', 1),
    # Kids Capsule insert card.
    AllowEntry('wordpress-theme/skyyrose-flagship/data/collections/kids-capsule/copy.md', _KIDS, 1),
    AllowEntry('wordpress-theme/skyyrose-flagship/data/collections/kids-capsule/index.html', _KIDS, 1),
    # Guard lists and assertions.
    AllowEntry('assets/brand/brand.yaml', _GUARD + ' (tagline.retired)', 1),
    AllowEntry('skyyrose/multi_agent/tools.py', _GUARD + ' (retired_taglines)', 1),
    AllowEntry('skyyrose/elite_studio/tests/test_brand_enforcement.py', _GUARD + '; comment quotes the kept founder quote', 1),
    AllowEntry('tests/agents/test_skyyrose_agents.py', _GUARD, 4),
    AllowEntry('tests/test_character_system.py', _GUARD, 2),
    AllowEntry('eval/brand-story.md', _GUARD + ' (grep test must equal 0)', 1),
    # Dated records.
    AllowEntry('docs/brand/canon-audit-2026-05-23.md', _RECORD, 4),
    AllowEntry('docs/brand/visual-audit-2026-05-23.md', _RECORD, 1),
    AllowEntry('docs/superpowers/plans/2026-05-25-v2-mockup-design.md', _RECORD + ' (plan)', 1),
    AllowEntry('tasks/adk-a2a-DESIGN_SPEC.md', _RECORD, 1),
    AllowEntry('tasks/v2-whole-site-rework-20260922/DESIGN-CONTRACT.html', _RECORD + ' (says the phrase is retired)', 1),
    AllowEntry('tasks/v2-whole-site-rework-20260922/HANDOFF.md', _RECORD + ' (says do not resurrect it)', 1),
    AllowEntry('tasks/relaunch-7day-20260911/rendered/campaign-edit.mjs', 'PR #1011 kept-on-purpose: old ad script', 1),
    AllowEntry('tasks/relaunch-7day-20260911/rendered/pilot-edit.js', 'PR #1011 kept-on-purpose: old ad script', 1),
    # Append-only logs, archives and captured pages: unpinned by nature.
    AllowEntry('.wolf/*', 'OpenWolf session logs and audit reports (append-only records)'),
    AllowEntry('archive/*', 'archived legacy site'),
    AllowEntry('screenshots/*', 'dated captured page snapshots'),
    AllowEntry('tests/fixtures/a11y/black_rose.html', 'captured live-page fixture (pinned)', 5),
    AllowEntry('tests/fixtures/a11y/homepage.html', 'captured live-page fixture (pinned)', 5),
    AllowEntry('tests/fixtures/a11y/shop.html', 'captured live-page fixture (pinned)', 6),
    AllowEntry('tests/fixtures/a11y/signature.html', 'captured live-page fixture (pinned)', 5),
    AllowEntry('tests/fixtures/homepage_skyyrose.html', 'captured live-page fixture (pinned)', 5),
    # Unresolved: found by the guard, not covered by a kept-on-purpose decision.
    AllowEntry('wordpress-theme/skyyrose-flagship/assets/css/collection-motion.css', _TRIAGE + ' (CSS comment)', 1),
    AllowEntry('skyyrose-suite/plugins/skyyrose-market/skills/skyyrose-social-influencer-outreach/SKILL.md', _TRIAGE + ' (outreach template)', 1),
    AllowEntry('_prototype/homepage/sections/close.html', _TRIAGE + ' (prototype)', 1),
    AllowEntry('_prototype/homepage/sections/letter.html', _TRIAGE + ' (prototype)', 1),
    AllowEntry('_prototype/homepage/sections/ticker.html', _TRIAGE + ' (prototype comment)', 1),
    AllowEntry('docs/brand/blog-luxury-*.md', _TRIAGE + ' (file name carries the phrase)', 1),
    AllowEntry('docs/brand/blog-black-rose.md', _TRIAGE + ' (names the draft above)', 1),
    AllowEntry('docs/brand/blog-kids-capsule.md', _TRIAGE + ' (names the draft above)', 1),
    AllowEntry('docs/brand/blog-love-hurts.md', _TRIAGE + ' (names the draft above)', 1),
    AllowEntry('docs/brand/blog-signature.md', _TRIAGE + ' (names the draft above); also quotes the kept founder quote', 2),
)  # fmt: skip


_TAG = re.compile(r"""</?[A-Za-z](?:"[^"]*"|'[^']*'|[^<>"'])*>""")
_ATTR = re.compile(r"""[\w:.-]+\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'<>]+))""")


def _count_letters(text: str) -> int:
    """Count the phrase in `text` after folding case, punctuation and entities."""
    normalized = re.sub(r"[^a-z]", "", html.unescape(text).lower())
    windows = re.finditer(rf"(?=(l[a-z]{{{RETIRED_LENGTH - 2}}}e))", normalized)
    return sum(
        hashlib.sha256(match.group(1).encode()).hexdigest() == RETIRED_DIGEST for match in windows
    )


def count_retired_copy(text: str) -> int:
    """Count case, punctuation, whitespace, markup, and hashtag variants.

    Two independent streams are summed, so nothing is counted twice:
    the text stream (every real HTML tag replaced by one space, so a phrase
    split across tags still joins up) and each attribute value on its own
    (every attribute, no exclusions: alt, href slugs, data-*, class, ...).
    `<?php` and `=>` are not tags.
    """
    attribute_values: list[str] = []

    def drop_tag(match: re.Match[str]) -> str:
        attribute_values.extend(v for groups in _ATTR.findall(match.group(0)) for v in groups if v)
        return " "

    text_stream = _TAG.sub(drop_tag, text)
    return _count_letters(text_stream) + sum(_count_letters(v) for v in attribute_values)


def contains_retired_copy(text: str) -> bool:
    return count_retired_copy(text) > 0


def _allowance(name: str, allowlist: Iterable[AllowEntry]) -> AllowEntry | None:
    return next((e for e in allowlist if fnmatchcase(name, e.pattern)), None)


def tracked_paths(root: Path) -> list[str]:
    """List tracked and untracked-but-not-ignored files, or raise RuntimeError."""
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"") or b""
        reason = detail.decode(errors="replace").strip() or str(exc)
        raise RuntimeError(f"git ls-files failed in {root}: {reason}") from exc
    return sorted({p for p in raw.decode("utf-8", "surrogateescape").split("\0") if p})


def find_violations(
    root: Path, names: Iterable[str], allowlist: Sequence[AllowEntry] = ALLOWLIST
) -> list[str]:
    """Return one message per violation; empty means the tree is clean."""
    problems: list[str] = []
    for name in names:
        path = root / name
        # The path name is checked for every entry; binaries and symlinks only
        # skip the content scan.
        count = count_retired_copy(name)
        scannable = (
            path.is_file()
            and not path.is_symlink()
            and path.suffix.lower() not in BINARY_EXTENSIONS
        )
        if scannable:
            try:
                count += count_retired_copy(path.read_bytes().decode("utf-8"))
            except UnicodeError:
                problems.append(
                    f"Cannot decode as UTF-8 (add to BINARY_EXTENSIONS if binary): {name}"
                )
                continue
            except OSError as exc:
                problems.append(f"Cannot read {name}: {exc.strerror or exc}")
                continue
        if not count:
            continue
        entry = _allowance(name, allowlist)
        if entry is None:
            problems.append(f"Retired brand copy must be removed: {name}")
        elif entry.max_count is not None and count > entry.max_count:
            problems.append(
                f"Retired brand copy increased in allowlisted file: {name} "
                f"({count} found, {entry.max_count} allowed; {entry.reason})"
            )
    return problems


def find_stale(
    root: Path, names: Iterable[str], allowlist: Sequence[AllowEntry] = ALLOWLIST
) -> list[str]:
    """Pinned entries whose files no longer carry the phrase (informational)."""
    names = list(names)
    stale = []
    for entry in allowlist:
        if entry.max_count is None:
            continue
        counts = []
        for name in names:
            path = root / name
            if fnmatchcase(name, entry.pattern) and path.is_file() and not path.is_symlink():
                try:
                    counts.append(
                        count_retired_copy(path.read_bytes().decode("utf-8"))
                        + count_retired_copy(name)
                    )
                except (UnicodeError, OSError):
                    counts.append(1)
        if not any(counts):
            stale.append(f"Stale allowlist entry (no occurrences left, delete it): {entry.pattern}")
        elif max(counts) < entry.max_count:
            stale.append(
                f"Allowlist pin can be lowered: {entry.pattern} "
                f"({max(counts)} found, {entry.max_count} pinned)"
            )
    return stale


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        '--root', type=Path, default=Path(__file__).resolve().parents[1],
        help='git working tree to scan (default: this repository)',
    )  # fmt: skip
    root = parser.parse_args(argv).root.resolve()
    try:
        names = tracked_paths(root)
    except RuntimeError as exc:
        print(f"Retired-copy check could not run: {exc}", file=sys.stderr)
        return 2
    problems = find_violations(root, names)
    for message in problems:
        print(message)
    for message in find_stale(root, names):
        print(f"warning: {message}")
    print(f"Retired-copy check: {len(problems)} violations")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
