import { beforeEach, expect, it, vi } from 'vitest';

const getServerSession = vi.hoisted(() => vi.fn());
vi.mock('next-auth', () => ({ getServerSession }));
vi.mock('../lib/auth', () => ({ authOptions: {} }));
import { getAdminSession } from '../lib/require-admin-session';

beforeEach(() => {
  getServerSession.mockReset();
});
it('retains a valid admin session for server-side data gates', async () => {
  const session = { user: { email: 'operator@example.test' }, expires: '2099-01-01T00:00:00Z' };
  getServerSession.mockResolvedValue(session);
  expect(await getAdminSession()).toBe(session);
});
it('returns null when no session exists', async () => {
  getServerSession.mockResolvedValue(null);
  expect(await getAdminSession()).toBeNull();
});
it('returns null for expired or migrated backend credentials before a server data call', async () => {
  getServerSession.mockResolvedValue({ user: { email: 'operator@example.test' }, authError: 'BackendTokenExpired' });
  const fetchProtectedData = vi.fn();
  const session = await getAdminSession();
  if (session) await fetchProtectedData();
  expect(session).toBeNull();
  expect(fetchProtectedData).not.toHaveBeenCalled();
});
