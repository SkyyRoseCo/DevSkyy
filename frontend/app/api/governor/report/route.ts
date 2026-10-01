import { withAuth } from '@/lib/api-auth';
import { getOwnerReport } from '@/lib/governor/server';
import { ReportAccessError } from '@/lib/governor/report-client';

const headers = {
  'Cache-Control': 'private, no-store',
  Pragma: 'no-cache',
  Vary: 'Cookie',
  'X-Content-Type-Options': 'nosniff',
};
export const GET = withAuth(async () => {
  try {
    return Response.json(await getOwnerReport(), { headers });
  } catch (error) {
    const status = error instanceof ReportAccessError ? error.status : 503;
    const message = error instanceof ReportAccessError ? error.message : 'Verified report evidence unavailable';
    return Response.json({ error: message }, { status, headers });
  }
});
