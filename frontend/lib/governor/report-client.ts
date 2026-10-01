/** Narrow read-only capability. Runtime secrets are supplied only by the server wrapper. */
import { createHmac } from 'node:crypto';
import { z } from 'zod';

const id = z.string().regex(/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/);
const digest = z.string().regex(/^[a-f0-9]{64}$/);
const amount = z
  .string()
  .max(100)
  .regex(/^\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$/);
const unit = z.enum([
  'usd',
  'credits',
  'provider_credits',
  'provider_api_requests',
  'renders',
  'images',
  'megapixels',
  'video_seconds',
  'frames',
  'upscales',
  'edits',
  'inference_tokens',
  'compute_seconds',
  'storage_bytes',
]);
const resources = z.partialRecord(unit, amount);
const operation = z.object({
  operation_id: id,
  job_id: id,
  grant_id: id,
  contract_id: digest,
  task_id: id.nullable(),
  state: z.enum([
    'RESERVED',
    'SUBMITTED',
    'PROVIDER_RUNNING',
    'RECONCILIATION_REQUIRED',
    'COMPLETED',
    'FAILED',
    'CANCELED',
  ]),
  billing_state: z.enum(['RESERVED', 'PENDING_ACTUAL', 'FINALIZED']),
  billing_unknown: z.boolean(),
  maximum: resources,
  actual: resources.nullable(),
  review_state: z.enum(['RECORDED', 'MISSING']),
});
const reportSchema = z.object({
  schema_version: z.literal('1.0'),
  evidence_mode: z.enum(['SIMULATED', 'LEDGER_RECORDS_ONLY']),
  ledger_authenticated: z.literal(true),
  ledger: z.object({ head_sequence: z.number().int().nonnegative() }),
  job_id: id,
  grant_id: id,
  resources: z.object({
    authorized: resources,
    consumed: resources,
    held: resources,
    available: resources,
    unspent_authorization: resources,
  }),
  operations: z.array(operation).max(10000),
  stopped: z.boolean(),
  revoked: z.boolean(),
  closed: z.boolean(),
  owner_acceptance: z.literal('UNVERIFIED'),
  actual_spend: z.null(),
  current_provider_execution: z.null(),
});
export type GovernorReport = z.infer<typeof reportSchema>;
export class ReportAccessError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
  }
}
export interface ReportSettings {
  ownerId?: string;
  backendUrl?: string;
  reportUrl?: string;
  authenticationKey?: string;
  siteId?: string;
  jobId?: string;
  grantId?: string;
}
export interface OwnerSession {
  accessToken?: string;
  user?: { email?: string | null };
}

function origin(value: string | undefined): string {
  let url: URL;
  try {
    url = new URL(value ?? '');
  } catch {
    throw new ReportAccessError(503, 'Reporting configuration unavailable');
  }
  const loopback = ['127.0.0.1', '[::1]'].includes(url.hostname);
  if (
    !(url.protocol === 'https:' || (url.protocol === 'http:' && loopback)) ||
    url.username ||
    url.password ||
    url.search ||
    url.hash ||
    url.pathname !== '/'
  ) {
    throw new ReportAccessError(503, 'Reporting configuration unavailable');
  }
  return url.origin;
}
async function boundedJson(response: Response, limit: number): Promise<unknown> {
  if (!response.body) throw new ReportAccessError(503, 'Verified report evidence unavailable');
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.length;
      if (size > limit) throw new ReportAccessError(503, 'Verified report evidence unavailable');
      chunks.push(chunk.value);
    }
    return JSON.parse(Buffer.concat(chunks).toString('utf8')) as unknown;
  } finally {
    await reader.cancel();
  }
}

export async function readOwnerReport(
  session: OwnerSession | null,
  settings: ReportSettings,
  request: typeof fetch = fetch
): Promise<{ report: GovernorReport; observedAt: string }> {
  if (!session?.accessToken) throw new ReportAccessError(401, 'Authentication required');
  // Email, roles and caller-supplied identity never select the owner.
  if (!settings.ownerId || !id.safeParse(settings.ownerId).success)
    throw new ReportAccessError(503, 'Owner authorization is not configured');
  const backend = origin(settings.backendUrl);
  try {
    const identityResponse = await request(`${backend}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${session.accessToken}` },
      cache: 'no-store',
      redirect: 'error',
      signal: AbortSignal.timeout(5000),
    });
    if (identityResponse.status === 401) throw new ReportAccessError(401, 'Authentication required');
    if (identityResponse.status === 403) throw new ReportAccessError(403, 'Owner access required');
    if (!identityResponse.ok) throw new ReportAccessError(503, 'Owner identity unavailable');
    const identity = z
      .object({ user_id: id, token_type: z.literal('access'), expires_at: z.string().datetime({ offset: true }) })
      .safeParse(await boundedJson(identityResponse, 8192));
    if (!identity.success || Date.parse(identity.data.expires_at) <= Date.now())
      throw new ReportAccessError(401, 'Authentication required');
    if (identity.data.user_id !== settings.ownerId) throw new ReportAccessError(403, 'Owner access required');
    const reportOrigin = origin(settings.reportUrl);
    if (
      !settings.authenticationKey ||
      Buffer.byteLength(settings.authenticationKey) < 32 ||
      !id.safeParse(settings.siteId).success ||
      !id.safeParse(settings.jobId).success ||
      !id.safeParse(settings.grantId).success
    ) {
      throw new ReportAccessError(503, 'Reporting configuration unavailable');
    }
    const path = `/v1/governor/report/${settings.jobId}/${settings.grantId}`;
    const timestamp = String(Math.floor(Date.now() / 1000));
    const signature = createHmac('sha256', settings.authenticationKey)
      .update(['GET', path, settings.siteId, timestamp].join('\n'))
      .digest('hex');
    const response = await request(`${reportOrigin}${path}`, {
      method: 'GET',
      cache: 'no-store',
      redirect: 'error',
      signal: AbortSignal.timeout(5000),
      headers: { 'X-Report-Timestamp': timestamp, 'X-Report-Site': settings.siteId!, 'X-Report-Signature': signature },
    });
    if (!response.ok) throw new ReportAccessError(503, 'Verified report evidence unavailable');
    const parsed = reportSchema.safeParse(await boundedJson(response, 1048576));
    if (
      !parsed.success ||
      parsed.data.job_id !== settings.jobId ||
      parsed.data.grant_id !== settings.grantId ||
      parsed.data.operations.some(op => op.job_id !== settings.jobId || op.grant_id !== settings.grantId)
    ) {
      throw new ReportAccessError(503, 'Verified report evidence unavailable');
    }
    return { report: parsed.data, observedAt: new Date().toISOString() };
  } catch (error) {
    if (error instanceof ReportAccessError) throw error;
    throw new ReportAccessError(503, 'Verified report evidence unavailable');
  }
}
