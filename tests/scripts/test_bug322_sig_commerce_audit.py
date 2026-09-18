"""Tests for scripts/bug322_sig_commerce_audit.py — git and HTTP fully faked.

Covers binding extraction (sha256 vs expected_sha256 keys, ledger strings),
sha256-verified matching against a synthetic branch tree, status assignment,
the gated delegation request shape, and the CLI modes.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path

import httpx
import pytest

from integrations.openai_agents_api import AccessProbe, AgentsApiClient
from scripts import bug322_sig_commerce_audit as audit

PREFIX = audit.STALE_PREFIX
GOOD = b"good-bytes"
GOOD_SHA = hashlib.sha256(GOOD).hexdigest()
BAD = b"bad-bytes"
BRANCH = "codex/fake-recovery"


def _stale(rel: str) -> str:
    return PREFIX + rel


def _write_contracts(root: Path) -> Path:
    contracts = root / "scene-contracts"
    contracts.mkdir()
    sig1 = {
        "schema": "skyyrose.scene-ooda/1",
        "source_bindings": [
            {"role": "unrelated", "path": "/elsewhere/keep.png", "sha256": "ff"},
            {
                "path": _stale("renders/scroll-world/SIG-COMMERCE-1/protected-input/look.png"),
                "sha256": GOOD_SHA,
            },
        ],
        "forbidden_inputs": [
            {
                "path": _stale("renders/scroll-world/SIG-COMMERCE-1/rejected/bad.png"),
                "sha256": GOOD_SHA,
            }
        ],
    }
    sig3 = {
        "schema": "skyyrose.scene-ooda/1",
        "source_bindings": [
            {
                "path": _stale("renders/scroll-world/SIG-COMMERCE-3/src/target.webp"),
                "sha256": GOOD_SHA,
            }
        ],
        "authority_dependencies": [
            {
                "path": _stale("renders/scroll-world/SIG-COMMERCE-3/correction-v5/receipt.json"),
                "expected_sha256": GOOD_SHA,
            },
            {
                "path": _stale("renders/scroll-world/SIG-COMMERCE-3/correction-v5/local.png"),
                "expected_sha256": GOOD_SHA,
            },
        ],
    }
    ledger = {
        "entries": [
            {
                "id": "SIG-COMMERCE-3-OODA-1",
                "evidence": [
                    _stale("renders/scroll-world/SIG-COMMERCE-3/correction-v5/receipt.json")
                ],
            }
        ]
    }
    (contracts / "sig-commerce-1-higgsfield-comfy-ooda.json").write_text(json.dumps(sig1))
    (contracts / "sig-commerce-3-higgsfield-comfy-ooda.json").write_text(json.dumps(sig3))
    (contracts / "br-commerce-2-higgsfield-comfy-ooda.json").write_text(json.dumps(sig1))
    (contracts / audit.LEDGER_NAME).write_text(json.dumps(ledger))
    return contracts


def _oid(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


class FakeGit:
    """Replays a synthetic branch tree plus an object store for the --deep scan.

    ``blobs`` = files on the recovery branch; ``elsewhere`` = extra blobs that
    exist only in the wider object store, keyed by their historical path.
    """

    def __init__(
        self,
        blobs: dict[str, bytes],
        exists: bool = True,
        elsewhere: dict[str, bytes] | None = None,
    ) -> None:
        self.blobs = blobs
        self.exists = exists
        self.elsewhere = elsewhere or {}
        self.calls: list[list[str]] = []

    def _store(self) -> dict[str, bytes]:
        return {_oid(d): d for d in [*self.blobs.values(), *self.elsewhere.values()]}

    def __call__(self, args: Sequence[str], stdin: bytes | None = None) -> bytes:
        args = list(args)
        self.calls.append(args)
        if args[0] == "rev-parse" and "--verify" in args:
            if not self.exists:
                raise subprocess.CalledProcessError(1, ["git", *args])
            return b"deadbeef\n"
        if args[0] == "rev-parse":
            return b"deadbeefcafe0000\n"
        if args[0] == "ls-tree":
            return "\0".join(self.blobs).encode("utf-8") + b"\0"
        if args[0] == "cat-file" and "--batch-all-objects" in args:
            return "".join(f"{o} blob {len(d)}\n" for o, d in self._store().items()).encode()
        if args[0] == "cat-file" and args[1] == "--batch":
            assert stdin is not None
            store = self._store()
            out = b""
            for oid in stdin.decode().split():
                out += f"{oid} blob {len(store[oid])}\n".encode() + store[oid] + b"\n"
            return out
        if args[0] == "cat-file":
            _, path = args[2].split(":", 1)
            return self.blobs[path]
        if args[0] == "rev-list":
            lines = [f"{_oid(d)} {p}" for p, d in [*self.blobs.items(), *self.elsewhere.items()]]
            return ("\n".join(lines) + "\n").encode()
        if args[0] == "log":
            return b"c0ffee00 2026-09-01 feat(v2): checkpoint\n"
        if args[0] == "for-each-ref":
            return b"codex/v2-approved-product-cards\n"
        raise AssertionError(f"unexpected git call {args}")


@pytest.fixture
def workspace(tmp_path: Path) -> tuple[Path, Path, FakeGit]:
    contracts = _write_contracts(tmp_path)
    project_root = tmp_path / "project"
    (project_root / "renders/scroll-world/SIG-COMMERCE-3/correction-v5").mkdir(parents=True)
    (project_root / "renders/scroll-world/SIG-COMMERCE-3/correction-v5/local.png").write_bytes(GOOD)
    git = FakeGit(
        {
            "renders/scroll-world/SIG-COMMERCE-1/protected-input/look.png": GOOD,
            "renders/scroll-world/other/rejected/bad.png": BAD,
            "renders/scroll-world/SIG-COMMERCE-3/correction-v5/receipt.json": GOOD,
            "unrelated/file.txt": b"x",
        }
    )
    return contracts, project_root, git


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def test_extract_bindings_reads_sha256_and_expected_sha256_from_sig_contracts_only(
    workspace: tuple[Path, Path, FakeGit],
) -> None:
    contracts, _, _ = workspace
    bindings = audit.extract_bindings(contracts)
    assert [b.json_path for b in bindings] == [
        "source_bindings.1",
        "forbidden_inputs.0",
        "source_bindings.0",
        "authority_dependencies.0",
        "authority_dependencies.1",
    ]
    assert all(b.expected_sha256 == GOOD_SHA for b in bindings)
    assert {b.contract for b in bindings} == {
        "sig-commerce-1-higgsfield-comfy-ooda.json",
        "sig-commerce-3-higgsfield-comfy-ooda.json",
    }
    assert (
        bindings[0].relative_target
        == "renders/scroll-world/SIG-COMMERCE-1/protected-input/look.png"
    )
    assert bindings[0].collection == "SIG-COMMERCE-1"
    assert bindings[0].basename == "look.png"


def test_extract_ledger_references_finds_bare_strings(
    workspace: tuple[Path, Path, FakeGit],
) -> None:
    contracts, _, _ = workspace
    refs = audit.extract_ledger_references(contracts / audit.LEDGER_NAME)
    assert len(refs) == 1
    assert refs[0].json_path == "entries.0.evidence.0"
    assert refs[0].expected_sha256 is None
    assert audit.extract_ledger_references(contracts / "nope.json") == []


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def test_run_local_audit_assigns_statuses_by_sha256_evidence(
    workspace: tuple[Path, Path, FakeGit],
) -> None:
    contracts, project_root, git = workspace
    report = audit.run_local_audit(
        contracts_dir=contracts, project_root=project_root, branch=BRANCH, git=git
    )
    by_path = {r["json_path"] + "@" + r["contract"][:14]: r for r in report["contract_bindings"]}
    look = by_path["source_bindings.1@sig-commerce-1"]
    assert look["status"] == audit.STATUS_RECOVERABLE
    assert (
        look["branch_match_path"] == "renders/scroll-world/SIG-COMMERCE-1/protected-input/look.png"
    )
    assert look["proposed_path"] == look["relative_target"]

    bad = by_path["forbidden_inputs.0@sig-commerce-1"]
    assert bad["status"] == audit.STATUS_HASH_MISMATCH
    assert bad["branch_candidates"] == [
        {
            "path": "renders/scroll-world/other/rejected/bad.png",
            "sha256": hashlib.sha256(BAD).hexdigest(),
            "match": False,
        }
    ]
    assert bad["proposed_path"] is None

    assert by_path["source_bindings.0@sig-commerce-3"]["status"] == audit.STATUS_MISSING

    receipt = by_path["authority_dependencies.0@sig-commerce-3"]
    assert receipt["status"] == audit.STATUS_RECOVERABLE

    local = by_path["authority_dependencies.1@sig-commerce-3"]
    assert local["status"] == audit.STATUS_ALREADY_LOCAL
    assert local["worktree"]["match"] is True
    assert local["branch_candidates"] == []

    assert report["summary"] == {
        "total_bindings": 5,
        "by_status": {"ALREADY_LOCAL": 1, "HASH_MISMATCH": 1, "MISSING": 1, "RECOVERABLE": 2},
        "by_collection": {
            "SIG-COMMERCE-1": {"HASH_MISMATCH": 1, "RECOVERABLE": 1},
            "SIG-COMMERCE-3": {"ALREADY_LOCAL": 1, "MISSING": 1, "RECOVERABLE": 1},
        },
    }
    assert report["ledger_references"][0]["status"] == audit.STATUS_RECOVERABLE
    assert report["recovery_branch"] == BRANCH
    assert report["recovery_branch_head"] == "deadbeefcafe0000"


def test_hash_compare_is_case_insensitive_and_existence_only_without_sha() -> None:
    assert audit._matches("ABC", "abc") is True
    assert audit._matches(None, "anything") is True
    assert audit._matches("abc", "abd") is False


def test_deep_scan_rescues_bindings_from_anywhere_in_the_object_store(
    workspace: tuple[Path, Path, FakeGit],
) -> None:
    contracts, project_root, _ = workspace
    git = FakeGit(
        {"renders/scroll-world/other/rejected/bad.png": BAD, "unrelated/file.txt": b"x"},
        elsewhere={"wordpress-theme/flagship-2/assets/plates/renamed-plate-v3.png": GOOD},
    )
    shallow = audit.run_local_audit(
        contracts_dir=contracts, project_root=project_root, branch=BRANCH, git=git
    )
    assert shallow["deep_object_store_scan"] is False
    assert shallow["summary"]["by_status"] == {"ALREADY_LOCAL": 1, "HASH_MISMATCH": 1, "MISSING": 3}

    deep = audit.run_local_audit(
        contracts_dir=contracts, project_root=project_root, branch=BRANCH, git=git, deep=True
    )
    assert deep["deep_object_store_scan"] is True
    assert deep["summary"]["by_status"] == {"ALREADY_LOCAL": 1, "RECOVERABLE_ELSEWHERE": 4}
    rescued = [r for r in deep["contract_bindings"] if r["status"] == "RECOVERABLE_ELSEWHERE"]
    match = rescued[0]["object_store_match"]
    assert match["blob"] == _oid(GOOD)
    assert match["size"] == len(GOOD)
    assert match["paths"] == ["wordpress-theme/flagship-2/assets/plates/renamed-plate-v3.png"]
    assert match["commits"] == ["c0ffee00 2026-09-01 feat(v2): checkpoint"]
    assert match["refs"] == ["codex/v2-approved-product-cards"]
    assert rescued[0]["proposed_path"] == rescued[0]["relative_target"]
    assert [c[0] for c in git.calls].count("log") == 1  # one provenance lookup per distinct sha


def test_deep_scan_leaves_truly_absent_bytes_missing() -> None:
    binding = audit.Binding("c.json", "source_bindings.0", PREFIX + "renders/x/a.png", "ab" * 32)
    result = audit.BindingResult(binding, audit.STATUS_MISSING, (), None, None)
    git = FakeGit({"renders/x/other.png": BAD})
    (kept,) = audit.deep_rescue([result], git)
    assert kept.status == audit.STATUS_MISSING
    assert kept.object_store is None
    assert not any(c[0] in ("rev-list", "log") for c in git.calls)


def test_chunks_by_size_respects_cap_and_never_drops_oids() -> None:
    blobs = [("a", 60), ("b", 50), ("c", 10), ("d", 200)]
    assert audit._chunks_by_size(blobs, 100) == [["a"], ["b", "c"], ["d"]]


def test_sha256_batch_parses_cat_file_batch_output() -> None:
    git = FakeGit({"one.png": GOOD, "two.png": BAD})
    digests = audit._sha256_batch(git, [_oid(GOOD), _oid(BAD)])
    assert digests == {_oid(GOOD): GOOD_SHA, _oid(BAD): hashlib.sha256(BAD).hexdigest()}


def test_run_local_audit_fails_closed_without_recovery_branch(
    workspace: tuple[Path, Path, FakeGit],
) -> None:
    contracts, project_root, _ = workspace
    git = FakeGit({}, exists=False)
    with pytest.raises(RuntimeError, match="recovery branch 'codex/fake-recovery' not found"):
        audit.run_local_audit(
            contracts_dir=contracts, project_root=project_root, branch=BRANCH, git=git
        )
    assert all(call[0] == "rev-parse" for call in git.calls)


# ---------------------------------------------------------------------------
# Delegation request (built, never fired)
# ---------------------------------------------------------------------------


def test_build_session_request_targets_three_parallel_subagents_over_text_only() -> None:
    request = audit.build_session_request({"summary": {"total_bindings": 21}})
    payload = request.to_payload()
    assert audit.AGENT_MODEL == "gpt-6-astra"
    assert payload["agent"]["model"] == audit.AGENT_MODEL
    assert payload["agent"]["multi_agent"] == {"enabled": True, "max_concurrent_subagents": 3}
    assert payload["environment"] == {"type": "none"}
    assert payload["stream"] is True
    assert json.loads(payload["input"]) == {"summary": {"total_bindings": 21}}
    instructions = payload["agent"]["instructions"]
    for collection in audit.COLLECTIONS:
        assert collection in instructions
    assert "one subagent per collection" in instructions
    assert "never propose edits to another collection's contract file" in instructions


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_args(workspace: tuple[Path, Path, FakeGit], *extra: str) -> list[str]:
    contracts, project_root, _ = workspace
    return [
        "--contracts-dir",
        str(contracts),
        "--project-root",
        str(project_root),
        "--branch",
        BRANCH,
        *extra,
    ]


def test_cli_local_only_prints_summary_writes_report_and_makes_no_http(
    workspace: tuple[Path, Path, FakeGit], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, git = workspace
    out = tmp_path / "out" / "report.json"

    def no_client() -> AgentsApiClient:
        raise AssertionError("local-only must never construct an HTTP client")

    rc = audit.main(
        _cli_args(workspace, "--local-only", "--out", str(out)), git=git, client_factory=no_client
    )
    assert rc == 0
    printed = capsys.readouterr().out
    assert "LOCAL ONLY — no OpenAI calls made." in printed
    assert "SIG-COMMERCE-1" in printed and "HASH_MISMATCH" in printed
    assert json.loads(out.read_text())["summary"]["total_bindings"] == 5


def test_cli_local_only_missing_branch_exits_one(
    workspace: tuple[Path, Path, FakeGit], capsys: pytest.CaptureFixture[str]
) -> None:
    rc = audit.main(_cli_args(workspace, "--local-only"), git=FakeGit({}, exists=False))
    assert rc == 1
    assert "not found" in capsys.readouterr().out


def _client_with(responses: list[httpx.Response]) -> AgentsApiClient:
    queue = list(responses)
    return AgentsApiClient(
        api_key="sk-test", transport=httpx.MockTransport(lambda _req: queue.pop(0))
    )


def test_cli_check_access_reports_probe(capsys: pytest.CaptureFixture[str]) -> None:
    rc = audit.main(
        ["--check-access"],
        client_factory=lambda: _client_with([httpx.Response(200, json={"data": []})]),
    )
    assert rc == 0
    assert "Agents API access: OK (HTTP 200)" in capsys.readouterr().out
    rc = audit.main(
        ["--check-access"],
        client_factory=lambda: _client_with([httpx.Response(403, json={"error": "scope"})]),
    )
    assert rc == 3


def test_cli_fire_aborts_when_model_is_unavailable_and_never_posts(
    workspace: tuple[Path, Path, FakeGit], capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, git = workspace
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.endswith("/agents/sessions"):
            return httpx.Response(200, json={"data": []})
        return httpx.Response(404, json={"error": {"message": "That model does not exist"}})

    rc = audit.main(
        _cli_args(workspace, "--fire", "--yes"),
        git=git,
        client_factory=lambda: AgentsApiClient(api_key="k", transport=httpx.MockTransport(handler)),
    )
    assert rc == 3
    out = capsys.readouterr().out
    assert "ABORT: model 'gpt-6-astra' is not available" in out
    assert "--model <id>" in out
    assert all(r.method == "GET" for r in seen)


def test_cli_fire_declined_at_prompt_never_posts(
    workspace: tuple[Path, Path, FakeGit], capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, git = workspace
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"id": "ok"})

    rc = audit.main(
        _cli_args(workspace, "--fire"),
        git=git,
        client_factory=lambda: AgentsApiClient(api_key="k", transport=httpx.MockTransport(handler)),
        prompt_fn=lambda _prompt: "n",
        is_tty=lambda: True,
    )
    assert rc == 2
    out = capsys.readouterr().out
    assert "STOP — Confirm before proceeding" in out
    assert "Not confirmed. No session created." in out
    assert [r.method for r in seen] == ["GET", "GET"]


def test_cli_fire_confirmed_streams_turn_and_deletes_session(
    workspace: tuple[Path, Path, FakeGit], capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, git = workspace
    seen: list[httpx.Request] = []
    sse = (
        b'event: agent.session.created\ndata: {"session": {"id": "sess_x"}}\n\n'
        b'event: agent.session.turn.completed\ndata: {"output_text": "consolidated patch"}\n\n'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.method == "POST":
            return httpx.Response(200, content=sse)
        return httpx.Response(200, json={"deleted": True} if request.method == "DELETE" else {})

    rc = audit.main(
        _cli_args(workspace, "--fire"),
        git=git,
        client_factory=lambda: AgentsApiClient(api_key="k", transport=httpx.MockTransport(handler)),
        prompt_fn=lambda _prompt: "y",
        is_tty=lambda: True,
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Turn state : completed" in out
    assert "consolidated patch" in out
    assert "Deleted session sess_x" in out
    assert [r.method for r in seen] == ["GET", "GET", "POST", "DELETE"]
    posted = json.loads(seen[2].content)
    assert posted["agent"]["multi_agent"]["max_concurrent_subagents"] == 3


def test_access_probe_dataclass_is_frozen() -> None:
    probe = AccessProbe(True, 200, "ok")
    with pytest.raises(AttributeError):
        probe.ok = False  # type: ignore[misc]


# --- money gate: fail-closed without a human (skyyrose/elite_studio/CLAUDE.md) -------------


def _ok_handler(seen: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"id": "ok", "data": []})

    return handler


def _fire(workspace, seen, *flags: str, **kw) -> int:
    _, _, git = workspace
    return audit.main(
        _cli_args(workspace, "--fire", *flags),
        git=git,
        client_factory=lambda: AgentsApiClient(
            api_key="k", transport=httpx.MockTransport(_ok_handler(seen))
        ),
        **kw,
    )


def test_yes_flag_without_a_tty_never_posts(
    workspace: tuple[Path, Path, FakeGit],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # An agent, cron job or CI step running `--fire --yes` used to spend money with no
    # human having seen the manifest. --yes is a convenience for a person at a terminal,
    # never a substitute for one.
    monkeypatch.delenv("SKYYROSE_AUTO_CONFIRM", raising=False)
    seen: list[httpx.Request] = []
    rc = _fire(workspace, seen, "--yes", is_tty=lambda: False)
    assert rc == 2
    out = capsys.readouterr().out
    assert "STOP — Confirm before proceeding" in out, "the manifest must print even when aborting"
    assert "non-interactive" in out and "SKYYROSE_AUTO_CONFIRM=1" in out
    assert "POST" not in [r.method for r in seen]


def test_no_tty_without_yes_aborts_cleanly_instead_of_crashing(
    workspace: tuple[Path, Path, FakeGit], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Previously fail-closed only by accident: input() raised an uncaught EOFError.
    monkeypatch.delenv("SKYYROSE_AUTO_CONFIRM", raising=False)
    seen: list[httpx.Request] = []

    def eof(_prompt: str) -> str:
        raise EOFError

    assert _fire(workspace, seen, is_tty=lambda: False, prompt_fn=eof) == 2
    assert _fire(workspace, seen, is_tty=lambda: True, prompt_fn=eof) == 2
    assert "POST" not in [r.method for r in seen]


def test_env_opt_in_is_the_only_non_interactive_path(
    workspace: tuple[Path, Path, FakeGit],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SKYYROSE_AUTO_CONFIRM", "1")
    seen: list[httpx.Request] = []
    _fire(workspace, seen, is_tty=lambda: False)
    assert "auto-confirmed via SKYYROSE_AUTO_CONFIRM=1" in capsys.readouterr().out
    assert "POST" in [r.method for r in seen]


@pytest.mark.parametrize("value", ["0", "true", "yes", ""])
def test_env_opt_in_requires_exactly_1(
    workspace: tuple[Path, Path, FakeGit], monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("SKYYROSE_AUTO_CONFIRM", value)
    seen: list[httpx.Request] = []
    assert _fire(workspace, seen, "--yes", is_tty=lambda: False) == 2
    assert "POST" not in [r.method for r in seen]


def test_yes_flag_at_a_real_terminal_still_works(
    workspace: tuple[Path, Path, FakeGit], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SKYYROSE_AUTO_CONFIRM", raising=False)
    seen: list[httpx.Request] = []
    _fire(workspace, seen, "--yes", is_tty=lambda: True)
    assert "POST" in [r.method for r in seen]


def test_production_default_tty_check_is_wired(
    workspace: tuple[Path, Path, FakeGit], monkeypatch: pytest.MonkeyPatch
) -> None:
    # No is_tty override: this exercises main()'s real default (sys.stdin.isatty). Under
    # pytest stdin is not a terminal — the same condition as an agent, cron or CI run.
    import sys

    monkeypatch.delenv("SKYYROSE_AUTO_CONFIRM", raising=False)
    assert not sys.stdin.isatty()
    seen: list[httpx.Request] = []
    assert _fire(workspace, seen, "--yes") == 2
    assert "POST" not in [r.method for r in seen]
