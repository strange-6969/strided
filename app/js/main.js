import { loadData } from './data.js';
import { subscribe, getState, setLang, setNote, recordAttempt, unfreeze, streak, stats, exportJson, importJson, resetAll } from './store.js';
import { isDue, dueCount, daysBetween, GRADES, isoDay } from './srs.js';

const root = document.getElementById('root');

let DATA = null;
let SPINE = null;
let CATALOG = null;

const app = {
  view: 'today',
  problemId: null,
  pattern: null,
  difficulty: 'all',
  catalogTopic: 'all',
  catalogDiff: 'all',
  openTiers: {},
  hintIndex: -1,
  timerStart: null,
  elapsed: 0,
  ticking: null,
  mode: 'practice',
};

const LANGS = [
  { id: 'java', label: 'Java' },
  { id: 'python', label: 'Py' },
  { id: 'cpp', label: 'C++' },
];

let PATTERN_BY_ID = {};
let CARD_BY_PATTERN = {};
let PROBLEM_BY_ID = {};

const esc = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---------- helpers ---------- */

function problemDue(p) {
  const card = getState().cards[p.id];
  return card && isDue(card, new Date());
}

function visibleProblems() {
  let list = DATA.problems;
  if (app.pattern) list = list.filter((p) => p.pattern === app.pattern);
  if (app.difficulty !== 'all') list = list.filter((p) => p.difficulty === app.difficulty);
  return list;
}

function dueList() {
  return DATA.problems.filter(problemDue);
}

function tierHot(tier) {
  return /n\^?[2-9]|2\^|m\*n/.test(tier);
}

function fmtTime(ms) {
  const t = Math.max(0, Math.floor(ms / 1000));
  const m = String(Math.floor(t / 60)).padStart(2, '0');
  const s = String(t % 60).padStart(2, '0');
  return `${m}:${s}`;
}

function toast(msg) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.setAttribute('role', 'status');
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2100);
}

/* ---------- chrome ---------- */

function rail(s) {
  const due = dueCount(s.cards, new Date());
  const st = streak();
  const nav = [
    ['today', 'Today', due || null],
    ['learn', 'Learn', null],
    ['map', 'Map', null],
    ['catalog', 'Sheet', null],
    ['practice', 'Practice', null],
    ['patterns', 'Patterns', null],
    ['progress', 'Progress', null],
  ];
  return `
  <aside class="rail">
    <div class="brand"><b>Strided</b><span>v1</span></div>

    <div>
      <div class="rail-label">Mode</div>
      <nav class="nav">
        ${nav
          .map(
            ([id, label, count]) => `
          <button data-nav="${id}" aria-current="${app.view === id}">
            <span>${label}</span>
            ${count ? `<span class="count">${count}</span>` : ''}
          </button>`
          )
          .join('')}
      </nav>
    </div>

    <div>
      <div class="rail-label">Language</div>
      <div class="langs">
        ${LANGS.map(
          (l) => `<button data-lang="${l.id}" aria-pressed="${s.lang === l.id}">${l.label}</button>`
        ).join('')}
      </div>
    </div>

    <div>
      <div class="rail-label">Streak</div>
      <div style="padding:0 8px;display:flex;gap:18px">
        <div class="stat"><span class="n">${st.streak}</span><span class="k">days</span></div>
        <div class="stat"><span class="n">${s.xp}</span><span class="k">xp</span></div>
      </div>
    </div>

    <div style="margin-top:auto;display:flex;flex-direction:column;gap:6px">
      <button class="ghost" data-act="export" style="justify-content:flex-start;font-size:12.5px;padding:8px 12px">Export backup</button>
      <button class="ghost" data-act="import" style="justify-content:flex-start;font-size:12.5px;padding:8px 12px">Import backup</button>
      <button class="ghost" data-act="reset" style="justify-content:flex-start;font-size:12.5px;padding:8px 12px">Reset progress</button>
    </div>
  </aside>`;
}

function mobileNav() {
  const items = [
    ['today', 'Today', '◈'],
    ['learn', 'Learn', '▤'],
    ['map', 'Map', '⌗'],
    ['catalog', 'Sheet', '≡'],
    ['practice', 'Practice', '▷'],
    ['patterns', 'Patterns', '◇'],
    ['progress', 'Progress', '◑'],
  ];
  return `
  <nav class="mobilenav">
    ${items
      .map(
        ([id, label, glyph]) => `
      <button data-nav="${id}" aria-current="${app.view === id}">
        <span class="gl" aria-hidden="true">${glyph}</span>
        <span>${label}</span>
      </button>`
      )
      .join('')}
  </nav>`;
}

/* ---------- dependency map ---------- */

/* A topic is unlocked when every topic it requires has at least one problem
   reached at least once. "Reached" is deliberately weaker than mastered: the
   point is to unblock the path, not to demand mastery before you can proceed. */
function spineStatus() {
  const cards = getState().cards;
  const reached = {};
  for (const t of SPINE.topics) {
    const links = SPINE.links.filter((l) => l.topic === t.id);
    const total = links.length;
    const started = links.filter((l) => cards[l.id] && cards[l.id].reps > 0).length;
    const mastered = links.filter((l) => cards[l.id] && cards[l.id].frozen).length;
    reached[t.id] = { total, started, mastered };
  }

  const unlocked = {};
  for (const t of SPINE.topics) {
    unlocked[t.id] = t.needs.every((n) => (reached[n].started || 0) > 0);
  }
  // A topic with no prerequisites is always open, and a topic whose problems
  // have not been authored yet stays visible but is not clickable.
  for (const t of SPINE.topics) {
    if (!t.needs.length) unlocked[t.id] = true;
  }
  return { reached, unlocked };
}

function viewMap(s) {
  if (!SPINE) return '<div class="empty"><h4>Loading the map</h4></div>';
  const { reached, unlocked } = spineStatus();
  const byId = Object.fromEntries(SPINE.topics.map((t) => [t.id, t]));

  const authored = SPINE.links.length;
  const problemsTotal = DATA.problems.length;
  const reachedCount = SPINE.topics.filter((t) => reached[t.id].started > 0).length;
  const nextUp = SPINE.topics.find((t) => unlocked[t.id] && reached[t.id].started === 0);
  const fullCoverage = SPINE.topics.every((t) => reached[t.id].total > 0);

  const groups = [];
  for (const t of SPINE.topics) {
    let g = groups.find((x) => x.name === t.group);
    if (!g) groups.push((g = { name: t.group, items: [] }));
    g.items.push(t);
  }

  return `
  <header class="topbar">
    <div>
      <h1>Dependency map</h1>
      <p>${SPINE.topics.length} topics in prerequisite order. Nothing unlocks until what it needs is reached</p>
    </div>
    <div class="statline">
      <div class="stat"><span class="n">${reachedCount}/${SPINE.topics.length}</span><span class="k">topics reached</span></div>
      <div class="stat"><span class="n">${authored}</span><span class="k">authored</span></div>
    </div>
  </header>

  ${
    nextUp
      ? `<div class="ladder-callout">
          <span class="lc-label">Unlocked next</span>
          <strong>${esc(nextUp.name)}</strong>
          <span class="lc-why">${
            nextUp.needs.length
              ? `needs ${nextUp.needs.map((n) => esc(byId[n].name)).join(', ')}`
              : 'no prerequisites'
          }</span>
        </div>`
      : ''
  }

  <div class="mapgroups">
    ${groups
      .map(
        (g) => `
      <section class="sec mapgroup">
        <h3>${esc(g.name)} <span class="hint">${g.items.length} topics</span></h3>
        <div class="maplist">
          ${g.items.map((t) => {
            const r = reached[t.id];
            const open = unlocked[t.id];
            const hasLadder = r.total > 0;
            /* A topic with no authored ladder is not "locked". Locked means a
               prerequisite is unmet, which is a state the learner can change.
               "Not written" is a state I have to change, and labelling it
               locked would blame the map for something it is honestly showing. */
            const cls = hasLadder ? '' : 'is-empty';
            const state = !hasLadder
              ? 'unauthored'
              : r.mastered > 0
              ? 'mastered'
              : r.started > 0
              ? 'active'
              : open
              ? 'ready'
              : 'locked';
            return `
            <button class="mapnode ${cls} ${hasLadder && !open ? 'is-locked' : ''}" data-topic="${t.id}" ${hasLadder ? '' : 'disabled'}>
              <span class="mn-step">${t.step}</span>
              <span class="mn-body">
                <span class="mn-name">${esc(t.name)}</span>
                <span class="mn-blurb">${esc(t.blurb)}</span>
                ${
                  t.needs.length
                    ? `<span class="mn-needs">needs ${t.needs.map((n) => esc(byId[n].name)).join(', ')}</span>`
                    : '<span class="mn-needs free">no prerequisites</span>'
                }
              </span>
              <span class="mn-right">
                <span class="mn-state" data-state="${state}">${state}</span>
                <span class="mn-count">${
                  hasLadder ? `${r.started}/${r.total}` : t.publishedTotal ? `0 of ${t.publishedTotal} on the sheet` : 'no published count'
                }</span>
              </span>
            </button>`;
          }).join('')}
        </div>
      </section>`
      )
      .join('')}
  </div>

  <div class="note">
    <h4>How far this goes, honestly</h4>
    <p>The spine covers every topic on the Striver A2Z sheet: <strong>${SPINE.topics.length} topics, ${SPINE.edges.length} prerequisite edges</strong>, topologically ordered. ${
      fullCoverage
        ? `All <strong>${SPINE.topics.length}</strong> topics now have at least one authored complexity ladder, across <strong>${authored} problems</strong> and ${authored * 3} approaches.`
        : `Authored ladders cover ${SPINE.topics.filter((t) => reached[t.id].total > 0).length} of ${SPINE.topics.length} topics, across ${authored} problems.`
    }</p>
    <p style="margin-top:8px">What that does <strong>not</strong> mean is problem-for-problem parity with the sheet. The sheet lists roughly 474 questions; this app writes up ${problemsTotal} of them, with a three-rung ladder and five escalating hints each. Coverage here means the topic spine is complete, not that every listed question has a walkthrough.</p>
    <p style="margin-top:8px">Each topic's count is its own authored total, so progress here is progress through the material on this site rather than a claim about the whole sheet.</p>
  </div>`;
}

/* ---------- sheet catalog ---------- */

/* The catalog is the whole sheet as a browsable index. What it deliberately
   does not do is pretend every row has a walkthrough: a row either carries an
   authored ladder and is clickable, or it is counted as catalog-only. */
function viewCatalog(s) {
  if (!CATALOG) {
    return `<header class="topbar"><div><h1>Sheet</h1><p>Loading the catalog</p></div></header>`;
  }

  const authoredByTopic = {};
  for (const l of SPINE.links) {
    authoredByTopic[l.topic] = (authoredByTopic[l.topic] || 0) + 1;
  }

  let rows = CATALOG.problems;
  if (app.catalogTopic !== 'all') rows = rows.filter((p) => p.topic === app.catalogTopic);
  if (app.catalogDiff !== 'all') rows = rows.filter((p) => p.difficulty === app.catalogDiff);

  const topics = Object.entries(CATALOG.byTopic).sort((a, b) => b[1] - a[1]);
  const diffs = ['Easy', 'Medium', 'Hard'];
  const authoredTotal = SPINE.links.length;

  /* Long lists need a component other than one long divide-y list, so the rows
     become a scan-able two column grid. */
  return `
  <header class="topbar">
    <div>
      <h1>Sheet</h1>
      <p>${CATALOG.problems.length} problems across ${topics.length} topics, in dependency order. ${authoredTotal} have a written walkthrough</p>
    </div>
    <div class="statline">
      <div class="stat"><span class="n">${CATALOG.problems.length}</span><span class="k">on the sheet</span></div>
      <div class="stat"><span class="n">${authoredTotal}</span><span class="k">written up</span></div>
    </div>
  </header>

  <div class="filters">
    <button data-cat-topic="all" aria-pressed="${app.catalogTopic === 'all'}">All topics</button>
    ${topics
      .map(
        ([id, n]) =>
          `<button data-cat-topic="${id}" aria-pressed="${app.catalogTopic === id}">${esc(
            PATTERN_BY_ID[id] ? PATTERN_BY_ID[id].name : id
          )} ${n}</button>`
      )
      .join('')}
  </div>
  <div class="filters">
    ${['all', ...diffs]
      .map(
        (d) =>
          `<button data-cat-diff="${d}" aria-pressed="${app.catalogDiff === d}">${d === 'all' ? 'All levels' : d}</button>`
      )
      .join('')}
  </div>

  <div class="catlist">
    ${rows
      .map((p) => {
        const authored = (authoredByTopic[p.topic] || 0) > 0;
        return `
      <div class="catrow${authored ? '' : ' is-bare'}">
        <span class="cat-title">${esc(p.title)}</span>
        <span class="cat-topic">${esc(PATTERN_BY_ID[p.topic] ? PATTERN_BY_ID[p.topic].name : p.topic)}</span>
        <span class="cat-diff" data-d="${p.difficulty}">${p.difficulty}</span>
      </div>`;
      })
      .join('')}
  </div>

  <div class="note">
    <h4>What this index is</h4>
    <p>Every problem on the Striver A2Z sheet, extracted from public solution mirrors and ordered by the same dependency graph as the <strong>Map</strong>. Titles, topic placement and difficulty bands only: no solution code and no LeetCode content is reproduced here.</p>
    <p style="margin-top:8px">A row marked in plain text belongs to a topic that has at least one written walkthrough. It does not mean that specific row has one: <strong>${authoredTotal}</strong> problems are written up in full, against <strong>${CATALOG.problems.length}</strong> on the sheet. Use <strong>Map</strong> to see which topics have material, and the topic filters here to plan the rest.</p>
  </div>`;
}

/* ---------- views ---------- */

/* An empty review queue is the first thing a new learner sees, so it earns its
   space: it names what the app does that a bare problem list does not, and it
   gives a concrete first action rather than a shrug. */
function firstSteps() {
  const starters = DATA.problems.slice(0, 3);
  return `
  <section class="sec" style="margin-top:8px">
    <h3>Start here <span class="hint">three problems that cover three patterns</span></h3>
    <div class="list">
      ${starters
        .map(
          (p) => `
      <button class="row" data-open="${p.id}">
        <span class="id">${p.id}</span>
        <span>
          <span class="title">${esc(p.title)}</span>
          <span class="meta">${esc(PATTERN_BY_ID[p.pattern].name)} · ${p.ladder.length} approaches</span>
        </span>
        <span class="right"><span class="chip ${p.difficulty.toLowerCase()}">${p.difficulty}</span></span>
      </button>`
        )
        .join('')}
    </div>
  </section>

  <div class="note">
    <h4>What makes this different from a checklist</h4>
    <p>Every problem carries a complexity ladder: the brute force approach first, then a better one, then the optimal, each labelled with its time and space cost and a note on why the trade was worth it. You see the improvement, not just the answer.</p>
    <p style="margin-top:8px">Alongside it sits a syntax card for the pattern, so the incantation you always forget is in the same place as the idea. Once you have worked a problem, it schedules its own return before you forget it.</p>
  </div>`;
}

function viewToday(s) {
  const due = dueList();
  const st = streak();
  const total = DATA.problems.length;
  const touched = Object.keys(s.cards).length;

  const body = due.length
    ? `<div class="list">${due
        .map(
          (p) => `
      <button class="row" data-open="${p.id}">
        <span class="id">${p.id}</span>
        <span>
          <span class="title">${esc(p.title)}</span>
          <span class="meta">${esc(PATTERN_BY_ID[p.pattern].name)}</span>
        </span>
        <span class="right">
          <span class="chip ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
          <span class="due">due</span>
        </span>
      </button>`
        )
        .join('')}</div>`
    : `<div class="empty">
        <h4>${touched ? 'Nothing due right now' : 'Your review queue is empty'}</h4>
        <p>${
          touched
            ? 'You have cleared everything scheduled for today. Learning a new problem now means it comes back tomorrow.'
            : 'Nothing is due because nothing is scheduled yet. Work a problem and it will pick its own return date.'
        }</p>
        <div class="btns" style="justify-content:center">
          <button class="primary" data-nav="learn">Browse problems</button>
          <button class="ghost" data-nav="patterns">See the 15 patterns</button>
        </div>
      </div>`;

  return `
  <header class="topbar">
    <div>
      <h1>Today</h1>
      <p>${due.length ? `${due.length} problem${due.length > 1 ? 's' : ''} scheduled for review` : 'No reviews scheduled'}</p>
    </div>
    <div class="statline">
      <div class="stat"><span class="n">${st.streak}</span><span class="k">day streak</span></div>
      <div class="stat"><span class="n">${s.xp}</span><span class="k">xp</span></div>
      <div class="stat"><span class="n">${touched}/${total}</span><span class="k">tracked</span></div>
    </div>
  </header>
  ${body}
  ${due.length ? '' : firstSteps()}`;
}

function problemRow(p, s) {
  const card = s.cards[p.id];
  const due = card && isDue(card, new Date());
  return `
  <button class="row" data-open="${p.id}">
    <span class="id">${p.id}</span>
    <span>
      <span class="title">${esc(p.title)}</span>
      <span class="meta">${esc(PATTERN_BY_ID[p.pattern].name)}${
        card && card.frozen ? ' · mastered' : card && card.due ? ` · due in ${Math.max(0, daysBetween(new Date(), card.due))}d` : ''
      }</span>
    </span>
    <span class="right">
      <span class="chip ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
      ${due ? '<span class="due">due</span>' : ''}
    </span>
  </button>`;
}

function viewLearn(s) {
  const list = visibleProblems();
  const diffs = ['all', 'Easy', 'Medium', 'Hard'];
  return `
  <header class="topbar">
    <div>
      <h1>Learn</h1>
      <p>Read the problem, walk the complexity ladder, memorise the syntax</p>
    </div>
  </header>

  <div class="filters">
    ${diffs
      .map(
        (d) =>
          `<button data-diff="${d}" aria-pressed="${app.difficulty === d}">${d === 'all' ? 'All' : d}</button>`
      )
      .join('')}
    ${app.pattern
      ? `<button data-pattern-clear="1" aria-pressed="true">${esc(PATTERN_BY_ID[app.pattern].name)} ✕</button>`
      : ''}
  </div>

  <div class="list">${list.map((p) => problemRow(p, s)).join('')}</div>`;
}

function viewPractice(s) {
  const due = dueList();
  const pool = due.length ? due : DATA.problems;
  const label = due.length ? 'Due for review' : 'Nothing due, practice anything';

  return `
  <header class="topbar">
    <div>
      <h1>Practice</h1>
      <p>${label}. Timer on, hints escalate, nothing is graded until you say so</p>
    </div>
    <div class="statline">
      <div class="stat"><span class="n">${due.length}</span><span class="k">due</span></div>
    </div>
  </header>

  <div class="list">${pool
    .slice(0, 8)
    .map(
      (p) => `
    <button class="row" data-open="${p.id}" data-mode="practice">
      <span class="id">${p.id}</span>
      <span>
        <span class="title">${esc(p.title)}</span>
        <span class="meta">${esc(PATTERN_BY_ID[p.pattern].name)}</span>
      </span>
      <span class="right">
        <span class="chip ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
        ${due.some((d) => d.id === p.id) ? '<span class="due">due</span>' : ''}
      </span>
    </button>`
    )
    .join('')}</div>`;
}

function viewPatterns() {
  const covered = DATA.problems.reduce((acc, p) => {
    acc[p.pattern] = (acc[p.pattern] || 0) + 1;
    return acc;
  }, {});
  const s = getState();
  const masteried = {};
  Object.entries(s.cards).forEach(([id, c]) => {
    if (c.frozen) {
      const p = PROBLEM_BY_ID[id];
      if (p) masteried[p.pattern] = (masteried[p.pattern] || 0) + 1;
    }
  });

  return `
  <header class="topbar">
    <div>
      <h1>Patterns</h1>
      <p>Fifteen families. Mastery is measured per pattern, not by problem count</p>
    </div>
  </header>

  <div class="pgrid">
    ${DATA.patterns
      .map((p) => {
        const n = covered[p.pattern] || 0;
        const m = masteried[p.pattern] || 0;
        return `
      <button class="pcard" data-pattern="${p.id}">
        <h4>${esc(p.name)}</h4>
        <p>${esc(p.blurb)}</p>
        <div class="cnt">${m}/${n} mastered${CARD_BY_PATTERN[p.pattern] ? ' · has syntax card' : ''}</div>
      </button>`;
      })
      .join('')}
  </div>`;
}

function heatmap(s) {
  const days = [];
  const now = new Date();
  for (let i = 69; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const k = isoDay(d);
    const n = s.activity[k] || 0;
    const v = n === 0 ? 0 : n >= 6 ? 3 : n >= 3 ? 2 : 1;
    days.push(`<i data-v="${v}" title="${k}: ${n}"></i>`);
  }
  return `<div class="heat">${days.join('')}</div>`;
}

function viewProgress(s) {
  const st = stats();
  const perPattern = DATA.patterns
    .map((p) => {
      const ids = DATA.problems.filter((x) => x.pattern === p.id).map((x) => x.id);
      const frozen = ids.filter((id) => s.cards[id] && s.cards[id].frozen).length;
      const reps = ids.reduce((n, id) => n + ((s.cards[id] && s.cards[id].reps) || 0), 0);
      const pct = ids.length ? Math.round(((frozen + Math.min(reps, ids.length)) / (ids.length * 2)) * 100) : 0;
      return { p, frozen, reps, pct, n: ids.length };
    })
    .filter((x) => x.n > 0 || x.frozen > 0)
    .sort((a, b) => b.pct - a.pct);

  return `
  <header class="topbar">
    <div>
      <h1>Progress</h1>
      <p>Stored in this browser only. Export a backup before you clear site data.</p>
    </div>
    <div class="statline">
      <div class="stat"><span class="n">${s.xp}</span><span class="k">xp</span></div>
      <div class="stat"><span class="n">${st.due}</span><span class="k">due</span></div>
      <div class="stat"><span class="n">${st.frozen}</span><span class="k">mastered</span></div>
      <div class="stat"><span class="n">${st.reps}</span><span class="k">reviews</span></div>
    </div>
  </header>

  <section class="sec">
    <h3>Activity <span class="hint">last 70 days</span></h3>
    ${heatmap(s)}
    <div class="legend">
      <b><span class="sw" style="background:var(--surface-2)"></span>none</b>
      <b><span class="sw" style="background:#3f5a24"></span>1 to 2</b>
      <b><span class="sw" style="background:#6d9a2f"></span>3 to 5</b>
      <b><span class="sw" style="background:var(--accent)"></span>6 or more</b>
    </div>
  </section>

  ${
    perPattern.length
      ? `<section class="sec">
    <h3>Pattern mastery</h3>
    <div class="bars">
      ${perPattern
        .map(
          (x) => `
        <div class="bar-row">
          <span class="nm">${esc(x.p.name)}</span>
          <span class="track"><span class="fill ${x.pct < 34 ? 'cold' : ''}" style="width:${Math.min(100, x.pct)}%"></span></span>
          <span class="val">${x.frozen}/${x.n}</span>
        </div>`
        )
        .join('')}
    </div>
  </section>`
      : `<div class="empty"><h4>No activity yet</h4><p>Solve or review a problem and this fills in.</p></div>`
  }

  <div class="note">
    <h4>Sources and independence</h4>
    <p>Problem titles, ids and difficulty mirror public LeetCode listings. Approach ladders, syntax cards and hints are original material written for Strided.</p>
    <p style="margin-top:8px">Strided is an independent study aid. It is not affiliated with, endorsed by, or sponsored by LeetCode, and it hosts none of LeetCode content.</p>
    <ul style="margin-top:10px">
      ${DATA.sources.map((s2) => `<li><a href="${s2.url}" target="_blank" rel="noopener noreferrer">${esc(s2.name)}</a>: ${esc(s2.note)}</li>`).join('')}
    </ul>
  </div>`;
}

/* ---------- problem detail ---------- */

function ladderBlock(p, s) {
  return `
  <section class="sec">
    <h3>Complexity ladder <span class="hint">brute to optimal, same problem</span></h3>
    <div class="ladder">
      ${p.ladder
        .map((l) => {
          const open = !!app.openTiers[p.id + l.tier];
          return `
        <div class="rung ${open ? 'is-open' : ''}" data-tier="${l.tier}">
          <button class="rung-head" data-tier-toggle="${l.tier}">
            <span>
              <span class="tier">${l.tier}</span>
              <span class="rung-label">${esc(l.label)}</span>
            </span>
            <span class="cx">
              <span class="t ${tierHot(l.time) ? 'hot' : ''}">${esc(l.time)}</span>
              <span class="s ${tierHot(l.space) ? 'hot' : ''}">${esc(l.space)}</span>
            </span>
          </button>
          ${
            open
              ? `<div class="rung-body">
            <p class="why">${esc(l.why)}</p>
            <pre><code>${esc(l.code[s.lang] || l.code.java)}</code></pre>
          </div>`
              : ''
          }
        </div>`;
        })
        .join('')}
    </div>
  </section>`;
}

function syntaxBlock(p, s) {
  const card = CARD_BY_PATTERN[p.pattern];
  if (!card) return '';
  return `
  <section class="sec">
    <h3>Syntax to remember <span class="hint">${esc(PATTERN_BY_ID[p.pattern].name)}</span></h3>
    <p class="syntax-note">${esc(card.note)}</p>
    <pre><code>${esc(card.snippets[s.lang] || card.snippets.java)}</code></pre>
  </section>`;
}

function linksBlock(p) {
  const rows = [];
  if (p.platform.leetcode) {
    rows.push(['LeetCode', `https://leetcode.com/problems/${p.platform.leetcode}/`, 'Solve and submit the original']);
  }
  if (p.platform.neetcode) rows.push(['NeetCode', p.platform.neetcode, 'Video walkthrough']);
  if (p.platform.walkccc) rows.push(['Walkccc', p.platform.walkccc, 'Annotated solutions']);
  if (!rows.length) return '';
  return `
  <section class="sec">
    <h3>Practice elsewhere <span class="hint">opens in a new tab</span></h3>
    <div class="links">
      ${rows
        .map(
          ([name, url, note]) => `
        <a class="link" href="${url}" target="_blank" rel="noopener noreferrer">
          <span>
            <span class="name">${esc(name)}</span>
            <span class="url">${esc(note)}</span>
          </span>
          <span class="arrow" aria-hidden="true">→</span>
        </a>`
        )
        .join('')}
    </div>
  </section>`;
}

function practiceBlock(p, s) {
  const card = s.cards[p.id];
  const elapsed = app.elapsed;
  const h = p.hints;
  const shown = app.hintIndex;

  return `
  <section class="sec">
    <h3>Practice <span class="hint">timer starts when you open this</span></h3>

    <div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:20px">
      <span class="timer ${elapsed > 45 * 60 * 1000 ? 'over' : ''}">${fmtTime(elapsed)}</span>
      <button class="ghost" data-act="timer" style="padding:8px 14px;font-size:13px">${
        app.timerStart ? 'Pause' : 'Start'
      }</button>
    </div>

    <div class="hintbox">
      ${
        shown < 0
          ? `<p class="locked">Hints escalate from a nudge to a full skeleton. Nothing is revealed until you ask.</p>`
          : `<p>${esc(h[shown])}</p>`
      }
    </div>
    <div class="hint-nav">
      ${h
        .map(
          (_, i) => `
        <button data-hint="${i}" aria-pressed="${i === shown}" ${i > shown + 1 ? 'disabled' : ''} title="Hint ${i + 1}">${i + 1}</button>`
        )
        .join('')}
    </div>

    <p style="font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--text-faint);margin:26px 0 10px">
      How did it go
    </p>
    <div class="verdicts">
      <button data-grade="3">
        <span class="lab">Solved it</span>
        <span class="next">climbs the ladder</span>
      </button>
      <button data-grade="2">
        <span class="lab">Used a hint</span>
        <span class="next">holds position</span>
      </button>
      <button data-grade="1">
        <span class="lab">Read the answer</span>
        <span class="next">holds position</span>
      </button>
    </div>
    <button class="ghost" data-grade="0" style="margin-top:9px;width:100%">I could not start</button>

    ${
      card && card.frozen
        ? `<div class="note" style="margin-top:22px">
             <h4>Mastered</h4>
             <p>Clean recall at a long interval with no lapses. It no longer appears in your review queue.</p>
             <button class="ghost" data-unfreeze="${p.id}" style="margin-top:12px">Bring it back</button>
           </div>`
        : ''
    }
  </section>`;
}

function notesBlock(p, s) {
  return `
  <section class="sec">
    <h3>Your note <span class="hint">why you missed it, not what you did</span></h3>
    <textarea
      id="note"
      rows="4"
      placeholder="The trap was ... Next time I will ..."
      style="width:100%;background:#0a0c0b;border:1px solid var(--line);border-radius:var(--radius-sm);padding:12px 14px;font-family:var(--sans);font-size:14px;line-height:1.6;resize:vertical;color:var(--text)"
    >${esc(s.notes[p.id] || '')}</textarea>
    <button class="ghost" data-act="note" style="margin-top:9px">Save note</button>
  </section>`;
}

function drillBlock(p) {
  const pat = PATTERN_BY_ID[p.pattern];
  return `
  <section class="sec">
    <h3>Pattern drill <span class="hint">transfer, not recall</span></h3>
    <p class="syntax-note">${esc(pat.drill)}</p>
  </section>`;
}

function viewProblem(p, s) {
  return `
  <div class="detail">
    <button class="back" data-back="1">← All problems</button>

    <header class="detail-head">
      <div class="head-row">
        <span class="chip ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
        <span class="chip">#${p.id}</span>
        <span class="chip">${esc(PATTERN_BY_ID[p.pattern].name)}</span>
      </div>
      <h2>${esc(p.title)}</h2>
      <div class="head-row">
        ${p.lists
          .map(
            (l) =>
              `<span class="chip">${esc(
                l === 'neetcode150' ? 'NeetCode 150' : l === 'blind75' ? 'Blind 75' : 'Striver SDE'
              )}</span>`
          )
          .join('')}
      </div>
    </header>

    <p class="statement">${esc(p.statement)}</p>

    <div class="idea"><p>${esc(p.keyIdea)}</p></div>

    ${ladderBlock(p, s)}
    ${syntaxBlock(p, s)}
    ${linksBlock(p)}
    ${drillBlock(p)}
    ${practiceBlock(p, s)}
    ${notesBlock(p, s)}
  </div>`;
}

/* ---------- render ---------- */

function render() {
  if (!DATA) return;
  const s = getState();
  let main;

  if (app.view === 'problem' && PROBLEM_BY_ID[app.problemId]) {
    main = viewProblem(PROBLEM_BY_ID[app.problemId], s);
  } else if (app.view === 'learn') main = viewLearn(s);
  else if (app.view === 'map') main = viewMap(s);
  else if (app.view === 'catalog') main = viewCatalog(s);
  else if (app.view === 'practice') main = viewPractice(s);
  else if (app.view === 'patterns') main = viewPatterns(s);
  else if (app.view === 'progress') main = viewProgress(s);
  else main = viewToday(s);

  root.innerHTML = `<div class="shell">${rail(s)}<main class="main">${main}</main></div>${mobileNav()}`;
  root.setAttribute('aria-busy', 'false');
}

/* ---------- timer ---------- */

function stopTimer() {
  if (app.ticking) clearInterval(app.ticking);
  app.ticking = null;
}

function startTimer() {
  if (app.ticking) return;
  if (!app.timerStart) app.timerStart = Date.now() - app.elapsed;
  app.ticking = setInterval(() => {
    app.elapsed = Date.now() - app.timerStart;
    const el = document.querySelector('.timer');
    if (el) el.textContent = fmtTime(app.elapsed);
  }, 500);
}

/* ---------- events ---------- */

document.addEventListener('click', (e) => {
  const t = e.target.closest('[data-nav],[data-open],[data-lang],[data-diff],[data-pattern],[data-topic],[data-cat-topic],[data-cat-diff],[data-pattern-clear],[data-tier-toggle],[data-hint],[data-grade],[data-back],[data-act],[data-unfreeze]');
  if (!t) return;

  if (t.dataset.nav) {
    stopTimer();
    app.view = t.dataset.nav;
    app.problemId = null;
    return render();
  }

  if (t.dataset.open) {
    stopTimer();
    app.problemId = t.dataset.open;
    app.mode = t.dataset.mode || 'practice';
    app.view = 'problem';
    app.openTiers = { [t.dataset.open + 'brute']: true };
    app.hintIndex = -1;
    app.timerStart = null;
    app.elapsed = 0;
    startTimer();
    return render();
  }

  if (t.dataset.back) {
    stopTimer();
    app.view = 'learn';
    app.problemId = null;
    return render();
  }

  if (t.dataset.lang) {
    setLang(t.dataset.lang);
    return;
  }

  if (t.dataset.diff) {
    app.difficulty = t.dataset.diff;
    return render();
  }

  if (t.dataset.catTopic) {
    app.catalogTopic = t.dataset.catTopic;
    return render();
  }

  if (t.dataset.catDiff) {
    app.catalogDiff = t.dataset.catDiff;
    return render();
  }

  /* A map node jumps to the problem list filtered to that topic, so the map is
     a way in rather than a diagram that only describes itself. */
  if (t.dataset.topic) {
    app.pattern = t.dataset.topic;
    app.difficulty = 'all';
    app.view = 'learn';
    return render();
  }

  if (t.dataset.pattern) {
    app.pattern = app.pattern === t.dataset.pattern ? null : t.dataset.pattern;
    app.difficulty = 'all';
    app.view = 'learn';
    return render();
  }

  if (t.dataset.patternClear) {
    app.pattern = null;
    return render();
  }

  if (t.dataset.tierToggle) {
    const key = app.problemId + t.dataset.tierToggle;
    app.openTiers[key] = !app.openTiers[key];
    return render();
  }

  if (t.dataset.hint) {
    app.hintIndex = Number(t.dataset.hint);
    return render();
  }

  if (t.dataset.grade) {
    const grade = Number(t.dataset.grade);
    const before = streak().streak;
    recordAttempt(app.problemId, grade);
    const after = streak().streak;
    stopTimer();
    const p = PROBLEM_BY_ID[app.problemId];
    const card = getState().cards[p.id];
    const msg =
      grade === 3
        ? `+${25} xp, next review ${card.due ? daysBetween(new Date(), card.due) : 1}d`
        : grade === 0
        ? 'Back tomorrow'
        : card && card.frozen
        ? 'Mastered, out of the queue'
        : `Next review in ${daysBetween(new Date(), card.due)}d`;
    toast(after > before ? `${msg} · streak ${after}` : msg);
    app.view = 'today';
    app.problemId = null;
    return render();
  }

  if (t.dataset.unfreeze) {
    unfreeze(t.dataset.unfreeze);
    toast('Back in the queue');
    return render();
  }

  if (t.dataset.act === 'timer') {
    if (app.ticking) {
      stopTimer();
    } else {
      startTimer();
    }
    return render();
  }

  if (t.dataset.act === 'note') {
    const box = document.getElementById('note');
    if (box) {
      setNote(app.problemId, box.value);
      toast('Note saved');
    }
    return;
  }

  if (t.dataset.act === 'export') {
    const blob = new Blob([exportJson()], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `strided-${isoDay(new Date())}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    return toast('Backup downloaded');
  }

  if (t.dataset.act === 'import') {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = async () => {
      const f = input.files && input.files[0];
      if (!f) return;
      try {
        importJson(await f.text());
        toast('Backup restored');
        render();
      } catch (err) {
        toast('Could not read that file');
      }
    };
    input.click();
    return;
  }

  if (t.dataset.act === 'reset') {
    if (confirm('Clear all progress, streaks and notes? Export a backup first if you want to keep it.')) {
      resetAll();
      toast('Progress cleared');
      render();
    }
  }
});

subscribe(render);

root.innerHTML = `<div class="empty" style="margin:40px auto;max-width:340px"><h4>Loading problems</h4><p>Fetching the dataset.</p></div>`;

loadData()
  .then(({ problems, spine, catalog }) => {
    DATA = problems;
    SPINE = spine;
    CATALOG = catalog;
    PATTERN_BY_ID = Object.fromEntries(DATA.patterns.map((p) => [p.id, p]));
    CARD_BY_PATTERN = Object.fromEntries(DATA.syntaxCards.map((c) => [c.pattern, c]));
    PROBLEM_BY_ID = Object.fromEntries(DATA.problems.map((p) => [p.id, p]));
    render();
  })
  .catch((err) => {
    root.innerHTML = `<div class="empty" style="margin:60px auto;max-width:420px">
      <h4>Could not load the problem set</h4>
      <p>The dataset failed to load. Reload the page. If it keeps failing, the app is being served from a path that does not include <code>/app/data/problems.json</code>.</p>
    </div>`;
    console.error(err);
  });

/* Debug hook so the verification step can drive real flows. */
window.__strided = {
  app,
  getState,
  recordAttempt,
  stats,
  isoDay,
  isDue,
  dueList: () => (DATA ? dueList() : []),
  get problems() {
    return DATA ? DATA.problems : [];
  },
  get patterns() {
    return DATA ? DATA.patterns : [];
  },
  get ready() {
    return !!DATA;
  },
  get spine() {
    return SPINE;
  },
  get catalog() {
    return CATALOG;
  },
  spineStatus: () => (SPINE ? spineStatus() : null),
};

/* Test surface for the flows that promise the learner their data is never
   trapped. Exposed deliberately rather than hidden: the backup path is the one
   feature a user cannot verify by looking at the screen. */
window.__importBackup = importJson;
window.__resetAll = resetAll;