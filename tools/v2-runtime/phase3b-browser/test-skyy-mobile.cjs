const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const out = path.resolve(__dirname, '../../../.artifacts/v2-cinematic-finalization-20260906/skyy');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
  const rows = [];
  try {
    for (const width of [320, 414, 768]) {
      const p = await b.newPage({ viewport: { width, height: 844 }, reducedMotion: 'reduce' });
      await p.goto((process.env.V2_BASE_URL || 'http://127.0.0.1:18416') + '/shop/', { waitUntil: 'load' });
      await p.locator('#skyyrose-mascot-recall').click();
      await p.waitForFunction(() => document.getElementById('skyy-ask-dialog').open);
      await p.locator('#skyyrose-mascot .skyyrose-mascot__image').evaluate(image => image.decode());
      await p.screenshot({ path: path.join(out, `mobile-${width}.png`) });
      const row = await p.evaluate(() => {
        let d = document.getElementById('skyy-ask-dialog'),
          i = document.getElementById('skyy-ask-input');
        return {
          dialog: d.getBoundingClientRect().toJSON(),
          input: i.getBoundingClientRect().toJSON(),
          scrollWidth: d.scrollWidth,
          clientWidth: d.clientWidth,
          focus: document.activeElement.id,
          posterResource: performance
            .getEntriesByType('resource')
            .find(e => e.name.includes('skyy-runtime-poster.webp'))
            ?.toJSON(),
        };
      });
      assert(row.dialog.left >= 0 && row.dialog.right <= width);
      assert(row.scrollWidth <= row.clientWidth + 1);
      assert.equal(row.focus, 'skyy-ask-input');
      assert(row.input.bottom <= row.dialog.bottom - 8, `Ask composer below visible dialog at${width}px`);
      await p.evaluate(requireQa('axe-core').source);
      row.axe = await p.evaluate(async () =>
        (await axe.run(document.getElementById('skyy-ask-dialog'))).violations.map(v => v.id)
      );
      assert.equal(row.axe.length, 0);
      await p.locator('#skyy-conversation').focus();
      await p.keyboard.press('PageDown');
      await p.waitForTimeout(400);
      if (width === 320) {
        assert(await p.locator('#skyy-conversation').evaluate(log => log.scrollTop > 0));
        await p.screenshot({ path: path.join(out, 'mobile-320-log-focus.png') });
      }
      await p.keyboard.press('Escape');
      assert(!(await p.locator('#skyy-ask-dialog').getAttribute('open')));
      rows.push({ width, ...row });
      await p.close();
    }
  } finally {
    await b.close();
    fs.writeFileSync(path.join(out, 'mobile-art-direction.json'), JSON.stringify(rows, null, 2));
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
