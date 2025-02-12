// vite.config.js

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

import { fileURLToPath, URL } from "node:url";
export default defineConfig({
  resolve: {
    extensions: [".mjs", ".js", ".ts", ".jsx", ".tsx", ".json", ".vue"],
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    watch: {
      usePolling: true,
    },
  },
  plugins: [vue()],
  envPrefix: "VITE_",
  optimizeDeps: {
    exclude: ["js-big-decimal"],
    maxAge: 60 * 60 * 24, // 24 hours
  },
});
