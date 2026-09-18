/**
 * PUT /api/catalog/:sku answers with the route's error conventions when the
 * registry writer is unavailable (503, fail closed), rejects (400), or
 * succeeds (200) — and never falls back to writing the CSV.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

const { getServerSessionMock, updateProductRowMock, getProductMock } = vi.hoisted(() => ({
  getServerSessionMock: vi.fn(),
  updateProductRowMock: vi.fn(),
  getProductMock: vi.fn(),
}));

vi.mock('next-auth', () => ({ getServerSession: getServerSessionMock }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('server-only', () => ({}));
vi.mock('@/lib/catalog', () => ({ getProduct: getProductMock }));
vi.mock('@/lib/catalog-write', async importOriginal => {
  const actual = await importOriginal<typeof import('@/lib/catalog-write')>();
  return { CatalogWriteError: actual.CatalogWriteError, updateProductRow: updateProductRowMock };
});

import { CatalogWriteError } from '@/lib/catalog-write';
import { PUT } from '@/app/api/catalog/[sku]/route';

const PRODUCT = { sku: 'br-001', name: 'Renamed' };

function put(sku: string, body: unknown) {
  return PUT(
    new NextRequest(`http://localhost/api/catalog/${sku}`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    }),
    { params: Promise.resolve({ sku }) }
  );
}

describe('PUT /api/catalog/[sku]', () => {
  beforeEach(() => {
    getServerSessionMock.mockReset().mockResolvedValue({ user: { email: 'operator@example.test' } });
    updateProductRowMock.mockReset();
    getProductMock.mockReset().mockReturnValue(PRODUCT);
  });

  it('writes through the registry and returns the re-read product', async () => {
    updateProductRowMock.mockResolvedValue({ product: PRODUCT, changed: true });

    const response = await put('br-001', { name: 'Renamed', price: 120, sizes: ['S', 'M'] });

    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toEqual({
      success: true,
      data: { product: PRODUCT, changed: true },
    });
    expect(updateProductRowMock).toHaveBeenCalledWith('br-001', {
      name: 'Renamed',
      price: '120',
      sizes: 'S|M',
    });
  });

  it('answers 503 and does not fall back when the registry writer is unavailable', async () => {
    updateProductRowMock.mockRejectedValue(
      new CatalogWriteError('unavailable', 'Product registry not reachable from this runtime')
    );
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const response = await put('br-001', { name: 'Renamed' });
    const body = await response.json();

    expect(response.status).toBe(503);
    expect(body.success).toBe(false);
    expect(body.error).toMatch(/read-only in this runtime/);
    expect(updateProductRowMock).toHaveBeenCalledTimes(1);
    consoleSpy.mockRestore();
  });

  it('answers 400 with the reason when the registry rejects the patch', async () => {
    updateProductRowMock.mockRejectedValue(
      new CatalogWriteError('rejected', 'Unknown or identity-changing catalog fields')
    );

    const response = await put('br-001', { name: 'Renamed' });

    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      success: false,
      error: 'Registry rejected the update: Unknown or identity-changing catalog fields',
    });
  });

  it('answers 404 when the writer reports the SKU vanished', async () => {
    updateProductRowMock.mockRejectedValue(new CatalogWriteError('not_found', 'SKU not found: br-001'));

    const response = await put('br-001', { name: 'Renamed' });

    expect(response.status).toBe(404);
    await expect(response.json()).resolves.toEqual({ success: false, error: 'Product not found' });
  });

  it('fails closed without a session', async () => {
    getServerSessionMock.mockResolvedValue(null);

    const response = await put('br-001', { name: 'Renamed' });

    expect(response.status).toBe(401);
    expect(updateProductRowMock).not.toHaveBeenCalled();
  });
});
