import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { buildBackendUrl } from '../lib/backend-proxy';
beforeEach(() => {
  vi.stubEnv('BACKEND_API_URL', 'https://backend.example.test');
});
afterEach(() => {
  vi.unstubAllEnvs();
});
it.each([
  '/health',
  '/ready',
  '/api/v1/assets',
  '/api/v1/tasks/abc',
  '/api/v1/elite-studio/operations',
  '/api/v2/usage',
])('allows current dashboard GET %s', path => {
  expect(buildBackendUrl(path, '?limit=2', 'GET')?.href).toBe(`https://backend.example.test${path}?limit=2`);
});
it.each([
  '/api/v1/auth/token',
  '/api/v1/webhooks/stripe',
  '/api/v1/unknown',
  '//evil.test/api/v1/assets',
  '/api/v1/assets/../auth',
  '/api/v1/assets/%2e%2e/auth',
  '/api/v1/assets/%252e%252e/auth',
  '/api/v1/assets/%2fsecret',
  '/api/v1/assets/a\\b',
  '/api/v1/assets/%00',
  '/api/v1/assets/a//b',
])('denies unsafe or unlisted route %s', path => {
  expect(buildBackendUrl(path, '', 'GET')).toBeNull();
});
it('limits methods to the actual dashboard operations', () => {
  expect(buildBackendUrl('/api/v1/tasks/abc/cancel', '', 'POST')).not.toBeNull();
  expect(buildBackendUrl('/api/v1/catalog/search', '', 'DELETE')).toBeNull();
  expect(buildBackendUrl('/health', '', 'POST')).toBeNull();
});
it.each([
  'https://user:password@example.test',
  'https://example.test/base',
  'https://example.test?target=bad',
  'ftp://example.test',
  'http://example.test',
])('fails closed for unsafe production configuration %s', origin => {
  vi.stubEnv('NODE_ENV', 'production');
  vi.stubEnv('BACKEND_API_URL', origin);
  expect(buildBackendUrl('/health', '', 'GET')).toBeNull();
});

it.each([
  ['/api/v1/monitoring/health', 'GET'],
  ['/api/v1/monitoring/metrics', 'GET'],
  ['/api/v1/batch/generate', 'POST'],
  ['/api/v1/batch/job/pause', 'POST'],
  ['/api/v1/autonomous/operations/job/start', 'POST'],
  ['/api/v1/social-media/queue', 'GET'],
  ['/api/v1/social-media/publish', 'POST'],
  ['/api/v1/commerce/pricing/optimize', 'POST'],
  ['/api/v1/competitors/brand', 'DELETE'],
  ['/api/v1/brand-assets/assets/id/approve', 'PATCH'],
  ['/api/v1/brand-assets/assets/id/reject', 'PATCH'],
  ['/api/v1/brand-assets/ingest/bulk', 'POST'],
  ['/api/v1/context-dev/extractions', 'POST'],
])('allows current client operation %s %s', (path, method) => {
  expect(buildBackendUrl(path, '', method)).not.toBeNull();
});
it('does not reinterpret reserved operation paths as dynamic identifiers', () => {
  expect(buildBackendUrl('/api/v1/assets/upload', '', 'DELETE')).toBeNull();
  expect(buildBackendUrl('/api/v1/batch/generate', '', 'GET')).toBeNull();
});

it('does not authorize incorrect brand asset mutation methods', () => {
  for (const action of ['approve', 'reject']) {
    expect(buildBackendUrl(`/api/v1/brand-assets/assets/id/${action}`, '', 'POST')).toBeNull();
  }
});
