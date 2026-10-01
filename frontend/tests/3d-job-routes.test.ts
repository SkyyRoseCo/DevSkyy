import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
import type { MeshyTaskResponse } from '@/lib/meshy/client';
import type { TripoTaskData } from '@/lib/tripo/client';

const mocks = vi.hoisted(() => ({
  session: vi.fn(),
  meshyText: vi.fn(),
  meshyImage: vi.fn(),
  tripoText: vi.fn(),
  tripoImage: vi.fn(),
  upload: vi.fn(),
  fetch: vi.fn(),
}));
vi.mock('next-auth', () => ({ getServerSession: mocks.session }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/meshy/client', async original => ({
  ...(await original<typeof import('@/lib/meshy/client')>()),
  meshyClient: { textTo3D: mocks.meshyText, imageTo3D: mocks.meshyImage },
}));
vi.mock('@/lib/tripo/client', async original => ({
  ...(await original<typeof import('@/lib/tripo/client')>()),
  tripoClient: { textTo3D: mocks.tripoText, imageTo3D: mocks.tripoImage, uploadImage: mocks.upload },
}));

beforeEach(() => {
  vi.resetModules();
  vi.resetAllMocks();
  mocks.session.mockResolvedValue({ user: { email: 'synthetic-operator@example.test' } });
  mocks.fetch.mockRejectedValue(new Error('Unexpected network request'));
  vi.stubGlobal('fetch', mocks.fetch);
  const meshyTask: MeshyTaskResponse = {
    id: 'synthetic-meshy',
    mode: 'preview',
    status: 'PENDING',
    progress: 0,
    model_urls: {},
    created_at: Date.UTC(2026, 8, 29),
  };
  const tripoTask: TripoTaskData = {
    task_id: 'synthetic-tripo',
    type: 'text_to_model',
    status: 'queued',
    input: {},
    output: {},
    progress: 0,
  };
  mocks.meshyText.mockResolvedValue(meshyTask);
  mocks.meshyImage.mockResolvedValue({ ...meshyTask, id: 'synthetic-meshy-image' });
  mocks.tripoText.mockResolvedValue(tripoTask);
  mocks.tripoImage.mockResolvedValue({ ...tripoTask, task_id: 'synthetic-tripo-image' });
  mocks.upload.mockResolvedValue('synthetic-upload-token');
});
afterEach(() => vi.unstubAllGlobals());

function postRequest(path: string, body: unknown) {
  return new NextRequest(`http://localhost/api/v1/3d/generate/${path}`, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('3D job route contract (mock providers; no generation)', () => {
  it('exports only the jobs HTTP handler', async () => {
    const route = await import('@/app/api/v1/3d/jobs/route');
    expect(Object.keys(route)).toEqual(['GET']);
  });

  it.each(['meshy', 'tripo'])('lists %s text and image submissions newest first', async provider => {
    const { POST: text } = await import('@/app/api/v1/3d/generate/text/route');
    const { POST: image } = await import('@/app/api/v1/3d/generate/image/route');
    const { GET } = await import('@/app/api/v1/3d/jobs/route');
    const textResponse = await text(postRequest('text', { prompt: 'Synthetic cube', provider }), undefined);
    const imageResponse = await image(
      postRequest('image', { image_url: 'https://fixture.example.test/cube.png', provider }),
      undefined
    );
    expect(textResponse.status).toBe(200);
    expect(imageResponse.status).toBe(200);
    const textJob = await textResponse.json();
    const imageJob = await imageResponse.json();
    expect(textJob).toMatchObject({ provider, status: 'queued', input_type: 'text', input: 'Synthetic cube' });
    expect(imageJob).toMatchObject({
      provider,
      status: 'queued',
      input_type: 'image',
      input: 'https://fixture.example.test/cube.png',
    });
    const list = await GET(new NextRequest('http://localhost/api/v1/3d/jobs'), undefined);
    expect(await list.json()).toEqual([imageJob, textJob]);
    const limited = await GET(new NextRequest('http://localhost/api/v1/3d/jobs?limit=1'), undefined);
    expect(await limited.json()).toEqual([imageJob]);
    expect(mocks.fetch).not.toHaveBeenCalled();
  });

  it('keeps all three handlers authenticated before provider work', async () => {
    mocks.session.mockResolvedValue(null);
    const { POST: text } = await import('@/app/api/v1/3d/generate/text/route');
    const { POST: image } = await import('@/app/api/v1/3d/generate/image/route');
    const { GET } = await import('@/app/api/v1/3d/jobs/route');
    expect((await text(postRequest('text', { prompt: 'Synthetic cube' }), undefined)).status).toBe(401);
    expect(
      (await image(postRequest('image', { image_url: 'https://fixture.example.test/cube.png' }), undefined)).status
    ).toBe(401);
    expect((await GET(new NextRequest('http://localhost/api/v1/3d/jobs'), undefined)).status).toBe(401);
    for (const provider of [
      mocks.meshyText,
      mocks.meshyImage,
      mocks.tripoText,
      mocks.tripoImage,
      mocks.upload,
      mocks.fetch,
    ]) {
      expect(provider).not.toHaveBeenCalled();
    }
  });
});
