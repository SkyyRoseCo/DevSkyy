"""Native prospective fence controls on the dedicated private clone only."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

if not __debug__:
    raise RuntimeError("Verification requires Python assertions; optimized mode is refused")

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-local"
EVIDENCE = ROOT / "tasks/release-gates-20261019/gate4-local/evidence"
PROFILE = '(version 1)(allow default)(deny network*)(allow network-outbound (remote unix-socket (literal "/private/tmp/sr-gate4-01a0f768.sock")))'
RUNTIME = json.loads((PRIVATE / "runtime-profile.json").read_text())
assert RUNTIME["profile"] == PROFILE
SKIPPED = RUNTIME["wp_skip_plugins"]
assert all(isinstance(s, str) and s.replace("-", "").isalnum() for s in SKIPPED)
BASE = [
    "/usr/bin/sandbox-exec", "-p", PROFILE, "php", "-d", "memory_limit=1G", "-d", "error_reporting=24575",
    "/opt/homebrew/bin/wp", "--path=" + str(PRIVATE / "wordpress"), "--skip-plugins=" + ",".join(SKIPPED),
    "eval-file", str(ROOT / "tools/v2-runtime/gate4-fixture.php"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    run_id = str(time.time_ns())
    results: list[dict] = []
    sequence = 0
    audit_paths: dict[tuple[Path, str], Path] = {}
    receipts: list[dict] = []
    report = {
        "status": "INCOMPLETE",
        "authentication": "NOT_APPLICABLE",
        "run_id": run_id,
        "runtime_profile_sha256": digest(PRIVATE / "runtime-profile.json"),
        "runtime_qualification": RUNTIME["qualification"],
        "skipped_plugins": SKIPPED,
        "source_pins": {
            str(p.relative_to(ROOT)): digest(p) for p in [
                Path(__file__), ROOT / "tools/v2-runtime/gate4-fixture.php",
                ROOT / "tools/v2-runtime/variation-migration-core-next.php",
                ROOT / "tools/v2-runtime/variation-migration-core.php",
            ]
        },
        "cases": results,
        "receipts": receipts,
        "limits": [
            "Prospective pinned private fixture only; frozen core/CLI unchanged and unqualified for deferred shutdown fencing",
            "Query filter records pre-execution attempts; full raw/native after-exit readback is separate evidence",
            "Lost-fence failure snapshots are observations, not fenced afterimages",
            "Explicit fresh resume envelopes are simulated review inputs; historical orphan never adopted",
        ],
    }
    reports = EVIDENCE / "fence-runs"
    reports.mkdir(exist_ok=True)
    report_path = reports / (run_id + ".json")

    def save() -> None:
        report_path.write_text(json.dumps(report, indent=2) + "\n")

    save()
    mutation_lock = PRIVATE / ".sr-gate4-run-lock"
    mutation_lock.mkdir()

    def run(case: Path, mode: str, expected: int = 0, **extra: str) -> dict:
        nonlocal sequence
        sequence += 1
        receipt = EVIDENCE / f"{case.stem}-{sequence}-{mode}.txt"
        report["current_operation"] = {"case": case.name, "mode": mode, "receipt": receipt.name}
        save()
        try:
            process = subprocess.run(
                BASE + [mode], env={**os.environ, "SR_GATE4_CASE": str(case), "SR_GATE4_FENCED": "1", "SR_GATE4_INVOCATION": str(sequence), **extra},
                capture_output=True, text=True, timeout=60, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            partial = getattr(error, "stdout", "") or ""
            stderr = getattr(error, "stderr", "") or ""
            receipt.write_bytes((partial.encode() if isinstance(partial, str) else partial) + (stderr.encode() if isinstance(stderr, str) else stderr))
            receipts.append({"path": receipt.name, "sha256": digest(receipt), "bytes": receipt.stat().st_size, "exception": type(error).__name__})
            save()
            raise
        receipt.write_text(process.stdout + process.stderr)
        receipts.append({"path": receipt.name, "sha256": digest(receipt), "bytes": receipt.stat().st_size, "exit": process.returncode})
        audit_paths[(case, mode)] = Path(str(case) + f".audit-{mode}-{sequence}.jsonl")
        save()
        assert process.returncode == expected, (process.returncode, process.stdout, process.stderr)
        return json.loads(process.stdout)

    def fresh(label: str) -> Path:
        case = PRIVATE / f"case-{run_id}-{label}.json"
        run(case, "prepare")
        return case

    def inspect_after(case: Path, mode: str, returned: dict) -> dict:
        current = run(case, "inspect")
        before = json.loads(Path(str(case) + ".raw-return.json").read_text())
        after = json.loads(Path(str(case) + ".raw-inspect.json").read_text())
        assert before == after, "post-process scoped raw drift"
        if returned.get("ok"):
            assert returned["fenced_raw_sha256"] == current["raw_sha256"]
            assert not returned["lock_owned_after_return"]
            assert current["digest"] == current["recorded_after"]
            assert current["native_payment_blocked"] is False
        if current["state"] == "FAILED":
            assert current["native_payment_blocked"] is True
        audit = audit_paths[(case, mode)]
        assert audit.is_file() and audit.read_bytes().endswith(b"\n"), "missing/truncated audit"
        events = [json.loads(line) for line in audit.read_text().splitlines()]
        assert events[0]["event"] == "BEGIN" and events[-1]["event"] == "PROCESS_SHUTDOWN_END"
        assert events[-1]["native_deferred_callback_registered"] is False
        receipts.append({"path": str(audit.relative_to(ROOT)), "sha256": digest(audit), "bytes": audit.stat().st_size})
        tables = {"wp_posts", "wp_postmeta", "wp_wc_product_meta_lookup", "wp_terms", "wp_term_taxonomy", "wp_term_relationships"}
        assert not [e for e in events if e["event"] == "WRITE_ATTEMPT" and not e["lock_owned"] and (e["table"] in tables or e["migration_journal"])]
        return current

    try:
        case = fresh("apply")
        returned = run(case, "apply")
        current = inspect_after(case, "apply", returned)
        assert current["state"] == "COMPLETE"
        results.append({"case": "apply", "status": "PASS", "native": current, "fenced_raw": returned["fenced_raw_sha256"]})
        returned = run(case, "apply")
        inspect_after(case, "apply", returned)
        results.append({"case": "completed-retry", "status": "PASS"})

        for label in ["snapshot-read", "parent-drift"]:
            control = fresh(label)
            run(control, "apply")
            if label == "parent-drift":
                run(control, "control-parent-drift")
            returned = run(control, "apply", 3, SR_GATE4_SNAPSHOT_FAILURE="1" if label == "snapshot-read" else "0")
            guard = run(control, "inspect-guard")
            assert guard["state"] == "FAILED" and guard["quarantined"] and guard["native_payment_blocked"]
            run(control, "resume", 3)
            results.append({"case": label, "status": "PASS_QUARANTINED", "native": guard, "reason": returned["error"]})

        for label in ["completed-first-read", "completed-second-read", "missing-raw", "raw-drift", "old-complete", "release", "ownership"]:
            control = fresh(label)
            run(control, "apply", SR_GATE4_FENCED="0" if label == "old-complete" else "1")
            if label in ["missing-raw", "raw-drift"]:
                run(control, "control-" + label)
            extra = {}
            if label.startswith("completed-"):
                extra["SR_GATE4_RAW_READ_FAILURE"] = "1" if label == "completed-first-read" else "2"
            if label in ["release", "ownership"]:
                extra["SR_GATE4_RELEASE_FAILURE"] = label
            failure = run(control, "apply", 3, **extra)
            current = run(control, "inspect")
            expected_state = "COMPLETE" if label in ["old-complete", "release", "ownership"] else "FAILED"
            assert current["state"] == expected_state
            results.append({"case": label, "status": "PASS_REFUSED", "reason": failure["error"], "native_state": current["state"], "limit": "Release-ack failure denies successful execution receipt; pre-release verified data may remain COMPLETE" if label in ["release", "ownership"] else None})

        case = fresh("failure")
        returned = run(case, "apply", 3, SR_GATE4_FAIL_AFTER_CHILD="1")
        current = inspect_after(case, "apply", returned)
        assert current["state"] == "FAILED"
        results.append({"case": "after-child-failure", "status": "PASS_GUARD_RETAINED", "native": current})
        returned = run(case, "resume")
        current = inspect_after(case, "resume", returned)
        assert current["state"] == "COMPLETE"
        results.append({"case": "explicit-resume", "status": "PASS", "native": current})

        for stage in ["initial", "reentrant", "save", "legacy", "raw-read"]:
            for target in (["same"] if stage == "raw-read" else ["same", "foreign"]):
                case = fresh(stage + "-" + target)
                before = run(case, "inspect")
                returned = run(case, "apply", 3, SR_GATE4_QUEUE_STAGE=stage, SR_GATE4_QUEUE_TARGET=target, SR_GATE4_RAW_READ_FAILURE="1" if stage == "raw-read" else "0")
                current = inspect_after(case, "apply", returned)
                assert before["foreign_raw_sha256"] == current["foreign_raw_sha256"]
                assert current["state"] == (None if stage == "initial" else "FAILED")
                results.append({"case": stage + "-" + target, "status": "PASS_REFUSED", "reason": returned["error"], "foreign_unchanged": True})
                if stage != "initial":
                    returned = run(case, "resume")
                    current = inspect_after(case, "resume", returned)
                    assert current["state"] == "COMPLETE"
                    results.append({"case": "reviewed-resume-" + stage + "-" + target, "status": "PASS", "native": current})

        case = fresh("connection")
        with (EVIDENCE / f"held-{run_id}.txt").open("w") as log:
            child = subprocess.Popen(BASE + ["apply"], env={**os.environ, "SR_GATE4_CASE": str(case), "SR_GATE4_FENCED": "1", "SR_GATE4_HOLD_AFTER_CHILD": "1"}, stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 20
                while not Path(str(case) + ".hold").exists():
                    assert time.monotonic() < deadline
                    time.sleep(.05)
                returned = run(case, "apply", 3)
                assert "Another size-migration writer is active" in returned["error"]
                results.append({"case": "competing-writer", "status": "PASS_REFUSED"})
                held = json.loads(Path(str(case) + ".hold").read_text())
                subprocess.run(["/opt/homebrew/bin/mariadb", "--no-defaults", "--socket=/tmp/sr-gate4-01a0f768.sock", "-uroot", "-e", "KILL CONNECTION " + str(int(held["connection_id"]))], check=True)
                returned = run(case, "resume")
                stable = run(case, "inspect")
                assert stable["raw_sha256"] == returned["fenced_raw_sha256"]
                Path(str(case) + ".release").write_text("release")
                child.wait(timeout=15)
                assert child.returncode in [1, 3]
                assert run(case, "inspect")["raw_sha256"] == stable["raw_sha256"]
                results.append({"case": "connection-loss-stale-writer", "status": "PASS", "stale_exit": child.returncode, "native": stable})
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait()
        report["status"] = "PASS_PROSPECTIVE_FENCE_PRIVATE_FIXTURE"
    except BaseException as error:
        report["failure"] = {"type": type(error).__name__, "message": str(error)[:1000]}
        raise
    finally:
        save()
        (EVIDENCE / "fence-results.json").write_text(json.dumps(report, indent=2) + "\n")
        mutation_lock.rmdir()
    print(report["status"], len(results))


if __name__ == "__main__":
    main()
