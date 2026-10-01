import { describe, expect, it, vi } from 'vitest';
import {
  ExecutionBudgetError,
  LAUNCH_DESK_QUOTE,
  RESERVE_EXECUTION_LUA,
  reserveExecution,
  type BudgetRequest,
} from '@/lib/os-execution-budget';

const env = {
  OS_LAUNCH_DESK_ENABLED: 'true',
  OS_LAUNCH_DESK_POLICY_ID: 'synthetic-policy-20260929',
  OS_LAUNCH_DESK_OWNER_IDS: 'synthetic-owner',
  OS_LAUNCH_DESK_MODEL: 'gpt-6-sol',
  OS_LAUNCH_DESK_MAX_OPERATIONS: '2',
  OS_LAUNCH_DESK_CAP_USD_MICROS: '41850336',
  OS_LAUNCH_DESK_EXPIRES_AT: '2000000000',
  OS_LAUNCH_DESK_MAX_INPUT_BYTES: '262144',
  OS_LAUNCH_DESK_RESERVATION_USD_MICROS: String(LAUNCH_DESK_QUOTE.minimumReservationUsdMicros),
  OS_LAUNCH_DESK_QUOTE_ID: LAUNCH_DESK_QUOTE.id,
  OS_LAUNCH_DESK_QUOTE_SOURCE: LAUNCH_DESK_QUOTE.source,
};
function request(): BudgetRequest {
  return {
    operationKind: 'launch-desk',
    operationId: crypto.randomUUID(),
    traceId: crypto.randomUUID(),
    actorId: 'synthetic-owner',
    model: 'gpt-6-sol',
    serializedInput: JSON.stringify({ instructions: 'Instructions', input: 'Evidence' }),
    executionConfig: 'one turn; 4096 output; zero retries; instructions; SDK; endpoint',
  };
}

describe('OS persistent reservation adapter (synthetic ledger; no authenticated Redis)', () => {
  it('is disabled by default and never creates a ledger request', async () => {
    const evalMock = vi.fn();
    await expect(reserveExecution(request(), { env: {}, ledger: { eval: evalMock } })).rejects.toMatchObject({
      code: 'DISABLED',
    });
    expect(evalMock).not.toHaveBeenCalled();
  });
  it.each(['0', '-1', 'NaN', 'Infinity', '1.5', '1e3', ' 2', '9007199254740992'])(
    'rejects malformed numeric approval %s',
    async value => {
      const evalMock = vi.fn();
      await expect(
        reserveExecution(request(), {
          env: { ...env, OS_LAUNCH_DESK_MAX_OPERATIONS: value },
          ledger: { eval: evalMock },
        })
      ).rejects.toMatchObject({ code: 'INVALID_POLICY' });
      expect(evalMock).not.toHaveBeenCalled();
    }
  );
  it.each([
    'OS_LAUNCH_DESK_MAX_OPERATIONS',
    'OS_LAUNCH_DESK_CAP_USD_MICROS',
    'OS_LAUNCH_DESK_EXPIRES_AT',
    'OS_LAUNCH_DESK_MAX_INPUT_BYTES',
    'OS_LAUNCH_DESK_RESERVATION_USD_MICROS',
    'OS_LAUNCH_DESK_POLICY_ID',
    'OS_LAUNCH_DESK_MODEL',
    'OS_LAUNCH_DESK_QUOTE_ID',
    'OS_LAUNCH_DESK_QUOTE_SOURCE',
    'OS_LAUNCH_DESK_OWNER_IDS',
  ])('requires explicit %s', async name => {
    await expect(
      reserveExecution(request(), { env: { ...env, [name]: '' }, ledger: { eval: vi.fn() } })
    ).rejects.toBeInstanceOf(ExecutionBudgetError);
  });
  it('cannot underquote or switch to an unknown-priced model', async () => {
    await expect(
      reserveExecution(request(), { env: { ...env, OS_LAUNCH_DESK_RESERVATION_USD_MICROS: '1' } })
    ).rejects.toMatchObject({ code: 'INVALID_POLICY' });
    await expect(reserveExecution({ ...request(), model: 'unknown' }, { env })).rejects.toMatchObject({
      code: 'INVALID_POLICY',
    });
  });
  it('rejects an authenticated user outside the intended owner scope', async () => {
    const evalMock = vi.fn();
    await expect(
      reserveExecution({ ...request(), actorId: 'other-user' }, { env, ledger: { eval: evalMock } })
    ).rejects.toMatchObject({ code: 'OWNER_SCOPE' });
    expect(evalMock).not.toHaveBeenCalled();
  });
  it('bounds UTF8 input including serialized instructions and evidence', async () => {
    const evalMock = vi.fn();
    await expect(
      reserveExecution(
        { ...request(), serializedInput: '🧵'.repeat(10) },
        {
          env: { ...env, OS_LAUNCH_DESK_MAX_INPUT_BYTES: '39' },
          ledger: { eval: evalMock },
        }
      )
    ).rejects.toMatchObject({ code: 'INPUT_LIMIT' });
    expect(evalMock).not.toHaveBeenCalled();
  });
  it('requires a persistent ledger and sanitizes failures without retry', async () => {
    await expect(reserveExecution(request(), { env })).rejects.toMatchObject({ code: 'LEDGER_UNAVAILABLE' });
    const evalMock = vi.fn().mockRejectedValue(new Error('SECRET_REDIS_DETAIL'));
    await expect(reserveExecution(request(), { env, ledger: { eval: evalMock } })).rejects.toThrow(
      'explicit, unchanged spending policy'
    );
    expect(evalMock).toHaveBeenCalledOnce();
  });
  it.each(['POLICY_CHANGED', 'EXPIRED', 'REPLAY', 'OPERATION_LIMIT', 'SPENDING_LIMIT'])(
    'propagates atomic %s denial',
    async code => {
      await expect(
        reserveExecution(request(), { env, ledger: { eval: vi.fn().mockResolvedValue([code]) } })
      ).rejects.toMatchObject({ code });
    }
  );
  it('uses one stable policy key across input changes; binds configuration independently', async () => {
    const evalMock = vi.fn().mockResolvedValue(['RESERVED', '1', '20925168']);
    const ledger = { eval: evalMock };
    await reserveExecution(request(), { env, ledger });
    await reserveExecution({ ...request(), serializedInput: 'Different evidence' }, { env, ledger });
    await reserveExecution(request(), { env: { ...env, OS_LAUNCH_DESK_CAP_USD_MICROS: '99999999' }, ledger });
    const calls = evalMock.mock.calls;
    expect(calls[0][0]).toBe(RESERVE_EXECUTION_LUA);
    expect(calls.map(call => call[1])).toEqual(Array(3).fill(['os-execution-budget:v1:synthetic-policy-20260929']));
    expect(calls[0][2][0]).toBe(calls[1][2][0]);
    expect(calls[0][2][0]).not.toBe(calls[2][2][0]);
    expect(JSON.parse(calls[0][2][7]).inputBytes).toBe(Buffer.byteLength(request().serializedInput));
    expect(JSON.parse(calls[0][2][7]).traceId).toMatch(/^[0-9a-f-]{36}$/);
  });
  it('binds a sanitized provider response receipt to the trace and operation without refund', async () => {
    const evalMock = vi.fn().mockResolvedValueOnce(['RESERVED', '1', '20925168']).mockResolvedValueOnce(1);
    const input = request();
    const reservation = await reserveExecution(input, { env, ledger: { eval: evalMock } });
    await reservation.recordProviderResponse('resp_synthetic');
    expect(evalMock.mock.calls[1][2]).toEqual([input.operationId, input.traceId, 'resp_synthetic']);
    expect(evalMock.mock.calls[1][1]).toEqual(evalMock.mock.calls[0][1]);
    await expect(reservation.recordProviderResponse('SECRET\nDETAIL')).rejects.toMatchObject({
      code: 'LEDGER_UNAVAILABLE',
    });
    expect(evalMock).toHaveBeenCalledTimes(2);
  });
});
