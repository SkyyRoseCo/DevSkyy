/**
 * Closed interlock for the missing Scarce Resource Governor integration.
 *
 * This checkout does not contain the verified Governor candidate or its quota
 * reservation/audit API. Keep provider requests denied until the real
 * Governor-owned authorization contract is available and wired here. An
 * environment flag must not be used to simulate that authorization.
 */
export type RunwayDryRunGovernorAuthorization = {
  authorized: true;
} | {
  authorized: false;
  reason: 'SCARCE_RESOURCE_GOVERNOR_UNAVAILABLE';
};

export function authorizeRunwayDryRunQuotaOperation(): RunwayDryRunGovernorAuthorization {
  return {
    authorized: false,
    reason: 'SCARCE_RESOURCE_GOVERNOR_UNAVAILABLE',
  };
}
