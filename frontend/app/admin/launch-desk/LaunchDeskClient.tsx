'use client';

import { useMemo, useRef, useState } from 'react';
import { readLaunchStream } from './stream';
import {
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  Check,
  ClipboardList,
  LoaderCircle,
  Radio,
  RotateCcw,
  Send,
  Sparkles,
  Users,
} from 'lucide-react';

interface LaunchForm {
  productBrief: string;
  audience: string;
  launchDate: string;
  constraints: string;
  availableAssets: string;
}

type ProgressState = 'waiting' | 'active' | 'complete';

interface ProgressItem {
  name: string;
  label: string;
  state: ProgressState;
}

const EMPTY_FORM: LaunchForm = {
  productBrief: '',
  audience: '',
  launchDate: '',
  constraints: '',
  availableAssets: '',
};

const TOOL_LABELS: Record<string, string> = {
  extract_launch_tasks: 'Extracting release work',
  check_launch_readiness: 'Checking readiness evidence',
  generate_owner_checklists: 'Assigning owner checklists',
  draft_channel_launch_copy: 'Drafting channel copy',
};

function setProgress(current: ProgressItem[], name: string, state: ProgressState): ProgressItem[] {
  const label = TOOL_LABELS[name] ?? name.replaceAll('_', ' ');
  const found = current.some(item => item.name === name);
  if (!found) return [...current, { name, label, state }];
  return current.map(item => (item.name === name ? { ...item, state } : item));
}

export function LaunchDeskClient() {
  const [form, setForm] = useState<LaunchForm>(EMPTY_FORM);
  const [answer, setAnswer] = useState('');
  const [progress, setProgressItems] = useState<ProgressItem[]>([]);
  const [error, setError] = useState('');
  const [traceId, setTraceId] = useState('');
  const [operationId, setOperationId] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const runIdRef = useRef(0);

  const canSubmit = useMemo(
    () => form.productBrief.trim().length >= 20 && form.audience.trim().length >= 3,
    [form.productBrief, form.audience]
  );

  const updateField = (field: keyof LaunchForm, value: string) => {
    setForm(current => ({ ...current, [field]: value }));
  };

  const reset = () => {
    runIdRef.current += 1;
    abortRef.current?.abort();
    abortRef.current = null;
    setForm(EMPTY_FORM);
    setAnswer('');
    setProgressItems([]);
    setError('');
    setTraceId('');
    setOperationId('');
    setIsRunning(false);
  };

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit || isRunning) return;

    const controller = new AbortController();
    const runId = runIdRef.current + 1;
    runIdRef.current = runId;
    abortRef.current = controller;
    setIsRunning(true);
    setAnswer('');
    setProgressItems([]);
    setError('');
    setTraceId('');
    setOperationId('');

    try {
      const response = await fetch('/api/launch-desk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Idempotency-Key': crypto.randomUUID() },
        body: JSON.stringify(form),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        const payload = (await response.json().catch(() => null)) as { error?: string; traceId?: string } | null;
        if (payload?.traceId) setTraceId(payload.traceId);
        throw new Error(payload?.error || `Launch Desk returned ${response.status}.`);
      }

      await readLaunchStream(response.body, streamed => {
        if (runIdRef.current !== runId) return;
        if (streamed.type === 'meta' && streamed.traceId) setTraceId(streamed.traceId);
        if (streamed.type === 'meta' && streamed.operationId) setOperationId(streamed.operationId);
        if (streamed.type === 'text_delta' && streamed.delta) {
          setAnswer(current => current + streamed.delta);
        }
        if (streamed.type === 'tool' && streamed.name && streamed.phase) {
          setProgressItems(current =>
            setProgress(current, streamed.name as string, streamed.phase === 'started' ? 'active' : 'complete')
          );
        }
      });
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === 'AbortError') return;
      if (runIdRef.current !== runId) return;
      controller.abort();
      setError(caught instanceof Error ? caught.message : 'Launch planning failed.');
    } finally {
      if (runIdRef.current === runId && abortRef.current === controller) {
        abortRef.current = null;
        setIsRunning(false);
      }
    }
  };

  return (
    <div className='px-5 py-6 md:px-9 md:py-8 max-w-[1480px]'>
      <section className='mb-7 grid gap-5 lg:grid-cols-[1.35fr_.65fr] lg:items-end'>
        <div>
          <div className='mb-3 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-[#C98A96]'>
            <Radio className='h-3.5 w-3.5' aria-hidden />
            Release planning agent
          </div>
          <h1 className='max-w-[760px] text-[clamp(2.1rem,4vw,4.3rem)] font-semibold leading-[0.98] tracking-[-0.03em] text-white'>
            Turn a rough launch into an owned release plan.
          </h1>
          <p className='mt-4 max-w-[720px] text-[15px] leading-7 text-[#A7A7AF]'>
            Launch Desk extracts the work, tests the brief against a readiness rubric, assigns owners, drafts channel
            copy, and calls out the decisions your team still needs to make.
          </p>
        </div>
        <div className='border-l border-white/10 pl-5 font-mono text-[10px] uppercase tracking-[0.13em] text-[#777780]'>
          <div className='mb-2 text-[#D5D5DA]'>Planning contract</div>
          <div className='grid grid-cols-2 gap-x-4 gap-y-2'>
            <span>Priority</span>
            <span className='text-right text-[#C98A96]'>P0 / P1 / P2</span>
            <span>Truth mode</span>
            <span className='text-right text-[#D7B66B]'>Fail closed</span>
            <span>Output</span>
            <span className='text-right text-[#D5D5DA]'>Progressive</span>
          </div>
        </div>
      </section>

      <div className='grid gap-[18px] xl:grid-cols-[minmax(0,.82fr)_minmax(0,1.18fr)]'>
        <form onSubmit={submit} className='border border-white/[0.08] bg-[#0D0D10] p-5 md:p-7'>
          <div className='mb-6 flex items-start justify-between gap-4'>
            <div>
              <div className='font-mono text-[10px] uppercase tracking-[0.18em] text-[#C98A96]'>Launch brief</div>
              <p className='mt-2 text-[13px] leading-5 text-[#85858D]'>Known facts first. Leave uncertainty visible.</p>
            </div>
            <button
              type='button'
              onClick={reset}
              className='flex min-h-11 items-center gap-2 border border-white/10 px-3 font-mono text-[9px] uppercase tracking-[0.14em] text-[#A0A0A8] hover:border-white/20 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#D7B66B]'
            >
              <RotateCcw className='h-3.5 w-3.5' aria-hidden /> Reset
            </button>
          </div>

          <div className='space-y-5'>
            <Field
              htmlFor='productBrief'
              label='Product brief'
              hint='What is shipping, for whom, and why now?'
              required
            >
              <textarea
                id='productBrief'
                value={form.productBrief}
                onChange={event => updateField('productBrief', event.target.value)}
                rows={7}
                minLength={20}
                maxLength={8000}
                required
                placeholder='We are launching…'
                className='launch-input resize-y'
              />
            </Field>

            <Field
              htmlFor='audience'
              label='Primary audience'
              hint='Buyer, user, segment, and adoption trigger.'
              required
            >
              <textarea
                id='audience'
                value={form.audience}
                onChange={event => updateField('audience', event.target.value)}
                rows={3}
                required
                placeholder='Engineering leads at…'
                className='launch-input resize-y'
              />
            </Field>

            <div className='grid gap-5 md:grid-cols-2'>
              <Field htmlFor='launchDate' label='Launch date' hint='Date, window, or event anchor.'>
                <div className='relative'>
                  <CalendarDays
                    className='pointer-events-none absolute left-3 top-3.5 h-4 w-4 text-[#66666E]'
                    aria-hidden
                  />
                  <input
                    id='launchDate'
                    value={form.launchDate}
                    onChange={event => updateField('launchDate', event.target.value)}
                    placeholder='2026-09-15'
                    className='launch-input pl-10'
                  />
                </div>
              </Field>
              <Field htmlFor='availableAssets' label='Available assets' hint='Demos, visuals, proof, docs, copy.'>
                <textarea
                  id='availableAssets'
                  value={form.availableAssets}
                  onChange={event => updateField('availableAssets', event.target.value)}
                  rows={3}
                  placeholder='Demo video, beta quotes…'
                  className='launch-input resize-y'
                />
              </Field>
            </div>

            <Field
              htmlFor='constraints'
              label='Constraints'
              hint='Budget, compliance, staffing, platform, dependencies.'
            >
              <textarea
                id='constraints'
                value={form.constraints}
                onChange={event => updateField('constraints', event.target.value)}
                rows={4}
                placeholder='Two engineers, no weekend launch…'
                className='launch-input resize-y'
              />
            </Field>
          </div>

          <button
            type='submit'
            disabled={!canSubmit || isRunning}
            className='mt-7 flex min-h-12 w-full items-center justify-center gap-3 bg-[#B76E79] px-5 font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-[#09090B] transition-colors hover:bg-[#C9828D] disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#D7B66B]'
          >
            {isRunning ? (
              <LoaderCircle className='h-4 w-4 animate-spin' aria-hidden />
            ) : (
              <Send className='h-4 w-4' aria-hidden />
            )}
            {isRunning ? 'Building launch plan' : 'Build launch plan'}
            {!isRunning && <ArrowRight className='h-4 w-4' aria-hidden />}
          </button>
        </form>

        <section
          aria-live='polite'
          aria-busy={isRunning}
          className='min-h-[720px] border border-white/[0.08] bg-[#0A0A0C]'
        >
          <div className='flex min-h-[66px] flex-wrap items-center justify-between gap-3 border-b border-white/[0.07] px-5 py-4 md:px-7'>
            <div className='flex items-center gap-3'>
              <Sparkles className='h-4 w-4 text-[#D7B66B]' aria-hidden />
              <span className='font-mono text-[10px] uppercase tracking-[0.18em] text-[#D5D5DA]'>Release plan</span>
            </div>
            {traceId && (
              <span title={traceId} className='font-mono text-[9px] tracking-[0.08em] text-[#62626A]'>
                TRACE {traceId.slice(0, 8)}
              </span>
            )}
          </div>

          {progress.length > 0 && (
            <div className='grid gap-px border-b border-white/[0.07] bg-white/[0.06] sm:grid-cols-2'>
              {progress.map(item => (
                <div key={item.name} className='flex min-h-[54px] items-center gap-3 bg-[#0D0D10] px-5'>
                  {item.state === 'complete' ? (
                    <span className='flex h-5 w-5 items-center justify-center rounded-full bg-[#76B58A]/15 text-[#76B58A]'>
                      <Check className='h-3 w-3' aria-hidden />
                    </span>
                  ) : (
                    <LoaderCircle className='h-4 w-4 animate-spin text-[#C98A96]' aria-hidden />
                  )}
                  <span className='font-mono text-[9px] uppercase tracking-[0.12em] text-[#A5A5AD]'>{item.label}</span>
                </div>
              ))}
            </div>
          )}

          {error && (
            <div
              role='alert'
              className='m-5 flex gap-3 border border-[#D46A6A]/30 bg-[#D46A6A]/[0.07] p-4 text-[#E7A0A0] md:m-7'
            >
              <AlertTriangle className='mt-0.5 h-4 w-4 flex-none' aria-hidden />
              <div>
                <div className='font-mono text-[10px] uppercase tracking-[0.14em]'>Planning interrupted</div>
                <p className='mt-2 text-[13px] leading-5'>{error}</p>
                {traceId && <p className='mt-2 break-all font-mono text-[11px]'>Trace: {traceId}</p>}
                {operationId && <p className='mt-1 break-all font-mono text-[11px]'>Operation: {operationId}</p>}
              </div>
            </div>
          )}

          {!answer && !error && (
            <div className='flex min-h-[600px] items-center justify-center p-7'>
              <div className='max-w-[470px] text-center'>
                <div className='mx-auto flex h-14 w-14 items-center justify-center border border-white/10 text-[#C98A96]'>
                  <ClipboardList className='h-6 w-6' aria-hidden />
                </div>
                <h2 className='mt-5 text-xl font-semibold text-white'>Your launch room is ready.</h2>
                <p className='mt-3 text-[14px] leading-6 text-[#85858D]'>
                  Submit the brief to watch task extraction, readiness review, owner assignment, and copy drafting
                  progress in real time.
                </p>
                <div className='mt-6 flex justify-center gap-5 font-mono text-[9px] uppercase tracking-[0.13em] text-[#66666E]'>
                  <span className='flex items-center gap-2'>
                    <Users className='h-3.5 w-3.5' aria-hidden /> Owners
                  </span>
                  <span className='flex items-center gap-2'>
                    <AlertTriangle className='h-3.5 w-3.5' aria-hidden /> Risks
                  </span>
                  <span className='flex items-center gap-2'>
                    <Sparkles className='h-3.5 w-3.5' aria-hidden /> Copy
                  </span>
                </div>
              </div>
            </div>
          )}

          {answer && (
            <article className='launch-output whitespace-pre-wrap px-5 py-6 text-[14px] leading-7 text-[#D2D2D7] md:px-8 md:py-8'>
              {answer}
              {isRunning && (
                <span className='ml-1 inline-block h-4 w-[2px] animate-pulse bg-[#C98A96] align-middle' aria-hidden />
              )}
            </article>
          )}
        </section>
      </div>

      <style jsx global>{`
        .launch-input {
          width: 100%;
          min-height: 44px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          background: #09090b;
          padding: 0.75rem;
          color: #eeeeef;
          font-size: 16px;
          line-height: 1.5;
          transition:
            border-color 120ms ease,
            background-color 120ms ease;
        }
        .launch-input::placeholder {
          color: #55555d;
        }
        .launch-input:hover {
          border-color: rgba(255, 255, 255, 0.18);
        }
        .launch-input:focus-visible {
          border-color: #d7b66b;
          outline: 2px solid rgba(215, 182, 107, 0.42);
          outline-offset: 2px;
        }
        .launch-output {
          overflow-wrap: anywhere;
        }
        @media (prefers-reduced-motion: reduce) {
          .launch-input {
            transition: none;
          }
          .launch-output + span,
          .animate-spin,
          .animate-pulse {
            animation: none !important;
          }
        }
      `}</style>
    </div>
  );
}

function Field({
  htmlFor,
  label,
  hint,
  required = false,
  children,
}: {
  htmlFor: string;
  label: string;
  hint: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className='mb-2 flex items-baseline justify-between gap-4'>
        <label htmlFor={htmlFor} className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#D5D5DA]'>
          {label} {required && <span className='text-[#C98A96]'>*</span>}
        </label>
        <span className='hidden text-right text-[10px] text-[#66666E] sm:block'>{hint}</span>
      </div>
      {children}
    </div>
  );
}
