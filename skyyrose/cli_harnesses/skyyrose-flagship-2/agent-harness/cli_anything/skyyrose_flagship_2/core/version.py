"""
SKYYROSE2_VERSION triple for the flagship-2 theme.

Sources that must agree before any deploy that changed shipped CSS/JS/PHP:
  functions.php  define( 'SKYYROSE2_VERSION', 'X.Y.Z' );
  style.css      Version: X.Y.Z
  readme.txt     Stable tag: X.Y.Z

package.json's "version" is reported for information only; it is not part of
the deploy cache-bust triple.

A bump stages all three new texts in memory, then replaces each file atomically
(temp file, fsync, os.replace). If a later replace fails, files already written
are restored from their original bytes.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
_PATTERNS: dict[str, re.Pattern[str]] = {
    "functions.php": re.compile(r"(define\(\s*'SKYYROSE2_VERSION'\s*,\s*')([^']+)(')"),
    "style.css": re.compile(r"^(Version:\s*)(\S+)()$", re.MULTILINE),
    "readme.txt": re.compile(r"^(Stable tag:\s*)(\S+)()$", re.MULTILINE),
}


class VersionError(RuntimeError):
    """Version could not be read or written."""


@dataclass(frozen=True)
class VersionState:
    sources: dict[str, str]
    package_json: str | None

    @property
    def consistent(self) -> bool:
        return len(set(self.sources.values())) == 1

    @property
    def current(self) -> str:
        if not self.consistent:
            raise VersionError(f"SKYYROSE2_VERSION sources disagree: {self.sources}")
        return next(iter(self.sources.values()))

    def to_dict(self) -> dict[str, object]:
        return {
            "sources": dict(self.sources),
            "consistent": self.consistent,
            "version": next(iter(self.sources.values())) if self.consistent else None,
            "package_json": self.package_json,
        }


def _match(theme: Path, name: str) -> tuple[str, re.Match[str]]:
    path = theme / name
    text = path.read_text(encoding="utf-8")
    matches = list(_PATTERNS[name].finditer(text))
    if len(matches) != 1:
        raise VersionError(f"Expected exactly one version marker in {path}, found {len(matches)}")
    return text, matches[0]


def read_version(theme: Path) -> VersionState:
    sources = {name: _match(theme, name)[1].group(2) for name in _PATTERNS}
    pkg = theme / "package.json"
    pkg_version = (
        json.loads(pkg.read_text(encoding="utf-8")).get("version") if pkg.is_file() else None
    )
    return VersionState(sources=sources, package_json=pkg_version)


def _atomic_write(path: Path, content: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".skyyrose2-ver-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def plan_bump(theme: Path, new_version: str) -> dict[str, tuple[str, str]]:
    """Return {file: (old_text, new_text)} without writing anything."""
    if not _SEMVER.match(new_version):
        raise VersionError(f"Version must be X.Y.Z, got {new_version!r}")
    state = read_version(theme)
    current = state.current
    if current == new_version:
        raise VersionError(f"Version is already {new_version}")
    plan: dict[str, tuple[str, str]] = {}
    for name in _PATTERNS:
        text, m = _match(theme, name)
        updated = text[: m.start(2)] + new_version + text[m.end(2) :]
        plan[name] = (text, updated)
    return plan


def write_version(theme: Path, new_version: str) -> VersionState:
    plan = plan_bump(theme, new_version)
    written: list[str] = []
    try:
        for name, (_, updated) in plan.items():
            _atomic_write(theme / name, updated)
            written.append(name)
    except BaseException:
        for name in written:
            _atomic_write(theme / name, plan[name][0])
        raise
    state = read_version(theme)
    if not state.consistent or state.current != new_version:
        raise VersionError(f"Post-write read-back disagrees: {state.sources}")
    return state
