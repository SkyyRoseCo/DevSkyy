/**
 * Plain-text renderers for the Agent OS terminal (`ls`, `ps`, `top`).
 * They print only fields the API actually returns — nothing is synthesized.
 */
import type { AgentInfo, MonitoringHealthResponse, Task } from '@/lib/api/types';

function col(value: string, width: number): string {
  return value.length >= width ? `${value.slice(0, width - 1)}…` : value.padEnd(width);
}

export function formatAgents(agents: AgentInfo[]): string[] {
  if (agents.length === 0) return ['No agents reported by /api/v1/agents.'];
  const header = `${col('NAME', 26)} ${col('CATEGORY', 14)} ${col('STATUS', 12)} VERSION`;
  const rows = agents.map(a => `${col(a.name, 26)} ${col(a.category, 14)} ${col(a.status, 12)} v${a.version}`);
  return [header, ...rows];
}

export function formatTasks(tasks: Task[]): string[] {
  if (tasks.length === 0) return ['No tasks.'];
  const header = `${col('TASK ID', 14)} ${col('AGENT', 12)} ${col('STATUS', 10)} PROMPT`;
  const rows = tasks.map(
    t => `${col(t.taskId, 14)} ${col(t.agentType, 12)} ${col(t.status, 10)} ${col(t.prompt, 48).trimEnd()}`
  );
  return [header, ...rows];
}

export function formatSystem(health: MonitoringHealthResponse): string[] {
  const s = health.system;
  const stats = [
    `cpu ${s.cpu_pct}%   mem ${s.memory_pct}%   disk ${s.disk_pct}%`,
    `req/min ${s.req_per_min}   success ${s.success_rate}%   latency ${s.avg_latency_ms}ms`,
  ];
  if (health.services.length === 0) return [...stats, 'No services reported.'];
  const services = health.services.map(
    svc =>
      `${col(svc.name, 22)} ${col(svc.status, 10)} up ${svc.uptime_pct}%  breaker ${svc.circuit_breaker}` +
      (svc.response_ms != null ? `  ${svc.response_ms}ms` : '')
  );
  return [...stats, '', ...services];
}
