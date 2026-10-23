/** Routes used by the dashboard clients. This is intentionally not an API-wide relay. */
const ROUTES: ReadonlyArray<readonly [RegExp, readonly string[]]> = [
  [/^\/(health|ready)$/, ['GET']],
  [/^\/api\/v2\/usage$/, ['GET']],
  [/^\/api\/v1\/agents$/, ['GET']],
  [/^\/api\/v1\/orchestration\/god-mode\/providers$/, ['GET']],
  [/^\/api\/v1\/orchestration\/god-mode\/runs$/, ['POST']],
  [/^\/api\/v1\/orchestration\/god-mode\/runs\/[0-9a-f-]{36}$/, ['GET']],
  [/^\/api\/v1\/orchestration\/god-mode\/runs\/[0-9a-f-]{36}\/cancel$/, ['POST']],
  [/^\/api\/v1\/monitoring\/(health|metrics)$/, ['GET']],
  [/^\/api\/v1\/autonomous\/operations$/, ['GET']],
  [/^\/api\/v1\/autonomous\/operations\/[^/]+\/history$/, ['GET']],
  [/^\/api\/v1\/autonomous\/operations\/[^/]+\/(start|stop)$/, ['POST']],
  [/^\/api\/v1\/batch$/, ['GET']],
  [/^\/api\/v1\/batch\/generate$/, ['POST']],
  [/^\/api\/v1\/batch\/[^/]+$/, ['GET']],
  [/^\/api\/v1\/batch\/[^/]+\/(pause|resume|cancel)$/, ['POST']],
  [/^\/api\/v1\/commerce\/pricing\/optimize$/, ['POST']],
  [/^\/api\/v1\/social-media\/queue$/, ['GET']],
  [/^\/api\/v1\/social-media\/(generate|schedule|campaign|publish)$/, ['POST']],
  [/^\/api\/v1\/assets$/, ['GET']],
  [/^\/api\/v1\/assets\/(upload|ingest)$/, ['POST']],
  [/^\/api\/v1\/assets\/(stats\/collections|per-sku|datasets|jobs\/[^/]+)$/, ['GET']],
  [/^\/api\/v1\/assets\/[^/]+$/, ['GET', 'PATCH', 'DELETE']],
  [/^\/api\/v1\/tasks$/, ['GET', 'POST']],
  [/^\/api\/v1\/tasks\/[^/]+$/, ['GET']],
  [/^\/api\/v1\/tasks\/[^/]+\/cancel$/, ['POST']],
  [/^\/api\/v1\/round-table(\/(providers|stats))?$/, ['GET']],
  [/^\/api\/v1\/round-table\/compete$/, ['POST']],
  [/^\/api\/v1\/qa\/reviews$/, ['GET']],
  [/^\/api\/v1\/qa\/reviews\/[^/]+$/, ['GET', 'PATCH']],
  [/^\/api\/v1\/qa\/reviews\/[^/]+\/regenerate$/, ['POST']],
  [/^\/api\/v1\/training\/(status|jobs|jobs\/[^/]+)$/, ['GET']],
  [/^\/api\/v1\/catalog\/(search|products\/[^/]+\/similar|collections\/[^/]+\/featured)$/, ['GET']],
  [/^\/api\/v1\/competitors$/, ['GET', 'POST']],
  [/^\/api\/v1\/competitors\/(assets|analytics\/(style-distribution|summary))$/, ['GET']],
  [/^\/api\/v1\/competitors\/[^/]+$/, ['DELETE']],
  [/^\/api\/v1\/brand-assets\/ingest\/bulk$/, ['POST']],
  [/^\/api\/v1\/brand-assets\/(training-readiness|assets|ingest\/[^/]+)$/, ['GET']],
  [/^\/api\/v1\/brand-assets\/assets\/[^/]+\/(approve|reject)$/, ['PATCH']],
  [/^\/api\/v1\/context-dev\/extractions$/, ['POST']],
  [/^\/api\/v1\/elite-studio\/operations$/, ['GET', 'POST']],
  [/^\/api\/v1\/elite-studio\/operations\/[^/]+$/, ['GET']],
  [/^\/api\/v1\/elite-studio\/operations\/[^/]+\/cancel$/, ['POST']],
  [/^\/api\/v1\/elite-studio\/(health|characters|characters\/[^/]+)$/, ['GET']],
];

/** Validate before URL construction, which would silently normalize traversal. */
export function buildBackendUrl(pathname: string, search: string, method: string): URL | null {
  if (!pathname.startsWith('/') || pathname.startsWith('//')) return null;
  const segments = pathname.slice(1).split('/');
  try {
    for (const raw of segments) {
      const segment = decodeURIComponent(raw);
      if (
        !segment ||
        segment === '.' ||
        segment === '..' ||
        /[\\/%?#]/.test(segment) ||
        hasControlCharacter(segment, true)
      )
        return null;
    }
  } catch {
    return null;
  }
  // First match wins so fixed operation names cannot fall through as dynamic IDs.
  const route = ROUTES.find(([pattern]) => pattern.test(pathname));
  if (!route || !route[1].includes(method)) return null;
  if (search && (!search.startsWith('?') || hasControlCharacter(search) || search.includes('#'))) return null;
  const origin = getBackendOrigin();
  if (!origin) return null;
  const url = new URL(pathname, origin);
  url.search = search;
  return url;
}

/** Server configuration fails closed rather than sending credentials to a fallback. */
export function getBackendOrigin(): string | null {
  const configured = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL;
  const value = configured || (process.env.NODE_ENV !== 'production' ? 'http://localhost:8000' : '');
  try {
    const url = new URL(value);
    if (url.username || url.password || url.pathname !== '/' || url.search || url.hash) return null;
    const localHttp =
      process.env.NODE_ENV !== 'production' &&
      url.protocol === 'http:' &&
      ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
    if (url.protocol !== 'https:' && !localHttp) return null;
    return url.origin;
  } catch {
    return null;
  }
}

function hasControlCharacter(value: string, includeSpace = false): boolean {
  return [...value].some(
    character => character.charCodeAt(0) <= (includeSpace ? 32 : 31) || character.charCodeAt(0) === 127
  );
}
