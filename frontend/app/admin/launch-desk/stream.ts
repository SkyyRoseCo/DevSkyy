export interface LaunchStreamEvent {
  type: 'meta' | 'tool' | 'text_delta' | 'done' | 'error';
  traceId?: string;
  operationId?: string;
  name?: string;
  phase?: 'started' | 'completed';
  delta?: string;
  message?: string;
}

export const LAUNCH_TOOLS = [
  'extract_launch_tasks',
  'check_launch_readiness',
  'generate_owner_checklists',
  'draft_channel_launch_copy',
] as const;

function parseEvent(data: string): LaunchStreamEvent {
  const value: unknown = JSON.parse(data);
  if (!value || typeof value !== 'object') throw new Error('Launch Desk returned an invalid event.');
  const event = value as Record<string, unknown>;
  const validType =
    typeof event.type === 'string' && ['meta', 'tool', 'text_delta', 'done', 'error'].includes(event.type);
  const validStrings = ['traceId', 'operationId', 'name', 'delta', 'message'].every(
    field => event[field] === undefined || typeof event[field] === 'string'
  );
  const validPhase = event.phase === undefined || event.phase === 'started' || event.phase === 'completed';
  if (
    !validType ||
    !validStrings ||
    !validPhase ||
    (event.type === 'text_delta' && typeof event.delta !== 'string') ||
    (event.type === 'tool' && (typeof event.name !== 'string' || event.phase === undefined))
  ) {
    throw new Error('Launch Desk returned an invalid event.');
  }
  return event as unknown as LaunchStreamEvent;
}

/** Consume the server's SSE contract; EOF is never evidence of success. */
export async function readLaunchStream(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: LaunchStreamEvent) => void
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let completed = false;
  let text = '';
  const tools = new Set<string>();
  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += done ? decoder.decode() : decoder.decode(value, { stream: true });
      const blocks = buffer.split(/\r?\n\r?\n/);
      buffer = blocks.pop() ?? '';
      for (const block of blocks) {
        const data = block
          .split(/\r?\n/)
          .filter(line => line.startsWith('data:'))
          .map(line => line.slice(5).trimStart())
          .join('\n');
        if (!data) continue;
        const event = parseEvent(data);
        if (event.type === 'error') throw new Error(event.message || 'Launch planning failed.');
        if (completed) throw new Error('Launch Desk returned an event after completion.');
        if (event.type === 'text_delta') text += event.delta;
        if (event.type === 'tool' && event.phase === 'completed' && event.name) tools.add(event.name);
        if (event.type === 'done') {
          if (!text.trim() || !LAUNCH_TOOLS.every(tool => tools.has(tool))) {
            throw new Error('Launch Desk did not complete all planning tools and a nonempty plan.');
          }
          completed = true;
        }
        onEvent(event);
      }
      if (done) break;
    }
    if (!completed)
      throw new Error('The connection ended before the plan completed. Contact the operator before retrying.');
  } finally {
    await reader.cancel().catch(() => undefined);
    reader.releaseLock();
  }
}
