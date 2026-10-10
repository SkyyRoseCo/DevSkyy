/**
 * Pure GPT-Live wire contracts. Nothing here opens a connection or records audio.
 * Transport stays blocked until duration enforcement and uncertain-start recovery
 * are verified; a planned-duration reserve is not a guaranteed spending ceiling.
 */

export const VOICE_MODEL = 'gpt-live-1' as const;
export const VOICE_INITIALIZATION_SECONDS = 15;
export const VOICE_RATE_MICRODOLLARS_PER_MINUTE = 50_000;
export const VOICE_MAX_SDP_BYTES = 65_536;
export const VOICE_MAX_USER_TEXT_BYTES = 4_096;
const MAX_INSTRUCTIONS_BYTES = 8_192;
const MAX_PLANNED_SECONDS = 3_600;

export interface VoiceServerPolicy {
  /** Trusted application instructions, never taken from the browser payload. */
  instructions: string;
}

export interface VoiceSessionRequest {
  session: {
    model: typeof VOICE_MODEL;
    instructions: string;
    store: false;
    delegation: { type: 'client' };
    client: {
      data_channel: {
        allowed_client_events: ['session.close'];
        allowed_server_events: Array<{ type: string }>;
      };
    };
    input: Array<{
      type: 'message';
      role: 'user';
      content: [{ type: 'input_text'; text: string }];
    }>;
  };
  transport: { type: 'webrtc'; sdp: string };
}

export interface VoiceCreationReceipt {
  sessionId: string;
  answerSdp: string;
  /** An HTTP creation response does not establish session.started. */
  phase: 'created';
  finalUsageConfirmed: false;
}

export interface VoiceUsageReceipt {
  eventId: string;
  cumulativeSeconds: number;
  finalUsageConfirmed: false;
}

export type VoiceCloseReason = 'close_requested' | 'expired' | 'content' | 'remote_hangup' | 'connection_lost';

export interface VoiceClosedReceipt {
  sessionId: string;
  eventId: string;
  reason: VoiceCloseReason;
  cumulativeSeconds: number;
  finalUsageConfirmed: true;
  model: typeof VOICE_MODEL;
  /** The provider uses active even for its final session snapshot. */
  snapshotStatus: 'active';
  expiresAt: number;
  storage: false | 'unconfirmed';
}

export interface VoiceDurationEstimate {
  currency: 'USD';
  plannedSeconds: number;
  reservedVoiceSeconds: number;
  reserveMicrodollars: number;
  providerDurationLimitVerified: false;
  hardSpendingCeilingGuaranteed: false;
}

function record(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error(`Invalid ${label}`);
  }
  const prototype: unknown = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) {
    throw new Error(`Invalid ${label}`);
  }
  return value as Record<string, unknown>;
}

function boundedText(value: unknown, maxBytes: number, label: string): string {
  if (
    typeof value !== 'string' ||
    value.length > maxBytes ||
    value.trim().length === 0 ||
    value.includes('\0') ||
    new TextEncoder().encode(value).length > maxBytes
  ) {
    // Never include user text, SDP network addresses, or provider content here.
    throw new Error(`Invalid ${label}`);
  }
  return value;
}

function sdp(value: unknown): string {
  const text = boundedText(value, VOICE_MAX_SDP_BYTES, 'SDP');
  if (!/^v=0\r?\n/.test(text)) throw new Error('Invalid SDP');
  return text;
}

function cumulativeSeconds(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) {
    throw new Error('Invalid voice usage');
  }
  return value;
}

/** Build documented POST /v1/live/sessions JSON without enabling transport. */
export function buildVoiceSessionRequest(
  browserPayload: unknown,
  serverPolicy: Readonly<VoiceServerPolicy>
): VoiceSessionRequest {
  const browser = record(browserPayload, 'voice request');
  if (Object.keys(browser).some(key => key !== 'sdp' && key !== 'userText')) {
    throw new Error('Unsupported voice request field');
  }
  const offer = sdp(browser.sdp);
  const instructions = boundedText(serverPolicy.instructions, MAX_INSTRUCTIONS_BYTES, 'voice policy');
  const userText =
    browser.userText === undefined
      ? undefined
      : boundedText(browser.userText, VOICE_MAX_USER_TEXT_BYTES, 'voice user text');
  return {
    session: {
      model: VOICE_MODEL,
      instructions,
      store: false,
      // Configures application-owned delegation; no delegate is executed here.
      delegation: { type: 'client' },
      client: {
        data_channel: {
          allowed_client_events: ['session.close'],
          allowed_server_events: [
            { type: 'session.started' },
            { type: 'session.usage.updated' },
            { type: 'session.closed' },
            { type: 'error' },
          ],
        },
      },
      input:
        userText === undefined
          ? []
          : [
              {
                type: 'message',
                role: 'user',
                content: [{ type: 'input_text', text: userText }],
              },
            ],
    },
    transport: { type: 'webrtc', sdp: offer },
  };
}

export function parseVoiceCreationReceipt(value: unknown): VoiceCreationReceipt {
  const response = record(value, 'voice creation response');
  const session = record(response.session, 'voice session');
  const transport = record(response.transport, 'voice transport');
  if (transport.type !== 'webrtc') throw new Error('Invalid voice transport');
  return {
    sessionId: boundedText(session.id, 256, 'voice session id'),
    answerSdp: sdp(transport.sdp),
    phase: 'created',
    finalUsageConfirmed: false,
  };
}

/** Usage updates are cumulative snapshots, never increments or final receipts. */
export function parseVoiceUsageReceipt(value: unknown): VoiceUsageReceipt {
  const event = record(value, 'voice usage event');
  if (event.type !== 'session.usage.updated') throw new Error('Invalid voice usage event');
  const usage = record(event.usage, 'voice usage');
  return {
    eventId: boundedText(event.event_id, 256, 'voice event id'),
    cumulativeSeconds: cumulativeSeconds(usage.seconds),
    finalUsageConfirmed: false,
  };
}

/** A matching session.closed receipt confirms final usage, including loss reasons. */
export function parseVoiceClosedReceipt(value: unknown, expectedSessionId: string): VoiceClosedReceipt {
  const expectedId = boundedText(expectedSessionId, 256, 'expected voice session id');
  const event = record(value, 'voice closed event');
  if (event.type !== 'session.closed') throw new Error('Invalid voice closed event');
  const session = record(event.session, 'voice session snapshot');
  const sessionId = boundedText(session.id, 256, 'voice session id');
  if (sessionId !== expectedId) throw new Error('Voice session receipt mismatch');
  const reasons: VoiceCloseReason[] = ['close_requested', 'expired', 'content', 'remote_hangup', 'connection_lost'];
  if (typeof event.reason !== 'string' || !reasons.includes(event.reason as VoiceCloseReason)) {
    throw new Error('Invalid voice close reason');
  }
  if (session.model !== VOICE_MODEL || session.status !== 'active') {
    throw new Error('Unexpected voice session snapshot');
  }
  if (typeof session.expires_at !== 'number' || !Number.isFinite(session.expires_at) || session.expires_at <= 0) {
    throw new Error('Invalid voice expiry');
  }
  if (session.store !== undefined && session.store !== false) {
    throw new Error('Unexpected voice storage policy');
  }
  const usage = record(event.usage, 'voice final usage');
  return {
    sessionId,
    eventId: boundedText(event.event_id, 256, 'voice event id'),
    reason: event.reason as VoiceCloseReason,
    cumulativeSeconds: cumulativeSeconds(usage.seconds),
    finalUsageConfirmed: true,
    model: VOICE_MODEL,
    snapshotStatus: 'active',
    expiresAt: session.expires_at,
    storage: session.store === false ? false : 'unconfirmed',
  };
}

/**
 * Voice-only planning estimate. Initialization reserves 15 seconds, credited
 * against running duration. Backend/tool charges require their own reservation.
 */
export function estimateVoiceDuration(plannedSeconds: number): VoiceDurationEstimate {
  if (!Number.isInteger(plannedSeconds) || plannedSeconds < 0 || plannedSeconds > MAX_PLANNED_SECONDS) {
    throw new Error('Invalid planned voice duration');
  }
  const reservedVoiceSeconds = Math.max(VOICE_INITIALIZATION_SECONDS, plannedSeconds);
  return {
    currency: 'USD',
    plannedSeconds,
    reservedVoiceSeconds,
    reserveMicrodollars: Math.ceil((reservedVoiceSeconds * VOICE_RATE_MICRODOLLARS_PER_MINUTE) / 60),
    providerDurationLimitVerified: false,
    hardSpendingCeilingGuaranteed: false,
  };
}

/** Cannot be enabled by client flags or local timers. No transport exists yet. */
export function voiceTransportReadiness() {
  return {
    enabled: false as const,
    blockers: [
      'approved_operation_and_spending_limit',
      'provider_enforced_duration_limit',
      'uncertain_session_creation_reconciliation',
      'authenticated_server_transport_and_delegation',
    ] as const,
  };
}
