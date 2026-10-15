import { describe, expect, it } from 'vitest';

import { confirmationPrompt, parseCommand, resolveConfirmation, tokenize } from '@/lib/agent-os/terminal';
import { formatAgents, formatSystem, formatTasks } from '@/lib/agent-os/format';
import type { AgentInfo, MonitoringHealthResponse, Task } from '@/lib/api/types';

describe('tokenize', () => {
  it('splits on whitespace and keeps quoted strings whole', () => {
    expect(tokenize('run commerce "price the SG hoodie"')).toEqual(['run', 'commerce', 'price the SG hoodie']);
    expect(tokenize('  ps   running ')).toEqual(['ps', 'running']);
    expect(tokenize("run creative 'single quoted'")).toEqual(['run', 'creative', 'single quoted']);
  });
});

describe('parseCommand', () => {
  it('parses the read-only commands', () => {
    expect(parseCommand('help')).toEqual({ kind: 'help' });
    expect(parseCommand('clear')).toEqual({ kind: 'clear' });
    expect(parseCommand('ls')).toEqual({ kind: 'ls' });
    expect(parseCommand('top')).toEqual({ kind: 'top' });
    expect(parseCommand('ps')).toEqual({ kind: 'ps' });
    expect(parseCommand('ps running')).toEqual({ kind: 'ps', status: 'running' });
  });

  it('is case-insensitive on the verb', () => {
    expect(parseCommand('LS')).toEqual({ kind: 'ls' });
  });

  it('returns null for blank input', () => {
    expect(parseCommand('   ')).toBeNull();
  });

  it('rejects an unknown ps status filter', () => {
    expect(parseCommand('ps sleeping')).toMatchObject({ kind: 'error' });
  });

  it('parses run with a quoted or unquoted multi-word prompt', () => {
    expect(parseCommand('run commerce "reprice kids capsule"')).toEqual({
      kind: 'run',
      agentType: 'commerce',
      prompt: 'reprice kids capsule',
    });
    expect(parseCommand('run marketing draft the launch email')).toEqual({
      kind: 'run',
      agentType: 'marketing',
      prompt: 'draft the launch email',
    });
  });

  it('rejects run for an agent type the tasks API does not accept', () => {
    expect(parseCommand('run wizard do stuff')).toMatchObject({ kind: 'error' });
  });

  it('rejects run with no prompt', () => {
    expect(parseCommand('run commerce')).toMatchObject({ kind: 'error' });
    expect(parseCommand('run commerce "   "')).toMatchObject({ kind: 'error' });
  });

  it('parses kill and open, and rejects them without an argument', () => {
    expect(parseCommand('kill abc-123')).toEqual({ kind: 'kill', taskId: 'abc-123' });
    expect(parseCommand('kill')).toMatchObject({ kind: 'error' });
    expect(parseCommand('open monitor')).toEqual({ kind: 'open', target: 'monitor' });
    expect(parseCommand('open')).toMatchObject({ kind: 'error' });
  });

  it('reports unknown commands as errors, not as no-ops', () => {
    expect(parseCommand('rm -rf /')).toMatchObject({ kind: 'error' });
  });
});

describe('confirmation gate', () => {
  const run = { kind: 'run', agentType: 'commerce', prompt: 'x' } as const;

  it('only an explicit y / yes confirms', () => {
    expect(resolveConfirmation('y')).toBe('confirm');
    expect(resolveConfirmation(' YES ')).toBe('confirm');
    expect(resolveConfirmation('')).toBe('abort');
    expect(resolveConfirmation('ok')).toBe('abort');
    expect(resolveConfirmation('n')).toBe('abort');
  });

  it('names the side effect in the prompt', () => {
    expect(confirmationPrompt(run)).toMatch(/commerce/);
    expect(confirmationPrompt(run)).toMatch(/cost/i);
    expect(confirmationPrompt({ kind: 'kill', taskId: 't1' })).toMatch(/t1/);
  });
});

describe('formatters', () => {
  const agent: AgentInfo = {
    name: 'commerce_agent',
    version: '2.1.0',
    category: 'commerce',
    status: 'active',
    capabilities: ['pricing'],
    endpoints: [],
    last_execution: null,
  };

  it('formatAgents renders one row per agent plus a header', () => {
    const lines = formatAgents([agent]);
    expect(lines).toHaveLength(2);
    expect(lines[1]).toMatch(/commerce_agent/);
    expect(lines[1]).toMatch(/active/);
  });

  it('formatAgents says so when the roster is empty', () => {
    expect(formatAgents([])).toEqual(['No agents reported by /api/v1/agents.']);
  });

  it('formatTasks renders pid-style rows and an empty message', () => {
    const task: Task = {
      taskId: 't-1',
      agentType: 'creative',
      prompt: 'Write the Black Rose drop copy',
      status: 'running',
      createdAt: '2026-09-26T10:00:00Z',
      metrics: { startTime: '2026-09-26T10:00:00Z' },
    };
    const lines = formatTasks([task]);
    expect(lines[1]).toMatch(/t-1/);
    expect(lines[1]).toMatch(/running/);
    expect(formatTasks([])).toEqual(['No tasks.']);
  });

  it('formatSystem reports real stats and each service', () => {
    const health: MonitoringHealthResponse = {
      timestamp: '2026-09-26T10:00:00Z',
      services: [
        {
          name: 'api',
          status: 'healthy',
          uptime_pct: 99.9,
          response_ms: 42,
          last_check: '2026-09-26T10:00:00Z',
          circuit_breaker: 'closed',
        },
      ],
      system: { cpu_pct: 12.5, memory_pct: 40, disk_pct: 55, req_per_min: 30, success_rate: 99, avg_latency_ms: 80 },
      events: [],
    };
    const out = formatSystem(health).join('\n');
    expect(out).toMatch(/cpu\s+12\.5%/);
    expect(out).toMatch(/api/);
    expect(out).toMatch(/healthy/);
  });
});
