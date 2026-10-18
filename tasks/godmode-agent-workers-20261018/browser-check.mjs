import { createRequire } from 'node:module';
import { createHmac, randomUUID } from 'node:crypto';
import { writeFileSync } from 'node:fs';
const require = createRequire('/Users/theceo/DevSkyy/frontend/package.json');
const { chromium } = require('@playwright/test');
const { encode } = require('next-auth/jwt');
const origin = 'http://localhost:3107';
const destination = '/Users/theceo/DevSkyy/tasks/godmode-agent-workers-20261018';
const secret = 'god-mode-synthetic-local-fixture-signing-20261018-key';
function backendToken(sub) {
  const now = Math.floor(Date.now() / 1000);
  const parts = [
    { alg: 'HS512', typ: 'JWT' },
    {
      sub,
      jti: randomUUID(),
      type: 'access',
      roles: ['admin'],
      iss: 'devskyy-platform',
      aud: 'devskyy-api',
      iat: now,
      exp: now + 1800,
    },
  ].map(x => Buffer.from(JSON.stringify(x)).toString('base64url'));
  return [...parts, createHmac('sha512', secret).update(parts.join('.')).digest('base64url')].join('.');
}
const browser = await chromium.launch({ headless: true, channel: 'chrome' });
async function signedContext(actor) {
  const context = await browser.newContext();
  const token = await encode({
    secret: 'godmode-local-ui-fixture-only-20261018',
    token: { sub: actor, email: actor + '@example.invalid', accessToken: backendToken(actor) },
    maxAge: 3600,
  });
  await context.addCookies([
    { name: 'next-auth.session-token', value: token, url: origin, httpOnly: true, sameSite: 'Lax' },
  ]);
  return context;
}
const anonymous = await browser.newContext();
const denial = await anonymous.request.get(origin + '/api/admin/god-mode/runtime/status');
const context = await signedContext('owner-local-fixture');
async function api(path, body) {
  const response =
    body === undefined
      ? await context.request.get(origin + '/api/admin/god-mode/runtime/' + path)
      : await context.request.post(origin + '/api/admin/god-mode/runtime/' + path, {
          data: body,
          headers: { Origin: origin },
        });
  return { status: response.status(), body: await response.json() };
}
const health = await api('status');
if (health.status !== 200) throw Error(JSON.stringify(health));
const page = await context.newPage();
const errors = [];
page.on('pageerror', e => errors.push(e.message));
await page.setViewportSize({ width: 1440, height: 1000 });
await page.goto(origin + '/admin/god-mode');
await page.getByText('Connected · local_allowlisted', { exact: true }).waitFor({ timeout: 30000 });
await page
  .getByLabel('Memory note', { exact: true })
  .fill(
    'LOCAL TEST FIXTURE: preserve current artwork and silent website requirements. This note grants no permission.'
  );
await page
  .getByLabel('Source / provenance', { exact: true })
  .fill('Synthetic local integration test; not founder acceptance');
const memoryResponse = page.waitForResponse(
  r => r.url().endsWith('/runtime/memory') && r.request().method() === 'POST'
);
await page.getByRole('button', { name: 'Save memory note', exact: true }).click();
const memorySaved = await memoryResponse;
if (memorySaved.status() !== 201) throw Error('Memory save failed: ' + (await memorySaved.text()));
await page.getByRole('button', { name: 'Owner: accept this memory', exact: true }).first().waitFor();
const memories = await api('memory?project=skyyrose');
const note = memories.body.records[0];
await page.getByRole('button', { name: 'Owner: accept this memory', exact: true }).first().click();
await page
  .getByText(/OWNER_ACCEPTED/)
  .first()
  .waitFor();
await page.getByLabel('Allowlisted workflow', { exact: true }).selectOption('campaign-readiness');
const createdResponse = page.waitForResponse(r => r.url().endsWith('/runtime/runs') && r.request().method() === 'POST');
await page.getByRole('button', { name: 'Create reviewable plan', exact: true }).click();
const created = await (await createdResponse).json();
const beforeApproval = await api(`runs/${created.id}/execute`, { plan_hash: created.plan_hash });
await page.getByRole('button', { name: 'Approve this exact plan', exact: true }).click();
await page.getByRole('button', { name: 'Execute approved plan', exact: true }).waitFor({ state: 'visible' });
await page.getByRole('button', { name: 'Execute approved plan', exact: true }).click();
await page.getByText(/^SUCCEEDED ·/).waitFor({ timeout: 180000 });
const result = await api('runs/' + created.id);
if (result.body.status !== 'SUCCEEDED') throw Error(JSON.stringify(result));
const replay = await api(`runs/${created.id}/execute`, { plan_hash: created.plan_hash });
const selfReview = await api(`runs/${created.id}/review`, {
  plan_hash: created.plan_hash,
  artifact_hash: result.body.artifact_hash,
  verdict: 'PASS',
  notes: 'Synthetic gate test',
});
await page.getByRole('heading', { name: 'Run the Fashion Theme Team', exact: true }).scrollIntoViewIfNeeded();
await page.screenshot({ path: destination + '/execution-desktop.png', fullPage: true });
await page.screenshot({ path: destination + '/execution-preview.png' });
const desktopOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
await page.setViewportSize({ width: 375, height: 812 });
await page.screenshot({ path: destination + '/execution-mobile.png', fullPage: true });
const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
const receipt = {
  agentWorkers: health.body.agent_workers,
  evidence_class: 'REPRODUCED_LOCAL',
  authentication: 'SYNTHETIC_LOCAL_SESSION_AND_SIGNED_JWT_ONLY',
  scope:
    'Real browser→NextAuth proxy→loopback FastAPI→actual fixed registry/campaign verifiers on fixture database; no real-account login or founder approval',
  anonymousStatus: denial.status(),
  runtimeStatus: health.status,
  runId: created.id,
  planHash: created.plan_hash,
  beforeApprovalStatus: beforeApproval.status,
  finalStatus: result.body.status,
  steps: result.body.steps.map(s => ({
    id: s.id,
    status: s.status,
    exit_code: s.exit_code,
    artifact_sha256: s.artifact_sha256,
    output_sha256: s.output_sha256,
  })),
  approvalReplayStatus: replay.status,
  selfReviewStatus: selfReview.status,
  memoryId: note.id,
  ownerAcceptedMemorySnapshotCount:
    result.body.plan.memory_context?.length ?? result.body.plan.accepted_memory?.length ?? null,
  desktopOverflow,
  mobileOverflow,
  pageErrors: errors,
};
writeFileSync(destination + '/browser-execution-receipt.json', JSON.stringify(receipt, null, 2) + '\n');
writeFileSync(destination + '/actual-run-receipt.json', JSON.stringify(result.body, null, 2) + '\n');
console.log(JSON.stringify(receipt, null, 2));
await browser.close();
