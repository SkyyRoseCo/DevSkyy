import { describe, expect, it, vi } from 'vitest';

import {
  createRunwayDryRunRateLimiter,
  RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS,
} from '../app/api/runway-dev/dry-run/rate-limit';

describe('Runway Dev dry-run distributed rate limiter', () => {
  it('allows one request per authenticated user per 60-second cooldown and then limits', async () => {
    const seenKeys = new Set<string>();
    const setIfAbsent = vi.fn(async (key: string, ttlSeconds: number) => {
      expect(ttlSeconds).toBe(RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS);
      if (seenKeys.has(key)) {
        return false;
      }
      seenKeys.add(key);
      return true;
    });
    const limit = createRunwayDryRunRateLimiter(setIfAbsent, 'test-hmac-secret');

    expect(await limit('Owner@Example.test')).toBe('allowed');
    expect(await limit('owner@example.test')).toBe('limited');
    expect(setIfAbsent).toHaveBeenCalledTimes(2);
    expect(setIfAbsent.mock.calls[0][0]).not.toContain('owner@example.test');
  });

  it('isolates users while keeping the route namespace fixed', async () => {
    const keys: string[] = [];
    const limit = createRunwayDryRunRateLimiter(async key => {
      keys.push(key);
      return true;
    }, 'test-hmac-secret');

    expect(await limit('first@example.test')).toBe('allowed');
    expect(await limit('second@example.test')).toBe('allowed');
    expect(keys[0]).not.toBe(keys[1]);
    expect(keys[0]).toMatch(/^devskyy:rate-limit:runway-dev:dry-run:v1:/);
  });

  it('fails closed if the shared store errors or authenticated identity is missing', async () => {
    const brokenLimit = createRunwayDryRunRateLimiter(async () => {
      throw new Error('store unavailable');
    }, 'test-hmac-secret');
    const store = vi.fn(async () => true);
    const missingIdentityLimit = createRunwayDryRunRateLimiter(store, 'test-hmac-secret');

    expect(await brokenLimit('owner@example.test')).toBe('unavailable');
    expect(await missingIdentityLimit(' ')).toBe('unavailable');
    expect(store).not.toHaveBeenCalled();
  });
});
