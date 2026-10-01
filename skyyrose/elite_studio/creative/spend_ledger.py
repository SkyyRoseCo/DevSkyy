"""Transactional economic ledger for a trusted governor service.

Creative workers must not receive the authority private key, integrity key, or a
writable database handle. Python object privacy and same-UID files are NOT a
sandbox. Ed25519 authenticates grants/admin commands; HMAC chains authenticate
ledger events. External checkpoints are required to detect whole-database rollback.
No network operation, billing inference, or creative approval is performed here.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
from collections.abc import Callable, Iterator, Mapping
from contextlib import closing, contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

DEFAULT_UNITS = frozenset(
    {
        "usd",
        "credits",
        "provider_credits",
        "provider_api_requests",
        "renders",
        "images",
        "megapixels",
        "video_seconds",
        "frames",
        "upscales",
        "edits",
        "inference_tokens",
        "compute_seconds",
        "storage_bytes",
    }
)
TERMINAL = frozenset({"COMPLETED", "FAILED", "CANCELED"})


class LedgerError(ValueError):
    """Invalid, stale, or unverifiable accounting evidence."""


class SpendDenied(LedgerError):
    """No new paid action is authorized."""


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _decimal(value: object) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise LedgerError("Resource amounts require Decimal, integer, or exact decimal string")
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise LedgerError("Invalid decimal amount") from exc
    if (
        not result.is_finite()
        or result < 0
        or result > Decimal("1e18")
        or result.as_tuple().exponent < -18
    ):
        raise LedgerError("Unsupported negative, nonfinite, or unbounded resource amount")
    return result


def _usage(values: Mapping, supported: frozenset[str], *, empty: bool = False) -> dict[str, str]:
    if not isinstance(values, Mapping) or (not values and not empty):
        raise LedgerError("COST_UNKNOWN: explicit bounded resource dimensions required")
    if set(values) - supported:
        raise LedgerError("Unsupported resource unit")
    return {key: str(_decimal(value)) for key, value in values.items()}


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise LedgerError("Explicit UTC-aware grant expiry required") from exc
    if parsed.tzinfo is None:
        raise LedgerError("Grant expiry needs timezone")
    return parsed


@dataclass(frozen=True)
class SpendGrant:
    grant_id: str
    job_id: str
    providers: tuple[str, ...]
    purposes: tuple[str, ...]
    limits: Mapping[str, Decimal | str | int]
    max_single_call: Mapping[str, Decimal | str | int]
    valid_until: str
    direction_limits: Mapping[str, Mapping[str, Decimal | str | int]] = field(default_factory=dict)
    stage_limits: Mapping[str, Mapping[str, Decimal | str | int]] = field(default_factory=dict)
    issued_by: str = "owner_authority"


class SpendAuthority:
    """Authority-side signer. Never give this object/key to a creative worker."""

    def __init__(self, private_key: Ed25519PrivateKey):
        self._key = private_key

    @property
    def public_key(self) -> bytes:
        return self._key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

    def _sign(self, body: dict) -> dict:
        return {
            "body": body,
            "signature": base64.b64encode(self._key.sign(_json(body).encode())).decode(),
        }

    def issue(self, grant: SpendGrant) -> dict:
        """Sign a snapshot, not a mutable shared grant mapping."""
        body = asdict(grant)
        for key in ("limits", "max_single_call"):
            body[key] = {unit: str(_decimal(value)) for unit, value in body[key].items()}
        for key in ("direction_limits", "stage_limits"):
            body[key] = {
                scope: {unit: str(_decimal(value)) for unit, value in limits.items()}
                for scope, limits in body[key].items()
            }
        body["providers"], body["purposes"] = list(body["providers"]), list(body["purposes"])
        return self._sign({"kind": "SPEND_GRANT", "grant": body})

    def command(
        self,
        action: str,
        target: str,
        reason: str,
        command_id: str,
        *,
        new_grant_id: str | None = None,
    ) -> dict:
        """Sign immutable revocation or closure; overrides require a new grant."""
        if action not in {"REVOKE_GRANT", "CLOSE_JOB", "OVERRIDE_STOP"}:
            raise LedgerError("Unsupported authority command")
        if not all(
            isinstance(value, str) and value.strip() for value in (target, reason, command_id)
        ):
            raise LedgerError("Authority command requires target, reason and stable ID")
        if action == "OVERRIDE_STOP" and not new_grant_id:
            raise LedgerError("Override requires a new grant ID")
        return self._sign(
            {
                "kind": "AUTHORITY_COMMAND",
                "action": action,
                "target": target,
                "reason": reason,
                "command_id": command_id,
                "new_grant_id": new_grant_id,
            }
        )


class SpendLedger:
    """Governor-owned accounting API. All mutations serialize in SQLite transactions."""

    def __init__(
        self,
        database: Path,
        authority_public_key: bytes,
        integrity_key: bytes,
        supported_units: frozenset[str] = DEFAULT_UNITS,
        clock: Callable[[], datetime] | None = None,
        minimum_checkpoint: dict | None = None,
    ):
        if len(integrity_key) < 32 or not supported_units or set(supported_units) - DEFAULT_UNITS:
            raise LedgerError("Strong integrity key and supported bounded units required")
        self.database = Path(database)
        self._public_key = Ed25519PublicKey.from_public_bytes(authority_public_key)
        self._integrity_key = integrity_key
        self.supported_units = frozenset(supported_units)
        self._clock = clock or (lambda: datetime.now(UTC))
        self._checkpoint = minimum_checkpoint
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS economic_events (
                  sequence INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, type TEXT NOT NULL,
                  payload TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS ledger_head (id INTEGER PRIMARY KEY CHECK(id=1), sequence INTEGER NOT NULL, hash TEXT NOT NULL);
                INSERT OR IGNORE INTO ledger_head VALUES (1, 0, '');
                CREATE TRIGGER IF NOT EXISTS no_event_update BEFORE UPDATE ON economic_events BEGIN SELECT RAISE(ABORT, 'Append-only economic events'); END;
                CREATE TRIGGER IF NOT EXISTS no_event_delete BEFORE DELETE ON economic_events BEGIN SELECT RAISE(ABORT, 'Append-only economic events'); END;
            """)
        with self._transaction():
            pass

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @contextmanager
    def _transaction(self) -> Iterator[tuple[sqlite3.Connection, dict]]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            state = self._load(connection)
            yield connection, state
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _verified(self, envelope: dict, kind: str) -> dict:
        try:
            self._public_key.verify(
                base64.b64decode(envelope["signature"], validate=True),
                _json(envelope["body"]).encode(),
            )
            body = envelope["body"]
        except (InvalidSignature, KeyError, TypeError, ValueError) as exc:
            raise SpendDenied("Untrusted authority signature") from exc
        if body.get("kind") != kind:
            raise SpendDenied("Wrong authority object kind")
        return body

    def _grant(self, value: dict) -> dict:
        required = set(SpendGrant.__dataclass_fields__)
        if set(value) != required or not all(
            isinstance(value[k], str) and value[k].strip()
            for k in ("grant_id", "job_id", "issued_by")
        ):
            raise LedgerError("Invalid immutable grant schema")
        for key in ("providers", "purposes"):
            if (
                not value[key]
                or not isinstance(value[key], list)
                or any(not isinstance(x, str) or not x.strip() for x in value[key])
            ):
                raise LedgerError("Grant must scope provider and purpose")
        _time(value["valid_until"])
        value["limits"] = _usage(value["limits"], self.supported_units)
        value["max_single_call"] = _usage(
            value["max_single_call"], frozenset(value["limits"]), empty=True
        )
        for key in ("direction_limits", "stage_limits"):
            if not isinstance(value[key], dict):
                raise LedgerError("Invalid scoped caps")
            value[key] = {
                scope: _usage(caps, frozenset(value["limits"]))
                for scope, caps in value[key].items()
            }
        return value

    def _load(self, connection: sqlite3.Connection) -> dict:
        state = {
            "grants": {},
            "operations": {},
            "revoked": set(),
            "closed": set(),
            "stopped": {},
            "commands": {},
            "override_grants": {},
            "grant_sequence": {},
            "stop_sequence": {},
            "sequence": 0,
        }
        previous, sequence = "", 0
        for row in connection.execute("SELECT * FROM economic_events ORDER BY sequence"):
            sequence += 1
            payload = json.loads(row["payload"])
            signed = {
                "sequence": row["sequence"],
                "timestamp": row["timestamp"],
                "type": row["type"],
                "payload": payload,
                "previous_hash": row["previous_hash"],
            }
            expected = hmac.new(
                self._integrity_key, _json(signed).encode(), hashlib.sha256
            ).hexdigest()
            if (
                row["sequence"] != sequence
                or row["previous_hash"] != previous
                or not hmac.compare_digest(expected, row["event_hash"])
            ):
                raise LedgerError("Economic ledger integrity failure")
            previous = row["event_hash"]
            if (
                self._checkpoint
                and sequence == self._checkpoint["sequence"]
                and previous != self._checkpoint["hash"]
            ):
                raise LedgerError("External ledger checkpoint mismatch")
            self._reduce(state, row["type"], payload)
        head = connection.execute("SELECT sequence, hash FROM ledger_head WHERE id=1").fetchone()
        if not head or head["sequence"] != sequence or head["hash"] != previous:
            raise LedgerError("Economic ledger head mismatch")
        if self._checkpoint and sequence < self._checkpoint["sequence"]:
            raise LedgerError("Economic ledger rollback detected")
        return state

    def _reduce(self, state: dict, event: str, payload: dict) -> None:
        state["sequence"] += 1
        if event == "GRANT_CREATED":
            grant = self._grant(self._verified(payload, "SPEND_GRANT")["grant"])
            state["grants"][grant["grant_id"]] = grant
            state["grant_sequence"][grant["grant_id"]] = state["sequence"]
        elif event == "AUTHORITY_COMMAND":
            command = self._verified(payload, "AUTHORITY_COMMAND")
            state["commands"][command["command_id"]] = command
            if command["action"] == "OVERRIDE_STOP":
                state["override_grants"][command["target"]] = command["new_grant_id"]
            else:
                state["revoked" if command["action"] == "REVOKE_GRANT" else "closed"].add(
                    command["target"]
                )
        elif event == "BUDGET_RESERVED":
            state["operations"][payload["operation_id"]] = payload
        elif event == "OPERATION_UPDATED":
            state["operations"][payload["operation_id"]].update(payload["updates"])
        elif event in {"PAID_STOP", "GOAL_SATISFIED"}:
            state["stopped"][payload["job_id"]] = payload["reason"]
            state["stop_sequence"][payload["job_id"]] = state["sequence"]
            state["override_grants"].pop(payload["job_id"], None)
        else:
            raise LedgerError("Unknown economic event")

    def _append(
        self, connection: sqlite3.Connection, state: dict, event: str, payload: dict
    ) -> None:
        head = connection.execute("SELECT sequence, hash FROM ledger_head WHERE id=1").fetchone()
        row = {
            "sequence": head["sequence"] + 1,
            "timestamp": self._clock().isoformat(),
            "type": event,
            "payload": json.loads(_json(payload)),
            "previous_hash": head["hash"],
        }
        digest = hmac.new(self._integrity_key, _json(row).encode(), hashlib.sha256).hexdigest()
        connection.execute(
            "INSERT INTO economic_events VALUES (?, ?, ?, ?, ?, ?)",
            (
                row["sequence"],
                row["timestamp"],
                event,
                _json(row["payload"]),
                row["previous_hash"],
                digest,
            ),
        )
        connection.execute(
            "UPDATE ledger_head SET sequence=?, hash=? WHERE id=1", (row["sequence"], digest)
        )
        self._reduce(state, event, row["payload"])

    def install_grant(self, envelope: dict) -> dict:
        """Only a signature from the configured authority can install a ceiling."""
        envelope = json.loads(_json(envelope))
        grant = self._grant(self._verified(envelope, "SPEND_GRANT")["grant"])
        with self._transaction() as (connection, state):
            existing = state["grants"].get(grant["grant_id"])
            if existing and existing != grant:
                raise SpendDenied("Grant IDs are immutable; use a newly signed grant")
            if not existing:
                self._append(connection, state, "GRANT_CREATED", envelope)
            return json.loads(_json(grant))

    def apply_authority(self, envelope: dict) -> None:
        command = self._verified(envelope, "AUTHORITY_COMMAND")
        with self._transaction() as (connection, state):
            previous = state["commands"].get(command["command_id"])
            if previous and previous != command:
                raise SpendDenied("Authority command ID changed")
            if not previous:
                if command["action"] == "OVERRIDE_STOP":
                    job_id, grant_id = command["target"], command["new_grant_id"]
                    grant = state["grants"].get(grant_id)
                    if (
                        job_id not in state["stopped"]
                        or job_id in state["closed"]
                        or not grant
                        or grant["job_id"] != job_id
                        or grant_id in state["revoked"]
                        or self._clock() >= _time(grant["valid_until"])
                        or state["grant_sequence"][grant_id] <= state["stop_sequence"][job_id]
                    ):
                        raise SpendDenied(
                            "Override needs a new valid same-job grant after the stop; closure/revocation remain effective"
                        )
                self._append(connection, state, "AUTHORITY_COMMAND", envelope)

    def _active(self, state: dict, grant_id: str, job_id: str) -> dict:
        grant = state["grants"].get(grant_id)
        if not grant or grant["job_id"] != job_id:
            raise SpendDenied("No authority for this job")
        if (
            grant_id in state["revoked"]
            or job_id in state["closed"]
            or (job_id in state["stopped"] and state["override_grants"].get(job_id) != grant_id)
        ):
            raise SpendDenied("PAID_STOP: revoked, closed or stopped")
        if self._clock() >= _time(grant["valid_until"]):
            raise SpendDenied("Spend grant expired")
        return grant

    @staticmethod
    def _held(operation: dict) -> dict:
        return (
            operation["actual"]
            if operation["billing_state"] == "FINALIZED"
            else operation["maximum"]
        )

    def _within(self, operations: list[dict], additional: dict, limits: dict) -> bool:
        with localcontext() as context:
            context.prec = 80
            return all(
                sum((Decimal(self._held(op).get(unit, "0")) for op in operations), Decimal(0))
                + Decimal(additional.get(unit, "0"))
                <= Decimal(cap)
                for unit, cap in limits.items()
            )

    def reserve(
        self,
        operation_id: str,
        *,
        grant_id: str,
        job_id: str,
        provider: str,
        purpose: str,
        direction: str,
        stage: str,
        maximum: Mapping,
        reason: str,
        contract_digest: str,
        metadata: dict | None = None,
        parent_operation_id: str | None = None,
        validate_history: Callable[[list[dict]], None] | None = None,
    ) -> dict:
        """Atomically reserve an explicit upper bound and persist idempotency before submit."""
        strings = (
            operation_id,
            grant_id,
            job_id,
            provider,
            purpose,
            direction,
            stage,
            reason,
            contract_digest,
        )
        if not all(isinstance(value, str) and value.strip() for value in strings):
            raise SpendDenied("Operation scope, reason and immutable contract required")
        maximum = _usage(maximum, self.supported_units)
        if not any(Decimal(value) > 0 for value in maximum.values()):
            raise SpendDenied("Paid reservation must declare nonzero bounded usage")
        plan = dict(
            operation_id=operation_id,
            grant_id=grant_id,
            job_id=job_id,
            provider=provider,
            purpose=purpose,
            direction=direction,
            stage=stage,
            maximum=maximum,
            reason=reason,
            contract_digest=contract_digest,
            metadata=json.loads(_json(metadata or {})),
            parent_operation_id=parent_operation_id,
        )
        digest = hashlib.sha256(_json(plan).encode()).hexdigest()
        with self._transaction() as (connection, state):
            previous = state["operations"].get(operation_id)
            if previous:
                if previous["request_digest"] != digest:
                    raise SpendDenied("Operation identity reused with different immutable inputs")
                return json.loads(_json(previous))
            grant = self._active(state, grant_id, job_id)
            if provider not in grant["providers"] or purpose not in grant["purposes"]:
                raise SpendDenied("Provider/purpose outside grant")
            if set(maximum) != set(grant["limits"]):
                raise SpendDenied(
                    "COST_UNKNOWN: every granted resource dimension needs an explicit bound"
                )
            history = [op for op in state["operations"].values() if op["job_id"] == job_id]
            for prior in history:
                evaluation_parent = (
                    parent_operation_id == prior["operation_id"]
                    and plan["metadata"].get("kind") == "EVALUATION"
                    and prior["grant_id"] == grant_id
                    and prior["state"] == "COMPLETED"
                    and prior["billing_state"] == "FINALIZED"
                )
                if (
                    prior["state"] not in TERMINAL
                    or prior["billing_state"] != "FINALIZED"
                    or (prior["review"] is None and not evaluation_parent)
                ):
                    raise SpendDenied(
                        "Unresolved operation: recovery, billing reconciliation and review required"
                    )
            if parent_operation_id and not any(
                op["operation_id"] == parent_operation_id and op["grant_id"] == grant_id
                for op in history
            ):
                raise SpendDenied("Nested paid operation requires same-job/grant parent")
            charged = [op for op in history if op["grant_id"] == grant_id]
            if not self._within(charged, maximum, grant["limits"]) or not self._within(
                [], maximum, grant["max_single_call"]
            ):
                raise SpendDenied("Budget/per-call ceiling exceeded")
            for key, value, field_name in (
                ("direction_limits", direction, "direction"),
                ("stage_limits", stage, "stage"),
            ):
                caps = grant[key]
                if caps and (
                    value not in caps
                    or not self._within(
                        [op for op in charged if op[field_name] == value], maximum, caps[value]
                    )
                ):
                    raise SpendDenied("Direction/stage budget ceiling exceeded")
            if validate_history:
                validate_history(json.loads(_json(history)))
            operation = {
                **plan,
                "request_digest": digest,
                "idempotency_key": operation_id,
                "state": "RESERVED",
                "billing_state": "RESERVED",
                "provider_operation_id": None,
                "actual": None,
                "billing_reference": None,
                "review": None,
            }
            self._append(connection, state, "BUDGET_RESERVED", operation)
            return json.loads(_json(operation))

    def mark_submitted(self, operation_id: str, provider_operation_id: str | None = None) -> dict:
        """Commit SUBMITTED before external invocation. Repeat invocation is denied."""
        if provider_operation_id is not None and (
            not isinstance(provider_operation_id, str) or not provider_operation_id.strip()
        ):
            raise LedgerError("Provider operation ID must be nonempty when known")
        with self._transaction() as (connection, state):
            operation = state["operations"][operation_id]
            self._active(state, operation["grant_id"], operation["job_id"])
            if operation["state"] != "RESERVED":
                raise SpendDenied(
                    "Operation already submitted: recover using stable idempotency key"
                )
            updates = {
                "state": "SUBMITTED",
                "billing_state": "PENDING_ACTUAL",
                "provider_operation_id": provider_operation_id,
            }
            self._append(
                connection,
                state,
                "OPERATION_UPDATED",
                {"operation_id": operation_id, "updates": updates},
            )
            return json.loads(_json(state["operations"][operation_id]))

    def record_outcome(
        self,
        operation_id: str,
        outcome: str,
        *,
        provider_operation_id: str | None = None,
        provider_state: str = "",
        evidence: dict | None = None,
    ) -> dict:
        """Failure/cancellation remains billable until authoritative reconciliation."""
        if provider_operation_id is not None and (
            not isinstance(provider_operation_id, str) or not provider_operation_id.strip()
        ):
            raise LedgerError("Provider operation ID must be nonempty when known")
        if outcome not in TERMINAL | {"PROVIDER_RUNNING", "RECONCILIATION_REQUIRED"}:
            raise LedgerError("Unsupported provider outcome")
        with self._transaction() as (connection, state):
            operation = state["operations"][operation_id]
            if operation["state"] == "RESERVED" or operation["state"] in TERMINAL:
                raise LedgerError("Submitted operation required; terminal outcomes are immutable")
            if (
                operation["provider_operation_id"] is not None
                and provider_operation_id is not None
                and operation["provider_operation_id"] != provider_operation_id
            ):
                raise LedgerError("Provider operation identity is immutable once known")
            updates = {
                "state": outcome,
                "billing_state": "PENDING_ACTUAL",
                "provider_operation_id": provider_operation_id
                or operation["provider_operation_id"],
                "provider_state": provider_state,
                "outcome_at": self._clock().isoformat(),
                "outcome_evidence": json.loads(_json(evidence or {})),
            }
            self._append(
                connection,
                state,
                "OPERATION_UPDATED",
                {"operation_id": operation_id, "updates": updates},
            )
            return json.loads(_json(state["operations"][operation_id]))

    def reconcile(self, operation_id: str, actual: Mapping, billing_reference: str) -> dict:
        """Record all known charges, including overages; never silently raise a ceiling."""
        actual = _usage(actual, self.supported_units)
        if not isinstance(billing_reference, str) or not billing_reference.strip():
            raise LedgerError("Authoritative billing evidence reference required")
        with self._transaction() as (connection, state):
            operation = state["operations"][operation_id]
            if operation["state"] not in TERMINAL or set(actual) != set(operation["maximum"]):
                raise LedgerError(
                    "Terminal outcome and complete actual usage required; unknown costs remain held"
                )
            if operation["billing_state"] == "FINALIZED":
                if (
                    operation["actual"] != actual
                    or operation["billing_reference"] != billing_reference
                ):
                    raise LedgerError("Final charges are immutable")
                return json.loads(_json(operation))
            self._append(
                connection,
                state,
                "OPERATION_UPDATED",
                {
                    "operation_id": operation_id,
                    "updates": {
                        "actual": actual,
                        "billing_reference": billing_reference,
                        "billing_state": "FINALIZED",
                    },
                },
            )
            grant = state["grants"][operation["grant_id"]]
            charged = [
                op for op in state["operations"].values() if op["grant_id"] == operation["grant_id"]
            ]
            over = not self._within(charged, {}, grant["limits"]) or not self._within(
                [], actual, grant["max_single_call"]
            )
            # Any breached maximum undermines the pricing bound: pause even below total ceiling.
            over = over or any(
                Decimal(value) > Decimal(operation["maximum"][unit])
                for unit, value in actual.items()
            )
            if over:
                self._append(
                    connection,
                    state,
                    "PAID_STOP",
                    {
                        "job_id": operation["job_id"],
                        "reason": "Actual charges exceeded the reserved or authorized bound",
                    },
                )
            return json.loads(_json(state["operations"][operation_id]))

    def record_review(
        self,
        operation_id: str,
        review: dict,
        *,
        stop_reason: str | None = None,
        goal_satisfied: bool = False,
    ) -> None:
        """Atomically persist review and its economic stop; never expose a continuation gap.

        The trusted governor computes the decision. Replaying an identical review
        may ensure its stop is present, but cannot replace the original review.
        """
        if not isinstance(review, dict) or not review:
            raise LedgerError("Nonempty attributed review required")
        if stop_reason is not None and (
            not isinstance(stop_reason, str) or not stop_reason.strip()
        ):
            raise LedgerError("A requested review stop needs a nonempty reason")
        if goal_satisfied and stop_reason is None:
            raise LedgerError("Goal completion requires an economic stop reason")
        review = json.loads(_json(review))
        with self._transaction() as (connection, state):
            operation = state["operations"][operation_id]
            if operation["state"] not in TERMINAL:
                raise LedgerError("Cannot review an unresolved operation")
            if operation["review"] is not None:
                if operation["review"] != review:
                    raise LedgerError("Review is immutable")
            else:
                self._append(
                    connection,
                    state,
                    "OPERATION_UPDATED",
                    {"operation_id": operation_id, "updates": {"review": review}},
                )
            if stop_reason is not None and state["stopped"].get(operation["job_id"]) != stop_reason:
                self._append(
                    connection,
                    state,
                    "GOAL_SATISFIED" if goal_satisfied else "PAID_STOP",
                    {"job_id": operation["job_id"], "reason": stop_reason},
                )

    def release_unsubmitted(self, operation_id: str, reason: str) -> None:
        """Only RESERVED work can be proven never submitted and safely released."""
        if not reason.strip():
            raise LedgerError("Release requires reason")
        with self._transaction() as (connection, state):
            operation = state["operations"][operation_id]
            if operation["state"] != "RESERVED":
                raise SpendDenied("Submitted cancellation cannot imply zero cost")
            self._append(
                connection,
                state,
                "OPERATION_UPDATED",
                {
                    "operation_id": operation_id,
                    "updates": {
                        "state": "CANCELED",
                        "billing_state": "FINALIZED",
                        "actual": dict.fromkeys(operation["maximum"], "0"),
                        "billing_reference": "LOCAL_NOT_SUBMITTED",
                        "review": {"status": "CANCELED_BEFORE_SUBMISSION", "reason": reason},
                    },
                },
            )

    def stop(self, job_id: str, reason: str, *, goal_satisfied: bool = False) -> None:
        if not job_id.strip() or not reason.strip():
            raise LedgerError("Stop requires job and reason")
        with self._transaction() as (connection, state):
            self._append(
                connection,
                state,
                "GOAL_SATISFIED" if goal_satisfied else "PAID_STOP",
                {"job_id": job_id, "reason": reason},
            )

    def operations(self, job_id: str) -> list[dict]:
        with self._transaction() as (_, state):
            return [op for op in state["operations"].values() if op["job_id"] == job_id]

    def operation(self, operation_id: str) -> dict:
        with self._transaction() as (_, state):
            return state["operations"][operation_id]

    def recovery_required(self, job_id: str) -> list[dict]:
        return [
            op
            for op in self.operations(job_id)
            if op["state"] in {"SUBMITTED", "PROVIDER_RUNNING", "RECONCILIATION_REQUIRED"}
        ]

    def checkpoint(self) -> dict:
        with self._transaction() as (connection, _):
            return dict(
                connection.execute("SELECT sequence, hash FROM ledger_head WHERE id=1").fetchone()
            )

    def events(self) -> list[dict]:
        with self._transaction() as (connection, _):
            return [
                {**dict(row), "payload": json.loads(row["payload"])}
                for row in connection.execute("SELECT * FROM economic_events ORDER BY sequence")
            ]

    def report(self, grant_id: str) -> dict:
        with self._transaction() as (_, state):
            grant = state["grants"][grant_id]
            operations = [op for op in state["operations"].values() if op["grant_id"] == grant_id]
            consumed, held, available, unused = {}, {}, {}, {}
            with localcontext() as context:
                context.prec = 80
                for unit, cap in grant["limits"].items():
                    consumed[unit] = sum(
                        (
                            Decimal(op["actual"][unit])
                            for op in operations
                            if op["billing_state"] == "FINALIZED"
                        ),
                        Decimal(0),
                    )
                    held[unit] = sum(
                        (
                            Decimal(op["maximum"][unit])
                            for op in operations
                            if op["billing_state"] != "FINALIZED"
                        ),
                        Decimal(0),
                    )
                    unused[unit] = Decimal(cap) - consumed[unit]
                    available[unit] = unused[unit] - held[unit]
            return {
                "grant": grant,
                "authorized": {u: Decimal(v) for u, v in grant["limits"].items()},
                "consumed": consumed,
                "held": held,
                "available": available,
                "unspent_authorization": unused,
                "stop_reason": state["stopped"].get(grant["job_id"]),
                "override_grant_id": state["override_grants"].get(grant["job_id"]),
                "revoked": grant_id in state["revoked"],
                "closed": grant["job_id"] in state["closed"],
                "operations": operations,
            }
