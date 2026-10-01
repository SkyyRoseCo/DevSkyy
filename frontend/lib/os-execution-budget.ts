import { createHash } from 'node:crypto';
import { Redis } from '@upstash/redis';

// Source verified 2026-09-29. This deliberately reserves the full context,
// adds input AND cache-write charges, and includes long-context, regional and
// Fast premiums. It is a pessimistic reservation, not a token estimate.
export const LAUNCH_DESK_QUOTE = {
  model: 'gpt-6-sol',
  source: 'https://developers.openai.com/api/docs/models/gpt-6-sol',
  id: 'gpt-6-sol-full-context-20260929-v1',
  contextTokens: 1_050_000,
  maxOutputTokens: 4096,
  minimumReservationUsdMicros: 20_925_168,
} as const;

type BudgetCode =
  | 'DISABLED'
  | 'INVALID_POLICY'
  | 'INPUT_LIMIT'
  | 'POLICY_CHANGED'
  | 'EXPIRED'
  | 'REPLAY'
  | 'OPERATION_LIMIT'
  | 'SPENDING_LIMIT'
  | 'LEDGER_UNAVAILABLE'
  | 'OWNER_SCOPE';

export class ExecutionBudgetError extends Error {
  constructor(public readonly code: BudgetCode) {
    super('Execution requires an available ledger and an explicit, unchanged spending policy.');
    this.name = 'ExecutionBudgetError';
  }
}

interface Policy {
  id: string;
  model: string;
  maxOperations: number;
  capUsdMicros: number;
  expiresAt: number;
  maxInputBytes: number;
  reservationUsdMicros: number;
  quoteId: string;
  quoteSource: string;
  ownerIds: string[];
}

export interface BudgetRequest {
  operationKind: 'launch-desk';
  operationId: string;
  traceId: string;
  actorId: string;
  model: string;
  serializedInput: string;
  // Includes instructions, SDK version, endpoint, turn/output/retry bounds and
  // model settings. Dynamic user input is recorded separately per reservation.
  executionConfig: string;
}

export interface BudgetLedger {
  eval(script: string, keys: string[], args: (string | number)[]): Promise<unknown>;
}

export interface ExecutionReservation {
  operationId: string;
  traceId: string;
  reservedUsdMicros: number;
  recordProviderResponse(responseId: string): Promise<void>;
}

function hash(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

type BudgetEnvironment = Readonly<Record<string, string | undefined>>;

function integer(env: BudgetEnvironment, name: string, max = 1_000_000_000_000): number {
  const raw = env[name];
  if (!raw || !/^[1-9]\d*$/.test(raw)) throw new ExecutionBudgetError('INVALID_POLICY');
  const value = Number(raw);
  if (!Number.isSafeInteger(value) || value > max) throw new ExecutionBudgetError('INVALID_POLICY');
  return value;
}

function policyFromEnv(env: BudgetEnvironment): Policy {
  if (env.OS_LAUNCH_DESK_ENABLED !== 'true') throw new ExecutionBudgetError('DISABLED');
  const id = env.OS_LAUNCH_DESK_POLICY_ID ?? '';
  if (!/^[A-Za-z0-9][A-Za-z0-9_-]{7,79}$/.test(id)) throw new ExecutionBudgetError('INVALID_POLICY');
  const ownerIds = [...new Set((env.OS_LAUNCH_DESK_OWNER_IDS ?? '').split(',').map(id => id.trim()))].sort();
  if (!ownerIds.length || ownerIds.length > 20 || ownerIds.some(id => !/^[A-Za-z0-9@._:+-]{1,128}$/.test(id)))
    throw new ExecutionBudgetError('INVALID_POLICY');
  const policy = {
    id,
    model: env.OS_LAUNCH_DESK_MODEL ?? '',
    maxOperations: integer(env, 'OS_LAUNCH_DESK_MAX_OPERATIONS', 10_000),
    capUsdMicros: integer(env, 'OS_LAUNCH_DESK_CAP_USD_MICROS'),
    expiresAt: integer(env, 'OS_LAUNCH_DESK_EXPIRES_AT', 4_102_444_800),
    maxInputBytes: integer(env, 'OS_LAUNCH_DESK_MAX_INPUT_BYTES', 262_144),
    reservationUsdMicros: integer(env, 'OS_LAUNCH_DESK_RESERVATION_USD_MICROS'),
    quoteId: env.OS_LAUNCH_DESK_QUOTE_ID ?? '',
    quoteSource: env.OS_LAUNCH_DESK_QUOTE_SOURCE ?? '',
    ownerIds,
  };
  if (
    policy.model !== LAUNCH_DESK_QUOTE.model ||
    policy.quoteId !== LAUNCH_DESK_QUOTE.id ||
    policy.quoteSource !== LAUNCH_DESK_QUOTE.source ||
    policy.reservationUsdMicros < LAUNCH_DESK_QUOTE.minimumReservationUsdMicros
  ) {
    throw new ExecutionBudgetError('INVALID_POLICY');
  }
  return policy;
}

/** One atomic persistent reservation; no TTL, refunds, retry or replay path. */
export const RESERVE_EXECUTION_LUA = `
local key = KEYS[1]
local digest = ARGV[1]
local previous = redis.call('HGET', key, 'policy_digest')
if previous and previous ~= digest then return {'POLICY_CHANGED'} end
local now = tonumber(redis.call('TIME')[1])
if now >= tonumber(ARGV[2]) then return {'EXPIRED'} end
local op = 'operation:' .. ARGV[3]
if redis.call('HEXISTS', key, op) == 1 then return {'REPLAY'} end
local count = tonumber(redis.call('HGET', key, 'reserved_operations') or '0')
local spend = tonumber(redis.call('HGET', key, 'reserved_usd_micros') or '0')
local amount = tonumber(ARGV[6])
if count + 1 > tonumber(ARGV[4]) then return {'OPERATION_LIMIT'} end
if spend + amount > tonumber(ARGV[5]) then return {'SPENDING_LIMIT'} end
redis.call('HSET', key, 'policy_digest', digest, 'policy', ARGV[7],
  'reserved_operations', count + 1, 'reserved_usd_micros', spend + amount,
  op, ARGV[8])
return {'RESERVED', tostring(count + 1), tostring(spend + amount)}
`;

const RECORD_PROVIDER_RESPONSE_LUA = `
local receipt = redis.call('HGET', KEYS[1], 'operation:' .. ARGV[1])
if not receipt then return 0 end
local operation = cjson.decode(receipt)
if operation.traceId ~= ARGV[2] then return 0 end
redis.call('HSET', KEYS[1], 'provider_response:' .. ARGV[1], ARGV[3])
return 1
`;

function persistentLedger(env: BudgetEnvironment): BudgetLedger {
  const url = env.UPSTASH_REDIS_REST_URL;
  const token = env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) throw new ExecutionBudgetError('LEDGER_UNAVAILABLE');
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' || parsed.username || parsed.password || parsed.search || parsed.hash) {
      throw new Error('Invalid ledger URL');
    }
    return new Redis({ url, token, retry: false, enableAutoPipelining: false });
  } catch {
    throw new ExecutionBudgetError('LEDGER_UNAVAILABLE');
  }
}

export async function reserveExecution(
  request: BudgetRequest,
  options: { env?: BudgetEnvironment; ledger?: BudgetLedger } = {}
): Promise<ExecutionReservation> {
  const env = options.env ?? process.env;
  const policy = policyFromEnv(env);
  if (!request.actorId || !policy.ownerIds.includes(request.actorId)) throw new ExecutionBudgetError('OWNER_SCOPE');
  if (
    request.operationKind !== 'launch-desk' ||
    request.model !== policy.model ||
    !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(request.operationId) ||
    !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(request.traceId) ||
    !request.executionConfig
  )
    throw new ExecutionBudgetError('INVALID_POLICY');
  const inputBytes = Buffer.byteLength(request.serializedInput, 'utf8');
  if (!inputBytes || inputBytes > policy.maxInputBytes) throw new ExecutionBudgetError('INPUT_LIMIT');
  const configuration = JSON.stringify({
    version: 1,
    ...policy,
    operationKind: request.operationKind,
    quote: LAUNCH_DESK_QUOTE,
    executionDigest: hash(request.executionConfig),
  });
  const ledger = options.ledger ?? persistentLedger(env);
  let result: unknown;
  try {
    result = await ledger.eval(
      RESERVE_EXECUTION_LUA,
      [`os-execution-budget:v1:${policy.id}`],
      [
        hash(configuration),
        policy.expiresAt,
        request.operationId,
        policy.maxOperations,
        policy.capUsdMicros,
        policy.reservationUsdMicros,
        configuration,
        JSON.stringify({
          operationId: request.operationId,
          traceId: request.traceId,
          actorDigest: hash(request.actorId),
          inputBytes,
          inputDigest: hash(request.serializedInput),
          reservedUsdMicros: policy.reservationUsdMicros,
        }),
      ]
    );
  } catch {
    // A lost acknowledgement may still have committed a reservation. Do not
    // retry, refund, or invoke the provider on an uncertain ledger result.
    throw new ExecutionBudgetError('LEDGER_UNAVAILABLE');
  }
  if (!Array.isArray(result) || result[0] !== 'RESERVED') {
    const known: BudgetCode[] = ['POLICY_CHANGED', 'EXPIRED', 'REPLAY', 'OPERATION_LIMIT', 'SPENDING_LIMIT'];
    const code = Array.isArray(result) && known.includes(result[0]) ? (result[0] as BudgetCode) : 'LEDGER_UNAVAILABLE';
    throw new ExecutionBudgetError(code);
  }
  return {
    operationId: request.operationId,
    traceId: request.traceId,
    reservedUsdMicros: policy.reservationUsdMicros,
    async recordProviderResponse(responseId: string) {
      if (!/^resp_[A-Za-z0-9_-]{1,180}$/.test(responseId)) throw new ExecutionBudgetError('LEDGER_UNAVAILABLE');
      try {
        const recorded = await ledger.eval(
          RECORD_PROVIDER_RESPONSE_LUA,
          [`os-execution-budget:v1:${policy.id}`],
          [request.operationId, request.traceId, responseId]
        );
        if (recorded !== 1) throw new Error('Receipt unavailable');
      } catch {
        throw new ExecutionBudgetError('LEDGER_UNAVAILABLE');
      }
    },
  };
}
