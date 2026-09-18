import { expect, test } from '@playwright/test';

import projection from '../../data/scene-authority.json';

test.describe('Scene Authority operator flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/auth/session', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          user: { name: 'Verification Operator', email: 'operator@example.test' },
          expires: '2099-01-01T00:00:00.000Z',
        }),
      });
    });
    await page.route('**/api/console/orders-count', async route => {
      await route.fulfill({ contentType: 'application/json', body: JSON.stringify({ count: 0 }) });
    });
    await page.route('**/api/v1/agents**', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          timestamp: '2026-09-02T00:00:00.000Z',
          total_agents: 0,
          active_agents: 0,
          agents_by_category: {},
          agents: [],
        }),
      });
    });
    await page.route('**/api/scene-authority', async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: projection }),
      });
    });
  });

  test('renders independent identity, product, and execution gates', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', message => {
      if (message.type() === 'error') consoleErrors.push(message.text());
    });

    await page.goto('/admin/scene-authority');

    await expect(page.getByRole('heading', { name: 'Scene Authority', level: 1 })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Scene Authority' })).toBeVisible();

    const loveHurts = page.getByRole('article').filter({ hasText: 'LH-COMMERCE-2' });
    await expect(loveHurts).toContainText('LH-MODEL-01');
    await expect(loveHurts).toContainText('FOUNDER APPROVED IDENTITY ONLY');
    await expect(loveHurts).toContainText('HARD FAIL');
    await expect(loveHurts).toContainText('NOT AUTHORIZED');
    await expect(loveHurts.getByText('Scene input').locator('..')).toContainText('BLOCKED');
    await expect(loveHurts.getByText('Paid execution').locator('..')).toContainText('BLOCKED');
    await expect(loveHurts.getByText('Deployment').locator('..')).toContainText('NOT AUTHORIZED');
    await expect(loveHurts.getByText('Promotion requirement').locator('..')).toContainText('FOUNDER APPROVED VISUAL');
    await expect(loveHurts).toContainText('full candidate REJECT');
    await expect(loveHurts).toContainText('front-facing exact-LH-003 VTO candidate has not passed independent and founder review');

    await expect(page.getByText('Mapped scenes').locator('..').getByText('5')).toBeVisible();
    expect(consoleErrors).toEqual([]);

    await page.screenshot({
      path: 'test-results/scene-authority-desktop.png',
      fullPage: true,
    });
  });
});
