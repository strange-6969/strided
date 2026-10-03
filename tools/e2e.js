/* Drives the real UI across the expanded dataset: every problem opens, every
   ladder opens, all three languages render, and each syntax card is present.
   Fails loudly rather than trusting the dataset validator alone. */

const { chromium } = require('playwright');
const BASE = process.env.STRIDED_URL || 'http://localhost:8788/';

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(`PAGEERROR ${e.message}`));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(`console: ${m.text()}`);
  });

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready);

  const problems = await page.evaluate(() =>
    window.__strided.problems.map((p) => ({
      id: p.id,
      title: p.title,
      pattern: p.pattern,
      tiers: p.ladder.length,
      hints: p.hints.length,
      langs: Object.keys(p.ladder[0].code),
    }))
  );
  console.log(`problems loaded: ${problems.length}`);

  const fails = [];
  for (const p of problems) {
    // open the problem
    await page.click('[data-nav="learn"]');
    await page.waitForTimeout(60);
    await page.click(`[data-open="${p.id}"]`);
    await page.waitForTimeout(120);

    const shown = await page.textContent('.detail-head h2');
    if (shown.trim() !== p.title) fails.push(`${p.id}: title "${shown}" != "${p.title}"`);

    const rungs = await page.$$eval('.rung', (els) => els.length);
    if (rungs !== p.tiers) fails.push(`${p.id}: ${rungs} rungs, expected ${p.tiers}`);

    const hintBtns = await page.$$eval('[data-hint]', (els) => els.length);
    if (hintBtns !== p.hints) fails.push(`${p.id}: ${hintBtns} hints, expected ${p.hints}`);

    const links = await page.$$eval('.link', (els) => els.length);
    if (links < 1) fails.push(`${p.id}: no external links`);

    // every rung opens and shows code in all three languages
    for (const lang of ['java', 'python', 'cpp']) {
      await page.click(`[data-lang="${lang}"]`);
      await page.waitForTimeout(40);
      const bodies = await page.$$eval('.rung-body', (els) => els.length);
      if (bodies < 1) {
        // brute rung should be open by default; if not, open one
        await page.click('[data-tier-toggle="optimal"]');
        await page.waitForTimeout(60);
      }
      const code = await page.textContent('.rung-body pre code');
      if (!code || code.trim().length < 10) fails.push(`${p.id}/${lang}: no code rendered`);
      /* undefined / NaN / [object Object] mean a template hole was rendered.
         Plain "null" is legitimate Java and C++ source, so it is not a signal
         on its own and must not be matched here. */
      const hole = code.match(/undefined|NaN|\[object Object\]/);
      if (hole) fails.push(`${p.id}/${lang}: code contains ${hole[0]}`);
    }

    // syntax card present for this pattern
    const hasSyntax = await page.evaluate(() =>
      [...document.querySelectorAll('.sec h3')].some((h) => h.textContent.includes('Syntax'))
    );
    if (!hasSyntax) fails.push(`${p.id}: no syntax card section`);

    // ladder must be visible in order
    const tierOrder = await page.$$eval('.rung', (els) => els.map((e) => e.dataset.tier));
    if (tierOrder.join(',') !== 'brute,better,optimal') {
      fails.push(`${p.id}: tier order ${tierOrder.join(',')}`);
    }
  }

  // pattern drill renders for a sample
  await page.click('[data-nav="patterns"]');
  await page.waitForTimeout(120);
  const cards = await page.$$eval('.pcard', (els) => els.length);
  const expectedPatterns = await page.evaluate(() => window.__strided.patterns.length);
  if (cards !== expectedPatterns) fails.push(`patterns grid: ${cards} cards, expected ${expectedPatterns}`);

  console.log(`pattern cards: ${cards}`);
  console.log(`problems exercised: ${problems.length}`);
  console.log(`failures: ${fails.length}`);
  fails.forEach((f) => console.log('  x', f));
  console.log(`page errors: ${errors.length}`);
  errors.forEach((e) => console.log('  !', e));

  await browser.close();
  process.exit(fails.length || errors.length ? 1 : 0);
})();