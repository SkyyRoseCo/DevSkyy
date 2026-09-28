import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';

import { withAuth } from '@/lib/api-auth';
import { authOptions } from '@/lib/auth';

import {
  buildRunwayDryRunPayload,
  isRunwayRouterConfigId,
  isTrustedRunwayApiBaseUrl,
  RunwayPreflightBodySchema,
  validateRunwayDryRunResponse,
} from './contract';
import { authorizeRunwayDryRunQuotaOperation } from './governor';
import { getRunwayRouterConfigurationGate } from './qualification-gate';
import { consumeRunwayDryRunRateLimit, RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS } from './rate-limit';

const RUNWAY_API_VERSION = '2024-11-06';
const MAX_REQUEST_BODY_BYTES = 1_024;

type ParsedRequestBody = { ok: true; value: unknown } | { ok: false; reason: 'INVALID_REQUEST' | 'REQUEST_TOO_LARGE' };

type RunwayConfiguration = {
  apiBaseUrl: string;
  apiSecret: string;
  routerConfigId: string;
};

function getRunwayConfiguration(): RunwayConfiguration | null {
  if (process.env.RUNWAY_DEV_DRY_RUN_ENABLED !== 'true') {
    return null;
  }

  const apiBaseUrl = process.env.RUNWAY_DEV_API_BASE_URL?.trim();
  const apiSecret = process.env.RUNWAYML_API_SECRET;
  const routerConfigId = process.env.RUNWAY_ROUTER_CONFIG_ID?.trim();

  if (!apiBaseUrl || !apiSecret || !routerConfigId || !isRunwayRouterConfigId(routerConfigId)) {
    return null;
  }

  if (!isTrustedRunwayApiBaseUrl(apiBaseUrl)) {
    return null;
  }

  return { apiBaseUrl, apiSecret, routerConfigId };
}

async function readBoundedJson(request: Request): Promise<ParsedRequestBody> {
  const contentLength = Number(request.headers.get('content-length'));
  if (Number.isFinite(contentLength) && contentLength > MAX_REQUEST_BODY_BYTES) {
    return { ok: false, reason: 'REQUEST_TOO_LARGE' };
  }

  const reader = request.body?.getReader();
  if (!reader) {
    return { ok: false, reason: 'INVALID_REQUEST' };
  }

  const chunks: Uint8Array[] = [];
  let totalBytes = 0;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      totalBytes += value.byteLength;
      if (totalBytes > MAX_REQUEST_BODY_BYTES) {
        await reader.cancel().catch(() => undefined);
        return { ok: false, reason: 'REQUEST_TOO_LARGE' };
      }

      chunks.push(value);
    }
  } catch {
    return { ok: false, reason: 'INVALID_REQUEST' };
  } finally {
    reader.releaseLock();
  }

  const bytes = new Uint8Array(totalBytes);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }

  try {
    return { ok: true, value: JSON.parse(new TextDecoder().decode(bytes)) as unknown };
  } catch {
    return { ok: false, reason: 'INVALID_REQUEST' };
  }
}

async function postHandler(request: NextRequest): Promise<Response> {
  const configuration = getRunwayConfiguration();
  if (!configuration) {
    return NextResponse.json(
      { ok: false, error: 'RUNWAY_DEV_DRY_RUN_NOT_CONFIGURED' },
      { status: 503, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  const parsedBody = await readBoundedJson(request);
  if (!parsedBody.ok && parsedBody.reason === 'REQUEST_TOO_LARGE') {
    return NextResponse.json(
      { ok: false, error: parsedBody.reason },
      { status: 413, headers: { 'Cache-Control': 'no-store' } }
    );
  }
  if (!parsedBody.ok) {
    return NextResponse.json(
      { ok: false, error: 'INVALID_REQUEST' },
      { status: 400, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  const parsedRequest = RunwayPreflightBodySchema.safeParse(parsedBody.value);
  if (!parsedRequest.success) {
    return NextResponse.json(
      { ok: false, error: 'INVALID_REQUEST' },
      { status: 400, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  const session = await getServerSession(authOptions);
  const authenticatedEmail = session?.user?.email?.trim();
  if (!authenticatedEmail) {
    return NextResponse.json(
      { ok: false, error: 'RUNWAY_DRY_RUN_IDENTITY_UNAVAILABLE' },
      { status: 503, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  const routerConfigurationGate = getRunwayRouterConfigurationGate();
  if (!routerConfigurationGate.ready) {
    return NextResponse.json(
      { ok: false, error: routerConfigurationGate.reason },
      { status: 503, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  const rateLimitResult = await consumeRunwayDryRunRateLimit(authenticatedEmail);
  if (rateLimitResult === 'unavailable') {
    return NextResponse.json(
      { ok: false, error: 'RUNWAY_DRY_RUN_RATE_LIMIT_UNAVAILABLE' },
      { status: 503, headers: { 'Cache-Control': 'no-store' } }
    );
  }
  if (rateLimitResult === 'limited') {
    return NextResponse.json(
      { ok: false, error: 'RUNWAY_DRY_RUN_RATE_LIMITED' },
      {
        status: 429,
        headers: {
          'Cache-Control': 'no-store',
          'Retry-After': String(RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS),
        },
      }
    );
  }

  const governorAuthorization = authorizeRunwayDryRunQuotaOperation();
  if (!governorAuthorization.authorized) {
    return NextResponse.json(
      { ok: false, error: governorAuthorization.reason },
      { status: 503, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  const aspectRatio = parsedRequest.data.aspectRatio ?? '4:5';
  const requestUrl = new URL('/v1/generate/image', configuration.apiBaseUrl);

  try {
    const providerResponse = await fetch(requestUrl, {
      method: 'POST',
      cache: 'no-store',
      signal: AbortSignal.timeout(15_000),
      headers: {
        Authorization: 'Bearer ' + configuration.apiSecret,
        'Content-Type': 'application/json',
        'X-Runway-Version': RUNWAY_API_VERSION,
      },
      body: JSON.stringify(buildRunwayDryRunPayload(configuration.routerConfigId, aspectRatio)),
    });

    if (!providerResponse.ok) {
      return NextResponse.json(
        { ok: false, error: 'RUNWAY_DEV_PREFLIGHT_REJECTED' },
        { status: 502, headers: { 'Cache-Control': 'no-store' } }
      );
    }

    const providerResult: unknown = await providerResponse.json();
    const validated = validateRunwayDryRunResponse(providerResult, configuration.routerConfigId, aspectRatio);

    if (!validated.ok) {
      return NextResponse.json(
        { ok: false, error: 'RUNWAY_DEV_ROUTER_POLICY_MISMATCH', reason: validated.reason },
        { status: 502, headers: { 'Cache-Control': 'no-store' } }
      );
    }

    return NextResponse.json(
      { ok: true, dryRun: true, taskCreated: false, decision: validated.decision },
      { headers: { 'Cache-Control': 'no-store' } }
    );
  } catch {
    return NextResponse.json(
      { ok: false, error: 'RUNWAY_DEV_PREFLIGHT_UNAVAILABLE' },
      { status: 502, headers: { 'Cache-Control': 'no-store' } }
    );
  }
}

export const POST = withAuth(postHandler);
