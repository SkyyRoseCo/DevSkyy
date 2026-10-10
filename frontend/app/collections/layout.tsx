import type { Metadata } from 'next';
import SiteNav from '@/components/navigation/SiteNav';
import IncentivePopup from '@/components/marketing/IncentivePopup';

export const metadata: Metadata = {
  title: {
    template: '%s | SkyyRose Collections',
    default: 'Collections | SkyyRose',
  },
  description:
    'Explore the SkyyRose luxury fashion collections. Immersive 3D experiences featuring Black Rose, Love Hurts, and Signature collections.',
  openGraph: {
    title: 'SkyyRose Collections',
    description:
      'Explore our immersive fashion collections.',
    siteName: 'SkyyRose',
    type: 'website',
  },
};

export default function CollectionsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      <SiteNav />
      {children}
      <IncentivePopup />
    </div>
  );
}
