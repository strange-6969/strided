/* Profile preferences, and the rule that makes the language preference
   meaningful: the chosen language must actually change the code that renders. */

const { chromium } = require('playwright');
const BASE = process.env.STRIDED_URL || 'http://localhost:8788/';

const fails = [];
const note = (ok, msg) => {
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${msg}`);
  if (!ok) fails.push(msg);
};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 1000 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(`PAGEERROR ${e.message}`));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(`console: ${m.text()}`);
  });

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready && window.__strided.spine);
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready && window.__strided.spine);

  // ---------- the view exists ----------
  await page.click('[data-nav="profile"]');
  await page.waitForTimeout(300);
  note((await page.$('.langgrid')) !== null, 'profile view renders the language grid');

  const langOpts = await page.$$eval('[data-set-lang]', (els) => els.map((e) => e.dataset.setLang));
  note(
    JSON.stringify(langOpts.sort()) === JSON.stringify(['cpp', 'java', 'python']),
    `all three languages offered (${langOpts.join(', ')})`
  );

  const defaultPressed = await page.$$eval('[data-set-lang][aria-pressed="true"]', (els) =>
    els.map((e) => e.dataset.setLang)
  );
  note(defaultPressed.length === 1, `exactly one language is selected by default (${defaultPressed})`);

  // ---------- the preference actually changes rendered code ----------
  //
  // This is the assertion that matters. A preference that stores a value but
  // does not reach the solution is a dead control.
  const sample = async (lang) => {
    await page.click('[data-nav="profile"]');
    await page.waitForTimeout(150);
    await page.click(`[data-set-lang="${lang}"]`);
    await page.waitForTimeout(200);
    await page.click('[data-nav="learn"]');
    await page.waitForTimeout(150);
    await page.click('[data-open]');
    await page.waitForTimeout(300);
    const rungs = await page.$$eval('.rung', (els) =>
      els.map((e) => e.dataset.tier)
    );
    if (rungs.length) {
      await page.click('[data-tier-toggle="optimal"]');
      await page.waitForTimeout(200);
    }
    return page.textContent('.rung-body pre code');
  };

  const javaCode = await sample('java');
  note(/int\s|for\s*\(/.test(javaCode), 'java preference renders java syntax');
  note(!/^\s*(def |import heapq)/m.test(javaCode), 'java preference does not render python');

  const pyCode = await sample('python');
  note(/(def |for .* in |import )/.test(pyCode), 'python preference renders python syntax');
  note(!/\bint\s+\w+\s*=/.test(pyCode), 'python preference does not render java');

  const cppCode = await sample('cpp');
  note(/#include|std::|vector<|int\s/.test(cppCode), 'cpp preference renders c++ syntax');
  note(!/\bdef \w+/.test(cppCode), 'cpp preference does not render python');

  // ---------- it persists across a reload, which is the whole point ----------
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready && window.__strided.spine);
  const persisted = await page.evaluate(() => {
    const s = window.__strided.getState();
    return { lang: s.lang, profileLang: s.profile.language };
  });
  note(persisted.lang === 'cpp', `language persists in state (${persisted.lang})`);
  note(persisted.profileLang === 'cpp', `language persists on the profile (${persisted.profileLang})`);

  // and the readout in the rail reflects it
  const readout = await page.textContent('.langreadout');
  note(/C\+\+/.test(readout), `rail readout shows the saved language (${readout.trim().split('\n')[0]})`);

  // ---------- visibility defaults to private ----------
  const vis = await page.evaluate(() => window.__strided.getState().profile.visibility);
  note(vis === 'friends' || vis === 'private', `progress visibility is not public by default (${vis})`);

  await page.click('[data-nav="profile"]');
  await page.waitForTimeout(200);
  await page.click('[data-set-vis="public"]');
  await page.waitForTimeout(200);
  const vis2 = await page.evaluate(() => window.__strided.getState().profile.visibility);
  note(vis2 === 'public', 'visibility can be raised deliberately');

  // ---------- display name ----------
  await page.fill('#displayName', 'Ada');
  await page.click('[data-act="saveName"]');
  await page.waitForTimeout(250);
  const name = await page.evaluate(() => window.__strided.getState().profile.displayName);
  note(name === 'Ada', `display name saves (${name})`);

  // over-long input is clamped rather than stored whole
  await page.fill('#displayName', 'x'.repeat(60));
  await page.click('[data-act="saveName"]');
  await page.waitForTimeout(250);
  const clamped = await page.evaluate(() => window.__strided.getState().profile.displayName);
  note(clamped.length <= 24, `display name is clamped to 24 characters (${clamped.length})`);

  // ---------- a stored profile missing keys must not break the app ----------
  const survived = await page.evaluate(() => {
    // Simulate a backup written by an older version with no profile at all.
    const raw = JSON.parse(localStorage.getItem('strided.v1'));
    delete raw.profile;
    localStorage.setItem('strided.v1', JSON.stringify(raw));
    return true;
  });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.ready && window.__strided.spine);
  const healed = await page.evaluate(() => window.__strided.getState().profile);
  note(!!healed && !!healed.visibility, `a backup with no profile is repaired on load (${JSON.stringify(healed)})`);
  await page.click('[data-nav="profile"]');
  await page.waitForTimeout(250);
  const stillRenders = await page.$$eval('[data-set-lang]', (els) => els.length);
  note(stillRenders === 3, `profile still renders after repair (${stillRenders} options)`);

  // ---------- nothing renders as undefined ----------
  // A stats key renamed in one file and not the other produced a literal
  // "undefined" in a dashboard figure. Assert on rendered text, not on the
  // store, because the store can be correct while the template is not.
  await page.click('[data-nav="profile"]');
  await page.waitForTimeout(250);
  const profileText = await page.innerText('body');
  note(!/undefined|NaN|\[object Object\]/.test(profileText),
    `profile renders no undefined values (${/undefined|NaN|\[object Object\]/.test(profileText) ? 'FOUND' : 'clean'})`);

  const figures = await page.$$eval('.stat .n', (els) => els.map((e) => e.textContent.trim()));
  note(figures.every((v) => /^\d+$/.test(v)), `every profile figure is a number (${figures.join(', ')})`);

  // and the same sweep across the other numeric views
  for (const view of ['today', 'progress', 'map', 'catalog']) {
    await page.click(`[data-nav="${view}"]`);
    await page.waitForTimeout(220);
    const txt = await page.innerText('body');
    const bad = txt.match(/undefined|NaN|\[object Object\]/);
    note(!bad, `${view} renders no undefined values${bad ? ' (found ' + bad[0] + ')' : ''}`);
  }

  const real = errors.filter((e) => !/favicon/i.test(e));
  note(real.length === 0, `no page errors (${real.length})`);
  real.forEach((e) => console.log('    !', e));

  console.log(`\n${fails.length} failure(s)`);
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})();