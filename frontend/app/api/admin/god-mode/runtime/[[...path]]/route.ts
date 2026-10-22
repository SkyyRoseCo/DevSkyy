import type { NextRequest } from 'next/server';

import { withAuth } from '@/lib/api-auth';
import { proxyGodModeRuntime } from '@/lib/god-mode-runtime-proxy';

export const maxDuration = 300;
type RouteContext = { params: Promise<{ path?: string[] }> };

async function proxy(request: NextRequest, context: RouteContext) {
  const { path = [] } = await context.params;
  return proxyGodModeRuntime(request, path);
}
export const GET = withAuth(proxy);
export const POST = withAuth(proxy);
