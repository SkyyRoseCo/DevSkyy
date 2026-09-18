/**
 * Admin Catalog API — single-SKU UPDATE.
 *
 * PUT /api/catalog/:sku  — patch editable commerce fields on one SKU and write
 * them THROUGH the product registry (`lib/catalog-write.ts` spawns the Python
 * writer, which regenerates the CSV/dossier projections). Validated with Zod
 * (strict: unknown keys rejected). Image columns are intentionally NOT accepted
 * here — they are SOT-governed.
 *
 * Fails closed: on a runtime where the registry or Python is unreachable
 * (serverless / read-only FS) the write answers 503 — there is no CSV fallback.
 */
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

import { withAuth } from '@/lib/api-auth';
import { getProduct } from '@/lib/catalog';
import { CatalogWriteError, updateProductRow } from '@/lib/catalog-write';
import { collapseNewlines, type CatalogPatch } from '@/lib/catalog-csv';

const patchSchema = z
  .object({
    name: z.string().trim().min(1).max(200).optional(),
    price: z.number().nonnegative().finite().optional(),
    badge: z.string().trim().max(120).optional(),
    sizes: z.array(z.string().trim().min(1)).max(20).optional(),
    color: z.string().trim().max(80).optional(),
    editionSize: z.number().int().nonnegative().optional(),
    published: z.boolean().optional(),
    isPreorder: z.boolean().optional(),
    description: z.string().trim().max(2000).optional(),
  })
  .strict();

type PatchInput = z.infer<typeof patchSchema>;

/** Convert the typed, validated input into raw catalog field strings. */
function toCsvPatch(input: PatchInput): CatalogPatch {
  // The editable catalog fields are single-line values: collapse any CR/LF a
  // pasted value carries before it reaches the registry writer.
  const patch: CatalogPatch = {};
  if (input.name !== undefined) patch.name = collapseNewlines(input.name);
  if (input.price !== undefined) patch.price = String(input.price);
  if (input.badge !== undefined) patch.badge = collapseNewlines(input.badge);
  if (input.sizes !== undefined) patch.sizes = input.sizes.map(collapseNewlines).join('|');
  if (input.color !== undefined) patch.color = collapseNewlines(input.color);
  if (input.editionSize !== undefined) patch.edition_size = String(input.editionSize);
  if (input.published !== undefined) patch.published = input.published ? '1' : '0';
  if (input.isPreorder !== undefined) patch.is_preorder = input.isPreorder ? '1' : '0';
  if (input.description !== undefined) patch.description = collapseNewlines(input.description);
  return patch;
}

async function putHandler(
  request: NextRequest,
  { params }: { params: Promise<{ sku: string }> }
) {
  const { sku } = await params;

  if (!getProduct(sku)) {
    return NextResponse.json({ success: false, error: 'Product not found' }, { status: 404 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ success: false, error: 'Invalid JSON body' }, { status: 400 });
  }

  const parsed = patchSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { success: false, error: 'Validation failed', issues: parsed.error.issues },
      { status: 400 }
    );
  }

  const patch = toCsvPatch(parsed.data);
  if (Object.keys(patch).length === 0) {
    return NextResponse.json(
      { success: false, error: 'No editable fields supplied' },
      { status: 400 }
    );
  }

  try {
    const { product, changed } = await updateProductRow(sku, patch);
    return NextResponse.json({ success: true, data: { product, changed } });
  } catch (error) {
    if (error instanceof CatalogWriteError) {
      if (error.kind === 'unavailable') {
        console.error('[api/catalog PUT] registry writer unavailable:', error.message);
        return NextResponse.json(
          {
            success: false,
            error:
              'Catalog is read-only in this runtime. Registry writes require a filesystem-backed deployment with Python (local / self-hosted), not serverless.',
          },
          { status: 503 }
        );
      }
      // SKU could be deleted between the existence check and the write (rare race).
      if (error.kind === 'not_found') {
        return NextResponse.json({ success: false, error: 'Product not found' }, { status: 404 });
      }
      // The registry writer refused the patch — Zod + collapseNewlines already
      // guard the input, so this names a validation gap; surface the reason.
      return NextResponse.json(
        { success: false, error: `Registry rejected the update: ${error.message}` },
        { status: 400 }
      );
    }
    console.error('[api/catalog PUT] write error:', error);
    return NextResponse.json({ success: false, error: 'Catalog write failed' }, { status: 500 });
  }
}

export const PUT = withAuth(putHandler);
