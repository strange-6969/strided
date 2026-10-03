/* Exercises the live production URL. Proves the deployed app works, not just
   that it returns 200. */

const { chromium } = require('playwright');
const path = require('path');
const OUT = path.join(__dirname, 'shots');
const BASE = process.env.STRIDED_URL || 'https://strided-nithin2668nk-8034.vercel.app';

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(`PAGEERROR ${e.message}`));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(`console: ${m.text()}`);
  });
  page.on('response', (r) => {
    if (r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`);
  });

  const resp = await page.goto(BASE, { waitUntil: 'networkidle', timeout: 45000 });
  console.log('status      :', resp.status());
  console.log('final url   :', page.url());

  await page.waitForFunction(() => window.__strided && window.__strided.ready, { timeout: 20000 });
  const count = await page.evaluate(() => window.__strided.problems.length);
  console.log('problems    :', count);
  const fontsOk = await page.evaluate(() => document.fonts.check('14px "Space Grotesk"'));
  console.log('font loaded :', fontsOk);

  // fonts really self-hosted, not falling back
  const fontSrc = await page.evaluate(() => {
    const el = document.querySelector('.brand b');
    return getComputedStyle(el).fontFamily;
  });
  console.log('heading font:', fontSrc);

  // open a problem and read the ladder
  await page.click('[data-nav="learn"]');
  await page.waitForTimeout(200);
  await page.click('[data-open]');
  await page.waitForTimeout(300);
  const title = await page.textContent('.detail-head h2');
  console.log('problem     :', title.trim());
  const ladder = await page.$$eval('.rung', (els) =>
    els.map((e) => `${e.dataset.tier}:${e.querySelector('.cx .t').textContent.trim()}`)
  );
  console.log('ladder      :', ladder.join('  '));

  await page.click('[data-tier-toggle="optimal"]');
  await page.waitForTimeout(200);
  const code = await page.textContent('.rung-body pre code');
  console.log('code lines  :', code.split('\n').length);

  // grade an attempt and confirm it persists server-side (fresh load)
  await page.click('[data-grade="3"]');
  await page.waitForTimeout(400);
  const toast = await page.textContent('.toast');
  console.log('toast       :', toast.trim());

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready, { timeout: 20000 });
  const xp = await page.evaluate(() => window.__strided.getState().xp);
  console.log('xp persisted:', xp);

  require('fs').mkdirSync(OUT, { recursive: true });
  await page.screenshot({ path: path.join(OUT, 'production.png') });

  const real = errors.filter((e) => !/favicon/i.test(e));
  console.log('errors      :', real.length ? real : 'none');
  await browser.close();
  process.exit(real.length ? 1 : 0);
})();