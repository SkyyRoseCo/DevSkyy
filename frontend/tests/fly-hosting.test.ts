import { describe, expect, it } from 'vitest';
import config from '../next.config';
import { GET } from '../app/healthz/route';

describe('portable dashboard hosting', () => {
  it('exposes liveness without leaking runtime details or requiring a session', async () => {
    const response = GET();
    expect(response.status).toBe(200);
    expect(response.headers.get('cache-control')).toContain('no-store');
    expect(await response.json()).toEqual({ status: 'ok' });
  });

  it('retains security and credentialed CORS headers outside Vercel', async () => {
    const rules = await config.headers!();
    const globalHeaders = rules.find(rule => rule.source === '/:path*')?.headers;
    expect(globalHeaders).toContainEqual({ key: 'X-Content-Type-Options', value: 'nosniff' });
    const apiHeaders = rules.find(rule => rule.source === '/api/:path*')?.headers;
    expect(apiHeaders).toContainEqual({ key: 'Access-Control-Allow-Origin', value: 'https://skyyrose.co' });
    expect(apiHeaders).toContainEqual({ key: 'Access-Control-Allow-Credentials', value: 'true' });
    expect(apiHeaders).toContainEqual({ key: 'Cache-Control', value: 'no-store, max-age=0' });
    expect(apiHeaders).not.toContainEqual({ key: 'Access-Control-Allow-Origin', value: '*' });
  });
});
