---
name: skyyrose-social-community-moderation
description: "Designs and runs the moderation system for SkyyRose brand communities — rules, escalation ladder, moderator guidelines, automated filters, and appeals — so The Concrete Garden stays culturally safe and brand-true."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — Community Moderation

## When to Use This Skill

- Writing or revising the moderation rules for The Concrete Garden (Discord or Circle)
- Building the escalation ladder for violations — what gets a redirect vs. a ban
- Training community champions (volunteer mods) on how to enforce rules
- Configuring keyword filters and automated moderation for the SkyyRose community
- Responding to an active moderation incident in the community
- Setting up the moderation log and appeals process

**DO NOT** use this for launching a new community from scratch (use `skyyrose-social-community-launch`), for writing the public-facing platform guidelines (use `skyyrose-social-platform-community-guidelines`), or for handling a brand-level crisis that has gone beyond the community walls (use `skyyrose-social-crisis-comms`).

---

## Brand Canon (non-negotiable)

- **Tagline (exact):** `` — Corey built this brand from Oakland. The community is an extension of that. Moderation must reflect the same earned, direct energy — not corporate stiffness.
- **Culture is not decorative.** SkyyRose is a Black-owned Oakland brand. Any disrespect toward Black culture, The Town, or community members gets removed immediately — no warnings, no debate.
- **No hype-merchant energy.** Mods don't generate artificial excitement. They hold space. Quiet consistency beats public drama.
- **Founder canon: no related-products cross-sell.** The community is not a sales floor. A member who only posts purchase links gets redirected; a spammer gets removed.
- **Collection voice never cross-attributed.** If a mod example message references a collection, use that collection's correct register (Black Rose = armor; Love Hurts = raw passion/bloodline; Signature = standard-setting). Never mix.
- Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## Phase 1: Brief

### Required Inputs

| Input | What to Ask | Default |
|-------|------------|---------|
| **Community platform** | Discord, Circle, or other? | Discord |
| **Community size** | Current member count? | Under 500 |
| **Mod team** | How many moderators (including community champions)? | 1 founder + 2 champions |
| **Current issues** | Any active moderation problems prompting this? | Proactive — no active issue |
| **Tone** | Strict enforcement or lighter touch? | Firm but culturally warm |
| **Tier** | Is this a free community or gated/paid founding tier? | Gated founding tier |

**GATE: Confirm brief before building guidelines.**

---

## Phase 2: Outline

```
1. Community Standards — the actual rules, written for members
2. Violation Categories — severity tiers with SkyyRose-specific examples
3. Escalation Procedures — exact steps per severity level
4. Moderator Guidelines — principles, decision framework, what mods never do
5. Automated Moderation — keyword filters, link holds, new-member restrictions
6. Appeals Process — how members contest decisions
```

**GATE: Approve outline before writing.**

---

## Phase 3: Build the System

### 1. Community Standards (member-facing)

```
## The Concrete Garden — Community Standards

These are the rules. They're short because they should be obvious to the
kind of people who belong here.

Rule 1: Real talk, real respect
  Disagree with ideas. Never attack people. This space includes members from
  all walks of Oakland and beyond — treat everyone the way you'd want to be
  treated in The Town.

Rule 2: Keep drops private
  Early access info (unreleased products, pre-order windows, pricing) stays
  inside these walls until the brand goes public. Leaking kills the advantage
  for everyone.

Rule 3: No spam, no poaching
  Drop a link to your work when it's genuinely relevant — not as an ad. Do
  not DM members with unsolicited pitches or services. This isn't a marketplace.

Rule 4: Stay in your channel
  Each channel has a purpose. Fit pics go in #fit-pics. Product feedback goes
  in #feedback. Using the right channel keeps the conversation valuable.

Rule 5: Culture is not a costume
  This is a Black-owned Oakland brand. Disrespect toward Black culture, The
  Town, or any member of this community will result in immediate removal.
  No warnings. No debate.

Rule 6: The founding member compact
  If you're a founding member, you helped build this. Use that status to
  model the culture, not exploit it. Founding member privileges can be revoked.
```

### 2. Violation Categories

```
## Violation Severity Levels

| Level    | Type                  | SkyyRose Examples                                          | Action                      |
|----------|-----------------------|------------------------------------------------------------|-----------------------------|
| Low      | Guideline friction    | Fit pic posted in #general, off-topic question in #feedback| Friendly channel redirect    |
| Medium   | Rule violation        | Repeated self-promo links, minor disrespect, drop leak attempt | Warning DM + content removed |
| High     | Serious violation     | Sustained harassment of a member, aggressive DM campaign   | Mute + founder review        |
| Critical | Zero tolerance        | Cultural disrespect (Rule 5), threats, doxxing, scams      | Immediate permanent ban      |
```

### 3. Escalation Procedures

```
## Escalation Playbook

### Low — Guideline Friction
1. Reply publicly with a warm redirect:
   "Hey [Name] — this is great but it'll get more eyes in #[correct-channel].
    Want to repost it there?"
2. If the same behavior repeats after the redirect → move to Medium.
3. No formal warning unless it continues after the redirect DM.

### Medium — Rule Violation
1. Remove or hide the offending content.
2. Send a private DM within 30 minutes:
   "Hey [Name] — I removed your post because [specific rule].
    What we'd love to see: [guidance]. No hard feelings — just keeping this
    space valuable for everyone who's in it. — [Mod name]"
3. Log the incident in the moderation log (see below).
4. Second offense: formal warning via DM. State clearly: next violation = mute.

### High — Serious Violation
1. Immediately mute the member (temporary restriction, platform-dependent).
2. Remove all offending content.
3. Investigate context: was this provoked? Is there a pattern in their history?
4. Escalate to Corey (or founding mod) within 1 hour. Founder decides: formal
   warning, temporary ban (7-30 days), or permanent ban.
5. Communicate the decision to the member via DM with clear, calm reasoning.
6. If the incident was public, post a brief note in the channel:
   "Moderation action was taken. Community standards are here: #welcome"

### Critical — Zero Tolerance
1. Immediate permanent ban. No warnings, no review delay.
2. Remove all content from the violating member.
3. If the incident involved Rule 5 (cultural disrespect): post a brief,
   direct acknowledgment in #general in Corey's voice or a mod's voice:
   "Someone crossed a line that doesn't exist for debate here. They're gone.
    This community is built on respect for The Town and for each other. Full stop."
4. If threats or illegal activity: report to the platform and document.
5. Do not publicly detail who was removed — name the rule, not the person.
```

### 4. Moderator Guidelines

```
## How SkyyRose Mods Operate

Principles:
  - Be consistent. Apply the same standard to a founding member as to a new member.
  - Assume confusion before malice. Most low-level violations are accidents.
  - Be firm and calm. Never hostile. The brand is Oakland-direct, not confrontational.
  - Document everything. Undocumented decisions are invisible to the next mod on shift.
  - Never moderate when reactive. If something made you angry, wait 10 minutes before
    drafting a response.
  - Culture violations (Rule 5) are the exception — act immediately, no cooling period.

Decision Framework:
  1. Is this a rule violation? → No: leave it. Yes: continue.
  2. Is someone being harmed or disrespected? → Yes: act immediately (mute/ban).
  3. Is this a first offense? → Yes: redirect or friendly DM.
  4. Was it intentional? → Accidents get more grace; patterns do not.
  5. Culture violation (Rule 5)? → Permanent ban. Escalate after, not before.
  6. Unsure? → Escalate to Corey or the founding mod. Never guess on edge cases.

What mods NEVER do:
  - Engage in public arguments with rule violators — always move to DMs
  - Make decisions based on personal relationships with members
  - Share moderation discussions outside the mod team
  - Moderate their own conflicts — hand off to another mod or Corey
  - Tease or hint at pending bans publicly — communicate privately first
  - Use community champion privileges to push personal content
```

### 5. Automated Moderation

```
## Automation Configuration

| Tool / Feature            | What It Does                                 | Platform           |
|---------------------------|----------------------------------------------|--------------------|
| Keyword filter            | Auto-flag or hold posts with banned terms    | Discord AutoMod    |
| Link hold for new members | Posts with links go to mod queue for 7 days  | Discord            |
| New member slowdown       | 10-minute posting delay for first 48 hours   | Discord            |
| Auto-welcome DM           | Sends onboarding message on join             | Discord / Circle   |
| Report system             | Members can flag content for mod review      | All platforms      |

Keyword filter list (starting set — review monthly):
  - Common slurs (platform default lists)
  - "DM me for details" / "check my bio" / "link below"
  - Competitor brand names (optional — evaluate quarterly)
  - Drop-leak trigger phrases: "going public", "I got the link", "early access code"

Do NOT auto-ban on keyword matches. Auto-flag for mod review. Context matters.
```

### 6. Appeals Process

```
## Member Appeals

If a member believes a moderation action was unfair:
  1. DM any mod other than the one who took the action (if possible)
  2. State what happened and why they disagree — no appeals accepted over a week
     after the action
  3. Mod team reviews within 48 hours
  4. Decision communicated via DM with reasoning
  5. Corey has final say on contested appeals

Appeals NOT available for:
  - Cultural disrespect violations (Rule 5)
  - Threats, doxxing, or illegal activity
  - Drop leaks (founding member compact violation)

Tone on appeals: honest and fair. If the mod made a mistake, acknowledge it.
Founding members who are wrongly banned should have their status restored.
```

### 7. Moderation Log

```
## Moderation Log Template

| Date       | Member      | Violation         | Severity | Action Taken          | Mod        | Notes                         |
|------------|-------------|-------------------|----------|-----------------------|------------|-------------------------------|
| 2026-06-01 | @handle     | Off-topic post    | Low      | Channel redirect (DM) | @champmod  | First offense, responded well |
| 2026-06-03 | @handle2    | Repeated promo    | Medium   | Warning DM + removal  | @champmod  | Second offense — logged       |
```

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Generate a moderation DM for a medium-level violation
mod_dm = agent.generate_post(
    sku=None,
    platform="discord",
    post_type="moderation_dm",
    context={
        "violation_level": "medium",
        "rule": "repeated_self_promo",
        "collection_context": None,
        "tone": "firm_warm"
    }
)
print(mod_dm.caption)

# Generate a public acknowledgment post after a critical-level removal
public_ack = agent.generate_post(
    sku=None,
    platform="discord",
    post_type="moderation_public_ack",
    context={
        "violation_level": "critical",
        "rule": "cultural_disrespect",
        "channel": "general"
    }
)
print(public_ack.caption)
```

```bash
# Smoke-test the moderation content type via the social venture
python -m skyyrose.elite_studio.ventures.social smoke \
  --sku none \
  --post-type moderation_dm \
  --platform discord
```

```json
// Moderation log entry schema (append to moderation-log.json)
{
  "date": "2026-06-01",
  "member_handle": "@example_handle",
  "violation_rule": "rule_3_spam",
  "severity": "medium",
  "action": "warning_dm_content_removed",
  "moderator": "@champmod",
  "notes": "Second self-promo offense this week. Warned clearly.",
  "appealed": false,
  "resolved": true
}
```

---

## Example: Moderating a Drop-Leak Attempt During BLACK Rose Crewneck Pre-Order

**Scenario:** A founding member posts in #general: "Yo the Black Rose crewneck pre-order link dropped — here it is for everyone [link]" — 3 days before the public launch. The early access window was only shared in #early-access.

**Severity:** Medium → escalates to High (founding member compact violation).

**Steps:**
1. Remove the post immediately.
2. Send a DM (mod voice, Black Rose register — armor/defiance, not anger):
   > "Hey [Name] — I had to pull your post. #early-access content is under a founding member compact — that link doesn't go public until [date]. This is your first warning; a second one ends your founding member status. We want you here. Just need you to hold the line."
3. Log the incident.
4. If this member was the source who leaked outside the server: escalate to Corey. Founding member status revoked. Permanent ban at Corey's discretion.

**Collection voice check:** Firm, specific, no hype. No "🔥 DROP LEAKED 🔥" energy. Oakland-direct.

---

## Anti-Patterns

- **Moderating in public** — a public argument with a rule violator turns a small violation into a community spectacle. Always move to DMs immediately.
- **Inconsistent enforcement** — banning a new member for what a founding member gets a redirect on destroys trust faster than any violation. Same rule, same standard.
- **Over-moderation** — removing every slightly off-topic post kills spontaneity and makes The Concrete Garden feel like a corporate FAQ. Reserve action for actual violations.
- **No moderation log** — undocumented decisions mean repeat offenders slip through and "you were warned before" becomes unprovable. Log every action.
- **Using Rule 5 as a catch-all** — cultural disrespect has a specific meaning in this community. Do not invoke it for ordinary rudeness that should be handled as Medium. Reserve it for genuine cultural harm.
- **Moderating emotionally** — if a post made a mod angry, the mod should flag it, step away, and let another mod handle it. Reactive moderation produces bad decisions.
- **Ignoring the appeals process** — members who appeal and never hear back become the community's loudest critics. 48-hour turnaround is a commitment, not a suggestion.
- **Public naming of removed members** — acknowledging that moderation action was taken is appropriate; naming the removed member publicly is not. Name the rule, not the person.
- **Hype-adjacent mod messages** — a mod who writes "Don't miss the early access drop in #early-access 🔥🔥" is not modding, they're marketing. That's not the mod's role.

---

## Recovery

- **Community is already toxic before a moderation system existed:** Post the new standards, announce a fresh start in #announcements in Corey's voice, and enforce immediately and consistently. Some founding members may leave — that is acceptable. The ones who stay will define the community's culture.
- **Mods disagree on a decision:** Use the decision framework in section 4. If the framework doesn't resolve it, Corey has final say. Document the gray area and update the playbook so the next case is clearer.
- **Member backlash against a moderation decision:** Share the reasoning in DMs — never argue publicly. If the decision was correct, stand by it calmly. If the mod made a mistake, acknowledge it honestly and restore any revoked access.
- **Too many violations to handle (community scaled fast):** Elevate 1-2 additional community champions immediately. Add more automated filters. Do not let the backlog grow — unresolved violations set the wrong precedent.
- **Solo moderation burnout:** Build the Community Champion pipeline from day one (see `skyyrose-social-community-launch`). One founder cannot moderate a 400-member community alone. Two trained champions + AutoMod handles 90% of cases.
- **A moderator becomes the problem (power-tripping or personal enforcement):** Remove their mod role privately, notify Corey, and audit their last 30 decisions for patterns. Correct any actions that were outside the guidelines.
