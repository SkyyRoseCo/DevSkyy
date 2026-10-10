---
name: skyyrose-social-pr-pitch
description: "Writes personalized SkyyRose media pitches to fashion journalists, streetwear editors, and podcast hosts — story-first, under 200 words, with a 2-touch follow-up sequence — for earned media coverage of drops, the founder story, or Oakland luxury fashion angles."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — PR Pitch

## When to Use This Skill

- Pitching a fashion journalist, streetwear editor, culture writer, or podcast host for earned media coverage
- Launching a new product or collection and seeking a story angle beyond the product itself
- Positioning Corey Foster as an expert voice on Oakland fashion, Black-owned luxury streetwear, or the "concrete-to-luxury" narrative
- Building a press list and personalizing pitches per publication beat
- Writing a follow-up sequence after an initial cold pitch

**DO NOT** use this for paid advertising or sponsored content placement (different budget line), for influencer pitches (use `skyyrose-social-influencer-outreach`), or for generating a press release (the first touchpoint is ALWAYS a personalized pitch email — never a press release).

---

## Brand Canon (non-negotiable)

No tagline is authorized. Do not restore retired slogans.
- **Founder voice is earned and unhurried.** Corey Foster. Oakland, CA. Not a hype-merchant, not a press-hungry startup founder. He built this from the Town. The pitch reflects that register.
- **No fabricated press placements, stats, or awards.** Any metric in a pitch must be real. Placeholder fields use `{operator-supplied}` — do not invent numbers to make the pitch look validated.
- **Collection voice is isolated.** A pitch about Black Rose uses "armor / defiant elegance / concrete answering back" — not Love Hurts language. Never cross-attribute.
- **Products by NAME, not SKU.** "Black Rose Crewneck" in a pitch to Complex. Not "br-001."

Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## Phase 1: Find the Angle

### Required Inputs

| Input | What to Confirm | Default |
|-------|----------------|---------|
| **News hook** | "What's the news? (drop, milestone, founder story, cultural moment)" | No default |
| **Why now?** | "Why is this timely for a journalist's audience right now?" | No default |
| **Target publication type** | "Streetwear/fashion media? Cultural media? Local Bay Area? Podcast?" | Streetwear/fashion |
| **Supporting fact or number** | "Any real data, milestone, or verifiable claim we can anchor the pitch on?" | None — pitch with story if no stats |

**GATE: News hook + why now must be confirmed before drafting.**

> If operator has no verifiable stats, the pitch leads with story — the Corey Foster / Oakland angle is genuinely pitchable without manufactured metrics. Do not invent numbers.

---

## Phase 2: Choose the Pitch Type

| Type | Best For | SkyyRose Use Case |
|------|----------|------------------|
| **Story pitch** | Founder human interest, brand origin | "Corey Foster built a luxury streetwear brand in Oakland — here's how The Town shaped it" |
| **News pitch** | Drop launch, milestone, collection release | "Black Rose collection drops this week — Oakland's answer to quiet-luxury streetwear" |
| **Trend pitch** | Riding a cultural moment | "Bay Area streetwear is moving past logomania — SkyyRose is part of why" |
| **Expert pitch** | Journalist needs a Black-owned luxury streetwear voice for a piece | "For your piece on independent luxury — Corey Foster, SkyyRose, Oakland" |

---

## Phase 3: Write the Pitch Email

**Total pitch length: under 200 words. Non-negotiable.**

### Artifact Specification

```
## SkyyRose PR Pitch — [Publication / Journalist Name]

**Pitch type:** [Story / News / Trend / Expert]
**Target:** [Journalist name], [Publication], [Beat / coverage area]
**Subject line:** [Under 60 characters. Specific, factual. Never "EXCITING NEWS" or "you won't believe."]

---

SUBJECT: [Subject line here]

Hi [Journalist first name],

[Opening: 1-2 sentences. Reference their SPECIFIC recent work — article headline, podcast episode title, or byline. Explain why it's relevant to what you're about to pitch. This is the personalization that separates SkyyRose pitches from spray-and-pray PR blasts.]

[Hook: 1 sentence. The story in the sharpest possible form. Journalist-facing angle — what would make their readers stop scrolling?]

[Story: 3-4 sentences. The substance.
- For story pitch: Corey's founding context, Oakland anchor, "" as the through-line.
- For news pitch: What dropped, what makes it different from everything else in the streetwear lane.
- For trend pitch: The cultural observation, anchored in a real SkyyRose fact.
- For expert pitch: Corey's credentials and specific point of view.]

[Proof: 1-2 sentences. Real verifiable claim OR an honest "here's who we are" without inflation.
Acceptable: "We've fulfilled {operator-supplied} pre-orders since launching in [year]."
Not acceptable: Fabricated press placements or made-up statistics.]

[Ask: 1 sentence. What are you offering — interview, exclusive preview, product sample, or data?]

[Sign-off:]
Corey Foster (or [Your Name] on behalf of SkyyRose)
Founder, SkyyRose — The Skyy Rose Collection
skyyrose.co
skyyroseco@gmail.com
[Phone — optional]

---

**Note to operator:** Remove this section before sending.
- Subject line under 60 chars: [✓/✗]
- Pitch under 200 words: [word count]
- Personalized opening references real journalist work: [✓/✗]
- No fabricated stats or press: [✓/✗]
- No attachments in first email: [✓/✗] — offer to send materials if they respond
```

---

## Phase 4: Write Follow-Up Sequence

**2 follow-ups only. After that, move on.**

### Follow-Up 1 (3-5 days after initial pitch)

```
SUBJECT: Re: [original subject line]

Hi [Name],

Quick follow-up — I know your inbox is a lot. [Add one new angle or fresh data point if available.
Example: "Since I emailed, we opened pre-orders and sold {operator-supplied} units in 48 hours."]

Happy to send a sample of [Product Name] or connect you with a customer in [city] who'd be a good quote. Either way, no pressure.

Corey
skyyrose.co
```

### Follow-Up 2 (7-10 days after Follow-Up 1 — final)

```
SUBJECT: Re: [original subject line]

Hi [Name],

Last message from me on this — I respect the inbox. If the timing doesn't fit, totally understand.

If you're ever doing a piece on Black-owned luxury streetwear, Oakland fashion, or the concrete-to-luxury movement and need a founder voice, reach me at skyyroseco@gmail.com anytime.

Corey Foster
SkyyRose
```

**After Follow-Up 2: do not send more.** Rework the angle or try a different publication.

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Pull collection-correct brand voice context to inform the pitch's story block
ctx = agent.get_collection_context("black-rose")
print(ctx["full_name"])   # collection name for the pitch headline
print(ctx["mood"])        # emotional register to anchor the story section
print(ctx["caption_hooks"])  # on-register lines to mine for the pitch hook

# A product blurb in the right voice (story-section talking points)
post = agent.generate_post("br-001", "instagram", "product_launch")
print(post.caption)       # never paste verbatim — mine it for the pitch's story angle
```

```bash
# Inspect the social venture surface that feeds the pitch:
python -m skyyrose.elite_studio.ventures.social status
```

### Press Tracker Schema (pitch-linked row)

```json
{
  "journalist": "Jordan Miles",
  "publication": "Hypebeast",
  "beat": "Independent streetwear / Black-owned brands",
  "pitch_type": "story",
  "subject_line": "Oakland luxury streetwear — founder story",
  "pitch_sent_date": "2026-06-01",
  "follow_up_1_date": "2026-06-05",
  "follow_up_2_date": "2026-06-14",
  "status": "awaiting_response",
  "reference_work": "Their March feature on post-logo streetwear brands",
  "offer": "founder interview + Black Rose Crewneck sample",
  "notes": "Pitch angle: Corey's Oakland story, concrete-to-luxury. No manufactured stats."
}
```

---

## Example: Black Rose Collection Story Pitch — Hypebeast

**Scenario:** Pitching the collection launch and Corey's founder origin story to a streetwear media writer who recently covered the resurgence of Black-owned independent brands.

---

**SUBJECT:** Oakland luxury brand built from The Town up — founder story

> Hi Jordan,
>
> Your piece on post-logo independent streetwear last month was one of the clearest-eyed reads on where the lane is heading — the point about earned aesthetic vs. borrowed luxury signifiers is exactly the tension SkyyRose was built around.
>
> I'm Corey Foster, founder of SkyyRose — luxury streetwear from Oakland, CA. Tagline is "" — not a metaphor, a fact. Four collections: Black Rose, Love Hurts, Signature, and Kids Capsule. The Black Rose Crewneck is the flagship — gothic luxury, armor energy, silver on dark. Made for The Town but built to travel.
>
> The angle I think fits your audience: how an independent Oakland founder is carving out a quiet-luxury streetwear lane with zero European-house references and zero VC money.
>
> Happy to do a founder interview, send you a sample, or share the brand story behind any of the pieces.
>
> Corey Foster
> Founder, SkyyRose
> skyyrose.co | skyyroseco@gmail.com

---

**Word count:** 174. Under 200. ✓
**Personalized opener:** Yes — references specific article. ✓
**No fabricated stats:** ✓ — no numbers invented. ✓
**No attachment:** ✓ — offer to send sample on response. ✓

---

## Anti-Patterns

- **Sending a press release as the first touchpoint** — journalists get 100+ pitches daily. A press release in the first email is the fastest way to get filtered. The first email is always a personalized pitch, under 200 words.
- **Fabricating stats or press placements** — never write "as seen in [publication]" if it hasn't happened. Journalists verify. Getting caught inventing press destroys credibility with the exact people you need.
- **Cross-attributing collection voice in the pitch** — a Black Rose pitch should not use Love Hurts language. The journalist may not know the difference, but the pitch reads as unspecific and the founder does.
- **Generic opener** — "I love your work and thought you might be interested in..." is the universal signal for spray-and-pray. Reference a specific article, episode, or series they produced.
- **Pitches over 200 words** — cut it. Every sentence that doesn't serve the hook or the proof is a sentence that loses the journalist. Say less, land harder.
- **Attaching a PDF or media kit to the first email** — offer to send materials if they respond. Attachments trigger spam filters and signal amateur-hour PR.
- **Subject lines with "EXCITING NEWS" / "Opportunity" / "Collab?" / "Quick Question"** — specific and factual beats clickbait. "Oakland luxury streetwear — founder story" beats "You NEED to feature this."
- **Following up more than twice** — after 2 follow-ups, the pitch is not a fit for this journalist at this time. Move on.
- **Pitching the wrong beat** — a streetwear media writer covers product, culture, and founders. A business journalist covers funding and revenue. Don't pitch the founder story to a business reporter without a business hook.

---

## Recovery

- **No verifiable stats available:** Lead with story. The Corey Foster / Oakland / concrete-to-luxury narrative is genuinely pitchable without metrics. "We've fulfilled orders" is more credible than a made-up number.
- **Pitch gets no response after 2 follow-ups:** The angle or publication is not a fit right now. Rework the angle (try Trend instead of Story, or try a local Bay Area outlet instead of national streetwear media) and revisit with a new pitch in 60 days.
- **Journalist responds but wants a press release:** Send the press release as a follow-up. First contact is always a pitch; materials come on request.
- **Journalist asks for exclusivity:** Evaluate against your timeline. Offering a 48-72 hour exclusive before wide release is standard and acceptable. Do not offer exclusivity past the drop date.
- **Pitch gets a "not now" response:** This is a win — they acknowledged you. Reply with a one-line thank-you and an invitation to reconnect when they're covering the beat. Add to the 90-day revisit queue.
