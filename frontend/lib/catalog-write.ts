/**
 * Canonical catalog WRITE path (server-only).
 *
 * Writes go THROUGH the single product registry
 * (`wordpress-theme/skyyrose-flagship/data/logo-registry.json`), never to the
 * CSV. This module spawns the one writer implementation —
 * `python -m skyyrose.core.product_registry update <sku> --registry <path>` —
 * which calls `update_catalog_fields`: the registry changes and the CSV +
 * dossier projections regenerate from it in the same locked transaction. There
 * is deliberately no TypeScript re-implementation of the projection logic.
 *
 * Boundaries (surfaced in the UI, not hidden):
 *  - A save updates the registry + its projections only. It does NOT reach
 *    skyyrose.co — that requires the downstream sync + a WordPress deploy.
 *  - Image columns are NOT writable here: image bindings belong to the
 *    renders/review queue, not this editor.
 *  - Fail closed. If the monorepo or Python is unreachable (serverless /
 *    read-only runtime such as Vercel, where `frontend/` is the root and the
 *    registry is not in scope), `CatalogWriteError` with `kind: 'unavailable'`
 *    is thrown and the route answers 503. There is no CSV fallback.
 *
 * Python executable: `DEVSKYY_PYTHON` env var, default `python3`. The writer
 * needs only the standard library plus the `skyyrose` package, which is put on
 * `PYTHONPATH` by running with the monorepo root as cwd.
 */
import 'server-only';

import { execFile, type ExecFileOptions } from 'node:child_process';
import path from 'node:path';

import { resolveRepoFile, resetCatalogCache, getProduct, type CatalogProduct } from './catalog';
import { EDITABLE_COLUMNS, type CatalogPatch } from './catalog-csv';

/** Same shape as `lib/api/endpoints/catalog.ts` SKU_RE: lowercase alphanum + hyphens. */
const SKU_RE = /^[a-z0-9][a-z0-9-]{1,31}$/;
const REGISTRY_RELATIVE = path.join('wordpress-theme', 'skyyrose-flagship', 'data', 'logo-registry.json');
const WRITER_MODULE = 'skyyrose.core.product_registry';
const WRITE_TIMEOUT_MS = 30_000;
const EDITABLE_SET: ReadonlySet<string> = new Set(EDITABLE_COLUMNS);

export interface UpdateResult {
  product: CatalogProduct;
  changed: boolean;
}

export type CatalogWriteErrorKind =
  /** Registry or Python not reachable from this runtime (read-only / serverless). */
  | 'unavailable'
  /** The registry writer refused the patch (unknown field, unsafe value, ...). */
  | 'rejected'
  /** The SKU is not in the registry. */
  | 'not_found';

export class CatalogWriteError extends Error {
  constructor(
    public readonly kind: CatalogWriteErrorKind,
    message: string
  ) {
    super(message);
    this.name = 'CatalogWriteError';
  }
}

interface WriterResult {
  ok: boolean;
  error?: string;
  changed?: string[];
}

interface WriterFailure extends NodeJS.ErrnoException {
  stdout?: string;
  killed?: boolean;
}

/** Spawn the writer with `input` on stdin; reject with stdout attached on failure. */
function runWriter(
  python: string,
  args: string[],
  options: ExecFileOptions,
  input: string
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = execFile(python, args, { ...options, encoding: 'utf8' }, (error, stdout) => {
      if (error) {
        reject(Object.assign(error as WriterFailure, { stdout: String(stdout ?? '') }));
        return;
      }
      resolve(String(stdout));
    });
    child.stdin?.end(input);
  });
}

function parseWriterOutput(stdout: string): WriterResult {
  try {
    const parsed = JSON.parse(stdout) as unknown;
    if (parsed && typeof parsed === 'object' && 'ok' in parsed) return parsed as WriterResult;
  } catch {
    // fall through — the writer did not print its JSON contract
  }
  throw new CatalogWriteError('unavailable', `Registry writer returned no JSON result: ${stdout.trim().slice(0, 200)}`);
}

/** Resolve the registry + monorepo root, or fail closed if not in scope. */
function locateRegistry(): { registryPath: string; repoRoot: string } {
  try {
    const registryPath = resolveRepoFile(REGISTRY_RELATIVE);
    const repoRoot = registryPath.slice(0, -REGISTRY_RELATIVE.length - 1);
    return { registryPath, repoRoot };
  } catch (error) {
    throw new CatalogWriteError(
      'unavailable',
      `Product registry not reachable from this runtime: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

/**
 * Apply `patch` (raw catalog cell strings, editable columns only) to one SKU
 * through the registry writer. Returns the re-read product (from the freshly
 * regenerated CSV projection) and whether any field actually changed.
 */
export async function updateProductRow(sku: string, patch: CatalogPatch): Promise<UpdateResult> {
  if (!SKU_RE.test(sku)) {
    throw new CatalogWriteError('rejected', `Invalid SKU: ${sku}`);
  }
  const changes: Record<string, string> = {};
  for (const [key, value] of Object.entries(patch)) {
    if (!EDITABLE_SET.has(key)) {
      throw new CatalogWriteError('rejected', `Column not editable: ${key}`);
    }
    if (typeof value !== 'string') {
      throw new CatalogWriteError('rejected', `Patch value for "${key}" must be a string`);
    }
    changes[key] = value;
  }
  if (Object.keys(changes).length === 0) {
    throw new CatalogWriteError('rejected', 'No editable fields supplied');
  }

  const { registryPath, repoRoot } = locateRegistry();
  const python = process.env.DEVSKYY_PYTHON || 'python3';
  const args = ['-m', WRITER_MODULE, 'update', sku, '--registry', registryPath];

  let stdout: string;
  try {
    stdout = await runWriter(
      python,
      args,
      {
        cwd: repoRoot,
        env: { ...process.env, PYTHONPATH: repoRoot },
        timeout: WRITE_TIMEOUT_MS,
        maxBuffer: 1024 * 1024,
        windowsHide: true,
      },
      JSON.stringify(changes)
    );
  } catch (error) {
    const err = error as WriterFailure;
    if (typeof err.stdout === 'string' && err.stdout.trim().startsWith('{')) {
      // Non-zero exit with the writer's JSON verdict on stdout.
      const verdict = parseWriterOutput(err.stdout);
      const message = verdict.error ?? 'Registry writer rejected the patch';
      throw new CatalogWriteError(message.startsWith('SKU not found') ? 'not_found' : 'rejected', message);
    }
    if (err.code === 'ENOENT' || err.code === 'EROFS' || err.code === 'EACCES') {
      throw new CatalogWriteError(
        'unavailable',
        `Registry writer (${python}) not runnable in this runtime: ${err.code}`
      );
    }
    if (err.killed) {
      throw new CatalogWriteError('unavailable', `Registry writer timed out after ${WRITE_TIMEOUT_MS}ms`);
    }
    throw new CatalogWriteError('unavailable', `Registry writer failed: ${err.message ?? String(error)}`);
  }

  const verdict = parseWriterOutput(stdout);
  if (!verdict.ok) {
    throw new CatalogWriteError('rejected', verdict.error ?? 'Registry writer rejected the patch');
  }

  resetCatalogCache();
  const product = getProduct(sku);
  if (!product) {
    throw new CatalogWriteError('not_found', `SKU not found after write: ${sku}`);
  }
  return { product, changed: (verdict.changed ?? []).length > 0 };
}
