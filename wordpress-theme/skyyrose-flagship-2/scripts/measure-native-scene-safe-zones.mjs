#!/usr/bin/env node

import { execFile, spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const execFileAsync = promisify(execFile);
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const themeDir = path.resolve(scriptDir, '..');
const repoDir = path.resolve(themeDir, '..', '..');
const baseDir = path.join(
  themeDir,
  'assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/preflight-v1',
);
const contractPath = path.join(
  baseDir,
  'vision-authored-prompts/lh-commerce-1-native-scene-regeneration-plan-v1.json',
);
const outputPath = path.join(baseDir, 'lh-commerce-1-responsive-safe-zones-v1.json');
const screenshotDir = path.join(baseDir, 'safe-zone-captures-v1');
const chromePath =
  process.env.SKYYROSE_CHROME_PATH ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const renderSourcePaths = [
  'tools/v2-theme-preview.php',
  'wordpress-theme/skyyrose-flagship-2/template-collection.php',
  'wordpress-theme/skyyrose-flagship-2/functions.php',
  'wordpress-theme/skyyrose-flagship-2/data/scene-narrative-blueprints.json',
  'wordpress-theme/skyyrose-flagship-2/data/founder-selected-theme-placeholders-v1.json',
  'wordpress-theme/skyyrose-flagship-2/data/product-presentation-registry.json',
  'wordpress-theme/skyyrose-flagship-2/assets/css/design-tokens.css',
  'wordpress-theme/skyyrose-flagship-2/assets/css/theme.css',
  'wordpress-theme/skyyrose-flagship-2/assets/js/theme.js',
  'wordpress-theme/skyyrose-flagship-2/assets/js/house-of-roses-motion.js',
  'wordpress-theme/skyyrose-flagship-2/assets/js/kids-capsule-reveal.js',
  'wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/archivo-latin.woff2',
  'wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/hanken-grotesk-latin.woff2',
  'wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/anton-latin.woff2',
  'wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/cinzel-latin.woff2',
  'wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/inter-latin.woff2',
];
const viewports = [
  { id: 'desktop', width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false },
  { id: 'tablet', width: 768, height: 1024, deviceScaleFactor: 1, mobile: false },
  { id: 'mobile', width: 390, height: 844, deviceScaleFactor: 1, mobile: true },
];
const commandTimeoutMs = 20_000;

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function wait(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function readJson(filePath) {
  const value = JSON.parse(await fs.readFile(filePath, 'utf8'));
  if (!value || Array.isArray(value) || typeof value !== 'object') {
    throw new Error(`JSON root must be an object: ${filePath}`);
  }
  return value;
}

async function writeFileAtomic(filePath, bytes) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  const temporary = `${filePath}.${process.pid}.${crypto.randomUUID()}.tmp`;
  const handle = await fs.open(temporary, 'wx');
  try {
    await handle.writeFile(bytes);
    await handle.sync();
  } finally {
    await handle.close();
  }
  try {
    await fs.rename(temporary, filePath);
  } finally {
    await fs.rm(temporary, { force: true });
  }
}

async function writeJsonAtomic(filePath, value) {
  await writeFileAtomic(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

class CdpClient {
  constructor(url) {
    this.socket = new WebSocket(url);
    this.nextId = 1;
    this.pending = new Map();
    this.closedError = null;
    this.opened = new Promise((resolve, reject) => {
      const timeout = setTimeout(
        () => reject(new Error('Chrome DevTools WebSocket open timed out')),
        commandTimeoutMs,
      );
      this.socket.addEventListener('open', () => {
        clearTimeout(timeout);
        resolve();
      }, { once: true });
      this.socket.addEventListener('error', () => {
        clearTimeout(timeout);
        reject(new Error('Chrome DevTools WebSocket failed to open'));
      }, { once: true });
    });
    this.socket.addEventListener('message', (event) => {
      let message;
      try {
        message = JSON.parse(event.data);
      } catch {
        this.failPending(new Error('Chrome DevTools returned malformed JSON'));
        return;
      }
      if (!message.id || !this.pending.has(message.id)) return;
      const pending = this.pending.get(message.id);
      this.pending.delete(message.id);
      clearTimeout(pending.timeout);
      if (message.error) pending.reject(new Error(message.error.message));
      else pending.resolve(message.result);
    });
    this.socket.addEventListener('close', () => {
      this.closedError = new Error('Chrome DevTools WebSocket closed');
      this.failPending(this.closedError);
    });
    this.socket.addEventListener('error', () => {
      this.closedError = new Error('Chrome DevTools WebSocket failed');
      this.failPending(this.closedError);
    });
  }

  failPending(error) {
    for (const pending of this.pending.values()) {
      clearTimeout(pending.timeout);
      pending.reject(error);
    }
    this.pending.clear();
  }

  async send(method, params = {}) {
    await this.opened;
    if (this.closedError) throw this.closedError;
    const id = this.nextId++;
    const response = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Chrome DevTools command timed out: ${method}`));
      }, commandTimeoutMs);
      this.pending.set(id, { resolve, reject, timeout });
    });
    this.socket.send(JSON.stringify({ id, method, params }));
    return response;
  }

  close() {
    this.failPending(new Error('Chrome DevTools client closed'));
    if (this.socket.readyState < WebSocket.CLOSING) this.socket.close();
  }
}

async function freeLoopbackPort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      const port = typeof address === 'object' && address ? address.port : 0;
      server.close((error) => (error ? reject(error) : resolve(port)));
    });
  });
}

async function waitForHttp(url) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(url, { redirect: 'error' });
      if (response.ok) return response;
    } catch {
      // The current-worktree PHP server may still be starting.
    }
    await wait(100);
  }
  throw new Error('Current-worktree V2 preview did not become available');
}

async function waitForPageTarget(port) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/list`);
      const targets = await response.json();
      const page = targets.find((target) => target.type === 'page');
      if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch {
      // Chrome may not have opened the debugging endpoint yet.
    }
    await wait(100);
  }
  throw new Error('Chrome DevTools page target did not become available');
}

async function terminateProcess(child) {
  if (!child || child.exitCode !== null || child.signalCode !== null) return;
  child.kill('SIGTERM');
  const exited = await Promise.race([
    new Promise((resolve) => child.once('exit', () => resolve(true))),
    wait(2000).then(() => false),
  ]);
  if (!exited && child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL');
    await Promise.race([
      new Promise((resolve) => child.once('exit', resolve)),
      wait(2000),
    ]);
  }
}

async function waitForReady(client) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const result = await client.send('Runtime.evaluate', {
      expression:
        "document.readyState === 'complete' && Boolean(document.querySelector('[data-scene-id=\"lh-commerce-1\"] .sr2-world__scene-image'))",
      returnByValue: true,
    });
    if (result.result.value === true) return;
    await wait(100);
  }
  throw new Error('V2 preview did not reach a measurable ready state');
}

const measurementExpression = `
(async () => {
  const scene = document.querySelector('[data-scene-id="lh-commerce-1"]');
  if (!scene) throw new Error('LH-COMMERCE-1 scene is missing');
  const stage = document.querySelector('#world')?.querySelector('[data-scroll-world-stage]');
  if (!stage) throw new Error('Scroll World stage is missing');
  const header = document.querySelector('.sr2-header');
  if (!header) throw new Error('Rendered V2 header is missing');
  const stageTop = stage.getBoundingClientRect().top + window.scrollY;
  const headerHeight = header.getBoundingClientRect().height;
  window.scrollTo({ top: Math.max(0, stageTop - headerHeight), behavior: 'instant' });
  const rail = scene.closest('[data-horizontal-rail]');
  if (rail) rail.scrollLeft = 0;
  const stabilityStyle = document.createElement('style');
  stabilityStyle.dataset.skyyroseMeasurement = 'true';
  stabilityStyle.textContent = '*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.sr2-preview-banner{display:none!important}';
  document.head.appendChild(stabilityStyle);
  await document.fonts.ready;
  const image = scene.querySelector('.sr2-world__scene-image');
  if (!image) throw new Error('LH-COMMERCE-1 scene image is missing');
  if (!image.complete) {
    await Promise.race([
      new Promise((resolve) => image.addEventListener('load', resolve, { once: true })),
      new Promise((_, reject) => image.addEventListener('error', () => reject(new Error('scene image failed to load')), { once: true })),
      new Promise((_, reject) => setTimeout(() => reject(new Error('scene image load timed out')), 10000)),
    ]);
  }
  if (image.decode) await image.decode();
  if (!image.naturalWidth || !image.naturalHeight) throw new Error('scene image has no intrinsic dimensions');
  const rectArray = (element) => {
    if (!element) throw new Error('required measured element is missing');
    const rect = element.getBoundingClientRect();
    return [rect.left, rect.top, rect.right, rect.bottom].map((value) => Number(value.toFixed(3)));
  };
  const geometry = () => ({
    image: rectArray(image),
    header: rectArray(header),
    products: rectArray(scene.querySelector('.sr2-world__products')),
    copy: rectArray(scene.querySelector('.sr2-world__copy')),
  });
  const first = geometry();
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  await new Promise((resolve) => setTimeout(resolve, 250));
  const second = geometry();
  if (JSON.stringify(first) !== JSON.stringify(second)) throw new Error('rendered scene geometry did not stabilize');
  const imageBox = image.getBoundingClientRect();
  const computed = getComputedStyle(image);
  if (computed.objectFit !== 'cover' || computed.objectPosition !== '50% 50%') {
    throw new Error('unsupported image crop transform: ' + computed.objectFit + ' / ' + computed.objectPosition);
  }
  const scale = Math.max(imageBox.width / image.naturalWidth, imageBox.height / image.naturalHeight);
  const renderedWidth = image.naturalWidth * scale;
  const renderedHeight = image.naturalHeight * scale;
  const offsetX = (imageBox.width - renderedWidth) / 2;
  const offsetY = (imageBox.height - renderedHeight) / 2;
  const clamp = (value) => Math.max(0, Math.min(1, value));
  const normalizeRect = (rect, id) => ({
    id,
    rect: [
      clamp((rect.left - imageBox.left - offsetX) / renderedWidth),
      clamp((rect.top - imageBox.top - offsetY) / renderedHeight),
      clamp((rect.right - imageBox.left - offsetX) / renderedWidth),
      clamp((rect.bottom - imageBox.top - offsetY) / renderedHeight),
    ].map((value) => Number(value.toFixed(6))),
    viewport_rect: [rect.left, rect.top, rect.right, rect.bottom].map((value) => Number(value.toFixed(2))),
  });
  const normalize = (element, id) => {
    if (!element) throw new Error('Missing UI safe-zone element: ' + id);
    return normalizeRect(element.getBoundingClientRect(), id);
  };
  const keepClear = [
    normalize(scene.querySelector('.sr2-world__products'), 'shopping_ui_product_links_and_price'),
    normalize(scene.querySelector('.sr2-world__copy'), 'scene_copy_and_primary_cta'),
  ];
  const headerBox = header.getBoundingClientRect();
  const intersection = {
    left: Math.max(headerBox.left, imageBox.left),
    top: Math.max(headerBox.top, imageBox.top),
    right: Math.min(headerBox.right, imageBox.right),
    bottom: Math.min(headerBox.bottom, imageBox.bottom),
  };
  if (intersection.left < intersection.right && intersection.top < intersection.bottom) {
    keepClear.unshift(normalizeRect(intersection, 'global_navigation'));
  }
  const body = document.body;
  return {
    scene_id: scene.dataset.sceneId,
    preview_identity: {
      route: body.dataset.previewRoute,
      theme: body.dataset.previewTheme,
      candidate: body.dataset.previewCandidate,
      commit: body.dataset.previewCommit,
      template: document.querySelector('meta[name="skyyrose-preview-template"]')?.content,
    },
    source_image: image.currentSrc || image.src,
    source_dimensions: [image.naturalWidth, image.naturalHeight],
    image_element_rect: [imageBox.left, imageBox.top, imageBox.right, imageBox.bottom].map((value) => Number(value.toFixed(2))),
    image_document_rect: [imageBox.left + window.scrollX, imageBox.top + window.scrollY, imageBox.right + window.scrollX, imageBox.bottom + window.scrollY].map((value) => Number(value.toFixed(2))),
    crop_transform: {
      scale: Number(scale.toFixed(8)),
      rendered_dimensions: [Number(renderedWidth.toFixed(3)), Number(renderedHeight.toFixed(3))],
      offset: [Number(offsetX.toFixed(3)), Number(offsetY.toFixed(3))],
      object_fit: computed.objectFit,
      object_position: computed.objectPosition,
    },
    keep_clear: keepClear,
  };
})()
`;

async function localIdentity() {
  const handoff = await readJson(path.join(repoDir, '.fashion-theme/codex-desktop-handoff.json'));
  const { stdout } = await execFileAsync('git', ['-C', repoDir, 'rev-parse', 'HEAD']);
  return { candidate: handoff.candidate?.candidate_id, commit: stdout.trim() };
}

async function main() {
  const major = Number(process.versions.node.split('.')[0]);
  if (major < 22 || typeof WebSocket !== 'function') {
    throw new Error('Node 22 or newer is required for the hardened CDP client');
  }
  await fs.access(chromePath);
  const contractBytes = await fs.readFile(contractPath);
  const contract = JSON.parse(contractBytes);
  const contractHash = sha256(contractBytes);
  await writeJsonAtomic(outputPath, {
    schema: 'skyyrose.native-scene-responsive-safe-zones.v1',
    status: 'BLOCKED_MEASUREMENT_IN_PROGRESS',
    attempted_at: new Date().toISOString(),
    scene_id: 'LH-COMMERCE-1',
    contract_sha256: contractHash,
  });
  const plate = contract.bindings?.generator_conditioning_references?.find(
    (item) => item.role === 'locked_environment_composition_reference',
  );
  if (!plate?.path || !plate.sha256) throw new Error('contract has no locked environment binding');
  const plateBytes = await fs.readFile(path.join(repoDir, plate.path));
  if (sha256(plateBytes) !== plate.sha256) throw new Error('locked environment bytes changed');
  if (JSON.stringify(plate.dimensions) !== JSON.stringify(contract.output_contract?.dimensions)) {
    throw new Error('locked environment and output dimensions differ');
  }
  const renderSourceBindings = await Promise.all(
    renderSourcePaths.map(async (relativePath) => {
      const bytes = await fs.readFile(path.join(repoDir, relativePath));
      return { path: relativePath, sha256: sha256(bytes), bytes: bytes.length };
    }),
  );
  const identity = await localIdentity();
  if (!identity.candidate || !/^[a-f0-9]{40}$/.test(identity.commit)) {
    throw new Error('current V2 worktree identity is incomplete');
  }

  const phpPort = await freeLoopbackPort();
  const pageUrl = `http://127.0.0.1:${phpPort}/tools/v2-theme-preview.php?route=love-hurts`;
  const php = spawn('php', ['-S', `127.0.0.1:${phpPort}`, '-t', repoDir], {
    cwd: repoDir,
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  const profile = await fs.mkdtemp(path.join(os.tmpdir(), 'skyyrose-safe-zones-'));
  let chrome;
  let client;
  try {
    const previewResponse = await waitForHttp(pageUrl);
    if (
      previewResponse.headers.get('x-skyyrose-preview-candidate') !== identity.candidate ||
      previewResponse.headers.get('x-skyyrose-preview-commit') !== identity.commit ||
      previewResponse.headers.get('x-skyyrose-preview-route') !== 'love-hurts' ||
      previewResponse.headers.get('x-skyyrose-preview-template') !== 'template-collection.php'
    ) {
      throw new Error('V2 preview headers do not match the current worktree identity');
    }
    const servedPlate = Buffer.from(
      await (await fetch(new URL(`/${plate.path}`, pageUrl))).arrayBuffer(),
    );
    if (sha256(servedPlate) !== plate.sha256) {
      throw new Error('V2 preview serves a stale or different scene plate');
    }
    for (const relativePath of renderSourcePaths.filter(
      (item) => item.startsWith('wordpress-theme/') && !item.endsWith('.php'),
    )) {
      const served = Buffer.from(
        await (await fetch(new URL(`/${relativePath}`, pageUrl))).arrayBuffer(),
      );
      const binding = renderSourceBindings.find((item) => item.path === relativePath);
      if (!binding || sha256(served) !== binding.sha256) {
        throw new Error(`V2 preview serves stale rendered code: ${relativePath}`);
      }
    }

    let debugEndpoint = '';
    chrome = spawn(
      chromePath,
      [
        '--headless=new',
        '--disable-gpu',
        '--no-first-run',
        '--no-default-browser-check',
        '--remote-debugging-port=0',
        `--user-data-dir=${profile}`,
        pageUrl,
      ],
      { stdio: ['ignore', 'ignore', 'pipe'] },
    );
    chrome.stderr.setEncoding('utf8');
    chrome.stderr.on('data', (chunk) => {
      const match = chunk.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) debugEndpoint = match[1];
    });
    for (let attempt = 0; attempt < 100 && !debugEndpoint; attempt += 1) await wait(100);
    if (!debugEndpoint) throw new Error('Chrome did not expose a DevTools endpoint');
    client = new CdpClient(await waitForPageTarget(Number(new URL(debugEndpoint).port)));
    await client.send('Page.enable');
    await client.send('Runtime.enable');
    const measurements = [];
    for (const viewport of viewports) {
      await client.send('Emulation.setDeviceMetricsOverride', {
        width: viewport.width,
        height: viewport.height,
        deviceScaleFactor: viewport.deviceScaleFactor,
        mobile: viewport.mobile,
      });
      await client.send('Page.navigate', { url: pageUrl });
      await waitForReady(client);
      const evaluated = await client.send('Runtime.evaluate', {
        expression: measurementExpression,
        awaitPromise: true,
        returnByValue: true,
      });
      if (evaluated.exceptionDetails) {
        throw new Error(
          evaluated.exceptionDetails.exception?.description || 'safe-zone evaluation failed',
        );
      }
      const measurement = evaluated.result.value;
      if (
        measurement.preview_identity.candidate !== identity.candidate ||
        measurement.preview_identity.commit !== identity.commit ||
        measurement.preview_identity.route !== 'love-hurts' ||
        measurement.preview_identity.template !== 'template-collection.php'
      ) {
        throw new Error(`rendered preview identity drifted at ${viewport.id}`);
      }
      const sourceUrl = new URL(measurement.source_image);
      if (sourceUrl.origin !== new URL(pageUrl).origin || sourceUrl.pathname !== `/${plate.path}`) {
        throw new Error(`rendered scene source path drifted at ${viewport.id}`);
      }
      if (JSON.stringify(measurement.source_dimensions) !== JSON.stringify(plate.dimensions)) {
        throw new Error(`rendered scene dimensions drifted at ${viewport.id}`);
      }
      await client.send('Runtime.evaluate', {
        expression: `(() => {
          document.querySelectorAll('[data-skyyrose-safe-zone-overlay]').forEach((node) => node.remove());
          for (const zone of ${JSON.stringify(measurement.keep_clear)}) {
            const [left, top, right, bottom] = zone.viewport_rect;
            const overlay = document.createElement('div');
            overlay.dataset.skyyroseSafeZoneOverlay = zone.id;
            overlay.style.cssText = 'position:absolute;z-index:2147483647;pointer-events:none;border:3px solid #00ffff;background:rgba(0,255,255,.12);color:#001414;font:700 12px/1.2 monospace;padding:3px;box-sizing:border-box';
            overlay.style.left = (left + window.scrollX) + 'px';
            overlay.style.top = (top + window.scrollY) + 'px';
            overlay.style.width = Math.max(1, right - left) + 'px';
            overlay.style.height = Math.max(1, bottom - top) + 'px';
            overlay.textContent = zone.id;
            document.body.appendChild(overlay);
          }
        })()`,
      });
      const [left, top, right, bottom] = measurement.image_document_rect;
      const screenshot = await client.send('Page.captureScreenshot', {
        format: 'png',
        captureBeyondViewport: true,
        fromSurface: true,
        clip: {
          x: Math.max(0, left),
          y: Math.max(0, top),
          width: right - left,
          height: bottom - top,
          scale: 1,
        },
      });
      const screenshotBuffer = Buffer.from(screenshot.data, 'base64');
      const screenshotPath = path.join(screenshotDir, `lh-commerce-1-${viewport.id}.png`);
      await writeFileAtomic(screenshotPath, screenshotBuffer);
      const written = await fs.readFile(screenshotPath);
      if (sha256(written) !== sha256(screenshotBuffer)) {
        throw new Error(`safe-zone screenshot write was not stable: ${viewport.id}`);
      }
      measurements.push({
        id: viewport.id,
        viewport: [viewport.width, viewport.height],
        measurement_source: 'rendered_v2_dom',
        screenshot: path.relative(repoDir, screenshotPath),
        screenshot_sha256: sha256(screenshotBuffer),
        source_image_sha256: plate.sha256,
        ...measurement,
      });
    }
    await writeJsonAtomic(outputPath, {
      schema: 'skyyrose.native-scene-responsive-safe-zones.v1',
      status: 'PASS_MEASURED_SAFE_ZONES',
      measured_at: new Date().toISOString(),
      scene_id: 'LH-COMMERCE-1',
      contract: path.relative(repoDir, contractPath),
      contract_sha256: contractHash,
      coordinate_space: 'normalized_generation_frame',
      preview_url: pageUrl,
      preview_identity: {
        route: 'love-hurts',
        template: 'template-collection.php',
        theme: measurements[0].preview_identity.theme,
        candidate: identity.candidate,
        commit: identity.commit,
      },
      source_asset: { path: plate.path, sha256: plate.sha256, dimensions: plate.dimensions },
      render_source_bindings: renderSourceBindings,
      breakpoints: measurements,
      generation_rule:
        'Every model, required product region, and enchanted rose must remain outside every keep-clear rectangle.',
    });
    console.log(`PASS_MEASURED_SAFE_ZONES breakpoints=${measurements.length} receipt=${outputPath}`);
  } finally {
    if (client) client.close();
    await terminateProcess(chrome);
    await terminateProcess(php);
    await fs.rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
}

main().catch(async (error) => {
  const contractBytes = await fs.readFile(contractPath).catch(() => null);
  await writeJsonAtomic(outputPath, {
    schema: 'skyyrose.native-scene-responsive-safe-zones.v1',
    status: 'BLOCKED_SAFE_ZONE_MEASUREMENT',
    attempted_at: new Date().toISOString(),
    scene_id: 'LH-COMMERCE-1',
    contract_sha256: contractBytes ? sha256(contractBytes) : null,
    reason: error instanceof Error ? error.message : 'unknown safe-zone measurement failure',
  }).catch(() => {});
  console.error(
    `BLOCKED_SAFE_ZONE_MEASUREMENT ${error instanceof Error ? error.message : 'unknown failure'}`,
  );
  process.exitCode = 1;
});
