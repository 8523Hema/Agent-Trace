import type { NextConfig } from "next";

if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL environment variable is required for deployment.");
}

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
