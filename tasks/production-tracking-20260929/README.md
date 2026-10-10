# Integrated tracking observer

The shipped configuration inventories sources in this checkout.
Repository-relative paths resolve against the repository containing
`refresh_tracking.py`, independent of the shell working directory. Absolute
paths remain supported for explicitly supplied local observation inputs.
Relative paths and symlinks escaping the checkout are rejected.

Run
`python3 tasks/production-tracking-20260929/refresh_tracking.py --output-dir /tmp/skyyrose-tracking-review`
for an offline source inventory and dashboard. The optional `--live` flag adds
only the configured public HTTP probes. Source presence and public HTTP liveness
do not establish authenticated integration, provider execution, spend, owner
acceptance, or deployment.

The configuration deliberately does not import historical observations or
manifests from other worktrees. Those are dated evidence, not current proof.
Optional connector, website, E2E, manifest and integration inputs must be
supplied explicitly with their original capture dates and compatible schemas.
Missing inputs remain unavailable. Refreshing their files never refreshes their
underlying observations.

The observer's hash chain and checkpoint detect local corruption; they are not
an independently anchored economic ledger. Preserve the observation log and
hidden checkpoint together when retaining an output directory. Synthetic
combined replay counts are excluded from actual traffic and spend.

Tests:
`python -m unittest discover -s tasks/production-tracking-20260929 -p 'test*.py' -v`.
The combined offline relay/Creative OS/Governor replay is
`python tasks/e2e-tracking-fixes-20260929/run_local_e2e.py --fixture-directory /tmp/unique-replay --record /tmp/unique-replay-record.json`;
use fresh paths. It requires PHP on PATH and records only synthetic local
evidence.
