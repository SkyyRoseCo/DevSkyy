"""Unit tests on synthetic git repositories; no network and no real theme."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from cli_anything.skyyrose_flagship_2.core import candidate as cand_mod
from cli_anything.skyyrose_flagship_2.core import evidence as ev
from cli_anything.skyyrose_flagship_2.core import gates as gates_mod
from cli_anything.skyyrose_flagship_2.core import session as sess_mod
from cli_anything.skyyrose_flagship_2.core import version as ver_mod
from cli_anything.skyyrose_flagship_2.utils import backend
from cli_anything.skyyrose_flagship_2.utils.backend import ScriptResult, Toolchain

THEME = backend.THEME_REL
DEPS = "d" * 64  # a healthy install: the deps lockfile is present


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    theme = root / THEME
    theme.mkdir(parents=True)
    (theme / "package.json").write_text(
        json.dumps(
            {
                "version": "2.5.1",
                "scripts": {
                    "check:registry": "true",
                    "build:assets": "true",
                    "render:commerce-scenes": "true",
                    "certify:x": "true",
                    "brand-new-script": "true",
                    "verify": "true",
                },
            }
        )
    )
    (theme / "functions.php").write_text("<?php\ndefine( 'SKYYROSE2_VERSION', '2.5.1' );\n")
    (theme / "style.css").write_text("/*\nTheme Name: X\nVersion: 2.5.1\n*/\n")
    (theme / "readme.txt").write_text("=== X ===\nStable tag: 2.5.1\n")
    reg = root / backend.REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text('{"products": {}}\n')
    digest = backend.sha256_file(reg)
    inputs = root / backend.BUILD_INPUTS_REL
    inputs.parent.mkdir(parents=True)
    inputs.write_text(
        json.dumps(
            {
                "node": "22.23.2",
                "npm": "10.9.8",
                "python": "3.12.12",
                "current_registry_sha256": digest,
                "input_hashes": {backend.REGISTRY_REL: digest},
            }
        )
    )
    _git(root, "init", "-q", "-b", "main")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    return root


@pytest.fixture(autouse=True)
def _home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKYYROSE2_CLI_HOME", str(tmp_path / "clihome"))


def _toolchain(deps: str | None = DEPS) -> Toolchain:
    return Toolchain(
        path_env="/usr/bin",
        node="22.23.2",
        npm="10.9.8",
        python="3.12.12",
        php="8.5.6",
        pins={"node": "22.23.2", "npm": "10.9.8", "python": "3.12.12"},
        deps_sha256=deps,
    )


def _result(
    script: str = "check:registry", rc: int = 0, changed: list[str] | None = None
) -> ScriptResult:
    return ScriptResult(
        script=script,
        command=["npm", "run", script],
        cwd=THEME,
        returncode=rc,
        duration_s=0.1,
        started_at="2026-10-10T00:00:00+00:00",
        stdout="ok\n",
        stderr="",
        changed_paths=changed or [],
    )


def _entry(
    repo: Path,
    sess: sess_mod.Session,
    script: str = "check:registry",
    rc: int = 0,
    owner: str = "builder",
    owner_source: str = "git",
    toolchain: Toolchain | None = None,
):
    scripts = backend.load_package_scripts(repo)
    gate = gates_mod.classify(script, scripts)
    cand = cand_mod.capture(repo)
    result = _result(script, rc)
    header = ev.log_header(
        gate=gate, result=result, before=cand, after=cand, owner=owner, owner_source=owner_source
    )
    log = sess.write_log(script, sess_mod.format_log(header, "ok", ""))
    return ev.run_entry(
        gate=gate,
        result=result,
        before=cand,
        after=cand,
        toolchain=toolchain or _toolchain(),
        log_path=log,
        owner=owner,
        owner_source=owner_source,
    )


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------


class TestGates:
    def test_every_script_gets_exactly_one_class(self, repo: Path) -> None:
        scripts = backend.load_package_scripts(repo)
        kinds = {g.name: g.kind for g in gates_mod.classify_all(scripts)}
        assert kinds == {
            "check:registry": "check",
            "build:assets": "build",
            "render:commerce-scenes": "blocked",
            "certify:x": "blocked",
            "brand-new-script": "unclassified",
            "verify": "check",
        }

    def test_unclassified_is_refused(self, repo: Path) -> None:
        with pytest.raises(gates_mod.GateRefusedError, match="unclassified"):
            gates_mod.require_runnable(
                "brand-new-script", backend.load_package_scripts(repo), "check"
            )

    @pytest.mark.parametrize("name", ["render:commerce-scenes", "certify:x"])
    def test_blocked_is_refused(self, repo: Path, name: str) -> None:
        with pytest.raises(gates_mod.GateRefusedError, match="blocked"):
            gates_mod.require_runnable(name, backend.load_package_scripts(repo), "build")

    def test_build_cannot_run_as_check(self, repo: Path) -> None:
        with pytest.raises(gates_mod.GateRefusedError, match="build"):
            gates_mod.require_runnable("build:assets", backend.load_package_scripts(repo), "check")

    def test_missing_script_is_refused(self, repo: Path) -> None:
        with pytest.raises(gates_mod.GateRefusedError, match="missing"):
            gates_mod.require_runnable("check:nope", backend.load_package_scripts(repo), "check")

    def test_image_judge_scripts_are_blocked_even_with_check_prefix(self) -> None:
        gate = gates_mod.classify(
            "check:image-judge-availability", {"check:image-judge-availability": "x"}
        )
        assert gate.kind == "blocked"


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------


class TestVersion:
    def test_reads_triple(self, repo: Path) -> None:
        state = ver_mod.read_version(repo / THEME)
        assert state.consistent and state.current == "2.5.1" and state.package_json == "2.5.1"

    def test_detects_disagreement(self, repo: Path) -> None:
        (repo / THEME / "readme.txt").write_text("Stable tag: 2.5.0\n")
        state = ver_mod.read_version(repo / THEME)
        assert not state.consistent
        with pytest.raises(ver_mod.VersionError, match="disagree"):
            _ = state.current

    @pytest.mark.parametrize("bad", ["2.5", "v2.6.0", "2.5.1"])
    def test_rejects_bad_or_noop_version(self, repo: Path, bad: str) -> None:
        with pytest.raises(ver_mod.VersionError):
            ver_mod.plan_bump(repo / THEME, bad)

    def test_plan_writes_nothing(self, repo: Path) -> None:
        before = (repo / THEME / "style.css").read_bytes()
        plan = ver_mod.plan_bump(repo / THEME, "2.6.0")
        assert sorted(plan) == ["functions.php", "readme.txt", "style.css"]
        assert (repo / THEME / "style.css").read_bytes() == before

    def test_write_updates_all_three(self, repo: Path) -> None:
        state = ver_mod.write_version(repo / THEME, "2.6.0")
        assert state.sources == {
            "functions.php": "2.6.0",
            "style.css": "2.6.0",
            "readme.txt": "2.6.0",
        }
        assert (
            "define( 'SKYYROSE2_VERSION', '2.6.0' );"
            in (repo / THEME / "functions.php").read_text()
        )

    def test_failed_write_rolls_back(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        real = ver_mod._atomic_write
        calls = {"n": 0}

        def flaky(path: Path, content: str) -> None:
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full")
            real(path, content)

        monkeypatch.setattr(ver_mod, "_atomic_write", flaky)
        with pytest.raises(OSError):
            ver_mod.write_version(repo / THEME, "2.6.0")
        assert ver_mod.read_version(repo / THEME).current == "2.5.1"


# ---------------------------------------------------------------------------
# candidate
# ---------------------------------------------------------------------------


class TestCandidate:
    def test_clean_revision_is_head(self, repo: Path) -> None:
        cand = cand_mod.capture(repo)
        assert not cand.dirty and cand.revision == _git(repo, "rev-parse", "HEAD").strip()

    def test_edit_dirties_and_changes_id(self, repo: Path) -> None:
        clean = cand_mod.capture(repo)
        (repo / THEME / "style.css").write_text("changed\n")
        dirty = cand_mod.capture(repo)
        assert dirty.dirty and dirty.candidate_id != clean.candidate_id
        assert dirty.revision.startswith(clean.head + "+dirty.")

    def test_second_edit_to_dirty_file_changes_id(self, repo: Path) -> None:
        (repo / THEME / "style.css").write_text("one\n")
        first = cand_mod.capture(repo)
        (repo / THEME / "style.css").write_text("two\n")
        assert cand_mod.capture(repo).candidate_id != first.candidate_id

    def test_untracked_gate_input_dirties_and_changes_id(self, repo: Path) -> None:
        clean = cand_mod.capture(repo)
        (repo / THEME / "new-template.php").write_text("<?php\n")
        dirty = cand_mod.capture(repo)
        assert dirty.dirty and dirty.candidate_id != clean.candidate_id
        assert f"{THEME}/new-template.php" in dirty.dirty_paths

    def test_untracked_outside_gate_inputs_is_ignored(self, repo: Path) -> None:
        clean = cand_mod.capture(repo)
        (repo / "notes.txt").write_text("scratch\n")
        assert cand_mod.capture(repo).candidate_id == clean.candidate_id

    def test_commit_changes_id(self, repo: Path) -> None:
        before = cand_mod.capture(repo)
        (repo / THEME / "style.css").write_text("Version: 2.5.1\nx\n")
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "edit")
        after = cand_mod.capture(repo)
        assert not after.dirty and after.candidate_id != before.candidate_id

    def test_pin_status_detects_drift(self, repo: Path) -> None:
        assert cand_mod.pin_status(repo)["in_sync"] is True
        (repo / backend.REGISTRY_REL).write_text('{"products": {"x": {}}}\n')
        status = cand_mod.pin_status(repo)
        assert status["in_sync"] is False and "founder approval" in status["action"]


# ---------------------------------------------------------------------------
# session
# ---------------------------------------------------------------------------


class TestSession:
    def test_round_trip(self, repo: Path) -> None:
        sess = sess_mod.new_session(repo)
        sess.add_run({"gate_id": "check:registry"})
        sess.save()
        loaded = sess_mod.load_session(sess.session_id)
        assert loaded.runs == [{"gate_id": "check:registry"}]
        assert sess_mod.current_session_id() == sess.session_id

    def test_schema_mismatch_rejected(self, repo: Path) -> None:
        sess = sess_mod.new_session(repo)
        sess.save()
        data = json.loads(sess.path.read_text())
        data["schema"] = "other"
        sess.path.write_text(json.dumps(data))
        with pytest.raises(sess_mod.SessionError, match="schema"):
            sess_mod.load_session(sess.session_id)

    def test_resume_only_same_repo(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        sess.save()
        assert sess_mod.open_or_create(repo).session_id == sess.session_id
        assert sess_mod.open_or_create(tmp_path / "elsewhere").session_id != sess.session_id

    def test_logs_written_per_run(self, repo: Path) -> None:
        sess = sess_mod.new_session(repo)
        log = sess.write_log(
            "check:registry", sess_mod.format_log({"gate_id": "check:registry"}, "out", "err")
        )
        assert (
            log.is_file()
            and "out" in log.read_text()
            and log.name.startswith("0001-check_registry")
        )


# ---------------------------------------------------------------------------
# evidence
# ---------------------------------------------------------------------------


class TestEvidence:
    def test_owner_cannot_review_own_candidate(self, repo: Path) -> None:
        with pytest.raises(ev.EvidenceError, match="independent"):
            ev.review_entry(
                candidate=cand_mod.capture(repo),
                reviewer="Builder",
                disposition="PASS",
                note="n",
                owners={"builder"},
            )

    def test_check_that_mutates_fails(self, repo: Path) -> None:
        sess = sess_mod.new_session(repo)
        gate = gates_mod.classify("check:registry", backend.load_package_scripts(repo))
        cand = cand_mod.capture(repo)
        entry = ev.run_entry(
            gate=gate,
            result=_result(changed=[f"{THEME}/style.css"]),
            before=cand,
            after=cand,
            toolchain=_toolchain(),
            log_path=sess.write_log("check:registry", sess_mod.format_log({}, "", "")),
            owner="builder",
            owner_source="git",
        )
        assert entry["status"] == "FAIL" and "changed tracked files" in entry["status_reason"]

    def test_stale_runs_excluded(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        old = _entry(repo, sess)
        (repo / THEME / "style.css").write_text("Version: 2.5.1\nedit\n")
        cand = cand_mod.capture(repo)
        with pytest.raises(ev.EvidenceError, match="No gate runs recorded"):
            ev.build_record(
                session_runs=[old],
                reviews=[],
                candidate=cand,
                toolchain=_toolchain(),
                out_dir=tmp_path / "out",
            )

    def test_dirty_is_partial_and_failed_is_blocked(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        (repo / THEME / "style.css").write_text("Version: 2.5.1\nedit\n")
        cand = cand_mod.capture(repo)
        passing = _entry(repo, sess)
        rec = ev.build_record(
            session_runs=[passing],
            reviews=[],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "a",
        )
        assert rec["claim"] == "partial" and rec["fashion_theme_team"]["status"] == "BLOCKED"
        failing = _entry(repo, sess, rc=1)
        rec = ev.build_record(
            session_runs=[failing],
            reviews=[],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "b",
        )
        assert rec["claim"] == "blocked" and rec["fashion_theme_team"]["status"] == "FAIL"
        assert rec["findings"][0]["severity"] == "P1"

    def test_independent_review_passes_clean_candidate(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        run = _entry(repo, sess)
        review = ev.review_entry(
            candidate=cand,
            reviewer="reviewer",
            disposition="PASS",
            note="read logs",
            owners={"builder"},
        )
        rec = ev.build_record(
            session_runs=[run],
            reviews=[review],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "out",
        )
        assert rec["claim"] == "verified"
        assert rec["fashion_theme_team"]["status"] == "PASS"
        assert rec["fashion_theme_team"]["gates"][0]["reviewer"] == "reviewer"

    def test_tampered_log_refused(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        run = _entry(repo, sess)
        Path(run["artifact"]["path"]).write_text("tampered")
        with pytest.raises(ev.EvidenceError, match="changed since the run"):
            ev.build_record(
                session_runs=[run],
                reviews=[],
                candidate=cand_mod.capture(repo),
                toolchain=_toolchain(),
                out_dir=tmp_path / "out",
            )


def test_repo_discovery_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SKYYROSE2_REPO_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(backend.RepoNotFoundError, match="--repo-root"):
        backend.find_repo_root()


def test_verify_refuses_without_wp_fixture(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from cli_anything.skyyrose_flagship_2.skyyrose_flagship_2_cli import CliState, cli
    from click.testing import CliRunner

    monkeypatch.delenv("V2_WP_FIXTURE", raising=False)
    pins = repo / backend.FIXTURE_PINS_REL
    pins.parent.mkdir(parents=True, exist_ok=True)
    pins.write_text("{}")
    result = CliRunner().invoke(
        cli, ["--json", "--repo-root", str(repo), "check", "run", "verify"], obj=CliState()
    )
    assert result.exit_code == 1, (result.output, result.exception)
    assert "fixture prepare" in json.loads(result.output)["error"]


def test_fixture_dir_is_keyed_by_pin_manifest(repo: Path, tmp_path: Path) -> None:
    pins = repo / backend.FIXTURE_PINS_REL
    pins.parent.mkdir(parents=True, exist_ok=True)
    pins.write_text('{"a": 1}')
    first = backend.managed_fixture_dir(repo, tmp_path)
    pins.write_text('{"a": 2}')
    assert backend.managed_fixture_dir(repo, tmp_path) != first


def test_missing_fixture_manifest_is_a_clear_error(repo: Path, tmp_path: Path) -> None:
    with pytest.raises(backend.BackendError, match="manifest missing"):
        backend.managed_fixture_dir(repo, tmp_path)


# ---------------------------------------------------------------------------
# Regression tests for the independent Fashion Theme Team review (2026-10-10)
# ---------------------------------------------------------------------------


class TestReviewFindings:
    def test_env_owner_swap_cannot_launder_self_review(self, repo: Path, tmp_path: Path) -> None:
        """P1: independence is judged against owners recorded on runs, not the env at review time."""
        sess = sess_mod.new_session(repo)
        run = _entry(repo, sess, owner="builder")
        cand = cand_mod.capture(repo)
        owners = ev.run_owners([run], cand)
        with pytest.raises(ev.EvidenceError, match="independent"):
            ev.review_entry(
                candidate=cand, reviewer="builder", disposition="PASS", note="n", owners=owners
            )
        forged = {
            "candidate_id": cand.candidate_id,
            "revision": cand.revision,
            "reviewer": "builder",
            "disposition": "PASS",
            "note": "n",
            "reviewed_at": "2026-10-10T00:00:00+00:00",
            "harness_sha256": backend.harness_sha256(),
        }
        rec = ev.build_record(
            session_runs=[run],
            reviews=[forged],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        assert rec["fashion_theme_team"]["status"] == "BLOCKED"

    def test_review_without_runs_is_refused(self, repo: Path) -> None:
        with pytest.raises(ev.EvidenceError, match="No gate runs"):
            ev.review_entry(
                candidate=cand_mod.capture(repo),
                reviewer="r",
                disposition="PASS",
                note="n",
                owners=set(),
            )

    def test_flipped_ledger_status_is_caught(self, repo: Path, tmp_path: Path) -> None:
        """P2: a FAIL edited to PASS in session.json disagrees with its hashed log."""
        sess = sess_mod.new_session(repo)
        run = _entry(repo, sess, rc=1)
        assert run["status"] == "FAIL"
        forged = {**run, "status": "PASS", "status_reason": "exit 0"}
        with pytest.raises(ev.EvidenceError, match="disagrees with its log"):
            ev.build_record(
                session_runs=[forged],
                reviews=[],
                candidate=cand_mod.capture(repo),
                toolchain=_toolchain(),
                out_dir=tmp_path / "o",
            )

    def test_runs_from_other_harness_code_are_stale(self, repo: Path, tmp_path: Path) -> None:
        """P1 provenance: evidence binds to the exact harness source that produced it."""
        sess = sess_mod.new_session(repo)
        run = {**_entry(repo, sess), "harness_sha256": "0" * 64}
        with pytest.raises(ev.EvidenceError, match="harness"):
            ev.build_record(
                session_runs=[run],
                reviews=[],
                candidate=cand_mod.capture(repo),
                toolchain=_toolchain(),
                out_dir=tmp_path / "o",
            )

    def test_record_carries_harness_hash(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        rec = ev.build_record(
            session_runs=[_entry(repo, sess)],
            reviews=[],
            candidate=cand_mod.capture(repo),
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        assert rec["cli"]["harness_sha256"] == backend.harness_sha256()
        assert rec["target"]["environment"].endswith(
            ";harness=" + backend.harness_sha256()[:12] + ";deps=" + DEPS[:12]
        )

    def test_earlier_failure_is_reported(self, repo: Path, tmp_path: Path) -> None:
        """P3: a later PASS supersedes an earlier FAIL but the FAIL stays visible."""
        sess = sess_mod.new_session(repo)
        failed = _entry(repo, sess, rc=1)
        sess.add_run(failed)
        passed = _entry(repo, sess)
        rec = ev.build_record(
            session_runs=[failed, passed],
            reviews=[],
            candidate=cand_mod.capture(repo),
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        assert rec["claim"] == "verified"
        assert rec["cli"]["earlier_failures"] == {"check:registry": 1}
        assert any(
            f["severity"] == "P3" and "failed 1 earlier" in f["description"]
            for f in rec["findings"]
        )

    def test_missing_pin_is_a_mismatch(self, repo: Path) -> None:
        """P3: a pin absent from build-inputs.json fails closed instead of going unchecked."""
        inputs = repo / backend.BUILD_INPUTS_REL
        data = json.loads(inputs.read_text())
        del data["npm"]
        inputs.write_text(json.dumps(data))
        tc = backend.resolve_toolchain(repo)
        assert not tc.ok and any(m.startswith("npm: no pin") for m in tc.mismatches)

    def test_unknown_owner_is_refused(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """P3: no anonymous gate owner."""
        monkeypatch.delenv("SKYYROSE2_GATE_OWNER", raising=False)
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "empty-gitconfig"))
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ev.EvidenceError, match="No gate owner"):
            ev.default_owner()


def test_review_of_other_harness_code_does_not_count(repo: Path, tmp_path: Path) -> None:
    sess = sess_mod.new_session(repo)
    run = _entry(repo, sess)
    cand = cand_mod.capture(repo)
    review = {
        **ev.review_entry(
            candidate=cand, reviewer="r", disposition="PASS", note="n", owners={"builder"}
        ),
        "harness_sha256": "0" * 64,
    }
    rec = ev.build_record(
        session_runs=[run],
        reviews=[review],
        candidate=cand,
        toolchain=_toolchain(),
        out_dir=tmp_path / "o",
    )
    assert rec["fashion_theme_team"]["status"] == "BLOCKED"


# ---------------------------------------------------------------------------
# CLI commands in-process (synthetic repo; real npm for the failing-gate path)
# ---------------------------------------------------------------------------


def _cli(repo: Path, *args: str, input: str | None = None):
    from cli_anything.skyyrose_flagship_2.skyyrose_flagship_2_cli import CliState, cli
    from click.testing import CliRunner

    return CliRunner().invoke(cli, ["--repo-root", str(repo), *args], obj=CliState(), input=input)


@pytest.fixture()
def pinned_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Accept the host toolchain so a synthetic gate can run through real npm."""
    import os

    tc = Toolchain(
        path_env=os.environ["PATH"],
        node="22.23.2",
        npm="10.9.8",
        python="3.12.12",
        php="8.5.6",
        pins={"node": "22.23.2", "npm": "10.9.8", "python": "3.12.12"},
        deps_sha256=DEPS,
    )
    monkeypatch.setattr(backend, "resolve_toolchain", lambda repo: tc)
    monkeypatch.setenv("SKYYROSE2_GATE_OWNER", "builder")


class TestCliCommands:
    def test_version_show_and_bump(self, repo: Path) -> None:
        shown = _cli(repo, "--json", "version", "show")
        assert shown.exit_code == 0 and json.loads(shown.output)["version"] == "2.5.1"
        plan = _cli(repo, "--json", "version", "bump", "--to", "2.6.0", "--plan")
        assert json.loads(plan.output)["files"] == ["functions.php", "readme.txt", "style.css"]
        assert ver_mod.read_version(repo / THEME).current == "2.5.1"
        bumped = _cli(repo, "--json", "version", "bump", "--to", "2.6.0")
        assert bumped.exit_code == 0 and ver_mod.read_version(repo / THEME).current == "2.6.0"

    def test_version_check_disagreement_exits_3(self, repo: Path) -> None:
        (repo / THEME / "readme.txt").write_text("Stable tag: 2.5.0\n")
        result = _cli(repo, "--json", "version", "check")
        assert result.exit_code == 3 and json.loads(result.stdout)["consistent"] is False

    def test_fixture_status_missing_then_present(
        self, repo: Path, tmp_path: Path, monkeypatch
    ) -> None:
        monkeypatch.delenv("V2_WP_FIXTURE", raising=False)
        pins = repo / backend.FIXTURE_PINS_REL
        pins.parent.mkdir(parents=True, exist_ok=True)
        pins.write_text("{}")
        missing = _cli(repo, "--json", "fixture", "status")
        assert missing.exit_code == 3 and json.loads(missing.stdout)["present"] is False
        fixture = tmp_path / "fx"
        fixture.mkdir()
        monkeypatch.setenv("V2_WP_FIXTURE", str(fixture))
        present = _cli(repo, "--json", "fixture", "status")
        assert present.exit_code == 0 and json.loads(present.output)["path"] == str(fixture)

    def test_session_new_and_show(self, repo: Path) -> None:
        created = json.loads(_cli(repo, "--json", "session", "new").output)
        shown = json.loads(_cli(repo, "--json", "session", "show").output)
        assert shown["session_id"] == created["session_id"] and shown["runs"] == []

    def test_failing_gate_exits_3_and_is_saved(self, repo: Path, pinned_ok: None) -> None:
        scripts = json.loads((repo / THEME / "package.json").read_text())
        scripts["scripts"]["check:registry"] = "exit 1"
        (repo / THEME / "package.json").write_text(json.dumps(scripts))
        result = _cli(repo, "--json", "check", "run", "check:registry")
        assert result.exit_code == 3
        payload = json.loads(result.output)
        assert payload["ok"] is False and payload["runs"][0]["status_reason"] == "exit 1"
        saved = sess_mod.load_session(payload["session_id"])
        assert [r["status"] for r in saved.runs] == ["FAIL"]

    def test_check_all_fail_fast_stops_at_first_failure(self, repo: Path, pinned_ok: None) -> None:
        pkg = json.loads((repo / THEME / "package.json").read_text())
        for name in gates_mod.CHECK_ALL_ORDER:
            pkg["scripts"][name] = "exit 0"
        pkg["scripts"][gates_mod.CHECK_ALL_ORDER[1]] = "exit 2"
        (repo / THEME / "package.json").write_text(json.dumps(pkg))
        result = _cli(repo, "--json", "check", "all", "--fail-fast")
        runs = json.loads(result.output)["runs"]
        assert result.exit_code == 3 and [r["status"] for r in runs] == ["PASS", "FAIL"]

    def test_dry_run_does_not_save(self, repo: Path, pinned_ok: None) -> None:
        result = _cli(repo, "--json", "--dry-run", "check", "run", "check:registry")
        assert result.exit_code == 0 and json.loads(result.output)["saved"] is False
        assert sess_mod.list_sessions() == []

    def test_repl_runs_piped_commands_and_exits(self, repo: Path) -> None:
        """Regression: prompt_toolkit swallowed piped stdin, so agents got no output."""
        result = _cli(repo, input="version show\nhelp\nversion bump --to 9\nexit\n")
        assert result.exit_code == 0, result.output
        assert "2.5.1" in result.output and "Version must be X.Y.Z" in result.output


# ---------------------------------------------------------------------------
# P3 follow-ups from the independent Fashion Theme Team review (2026-10-11)
# ---------------------------------------------------------------------------


def _review(cand, reviewer: str, disposition: str, at: str) -> dict:
    entry = ev.review_entry(
        candidate=cand, reviewer=reviewer, disposition=disposition, note="n", owners={"builder"}
    )
    return {**entry, "reviewed_at": at}


class TestP3Followups:
    # P3a: gate-owner identity is self-asserted -----------------------------

    def test_default_owner_reports_its_source(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("SKYYROSE2_GATE_OWNER", "someone")
        assert ev.default_owner() == ("someone", "env")
        monkeypatch.delenv("SKYYROSE2_GATE_OWNER")
        cfg = tmp_path / "gitconfig"
        cfg.write_text("[user]\n\tname = From Git\n")
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        monkeypatch.chdir(tmp_path)
        assert ev.default_owner() == ("From Git", "git")

    def test_env_owner_is_recorded_flagged_and_does_not_block(
        self, repo: Path, tmp_path: Path
    ) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        run = _entry(repo, sess, owner="builder", owner_source="env")
        header = sess_mod.read_log_header(Path(run["artifact"]["path"]))
        assert run["owner_source"] == "env" and header["owner_source"] == "env"
        rec = ev.build_record(
            session_runs=[run],
            reviews=[_review(cand, "reviewer", "PASS", "2026-10-11T00:00:00+00:00")],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        ftt = rec["fashion_theme_team"]
        assert ftt["owner_sources"] == {"builder": ["env"]}
        assert ftt["gates"][0]["owner_source"] == "env"
        p3 = [f for f in rec["findings"] if ev.UNVERIFIED_OWNER in f["description"]]
        assert len(p3) == 1 and p3[0]["severity"] == "P3" and p3[0]["status"] == "OPEN"
        assert rec["claim"] == "verified" and ftt["status"] == "PASS"

    def test_git_owner_raises_no_unverified_finding(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        rec = ev.build_record(
            session_runs=[_entry(repo, sess, owner_source="git")],
            reviews=[],
            candidate=cand_mod.capture(repo),
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        assert rec["fashion_theme_team"]["owner_sources"] == {"builder": ["git"]}
        assert not any(ev.UNVERIFIED_OWNER in f["description"] for f in rec["findings"])

    def test_ledger_owner_source_edit_is_caught(self, repo: Path, tmp_path: Path) -> None:
        """Rewriting env -> git in session.json would hide the finding; the log header disagrees."""
        sess = sess_mod.new_session(repo)
        run = _entry(repo, sess, owner_source="env")
        with pytest.raises(ev.EvidenceError, match="disagrees with its log"):
            ev.build_record(
                session_runs=[{**run, "owner_source": "git"}],
                reviews=[],
                candidate=cand_mod.capture(repo),
                toolchain=_toolchain(),
                out_dir=tmp_path / "o",
            )

    # P3b: reviews from every session count ----------------------------------

    def test_any_fail_review_decides(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        run = _entry(repo, sess)

        def verdict(reviews: list[dict]) -> str:
            return ev.build_record(
                session_runs=[run],
                reviews=reviews,
                candidate=cand,
                toolchain=_toolchain(),
                out_dir=tmp_path / "o",
            )["fashion_theme_team"]["status"]

        fail_then_pass = [
            _review(cand, "r1", "PASS", "2026-10-11T00:00:02+00:00"),
            _review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"),
        ]
        assert (
            verdict(fail_then_pass) == "FAIL"
        )  # a FAIL is permanent, even against a later same-name PASS
        other_fails = [
            _review(cand, "r2", "FAIL", "2026-10-11T00:00:01+00:00"),
            _review(cand, "r1", "PASS", "2026-10-11T00:00:05+00:00"),
        ]
        assert verdict(other_fails) == "FAIL"  # a later PASS by someone else does not clear it
        assert verdict([_review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00")]) == "FAIL"

    def test_session_new_keeps_an_earlier_fail_review(self, repo: Path, pinned_ok: None) -> None:
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        failed = _cli(
            repo, "evidence", "review", "--reviewer", "r1", "--disposition", "FAIL", "--note", "x"
        )
        assert failed.exit_code == 0, failed.output
        assert _cli(repo, "session", "new").exit_code == 0
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        passed = _cli(
            repo, "evidence", "review", "--reviewer", "r2", "--disposition", "PASS", "--note", "y"
        )
        assert passed.exit_code == 0, passed.output
        out = _cli(repo, "--json", "evidence", "export", "--no-validate")
        payload = json.loads(out.output)
        assert payload["fashion_theme_team"] == "FAIL", payload
        assert "r1" in payload["fashion_theme_team_reason"]

    def test_runner_in_another_session_cannot_review(self, repo: Path, pinned_ok: None) -> None:
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        assert _cli(repo, "session", "new").exit_code == 0
        self_review = _cli(
            repo,
            "--json",
            "evidence",
            "review",
            "--reviewer",
            "builder",
            "--disposition",
            "PASS",
            "--note",
            "z",
        )
        assert self_review.exit_code == 1 and "independent" in self_review.output

    def test_corrupt_session_file_fails_closed(self, repo: Path) -> None:
        good = sess_mod.new_session(repo)
        good.save()
        (sess_mod.state_home() / "sessions" / "logs-only").mkdir(parents=True)
        assert [s.session_id for s in sess_mod.other_sessions()] == [good.session_id]
        assert sess_mod.other_sessions(exclude=good.session_id) == []
        bad = sess_mod.new_session(repo)
        bad.save()
        bad.path.write_text("{not json")
        with pytest.raises(sess_mod.SessionError, match="not valid JSON"):
            sess_mod.other_sessions(exclude=good.session_id)
        bad.path.write_text(json.dumps({"schema": sess_mod.SCHEMA}))
        with pytest.raises(sess_mod.SessionError, match="malformed"):
            sess_mod.other_sessions()

    # P3c: installed deps are part of the environment -----------------------

    def test_deps_digest_reaches_environment_label(self, repo: Path) -> None:
        assert backend.deps_digest(repo) is None
        assert backend.resolve_toolchain(repo).deps_sha256 is None
        assert backend.environment_label(_toolchain(None)).endswith(";deps=none")
        lock = repo / backend.DEPS_LOCK_REL
        lock.parent.mkdir(parents=True)
        lock.write_text('{"lockfileVersion": 3}\n')
        digest = backend.sha256_file(lock)
        assert backend.resolve_toolchain(repo).deps_sha256 == digest
        assert backend.environment_label(_toolchain(digest)).endswith(f";deps={digest[:12]}")

    def test_run_under_other_deps_is_not_a_pass(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        run = _entry(repo, sess, toolchain=_toolchain("a" * 64))
        rec = ev.build_record(
            session_runs=[run],
            reviews=[_review(cand, "reviewer", "PASS", "2026-10-11T00:00:00+00:00")],
            candidate=cand,
            toolchain=_toolchain("b" * 64),
            out_dir=tmp_path / "o",
        )
        assert run["status"] == "PASS"
        assert rec["criteria"][0]["status"] == "FAIL" and rec["claim"] == "blocked"
        assert rec["fashion_theme_team"]["status"] == "FAIL"

    def test_doctor_reports_deps_digest(
        self, repo: Path, pinned_ok: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        pins = repo / backend.FIXTURE_PINS_REL
        pins.parent.mkdir(parents=True, exist_ok=True)
        pins.write_text("{}")
        tc = backend.resolve_toolchain(repo)
        monkeypatch.setattr(
            backend,
            "resolve_toolchain",
            lambda repo: Toolchain(**{**tc.__dict__, "deps_sha256": None}),
        )
        missing = json.loads(_cli(repo, "--json", "doctor").stdout)
        assert missing["ok"] is False and missing["deps_label"] == "none"
        assert "npm ci" in missing["deps_hint"]
        monkeypatch.setattr(
            backend,
            "resolve_toolchain",
            lambda repo: Toolchain(**{**tc.__dict__, "deps_sha256": "c" * 64}),
        )
        present = json.loads(_cli(repo, "--json", "doctor").stdout)
        assert present["deps_sha256"] == "c" * 64 and present["deps_label"] == "c" * 12
        assert present["deps_hint"] is None


# ---------------------------------------------------------------------------
# Review round 2 (2026-10-11): FAIL laundering, owner provenance, deps=none
# ---------------------------------------------------------------------------


def _export(repo: Path) -> dict:
    out = _cli(repo, "--json", "evidence", "export", "--no-validate")
    assert out.exit_code == 0, out.output
    return json.loads(Path(json.loads(out.output)["record"]).read_text())


class TestReviewRound2:
    # P1 / P2: owner filtering must never drop a FAIL ------------------------

    def test_fail_survives_reviewer_becoming_owner_in_other_session(
        self, repo: Path, tmp_path: Path
    ) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        run = _entry(repo, sess, owner="alice")
        other = sess_mod.new_session(repo)
        laundering = _entry(repo, other, owner="bob", owner_source="env")
        rec = ev.build_record(
            session_runs=[run],
            reviews=[
                _review(cand, "bob", "FAIL", "2026-10-11T00:00:01+00:00"),
                _review(cand, "carol", "PASS", "2026-10-11T00:00:02+00:00"),
            ],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
            other_runs=[laundering],
        )
        ftt = rec["fashion_theme_team"]
        assert ftt["status"] == "FAIL" and "bob" in ftt["reason"], ftt
        assert ftt["owners"] == ["alice", "bob"]
        assert [r["reviewer"] for r in ftt["reviews_considered"]] == ["bob", "carol"]

    def test_owner_pass_never_counts(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        rec = ev.build_record(
            session_runs=[_entry(repo, sess), _entry(repo, sess, owner="r1")],
            reviews=[_review(cand, "r1", "PASS", "2026-10-11T00:00:01+00:00")],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        assert rec["fashion_theme_team"]["status"] == "BLOCKED"
        assert rec["fashion_theme_team"]["reviews_considered"] == []

    def test_fail_cannot_be_withdrawn_by_same_name_pass(self, repo: Path, tmp_path: Path) -> None:
        """Round 3: names are self-declared, so a later same-name PASS never clears a FAIL."""
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        rec = ev.build_record(
            session_runs=[_entry(repo, sess), _entry(repo, sess, owner="r1")],
            reviews=[
                _review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"),
                _review(cand, "r1", "PASS", "2026-10-11T00:00:02+00:00"),
            ],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        assert rec["fashion_theme_team"]["status"] == "FAIL"

    @pytest.mark.timeout(60)
    def test_cli_cannot_launder_fail_through_owner_run_in_other_session(
        self, repo: Path, pinned_ok: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Reviewer's exact repro: FAIL, then a run as r1 elsewhere, then a fresh PASS."""
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        failed = _cli(
            repo, "evidence", "review", "--reviewer", "r1", "--disposition", "FAIL", "--note", "x"
        )
        assert failed.exit_code == 0, failed.output
        assert _cli(repo, "session", "new").exit_code == 0
        monkeypatch.setenv("SKYYROSE2_GATE_OWNER", "r1")
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        monkeypatch.setenv("SKYYROSE2_GATE_OWNER", "builder")
        assert _cli(repo, "session", "new").exit_code == 0
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        passed = _cli(
            repo, "evidence", "review", "--reviewer", "r2", "--disposition", "PASS", "--note", "y"
        )
        assert passed.exit_code == 0, passed.output
        rec = _export(repo)
        ftt = rec["fashion_theme_team"]
        assert ftt["status"] == "FAIL" and "r1" in ftt["reason"], ftt
        # P2: the laundering run lives only in another session, yet it is disclosed.
        assert ftt["owner_sources"] == {"builder": ["env"], "r1": ["env"]}
        unverified = [f for f in rec["findings"] if ev.UNVERIFIED_OWNER in f["description"]]
        assert len(unverified) == 1 and "r1" in unverified[0]["description"]

    # P2: owner_sources and the env finding cover every owner-feeding run --------

    def test_superseded_env_run_is_disclosed(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        superseded = _entry(repo, sess, owner="bob", owner_source="env")
        latest = _entry(repo, sess, owner="alice")
        rec = ev.build_record(
            session_runs=[superseded, latest],
            reviews=[],
            candidate=cand_mod.capture(repo),
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
        ftt = rec["fashion_theme_team"]
        assert [g["owner"] for g in ftt["gates"]] == ["alice"]
        assert set(ftt["owners"]) == set(ftt["owner_sources"]) == {"alice", "bob"}
        assert ftt["owner_sources"] == {"alice": ["git"], "bob": ["env"]}
        unverified = [f for f in rec["findings"] if ev.UNVERIFIED_OWNER in f["description"]]
        assert len(unverified) == 1 and "bob" in unverified[0]["description"]
        assert "alice" not in unverified[0]["description"]

    def test_run_without_owner_source_counts_as_unverified(self, repo: Path) -> None:
        cand = cand_mod.capture(repo)
        legacy = {"candidate_id": cand.candidate_id, "owner": "old"}
        assert ev.owner_sources_for([legacy], cand) == {"old": ["unrecorded"]}

    # P2: owner_source "git" cannot be supplied through the environment ---------

    def test_git_owner_ignores_env_config_injection_and_other_cwd(
        self, repo: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("SKYYROSE2_GATE_OWNER", raising=False)
        cfg = tmp_path / "gitconfig"
        cfg.write_text("[user]\n\tname = From Git\n")
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
        monkeypatch.setenv("GIT_CONFIG_KEY_0", "user.name")
        monkeypatch.setenv("GIT_CONFIG_VALUE_0", "alice")
        monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'user.name'='mallory'")
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        _git(elsewhere, "init", "-q")
        _git(elsewhere, "config", "user.name", "cwd-local")
        monkeypatch.chdir(elsewhere)
        assert ev.default_owner(repo) == ("From Git", "git")
        assert ev.default_owner(elsewhere) == ("cwd-local", "git")

    # P2: unidentified installed deps block, never pass -------------------------

    def test_deps_none_at_run_and_export_blocks(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        run = _entry(repo, sess, toolchain=_toolchain(None))
        rec = ev.build_record(
            session_runs=[run],
            reviews=[_review(cand, "reviewer", "PASS", "2026-10-11T00:00:00+00:00")],
            candidate=cand,
            toolchain=_toolchain(None),
            out_dir=tmp_path / "o",
        )
        assert run["status"] == "PASS" and run["environment"] == rec["target"]["environment"]
        assert rec["criteria"][0]["status"] == "FAIL" and rec["claim"] == "blocked"
        assert "deps are unidentified" in rec["criteria"][0]["reason"]
        assert any(
            f["severity"] == "P1" and "deps are unidentified" in f["description"]
            for f in rec["findings"]
        )
        ftt = rec["fashion_theme_team"]
        assert ftt["status"] == "BLOCKED" and backend.DEPS_LOCK_REL in ftt["reason"]

    def test_reviewer_fail_outranks_unidentified_deps(self, repo: Path, tmp_path: Path) -> None:
        sess = sess_mod.new_session(repo)
        cand = cand_mod.capture(repo)
        rec = ev.build_record(
            session_runs=[_entry(repo, sess, toolchain=_toolchain(None))],
            reviews=[_review(cand, "reviewer", "FAIL", "2026-10-11T00:00:00+00:00")],
            candidate=cand,
            toolchain=_toolchain(None),
            out_dir=tmp_path / "o",
        )
        assert rec["fashion_theme_team"]["status"] == "FAIL"


class TestReviewRound3:
    """A FAIL on a candidate is permanent; only a new candidate (a code change) gets past it."""

    def _rec(self, repo: Path, tmp_path: Path, reviews: list[dict]) -> dict:
        sess = sess_mod.new_session(repo)
        return ev.build_record(
            session_runs=[_entry(repo, sess)],
            reviews=reviews,
            candidate=cand_mod.capture(repo),
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )

    def test_fail_from_other_harness_still_stands(self, repo: Path, tmp_path: Path) -> None:
        cand = cand_mod.capture(repo)
        old = {
            **_review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"),
            "harness_sha256": "0" * 64,
        }
        later_pass = _review(cand, "r2", "PASS", "2026-10-11T00:00:02+00:00")
        rec = self._rec(repo, tmp_path, [old, later_pass])
        assert rec["fashion_theme_team"]["status"] == "FAIL"

    def test_case_folded_same_name_pass_cannot_clear_fail(self, repo: Path, tmp_path: Path) -> None:
        cand = cand_mod.capture(repo)
        reviews = [
            _review(cand, "bob", "FAIL", "2026-10-11T00:00:01+00:00"),
            _review(cand, " BOB ", "PASS", "2026-10-11T00:00:02+00:00"),
        ]
        assert self._rec(repo, tmp_path, reviews)["fashion_theme_team"]["status"] == "FAIL"

    @pytest.mark.parametrize(
        "bad", [{"disposition": "fail"}, {"disposition": None}, {"reviewer": None}]
    )
    def test_malformed_review_fails_closed(self, repo: Path, tmp_path: Path, bad: dict) -> None:
        cand = cand_mod.capture(repo)
        review = {**_review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"), **bad}
        with pytest.raises(ev.EvidenceError, match="Malformed review"):
            self._rec(repo, tmp_path, [review])

    def test_fail_on_other_candidate_does_not_leak(self, repo: Path, tmp_path: Path) -> None:
        cand = cand_mod.capture(repo)
        other = {
            **_review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"),
            "candidate_id": "f" * 16,
        }
        good = _review(cand, "r2", "PASS", "2026-10-11T00:00:02+00:00")
        assert self._rec(repo, tmp_path, [other, good])["fashion_theme_team"]["status"] == "PASS"


class TestReviewNits:
    """The three P3s noted on #1071."""

    def _rec(self, repo: Path, tmp_path: Path, reviews: list) -> dict:
        sess = sess_mod.new_session(repo)
        return ev.build_record(
            session_runs=[_entry(repo, sess)],
            reviews=reviews,
            candidate=cand_mod.capture(repo),
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )

    @pytest.mark.parametrize("name", ["", "   ", "\t\n"])
    def test_blank_reviewer_is_refused(self, repo: Path, name: str) -> None:
        with pytest.raises(ev.EvidenceError, match="non-blank"):
            ev.review_entry(
                candidate=cand_mod.capture(repo),
                reviewer=name,
                disposition="PASS",
                note="n",
                owners={"builder"},
            )

    def test_reviewer_name_is_stored_trimmed(self, repo: Path) -> None:
        entry = ev.review_entry(
            candidate=cand_mod.capture(repo),
            reviewer="  r1 ",
            disposition="PASS",
            note="n",
            owners={"builder"},
        )
        assert entry["reviewer"] == "r1"

    @pytest.mark.parametrize("bad", ["not-a-dict", 42, None, ["x"]])
    def test_non_dict_review_is_a_clean_error(
        self, repo: Path, tmp_path: Path, bad: object
    ) -> None:
        with pytest.raises(ev.EvidenceError, match="Malformed review"):
            self._rec(repo, tmp_path, [bad])

    @pytest.mark.parametrize(
        "edit", [{"candidate_id": None}, {"candidate_id": ""}, {"reviewer": "  "}]
    )
    def test_unattributable_fail_fails_closed(self, repo: Path, tmp_path: Path, edit: dict) -> None:
        cand = cand_mod.capture(repo)
        review = {**_review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"), **edit}
        with pytest.raises(ev.EvidenceError, match="Malformed review"):
            self._rec(repo, tmp_path, [review])

    def test_cli_rejects_non_dict_review_without_traceback(
        self, repo: Path, pinned_ok: None
    ) -> None:
        assert _cli(repo, "check", "run", "check:registry").exit_code == 0
        sid = sess_mod.current_session_id()
        path = sess_mod.state_home() / "sessions" / sid / "session.json"
        data = json.loads(path.read_text())
        data["reviews"] = ["junk"]
        path.write_text(json.dumps(data))
        result = _cli(repo, "--json", "evidence", "export", "--no-validate")
        assert result.exit_code == 1
        assert "Malformed review" in json.loads(result.stdout)["error"]


@pytest.mark.parametrize("name", ["\u200b", "\ufeff", "\u2060 \u200b"])
def test_invisible_only_reviewer_is_refused(repo: Path, name: str) -> None:
    with pytest.raises(ev.EvidenceError, match="non-blank"):
        ev.review_entry(
            candidate=cand_mod.capture(repo),
            reviewer=name,
            disposition="PASS",
            note="n",
            owners={"builder"},
        )


@pytest.mark.parametrize("cid", [" {c} ", "{c}\n", "{C}", "{c}0"])
def test_padded_or_altered_candidate_id_fails_closed(repo: Path, tmp_path: Path, cid: str) -> None:
    sess = sess_mod.new_session(repo)
    cand = cand_mod.capture(repo)
    bad = {
        **_review(cand, "r1", "FAIL", "2026-10-11T00:00:01+00:00"),
        "candidate_id": cid.format(c=cand.candidate_id, C=cand.candidate_id.upper()),
    }
    with pytest.raises(ev.EvidenceError, match="Malformed review"):
        ev.build_record(
            session_runs=[_entry(repo, sess)],
            reviews=[bad],
            candidate=cand,
            toolchain=_toolchain(),
            out_dir=tmp_path / "o",
        )
