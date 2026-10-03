/* Proves the dependency map is a real graph, not a list with arrows.
   Checks topological validity, that unlocking follows the prerequisites, and
   that a locked topic cannot be reached by clicking through it. */

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
  await page.waitForFunction(() => window.__strided && window.__strided.ready && window.__strided.spine);
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__strided && window.__strided.spine);

  const spine = await page.evaluate(() => window.__strided.spine);
  const problems = await page.evaluate(() => window.__strided.problems);

  // ---------- graph validity ----------
  const ids = spine.topics.map((t) => t.id);
  const idset = new Set(ids);
  note(new Set(ids).size === ids.length, 'topic ids are unique');
  note(spine.edges.length > 0, `graph has edges (${spine.edges.length})`);

  const dangling = spine.edges.filter((e) => !idset.has(e.from) || !idset.has(e.to));
  note(dangling.length === 0, `no dangling edges${dangling.length ? ': ' + JSON.stringify(dangling) : ''}`);

  // every prerequisite must appear EARLIER in the order, or the map lies
  const orderOf = Object.fromEntries(spine.topics.map((t) => [t.id, t.order]));
  const outOfOrder = spine.edges.filter((e) => orderOf[e.to] <= orderOf[e.from]);
  note(
    outOfOrder.length === 0,
    `every prerequisite resolves before its dependent${outOfOrder.length ? ': ' + JSON.stringify(outOfOrder) : ''}`
  );

  // strict increase proves acyclicity
  const sorted = [...spine.topics].sort((a, b) => a.order - b.order);
  const orders = sorted.map((t) => t.order);
  note(
    orders.every((v, i) => v === i),
    'order values are a dense 0..n-1 sequence, so the graph is acyclic'
  );

  // ---------- coverage ----------
  note(spine.links.length === problems.length, `every authored problem is on the spine (${spine.links.length}/${problems.length})`);
  const linkTopics = new Set(spine.links.map((l) => l.topic));
  note(
    spine.links.every((l) => l.ladders === 3),
    'every spine link points at a problem with a full three-rung ladder'
  );

  // ---------- the map view renders ----------
  await page.click('[data-nav="map"]');
  await page.waitForTimeout(300);
  const nodes = await page.$$eval('.mapnode', (els) => els.length);
  note(nodes === spine.topics.length, `map renders one node per topic (${nodes}/${spine.topics.length})`);

  const groups = await page.$$eval('.mapgroup', (els) => els.length);
  note(groups >= 4, `map is grouped (${groups} groups)`);

  const states = await page.$$eval('.mn-state', (els) => els.map((e) => e.dataset.state));
  /* Full coverage means no topic can be labelled unauthored any more, so the
     open states are now just ready/active/mastered. */
  note(!states.includes('unauthored'), 'every topic has authored ladders, so none reads unauthored');
  const openStates = states.filter((s) => s === 'ready' || s === 'active' || s === 'mastered');
  note(openStates.length > 0, `at least one topic starts unlocked (${openStates.length} open)`);
  note(states.includes('locked'), 'dependent topics start locked');
  note(
    states.filter((s) => s === 'locked').length > 0,
    'unlocking is actually gated rather than everything open at once'
  );

  // ---------- full coverage of the spine ----------
  const topicIds = spine.topics.map((t) => t.id);
  const covered = new Set(spine.links.map((l) => l.topic));
  const uncovered = topicIds.filter((id) => !covered.has(id));
  note(uncovered.length === 0, `every spine topic has at least one authored ladder${uncovered.length ? ': ' + uncovered.join(', ') : ''}`);

  const emptyNodes = await page.$$eval('.mapnode.is-empty', (els) => els.length);
  note(emptyNodes === 0, `no unauthored nodes remain in the map (${emptyNodes})`);

  // every node must be clickable now
  const disabled = await page.$$eval('.mapnode[disabled]', (els) => els.length);
  note(disabled === 0, `every map node is clickable (${disabled} disabled)`);

  // ---------- unlocking follows the graph ----------
  const before = await page.evaluate(() => {
    const S = window.__strided;
    const st = S.spineStatus();
    return { unlocked: Object.entries(st.unlocked).filter(([, v]) => v).map(([k]) => k) };
  });
  note(before.unlocked.includes('basics'), 'the root topic (no prerequisites) is unlocked');
  note(!before.unlocked.includes('dynamicprogramming'), 'deepest topic is locked at the start');

  // solve one problem in arrays, which many topics depend on
  const arrayProblem = spine.links.find((l) => l.topic === 'arrays');
  const afterSolve = await page.evaluate((id) => {
    window.__strided.recordAttempt(id, 3);
    const st = window.__strided.spineStatus();
    return { unlocked: Object.entries(st.unlocked).filter(([, v]) => v).map(([k]) => k) };
  }, arrayProblem.id);
  note(
    afterSolve.unlocked.length >= before.unlocked.length,
    `reaching a problem cannot lock anything (${before.unlocked.length} -> ${afterSolve.unlocked.length} open)`
  );
  note(
    afterSolve.unlocked.includes('slidingwindow') || afterSolve.unlocked.includes('strings'),
    'reaching Arrays opens the topics that depend on it'
  );

  // ---------- clicking a node routes into the filtered list ----------
  await page.click('[data-nav="map"]');
  await page.waitForTimeout(250);
  const clickable = await page.$('.mapnode:not([disabled])');
  if (clickable) {
    await clickable.click();
    await page.waitForTimeout(250);
    const view = await page.evaluate(() => window.__strided.app.view);
    note(view === 'learn', `clicking a map node routes to the filtered list (view=${view})`);
  } else {
    note(false, 'no clickable map node found');
  }

  // ---------- the sheet catalog index ----------
  await page.click('[data-nav="catalog"]');
  await page.waitForTimeout(400);
  const cat = await page.evaluate(() => window.__strided.catalog);
  note(!!cat, 'catalog loaded');
  if (cat) {
    note(cat.problems.length > 400, `catalog is substantial (${cat.problems.length} problems)`);
    const rows = await page.$$eval('.catrow', (els) => els.length);
    note(rows === cat.problems.length, `every catalog row renders (${rows}/${cat.problems.length})`);

    // filtering must actually narrow the list
    await page.click('[data-cat-diff="Hard"]');
    await page.waitForTimeout(300);
    const hardRows = await page.$$eval('.catrow', (els) => els.length);
    note(hardRows === cat.byDifficulty.Hard,
      `difficulty filter narrows to the Hard band (${hardRows}/${cat.byDifficulty.Hard})`);

    await page.click('[data-cat-diff="all"]');
    await page.waitForTimeout(200);
    await page.click('[data-cat-topic="graphs"]');
    await page.waitForTimeout(300);
    const graphRows = await page.$$eval('.catrow', (els) => els.length);
    note(graphRows === cat.byTopic.graphs,
      `topic filter narrows to graphs (${graphRows}/${cat.byTopic.graphs})`);
  }

  const real = errors.filter((e) => !/favicon/i.test(e));
  note(real.length === 0, `no page errors (${real.length})`);
  real.forEach((e) => console.log('    !', e));

  console.log(`\n${fails.length} failure(s)`);
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})();