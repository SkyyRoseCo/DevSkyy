"""CLI entry point — `python -m scripts.pr_automator`."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

from scripts.pr_automator.core import (
    GhClient,
    GhError,
    GitError,
    RiskPaths,
    State,
)
from scripts.pr_automator.core import git_run as _git
from scripts.pr_automator.core import (
    setup_logging,
)
from scripts.pr_automator.gates import run_gates
from scripts.pr_automator.merge_gate import (
    MAX_CYCLES_PER_SHA,
    NEEDS_HUMAN_LABEL,
    OPT_IN_LABEL,
    evaluate,
    package_root,
)
from scripts.pr_automator.reviewer import ReviewerAgent, ReviewVerdict, fetch_diff

logger = logging.getLogger("pr_automator.cli")

PR_VIEW_FIELDS = [
    "number",
    "headRefName",
    "headRefOid",
    "baseRefName",
    "isDraft",
    "author",
    "labels",
    "mergeable",
    "mergeStateStatus",
    "reviews",
]


def _cleanup_worktree(repo_root: Path, pr_number: int) -> None:
    """Remove the per-PR worktree + tracking branch. Called after a successful
    merge so worktrees don't accumulate forever (disk-fill DoS)."""
    target = repo_root / f".claude/worktrees/pr-auto-{pr_number}"
    branch = f"pr-auto-{pr_number}"
    if target.exists():
        try:
            _git(repo_root, "worktree", "remove", "--force", str(target), check=False)
        except Exception as e:  # noqa: BLE001 - best-effort cleanup
            logger.warning("worktree remove failed for #%s: %s", pr_number, e)
    try:
        _git(repo_root, "branch", "-D", branch, check=False)
    except Exception as e:  # noqa: BLE001 - best-effort cleanup
        logger.warning("branch delete failed for %s: %s", branch, e)


def prepare_worktree(repo_root: Path, pr_number: int, head_ref: str, head_sha: str) -> Path:
    """Create or update a worktree at .claude/worktrees/pr-auto-<N> on the PR head SHA.

    Uses ``+pull/{N}/head`` (force-update refspec) so a PR's force-push
    doesn't make the fetch fail silently and leave the worktree on a stale
    SHA. Also fetches ``origin/main`` so the local diff fallback can find a
    merge-base.
    """
    target = repo_root / f".claude/worktrees/pr-auto-{pr_number}"
    branch = f"pr-auto-{pr_number}"
    if not target.exists():
        _git(repo_root, "fetch", "origin", f"+pull/{pr_number}/head:{branch}")
        _git(repo_root, "worktree", "add", str(target), branch)
    _git(target, "fetch", "origin", f"+pull/{pr_number}/head", check=False)
    _git(target, "fetch", "origin", "main", check=False)
    _git(target, "checkout", head_sha)
    return target


# ---------------------------------------------------------------------------
# Cycle helpers — run_cycle is now a thin orchestrator over these.
# ---------------------------------------------------------------------------


def _try_label(gh: GhClient, pr_number: int, label: str, dry_run: bool) -> None:
    """Best-effort label add; logs a warning if it fails."""
    if dry_run:
        return
    try:
        gh.pr_label_add(pr_number, label)
    except GhError as e:
        logger.warning("could not add `%s` label to #%s: %s", label, pr_number, e)


def _check_opt_in(labels: set[str], pr_number: int, force: bool) -> bool:
    """Return True if cycle should proceed, False to skip."""
    if OPT_IN_LABEL in labels:
        return True
    if not force:
        logger.info(
            "PR #%s missing `%s` label — skipping (add it with `gh pr edit %s --add-label %s`, or pass --force)",
            pr_number,
            OPT_IN_LABEL,
            pr_number,
            OPT_IN_LABEL,
        )
        return False
    logger.warning("--force: bypassing opt-in label check on PR #%s", pr_number)
    return True


def _get_changed_files(
    gh: GhClient,
    worktree: Path,
    pr_number: int,
    base_ref: str,
) -> list[str] | None:
    """Get the PR's changed-file list. ``None`` signals fatal failure."""
    try:
        return gh.pr_changed_files(pr_number)
    except GhError as e:
        logger.warning(
            "gh pr diff (--name-only) failed (%s) — falling back to local git diff",
            str(e).splitlines()[0][:200],
        )
    try:
        mb = _git(worktree, "merge-base", base_ref, "HEAD")
        out = _git(worktree, "diff", "--name-only", f"{mb}..HEAD")
        return [line.strip() for line in out.splitlines() if line.strip()]
    except GitError as ge:
        # git_run raises GitError for both non-zero exit and timeout, so one
        # catch is sufficient here — a hung git fetch/diff returns a clean
        # failure instead of crashing the cycle with an uncaught traceback.
        logger.error("local git diff fallback failed: %s", ge)
        return None


def _get_review(
    skip_review: bool, worktree: Path, pr_number: int, base_ref: str
) -> ReviewVerdict | None:
    """Get the reviewer-agent verdict. ``None`` signals fatal failure."""
    if skip_review:
        return ReviewVerdict(
            verdict="DEFER_HUMAN",
            confidence=0,
            scope_assessment="(reviewer skipped)",
            risk_assessment="unknown",
            defer_reasons=["--skip-review flag set"],
        )
    diff_text = fetch_diff(worktree, pr_number, base_ref=base_ref)
    try:
        return ReviewerAgent().review(pr_number, diff_text)
    except Exception as e:  # pragma: no cover - subprocess failures
        logger.error("reviewer agent failed: %s", e)
        return None


def _post_review(gh: GhClient, review: ReviewVerdict, gates_pass: bool, pr_number: int) -> None:
    decision_flag = (
        "APPROVE"
        if review.is_approve and gates_pass
        else ("COMMENT" if review.is_defer else "REQUEST_CHANGES")
    )
    try:
        gh.pr_review(pr_number, decision_flag, review.to_yaml_body())
    except GhError as e:
        logger.warning("could not post review: %s", e)


def _do_merge(gh: GhClient, repo_root: Path, pr_number: int, admin: bool, dry_run: bool) -> int:
    """Execute the squash merge and clean up. Returns 0 on success, 3 on failure."""
    logger.info(
        "PR #%s — predicate green, merging (squash%s)",
        pr_number,
        " --admin" if admin else "",
    )
    if dry_run:
        return 0
    try:
        gh.pr_merge(pr_number, method="squash", admin=admin)
        logger.info("MERGED #%s", pr_number)
        _cleanup_worktree(repo_root, pr_number)
        return 0
    except GhError as e:
        logger.error("merge failed: %s", e)
        return 3


def run_cycle(
    pr_number: int,
    repo_root: Path,
    *,
    dry_run: bool = False,
    skip_review: bool = False,
    force: bool = False,
    admin: bool = False,
) -> int:
    """One full cycle on a single PR. Returns exit code (0=ok, 2=blocked, 3=error)."""
    gh = GhClient(dry_run=dry_run)
    state = State.load()

    if state.paused:
        logger.warning("automator paused (global). Use --resume to clear.")
        return 2

    try:
        pr = gh.pr_view(pr_number, fields=PR_VIEW_FIELDS)
    except GhError as e:
        logger.error("gh pr view failed for #%s: %s", pr_number, e)
        return 3

    head_sha = pr["headRefOid"]
    head_ref = pr["headRefName"]
    labels = {lbl["name"] for lbl in pr.get("labels", [])}

    if not _check_opt_in(labels, pr_number, force):
        return 2

    pr_state = state.for_pr(pr_number)
    if pr_state.last_sha == head_sha and pr_state.cycle_count >= MAX_CYCLES_PER_SHA:
        logger.warning(
            "PR #%s hit cycle cap (%d) on SHA %s — labeling needs-human",
            pr_number,
            MAX_CYCLES_PER_SHA,
            head_sha[:8],
        )
        _try_label(gh, pr_number, NEEDS_HUMAN_LABEL, dry_run)
        return 2

    logger.info(
        "PR #%s — head=%s ref=%s cycle=%d",
        pr_number,
        head_sha[:8],
        head_ref,
        pr_state.cycle_count + 1,
    )

    worktree = prepare_worktree(repo_root, pr_number, head_ref, head_sha)
    base_ref = f"origin/{pr.get('baseRefName', 'main')}"

    changed = _get_changed_files(gh, worktree, pr_number, base_ref)
    if changed is None:
        return 3
    logger.info("changed files: %d", len(changed))

    # Auto-fix push was removed in 8b98db990: it bypassed the entire
    # 10-check predicate. The reviewer now flags lint/format issues as
    # REQUEST_CHANGES findings instead.
    gates = run_gates(worktree, changed)
    logger.info("gates:\n%s", gates.render())

    review = _get_review(skip_review, worktree, pr_number, base_ref)
    if review is None:
        return 3
    logger.info("reviewer verdict: %s (confidence %d)", review.verdict, review.confidence)

    if not skip_review and not dry_run:
        _post_review(gh, review, gates.all_pass, pr_number)

    risk_paths = RiskPaths.load(package_root() / "RISK_PATHS.txt")
    decision = evaluate(
        pr_number=pr_number,
        pr_view=pr,
        gates=gates,
        review=review,
        risk_paths=risk_paths,
        changed_files=changed,
        state=state,
        head_sha=head_sha,
    )
    logger.info("\n%s", decision.render())

    state.record_cycle(
        pr_number,
        head_sha,
        review.verdict,
        green=gates.all_pass,
        blocked=None if decision.can_merge else "predicate_fail",
    )

    if decision.can_merge:
        return _do_merge(gh, repo_root, pr_number, admin, dry_run)

    if review.is_defer:
        _try_label(gh, pr_number, NEEDS_HUMAN_LABEL, dry_run)
    return 2


def gc_worktrees(repo_root: Path, open_pr_numbers: set[int]) -> int:
    """Remove cached per-PR worktrees for PRs that are no longer open.

    A PR-closed-without-merge case (or a long-stale PR that's been
    superseded) leaves a `pr-auto-{N}` worktree on disk that the merge
    cleanup never reaches. This GC pass — called once per ``watch_loop``
    iteration — reclaims those. Open PRs are always preserved; the GC is
    intentionally conservative.

    Returns the number of worktrees removed.
    """
    base = repo_root / ".claude/worktrees"
    if not base.exists():
        return 0
    removed = 0
    for child in base.iterdir():
        name = child.name
        if not name.startswith("pr-auto-"):
            continue
        try:
            pr_n = int(name.removeprefix("pr-auto-"))
        except ValueError:
            continue
        if pr_n in open_pr_numbers:
            continue
        logger.info("gc: PR #%s no longer open — removing worktree", pr_n)
        _cleanup_worktree(repo_root, pr_n)
        removed += 1
    return removed


def watch_loop(repo_root: Path, *, interval: int, dry_run: bool, admin: bool) -> int:
    """Poll open PRs forever, run a cycle on each that has the opt-in label."""
    gh = GhClient(dry_run=dry_run)
    logger.info("watch mode — polling every %ds (Ctrl+C to stop)", interval)
    while True:
        try:
            prs = gh.pr_list_open()
        except GhError as e:
            logger.error("gh pr list failed: %s — sleeping", e)
            time.sleep(interval)
            continue

        # Reap worktrees for PRs that are no longer open.
        gc_worktrees(repo_root, {int(p["number"]) for p in prs})

        for pr in prs:
            labels = {lbl["name"] for lbl in pr.get("labels", [])}
            if OPT_IN_LABEL not in labels or pr.get("isDraft"):
                continue
            try:
                run_cycle(pr["number"], repo_root, dry_run=dry_run, admin=admin)
            except KeyboardInterrupt:
                raise
            except Exception as e:  # pragma: no cover
                logger.exception("cycle on #%s crashed: %s", pr["number"], e)

        time.sleep(interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pr_automator")
    parser.add_argument("--watch", action="store_true", help="daemon mode — poll PRs forever")
    parser.add_argument("--once", action="store_true", help="run one cycle on a single PR")
    parser.add_argument("--pr", type=int, help="PR number (required with --once)")
    parser.add_argument("--dry-run", action="store_true", help="never call mutating gh commands")
    parser.add_argument(
        "--skip-review", action="store_true", help="skip the Claude reviewer agent (smoke testing)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="bypass the opt-in label check (one-off manual cycle on a specific PR)",
    )
    parser.add_argument(
        "--admin",
        action="store_true",
        help="merge with `gh pr merge --admin` (bypasses branch protection — opt-in only)",
    )
    parser.add_argument("--pause", action="store_true", help="set global pause flag")
    parser.add_argument("--resume", action="store_true", help="clear global pause flag")
    parser.add_argument("--status", action="store_true", help="print current state JSON")
    parser.add_argument("--interval", type=int, default=60, help="watch poll interval (seconds)")
    parser.add_argument(
        "--repo-root", type=Path, default=None, help="repo root (default: detect via git rev-parse)"
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose)

    if args.pause:
        s = State.load()
        s.paused = True
        s.save()
        print("automator: PAUSED")
        return 0
    if args.resume:
        s = State.load()
        s.paused = False
        s.save()
        print("automator: RESUMED")
        return 0
    if args.status:
        s = State.load()
        import json as _json

        print(
            _json.dumps(
                {
                    "paused": s.paused,
                    "prs": {k: v.__dict__ for k, v in s.prs.items()},
                },
                indent=2,
            )
        )
        return 0

    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        try:
            out = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            repo_root = Path(out)
        except subprocess.CalledProcessError:
            print("error: not in a git repo (use --repo-root)", file=sys.stderr)
            return 3

    if args.watch:
        return watch_loop(
            repo_root,
            interval=args.interval,
            dry_run=args.dry_run,
            admin=args.admin,
        )

    if args.once:
        if not args.pr:
            print("error: --once requires --pr <N>", file=sys.stderr)
            return 3
        return run_cycle(
            args.pr,
            repo_root,
            dry_run=args.dry_run,
            skip_review=args.skip_review,
            force=args.force,
            admin=args.admin,
        )

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
