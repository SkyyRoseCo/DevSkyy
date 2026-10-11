# Test Isolation Flake Sprint — Handoff Doc

**Date**: 2026-05-27
**Worktree**: `~/DevSkyy/.claude/worktrees/audit-p0-sprint`
**Branch**: `fix/audit-2026-05-23-p0-sprint`
**Status**: Diagnostic-only — NO fixes applied. Sprint deferred per founder direction.

---

## Symptom

Different test fails per full-suite run, but each fails-in-full test **passes in isolation**:

| Iter | Failed test | Isolated re-run result |
|------|-------------|------------------------|
| 15   | `tests/orchestration/test_embedding_engine.py::test_cohere_embed_single_text` | ✅ passed in 1.02s |
| 16   | `tests/test_zero_trust.py::TestCertificateAuthority::test_load_ca` | ✅ passed in 1.02s |
| 18   | `tests/test_zero_trust.py::TestCertificateAuthority::test_load_ca` (same as iter 16) | ✅ passed isolated |

**Pattern**: order-dependent pollution. Some earlier test mutates shared state (env vars, `sys.modules`, httpx transport, crypto context, or similar) without restoring it.

---

## What is NOT broken

- ✅ Code under test is correct (passes isolated)
- ✅ Test fixtures are correct (passes isolated)
- ✅ pytest config is fine (`pyproject.toml` rootdir, asyncio mode auto)
- ✅ No regression from this session's commits — same pattern existed before

---

## What IS broken

- ❌ Test isolation — somewhere in `tests/` (~5500 tests) at least one test mutates global state without cleanup
- ❌ CI signal noise — full-suite runs become non-deterministic per which test pollutes first

---

## Suspects (ranked by likelihood)

1. **`os.environ` mutation without `monkeypatch`** — JWT/encryption env vars touched by `tests/test_zero_trust.py` neighbors, `tests/test_mfa.py`, `tests/test_security.py`
2. **`sys.modules` cache pollution** — anywhere a test does `del sys.modules['x']` or `importlib.reload()` to swap a global singleton
3. **`httpx` transport mocking** — global mount applied in one test, not torn down (affects cohere + zero_trust both use httpx)
4. **Crypto library state** — `cryptography.x509` CA cache, `passlib` context registration
5. **Asyncio loop state** — `asyncio-1.3.0` mode=auto + scope=function should isolate, but custom event-loop fixtures can leak

---

## Repro recipe

```bash
cd ~/DevSkyy/.claude/worktrees/audit-p0-sprint
/Library/Frameworks/Python.framework/Versions/3.14/bin/pytest tests/ \
  -p no:cacheprovider --timeout=30 --tb=no -q --no-header \
  --ignore=tests/aos/test_smoke_real_agent.py \
  > /tmp/pytest-flake-repro.txt 2>&1
grep -E "^FAILED " /tmp/pytest-flake-repro.txt
```

Expected: 0-1 FAILED line, different test each run. Each one passes isolated.

---

## Recommended bisect

**Cost estimate**: 30-60 min hands-on.

1. **Find what runs immediately before the failure** — use `pytest --collect-only -q` to dump deterministic test order. Find `test_load_ca` (or whichever failed last). Note the 10 tests immediately preceding it.

2. **Bisect those 10**:
   ```bash
   # Run each preceding test ALONE then run the failing test — if pair fails, that test pollutes
   for t in $(grep -B10 "test_load_ca" collect.txt | head -10); do
     echo "=== $t ==="
     pytest "$t" tests/test_zero_trust.py::TestCertificateAuthority::test_load_ca --timeout=15
   done
   ```

3. **When pair fails**: inspect the polluter for:
   - `os.environ[X] = Y` without restore
   - `sys.modules.pop("X")` or `importlib.reload()`
   - `httpx.MockTransport` applied at module level
   - Singleton mutation (e.g. `from foo import singleton; singleton.cleared = True`)

4. **Fix at the polluter**, not at the victim. Add the cleanup the polluter is missing.

---

## Why NOT skip / xfail

Per `drive-to-green` and `CLAUDE.md` rules:
- ❌ Adding `@pytest.mark.skip` hides the bug
- ❌ Adding `@pytest.mark.xfail(strict=False)` lets it silently regress
- ❌ Adding `@pytest.mark.flaky` invents a new marker without a plugin

The correct fix is finding + cleaning up the polluter. That's what this sprint is for when scheduled.

---

## Out of scope for this sprint

- Other pre-existing flakes (e.g. `tests/aos/test_smoke_real_agent.py` 15s timeout — known per cmem #8690, aiosqlite hang, separate fix)
- Real test failures (none — all fixed in this session's PR-ready commits)

---

## Tracking

When picked up, link to this doc + cite the cmem observations:
- `cmem #8690` — smoke test aiosqlite hang (related but distinct)
- This session's fixes: `c1d727e7a` (canon), AOS enum fix, mock fix, manifest gen, 5 patch-target fixes
