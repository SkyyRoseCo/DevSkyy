import { NextRequest, NextResponse } from 'next/server';
import { withAuth } from '@/lib/api-auth';
import { meshyClient, toJob3D as meshyToJob3D } from '@/lib/meshy/client';
import { tripoClient, toJob3D as tripoToJob3D } from '@/lib/tripo/client';
import { jobStore } from '../../jobs/store';

async function postHandler(request: NextRequest) {
  let body: { prompt?: string; provider?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const prompt = body.prompt?.trim();
  if (!prompt) {
    return NextResponse.json({ error: 'Prompt is required' }, { status: 400 });
  }
  if (prompt.length > 5000) {
    return NextResponse.json({ error: 'Prompt too long (max 5000 chars)' }, { status: 400 });
  }

  const provider = body.provider || 'meshy';

  try {
    let job;

    if (provider === 'tripo') {
      const task = await tripoClient.textTo3D({ prompt });
      job = tripoToJob3D(task, 'text', prompt);
    } else {
      const task = await meshyClient.textTo3D({ mode: 'preview', prompt });
      job = meshyToJob3D(task, 'text', prompt);
    }

    jobStore.unshift(job);

    return NextResponse.json(job);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Generation failed';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export const POST = withAuth(postHandler);
