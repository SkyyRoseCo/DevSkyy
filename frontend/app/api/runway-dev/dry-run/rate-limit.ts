import { createHmac } from 'node:crypto';

import { Queue } from 'bullmq';

export const RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS = 60;
const REDIS_QUEUE_NAME = 'runway-dev-dry-run-rate-limit';
const REDIS_KEY_PREFIX = 'devskyy:rate-limit:runway-dev:dry-run:v1';
const REDIS_OPERATION_TIMEOUT_MS = 3_000;

export type RunwayDryRunRateLimitResult = 'allowed' | 'limited' | 'unavailable';
export type SetIfAbsent = (key: string, ttlSeconds: number) => Promise<boolean>;

const RATE_LIMIT_SET_NX_COMMAND = 'devskyyRunwayDryRunRateLimitSetNx';
const RATE_LIMIT_SET_NX_SCRIPT = [
  "local result = redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2], 'NX')",
  'if result then return 1 else return 0 end',
].join('\n');

let rateLimitQueue: Queue | null | undefined;

function withTimeout<T>(operation: Promise<T>, timeoutMs: number): Promise<T> {
  let timer: ReturnType<typeof setTimeout>;
  return Promise.race([
    operation,
    new Promise<T>((_resolve, reject) => {
      timer = setTimeout(() => reject(new Error('RATE_LIMIT_STORE_TIMEOUT')), timeoutMs);
    }),
  ]).finally(() => clearTimeout(timer));
}

function getRateLimitQueue(): Queue | null {
  if (rateLimitQueue !== undefined) {
    return rateLimitQueue;
  }

  const redisUrl = process.env.REDIS_URL?.trim();
  if (!redisUrl) {
    rateLimitQueue = null;
    return rateLimitQueue;
  }

  try {
    const parsed = new URL(redisUrl);
    if ((parsed.protocol !== 'redis:' && parsed.protocol !== 'rediss:') || !parsed.hostname) {
      rateLimitQueue = null;
      return rateLimitQueue;
    }

    const queue = new Queue(REDIS_QUEUE_NAME, {
      connection: {
        url: redisUrl,
        connectTimeout: 2_000,
        enableOfflineQueue: false,
        maxRetriesPerRequest: 1,
        retryStrategy: attempt => (attempt <= 1 ? 100 : null),
      },
      skipMetasUpdate: true,
    });
    // Prevent an unavailable shared store from surfacing credentials or an
    // unhandled EventEmitter error. The caller receives a closed failure.
    queue.on('error', () => undefined);
    rateLimitQueue = queue;
    return queue;
  } catch {
    rateLimitQueue = null;
    return rateLimitQueue;
  }
}

export function createRunwayDryRunRateLimiter(
  setIfAbsent: SetIfAbsent,
  hmacSecret: string
): (authenticatedEmail: string) => Promise<RunwayDryRunRateLimitResult> {
  return async (authenticatedEmail: string) => {
    const normalizedEmail = authenticatedEmail.trim().toLowerCase();
    if (!normalizedEmail || !hmacSecret) {
      return 'unavailable';
    }

    const identityDigest = createHmac('sha256', hmacSecret).update(normalizedEmail).digest('hex');
    const key = `${REDIS_KEY_PREFIX}:${identityDigest}`;

    try {
      return (await setIfAbsent(key, RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS)) ? 'allowed' : 'limited';
    } catch {
      return 'unavailable';
    }
  };
}

export async function consumeRunwayDryRunRateLimit(authenticatedEmail: string): Promise<RunwayDryRunRateLimitResult> {
  const hmacSecret = process.env.NEXTAUTH_SECRET;
  const queue = getRateLimitQueue();
  if (!hmacSecret || !queue) {
    return 'unavailable';
  }

  const setIfAbsent: SetIfAbsent = async (key, ttlSeconds) => {
    try {
      const client = await withTimeout(queue.client, REDIS_OPERATION_TIMEOUT_MS);
      client.defineCommand(RATE_LIMIT_SET_NX_COMMAND, {
        numberOfKeys: 1,
        lua: RATE_LIMIT_SET_NX_SCRIPT,
      });
      const result: unknown = await withTimeout(
        client.runCommand(RATE_LIMIT_SET_NX_COMMAND, [key, '1', String(ttlSeconds)]),
        REDIS_OPERATION_TIMEOUT_MS
      );
      return result === 1 || result === '1';
    } catch (error) {
      // BullMQ caches its first connection attempt and this retryStrategy gives
      // up after one retry, so a failed client never recovers. Drop it so the
      // next request reconnects; this request still fails closed.
      if (rateLimitQueue === queue) {
        rateLimitQueue = undefined;
      }
      void queue.close().catch(() => undefined);
      throw error;
    }
  };

  return createRunwayDryRunRateLimiter(setIfAbsent, hmacSecret)(authenticatedEmail);
}
