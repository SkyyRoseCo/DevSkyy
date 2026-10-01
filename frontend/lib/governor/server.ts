import 'server-only';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { readOwnerReport, type OwnerSession } from './report-client';

export async function getOwnerReport() {
  const session = (await getServerSession(authOptions)) as OwnerSession | null;
  return readOwnerReport(session, {
    ownerId: process.env.GOVERNOR_OWNER_USER_ID,
    backendUrl: process.env.GOVERNOR_IDENTITY_API_URL,
    reportUrl: process.env.GOVERNOR_REPORT_URL,
    authenticationKey: process.env.GOVERNOR_REPORT_AUTH_KEY,
    siteId: process.env.GOVERNOR_REPORT_SITE_ID,
    jobId: process.env.GOVERNOR_REPORT_JOB_ID,
    grantId: process.env.GOVERNOR_REPORT_GRANT_ID,
  });
}
