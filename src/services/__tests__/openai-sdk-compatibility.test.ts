import { createRequire } from 'node:module';
import type OpenAI from 'openai';
import { describe, expect, it, vi } from 'vitest';

const require = createRequire(import.meta.url);
// Match the two direct SDK consumers without importing their executable demos:
// skyyrose/build/{tool-calling,generate-models-2vision}.js.
const constructors: [string, typeof OpenAI][] = [
  ['named CommonJS export', (require('openai') as { OpenAI: typeof OpenAI }).OpenAI],
  ['direct CommonJS export', require('openai') as typeof OpenAI],
];

function completion(message: object) {
  return new Response(
    JSON.stringify({
      id: 'offline-completion',
      object: 'chat.completion',
      created: 0,
      model: 'offline-model',
      choices: [{ index: 0, finish_reason: 'stop', message }],
    }),
    { headers: { 'content-type': 'application/json' } }
  );
}

describe.each(constructors)('OpenAI SDK compatibility: %s', (_name, Constructor) => {
  it('preserves tool schemas, argument JSON, and the follow-up tool result', async () => {
    const requests: Request[] = [];
    const toolCall = {
      id: 'offline-call',
      type: 'function' as const,
      function: { name: 'lookup', arguments: JSON.stringify({ query: 'offline fixture' }) },
    };
    const fetch = vi.fn<typeof globalThis.fetch>(async (input, init) => {
      requests.push(new Request(input, init));
      return requests.length === 1
        ? completion({ role: 'assistant', content: null, tool_calls: [toolCall] })
        : completion({ role: 'assistant', content: 'Offline lookup complete' });
    });
    const client = new Constructor({
      apiKey: 'offline-test-key',
      baseURL: 'https://sdk-test.invalid/v1',
      maxRetries: 0,
      fetch,
    });
    const tools: OpenAI.Chat.Completions.ChatCompletionTool[] = [
      {
        type: 'function',
        function: {
          name: 'lookup',
          description: 'Offline fixture',
          parameters: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] },
        },
      },
    ];
    const first = await client.chat.completions.create({
      model: 'offline-model',
      messages: [{ role: 'user', content: 'Find a fixture' }],
      tools,
    });
    const message = first.choices[0]!.message;
    expect(message.tool_calls).toEqual([toolCall]);
    const returnedToolCall = message.tool_calls![0]!;
    if (returnedToolCall.type !== 'function') throw new Error('Expected a function tool call');
    expect(JSON.parse(returnedToolCall.function.arguments)).toEqual({ query: 'offline fixture' });
    const second = await client.chat.completions.create({
      model: 'offline-model',
      messages: [
        { role: 'user', content: 'Find a fixture' },
        message,
        { role: 'tool', tool_call_id: returnedToolCall.id, content: '{"found":1}' },
      ],
      tools,
    });
    expect(second.choices[0]!.message.content).toBe('Offline lookup complete');
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(requests[0]!.url).toBe('https://sdk-test.invalid/v1/chat/completions');
    expect(await requests[0]!.json()).toMatchObject({ model: 'offline-model', tools });
    expect(await requests[1]!.json()).toMatchObject({
      messages: [
        { role: 'user', content: 'Find a fixture' },
        { role: 'assistant', tool_calls: [toolCall] },
        { role: 'tool', tool_call_id: 'offline-call', content: '{"found":1}' },
      ],
    });
  });

  it('preserves the vision content shape and text response used by the image-analysis consumer', async () => {
    const requests: Request[] = [];
    const fetch = vi.fn<typeof globalThis.fetch>(async (input, init) => {
      requests.push(new Request(input, init));
      return completion({ role: 'assistant', content: 'Offline response fixture' });
    });
    const client = new Constructor({
      apiKey: 'offline-test-key',
      baseURL: 'https://sdk-test.invalid/v1',
      maxRetries: 0,
      fetch,
    });
    const content: OpenAI.Chat.Completions.ChatCompletionContentPart[] = [
      { type: 'text', text: 'Offline serialization fixture' },
      { type: 'image_url', image_url: { url: 'data:image/jpeg;base64,AA==', detail: 'high' } },
    ];
    const response = await client.chat.completions.create({
      model: 'offline-model',
      messages: [{ role: 'user', content }],
      max_tokens: 1500,
      temperature: 0.3,
    });
    expect(response.choices[0]!.message.content).toBe('Offline response fixture');
    expect(await requests[0]!.json()).toMatchObject({
      messages: [{ role: 'user', content }],
      max_tokens: 1500,
      temperature: 0.3,
    });
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});
