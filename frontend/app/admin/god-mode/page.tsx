'use client';

import { useEffect, useRef, useState } from 'react';
import { ApiError } from '@/lib/api/errors';
import { godMode, getGodModeRecoveryKey } from '@/lib/api/endpoints/god-mode';

const fields = ['mission_id', 'objective', 'role', 'context', 'scope', 'deliverables',
    'acceptance', 'authority', 'verification', 'recovery', 'return_contract'] as const;
type Mission = Record<(typeof fields)[number], string>;
type Discovery = Awaited<ReturnType<typeof godMode.providers>>;
type Run = Awaited<ReturnType<typeof godMode.status>>;
type Request = Parameters<typeof godMode.start>[0];
const active = new Set(['queued', 'running', 'cancel_requested']);
const inputClass = 'w-full rounded border border-gray-700 bg-gray-900 p-3 text-white';

export default function GodModePage() {
    const [discovery, setDiscovery] = useState<Discovery | null>(null);
    const [provider, setProvider] = useState('');
    const [model, setModel] = useState('');
    const [mission, setMission] = useState<Mission>(() => Object.fromEntries(fields.map(f => [f, ''])) as Mission);
    const [tools, setTools] = useState<string[]>([]);
    const [calls, setCalls] = useState(3);
    const [tokens, setTokens] = useState(2048);
    const [seconds, setSeconds] = useState(120);
    const [budget, setBudget] = useState(0.25);
    const [authorized, setAuthorized] = useState(false);
    const [run, setRun] = useState<Run | null>(null);
    const [error, setError] = useState('');
    const [recovering, setRecovering] = useState(true);
    const [busy, setBusy] = useState(false);
    const [uncertain, setUncertain] = useState(false);
    const recovery = useRef('');
    const pending = useRef<{body: Request; key: string} | null>(null);
    const runId = run?.id;
    const runState = run?.state;
    const selected = discovery?.providers.find(p => p.id === provider);
    const locked = recovering || busy || uncertain || Boolean(run && active.has(run.state));

    useEffect(() => {
        let disposed = false;
        async function restore() {
          try {
            const key = await getGodModeRecoveryKey();
            if (disposed) return;
            recovery.current = key;
            const saved = sessionStorage.getItem(recovery.current);
            if (saved) {
                const value: {pending?: {body: Request; key: string}; runId?: string} = JSON.parse(saved);
                if (value.pending) {
                    pending.current = value.pending;
                    setUncertain(true); setRecovering(false);
                    setError('An earlier submission needs reconciliation. Retry uses its original request key.');
                } else if (value.runId) {
                    godMode.status(value.runId).then(result => { if (!disposed) { setRun(result); setRecovering(false); } })
                        .catch(() => { if (!disposed) setError('Previous run status unavailable. Do not repeat the mission until reconciled.'); });
                } else { setRecovering(false); }
            } else { setRecovering(false); }
          } catch {
            if (!disposed) setError('Sign in and allow session storage so mission recovery can be preserved.');
          }
        }
        void restore();
        godMode.providers().then(result => { if (!disposed) setDiscovery(result); })
            .catch(() => { if (!disposed) setError('Provider discovery failed. Check your administrator session and backend connection.'); });
        return () => { disposed = true; };
    }, []);

    useEffect(() => {
        if (!runId || !runState || !active.has(runState)) return;
        let disposed = false;
        let timer: ReturnType<typeof setTimeout>;
        const refresh = async () => {
            try {
                const result = await godMode.status(runId);
                if (!disposed) setRun(result);
            } catch {
                if (!disposed) setError('Status unavailable. The run may still be executing; no new run was submitted.');
            }
            if (!disposed) timer = setTimeout(refresh, 3000);
        };
        timer = setTimeout(refresh, 1500);
        return () => { disposed = true; clearTimeout(timer); };
    }, [runId, runState]);

    async function submit() {
        if (busy) return;
        setBusy(true); setError('');
        try {
            if (!recovery.current || await getGodModeRecoveryKey() !== recovery.current) throw new Error();
        } catch { setError('Session changed. Reload before submitting.'); setBusy(false); return; }
        if (!pending.current) {
            pending.current = { key: crypto.randomUUID(), body: {
                mission, provider, model, tools, max_calls: calls, max_output_tokens: tokens,
                timeout_seconds: seconds, max_cost_usd: budget, authorize_paid: true,
            }};
        }
        try {
            // Persist before the network request, so reload cannot silently create another run.
            sessionStorage.setItem(recovery.current, JSON.stringify({pending: pending.current}));
            const result = await godMode.start(pending.current.body, pending.current.key);
            sessionStorage.setItem(recovery.current, JSON.stringify({runId: result.id}));
            setRun(result); setUncertain(false); pending.current = null;
        } catch (failure) {
            if (!uncertain && failure instanceof ApiError && [400, 401, 403, 409, 422].includes(failure.status)) {
                sessionStorage.removeItem(recovery.current);
                pending.current = null; setUncertain(false);
                setError(failure.message);
                return;
            }
            setUncertain(true);
            setError('Submission could not be confirmed. Retry preserves the same mission and request key to prevent duplicate execution.');
        } finally { setBusy(false); }
    }

    async function cancel() {
        if (!run) return;
        setBusy(true);
        try { setRun(await godMode.cancel(run.id)); }
        catch { setError('Cancellation could not be confirmed. Refresh status before further action.'); }
        finally { setBusy(false); }
    }

    return <main className="mx-auto max-w-4xl space-y-6 p-4 md:p-8">
        <header><h1 className="text-3xl font-bold">God Mode missions</h1>
            <p className="mt-2 text-gray-400">Direct a bounded agent through your configured providers. Define the deliverable and how it must be verified.</p></header>
        {error && <p role="alert" className="rounded border border-red-800 bg-red-950 p-4">{error}</p>}
        {!discovery && !error && <p role="status">Loading provider capabilities…</p>}
        {discovery && !discovery.paid_execution_enabled && <p role="status">Execution is disabled on this backend. Provider configuration remains visible.</p>}
        <form onSubmit={event => { event.preventDefault(); void submit(); }} className="space-y-5">
            <fieldset disabled={locked} className="space-y-5 disabled:opacity-60">
                <div className="grid gap-4 md:grid-cols-2">
                    <label>Provider<select required className={inputClass} value={provider} onChange={e => { setProvider(e.target.value); setModel(''); }}>
                        <option value="">Select provider</option>{discovery?.providers.map(p => <option key={p.id} value={p.id} disabled={!p.enabled || !p.configured || !p.models.length}>{p.id}{!p.configured ? ' — unconfigured' : ''}</option>)}
                    </select></label>
                    <label>Model<select required className={inputClass} value={model} onChange={e => setModel(e.target.value)}><option value="">Select model</option>{selected?.models.map(m => <option key={m} value={m}>{m}</option>)}</select></label>
                </div>
                {fields.map(field => <label className="block" key={field}><span className="capitalize">{field.replaceAll('_', ' ')}</span>
                    <textarea required maxLength={12000} rows={field === 'mission_id' ? 1 : 3} className={inputClass} value={mission[field]} onChange={e => setMission({...mission, [field]: e.target.value})}/>
                </label>)}
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                    <label>Model calls<input className={inputClass} type="number" required min={1} max={8} value={calls} onChange={e => setCalls(Number(e.target.value))}/></label>
                    <label>Output tokens / call<input className={inputClass} type="number" required min={128} max={8192} value={tokens} onChange={e => setTokens(Number(e.target.value))}/></label>
                    <label>Seconds<input className={inputClass} type="number" required min={10} max={300} value={seconds} onChange={e => setSeconds(Number(e.target.value))}/></label>
                    <label>Budget (USD)<input className={inputClass} type="number" required min={0.01} max={100} step={0.01} value={budget} onChange={e => setBudget(Number(e.target.value))}/></label>
                </div>
                {discovery?.tools.map(tool => <label className="block" key={tool}><input type="checkbox" checked={tools.includes(tool)} onChange={e => setTools(e.target.checked ? [...tools, tool] : tools.filter(t => t !== tool))}/> {tool}</label>)}
                <label className="flex items-start gap-3"><input required type="checkbox" checked={authorized} onChange={e => setAuthorized(e.target.checked)}/><span>I authorize paid execution for this mission within the stated limits. Cost reservations use the server’s configured rates.</span></label>
                <button type="submit" disabled={!discovery?.paid_execution_enabled || !authorized} className="rounded bg-rose-600 px-5 py-3 font-semibold disabled:opacity-40">Run mission</button>
            </fieldset>
        </form>
        {uncertain && <button disabled={busy} onClick={() => void submit()} className="rounded border p-3">Retry same submission</button>}
        {run && <section aria-live="polite" className="space-y-3 rounded border border-gray-700 p-5">
            <h2 className="text-xl font-semibold">Mission: {run.state}</h2><p className="break-all text-sm text-gray-400">Run {run.id}</p>
            <p>Verification: {run.verification} · Release: {run.release}</p>
            {active.has(run.state) && <button disabled={busy || run.state === 'cancel_requested'} onClick={() => void cancel()} className="rounded border p-3">Request cancellation</button>}
            {run.state === 'cancel_requested' && <p>The current provider call may still finish and incur cost.</p>}
            {run.error && <p role="alert">{run.error}</p>}
            {run.output && <pre className="whitespace-pre-wrap break-words font-sans">{run.output}</pre>}
        </section>}
    </main>;
}
