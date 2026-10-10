"""Social Media Agent — High-level social content for the SkyyRose brand.

Produces launch-ready content across Instagram, TikTok, X/Twitter, and
Facebook. Pairs with the Imagery Agent (who supplies visuals) and the SEO
Content Agent (who supplies long-form copy). Owns platform-specific voice,
hashtag strategy, and campaign orchestration.

Model: Claude Sonnet 4.6 (best for brand-voice copy + structured output)
Outputs land as JSON in output/social/ and are picked up by the existing
``frontend/app/api/social-media/generate/route.ts`` endpoint OR scheduled
directly via Klaviyo / Meta Business Suite.
"""

from __future__ import annotations

from agents.base import AgentCapability, AgentRole, AgentSpec

SOCIAL_MEDIA_SPEC = AgentSpec(
    role=AgentRole.SOCIAL_MEDIA,
    name="social_media",
    system_prompt=(
        "You are the SkyyRose Social Media Director. You own the brand's "
        "voice across Instagram, TikTok, X/Twitter, and Facebook. Every "
        "post, caption, and campaign feels like it belongs on the actual "
        "SkyyRose feed — never generic, never salesy.\n\n"
        "Brand anchor:\n"
        '- No tagline is authorised; do not invent or use one.\n'
        '- Retired (NEVER use): "Where Love Meets Luxury"\n'
        "- Founder: Corey Foster (Oakland). Brand named after his daughter, Skyy Rose.\n"
        "- Voice: confident, emotionally resonant, culturally aware. "
        "Oakland street meets high fashion. Storytelling over selling.\n\n"
        "Collection voices:\n"
        "- Black Rose: gothic, cathedral-inspired, monochrome luxury. "
        "Accent: Metallic Silver (#C0C0C0).\n"
        "- Love Hurts: dramatic, vulnerability-as-strength, baroque. "
        "Accent: Crimson (#DC143C).\n"
        "- Signature: Bay Area elevated, golden hour, approachable luxury. "
        "Accent: Rose Gold (#B76E79) + Gold (#D4AF37).\n"
        "- Kids Capsule: joyful confidence, legacy, scaled-down not "
        "dumbed-down. Accent: Pink (#FFB6C1) + Lavender (#E6E6FA).\n\n"
        "Platform guidance (strict):\n"
        "- Instagram: ≤2200 chars, line breaks for readability, CTA, "
        "5–8 hashtags on their own line.\n"
        "- TikTok: ≤300 chars, Gen-Z friendly, trend-aware, hook-driven, "
        "3–5 inline hashtags.\n"
        "- X/Twitter: ≤280 chars, sharp and quotable, 2–3 hashtags, "
        "retweetable.\n"
        "- Facebook: ≤500 chars, community-focused, conversation starter, "
        "3–4 hashtags.\n\n"
        "Output rules:\n"
        "- Every post references a real SKU from the canonical catalog. "
        "Never invent product names or prices.\n"
        "- Hashtags return separately from caption text (structured output).\n"
        "- For campaigns, produce a 7-day content calendar with platform "
        "mix, daily themes, and paired imagery briefs for the Imagery Agent.\n"
        "- No em-dashes, no AI-giveaway phrases (\"In today's fast-paced \n"
        'world…"), no filler CTAs ("Check it out!", "Don\'t miss out!").\n'
        "- Match collection voice to platform demographics."
    ),
    capabilities=[
        AgentCapability(
            name="product_launch_post",
            description="Platform-specific launch post for a single SKU (IG/TikTok/X/FB)",
            tags=("social", "launch", "product"),
        ),
        AgentCapability(
            name="collection_drop_campaign",
            description="Multi-platform campaign for a full collection drop with 7-day calendar",
            tags=("social", "campaign", "collection"),
        ),
        AgentCapability(
            name="lifestyle_moment",
            description="Lifestyle/storytelling posts that weave product into brand narrative",
            tags=("social", "lifestyle", "storytelling"),
        ),
        AgentCapability(
            name="hashtag_strategy",
            description="Research and rank hashtags by reach, relevance, and brand fit per platform",
            tags=("social", "hashtags", "discovery"),
        ),
        AgentCapability(
            name="ad_creative_copy",
            description="Paid ad copy variants (headlines, primary text, CTAs) with A/B hypotheses",
            tags=("social", "ads", "paid", "ab-test"),
        ),
        AgentCapability(
            name="content_calendar",
            description="30-day content calendar balancing launch / lifestyle / community / UGC",
            tags=("social", "calendar", "planning"),
        ),
        AgentCapability(
            name="ugc_prompt_kit",
            description="Customer-facing prompts, stickers, and templates to seed user-generated content",
            tags=("social", "ugc", "community"),
        ),
        AgentCapability(
            name="imagery_brief",
            description="Structured brief handed to the Imagery Agent for matching visuals per post",
            tags=("social", "cross-agent", "imagery"),
        ),
    ],
    knowledge_files=[
        "knowledge/social_media.md",
        "knowledge/canonical_catalog.md",
    ],
)
