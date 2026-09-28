import { NextRequest, NextResponse } from 'next/server';
import { withAuth } from '@/lib/api-auth';
import { meshyClient, toJob3D as meshyToJob3D } from '@/lib/meshy/client';
import { tripoClient, toJob3D as tripoToJob3D } from '@/lib/tripo/client';
import { jobStore } from '../../jobs/store';

async function postHandler(request: NextRequest) {
  let body: { image_url?: string; provider?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const imageUrl = body.image_url;
  if (!imageUrl) {
    return NextResponse.json({ error: 'image_url is required' }, { status: 400 });
  }

  try {
    new URL(imageUrl);
  } catch {
    return NextResponse.json({ error: 'Invalid image URL' }, { status: 400 });
  }

  if (imageUrl.length > 2000) {
    return NextResponse.json({ error: 'Image URL too long' }, { status: 400 });
  }

  const provider = body.provider || 'meshy';

  try {
    let job;

    if (provider === 'tripo') {
      const fileToken = await tripoClient.uploadImage(imageUrl);
      const task = await tripoClient.imageTo3D({ file_token: fileToken });
      job = tripoToJob3D(task, 'image', imageUrl);
    } else {
      const task = await meshyClient.imageTo3D({ image_url: imageUrl });
      job = meshyToJob3D(task, 'image', imageUrl);
    }

    jobStore.unshift(job);

    return NextResponse.json(job);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Generation failed';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export const POST = withAuth(postHandler);
