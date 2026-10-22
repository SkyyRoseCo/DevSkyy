import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard, ConsoleRow } from '@/components/console/Card';
import { StatusPill } from '@/components/console/StatusPill';
import { getOrders, type WcOrder } from '@/lib/wp/client';
import { getCatalog } from '@/lib/catalog';
import {
  buildSkuToCollectionMap,
  mapOrderStatus,
  orderCollection,
  orderCustomerName,
  orderPieceSummary,
  orderTotal,
} from '@/lib/console/orders';
import { formatCount, formatCurrency } from '@/lib/console/format';
import { getAdminSession } from '@/lib/require-admin-session';

async function safeOrders(): Promise<WcOrder[]> {
  try {
    return await getOrders({ per_page: 100 });
  } catch {
    return [];
  }
}

export default async function OrdersPage() {
  const session = await getAdminSession();
  const [orders, catalog] = await Promise.all([
    session ? safeOrders() : Promise.resolve([]),
    Promise.resolve(getCatalog()),
  ]);
  const skuToCollection = buildSkuToCollectionMap(catalog);

  const counts = {
    New: orders.filter(o => o.status === 'on-hold' || o.status === 'pending').length,
    Processing: orders.filter(o => o.status === 'processing').length,
    Shipped: orders.filter(o => o.status === 'shipped').length,
    Fulfilled: orders.filter(o => o.status === 'completed').length,
  };

  const sorted = [...orders]
    .filter(o => o.status !== 'trash')
    .sort((a, b) => ((b.date_created as string) ?? '').localeCompare((a.date_created as string) ?? ''));

  return (
    <>
      <TopBar title='Orders' />
      <div className='px-9 py-8 max-w-[1320px]'>
        <div className='grid grid-cols-4 gap-[18px] mb-[22px]'>
          {(Object.entries(counts) as [keyof typeof counts, number][]).map(([label, value]) => (
            <ConsoleCard key={label} className='p-5'>
              <div className='font-mono text-[10px] tracking-[0.18em] text-[#A0A0A0] uppercase'>{label}</div>
              <div
                className='text-[34px] font-semibold mt-3 leading-none'
                style={{
                  fontFamily: 'var(--font-barlow)',
                  color: label === 'Fulfilled' ? '#5FBF7F' : label === 'Processing' ? '#E5A85C' : 'var(--acc)',
                }}
              >
                {formatCount(value)}
              </div>
            </ConsoleCard>
          ))}
        </div>

        <ConsoleCard className='p-6'>
          <div className='flex justify-between items-center gap-4 flex-wrap mb-2.5'>
            <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
              All Orders
            </span>
            <span className='font-mono text-[9px] tracking-[0.1em] text-[#7A7A82] uppercase'>
              {formatCount(sorted.length)} total
            </span>
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
          {sorted.length === 0 && <div className='font-mono text-[10px] text-[#7A7A82] py-4'>No orders found.</div>}
          {sorted.map(order => {
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
