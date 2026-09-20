"""Tests for mcp_servers.worktree_fleet.git_ops — real tmp git repos, no mocks.

bug-231: everything under tmp_path, never a real repo. This module shells out
to git directly, so faking it with mocks would just test the mock.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from mcp_servers.worktree_fleet.git_ops import (
    PushState,
    _commit_subjects,
    add_worktree,
    is_dirty,
    push_status,
    remove_worktree,
)


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A bare 'origin' + a cloned 'main' worktree with one commit, pushed."""
    origin = tmp_path / "origin.git"
    main = tmp_path / "main"
    _git(["init", "--bare", "--initial-branch=main", str(origin)], cwd=tmp_path)
    _git(["clone", str(origin), str(main)], cwd=tmp_path)
    _git(["config", "user.email", "test@example.com"], cwd=main)
    _git(["config", "user.name", "Test"], cwd=main)
    (main / "README.md").write_text("hello\n")
    _git(["add", "README.md"], cwd=main)
    _git(["commit", "-m", "initial"], cwd=main)
    _git(["push", "origin", "main"], cwd=main)
    return main


class TestAddWorktree:
    def test_creates_new_branch_worktree(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-feature"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="feature-a", base_ref="main")
        assert (wt_path / "README.md").exists()
        assert _git(["branch", "--show-current"], cwd=wt_path).stdout.strip() == "feature-a"

    def test_adopts_existing_local_branch_with_no_dash_b(self, repo: Path, tmp_path: Path) -> None:
        _git(["branch", "existing-branch"], cwd=repo)
        wt_path = tmp_path / "wt-adopt"
        add_worktree(
            repo_root=repo, worktree_path=wt_path, branch="existing-branch", base_ref="main"
        )
        assert _git(["branch", "--show-current"], cwd=wt_path).stdout.strip() == "existing-branch"


class TestIsDirty:
    def test_clean_worktree_is_not_dirty(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-clean"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="clean-branch", base_ref="main")
        assert is_dirty(wt_path) is False

    def test_untracked_file_makes_it_dirty(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-dirty"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="dirty-branch", base_ref="main")
        (wt_path / "new.txt").write_text("x")
        assert is_dirty(wt_path) is True


class TestPushStatus:
    def test_no_new_commits_is_safe_even_with_no_upstream(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-nonew"
        add_worktree(
            repo_root=repo, worktree_path=wt_path, branch="no-new-commits", base_ref="main"
        )
        status = push_status(wt_path, branch="no-new-commits", base_ref="main")
        assert status.state == PushState.NO_NEW_COMMITS

    def test_never_pushed_with_commits_is_a_distinct_state_not_an_error(
        self, repo: Path, tmp_path: Path
    ) -> None:
        """The advisor-flagged case: a freshly claimed branch has no upstream at
        all (`git log @{u}..` would raise, not return empty) — this must be
        classified, not crash.
        """
        wt_path = tmp_path / "wt-neverpushed"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="never-pushed", base_ref="main")
        (wt_path / "new.py").write_text("x = 1\n")
        _git(["add", "new.py"], cwd=wt_path)
        _git(["commit", "-m", "local only"], cwd=wt_path)

        status = push_status(wt_path, branch="never-pushed", base_ref="main")
        assert status.state == PushState.NEVER_PUSHED
        assert "local only" in " ".join(status.unpushed_commits)

    def test_pushed_with_upstream_configured_is_up_to_date(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = tmp_path / "wt-pushed"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="pushed-branch", base_ref="main")
        (wt_path / "new.py").write_text("x = 1\n")
        _git(["add", "new.py"], cwd=wt_path)
        _git(["commit", "-m", "pushed commit"], cwd=wt_path)
        _git(["push", "-u", "origin", "pushed-branch"], cwd=wt_path)

        status = push_status(wt_path, branch="pushed-branch", base_ref="main")
        assert status.state == PushState.UP_TO_DATE

    def test_upstream_configured_but_local_commit_ahead_is_unpushed(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = tmp_path / "wt-ahead"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="ahead-branch", base_ref="main")
        (wt_path / "a.py").write_text("1\n")
        _git(["add", "a.py"], cwd=wt_path)
        _git(["commit", "-m", "first"], cwd=wt_path)
        _git(["push", "-u", "origin", "ahead-branch"], cwd=wt_path)

        (wt_path / "b.py").write_text("2\n")
        _git(["add", "b.py"], cwd=wt_path)
        _git(["commit", "-m", "second, unpushed"], cwd=wt_path)

        status = push_status(wt_path, branch="ahead-branch", base_ref="main")
        assert status.state == PushState.UNPUSHED
        assert "second, unpushed" in " ".join(status.unpushed_commits)


class TestRemoveWorktree:
    def test_removes_a_clean_worktree(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-remove"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="remove-branch", base_ref="main")
        remove_worktree(repo_root=repo, worktree_path=wt_path)
        assert not wt_path.exists()

    def test_refuses_to_remove_dirty_worktree_without_force(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = tmp_path / "wt-remove-dirty"
        add_worktree(
            repo_root=repo, worktree_path=wt_path, branch="remove-dirty-branch", base_ref="main"
        )
        (wt_path / "new.txt").write_text("x")
        with pytest.raises(subprocess.CalledProcessError):
            remove_worktree(repo_root=repo, worktree_path=wt_path, force=False)
        assert wt_path.exists()


class TestOptionInjection:
    """Caller-supplied refs and paths must never reach git as options.

    Reproduced before the fix: base_ref="--force" was accepted and the worktree
    was created with --force in effect.
    """

    @pytest.mark.parametrize("base_ref", ["--force", "-f", "--detach", "--lock"])
    def test_option_like_base_ref_is_rejected_before_git_runs(
        self, repo: Path, tmp_path: Path, base_ref: str
    ) -> None:
        wt_path = tmp_path / "wt-inject"
        with pytest.raises(ValueError, match="base_ref"):
            add_worktree(repo_root=repo, worktree_path=wt_path, branch="feat-x", base_ref=base_ref)
        assert not wt_path.exists()
        assert "feat-x" not in _git(["branch", "--list"], cwd=repo).stdout

    @pytest.mark.parametrize("branch", ["--detach", "-b", "--orphan"])
    def test_option_like_branch_is_rejected(self, repo: Path, tmp_path: Path, branch: str) -> None:
        wt_path = tmp_path / "wt-inject"
        with pytest.raises(ValueError, match="branch"):
            add_worktree(repo_root=repo, worktree_path=wt_path, branch=branch, base_ref="main")
        assert not wt_path.exists()

    def test_option_like_worktree_path_is_rejected(self, repo: Path) -> None:
        with pytest.raises(ValueError, match="worktree_path"):
            add_worktree(
                repo_root=repo, worktree_path=Path("--force"), branch="feat-y", base_ref="main"
            )
        with pytest.raises(ValueError, match="worktree_path"):
            remove_worktree(repo_root=repo, worktree_path=Path("--force"))

    def test_push_status_rejects_option_like_refs(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-ps"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="feat-ps", base_ref="main")
        with pytest.raises(ValueError, match="base_ref"):
            push_status(wt_path, branch="feat-ps", base_ref="--all")
        with pytest.raises(ValueError, match="branch"):
            push_status(wt_path, branch="--all", base_ref="main")

    def test_dashes_inside_a_name_are_still_fine(self, repo: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-ok"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="feat/a-b--c", base_ref="main")
        assert _git(["branch", "--show-current"], cwd=wt_path).stdout.strip() == "feat/a-b--c"


class TestUnresolvableBaseRef:
    """A base_ref git cannot resolve must never read as "nothing to report".

    Reproduced before the fix: `git log mian..HEAD` exits non-zero,
    _commit_subjects swallowed it and returned [], and push_status answered
    NO_NEW_COMMITS for a worktree whose only commit exists on no remote — so
    release() waved it through. "Couldn't check" now has its own state.
    """

    def _worktree_with_one_local_commit(self, repo: Path, tmp_path: Path, name: str) -> Path:
        wt_path = tmp_path / f"wt-{name}"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch=name, base_ref="main")
        (wt_path / "new.py").write_text("x = 1\n")
        _git(["add", "new.py"], cwd=wt_path)
        _git(["commit", "-m", "local only"], cwd=wt_path)
        return wt_path

    def test_unresolvable_base_ref_is_unknown_not_no_new_commits(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = self._worktree_with_one_local_commit(repo, tmp_path, "typo-base")
        status = push_status(wt_path, branch="typo-base", base_ref="mian")
        assert status.state is PushState.UNKNOWN
        assert "mian" in status.reason

    def test_unresolvable_base_ref_is_unknown_even_when_nothing_was_committed(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = tmp_path / "wt-empty-typo"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="empty-typo", base_ref="main")
        status = push_status(wt_path, branch="empty-typo", base_ref="mian")
        assert status.state is PushState.UNKNOWN

    def test_resolvable_base_ref_still_classifies_normally(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = self._worktree_with_one_local_commit(repo, tmp_path, "good-base")
        assert push_status(wt_path, branch="good-base", base_ref="main").state is (
            PushState.NEVER_PUSHED
        )

    def test_commit_subjects_raises_rather_than_returning_empty(
        self, repo: Path, tmp_path: Path
    ) -> None:
        wt_path = tmp_path / "wt-subjects"
        add_worktree(repo_root=repo, worktree_path=wt_path, branch="subjects", base_ref="main")
        with pytest.raises(ValueError, match="nope"):
            _commit_subjects(wt_path, "nope..HEAD")


class TestBranchMustBeALocalBranch:
    """`git rev-parse --verify <name>` is a REVISION check, not a branch check.

    A tag, SHA, HEAD or remote-tracking name passed as `branch` made
    `git worktree add <path> <name>` produce a DETACHED worktree; its commits
    then belonged to no branch, and removing it orphaned them (reachable only
    via reflog). Adoption now requires refs/heads/<branch>.
    """

    @pytest.fixture
    def tagged(self, repo: Path) -> Path:
        _git(["tag", "v1.0"], cwd=repo)
        return repo

    def test_tag_name_is_refused_instead_of_detaching(self, tagged: Path, tmp_path: Path) -> None:
        wt_path = tmp_path / "wt-tag"
        with pytest.raises(ValueError, match="not a local branch"):
            add_worktree(repo_root=tagged, worktree_path=wt_path, branch="v1.0", base_ref="main")
        assert not wt_path.exists()

    def test_commit_sha_is_refused(self, repo: Path, tmp_path: Path) -> None:
        sha = _git(["rev-parse", "HEAD"], cwd=repo).stdout.strip()
        with pytest.raises(ValueError, match="not a local branch"):
            add_worktree(
                repo_root=repo, worktree_path=tmp_path / "wt-sha", branch=sha, base_ref="main"
            )

    def test_head_is_refused(self, repo: Path, tmp_path: Path) -> None:
        # git check-ref-format rejects HEAD as a branch name outright, so this
        # one is refused a step earlier than the tag/SHA cases.
        wt_path = tmp_path / "wt-head"
        with pytest.raises(ValueError, match="'HEAD'"):
            add_worktree(repo_root=repo, worktree_path=wt_path, branch="HEAD", base_ref="main")
        assert not wt_path.exists()

    def test_remote_tracking_name_is_refused(self, repo: Path, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not a local branch"):
            add_worktree(
                repo_root=repo,
                worktree_path=tmp_path / "wt-remote",
                branch="origin/main",
                base_ref="main",
            )

    def test_syntactically_invalid_branch_name_is_refused(self, repo: Path, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not a valid branch name"):
            add_worktree(
                repo_root=repo,
                worktree_path=tmp_path / "wt-bad",
                branch="bad..name",
                base_ref="main",
            )

    def test_every_created_worktree_has_a_branch_of_its_own(
        self, tagged: Path, tmp_path: Path
    ) -> None:
        """The property the two refusals exist to protect."""
        wt_path = tmp_path / "wt-attached"
        add_worktree(repo_root=tagged, worktree_path=wt_path, branch="attached", base_ref="main")
        assert _git(["symbolic-ref", "HEAD"], cwd=wt_path).stdout.strip() == "refs/heads/attached"
