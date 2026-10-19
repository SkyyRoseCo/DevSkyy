'use strict';

/** Conservative normalized successor contract; not the missing legacy collector. */
function classifyRow(row) {
  const unknown = { disposition: 'UNKNOWN', cookie_presence: 'UNKNOWN', cookie_count: null };
  if (!row || row.schema !== 'skyyrose.network-row.v1' || row.capture_complete !== true || row.truncated !== false || row.redirects_complete !== true || row.request_count !== 1 || row.finished_count !== 1 || row.failed_count !== 0 || row.response_count !== 1 || row.request_extra_count !== 1 || row.response_extra_count !== 1 || row.has_response_extra !== true || row.from_disk_cache !== false || row.from_prefetch_cache !== false || row.from_service_worker !== false || row.router_present !== false || !row.request_headers || typeof row.request_headers !== 'object' || Array.isArray(row.request_headers)) return unknown;
  const keys = Object.keys(row.request_headers).filter(key => key.toLowerCase() === 'cookie');
  if (keys.length > 1 || keys.some(key => typeof row.request_headers[key] !== 'string')) return unknown;
  const cookie = keys.length ? row.request_headers[keys[0]] : '';
  if (keys.length && !cookie.trim()) return unknown;
  const parts = cookie ? cookie.split(';').map(value => value.trim()) : [];
  if (parts.some(value => !/^[!#$%&'*+.^_`|~0-9A-Za-z-]+=/.test(value))) return unknown;
  return { disposition: 'CAPTURED_REQUEST_HEADERS', cookie_presence: cookie ? 'PRESENT' : 'ABSENT', cookie_count: parts.length };
}

/** Persist only explicit structural fields; no raw headers, values or log text. */
function evidenceProjection(rows, errorCount) {
  if (!Array.isArray(rows) || !Number.isSafeInteger(errorCount) || errorCount < 0) throw new TypeError('Explicit evidence rows and error count required');
  return { schema: 'skyyrose.redacted-network-evidence.v1', raw_headers_retained: false, raw_log_text_retained: false, screenshot_resources_retained: false, error_count: errorCount, rows: rows.map(row => classifyRow(row)) };
}
module.exports = { classifyRow, evidenceProjection };
