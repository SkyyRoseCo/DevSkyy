import path from 'node:path';
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: { environment: 'node', include: ['lib/god-mode-runtime-proxy.test.ts'] },
  resolve: { alias: { '@': path.resolve('.') } },
});
