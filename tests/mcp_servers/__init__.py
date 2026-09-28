"""Package marker.

Without it, pytest imports this directory's conftest.py under the plain
module name "conftest", which replaces the ROOT conftest.py in sys.modules.
tests/test_bug263_fork_safety.py does `import conftest` to read the darwin
fork-safety guard's pre-spawned tracker pid, and got this package's conftest
instead — the guard looked removed. tests/ and tests/integrations/ carry the
same marker for the same reason.
"""
