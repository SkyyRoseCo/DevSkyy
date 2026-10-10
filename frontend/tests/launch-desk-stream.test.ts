import { describe, expect, it, vi } from 'vitest';
import { LAUNCH_TOOLS, readLaunchStream } from '@/app/admin/launch-desk/stream';

const tools = LAUNCH_TOOLS.map(name => `data: ${JSON.stringify({ type: 'tool', name, phase: 'completed' })}\n\n`).join(
  ''
);
const text = 'data: {"type":"text_delta","delta":"Plan"}\n\n';
const done = 'data: {"type":"done"}\n\n';

function chunks(...values: string[]) {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      values.forEach(value => controller.enqueue(new TextEncoder().encode(value)));
      controller.close();
    },
  });
}

describe('Launch Desk browser stream', () => {
  it('handles events split across network chunks', async () => {
    const receive = vi.fn();
    await readLaunchStream(
      chunks(tools, 'data: {"type":"text_', 'delta","delta":"Plan"}\n', '\ndata: {"type":"done"}\n\n'),
      receive
    );
    expect(receive.mock.calls.map(([event]) => event.type)).toEqual([
      'tool',
      'tool',
      'tool',
      'tool',
      'text_delta',
      'done',
    ]);
  });
  it('accepts CRLF-delimited events', async () => {
    await expect(
      readLaunchStream(chunks((tools + text + done).replaceAll('\n', '\r\n')), vi.fn())
    ).resolves.toBeUndefined();
  });
  it('rejects a truncated response', async () => {
    await expect(
      readLaunchStream(chunks('data: {"type":"text_delta","delta":"Partial"}\n\n'), vi.fn())
    ).rejects.toThrow('before the plan completed');
  });
  it('propagates server failures instead of reporting completion', async () => {
    await expect(readLaunchStream(chunks('data: {"type":"error","message":"Try later"}\n\n'), vi.fn())).rejects.toThrow(
      'Try later'
    );
  });
  it.each([done, tools + done, text + done, tools + 'data: {"type":"text_delta","delta":"  "}\n\n' + done])(
    'rejects success without all tools and nonempty output',
    async input => {
      await expect(readLaunchStream(chunks(input), vi.fn())).rejects.toThrow('all planning tools');
    }
  );
  it('rejects events after terminal success', async () => {
    await expect(readLaunchStream(chunks(tools + text + done + text), vi.fn())).rejects.toThrow('after completion');
  });
  it('cancels an upstream stream after an invalid event', async () => {
    const cancel = vi.fn();
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('data: invalid-json\n\n'));
      },
      cancel,
    });
    await expect(readLaunchStream(stream, vi.fn())).rejects.toThrow();
    expect(cancel).toHaveBeenCalledOnce();
    expect(stream.locked).toBe(false);
  });
  it.each([
    { type: 'meta', traceId: {} },
    { type: 'text_delta', delta: 123 },
    { type: 'tool', name: 'check', phase: 'invented' },
  ])('rejects malformed event fields: %j', async event => {
    const receive = vi.fn();
    await expect(readLaunchStream(chunks(`data: ${JSON.stringify(event)}\n\n`), receive)).rejects.toThrow(
      'invalid event'
    );
    expect(receive).not.toHaveBeenCalled();
  });
});
