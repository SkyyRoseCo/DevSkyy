# Blender render worker recovery — draft qualification

Recovered from `feat/single-product-entry-point` at
`1693beec2336ad1fc5a68c2b5fa7dee9aaad3fdf` onto main. This draft preserves a
standalone renderer, artifact stores, schemas, tests, and its proposed container
recipe. It does not mount the API in the application or enable a compose
service.

Recovery fixes require administrator access to the router, consume owned Redis
pending deliveries, prevent implicit queue trimming, add a retry before settling
the original delivery, retain jobs when terminal persistence fails, and avoid
rendering an already completed record after an ACK failure. Product
specifications remain owned by the canonical registry; this recovery changes no
product facts.

## Qualification still required before activation

- Bound the entire fetch, optimize, render, publish, and persistence interval,
  or implement lease renewal and fencing. The one-hour reclaim threshold is not
  proof that a live job cannot be reclaimed. Multiworker operation is not
  qualified.
- Test Redis crashes and reconnections around enqueue, reclaim, retry and ACK
  with a real Redis service. Retryable infrastructure outages also need bounded
  backoff and operational alerting.
- Build and verify the Docker image, its pinned binaries, the one-shot command
  and production artifact store. The inherited download/version comments are
  historical source claims, not verification performed in this recovery.
- Exercise real Blender and gltfpack end to end and inspect output quality.
  Local synthetic runner tests do not verify rendering or product fidelity.
- Add application/compose wiring only after these gates pass. No provider calls,
  deployment or product-media promotion are authorized by this draft.
