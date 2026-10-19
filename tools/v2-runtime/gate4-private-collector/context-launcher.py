#!/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I
"""No-fork pre-exec ownership barrier for the synthetic public-API probe."""

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time

CHROME = Path(
    "/Users/theceo/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell"
)
CHROME_SHA = "a0bfe7b4da4787b66058477d696cd1d09065d25f06a548947722b9af77ee8282"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate ownership field")
        result[key] = value
    return result


def read_regular(path, limit):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_uid != os.geteuid()
            or before.st_size > limit
        ):
            raise ValueError("Invalid ownership record file")
        raw = os.read(descriptor, limit + 1)
        after = os.fstat(descriptor)
        current = path.lstat()

        def identity(value):
            return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns

        if (
            identity(before) != identity(after)
            or identity(current) != identity(before)
            or not stat.S_ISREG(current.st_mode)
            or len(raw) != before.st_size
        ):
            raise ValueError("Ownership record changed during read")
        return raw
    finally:
        os.close(descriptor)


def run(target, expected_sha, folder, nonce, args, deadline=10):
    """Tests pass a harmless pinned target; production main pins Chromium only."""
    if not re.fullmatch(r"[0-9a-f-]{36}", nonce):
        raise ValueError("Invalid ownership nonce")
    if (
        folder.is_symlink()
        or folder.resolve() != folder
        or stat.S_IMODE(folder.stat().st_mode) != 0o700
    ):
        raise ValueError("Nonprivate ownership directory")
    if target.is_symlink() or not target.is_file() or digest(target) != expected_sha:
        raise ValueError("Executable identity mismatch")
    if os.getpid() != os.getpgrp():
        raise ValueError("Broker must lead a separate process group")
    profiles = [
        arg.removeprefix("--user-data-dir=") for arg in args if arg.startswith("--user-data-dir=")
    ]
    if len(profiles) != 1 or "--remote-debugging-pipe" not in args:
        raise ValueError("Unexpected launch arguments")
    profile = Path(profiles[0])
    if (
        profile.is_symlink()
        or profile.resolve() != profile
        or not profile.is_relative_to(folder / "tmp")
        or not profile.is_dir()
    ):
        raise ValueError("Profile outside owned private root")
    pipes = {}
    for descriptor in (3, 4):
        value = os.fstat(descriptor)
        if not (stat.S_ISFIFO(value.st_mode) or stat.S_ISSOCK(value.st_mode)):
            raise ValueError("Invalid CDP pipe descriptor")
        os.set_inheritable(descriptor, True)
        pipes[str(descriptor)] = {
            "device": str(value.st_dev),
            "inode": str(value.st_ino),
            "type": stat.S_IFMT(value.st_mode),
            "inheritable": os.get_inheritable(descriptor),
        }
    record = {
        "kind": "pre-exec-registration",
        "nonce": nonce,
        "pid": os.getpid(),
        "group": os.getpgrp(),
        "parent": os.getppid(),
        "target": str(target),
        "target_sha256": expected_sha,
        "launcher_sha256": digest(Path(__file__).resolve()),
        "profile": str(profile),
        "args": args,
        "pipes": pipes,
        "environment_sha256": hashlib.sha256(
            json.dumps(dict(os.environ), sort_keys=True).encode()
        ).hexdigest(),
    }
    pending = folder / "broker-registration.partial"
    registered = folder / "broker-registration.json"
    ack = folder / "broker-ack.json"
    # Preexisting ACKs are never authority for a new target execution.
    if ack.exists() or registered.exists():
        raise ValueError("Stale ownership state")
    serialized = (json.dumps(record) + "\n").encode()
    if len(serialized) > 65536:
        raise ValueError("Ownership registration exceeds bound")
    registration_sha = hashlib.sha256(serialized).hexdigest()
    with pending.open("xb") as stream:
        os.chmod(pending, 0o600)
        stream.write(serialized)
        stream.flush()
        os.fsync(stream.fileno())
    os.link(pending, registered)
    pending.unlink()
    end = time.monotonic() + deadline
    while time.monotonic() < end:
        if ack.exists():
            raw = read_regular(ack, 4096)
            if read_regular(registered, 65536) != serialized:
                raise ValueError("Ownership registration changed after publication")
            if len(raw) > 4096 or not raw.endswith(b"\n"):
                raise ValueError("Incomplete ownership acknowledgement")
            value = json.loads(raw, object_pairs_hook=object_pairs)
            if value != {
                "kind": "pre-exec-ack",
                "nonce": nonce,
                "pid": record["pid"],
                "group": record["group"],
                "registration_sha256": registration_sha,
            }:
                raise ValueError("Ownership acknowledgement mismatch")
            if digest(target) != expected_sha:
                raise ValueError("Executable changed before exec")
            os.execv(str(target), [str(target), *args])
            raise RuntimeError("exec returned")
        time.sleep(0.02)
    raise TimeoutError("Pre-exec ownership acknowledgement deadline")


def main():
    root = Path(__file__).resolve().parents[3]
    folder = Path(os.environ["SR_CONTEXT_FOLDER"])
    if (
        folder.parent != root / ".artifacts/release-gates-20261019/gate4-private-collector-context"
        or not re.fullmatch(r"probe-[0-9]{13}", folder.name)
    ):
        raise ValueError("Unexpected probe directory")
    run(CHROME, CHROME_SHA, folder, os.environ["SR_CONTEXT_NONCE"], sys.argv[1:])


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # No arguments, environment values or raw protocol material reach stderr.
        print(
            json.dumps({"status": "FAIL_PRE_EXEC_BROKER", "error_type": type(error).__name__}),
            file=sys.stderr,
        )
        sys.exit(71)
