# cli-anything-skyyrose-flagship-2

An agent CLI for the **SkyyRose Flagship 2** WordPress theme
(`wordpress-theme/skyyrose-flagship-2`). It runs the theme's own npm gates under
the pinned V2 toolchain. Each run is recorded and tied to the exact version of
the files it ran against. The CLI then exports one evidence record that both of
these accept:

- **God Mode X**: its own `check_completion.py` validates the record.
- **Fashion Theme Team**: the record carries its release-engineer fields and
  gives its PASS / FAIL / BLOCKED verdict.

There is no deploy, recertification, or paid-provider command. Deploys stay
behind `scripts/deploy-theme.sh` and the STOP-AND-SHOW rule. Image-generation
and judge scripts are refused.

## Requirements (the real software)

| Tool               | Version                                                                                        | How to supply it                                                                                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Node / npm         | exactly the pins in `tools/v2-source-certification/build-inputs.json` (22.23.2 / 10.9.8)       | download the nodejs.org tarball, check its sha256 against `SHASUMS256.txt`, and set `SKYYROSE2_NODE_BIN_DIR=<extract>/bin`. Homebrew's Node is a different patch version and gets rejected. |
| Python             | the `python` pin (3.12.12)                                                                     | activate the repo `.venv`, or set `SKYYROSE2_PYTHON_BIN_DIR`                                                                                                                                |
| PHP                | any 8.x on PATH                                                                                | `brew install php`                                                                                                                                                                          |
| Theme node_modules | from `npm-shrinkwrap.json`                                                                     | `cd wordpress-theme/skyyrose-flagship-2 && npm ci` with the pinned Node on PATH                                                                                                             |
| WP/Woo fixture     | 7 hash-pinned WordPress 7.1 / WooCommerce 11.1.0 files, needed by `verify` and `package:theme` | `cli-anything-skyyrose-flagship-2 fixture prepare` (free public downloads, checked against `tools/v2-runtime/fixtures/pdp-native-template-hashes.json`), or set `V2_WP_FIXTURE`             |
| God Mode X         | `SkyyRoseCo/god-mode-x` checkout                                                               | `gh repo clone SkyyRoseCo/god-mode-x ~/god-mode-x`, or set `GOD_MODE_X_ROOT`                                                                                                                |

## Install

```bash
cd skyyrose/cli_harnesses/skyyrose-flagship-2/agent-harness
/path/to/DevSkyy/.venv/bin/python -m pip install -e .
cli-anything-skyyrose-flagship-2 doctor
```

## Usage

The CLI uses the DevSkyy checkout containing the current directory. To point it
at another checkout, pass `--repo-root` or set `SKYYROSE2_REPO_ROOT`. It never
falls back to a default checkout.

```bash
cli-anything-skyyrose-flagship-2                 # REPL
cli-anything-skyyrose-flagship-2 doctor          # toolchain, pins, node_modules, fixture, God Mode X
cli-anything-skyyrose-flagship-2 fixture prepare # pinned WP/Woo files for verify
cli-anything-skyyrose-flagship-2 info            # candidate id + SKYYROSE2_VERSION
cli-anything-skyyrose-flagship-2 scripts list --kind check
cli-anything-skyyrose-flagship-2 check run check:registry lint:php
cli-anything-skyyrose-flagship-2 check all # standard read-only set, ending with `verify`
cli-anything-skyyrose-flagship-2 build run build:assets --plan
cli-anything-skyyrose-flagship-2 build run build:assets
cli-anything-skyyrose-flagship-2 version check
cli-anything-skyyrose-flagship-2 version bump --to 2.5.2 --plan
cli-anything-skyyrose-flagship-2 pin status      # registry vs V2 pin (read-only)
cli-anything-skyyrose-flagship-2 evidence export # God Mode X record + FTT verdict
cli-anything-skyyrose-flagship-2 evidence review --reviewer theme-release-engineer \
  --disposition PASS --note "read logs for check:registry..verify"
cli-anything-skyyrose-flagship-2 evidence validate path/to/task-evidence.json
```

Add `--json` before the subcommand for machine output. Add `--dry-run` to run
without saving the session ledger.

Exit codes: `0` ok · `1` refused or usage error · `3` a gate ran and failed, or
God Mode X rejected the record.

## Gate classes

The script list comes from `package.json` each time the CLI runs. Which scripts
may run is set only in `core/gates.py`:

- **check**: read-only. If a check changes a tracked file, it is recorded as
  FAIL.
- **build**: rewrites tracked theme outputs and reports the changed paths.
- **blocked**: `render:*`, `certify:*`, `workflow:*`, `author:*`, and the
  image-judge and image-generation scripts. These are never run.
- **unclassified**: a new script nobody has classified yet. It is refused until
  someone adds it to `core/gates.py`.

## Evidence model

- **Candidate id**: a hash of HEAD, the theme's tree object, and the bytes of
  every tracked change. Any edit creates a new candidate, so runs from an older
  tree are dropped from the export, and the export reports how many.
- **God Mode X claim**:
  - `verified`: the tree is clean and every included gate passed.
  - `partial`: the tree is dirty.
  - `blocked`: a gate failed.

  The CLI never upgrades a claim to get past the checker. God Mode X rejects
  `partial` and `blocked` by design.

- **Fashion Theme Team verdict**:
  - FAIL: a gate failed or ran in a different environment, or an independent
    reviewer's latest review is FAIL.
  - BLOCKED: the tree is dirty, or no independent review exists yet. A review by
    anyone recorded as running a gate on that candidate is refused (checked
    against the owners stored on the runs, not the current environment).
  - PASS: every gate passed and an independent reviewer accepted it. That means
    ready for founder review only.

  Reviews are read from **every session** in the CLI home that matches the same
  `candidate_id` and `harness_sha256`, so `session new` cannot drop an earlier
  FAIL. Each reviewer's latest review (by `reviewed_at`) stands. One independent
  FAIL makes the verdict FAIL; otherwise PASS needs at least one independent
  PASS. Anyone who ran a gate on the candidate in any session counts as an
  owner. A session file that cannot be read stops the export or review with an
  error instead of being skipped.

## Provenance

- Each run log starts with a JSON header holding the return code, changed paths,
  candidate, and harness hash. At export, the CLI re-derives each run's status
  from that hashed log and refuses an edited ledger.
- Records include `cli.harness_sha256`, a hash of this CLI's own source, and the
  target environment label carries it too. Runs made by different CLI code count
  as stale.
- If a gate failed earlier on the same candidate and then passed on a rerun, the
  earlier failure is reported as a P3 finding.
- **Gate owner source.** Each run and its log header record `owner_source`:
  `env` when `SKYYROSE2_GATE_OWNER` named the owner, otherwise `git`
  (`git config user.name`). The record lists them in
  `fashion_theme_team.owner_sources`. When any included run has an `env` owner,
  the record carries an OPEN P3 finding, "gate owner supplied via
  SKYYROSE2_GATE_OWNER is unverified". It does not block. Editing the source in
  the ledger makes it disagree with the hashed log, and the export refuses it.
- **Installed deps.** The candidate id covers tracked files only, not
  `node_modules`. The environment label therefore ends with `;deps=<12 hex>`,
  the sha256 of
  `wordpress-theme/skyyrose-flagship-2/node_modules/.package-lock.json` (the
  hidden lockfile `npm ci` writes), or `;deps=none` when that file is missing. A
  run made with different installed deps has a different environment from the
  export, so it does not count as a PASS. `doctor` reports the digest and flags
  a missing lockfile.

## Preview

Not implemented. The theme gates produce no visual intermediate state.
Rendered-page evidence comes from God Mode X's `browser_inspect` against a
staging URL, which this CLI does not drive.

## Tests

```bash
SKYYROSE2_E2E=1 SKYYROSE2_NODE_BIN_DIR=... CLI_ANYTHING_FORCE_INSTALLED=1 \
  python -m pytest cli_anything/skyyrose_flagship_2/tests -v -s
```

The E2E tests run the real theme scripts and God Mode X's real checker. They run
only when you opt in with `SKYYROSE2_E2E=1`, because one of them briefly edits a
tracked theme file; run them in a dedicated worktree. Once you opt in, a missing
toolchain or checker makes them fail; they never skip.

**Reviewer identity is self-declared.** `evidence review` checks only that the
reviewer's name differs from every owner recorded on the candidate's runs. It
does not prove who the reviewer is. The gate owner is also just a name: from git
config, or freely chosen through `SKYYROSE2_GATE_OWNER` (flagged as above).
