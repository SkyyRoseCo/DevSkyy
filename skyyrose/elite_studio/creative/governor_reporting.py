"""Verified, bounded accounting projections with no writable Governor capability.

Ledger authentication proves persisted records, not provider execution, billing
truth, or owner approval. No transport, runtime, signer, or grant is constructed.
"""

from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from decimal import Decimal, localcontext
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .spend_ledger import DEFAULT_UNITS, LedgerError, SpendLedger

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_STATES = {
    "RESERVED",
    "SUBMITTED",
    "PROVIDER_RUNNING",
    "RECONCILIATION_REQUIRED",
    "COMPLETED",
    "FAILED",
    "CANCELED",
}
_BILLING = {"RESERVED", "PENDING_ACTUAL", "FINALIZED"}


def identifier(value: object) -> str:
    """Identifiers are opaque values; URLs and arbitrary prose are not emitted."""
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise LedgerError("Invalid bounded report identity")
    return value


class ReadOnlyLedger:
    """Only verification methods are shared; mutation methods are unavailable.

    Each report verifies the signed event chain and external minimum checkpoint
    within one read snapshot. SQLite enforces mode=ro and query_only, including
    when application code accidentally attempts a write.
    """

    _verified = SpendLedger._verified
    _grant = SpendLedger._grant
    _load = SpendLedger._load
    _reduce = SpendLedger._reduce

    def __init__(
        self,
        database: Path,
        authority_public_key: bytes,
        integrity_key: bytes,
        *,
        minimum_checkpoint: dict,
        max_events: int = 10_000,
    ):
        if len(integrity_key) < 32:
            raise LedgerError("Strong ledger integrity key required")
        if (
            not isinstance(minimum_checkpoint, dict)
            or set(minimum_checkpoint) != {"sequence", "hash"}
            or type(minimum_checkpoint["sequence"]) is not int
            or minimum_checkpoint["sequence"] < 0
            or (
                minimum_checkpoint["hash"] != ""
                if minimum_checkpoint["sequence"] == 0
                else not isinstance(minimum_checkpoint["hash"], str)
                or not _DIGEST.fullmatch(minimum_checkpoint["hash"])
            )
        ):
            raise LedgerError("Trusted external minimum checkpoint required")
        if type(max_events) is not int or not 1 <= max_events <= 100_000:
            raise LedgerError("Bounded ledger event count required")
        self.database = Path(database).resolve(strict=True)
        if not self.database.is_file():
            raise LedgerError("Existing ledger database required")
        self._public_key = Ed25519PublicKey.from_public_bytes(authority_public_key)
        self._integrity_key = integrity_key
        self._checkpoint = dict(minimum_checkpoint)
        self.supported_units = DEFAULT_UNITS
        self.max_events = max_events

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database.as_uri() + "?mode=ro", uri=True, isolation_level=None, timeout=5
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        return connection

    def report(self, *, job_id: str, grant_id: str) -> dict:
        job_id, grant_id = identifier(job_id), identifier(grant_id)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN")
            count = connection.execute("SELECT count(*) FROM economic_events").fetchone()[0]
            size = connection.execute(
                "SELECT max(length(CAST(payload AS BLOB))) FROM economic_events"
            ).fetchone()[0]
            if count > self.max_events or (size or 0) > 1_048_576:
                raise LedgerError("Ledger exceeds bounded report read limits")
            state = self._load(connection)
            head = connection.execute("SELECT sequence FROM ledger_head WHERE id=1").fetchone()
            grant = state["grants"].get(grant_id)
            if grant is None or grant["job_id"] != job_id:
                raise LedgerError("Requested job/grant scope not found")
            operations = [
                op
                for op in state["operations"].values()
                if op["grant_id"] == grant_id and op["job_id"] == job_id
            ]
            resources = {
                key: {}
                for key in ("authorized", "consumed", "held", "available", "unspent_authorization")
            }
            with localcontext() as context:
                context.prec = 80
                for unit, value in grant["limits"].items():
                    cap = Decimal(value)
                    consumed = sum(
                        (
                            Decimal(op["actual"][unit])
                            for op in operations
                            if op["billing_state"] == "FINALIZED"
                        ),
                        Decimal(0),
                    )
                    held = sum(
                        (
                            Decimal(op["maximum"][unit])
                            for op in operations
                            if op["billing_state"] != "FINALIZED"
                        ),
                        Decimal(0),
                    )
                    for key, amount in (
                        ("authorized", cap),
                        ("consumed", consumed),
                        ("held", held),
                        ("available", cap - consumed - held),
                        ("unspent_authorization", cap - consumed),
                    ):
                        resources[key][unit] = str(amount)
            projected = [self._operation(op) for op in operations]
            simulated = any(op.get("metadata", {}).get("simulated") is True for op in operations)
            return {
                "schema_version": "1.0",
                "evidence_mode": "SIMULATED" if simulated else "LEDGER_RECORDS_ONLY",
                "ledger_authenticated": True,
                "ledger": {"head_sequence": head["sequence"]},
                "job_id": job_id,
                "grant_id": grant_id,
                "resources": resources,
                "operations": projected,
                "stopped": job_id in state["stopped"],
                "revoked": grant_id in state["revoked"],
                "closed": job_id in state["closed"],
                "owner_acceptance": "UNVERIFIED",
                "actual_spend": None,
                "current_provider_execution": None,
            }

    @staticmethod
    def _operation(op: dict) -> dict:
        if (
            op["state"] not in _STATES
            or op["billing_state"] not in _BILLING
            or not _DIGEST.fullmatch(op["contract_digest"])
        ):
            raise LedgerError("Unsupported operation report schema")
        from .spend_ledger import _usage

        maximum = _usage(op["maximum"], DEFAULT_UNITS)
        actual = _usage(op["actual"], frozenset(maximum)) if op["actual"] is not None else None
        task = op["provider_operation_id"]
        return {
            "operation_id": identifier(op["operation_id"]),
            "job_id": identifier(op["job_id"]),
            "grant_id": identifier(op["grant_id"]),
            "contract_id": op["contract_digest"],
            "task_id": identifier(task) if task is not None else None,
            "state": op["state"],
            "billing_state": op["billing_state"],
            "billing_unknown": op["billing_state"] != "FINALIZED",
            "maximum": maximum,
            "actual": actual,
            "review_state": "RECORDED" if op["review"] is not None else "MISSING",
        }
