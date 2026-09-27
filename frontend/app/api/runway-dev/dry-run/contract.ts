import { z } from 'zod';

export const RUNWAY_IMAGE_MODEL = 'gpt_image_2_5_sunburst';
export const RUNWAY_MAX_IMAGE_CREDITS = 76;
export const RUNWAY_PREFLIGHT_RESOLUTION = '2k';
export const RUNWAY_PREFLIGHT_OUTPUT_COUNT = 1;
export const RUNWAY_PREFLIGHT_PROMPT =
  'A neutral studio still life of one unbranded ceramic vessel on a plain warm-gray background. No text, logos, or people.';

export const RUNWAY_ASPECT_RATIOS = [
  '16:9',
  '9:16',
  '1:1',
  '4:3',
  '3:4',
  '21:9',
  '2:3',
  '3:2',
  '4:5',
  '5:4',
] as const;

export type RunwayAspectRatio = (typeof RUNWAY_ASPECT_RATIOS)[number];

export const RunwayPreflightBodySchema = z
  .object({
    aspectRatio: z.enum(RUNWAY_ASPECT_RATIOS).optional(),
  })
  .strict();

export type RunwayPreflightBody = z.infer<typeof RunwayPreflightBodySchema>;

export function buildRunwayDryRunPayload(
  configId: string,
  aspectRatio: RunwayAspectRatio = '4:5',
) {
  return {
    configId,
    dryRun: true as const,
    input: {
      promptText: RUNWAY_PREFLIGHT_PROMPT,
      aspectRatio,
      resolution: RUNWAY_PREFLIGHT_RESOLUTION,
      outputCount: RUNWAY_PREFLIGHT_OUTPUT_COUNT,
    },
  };
}

const RunwayDryRunResponseSchema = z
  .object({
    dryRun: z.boolean(),
    id: z.unknown().optional(),
    routing: z
      .object({
        model: z.string(),
        configId: z.string(),
        resolvedSettings: z.object({
          optimizeFor: z.enum(['cost', 'latency', 'quality']),
          priceCeiling: z.number().nullable(),
        }),
        resolvedInput: z.object({
          ratio: z.string(),
          aspectRatio: z.enum(RUNWAY_ASPECT_RATIOS),
          resolution: z.enum(['1k', '2k', '4k']),
        }),
        estimatedCost: z.object({
          credits: z.number().finite().nonnegative(),
        }),
      })
      .passthrough(),
  })
  .passthrough();

export type RunwayDryRunDecision = {
  model: typeof RUNWAY_IMAGE_MODEL;
  configId: string;
  optimizeFor: 'cost' | 'latency' | 'quality';
  pricing: {
    estimatedCostCredits: number;
    /** The effective ceiling reported for this dry-run request. */
    routerCeilingCredits: number;
    /** Dry-run responses contain an estimate, not a live task maximum. */
    providerBoundMaximumCredits: null;
    /** Runway documents dry-runs as unbilled and non-generative. */
    reservationBoundCredits: 0;
  };
  aspectRatio: RunwayAspectRatio;
  resolution: '2k';
};

export type RunwayDryRunValidation =
  | { ok: true; decision: RunwayDryRunDecision }
  | {
      ok: false;
      reason:
        | 'INVALID_PROVIDER_RESPONSE'
        | 'DRY_RUN_NOT_CONFIRMED'
        | 'TASK_ID_RETURNED'
        | 'ARTIFACT_RETURNED'
        | 'ROUTER_CONFIG_MISMATCH'
        | 'MODEL_NOT_ALLOWLISTED'
        | 'PRICE_CEILING_MISSING'
        | 'PRICE_CEILING_OUT_OF_POLICY'
        | 'ESTIMATE_EXCEEDS_CEILING'
        | 'RESOLVED_INPUT_MISMATCH';
    };

export function validateRunwayDryRunResponse(
  value: unknown,
  expectedConfigId: string,
  expectedAspectRatio: RunwayAspectRatio,
): RunwayDryRunValidation {
  const parsed = RunwayDryRunResponseSchema.safeParse(value);
  if (!parsed.success) {
    return { ok: false, reason: 'INVALID_PROVIDER_RESPONSE' };
  }

  const result = parsed.data;
  if (!result.dryRun) {
    return { ok: false, reason: 'DRY_RUN_NOT_CONFIRMED' };
  }
  if (result.id !== undefined) {
    return { ok: false, reason: 'TASK_ID_RETURNED' };
  }
  if (result.taskId !== undefined || result.task !== undefined) {
    return { ok: false, reason: 'TASK_ID_RETURNED' };
  }
  if (['asset', 'assets', 'output', 'outputs'].some((key) => Object.hasOwn(result, key))) {
    return { ok: false, reason: 'ARTIFACT_RETURNED' };
  }

  const routing = result.routing;
  if (routing.configId !== expectedConfigId) {
    return { ok: false, reason: 'ROUTER_CONFIG_MISMATCH' };
  }
  if (routing.model !== RUNWAY_IMAGE_MODEL) {
    return { ok: false, reason: 'MODEL_NOT_ALLOWLISTED' };
  }

  const priceCeiling = routing.resolvedSettings.priceCeiling;
  if (priceCeiling === null) {
    return { ok: false, reason: 'PRICE_CEILING_MISSING' };
  }
  if (priceCeiling <= 0 || priceCeiling > RUNWAY_MAX_IMAGE_CREDITS) {
    return { ok: false, reason: 'PRICE_CEILING_OUT_OF_POLICY' };
  }
  if (routing.estimatedCost.credits > priceCeiling) {
    return { ok: false, reason: 'ESTIMATE_EXCEEDS_CEILING' };
  }
  if (
    routing.resolvedInput.ratio !== expectedAspectRatio ||
    routing.resolvedInput.aspectRatio !== expectedAspectRatio ||
    routing.resolvedInput.resolution !== RUNWAY_PREFLIGHT_RESOLUTION
  ) {
    return { ok: false, reason: 'RESOLVED_INPUT_MISMATCH' };
  }

  return {
    ok: true,
    decision: {
      model: RUNWAY_IMAGE_MODEL,
      configId: routing.configId,
      optimizeFor: routing.resolvedSettings.optimizeFor,
      pricing: {
        estimatedCostCredits: routing.estimatedCost.credits,
        routerCeilingCredits: priceCeiling,
        providerBoundMaximumCredits: null,
        reservationBoundCredits: 0,
      },
      aspectRatio: routing.resolvedInput.aspectRatio,
      resolution: RUNWAY_PREFLIGHT_RESOLUTION,
    },
  };
}

export function isRunwayRouterConfigId(value: string): boolean {
  return /^[a-z0-9][a-z0-9-]{0,62}$/.test(value);
}

export function isTrustedRunwayApiBaseUrl(value: string): boolean {
  try {
    const parsedUrl = new URL(value);
    return (
      parsedUrl.origin === 'https://api.dev.runwayml.com' &&
      parsedUrl.pathname === '/' &&
      parsedUrl.search.length === 0 &&
      parsedUrl.hash.length === 0
    );
  } catch {
    return false;
  }
}
