import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [new URL('http://localhost:8080/api/files/**'), new URL('https://api.flooq.io/api/files/**')],
  },
  compiler: {
    removeConsole: false,
  },
  allowedDevOrigins: ['http://localhost'],
  serverRuntimeConfig: {
    NEXT_PUBLIC_POCKETBASE_URL: process.env.NEXT_PUBLIC_POCKETBASE_URL,
    REPORTER_URL: process.env.REPORTER_URL,
  },
};

export default nextConfig;
