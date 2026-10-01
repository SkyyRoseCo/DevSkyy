import { NextResponse, type NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';

import { withAuth } from '@/lib/api-auth';
import { authOptions } from '@/lib/auth';
import { ExecutionBudgetError, reserveExecution } from '@/lib/os-execution-budget';

import {
  createLaunchDeskAgent,
  createLaunchDeskRunner,
  formatLaunchPrompt,
  launchDeskModel,
  launchDeskExecutionConfig,
} from './_lib/agent';
import { assessLaunchReadiness, buildOwnerChecklists, draftLaunchCopy, extractLaunchTasks } from './_lib/tools';
import { launchBriefSchema } from './_lib/types';

export const maxDuration = 120;

interface StreamEvent {
  type: 'meta' | 'tool' | 'text_delta' | 'done' | 'error';
  [key: string]: unknown;
}

function sse(event: StreamEvent): Uint8Array {
  return new TextEncoder().encode(`data: ${JSON.stringify(event)}\n\n`);
}

async function handleLaunchDesk(request: NextRequest): Promise<Response> {
  if (!process.env.OPENAI_API_KEY) {
    return NextResponse.json(
      { success: false, error: 'OPENAI_API_KEY is not configured on the server.' },
      { status: 503 }
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ success: false, error: 'Request body must be JSON.' }, { status: 400 });
  }

  const parsed = launchBriefSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { success: false, error: 'Launch brief is invalid.', issues: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const traceId = crypto.randomUUID();
  const toolEvents: StreamEvent[] = [];
  let prompt: string;
  let reservation: Awaited<ReturnType<typeof reserveExecution>>;
  try {
    const session = await getServerSession(authOptions);
    const runTool = <T>(name: string, execute: () => T): T => {
      toolEvents.push({ type: 'tool', phase: 'started', name });
      const output = execute();
      toolEvents.push({ type: 'tool', phase: 'completed', name });
      return output;
    };
    const tasks = runTool('extract_launch_tasks', () => extractLaunchTasks(parsed.data));
    const readiness = runTool('check_launch_readiness', () => assessLaunchReadiness(parsed.data));
    const ownerChecklists = runTool('generate_owner_checklists', () => buildOwnerChecklists(tasks));
    const channelDrafts = runTool('draft_channel_launch_copy', () =>
      draftLaunchCopy({
        productName: 'Launch candidate',
        promise: parsed.data.productBrief.split(/[.!?]/, 1)[0]?.trim() || 'A new product release',
        audience: parsed.data.audience,
      })
    );
    prompt = formatLaunchPrompt(parsed.data, { tasks, readiness, ownerChecklists, channelDrafts });
    const executionConfig = launchDeskExecutionConfig();
    reservation = await reserveExecution({
      operationKind: 'launch-desk',
      operationId: request.headers.get('Idempotency-Key') ?? '',
      traceId,
      actorId: session?.user?.email ?? '',
      model: launchDeskModel(),
      executionConfig,
      serializedInput: JSON.stringify({ executionConfig, input: prompt }),
    });
  } catch (error) {
    const code = error instanceof ExecutionBudgetError ? error.code : 'PREPARATION_FAILED';
    const status =
      code === 'OWNER_SCOPE'
        ? 403
        : code === 'REPLAY'
          ? 409
          : code === 'INPUT_LIMIT'
            ? 413
            : ['OPERATION_LIMIT', 'SPENDING_LIMIT'].includes(code)
              ? 429
              : 503;
    return NextResponse.json(
      {
        success: false,
        code,
        traceId,
        error: 'Launch Desk execution is unavailable under the current owner and spending policy.',
      },
      { status }
    );
  }
  const cancellation = new AbortController();
  const signal = AbortSignal.any([request.signal, cancellation.signal, AbortSignal.timeout(90_000)]);
  let closed = false;

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (event: StreamEvent) => {
        if (!closed) controller.enqueue(sse(event));
      };

      send({
        type: 'meta',
        traceId,
        operationId: reservation.operationId,
        model: launchDeskModel(),
        message: 'Launch Desk is reading the brief.',
      });
      for (const event of toolEvents) send(event);

      try {
        signal.throwIfAborted();
        const result = await createLaunchDeskRunner().run(createLaunchDeskAgent(), prompt, {
          stream: true,
          signal,
          maxTurns: 1,
        });

        let providerCompleted = false;
        let text = '';
        let terminalResponses = 0;
        for await (const event of result) {
          if (event.type === 'raw_model_stream_event') {
            const data = event.data;
            if (data.type === 'output_text_delta' && typeof data.delta === 'string') {
              text += data.delta;
              send({ type: 'text_delta', delta: data.delta });
            }
            if (data.type === 'response_done') {
              terminalResponses += 1;
              providerCompleted = data.response.providerData?.status === 'completed';
              await reservation.recordProviderResponse(data.response.id);
            }
            continue;
          }
        }

        await result.completed;
        signal.throwIfAborted();
        if (
          !providerCompleted ||
          terminalResponses !== 1 ||
          !text.trim() ||
          toolEvents.filter(event => event.phase === 'completed').length !== 4
        ) {
          throw new Error('Provider response did not complete a nonempty plan.');
        }
        send({ type: 'done', traceId, operationId: reservation.operationId });
      } catch (error) {
        console.error('Launch Desk planning failed.', {
          traceId,
          kind: error instanceof Error ? error.name : 'UnknownError',
        });
        send({
          type: 'error',
          message:
            'Launch Desk could not complete this plan. Its reservation is retained; contact the operator with the trace ID before retrying.',
          traceId,
          operationId: reservation.operationId,
        });
      } finally {
        if (!closed) {
          closed = true;
          controller.close();
        }
      }
    },
    cancel() {
      closed = true;
      cancellation.abort();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}

export const POST = withAuth(handleLaunchDesk);
