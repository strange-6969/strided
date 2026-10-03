/* Spaced repetition engine.
   Grade 0..3 mapped from the five practice verdicts. Interval ladder grows on
   recall and collapses on failure. Any reasonable scheduler beats massed
   practice (Cepeda et al. 2006); the ladder is deliberately simple so the
   behaviour is inspectable rather than clever. */

export const GRADES = {
  solvedSolo: 3,
  hinted: 2,
  peeked: 1,
  gaveUp: 0,
};

const LADDER = [1, 3, 7, 16, 35, 72, 150];

/* step is the index of the NEXT interval and starts at -1 (never reviewed),
   so the first successful recall lands on LADDER[0] rather than skipping it. */
export function initialCard() {
  return { step: -1, due: null, reps: 0, lapses: 0, last: null, frozen: false };
}

export function schedule(card, grade, today = new Date()) {
  const next = { ...card };

  if (grade === GRADES.gaveUp) {
    next.step = -1;
    next.lapses += 1;
    next.due = addDays(today, 1);
  } else {
    /* A weak recall must not advance as far as a clean one. Grade caps how far
       up the ladder this attempt may climb, so "used a hint" can never produce
       the same interval as "solved it alone".
       From step -1: solo lands on LADDER[0] (1 day), a hint holds at LADDER[0],
       peeking holds at LADDER[0]. Only repeated clean recall climbs. */
    const climb = grade === GRADES.solvedSolo ? 1 : 0;
    next.step = Math.max(0, Math.min(next.step + climb, LADDER.length - 1));
    next.due = addDays(today, LADDER[next.step]);
  }

  next.reps += 1;
  next.last = isoDay(today);

  // Sustained clean recall at a long interval means it is mastered.
  if (grade === GRADES.solvedSolo && next.step >= 4 && next.lapses === 0) {
    next.frozen = true;
  }

  return next;
}

export function isDue(card, today = new Date()) {
  if (!card || !card.due || card.frozen) return false;
  return startOfDay(card.due) <= startOfDay(today);
}

/* Due count ignores frozen cards: mastery should reduce surface area. */
export function dueCount(cards, today = new Date()) {
  return Object.values(cards).filter((c) => isDue(c, today)).length;
}

export function addDays(date, n) {
  const d = new Date(date);
  d.setDate(d.getDate() + n);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function startOfDay(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function daysBetween(a, b) {
  return Math.round((startOfDay(b) - startOfDay(a)) / 86400000);
}

/* Day keys are built from LOCAL calendar parts, never toISOString().
   A learner in IST creating a card at 07:00 local is on the local date; using
   UTC here silently files the review under the previous day and shifts every
   streak boundary. */
export function isoDay(date) {
  const d = new Date(date);
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

/* Streak accounting.
   A freeze covers exactly one missed day. Two consecutive misses ends the
   streak: this is deliberate. An unbreakable streak teaches users to stop
   playing rather than to play honestly. */
export function computeStreak(activity, today = new Date()) {
  const days = new Set(Object.keys(activity));
  let streak = 0;
  let cursor = startOfDay(today);
  let freezes = 0;

  if (!days.has(isoDay(cursor))) {
    cursor = addDays(cursor, -1);
    if (!days.has(isoDay(cursor))) return { streak: 0, freezesLeft: 1 };
  }

  for (let i = 0; i < 400; i++) {
    const key = isoDay(cursor);
    if (days.has(key)) {
      streak += 1;
    } else if (freezes === 0) {
      freezes = 1;
    } else {
      break;
    }
    cursor = addDays(cursor, -1);
  }

  return { streak, freezesLeft: freezes === 0 ? 1 : 0 };
}

export function markActivity(activity, date = new Date()) {
  const key = isoDay(date);
  return { ...activity, [key]: (activity[key] || 0) + 1 };
}

/* XP with decay. A lapse costs a fraction of the bank so a long absence is
   visible without wiping all progress. */
export function applyXp(xp, grade) {
  const gain = { 3: 25, 2: 15, 1: 6, 0: 0 }[grade] ?? 0;
  const penalty = grade === 0 ? 4 : 0;
  return Math.max(0, xp + gain - penalty);
}