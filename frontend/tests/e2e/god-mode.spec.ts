import { expect, test, type Page } from '@playwright/test';

const run = {
  id: '550e8400-e29b-41d4-a716-446655440000', state: 'running',
  provider: 'fixture', model: 'fixture-model', mission_id: 'browser-mission',
  created_at: 1, events: [], output: null as string | null,
  verification: 'NOT_RUN', release: 'NOT_DEPLOYED',
};
const fields = ['mission_id', 'objective', 'role', 'context', 'scope', 'deliverables',
  'acceptance', 'authority', 'verification', 'recovery', 'return_contract'];
const discovery = {
  providers: [{ id: 'fixture', default_model: 'fixture-model', models: ['fixture-model'],
    enabled: true, configured: true, authenticated: false, execution_protocol: 'json-actions-v1' }],
  tools: ['fixture_read'], paid_execution_enabled: true,
};

async function prepare(page: Page) {
  await page.route('**/api/auth/session', route => route.fulfill({json: {
    user: {name: 'Test operator', email: 'test@example.invalid', backendSubject: 'browser-owner'}, expires: '2099-01-01T00:00:00Z',
  }}));
  await page.route('**/api/console/orders-count', route => route.fulfill({json: {count: 0}}));
  await page.route('**/api/platform/api/v1/agents**', route => route.fulfill({json: {agents: []}}));
  await page.route('**/api/platform/api/v1/orchestration/god-mode/providers', route => route.fulfill({json: discovery}));
}

async function fillMission(page: Page) {
  await page.goto('/admin/god-mode');
  await page.getByRole('combobox', {name: 'Provider', exact: true}).selectOption('fixture');
  await page.getByRole('combobox', {name: 'Model', exact: true}).selectOption('fixture-model');
  for (const field of fields) {
    await page.getByLabel(field.replaceAll('_', ' '), {exact: true}).fill(
      field === 'mission_id' ? 'browser-mission' : 'Concrete ' + field + ' for fixture verification',
    );
  }
  await page.getByLabel('fixture_read', {exact: true}).check();
  await expect(page.getByRole('button', {name: 'Run mission', exact: true})).toBeDisabled();
  await page.getByLabel('I authorize paid execution', {exact: false}).check();
}

test.beforeEach(async ({page}) => prepare(page));

test('executes the chosen mission once and renders a receipt at both viewport sizes', async ({page}, info) => {
  let submissions = 0;
  await page.route('**/api/platform/api/v1/orchestration/god-mode/runs', async route => {
    submissions++;
    const request = route.request();
    expect(request.headers()['authorization']).toBeUndefined();
    expect(new URL(request.url()).pathname).toContain('/api/platform/api/v1/');
    expect(request.headers()['idempotency-key']).toBeTruthy();
    expect(request.postDataJSON()).toMatchObject({
      provider: 'fixture', model: 'fixture-model', tools: ['fixture_read'], authorize_paid: true,
      max_calls: 3, max_output_tokens: 2048, timeout_seconds: 120, max_cost_usd: 0.25,
    });
    expect(Object.keys(request.postDataJSON().mission)).toEqual(fields);
    await route.fulfill({status: 202, json: run});
  });
  await page.route('**/api/platform/api/v1/orchestration/god-mode/runs/*', route => route.fulfill({
    json: {...run, state: 'completed', output: '<script>unsafe()</script> Verified fixture deliverable'},
  }));
  await fillMission(page);
  await page.getByRole('button', {name: 'Run mission', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Mission: completed'})).toBeVisible();
  await expect(page.getByText('Verification: NOT_RUN · Release: NOT_DEPLOYED')).toBeVisible();
  await expect(page.locator('pre')).toContainText('<script>unsafe()</script>');
  expect(submissions).toBe(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({path: info.outputPath('completed.png'), fullPage: true});
});

test('reload and retry preserve the original request after an ambiguous failure', async ({page}) => {
  const sent: {key: string; body: string | null}[] = [];
  await page.route('**/api/platform/api/v1/orchestration/god-mode/runs', async route => {
    sent.push({key: route.request().headers()['idempotency-key'], body: route.request().postData()});
    await route.fulfill(sent.length === 1 ? {status: 503, json: {detail: 'Receipt lost'}} :
      {status: 202, json: {...run, state: 'completed', output: 'Recovered original run'}});
  });
  await fillMission(page);
  await page.getByRole('button', {name: 'Run mission', exact: true}).click();
  await expect(page.getByRole('button', {name: 'Retry same submission'})).toBeVisible();
  await page.reload();
  await page.getByRole('button', {name: 'Retry same submission'}).click();
  await expect(page.getByRole('heading', {name: 'Mission: completed'})).toBeVisible();
  expect(sent).toHaveLength(2);
  expect(sent[1]).toEqual(sent[0]);
});

test('requests cancellation without dispatching another mission', async ({page}) => {
  let submissions = 0;
  let cancellations = 0;
  await page.route('**/api/platform/api/v1/orchestration/god-mode/runs', async route => {
    submissions++;
    await route.fulfill({status: 202, json: run});
  });
  await page.route('**/api/platform/api/v1/orchestration/god-mode/runs/*', route => route.fulfill({json: run}));
  await page.route('**/api/platform/api/v1/orchestration/god-mode/runs/*/cancel', async route => {
    cancellations++;
    await route.fulfill({json: {...run, state: 'cancel_requested'}});
  });
  await fillMission(page);
  await page.getByRole('button', {name: 'Run mission', exact: true}).click();
  await page.getByRole('button', {name: 'Request cancellation'}).click();
  await expect(page.getByRole('heading', {name: 'Mission: cancel_requested'})).toBeVisible();
  await expect(page.getByText('The current provider call may still finish and incur cost.')).toBeVisible();
  expect(submissions).toBe(1); expect(cancellations).toBe(1);
});
