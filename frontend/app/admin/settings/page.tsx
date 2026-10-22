import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard } from '@/components/console/Card';
import { getPlatformConnections } from '@/lib/social-media/config';

type Status = 'Connected' | 'Action needed' | 'Not connected';

interface IntegrationItem {
  name: string;
  desc: string;
  status: Status;
  fields: string[];
}

interface IntegrationGroup {
  group: string;
  items: IntegrationItem[];
}

function statusColor(status: Status): string {
  if (status === 'Connected') return '#5FBF7F';
  if (status === 'Action needed') return '#E5A85C';
  return '#8A8A92';
}

function envStatus(present: boolean[]): Status {
  if (present.every(Boolean)) return 'Connected';
  if (present.some(Boolean)) return 'Action needed';
  return 'Not connected';
}

export default function SettingsPage() {
  const wpPresent = [
    Boolean(process.env.WP_BASE_URL),
    Boolean(process.env.WP_APP_USER),
    Boolean(process.env.WP_APP_PASSWORD),
  ];
  const wcPresent = [Boolean(process.env.WC_CONSUMER_KEY), Boolean(process.env.WC_CONSUMER_SECRET)];
  const stripePresent = [Boolean(process.env.STRIPE_SECRET_KEY)];
  const webhookPresent = [Boolean(process.env.WP_WEBHOOK_SECRET)];
  const claudePresent = [Boolean(process.env.ANTHROPIC_API_KEY)];

  const socials = getPlatformConnections();
  const socialByPlatform = new Map(socials.map(s => [s.platform, s]));

  const groups: IntegrationGroup[] = [
    {
      group: 'Storefront',
      items: [
        {
          name: 'WordPress',
          desc: 'skyyrose.co · theme and REST API',
          status: envStatus(wpPresent),
          fields: ['Site URL (WP_BASE_URL)', 'Application password'],
        },
        {
          name: 'WooCommerce',
          desc: 'Orders, products and inventory',
          status: envStatus(wcPresent),
          fields: ['Consumer key', 'Consumer secret'],
        },
      ],
    },
    {
      group: 'Payments',
      items: [
        {
          name: 'Stripe',
          desc: 'Checkout and payouts',
          status: envStatus(stripePresent),
          fields: ['Secret key (STRIPE_SECRET_KEY)'],
        },
      ],
    },
    {
      group: 'Social',
      items: [
        {
          name: 'Instagram',
          desc: 'DMs and scheduled posts',
          status: socialByPlatform.get('instagram')?.connected ? 'Connected' : 'Not connected',
          fields: ['INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_BUSINESS_ACCOUNT_ID'],
        },
        {
          name: 'TikTok',
          desc: 'Clip scheduling',
          status: socialByPlatform.get('tiktok')?.connected ? 'Connected' : 'Not connected',
          fields: ['TIKTOK_ACCESS_TOKEN'],
        },
        {
          name: 'X',
          desc: 'Drop threads',
          status: socialByPlatform.get('twitter')?.connected ? 'Connected' : 'Not connected',
          fields: ['TWITTER_API_KEY', 'TWITTER_API_SECRET'],
        },
        {
          name: 'Facebook',
          desc: 'Catalog sync',
          status: socialByPlatform.get('facebook')?.connected ? 'Connected' : 'Not connected',
          fields: ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID'],
        },
        { name: 'Pinterest', desc: 'Lookbook pins', status: 'Not connected', fields: ['Not wired in this build'] },
        { name: 'YouTube', desc: 'Film uploads', status: 'Not connected', fields: ['Not wired in this build'] },
      ],
    },
    {
      group: 'Automation and Infrastructure',
      items: [
        {
          name: 'Webhooks',
          desc: 'Real-time order and stock events',
          status: envStatus(webhookPresent),
          fields: ['Signing secret (WP_WEBHOOK_SECRET)'],
        },
        {
          name: 'Claude API',
          desc: 'DevSkyy agent intelligence',
          status: envStatus(claudePresent),
          fields: ['API key (ANTHROPIC_API_KEY)'],
        },
        {
          name: 'CDN / Media',
          desc: 'Imagery delivery and cache',
          status: 'Not connected',
          fields: ['Not wired in this build'],
        },
      ],
    },
  ];

  return (
    <>
      <TopBar title='Settings' />
      <div className='px-4 sm:px-9 py-8 max-w-[1320px] min-w-0'>
        <div
          className='rounded-[10px] p-[24px_26px] mb-[22px] border'
          style={{ borderColor: 'rgba(183,110,121,.28)', background: 'linear-gradient(135deg,#100E12,#0A0A0A)' }}
        >
          <span className='font-mono text-[10px] tracking-[0.22em] uppercase' style={{ color: 'var(--acc)' }}>
            Configure and Wire Up
          </span>
          <p
            className='italic text-[15px] text-white/65 mt-2 max-w-[64ch]'
            style={{ fontFamily: 'var(--font-playfair)' }}
          >
            Connection status reads real environment variables server-side — nothing here is simulated. Set the missing
            ones in <code className='not-italic font-mono text-[13px]'>.env.local</code> (see{' '}
            <code className='not-italic font-mono text-[13px]'>.env.example</code>) and redeploy to flip a card to
            Connected.
          </p>
        </div>

        {groups.map(g => (
          <div key={g.group} className='mb-6'>
            <div className='font-mono text-[10px] tracking-[0.18em] text-[#8A8A92] uppercase mb-3'>{g.group}</div>
            <div className='grid grid-cols-1 sm:grid-cols-2 gap-[14px]'>
              {g.items.map(item => (
                <ConsoleCard key={item.name} className='p-5 min-w-0 break-words'>
                  <div className='flex flex-wrap justify-between items-center gap-2.5'>
                    <span
                      className='text-[15px] tracking-[0.06em] text-white uppercase'
                      style={{ fontFamily: 'var(--font-cinzel)' }}
                    >
                      {item.name}
                    </span>
                    <span
                      className='inline-flex items-center gap-1.5 font-mono text-[8.5px] tracking-[0.12em] uppercase'
                      style={{ color: statusColor(item.status) }}
                    >
                      <span className='w-1.5 h-1.5 rounded-full' style={{ background: statusColor(item.status) }} />
                      {item.status}
                    </span>
                  </div>
                  <div className='text-[12.5px] text-[#9A9AA2] mt-1.5'>{item.desc}</div>
                  <div className='flex flex-col gap-2.5 mt-4'>
                    {item.fields.map(field => (
                      <div key={field}>
                        <div className='font-mono text-[8.5px] tracking-[0.12em] text-[#7A7A82] uppercase mb-1.5'>
                          {field}
                        </div>
                        <div className='font-mono text-[11px] text-[#5A5A62] bg-white/[0.03] border border-white/[0.08] rounded-md px-3 py-2.5'>
                          {item.status === 'Connected' ? 'Configured' : 'Not configured'}
                        </div>
                      </div>
                    ))}
                  </div>
                </ConsoleCard>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
