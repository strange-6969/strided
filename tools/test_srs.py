import json, subprocess, textwrap, sys

SRS = '/home/strange/Projects/strided/app/js/srs.js'
js = open(SRS).read()
TODAY = "new Date('2026-10-03T00:00:00')"

TESTS = [
("interval grows on recall", f"""
  let c = initialCard();
  c = schedule(c, 3, {TODAY});
  const d1 = daysBetween({TODAY}, c.due);
  if (d1 !== 1) throw new Error('first solo due should be 1 day, got ' + d1);
  c = schedule(c, 3, {TODAY}); c = schedule(c, 3, {TODAY});
  if (!(daysBetween({TODAY}, c.due) > d1)) throw new Error('interval did not grow');
"""),
("give-up resets step and schedules tomorrow", f"""
  let c = initialCard();
  for (let i=0;i<3;i++) c = schedule(c, 3, {TODAY});
  const before = c.step;
  c = schedule(c, 0, {TODAY});
  if (c.step !== -1) throw new Error('step should return to the floor, got ' + c.step);
  if (c.lapses !== 1) throw new Error('lapse not counted');
  if (daysBetween({TODAY}, c.due) !== 1) throw new Error('due should be 1 day after give-up');
"""),
("a weak recall never climbs the ladder", f"""
  // A brand new card reviews tomorrow whatever the grade: nothing is known yet.
  const freshHint = schedule(initialCard(), 2, {TODAY});
  const freshSolo = schedule(initialCard(), 3, {TODAY});
  if (daysBetween({TODAY}, freshHint.due) !== 1) throw new Error('new card should return tomorrow');
  if (daysBetween({TODAY}, freshSolo.due) !== 1) throw new Error('new card should return tomorrow');

  // From an established position, grade controls whether the ladder is climbed.
  let hinted = initialCard();
  for (let i=0;i<3;i++) hinted = schedule(hinted, 3, {TODAY});
  const before = hinted.step;
  const held = schedule(hinted, 2, {TODAY});
  if (held.step !== before) throw new Error('a hint must not climb: ' + before + ' -> ' + held.step);

  let peeked = initialCard();
  for (let i=0;i<3;i++) peeked = schedule(peeked, 3, {TODAY});
  if (schedule(peeked, 1, {TODAY}).step !== before) throw new Error('peeking must not climb');

  let climbed = initialCard();
  for (let i=0;i<3;i++) climbed = schedule(climbed, 3, {TODAY});
  if (!(schedule(climbed, 3, {TODAY}).step > before)) throw new Error('a solo solve must climb');
"""),
("mastery freezes only after sustained clean recall", f"""
  let c = initialCard();
  for (let i=0;i<5;i++) c = schedule(c, 3, {TODAY});
  if (!c.frozen) throw new Error('not frozen after 5 clean solves: reps=' + c.reps + ' step=' + c.step);
"""),
("a single lapse permanently blocks freeze", f"""
  let c = initialCard();
  for (let i=0;i<3;i++) c = schedule(c, 3, {TODAY});
  c = schedule(c, 0, {TODAY});
  for (let i=0;i<8;i++) c = schedule(c, 3, {TODAY});
  if (c.frozen) throw new Error('lapse must disqualify mastery');
"""),
("frozen card is never due", f"""
  let c = initialCard(); c.frozen = true; c.due = {TODAY};
  if (isDue(c, {TODAY})) throw new Error('frozen card reported due');
"""),
("dueCount ignores frozen and unscheduled", f"""
  const cards = {{ a: {{ due: {TODAY}, frozen: false }}, b: {{ due: {TODAY}, frozen: true }}, c: {{ due: null, frozen: false }} }};
  const n = dueCount(cards, {TODAY});
  if (n !== 1) throw new Error('expected 1 due, got ' + n);
"""),
("streak counts consecutive days", f"""
  const r = computeStreak({{ '2026-10-03':1, '2026-10-02':2, '2026-10-01':1 }}, {TODAY});
  if (r.streak !== 3) throw new Error('expected 3, got ' + r.streak);
"""),
("one missed day is covered by a freeze", f"""
  const r = computeStreak({{ '2026-10-03':1, '2026-10-01':1, '2026-09-30':1 }}, {TODAY});
  if (r.streak !== 3) throw new Error('freeze did not bridge the gap, got ' + r.streak);
"""),
("two consecutive misses end the streak", f"""
  const r = computeStreak({{ '2026-10-03':1, '2026-09-30':1, '2026-09-29':1 }}, {TODAY});
  if (r.streak !== 1) throw new Error('two gaps must break the streak, got ' + r.streak);
"""),
("streak survives until end of today", f"""
  const r = computeStreak({{ '2026-10-02':1, '2026-10-01':1 }}, {TODAY});
  if (r.streak !== 2) throw new Error('should not break before midnight, got ' + r.streak);
"""),
("empty activity gives zero streak", f"""
  const r = computeStreak({{}}, {TODAY});
  if (r.streak !== 0) throw new Error('expected 0, got ' + r.streak);
"""),
("xp gains on success", f"""
  let xp = 0;
  xp = applyXp(xp, 3); if (xp !== 25) throw new Error('solo +25, got ' + xp);
  xp = applyXp(xp, 2); if (xp !== 40) throw new Error('hinted +15, got ' + xp);
  xp = applyXp(xp, 1); if (xp !== 46) throw new Error('peeked +6, got ' + xp);
"""),
("xp decays on failure but floors at zero", f"""
  if (applyXp(10, 0) !== 6) throw new Error('give-up should cost 4');
  if (applyXp(0, 0) !== 0) throw new Error('xp must not go negative');
"""),
("markActivity increments today", f"""
  let a = markActivity({{}}, {TODAY});
  a = markActivity(a, {TODAY});
  if (a['2026-10-03'] !== 2) throw new Error('expected 2, got ' + a['2026-10-03']);
"""),
("addDays crosses month boundary", f"""
  const d = addDays(new Date('2026-01-30T00:00:00'), 3);
  if (isoDay(d) !== '2026-02-02') throw new Error('got ' + isoDay(d));
"""),
]

results = []
for name, body in TESTS:
    src = js + "\n\nconst out = (() => {\n" + textwrap.indent(body.strip(), '  ') + "\n  return 'PASS';\n})();\nconsole.log(out);\n"
    open('/tmp/srs_t.js','w').write(src)
    r = subprocess.run(['node','/tmp/srs_t.js'], capture_output=True, text=True, timeout=30)
    ok = r.returncode == 0 and 'PASS' in r.stdout
    err = ''
    if not ok:
        lines = [l for l in r.stderr.strip().splitlines() if l.strip()]
        err = lines[-1][:160] if lines else r.stdout[:160]
    results.append((ok, name, err))

print("=" * 70)
for ok, name, err in results:
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok and err:
        print("        -> " + err)
print("=" * 70)
passed = sum(1 for o,_,_ in results if o)
print(f"{passed}/{len(results)} passed")
sys.exit(0 if passed == len(results) else 1)