/**
 * Agent OS terminal — pure command parsing and the confirmation gate.
 * Execution (the fetches) lives in components/agent-os/TerminalApp.tsx; this
 * module only decides WHAT a line of input means, so it is fully unit-tested.
 */

/** Mirrors `SuperAgentTypeLiteral` in api/tasks.py — the only agent types
 *  POST /api/v1/tasks accepts. Anything else is rejected before a request. */
export const TASK_AGENT_TYPES = ['commerce', 'creative', 'marketing', 'support', 'operations', 'analytics'] as const;
export type TaskAgentType = (typeof TASK_AGENT_TYPES)[number];

export const TASK_STATUSES = ['pending', 'running', 'completed', 'failed'] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];

/** Commands with a real side effect. They never execute without a `y`. */
export type GatedCommand = { kind: 'run'; agentType: TaskAgentType; prompt: string } | { kind: 'kill'; taskId: string };

export type TerminalCommand =
  | { kind: 'help' }
  | { kind: 'clear' }
  | { kind: 'ls' }
  | { kind: 'top' }
  | { kind: 'ps'; status?: TaskStatus }
  | { kind: 'open'; target: string }
  | GatedCommand
  | { kind: 'error'; message: string };

export const HELP_LINES = [
  'ls                         list agents (GET /api/v1/agents)',
  'ps [status]                list tasks — status: pending|running|completed|failed',
  'top                        system health (GET /api/v1/monitoring/health)',
  'open <app>                 open a window: tasks | monitor | <agent name>',
  'run <type> "<prompt>"      submit a task — type: ' + TASK_AGENT_TYPES.join('|'),
  'kill <taskId>              cancel a pending/running task',
  'clear                      clear the screen',
];

/** Whitespace split that keeps "double" or 'single' quoted spans intact. */
export function tokenize(input: string): string[] {
  const tokens: string[] = [];
  const re = /"([^"]*)"|'([^']*)'|(\S+)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(input)) !== null) tokens.push(m[1] ?? m[2] ?? m[3]);
  return tokens;
}

function isTaskAgentType(v: string): v is TaskAgentType {
  return (TASK_AGENT_TYPES as readonly string[]).includes(v);
}

function isTaskStatus(v: string): v is TaskStatus {
  return (TASK_STATUSES as readonly string[]).includes(v);
}

function parseRun(args: string[]): TerminalCommand {
  const [type, ...rest] = args;
  if (!type) return { kind: 'error', message: 'usage: run <type> "<prompt>"' };
  const agentType = type.toLowerCase();
  if (!isTaskAgentType(agentType)) {
    return { kind: 'error', message: `unknown agent type "${type}" — use ${TASK_AGENT_TYPES.join('|')}` };
  }
  const prompt = rest.join(' ').trim();
  if (!prompt) return { kind: 'error', message: 'run: a prompt is required' };
  return { kind: 'run', agentType, prompt };
}

function parsePs(args: string[]): TerminalCommand {
  if (args.length === 0) return { kind: 'ps' };
  const status = args[0].toLowerCase();
  if (!isTaskStatus(status)) {
    return { kind: 'error', message: `ps: unknown status "${args[0]}" — use ${TASK_STATUSES.join('|')}` };
  }
  return { kind: 'ps', status };
}

/** null for a blank line; an `error` command for anything unparseable. */
export function parseCommand(input: string): TerminalCommand | null {
  const [verb, ...args] = tokenize(input);
  if (!verb) return null;
  switch (verb.toLowerCase()) {
    case 'help':
      return { kind: 'help' };
    case 'clear':
      return { kind: 'clear' };
    case 'ls':
      return { kind: 'ls' };
    case 'top':
      return { kind: 'top' };
    case 'ps':
      return parsePs(args);
    case 'open':
      return args[0] ? { kind: 'open', target: args.join(' ') } : { kind: 'error', message: 'usage: open <app>' };
    case 'run':
      return parseRun(args);
    case 'kill':
      return args[0] ? { kind: 'kill', taskId: args[0] } : { kind: 'error', message: 'usage: kill <taskId>' };
    default:
      return { kind: 'error', message: `command not found: ${verb} — type "help"` };
  }
}

/** Only an explicit y/yes proceeds; everything else (including Enter) aborts. */
export function resolveConfirmation(input: string): 'confirm' | 'abort' {
  const v = input.trim().toLowerCase();
  return v === 'y' || v === 'yes' ? 'confirm' : 'abort';
}

export function confirmationPrompt(cmd: GatedCommand): string {
  if (cmd.kind === 'run') {
    return `Submit a ${cmd.agentType} task? This runs a model call and may cost money. [y/N]`;
  }
  return `Cancel task ${cmd.taskId}? [y/N]`;
}
