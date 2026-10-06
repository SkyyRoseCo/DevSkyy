"""
Expand SkyyRose brand voice dataset from 5 to 150+ examples using Claude API.

Categories:
- Product descriptions (30 per collection × 3 = 90)
- Social media posts (20 examples)
- Email marketing copy (15 examples)
- Customer service responses (15 examples)
- Brand storytelling (10 examples)

Total: 150 examples
"""

import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment")

# SkyyRose brand voice system prompt
SYSTEM_PROMPT = """You are SkyyRose's brand voice - a luxury streetwear brand from Oakland, California.

Brand Guidelines:
- Tone: Sophisticated yet accessible, bold yet elegant
- Style: Poetic, evocative, with street culture authenticity
- Colors: Rose gold (#B76E79), black (#1A1A1A), pastels
- Collections: Signature (classic), Black Rose (dark romantic), Love Hurts (edgy)

Always emphasize:
- Premium quality and craftsmanship
- Oakland heritage and authenticity
- Gender-neutral inclusivity
- Limited edition exclusivity
- Emotional connection through fashion

Never use: cheap, discount, basic, generic, mass-produced"""


# Product templates (90 examples: 30 per collection)
PRODUCT_PROMPTS = {
    "signature": [
        "Write a product description for a rose gold hoodie.",
        "Describe a premium Signature collection t-shirt.",
        "Create copy for a Signature collection joggers.",
        "Write about a rose gold bomber jacket.",
        "Describe a luxury Signature crewneck sweatshirt.",
        "Create a product page for Signature collection socks.",
        "Write about a rose gold baseball cap.",
        "Describe Signature collection sweatpants.",
        "Create copy for a premium Signature polo shirt.",
        "Write about a rose gold track jacket.",
        "Describe a Signature collection windbreaker.",
        "Create a product description for a rose gold tank top.",
        "Write about Signature collection cargo pants.",
        "Describe a premium rose gold vest.",
        "Create copy for a Signature collection beanie.",
        "Write about a rose gold long-sleeve tee.",
        "Describe Signature collection shorts.",
        "Create a product page for a rose gold zip-up hoodie.",
        "Write about Signature collection track pants.",
        "Describe a premium rose gold henley.",
        "Create copy for Signature collection gloves.",
        "Write about a rose gold windbreaker jacket.",
        "Describe a Signature collection cardigan.",
        "Create a product description for rose gold leggings.",
        "Write about Signature collection slides.",
        "Describe a premium rose gold turtleneck.",
        "Create copy for a Signature collection scarf.",
        "Write about a rose gold bucket hat.",
        "Describe Signature collection palazzo pants.",
        "Create a product page for a rose gold puffer jacket.",
    ],
    "black_rose": [
        "Describe the Black Rose collection aesthetic.",
        "Write a product description for a Black Rose hoodie.",
        "Create copy for Black Rose collection leather jacket.",
        "Write about a Black Rose graphic tee.",
        "Describe Black Rose collection jeans.",
        "Create a product page for Black Rose bomber jacket.",
        "Write about Black Rose collection cargo pants.",
        "Describe a Black Rose windbreaker.",
        "Create copy for a Black Rose crewneck.",
        "Write about Black Rose collection beanie.",
        "Describe a Black Rose long coat.",
        "Create a product description for Black Rose joggers.",
        "Write about Black Rose collection snapback.",
        "Describe a Black Rose zip-up hoodie.",
        "Create copy for Black Rose track pants.",
        "Write about a Black Rose denim jacket.",
        "Describe Black Rose collection shorts.",
        "Create a product page for Black Rose vest.",
        "Write about Black Rose collection gloves.",
        "Describe a Black Rose puffer jacket.",
        "Create copy for a Black Rose turtleneck.",
        "Write about Black Rose collection boots.",
        "Describe a Black Rose oversized tee.",
        "Create a product description for Black Rose sweatpants.",
        "Write about Black Rose collection cap.",
        "Describe a Black Rose trench coat.",
        "Create copy for Black Rose long-sleeve shirt.",
        "Write about a Black Rose hoodie dress.",
        "Describe Black Rose collection backpack.",
        "Create a product page for Black Rose sneakers.",
    ],
    "love_hurts": [
        "Create marketing copy for Love Hurts windbreaker.",
        "Write a product description for a Love Hurts hoodie.",
        "Describe Love Hurts collection graphic tee.",
        "Create copy for Love Hurts bomber jacket.",
        "Write about Love Hurts collection joggers.",
        "Describe a Love Hurts crewneck sweatshirt.",
        "Create a product page for Love Hurts track jacket.",
        "Write about Love Hurts collection cap.",
        "Describe Love Hurts sweatpants.",
        "Create copy for a Love Hurts zip-up hoodie.",
        "Write about Love Hurts collection shorts.",
        "Describe a Love Hurts long-sleeve tee.",
        "Create a product description for Love Hurts vest.",
        "Write about Love Hurts collection beanie.",
        "Describe a Love Hurts denim jacket.",
        "Create copy for Love Hurts cargo pants.",
        "Write about a Love Hurts tank top.",
        "Describe Love Hurts collection windbreaker pants.",
        "Create a product page for Love Hurts polo shirt.",
        "Write about Love Hurts collection slides.",
        "Describe a Love Hurts puffer jacket.",
        "Create copy for Love Hurts leggings.",
        "Write about a Love Hurts bucket hat.",
        "Describe Love Hurts collection turtleneck.",
        "Create a product description for Love Hurts scarf.",
        "Write about Love Hurts collection gloves.",
        "Describe a Love Hurts oversized hoodie.",
        "Create copy for Love Hurts track pants.",
        "Write about a Love Hurts cardigan.",
        "Describe Love Hurts collection sneakers.",
    ],
}

# Social media prompts (20 examples)
SOCIAL_MEDIA_PROMPTS = [
    "Write an Instagram caption for a new collection drop.",
    "Create a Twitter post announcing a limited restock.",
    "Write a Facebook post about Oakland heritage.",
    "Create an Instagram story text for behind-the-scenes content.",
    "Write a LinkedIn post about brand values.",
    "Create a Pinterest description for a product board.",
    "Write a TikTok video caption for a styling video.",
    "Create an Instagram carousel caption about craftsmanship.",
    "Write a Twitter thread intro about sustainability.",
    "Create a Facebook event description for a pop-up shop.",
    "Write an Instagram caption for customer spotlight.",
    "Create a Twitter post celebrating a milestone.",
    "Write a social post about community impact.",
    "Create an Instagram Reel caption for unboxing content.",
    "Write a social media poll question about preferences.",
    "Create a story highlight cover description.",
    "Write a social post introducing a collaboration.",
    "Create an Instagram caption for throwback content.",
    "Write a Twitter post responding to positive feedback.",
    "Create a social post announcing a giveaway.",
]

# Email marketing prompts (15 examples)
EMAIL_PROMPTS = [
    "Write a welcome email for new subscribers.",
    "Create an abandoned cart reminder email.",
    "Write a new collection launch email.",
    "Create a VIP early access email.",
    "Write a seasonal sale announcement email.",
    "Create a post-purchase thank you email.",
    "Write a restock notification email.",
    "Create a birthday discount email.",
    "Write a brand story email.",
    "Create a customer review request email.",
    "Write a style guide email.",
    "Create a limited edition drop announcement email.",
    "Write a win-back campaign email.",
    "Create a referral program email.",
    "Write a holiday gift guide email.",
]

# Customer service prompts (15 examples)
CUSTOMER_SERVICE_PROMPTS = [
    "Respond to a customer asking about sizing.",
    "Reply to an order tracking inquiry.",
    "Respond to a return request.",
    "Reply to a product recommendation request.",
    "Respond to a shipping delay complaint.",
    "Reply to a question about materials.",
    "Respond to a collaboration inquiry.",
    "Reply to a wholesale partnership request.",
    "Respond to a quality concern.",
    "Reply to a customization request.",
    "Respond to a gift wrapping inquiry.",
    "Reply to a pre-order question.",
    "Respond to an exchange request.",
    "Reply to a question about care instructions.",
    "Respond to a restock notification request.",
]

# Brand storytelling prompts (10 examples)
STORYTELLING_PROMPTS = [
    "Write about SkyyRose's Oakland origins.",
    "Describe the brand's design philosophy.",
    "Write about the inspiration behind the logo.",
    "Describe what the SkyyRose rose motif represents.",
    "Write about the brand's commitment to quality.",
    "Describe the vision for SkyyRose's future.",
    "Write about the cultural influences on the brand.",
    "Describe a day in the life at SkyyRose.",
    "Write about the brand's community involvement.",
    "Describe what makes SkyyRose different from other brands.",
]


async def generate_response(prompt: str, client: httpx.AsyncClient) -> str:
    """Generate a brand voice response using Claude API."""
    try:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]
    except Exception as e:
        print(f"Error generating response for '{prompt[:50]}...': {e}")
        return None


async def expand_dataset():
    """Generate 150+ brand voice examples."""
    print("=" * 70)
    print("  SKYYROSE BRAND VOICE DATASET EXPANSION")
    print("  Target: 150+ examples (from 5)")
    print("=" * 70)
    print()

    examples = []
    total_prompts = 0

    # Count total
    for collection_prompts in PRODUCT_PROMPTS.values():
        total_prompts += len(collection_prompts)
    total_prompts += len(SOCIAL_MEDIA_PROMPTS)
    total_prompts += len(EMAIL_PROMPTS)
    total_prompts += len(CUSTOMER_SERVICE_PROMPTS)
    total_prompts += len(STORYTELLING_PROMPTS)

    print(f"Total prompts to generate: {total_prompts}")
    print()

    async with httpx.AsyncClient() as client:
        # Generate product descriptions
        print("[1/5] Generating product descriptions (90)...")
        for collection, prompts in PRODUCT_PROMPTS.items():
            print(f"  → {collection.title()} collection ({len(prompts)} prompts)")
            for i, prompt in enumerate(prompts, 1):
                response = await generate_response(prompt, client)
                if response:
                    examples.append(
                        {
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": response},
                            ]
                        }
                    )
                print(f"    [{i}/{len(prompts)}] ✓", end="\r")
                await asyncio.sleep(0.5)  # Rate limiting
            print(f"    [{len(prompts)}/{len(prompts)}] ✓ Complete")

        # Generate social media posts
        print("\n[2/5] Generating social media posts (20)...")
        for i, prompt in enumerate(SOCIAL_MEDIA_PROMPTS, 1):
            response = await generate_response(prompt, client)
            if response:
                examples.append(
                    {
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response},
                        ]
                    }
                )
            print(f"  [{i}/{len(SOCIAL_MEDIA_PROMPTS)}] ✓", end="\r")
            await asyncio.sleep(0.5)
        print(f"  [{len(SOCIAL_MEDIA_PROMPTS)}/{len(SOCIAL_MEDIA_PROMPTS)}] ✓ Complete")

        # Generate email marketing copy
        print("\n[3/5] Generating email marketing copy (15)...")
        for i, prompt in enumerate(EMAIL_PROMPTS, 1):
            response = await generate_response(prompt, client)
            if response:
                examples.append(
                    {
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response},
                        ]
                    }
                )
            print(f"  [{i}/{len(EMAIL_PROMPTS)}] ✓", end="\r")
            await asyncio.sleep(0.5)
        print(f"  [{len(EMAIL_PROMPTS)}/{len(EMAIL_PROMPTS)}] ✓ Complete")

        # Generate customer service responses
        print("\n[4/5] Generating customer service responses (15)...")
        for i, prompt in enumerate(CUSTOMER_SERVICE_PROMPTS, 1):
            response = await generate_response(prompt, client)
            if response:
                examples.append(
                    {
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response},
                        ]
                    }
                )
            print(f"  [{i}/{len(CUSTOMER_SERVICE_PROMPTS)}] ✓", end="\r")
            await asyncio.sleep(0.5)
        print(f"  [{len(CUSTOMER_SERVICE_PROMPTS)}/{len(CUSTOMER_SERVICE_PROMPTS)}] ✓ Complete")

        # Generate brand storytelling
        print("\n[5/5] Generating brand storytelling (10)...")
        for i, prompt in enumerate(STORYTELLING_PROMPTS, 1):
            response = await generate_response(prompt, client)
            if response:
                examples.append(
                    {
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response},
                        ]
                    }
                )
            print(f"  [{i}/{len(STORYTELLING_PROMPTS)}] ✓", end="\r")
            await asyncio.sleep(0.5)
        print(f"  [{len(STORYTELLING_PROMPTS)}/{len(STORYTELLING_PROMPTS)}] ✓ Complete")

    # Save expanded dataset
    output_path = Path("datasets/skyyrose_brand_voice/train_expanded.jsonl")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")

    print()
    print("=" * 70)
    print("  DATASET EXPANSION COMPLETE")
    print("=" * 70)
    print(f"  Generated: {len(examples)} examples")
    print("  Original: 5 examples")
    print(f"  Expansion: {len(examples) / 5:.1f}x")
    print(f"  Saved to: {output_path}")
    print()

    return examples


if __name__ == "__main__":
    asyncio.run(expand_dataset())
