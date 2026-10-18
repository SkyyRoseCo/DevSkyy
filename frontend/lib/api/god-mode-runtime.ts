/** Browser transport for authenticated GOD MODE workflows. No credentials or authority in bodies. */
export class GodModeRuntimeError extends Error {
  constructor(message: string, public readonly status: number) { super(message); }
}

export async function godModeRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const route = path.startsWith('/') ? path : `/${path}`;
  if (!/^\/(?:status|workflows|runs|memory)(?:[/?]|$)/.test(route) || route.includes('..')) {
    throw new GodModeRuntimeError('Unsupported GOD MODE route.', 400);
  }
  const response = await fetch(`/api/admin/god-mode/runtime${route}`, {
    ...init, credentials: 'same-origin', cache: 'no-store',
    headers: { 'Content-Type': 'application/json', ...init.headers },
  });
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data && typeof data === 'object' && 'error' in data && typeof data.error === 'string'
      ? data.error : data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string'
        ? data.detail : `Runtime request failed (${response.status}).`;
    throw new GodModeRuntimeError(message, response.status);
  }
  return data as T;
}
