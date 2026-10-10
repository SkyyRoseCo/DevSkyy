# PR 994 CI repair — 2026-09-29

The first full CI run on 922503ef054a6587d6bb66b5a04f156b0fc5ceaf passed 7,760 Python tests and failed two material-classification tests. SG-015's founder-confirmed `Windbreaker fabric.` wording was not recognized, and the rendering-class regression map reflected the superseded material specifications.

The classifier now has a distinct windbreaker rendering class with an explicit shell sheen preset. This renderer choice establishes no fiber composition and writes nothing to the product registry. The regression map uses the current registry materials: cotton for the Kids/Mint & Lavender pieces, the existing polyester renderer class for the three blend joggers, and windbreaker for SG-015. Historical nylon fixture wording is explicitly marked historical. Coverage checks that windbreaker does not imply nylon, explicit nylon still classifies as nylon, and negated windbreaker fails closed.

The root TypeScript job stopped at the production dependency audit before unit tests ran. Corey approved compatible dependency fixes in this chat. The lock changes only Joi 18.2.5 → 18.2.6 and Undici 8.10.0 → 8.10.2 (version, tarball URL, integrity); all other package entries and both dependency graphs/engine requirements are identical. Package metadata and integrity were read from the npm registry. No audit gate was weakened.

Local verification:

- 187 pipeline3d tests passed; one existing skip because gltfpack is unavailable.
- 690 root tests passed in 27 test files using the existing shared dependency installation, Node 26.8.1. This is not a fresh Node 22 dependency installation.
- The installed Homebrew Node 22.23.2 could not start because libsimdutf.34.dylib is missing; CI supplies the required Node 22 verification.
- Exact patched Joi/Undici releases installed separately in /tmp/pr994-dependency-verify. Joi accepts a valid ISO date and rejects an invalid one; Undici completes a MockAgent JSON request with network disabled. Authentication not applicable; offline smoke test.
- Production audit (`npm audit --omit=dev --audit-level=high`) exits 0, with six existing moderate findings outside this targeted repair.
- Black, Ruff, isort and diff checks passed for changed Python files.

CI must pass on the pushed final head before merge. Product specifications and image binaries are untouched by this repair. No deployment or generation occurred.
