import { expect, test } from '@playwright/test';

// The Operator Console replaced the editable settings form in c2d439d70.
// These browser tests cover its read-only integration inventory. Only session
// and unrelated navigation badges are fixtures; the page and server-rendered
// connection states are real. This is not a live-provider connection test.
test.describe('Settings integration inventory', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/auth/session', route => route.fulfill({
      json: {
        user: { name: 'Test Operator', email: 'operator@example.test' },
        expires: '2099-01-01T00:00:00.000Z',
      },
    }));
    await page.route('**/api/console/orders-count', route => route.fulfill({ json: { count: 0 } }));
    await page.route('**/api/v1/agents**', route => route.fulfill({
      json: { timestamp: '2026-09-02T00:00:00.000Z', total_agents: 0, active_agents: 0, agents_by_category: {}, agents: [] },
    }));
    await page.goto('/admin/settings');
    await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  });

  test('explains how connection configuration is managed', async ({ page }) => {
    await expect(page.getByText('Configure and Wire Up', { exact: true })).toBeVisible();
    await expect(page.getByText(/Connection status reads real environment variables server-side/)).toBeVisible();
    await expect(page.getByText('.env.example', { exact: true })).toBeVisible();
  });

  test('groups integrations by operational responsibility', async ({ page }) => {
    for (const group of ['Storefront', 'Payments', 'Social', 'Automation and Infrastructure']) {
      await expect(page.getByText(group, { exact: true })).toBeVisible();
    }
    await expect(page.locator('.dsh-card')).toHaveCount(12);
  });

  const integrations = [
    { name: 'WordPress', fields: ['Site URL (WP_BASE_URL)', 'Application password'] },
    { name: 'WooCommerce', fields: ['Consumer key', 'Consumer secret'] },
    { name: 'Stripe', fields: ['Secret key (STRIPE_SECRET_KEY)'] },
    { name: 'Instagram', fields: ['INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_BUSINESS_ACCOUNT_ID'] },
    { name: 'TikTok', fields: ['TIKTOK_ACCESS_TOKEN'] },
    { name: 'X', fields: ['TWITTER_API_KEY', 'TWITTER_API_SECRET'] },
    { name: 'Facebook', fields: ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID'] },
    { name: 'Pinterest', fields: ['Not wired in this build'] },
    { name: 'YouTube', fields: ['Not wired in this build'] },
    { name: 'Webhooks', fields: ['Signing secret (WP_WEBHOOK_SECRET)'] },
    { name: 'Claude API', fields: ['API key (ANTHROPIC_API_KEY)'] },
    { name: 'CDN / Media', fields: ['Not wired in this build'] },
  ];

  for (const { name, fields } of integrations) {
    test(`${name} shows its configuration requirements and status`, async ({ page }) => {
      const card = page.locator('.dsh-card').filter({ has: page.getByText(name, { exact: true }) });
      await expect(card).toHaveCount(1);
      await expect(card).toBeVisible();
      await expect(card.getByText(/^(Connected|Action needed|Not connected)$/)).toBeVisible();
      for (const field of fields) await expect(card.getByText(field, { exact: true })).toBeVisible();
      // Status fields expose configuration presence, never credential values.
      await expect(card.getByText(/^(Configured|Not configured)$/)).toHaveCount(fields.length);
    });
  }

  test('unwired services remain explicitly disconnected', async ({ page }) => {
    for (const name of ['Pinterest', 'YouTube', 'CDN / Media']) {
      const card = page.locator('.dsh-card').filter({ has: page.getByText(name, { exact: true }) });
      await expect(card.getByText('Not connected', { exact: true })).toBeVisible();
      await expect(card.getByText('Not configured', { exact: true })).toBeVisible();
    }
  });

  test('configuration inventory does not offer credential editing or simulated saving', async ({ page }) => {
    await expect(page.locator('.dsh-card input, .dsh-card textarea')).toHaveCount(0);
    await expect(page.getByRole('button', { name: /Save All|Saved/i })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'New Drop' })).toHaveAttribute('href', '/admin/collections');
  });

  test('retains the settings navigation destination', async ({ page }) => {
    const link = page.getByRole('link', { name: 'Settings', exact: true });
    await expect(link).toHaveAttribute('href', '/admin/settings');
    await link.click();
    await expect(page).toHaveURL(/\/admin\/settings$/);
    await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  });

  test('keeps the connection inventory within the viewport', async ({ page }, testInfo) => {
    const dimensions = await page.evaluate(() => ({
      content: document.documentElement.scrollWidth,
      viewport: document.documentElement.clientWidth,
    }));
    expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
    await page.screenshot({ path: testInfo.outputPath('settings-layout.png'), fullPage: true });
  });

  test('navigation has a visible focus indicator', async ({ page, isMobile }) => {
    const overview = page.getByRole('link', { name: 'Overview', exact: true });
    // iOS WebKit emulation does not implement desktop Tab-to-link traversal.
    // Exercise its focus styling directly; desktop also verifies Tab order.
    if (isMobile) await overview.focus();
    else await page.keyboard.press('Tab');
    await expect(overview).toBeFocused();
    await expect(overview).toHaveCSS('box-shadow', /rgb\(255, 255, 255\).*2px/);
  });
});
