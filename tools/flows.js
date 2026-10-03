/* Exercises the flows that the earlier suites never touched: mastery, unfreeze,
   export and import. These are the features that promise the learner their data
   is never trapped, so "it renders" is not evidence they work. */

const { chromium } = require('playwright');
const BASE = process.env.STRIDED_URL || 'http://localhost:8788/';

const fails = [];
const note = (ok, msg) => {
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${msg}`);
  if (!ok) fails.push(msg);
};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(`PAGEERROR ${e.message}`));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(`console: ${m.text()}`);
  });

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready);

  // start from a clean slate so counts are predictable
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready);

  // ---------- 1. mastery freezes a problem out of the queue ----------
  const mastered = await page.evaluate(async () => {
    const S = window.__strided;
    const id = S.problems[0].id;
    for (let i = 0; i < 6; i++) S.recordAttempt(id, 3);
    const card = S.getState().cards[id];
    return { id, frozen: !!card.frozen, step: card.step, due: card.due, dueList: S.dueList().map((p) => p.id) };
  });
  note(mastered.frozen === true, `mastery freezes the card (frozen=${mastered.frozen}, step=${mastered.step})`);
  note(!mastered.dueList.includes(mastered.id), 'a mastered problem leaves the due queue');
  note(mastered.step >= 4, `step reached the long-interval rung (step=${mastered.step})`);

  // the UI must reflect mastery, not just the store
  await page.click('[data-nav="progress"]');
  await page.waitForTimeout(200);
  const masteredStat = await page.textContent('.statline');
  note(/1/.test(masteredStat), 'progress view shows the mastered count');

  // ---------- 2. unfreeze actually returns it to rotation ----------
  await page.click('[data-nav="learn"]');
  await page.waitForTimeout(150);
  await page.click(`[data-open="${mastered.id}"]`);
  await page.waitForTimeout(200);
  const hasUnfreeze = await page.$('[data-unfreeze]');
  note(!!hasUnfreeze, 'the mastered problem offers a bring-back control');

  if (hasUnfreeze) {
    await hasUnfreeze.click();
    await page.waitForTimeout(250);
    const after = await page.evaluate((id) => {
      const S = window.__strided;
      const c = S.getState().cards[id];
      return { frozen: !!c.frozen, due: c.due, step: c.step, lapses: c.lapses, dueList: S.dueList().map((p) => p.id) };
    }, mastered.id);

    note(after.frozen === false, 'unfreeze clears the frozen flag');
    note(after.step === -1, `unfreeze resets the ladder to the floor (step=${after.step})`);
    note(after.lapses >= 1, `unfreeze records a lapse so mastery must be re-earned (lapses=${after.lapses})`);
    /* "Reviewable again" means it is scheduled, not that it is due today.
       unfreeze deliberately books it for tomorrow, so asserting it is in today's
       queue would be asserting the bug I just fixed. Assert the schedule instead. */
    note(after.due !== null, `unfreeze schedules a real return date (due=${after.due})`);
    const scheduledTomorrow = await page.evaluate((id) => {
      const S = window.__strided;
      const c = S.getState().cards[id];
      const due = new Date(c.due);
      const today = new Date();
      due.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      return Math.round((due - today) / 86400000);
    }, mastered.id);
    note(scheduledTomorrow === 1, `the released problem comes back tomorrow, not never (in ${scheduledTomorrow}d)`);
    note(!after.dueList.includes(mastered.id), 'and it is not forced into today, which would be a surprise');
  }

  // ---------- 3. export produces valid, complete JSON ----------
  const backup = await page.evaluate(() => JSON.parse(localStorage.getItem('strided.v1')));
  note(!!backup && typeof backup === 'object', 'progress is persisted to localStorage');
  note(Array.isArray(backup.cards) === false && typeof backup.cards === 'object', 'export shape carries a cards map');
  note(typeof backup.xp === 'number', `export carries xp (${backup.xp})`);
  note(typeof backup.activity === 'object' && Object.keys(backup.activity).length > 0, 'export carries the activity log');
  note(typeof backup.lang === 'string' && backup.lang.length > 0, `export carries the language choice (${backup.lang})`);

  // ---------- 4. import restores a wiped state ----------
  const restored = await page.evaluate((payload) => {
    const S = window.__strided;
    window.__resetAll();
    const before = S.getState().xp;
    S.recordAttempt(S.problems[1].id, 3);
    const midXp = S.getState().xp;
    window.__importBackup(JSON.stringify(payload));
    return {
      before,
      midXp,
      afterXp: S.getState().xp,
      cards: Object.keys(S.getState().cards).length,
      expected: Object.keys(payload.cards).length,
      lang: S.getState().lang,
    };
  }, backup);

  note(restored.before === 0, 'resetAll clears xp');
  note(restored.midXp === 25, `a fresh solve earns xp (${restored.midXp})`);
  note(restored.afterXp === backup.xp, `import restores the original xp (${restored.afterXp} vs ${backup.xp})`);
  note(restored.cards === restored.expected, `import restores every tracked card (${restored.cards}/${restored.expected})`);
  note(restored.lang === backup.lang, `import restores the language choice (${restored.lang})`);

  // ---------- 5. import rejects junk without destroying state ----------
  const junk = await page.evaluate(() => {
    const S = window.__strided;
    const before = S.getState().xp;
    let threw = false;
    try {
      window.__importBackup('this is not json');
    } catch (e) {
      threw = true;
    }
    return { before, after: S.getState().xp, threw };
  });
  note(junk.threw === true, 'malformed import is rejected rather than silently accepted');
  note(junk.after === junk.before, 'a failed import leaves existing progress intact');

  const real = errors.filter((e) => !/favicon/i.test(e));
  note(real.length === 0, `no page errors (${real.length})`);
  real.forEach((e) => console.log('    !', e));

  console.log(`\n${fails.length} failure(s)`);
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})();