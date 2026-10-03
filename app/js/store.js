/* Store: localStorage-backed progress. No backend, no account.
   Export and import are first class so a learner is never trapped. */

import { initialCard, schedule, applyXp, markActivity, computeStreak, isoDay, isDue } from './srs.js';

const KEY = 'strided.v1';

const EMPTY = {
  cards: {},
  xp: 0,
  activity: {},
  lang: 'java',
  notes: {},
};

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...EMPTY };
    const parsed = JSON.parse(raw);
    return { ...EMPTY, ...parsed };
  } catch {
    return { ...EMPTY };
  }
}

let state = load();
const listeners = new Set();

function persist() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* private browsing or a full quota. The session still works in memory;
       the learner just cannot return to it later. */
  }
}

function emit() {
  persist();
  listeners.forEach((fn) => fn(state));
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function getState() {
  return state;
}

export function setLang(lang) {
  state = { ...state, lang };
  emit();
}

export function setNote(problemId, text) {
  const notes = { ...state.notes, [problemId]: text };
  state = { ...state, notes };
  emit();
}

/* Recording an attempt is the only write that touches scheduling, xp and the
   daily activity log, so those three can never drift out of sync. */
export function recordAttempt(problemId, grade) {
  const prev = state.cards[problemId] || initialCard();
  const next = schedule(prev, grade, new Date());
  const cards = { ...state.cards, [problemId]: next };
  const xp = applyXp(state.xp, grade);
  const activity = markActivity(state.activity, new Date());
  state = { ...state, cards, xp, activity };
  emit();
  return next;
}

export function unfreeze(problemId) {
  const prev = state.cards[problemId];
  if (!prev) return;
  const cards = { ...state.cards, [problemId]: { ...prev, frozen: false, step: -1, due: null, lapses: prev.lapses + 1 } };
  state = { ...state, cards };
  emit();
}

export function resetAll() {
  state = { ...EMPTY };
  emit();
}

export function exportJson() {
  return JSON.stringify(state, null, 2);
}

export function importJson(text) {
  const parsed = JSON.parse(text);
  if (!parsed || typeof parsed !== 'object') throw new Error('Not a Strided backup file.');
  state = { ...EMPTY, ...parsed };
  emit();
  return true;
}

export function streak() {
  return computeStreak(state.activity, new Date());
}

export function todayKey() {
  return isoDay(new Date());
}

export function stats() {
  const cards = Object.values(state.cards);
  /* Count due with the same isDue predicate the UI uses. Comparing raw
     instants here would drift from day-boundary logic at the edges. */
  return {
    tracked: cards.length,
    due: cards.filter((c) => isDue(c, new Date())).length,
    frozen: cards.filter((c) => c.frozen).length,
    reps: cards.reduce((n, c) => n + (c.reps || 0), 0),
  };
}