# SkyyRose Kids debut — rough board review

Open [preview.html](preview.html) locally. Choose a route, play or scrub, and try 'Watch without directing notes' before reading the intention. Exact source images are shown separately beneath the sequences.

| Route | Runtime | Local movie | Contact sheet |
|---|---|---|---|
| A / She Moved First | 24s | [Timed board](exports/Kids-Route-A-rough-board.mp4) | [Frames](exports/Sequence-A-contact.png) |
| B / Out of the Frame | 22s | [Timed board](exports/Kids-Route-B-rough-board.mp4) | [Frames](exports/Sequence-B-contact.png) |
| C / Room for the View | 22s | [Timed board](exports/Kids-Route-C-rough-board.mp4) | [Frames](exports/Sequence-C-contact.png) |

These are schematic directing tools, not generated fashion footage. Movie exports hold each shot's endpoint for its planned duration. The browser also shows simple position/pose interpolation. Figure colors identify roles and do not reproduce garments or faces. The source panels show the actual reference files uncropped and unchanged. Source paths are local to this workspace and machine.

Read [Director's decision](DIRECTOR-DECISION.md), [Kids shot packet](KIDS-SHOT-PACKET.md), [Collection beats](COLLECTION-BEATS.md), [source audit](SOURCE-REVIEW.md), and [independent schematic review](qa/story-review.md).

Reproduce exports and focused browser checks with the bundled Node executable:

```sh
/Users/theceo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node /Users/theceo/.codex/worktrees/dae3/DevSkyy/tasks/relaunch-7day-20260911/collection-films/directing-workflow/kids-boards/export-review.cjs
```

The script uses bundled Playwright and local FFmpeg, overwrites this package's derived exports/QA files, and does not call providers. Keep independent review evidence snapshots if revising boards. No campaign or film approval follows from a successful export.
