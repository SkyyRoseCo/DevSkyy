import { MEMORY_CONTENT_LIMIT, MEMORY_PROVENANCE_LIMIT, MEMORY_QUERY_LIMIT, memoryTimestamp } from './runtime-state';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
  RuntimeOperations,
  applyRunResult,
  canExecute,
  needsPolling,
  runtimeError,
  type RuntimeRun,
} from './runtime-state';
const fixture: RuntimeRun = {
  id: 'run-1',
  project: 'skyyrose',
  workflow: 'source-audit',
  status: 'PENDING_APPROVAL',
  plan_hash: 'abc',
  plan: {},
  approval: null,
  steps: [],
  events: [],
};
test('execution requires backend approved state and approval receipt', () => {
  assert.equal(canExecute(fixture), false);
  assert.equal(canExecute({ ...fixture, status: 'APPROVED' }), false);
  assert.equal(canExecute({ ...fixture, status: 'APPROVED', approval: { plan_hash: 'abc' } }), true);
  for (const status of ['SUCCEEDED', 'CANCELLED', 'INVALIDATED', 'FAILED', 'RUNNING'])
    assert.equal(canExecute({ ...fixture, status, approval: {} }), false);
});
test('only actual backend running state is polled', () => {
  assert.equal(needsPolling({ ...fixture, status: 'RUNNING' }), true);
  assert.equal(needsPolling(fixture), false);
  assert.equal(needsPolling({ ...fixture, status: 'SUCCEEDED' }), false);
});
test('authentication and HTTP errors retain actionable messages', () => {
  assert.equal(runtimeError(new Error('401: Sign in again')), '401: Sign in again');
  assert.match(runtimeError(null), /Retry the connection/);
});
test('proxy is authenticated and cannot launch a local shell', () => {
  const route = readFileSync(new URL('../../api/admin/god-mode/runtime/[[...path]]/route.ts', import.meta.url), 'utf8');
  assert.match(route, /withAuth<RouteContext>/);
  assert.match(route, /proxyGodModeRuntime\(request, path\)/);
  assert.doesNotMatch(route, /child_process|execSync|spawn\(/);
});
test('workspace keeps approval, artifact evidence and memory trust explicit', () => {
  const source = readFileSync(new URL('./runtime-workspace.tsx', import.meta.url), 'utf8');
  assert.match(source, /Approve this exact plan/);
  assert.match(source, /plan_hash: run.plan_hash/);
  assert.match(source, /connection\?\.can_approve !== true/);
  assert.match(source, /Step results and artifact evidence/);
  assert.match(source, /note.trust/);
  assert.doesNotMatch(source, /localStorage|sessionStorage|setTimeout.*SUCCEEDED/);
});

test('UI transport fails closed on backend authentication and disconnected runtime', async () => {
  const { godModeRequest } = await import('../../../lib/api/god-mode-runtime');
  const original = globalThis.fetch;
  try {
    for (const status of [401, 403, 503]) {
      globalThis.fetch = async () => new Response(JSON.stringify({ error: `runtime-${status}` }), { status });
      await assert.rejects(godModeRequest('status'), new RegExp(`runtime-${status}`));
    }
  } finally {
    globalThis.fetch = original;
  }
});

test('UI sends exact plan approval without client actor or role claims', async () => {
  const { godModeRequest } = await import('../../../lib/api/god-mode-runtime');
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async (path, init) => {
      assert.equal(path, '/api/admin/god-mode/runtime/runs/run-1/approve');
      assert.equal(init?.credentials, 'same-origin');
      assert.equal(init?.method, 'POST');
      assert.deepEqual(JSON.parse(String(init?.body)), { plan_hash: 'abc' });
      return new Response(JSON.stringify({ ...fixture, status: 'APPROVED', approval: { plan_hash: 'abc' } }));
    };
    const result = await godModeRequest<RuntimeRun>('runs/run-1/approve', {
      method: 'POST',
      body: JSON.stringify({ plan_hash: 'abc' }),
    });
    assert.equal(result.status, 'APPROVED');
  } finally {
    globalThis.fetch = original;
  }
});

test('memory limits and Unix-second timestamps match the backend contract', () => {
  assert.equal(MEMORY_CONTENT_LIMIT, 8000);
  assert.equal(MEMORY_PROVENANCE_LIMIT, 500);
  assert.equal(MEMORY_QUERY_LIMIT, 200);
  assert.equal(memoryTimestamp(0), '1970-01-01 00:00:00.000 UTC');
  assert.equal(memoryTimestamp(Number.NaN), 'Timestamp unavailable');
  const source = readFileSync(new URL('./runtime-workspace.tsx', import.meta.url), 'utf8');
  assert.match(source, /memoryTimestamp\(note.created\)/);
  assert.doesNotMatch(source, /note.created_at|maxLength=\{12000\}|maxLength=\{2000\}/);
});

test('deferred execution retains selection lock after same-run cancellation completes', async () => {
  const operations = new RuntimeOperations();
  let current: RuntimeRun | null = { ...fixture, status: 'APPROVED', approval: {} };
  let resolveExecution!: (value: RuntimeRun) => void;
  const deferred = new Promise<RuntimeRun>(resolve => {
    resolveExecution = resolve;
  });
  const execution = operations.begin('execute', fixture.id)!;
  const pending = deferred.then(result => {
    current = applyRunResult(current, fixture.id, result, true);
    operations.finish(execution);
  });
  const cancellation = operations.begin('cancel', fixture.id)!;
  assert.ok(cancellation);
  current = applyRunResult(current, fixture.id, { ...fixture, status: 'CANCELLED' }, true);
  operations.finish(cancellation);
  assert.equal(operations.executingRunId, fixture.id);
  assert.equal(operations.busy, 'execute');
  assert.equal(operations.begin('plan', null), null);
  assert.equal(operations.begin('load run', 'run-2'), null);
  assert.equal(operations.begin('cancel', 'run-2'), null);
  resolveExecution({ ...fixture, status: 'CANCELLED' });
  await pending;
  assert.equal(operations.executingRunId, null);
  assert.equal(operations.busy, null);
  const selection = operations.begin('load run', 'run-2');
  assert.ok(selection);
  current = { ...fixture, id: 'run-2' };
  assert.equal(applyRunResult(current, fixture.id, { ...fixture, status: 'SUCCEEDED' }, true)?.id, 'run-2');
  assert.equal(applyRunResult(current, 'run-2', { ...current, status: 'SUCCEEDED' }, false), current);
});

test('catalog controls availability without treating configured adapters as live-qualified', async () => {
  const { workflowEnabled } = await import('./runtime-state');
  const workflow = {
    id: 'fashion-campaign-analysis',
    title: 'Campaign analysis',
    description: '',
    approval_required: true,
    steps: [],
  };
  assert.equal(workflowEnabled(undefined), false);
  assert.equal(workflowEnabled(workflow), false);
  assert.equal(workflowEnabled({ ...workflow, enabled: false, unavailable_reason: 'Adapter unavailable' }), false);
  assert.equal(workflowEnabled({ ...workflow, enabled: true }), true);
  for (const id of ['source-audit', 'campaign-readiness', 'fashion-verification']) {
    assert.equal(workflowEnabled({ ...workflow, id }), true);
    assert.equal(workflowEnabled({ ...workflow, id, enabled: false }), false);
  }
  const source = readFileSync(new URL('./runtime-workspace.tsx', import.meta.url), 'utf8');
  assert.match(source, /connection\.agent_workers\.main_worker/);
  assert.match(source, /connection\.agent_workers\.independent_reviewer/);
  assert.match(source, /selected.unavailable_reason/);
  assert.match(source, /disabled=\{!available \|\| !workflowEnabled\(selected\) \|\| locked\}/);
  assert.match(source, /if \(!workflowEnabled\(selected\)\) return/);
  assert.match(source, /Configuration is separate from live qualification/);
  assert.doesNotMatch(source, /set.*model|set.*engine|bypassPermissions/);
});

test('machine review summary preserves receipt verdict, findings and reviewed artifact binding', async () => {
  const { stepSummaries } = await import('./runtime-state');
  assert.deepEqual(
    stepSummaries([
      null,
      {},
      'invalid',
      { id: 'claude-worker', status: 'PASSED', artifact: { arbitrary: 'not a verdict' } },
      {
        id: 'codex-reviewer',
        status: 'PASSED',
        artifact: {
          verdict: 'FAIL',
          findings: [{ reason: 'coverage gap' }],
          worker_artifact_sha256: 'source-bound-hash',
        },
      },
    ]),
    [
      { id: 'claude-worker', status: 'PASSED' },
      { id: 'codex-reviewer', status: 'PASSED', verdict: 'FAIL', findings: 1, workerArtifactHash: 'source-bound-hash' },
    ]
  );
  const source = readFileSync(new URL('./runtime-workspace.tsx', import.meta.url), 'utf8');
  assert.match(source, /Machine review does not grant human acceptance/);
  assert.match(source, /Machine verdict: \{step.verdict\}/);
});
