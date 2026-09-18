/**
 * `lib/catalog-write.ts` writes THROUGH the product registry by spawning the
 * Python writer, and never touches the CSV projection itself.
 *
 * child_process is mocked at the boundary (unit test). The Python side of the
 * contract is covered by tests/test_product_registry_cli.py at the repo root.
 */
import fs from 'node:fs';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const { execFileMock, getProductMock, resetCatalogCacheMock, resolveRepoFileMock } = vi.hoisted(() => ({
  execFileMock: vi.fn(),
  getProductMock: vi.fn(),
  resetCatalogCacheMock: vi.fn(),
  resolveRepoFileMock: vi.fn(),
}));

vi.mock('server-only', () => ({}));
vi.mock('node:child_process', () => ({ execFile: execFileMock }));
vi.mock('@/lib/catalog', () => ({
  resolveRepoFile: resolveRepoFileMock,
  resetCatalogCache: resetCatalogCacheMock,
  getProduct: getProductMock,
}));

import { CatalogWriteError, updateProductRow } from '@/lib/catalog-write';

const REPO = '/srv/devskyy';
const REGISTRY = `${REPO}/wordpress-theme/skyyrose-flagship/data/logo-registry.json`;
const PRODUCT = { sku: 'br-001', name: 'Renamed' };

type ExecCb = (error: (Error & { code?: string; killed?: boolean }) | null, stdout: string, stderr: string) => void;

interface Spawned {
  file: string;
  args: string[];
  options: { cwd?: string; env?: Record<string, string>; timeout?: number };
  stdin: string;
}

/** Program the child_process boundary: capture the spawn, reply with `stdout` (+ optional error). */
function arm(stdout: string, error: (Error & { code?: string; killed?: boolean }) | null = null): Spawned {
  const spawned: Spawned = { file: '', args: [], options: {}, stdin: '' };
  execFileMock.mockImplementation((file: string, args: string[], options: Spawned['options'], cb: ExecCb) => {
    spawned.file = file;
    spawned.args = args;
    spawned.options = options;
    queueMicrotask(() => cb(error, stdout, ''));
    return {
      stdin: {
        end: (input: string) => {
          spawned.stdin = input;
        },
      },
    };
  });
  return spawned;
}

describe('updateProductRow — registry writer boundary', () => {
  let writeFileSpy: ReturnType<typeof vi.spyOn>;
  let renameSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    execFileMock.mockReset();
    getProductMock.mockReset();
    resetCatalogCacheMock.mockReset();
    resolveRepoFileMock.mockReset();
    resolveRepoFileMock.mockReturnValue(REGISTRY);
    getProductMock.mockReturnValue(PRODUCT);
    writeFileSpy = vi.spyOn(fs, 'writeFileSync');
    renameSpy = vi.spyOn(fs, 'renameSync');
    delete process.env.DEVSKYY_PYTHON;
  });

  afterEach(() => {
    writeFileSpy.mockRestore();
    renameSpy.mockRestore();
    delete process.env.DEVSKYY_PYTHON;
  });

  it('spawns the Python writer with an args array, the patch on stdin, and no CSV write', async () => {
    const spawned = arm(JSON.stringify({ ok: true, sku: 'br-001', changed: ['name'], registry: REGISTRY }));

    const result = await updateProductRow('br-001', { name: 'Renamed', price: '120' });

    expect(spawned.file).toBe('python3');
    expect(spawned.args).toEqual(['-m', 'skyyrose.core.product_registry', 'update', 'br-001', '--registry', REGISTRY]);
    expect(spawned.options.cwd).toBe(REPO);
    expect(spawned.options.env?.PYTHONPATH).toBe(REPO);
    expect(spawned.options.timeout).toBeGreaterThan(0);
    expect(JSON.parse(spawned.stdin)).toEqual({ name: 'Renamed', price: '120' });
    expect(result).toEqual({ product: PRODUCT, changed: true });
    expect(resetCatalogCacheMock).toHaveBeenCalledTimes(1);
    expect(getProductMock).toHaveBeenCalledWith('br-001');
    expect(writeFileSpy).not.toHaveBeenCalled();
    expect(renameSpy).not.toHaveBeenCalled();
  });

  it('honors DEVSKYY_PYTHON for the interpreter', async () => {
    process.env.DEVSKYY_PYTHON = '/opt/venv/bin/python';
    const spawned = arm(JSON.stringify({ ok: true, changed: [] }));

    const result = await updateProductRow('br-001', { badge: 'Drop 2' });

    expect(spawned.file).toBe('/opt/venv/bin/python');
    expect(result.changed).toBe(false);
  });

  it('rejects an invalid SKU before spawning anything', async () => {
    await expect(updateProductRow('BR 001; rm -rf /', { name: 'x' })).rejects.toMatchObject({
      name: 'CatalogWriteError',
      kind: 'rejected',
    });
    expect(execFileMock).not.toHaveBeenCalled();
  });

  it('rejects a non-editable column before spawning anything', async () => {
    const patch = { image: 'assets/x.webp' } as unknown as Parameters<typeof updateProductRow>[1];
    await expect(updateProductRow('br-001', patch)).rejects.toMatchObject({
      kind: 'rejected',
      message: 'Column not editable: image',
    });
    expect(execFileMock).not.toHaveBeenCalled();
  });

  it('fails closed when the registry is not in scope (serverless / Vercel)', async () => {
    resolveRepoFileMock.mockImplementation(() => {
      throw new Error('Repo file not found: wordpress-theme/... (searched up from /var/task)');
    });

    await expect(updateProductRow('br-001', { name: 'x' })).rejects.toMatchObject({
      kind: 'unavailable',
    });
    expect(execFileMock).not.toHaveBeenCalled();
    expect(writeFileSpy).not.toHaveBeenCalled();
    expect(renameSpy).not.toHaveBeenCalled();
  });

  it('fails closed when the Python interpreter is missing (ENOENT)', async () => {
    arm('', Object.assign(new Error('spawn python3 ENOENT'), { code: 'ENOENT' }));

    const error = await updateProductRow('br-001', { name: 'x' }).catch((e: unknown) => e);

    expect(error).toBeInstanceOf(CatalogWriteError);
    expect((error as CatalogWriteError).kind).toBe('unavailable');
    expect(resetCatalogCacheMock).not.toHaveBeenCalled();
    expect(writeFileSpy).not.toHaveBeenCalled();
  });

  it('surfaces the writer JSON verdict on a non-zero exit', async () => {
    arm(
      JSON.stringify({ ok: false, error: 'Unknown or identity-changing catalog fields' }),
      Object.assign(new Error('Command failed'), { code: 1 as unknown as string })
    );

    await expect(updateProductRow('br-001', { name: 'x' })).rejects.toMatchObject({
      kind: 'rejected',
      message: 'Unknown or identity-changing catalog fields',
    });
    expect(resetCatalogCacheMock).not.toHaveBeenCalled();
  });

  it('maps an unknown SKU from the writer to not_found', async () => {
    arm(
      JSON.stringify({ ok: false, error: 'SKU not found: zz-999' }),
      Object.assign(new Error('Command failed'), { code: 1 as unknown as string })
    );

    await expect(updateProductRow('zz-999', { name: 'x' })).rejects.toMatchObject({ kind: 'not_found' });
  });

  it('treats non-JSON writer output as unavailable, never as success', async () => {
    arm('Traceback (most recent call last): ...');

    await expect(updateProductRow('br-001', { name: 'x' })).rejects.toMatchObject({ kind: 'unavailable' });
    expect(resetCatalogCacheMock).not.toHaveBeenCalled();
  });
});
