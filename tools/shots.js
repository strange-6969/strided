const { chromium } = require('playwright');

const path = require('path');
const fs = require('fs');
const OUT = path.join(__dirname, 'shots');
const BASE = process.env.STRIDED_URL || 'http://localhost:8788/';

const SHOTS = [
  { name: 'desktop-today', w: 1280, h: 900, steps: async () => {} },
  {
    name: 'desktop-detail',
    w: 1280,
    h: 1000,
    steps: async (p) => {
      await p.click('[data-nav="learn"]');
      await p.click('[data-open]');
      await p.waitForTimeout(300);
      await p.click('[data-tier-toggle="optimal"]');
      // Hints unlock one at a time, so click hint 1 before hint 2.
      await p.click('[data-hint="0"]');
      await p.waitForTimeout(150);
      await p.click('[data-hint="1"]');
      await p.waitForTimeout(300);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'desktop-patterns',
    w: 1280,
    h: 900,
    steps: async (p) => {
      await p.click('[data-nav="patterns"]');
      await p.waitForTimeout(300);
    },
  },
  {
    name: 'desktop-progress',
    w: 1280,
    h: 1000,
    steps: async (p) => {
      await p.click('[data-nav="progress"]');
      await p.waitForTimeout(300);
    },
  },
  {
    name: 'desktop-map',
    w: 1280,
    h: 1100,
    steps: async (p) => {
      await p.click('[data-nav="map"]');
      await p.waitForTimeout(350);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'mobile-map',
    w: 390,
    h: 844,
    steps: async (p) => {
      await p.click('.mobilenav [data-nav="map"]');
      await p.waitForTimeout(350);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'desktop-catalog',
    w: 1280,
    h: 1000,
    steps: async (p) => {
      await p.click('[data-nav="catalog"]');
      await p.waitForTimeout(500);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'desktop-profile',
    w: 1280,
    h: 1000,
    steps: async (p) => {
      await p.click('[data-nav="profile"]');
      await p.waitForTimeout(350);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'mobile-profile',
    w: 390,
    h: 844,
    steps: async (p) => {
      await p.click('.mobilenav [data-nav="profile"]');
      await p.waitForTimeout(350);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'mobile-catalog',
    w: 390,
    h: 844,
    steps: async (p) => {
      await p.click('.mobilenav [data-nav="catalog"]');
      await p.waitForTimeout(500);
      await p.evaluate(() => window.scrollTo(0, 0));
    },
  },
  {
    name: 'mobile-today',
    w: 390,
    h: 844,
    steps: async () => {},
  },
  {
    name: 'mobile-detail',
    w: 390,
    h: 844,
    steps: async (p) => {
      await p.click('.mobilenav [data-nav="learn"]');
      await p.click('[data-open]');
      await p.waitForTimeout(300);
      await p.click('[data-tier-toggle="optimal"]');
      await p.waitForTimeout(250);
    },
  },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const errors = [];

  for (const s of SHOTS) {
    const ctx = await browser.newContext({
      viewport: { width: s.w, height: s.h },
      deviceScaleFactor: 2,
    });
    const page = await ctx.newPage();
    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(`${s.name}: ${m.text()}`);
    });
    page.on('pageerror', (e) => errors.push(`${s.name}: PAGEERROR ${e.message}`));

    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.__strided && window.__strided.ready, { timeout: 10000 });
    await s.steps(page);
    await page.waitForTimeout(350);

    // measure overflow at this exact viewport
    const overflow = await page.evaluate(() => ({
      docW: document.documentElement.scrollWidth,
      winW: window.innerWidth,
      overflow: document.documentElement.scrollWidth > window.innerWidth + 2,
    }));

    await page.screenshot({ path: `${OUT}/${s.name}.png`, fullPage: false });
    console.log(
      `${s.name.padEnd(20)} ${s.w}x${s.h}  docW=${overflow.docW} winW=${overflow.winW}  overflow=${overflow.overflow}`
    );
    await ctx.close();
  }

  await browser.close();
  console.log('\nconsole errors:', errors.length ? errors : 'none');
})();