'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('playwright');
const sharp = require('sharp');

const themeDir = path.resolve(__dirname, '..');
const evidenceDir = path.join(
  themeDir,
  'assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/evidence/rendered'
);
const baseUrl = process.env.SR2_COMMERCE_PREVIEW_URL;

if (!baseUrl) {
  throw new Error('SR2_COMMERCE_PREVIEW_URL is required. Run the shell wrapper instead of invoking this file directly.');
}

const collections = {
  'black-rose': ['br-commerce-1', 'br-commerce-2', 'br-commerce-3'],
  'love-hurts': ['lh-commerce-1', 'lh-commerce-2', 'lh-commerce-3'],
  signature: ['sig-commerce-1', 'sig-commerce-2', 'sig-commerce-3'],
};
const viewports = {
  'desktop-1440x900': { width: 1440, height: 900 },
  'tablet-768x1024': { width: 768, height: 1024 },
  'mobile-390x844': { width: 390, height: 844 },
};

async function makeContactSheet(viewportName, viewport, records) {
  const tileWidth = 480;
  const tileHeight = Math.round((tileWidth * viewport.height) / viewport.width);
  const tiles = [];
  for (const [index, record] of records.entries()) {
    const image = await sharp(record.file)
      .resize(tileWidth, tileHeight, { fit: 'contain', background: '#080808' })
      .composite([
        {
          input: Buffer.from(
            `<svg width="${tileWidth}" height="${tileHeight}"><rect x="0" y="${tileHeight - 38}" width="${tileWidth}" height="38" fill="rgba(0,0,0,.82)"/><text x="14" y="${tileHeight - 13}" fill="#fff" font-family="Arial, sans-serif" font-size="18">${record.collection} · ${record.sceneId}</text></svg>`
          ),
        },
      ])
      .png()
      .toBuffer();
    tiles.push({
      input: image,
      left: (index % 3) * tileWidth,
      top: Math.floor(index / 3) * tileHeight,
    });
  }
  await sharp({
    create: {
      width: tileWidth * 3,
      height: tileHeight * 3,
      channels: 4,
      background: '#080808',
    },
  })
    .composite(tiles)
    .png()
    .toFile(path.join(evidenceDir, `${viewportName}-contact-sheet.png`));
}

async function run() {
  await fs.mkdir(evidenceDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const records = [];
  const errors = [];

  try {
    for (const [viewportName, viewport] of Object.entries(viewports)) {
      const context = await browser.newContext({ viewport, reducedMotion: 'reduce' });
      const page = await context.newPage();
      page.on('pageerror', (error) => errors.push(`${viewportName}: ${error.message}`));

      for (const [collection, sceneIds] of Object.entries(collections)) {
        for (const sceneId of sceneIds) {
          await page.goto(`${baseUrl}?route=${collection}`, {
            waitUntil: 'networkidle',
            timeout: 30_000,
          });
          await page.addStyleTag({
            content: '*,*::before,*::after{animation-duration:0s!important;transition-duration:0s!important;scroll-behavior:auto!important}.sr2-preview-banner,[data-site-header],.sr2-skip{display:none!important}',
          });
          await page.evaluate(() => document.fonts?.ready);

          const documentOverflow = await page.evaluate(
            () => document.documentElement.scrollWidth - document.documentElement.clientWidth
          );
          if (documentOverflow > 1) {
            throw new Error(`${collection} at ${viewportName} has ${documentOverflow}px document overflow`);
          }

          const scene = page.locator(`[data-scene-id="${sceneId}"]`);
          if ((await scene.count()) !== 1) {
            throw new Error(`${collection}/${sceneId} must resolve to exactly one rendered scene`);
          }
          const sceneBox = await scene.boundingBox();
          if (!sceneBox || sceneBox.width < 1) {
            throw new Error(`${collection}/${sceneId} has no measurable render box`);
          }
          await page.evaluate(
            ({ targetSceneId, targetWidth }) => {
              const target = document.querySelector(`[data-scene-id="${targetSceneId}"]`);
              const world = target?.closest('[data-horizontal-world]');
              const stage = target?.closest('[data-scroll-world-stage]');
              const rail = target?.closest('[data-horizontal-rail]');
              if (!target || !world || !stage || !rail) {
                throw new Error(`Unable to isolate ${targetSceneId}`);
              }
              world.classList.remove('is-scroll-world');
              world.style.height = 'auto';
              stage.style.height = 'auto';
              rail.style.display = 'block';
              rail.style.overflow = 'visible';
              rail.style.padding = '0';
              rail.style.transform = 'none';
              for (const candidate of rail.querySelectorAll('[data-scene-id]')) {
                candidate.style.display = candidate === target ? 'block' : 'none';
              }
              target.style.width = `${Math.round(targetWidth)}px`;
              target.style.margin = '0 auto';
              for (const image of target.querySelectorAll('img')) {
                image.loading = 'eager';
              }
            },
            { targetSceneId: sceneId, targetWidth: sceneBox.width }
          );
          await scene.scrollIntoViewIfNeeded();
          await scene.locator('img').evaluateAll(async (images) => {
            await Promise.all(
              images.map(async (image) => {
                if (!image.complete || image.naturalWidth < 1) {
                  await new Promise((resolve, reject) => {
                    image.addEventListener('load', resolve, { once: true });
                    image.addEventListener('error', reject, { once: true });
                  });
                }
                if (typeof image.decode === 'function') {
                  await image.decode();
                }
              })
            );
          });
          if ((await scene.getAttribute('data-scene-id')) !== sceneId) {
            throw new Error(`Scene isolation drifted while capturing ${collection}/${sceneId}`);
          }
          const file = path.join(evidenceDir, `${collection}-${sceneId}-${viewportName}.png`);
          await scene.screenshot({ path: file, animations: 'disabled' });
          records.push({
            collection,
            sceneId,
            viewport: viewportName,
            file,
            commerceState: await scene.getAttribute('data-product-state'),
            compositeState: await scene.getAttribute('data-composite-state'),
          });
        }
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }

  if (errors.length) {
    throw new Error(`Browser page errors:\n${errors.join('\n')}`);
  }
  if (records.length !== 27) {
    throw new Error(`Expected 27 scene renders, received ${records.length}`);
  }

  await fs.writeFile(path.join(evidenceDir, 'render-evidence.json'), `${JSON.stringify(records, null, 2)}\n`);
  for (const [viewportName, viewport] of Object.entries(viewports)) {
    await makeContactSheet(
      viewportName,
      viewport,
      records.filter((record) => record.viewport === viewportName)
    );
  }

  console.log('PASS captured 27 scene renders with zero page errors and zero document overflow');
}

run().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
