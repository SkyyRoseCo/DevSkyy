import { connection } from 'next/server';
import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard, ConsoleRow } from '@/components/console/Card';
import { RevenueChart } from '@/components/console/RevenueChart';
import { StatusPill } from '@/components/console/StatusPill';
import { OverviewKpis } from '@/components/console/screens/OverviewKpis';
import { AgentsListCard } from '@/components/console/screens/AgentsListCard';
import { getOrders, getAdminProducts, type WcOrder, type WcAdminProduct } from '@/lib/wp/client';
import { getCatalog } from '@/lib/catalog';
import { getAdminSession } from '@/lib/require-admin-session';
import { COLLECTION_ACCENT } from '@/lib/console/brand';
import {
  buildSkuToCollectionMap,
  latestOrderDate,
  mapOrderStatus,
  orderCollection,
  orderCustomerName,
  orderPieceSummary,
  orderTotal,
  revenueByCollection,
  weeklyRevenueSeries,
} from '@/lib/console/orders';
import { formatCurrency, formatPercent } from '@/lib/console/format';
import type { CollectionSlug } from '@/lib/collections';

async function safeOrders(): Promise<WcOrder[]> {
  // connection() must resolve before Date.now() — Cache Components treats
  // the current time as request-bound data, not something a Server
  // Component can read during static prerendering on its own.
  await connection();
  try {
    const sixtyDaysAgo = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString();
    return await getOrders({ after: sixtyDaysAgo, per_page: 100 });
  } catch {
    return [];
  }
}

async function safeAdminProducts(): Promise<WcAdminProduct[]> {
  try {
    return await getAdminProducts();
  } catch {
    return [];
  }
}

export default async function OverviewPage() {
  const session = await getAdminSession();
  const [orders, adminProducts] = session ? await Promise.all([safeOrders(), safeAdminProducts()]) : [[], []];
  const catalog = getCatalog();
  const skuToCollection = buildSkuToCollectionMap(catalog);
  const referenceDate = latestOrderDate(orders);
  const wired = orders.length > 0 || adminProducts.length > 0;

  const currentWeekly = weeklyRevenueSeries(orders, 5, 0);
  const priorWeekly = weeklyRevenueSeries(orders, 5, 5);
  const revTotal = currentWeekly.reduce((a, b) => a + b, 0);

  const collectionRevenue = revenueByCollection(orders, skuToCollection);
  const catalogCollections = new Set(catalog.map(p => p.collection));

  const inventory = adminProducts
    .filter(p => p.manage_stock)
    .map(p => {
      const catalogEntry = catalog.find(c => c.sku === p.sku);
      const collectionLabel = catalogEntry?.collection ?? '—';
      if (p.stock_status === 'outofstock') return { name: p.name, collectionLabel, flag: 'Out of stock', ...danger() };
      if (typeof p.stock_quantity === 'number' && p.stock_quantity <= 5) {
        return { name: p.name, collectionLabel, flag: `${p.stock_quantity} left`, ...warning() };
      }
      return { name: p.name, collectionLabel, flag: 'Healthy', ...idle() };
    })
    .filter(i => i.flag !== 'Healthy')
    .slice(0, 4);

  const recentOrders = [...orders]
    .filter(o => o.status !== 'trash')
    .sort((a, b) => (b.date_created as string).localeCompare(a.date_created as string))
    .slice(0, 5);

  return (
    <>
      <TopBar title='Overview' />
      <div className='px-9 py-8 max-w-[1320px]'>
        {!wired && (
          <ConsoleCard className='p-5 mb-6'>
            <span className='font-mono text-[11px] text-[#E5A85C]'>
              WooCommerce isn&apos;t returning data yet — wire credentials on the Settings screen. Figures below are
              empty until then.
            </span>
          </ConsoleCard>
        )}

        <OverviewKpis orders={orders} referenceDate={referenceDate.toISOString()} />

        <div className='grid grid-cols-[1.55fr_1fr] gap-[18px] mb-[22px]'>
          <ConsoleCard className='p-6'>
            <div className='flex justify-between items-start mb-2'>
              <div>
                <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
                  Revenue
                </span>
                <div className='text-[28px] font-semibold text-white mt-2' style={{ fontFamily: 'var(--font-barlow)' }}>
                  {formatCurrency(revTotal)}
                </div>
              </div>
              <div className='flex gap-[18px] font-mono text-[10px] tracking-[0.1em] text-[#A0A0A0] uppercase'>
                <span className='flex items-center gap-[7px]'>
                  <span className='w-[9px] h-[2px]' style={{ background: 'var(--acc)' }} /> This period
                </span>
                <span className='flex items-center gap-[7px]'>
                  <span className='w-[9px] h-[2px] bg-[#3A3A42]' /> Prior
                </span>
              </div>
            </div>
            <RevenueChart
              current={currentWeekly}
              prior={priorWeekly}
              labels={['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Now']}
              gradientId='dshFillOverview'
            />
          </ConsoleCard>

          <AgentsListCard />
        </div>

        <div className='grid grid-cols-[1.55fr_1fr] gap-[18px] mb-[22px]'>
          <ConsoleCard className='p-6'>
            <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
              Collection Performance
            </span>
            <div className='flex flex-col gap-5 mt-[22px]'>
              {collectionRevenue.length === 0 && (
                <div className='font-mono text-[10px] text-[#7A7A82]'>No attributed orders in the last 60 days.</div>
              )}
              {collectionRevenue.map(c => {
                const accent = COLLECTION_ACCENT[c.slug as CollectionSlug] ?? '#8A8A92';
                const label = catalogCollections.has(c.slug) ? c.slug.replace('-', ' ') : c.slug;
                return (
                  <div key={c.slug}>
                    <div className='flex justify-between items-baseline mb-[9px]'>
                      <span
                        className='text-[13px] tracking-[0.12em] uppercase text-[#E0E0E0]'
                        style={{ fontFamily: 'var(--font-cinzel)' }}
                      >
                        {label}
                      </span>
                      <span className='text-[13px] text-[#A0A0A0]' style={{ fontFamily: 'var(--font-barlow)' }}>
                        {formatCurrency(c.revenue)} · {formatPercent(c.share)}
                      </span>
                    </div>
                    <div className='h-[7px] rounded-full overflow-hidden bg-[#1A1A20]'>
                      <div
                        className='h-full rounded-full'
                        style={{ width: formatPercent(c.share), background: accent }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </ConsoleCard>

          <ConsoleCard className='p-6'>
            <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
              Inventory Signals
            </span>
            <div className='flex flex-col gap-0.5 mt-3.5'>
              {inventory.length === 0 && (
                <div className='font-mono text-[10px] text-[#7A7A82] py-2'>No low-stock or out-of-stock signals.</div>
              )}
              {inventory.map((item, i) => (
                <ConsoleRow key={`${item.name}-${i}`} className='flex items-center gap-3 px-1.5 py-[11px]'>
                  <div className='flex-1 min-w-0'>
                    <div className='text-[13px] text-[#E0E0E0] truncate'>{item.name}</div>
                    <div className='font-mono text-[9.5px] tracking-[0.12em] text-[#7A7A82] uppercase mt-0.5'>
                      {item.collectionLabel}
                    </div>
                  </div>
                  <StatusPill label={item.flag} bg={item.bg} color={item.color} className='flex-none' />
                </ConsoleRow>
              ))}
            </div>
          </ConsoleCard>
        </div>

        <ConsoleCard className='p-6'>
          <div className='flex justify-between items-center mb-1.5'>
            <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
              Recent Orders
            </span>
            <a
              href='/admin/orders'
              className='font-mono text-[10px] tracking-[0.14em] text-[#A0A0A0] uppercase cursor-pointer'
            >
              View all
            </a>
          </div>
          <div
            className='grid gap-3 px-2 py-3.5 border-b border-white/[0.08] font-mono text-[9.5px] tracking-[0.14em] text-[#7A7A82] uppercase'
            style={{ gridTemplateColumns: '120px 1.4fr 1.6fr 1fr 100px 120px' }}
          >
            <span>Order</span>
            <span>Customer</span>
            <span>Piece</span>
            <span>Collection</span>
            <span className='text-right'>Total</span>
            <span className='text-right'>Status</span>
          </div>
          {recentOrders.length === 0 && (
            <div className='font-mono text-[10px] text-[#7A7A82] py-4'>No orders in the last 60 days.</div>
          )}
          {recentOrders.map(order => {
            const status = mapOrderStatus(order.status);
            return (
              <ConsoleRow
                key={order.id}
                className='grid gap-3 px-2 py-[15px] border-b border-white/[0.04] items-center'
                style={{ gridTemplateColumns: '120px 1.4fr 1.6fr 1fr 100px 120px' }}
              >
                <span className='font-mono text-[11.5px] tracking-[0.04em]' style={{ color: 'var(--acc)' }}>
                  #{(order.number as string) ?? order.id}
                </span>
                <span className='text-[13.5px] text-[#E0E0E0]'>{orderCustomerName(order)}</span>
                <span className='italic text-[14px] text-[#C8C8C8]' style={{ fontFamily: 'var(--font-playfair)' }}>
                  {orderPieceSummary(order)}
                </span>
                <span className='font-mono text-[10px] tracking-[0.1em] text-[#9A9AA2] uppercase'>
                  {orderCollection(order, skuToCollection)}
                </span>
                <span
                  className='text-[14px] text-white text-right font-medium'
                  style={{ fontFamily: 'var(--font-barlow)' }}
                >
                  {formatCurrency(orderTotal(order))}
                </span>
                <span className='text-right'>
                  <StatusPill label={status.label} bg={status.bg} color={status.color} />
                </span>
              </ConsoleRow>
            );
          })}
        </ConsoleCard>
      </div>
    </>
  );
}

function danger() {
  return { bg: 'rgba(220,20,60,.12)', color: '#DC143C' };
}
function warning() {
  return { bg: 'rgba(229,168,92,.12)', color: '#E5A85C' };
}
function idle() {
  return { bg: 'rgba(255,255,255,.05)', color: '#8A8A92' };
}
