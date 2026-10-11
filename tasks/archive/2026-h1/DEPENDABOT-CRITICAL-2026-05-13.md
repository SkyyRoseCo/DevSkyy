# Dependabot Critical Triage — 2026-05-13

Snapshot of open `severity=critical` Dependabot alerts on `main` at commit `2097edc77`.
Source: `gh api /repos/The-Skyy-Rose-Collection-LLC/DevSkyy/dependabot/alerts?state=open&severity=critical`.

GitHub-wide total: **432 open** (6 critical · 161 high · 222 moderate · 43 low).
This doc covers the 6 critical alerts only. High/moderate triage deferred.

---

## Critical Alerts (6)

| # | Package | Sev | Fix | GHSA | Class | Manifest |
|---|---------|-----|-----|------|-------|----------|
| 580 | protobufjs | critical | 7.5.5 | [GHSA-xq3m-2v4x-88gg](https://github.com/advisories/GHSA-xq3m-2v4x-88gg) | Arbitrary code execution | transitive (frontend/package-lock.json) |
| 579 | protobufjs | critical | 7.5.5 | [GHSA-xq3m-2v4x-88gg](https://github.com/advisories/GHSA-xq3m-2v4x-88gg) | Arbitrary code execution | transitive — DUPLICATE of #580 |
| 483 | mlflow | critical | 3.9.0rc0 | [GHSA-vhcx-3pq2-4fvc](https://github.com/advisories/GHSA-vhcx-3pq2-4fvc) | Path traversal | **direct** (`pyproject.toml: mlflow>=3.5.0`) |
| 458 | handlebars | critical | 4.7.9 | [GHSA-2w6w-674q-4c4q](https://github.com/advisories/GHSA-2w6w-674q-4c4q) | JS injection via AST type confusion | transitive (no direct manifest match) |
| 419 | nltk | critical | 3.9.3 | [GHSA-7p94-766c-hgjp](https://github.com/advisories/GHSA-7p94-766c-hgjp) | Zip Slip | **direct** (`pyproject.toml: nltk>=3.9.1`) |
| 382 | simple-git | critical | 3.32.3 | [GHSA-r275-fr43-pm7q](https://github.com/advisories/GHSA-r275-fr43-pm7q) | RCE via blockUnsafeOperationsPlugin bypass | transitive (no direct manifest match) |

---

## Recommended remediation (per-CVE PRs)

### #419 nltk — **quickest win**
Direct dep, current spec `nltk>=3.9.1` already permits the fixed 3.9.3.
- Bump pinned/locked install: `pip install -U "nltk>=3.9.3"`
- Update lockfile / requirements snapshot in same PR.
- Smoke test: anything that imports `nltk.download` or `nltk.data.find` (Zip Slip is in archive extraction).

### #483 mlflow — needs decision
Fix is `3.9.0rc0` (release candidate). Options:
1. Bump constraint to `mlflow>=3.9.0rc0` accepting pre-release.
2. Wait for GA `3.9.0` then pin `mlflow>=3.9.0`.
3. Workaround: audit code paths that call `mlflow.artifacts.download_artifacts` or `mlflow.set_tracking_uri` with user-controlled paths.

### #580 + #579 protobufjs (dup) — transitive
`npm audit fix` in `frontend/` should pull a parent that depends on protobufjs@>=7.5.5. If parent doesn't ship a fix, add `overrides` block to `frontend/package.json`:
```json
"overrides": { "protobufjs": "^7.5.5" }
```
Close #579 as duplicate of #580 via `gh api -X PATCH /repos/.../dependabot/alerts/579 -f state=dismissed -f dismissed_reason=duplicate`.

### #458 handlebars — transitive
`npm audit fix` in `frontend/`. If transitive parent doesn't update, add override `"handlebars": "^4.7.9"`.

### #382 simple-git — transitive
`npm audit fix` in `frontend/`. Override target: `"simple-git": "^3.32.3"`.

---

## Scope decisions

- This doc is **inventory + recommendation only**. No package bumps in this commit.
- Per-CVE PRs to follow. Order: #419 nltk (smallest blast radius) → #580/#579 protobufjs → #458 handlebars → #382 simple-git → #483 mlflow (decision needed).
- High/moderate triage (161 + 222 = 383 alerts) is a separate effort. Recommend `gh api ... severity=high --paginate` dumped into a follow-up audit doc.

---

## Verification log

```bash
# Snapshot command (re-run to refresh):
gh api -H "Accept: application/vnd.github+json" \
  "/repos/The-Skyy-Rose-Collection-LLC/DevSkyy/dependabot/alerts?state=open&severity=critical&per_page=20" \
  --jq '.[] | {num,sev:.security_vulnerability.severity,pkg:.security_advisory.package.name,fix:.security_vulnerability.first_patched_version.identifier,ghsa:.security_advisory.ghsa_id,sum:.security_advisory.summary}'

# Direct-dep grep:
grep -E 'mlflow|nltk' pyproject.toml          # → mlflow>=3.5.0, nltk>=3.9.1
grep -lr protobufjs --include='package*.json' # → frontend/package-lock.json only
```

Owner: `The-Skyy-Rose-Collection-LLC` · Repo: `DevSkyy` · Branch: `chore/p1-p5-backlog`.
