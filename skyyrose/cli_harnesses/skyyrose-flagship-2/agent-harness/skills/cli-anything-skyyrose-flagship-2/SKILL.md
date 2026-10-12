---
name: >-
  cli-anything-skyyrose-flagship-2
description: >-
  Run the SkyyRose Flagship 2 WordPress theme's npm gates (check:*, lint:php, verify, build:*) under the
  pinned V2 toolchain, bump the SKYYROSE2_VERSION triple, report V2 registry-pin drift, and export
  candidate-bound evidence that God Mode X validates and the Fashion Theme Team reviews. Use for
  flagship-2 build/verify/handoff work; never for deploys, recerts, or image generation.
---

# cli-anything-skyyrose-flagship-2

An agent CLI for `wordpress-theme/skyyrose-flagship-2`. It runs the theme's own
npm scripts. Each run is recorded against the exact version of the files it ran
on, called the *candidate*. The CLI then exports one God Mode X `task-evidence`
record, which also carries the Fashion Theme Team verdict.

## Before you start

```bash
cli-anything-skyyrose-flagship-2 --json doctor
```

If `ok` is false, fix whatever it names before running gates:

- **Node/npm mismatch**: set `SKYYROSE2_NODE_BIN_DIR` to the `bin/` of the
  exact pinned nodejs.org build. Homebrew's Node is rejected.
- **Python mismatch**: activate the repo `.venv`.
- **node_modules missing**: run `npm ci` in the theme directory with the pinned
  Node.
- **WP fixture missing**: run `fixture prepare`. It is needed by `verify` and
  `package:theme`, which refuse to run without it.
- **God Mode X missing**: clone `SkyyRoseCo/god-mode-x`, or set `GOD_MODE_X_ROOT`.

The CLI operates on the DevSkyy checkout that contains the current directory.
To use another checkout, pass `--repo-root` or set `SKYYROSE2_REPO_ROOT`.

## Commands

| Group | Command | Effect |
|---|---|---|
| introspection | `doctor`, `info`, `scripts list [--kind check\|build\|blocked\|unclassified]`, `pin status`, `version show\|check` | read-only |
| gates | `check run <script>...`, `check all [--fail-fast]` | run read-only gates; a gate that changes a tracked file is recorded as FAIL |
| builds | `build run <script> [--plan]` | regenerate tracked theme outputs and report changed paths |
| version | `version bump --to X.Y.Z [--plan]` | atomically sets `functions.php`, `style.css` and `readme.txt` |
| fixture | `fixture prepare\|status` | pinned WordPress/WooCommerce files that `verify` needs |
| ledger | `session new\|show\|list` | append-only gate-run ledger, stored outside the repo |
| evidence | `evidence export [-o DIR]`, `evidence review --reviewer R --disposition PASS\|FAIL --note N`, `evidence validate FILE` | God Mode X record and Fashion Theme Team verdict |

Put `--json` before the subcommand to get machine output; stdout is then always
exactly one JSON document. `--dry-run` runs the command without saving the
ledger.

**Exit codes:** `0` ok · `1` refused or usage error · `3` a gate failed or God
Mode X rejected the record.

## Typical flow

```bash
cli-anything-skyyrose-flagship-2 --json check all
cli-anything-skyyrose-flagship-2 --json evidence export
# a different agent or person reviews the logs, then:
cli-anything-skyyrose-flagship-2 evidence review --reviewer theme-release-engineer \
  --disposition PASS --note "read all 12 gate logs; verify chain green"
cli-anything-skyyrose-flagship-2 --json evidence export
```

## Rules the CLI enforces

- **Refused scripts.** `render:*`, `certify:*`, `workflow:*`, `author:*`, and
  the image-judge and image-generation scripts never run, because they can make
  paid provider calls. A script not yet classified in `core/gates.py` is also
  refused.
- **New candidate on every edit.** Any edit or commit produces a new candidate
  id. Older runs are left out of the export, and the export reports how many.
- **Honest claims.** God Mode X claims are `verified` for a clean tree where
  every gate passed, `partial` for a dirty tree, and `blocked` when a gate
  failed. God Mode X rejects `partial` and `blocked`, and the CLI never
  upgrades a claim to get past it.
- **Independent review.** The Fashion Theme Team verdict stays BLOCKED until
  someone other than the gate owner records a PASS review. Its PASS means ready
  for founder review only; it never authorises a deploy or merge.
- **Not in this CLI:** deploy, cache purge, WooCommerce writes, and moving V2
  pins (recertification). All of these need founder approval.
