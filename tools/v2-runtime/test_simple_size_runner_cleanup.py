"""Bounded real harmless-command control; no DB, PHP server or browser."""

import importlib.util
from pathlib import Path
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    "size_runner", Path(__file__).with_name("run_simple_size_native.py")
)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ClosedGroupRetirement(unittest.TestCase):
    def test_finalization_never_signals_a_retired_command(self):
        runner.PRIVATE = (
            runner.ROOT
            / ".artifacts/release-gates-20261019/simple-size-runner-controls"
            / ("run-" + runner.RUN)
        )
        runner.guard(runner.PRIVATE)
        runner.PRIVATE.mkdir(parents=True, mode=0o700)
        runner.TASK_ENV = {"PATH": "/usr/bin:/bin"}
        with mock.patch.object(runner.subprocess, "Popen", wraps=runner.subprocess.Popen) as launch:
            runner.command(["/usr/bin/true"])
        child = launch.return_value
        # The actual receipt, not the mock wrapper, binds the observed command PID.
        import json

        receipt = json.loads((runner.PRIVATE / "command-0001.json").read_text())
        self.assertEqual(receipt["exit"], 0)
        self.assertTrue(receipt["group_retired"])
        self.assertEqual(runner.COMMAND_CHILDREN, [])
        with mock.patch.object(
            runner.os, "killpg", side_effect=AssertionError("retired PID must not be signalled")
        ) as signal:
            self.assertEqual(runner.cleanup_owned(), [])
            signal.assert_not_called()
            # Modified-registry negative control: the former bug attempts a signal.
            child.pid = receipt["pid"]
            runner.COMMAND_CHILDREN.append(child)
            refused = runner.cleanup_owned()
            self.assertEqual(refused[0]["error"], "AssertionError")
            signal.assert_called_once()
            runner.COMMAND_CHILDREN.remove(child)
        runner.write(
            runner.PRIVATE / "control.json",
            {
                "status": "PASS_REAL_COMMAND_RETIRED_AND_MODIFIED_REGISTRY_DETECTED",
                "authentication": "NOT_APPLICABLE_OFFLINE",
                "runner": runner.pin(Path(runner.__file__)),
                "test": runner.pin(Path(__file__)),
                "command": receipt,
                "modified_registry_control": "MOCK_SIGNAL_ONLY_NO_HISTORICAL_PID_SIGNALLED",
            },
        )


if __name__ == "__main__":
    unittest.main()
