import { defineConfig, devices } from '@playwright/test';

// Offline UI qualification: network responses are intercepted by the spec.
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: 'god-mode.spec.ts',
  workers: 1,
  retries: 0,
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    launchOptions: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
      args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-gl=angle', '--use-angle=swiftshader'],
    } : {},
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 5'] } },
  ],
  webServer: process.env.BASE_URL ? undefined : {
    command: process.env.CI ? 'npm run start -- --hostname 127.0.0.1' : 'npm run dev -- --hostname 127.0.0.1',
    url: 'http://127.0.0.1:3000/healthz',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
