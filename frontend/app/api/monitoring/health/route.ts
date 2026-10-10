/**
 * Health Check Endpoint - Next.js Route Handler
 */

import { NextResponse } from 'next/server';

import { withAuth } from '@/lib/api-auth';

const startTime = Date.now();

async function getHandler() {
  try {
    const uptimeSeconds = (Date.now() - startTime) / 1000;
    const memoryUsage = process.memoryUsage();
    const memoryMB = memoryUsage.heapUsed / 1024 / 1024;

    const healthStatus = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime_seconds: Math.round(uptimeSeconds),
      version: process.env.APP_REVISION?.substring(0, 7) || 'unknown',
      region: process.env.FLY_REGION || 'local',
      checks: {
        api: true,
      },
      metrics: {
        memory_mb: Math.round(memoryMB * 100) / 100,
        requests_total: 0,
      },
    };

    return NextResponse.json(healthStatus, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 }
    );
  }
}

export const GET = withAuth(getHandler);
