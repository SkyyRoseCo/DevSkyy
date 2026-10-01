import { beforeEach, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ session: vi.fn(), report: vi.fn() }));
vi.mock('next-auth', () => ({ getServerSession: mocks.session }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/governor/server', () => ({ getOwnerReport: mocks.report }));
import * as route from '../app/api/governor/report/route';
import { ReportAccessError } from '../lib/governor/report-client';
import { NextRequest } from 'next/server';

beforeEach(() => {
  vi.clearAllMocks();
  mocks.session.mockResolvedValue({ user: { email: 'synthetic@example.test' } });
});
it('GET is the only exported report operation', () => {
  expect(Object.keys(route)).toEqual(['GET']);
});
it('denies direct anonymous API requests without invoking report capability', async () => {
  mocks.session.mockResolvedValue(null);
  const response = await route.GET(new NextRequest('http://localhost/api/governor/report'), undefined);
  expect(response.status).toBe(401);
  expect(response.headers.get('Cache-Control')).toContain('no-store');
  expect(mocks.report).not.toHaveBeenCalled();
});
it.each([401, 403, 503])('returns redacted no-store rejection %i for direct API access', async status => {
  mocks.report.mockRejectedValue(new ReportAccessError(status, 'Owner access required'));
  const response = await route.GET(new NextRequest('http://localhost/api/governor/report'), undefined);
  expect(response.status).toBe(status);
  expect(response.headers.get('Cache-Control')).toBe('private, no-store');
  expect(response.headers.get('Vary')).toBe('Cookie');
  expect(await response.json()).toEqual({ error: 'Owner access required' });
});
it('does not leak an unexpected error or its credentials', async () => {
  mocks.report.mockRejectedValue(new Error('raw credential failure'));
  const response = await route.GET(new NextRequest('http://localhost/api/governor/report'), undefined);
  expect(response.status).toBe(503);
  expect(await response.json()).toEqual({ error: 'Verified report evidence unavailable' });
});
it('returns only the server report and observed timestamp on the authorized path', async () => {
  mocks.report.mockResolvedValue({ report: { evidence_mode: 'SIMULATED' }, observedAt: '2026-10-01T00:00:00Z' });
  const response = await route.GET(new NextRequest('http://localhost/api/governor/report'), undefined);
  expect(response.status).toBe(200);
  expect(response.headers.get('Cache-Control')).toContain('no-store');
  expect(await response.json()).toEqual({ report: { evidence_mode: 'SIMULATED' }, observedAt: '2026-10-01T00:00:00Z' });
});
it('redacts session-provider exceptions before entering report capability', async () => {
  mocks.session.mockRejectedValue(new Error('synthetic credential contents'));
  const response = await route.GET(new NextRequest('http://localhost/api/governor/report'), undefined);
  expect(response.status).toBe(503);
  expect(response.headers.get('Cache-Control')).toContain('no-store');
  expect(await response.json()).toEqual({ success: false, error: 'Authentication unavailable' });
  expect(mocks.report).not.toHaveBeenCalled();
});
