# Monorepo consolidation baseline

Historical inventory of DevSkyy `main` commit
`268e8fef8c865db1b9329b01e54ab14fd260a2ab`. These figures describe that exact
Git tree, not the current checkout or today's `main`. This document is a
migration proposal; it does not authorize archiving, deletion, or history
rewriting.

## Measured snapshot

| Metric                                         |         Value |
| ---------------------------------------------- | ------------: |
| Tracked blob entries (including symlink blobs) |         9,070 |
| Gitlink entries (submodule contents excluded)  |             5 |
| Total blob and gitlink entries                 |         9,075 |
| Sum of blob bytes across tracked paths         | 1,140,049,966 |
| Exact duplicate blob groups                    |           604 |
| Repeated blob bytes beyond one copy per group  |   121,770,039 |

Blob byte totals are logical file-content sizes, not Git pack size, checkout
disk usage, or guaranteed storage savings. Identical content may be
intentionally needed at multiple paths; duplication alone does not make a file
removable.

### Reproduce the inventory

From the repository root, run this read-only command with Python 3. It reads
only local Git objects and requires the named historical commit to be available.
It does not follow symlink targets, inspect submodule contents, or contact an
external service. Authentication is not applicable.

```bash
python3 - << 'PY_INVENTORY'
import collections
import subprocess

snapshot = "268e8fef8c865db1b9329b01e54ab14fd260a2ab"
entries = subprocess.check_output(
    ["git", "ls-tree", "-r", "-l", "-z", snapshot]
).split(b"\0")
counts = collections.Counter()
sizes = {}
gitlinks = 0
for entry in filter(None, entries):
    metadata, path = entry.split(b"\t", 1)
    mode, kind, oid, size = metadata.split()
    if kind == b"commit":
        gitlinks += 1
    elif kind == b"blob":
        counts[oid] += 1
        sizes[oid] = int(size)
print("blob_entries:", sum(counts.values()))
print("gitlink_entries:", gitlinks)
print("total_entries:", sum(counts.values()) + gitlinks)
print("blob_bytes:", sum(sizes[oid] * count for oid, count in counts.items()))
print("duplicate_groups:", sum(count > 1 for count in counts.values()))
print("repeated_bytes:", sum(sizes[oid] * (count - 1) for oid, count in counts.items()))
PY_INVENTORY
```

The reproduced output is `9070`, `5`, `9075`, `1140049966`, `604`, and
`121770039`, in that order. To measure a newer snapshot, explicitly replace
`snapshot` with its full commit ID and record a separate result; do not relabel
these historical figures as current.

### Unvalidated archive estimate

The original proposal estimated **1,130 candidate files / 683,989,940 bytes**
under `assets/`, `renders/`, `screenshots/`, `archive/`, `_prototype/`, and
`docs/design-mockups/`. Its exact media-selection filter and candidate manifest
were not recorded, so these two estimates have not been reproduced. They are not
measured savings or an approved removal list. Before using them for a migration
decision, record the source commit, explicit selection rules, and per-path
manifest, then recalculate the count and byte total.

Production theme assets are not automatically removable. Preserve
founder-confirmed product facts, authoritative media, runtime references, and
working features.

## Required migration gates

1. Inventory the object with original path, Git blob SHA, byte size, media type,
   source commit, proposed archive path, and schema version.
2. Classify every reference as runtime, build-time, documentation-only, or
   orphaned.
3. After approval, copy to the proposed destination
   `SkyyRoseLLC/DevSkyy-Assets/archive/<original-path>`; verify the intended
   private repository and permitted scope before any transfer. Its availability
   and access are not established by this offline inventory.
4. Record and verify SHA-256 for the archived object.
5. Preserve necessary optimized runtime derivatives in DevSkyy.
6. Replace source directories with locator documentation where useful.
7. Run affected builds and tests before proposing deletion.
8. Remove files only in reviewed, independently revertible batches.
9. Treat Git-history rewriting as a separate operation requiring explicit
   approval.

## Proposed target architecture

- `apps/`: deployable API, storefront, and WordPress application boundaries
- `packages/`: shared Python/TypeScript/commerce libraries
- `services/`: independently deployed integrations
- `tooling/`: scripts, CI helpers, generators, and configuration
- `docs/`: active architecture and operations documentation
- private asset archive: original media, renders, source models, and historical
  exports

Directory moves will follow asset extraction and dependency mapping so the
repository does not combine structural churn with unverified runtime changes.
