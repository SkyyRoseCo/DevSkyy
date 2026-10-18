/** Offline mocked-session regressions; not evidence of a live account login. */
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
const { getServerSessionMock } = vi.hoisted(() => ({ getServerSessionMock: vi.fn() }));
vi.mock('next-auth', () => ({ getServerSession: getServerSessionMock }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
import { GET } from '@/app/api/admin/god-mode/route';
import projection from './registry.generated.json';
const pageSource = readFileSync(path.resolve('app/admin/god-mode/page.tsx'), 'utf8');
const apiSource = readFileSync(path.resolve('app/api/admin/god-mode/route.ts'), 'utf8');
describe('GOD MODE dashboard boundary', () => {
  beforeEach(() => getServerSessionMock.mockReset());
  it('rejects anonymous requests without returning source registry', async () => {
    getServerSessionMock.mockResolvedValue(null);
    const response = await GET(new NextRequest('http://localhost/api/admin/god-mode'), undefined);
    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ success: false, error: 'Unauthorized' });
  });
  it('returns exactly generated snapshot for mocked authenticated session', async () => {
    getServerSessionMock.mockResolvedValue({ user: { email: 'operator@example.test' } });
    const response = await GET(new NextRequest('http://localhost/api/admin/god-mode'), undefined);
    expect(response.status).toBe(200);
    expect(response.headers.get('Cache-Control')).toBe('private, no-store');
    expect(await response.json()).toEqual({ success: true, data: projection });
  });
  it('keeps the inventory read-only and delegates execution to the authenticated runtime', () => {
    expect(apiSource.match(/export const \w+/g)).toEqual(['export const GET']);
    expect(apiSource).not.toMatch(/child_process|exec\(|spawn\(|readFile|writeFile|fetch\(/);
    expect(pageSource).not.toMatch(/child_process|exec\(|spawn\(|fetch\(|use client/);
    expect(pageSource).toContain('<RuntimeWorkspace />');
    const runtimeRoute = readFileSync(path.resolve('app/api/admin/god-mode/runtime/[[...path]]/route.ts'), 'utf8');
    expect(runtimeRoute).toContain('withAuth<RouteContext>');
    expect(runtimeRoute).toContain('proxyGodModeRuntime(request, path)');
    expect(runtimeRoute).not.toMatch(/child_process|exec\(|spawn\(|readFile|writeFile/);
  });
  it('gates source inventory behind server session and wraps dynamic work in Suspense', () => {
    expect(pageSource.indexOf('if (!session)')).toBeLessThan(pageSource.indexOf('const groups ='));
    expect(pageSource).toMatch(/<Suspense[\s\S]*<Workspace \/>/);
  });
  it('links to existing local dashboard routes', () => {
    const links = [...pageSource.matchAll(/href: '(\/admin\/[^']+)'/g)].map(match => match[1]);
    expect(links.length).toBeGreaterThanOrEqual(6);
    for (const link of links) expect(existsSync(path.resolve(`app${link}/page.tsx`)), link).toBe(true);
  });
  it('contains no developer filesystem paths or embedded secret values', () => {
    expect(JSON.stringify(projection)).not.toMatch(/\/Users\/|\/private\/|\/tmp\/|file:\/\/|sk-[A-Za-z0-9]{20}/);
    expect(projection.schemaVersion).toBe(1);
    expect(projection.team.controller).toBe('GOD MODE');
  });
});
