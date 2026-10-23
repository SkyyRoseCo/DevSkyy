import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard } from '@/components/console/Card';
import { getAdminProducts, type WcAdminProduct } from '@/lib/wp/client';
import { getCatalog } from '@/lib/catalog';
import { COLLECTION_ACCENT } from '@/lib/console/brand';
import { formatCurrency } from '@/lib/console/format';
import type { CollectionSlug } from '@/lib/collections';
import { getAdminSession } from '@/lib/require-admin-session';

async function safeAdminProducts(): Promise<WcAdminProduct[]> {
  try {
    return await getAdminProducts();
  } catch {
    return [];
  }
}

function stockView(p: WcAdminProduct): { label: string; color: string } {
  if (p.stock_status === 'outofstock') return { label: 'Out of stock', color: '#E5A85C' };
  if (typeof p.stock_quantity === 'number' && p.stock_quantity <= 5)
    return { label: `${p.stock_quantity} left`, color: '#E5A85C' };
  if (p.stock_status === 'onbackorder') return { label: 'Backorder', color: '#E5A85C' };
  return { label: 'Healthy', color: '#8A8A92' };
}

export default async function ProductsPage() {
  const session = await getAdminSession();
  const [wcProducts, catalog] = await Promise.all([
    session ? safeAdminProducts() : Promise.resolve([]),
    Promise.resolve(getCatalog()),
  ]);
  const catalogBySku = new Map(catalog.map(p => [p.sku, p]));

  // WC is the live source (real price/stock); the catalog CSV supplies the
  // collection accent when a SKU match exists. Products only in WC (no SOT
  // catalog entry) still render — collection accent falls back to neutral.
  const products = wcProducts.filter(p => Boolean(p.sku));

  return (
    <>
      <TopBar title='Products' />
      <div className='px-9 py-8 max-w-[1320px]'>
        {products.length === 0 && (
          <ConsoleCard className='p-5 mb-6'>
            <span className='font-mono text-[11px] text-[#E5A85C]'>
              No products returned from WooCommerce — wire credentials on the Settings screen.
            </span>
          </ConsoleCard>
        )}
        <div className='grid grid-cols-3 gap-[18px]'>
          {products.map(p => {
            const catalogEntry = catalogBySku.get(p.sku);
            const slug = catalogEntry?.collection as CollectionSlug | undefined;
            const accent = (slug && COLLECTION_ACCENT[slug]) || '#8A8A92';
            const stock = stockView(p);
            const image = p.images?.[0]?.src;
            return (
              <ConsoleCard key={p.id} className='overflow-hidden'>
                <div className='relative h-[200px] flex items-center justify-center bg-[#0e0e10]'>
                  {image ? (
                    // eslint-disable-next-line @next/next/no-img-element -- WC-hosted product photo, dimensions vary per SKU
                    <img src={image} alt={p.name} className='absolute inset-0 w-full h-full object-cover' />
                  ) : (
                    <span className='font-mono text-[9px] tracking-[0.12em] text-[#5A5A62] uppercase'>
                      no image on file
                    </span>
                  )}
                  {catalogEntry && (
                    <span
                      className='absolute top-3 left-3 font-mono text-[8.5px] tracking-[0.14em] uppercase'
                      style={{ color: accent }}
                    >
                      {catalogEntry.collection.replace('-', ' ')}
                    </span>
                  )}
                </div>
                <div className='p-[18px]'>
                  <div
                    className='italic text-[17px] text-white leading-tight'
                    style={{ fontFamily: 'var(--font-playfair)' }}
                  >
                    {p.name}
                  </div>
                  <div className='flex justify-between items-center mt-3.5'>
                    <span className='text-[16px] text-white font-medium' style={{ fontFamily: 'var(--font-barlow)' }}>
                      {formatCurrency(Number(p.price) || 0)}
                    </span>
                    <span className='font-mono text-[9px] tracking-[0.1em] uppercase' style={{ color: stock.color }}>
                      {stock.label}
                    </span>
                  </div>
                </div>
              </ConsoleCard>
            );
          })}
        </div>
      </div>
    </>
  );
}
