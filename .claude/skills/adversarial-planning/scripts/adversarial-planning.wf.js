export const meta = {
  name: "adversarial-planning",
  description:
    "Fail-closed Workflow adapter. Use the local CLI until this runtime can attest providers and atomically consume execution approvals.",
  whenToUse:
    "This adapter is intentionally blocked. Run adversarial planning through the local CLI.",
  phases: [{ title: "Preflight" }],
};

return {
  status: "BLOCKED",
  reason:
    "Workflow has no verified fresh Claude/Codex provider attestation, trusted direct Codex response channel, or durable atomic one-time execution ledger. Use the local_cli route.",
};
