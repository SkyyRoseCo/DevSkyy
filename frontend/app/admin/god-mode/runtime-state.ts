/** Presentation state only; backend approval, execution and memory remain authoritative. */
export interface RuntimeStatus {
  status: string;
  runtime: string;
  can_approve?: boolean;
  can_promote_memory?: boolean;
  limits: Record<string, unknown>;
  agent_workers?: {
    main_worker: RuntimeEngine;
    independent_reviewer: RuntimeEngine;
    scope: string;
    production_enabled: boolean;
  };
}
export interface RuntimeEngine {
  engine: string;
  state: string;
  model?: string;
  reason?: string;
}
export interface RuntimeWorkflow {
  id: string;
  title: string;
  description: string;
  approval_required: boolean;
  enabled?: boolean;
  unavailable_reason?: string;
  steps: { id: string; title: string; owner: string; verifier: string }[];
}
export interface RuntimeRun {
  id: string;
  project: string;
  workflow: string;
  status: string;
  plan_hash: string;
  plan: unknown;
  approval: unknown;
  steps: unknown[];
  events: unknown[];
  artifact_hash?: string;
  reviews?: unknown[];
}
export interface RuntimeMemory {
  id: string;
  project: string;
  kind: string;
  content: string;
  provenance: string;
  trust: string;
  revision: number;
  supersedes: string | null;
  actor: string;
  created: number;
}
export function canExecute(run: RuntimeRun): boolean {
  return run.status === 'APPROVED' && run.approval !== null;
}
export function needsPolling(run: RuntimeRun): boolean {
  return run.status === 'RUNNING';
}
export function runtimeError(error: unknown): string {
  return error instanceof Error ? error.message : 'The runtime request failed. Retry the connection.';
}

/** API limits mirror skyyrose/godmode_runtime/api.py; timestamps are Unix seconds. */
export const MEMORY_CONTENT_LIMIT = 8000;
export const MEMORY_PROVENANCE_LIMIT = 500;
export const MEMORY_QUERY_LIMIT = 200;
export function memoryTimestamp(seconds: number): string {
  if (!Number.isFinite(seconds)) return 'Timestamp unavailable';
  const date = new Date(seconds * 1000);
  return Number.isNaN(date.getTime())
    ? 'Timestamp unavailable'
    : date.toISOString().replace('T', ' ').replace('Z', ' UTC');
}

/** Execution retains its own lease while a same-run cancellation request is in flight. */
export class RuntimeOperations {
  private pending = new Map<symbol, { label: string; runId: string | null }>();
  private execution: symbol | null = null;
  get executingRunId(): string | null {
    return this.execution ? this.pending.get(this.execution)?.runId || null : null;
  }
  get busy(): string | null {
    return [...this.pending.values()].at(-1)?.label || null;
  }
  begin(label: string, runId: string | null): symbol | null {
    const sameRunCancel =
      label === 'cancel' &&
      runId !== null &&
      this.executingRunId === runId &&
      ![...this.pending.values()].some(item => item.label === 'cancel');
    if (this.pending.size && !sameRunCancel) return null;
    const token = Symbol(label);
    this.pending.set(token, { label, runId });
    if (label === 'execute') this.execution = token;
    return token;
  }
  finish(token: symbol): void {
    this.pending.delete(token);
    if (this.execution === token) this.execution = null;
  }
}
export function applyRunResult(
  current: RuntimeRun | null,
  requestedId: string,
  result: RuntimeRun,
  active: boolean
): RuntimeRun | null {
  return active && current?.id === requestedId && result.id === requestedId ? result : current;
}

/** Older catalogs only qualify the three fixed offline workflows. */
export function workflowEnabled(workflow: RuntimeWorkflow | undefined): boolean {
  if (!workflow) return false;
  if (typeof workflow.enabled === 'boolean') return workflow.enabled;
  return ['source-audit', 'campaign-readiness', 'fashion-verification'].includes(workflow.id);
}
export interface RuntimeStepSummary {
  id: string;
  status: string;
  verdict?: string;
  findings?: number;
  workerArtifactHash?: string;
}
export function stepSummaries(steps: unknown[]): RuntimeStepSummary[] {
  return steps.flatMap(step => {
    if (!step || typeof step !== 'object') return [];
    const receipt = step as Record<string, unknown>;
    if (typeof receipt.id !== 'string' || typeof receipt.status !== 'string') return [];
    const artifact =
      receipt.artifact && typeof receipt.artifact === 'object' ? (receipt.artifact as Record<string, unknown>) : {};
    return [
      {
        id: receipt.id,
        status: receipt.status,
        ...(typeof artifact.verdict === 'string' ? { verdict: artifact.verdict } : {}),
        ...(Array.isArray(artifact.findings) ? { findings: artifact.findings.length } : {}),
        ...(typeof artifact.worker_artifact_sha256 === 'string'
          ? { workerArtifactHash: artifact.worker_artifact_sha256 }
          : {}),
      },
    ];
  });
}
