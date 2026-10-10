import type { Metadata } from 'next';
import CollectionsLanding from './CollectionsLanding';
import { getAllEnrichedCollections } from '@/lib/catalog-server';

export const metadata: Metadata = {
  title: 'Collections | SkyyRose',
  description:
    'Discover the SkyyRose luxury fashion collections. Three immersive worlds: Black Rose, Love Hurts, and Signature.',
  openGraph: {
    title: 'SkyyRose Collections',
    description: 'Three immersive worlds await.',
  },
};

export default async function CollectionsPage() {
  const collections = getAllEnrichedCollections();
  return <CollectionsLanding collections={collections} />;
}
