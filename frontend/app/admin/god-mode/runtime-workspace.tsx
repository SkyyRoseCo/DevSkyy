'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import { godModeRequest } from '@/lib/api/god-mode-runtime';
import {
  RuntimeOperations,
  applyRunResult,
  MEMORY_CONTENT_LIMIT,
  MEMORY_PROVENANCE_LIMIT,
  MEMORY_QUERY_LIMIT,
  memoryTimestamp,
  canExecute,
  needsPolling,
  runtimeError,
  workflowEnabled,
  stepSummaries,
  type RuntimeMemory,
  type RuntimeRun,
  type RuntimeStatus,
  type RuntimeWorkflow,
} from './runtime-state';

const box = 'rounded-xl border border-white/10 bg-[#101014] p-5 sm:p-6';
const input =
  'w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-[#D7A3AB]';
const button =
  'rounded-lg border border-[#D7A3AB]/40 px-4 py-2 text-sm text-[#EDC9CE] disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-[#D7A3AB]';
const project = 'skyyrose';
function Evidence({ title, value }: { title: string; value: unknown }) {
  return (
    <details className='mt-3 rounded-lg border border-white/10 p-3'>
      <summary className='cursor-pointer text-sm text-[#EDC9CE]'>{title}</summary>
      <pre className='mt-3 max-h-80 overflow-auto whitespace-pre-wrap break-all text-xs leading-5 text-[#B7B7C2]'>
        {JSON.stringify(value, null, 2)}
      </pre>
    </details>
  );
}

export default function RuntimeWorkspace() {
  const [connection, setConnection] = useState<RuntimeStatus | null>(null);
  const [workflows, setWorkflows] = useState<RuntimeWorkflow[]>([]);
  const [runs, setRuns] = useState<RuntimeRun[]>([]);
  const [run, setRun] = useState<RuntimeRun | null>(null);
  const [memory, setMemory] = useState<RuntimeMemory[]>([]);
  const [workflow, setWorkflow] = useState('');
  const [query, setQuery] = useState('');
  const [content, setContent] = useState('');
  const [provenance, setProvenance] = useState('');
  const [kind, setKind] = useState('observation');
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewVerdict, setReviewVerdict] = useState('FAIL');
  const [busy, setBusy] = useState<string | null>(null);
  const [executingRunId, setExecutingRunId] = useState<string | null>(null);
  const operations = useRef(new RuntimeOperations());
  const locked = !!busy || executingRunId !== null;
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const active = useRef(true);
  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const status = await godModeRequest<RuntimeStatus>('status');
      const [catalog, history, notes] = await Promise.all([
        godModeRequest<{ workflows: RuntimeWorkflow[] }>('workflows'),
        godModeRequest<{ runs: RuntimeRun[] }>(`runs?project=${project}`),
        godModeRequest<{ records: RuntimeMemory[] }>(`memory?project=${project}`),
      ]);
      if (!active.current) return;
      setConnection(status);
      setWorkflows(catalog.workflows);
      setRuns(history.runs);
      setMemory(notes.records);
      setWorkflow(current => current || catalog.workflows[0]?.id || '');
    } catch (failure) {
      if (active.current) {
        setConnection(null);
        setError(runtimeError(failure));
      }
    } finally {
      if (active.current) setLoading(false);
    }
  }, []);
  useEffect(() => {
    active.current = true;
    void load();
    return () => {
      active.current = false;
    };
  }, [load]);
  useEffect(() => {
    if (!run || (!needsPolling(run) && executingRunId !== run.id)) return;
    const id = run.id;
    const timer = setInterval(() => {
      void godModeRequest<RuntimeRun>(`runs/${encodeURIComponent(id)}`)
        .then(result => {
          setRun(current => applyRunResult(current, id, result, active.current));
        })
        .catch(failure => {
          if (active.current) setError(runtimeError(failure));
        });
    }, 2500);
    return () => clearInterval(timer);
  }, [run, executingRunId]);
  async function act(label: string, task: () => Promise<void>) {
    const token = operations.current.begin(label, run?.id || null);
    if (!token || !active.current) return;
    setBusy(operations.current.busy);
    setExecutingRunId(operations.current.executingRunId);
    setError(null);
    setMessage('');
    try {
      await task();
    } catch (failure) {
      if (active.current) setError(runtimeError(failure));
    } finally {
      operations.current.finish(token);
      if (active.current) {
        setBusy(operations.current.busy);
        setExecutingRunId(operations.current.executingRunId);
      }
    }
  }
  function updateRunResult(id: string, result: RuntimeRun) {
    setRun(current => applyRunResult(current, id, result, active.current));
  }
  async function mutate(path: string, body: unknown) {
    return godModeRequest<RuntimeRun>(path, { method: 'POST', body: JSON.stringify(body) });
  }
  const available = connection?.status === 'connected';
  const selected = workflows.find(item => item.id === workflow);
  return (
    <section className={box} aria-labelledby='runtime-heading'>
      <div className='flex flex-wrap items-center justify-between gap-3'>
        <div>
          <p className='font-mono text-xs uppercase tracking-widest text-[#D7A3AB]'>Live mission control</p>
          <h2 id='runtime-heading' className='mt-2 text-xl font-semibold text-white'>
            Run the Fashion Theme Team
          </h2>
        </div>
        <button type='button' className={button} disabled={loading || locked} onClick={() => void load()}>
          Refresh connection
        </button>
      </div>
      <p role='status' aria-live='polite' className='mt-4 text-sm text-[#CAC5D1]'>
        {loading
          ? 'Checking the authenticated runtime…'
          : available
            ? `Connected · ${connection.runtime}`
            : 'Runtime unavailable. Execution is disabled.'}
      </p>
      <p className='mt-2 text-xs leading-6 text-[#B7B7C2]'>
        Plans require explicit approval of their exact hash. Local workflow execution, independent review, founder
        acceptance and publication remain separate gates.
      </p>
      {error && (
        <p role='alert' className='mt-4 break-words rounded-lg border border-red-400/40 p-3 text-sm text-red-200'>
          {error}
        </p>
      )}
      {message && (
        <p role='status' className='mt-3 text-sm text-[#EDC9CE]'>
          {message}
        </p>
      )}
      {connection?.agent_workers && (
        <div className='mt-4 rounded-lg border border-[#D7A3AB]/25 p-4'>
          <h3 className='text-sm font-semibold text-white'>GOD MODE worker routing</h3>
          <dl className='mt-3 grid gap-3 sm:grid-cols-2'>
            {(
              [
                ['Main worker', connection.agent_workers.main_worker],
                ['Independent machine reviewer', connection.agent_workers.independent_reviewer],
              ] as const
            ).map(([role, engine]) => (
              <div key={role} className='min-w-0'>
                <dt className='text-xs text-[#B7B7C2]'>{role}</dt>
                <dd className='mt-1 break-words text-sm text-white'>{engine.engine}</dd>
                <dd className='mt-1 break-words font-mono text-xs text-[#D7A3AB]'>{engine.state}</dd>
                {engine.model && <dd className='mt-1 break-words text-xs text-[#B7B7C2]'>Model: {engine.model}</dd>}
                {engine.reason && <dd className='mt-1 break-words text-xs text-[#B7B7C2]'>{engine.reason}</dd>}
              </div>
            ))}
          </dl>
          <p className='mt-3 break-words text-xs leading-6 text-[#B7B7C2]'>
            Scope: {connection.agent_workers.scope}. Configuration is separate from live qualification. Approvals and
            accepted project memory remain in GOD MODE. Machine review does not grant human acceptance.
          </p>
          <p className='text-xs leading-6 text-[#B7B7C2]'>
            Production execution:{' '}
            {connection.agent_workers.production_enabled
              ? 'Reported enabled by runtime — inspect scope and gates.'
              : 'Disabled'}
          </p>
        </div>
      )}
      {connection && <Evidence title='Runtime permissions and limits' value={connection} />}
      <div className='mt-6 grid gap-6 xl:grid-cols-2'>
        <div className='min-w-0 space-y-4'>
          <label className='block text-sm text-white' htmlFor='workflow-select'>
            Allowlisted workflow
          </label>
          <select
            id='workflow-select'
            className={input}
            value={workflow}
            disabled={!available || locked}
            onChange={event => setWorkflow(event.target.value)}
          >
            {workflows.map(item => (
              <option key={item.id} value={item.id}>
                {item.title}
                {workflowEnabled(item) ? '' : ' — unavailable'}
              </option>
            ))}
          </select>
          {selected && (
            <>
              <p className='text-sm leading-6 text-[#B7B7C2]'>{selected.description}</p>
              {!workflowEnabled(selected) && (
                <p role='status' className='text-sm leading-6 text-amber-200'>
                  {selected.unavailable_reason ||
                    'This workflow is unavailable. Refresh the runtime for qualification details.'}
                </p>
              )}
              <ol className='space-y-2'>
                {selected.steps.map(step => (
                  <li key={step.id} className='rounded-lg border border-white/10 p-3 text-sm text-white'>
                    {step.title}
                    <p className='mt-1 text-xs text-[#B7B7C2]'>
                      Owner: {step.owner} · Verifier: {step.verifier}
                    </p>
                  </li>
                ))}
              </ol>
            </>
          )}
          <button
            className={button}
            disabled={!available || !workflowEnabled(selected) || locked}
            onClick={() =>
              void act('plan', async () => {
                if (!workflowEnabled(selected)) return;
                const result = await mutate('runs', { project, workflow, idempotency_key: crypto.randomUUID() });
                if (!active.current) return;
                setRun(result);
                setRuns(current => [result, ...current.filter(item => item.id !== result.id)]);
              })
            }
          >
            {busy === 'plan' ? 'Preparing plan…' : 'Create reviewable plan'}
          </button>
          <label className='block text-sm text-white' htmlFor='run-select'>
            Saved runs
          </label>
          <select
            id='run-select'
            className={input}
            value={run?.id || ''}
            disabled={!available || locked}
            onChange={event => {
              const id = event.target.value;
              if (id)
                void act('load run', async () => {
                  const result = await godModeRequest<RuntimeRun>(`runs/${encodeURIComponent(id)}`);
                  if (active.current) setRun(result);
                });
            }}
          >
            <option value=''>Select a run</option>
            {runs.map(item => (
              <option key={item.id} value={item.id}>
                {item.workflow} · {item.id.slice(0, 8)}
              </option>
            ))}
          </select>
          {run && (
            <div className='min-w-0 rounded-xl border border-[#D7A3AB]/25 p-4'>
              <h3 className='text-lg text-white'>{run.workflow}</h3>
              <p className='mt-2 break-all font-mono text-xs text-[#D7A3AB]'>
                {run.status} · {run.id}
              </p>
              <p className='mt-3 break-all text-xs text-[#B7B7C2]'>Plan SHA-256: {run.plan_hash}</p>
              <Evidence title='Inspect the exact plan before approval' value={run.plan} />
              <div className='mt-4 flex flex-wrap gap-2'>
                <button
                  className={button}
                  disabled={
                    !available || locked || run.status !== 'PENDING_APPROVAL' || connection?.can_approve !== true
                  }
                  onClick={() =>
                    void act('approve', async () =>
                      updateRunResult(run.id, await mutate(`runs/${run.id}/approve`, { plan_hash: run.plan_hash }))
                    )
                  }
                >
                  Approve this exact plan
                </button>
                <button
                  className={button}
                  disabled={!available || locked || !canExecute(run)}
                  onClick={() =>
                    void act('execute', async () => {
                      const id = run.id;
                      updateRunResult(id, await mutate(`runs/${id}/execute`, { plan_hash: run.plan_hash }));
                      if (!active.current) return;
                      setMessage(
                        'Execution returned. Inspect the recorded step evidence and separate review gates below.'
                      );
                    })
                  }
                >
                  {busy === 'execute' ? 'Executing approved workflow…' : 'Execute approved plan'}
                </button>
                <button
                  className={button}
                  disabled={
                    !available ||
                    busy === 'cancel' ||
                    (locked && executingRunId !== run.id) ||
                    !['PENDING_APPROVAL', 'APPROVED', 'RUNNING'].includes(run.status)
                  }
                  onClick={() =>
                    void act('cancel', async () => updateRunResult(run.id, await mutate(`runs/${run.id}/cancel`, {})))
                  }
                >
                  Cancel run
                </button>
              </div>
              {connection?.can_approve !== true && (
                <p className='mt-3 text-xs text-[#B7B7C2]'>Plan approval requires an authorized owner account.</p>
              )}
              {run.status === 'SUCCEEDED' && run.artifact_hash && (
                <form
                  className='mt-4 space-y-3 rounded-lg border border-white/10 p-3'
                  onSubmit={event => {
                    event.preventDefault();
                    void act('review', async () => {
                      updateRunResult(
                        run.id,
                        await mutate(`runs/${run.id}/review`, {
                          plan_hash: run.plan_hash,
                          artifact_hash: run.artifact_hash,
                          verdict: reviewVerdict,
                          notes: reviewNotes,
                        })
                      );
                      if (active.current) setReviewNotes('');
                    });
                  }}
                >
                  <h4 className='text-sm font-semibold text-white'>Independent artifact review</h4>
                  <p className='text-xs leading-6 text-[#B7B7C2]'>
                    Requires a different authorized reviewer from the plan submitter, approver and executor. The server
                    checks identity and exact artifact hashes. This review does not publish or accept creative work on
                    your behalf.
                  </p>
                  <label className='block text-sm text-white' htmlFor='review-verdict'>
                    Verdict
                  </label>
                  <select
                    id='review-verdict'
                    className={input}
                    value={reviewVerdict}
                    onChange={event => setReviewVerdict(event.target.value)}
                  >
                    <option value='FAIL'>FAIL — changes required</option>
                    <option value='PASS'>PASS — inspected evidence</option>
                  </select>
                  <label className='block text-sm text-white' htmlFor='review-notes'>
                    Review evidence and observations
                  </label>
                  <textarea
                    id='review-notes'
                    className={input}
                    rows={3}
                    maxLength={4000}
                    required
                    value={reviewNotes}
                    onChange={event => setReviewNotes(event.target.value)}
                  />
                  <button
                    className={button}
                    disabled={!available || locked || connection?.can_approve !== true || !reviewNotes.trim()}
                  >
                    Record independent review
                  </button>
                </form>
              )}
              <div className='mt-4 rounded-lg border border-white/10 p-3'>
                <h4 className='text-sm font-semibold text-white'>Recorded workflow results</h4>
                <ul className='mt-2 space-y-2 text-xs leading-6 text-[#B7B7C2]'>
                  {stepSummaries(run.steps).map((step, index) => (
                    <li key={`${step.id}-${index}`} className='break-words'>
                      <span className='text-white'>{step.id}</span>: {step.status}
                      {step.verdict && <span> · Machine verdict: {step.verdict}</span>}
                      {step.findings !== undefined && <span> · Findings: {step.findings}</span>}
                      {step.workerArtifactHash && (
                        <p className='break-all'>Reviewed worker artifact SHA-256: {step.workerArtifactHash}</p>
                      )}
                    </li>
                  ))}
                </ul>
                {run.steps.length === 0 && <p className='mt-2 text-xs text-[#B7B7C2]'>No recorded step results yet.</p>}
                <p className='mt-3 text-xs leading-6 text-[#B7B7C2]'>
                  A Codex machine verdict is separate from the authorized human artifact review, founder acceptance and
                  release. Inspect the full receipts before advancing.
                </p>
              </div>
              <Evidence title='Independent review receipts' value={run.reviews || []} />
              <Evidence title='Step results and artifact evidence' value={run.steps} />
              <Evidence title='Audit events' value={run.events} />
              <Evidence title='Approval and remaining gates' value={run} />
            </div>
          )}
        </div>
        <div className='min-w-0'>
          <h3 className='text-lg font-semibold text-white'>Project memory</h3>
          <p className='mt-2 text-xs leading-6 text-[#B7B7C2]'>
            SkyyRose scope. Notes retain provenance and trust. Owner promotion records acceptance; memory never replaces
            the product registry or grants execution approval.
          </p>
          <form
            className='mt-4 flex gap-2'
            onSubmit={event => {
              event.preventDefault();
              void act('search', async () => {
                const result = await godModeRequest<{ records: RuntimeMemory[] }>(
                  `memory?project=${project}&query=${encodeURIComponent(query)}`
                );
                if (active.current) setMemory(result.records);
              });
            }}
          >
            <label className='sr-only' htmlFor='memory-search'>
              Search project memory
            </label>
            <input
              id='memory-search'
              maxLength={MEMORY_QUERY_LIMIT}
              className={input}
              value={query}
              onChange={event => setQuery(event.target.value)}
              placeholder='Search decisions and handoffs'
            />
            <button className={button} disabled={!available || locked}>
              Search
            </button>
          </form>
          <form
            className='mt-5 space-y-3'
            onSubmit={event => {
              event.preventDefault();
              void act('save note', async () => {
                const note = await godModeRequest<RuntimeMemory>('memory', {
                  method: 'POST',
                  body: JSON.stringify({ project, kind, content, provenance }),
                });
                if (!active.current) return;
                setMemory(current => [note, ...current]);
                setContent('');
                setProvenance('');
                setMessage('Memory saved with provenance.');
              });
            }}
          >
            <label className='block text-sm text-white' htmlFor='memory-kind'>
              Record type
            </label>
            <select id='memory-kind' className={input} value={kind} onChange={event => setKind(event.target.value)}>
              <option value='observation'>Observation</option>
              <option value='decision'>Decision</option>
              <option value='handoff'>Handoff</option>
            </select>
            <label className='block text-sm text-white' htmlFor='memory-content'>
              Memory note
            </label>
            <textarea
              id='memory-content'
              className={input}
              rows={3}
              maxLength={MEMORY_CONTENT_LIMIT}
              required
              value={content}
              onChange={event => setContent(event.target.value)}
            />
            <label className='block text-sm text-white' htmlFor='memory-provenance'>
              Source / provenance
            </label>
            <input
              id='memory-provenance'
              className={input}
              maxLength={MEMORY_PROVENANCE_LIMIT}
              required
              value={provenance}
              onChange={event => setProvenance(event.target.value)}
              placeholder='Source document, verified receipt or direct instruction'
            />
            <button className={button} disabled={!available || locked || !content.trim() || !provenance.trim()}>
              Save memory note
            </button>
          </form>
          <ul className='mt-5 max-h-[640px] space-y-3 overflow-auto'>
            {memory.map(note => (
              <li key={note.id} className='rounded-lg border border-white/10 p-4'>
                <p className='text-xs text-[#D7A3AB]'>
                  {note.kind} · {note.trust} · revision {note.revision}
                </p>
                <p className='mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-white'>{note.content}</p>
                <p className='mt-2 break-words text-xs leading-5 text-[#B7B7C2]'>Source: {note.provenance}</p>
                <p className='mt-1 text-xs text-[#B7B7C2]'>{memoryTimestamp(note.created)}</p>
                {note.trust !== 'OWNER_ACCEPTED' && (
                  <button
                    className={`${button} mt-3`}
                    disabled={!available || locked || connection?.can_promote_memory !== true}
                    onClick={() =>
                      void act('promote', async () => {
                        const result = await godModeRequest<RuntimeMemory>(`memory/${note.id}/promote`, {
                          method: 'POST',
                          body: '{}',
                        });
                        if (!active.current) return;
                        setMemory(current => current.map(item => (item.id === result.id ? result : item)));
                      })
                    }
                  >
                    Owner: accept this memory
                  </button>
                )}
              </li>
            ))}
          </ul>
          {available && memory.length === 0 && (
            <p className='mt-4 text-sm text-[#B7B7C2]'>No matching memory records.</p>
          )}
        </div>
      </div>
    </section>
  );
}
