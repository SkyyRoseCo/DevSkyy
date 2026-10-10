import type { Metadata } from 'next';
import HomePage from './(storefront)/HomePage';
import SiteNav from '@/components/navigation/SiteNav';
import IncentivePopup from '@/components/marketing/IncentivePopup';
import { getAllEnrichedCollections } from '@/lib/catalog-server';

export const metadata: Metadata = {
  title: 'SkyyRose',
  description:
    'Discover luxury fashion reimagined. Three immersive collections: Black Rose, Love Hurts, and Signature. AI-crafted designs, 3D experiences, exclusive pre-orders.',
  openGraph: {
    title: 'SkyyRose',
    description:
      'Luxury fashion reimagined through AI and immersive 3D experiences.',
    images: [{ url: '/images/og-homepage.jpg', width: 1200, height: 630 }],
  },
};

export default function Home() {
  const collections = getAllEnrichedCollections();
  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      <SiteNav />
      <main>
        <HomePage collections={collections} />
      </main>
      <IncentivePopup />
    </div>
  );
}
