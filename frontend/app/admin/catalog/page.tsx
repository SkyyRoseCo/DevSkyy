'use client';

/**
 * /admin/catalog — Product / SKU editor against the canonical catalog CSV.
 *
 * Agents (and the founder) edit per-SKU commerce fields here: copy, price,
 * badge, sizes, edition size, and the published / pre-order flags. Writes land
 * in `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` — the ONE
 * source of truth — via `PUT /api/catalog/:sku`.
 *
 * Deliberately NOT here:
 *  - Image assignment. Product imagery is governed by the generated SOT
 *    manifest (`data/sot-images.json`); this page DISPLAYS the SOT set read-only
 *    and leaves assignment to the renders/review queue (the SOT-promotion surface).
 *  - Live publishing. A save updates the upstream CSV only; reaching skyyrose.co
 *    needs catalog sync + a WordPress deploy.
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'motion/react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Save, RefreshCw, Check, AlertCircle, Search, Package, ImageOff, Info, Tag } from 'lucide-react';

interface SotImageSet {
  front?: string;
  back?: string;
  packshot?: string;
}

interface CatalogProduct {
  sku: string;
  name: string;
  price: number;
  collection: string;
  description: string;
  badge: string;
  image: string;
  frontModelImage: string;
  backImage: string;
  backModelImage: string;
  sizes: string[];
  color: string;
  editionSize: number;
  published: boolean;
  isPreorder: boolean;
  brandingSpec: string;
  sot: SotImageSet | null;
}

interface DraftFields {
  name: string;
  price: string;
  badge: string;
  sizes: string;
  color: string;
  editionSize: string;
  published: boolean;
  isPreorder: boolean;
  description: string;
}

type SaveStatus = 'idle' | 'saving' | 'success' | 'error';

const COLLECTION_LABELS: Record<string, string> = {
  'black-rose': 'Black Rose',
  'love-hurts': 'Love Hurts',
  signature: 'Signature',
  'kids-capsule': 'Kids Capsule',
};

function collectionLabel(slug: string): string {
  return COLLECTION_LABELS[slug] ?? slug;
}

function toDraft(p: CatalogProduct): DraftFields {
  return {
    name: p.name,
    price: String(p.price),
    badge: p.badge,
    sizes: p.sizes.join(', '),
    color: p.color,
    editionSize: String(p.editionSize),
    published: p.published,
    isPreorder: p.isPreorder,
    description: p.description,
  };
}

function parseSizes(raw: string): string[] {
  return raw
    .split(/[,|]/)
    .map(s => s.trim())
    .filter(Boolean);
}

/** Build a patch of only the fields that changed vs the on-disk product. */
function buildPatch(draft: DraftFields, p: CatalogProduct): Record<string, unknown> {
  const patch: Record<string, unknown> = {};

  if (draft.name.trim() !== p.name) patch.name = draft.name.trim();
  if (draft.badge.trim() !== p.badge) patch.badge = draft.badge.trim();
  if (draft.color.trim() !== p.color) patch.color = draft.color.trim();
  if (draft.description.trim() !== p.description) patch.description = draft.description.trim();
  if (draft.published !== p.published) patch.published = draft.published;
  if (draft.isPreorder !== p.isPreorder) patch.isPreorder = draft.isPreorder;

  const price = Number(draft.price);
  if (Number.isFinite(price) && price !== p.price) patch.price = price;

  const editionSize = Number.parseInt(draft.editionSize, 10);
  if (Number.isFinite(editionSize) && editionSize !== p.editionSize) {
    patch.editionSize = editionSize;
  }

  const sizes = parseSizes(draft.sizes);
  if (sizes.join('|') !== p.sizes.join('|')) patch.sizes = sizes;

  return patch;
}

export default function CatalogPage() {
  const [products, setProducts] = useState<CatalogProduct[]>([]);
  const [collections, setCollections] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  const [search, setSearch] = useState('');
  const [collectionFilter, setCollectionFilter] = useState('all');
  const [selectedSku, setSelectedSku] = useState<string | null>(null);

  const [draft, setDraft] = useState<DraftFields | null>(null);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [saveError, setSaveError] = useState('');

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setLoadError('');
    try {
      const res = await fetch('/api/catalog', { cache: 'no-store' });
      const json = await res.json();
      if (!res.ok || !json.success) {
        throw new Error(json.error || `Request failed (${res.status})`);
      }
      if (!json?.data || !Array.isArray(json.data.products)) {
        throw new Error('Unexpected response shape');
      }
      setProducts(json.data.products as CatalogProduct[]);
      setCollections((json.data.collections as string[]) ?? []);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load catalog');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const selected = useMemo(() => products.find(p => p.sku === selectedSku) ?? null, [products, selectedSku]);

  const selectProduct = useCallback((p: CatalogProduct) => {
    setSelectedSku(p.sku);
    setDraft(toDraft(p));
    setSaveStatus('idle');
    setSaveError('');
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return products.filter(p => {
      if (collectionFilter !== 'all' && p.collection !== collectionFilter) return false;
      if (!q) return true;
      return (
        p.sku.toLowerCase().includes(q) || p.name.toLowerCase().includes(q) || p.collection.toLowerCase().includes(q)
      );
    });
  }, [products, search, collectionFilter]);

  const dirty = useMemo(() => {
    if (!draft || !selected) return false;
    return Object.keys(buildPatch(draft, selected)).length > 0;
  }, [draft, selected]);

  const updateField = useCallback(<K extends keyof DraftFields>(key: K, value: DraftFields[K]) => {
    setDraft(prev => (prev ? { ...prev, [key]: value } : prev));
    setSaveStatus('idle');
  }, []);

  const save = useCallback(async () => {
    if (!draft || !selected) return;
    const patch = buildPatch(draft, selected);
    if (Object.keys(patch).length === 0) return;

    setSaveStatus('saving');
    setSaveError('');
    try {
      const res = await fetch(`/api/catalog/${selected.sku}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patch),
      });
      const json = await res.json();
      if (!res.ok || !json.success) {
        throw new Error(json.error || `Save failed (${res.status})`);
      }
      const updated = json.data.product as CatalogProduct;
      setProducts(prev => prev.map(p => (p.sku === updated.sku ? { ...updated, sot: p.sot } : p)));
      setDraft(toDraft({ ...updated, sot: selected.sot }));
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 2500);
    } catch (err) {
      setSaveStatus('error');
      setSaveError(err instanceof Error ? err.message : 'Save failed');
    }
  }, [draft, selected]);

  return (
    <div className='container mx-auto py-8 space-y-6'>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className='mb-6 flex items-center justify-between'>
          <div>
            <h1 className='font-display text-4xl luxury-text-gradient mb-2'>Catalog</h1>
            <p className='text-gray-400'>Edit the canonical product CSV — the one source of truth for every SKU.</p>
          </div>
          <Button onClick={loadCatalog} variant='outline' disabled={loading} className='border-gray-700 text-gray-300'>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Reload
          </Button>
        </div>

        <div className='mb-6 flex items-start gap-3 rounded-lg border border-rose-500/20 bg-rose-500/5 p-4'>
          <Info className='mt-0.5 h-5 w-5 shrink-0 text-rose-400' />
          <p className='text-sm text-gray-400'>
            Saves write the upstream catalog CSV only — they do <strong>not</strong> publish to skyyrose.co (that needs
            catalog sync + a WordPress deploy). Product imagery is SOT-governed and shown read-only here; image
            assignment lives in the renders / review queue. CSV writes require a filesystem-backed runtime (local /
            self-hosted).
          </p>
        </div>

        {loadError && (
          <div className='mb-6 flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4'>
            <AlertCircle className='h-5 w-5 text-red-400' />
            <p className='text-red-400'>{loadError}</p>
          </div>
        )}

        <div className='grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]'>
          {/* ── Product list ─────────────────────────────────────────── */}
          <Card className='bg-gray-900 border-gray-800'>
            <CardHeader className='pb-4'>
              <div className='flex items-center justify-between'>
                <CardTitle className='text-lg'>
                  Products
                  <span className='ml-2 text-sm font-normal text-gray-500'>
                    {filtered.length}/{products.length}
                  </span>
                </CardTitle>
              </div>
              <div className='space-y-3 pt-2'>
                <div className='relative'>
                  <Search className='absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500' />
                  <Input
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder='Search SKU, name, collection…'
                    className='bg-gray-800 border-gray-700 pl-9'
                  />
                </div>
                <select
                  value={collectionFilter}
                  onChange={e => setCollectionFilter(e.target.value)}
                  className='w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm'
                >
                  <option value='all'>All collections</option>
                  {collections.map(c => (
                    <option key={c} value={c}>
                      {collectionLabel(c)}
                    </option>
                  ))}
                </select>
              </div>
            </CardHeader>
            <CardContent className='max-h-[60vh] space-y-1 overflow-auto p-2'>
              {loading && <p className='p-4 text-sm text-gray-500'>Loading catalog…</p>}
              {!loading && filtered.length === 0 && <p className='p-4 text-sm text-gray-500'>No products match.</p>}
              {filtered.map(p => {
                const isActive = p.sku === selectedSku;
                return (
                  <button
                    key={p.sku}
                    type='button'
                    onClick={() => selectProduct(p)}
                    className={`flex w-full items-center justify-between gap-3 rounded-md px-3 py-2 text-left transition-colors ${
                      isActive ? 'bg-rose-500/10 text-rose-300' : 'text-gray-300 hover:bg-gray-800'
                    }`}
                  >
                    <div className='min-w-0'>
                      <p className='truncate text-sm font-medium'>{p.name}</p>
                      <p className='font-mono text-xs text-gray-500'>
                        {p.sku} · {collectionLabel(p.collection)}
                      </p>
                    </div>
                    <div className='flex shrink-0 items-center gap-2'>
                      <span className='text-sm text-gray-400'>${p.price}</span>
                      {!p.published && (
                        <Badge variant='outline' className='border-gray-700 text-gray-500'>
                          draft
                        </Badge>
                      )}
                      {p.isPreorder && <Badge className='bg-amber-500/20 text-amber-300'>pre-order</Badge>}
                    </div>
                  </button>
                );
              })}
            </CardContent>
          </Card>

          {/* ── Editor panel ─────────────────────────────────────────── */}
          {!selected || !draft ? (
            <Card className='flex items-center justify-center bg-gray-900 border-gray-800'>
              <div className='p-10 text-center text-gray-500'>
                <Package className='mx-auto mb-3 h-10 w-10 opacity-40' />
                <p>Select a product to edit.</p>
              </div>
            </Card>
          ) : (
            <Card className='bg-gray-900 border-gray-800'>
              <CardHeader>
                <div className='flex items-start justify-between gap-4'>
                  <div>
                    <CardTitle className='flex items-center gap-2 text-xl'>
                      <Tag className='h-4 w-4 text-rose-400' />
                      {selected.name}
                    </CardTitle>
                    <CardDescription className='font-mono'>
                      {selected.sku} · {collectionLabel(selected.collection)}
                    </CardDescription>
                  </div>
                  <Button
                    onClick={save}
                    disabled={!dirty || saveStatus === 'saving'}
                    className='bg-rose-500 hover:bg-rose-600 disabled:opacity-40'
                  >
                    {saveStatus === 'saving' ? (
                      <>
                        <RefreshCw className='mr-2 h-4 w-4 animate-spin' />
                        Saving…
                      </>
                    ) : saveStatus === 'success' ? (
                      <>
                        <Check className='mr-2 h-4 w-4' />
                        Saved
                      </>
                    ) : (
                      <>
                        <Save className='mr-2 h-4 w-4' />
                        Save
                      </>
                    )}
                  </Button>
                </div>
                {saveStatus === 'error' && (
                  <div className='mt-3 flex items-center gap-2 rounded-md border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400'>
                    <AlertCircle className='h-4 w-4 shrink-0' />
                    {saveError}
                  </div>
                )}
              </CardHeader>

              <CardContent className='space-y-5'>
                <div className='grid grid-cols-1 gap-4 sm:grid-cols-2'>
                  <div className='space-y-2 sm:col-span-2'>
                    <Label htmlFor='f-name'>Name</Label>
                    <Input
                      id='f-name'
                      value={draft.name}
                      onChange={e => updateField('name', e.target.value)}
                      className='bg-gray-800 border-gray-700'
                    />
                  </div>

                  <div className='space-y-2'>
                    <Label htmlFor='f-price'>Price (USD)</Label>
                    <Input
                      id='f-price'
                      type='number'
                      min={0}
                      step='1'
                      value={draft.price}
                      onChange={e => updateField('price', e.target.value)}
                      className='bg-gray-800 border-gray-700'
                    />
                  </div>

                  <div className='space-y-2'>
                    <Label htmlFor='f-edition'>Edition size</Label>
                    <Input
                      id='f-edition'
                      type='number'
                      min={0}
                      step='1'
                      value={draft.editionSize}
                      onChange={e => updateField('editionSize', e.target.value)}
                      className='bg-gray-800 border-gray-700'
                    />
                  </div>

                  <div className='space-y-2'>
                    <Label htmlFor='f-badge'>Badge</Label>
                    <Input
                      id='f-badge'
                      value={draft.badge}
                      onChange={e => updateField('badge', e.target.value)}
                      placeholder='(none)'
                      className='bg-gray-800 border-gray-700'
                    />
                  </div>

                  <div className='space-y-2'>
                    <Label htmlFor='f-color'>Color</Label>
                    <Input
                      id='f-color'
                      value={draft.color}
                      onChange={e => updateField('color', e.target.value)}
                      className='bg-gray-800 border-gray-700'
                    />
                  </div>

                  <div className='space-y-2 sm:col-span-2'>
                    <Label htmlFor='f-sizes'>Sizes</Label>
                    <Input
                      id='f-sizes'
                      value={draft.sizes}
                      onChange={e => updateField('sizes', e.target.value)}
                      placeholder='S, M, L, XL'
                      className='bg-gray-800 border-gray-700'
                    />
                    <p className='text-xs text-gray-500'>Comma-separated. Stored pipe-delimited in the CSV.</p>
                  </div>

                  <div className='space-y-2 sm:col-span-2'>
                    <Label htmlFor='f-description'>Description</Label>
                    <Textarea
                      id='f-description'
                      value={draft.description}
                      onChange={e => updateField('description', e.target.value)}
                      rows={4}
                      className='bg-gray-800 border-gray-700'
                    />
                  </div>
                </div>

                <div className='flex flex-wrap gap-6'>
                  <div className='flex items-center gap-3'>
                    <Switch
                      id='f-published'
                      checked={draft.published}
                      onCheckedChange={v => updateField('published', v)}
                    />
                    <Label htmlFor='f-published'>Published</Label>
                  </div>
                  <div className='flex items-center gap-3'>
                    <Switch
                      id='f-preorder'
                      checked={draft.isPreorder}
                      onCheckedChange={v => updateField('isPreorder', v)}
                    />
                    <Label htmlFor='f-preorder'>Pre-order</Label>
                  </div>
                </div>

                <Separator className='bg-gray-800' />

                <SotImagery product={selected} />
              </CardContent>
            </Card>
          )}
        </div>
      </motion.div>
    </div>
  );
}

/** Read-only SOT imagery panel — shows what the front-first resolver serves. */
function SotImagery({ product }: { product: CatalogProduct }) {
  const slots: Array<{ key: keyof SotImageSet; label: string }> = [
    { key: 'front', label: 'Front (on-model)' },
    { key: 'back', label: 'Back' },
    { key: 'packshot', label: 'Packshot' },
  ];

  return (
    <div className='space-y-3'>
      <div className='flex items-center justify-between'>
        <h3 className='text-sm font-medium text-gray-300'>SOT imagery (read-only)</h3>
        <span className='text-xs text-gray-500'>assign in renders / review</span>
      </div>
      <div className='grid grid-cols-3 gap-3'>
        {slots.map(({ key, label }) => {
          const path = product.sot?.[key] ?? '';
          return (
            <div key={key} className='space-y-1'>
              <ImagePreview path={path} alt={`${product.sku} ${label}`} />
              <p className='text-xs font-medium text-gray-400'>{label}</p>
              <p className='truncate font-mono text-[10px] text-gray-600' title={path}>
                {path || '— none —'}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ImagePreview({ path, alt }: { path: string; alt: string }) {
  const [broken, setBroken] = useState(false);
  const src = path ? `/${path.replace(/^\/+/, '')}` : '';

  if (!path || broken) {
    return (
      <div className='flex aspect-square items-center justify-center rounded-md border border-gray-800 bg-gray-800/40'>
        <ImageOff className='h-5 w-5 text-gray-600' />
      </div>
    );
  }

  return (
    // SOT paths are theme assets not served by the dashboard; best-effort preview
    // with graceful onError fallback rather than next/image (which would throw on
    // an unconfigured host and can't degrade the same way).
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      onError={() => setBroken(true)}
      className='aspect-square w-full rounded-md border border-gray-800 object-cover'
    />
  );
}
