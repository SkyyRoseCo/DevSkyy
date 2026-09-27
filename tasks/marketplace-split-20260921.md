> SUPERSEDED CANDIDATE: current packaging is documented in `tasks/current-package-6e988bac.md`. Earlier installation evidence remains historical; old split artifacts preserved outside the worktree under `/tmp/skyyrose-superseded-release-packages-20260921-2252/`.

# V2 marketplace split-package prototype — 2026-09-21

## Scope and isolation

- Worktree: `/Users/theceo/.codex/worktrees/marketplace-split/DevSkyy`
- Branch: `codex/v2-marketplace-split-20260921`
- Base: `2c7644772be1d19c9218ebfb2b980350033b83f7`
- No deployment, production mutation, paid provider call, credential copy, or
  product-registry edit was performed.
- Input was the verified complete V2 bundle with SHA-256
  `e1a35cc901854714f471e1256e6f2aa60a4610788c07f033a65f7cc65f67ce5d`.

## Final prototype release

Release directory:
`wordpress-theme/skyyrose-flagship-2/dist-marketplace-2.4.4-e1a35cc9/`

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `skyyrose-flagship-2-core.zip` | 1,732,148 | `8e74c099f2884dbfdf925a557449e3c18062da7a157ec2c2e30d41afad366d67` |
| `skyyrose-flagship-2-required-media.zip` | 167,577,818 | `f821432712b1319fe25ca6ccba66a1f24f79ad9552277711d45116a9098bb911` |
| `core-manifest.json` | 29,648 | `6bf75c00ea4a2c45ffc5142b0e2bc824cc30a4301fb05ca59e9051f97cd5031f` |
| `required-media-manifest.json` | 78,237 | `8f93143f8798c078ffcaa3dc1f6060c231dd9abe4329c5ba3e9098e6a010fa47` |
| `full-payload-manifest.json` | 107,946 | `06675a40101592be4af2482f775a87a94aceec009271ac28f06d96251f56d3ac` |
| `optional-demo-manifest.json` | 272 | `35a4b43b2f9a4f4ff394f45a2fe982e6416420ad039e48b70d521aee68c74488` |
| `install-required-media.py` | 9,431 | `c53c1679802d3835496360a23c99cf41af020886ac037aedfd600c0f8fda00e5` |
| `split-release.json` | 894 | `e15da9ce8e0883b568c67c9ff52d634b1096b0037a484fb1304e2715e95079cc` |

The core contains 173 files and 4,302,639 uncompressed bytes. Required brand
media contains 385 files and 168,421,202 uncompressed bytes. Their disjoint
union is exactly the complete source payload: 558 files and 172,723,841 bytes.
Optional demo content is empty because the verified theme does not contain a
separable demo-only payload. Required media remains required for a complete
storefront.

## Safety and integrity behavior

- The builder requires the expected source-archive SHA-256, refuses a nonempty
  destination, builds in a sibling temporary directory, and publishes by rename.
- The installer requires an independently supplied release-descriptor SHA-256.
  That descriptor pins the source bundle and every archive and manifest.
- Extraction rejects duplicate, absolute, parent-relative, drive-prefixed, UNC,
  backslash, nonregular, oversized, excessive-compression, and undeclared ZIP
  entries. Reads are bounded to declared file sizes.
- Reconstruction occurs beside the installed theme. Every path, byte length,
  and SHA-256 must match the full manifest before the existing theme is renamed
  to a rollback path and the complete candidate is moved into place.
- On an installation failure after the swap begins, the previous theme is
  restored. The core archive alone is not an activatable complete storefront.

## Verification performed

- `black --check tools/v2-marketplace-package/*.py` — PASS
- `ruff check tools/v2-marketplace-package/*.py` — PASS
- `bandit -q -r tools/v2-marketplace-package` — PASS
- `python3 tools/v2-marketplace-package/test_split_package.py` — PASS (3 tests)
- deterministic package rebuild from the pinned full archive — PASS
- `git diff --check` — PASS

Regression tests prove deterministic artifact hashes, exact disjoint union,
atomic reconstruction, rejection of a tampered media archive before mutation,
rejection of Windows traversal forms, and refusal to publish into a stale
nonempty directory.

## Open marketplace gates

- Confirm the target marketplace's maximum archive size and whether its review
  flow permits a required companion archive. The required-media ZIP is about
  160 MiB compressed.
- Confirm media/font/video redistribution licenses and marketplace disclosure
  requirements before public submission.
- Publish the release-descriptor hash over an authenticated channel separate
  from the downloadable artifacts.
- Run the documented install and rollback workflow in a clean reviewer-style
  WordPress environment. This local prototype is preparation, not marketplace
  certification or a production release.
