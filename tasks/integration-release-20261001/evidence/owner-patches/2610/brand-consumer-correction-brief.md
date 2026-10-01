# Stream 4 bounded brand-consumer correction

The source patch removes retired brand copy from 42 owned active consumers. It
introduces no replacement slogan, product facts, artwork, or generated media.
The integration owner applied the patch; this stream only inspected that
checkout and prepared its patch in isolated Git exports.

## Authority and creative reference

The reviewed authority is `assets/brand/brand.yaml` at
`f3e2b91cad3a17f25aabde6932cfbfb593f0b694`: the active tagline is empty and the
two retired expressions remain in its history. Current founder product facts
remain authoritative as `FOUNDER_CONFIRMED`. The single editable product source
is `wordpress-theme/skyyrose-flagship/data/logo-registry.json`; default reads use
`from skyyrose.core.product import get_product`. Neither authority file changes.

Required prompting reference, read before this copy work:
[/Users/theceo/.codex/creative-standards/imagery-prompting.md](/Users/theceo/.codex/creative-standards/imagery-prompting.md).
Its collection identity, fidelity, natural integration and review requirements
continue to govern creative work. This correction only omits retired copy from
existing source. No prompt is submitted, provider called, media generated,
spending incurred, or publishing performed. Provider-specific controls are not
applicable. Existing generation and release holds remain in force.

## Patch and ownership

Patch: `evidence/brand-consumer-corrections.patch`, SHA-256
`6045059fef6103a8194ca5e540d55ca44678ea117049a367e69eb5a4b7deab7e`.
It contains 40 Python files plus the original theme's mascot source and rebuilt
minified output. Shared constants consume `BrandConfig.load().tagline_active`;
their chain/context callers omit an empty clause cleanly while retaining the
three collection-specific taglines. Static training inputs preserve feature
descriptions and remove retired slogans and one compact retired hashtag. The
mascot greeting reads `Hey! I’m Skyy 👋 Welcome to SkyyRose.`

`creative/nodes.py` belongs wholly to Stream 3 and is absent from this patch.
The newer Governor rewrite already corrected `creative/runner.py`; that file is
also absent. `creative/checkpointer.py` changes only its retired module guidance
line and retains the newer Governor's pool cleanup. The physical Kids Capsule
insert description in `data/collections/kids-capsule/copy.md` stays untouched.
Historical evidence, registry bindings and founder specifications stay intact.
The inventory records other owners; this is not a whole-repository brand gate.

## Evidence boundaries

`evidence/brand-consumer-bindings.json` describes the original **f3e patch base**
and resulting f3e bytes. It must not be interpreted as the current integration
full-file hash list. `evidence/brand-consumer-adoption-bindings.json` separately
records all 42 before/after hashes against the actual validation source
`c4d971022aee75b6ea58b13b44cdc9d91aeb81e9`. The checkpointer is the one differing
full-file binding because its Governor implementation changed between sources:
current before `a1d4a398b087437ade94438f4914b493f0281504856da6ee773a8244a3077e71`,
current corrected `b3b261c023869394ec774d21bb8baa2508a1ae99cdc71b635fd874de8f22984d`.
Do not overwrite newer code to match the original patch-base hash.

The validation export contains exact c4d source plus this patch. Actual
network-denied regression output is saved in `evidence/brand-consumer-tests.log`.
The copy-node test is explicitly skipped while Stream 3 owns that correction;
there is no passing claim for its future source. No authenticated execution is
claimed; authentication is not applicable to these offline checks. The JSON
verification receipt records preserved-source hashes and final check results.

Reproduction uses the repository virtual environment and an isolated export:

```sh
BRAND_CONSUMER_CANDIDATE=/absolute/c4d-plus-patch-export \
  .venv/bin/python -m unittest discover -s tools/3d-commerce \
  -p test_brand_consumer_patch.py -v
```

The preparation function itself rejects active Git checkouts and requires the
exact reviewed brand authority and every owned target's baseline bytes before
any write. All literal and Python AST checks also complete before the first
write. A newer isolated export is rejected rather than overwritten to an older
baseline. Its Terser dependency is pinned to 5.36.0 and the owning build options;
it rebuilds only the mascot minified output. Review reproduced the earlier
missing per-file boundary in a temporary directory; this tooling repair does
not change the already adopted source patch.

Final combined source freeze, semantic certification review, accepted asset
approval, device/product fidelity and deployment remain separate gates. The
integration owner owns cross-stream bug-ID reconciliation; historical receipts
are preserved without guessing new identifiers or independently renumbering.
