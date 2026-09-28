/**
 * Closed router-configuration interlock.
 *
 * A live router is configured, but this application does not bind its ID,
 * version, and settings digest to server runtime. A dry-run response cannot
 * establish that binding, so keep the route closed until it is implemented.
 */
export type RunwayRouterConfigurationGate = {
  ready: false;
  reason: 'ROUTER_CONFIGURATION_NOT_RUNTIME_BOUND';
};

export function getRunwayRouterConfigurationGate(): RunwayRouterConfigurationGate {
  return { ready: false, reason: 'ROUTER_CONFIGURATION_NOT_RUNTIME_BOUND' };
}
