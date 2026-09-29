import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { NextRequest } from 'next/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const { session } = vi.hoisted(() => ({ session: vi.fn() }));
vi.mock('next-auth', () => ({ getServerSession: session }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));

let directory: string;
let settingsPath: string;

beforeEach(async () => {
  directory = await mkdtemp(path.join(tmpdir(), 'devskyy-settings-test-'));
  settingsPath = path.join(directory, 'state', 'settings.json');
  vi.stubEnv('SETTINGS_FILE', settingsPath);
  vi.resetModules();
  session.mockResolvedValue({ user: { email: 'operator@example.test' } });
});

afterEach(async () => {
  vi.unstubAllEnvs();
  await rm(directory, { recursive: true, force: true });
});

describe('persistent dashboard settings', () => {
  it('reads an authenticated save after the route module is reloaded', async () => {
    const settings = { ui: { theme: 'dark' } };
    const { POST } = await import('../app/api/settings/route');
    const response = await POST(
      new NextRequest('http://localhost/api/settings', {
        method: 'POST',
        body: JSON.stringify(settings),
        headers: { 'Content-Type': 'application/json' },
      }),
      undefined
    );
    expect(response.status).toBe(200);
    expect(JSON.parse(await readFile(settingsPath, 'utf8'))).toEqual(settings);
    expect((await stat(settingsPath)).mode & 0o777).toBe(0o600);

    vi.resetModules();
    const { GET } = await import('../app/api/settings/route');
    const saved = await GET(new NextRequest('http://localhost/api/settings'), undefined);
    expect(await saved.json()).toEqual(settings);
  });

  it('rejects an unauthenticated write before touching storage', async () => {
    session.mockResolvedValue(null);
    const { POST } = await import('../app/api/settings/route');
    const response = await POST(
      new NextRequest('http://localhost/api/settings', {
        method: 'POST',
        body: '{}',
      }),
      undefined
    );
    expect(response.status).toBe(401);
    await expect(stat(settingsPath)).rejects.toMatchObject({ code: 'ENOENT' });
  });
});
