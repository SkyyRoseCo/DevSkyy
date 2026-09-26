export interface ConsoleNavItem {
  id: string;
  href: string;
  label: string;
}

export const CONSOLE_NAV_ITEMS: ConsoleNavItem[] = [
  { id: 'overview', href: '/admin', label: 'Overview' },
  { id: 'hub', href: '/admin/hub', label: 'The Hub' },
  { id: 'orders', href: '/admin/orders', label: 'Orders' },
  { id: 'products', href: '/admin/products', label: 'Products' },
  { id: 'collections', href: '/admin/collections', label: 'Collections' },
  { id: 'scene-authority', href: '/admin/scene-authority', label: 'Scene Authority' },
  { id: 'agents', href: '/admin/agents', label: 'Agent OS' },
  { id: 'web-extraction', href: '/admin/web-extraction', label: 'Web Extract' },
  { id: 'customers', href: '/admin/customers', label: 'Customers' },
  { id: 'settings', href: '/admin/settings', label: 'Settings' },
];
