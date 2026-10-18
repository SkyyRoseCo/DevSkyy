import { NextResponse } from 'next/server';

import { withAuth } from '@/lib/api-auth';
import projection from '../../../admin/god-mode/registry.generated.json';

/** Authenticated source snapshot only. No filesystem reads or tool dispatch. */
export const GET = withAuth(async () =>
  NextResponse.json(
    {
      success: true,
      data: projection,
    },
    { headers: { 'Cache-Control': 'private, no-store' } }
  )
);
