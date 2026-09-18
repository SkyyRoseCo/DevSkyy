import { expect, test } from '@playwright/test'

test.describe('Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/SkyyRose|DevSkyy/)
  })

  test('collections page loads', async ({ page }) => {
    // No console errors
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/collections')
    await expect(page.getByRole('heading', { name: 'Collections', exact: true })).toBeVisible()
    await page.waitForTimeout(2000)
    expect(errors.filter((e) => !e.includes('favicon'))).toHaveLength(0)
  })

  test('login page loads', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('body')).toBeVisible()
  })

  test('pre-order page loads', async ({ page }) => {
    await page.goto('/pre-order')
    await expect(page.locator('body')).toBeVisible()
  })

  test('checkout page loads', async ({ page }) => {
    await page.goto('/checkout')
    await expect(page.locator('body')).toBeVisible()
  })

  test('collection detail pages load', async ({ page }) => {
    for (const slug of ['signature', 'black-rose', 'love-hurts']) {
      await page.goto(`/collections/${slug}`)
      await expect(page.locator('body')).toBeVisible()
    }
  })

  test('wiring health details require authentication', async ({ request }) => {
    const response = await request.get('/api/health')
    // This route probes authenticated WP/WC wiring, not a public liveness URL.
    expect(response.status()).toBe(401)
    await expect(response.json()).resolves.toMatchObject({ error: 'Unauthorized' })
  })
})

test.describe('Mobile Responsive', () => {
  test('homepage renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/')
    await expect(page.locator('body')).toBeVisible()
  })
})
