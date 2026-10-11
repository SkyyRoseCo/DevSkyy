"""
cli-anything-skyyrose-flagship-2 — agent CLI for the SkyyRose Flagship 2 theme.

Runs the theme's own npm gates under the pinned V2 toolchain, records every run
in a session ledger bound to the exact candidate tree, and exports evidence that
God Mode X validates and the Fashion Theme Team reviews.

No subcommand opens the REPL. ``--json`` gives machine output on every command.
There is no deploy, recertification, or paid-provider command by design.
"""

from __future__ import annotations

import json
import shlex
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click
from cli_anything.skyyrose_flagship_2 import __version__
from cli_anything.skyyrose_flagship_2.core import candidate as cand_mod
from cli_anything.skyyrose_flagship_2.core import evidence as ev
from cli_anything.skyyrose_flagship_2.core import gates as gates_mod
from cli_anything.skyyrose_flagship_2.core import session as sess_mod
from cli_anything.skyyrose_flagship_2.core import version as ver_mod
from cli_anything.skyyrose_flagship_2.utils import backend

_GATE_EXIT = 3  # a gate ran and failed (distinct from usage/refusal errors = 1)


@dataclass
class CliState:
    json_output: bool = False
    repo_arg: str | None = None
    dry_run: bool = False
    repl_mode: bool = False
    _repo: Path | None = None
    _session: sess_mod.Session | None = None
    _skin: Any = None

    @property
    def repo(self) -> Path:
        if self._repo is None:
            self._repo = backend.find_repo_root(self.repo_arg)
        return self._repo

    @property
    def session(self) -> sess_mod.Session:
        if self._session is None:
            self._session = sess_mod.open_or_create(self.repo)
        return self._session

    @property
    def skin(self) -> Any:
        if self._skin is None:
            from cli_anything.skyyrose_flagship_2.utils.repl_skin import ReplSkin

            self._skin = ReplSkin("skyyrose_flagship_2", version=__version__)
        return self._skin

    def autosave(self) -> None:
        if self._session is not None and self._session.modified and not self.dry_run:
            self._session.save()


pass_state = click.make_pass_decorator(CliState, ensure=True)


def emit(state: CliState, payload: dict[str, Any], human: str | None = None) -> None:
    if state.json_output:
        click.echo(json.dumps(payload, indent=2, default=str))
    elif human is not None:
        click.echo(human)
    else:
        for key, value in payload.items():
            click.echo(f"  {key}: {value}")


def fail(state: CliState, message: str, code: int = 1, **extra: Any) -> None:
    if state.json_output:
        click.echo(json.dumps({"ok": False, "error": message, **extra}, indent=2, default=str))
    else:
        click.echo(f"✗ {message}", err=True)
    if state.repl_mode:
        raise click.exceptions.Exit(code)
    sys.exit(code)


def finish(state: CliState, message: str, code: int) -> None:
    """Exit non-zero after the payload was already emitted (keeps --json stdout one document)."""
    click.echo(f"✗ {message}", err=True)
    if state.repl_mode:
        raise click.exceptions.Exit(code)
    sys.exit(code)


def guarded(fn):
    """Turn backend/domain errors into clean, agent-readable failures."""
    import functools

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        state = click.get_current_context().find_object(CliState)
        try:
            return fn(*args, **kwargs)
        except (
            backend.BackendError,
            gates_mod.GateRefusedError,
            ver_mod.VersionError,
            sess_mod.SessionError,
            ev.EvidenceError,
        ) as exc:
            fail(state, str(exc))

    return wrapper


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.option("--json", "json_output", is_flag=True, help="Emit JSON output.")
@click.option("--repo-root", envvar="SKYYROSE2_REPO_ROOT", help="DevSkyy checkout to operate on.")
@click.option("--dry-run", is_flag=True, help="Run the command but do not save the session ledger.")
@click.version_option(__version__, package_name="cli-anything-skyyrose-flagship-2")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, repo_root: str | None, dry_run: bool) -> None:
    """SkyyRose Flagship 2 theme: gates, version, pins, and shared evidence."""
    state = ctx.ensure_object(CliState)
    if not state.repl_mode:
        state.json_output = json_output
        state.repo_arg = repo_root
        state.dry_run = dry_run
        ctx.call_on_close(state.autosave)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ---------------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------------


@cli.command()
@pass_state
@guarded
def doctor(state: CliState) -> None:
    """Check the repo, toolchain pins, product-registry pin and God Mode X checker."""
    repo = state.repo
    tc = backend.resolve_toolchain(repo)
    pins = cand_mod.pin_status(repo)
    checker: str | None
    checker_error: str | None
    try:
        checker = str(ev.find_checker())
    except ev.EvidenceError as exc:
        checker = None
        checker_error = str(exc)
    else:
        checker_error = None
    node_modules = (backend.theme_dir(repo) / "node_modules").is_dir()
    deps = tc.deps_sha256
    fixture = backend.fixture_dir(repo, sess_mod.state_home())
    healthy = (
        tc.ok
        and pins["in_sync"]
        and checker is not None
        and node_modules
        and deps is not None
        and fixture is not None
    )
    payload = {
        "ok": healthy,
        "repo_root": str(repo),
        "toolchain": tc.to_dict(),
        "registry_pin": pins,
        "node_modules": node_modules,
        "node_modules_hint": (
            None
            if node_modules
            else f"cd {backend.theme_dir(repo)} && npm ci  (with the pinned node on PATH)"
        ),
        "deps_sha256": deps,
        "deps_label": deps[:12] if deps else "none",
        "deps_hint": (
            None
            if deps
            else f"{backend.DEPS_LOCK_REL} missing: installed deps are unidentified (environment "
            f"label deps=none). Run `npm ci` in {backend.theme_dir(repo)} with the pinned node."
        ),
        "god_mode_x_checker": checker,
        "god_mode_x_error": checker_error,
        "wp_fixture": str(fixture) if fixture else None,
    }
    lines = [
        f"repo         {repo}",
        f"toolchain    {'ok' if tc.ok else 'MISMATCH'}  {tc.versions()}",
        *[f"  ✗ {m}" for m in tc.mismatches],
        f"registry pin {'in sync' if pins['in_sync'] else 'DRIFTED'}",
        f"node_modules {'present' if node_modules else 'missing — ' + str(payload['node_modules_hint'])}",
        f"deps digest  {deps[:12] if deps else 'MISSING — ' + str(payload['deps_hint'])}",
        f"god mode x   {checker or checker_error}",
        f"wp fixture   {fixture or 'missing — run `fixture prepare` (needed by verify, package:theme)'}",
    ]
    emit(state, payload, "\n".join(lines))
    if not healthy:
        finish(state, "doctor found problems", 1)


@cli.command()
@pass_state
@guarded
def info(state: CliState) -> None:
    """Show the candidate identity and the SKYYROSE2_VERSION triple."""
    repo = state.repo
    cand = cand_mod.capture(repo)
    ver = ver_mod.read_version(backend.theme_dir(repo))
    payload = {"repo_root": str(repo), "candidate": cand.to_dict(), "version": ver.to_dict()}
    human = (
        f"candidate {cand.candidate_id}  {cand.revision}  branch={cand.branch}\n"
        f"theme     {cand.artifact}\n"
        f"version   {ver.to_dict()['version'] or 'INCONSISTENT ' + str(ver.sources)}"
    )
    emit(state, payload, human)


@cli.group()
def scripts() -> None:
    """Inspect the theme's npm scripts and how this CLI classifies them."""


@scripts.command("list")
@click.option("--kind", type=click.Choice(["check", "build", "blocked", "unclassified"]))
@pass_state
@guarded
def scripts_list(state: CliState, kind: str | None) -> None:
    gates = gates_mod.classify_all(backend.load_package_scripts(state.repo))
    if kind:
        gates = [g for g in gates if g.kind == kind]
    rows = [g.to_dict() for g in gates]
    human = "\n".join(
        f"{g.kind:13} {g.name}" + (f"   ({g.reason})" if g.reason else "") for g in gates
    )
    emit(state, {"scripts": rows, "count": len(rows)}, human)


@cli.group()
def pin() -> None:
    """V2 certification pins (read-only)."""


@pin.command("status")
@pass_state
@guarded
def pin_status_cmd(state: CliState) -> None:
    payload = cand_mod.pin_status(state.repo)
    emit(
        state,
        payload,
        f"in_sync={payload['in_sync']}  actual={payload['actual_sha256'][:12]}  "
        f"pinned={str(payload['current_registry_sha256'])[:12]}"
        + (f"\n{payload['action']}" if payload["action"] else ""),
    )
    if not payload["in_sync"]:
        finish(state, "registry pin drifted", _GATE_EXIT)


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def _execute(state: CliState, name: str, kind: str, timeout: float | None) -> dict[str, Any]:
    repo = state.repo
    gate = gates_mod.require_runnable(name, backend.load_package_scripts(repo), kind)
    extra_env: dict[str, str] = {}
    if name in gates_mod.NEEDS_WP_FIXTURE:
        fixture = backend.fixture_dir(repo, sess_mod.state_home())
        if fixture is None:
            raise backend.BackendError(
                f"{name} needs the pinned WordPress/WooCommerce fixture. Run "
                "`cli-anything-skyyrose-flagship-2 fixture prepare` or set V2_WP_FIXTURE."
            )
        extra_env["V2_WP_FIXTURE"] = str(fixture)
    tc = backend.resolve_toolchain(repo)
    if not tc.ok:
        raise backend.ToolchainMismatchError(
            "Toolchain does not match the V2 pins: " + " | ".join(tc.mismatches)
        )
    owner, owner_source = ev.default_owner()  # fail before running, never record an anonymous run
    before = cand_mod.capture(repo)
    result = backend.run_npm_script(repo, name, tc, timeout=timeout, extra_env=extra_env)
    after = cand_mod.capture(repo)
    sess = state.session
    text = sess_mod.format_log(
        ev.log_header(
            gate=gate,
            result=result,
            before=before,
            after=after,
            owner=owner,
            owner_source=owner_source,
        ),
        result.stdout,
        result.stderr,
    )
    if state.dry_run:
        log = Path(tempfile.mkdtemp(prefix="skyyrose2-dry-")) / f"{name.replace(':', '_')}.log"
        log.write_text(text, encoding="utf-8")
    else:
        log = sess.write_log(name, text)
    entry = ev.run_entry(
        gate=gate,
        result=result,
        before=before,
        after=after,
        toolchain=tc,
        log_path=log,
        owner=owner,
        owner_source=owner_source,
    )
    sess.add_run(entry)
    if not state.repl_mode:
        state.autosave()
    return entry


def _gate_line(entry: dict[str, Any]) -> str:
    mark = "✓" if entry["status"] == "PASS" else "✗"
    changed = f"  changed: {', '.join(entry['changed_paths'])}" if entry["changed_paths"] else ""
    return f"{mark} {entry['gate_id']:28} {entry['status']:4} {entry['status_reason']}{changed}"


@cli.group()
def check() -> None:
    """Run read-only gates (they must not change tracked files)."""


@check.command("run")
@click.argument("names", nargs=-1, required=True)
@click.option("--timeout", type=float, default=None, help="Seconds before a gate is killed.")
@pass_state
@guarded
def check_run(state: CliState, names: tuple[str, ...], timeout: float | None) -> None:
    """Run one or more read-only gates, e.g. `check run check:registry lint:php`."""
    entries = [_execute(state, name, "check", timeout) for name in names]
    _report_gates(state, entries)


@check.command("all")
@click.option("--fail-fast", is_flag=True, help="Stop at the first failing gate.")
@click.option("--timeout", type=float, default=None)
@pass_state
@guarded
def check_all(state: CliState, fail_fast: bool, timeout: float | None) -> None:
    """Run the standard read-only set, ending with the full `verify` chain."""
    entries = []
    for name in gates_mod.CHECK_ALL_ORDER:
        entries.append(_execute(state, name, "check", timeout))
        if fail_fast and entries[-1]["status"] != "PASS":
            break
    _report_gates(state, entries)


@cli.group()
def build() -> None:
    """Run local build gates that regenerate tracked theme outputs (never deploys)."""


@build.command("run")
@click.argument("name")
@click.option("--plan", is_flag=True, help="Show what would run without running it.")
@click.option("--timeout", type=float, default=None)
@pass_state
@guarded
def build_run(state: CliState, name: str, plan: bool, timeout: float | None) -> None:
    """Run a build gate and report which tracked files it changed."""
    scripts_map = backend.load_package_scripts(state.repo)
    gate = gates_mod.require_runnable(name, scripts_map, "build")
    if plan:
        emit(
            state,
            {"plan": True, "gate": gate.to_dict(), "cwd": backend.THEME_REL},
            f"would run: npm run {name}\n  -> {gate.command}",
        )
        return
    _report_gates(state, [_execute(state, name, "build", timeout)])


def _report_gates(state: CliState, entries: list[dict[str, Any]]) -> None:
    ok = all(e["status"] == "PASS" for e in entries)
    payload = {
        "ok": ok,
        "session_id": state.session.session_id,
        "saved": not state.dry_run,
        "runs": entries,
    }
    emit(state, payload, "\n".join(_gate_line(e) for e in entries))
    if not ok:
        if state.repl_mode:
            return
        state.autosave()
        sys.exit(_GATE_EXIT)


@cli.group()
def fixture() -> None:
    """Hash-pinned native WordPress 7.1 / WooCommerce 11.1.0 files used by `verify`."""


@fixture.command("status")
@pass_state
@guarded
def fixture_status(state: CliState) -> None:
    found = backend.fixture_dir(state.repo, sess_mod.state_home())
    payload = {
        "present": found is not None,
        "path": str(found) if found else None,
        "managed_path": str(backend.managed_fixture_dir(state.repo, sess_mod.state_home())),
    }
    emit(state, payload, f"{'present' if found else 'missing'}  {found or payload['managed_path']}")
    if found is None:
        finish(state, "fixture missing", _GATE_EXIT)


@fixture.command("prepare")
@pass_state
@guarded
def fixture_prepare(state: CliState) -> None:
    """Download the 7 pinned files via the repo's own hash-checking script (free, public sources)."""
    repo = state.repo
    path = backend.prepare_fixture(repo, sess_mod.state_home(), backend.resolve_toolchain(repo))
    emit(state, {"ok": True, "path": str(path)}, f"✓ fixture ready at {path}")


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


@cli.group()
def version() -> None:
    """SKYYROSE2_VERSION triple (functions.php, style.css, readme.txt)."""


@version.command("show")
@pass_state
@guarded
def version_show(state: CliState) -> None:
    ver = ver_mod.read_version(backend.theme_dir(state.repo))
    emit(
        state,
        ver.to_dict(),
        "\n".join(f"{k:14} {v}" for k, v in ver.sources.items())
        + f"\n{'package.json':14} {ver.package_json} (informational)",
    )


@version.command("check")
@pass_state
@guarded
def version_check(state: CliState) -> None:
    ver = ver_mod.read_version(backend.theme_dir(state.repo))
    emit(state, ver.to_dict(), f"consistent={ver.consistent} {ver.sources}")
    if not ver.consistent:
        finish(state, "version sources disagree", _GATE_EXIT)


@version.command("bump")
@click.option("--to", "new_version", required=True, help="New X.Y.Z version.")
@click.option("--plan", is_flag=True, help="Show the change without writing.")
@pass_state
@guarded
def version_bump(state: CliState, new_version: str, plan: bool) -> None:
    """Bump all three sources atomically (local files only; deploy is separate)."""
    theme = backend.theme_dir(state.repo)
    if plan:
        changes = ver_mod.plan_bump(theme, new_version)
        emit(
            state,
            {"plan": True, "to": new_version, "files": sorted(changes)},
            f"would set {new_version} in: {', '.join(sorted(changes))}",
        )
        return
    result = ver_mod.write_version(theme, new_version)
    emit(
        state,
        {"ok": True, **result.to_dict()},
        f"✓ SKYYROSE2_VERSION = {new_version} in all three sources",
    )


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


@cli.group()
def session() -> None:
    """The gate-run ledger."""


@session.command("new")
@pass_state
@guarded
def session_new(state: CliState) -> None:
    state._session = sess_mod.new_session(state.repo)
    if not state.dry_run:
        state._session.save()
    emit(state, state._session.summary(), f"session {state._session.session_id}")


@session.command("show")
@pass_state
@guarded
def session_show(state: CliState) -> None:
    sess = state.session
    payload = {**sess.summary(), "runs": sess.runs, "reviews": sess.reviews}
    emit(
        state,
        payload,
        "\n".join(
            [
                f"session {sess.session_id} ({len(sess.runs)} runs)",
                *(_gate_line(r) for r in sess.runs),
            ]
        ),
    )


@session.command("list")
@pass_state
def session_list(state: CliState) -> None:
    rows = sess_mod.list_sessions()
    emit(
        state,
        {"sessions": rows, "current": sess_mod.current_session_id()},
        "\n".join(f"{r['session_id']}  runs={r.get('runs')}" for r in rows) or "no sessions",
    )


# ---------------------------------------------------------------------------
# Evidence (Fashion Theme Team + God Mode X)
# ---------------------------------------------------------------------------


@cli.group()
def evidence() -> None:
    """Export, validate, and review evidence for the current candidate."""


@evidence.command("export")
@click.option("-o", "--out", "out_dir", type=click.Path(file_okay=False), help="Output directory.")
@click.option("--task-id", default=None)
@click.option("--objective", default=None)
@click.option(
    "--validate/--no-validate", default=True, help="Run God Mode X's checker on the result."
)
@pass_state
@guarded
def evidence_export(
    state: CliState, out_dir: str | None, task_id: str | None, objective: str | None, validate: bool
) -> None:
    """Write a God Mode X task-evidence record (with the Fashion Theme Team verdict)."""
    repo = state.repo
    cand = cand_mod.capture(repo)
    tc = backend.resolve_toolchain(repo)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = (
        Path(out_dir)
        if out_dir
        else state.session.directory / "evidence" / f"{cand.candidate_id}-{stamp}"
    )
    others = sess_mod.other_sessions(exclude=state.session.session_id)
    out.mkdir(parents=True, exist_ok=True)
    record = ev.build_record(
        session_runs=state.session.runs,
        reviews=[*(r for o in others for r in o.reviews), *state.session.reviews],
        candidate=cand,
        toolchain=tc,
        out_dir=out,
        task_id=task_id,
        objective=objective,
        other_runs=[r for o in others for r in o.runs],
    )
    path = ev.write_record(record, out)
    verdict = ev.validate_with_god_mode_x(path, ev.find_checker()) if validate else None
    ftt = record["fashion_theme_team"]
    payload = {
        "record": str(path),
        "claim": record["claim"],
        "fashion_theme_team": ftt["status"],
        "fashion_theme_team_reason": ftt["reason"],
        "god_mode_x": verdict,
    }
    human = (
        f"record   {path}\nclaim    {record['claim']}\nFTT      {ftt['status']} — {ftt['reason']}"
        + (
            f"\nGMX      {verdict['gate']}" + "".join(f"\n  - {p}" for p in verdict["problems"])
            if verdict
            else ""
        )
    )
    emit(state, payload, human)
    if verdict and verdict["gate"] != "PASS":
        finish(state, "God Mode X rejected the record (see problems)", _GATE_EXIT)


@evidence.command("validate")
@click.argument("record", type=click.Path(exists=True, dir_okay=False))
@pass_state
@guarded
def evidence_validate(state: CliState, record: str) -> None:
    """Validate any task-evidence record with God Mode X's own checker."""
    verdict = ev.validate_with_god_mode_x(Path(record), ev.find_checker())
    emit(
        state,
        verdict,
        f"{verdict['gate']}" + "".join(f"\n  - {p}" for p in verdict.get("problems", [])),
    )
    if verdict["gate"] != "PASS":
        finish(state, "God Mode X rejected the record", _GATE_EXIT)


@evidence.command("review")
@click.option(
    "--reviewer", required=True, help="Independent reviewer (must not be the gate owner)."
)
@click.option("--disposition", type=click.Choice(["PASS", "FAIL"]), required=True)
@click.option("--note", required=True, help="What was inspected.")
@pass_state
@guarded
def evidence_review(state: CliState, reviewer: str, disposition: str, note: str) -> None:
    """Record an independent Fashion Theme Team review of the current candidate."""
    cand = cand_mod.capture(state.repo)
    others = sess_mod.other_sessions(exclude=state.session.session_id)
    entry = ev.review_entry(
        candidate=cand,
        reviewer=reviewer,
        disposition=disposition,
        note=note,
        owners=ev.run_owners([*(r for o in others for r in o.runs), *state.session.runs], cand),
    )
    state.session.add_review(entry)
    if not state.repl_mode:
        state.autosave()
    emit(
        state,
        {"ok": True, "review": entry},
        f"✓ {disposition} by {reviewer} on {cand.candidate_id}",
    )


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------


@cli.command()
@click.pass_context
def repl(ctx: click.Context) -> None:
    """Interactive mode (default when no subcommand is given)."""
    state = ctx.ensure_object(CliState)
    state.repl_mode = True
    skin = state.skin
    skin.print_banner()
    # prompt_toolkit swallows piped (non-TTY) input; agents pipe commands, so use input() there.
    pt = skin.create_prompt_session() if sys.stdin.isatty() else None
    commands = {
        name: (cmd.help or "").split("\n")[0]
        for name, cmd in cli.commands.items()
        if name != "repl"
    }
    while True:
        try:
            line = skin.get_input(
                pt,
                project_name="flagship-2",
                modified=bool(state._session and state._session.modified),
            )
        except (EOFError, KeyboardInterrupt):
            break
        line = (line or "").strip()
        if not line:
            continue
        if line in {"exit", "quit"}:
            break
        if line == "help":
            skin.help(commands)
            continue
        try:
            cli.main(
                args=shlex.split(line),
                prog_name="skyyrose-flagship-2",
                standalone_mode=False,
                obj=state,
            )
        except click.exceptions.Exit:
            pass
        except click.ClickException as exc:
            skin.error(exc.format_message())
        except ValueError as exc:
            skin.error(str(exc))
        if state._session is not None and state._session.modified and not state.dry_run:
            state._session.save()
    skin.print_goodbye()


def main() -> None:
    cli(obj=CliState())


if __name__ == "__main__":
    main()
