import path from 'node:path';
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: { environment: 'node', include: ['app/admin/god-mode/god-mode.test.tsx'] },
  resolve: { alias: { '@': path.resolve('.') } },
});
