import { createHmac } from 'node:crypto';
import { createServer } from 'node:http';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { readOwnerReport, type ReportSettings } from '../lib/governor/report-client';

const settings: ReportSettings = {
  ownerId: 'immutable-owner-id',
  backendUrl: 'https://identity.test',
  reportUrl: 'https://report.test',
  authenticationKey: 'synthetic-read-only-report-key-00000',
  siteId: 'synthetic-site',
  jobId: 'synthetic-job',
  grantId: 'synthetic-grant',
};
const session = { accessToken: 'synthetic-token', user: { email: 'corey@skyyrose.co' } };
function identity(user_id = settings.ownerId, expires_at = new Date(Date.now() + 60000).toISOString()) {
  return { user_id, token_type: 'access', expires_at };
}
function fixture() {
  return {
    schema_version: '1.0',
    evidence_mode: 'SIMULATED',
    ledger_authenticated: true,
    ledger: { head_sequence: 1 },
    job_id: settings.jobId,
    grant_id: settings.grantId,
    resources: {
      authorized: { provider_api_requests: '1' },
      consumed: {},
      held: {},
      available: {},
      unspent_authorization: {},
    },
    operations: [],
    stopped: false,
    revoked: false,
    closed: false,
    owner_acceptance: 'UNVERIFIED',
    actual_spend: null,
    current_provider_execution: null,
  };
}
afterEach(() => vi.restoreAllMocks());

describe('owner-only read-only report', () => {
  it.each([null, {}, { user: { email: 'corey@skyyrose.co' } }])(
    'denies session without authenticated backend token',
    async value => {
      const request = vi.fn();
      await expect(readOwnerReport(value, settings, request)).rejects.toMatchObject({ status: 401 });
      expect(request).not.toHaveBeenCalled();
    }
  );
  it('fails closed without configured immutable owner', async () => {
    const request = vi.fn();
    await expect(readOwnerReport(session, { ...settings, ownerId: undefined }, request)).rejects.toMatchObject({
      status: 503,
    });
    expect(request).not.toHaveBeenCalled();
  });
  it('denies another subject despite matching owner email and forged session id', async () => {
    const request = vi.fn().mockResolvedValue(Response.json(identity('another-subject')));
    await expect(
      readOwnerReport({ ...session, id: settings.ownerId } as typeof session, settings, request)
    ).rejects.toMatchObject({ status: 403 });
    expect(request).toHaveBeenCalledTimes(1);
  });
  it.each([new Date(Date.now() - 1000).toISOString(), 'invalid'])(
    'denies expired or malformed backend identity',
    async expiry => {
      const request = vi.fn().mockResolvedValue(Response.json(identity(settings.ownerId, expiry)));
      await expect(readOwnerReport(session, settings, request)).rejects.toMatchObject({ status: 401 });
      expect(request).toHaveBeenCalledTimes(1);
    }
  );
  it.each([401, 403, 500])('never reads ledger after identity HTTP %i', async status => {
    const request = vi.fn().mockResolvedValue(new Response('no', { status }));
    await expect(readOwnerReport(session, settings, request)).rejects.toMatchObject({
      status: status === 500 ? 503 : status,
    });
    expect(request).toHaveBeenCalledTimes(1);
  });
  it('accepts backend owner with altered email and signs only exact GET scope', async () => {
    const request = vi
      .fn()
      .mockResolvedValueOnce(Response.json(identity()))
      .mockResolvedValueOnce(Response.json({ ...fixture(), secret: 'do-not-project' }));
    const result = await readOwnerReport({ ...session, user: { email: 'changed@example.test' } }, settings, request);
    expect(result.report).toEqual(fixture());
    const [url, options] = request.mock.calls[1];
    expect(url).toBe('https://report.test/v1/governor/report/synthetic-job/synthetic-grant');
    expect(options).toMatchObject({ method: 'GET', redirect: 'error', cache: 'no-store' });
    const headers = options.headers;
    const expected = createHmac('sha256', settings.authenticationKey!)
      .update(
        [
          'GET',
          '/v1/governor/report/synthetic-job/synthetic-grant',
          settings.siteId,
          headers['X-Report-Timestamp'],
        ].join('\n')
      )
      .digest('hex');
    expect(headers['X-Report-Signature']).toBe(expected);
    expect(headers.Authorization).toBeUndefined();
    expect(JSON.stringify(result)).not.toContain('synthetic-token');
  });
  it.each([
    { job_id: 'other-job' },
    { ledger_authenticated: false },
    { actual_spend: 0 },
    { evidence_mode: 'LIVE' },
    { owner_acceptance: 'APPROVED' },
  ])('rejects incompatible or cross-scope evidence %j', async change => {
    const request = vi
      .fn()
      .mockResolvedValueOnce(Response.json(identity()))
      .mockResolvedValueOnce(Response.json({ ...fixture(), ...change }));
    await expect(readOwnerReport(session, settings, request)).rejects.toMatchObject({ status: 503 });
  });
  it('bounds upstream response and redacts exception details', async () => {
    const request = vi
      .fn()
      .mockResolvedValueOnce(Response.json(identity()))
      .mockResolvedValueOnce(new Response('x'.repeat(1048577)));
    await expect(readOwnerReport(session, settings, request)).rejects.toMatchObject({
      status: 503,
      message: 'Verified report evidence unavailable',
    });
    const failed = vi.fn().mockRejectedValue(new Error('secret raw transport error'));
    await expect(readOwnerReport(session, settings, failed)).rejects.toMatchObject({
      status: 503,
      message: 'Verified report evidence unavailable',
    });
  });
  it.each([
    'http://identity.test',
    'http://report.test',
    'http://localhost',
    'https://user:password@report.test',
    'https://report.test/path',
    'https://report.test?scope=other',
    'file:///tmp/ledger',
  ])('rejects report origin configuration %s', async reportUrl => {
    const request = vi.fn().mockResolvedValueOnce(Response.json(identity()));
    await expect(readOwnerReport(session, { ...settings, reportUrl }, request)).rejects.toMatchObject({ status: 503 });
    expect(request).toHaveBeenCalledTimes(1);
  });
  it('exercises real loopback HTTP transport and signature validation with synthetic identity/report fixtures', async () => {
    const seen: string[] = [];
    const server = createServer((req, res) => {
      seen.push(`${req.method} ${req.url}`);
      if (req.url === '/api/v1/auth/me' && req.headers.authorization === 'Bearer synthetic-token') {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(identity()));
        return;
      }
      const timestamp = req.headers['x-report-timestamp'];
      const expected = createHmac('sha256', settings.authenticationKey!)
        .update(['GET', req.url, settings.siteId, timestamp].join('\n'))
        .digest('hex');
      if (req.method !== 'GET' || req.headers['x-report-signature'] !== expected) {
        res.writeHead(403);
        res.end();
        return;
      }
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify(fixture()));
    });
    await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
    const address = server.address();
    if (!address || typeof address === 'string') throw new Error('Missing test address');
    const url = `http://127.0.0.1:${address.port}`;
    try {
      const result = await readOwnerReport(session, { ...settings, backendUrl: url, reportUrl: url });
      expect(result.report.evidence_mode).toBe('SIMULATED');
      expect(seen).toEqual(['GET /api/v1/auth/me', 'GET /v1/governor/report/synthetic-job/synthetic-grant']);
    } finally {
      await new Promise<void>((resolve, reject) => server.close(error => (error ? reject(error) : resolve())));
    }
  });
});
it('rejects insecure identity origin before forwarding bearer credentials', async () => {
  const request = vi.fn();
  await expect(
    readOwnerReport(session, { ...settings, backendUrl: 'http://identity.example.test' }, request)
  ).rejects.toMatchObject({ status: 503 });
  expect(request).not.toHaveBeenCalled();
});
