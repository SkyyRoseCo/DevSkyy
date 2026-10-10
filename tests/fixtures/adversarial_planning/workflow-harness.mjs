import fs from "node:fs";
import { webcrypto } from "node:crypto";

if (!globalThis.crypto) {
  Object.defineProperty(globalThis, "crypto", { value: webcrypto });
}

const payload = JSON.parse(fs.readFileSync(0, "utf8"));
const source = fs
  .readFileSync(payload.workflowPath, "utf8")
  .replace(/^export const meta =/m, "const meta =");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const workflow = new AsyncFunction("args", "phase", "agent", "log", source);
const phases = [];
const calls = [];
let debateIndex = 0;
const agent = async (prompt, options) => {
  calls.push({
    label: options.label,
    model: options.model,
    prompt,
  });
  if (options.label.startsWith("claude-fable-codex-debate-r")) {
    return payload.debate[debateIndex++];
  }
  if (options.label === "claude-fable-codex-execution-relay") {
    return payload.execution;
  }
  if (options.label === "claude-fable-independent-execution-review") {
    return payload.review;
  }
  throw new Error("unexpected mock agent label");
};
const result = await workflow(
  payload.args,
  (name) => phases.push(name),
  agent,
  () => {},
);
process.stdout.write(JSON.stringify({ result, phases, calls }));
