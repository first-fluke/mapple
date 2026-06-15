import { initOpenNextCloudflareForDev } from '@opennextjs/cloudflare';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '9000',
        pathname: '/avatars/**',
      },
    ],
  },
  experimental: {
    authInterrupts: true,
  },
  async rewrites() {
    const apiUrl = process.env.API_URL || 'http://localhost:11008';
    return [
      {
        source: '/api/proxy/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;

// Enables OpenNext's Cloudflare bindings (getCloudflareContext) during `next dev`.
initOpenNextCloudflareForDev();
