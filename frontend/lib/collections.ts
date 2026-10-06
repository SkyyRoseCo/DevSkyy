export type CollectionSlug = 'black-rose' | 'love-hurts' | 'signature' | 'kids-capsule';

export interface CollectionProduct {
  id: string;
  name: string;
  price: number;
  image: string;
  sizes: string[];
  category?: string;
  description?: string;
}

export interface CollectionScene {
  id: string;
  name: string;
  description: string;
  backgroundImage: string;
  /**
   * Always [] on the raw COLLECTIONS config below — real product data is
   * SOT-authoritative and injected at request time by
   * `getEnrichedCollection`/`getAllEnrichedCollections` in catalog-server.ts.
   * Never hand-populate this array; it silently drifts from the catalog CSV.
   */
  products: CollectionProduct[];
}

export interface CollectionConfig {
  slug: CollectionSlug;
  name: string;
  tagline: string;
  description: string;
  accentColor: string;
  accentColorRGB: string;
  bgColor: string;
  heroImage: string;
  scenes: CollectionScene[];
  environment: 'night' | 'apartment' | 'studio';
  enableBloom: boolean;
  bloomStrength: number;
}

export const COLLECTIONS: Record<CollectionSlug, CollectionConfig> = {
  'black-rose': {
    slug: 'black-rose',
    name: 'Black Rose',
    tagline: 'Where Darkness Blooms',
    description:
      'A gothic garden of silver and shadow. Wrought-iron racks draped in velvet, stone pedestals crowned with glass bell jars, and roses that never wilt.',
    accentColor: '#C0C0C0',
    accentColorRGB: '192, 192, 192',
    bgColor: '#0D0D0D',
    heroImage: '/images/scenes/black-rose-garden.jpg',
    environment: 'night',
    enableBloom: true,
    bloomStrength: 0.4,
    scenes: [
      {
        id: 'the-garden',
        name: 'The Garden',
        description: 'Wrought-iron racks amid gothic rose arbors',
        backgroundImage: '/images/scenes/black-rose-garden.jpg',
        products: [],
      },
    ],
  },
  'love-hurts': {
    slug: 'love-hurts',
    name: 'Love Hurts',
    tagline: 'Pain is Beautiful',
    description:
      'A candlelit ballroom of crimson and gold. Crystal chandeliers cast warm light on velvet chaises and ornate frames, where every piece tells a story of passion.',
    accentColor: '#DC143C',
    accentColorRGB: '220, 20, 60',
    bgColor: '#1A0A0F',
    heroImage: '/images/scenes/love-hurts-ballroom.jpg',
    environment: 'apartment',
    enableBloom: true,
    bloomStrength: 0.3,
    scenes: [
      {
        id: 'the-ballroom',
        name: 'The Ballroom',
        description: 'Candlelit manor with crystal chandeliers',
        backgroundImage: '/images/scenes/love-hurts-ballroom.jpg',
        products: [],
      },
      {
        id: 'the-manor',
        name: 'The Manor',
        description: 'Golden pedestals with flickering candlelight',
        backgroundImage: '/images/scenes/love-hurts-manor.jpg',
        products: [],
      },
    ],
  },
  signature: {
    slug: 'signature',
    name: 'Signature',
    tagline: 'The Art of Being',
    description:
      'An ultra-modern runway experience. Glass venues overlooking the Bay Bridge, marble showrooms, and intimate fitting rooms where every piece is a statement.',
    accentColor: '#B76E79',
    accentColorRGB: '183, 110, 121',
    bgColor: '#0A0A0A',
    heroImage: '/images/scenes/signature-runway.jpg',
    environment: 'studio',
    enableBloom: true,
    bloomStrength: 0.35,
    scenes: [
      {
        id: 'the-runway',
        name: 'The Runway',
        description: 'Bay Bridge glass venue with industrial racks',
        backgroundImage: '/images/scenes/signature-runway.jpg',
        products: [],
      },
      {
        id: 'the-showroom',
        name: 'The Showroom',
        description: 'Grand exhibition hall with marble columns',
        backgroundImage: '/images/scenes/signature-showroom.jpg',
        products: [],
      },
      {
        id: 'the-fitting-room',
        name: 'The Fitting Room',
        description: 'Intimate dressing area with signature racks',
        backgroundImage: '/images/scenes/signature-fitting-room.jpg',
        products: [],
      },
    ],
  },
  'kids-capsule': {
    slug: 'kids-capsule',
    name: 'Kids Capsule',
    tagline: '',
    description:
      'Bold colorblock hoodie and jogger sets designed for young ones who wear luxury from the start. Limited edition drops in sizes 2T–7.',
    accentColor: '#B76E79',
    accentColorRGB: '183, 110, 121',
    bgColor: '#0A0A0A',
    heroImage: '/images/scenes/kids-capsule-hero.jpg',
    environment: 'studio',
    enableBloom: false,
    bloomStrength: 0,
    scenes: [
      {
        id: 'the-playground',
        name: 'The Playground',
        description: 'Vibrant colorblock sets for the next generation',
        backgroundImage: '/images/scenes/kids-capsule-hero.jpg',
        products: [],
      },
    ],
  },
};

export function getCollection(slug: string): CollectionConfig | undefined {
  return COLLECTIONS[slug as CollectionSlug];
}

export function getAllCollections(): CollectionConfig[] {
  return Object.values(COLLECTIONS);
}

export function getAllCollectionSlugs(): CollectionSlug[] {
  return Object.keys(COLLECTIONS) as CollectionSlug[];
}
