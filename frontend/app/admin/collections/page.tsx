import { connection } from 'next/server';
import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard } from '@/components/console/Card';
import { getOrders, type WcOrder } from '@/lib/wp/client';
import { getCatalog } from '@/lib/catalog';
import { getAllCollectionSlugs, getCollection } from '@/lib/collections';
import { COLLECTION_ACCENT } from '@/lib/console/brand';
import { buildSkuToCollectionMap, revenueByCollection } from '@/lib/console/orders';
import { formatCurrency, formatPercent } from '@/lib/console/format';
import { getAdminSession } from '@/lib/require-admin-session';
import type { CollectionSlug } from '@/lib/collections';

async function safeOrders(): Promise<WcOrder[]> {
  await connection();
  try {
    const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString();
    return await getOrders({ after: sixtyDaysAgo, per_page: 100 });
  } catch {
    return [];
  }
}

function haloFor(hex: string): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},.16)`;
}

export default async function CollectionsPage() {
  const session = await getAdminSession();
  const [orders, catalog] = await Promise.all([
    session ? safeOrders() : Promise.resolve([]),
    Promise.resolve(getCatalog()),
  ]);
  const skuToCollection = buildSkuToCollectionMap(catalog);
  const revenue = new Map(revenueByCollection(orders, skuToCollection).map((c) => [c.slug, c]));
  const pieceCounts = new Map<string, number>();
  catalog.forEach((p) => {
    if (p.published) pieceCounts.set(p.collection, (pieceCounts.get(p.collection) ?? 0) + 1);
  });

  const slugs = getAllCollectionSlugs();

  return (
    <>
      <TopBar title="Collections" />
      <div className="px-9 py-8 max-w-[1320px]">
        <div className="grid grid-cols-2 gap-[18px]">
          {slugs.map((slug) => {
            const brand = getCollection(slug);
            if (!brand) return null;
            const accent = COLLECTION_ACCENT[slug as CollectionSlug] ?? brand.accentColor;
            const rev = revenue.get(slug);
            return (
              <ConsoleCard key={slug} className="relative overflow-hidden">
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{ background: `radial-gradient(80% 120% at 85% 0%, ${haloFor(accent)}, transparent 60%)` }}
                />
                <div className="relative p-[28px_26px_26px]">
                  <span className="font-mono text-[10px] tracking-[0.22em] uppercase" style={{ color: accent }}>
                    {brand.name}
                  </span>
                  {brand.tagline ? (
                    <p
                      className="italic text-[20px] text-[#F0F0F0] leading-[1.35] mt-3.5 max-w-[32ch]"
                      style={{ fontFamily: 'var(--font-playfair)' }}
                    >
                      {brand.tagline}
                    </p>
                  ) : null}
                  <div className="flex gap-[30px] mt-6">
                    <Stat label="Revenue" value={rev ? formatCurrency(rev.revenue) : '—'} />
                    <Stat label="Share" value={rev ? formatPercent(rev.share) : '—'} />
                    <Stat label="Pieces" value={String(pieceCounts.get(slug) ?? 0)} />
                  </div>
                </div>
                <div className="relative h-1" style={{ background: accent }} />
              </ConsoleCard>
            );
          })}
        </div>
      </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[22px] font-semibold text-white leading-none" style={{ fontFamily: 'var(--font-barlow)' }}>
        {value}
      </div>
      <div className="font-mono text-[9px] tracking-[0.14em] text-[#8A8A92] uppercase mt-1">{label}</div>
    </div>
  );
}
