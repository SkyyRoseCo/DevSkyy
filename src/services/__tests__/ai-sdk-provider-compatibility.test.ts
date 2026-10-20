import { createRequire } from 'node:module';
import { createAmazonBedrock } from '@ai-sdk/amazon-bedrock';
import { createAnthropic } from '@ai-sdk/anthropic';
import { createAzure } from '@ai-sdk/azure';
import { createCohere } from '@ai-sdk/cohere';
import { createGateway } from '@ai-sdk/gateway';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createVertex } from '@ai-sdk/google-vertex';
import { createGroq } from '@ai-sdk/groq';
import { createHuggingFace } from '@ai-sdk/huggingface';
import { createMistral } from '@ai-sdk/mistral';
import { createOpenAI } from '@ai-sdk/openai';
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';
import { createXai } from '@ai-sdk/xai';
import { generateText, type LanguageModel } from 'ai';
import { describe, expect, it, vi } from 'vitest';

// Every AI SDK major introduces a new provider specification. The root `ai`
// core and all 13 root providers must sit on the same generation, otherwise
// `generateText` rejects the model at runtime ("Unsupported model version").
// Each model below is constructed offline with fixture credentials; nothing
// here opens a network connection.
const require = createRequire(import.meta.url);
const offline = { apiKey: 'offline-fixture-key' };
const models: [string, LanguageModel][] = [
  ['amazon-bedrock', createAmazonBedrock({ region: 'us-east-1' })('offline-model')],
  ['anthropic', createAnthropic(offline)('offline-model')],
  ['azure', createAzure({ ...offline, resourceName: 'offline' })('offline-model')],
  ['cohere', createCohere(offline)('command-r-plus')],
  ['gateway', createGateway(offline)('openai/offline-model')],
  ['google', createGoogleGenerativeAI(offline)('offline-model')],
  ['google-vertex', createVertex({ project: 'offline', location: 'us-central1' })('offline-model')],
  ['groq', createGroq(offline)('offline-model')],
  ['huggingface', createHuggingFace(offline)('offline-model')],
  ['mistral', createMistral(offline)('offline-model')],
  ['openai', createOpenAI(offline)('offline-model')],
  [
    'openai-compatible',
    createOpenAICompatible({ ...offline, name: 'offline', baseURL: 'https://offline.invalid' })('offline-model'),
  ],
  ['xai', createXai(offline)('offline-model')],
];

function reply(content: object[]) {
  return new Response(
    JSON.stringify({
      content,
      finishReason: { unified: 'stop', raw: 'stop' },
      usage: {
        inputTokens: { total: 1, noCache: 1, cacheRead: 0, cacheWrite: 0 },
        outputTokens: { total: 1, text: 1, reasoning: 0 },
      },
      warnings: [],
    }),
    { headers: { 'content-type': 'application/json' } }
  );
}

describe('coordinated AI SDK providers', () => {
  it('resolves the root core to AI SDK 7', () => {
    const { version } = require('ai/package.json') as { version: string };
    expect(version.split('.')[0]).toBe('7');
  });

  it.each(models)('%s exposes a core-compatible provider-v4 language model', (_name, model) => {
    expect(typeof model).toBe('object');
    expect(model).toMatchObject({
      specificationVersion: 'v4',
      doGenerate: expect.any(Function),
      doStream: expect.any(Function),
    });
  });

  it('sends a Gateway v4 text request through the injected transport only', async () => {
    const requests: Request[] = [];
    const fetch = vi.fn<typeof globalThis.fetch>(async (input, init) => {
      requests.push(new Request(input, init));
      return reply([{ type: 'text', text: 'Offline text' }]);
    });
    const gateway = createGateway({ ...offline, baseURL: 'https://offline.invalid/v4/ai', fetch });
    const result = await generateText({
      model: gateway('openai/offline-model'),
      prompt: 'Offline prompt',
      maxRetries: 0,
    });
    expect(result.text).toBe('Offline text');
    expect(requests).toHaveLength(1);
    expect(requests[0]!.url).toBe('https://offline.invalid/v4/ai/language-model');
    expect(requests[0]!.headers.get('authorization')).toBe('Bearer offline-fixture-key');
    expect(requests[0]!.headers.get('ai-language-model-specification-version')).toBe('4');
    expect(await requests[0]!.json()).toMatchObject({
      prompt: [{ role: 'user', content: [{ type: 'text', text: 'Offline prompt' }] }],
    });
  });
});
