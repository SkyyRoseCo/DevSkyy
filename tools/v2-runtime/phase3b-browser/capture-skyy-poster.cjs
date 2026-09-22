/** Deterministic local render of the unchanged approved rig/camera/idle pose. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const root = path.resolve(__dirname, '../../..');
const theme = path.join(root, 'wordpress-theme/skyyrose-flagship-2');
const destination = path.join(theme, 'assets/images/skyy-runtime-poster.webp');
(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1.5 });
    page.on('pageerror', error => console.log('PAGEERROR', error.message));
    for (const name of ['skyy-3d', 'mascot', 'mascot-loader']) {
      await page.route(`**/${name}.min.js*`, route =>
        route.fulfill({
          contentType: 'application/javascript',
          body: fs.readFileSync(path.join(theme, `assets/js/${name}.js`), 'utf8'),
        })
      );
    }
    await page.goto((process.env.V2_BASE_URL || 'http://127.0.0.1:18416') + '/shop/', { waitUntil: 'load' });
    await page.locator('#skyyrose-mascot-recall').click();
    await page.waitForFunction(
      () => window.skyyRoseMascot3D?.isReady() || window.skyyRoseMascot3D?.getFailureReason(),
      null,
      { timeout: 45000 }
    );
    console.log(
      await page.evaluate(() => ({
        state: window.skyyRoseMascot3D?.getRenderState(),
        failure: window.skyyRoseMascot3D?.getFailureReason(),
      }))
    );
    const captured = await page.evaluate(() => ({
      data: window.skyyRoseMascot3D.capturePoster(),
      profile: window.skyyRoseMascot3D.getProfile(),
    }));
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    const sourcePng = path.join(root, '.artifacts/v2-cinematic-finalization-20260906/skyy/poster-source.png');
    fs.writeFileSync(sourcePng, Buffer.from(captured.data.split(',')[1], 'base64'));
    require('node:child_process').execFileSync(process.env.V2_PYTHON || 'python3', [
      '-c',
      'from PIL import Image; import sys; Image.open(sys.argv[1]).save(sys.argv[2], lossless=True, method=6)',
      sourcePng,
      destination,
    ]);
    const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
    const receipt = {
      generatedAt: new Date().toISOString(),
      method:
        'Local WebGL render; same existing canonical model, runtime camera, lighting and time-zero relaxed idle pose. No model, rig, face, clothing or texture edits.',
      output: path.relative(root, destination),
      outputSha256: hash(destination),
      encoding: 'Lossless WebP from raw canvas PNG; identical decoded pixels',
      sourcePngSha256: hash(sourcePng),
      modelSha256: hash(path.join(theme, 'assets/models/skyy-mascot.glb')),
      runtimeSha256: hash(path.join(theme, 'assets/js/skyy-3d.js')),
      camera: { fov: 30, aspect: 220 / 340, position: [0, 1.1, 4.1], lookAt: [0, 0.9, 0] },
      width: 330,
      height: 510,
      profile: captured.profile,
    };
    const artifact = path.join(root, '.artifacts/v2-cinematic-finalization-20260906/skyy/poster-provenance.json');
    fs.writeFileSync(artifact, JSON.stringify(receipt, null, 2));
    console.log(JSON.stringify(receipt));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
