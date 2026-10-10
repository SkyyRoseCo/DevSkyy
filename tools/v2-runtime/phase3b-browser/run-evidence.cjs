const fs = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');

/** Invalidate a previous receipt before work starts; sidecars also cover array outputs. */
function beginRun(output) {
  const runId = randomUUID();
  const startedAt = new Date().toISOString();
  const sidecar = output.replace(/\.json$/, '') + '.run.json';
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const write = (file, value) => {
    const temporary = file + '.' + runId + '.tmp';
    fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n');
    fs.renameSync(temporary, file);
  };
  const record = (status, extra = {}) => ({ runId, startedAt, status, artifact: path.basename(output), ...extra });
  const running = record('RUNNING');
  write(sidecar, running);
  write(output, running);
  return {
    pass(value) {
      const receipt = record('PASS', { finishedAt: new Date().toISOString() });
      write(output, Array.isArray(value) ? value : { ...value, ...receipt });
      write(sidecar, receipt);
    },
    fail(error, details = {}) {
      const receipt = record('FAIL', { finishedAt: new Date().toISOString(), error: error?.stack || String(error) });
      write(output, { ...details, ...receipt });
      write(sidecar, receipt);
    },
  };
}

module.exports = { beginRun };
