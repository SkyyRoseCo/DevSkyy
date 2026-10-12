"""
Backend for the SkyyRose Flagship 2 theme: the theme's own npm scripts.

The real software here is the V2 build/verify toolchain declared in
``wordpress-theme/skyyrose-flagship-2/package.json``. This module never
reimplements a gate; it locates the repository, proves the toolchain matches the
certification pins in ``tools/v2-source-certification/build-inputs.json``, and
runs ``npm run <script>`` as a subprocess (args as a list, never ``shell=True``).

Every failure raises a typed error with an actionable message so an agent can
self-correct.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

THEME_REL = "wordpress-theme/skyyrose-flagship-2"
BUILD_INPUTS_REL = "tools/v2-source-certification/build-inputs.json"
REGISTRY_REL = "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
FIXTURE_SCRIPT_REL = "tools/v2-source-certification/prepare-native-fixture.py"
FIXTURE_PINS_REL = "tools/v2-runtime/fixtures/pdp-native-template-hashes.json"
# The hidden lockfile `npm ci` writes: it names every installed package and version.
DEPS_LOCK_REL = f"{THEME_REL}/node_modules/.package-lock.json"
NODE_DOWNLOAD = "https://nodejs.org/dist/v{version}/node-v{version}-darwin-arm64.tar.gz"


class BackendError(RuntimeError):
    """Base class for backend errors."""


class RepoNotFoundError(BackendError):
    """No DevSkyy checkout containing the flagship-2 theme could be located."""


class ToolchainMismatchError(BackendError):
    """A tool is missing or does not match the certification pin."""


# ---------------------------------------------------------------------------
# Repository discovery
# ---------------------------------------------------------------------------


def _is_repo(path: Path) -> bool:
    return (path / THEME_REL / "package.json").is_file() and (path / BUILD_INPUTS_REL).is_file()


def find_repo_root(explicit: str | os.PathLike[str] | None = None) -> Path:
    """
    Resolve the DevSkyy checkout to operate on.

    Order: explicit argument, ``SKYYROSE2_REPO_ROOT``, then the current directory
    and its ancestors. There is deliberately no home-directory default: the
    shared checkout is often on another branch, and a silent fallback would
    certify the wrong tree.
    """
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    elif os.environ.get("SKYYROSE2_REPO_ROOT"):
        candidates.append(Path(os.environ["SKYYROSE2_REPO_ROOT"]).expanduser())
    else:
        cwd = Path.cwd().resolve()
        candidates.extend([cwd, *cwd.parents])
    for candidate in candidates:
        if _is_repo(candidate):
            return candidate.resolve()
    tried = candidates[0] if explicit or os.environ.get("SKYYROSE2_REPO_ROOT") else Path.cwd()
    raise RepoNotFoundError(
        f"No DevSkyy checkout with {THEME_REL}/package.json found from {tried}. "
        "Run from inside a checkout, or pass --repo-root / set SKYYROSE2_REPO_ROOT."
    )


def theme_dir(repo: Path) -> Path:
    return repo / THEME_REL


def load_package_scripts(repo: Path) -> dict[str, str]:
    """Return the ``scripts`` map from the theme's package.json (read at call time)."""
    data = json.loads((theme_dir(repo) / "package.json").read_text(encoding="utf-8"))
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        raise BackendError(f"{THEME_REL}/package.json has no scripts object")
    return {str(k): str(v) for k, v in scripts.items()}


def load_build_inputs(repo: Path) -> dict[str, Any]:
    return json.loads((repo / BUILD_INPUTS_REL).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Toolchain
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Toolchain:
    """Resolved tool versions and the PATH every gate subprocess runs under."""

    path_env: str
    node: str | None
    npm: str | None
    python: str | None
    php: str | None
    pins: dict[str, str]
    mismatches: tuple[str, ...] = field(default_factory=tuple)
    deps_sha256: str | None = None

    @property
    def ok(self) -> bool:
        return not self.mismatches

    def versions(self) -> dict[str, str | None]:
        return {"node": self.node, "npm": self.npm, "python": self.python, "php": self.php}

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["ok"] = self.ok
        out["mismatches"] = list(self.mismatches)
        out.pop("path_env")
        return out


def _probe(argv: list[str], env: dict[str, str]) -> str | None:
    exe = shutil.which(argv[0], path=env["PATH"])
    if not exe:
        return None
    try:
        proc = subprocess.run([exe, *argv[1:]], capture_output=True, text=True, env=env, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (proc.stdout or proc.stderr).strip()
    return text.splitlines()[0] if text else None


def _python_bin_dir() -> Path | None:
    """Directory of the interpreter to expose as ``python3`` to npm scripts."""
    explicit = os.environ.get("SKYYROSE2_PYTHON_BIN_DIR")
    if explicit:
        return Path(explicit).expanduser()
    venv = os.environ.get("VIRTUAL_ENV")
    if venv and (Path(venv) / "bin" / "python3").exists():
        return Path(venv) / "bin"
    return None


def resolve_toolchain(repo: Path) -> Toolchain:
    """
    Build the subprocess PATH and compare each tool to its certification pin.

    ``SKYYROSE2_NODE_BIN_DIR`` (a directory holding ``node`` and ``npm``) is put
    first on PATH, which is how the exact pinned Node is supplied when the
    system Node differs. The python interpreter is taken from
    ``SKYYROSE2_PYTHON_BIN_DIR`` or the active virtualenv.
    """
    pins_raw = load_build_inputs(repo)
    pins = {k: str(pins_raw[k]) for k in ("node", "npm", "python") if k in pins_raw}
    parts: list[str] = []
    node_dir = os.environ.get("SKYYROSE2_NODE_BIN_DIR")
    if node_dir:
        parts.append(str(Path(node_dir).expanduser()))
    py_dir = _python_bin_dir()
    if py_dir:
        parts.append(str(py_dir))
    parts.append(os.environ.get("PATH", ""))
    env = {**os.environ, "PATH": os.pathsep.join(p for p in parts if p)}

    node = _probe(["node", "--version"], env)
    npm = _probe(["npm", "--version"], env)
    python = _probe(["python3", "--version"], env)
    php = _probe(["php", "-r", "echo PHP_VERSION;"], env)
    found = {
        "node": node.lstrip("v") if node else None,
        "npm": npm,
        "python": python.split()[-1] if python else None,
    }
    mismatches: list[str] = [
        f"{tool}: no pin in {BUILD_INPUTS_REL}; refusing to run unpinned."
        for tool in ("node", "npm", "python")
        if tool not in pins
    ]
    for tool, want in pins.items():
        have = found.get(tool)
        if have != want:
            hint = ""
            if tool == "node":
                hint = (
                    f" Download {NODE_DOWNLOAD.format(version=want)}, verify its sha256 against "
                    f"nodejs.org SHASUMS256.txt, extract it, and set SKYYROSE2_NODE_BIN_DIR to its bin/."
                )
            elif tool == "python":
                hint = " Activate the repo .venv or set SKYYROSE2_PYTHON_BIN_DIR."
            mismatches.append(f"{tool}: pinned {want}, found {have or 'not on PATH'}.{hint}")
    if php is None:
        mismatches.append("php: not on PATH (needed by verify, lint:php, check:provisioning).")
    return Toolchain(
        path_env=env["PATH"],
        node=found["node"],
        npm=npm,
        python=found["python"],
        php=php,
        pins=pins,
        mismatches=tuple(mismatches),
        deps_sha256=deps_digest(repo),
    )


def deps_digest(repo: Path) -> str | None:
    """
    sha256 of the theme's installed-deps lockfile (``node_modules/.package-lock.json``),
    or None when it is absent. It identifies the installed node_modules, which the
    candidate id (tracked files only) does not cover.
    """
    lock = repo / DEPS_LOCK_REL
    return sha256_file(lock) if lock.is_file() else None


def harness_sha256() -> str:
    """
    Digest of this CLI's own source (excluding tests), so evidence names the
    exact tool code that produced it. The harness can be untracked, so a git
    revision is not enough.
    """
    package = Path(__file__).resolve().parents[1]
    h = hashlib.sha256()
    for path in sorted(package.rglob("*.py")):
        rel = path.relative_to(package).as_posix()
        if rel.startswith("tests/") or "__pycache__" in rel:
            continue
        h.update(rel.encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def environment_label(tc: Toolchain) -> str:
    """Runs whose label differs from the export's (other tools, harness or deps) do not PASS."""
    v = tc.versions()
    deps = tc.deps_sha256[:12] if tc.deps_sha256 else "none"
    return (
        f"local:{socket.gethostname()};node={v['node']};npm={v['npm']};"
        f"python={v['python']};php={v['php']};harness={harness_sha256()[:12]};deps={deps}"
    )


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def git(repo: Path, *args: str, binary: bool = False) -> bytes | str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=not binary)
    if proc.returncode != 0:
        err = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode(errors="replace")
        raise BackendError(f"git {' '.join(args)} failed: {err.strip()}")
    return proc.stdout


# Untracked (non-ignored) files here are executed or read by the gates, so they
# are part of what a gate result is evidence for.
GATE_INPUT_DIRS = (THEME_REL, "tools/v2-runtime", "tools/v2-source-certification")


def tracked_changes(repo: Path) -> set[str]:
    """
    Paths that make the tree differ from HEAD for gate purposes.

    Tracked content differing from HEAD (staged or unstaged), plus untracked,
    non-ignored files under GATE_INPUT_DIRS (a new PHP file is linted and
    verified even though HEAD lacks it).
    """
    changed = git(repo, "diff", "HEAD", "--name-only", "-z")
    untracked = git(
        repo, "ls-files", "--others", "--exclude-standard", "-z", "--", *GATE_INPUT_DIRS
    )
    return {p for p in (str(changed) + "\0" + str(untracked)).split("\0") if p}


def content_digest(repo: Path, paths: set[str]) -> str:
    """Hash the current bytes of *paths* so an edit to an already-dirty file is visible."""
    h = hashlib.sha256()
    for rel in sorted(paths):
        h.update(rel.encode() + b"\0")
        target = repo / rel
        h.update(sha256_file(target).encode() if target.is_file() else b"<absent>")
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Script runner
# ---------------------------------------------------------------------------


@dataclass
class ScriptResult:
    script: str
    command: list[str]
    cwd: str
    returncode: int
    duration_s: float
    started_at: str
    stdout: str
    stderr: str
    changed_paths: list[str]
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def run_npm_script(
    repo: Path,
    script: str,
    toolchain: Toolchain,
    timeout: float | None = None,
    extra_env: dict[str, str] | None = None,
) -> ScriptResult:
    """
    Run ``npm run <script>`` in the theme directory under the resolved toolchain.

    Reports every tracked path whose content changed during the run, including
    paths that were already dirty beforehand (detected by content hash).
    """
    npm = shutil.which("npm", path=toolchain.path_env)
    if not npm:
        raise ToolchainMismatchError("npm not found on the resolved PATH")
    before = tracked_changes(repo)
    before_digest = {p: content_digest(repo, {p}) for p in before}
    env = {**os.environ, **(extra_env or {}), "PATH": toolchain.path_env}
    command = [npm, "run", script]
    started = datetime.now(UTC).isoformat(timespec="seconds")
    t0 = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            cwd=str(theme_dir(repo)),
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc = 124
        out = (
            exc.stdout.decode(errors="replace")
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        err = (
            exc.stderr.decode(errors="replace")
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "")
        )
    duration = round(time.monotonic() - t0, 2)
    after = tracked_changes(repo)
    changed = after ^ before
    changed |= {p for p in before & after if content_digest(repo, {p}) != before_digest[p]}
    return ScriptResult(
        script=script,
        command=["npm", "run", script],
        cwd=THEME_REL,
        returncode=rc,
        duration_s=duration,
        started_at=started,
        stdout=out,
        stderr=err,
        changed_paths=sorted(changed),
        timed_out=timed_out,
    )


# ---------------------------------------------------------------------------
# Native WordPress/WooCommerce fixture (needed by verify's PDP gallery test)
# ---------------------------------------------------------------------------


def managed_fixture_dir(repo: Path, home: Path) -> Path:
    """Fixture path keyed by the pin manifest, so a pin change never reuses old bytes."""
    manifest = repo / FIXTURE_PINS_REL
    if not manifest.is_file():
        raise BackendError(f"Fixture pin manifest missing: {FIXTURE_PINS_REL}")
    digest = sha256_file(manifest)[:16]
    return home / "fixtures" / f"wp-native-{digest}"


def fixture_dir(repo: Path, home: Path) -> Path | None:
    """``V2_WP_FIXTURE`` when set, else the CLI-managed fixture if it exists."""
    explicit = os.environ.get("V2_WP_FIXTURE")
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.is_dir() else None
    managed = managed_fixture_dir(repo, home)
    return managed if managed.is_dir() else None


def prepare_fixture(repo: Path, home: Path, toolchain: Toolchain) -> Path:
    """Run the repo's own hash-checked fixture builder into the managed location."""
    dest = managed_fixture_dir(repo, home)
    if dest.is_dir():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    python = shutil.which("python3", path=toolchain.path_env)
    if not python:
        raise ToolchainMismatchError("python3 not found on the resolved PATH")
    proc = subprocess.run(
        [python, str(repo / FIXTURE_SCRIPT_REL), str(dest)],
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PATH": toolchain.path_env},
    )
    if proc.returncode != 0:
        shutil.rmtree(dest, ignore_errors=True)
        raise BackendError(
            f"Fixture preparation failed: {(proc.stderr or proc.stdout).strip()[-600:]}"
        )
    return dest
