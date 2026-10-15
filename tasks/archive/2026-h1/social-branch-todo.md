# Elite Studio — Social Media Branch

Build the social media branch of the Elite Studio "elite team": a deep-wired
`social` venture + a SkyyRose-branded social skills library scaffolded from the
Claude Skills bundle. SaaS-product feel, dedicated to The Skyy Rose Collection.

User decisions (locked via AskUserQuestion 2026-05-27):
- **Scope**: Refactor `skyyrose-content-engine` into an index hub + scaffold the full
  relevant set (~27 sub-skills).
- **Venture depth**: Deep wiring now — `SocialMediaAgent` live as a node;
  `CreativeAgent` + `MarketingAgent` wired but cost-gated.
- **Drops**: 11 off-brand source skills excluded.

## Prereq fix
- [x] `agents/social_media_agent.py::_load_catalog()` — import-safe (FileNotFoundError →
      {} + actionable warning). Verified: import clean, real post on br-001.

## Venture surface — `skyyrose/elite_studio/ventures/social/` ✅ DONE (8/8 tests pass)
- [x] `config.py`, `state.py`, `agents.py`, `pipeline.py`, `cli.py`, `__init__.py`,
      `__main__.py`, `tests/test_smoke.py`
- [x] Registered in `ventures/__init__.py`; README roster updated (social: beta)
- [x] Verified: `python -m ...ventures.social smoke` → 3 real posts, gates off

## Content-engine migration map (advisor — seed sub-skills before layering source)
| content-engine section | → target sub-skill |
|---|---|
| Content Pillars + ratios | social-media-strategy |
| Weekly Rhythm + Monthly Specials | social-media-calendar |
| Instagram Playbook (carousel bits) + Caption Formulas + br-001 example | instagram-carousel |
| TikTok Playbook + Video Script Templates (15/30/60s) | tiktok-script + short-form-video-plan |
| X/Twitter Playbook | twitter-thread + thread-hook-writer |
| Pinterest Playbook | pinterest-strategy |
| Hashtag Strategy block | hashtag-strategy |
| Cross-Platform Repurposing flow | social-media-strategy |
| Anti-Patterns | distribute by topic |

## Skills library — `.claude/skills/skyyrose-social-*/` ✅ DONE
- [x] `skyyrose-content-engine/brand-guardrails.md` shared canon (Five refs, collection
      voice, lockups, tagline, no-urgency canon, LOCKED code-example template, migration map)
- [x] 27 branded SKILL.md (5 parallel subagents, themed batches) — 244-414 lines each
- [x] Refactored `skyyrose-content-engine/SKILL.md` into the index hub

## Post-build anti-hallucination pass ✅ (verify-before-claim caught subagent invention)
- [x] Removed 10 invented `post.*` attrs (.slides/.script/.thread_tweets/etc) — agent
      returns caption+hashtags only; skill is the structuring layer
- [x] Fixed 5 bogus `generate_post(name, "press", invented_type)` → real
      `get_collection_context(...)` + valid `generate_post`
- [x] Replaced retired SKU `lh-001` → `lh-004` (Love Hurts Bomber Jacket); removed invalid
      `--mode` CLI flags
- [x] Re-audit clean: all calls use valid SKUs/platforms/content_types

## Verify ✅ ALL GREEN
- [x] `import agents.social_media_agent` clean; real post on br-001 + lh-004
- [x] `pytest .../ventures/social/tests/` → 8 passed
- [x] `python -m ...ventures.social smoke` → 3 real posts, cost gates off
- [x] 28/28 skill frontmatters valid; all reference brand-guardrails.md
- [x] registry: ('imagery','photo','threed','video','social')
