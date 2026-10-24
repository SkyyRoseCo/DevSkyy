import { z } from 'zod';
import { ApiError } from './errors';
import { API_URL } from './config';

const REQUEST_TIMEOUT = 30000; // 30 seconds

export function getAuthToken(): string | null {
  // Credentials live exclusively in the encrypted HttpOnly session cookie.
  return null;
}

export async function getAuthHeaders(): Promise<HeadersInit> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Request-ID': crypto.randomUUID(),
  };
  return headers;
}

/** Only rewrite the configured backend origin in browser code. */
export function toDashboardApiUrl(url: string): string {
  if (typeof window === 'undefined') return url;
  try {
    const target = new URL(url);
    const backend = new URL(API_URL);
    if (target.origin === backend.origin && !target.username && !target.password) {
      return `/api/platform${target.pathname}${target.search}`;
    }
  } catch {
    /* Relative dashboard URLs already use the same-origin cookie. */
  }
  return url;
}

export async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout = REQUEST_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  const abort = () => controller.abort(options.signal?.reason);
  if (options.signal?.aborted) abort();
  else options.signal?.addEventListener('abort', abort, { once: true });

  try {
    const response = await fetch(toDashboardApiUrl(url), {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
    options.signal?.removeEventListener('abort', abort);
  }
}

export async function handleResponse<T>(response: Response, schema: z.ZodType<T>): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw ApiError.fromResponse(response.status, body);
  }

  const data = await response.json();

  // Validate response against schema
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error('API response validation failed:', result.error.issues);
    throw new ApiError('Invalid API response format', 500, 'VALIDATION_ERROR', result.error.issues);
  }

  return result.data;
}

export async function handleArrayResponse<T>(response: Response, schema: z.ZodType<T>): Promise<T[]> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw ApiError.fromResponse(response.status, body);
  }

  const data = await response.json();

  if (!Array.isArray(data)) {
    throw new ApiError('Expected array response', 500, 'INVALID_FORMAT');
  }

  // Validate each item
  const results: T[] = [];
  for (const item of data) {
    const result = schema.safeParse(item);
    if (result.success) {
      results.push(result.data);
    } else {
      console.warn('Skipping invalid item:', result.error.issues);
    }
  }

  return results;
}
