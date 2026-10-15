import { beforeEach, describe, expect, it, vi } from 'vitest';
import path from 'node:path';

vi.mock('server-only', () => ({}));
vi.mock('node:fs', () => ({ statSync: vi.fn() }));
vi.mock('@/lib/catalog', () => ({ getCatalog: () => [] }));

import { statSync } from 'node:fs';
import * as collections from '@/lib/collections';
import { getAllEnrichedCollections, getEnrichedCollection } from '@/lib/catalog-server';

const stat = vi.mocked(statSync);

beforeEach(() => {
  vi.restoreAllMocks();
  stat.mockReset();
});

describe('collection hero availability', () => {
  it('retains existing local images and checks their public path', () => {
    stat.mockReturnValue({ isFile: () => true } as ReturnType<typeof statSync>);
    const result = getEnrichedCollection('black-rose');
    expect(result?.heroImageAvailable).toBe(true);
    expect(result?.heroImage).toBe(collections.COLLECTIONS['black-rose'].heroImage);
    expect(stat).toHaveBeenCalledWith(path.resolve('public/images/scenes/black-rose-garden.jpg'));
  });

  it('marks all absent local heroes unavailable without changing scene identities', () => {
    stat.mockImplementation(() => { throw Object.assign(new Error('missing'), { code: 'ENOENT' }); });
    for (const result of getAllEnrichedCollections()) {
      const original = collections.COLLECTIONS[result.slug];
      expect(result.heroImageAvailable).toBe(false);
      expect(result.heroImage).toBe(original.heroImage);
      expect(result.scenes.map(scene => scene.id)).toEqual(original.scenes.map(scene => scene.id));
    }
  });

  it('does not treat a directory as an image', () => {
    stat.mockReturnValue({ isFile: () => false } as ReturnType<typeof statSync>);
    expect(getEnrichedCollection('black-rose')?.heroImageAvailable).toBe(false);
  });

  it('preserves remote images without a local lookup', () => {
    const original = collections.COLLECTIONS['black-rose'];
    vi.spyOn(collections, 'getCollection').mockReturnValue({ ...original, heroImage: 'https://images.example.test/hero.webp' });
    expect(getEnrichedCollection('black-rose')?.heroImageAvailable).toBe(true);
    expect(stat).not.toHaveBeenCalled();
  });

  it('checks availability even when a collection has no scenes', () => {
    const original = collections.COLLECTIONS['black-rose'];
    vi.spyOn(collections, 'getCollection').mockReturnValue({ ...original, scenes: [] });
    stat.mockImplementation(() => { throw new Error('missing'); });
    expect(getEnrichedCollection('black-rose')).toMatchObject({ heroImageAvailable: false, scenes: [] });
  });

  it('rejects a local image path escaping public', () => {
    const original = collections.COLLECTIONS['black-rose'];
    vi.spyOn(collections, 'getCollection').mockReturnValue({ ...original, heroImage: '/images/../../outside.webp' });
    expect(getEnrichedCollection('black-rose')?.heroImageAvailable).toBe(false);
    expect(stat).not.toHaveBeenCalled();
  });
});
