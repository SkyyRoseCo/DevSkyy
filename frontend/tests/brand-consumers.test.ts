import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';

const { session, catalog, llmKey, generateText } = vi.hoisted(() => ({
  session: vi.fn(),
  catalog: vi.fn(),
  llmKey: vi.fn(),
  generateText: vi.fn(),
}));
vi.mock('next-auth', () => ({ getServerSession: session }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/catalog', () => ({ getProduct: catalog }));
vi.mock('@/lib/social-media/config', () => ({ hasLlmKey: llmKey }));
vi.mock('ai', () => ({ generateText }));
vi.mock('@ai-sdk/anthropic', () => ({ anthropic: vi.fn(() => 'offline-mock') }));

import { POST } from '@/app/api/social-media/generate/route';

const retired = /luxury\s*grows\s*from\s*concrete|where\s*love\s*meets\s*luxury/i;
const platforms = ['instagram', 'tiktok', 'twitter', 'facebook'];
const contentTypes = ['product_launch', 'collection_drop', 'lifestyle'];

async function post(platform = 'instagram', content_type = 'product_launch') {
  const response = await POST(
    new NextRequest('http://localhost/api/social-media/generate', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ product_sku: 'fixture-sku', platform, content_type }),
    }),
    undefined
  );
  return { response, body: await response.json() };
}

describe('retired brand consumers', () => {
  beforeEach(() => {
    session.mockReset().mockResolvedValue({ user: { email: 'offline@example.invalid' } });
    catalog.mockReset().mockReturnValue({ name: 'Canonical fixture name', collection: 'black-rose' });
    llmKey.mockReset().mockReturnValue(false);
    generateText.mockReset();
  });

  it.each(platforms.flatMap(platform => contentTypes.map(type => [platform, type])))(
    'omits retired text and hashtags from %s %s templates',
    async (platform, type) => {
      const { response, body } = await post(platform, type);
      expect(response.status).toBe(200);
      expect(body.post.caption).toContain('Canonical fixture name');
      expect(JSON.stringify(body.post)).not.toMatch(retired);
      expect(body.llm_generated).toBe(false);
      expect(generateText).not.toHaveBeenCalled();
    }
  );

  it.each(['plain caption', '{"caption":"Canonical draft","hashtags":null}'])(
    'uses no retired hashtag in offline mocked LLM response fallback: %s',
    async text => {
      llmKey.mockReturnValue(true);
      generateText.mockResolvedValue({ text });
      const { body } = await post();
      expect(body.post.hashtags).toEqual(['#SkyyRose']);
      expect(JSON.stringify(body.post)).not.toMatch(retired);
      const request = generateText.mock.calls[0][0];
      expect(request.system).toContain('No active brand tagline');
      expect(request.system).not.toMatch(retired);
    }
  );

  it('falls back locally after a mocked provider error without retired text', async () => {
    llmKey.mockReturnValue(true);
    generateText.mockRejectedValue(new Error('offline mocked failure'));
    const { body } = await post();
    expect(body.llm_generated).toBe(false);
    expect(JSON.stringify(body.post)).not.toMatch(retired);
  });

  it('retains authentication and unknown-SKU denial', async () => {
    session.mockResolvedValue(null);
    expect((await post()).response.status).toBe(401);
    expect(catalog).not.toHaveBeenCalled();
    session.mockResolvedValue({ user: { email: 'offline@example.invalid' } });
    catalog.mockReturnValue(undefined);
    expect((await post()).response.status).toBe(404);
    expect(generateText).not.toHaveBeenCalled();
  });

  it('removes retired UI, metadata and collection defaults from the assigned files', () => {
    const files = [
      'app/(storefront)/HomePage.tsx',
      'app/admin/elite-studio/design/page.tsx',
      'app/admin/elite-studio/layout.tsx',
      'app/admin/elite-studio/page.tsx',
      'app/collections/CollectionsLanding.tsx',
      'app/collections/[slug]/CollectionExperience.tsx',
      'app/collections/layout.tsx',
      'app/collections/page.tsx',
      'app/page.tsx',
      'app/pre-order/PreOrderPage.tsx',
      'components/mascot/MascotBubble.tsx',
      'lib/collections.ts',
      'DEPLOYMENT.md',
    ];
    for (const file of files) {
      expect(fs.readFileSync(path.join(process.cwd(), file), 'utf8'), file).not.toMatch(retired);
    }
  });
});
