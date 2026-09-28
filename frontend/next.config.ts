import path from 'path';
import type { NextConfig } from 'next';

// On Vercel, rootDirectory=frontend so only this dir is uploaded; the
// repo-root lockfile isn't in build scope and there's no ambiguous-root
// warning to suppress. Setting outputFileTracingRoot above the project
// root on Vercel causes a doubled-path bug in the post-build trace step
// (looks for .next/routes-manifest.json at /vercel/path1/path1/.next/...
// and crashes with ENOENT).
//
// Locally, both lockfiles are present, so we still set the override —
// but only when not running on Vercel.
const isVercel = !!process.env.VERCEL;
const standalone = process.env.NEXT_OUTPUT_STANDALONE === '1';
const tracingRoot = standalone ? __dirname : isVercel ? undefined : path.resolve(__dirname, '..');

const nextConfig: NextConfig = {
  reactStrictMode: true,
  ...(standalone && { output: 'standalone' }),
  async headers() {
    // These headers previously lived only in vercel.json. Apply them on every host.
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(self), microphone=(self), geolocation=(self)' },
        ],
      },
      {
        source: '/api/:path*',
        headers: [
          { key: 'Cache-Control', value: 'no-store, max-age=0' },
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'X-Requested-With, Content-Type, Authorization' },
          { key: 'Access-Control-Allow-Origin', value: 'https://skyyrose.co' },
        ],
      },
      {
        source: '/collections/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors 'self' https://skyyrose.com https://*.skyyrose.com",
          },
        ],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/admin',
        permanent: false,
      },
    ];
  },
  outputFileTracingIncludes: {
    '/*': ['./data/skyyrose-catalog.csv'],
  },
  ...(tracingRoot && { outputFileTracingRoot: tracingRoot }),
  ...(tracingRoot && { turbopack: { root: tracingRoot } }),
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.skyyrose.co',
      },
      {
        protocol: 'https',
        hostname: '**.devskyy.app',
      },
    ],
  },
  cacheComponents: true,
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
};

export default nextConfig;
