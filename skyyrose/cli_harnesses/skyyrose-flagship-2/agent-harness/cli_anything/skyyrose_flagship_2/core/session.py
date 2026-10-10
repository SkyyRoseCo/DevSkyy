"""
Session = an append-only ledger of gate runs for one repository checkout.

Layout under the state home (``SKYYROSE2_CLI_HOME``, default
``~/.cli-anything/skyyrose-flagship-2``):

  current                     name of the active session
  sessions/<id>/session.json  ledger (runs, reviews), saved under an flock
  sessions/<id>/logs/<n>-<gate>.log  full stdout+stderr of each run

Nothing is written inside the repository.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

SCHEMA = "skyyrose.flagship2.cli-session.v1"


def state_home() -> Path:
    return Path(
        os.environ.get(
            "SKYYROSE2_CLI_HOME", str(Path.home() / ".cli-anything" / "skyyrose-flagship-2")
        )
    ).expanduser()


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _locked_save_json(path: Path, data: Any) -> None:
    """Write JSON under an exclusive lock, truncating only inside the lock."""
    try:
        fh = open(path, "r+", encoding="utf-8")
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(path, "w", encoding="utf-8")
    with fh:
        locked = False
        try:
            import fcntl

            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            pass
        try:
            fh.seek(0)
            fh.truncate()
            json.dump(data, fh, indent=2, sort_keys=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            if locked:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


_RUN_MARK = "--- run ---\n"


def format_log(header: dict[str, Any], stdout: str, stderr: str) -> str:
    """Log = one JSON header line (the facts the status is derived from) + raw output."""
    return (
        f"{_RUN_MARK}{json.dumps(header, sort_keys=True)}\n"
        f"--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}\n"
    )


def read_log_header(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith(_RUN_MARK):
        raise SessionError(f"Log {path} has no run header")
    line = text[len(_RUN_MARK) :].split("\n", 1)[0]
    try:
        header = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SessionError(f"Log {path} has an unreadable run header: {exc}") from exc
    if not isinstance(header, dict):
        raise SessionError(f"Log {path} run header is not an object")
    return header


class SessionError(RuntimeError):
    """Session missing or unreadable."""


@dataclass
class Session:
    session_id: str
    repo_root: str
    created_at: str
    runs: list[dict[str, Any]] = field(default_factory=list)
    reviews: list[dict[str, Any]] = field(default_factory=list)
    modified: bool = False

    @property
    def directory(self) -> Path:
        return state_home() / "sessions" / self.session_id

    @property
    def path(self) -> Path:
        return self.directory / "session.json"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "session_id": self.session_id,
            "repo_root": self.repo_root,
            "created_at": self.created_at,
            "runs": self.runs,
            "reviews": self.reviews,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "repo_root": self.repo_root,
            "created_at": self.created_at,
            "path": str(self.path),
            "runs": len(self.runs),
            "reviews": len(self.reviews),
            "last_run": self.runs[-1]["gate_id"] if self.runs else None,
        }

    def write_log(self, gate: str, text: str) -> Path:
        logs = self.directory / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", gate)
        path = logs / f"{len(self.runs) + 1:04d}-{safe}.log"
        path.write_text(text, encoding="utf-8")
        return path

    def add_run(self, record: dict[str, Any]) -> None:
        self.runs.append(record)
        self.modified = True

    def add_review(self, record: dict[str, Any]) -> None:
        self.reviews.append(record)
        self.modified = True

    def save(self) -> Path:
        _locked_save_json(self.path, self.to_dict())
        (state_home() / "current").write_text(self.session_id + "\n", encoding="utf-8")
        self.modified = False
        return self.path


def new_session(repo_root: Path) -> Session:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    sess = Session(
        session_id=f"{stamp}-{uuid.uuid4().hex[:6]}",
        repo_root=str(repo_root),
        created_at=_now(),
        modified=True,
    )
    return sess


def load_session(session_id: str) -> Session:
    path = state_home() / "sessions" / session_id / "session.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SessionError(f"No session {session_id!r} at {path}") from exc
    except json.JSONDecodeError as exc:
        raise SessionError(f"Session file {path} is not valid JSON: {exc}") from exc
    if data.get("schema") != SCHEMA:
        raise SessionError(
            f"Session file {path} has schema {data.get('schema')!r}, expected {SCHEMA}"
        )
    return Session(
        session_id=data["session_id"],
        repo_root=data["repo_root"],
        created_at=data["created_at"],
        runs=list(data.get("runs", [])),
        reviews=list(data.get("reviews", [])),
    )


def current_session_id() -> str | None:
    pointer = state_home() / "current"
    if not pointer.is_file():
        return None
    value = pointer.read_text(encoding="utf-8").strip()
    return value or None


def open_or_create(repo_root: Path) -> Session:
    """Load the active session if it belongs to *repo_root*; otherwise start a new one."""
    sid = current_session_id()
    if sid:
        try:
            sess = load_session(sid)
        except SessionError:
            sess = None
        if sess is not None and Path(sess.repo_root) == repo_root:
            return sess
    return new_session(repo_root)


def list_sessions() -> list[dict[str, Any]]:
    root = state_home() / "sessions"
    if not root.is_dir():
        return []
    out = []
    for child in sorted(root.iterdir()):
        if (child / "session.json").is_file():
            try:
                out.append(load_session(child.name).summary())
            except SessionError as exc:
                out.append({"session_id": child.name, "error": str(exc)})
    return out
