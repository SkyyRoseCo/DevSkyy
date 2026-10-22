import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard, ConsoleRow } from '@/components/console/Card';
import { getCustomers, getOrders, type WcCustomer, type WcOrder } from '@/lib/wp/client';
import { aggregateByCustomer } from '@/lib/console/orders';
import { getAdminSession } from '@/lib/require-admin-session';
import { formatCount, formatCurrency } from '@/lib/console/format';
import { agentInitials, agentGradient } from '@/lib/console/agents';

async function safeCustomers(): Promise<WcCustomer[]> {
  try {
    return await getCustomers({ per_page: 50 });
  } catch {
    return [];
  }
}

async function safeOrders(): Promise<WcOrder[]> {
  try {
    return await getOrders({ per_page: 100 });
  } catch {
    return [];
  }
}

/** Real WC customer records don't carry order-count/spend on the customer
 *  resource itself (verified via WooCommerce REST docs) — those numbers are
 *  aggregated here from real orders, not read from a field that doesn't exist. */
function tierFor(spend: number): { label: string; color: string } {
  if (spend >= 5000) return { label: 'Atelier', color: 'var(--acc)' };
  if (spend >= 1000) return { label: 'Signature', color: '#D4AF37' };
  return { label: 'New', color: '#5FBF7F' };
}

export default async function CustomersPage() {
  const session = await getAdminSession();
  const [customers, orders] = session
    ? await Promise.all([safeCustomers(), safeOrders()])
    : [[], []];
  const bySpend = aggregateByCustomer(orders);

  return (
    <>
      <TopBar title="Customers" />
      <div className="px-9 py-8 max-w-[1320px]">
        <ConsoleCard className="p-6">
          <span className="font-mono text-[10px] tracking-[0.18em] uppercase" style={{ color: 'var(--acc)' }}>
            Customers
          </span>
          <div
            className="grid gap-3 px-2 pt-4 pb-3.5 border-b border-white/[0.08] font-mono text-[9.5px] tracking-[0.14em] text-[#7A7A82] uppercase mt-2"
            style={{ gridTemplateColumns: '2fr 1fr 1.4fr 80px 110px' }}
          >
            <span>Name</span>
            <span>Tier</span>
            <span>Location</span>
            <span className="text-right">Orders</span>
            <span className="text-right">Spend</span>
          </div>
          {customers.length === 0 && (
            <div className="font-mono text-[10px] text-[#7A7A82] py-4">
              No customers returned from WooCommerce — wire credentials on the Settings screen.
            </div>
          )}
          {customers.map((c) => {
            const name = `${c.first_name ?? ''} ${c.last_name ?? ''}`.trim() || c.email || 'Unnamed';
            const agg = bySpend.get(c.id) ?? { orderCount: 0, spend: 0 };
            const tier = tierFor(agg.spend);
            const location = [c.billing?.city, c.billing?.state].filter(Boolean).join(', ') || '—';
            return (
              <ConsoleRow key={c.id} className="grid gap-3 px-2 py-3.5 border-b border-white/[0.04] items-center" style={{ gridTemplateColumns: '2fr 1fr 1.4fr 80px 110px' }}>
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className="w-9 h-9 rounded-full flex items-center justify-center text-[12px] font-semibold flex-none"
                    style={{ background: agentGradient(name), color: '#0A0A0A', fontFamily: 'var(--font-cinzel)' }}
                  >
                    {agentInitials(name)}
                  </div>
                  <span className="text-[13.5px] text-[#E0E0E0] truncate">{name}</span>
                </div>
                <span className="font-mono text-[9px] tracking-[0.1em] uppercase" style={{ color: tier.color }}>
                  {tier.label}
                </span>
                <span className="text-[12.5px] text-[#9A9AA2]">{location}</span>
                <span className="text-[14px] text-[#E0E0E0] text-right" style={{ fontFamily: 'var(--font-cinzel)' }}>
                  {formatCount(agg.orderCount)}
                </span>
                <span className="text-[14px] text-white text-right font-medium" style={{ fontFamily: 'var(--font-cinzel)' }}>
                  {formatCurrency(agg.spend)}
                </span>
              </ConsoleRow>
            );
          })}
        </ConsoleCard>
      </div>
    </>
  );
}
