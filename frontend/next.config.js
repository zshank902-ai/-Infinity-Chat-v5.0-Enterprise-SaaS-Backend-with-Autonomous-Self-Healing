/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Disable server-side features that might crash
  serverExternalPackages: ["lucide-react"],
};

module.exports = nextConfig;
