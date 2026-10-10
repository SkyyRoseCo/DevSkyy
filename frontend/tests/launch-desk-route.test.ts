import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

const mocks = vi.hoisted(() => ({ run: vi.fn(), reserve: vi.fn(), receipt: vi.fn(), authenticated: true }));
vi.mock('next-auth', () => ({
  getServerSession: async () => (mocks.authenticated ? { user: { email: 'synthetic-user@example.test' } } : null),
}));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/os-execution-budget', async original => ({
  ...(await original<typeof import('@/lib/os-execution-budget')>()),
  reserveExecution: mocks.reserve,
}));
vi.mock('@/app/api/launch-desk/_lib/agent', () => ({
  createLaunchDeskAgent: () => ({}),
  createLaunchDeskRunner: () => ({ run: mocks.run }),
  launchDeskModel: () => 'gpt-6-sol',
  formatLaunchPrompt: () => 'Synthetic test input',
  launchDeskExecutionConfig: () => 'Synthetic instructions and bounded settings',
}));
import { POST } from '@/app/api/launch-desk/route';
import { ExecutionBudgetError } from '@/lib/os-execution-budget';

function request(
  body: unknown = { productBrief: 'Release a documented API with rollback and support.', audience: 'Developers' }
) {
  return new NextRequest('http://localhost/api/launch-desk', {
    method: 'POST',
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': crypto.randomUUID(),
    },
  });
}

beforeEach(() => {
  vi.stubEnv('OPENAI_API_KEY', 'synthetic-test-key');
  mocks.authenticated = true;
  mocks.run.mockReset();
  mocks.receipt.mockReset().mockImplementation(async (responseId: string) => {
    if (!/^resp_[A-Za-z0-9_-]{1,180}$/.test(responseId)) throw new ExecutionBudgetError('LEDGER_UNAVAILABLE');
  });
  mocks.reserve.mockReset().mockImplementation(async input => ({
    operationId: input.operationId,
    traceId: input.traceId,
    reservedUsdMicros: 20_925_168,
    recordProviderResponse: mocks.receipt,
  }));
});
afterEach(() => vi.unstubAllEnvs());

describe('Launch Desk route contract (mock provider; no live inference)', () => {
  it('rejects unauthenticated requests before invoking a provider', async () => {
    mocks.authenticated = false;
    expect((await POST(request(), undefined)).status).toBe(401);
    expect(mocks.run).not.toHaveBeenCalled();
    expect(mocks.reserve).not.toHaveBeenCalled();
  });
  it('fails closed without a server credential', async () => {
    vi.stubEnv('OPENAI_API_KEY', '');
    expect((await POST(request(), undefined)).status).toBe(503);
    expect(mocks.run).not.toHaveBeenCalled();
  });
  it('rejects invalid briefs before invoking a provider', async () => {
    expect((await POST(request({ productBrief: 'short' }), undefined)).status).toBe(400);
    expect(mocks.run).not.toHaveBeenCalled();
  });
  it('streams output and completion after bounded provider execution', async () => {
    mocks.run.mockResolvedValue({
      async *[Symbol.asyncIterator]() {
        yield { type: 'raw_model_stream_event', data: { type: 'output_text_delta', delta: 'Test plan' } };
        yield {
          type: 'raw_model_stream_event',
          data: { type: 'response_done', response: { id: 'resp_synthetic', providerData: { status: 'completed' } } },
        };
      },
      completed: Promise.resolve(),
    });
    const response = await POST(request(), undefined);
    const output = await response.text();
    expect(output).toContain('"delta":"Test plan"');
    expect(output).toContain('"type":"done"');
    expect(mocks.run.mock.calls[0][2]).toMatchObject({ maxTurns: 1, stream: true });
    expect(mocks.run.mock.calls[0][2].signal).toBeInstanceOf(AbortSignal);
    expect(mocks.reserve).toHaveBeenCalledBefore(mocks.run);
    expect(mocks.reserve.mock.calls[0][0]).toMatchObject({
      actorId: 'synthetic-user@example.test',
      model: 'gpt-6-sol',
    });
    expect(mocks.reserve.mock.calls[0][0].serializedInput).toContain('Synthetic instructions');
    expect((output.match(/"phase":"completed"/g) ?? []).length).toBe(4);
    expect(output).toContain(mocks.reserve.mock.calls[0][0].operationId);
    expect(output).toContain(mocks.reserve.mock.calls[0][0].traceId);
    expect(mocks.receipt).toHaveBeenCalledWith('resp_synthetic');
  });
  it('does not mark provider failures complete or leak their details', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    mocks.run.mockRejectedValue(new Error('PRIVATE_PROVIDER_DETAIL'));
    const output = await (await POST(request(), undefined)).text();
    expect(output).toContain('"type":"error"');
    expect(output).not.toContain('"type":"done"');
    expect(output).not.toContain('PRIVATE_PROVIDER_DETAIL');
    expect(JSON.stringify(log.mock.calls)).not.toContain('PRIVATE_PROVIDER_DETAIL');
    log.mockRestore();
  });
  it.each(['incomplete', 'failed', 'missing'])('rejects a %s terminal response', async status => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    mocks.run.mockResolvedValue({
      async *[Symbol.asyncIterator]() {
        yield { type: 'raw_model_stream_event', data: { type: 'output_text_delta', delta: 'Partial plan' } };
        if (status !== 'missing')
          yield {
            type: 'raw_model_stream_event',
            data: {
              type: 'response_done',
              response: { providerData: { status, incomplete_details: { reason: 'max_output_tokens' } } },
            },
          };
      },
      completed: Promise.resolve(),
    });
    const output = await (await POST(request(), undefined)).text();
    expect(output).toContain('"type":"error"');
    expect(output).not.toContain('"type":"done"');
    log.mockRestore();
  });
  it('aborts provider work when the response consumer cancels', async () => {
    mocks.run.mockImplementation(
      (_agent, _input, { signal }: { signal: AbortSignal }) =>
        new Promise((_resolve, reject) => {
          signal.addEventListener('abort', () => reject(new DOMException('Cancelled', 'AbortError')), { once: true });
        })
    );
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    const response = await POST(request(), undefined);
    await response.body!.cancel();
    expect(mocks.run.mock.calls[0][2].signal.aborted).toBe(true);
    expect(mocks.reserve).toHaveBeenCalledOnce();
    log.mockRestore();
  });
  it.each(['', '  \n\t'])('rejects completed provider output without visible text (%j)', async delta => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    mocks.run.mockResolvedValue({
      async *[Symbol.asyncIterator]() {
        yield { type: 'raw_model_stream_event', data: { type: 'output_text_delta', delta } };
        yield {
          type: 'raw_model_stream_event',
          data: { type: 'response_done', response: { providerData: { status: 'completed' } } },
        };
      },
      completed: Promise.resolve(),
    });
    const output = await (await POST(request(), undefined)).text();
    expect(output).toContain('"type":"error"');
    expect(output).not.toContain('"type":"done"');
    expect(mocks.reserve).toHaveBeenCalledOnce();
    log.mockRestore();
  });
  it.each([
    ['DISABLED', 503],
    ['LEDGER_UNAVAILABLE', 503],
    ['POLICY_CHANGED', 503],
    ['OWNER_SCOPE', 403],
    ['REPLAY', 409],
    ['SPENDING_LIMIT', 429],
    ['OPERATION_LIMIT', 429],
  ] as const)('denies %s before any provider execution', async (code, status) => {
    mocks.reserve.mockRejectedValue(new ExecutionBudgetError(code));
    const response = await POST(request(), undefined);
    expect(response.status).toBe(status);
    expect((await response.json()).code).toBe(code);
    expect(mocks.run).not.toHaveBeenCalled();
  });
  it('retains the reservation and rejects success when provider receipt storage fails', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    mocks.receipt.mockRejectedValue(new ExecutionBudgetError('LEDGER_UNAVAILABLE'));
    mocks.run.mockResolvedValue({
      async *[Symbol.asyncIterator]() {
        yield { type: 'raw_model_stream_event', data: { type: 'output_text_delta', delta: 'Test plan' } };
        yield {
          type: 'raw_model_stream_event',
          data: {
            type: 'response_done',
            response: {
              id: 'resp_synthetic',
              providerData: { status: 'completed' },
            },
          },
        };
      },
      completed: Promise.resolve(),
    });
    const output = await (await POST(request(), undefined)).text();
    expect(output).toContain('"type":"error"');
    expect(output).not.toContain('"type":"done"');
    expect(output).toContain(mocks.reserve.mock.calls[0][0].traceId);
    expect(output).toContain(mocks.reserve.mock.calls[0][0].operationId);
    expect(mocks.run).toHaveBeenCalledOnce();
    expect(mocks.reserve).toHaveBeenCalledOnce();
    expect(mocks.receipt).toHaveBeenCalledOnce();
    log.mockRestore();
  });
  it.each([undefined, '', 'invalid-provider-id'])(
    'rejects completed text with missing/invalid provider ID %j',
    async id => {
      const log = vi.spyOn(console, 'error').mockImplementation(() => {});
      mocks.run.mockResolvedValue({
        async *[Symbol.asyncIterator]() {
          yield { type: 'raw_model_stream_event', data: { type: 'output_text_delta', delta: 'Test plan' } };
          yield {
            type: 'raw_model_stream_event',
            data: {
              type: 'response_done',
              response: {
                id,
                providerData: { status: 'completed' },
              },
            },
          };
        },
        completed: Promise.resolve(),
      });
      const output = await (await POST(request(), undefined)).text();
      expect(output).toContain('"type":"error"');
      expect(output).not.toContain('"type":"done"');
      expect(mocks.reserve).toHaveBeenCalledOnce();
      expect(mocks.run).toHaveBeenCalledOnce();
      expect(mocks.receipt).toHaveBeenCalledOnce();
      log.mockRestore();
    }
  );
});
