import { describe, expect, it } from 'vitest';

import {
  buildRunwayDryRunPayload,
  isRunwayRouterConfigId,
  isTrustedRunwayApiBaseUrl,
  RUNWAY_IMAGE_MODEL,
  RUNWAY_MAX_IMAGE_CREDITS,
  RUNWAY_PREFLIGHT_PROMPT,
  RunwayPreflightBodySchema,
  validateRunwayDryRunResponse,
} from '../app/api/runway-dev/dry-run/contract';

const CONFIG_ID = 'skyyrose-image-preflight';
const ASPECT_RATIO = '4:5';

function validDryRunResponse() {
  return {
    dryRun: true,
    routing: {
      model: RUNWAY_IMAGE_MODEL,
      configId: CONFIG_ID,
      resolvedSettings: {
        optimizeFor: 'quality',
        priceCeiling: RUNWAY_MAX_IMAGE_CREDITS,
      },
      resolvedInput: {
        ratio: '4:5',
        aspectRatio: ASPECT_RATIO,
        resolution: '2k',
      },
      estimatedCost: { credits: 16 },
    },
  };
}

describe('Runway Dev image router dry-run contract', () => {
  it('builds a synthetic, single-image request with no references and dryRun enabled', () => {
    const payload = buildRunwayDryRunPayload(CONFIG_ID, ASPECT_RATIO);

    expect(payload).toEqual({
      configId: CONFIG_ID,
      dryRun: true,
      input: {
        promptText: RUNWAY_PREFLIGHT_PROMPT,
        aspectRatio: ASPECT_RATIO,
        resolution: '2k',
        outputCount: 1,
      },
    });
    expect('referenceImages' in payload.input).toBe(false);
  });

  it('rejects caller-supplied prompts, model overrides, and reference uploads', () => {
    expect(RunwayPreflightBodySchema.safeParse({ aspectRatio: ASPECT_RATIO }).success).toBe(true);
    expect(
      RunwayPreflightBodySchema.safeParse({
        aspectRatio: ASPECT_RATIO,
        promptText: 'caller content',
      }).success
    ).toBe(false);
    expect(
      RunwayPreflightBodySchema.safeParse({
        aspectRatio: ASPECT_RATIO,
        referenceImages: [{ uri: 'https://example.test/image.png' }],
      }).success
    ).toBe(false);
    expect(RunwayPreflightBodySchema.safeParse({ model: 'gpt_image_2_5_flare' }).success).toBe(false);
    expect(RunwayPreflightBodySchema.safeParse({ outputCount: 10 }).success).toBe(false);
  });

  it('accepts only the fixed Runway API host and a slug-shaped config ID', () => {
    expect(isTrustedRunwayApiBaseUrl('https://api.dev.runwayml.com')).toBe(true);
    expect(isTrustedRunwayApiBaseUrl('https://example.test')).toBe(false);
    expect(isTrustedRunwayApiBaseUrl('http://api.dev.runwayml.com')).toBe(false);
    expect(isRunwayRouterConfigId('skyyrose-image-preflight')).toBe(true);
    expect(isRunwayRouterConfigId('../other-host')).toBe(false);
  });

  it('accepts a dry-run decision only for the pinned model, config, input, and bounded estimate', () => {
    const result = validateRunwayDryRunResponse(validDryRunResponse(), CONFIG_ID, ASPECT_RATIO);

    expect(result).toMatchObject({
      ok: true,
      decision: {
        model: RUNWAY_IMAGE_MODEL,
        configId: CONFIG_ID,
        pricing: {
          estimatedCostCredits: 16,
          routerCeilingCredits: RUNWAY_MAX_IMAGE_CREDITS,
          providerBoundMaximumCredits: null,
          reservationBoundCredits: 0,
        },
        aspectRatio: ASPECT_RATIO,
        resolution: '2k',
      },
    });
  });

  it.each([
    ['live task response', { ...validDryRunResponse(), dryRun: false }, 'DRY_RUN_NOT_CONFIRMED'],
    [
      'task identifier in a dry-run response',
      { ...validDryRunResponse(), id: 'unexpected-task-id' },
      'TASK_ID_RETURNED',
    ],
    ['artifact returned by a dry-run response', { ...validDryRunResponse(), outputs: [] }, 'ARTIFACT_RETURNED'],
    [
      'different router config',
      {
        ...validDryRunResponse(),
        routing: { ...validDryRunResponse().routing, configId: 'other-config' },
      },
      'ROUTER_CONFIG_MISMATCH',
    ],
    [
      'fallback model',
      {
        ...validDryRunResponse(),
        routing: { ...validDryRunResponse().routing, model: 'gpt_image_2_5_flare' },
      },
      'MODEL_NOT_ALLOWLISTED',
    ],
    [
      'router without a ceiling',
      {
        ...validDryRunResponse(),
        routing: {
          ...validDryRunResponse().routing,
          resolvedSettings: { optimizeFor: 'quality', priceCeiling: null },
        },
      },
      'PRICE_CEILING_MISSING',
    ],
    [
      'router ceiling above policy',
      {
        ...validDryRunResponse(),
        routing: {
          ...validDryRunResponse().routing,
          resolvedSettings: { optimizeFor: 'quality', priceCeiling: RUNWAY_MAX_IMAGE_CREDITS + 1 },
        },
      },
      'PRICE_CEILING_OUT_OF_POLICY',
    ],
    [
      'estimate above the router ceiling',
      {
        ...validDryRunResponse(),
        routing: {
          ...validDryRunResponse().routing,
          resolvedSettings: { optimizeFor: 'quality', priceCeiling: 8 },
          estimatedCost: { credits: 9 },
        },
      },
      'ESTIMATE_EXCEEDS_CEILING',
    ],
    [
      'provider-resolved ratio mismatch',
      {
        ...validDryRunResponse(),
        routing: {
          ...validDryRunResponse().routing,
          resolvedInput: { ratio: '1:1', aspectRatio: ASPECT_RATIO, resolution: '2k' },
        },
      },
      'RESOLVED_INPUT_MISMATCH',
    ],
  ] as const)('fails closed for %s', (_caseName, response, reason) => {
    expect(validateRunwayDryRunResponse(response, CONFIG_ID, ASPECT_RATIO)).toEqual({
      ok: false,
      reason,
    });
  });
});
