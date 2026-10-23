import { afterEach, describe, expect, it, vi } from 'vitest';
import { encode } from 'next-auth/jwt';
import { NextRequest } from 'next/server';

vi.mock('server-only', () => ({}));
import { authOptions } from '../lib/auth';
import { getBackendAccessToken } from '../lib/backend-session';

const jwt = authOptions.callbacks!.jwt!;
const session = authOptions.callbacks!.session!;
afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe('dashboard credential boundary', () => {
  it('keeps backend credentials out of public sessions', async () => {
    const result = await session({
      session: { user: { email: 'user@example.test' }, expires: '' },
      token: { accessToken: 'private', refreshToken: 'private-refresh', accessTokenExpiresAt: Date.now() + 60000 },
    } as unknown as Parameters<typeof session>[0]);
    expect(result).not.toHaveProperty('accessToken');
    expect(result).not.toHaveProperty('refreshToken');
  });
  it('marks an expired backend token without refreshing it', async () => {
    const fetcher = vi.fn();
    vi.stubGlobal('fetch', fetcher);
    const token = await jwt({
      token: { accessToken: 'private', accessTokenExpiresAt: Date.now() - 1 },
    } as unknown as Parameters<typeof jwt>[0]);
    expect(token.authError).toBe('BackendTokenExpired');
    expect(token.accessToken).toBeUndefined();
    expect(fetcher).not.toHaveBeenCalled();
  });
  it.each([
    {},
    { access_token: 1, expires_in: 900 },
    { access_token: ' ', expires_in: 900 },
    { access_token: 'secret', expires_in: -1 },
    { access_token: 'secret', expires_in: '900' },
  ])('rejects malformed backend authentication response %j', async body => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json(body)));
    const provider = authOptions.providers[0] as unknown as {
      options: { authorize: (credentials: { email: string; password: string }, request: object) => Promise<unknown> };
    };
    expect(await provider.options.authorize({ email: 'user@example.test', password: 'example-only' }, {})).toBeNull();
  });
  it('stores validated backend expiry in the encrypted JWT without retaining refresh credentials', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(
          Response.json({ access_token: 'backend-private', refresh_token: 'discard-me', expires_in: 900 })
        )
    );
    const provider = authOptions.providers[0] as unknown as {
      options: {
        authorize: (
          credentials: { email: string; password: string },
          request: object
        ) => Promise<Record<string, unknown> | null>;
      };
    };
    const user = await provider.options.authorize({ email: 'user@example.test', password: 'example-only' }, {});
    expect(user?.accessToken).toBe('backend-private');
    expect(user?.accessTokenExpiresAt).toBeGreaterThan(Date.now());
    expect(user).not.toHaveProperty('refreshToken');
    const token = await jwt({ token: { refreshToken: 'old-private' }, user } as unknown as Parameters<typeof jwt>[0]);
    expect(token.accessToken).toBe('backend-private');
    expect(token).not.toHaveProperty('refreshToken');
    expect(token.authError).toBeUndefined();
  });
  it('retains the fifteen minute dashboard session', () => {
    expect(authOptions.session?.maxAge).toBe(900);
  });
  it('uses encrypted cookie credentials and ignores caller Bearer tokens', async () => {
    vi.stubEnv('NEXTAUTH_SECRET', 'synthetic-test-secret');
    vi.stubEnv('NEXTAUTH_URL', 'http://localhost:3000');
    const encrypted = await encode({
      secret: 'synthetic-test-secret',
      token: { accessToken: 'backend-secret', accessTokenExpiresAt: Date.now() + 60000 },
    });
    expect(
      await getBackendAccessToken(
        new NextRequest('http://localhost:3000/api/platform/health', {
          headers: { cookie: `next-auth.session-token=${encrypted}` },
        })
      )
    ).toBe('backend-secret');
    expect(
      await getBackendAccessToken(
        new NextRequest('http://localhost:3000/api/platform/health', {
          headers: { authorization: `Bearer ${encrypted}` },
        })
      )
    ).toBeNull();
  });
  it('supports chunked encrypted cookies without trusting a conflicting Bearer', async () => {
    vi.stubEnv('NEXTAUTH_SECRET', 'synthetic-test-secret');
    vi.stubEnv('NEXTAUTH_URL', 'https://dashboard.example.test');
    const encrypted = await encode({
      secret: 'synthetic-test-secret',
      token: { accessToken: 'cookie-private', accessTokenExpiresAt: Date.now() + 60000 },
    });
    const half = Math.floor(encrypted.length / 2);
    const request = new NextRequest('https://dashboard.example.test', {
      headers: {
        cookie: `__Secure-next-auth.session-token.0=${encrypted.slice(0, half)}; __Secure-next-auth.session-token.1=${encrypted.slice(half)}`,
        authorization: 'Bearer untrusted',
      },
    });
    expect(await getBackendAccessToken(request)).toBe('cookie-private');
  });
  it('fails closed without a configured secret', async () => {
    vi.stubEnv('NEXTAUTH_SECRET', '');
    expect(await getBackendAccessToken(new NextRequest('http://localhost:3000'))).toBeNull();
  });
  it.each([undefined, 0, Date.now() - 1000])('rejects expired or incomplete encrypted credentials %s', async expiry => {
    vi.stubEnv('NEXTAUTH_SECRET', 'synthetic-test-secret');
    vi.stubEnv('NEXTAUTH_URL', 'http://localhost:3000');
    const encrypted = await encode({
      secret: 'synthetic-test-secret',
      token: { accessToken: 'private', accessTokenExpiresAt: expiry },
    });
    expect(
      await getBackendAccessToken(
        new NextRequest('http://localhost:3000', { headers: { cookie: `next-auth.session-token=${encrypted}` } })
      )
    ).toBeNull();
  });
});
