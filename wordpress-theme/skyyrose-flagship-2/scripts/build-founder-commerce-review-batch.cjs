'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');

const themeDir = path.resolve(__dirname, '..');
const repoDir = path.resolve(themeDir, '../..');
const candidateDir = path.join(
  themeDir,
  'assets/scroll-world/generated-candidates/founder-commerce-scenes-v1'
);
const layerDir = path.join(candidateDir, 'protected-model-layers');
const outputDir = path.join(candidateDir, 'founder-review-batch-v2');
const promptContractFile = path.join(candidateDir, 'image-model-prompts-v1.json');
const preflightReceiptFile = path.join(
  candidateDir,
  'preflight-v1/pass-ready-to-generate-receipt-v1.json'
);
const generationBatchFile = path.join(
  candidateDir,
  'postflight-v1/generation-batch-manifest-v1.json'
);
const adversarialReceiptFile = path.join(
  candidateDir,
  'postflight-v1/pass-adversarial-verification-receipt-v1.json'
);
const width = 1672;
const height = 941;

const scenes = [
  {
    collection: 'Black Rose',
    id: 'br-commerce-1',
    promptId: 'br-commerce-1-v2',
    skus: ['br-001', 'br-002'],
    detailCrop: { left: 846, top: 128, width: 491, height: 590 },
    plate: 'black-rose/br-commerce-1-font-type-foundry-plate-v1.png',
    layers: [
      { file: 'br-commerce-1-crew-jogger-generated-protected-v2.png', skus: ['br-001', 'br-002'], height: 872, left: 846 },
    ],
  },
  {
    collection: 'Black Rose',
    id: 'br-commerce-2',
    promptId: 'br-commerce-2-v3',
    skus: ['br-005', 'br-007'],
    detailCrop: { left: 208, top: 112, width: 492, height: 650 },
    plate: 'black-rose/br-commerce-2-waterfront-plate-v1.png',
    fidelityContracts: [
      'br-005: raised tonal silicone cut-out at wearer-right chest',
      'br-005: large embroidered rose artwork on side body, never sleeve or arm',
      'br-007: narrow white side construction, never broad white front-leg panel',
      'br-007: complete Love Hurts script on black field above narrow white insert',
    ],
    layers: [
      { file: 'br-commerce-2-hoodie-shorts-generated-protected-v3.png', skus: ['br-005', 'br-007'], height: 874, left: 208 },
    ],
  },
  {
    collection: 'Love Hurts',
    id: 'lh-commerce-1',
    promptId: 'lh-commerce-1-v2',
    skus: ['lh-004', 'lh-002', 'lh-006'],
    detailCrop: { left: 88, top: 118, width: 580, height: 650 },
    plate: 'love-hurts/lh-commerce-1-bomber-cathedral-plate-v1.png',
    layers: [
      { file: 'lh-commerce-1-two-model-bomber-generated-protected-v2.png', skus: ['lh-004', 'lh-002', 'lh-006'], height: 872, left: 88 },
    ],
  },
  {
    collection: 'Love Hurts',
    id: 'lh-commerce-2',
    promptId: 'lh-commerce-2-v2',
    skus: ['lh-003'],
    detailCrop: { left: 174, top: 360, width: 580, height: 500 },
    plate: 'love-hurts/lh-commerce-2-shorts-chamber-plate-v1.png',
    layers: [
      { file: 'lh-commerce-2-neutral-top-generated-protected-v2.png', skus: ['lh-003'], height: 872, left: 174 },
    ],
  },
  {
    collection: 'Love Hurts',
    id: 'lh-commerce-3',
    promptId: 'lh-commerce-3-v1',
    skus: ['lh-005'],
    detailCrop: { left: 80, top: 190, width: 786, height: 620 },
    plate: 'love-hurts/lh-commerce-3-fannie-vitrine-plate-v1.png',
    layers: [
      {
        file: 'lh-005-onmodel-logo-pass-protected-v1.png',
        skus: ['lh-005'],
        height: 1180,
        left: 80,
        cropHeight: 941,
      },
    ],
  },
  {
    collection: 'Signature',
    id: 'sig-commerce-1',
    promptId: 'sig-commerce-1-v2',
    skus: ['sg-009', 'sg-007'],
    detailCrop: { left: 222, top: 70, width: 491, height: 610 },
    plate: 'signature/sig-commerce-1-oakland-atelier-plate-v1.png',
    layers: [
      { file: 'sig-commerce-1-sherpa-beanie-generated-protected-v2.png', skus: ['sg-009', 'sg-007'], height: 872, left: 222 },
    ],
  },
  {
    collection: 'Signature',
    id: 'sig-commerce-2',
    promptId: 'sig-commerce-2-v2',
    skus: ['sg-013', 'sg-014', 'sg-006'],
    detailCrop: { left: 258, top: 120, width: 1073, height: 660 },
    plate: 'signature/sig-commerce-2-fog-over-bay-plate-v1.png',
    layers: [
      { file: 'sig-commerce-2-male-mint-set-generated-protected-v2.png', skus: ['sg-013', 'sg-014'], height: 820, left: 258 },
      { file: 'sig-commerce-2-female-hoodie-generated-protected-v1.png', skus: ['sg-006'], height: 820, left: 870 },
    ],
  },
  {
    collection: 'Signature',
    id: 'sig-commerce-3',
    promptId: 'sig-commerce-3-v3',
    skus: ['sg-005', 'sg-001', 'sg-015', 'sg-002', 'sg-003'],
    detailCrop: { left: 20, top: 176, width: 1241, height: 650 },
    plate: 'signature/sig-commerce-3-departure-terrace-plate-v1.png',
    fidelityContracts: [
      'sg-005 + sg-001: complete Bay Bridge shirt-and-shorts look must be visually prominent and readable',
      'sg-001: blue waistband, white drawstring, daytime Bay Bridge wrap, blue rose at lower wearer-left leg',
      'sg-005: white tee with large blue Bay Bridge rose-cluster centered on chest',
    ],
    layers: [
      { file: 'sg-005-bay-bridge-pair-protected-candidate-v2.png', skus: ['sg-005', 'sg-001'], height: 872, left: 10 },
      { file: 'sg-015-onmodel-protected-candidate-v1.png', skus: ['sg-015'], height: 710, left: 520 },
      { file: 'sig-commerce-3-stay-golden-generated-protected-v1.png', skus: ['sg-002', 'sg-003'], height: 710, left: 945 },
    ],
  },
];

async function sha256(file) {
  return crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
}

async function requireGenerationGates(currentProductSotSha) {
  let preflight;
  let generationBatch;
  let adversarial;
  try {
    preflight = JSON.parse(await fs.readFile(preflightReceiptFile, 'utf8'));
    generationBatch = JSON.parse(await fs.readFile(generationBatchFile, 'utf8'));
    adversarial = JSON.parse(await fs.readFile(adversarialReceiptFile, 'utf8'));
  } catch (error) {
    throw new Error(
      `compositor blocked: preflight, generation-batch, and adversarial receipts are mandatory: ${error.message}`
    );
  }
  if (preflight.status !== 'PASS_READY_TO_GENERATE') {
    throw new Error('compositor blocked: image-generation preflight did not pass');
  }
  if (preflight.product_sot?.sha256 !== currentProductSotSha) {
    throw new Error('compositor blocked: preflight receipt is stale against product SOT');
  }
  if (preflight.prompt_contract?.sha256 !== (await sha256(promptContractFile))) {
    throw new Error('compositor blocked: prompt contract changed after preflight');
  }
  if (generationBatch.preflight_receipt_sha256 !== (await sha256(preflightReceiptFile))) {
    throw new Error('compositor blocked: generated batch is not bound to current preflight');
  }
  if (adversarial.status !== 'PASS_ADVERSARIAL_VERIFICATION') {
    throw new Error('compositor blocked: adversarial tournament did not pass');
  }
  if (
    adversarial.generation_batch_manifest?.sha256 !==
    (await sha256(generationBatchFile))
  ) {
    throw new Error('compositor blocked: adversarial receipt is stale against generated batch');
  }
  if (adversarial.reviewers?.length !== 3) {
    throw new Error('compositor blocked: two vision judges plus synthesis are required');
  }
  for (const [jobId, expectedHash] of Object.entries(adversarial.reviewed_outputs || {})) {
    const output = generationBatch.jobs?.[jobId]?.output;
    if (!output || output.sha256 !== expectedHash) {
      throw new Error(`compositor blocked: adversarial output binding missing for ${jobId}`);
    }
    const outputFile = path.join(repoDir, output.path);
    if ((await sha256(outputFile)) !== expectedHash) {
      throw new Error(`compositor blocked: reviewed output hash drift for ${jobId}`);
    }
  }
  if (
    Object.keys(adversarial.reviewed_outputs || {}).length !==
    preflight.active_generation_jobs.length
  ) {
    throw new Error('compositor blocked: not every receipt-bound generation job was reviewed');
  }
  return { preflight, generationBatch, adversarial };
}

async function prepareLayer(spec) {
  const file = path.join(layerDir, spec.file);
  const receiptFile = file.replace(/\.png$/i, '.receipt.json');
  let sourceReceipt;
  try {
    sourceReceipt = JSON.parse(await fs.readFile(receiptFile, 'utf8'));
  } catch (error) {
    throw new Error(`${spec.file} is missing its protected-layer receipt: ${error.message}`);
  }
  const metadata = await sharp(file).metadata();
  if (!metadata.hasAlpha) {
    throw new Error(`${spec.file} is not a protected alpha layer`);
  }
  if (!Array.isArray(spec.skus) || spec.skus.length === 0) {
    throw new Error(`${spec.file} is missing its explicit SKU coverage`);
  }
  let { data, info } = await sharp(file)
    .resize({ height: spec.height, fit: 'inside', withoutEnlargement: false })
    .png()
    .toBuffer({ resolveWithObject: true });
  if (spec.cropHeight) {
    if (spec.cropHeight > info.height || spec.cropHeight > height) {
      throw new Error(`${spec.file} requests an invalid crop height`);
    }
    ({ data, info } = await sharp(data)
      .extract({ left: 0, top: spec.cropTop || 0, width: info.width, height: spec.cropHeight })
      .png()
      .toBuffer({ resolveWithObject: true }));
  }
  const top = spec.cropHeight ? 0 : height - info.height;
  if (spec.left < 0 || top < 0 || spec.left + info.width > width) {
    throw new Error(`${spec.file} falls outside the ${width}x${height} canvas`);
  }
  return {
    composite: { input: data, left: spec.left, top },
    receipt: {
      file: path.relative(themeDir, file),
      sha256: await sha256(file),
      source_state: spec.file.includes('-generated-')
        ? 'GENERATED_FOUNDER_REVIEW_CANDIDATE'
        : 'EXISTING_FOUNDER_REVIEW_CANDIDATE',
      protected_layer_receipt: path.relative(themeDir, receiptFile),
      protected_layer_receipt_sha256: await sha256(receiptFile),
      protected_source: sourceReceipt.source,
      protected_source_sha256: sourceReceipt.source_sha256,
      rgb_preserved: sourceReceipt.rgb_preserved,
      source_dimensions: [metadata.width, metadata.height],
      rendered_bounds: [spec.left, top, info.width, info.height],
      skus: spec.skus,
    },
  };
}

function shadowSvg(layerReceipts) {
  const ellipses = layerReceipts
    .map((layer) => {
      const [left, , layerWidth] = layer.rendered_bounds;
      const cx = left + layerWidth / 2;
      const rx = Math.max(80, layerWidth * 0.34);
      return `<ellipse cx="${cx}" cy="918" rx="${rx}" ry="18" fill="rgba(0,0,0,.55)"/>`;
    })
    .join('');
  return Buffer.from(
    `<svg width="${width}" height="${height}"><defs><filter id="blur"><feGaussianBlur stdDeviation="13"/></filter></defs><g filter="url(#blur)">${ellipses}</g></svg>`
  );
}

async function renderScene(scene, productBySku, openingProducts, upstreamScenes) {
  const plate = path.join(candidateDir, scene.plate);
  const plateMetadata = await sharp(plate).metadata();
  if (plateMetadata.width !== width || plateMetadata.height !== height) {
    throw new Error(`${scene.plate} must remain ${width}x${height}`);
  }

  const prepared = [];
  for (const layer of scene.layers) {
    prepared.push(await prepareLayer(layer));
  }
  const layerReceipts = prepared.map((item) => item.receipt);
  const output = path.join(outputDir, `${scene.id}-founder-review-v2.png`);
  await sharp(plate)
    .composite([
      { input: shadowSvg(layerReceipts), left: 0, top: 0 },
      ...prepared.map((item) => item.composite),
    ])
    .png({ compressionLevel: 9 })
    .toFile(output);

  return {
    collection: scene.collection,
    scene_id: scene.id,
    prompt_contract_id: scene.promptId,
    approval_state: 'FOUNDER_REVIEW_REQUIRED',
    plate: path.relative(themeDir, plate),
    plate_sha256: await sha256(plate),
    upstream_plate_state: upstreamScenes.get(scene.id.toUpperCase())?.plate_state || 'UNVERIFIED',
    products: scene.skus.map((sku) => {
      const product = productBySku.get(sku);
      const opening = openingProducts[sku];
      if (!product || !opening) {
        throw new Error(`${scene.id} is missing product provenance for ${sku}`);
      }
      return {
        sku,
        name: product.identity.name,
        product_hash: product.product_hash,
        dossier: product.source.dossier,
        dossier_sha256: product.source.dossier_sha256,
        references: product.references,
        opening_media_state: opening.status || 'APPROVED_OPENING_MEDIA',
        opening_media_reason:
          opening.reason || 'Opening media provides one or more approved product views.',
      };
    }),
    fidelity_contracts: scene.fidelityContracts || [],
    layers: layerReceipts,
    output: path.relative(themeDir, output),
    output_sha256: await sha256(output),
    dimensions: [width, height],
  };
}

async function makeContactSheet(records) {
  const tileWidth = 836;
  const tileHeight = 471;
  const bannerHeight = 52;
  const tiles = [];
  for (const [index, record] of records.entries()) {
    const file = path.join(themeDir, record.output);
    const label = `${record.collection}  /  ${record.scene_id}`;
    const tile = await sharp(file)
      .resize(tileWidth, tileHeight, { fit: 'cover' })
      .composite([
        {
          input: Buffer.from(
            `<svg width="${tileWidth}" height="${tileHeight}"><rect width="${tileWidth}" height="42" fill="rgba(0,0,0,.82)"/><text x="18" y="28" fill="#fff" font-family="Arial, sans-serif" font-size="20" font-weight="700">${label}</text></svg>`
          ),
        },
      ])
      .png()
      .toBuffer();
    tiles.push({
      input: tile,
      left: (index % 2) * tileWidth,
      top: bannerHeight + Math.floor(index / 2) * tileHeight,
    });
  }
  const output = path.join(outputDir, 'founder-review-eight-scene-contact-sheet-v2.png');
  const banner = Buffer.from(
    `<svg width="${tileWidth * 2}" height="${bannerHeight}"><rect width="100%" height="100%" fill="#7d0016"/><text x="18" y="33" fill="#fff" font-family="Arial, sans-serif" font-size="21" font-weight="700">FOUNDER REVIEW REQUIRED — PRODUCT CANDIDATES, NOT APPROVED ASSETS — BR3 ALREADY APPROVED / EXCLUDED</text></svg>`
  );
  await sharp({
    create: {
      width: tileWidth * 2,
      height: bannerHeight + tileHeight * 4,
      channels: 4,
      background: '#050505',
    },
  })
    .composite([{ input: banner, left: 0, top: 0 }, ...tiles])
    .png({ compressionLevel: 9 })
    .toFile(output);
  return {
    output: path.relative(themeDir, output),
    sha256: await sha256(output),
    dimensions: [tileWidth * 2, bannerHeight + tileHeight * 4],
  };
}

async function makeDetailSheet(records) {
  const tileWidth = 836;
  const tileHeight = 471;
  const bannerHeight = 52;
  const tiles = [];
  for (const [index, record] of records.entries()) {
    const scene = scenes.find((candidate) => candidate.id === record.scene_id);
    const file = path.join(themeDir, record.output);
    const label = `${record.collection}  /  ${record.scene_id}  /  product-detail review`;
    const tile = await sharp(file)
      .extract(scene.detailCrop)
      .resize(tileWidth, tileHeight, { fit: 'contain', background: '#050505' })
      .composite([
        {
          input: Buffer.from(
            `<svg width="${tileWidth}" height="${tileHeight}"><rect width="${tileWidth}" height="42" fill="rgba(0,0,0,.82)"/><text x="18" y="28" fill="#fff" font-family="Arial, sans-serif" font-size="18" font-weight="700">${label}</text></svg>`
          ),
        },
      ])
      .png()
      .toBuffer();
    tiles.push({
      input: tile,
      left: (index % 2) * tileWidth,
      top: bannerHeight + Math.floor(index / 2) * tileHeight,
    });
  }
  const output = path.join(outputDir, 'founder-review-eight-scene-product-detail-sheet-v2.png');
  const banner = Buffer.from(
    `<svg width="${tileWidth * 2}" height="${bannerHeight}"><rect width="100%" height="100%" fill="#7d0016"/><text x="18" y="33" fill="#fff" font-family="Arial, sans-serif" font-size="21" font-weight="700">FOUNDER REVIEW REQUIRED — PRODUCT DETAIL CHECK — NO PRODUCTION APPROVAL INFERRED</text></svg>`
  );
  await sharp({
    create: {
      width: tileWidth * 2,
      height: bannerHeight + tileHeight * 4,
      channels: 4,
      background: '#050505',
    },
  })
    .composite([{ input: banner, left: 0, top: 0 }, ...tiles])
    .png({ compressionLevel: 9 })
    .toFile(output);
  return {
    output: path.relative(themeDir, output),
    sha256: await sha256(output),
    dimensions: [tileWidth * 2, bannerHeight + tileHeight * 4],
    evidence_state: 'FOUNDER_VISUAL_REVIEW_AID_NOT_AUTOMATIC_APPROVAL',
  };
}

async function run() {
  await fs.mkdir(outputDir, { recursive: true });
  const productSotFile = path.join(repoDir, 'data/product-sot.json');
  const openingMediaFile = path.join(themeDir, 'data/opening-product-media.json');
  const upstreamManifestFile = path.join(candidateDir, 'manifest.json');
  const productSot = JSON.parse(await fs.readFile(productSotFile, 'utf8'));
  const openingMedia = JSON.parse(await fs.readFile(openingMediaFile, 'utf8'));
  const upstreamManifest = JSON.parse(await fs.readFile(upstreamManifestFile, 'utf8'));
  const promptContract = JSON.parse(await fs.readFile(promptContractFile, 'utf8'));
  const currentProductSotSha = await sha256(productSotFile);
  if (promptContract.product_sot_sha256 !== currentProductSotSha) {
    throw new Error('image-model prompt contract is stale against product SOT');
  }
  if (promptContract.policy?.direct_untracked_chat_prompt_forbidden !== true) {
    throw new Error('image-model prompt contract must forbid untracked chat prompts');
  }
  const generationGates = await requireGenerationGates(currentProductSotSha);
  for (const scene of scenes) {
    const prompt = promptContract.scene_registry?.[scene.promptId];
    if (!prompt || prompt.scene_id !== scene.id) {
      throw new Error(`${scene.id} is missing its JSON image-model prompt contract`);
    }
    if (JSON.stringify(prompt.skus) !== JSON.stringify(scene.skus)) {
      throw new Error(`${scene.id} prompt SKU cast disagrees with scene cast`);
    }
  }
  const productRecords = Array.isArray(productSot.products)
    ? productSot.products
    : Object.values(productSot.products);
  const productBySku = new Map(productRecords.map((product) => [product.sku, product]));
  const upstreamScenes = new Map(
    upstreamManifest.scenes.map((scene) => [scene.scene_id, scene])
  );
  const records = [];
  for (const scene of scenes) {
    records.push(
      await renderScene(scene, productBySku, openingMedia.products, upstreamScenes)
    );
  }
  const contactSheet = await makeContactSheet(records);
  const productDetailSheet = await makeDetailSheet(records);
  const manifest = {
    schema: 'skyyrose.founder-commerce-review-batch.v2',
    generated_at: new Date().toISOString(),
    approval_state: 'FOUNDER_REVIEW_REQUIRED',
    production_wired: false,
    note: 'Mechanical composites for founder review. Approval is not inferred from generation or validation.',
    product_sot: {
      file: path.relative(themeDir, productSotFile),
      sha256: currentProductSotSha,
    },
    image_model_prompt_contract: {
      file: path.relative(themeDir, promptContractFile),
      sha256: await sha256(promptContractFile),
      format: 'json',
      direct_untracked_chat_prompt_forbidden: true,
    },
    image_generation_gates: {
      preflight_receipt: {
        file: path.relative(themeDir, preflightReceiptFile),
        sha256: await sha256(preflightReceiptFile),
        status: generationGates.preflight.status,
        reviewed_file_count: generationGates.preflight.reviewed_file_count,
      },
      generation_batch_manifest: {
        file: path.relative(themeDir, generationBatchFile),
        sha256: await sha256(generationBatchFile),
      },
      adversarial_verification_receipt: {
        file: path.relative(themeDir, adversarialReceiptFile),
        sha256: await sha256(adversarialReceiptFile),
        status: generationGates.adversarial.status,
        reviewers: generationGates.adversarial.reviewers,
      },
    },
    opening_product_media: {
      file: path.relative(themeDir, openingMediaFile),
      sha256: await sha256(openingMediaFile),
      product_sot_sha256: openingMedia.product_sot_sha256,
    },
    already_approved_scene: {
      scene_id: 'BR-COMMERCE-3',
      excluded_from_remaining_eight_review: true,
      asset: upstreamScenes.get('BR-COMMERCE-3').asset,
      sha256: upstreamScenes.get('BR-COMMERCE-3').sha256,
      plate_state: upstreamScenes.get('BR-COMMERCE-3').plate_state,
      composite_state: upstreamScenes.get('BR-COMMERCE-3').composite_state,
    },
    scenes: records,
    contact_sheet: contactSheet,
    product_detail_sheet: productDetailSheet,
  };
  await fs.writeFile(path.join(outputDir, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`);
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
