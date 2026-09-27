import { NextRequest, NextResponse } from 'next/server';
import { withAuth } from '@/lib/api-auth';
import { jobStore } from './store';

async function getHandler(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const limit = Math.min(Math.max(1, Number(searchParams.get('limit')) || 20), 100);

  return NextResponse.json(jobStore.slice(0, limit));
}

export const GET = withAuth(getHandler);
