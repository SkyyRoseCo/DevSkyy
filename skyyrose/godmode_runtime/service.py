"""Durable workstation runtime. No shell, provider dispatch, or arbitrary executable inputs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from collections.abc import Iterator

PROJECT = "skyyrose"
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED", "INTERRUPTED", "INVALIDATED"}
WORKFLOWS = {
    "source-audit": {
        "title": "Fashion team source audit",
        "description": "Build a source-bound team assignment and inspect all migrated SkyyRose skills.",
        "steps": [
            {
                "id": "team-assignment",
                "title": "Inspect skills and build team assignment",
                "owner": "fashion-theme-team",
                "verifier": "source-inventory-check",
            }
        ],
    },
    "campaign-readiness": {
        "title": "Campaign workflow readiness",
        "description": "Run the actual registry projection and campaign contract verifiers; no production.",
        "steps": [
            {
                "id": "team-assignment",
                "title": "Build team assignment",
                "owner": "god-mode",
                "verifier": "source-inventory-check",
            },
            {
                "id": "product-registry",
                "title": "Check product registry projections",
                "owner": "product-truth",
                "verifier": "sync_product_registry --check",
            },
            {
                "id": "campaign-contract",
                "title": "Check campaign workflow contracts",
                "owner": "campaign-ooda",
                "verifier": "workflow_guard verify",
            },
        ],
    },
    "fashion-verification": {
        "title": "Fashion skill migration verification",
        "description": "Run the canonical Fashion migration verifier and source-bound team audit.",
        "steps": [
            {
                "id": "team-assignment",
                "title": "Build team assignment",
                "owner": "god-mode",
                "verifier": "source-inventory-check",
            },
            {
                "id": "fashion-migration",
                "title": "Verify SkyyRose skill migration",
                "owner": "fashion-designops",
                "verifier": "verify-skyyrose-migration",
            },
        ],
    },
}


AGENT_WORKFLOWS = {"fashion-campaign-analysis", "fashion-skill-analysis"}
for _workflow, _title in (
    ("fashion-campaign-analysis", "Claude campaign coverage + Codex review"),
    ("fashion-skill-analysis", "Claude Fashion skill audit + Codex review"),
):
    WORKFLOWS[_workflow] = {
        "title": _title,
        "description": "Approved source-packet analysis by Claude, independently reviewed by Codex. No media production or project edits.",
        "steps": [
            {
                "id": "claude-worker",
                "title": "Claude source-bound analysis",
                "owner": "claude-agent-sdk",
                "verifier": "schema and exact preorder coverage",
            },
            {
                "id": "codex-reviewer",
                "title": "Independent Codex machine review",
                "owner": "codex-exec-cli",
                "verifier": "immutable worker artifact binding; separate human acceptance",
            },
        ],
    }


class RuntimeConflict(ValueError):
    """A transition would violate the approved contract."""


class RuntimeNotFound(LookupError):
    """The requested run or memory does not exist."""


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def scrub(text: str) -> str:
    """Conservative output redaction; never read environment or credential files."""
    text = re.sub(r"(?i)(bearer\s+)[\w.\-]+", r"\1[REDACTED]", text)
    return re.sub(
        r"(?i)((?:api[_-]?key|token|password|secret)\s*[=:]\s*)[^\s,;]+", r"\1[REDACTED]", text
    )[:16000]


class Runtime:
    """One workstation executor, SQLite WAL, transactional claims, no automatic replay."""

    def __init__(self, root: Path, team: Path, db: Path, *, timeout: float = 90.0):
        self.root = root.resolve()
        self.team = team.resolve()
        self.db = db.resolve()
        self.timeout = timeout
        self.db.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, project TEXT NOT NULL, workflow TEXT NOT NULL,
                    idem TEXT NOT NULL, actor TEXT NOT NULL, status TEXT NOT NULL,
                    plan TEXT NOT NULL, plan_hash TEXT NOT NULL, approval TEXT,
                    created REAL NOT NULL, updated REAL NOT NULL, lease REAL,
                    cancel INTEGER NOT NULL DEFAULT 0, UNIQUE(project,idem)
                );
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
                    kind TEXT NOT NULL, actor TEXT NOT NULL, at REAL NOT NULL, data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL, actor TEXT NOT NULL,
                    plan_hash TEXT NOT NULL, artifact_hash TEXT NOT NULL, verdict TEXT NOT NULL,
                    notes TEXT NOT NULL, at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY, project TEXT NOT NULL, kind TEXT NOT NULL,
                    content TEXT NOT NULL, provenance TEXT NOT NULL, trust TEXT NOT NULL,
                    actor TEXT NOT NULL, created REAL NOT NULL, revision INTEGER NOT NULL,
                    supersedes TEXT, promoted_by TEXT, promoted_at REAL
                );
            """)
        os.chmod(self.db, 0o600)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    @staticmethod
    def project(project: str) -> None:
        if project != PROJECT:
            raise ValueError("Only the explicitly configured SkyyRose project is enabled")

    def event(self, conn: sqlite3.Connection, run: str, kind: str, actor: str, data: Any) -> None:
        conn.execute(
            "INSERT INTO events(run_id,kind,actor,at,data) VALUES(?,?,?,?,?)",
            (run, kind, actor, time.time(), canonical(data)),
        )

    def _sources(self) -> dict[str, str]:
        paths = [
            self.root / "AGENTS.md",
            self.root / "SOT.md",
            self.root / "logo-registry.json",
            self.team / "skills/fashion-theme-team/SKILL.md",
            self.team / "skills/fashion-theme-team/references/skyyrose-skill-migration.json",
            self.team / "scripts/verify-skyyrose-migration.py",
            self.root / "scripts/sync_product_registry.py",
            self.root / ".agents/skills/skyyrose-campaign-ooda/scripts/workflow_guard.py",
            self.root
            / ".agents/skills/skyyrose-campaign-ooda/references/production-workflows.json",
        ]
        manifest = json.loads(paths[4].read_text())
        for entry in manifest["skills"]:
            target = (self.team / entry["target"]).resolve()
            if not target.is_relative_to(self.team):
                raise ValueError("Skill target escapes team source")
            paths.extend(
                p
                for p in target.parent.rglob("*")
                if p.is_file()
                and p.suffix in {".md", ".json", ".py", ".sh"}
                and "__pycache__" not in p.parts
            )
        # Resolve indexed canon bytes too; an unchanged SOT link is not unchanged canon.
        canon_candidates = [
            self.root / "docs/brand/constitution-v1/CONSTITUTION.md",
            self.root / "docs/brand/constitution-v1/OWNER-RATIFICATION-20260923.md",
            self.root / "docs/brand/constitution-v1/OWNER-RATIFICATION-KPS-20260923.md",
            self.root / "knowledge-base/seed/from-interview.md",
            self.root / "assets/brand/brand.yaml",
        ]
        canon_candidates.extend(
            (self.root / "wordpress-theme/skyyrose-flagship/data/collections").glob(
                "*/identity.json"
            )
        )
        paths.extend(path for path in canon_candidates if path.is_file())
        paths.extend((self.root / "skyyrose/core").glob("*.py"))
        paths.extend(Path(__file__).parent.glob("*.py"))
        api_source = self.root / "api/v1/god_mode.py"
        if api_source.is_file():
            paths.append(api_source)
        return {str(p): digest(p.read_bytes()) for p in sorted(set(paths))}

    def _agent_plan(self, workflow: str) -> dict[str, Any]:
        from .agent_adapters import adapter_contract
        from .agent_packets import build_packet

        contract = adapter_contract()
        if not contract.get("available"):
            raise ValueError(
                "Claude/Codex adapters are not configured; inspect agent worker status"
            )
        memory = self.memory(PROJECT, "", trusted_only=True)
        packet = build_packet(self.root, self.team, workflow, self._sources(), memory)
        return {
            "scope": "BOUNDED_AGENT_ANALYSIS_NO_PRODUCTION",
            "provider_dispatch": True,
            "paid_calls": True,
            "agent_contract": contract,
            "source_packet": packet,
            "allowance": {
                "claude_max_budget_usd": 1.0,
                "codex_billing": "existing_chatgpt_allowance_no_api_key_fallback",
                "max_run_calls": 2,
                "daily_run_limit": 2,
                "retry": "NEVER_AUTOMATIC",
                "production": False,
            },
        }

    def _agent_step(self, row: sqlite3.Row, stage: str) -> dict[str, Any]:
        from .agent_adapters import AdapterError, run_stage
        from .agent_packets import verify_coverage

        plan = json.loads(row["plan"])
        worker = None
        if stage == "codex-reviewer":
            candidates = [s for s in self.get(row["id"])["steps"] if s["id"] == "claude-worker"]
            if len(candidates) != 1 or candidates[0]["status"] != "PASSED":
                raise RuntimeConflict("A frozen successful Claude artifact is required")
            worker = candidates[0]["artifact"]
        try:
            receipt = run_stage(
                stage,
                plan["source_packet"],
                plan["agent_contract"],
                lambda: self._cancelled(row["id"]),
                worker=worker,
            )
        except AdapterError as exc:
            return {
                "id": stage,
                "status": "FAILED",
                "error_code": str(exc),
                "usage": "UNKNOWN_RESERVATION_RETAINED",
                "production_authority": False,
                "human_acceptance": "NOT_GRANTED",
            }
        if receipt.get("status") == "PASSED":
            if stage == "claude-worker":
                try:
                    verify_coverage(plan["source_packet"], receipt["artifact"])
                except ValueError:
                    receipt["status"] = "FAILED"
                    receipt["error_code"] = "incomplete_preorder_coverage"
            elif receipt["artifact"]["verdict"] != "PASS":
                receipt["status"] = "FAILED"
        receipt["human_acceptance"] = "NOT_GRANTED"
        receipt["production_authority"] = False
        return receipt

    def create(self, project: str, workflow: str, idem: str, actor: str) -> dict[str, Any]:
        self.project(project)
        if workflow not in WORKFLOWS or not re.fullmatch(r"[A-Za-z0-9_\-]{8,128}", idem):
            raise ValueError("Unknown workflow or invalid idempotency key")
        agent_plan = self._agent_plan(workflow) if workflow in AGENT_WORKFLOWS else None
        with self.transaction() as conn:
            prior = conn.execute(
                "SELECT id,workflow,actor FROM runs WHERE project=? AND idem=?", (project, idem)
            ).fetchone()
            if prior:
                if prior["workflow"] != workflow or prior["actor"] != actor:
                    raise RuntimeConflict("Idempotency key already binds another submission")
                run_id = prior["id"]
            else:
                if (
                    conn.execute(
                        "SELECT count(*) FROM runs WHERE actor=? AND created>?",
                        (actor, time.time() - 86400),
                    ).fetchone()[0]
                    >= 100
                ):
                    raise RuntimeConflict("Daily operator run quota reached")
                run_id = str(uuid.uuid4())
                plan = {
                    "schema_version": 1,
                    "project": project,
                    "workflow": workflow,
                    "steps": WORKFLOWS[workflow]["steps"],
                    "sources": self._sources(),
                    "scope": "OFFLINE_LOCAL_READ_ONLY",
                    "provider_dispatch": False,
                    "paid_calls": False,
                    "release": False,
                    "independent_visual_review": "NOT_PERFORMED",
                    "executor_revision": "1",
                    "max_step_seconds": self.timeout,
                    "memory_snapshot": self.memory(PROJECT, "", trusted_only=True),
                }
                if agent_plan:
                    plan.update(agent_plan)
                encoded = canonical(plan)
                now = time.time()
                conn.execute(
                    "INSERT INTO runs(id,project,workflow,idem,actor,status,plan,plan_hash,created,updated) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        run_id,
                        project,
                        workflow,
                        idem,
                        actor,
                        "PENDING_APPROVAL",
                        encoded,
                        digest(encoded.encode()),
                        now,
                        now,
                    ),
                )
                self.event(conn, run_id, "CREATED", actor, {"scope": plan["scope"]})
        return self.get(run_id)

    def _get(self, conn: sqlite3.Connection, run_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise RuntimeNotFound("Unknown run")
        return row

    def _agent_drift(self, row: sqlite3.Row, plan: dict[str, Any]) -> bool:
        current = self._agent_plan(row["workflow"])
        return any(plan.get(key) != value for key, value in current.items())

    def _drift(self, row: sqlite3.Row) -> bool:
        try:
            plan = json.loads(row["plan"])
            return (
                (row["workflow"] in AGENT_WORKFLOWS and self._agent_drift(row, plan))
                or self._sources() != plan["sources"]
                or self.memory(PROJECT, "", trusted_only=True) != plan["memory_snapshot"]
            )
        except (OSError, ValueError, KeyError):
            return True

    def _invalidate(self, conn: sqlite3.Connection, row: sqlite3.Row, actor: str) -> None:
        conn.execute(
            "UPDATE runs SET status='INVALIDATED',approval=NULL,updated=? WHERE id=?",
            (time.time(), row["id"]),
        )
        self.event(conn, row["id"], "SOURCE_DRIFT", actor, {"approval_revoked": True})

    def approve(self, run_id: str, plan_hash: str, actor: str) -> dict[str, Any]:
        invalid = False
        with self.transaction() as conn:
            row = self._get(conn, run_id)
            if row["status"] != "PENDING_APPROVAL" or row["plan_hash"] != plan_hash:
                raise RuntimeConflict(
                    "Only a pending run with this exact plan hash can be approved"
                )
            if self._drift(row):
                self._invalidate(conn, row, actor)
                invalid = True
            else:
                approval = {
                    "actor": actor,
                    "plan_hash": plan_hash,
                    "approved_at": time.time(),
                    "expires_at": time.time() + 900,
                    "scope": json.loads(row["plan"])["scope"],
                }
                conn.execute(
                    "UPDATE runs SET status='APPROVED',approval=?,updated=? WHERE id=?",
                    (canonical(approval), time.time(), run_id),
                )
                self.event(conn, run_id, "OWNER_APPROVED", actor, approval)
        if invalid:
            raise RuntimeConflict("Sources changed; create and approve a fresh plan")
        return self.get(run_id)

    def get(self, run_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = dict(self._get(conn, run_id))
            events = [
                {
                    "seq": e["seq"],
                    "kind": e["kind"],
                    "actor": e["actor"],
                    "at": e["at"],
                    "data": json.loads(e["data"]),
                }
                for e in conn.execute("SELECT * FROM events WHERE run_id=? ORDER BY seq", (run_id,))
            ]
            reviews = [
                dict(r)
                for r in conn.execute("SELECT * FROM reviews WHERE run_id=? ORDER BY at", (run_id,))
            ]
        return {
            "artifact_hash": digest(
                canonical([e["data"] for e in events if e["kind"] == "STEP_FINISHED"]).encode()
            ),
            "reviews": reviews,
            "id": row["id"],
            "project": row["project"],
            "workflow": row["workflow"],
            "actor": row["actor"],
            "status": row["status"],
            "plan_hash": row["plan_hash"],
            "plan": json.loads(row["plan"]),
            "approval": json.loads(row["approval"]) if row["approval"] else None,
            "created_at": row["created"],
            "updated_at": row["updated"],
            "events": events,
            "steps": [e["data"] for e in events if e["kind"] == "STEP_FINISHED"],
        }

    def runs(
        self, project: str, *, actor: str | None = None, owner: bool = False
    ) -> list[dict[str, Any]]:
        self.project(project)
        self.recover()
        with self.connect() as conn:
            sql = "SELECT id FROM runs WHERE project=?"
            params: list[Any] = [project]
            if not owner:
                sql += " AND actor=?"
                params.append(actor)
            ids = [
                r["id"]
                for r in conn.execute(sql + " ORDER BY created DESC, id DESC LIMIT 50", params)
            ]
        return [self.get(r) for r in ids]

    def recover(self) -> int:
        """Expired executions become interrupted, never replayed or reapproved."""
        with self.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM runs WHERE status='RUNNING' AND lease<?", (time.time(),)
            ).fetchall()
            for row in rows:
                conn.execute(
                    "UPDATE runs SET status='INTERRUPTED',approval=NULL,updated=? WHERE id=?",
                    (time.time(), row["id"]),
                )
                self.event(conn, row["id"], "LEASE_EXPIRED", "runtime", {"automatic_replay": False})
        return len(rows)

    def cancel(self, run_id: str, actor: str) -> dict[str, Any]:
        with self.transaction() as conn:
            row = self._get(conn, run_id)
            if row["status"] not in TERMINAL:
                status = "RUNNING" if row["status"] == "RUNNING" else "CANCELLED"
                conn.execute(
                    "UPDATE runs SET cancel=1,status=?,approval=NULL,updated=? WHERE id=?",
                    (status, time.time(), run_id),
                )
                self.event(conn, run_id, "CANCEL_REQUESTED", actor, {"process_poll_seconds": 0.1})
        return self.get(run_id)

    def _cancelled(self, run_id: str) -> bool:
        with self.connect() as conn:
            row = self._get(conn, run_id)
            return bool(row["cancel"]) or row["status"] != "RUNNING" or row["lease"] < time.time()

    def _command(self, step: str) -> list[str]:
        commands = {
            "product-registry": [
                sys.executable,
                str(self.root / "scripts/sync_product_registry.py"),
                "--check",
            ],
            "campaign-contract": [
                sys.executable,
                str(self.root / ".agents/skills/skyyrose-campaign-ooda/scripts/workflow_guard.py"),
                "verify",
            ],
            "fashion-migration": [
                sys.executable,
                str(self.team / "scripts/verify-skyyrose-migration.py"),
            ],
        }
        return commands[step]

    def _process(self, run_id: str, step: str) -> dict[str, Any]:
        command = self._command(step)
        started = time.time()
        with (
            tempfile.TemporaryDirectory(prefix="godmode-check-") as temp,
            tempfile.TemporaryFile() as log,
        ):
            env = {
                "PATH": os.defpath,
                "HOME": temp,
                "LANG": "en_US.UTF-8",
                "PYTHONPATH": str(self.root),
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            process = subprocess.Popen(
                command,
                cwd=self.root,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            cause = None
            try:
                while process.poll() is None:
                    if self._cancelled(run_id):
                        cause = "CANCELLED"
                    elif time.time() - started > self.timeout:
                        cause = "TIMEOUT"
                    elif os.fstat(log.fileno()).st_size > 1_000_000:
                        cause = "OUTPUT_LIMIT"
                    if cause:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        break
                    time.sleep(0.1)
                process.wait(timeout=5)
            finally:
                # Kill the whole owned process group, including children whose parent exited.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5)
            if os.fstat(log.fileno()).st_size > 1_000_000:
                cause = "OUTPUT_LIMIT"
            log.seek(0)
            output = scrub(log.read(16000).decode("utf-8", errors="replace"))
        return {
            "id": step,
            "status": cause or ("PASSED" if process.returncode == 0 else "FAILED"),
            "exit_code": process.returncode,
            "elapsed_seconds": round(time.time() - started, 3),
            "output": output,
            "output_sha256": digest(output.encode()),
            "command_id": step,
            "verification_scope": "MECHANICAL_ONLY",
        }

    def _assignment(self, row: sqlite3.Row) -> dict[str, Any]:
        manifest = json.loads(
            (
                self.team / "skills/fashion-theme-team/references/skyyrose-skill-migration.json"
            ).read_text()
        )
        skills = []
        for item in manifest["skills"]:
            path = self.team / item["target"]
            text = path.read_text()
            skills.append(
                {
                    "id": item["id"],
                    "sha256": digest(text.encode()),
                    "headings": re.findall(r"^#{1,3} (.+)$", text, re.MULTILINE),
                    "example_reference_present": "example" in text.lower(),
                    "owner": "fashion-theme-team",
                }
            )
        artifact = {
            "mission": "Source-bound SkyyRose skill audit and team routing",
            "parent": "god-mode",
            "team": "fashion-theme-team",
            "method": "DETERMINISTIC_SOURCE_INSPECTION_NOT_LLM_AGENT",
            "skills": skills,
            "workflow": row["workflow"],
            "source_count": len(json.loads(row["plan"])["sources"]),
            "product_authority": "get_product(sku); founder corrections authoritative",
            "memory_context": json.loads(row["plan"])["memory_snapshot"],
            "memory_policy": "Context data only, never execution instructions or approval",
            "independent_review": "NOT_PERFORMED",
            "release": "NOT_AUTHORIZED",
        }
        return {
            "id": "team-assignment",
            "status": "PASSED",
            "artifact": artifact,
            "artifact_sha256": digest(canonical(artifact).encode()),
            "verification_scope": "SOURCE_STRUCTURE_ONLY",
        }

    def execute(self, run_id: str, plan_hash: str, actor: str) -> dict[str, Any]:
        self.recover()
        invalid = False
        with self.transaction() as conn:
            row = self._get(conn, run_id)
            approval = json.loads(row["approval"]) if row["approval"] else {}
            if (
                row["status"] != "APPROVED"
                or row["plan_hash"] != plan_hash
                or approval.get("plan_hash") != plan_hash
                or approval.get("expires_at", 0) < time.time()
            ):
                raise RuntimeConflict("A fresh owner approval of this exact plan is required")
            if self._drift(row):
                self._invalidate(conn, row, actor)
                invalid = True
            else:
                if conn.execute("SELECT 1 FROM runs WHERE status='RUNNING'").fetchone():
                    raise RuntimeConflict(
                        "Workstation executor is busy; no duplicate task was launched"
                    )
                if row["workflow"] in AGENT_WORKFLOWS:
                    used = conn.execute(
                        "SELECT count(*) FROM events WHERE kind='AGENT_ALLOWANCE_RESERVED' AND at>?",
                        (time.time() - 86400,),
                    ).fetchone()[0]
                    if used >= 2:
                        raise RuntimeConflict(
                            "Daily two-run agent qualification allowance exhausted; reservations are not automatically refunded"
                        )
                    self.event(
                        conn,
                        run_id,
                        "AGENT_ALLOWANCE_RESERVED",
                        actor,
                        {
                            "claude_max_budget_usd": 1.0,
                            "codex_auth": "existing_chatgpt_allowance",
                            "max_calls": 2,
                            "unknown_usage_retained": True,
                        },
                    )
                conn.execute(
                    "UPDATE runs SET status='RUNNING',lease=?,updated=? WHERE id=?",
                    (
                        time.time()
                        + len(json.loads(row["plan"])["steps"])
                        * (
                            max(
                                self.timeout,
                                json.loads(row["plan"])
                                .get("agent_contract", {})
                                .get("timeout_seconds", 0),
                            )
                            + 10
                        )
                        + 30,
                        time.time(),
                        run_id,
                    ),
                )
                self.event(
                    conn,
                    run_id,
                    "EXECUTION_STARTED",
                    actor,
                    {"plan_hash": plan_hash, "approval_actor": approval["actor"]},
                )
        if invalid:
            raise RuntimeConflict("Source drift invalidated approval")
        outcome = "SUCCEEDED"
        try:
            for step in json.loads(row["plan"])["steps"]:
                if self._cancelled(run_id):
                    outcome = "CANCELLED"
                    break
                if self._drift(row):
                    outcome = "INVALIDATED"
                    break
                if step["id"] in {"claude-worker", "codex-reviewer"}:
                    receipt = self._agent_step(row, step["id"])
                else:
                    receipt = (
                        self._assignment(row)
                        if step["id"] == "team-assignment"
                        else self._process(run_id, step["id"])
                    )
                with self.transaction() as conn:
                    current = self._get(conn, run_id)
                    if (
                        current["status"] != "RUNNING"
                        or current["cancel"]
                        or current["lease"] < time.time()
                    ):
                        outcome = "CANCELLED"
                        break
                    self.event(conn, run_id, "STEP_FINISHED", "runtime-verifier", receipt)
                if receipt["status"] != "PASSED":
                    outcome = "CANCELLED" if receipt["status"] == "CANCELLED" else "FAILED"
                    break
            if self._drift(row):
                outcome = "INVALIDATED"
            elif self._cancelled(run_id):
                outcome = "CANCELLED"
        except Exception as exc:
            outcome = "FAILED"
            with self.transaction() as conn:
                if self._get(conn, run_id)["status"] != "RUNNING":
                    return self.get(run_id)
                self.event(
                    conn,
                    run_id,
                    "EXECUTION_ERROR",
                    "runtime",
                    {
                        "error_type": type(exc).__name__,
                        "detail": "Local execution failed; inspect bounded verifier receipts",
                    },
                )
        self.recover()
        with self.transaction() as conn:
            current = self._get(conn, run_id)
            if current["status"] != "RUNNING":
                return self.get(run_id)
            # Cancellation can commit after the last unlocked poll. Respect it
            # inside the same transaction that commits the terminal outcome.
            if current["cancel"]:
                outcome = "CANCELLED"
            conn.execute(
                "UPDATE runs SET status=?,approval=NULL,lease=NULL,updated=? WHERE id=? AND status='RUNNING'",
                (outcome, time.time(), run_id),
            )
            persisted_status = self._get(conn, run_id)["status"]
            self.event(
                conn,
                run_id,
                "EXECUTION_FINISHED",
                "runtime",
                {
                    "status": persisted_status,
                    "owner_acceptance": "NOT_GRANTED",
                    "production_authority": False,
                },
            )
        return self.get(run_id)

    def memory(
        self,
        project: str,
        query: str,
        *,
        trusted_only: bool = False,
        actor: str | None = None,
        owner: bool = False,
    ) -> list[dict[str, Any]]:
        self.project(project)
        if len(query) > 200:
            raise ValueError("Search query exceeds limit")
        with self.connect() as conn:
            sql = """WITH RECURSIVE ancestry(descendant, ancestor) AS (
                SELECT id, supersedes FROM memories WHERE supersedes IS NOT NULL
                UNION
                SELECT ancestry.descendant, parent.supersedes
                FROM ancestry JOIN memories parent ON parent.id=ancestry.ancestor
                WHERE parent.supersedes IS NOT NULL
            ) SELECT * FROM memories WHERE project=?
              AND (content LIKE ? ESCAPE '\\' OR provenance LIKE ? ESCAPE '\\')"""
            literal = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            params: list[Any] = [project, f"%{literal}%", f"%{literal}%"]
            if actor is not None and not owner:
                sql += " AND (trust='OWNER_ACCEPTED' OR actor=?)"
                params.append(actor)
            if trusted_only:
                sql += """ AND trust='OWNER_ACCEPTED' AND NOT EXISTS (
                    SELECT 1 FROM ancestry JOIN memories newer ON newer.id=ancestry.descendant
                    WHERE ancestry.ancestor=memories.id AND newer.trust='OWNER_ACCEPTED'
                )"""
            # Search is bounded for display; an approval context must retain
            # every current accepted decision, including older standing rules.
            suffix = " ORDER BY created DESC, id DESC" + ("" if trusted_only else " LIMIT 100")
            return [dict(r) for r in conn.execute(sql + suffix, params)]

    def add_memory(
        self,
        project: str,
        kind: str,
        content: str,
        provenance: str,
        actor: str,
        supersedes: str | None = None,
        owner: bool = False,
    ) -> dict[str, Any]:
        self.project(project)
        if (
            kind not in {"decision", "observation", "handoff"}
            or not 1 <= len(content.strip()) <= 8000
            or not 1 <= len(provenance.strip()) <= 500
        ):
            raise ValueError("Invalid memory kind/content/provenance")
        if re.search(
            r"(?i)(?:\b(?:sk|ghp|github_pat|AKIA)[-_][A-Za-z0-9]{12,}|-----BEGIN .*PRIVATE KEY|bearer\s+[A-Za-z0-9._-]{12,}|(?:password|api[_-]?key|secret|token)\s*[=:]\s*\S+)",
            content + " " + provenance,
        ):
            raise ValueError("Credential-like data is not permitted in project memory")
        with self.transaction() as conn:
            if (
                conn.execute(
                    "SELECT count(*) FROM memories WHERE actor=? AND created>?",
                    (actor, time.time() - 86400),
                ).fetchone()[0]
                >= 100
            ):
                raise RuntimeConflict("Daily operator memory quota reached")
            revision = 1
            if supersedes:
                old = conn.execute(
                    "SELECT * FROM memories WHERE id=? AND project=?", (supersedes, project)
                ).fetchone()
                if not old:
                    raise RuntimeNotFound("Superseded record does not exist in project")
                if not owner and (old["actor"] != actor or old["trust"] != "UNTRUSTED"):
                    raise RuntimeConflict(
                        "Only the owner may revise shared or another actor's memory"
                    )
                if old["kind"] != kind:
                    raise RuntimeConflict("A revision must retain its original memory kind")
                revision = old["revision"] + 1
            memory_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO memories(id,project,kind,content,provenance,trust,actor,created,revision,supersedes) VALUES(?,?,?,?,?,'UNTRUSTED',?,?,?,?)",
                (
                    memory_id,
                    project,
                    kind,
                    content,
                    provenance,
                    actor,
                    time.time(),
                    revision,
                    supersedes,
                ),
            )
            record = dict(
                conn.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
            )
        return record

    def promote(self, memory_id: str, actor: str) -> dict[str, Any]:
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
            if not row:
                raise RuntimeNotFound("Unknown memory")
            if row["trust"] != "UNTRUSTED":
                raise RuntimeConflict("Memory has already been promoted")
            ancestors: set[str] = set()
            root = row
            while root["supersedes"]:
                ancestors.add(root["supersedes"])
                root = conn.execute(
                    "SELECT * FROM memories WHERE id=?", (root["supersedes"],)
                ).fetchone()
            accepted = conn.execute(
                """WITH RECURSIVE lineage(id) AS (
                    SELECT id FROM memories WHERE id=?
                    UNION
                    SELECT child.id FROM memories child JOIN lineage ON child.supersedes=lineage.id
                ) SELECT memories.id FROM memories JOIN lineage USING(id)
                  WHERE trust='OWNER_ACCEPTED'""",
                (root["id"],),
            ).fetchall()
            if any(record["id"] not in ancestors for record in accepted):
                raise RuntimeConflict("A different revision already supersedes this record")
            conn.execute(
                "UPDATE memories SET trust='OWNER_ACCEPTED',promoted_by=?,promoted_at=? WHERE id=?",
                (actor, time.time(), memory_id),
            )
            return dict(conn.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone())

    def review(
        self, run_id: str, plan_hash: str, artifact_hash: str, verdict: str, notes: str, actor: str
    ) -> dict[str, Any]:
        """Independent review is a separate human attestation, never a release approval."""
        run = self.get(run_id)
        if verdict not in {"PASS", "FAIL"} or not notes.strip() or len(notes) > 4000:
            raise ValueError("Review requires a verdict and bounded observations")
        with self.transaction() as conn:
            row = self._get(conn, run_id)
            approval_events = conn.execute(
                "SELECT actor FROM events WHERE run_id=? AND kind IN ('OWNER_APPROVED','EXECUTION_STARTED')",
                (run_id,),
            ).fetchall()
            producers = {row["actor"], *[event["actor"] for event in approval_events]}
            if actor in producers:
                raise RuntimeConflict("Reviewer must differ from submitter, approver, and executor")
            if (
                row["status"] != "SUCCEEDED"
                or row["plan_hash"] != plan_hash
                or run["artifact_hash"] != artifact_hash
            ):
                raise RuntimeConflict(
                    "Review must bind a mechanically successful run's exact plan and artifacts"
                )
            if self._drift(row):
                raise RuntimeConflict("Sources changed; a fresh run is required before review")
            review_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO reviews VALUES(?,?,?,?,?,?,?,?)",
                (
                    review_id,
                    run_id,
                    actor,
                    plan_hash,
                    artifact_hash,
                    verdict,
                    scrub(notes),
                    time.time(),
                ),
            )
            self.event(
                conn,
                run_id,
                "INDEPENDENT_REVIEW",
                actor,
                {"review_id": review_id, "verdict": verdict, "release_authority": False},
            )
        return self.get(run_id)
