/**
 * Social Media Pipeline - Post Generation Route
 *
 * POST /api/social-media/generate
 *   Body: { product_sku: string, platform: string, content_type?: string }
 *   Returns: SocialPost
 *
 * Uses Claude (via Vercel AI SDK) to generate platform-optimized captions
 * with SkyyRose brand voice. Falls back to template-based generation when
 * ANTHROPIC_API_KEY is not set.
 */

import { NextRequest, NextResponse } from 'next/server';
import { withAuth } from '@/lib/api-auth';
import { hasLlmKey } from '@/lib/social-media/config';
import { getProduct as getCatalogProduct } from '@/lib/catalog';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GenerateRequest {
  product_sku: string;
  platform: 'instagram' | 'tiktok' | 'twitter' | 'facebook';
  content_type?: string;
}

interface SocialPost {
  id: string;
  platform: string;
  content_type: string;
  caption: string;
  hashtags: string[];
  media_urls: string[];
  product_sku: string;
  collection: string;
  scheduled_at: string | null;
  published_at: string | null;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  engagement: Record<string, number>;
}

// ---------------------------------------------------------------------------
// Collection descriptions for brand context
// ---------------------------------------------------------------------------

const COLLECTION_DESCRIPTIONS: Record<string, string> = {
  'black-rose':
    'The Black Rose collection is a bold statement of identity and resilience. Cathedral-inspired, it blends dark luxury with streetwear edge. Think gothic romance meets modern power.',
  'love-hurts':
    'Love Hurts explores the beauty in vulnerability. Castle-inspired pieces with a raw emotional edge - where heartbreak becomes art and fashion becomes armor.',
  signature:
    'The Signature collection is the quintessential SkyyRose experience. A city-tour aesthetic that blends upscale comfort with effortless cool. Golden hour vibes.',
};

// ---------------------------------------------------------------------------
// Platform-specific caption guidance
// ---------------------------------------------------------------------------

const PLATFORM_GUIDANCE: Record<string, string> = {
  instagram:
    'Write an Instagram caption (max 2200 chars). Use line breaks for readability. Include a call-to-action. End with 5-8 relevant hashtags on their own line. Aesthetic and aspirational tone.',
  tiktok:
    'Write a TikTok caption (max 300 chars). Punchy, Gen-Z friendly, trend-aware. Include 3-5 hashtags inline. Keep it conversational and hook-driven.',
  twitter:
    'Write an X/Twitter post (max 280 chars). Sharp, quotable, and attention-grabbing. Include 2-3 hashtags. Make it retweetable.',
  facebook:
    'Write a Facebook post (max 500 chars). Warm, community-focused, inviting. Include a question or conversation starter. End with 3-4 hashtags.',
};

// ---------------------------------------------------------------------------
// Template fallback (no LLM key)
// ---------------------------------------------------------------------------

function generateFromTemplate(
  product: { label: string; collection: string },
  platform: string,
  contentType: string
): { caption: string; hashtags: string[] } {
  const collectionLabel = product.collection.replace(/-/g, ' ');
  const collectionTag = `#${product.collection.replace(/-/g, '')}`;

  const baseHashtags = ['#SkyyRose', '#LuxuryStreetwear', collectionTag];

  const templates: Record<string, Record<string, string>> = {
    product_launch: {
      instagram: `Introducing ${product.label} from the ${collectionLabel} collection.\n\nAvailable now at skyyrose.co\n\n${baseHashtags.join(' ')} #NewDrop #FashionForward`,
      tiktok: `${product.label} just dropped and it's giving EVERYTHING. ${collectionLabel} collection hits different. Link in bio ${baseHashtags.slice(0, 3).join(' ')} #NewDrop`,
      twitter: `${product.label} is here. ${collectionLabel} collection.\n\nskyyrose.co ${baseHashtags.slice(0, 2).join(' ')}`,
      facebook: `We're thrilled to introduce the ${product.label} from our ${collectionLabel} collection.\n\nWhich piece speaks to you? Drop a comment below and let us know.\n\nShop now: skyyrose.co\n\n${baseHashtags.slice(0, 3).join(' ')}`,
    },
    collection_drop: {
      instagram: `The ${collectionLabel} collection is a mood.\n\n${product.label} embodies everything SkyyRose stands for -- the intersection of love and luxury, where every piece tells your story.\n\nLink in bio.\n\n${baseHashtags.join(' ')} #CollectionDrop`,
      tiktok: `${collectionLabel} collection is out NOW. ${product.label} is that piece you didn't know you needed. ${baseHashtags.slice(0, 3).join(' ')}`,
      twitter: `The ${collectionLabel} collection just dropped. ${product.label} is the one. ${baseHashtags.slice(0, 2).join(' ')}`,
      facebook: `Our ${collectionLabel} collection has arrived, and ${product.label} is a standout.\n\nWhat do you think? Let us know in the comments!\n\n${baseHashtags.slice(0, 3).join(' ')}`,
    },
    lifestyle: {
      instagram: `Living in ${product.label}.\n\nThe ${collectionLabel} collection was made for moments like these. Luxury you can feel. Style you can own.\n\n${baseHashtags.join(' ')} #SkyyRoseLifestyle`,
      tiktok: `POV: you just unboxed the ${product.label} and your fit game changed forever ${baseHashtags.slice(0, 3).join(' ')} #OOTD`,
      twitter: `Some pieces change how you walk into a room. ${product.label} is one of them. ${baseHashtags.slice(0, 2).join(' ')}`,
      facebook: `How do you style your ${product.label}? We'd love to see your looks!\n\nTag us in your photos for a chance to be featured.\n\n${baseHashtags.slice(0, 3).join(' ')}`,
    },
  };

  const typeTemplates = templates[contentType] ?? templates.product_launch;
  const caption = typeTemplates[platform] ?? typeTemplates.instagram;

  const platformHashtags: Record<string, string[]> = {
    instagram: [...baseHashtags, '#NewDrop', '#FashionForward', '#OOTD', '#StreetLuxury'],
    tiktok: [...baseHashtags.slice(0, 3), '#NewDrop', '#FashionTok'],
    twitter: baseHashtags.slice(0, 3),
    facebook: [...baseHashtags.slice(0, 3), '#Fashion'],
  };

  return {
    caption,
    hashtags: platformHashtags[platform] ?? baseHashtags,
  };
}

// ---------------------------------------------------------------------------
// LLM-powered generation (Vercel AI SDK + Claude)
// ---------------------------------------------------------------------------

async function generateWithLlm(
  product: { label: string; collection: string },
  platform: string,
  contentType: string
): Promise<{ caption: string; hashtags: string[] }> {
  // Dynamic import to avoid build-time issues when the key is absent
  const { generateText } = await import('ai');
  const { anthropic } = await import('@ai-sdk/anthropic');

  const collectionDesc =
    COLLECTION_DESCRIPTIONS[product.collection] ?? `The ${product.collection} collection by SkyyRose.`;

  const systemPrompt = `You are the social media voice of SkyyRose, a luxury streetwear fashion brand.
No active brand tagline. Do not invent a replacement or reuse retired slogans.
Brand color: Rose Gold (#B76E79)
Tone: Confident, aspirational, emotionally resonant, culturally aware. Never generic or salesy.
The brand bridges high fashion and streetwear with deep emotional storytelling.

Collection context: ${collectionDesc}

Rules:
- Always weave in the brand voice naturally
- Never use generic filler phrases like "Check it out!" or "Don't miss out!"
- Each post should feel like it belongs on the brand's actual feed
- Hashtags should be returned separately, not embedded in the caption text
- Return ONLY a JSON object with "caption" and "hashtags" keys
- "hashtags" should be an array of strings, each starting with #`;

  const userPrompt = `Generate a ${contentType.replace(/_/g, ' ')} social media post for the product "${product.label}" from the "${product.collection.replace(/-/g, ' ')}" collection.

Platform: ${platform}
${PLATFORM_GUIDANCE[platform] ?? ''}

Return JSON only: { "caption": "...", "hashtags": ["#...", ...] }`;

  const result = await generateText({
    model: anthropic('claude-sonnet-4-20250514'),
    system: systemPrompt,
    prompt: userPrompt,
    maxOutputTokens: 1024,
    temperature: 0.8,
  });

  // Parse the LLM response -- it should be JSON
  const text = result.text.trim();
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    // Fallback: treat the whole response as caption
    return {
      caption: text,
      hashtags: ['#SkyyRose'],
    };
  }

  const parsed = JSON.parse(jsonMatch[0]) as { caption: string; hashtags: string[] };
  return {
    caption: parsed.caption ?? text,
    hashtags: Array.isArray(parsed.hashtags) ? parsed.hashtags : ['#SkyyRose'],
  };
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

async function postHandler(request: NextRequest) {
  try {
    const body = (await request.json()) as GenerateRequest;

    // Validate required fields
    if (!body.product_sku?.trim()) {
      return NextResponse.json(
        { success: false, error: 'product_sku is required' },
        { status: 400 }
      );
    }
    if (!body.platform?.trim()) {
      return NextResponse.json(
        { success: false, error: 'platform is required' },
        { status: 400 }
      );
    }

    const validPlatforms = ['instagram', 'tiktok', 'twitter', 'facebook'];
    if (!validPlatforms.includes(body.platform)) {
      return NextResponse.json(
        { success: false, error: `Invalid platform. Must be one of: ${validPlatforms.join(', ')}` },
        { status: 400 }
      );
    }

    const canonical = getCatalogProduct(body.product_sku);
    if (!canonical) {
      return NextResponse.json(
        { success: false, error: `Unknown product SKU: ${body.product_sku}` },
        { status: 404 }
      );
    }
    const product = { label: canonical.name, collection: canonical.collection };

    const contentType = body.content_type ?? 'product_launch';
    let caption: string;
    let hashtags: string[];
    let llm_generated = false;

    if (hasLlmKey()) {
      try {
        const result = await generateWithLlm(product, body.platform, contentType);
        caption = result.caption;
        hashtags = result.hashtags;
        llm_generated = true;
      } catch (llmError) {
        // LLM failed -- fall back to templates
        const fallback = generateFromTemplate(product, body.platform, contentType);
        caption = fallback.caption;
        hashtags = fallback.hashtags;
      }
    } else {
      const result = generateFromTemplate(product, body.platform, contentType);
      caption = result.caption;
      hashtags = result.hashtags;
    }

    const post: SocialPost = {
      id: generateId(),
      platform: body.platform,
      content_type: contentType,
      caption,
      hashtags,
      media_urls: [],
      product_sku: body.product_sku,
      collection: product.collection,
      scheduled_at: null,
      published_at: null,
      status: 'draft',
      engagement: {},
    };

    return NextResponse.json({
      success: true,
      llm_generated,
      post,
    });
  } catch (error) {
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const POST = withAuth(postHandler);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function generateId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).slice(2, 8);
  return `sp_${timestamp}_${random}`;
}
