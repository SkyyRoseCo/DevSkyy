'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { z } from 'zod';

// =============================================================================
// CONFIGURATION
// =============================================================================

const WS_URL = (() => {
  const url = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
  try {
    // Validate WebSocket URL format
    const parsed = new URL(url);
    if (!['ws:', 'wss:'].includes(parsed.protocol)) {
      console.error('Invalid WebSocket protocol, falling back to localhost');
      return 'ws://localhost:8000';
    }
    return url;
  } catch {
    console.error('Invalid WS_URL, falling back to localhost');
    return 'ws://localhost:8000';
  }
})();

const MAX_RECONNECT_ATTEMPTS = 5;
const MAX_MESSAGE_HISTORY = 100;
const SEND_RATE_LIMIT_MS = 100; // Minimum time between sends

// =============================================================================
// ZOD SCHEMAS
// =============================================================================

const WebSocketMessageSchema = z.object({
  type: z.string(),
  data: z.unknown(),
  timestamp: z.string(),
});

const RoundTableEventSchema = z.object({
  event: z.enum(['competition_started', 'provider_responded', 'competition_completed', 'error']),
  competition_id: z.string().optional(),
  provider_id: z.string().optional(),
  result: z
    .object({
      score: z.number(),
      latency_ms: z.number(),
    })
    .optional(),
  winner: z.string().optional(),
  error: z.string().optional(),
});

const Pipeline3DEventSchema = z.object({
  event: z.enum(['job_queued', 'job_started', 'job_progress', 'job_completed', 'job_failed']),
  job_id: z.string(),
  provider: z.string().optional(),
  progress: z.number().min(0).max(100).optional(),
  output_url: z.string().url().optional(),
  error: z.string().optional(),
});

// =============================================================================
// TYPES
// =============================================================================

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketMessage<T = unknown> {
  type: string;
  data: T;
  timestamp: string;
}

export type RoundTableEvent = z.infer<typeof RoundTableEventSchema>;
export type Pipeline3DEvent = z.infer<typeof Pipeline3DEventSchema>;

export interface WebSocketError {
  code: string;
  message: string;
  timestamp: Date;
}

// =============================================================================
// VALIDATION UTILITIES
// =============================================================================

function validateChannel(channel: string): boolean {
  // Only allow alphanumeric, underscores, and hyphens
  return /^[a-zA-Z0-9_-]+$/.test(channel);
}

function parseMessage<T>(data: string, schema?: z.ZodType<T>): WebSocketMessage<T> | null {
  try {
    const parsed = JSON.parse(data);

    // Validate base message structure
    const baseResult = WebSocketMessageSchema.safeParse(parsed);
    if (!baseResult.success) {
      console.warn('Invalid WebSocket message structure:', baseResult.error.issues);
      return null;
    }

    // If a specific schema is provided, validate the data field
    if (schema) {
      const dataResult = schema.safeParse(baseResult.data.data);
      if (!dataResult.success) {
        console.warn('Invalid message data:', dataResult.error.issues);
        // Return with raw data if schema validation fails
        return baseResult.data as WebSocketMessage<T>;
      }
      return {
        ...baseResult.data,
        data: dataResult.data,
      };
    }

    return baseResult.data as WebSocketMessage<T>;
  } catch (err) {
    console.error('Failed to parse WebSocket message:', err);
    return null;
  }
}

// =============================================================================
// MAIN HOOK
// =============================================================================

export function useWebSocket<T = unknown>(
  channel: string,
  options?: {
    schema?: z.ZodType<T>;
    autoConnect?: boolean;
  }
) {
  const { schema, autoConnect = true } = options || {};

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage<T> | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage<T>[]>([]);
  const [error, setError] = useState<WebSocketError | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const lastSendTimeRef = useRef(0);

  // Validate channel on mount
  const isValidChannel = validateChannel(channel);

  const connect = useCallback(() => {
    if (!isValidChannel) {
      setError({
        code: 'INVALID_CHANNEL',
        message: `Invalid channel name: ${channel}`,
        timestamp: new Date(),
      });
      setStatus('error');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    // This backend handshake does not consume a bearer credential. Never put
    // credentials in URLs, where browser history and proxy logs can retain them.
    const wsUrl = `${WS_URL}/api/ws/${encodeURIComponent(channel)}`;

    setStatus('connecting');
    setError(null);

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setStatus('connected');
        reconnectAttemptsRef.current = 0;
        setError(null);
      };

      ws.onmessage = event => {
        const message = parseMessage<T>(event.data, schema);
        if (message) {
          setLastMessage(message);
          setMessages(prev => {
            const next = [...prev, message];
            // Keep only the last N messages to prevent memory issues
            return next.slice(-MAX_MESSAGE_HISTORY);
          });
        }
      };

      ws.onerror = event => {
        setStatus('error');
        setError({
          code: 'CONNECTION_ERROR',
          message: 'WebSocket connection error',
          timestamp: new Date(),
        });
        console.error('WebSocket error:', event);
      };

      ws.onclose = event => {
        setStatus('disconnected');
        wsRef.current = null;

        // Don't reconnect if closed normally (code 1000) or due to auth failure (code 4001)
        if (event.code === 1000 || event.code === 4001) {
          return;
        }

        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else {
          setError({
            code: 'MAX_RECONNECT_EXCEEDED',
            message: `Failed to reconnect after ${MAX_RECONNECT_ATTEMPTS} attempts`,
            timestamp: new Date(),
          });
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setStatus('error');
      setError({
        code: 'CONNECTION_FAILED',
        message: err instanceof Error ? err.message : 'Failed to create WebSocket',
        timestamp: new Date(),
      });
    }
  }, [channel, isValidChannel, schema]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }
    setStatus('disconnected');
    reconnectAttemptsRef.current = 0;
  }, []);

  const send = useCallback((data: unknown): boolean => {
    // Rate limiting
    const now = Date.now();
    if (now - lastSendTimeRef.current < SEND_RATE_LIMIT_MS) {
      console.warn('Send rate limited');
      return false;
    }

    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return false;
    }

    try {
      const serialized = JSON.stringify(data);
      // Basic size check (100KB limit)
      if (serialized.length > 100 * 1024) {
        console.error('Message too large');
        return false;
      }
      wsRef.current.send(serialized);
      lastSendTimeRef.current = now;
      return true;
    } catch (err) {
      console.error('Failed to send message:', err);
      return false;
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setLastMessage(null);
  }, []);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => disconnect();
  }, [autoConnect, connect, disconnect]);

  return {
    status,
    lastMessage,
    messages,
    error,
    send,
    connect,
    disconnect,
    clearMessages,
    resetError,
    isConnected: status === 'connected',
  };
}

// =============================================================================
// SPECIALIZED HOOKS
// =============================================================================

export function useRoundTableWS() {
  return useWebSocket<RoundTableEvent>('round_table', {
    schema: RoundTableEventSchema,
  });
}

export function use3DPipelineWS() {
  return useWebSocket<Pipeline3DEvent>('3d_pipeline', {
    schema: Pipeline3DEventSchema,
  });
}
