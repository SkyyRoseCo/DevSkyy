"""Hermetic Git/filesystem boundary tests; no network or project bootstrap."""

import json
import os
import shlex
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts import repository_inventory as inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Inventory Fixture")
        self.git("config", "user.email", "inventory@example.invalid")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args])

    def file(self, name, text="fixture"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "-qm", "fixture")

    def report(self, **kwargs):
        return inventory.build_report(self.root, **kwargs)

    def test_inventory_preserves_git_and_filesystem_axes(self):
        self.file(".gitignore", "ignored/\n")
        self.file("source.py")
        self.file("empty.py", "")
        self.file("deleted.py")
        self.commit()
        (self.root / "deleted.py").unlink()
        self.file("untracked.py")
        self.file("ignored/cache.bin")
        entries = {e["path"]: e for e in self.report()["worktree"]}
        self.assertEqual(entries["deleted.py"]["status"], "missing")
        self.assertEqual(entries["empty.py"]["size_bytes"], 0)
        self.assertEqual(entries["untracked.py"]["git_category"], "untracked")
        self.assertEqual(entries["ignored/cache.bin"]["git_category"], "ignored")

    def test_sensitive_files_never_opened_or_exposed(self):
        for name in [
            ".env.example",
            "credentials.json",
            "keys/private.key",
            "frontend/.codex/config.toml",
            "source.py",
        ]:
            self.file(name, "PRIVATE_FIXTURE_VALUE")
        self.commit()
        real_read = inventory.read_regular

        def guarded(root, path, limit):
            self.assertFalse(inventory.sensitive(path), path)
            return real_read(root, path, limit)

        with patch.object(inventory, "read_regular", side_effect=guarded):
            report = self.report(hash_worktree=True, candidates=["source.py"])
        serialized = json.dumps(report)
        self.assertNotIn("PRIVATE_FIXTURE_VALUE", serialized)
        protected = [e for e in report["snapshot"]["entries"] if e["category"] == "sensitive"]
        self.assertEqual(len(protected), 4)
        self.assertTrue(all("git_oid" not in e for e in protected))

    def test_nul_safe_names_and_snapshot_duplicates(self):
        names = ["space file.py", "line\nfile.py", "tab\tfile.py", "--flag.py", "é.py"]
        for name in names:
            self.file(name, "identical")
        self.commit()
        report = self.report()
        self.assertEqual({e["path"] for e in report["snapshot"]["entries"]}, set(names))
        self.assertEqual(report["snapshot"]["duplicate_candidates"][0]["paths"], sorted(names))
        self.assertEqual(report["snapshot"]["repeated_logical_bytes"], 4 * len("identical"))

    def test_symlinks_never_followed_even_in_parent(self):
        self.file("parent/source.py")
        os.symlink("absent", self.root / "broken")
        os.symlink("cycle", self.root / "cycle")
        self.commit()
        (self.root / "parent/source.py").unlink()
        (self.root / "parent").rmdir()
        outside = Path(self.temp.name).parent / (self.root.name + "-outside")
        outside.mkdir()
        self.addCleanup(outside.rmdir)
        external = outside / "source.py"
        external.write_text("external")
        self.addCleanup(external.unlink)
        os.symlink(outside, self.root / "parent")
        report = self.report(hash_worktree=True)
        entries = {e["path"]: e for e in report["worktree"]}
        self.assertEqual(entries["broken"]["kind"], "symlink")
        self.assertEqual(entries["cycle"]["kind"], "symlink")
        self.assertEqual(entries["parent/source.py"]["status"], "inaccessible")
        with self.assertRaises(OSError):
            inventory.read_regular(self.root, "parent/source.py", 1024)

    def test_gitlinks_and_nested_repositories_are_not_traversed(self):
        self.file("source.py")
        self.commit()
        head = self.git("rev-parse", "HEAD").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", f"160000,{head},submodule")
        self.git("commit", "-qm", "gitlink")
        nested = self.root / "nested"
        nested.mkdir()
        subprocess.check_call(["git", "-C", str(nested), "init", "-q"])
        self.file("nested/private.py")
        report = self.report(hash_worktree=True)
        self.assertEqual(report["snapshot"]["gitlink_entries"], 1)
        entries = {e["path"]: e for e in report["worktree"]}
        self.assertEqual(entries["submodule"]["kind"], "gitlink")
        self.assertEqual(entries["nested"]["kind"], "directory")
        self.assertNotIn("nested/private.py", entries)

    def test_reference_graph_reports_locations_and_case_risks_without_snippets(self):
        self.file("assets/model.glb")
        self.file("Dockerfile", "COPY assets/model.glb /app/\n")
        self.file("docs/readme.md", "Example: ASSETS/MODEL.GLB\n")
        self.commit()
        report = self.report(candidates=["assets/model.glb"])
        graph = report["references"]
        self.assertEqual(len(graph["edges"]), 2)
        self.assertEqual(graph["edges"][0]["match"], "exact_literal")
        self.assertEqual(graph["edges"][1]["match"], "casefold_literal")
        self.assertEqual(graph["edges"][1]["layer"], "documentation")
        self.assertNotIn("COPY", json.dumps(graph))

    def test_budget_and_binary_coverage_are_explicit(self):
        self.file("a.py", "x" * 20)
        self.file("b.py", "x\0y")
        self.file("c.py", "target")
        self.commit()
        report = self.report(candidates=["c.py"], max_file_bytes=10, max_total_bytes=10)
        skipped = {e["path"]: e["reason"] for e in report["references"]["skipped"]}
        self.assertEqual(skipped["a.py"], "file_budget")
        self.assertEqual(skipped["b.py"], "binary")
        self.assertFalse(report["references"]["coverage_complete"])

    def test_permission_and_changed_file_fail_closed(self):
        self.file("a.py")
        self.commit()
        with patch.object(inventory, "read_regular", side_effect=PermissionError()):
            report = self.report(hash_worktree=True, candidates=["a.py"])
        self.assertEqual(report["worktree"][0]["analysis"], "unreadable_or_changed")
        self.assertFalse(report["references"]["coverage_complete"])
        with patch.object(inventory.os, "read", side_effect=[b"fixture", b""]):
            with patch.object(inventory, "signature", side_effect=[(1,), (2,)]):
                with self.assertRaises(OSError):
                    inventory.read_regular(self.root, "a.py", 100)

    def test_deterministic_report_and_metadata_only_default(self):
        self.file("a.py")
        self.commit()
        with patch.object(inventory, "read_regular", side_effect=AssertionError("must not read")):
            a = self.report()
            b = self.report()
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_invalid_candidates_and_snapshots_fail_closed(self):
        self.file("a.py")
        self.commit()
        for candidate in ["../escape", "/absolute", ".git/config", "missing", "a.py/.."]:
            with self.assertRaises(ValueError):
                self.report(candidates=[candidate])
        with self.assertRaises(subprocess.CalledProcessError):
            self.report(snapshot="--help")

    def test_collision_detection_independent_of_host_filesystem(self):
        collisions = inventory.collisions(["A.py", "a.py", "é.py", "e\u0301.py"])
        self.assertEqual(collisions["casefold"], [["A.py", "a.py"]])
        self.assertEqual(collisions["unicode_nfc"], [["e\u0301.py", "é.py"]])

    def test_cli_partial_result_is_successful_inventory_but_fails_strict_gate(self):
        self.file("a.py")
        self.file("binary.glb")
        self.commit()
        output = StringIO()
        with redirect_stdout(output):
            code = inventory.main(
                ["--root", str(self.root), "--candidate", "a.py", "--require-complete-references"]
            )
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(output.getvalue())["references"]["coverage_complete"])
        with redirect_stdout(StringIO()):
            self.assertEqual(inventory.main(["--root", str(self.root)]), 0)
        with redirect_stderr(StringIO()):
            self.assertEqual(inventory.main(["--root", str(self.root), "--candidate", "../x"]), 2)

    def test_symlink_substituted_before_content_access_is_rejected(self):
        path = self.file("a.py")
        self.commit()
        path.unlink()
        os.symlink(".git/config", path)
        with self.assertRaises(OSError):
            inventory.read_regular(self.root, "a.py", 1024)

    def test_hash_budget_and_ignored_content_policy(self):
        self.file(".gitignore", "ignored/\n")
        self.file("a.py", "duplicate")
        self.file("b.py", "duplicate")
        self.commit()
        self.file("ignored/a.py", "do not read")
        real_read = inventory.read_regular

        def guarded(root, path, limit):
            self.assertFalse(path.startswith("ignored/"))
            return real_read(root, path, limit)

        with patch.object(inventory, "read_regular", side_effect=guarded):
            report = self.report(hash_worktree=True, max_total_bytes=17)
        entries = {e["path"]: e for e in report["worktree"]}
        self.assertEqual(entries["b.py"]["analysis"], "total_budget")
        self.assertEqual(entries["ignored/a.py"]["analysis"], "metadata_only")
        self.assertLessEqual(report["hash_coverage"]["hash_bytes_attempted"], 17)

    def test_known_configuration_credential_stores_are_metadata_only(self):
        for name in [
            ".codex/config.toml",
            ".claude/settings.local.json",
            ".npmrc",
            ".netrc",
            ".mcp.json",
            "auth.json",
            "password-store/account.json",
            ".Codex/CONFIG.TOML",
            ".claude/Settings.Local.json",
            "frontend/.Codex/CONFIG.TOML",
            "frontend/.claude/Settings.Local.json",
            "plugins/tool/.claude/settings.json",
            "plugins/tool/.claude/settings.custom.json",
            "frontend/.codex/config.local.toml",
        ]:
            self.assertTrue(inventory.sensitive(name), name)

    def test_repository_root_with_trailing_whitespace(self):
        nested = self.root / "repo \n"
        nested.mkdir()
        self.root = nested
        self.git("init", "-q")
        self.git("config", "user.name", "Inventory Fixture")
        self.git("config", "user.email", "inventory@example.invalid")
        self.file("a.py")
        self.commit()
        self.assertEqual(self.report()["snapshot"]["blob_entries"], 1)

    def test_initialized_submodule_dirty_content_is_not_inspected(self):
        self.file("a.py")
        self.commit()
        self.git(
            "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(self.root), "module"
        )
        self.commit()
        self.file("module/untracked.py")
        self.assertTrue(self.git("status", "--porcelain"))
        report = self.report()
        self.assertIsNone(report["checkout"]["dirty"])
        self.assertFalse(report["checkout"]["index_changed_from_head"])
        self.assertNotIn("module/untracked.py", {e["path"] for e in report["worktree"]})

    def test_default_inventory_never_executes_clean_filters_on_sensitive_files(self):
        self.file(".env", "A" * 16)
        self.file(".gitattributes", ".env filter=probe\n")
        self.commit()
        marker = self.root / "filter-marker"
        self.git("config", "filter.probe.clean", "tee " + shlex.quote(str(marker)))
        path = self.file(".env", "B" * 16)
        info = path.stat()
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000_000))
        report = self.report()
        self.assertFalse(marker.exists())
        self.assertIsNone(report["checkout"]["dirty"])
        self.assertFalse(report["checkout"]["index_changed_from_head"])
        # Positive control proves this fixture detects ordinary Git status reads.
        self.git("status", "--porcelain")
        self.assertEqual(marker.read_text(), "B" * 16)

    def test_git_queries_disable_lazy_fetch_and_interactive_prompts(self):
        self.file("a.py")
        self.commit()
        original = inventory.subprocess.check_output

        def guarded(*args, **kwargs):
            self.assertEqual(kwargs["env"]["GIT_NO_LAZY_FETCH"], "1")
            self.assertEqual(kwargs["env"]["GIT_TERMINAL_PROMPT"], "0")
            return original(*args, **kwargs)

        with patch.object(inventory.subprocess, "check_output", side_effect=guarded):
            self.assertEqual(self.report()["snapshot"]["blob_entries"], 1)

    def test_index_changes_are_separate_from_selected_snapshot_and_working_contents(self):
        self.file("a.py", "first")
        self.commit()
        first = self.git("rev-parse", "HEAD").decode().strip()
        self.file("a.py", "second")
        self.git("add", "a.py")
        self.assertTrue(self.report()["checkout"]["index_changed_from_head"])
        self.commit()
        self.assertFalse(self.report(snapshot=first)["checkout"]["index_changed_from_head"])
        self.file("a.py", "third")
        report = self.report()
        self.assertFalse(report["checkout"]["index_changed_from_head"])
        self.assertIsNone(report["checkout"]["dirty"])


if __name__ == "__main__":
    unittest.main()
